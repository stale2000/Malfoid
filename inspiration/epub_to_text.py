#!/usr/bin/env python3
"""Extract EPUB reading-order text into a UTF-8 plain-text file."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import posixpath
from pathlib import Path
import re
from urllib.parse import unquote
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
OPF_NS = "http://www.idpf.org/2007/opf"
BLOCK_TAGS = {
    "address", "article", "blockquote", "body", "br", "dd", "div", "dl",
    "dt", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "li", "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
}
SKIP_TAGS = {"head", "script", "style", "svg", "nav"}


class XHTMLText(HTMLParser):
    """Collect readable body text while preserving block boundaries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth += 1
            return
        if tag in SKIP_TAGS:
            self.skip_depth = 1
            return
        if tag == "body":
            self.in_body = True
        if self.in_body and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if self.in_body and tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.in_body and not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(self.parts).splitlines()]
        result: list[str] = []
        for line in lines:
            if line or (result and result[-1]):
                result.append(line)
        return "\n".join(result).strip()


def epub_text(epub_path: Path) -> str:
    with ZipFile(epub_path) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(f"{{{CONTAINER_NS}}}rootfiles/{{{CONTAINER_NS}}}rootfile")
        if rootfile is None or "full-path" not in rootfile.attrib:
            raise ValueError("EPUB container does not identify its package document")

        package_path = rootfile.attrib["full-path"]
        package_dir = posixpath.dirname(package_path)
        package = ET.fromstring(archive.read(package_path))
        metadata = package.find(f"{{{OPF_NS}}}metadata")
        if metadata is None:
            raise ValueError("EPUB package has no metadata")
        dc_ns = "http://purl.org/dc/elements/1.1/"
        title = metadata.findtext(f"{{{dc_ns}}}title", default="").strip()
        creator = metadata.findtext(f"{{{dc_ns}}}creator", default="").strip()
        manifest: dict[str, str] = {}
        for item in package.findall(f"{{{OPF_NS}}}manifest/{{{OPF_NS}}}item"):
            if item.get("id") and item.get("href") and item.get("properties") != "nav":
                manifest[item.attrib["id"]] = item.attrib["href"]

        spine = package.find(f"{{{OPF_NS}}}spine")
        if spine is None:
            raise ValueError("EPUB package has no reading-order spine")

        sections: list[str] = []
        if title:
            sections.append(title + (f"\nby {creator}" if creator else ""))
        for ref in spine.findall(f"{{{OPF_NS}}}itemref"):
            if ref.get("linear", "yes") == "no":
                continue
            href = manifest.get(ref.get("idref", ""))
            if not href:
                continue
            document_path = posixpath.normpath(
                posixpath.join(package_dir, unquote(href.split("#", 1)[0]))
            )
            parser = XHTMLText()
            parser.feed(archive.read(document_path).decode("utf-8"))
            section = parser.text()
            if section:
                sections.append(section)

    if not sections:
        raise ValueError("EPUB reading order contains no extractable text")
    return "\n\n".join(sections) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", type=Path, help="source EPUB file")
    parser.add_argument("output", type=Path, help="destination UTF-8 text file")
    args = parser.parse_args()
    if not args.epub.is_file():
        parser.error(f"EPUB not found: {args.epub}")
    if args.output.exists():
        parser.error(f"Output already exists: {args.output} (remove it before replacing)")

    try:
        text = epub_text(args.epub)
    except (BadZipFile, KeyError, ET.ParseError, UnicodeDecodeError, ValueError) as error:
        parser.error(f"Could not extract EPUB text: {error}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        output.write(text)
    print(f"Wrote {len(text):,} characters to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
