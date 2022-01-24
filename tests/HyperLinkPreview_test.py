import unittest
import requests
from src.hyperlink_preview.hyperlink_preview import has_og_property
import src.hyperlink_preview as HP
from bs4.element import Tag

class TestUrl(unittest.TestCase):
    def test_fetch_errors(self):
        with self.assertRaises(requests.exceptions.RequestException):
            HP.HyperLinkPreview(url="")
        with self.assertRaises(requests.exceptions.RequestException):
            HP.HyperLinkPreview(url="http://")

    def test_fetch(self):
        url = "https://stackoverflow.com/questions/26623026/cant-catch-systemexit-exception-python"
        hp = HP.HyperLinkPreview(url=url)
        self.assertIsNotNone(hp.html)
        if hp.html is not None:
            self.assertTrue("exception in the following fashion" in hp.html)

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
        self.assertEqual(hp.get_title(), "How to Create a Link Preview: The Definite Guide [Implementation and Demo Included] - Andrej Gajdos")
        self.assertEqual(hp.get_type(), "article")
        self.assertEqual(hp.get_image(), "https://andrejgajdos.com/wp-content/uploads/2019/11/generating-link-preview.png")
        self.assertEqual(hp.get_url(), "https://andrejgajdos.com/how-to-create-a-link-preview/")
        self.assertEqual(hp.get_description(), "The whole strategy of creating link previews, including implementation using open-source libraries in node.js. The whole solution is released as npm package.")

