#!/usr/bin/env python3
"""format.py — Parse DuckDuckGo HTML search results into raw YAML.

Usage:
    python3 format.py [--limit N] <html-file>

Reads HTML from a file (produced by search.sh via scrapling) and extracts
search result fields using only Python builtins (html.parser).

Outputs YAML to stdout. Output is never summarized or transformed —
exact extracted data is written as YAML.

Output fields per result (only present if available in the HTML):
    title   — Text of the result title link (.result__a)
    url     — href of the result title link
    domain  — Text of the result URL display (.result__url)
    snippet — Plain text of the result snippet (.result__snippet), <b> tags stripped
"""

import html
import re
import sys
from html.parser import HTMLParser


class _SingleResultParser(HTMLParser):
    """Parse a single DuckDuckGo result block (one .web-result div).

    Extracts title, url, domain, and snippet from the HTML structure.
    Designed to handle inner tags like <b> within captured elements.
    """

    def __init__(self):
        super().__init__()
        self.result = {}
        self._capture_text = None
        self._text_parts = []

    def _flush_text(self):
        """Flush accumulated text into the current result field."""
        if self._capture_text:
            text = html.unescape("".join(self._text_parts).strip())
            # Strip * markers that scrapling's --ai-targeted converts <b> to
            if self._capture_text == "snippet":
                text = re.sub(r"\*+", "", text)
            self.result[self._capture_text] = text
        self._capture_text = None
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "a":
            if "result__a" in cls:
                self.result["url"] = attrs_dict.get("href", "")
                self._capture_text = "title"
                self._text_parts = []
            elif "result__url" in cls:
                self._capture_text = "domain"
                self._text_parts = []
            elif "result__snippet" in cls:
                self._capture_text = "snippet"
                self._text_parts = []

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_text:
            self._flush_text()

    def handle_data(self, data):
        if self._capture_text:
            self._text_parts.append(data)


def parse_html(html_content):
    """Parse DuckDuckGo HTML and return list of result dicts.

    Scrapling isolates .web-result divs, so we find each complete
    .web-result div block and parse it independently.
    """
    results = []

    # Find all start positions of .web-result divs
    starts = []
    for m in re.finditer(r'<div[^>]*\bclass="[^"]*\bweb-result\b', html_content):
        starts.append(m.start())

    if not starts:
        return results

    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(html_content)
        block_html = html_content[start:end]

        parser = _SingleResultParser()
        try:
            parser.feed(block_html)
        except Exception:
            continue

        if parser.result.get("title") or parser.result.get("url"):
            results.append(parser.result)

    return results


def format_yaml(results):
    """Format results as simple YAML using only builtins.

    Produces a clean list of mappings, one result per block.
    Output is exact data — no summarization or transformation.
    """
    lines = []
    for i, r in enumerate(results):
        if i > 0:
            lines.append("")
        lines.append(f"- title: {_yaml_scalar(r.get('title', ''))}")
        lines.append(f"  url: {_yaml_scalar(r.get('url', ''))}")
        domain = r.get("domain", "")
        snippet = r.get("snippet", "")
        if domain:
            lines.append(f"  domain: {_yaml_scalar(domain)}")
        if snippet:
            lines.append(f"  snippet: {_yaml_multiline(snippet)}")
    return "\n".join(lines) + "\n"


def _yaml_scalar(value):
    """Escape a scalar value for YAML output."""
    if not value:
        return "''"
    # Use single quotes and escape internal single quotes by doubling them
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _yaml_multiline(value):
    """Format a potentially long string as a YAML literal block."""
    if not value:
        return "''"
    # If it's short and has no newlines, inline it
    if len(value) < 80 and "\n" not in value:
        return _yaml_scalar(value)
    # Use literal block scalar for longer text
    indented = value.replace("\n", "\n  ")
    return f"|\n  {indented}"


def main():
    if len(sys.argv) < 2:
        print("Usage: format.py [--limit N] <html-file>", file=sys.stderr)
        sys.exit(1)

    limit = None
    filepath = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--limit":
            if i + 1 >= len(args):
                print("Error: --limit requires a numeric value", file=sys.stderr)
                sys.exit(1)
            try:
                limit = int(args[i + 1])
            except ValueError:
                print("Error: --limit must be a positive integer", file=sys.stderr)
                sys.exit(1)
            i += 2
        else:
            filepath = args[i]
            i += 1

    if not filepath:
        print("Error: No HTML file path provided.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    results = parse_html(html_content)

    # Apply limit if specified
    if limit is not None:
        results = results[:limit]

    print(format_yaml(results), end="")


if __name__ == "__main__":
    main()
