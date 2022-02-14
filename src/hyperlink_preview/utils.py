"""
Some utils functions for hyperlink preview
"""

from urllib.parse import urljoin
from bs4.element import Comment

def has_og_property(meta_tag, properties):
    """
    Checks if the given meta tag has an attribute property equals to og:something,
    something being in properties.
    Returns:
        None if the given tag "is" not og:something. something otherwise.
    """
    try:
        if not meta_tag["property"].startswith("og:"):
            return None
        _property = meta_tag["property"][len("og:"):] # remove og: from beginning of tag
        if _property in properties:
            return _property
    except: # pylint: disable=bare-except
        pass
    return None

def tag_visible(element) -> bool:
    """
    check if a bs4 element is visible
    (as we can, it may be not if js hide it, but we do what we can to be fast)
    Returns
        True if element is probably visible
        False otherwise (in style tag, or script, or ...)
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def get_base_url(full_url):
    """
    Returns:
        from full url: the scheme and the domain, port, and path.
        Return ends with a /
    """
    url_base = urljoin(full_url, "remove_me")[0:-len("remove_me")]
    return url_base


def get_img_url(img_src, url_base):
    """
    Get an image url from the src attribute af an image, and the page base url
    """
    if not img_src:
        return None
    if not "//" in img_src: ## it's not an absolute url
        if img_src[0] == "/":
            img_src = img_src[1:]
        img_src = url_base + img_src
    return img_src
