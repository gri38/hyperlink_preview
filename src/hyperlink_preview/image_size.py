"""
Get the size of a picture without reading the whole picture.
"""

from operator import attrgetter
import struct
from typing import Optional, Tuple, List
import logging
from requests import Response

logger = logging.getLogger('hyperlinkpreview')

class ImageSize:
    """
    Small POD struct to store image url, and WxH
    """
    def __init__(self, url: str, width: int, height:int):
        self.url = url
        self.width = width
        self.height = height
        self.area_pixels = self.width * self.height
        self.ratio = max(self.width, self.height) / min(self.width, self.height)

    def __str__(self):
        return f"{self.url}: {self.width}x{self.height}; A={self.area_pixels}, R={self.ratio}"

    def __repr__(self):
        return str(self)

class ImageDataList:
    """
    Class to store images with their sizes.
    They are stored in 3 lists: ok, too small (< 50px x 50px), and bad ration
    (longest side / smallest side > 3)
    """
    def __init__(self):
        self.images_ok:List[ImageSize] = []
        self.images_too_small:List[ImageSize] = []
        self.images_bad_ratio:List[ImageSize] = []

    def append(self, image_size:ImageSize):
        """
        Append the given image in one of the lists.
        """
        if image_size.width <= 50 or image_size.height <= 50:
            self.images_too_small.append(image_size)
        elif image_size.ratio > 3:
            self.images_bad_ratio.append(image_size)
        else:
            self.images_ok.append(image_size)

    def get_best_image(self) -> Optional[str]:
        """
        Returns:
            url of best image
        """
        best_image = self.get_best_image_in_list(self.images_ok)
        if best_image:
            return best_image.url

        best_image = self.get_best_image_in_list(self.images_bad_ratio)
        if best_image:
            return best_image.url

        best_image = self.get_best_image_in_list(self.images_too_small)
        if best_image:
            return best_image.url

        return None

    @staticmethod
    def get_best_image_in_list(image_list:List[ImageSize]) -> Optional[ImageSize]:
        """
        Returns:
            image with the max pixels
        """
        try:
            return max(image_list, key=attrgetter("area_pixels"))
        except:  # pylint: disable=bare-except
            return None

def get_size(req: Response) -> Tuple[int, int]:
    """
    Args:
        req: a request opened in stream mode.

    Returns:
        (width, height). (-1, -1) if not found.
    """
    try:
        data = ResponseReader(req)
        if data[0:len(b'GIF89a')] in (b'GIF87a', b'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            logger.debug(f"GIF size: {w}x{h}")
            return (int(w), int(h))

        if data[0:len(b'\211PNG\r\n\032\n')] == b'\211PNG\r\n\032\n' and data[12:16] == b'IHDR':
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            logger.debug(f"PNG size: {w}x{h}")
            return (int(w), int(h))

        if data[0:len(b'\211PNG\r\n\032\n')] == b'\211PNG\r\n\032\n':
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            logger.debug(f"old PNG size: {w}x{h}")
            return (int(w), int(h))

        if data[0:len(b'\377\330')] == b'\377\330':
            # JPEG
            off = 0
            while off < 500 * 1024: # let's read only 500KB
                while data[off] == 0xff:
                    off = off + 1
                mrkr = data[off]
                off = off + 1
                if mrkr == 0xd8:
                    continue # SOI
                if mrkr == 0xd9:
                    break # EOI
                if 0xd0 <= mrkr <= 0xd7:
                    continue
                if mrkr == 0x01:
                    continue # TEM

                length = data[off] << 8 | data[off+1]
                off = off + 2

                if mrkr == 0xc0:
                    w = (data[off+3]<<8) | data[off+4]
                    h = (data[off+1]<<8) | data[off+2]
                    logger.debug(f"JPG size: {w}x{h}")
                    return (int(w), int(h))
                off = off + length - 2

    except StopIteration:
        pass
    logger.error("Image type not supported")
    return (-1, -1)

class ResponseReader:
    """
    Class to access byte(s) in a response of a requests.get(stream=True).
    Bytes are read when need by chunk of 32 bytes.

    Exemple:
        r = requests.get(url, stream=True)
        data = ResponseReader(r)
        data[12]
        data[0:12]
    """
    def __init__(self, req: Response):
        self.req = req
        self.read_count = 0 # number of bytes read
        self.data = b''

    def __getitem__(self, key):
        """
        Args:
            key: supported types: int: index, and slice with start and stop
        """
        if isinstance(key, int):
            index = key
        elif isinstance(key, slice):
            if key.start is None or key.stop is None:
                raise IndexError("Key slice start or stop are None")
            if key.start > key.stop:
                raise IndexError("Key slice start > stop")
            index = key.stop
        else:
            raise IndexError(f"key type is [{type(key)}]. Only int and slice are supported")

        while (index + 1) > self.read_count:
            self.data = self.data + next(self.req.iter_content(32))
            self.read_count = self.read_count + 32
        return self.data[key]
