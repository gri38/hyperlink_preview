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
        url = "https://support.microsoft.com/en-us/topic/0fdcaf87-ee5e-8929-e54c-65e04235a634"
        hp = HP.HyperLinkPreview(url=url)
        self.assertEqual(hp.get_data()["title"], 'Well-known security identifiers in Windows operating systems')
        self.assertEqual(hp.get_data()["type"], None)
        self.assertEqual(hp.get_data()["image"], 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31')
        self.assertEqual(hp.get_data()["url"], 'https://support.microsoft.com/en-us/topic/0fdcaf87-ee5e-8929-e54c-65e04235a634')
        self.assertEqual(hp.get_data()["site_name"], 'support.microsoft')
        self.assertEqual(hp.get_data()["domain"], 'support.microsoft.com')
        self.assertEqual(hp.get_data()["description"], 'A security identifier (SID) is a unique value of variable length that is used to identify a security principal (such as a security group) in Windows operating systems. SIDs that identify generic users or generic groups is particularly well-known. Their values remain constant across all operating systems. This information is useful for troubleshooting issues that involve security. It is also useful for troubleshooting display issues in the Windows access control list (ACL) editor. Windows tracks a security principal by its SID. To display the security principal in the ACL editor, Windows resolves the SID to its associated security principal name. Note: This article describes circumstances under which the ACL editor displays a security principal SID instead of the security principal name. Over time, this set of well-known SIDs has grown. The tables in this article organize these SIDs according to which version of Windows introduced them. Well-known SIDs (all versions of Windows) SIDs add')
