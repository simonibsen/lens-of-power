#!/usr/bin/env python3
"""Fetch article content from a URL using multiple extraction strategies.

Stdlib-only (no external dependencies). Tries in order:
1. JSON-LD extraction (articleBody, headline)
2. Meta tag extraction (title, og:*, description)
3. Paragraph extraction (<p> tags, filtered for substance)

Exit codes: 0 = content extracted, 1 = fetch failed, 2 = no content extracted.
"""

import json
import re
import sys
import urllib.request
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError


# ---------------------------------------------------------------------------
# HTML parsers
# ---------------------------------------------------------------------------

class TagCollector(HTMLParser):
    """Single-pass HTML parser that collects JSON-LD blocks, meta tags,
    <title>, and <p> content."""

    def __init__(self):
        super().__init__()
        self.json_ld_blocks: list[str] = []
        self.meta: dict[str, str] = {}
        self.title = ""
        self.paragraphs: list[str] = []

        self._in_script_ld = False
        self._in_title = False
        self._in_p = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_script_ld = True
            self._buf = ""
        elif tag == "title":
            self._in_title = True
            self._buf = ""
        elif tag == "p":
            self._in_p = True
            self._buf = ""
        elif tag == "meta":
            name = a.get("name", a.get("property", "")).lower()
            content = a.get("content", "")
            if name and content:
                self.meta[name] = content

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script_ld:
            self._in_script_ld = False
            self.json_ld_blocks.append(self._buf)
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = self._buf.strip()
        elif tag == "p" and self._in_p:
            self._in_p = False
            text = self._buf.strip()
            if text:
                self.paragraphs.append(text)

    def handle_data(self, data):
        if self._in_script_ld or self._in_title or self._in_p:
            self._buf += data


def strip_tags(html: str) -> str:
    """Remove HTML tags from a string."""
    return unescape(re.sub(r"<[^>]+>", "", html))


# ---------------------------------------------------------------------------
# Extraction strategies
# ---------------------------------------------------------------------------

def extract_json_ld(blocks: list[str]) -> tuple[str, str]:
    """Try to extract headline and articleBody from JSON-LD blocks.
    Returns (headline, body) — either may be empty."""
    headline = ""
    body = ""

    for raw in blocks:
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue

        # JSON-LD can be a single object or a list
        items = data if isinstance(data, list) else [data]

        for item in items:
            if not isinstance(item, dict):
                continue

            # Check @graph arrays (common wrapper)
            if "@graph" in item:
                items.extend(
                    i for i in item["@graph"] if isinstance(i, dict)
                )
                continue

            h = item.get("headline", "")
            b = item.get("articleBody", "")

            if h and not headline:
                headline = strip_tags(str(h)).strip()
            if b and not body:
                body = strip_tags(str(b)).strip()

            if headline and body:
                return headline, body

    return headline, body


def extract_meta(meta: dict[str, str], title: str) -> dict[str, str]:
    """Extract best headline and description from meta tags."""
    result: dict[str, str] = {}

    headline = (
        meta.get("og:title")
        or meta.get("twitter:title")
        or title
    )
    if headline:
        result["headline"] = headline.strip()

    description = (
        meta.get("og:description")
        or meta.get("twitter:description")
        or meta.get("description")
    )
    if description:
        result["description"] = description.strip()

    return result


def extract_paragraphs(paragraphs: list[str]) -> list[str]:
    """Filter and deduplicate paragraphs. Keep substantial ones (>40 chars)."""
    seen: set[str] = set()
    result: list[str] = []
    for p in paragraphs:
        text = strip_tags(p).strip()
        if len(text) > 40 and text not in seen:
            seen.add(text)
            result.append(text)
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fetch(url: str) -> str:
    """Fetch URL content with browser-like headers."""
    req = urllib.request.Request(url, headers={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch-article.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    # Step 1: Fetch
    try:
        html = fetch(url)
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Parse
    parser = TagCollector()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(2)

    # Step 3: Extract — try JSON-LD first
    headline, body = extract_json_ld(parser.json_ld_blocks)
    meta = extract_meta(parser.meta, parser.title)
    paragraphs = extract_paragraphs(parser.paragraphs)

    # Determine best headline
    best_headline = headline or meta.get("headline", "")

    # Determine best body
    if body:
        body_text = body
    elif paragraphs:
        body_text = "\n\n".join(paragraphs)
    else:
        body_text = ""

    # Step 4: Output
    if not best_headline and not body_text:
        description = meta.get("description", "")
        if description:
            # Last resort: output just the description
            print(f"# {url}\n")
            print(description)
            sys.exit(0)
        print("No content could be extracted.", file=sys.stderr)
        sys.exit(2)

    if best_headline:
        print(f"# {best_headline}\n")

    description = meta.get("description", "")
    if description and description != body_text[:len(description)]:
        print(f"> {description}\n")

    if body_text:
        print(body_text)

    sys.exit(0)


if __name__ == "__main__":
    main()
