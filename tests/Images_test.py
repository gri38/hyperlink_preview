import unittest
import src.hyperlink_preview as HP

class ImagesUrl(unittest.TestCase):
    @staticmethod
    def get_image(url):
        hlp = HP.HyperLinkPreview(url=url)
        data = hlp.get_data()
        return data["image"]

    def test_image_in_og(self):
        self.assertEqual(ImagesUrl.get_image("https://www.youtube.com/watch?v=XsZDWNk_RIA"), 
                         "https://i.ytimg.com/vi/XsZDWNk_RIA/maxresdefault.jpg")

    def test_image_parse(self):
        self.assertEqual(ImagesUrl.get_image("https://diconombre.pagesperso-orange.fr/TableMat.htm"), 
                         "https://diconombre.pagesperso-orange.fr/TableMat_fichiers/image024.gif")
    
    def test_image_parse_relative_path(self):
        self.assertEqual(ImagesUrl.get_image("https://annystudio.com/software/colorpicker/"), 
                         "https://annystudio.com/software/colorpicker/justcolorpicker-anatomy.png")

    def test_image_your_name(self):
        self.assertEqual(ImagesUrl.get_image("https://en.wikipedia.org/wiki/Your_Name"), 
                         "https://upload.wikimedia.org/wikipedia/en/0/0b/Your_Name_poster.png")

    def test_image_arte(self):
        self.assertEqual(ImagesUrl.get_image("https://www.arte.tv/fr/videos/RC-021426/voyages-au-pays-des-maths/"), 
                         "https://api-cdn.arte.tv/api/mami/v1/program/fr/RC-021426/1920x1080?ts=1632401984&type=TEXT&watermark=true")
    
    def test_image_joplin(self):
        self.assertEqual(ImagesUrl.get_image("https://joplinapp.org/"), 
                         "https://joplinapp.org/images/home-top-img-2x.png")

    def test_img_as_base64(self):
        self.assertEqual(ImagesUrl.get_image("https://raymii.org/s/snippets/Sending_commands_or_input_to_a_screen_session.html"), 
                         None)

    def test_no_img(self):
        self.assertEqual(ImagesUrl.get_image("https://grenoble.craigslist.org/"), 
                         None)