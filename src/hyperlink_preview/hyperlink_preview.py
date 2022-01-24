"""
Parse an url preview data (base on Open Graph protocol, but not only)
Instantiate a HyperLinkPreview object.
"""

import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup

def has_og_property(meta_tag, properties):
    """
    Checks if the given meta tag has an attribute property equals to og:something,
    something being in properties.
    Returns:
        None if the given tag "is" not og:something. something otherwise.
    """
    print(type(meta_tag))
    print(meta_tag)
    try:
        if not meta_tag["property"].startswith("og:"):
            return None
        _property = meta_tag["property"][len("og:"):] # remove og: from beginning of tag
        if _property in properties:
            return _property
    except: # pylint: disable=bare-except
        pass
    return None

class HyperLinkPreview:
    """
    Class to parse an url preview data (base on Open Graph protocol, but not only)
    """

    properties = ['title', 'type', 'image', 'url', 'description']

    def __init__(self, url:str = None, html: str = None):
        self.datas = {property: None for property in HyperLinkPreview.properties}
        print(self.datas)
        if url is not None:
            html = self._fetch(url)
        self.html = html
        self._parse()

    def get_title(self) -> Optional[str]:
        """
        Returns:
            The title of the hyperlink preview or None
        """
        return self.datas["title"]

    def get_type(self) -> Optional[str]:
        """
        Returns:
            The type of the hyperlink preview or None
        """
        return self.datas["type"]

    def get_image(self) -> Optional[str]:
        """
        Returns:
            The image of the hyperlink preview or None
        """
        return self.datas["image"]

    def get_url(self) -> Optional[str]:
        """
        Returns:
            The url of the hyperlink preview or None
        """
        return self.datas["url"]

    def get_description(self) -> Optional[str]:
        """
        Returns:
            The description of the hyperlink preview or None
        """
        return self.datas["description"]

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
            logging.error(f"Cannot fetch url [{url}]: [{ex}]")
            raise ex

    def _parse(self):
        soup = BeautifulSoup(self.html, "html.parser")
        metas = soup.findAll("meta")
        for one_meta_tag in metas:
            _property = has_og_property(one_meta_tag, HyperLinkPreview.properties)
            if _property:
                try:
                    self.datas[_property] = one_meta_tag["content"]
                except: # pylint: disable=bare-except
                    pass # don't care if meta tag has no "content" attribute.
        print(self.datas)
