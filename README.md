# hyperlink_preview

## Purpose

Hyperlink_preview allows getting data needed to display a small visual preview of a http link.  
It searches deeper than only `<meta property="og:` tags. It also parses other tags in \<head\> or the html \<body\> if needed to have all data needed for the preview.  
It also have an "asynchronous" data getter to avoid having to wait for the full analysis of the images (see below).

## Demo
A small demo is provided.  
Create an venv, install the package, and test (above code is for windows):
```
py -3 -m venv venv
venv\Scripts\activate.bat
pip install hyperlink_preview
python -m hyperlink_preview.demo_html https://en.wikipedia.org/wiki/Your_Name
```
It will:
- get the data to build the preview:
```
Data for preview:
    title: Your Name - Wikipedia
    type: website
    image: https://upload.wikimedia.org/wikipedia/en/0/0b/Your_Name_poster.png
    url: https://en.wikipedia.org/wiki/Your_Name
    description: Your Name (Japanese: 君の名は。,...
    site_name: en.wikipedia
    domain: en.wikipedia.org
```
- and open your web browser with an exemple of a preview:


![image](https://user-images.githubusercontent.com/26554495/151885801-10da1770-6b4a-4633-8541-3be7a275c755.png)

## Install

```
pip install hyperlink_preview
```

## Usage

```python
import hyperlink_preview as HLP

hlp = HLP.HyperLinkPreview(url="https://en.wikipedia.org/wiki/Your_Name")
if hlp.is_valid:
    preview_data = hlp.get_data()
    # Return a dict with keys: ['title', 'type', 'image', 'url', 'description', 'site_name']
    # Values are None or the value for building a preview.
```

## Details

HyperLinkPreview searches for [og tags](https://ogp.me/).  
If the target link does not provide them (or not all), HyperLinkPreview searches deeper to find suitable data.  

### About images and performance

If no image is provided, we search for all img tags in the html. Today `GIF, PNG and JPG image formats are handled`.  
We take the sizes of all those images, and we give preference to the largest, and whose ratio is <3 and whose sides are > 50px.  
For the sake of efficiency:
  - **read only bytes necessary** to know the dimensions of the images (not the whole image)
  - **parallelized requests** to all the images

However, if the target link contains a lot of pictures, it can take a while (one to several seconds) to do all the requests. A hyperlink preview may need to be displayed quickly (for instance: on mouse hover). In that case:

### Get all data except image first, then image
```python
import hyperlink_preview as HLP

hlp = HLP.HyperLinkPreview(url="https://en.wikipedia.org/wiki/Your_Name")
if hlp.is_valid:
    preview_data = hlp.get_data(wait_for_imgs=False)
    # returns as soon as the data are fetched, but don't wait to "parse" all images tags if needed.
    # it allows you to display a spinner as link preview image (or anything else to keep your user waiting).
    

# ... later you can get the remaining image data id needed:
if preview_data["image"] is None:
    preview_data = hlp.get_data(wait_for_imgs=True)
```
