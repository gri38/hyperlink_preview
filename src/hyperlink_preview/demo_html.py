"""
This module to call hyperlink_preview and display the result in a webbrowser.
Provided as sample html and how to call hyperlink_preview.
"""

from pathlib import Path
import shutil
import tempfile
import time
import webbrowser
import argparse
from . import hyperlink_preview as HLP
import html


if __name__ == "__main__":
    template_html = """
    <!DOCTYPE html>
    <html lang="en">
    <meta charset="UTF-8">
    <title>Hyperlink "demo"</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"
        integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <style>
    <!--
        .hlp {
            display: flex;
            background-color: #ff44110D;
            border: solid 1px #f41;
            border-radius: 4px;
        }
        .hlp-img {
        }
        .hlp-img img{
        height: 0;
        border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
        }
        .hlp-informations {
            display: flex;
            flex-direction: column;
            padding: 16px;
        }
        .hlp-info-header {
            display: flex;
            margin-bottom: 1em;
        }
        .hlp-info-type {
            background-color: #f41;
            color: #E3E3E3;
            border-radius: 3px;
            padding: 0 10px;
            text-transform: uppercase;
            margin-right: 10px;
            font-size: 0.7em;
            display: flex;
            align-items: center;
        }
        .hlp-info-title {
            text-decoration: none;
            color: #f41;
            font-weight: bold;
        }
        .hlp-info-desc {
            text-align: justify;
            color: #333;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 4; /* number of lines to show */
            line-clamp: 4; 
            -webkit-box-orient: vertical;
        }
        .hlp-info-link-ico {
            height: 24px;
            width: 24px;
            margin-right: 10px;
        }
        .hlp-info-link-ico path {
            fill: #ffa288;
        }
        .hlp-info-domain {
            margin-top: 1em;
            display: flex;
            align-items: center;
            color: #ffa288;
        }
    -->
    </style>

    <body onload="adapt_hlp_img();">

        <div class="hlp">
            <div class="hlp-img">
                <img src="PLACEHOLDER_IMG">
            </div>
            <div class="hlp-informations">
                <div class="hlp-info-header">
                    <span class="hlp-info-type">PLACEHOLDER_TYPE</span>
                    <a href="PLACEHOLDER_URL" class="hlp-info-title">PLACEHOLDER_TITLE</a>
                </div>
                <div class="hlp-info-desc">
                    PLACEHOLDER_DESC
                </div>
                <div class="hlp-info-domain">
                    <svg class="hlp-info-link-ico" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px"
                        y="0px" width="512px" height="512px" viewBox="0 0 512 512" enable-background="new 0 0 512 512" xml:space="preserve">
                        <script xmlns="" id="__gaOptOutExtension" />
                        <path fill="#010101"
                            d="M459.654,233.373l-90.531,90.5c-49.969,50-131.031,50-181,0c-7.875-7.844-14.031-16.688-19.438-25.813  l42.063-42.063c2-2.016,4.469-3.172,6.828-4.531c2.906,9.938,7.984,19.344,15.797,27.156c24.953,24.969,65.563,24.938,90.5,0  l90.5-90.5c24.969-24.969,24.969-65.563,0-90.516c-24.938-24.953-65.531-24.953-90.5,0l-32.188,32.219  c-26.109-10.172-54.25-12.906-81.641-8.891l68.578-68.578c50-49.984,131.031-49.984,181.031,0  C509.623,102.342,509.623,183.389,459.654,233.373z M220.326,382.186l-32.203,32.219c-24.953,24.938-65.563,24.938-90.516,0  c-24.953-24.969-24.953-65.563,0-90.531l90.516-90.5c24.969-24.969,65.547-24.969,90.5,0c7.797,7.797,12.875,17.203,15.813,27.125  c2.375-1.375,4.813-2.5,6.813-4.5l42.063-42.047c-5.375-9.156-11.563-17.969-19.438-25.828c-49.969-49.984-131.031-49.984-181.016,0  l-90.5,90.5c-49.984,50-49.984,131.031,0,181.031c49.984,49.969,131.031,49.969,181.016,0l68.594-68.594  C274.561,395.092,246.42,392.342,220.326,382.186z" />
                    </svg>
                    <span>PLACEHOLDER_DOMAIN</span>
                </div>
            </div>
        </div>
        <script>
            $(".hlp-img").height($(".hlp-informations").outerHeight());
            $(".hlp-img img").height("100%");
        </script>

    </body>

    </html>"""

    parser = argparse.ArgumentParser(description='Build an hyperlink preview and open it in a webbrowser')
    parser.add_argument('url', type=str, help='url of the link')
    args = parser.parse_args()

    hlp = HLP.HyperLinkPreview(url=args.url)
    if not hlp.is_valid:
        print(f"error while parsing preview of [{args.url}]")
    else:
        preview_data = hlp.get_data()
        print("Data for preview:")
        for key, value in preview_data.items():
            print(f"    {key}: {value}")
        try:
            template_html = template_html.replace("PLACEHOLDER_IMG", preview_data["image"])
        except:
            template_html = template_html.replace("PLACEHOLDER_IMG", "https://upload.wikimedia.org/wikipedia/commons/8/85/Media_Viewer_Icon_-_Link_Hover.svg")
        
        try:
            template_html = template_html.replace("PLACEHOLDER_TYPE", preview_data["type"])
        except:
            template_html = template_html.replace("PLACEHOLDER_TYPE", "link")

        template_html = template_html.replace("PLACEHOLDER_URL", args.url)
        template_html = template_html.replace("PLACEHOLDER_TITLE", preview_data["title"])
        template_html = template_html.replace("PLACEHOLDER_DESC", html.escape(preview_data["description"]))
        template_html = template_html.replace("PLACEHOLDER_DOMAIN", preview_data["domain"])

        try:
            temp_folder = Path(tempfile.mkdtemp())
            temp_file  = temp_folder / "hyperlink_preview_demo.html"
            print(temp_file)
            with open(temp_file, "w", encoding="utf-8") as html:
                html.write(template_html)
            webbrowser.open(str(temp_file))
            time.sleep(10)
        finally:
            try:
                print(f"let's delete {temp_file}")
                shutil.rmtree(temp_folder)
            except Exception:
                pass
