#!/usr/bin/env python3
"""Download only captioned paper figures and write a per-paper provenance manifest."""

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


CAPTION_RE = re.compile(r"\b(?:figure|fig\.?|table)\s*\d+\b", re.IGNORECASE)
DECORATIVE_RE = re.compile(r"(?:logo|icon|avatar|badge|favicon)", re.IGNORECASE)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


class _FigureParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.figures = []
        self.current = None
        self.in_caption = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "figure":
            self.current = {"images": [], "caption_parts": []}
            return
        if self.current is None:
            return
        if tag.lower() == "img" and attrs.get("src"):
            self.current["images"].append(
                {"src": attrs["src"], "alt": attrs.get("alt", "")}
            )
        elif tag.lower() == "figcaption":
            self.in_caption = True

    def handle_endtag(self, tag):
        if tag.lower() == "figcaption":
            self.in_caption = False
        elif tag.lower() == "figure" and self.current is not None:
            self.current["caption"] = " ".join(self.current["caption_parts"]).strip()
            self.figures.append(self.current)
            self.current = None
            self.in_caption = False

    def handle_data(self, data):
        if self.current is not None and self.in_caption:
            self.current["caption_parts"].append(data.strip())


def collect_figure_images(html, html_url):
    """Return images inside figures with an explicit paper figure/table caption."""
    parser = _FigureParser()
    parser.feed(html)
    parsed_page = urlparse(html_url)
    found = []
    for figure in parser.figures:
        caption = figure.get("caption", "")
        if not CAPTION_RE.search(caption):
            continue
        for image in figure["images"]:
            image_url = urljoin(html_url, image["src"])
            parsed_image = urlparse(image_url)
            if parsed_image.netloc != parsed_page.netloc:
                continue
            if DECORATIVE_RE.search(parsed_image.path):
                continue
            found.append(
                {
                    "url": image_url,
                    "alt": image["alt"],
                    "caption": caption,
                }
            )
    return found


def _image_dimensions(path):
    try:
        from PIL import Image
        with Image.open(str(path)) as image:
            return image.width, image.height
    except Exception:
        return None, None


def build_image_manifest(article_dir, paper_url, source_by_name=None):
    """Describe only raster/vector images in this article's own images folder."""
    article_dir = Path(article_dir).resolve()
    images_dir = (article_dir / "images").resolve()
    try:
        images_dir.relative_to(article_dir)
    except ValueError:
        raise ValueError("article images directory escapes article folder")

    source_by_name = source_by_name or {}
    items = []
    if images_dir.exists():
        for path in sorted(images_dir.iterdir(), key=lambda item: item.name.lower()):
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            resolved = path.resolve()
            try:
                resolved.relative_to(images_dir)
            except ValueError:
                raise ValueError("image symlink escapes this article folder")
            width, height = _image_dimensions(path)
            items.append(
                {
                    "path": "images/" + path.name,
                    "source_url": source_by_name.get(path.name, paper_url),
                    "width": width,
                    "height": height,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    return {"paper_url": paper_url, "images": items}


def write_image_manifest(article_dir, paper_url, source_by_name=None):
    article_dir = Path(article_dir).resolve()
    manifest_path = article_dir / "work" / "images-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_image_manifest(article_dir, paper_url, source_by_name)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _html_url(paper_url):
    if "/abs/" in paper_url:
        return paper_url.replace("/abs/", "/html/")
    if "/html/" in paper_url:
        return paper_url
    raise ValueError("Unsupported paper URL; expected arXiv /abs/ or /html/")


def download_arxiv_html_images(arxiv_url, output_dir):
    html_url = _html_url(arxiv_url)
    print("📄 获取论文 HTML: {}".format(html_url))
    response = requests.get(html_url, timeout=30)
    response.raise_for_status()
    figures = collect_figure_images(response.text, html_url)
    if not figures:
        print("⚠️ 未找到带论文图号的图；为避免混入网页装饰图片，未下载任何图片")
        return []

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    sources = {}
    figure_number = 1
    table_number = 1
    for item in figures:
        parsed = urlparse(item["url"])
        extension = Path(parsed.path).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            extension = ".png"
        is_table = re.search(r"\btable\b", item["caption"], re.IGNORECASE)
        prefix = "table" if is_table else "figure"
        if is_table:
            filename = "{}{}{}".format(prefix, table_number, extension)
            table_number += 1
        else:
            filename = "{}{}{}".format(prefix, figure_number, extension)
            figure_number += 1
        destination = output_dir / filename
        try:
            image_response = requests.get(item["url"], timeout=30)
            image_response.raise_for_status()
            content_type = image_response.headers.get("Content-Type", "").lower()
            if not content_type.startswith("image/"):
                print("⚠️ 跳过非图片资源: {}".format(item["url"]))
                continue
            destination.write_bytes(image_response.content)
            downloaded.append(str(destination))
            sources[filename] = item["url"]
            print("✓ 下载论文图: {} ({})".format(filename, item["caption"]))
        except Exception as error:
            print("✗ 下载论文图失败: {} ({})".format(item["url"], error))

    article_dir = output_dir.parent
    manifest_path = write_image_manifest(article_dir, arxiv_url, sources)
    print("图片来源清单: {}".format(manifest_path))
    return downloaded


def download_huggingface_paper_images(paper_url, output_dir):
    response = requests.get(paper_url, timeout=30)
    response.raise_for_status()
    match = re.search(r"arxiv\.org/abs/(\d+\.\d+)", response.text)
    if not match:
        print("❌ 页面中未找到 arXiv 论文链接")
        return []
    return download_arxiv_html_images(
        "https://arxiv.org/abs/{}".format(match.group(1)), output_dir
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_url")
    parser.add_argument("output_dir", help="本论文 article/images 目录")
    args = parser.parse_args(argv)
    if "arxiv.org" in args.paper_url:
        downloaded = download_arxiv_html_images(args.paper_url, args.output_dir)
    elif "huggingface.co" in args.paper_url:
        downloaded = download_huggingface_paper_images(args.paper_url, args.output_dir)
    else:
        print("❌ 不支持的论文源: {}".format(args.paper_url))
        return 2
    print("完成：共下载 {} 张论文图".format(len(downloaded)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
