"""
Parse an url preview data (base on Open Graph protocol, but not only)
Instantiate a HyperLinkPreview object.
"""

import logging
import queue
from threading import Thread, Lock, Event
from typing import Dict, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from . import utils
from . import image_size

logger = logging.getLogger('hyperlinkpreview')

class HyperLinkPreview:
    """
    Class to parse an url preview data (base on Open Graph protocol, but not only)
    Warning: constructor raises if url is not accessible: handle it.
    """

    properties = ['title', 'type', 'image', 'url', 'description', 'site_name']

    def __init__(self, url:str):
        """
        Raises:
            - requests.exceptions.RequestException: if cannot get url
            - ValueError if no url or None
        """
        self.data_lock = Lock()
        self.is_valid = False
        self.full_parsed = Event()
        self._datas: Dict[str, Optional[str]] = \
            {property: None for property in HyperLinkPreview.properties}
        if url is None or not url:
            raise ValueError("url is None")
        _html = self._fetch(url)
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug(f"fetched html size: {len(_html)}")

        self.link_url = url
        self._parse(_html)

    def get_data(self, wait_for_imgs=True):
        """
        Args:
            wait_for_imgs: - if True, waits for the images parse before returning.
                             The image parse is when no image info in the head, and we need to parse the whole html for img tags.
                           - if False, retruns without waiting. Caller should check the 'image' value in the returned dict,
                             if it is None, another call to this method with wait_for_imgs=True is required to have the image.
        Returns:
            The data dict (a copy). Keys are ['title', 'type', 'image', 'url', 'description', 'site_name']
        """
        if wait_for_imgs:
            self.full_parsed.wait()
            with self.data_lock:
                return self._datas.copy()

        with self.data_lock:
            return self._datas.copy()

    def _fetch(self, url: str) -> str:
        """
        Returns:
            the html content of the given url

        Raises:
            requests.exceptions.RequestException: If cannot get url.
        """
        try:
            return requests.get(url).text
        except requests.exceptions.RequestException as ex:
            logging.error("Cannot fetch url [%s]: [%s]", url, ex)
            raise ex

    def _parse(self, html):
        """
        First parse og tags, then search deeper if some tags were not present.
        """
        if not html:
            self.full_parsed.set()
            return
        
        i = 0
        html_len = len(html)
        skip_chars = ["\n", "\r", "\t", " "]
        while i < html_len and html[i] in skip_chars:
            i += 1

        if not html[i] == "<" and not html[i + 1] == "<":
            self.full_parsed.set()
            return
        with self.data_lock:
            soup = BeautifulSoup(str(html), "html.parser")
            self.is_valid = True
            metas = soup.findAll("meta")
            for one_meta_tag in metas:
                _property = utils.has_og_property(one_meta_tag, HyperLinkPreview.properties)
                if _property:
                    try:
                        self._datas[_property] = one_meta_tag["content"]
                    except: # pylint: disable=bare-except
                        pass # don't care if meta tag has no "content" attribute.

            self._parse_deeper_url()
            self._parse_deeper_domain()
            self._parse_deeper_site_name()
            self._parse_deeper_title(soup)
            self._parse_deeper_description(soup)
            self._parse_deeper_image(soup)

    def _parse_deeper_url(self):
        url = self._datas["url"]
        if url:
            return
        self._datas["url"] = self.link_url

    def _parse_deeper_domain(self):
        url = self._datas["url"]
        domain= urlparse(url).netloc
        self._datas["domain"] = str(domain)

    def _parse_deeper_site_name(self):
        name = self._datas["site_name"]
        if name:
            return
        domain = self._datas["domain"]
        if not domain:
            return
        name = domain.replace("www.", "")
        try:
            name = name[0:name.rindex(".")]
        except: # pylint: disable=bare-except
            pass
        self._datas["site_name"] = name

    def _parse_deeper_title(self, soup: BeautifulSoup):
        title = self._datas["title"]
        if title:
            return
        title_tag = soup.find('title')
        if title_tag:
            self._datas["title"] = title_tag.text
            return
        title_tag = soup.find('h1')
        if title_tag:
            self._datas["title"] = title_tag.text
            return
        title_tag = soup.find('h2')
        if title_tag:
            self._datas["title"] = title_tag.text
            return

    def _parse_deeper_description(self, soup: BeautifulSoup):
        """
        If self.get_description() == None, search a description in:
          - <meta name="description">
          - then <meta name="twitter:description">
          - then: 1000 first char of text in <p> tags.
        """
        description = self._datas["description"]
        if description:
            return
        description_meta_tag = soup.find('meta',  {"name": "Description"})
        if description_meta_tag:
            self._datas["description"] = str(description_meta_tag["content"]) # type: ignore
            return

        # usually twitter description are for subscription: it's not a description on the page.
        # description_meta_tag = soup.find('meta',  {"name": "twitter:description"})
        # if description_meta_tag:
        #     self.datas["description"] = description_meta_tag["content"]
        #     return
        # let's take the visible text from <p>:

        p_tags = soup.findAll('p')
        visible_p_tags = list(filter(utils.tag_visible, p_tags))
        visible_text = " ".join(one_p.text.strip() for one_p in visible_p_tags)
        visible_text = visible_text.replace("\n", " ")
        visible_text = ' '.join(visible_text.split()) # remove multiple spaces
        self._datas["description"] = visible_text[0:1000]

    def _parse_deeper_image(self, soup):
        image = self._datas["image"]
        if image:
            self.full_parsed.set()
            return
        image_tag = soup.find('link',  {"rel": "image_src"})
        if image_tag:
            self._datas["image"] = image_tag["href"]
            self.full_parsed.set()
            return

        # No image info provided. We'll search for all images, in a dedicated thread:
        Thread(target=self._parse_deeper_image_in_tags, args=[soup]).start()

    def _parse_deeper_image_in_tags(self, soup):
        try:
            src_queue = queue.Queue()
            img_tags = soup.findAll("img")
            candidates = image_size.ImageDataList()
            for one_tag in img_tags:
                try:
                    src = one_tag["src"]
                except:  # pylint: disable=bare-except
                    continue
                src = utils.get_img_url(src, utils.get_base_url(self.link_url))
                if src is None:
                    continue
                src_queue.put(src)

            for _ in range(16):
                Thread(target=self.fetch_image_size, args=[src_queue, candidates], daemon=True).start()

            src_queue.join()
            with self.data_lock:
                self._datas["image"] = candidates.get_best_image()
        finally:
            self.full_parsed.set()

    def fetch_image_size(self, src_queue, candidates: image_size.ImageDataList):
        """
        Args:
            src_queue: the queue containing all urls to image to fetch and get size.
            candidates: the list to append images
        """
        try:
            while True:
                src = src_queue.get(block=False)
                # logging.debug(f"Start processing {src}")
                try: # important to avoid dead lock of queue join.
                    with requests.get(src, stream=True) as response:
                        if response.status_code == 200:
                            width, height = image_size.get_size(response)
                            # logging.debug(f"Processing {src}: width: [{width}]")
                            if width != -1:
                                candidates.append(image_size.ImageSize(src, width, height))
                except: # pylint: disable=bare-except
                    # logging.debug(f"End processing {src}: exception")
                    pass
                finally:
                    src_queue.task_done()

        except queue.Empty:
            # logging.debug(f"End processing: Queue empty")
            pass
