import unittest
import requests
from src.hyperlink_preview.utils import has_og_property
import src.hyperlink_preview as HP
from bs4.element import Tag

class TestUrl(unittest.TestCase):
    def test_fetch_errors(self):
        with self.assertRaises(ValueError):
            HP.HyperLinkPreview(url="")
        with self.assertRaises(requests.exceptions.RequestException):
            HP.HyperLinkPreview(url="http://")
        with self.assertRaises(ValueError):
            HP.HyperLinkPreview(url=None)

    def test_fetch(self):
        url = "https://stackoverflow.com/questions/26623026/cant-catch-systemexit-exception-python"
        hp = HP.HyperLinkPreview(url=url)
        self.assertTrue(hp.is_valid)

        url_img = "https://www.tolkiendil.com/_media/logo/logo.png?w=500"
        hp = HP.HyperLinkPreview(url=url_img)
        self.assertFalse(hp.is_valid)


    # def test_fetch_bot_forbiden(self):
    #     url = "file:///C:/Users/frguni0/workspace/hyperlink_preview/tests/test.html"
    #     hp = HP.HyperLinkPreview(url=url)
    #     print("toto")

class TestOgProperty(unittest.TestCase):
    def test_has_og_property(self):
        self.assertEqual(has_og_property(Tag(name="meta", attrs={"property":"og:image"}), ["image"]), "image")
        self.assertIsNone(has_og_property(Tag(name="meta", attrs={"property":"image"}), ["image"]))
        self.assertIsNone(has_og_property(Tag(name="meta", attrs={"property":"og:imagez"}), ["image"]))
        self.assertEqual(has_og_property(Tag(name="meta", attrs={"property":"og:image"}), ["url", "image"]), "image")

class TestParse(unittest.TestCase):
    def test_andrejgajdos(self):
        url = "https://andrejgajdos.com/how-to-create-a-link-preview/"
        hp = HP.HyperLinkPreview(url=url)
        self.assertEqual(hp.get_data()["title"], "How to Create a Link Preview: The Definite Guide [Implementation and Demo Included] - Andrej Gajdos")
        self.assertEqual(hp.get_data()["type"], "article")
        self.assertEqual(hp.get_data()["image"], "https://andrejgajdos.com/wp-content/uploads/2019/11/generating-link-preview.png")
        self.assertEqual(hp.get_data()["url"], "https://andrejgajdos.com/how-to-create-a-link-preview/")
        self.assertEqual(hp.get_data()["description"], "The whole strategy of creating link previews, including implementation using open-source libraries in node.js. The whole solution is released as npm package.")

class TestParseHtml(unittest.TestCase):
    def test_html_begins_with_nl(self):
        url = "https://github.com/apprenticeharper/DeDRM_tools/releases"
        hp = HP.HyperLinkPreview(url=url)
        self.assertEqual(hp.get_data()["title"], "Releases · apprenticeharper/DeDRM_tools")
        self.assertEqual(hp.get_data()["type"], "object")
        self.assertTrue("https://opengraph.githubassets.com/" in hp.get_data()["image"])
        self.assertTrue("/apprenticeharper/DeDRM_tools" in hp.get_data()["image"])
        self.assertEqual(hp.get_data()["url"], "/apprenticeharper/DeDRM_tools/releases")
        self.assertEqual(hp.get_data()["description"], "DeDRM tools for ebooks. Contribute to apprenticeharper/DeDRM_tools development by creating an account on GitHub.")

    def test_not_html(self):
        url = "https://andrejgajdos.com/wp-content/uploads/2019/11/generating-link-preview.png"
        hp = HP.HyperLinkPreview(url=url)
        for one_value in hp.get_data().values():
            self.assertIsNone(one_value)

    def test_html_begins_with_windows_nl(self):
        url = "https://social.technet.microsoft.com/wiki/contents/articles/51722.windows-problem-steps-recorder-psr-quick-and-easy-documenting-of-your-steps-and-procedures.aspx"
        hp = HP.HyperLinkPreview(url=url)
        print(hp.get_data())
        self.assertEqual(hp.get_data()["title"], "\r\n\tWindows Problem Steps Recorder (PSR): quick and easy documenting of your steps and procedures - TechNet Articles - United States (English) - TechNet Wiki\r\n")
        self.assertEqual(hp.get_data()["type"], None)
        self.assertEqual(hp.get_data()["image"], 'https://social.technet.microsoft.com/wiki/resized-image.ashx/__size/550x0/__key/communityserver-wikis-components-files/00-00-00-00-05/4428.psr.JPG')
        self.assertEqual(hp.get_data()["url"], 'https://social.technet.microsoft.com/wiki/contents/articles/51722.windows-problem-steps-recorder-psr-quick-and-easy-documenting-of-your-steps-and-procedures.aspx')
        self.assertEqual(hp.get_data()["site_name"], 'social.technet.microsoft')
        self.assertEqual(hp.get_data()["domain"], 'social.technet.microsoft.com')
        self.assertEqual(hp.get_data()["description"], "Problem steps recorder is a tool that is available in Windows since Windows 7 (client) / Windows 2008 R2. In this blog post, you'll be able to find more details on PSR (or Problem Steps Recorder). In short: So it's an ideal tool to document steps and procedures on the fly, while you're executing. Although it's a very handy tool and quick and easy to use, one of the disadvantages is that it does not capture keystrokes. Another disadvantage is that PSR is taken full-screen snapshots, but you can solve this to edit the saved file, extract or edit the images and resave the document. Hit the Windows button and start typing psr… (or run psr.exe) The configuration settings are 'hiding' in the Help/Settings button, on the right-hand side of the menu... There are 2 settings you need to look at: You must make sure to set the number of screenshots at a sufficiently high level. In early versions of PSR you can set it to 99, but newer versions (W10, W2012) you can go up to 999. A note of advice: se")
