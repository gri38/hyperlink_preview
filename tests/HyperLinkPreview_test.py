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
        self.assertEqual(hp.get_data()["image"], "https://opengraph.githubassets.com/364d50dfedc00216c2e3aaa0b25b4aef9f99ec6aadfd6eb2b9c027e4928d478c/apprenticeharper/DeDRM_tools")
        self.assertEqual(hp.get_data()["url"], "/apprenticeharper/DeDRM_tools/releases")
        self.assertEqual(hp.get_data()["description"], "DeDRM tools for ebooks. Contribute to apprenticeharper/DeDRM_tools development by creating an account on GitHub.")

    def test_not_html(self):
        url = "https://andrejgajdos.com/wp-content/uploads/2019/11/generating-link-preview.png"
        hp = HP.HyperLinkPreview(url=url)
        for one_value in hp.get_data().values():
            self.assertIsNone(one_value)
