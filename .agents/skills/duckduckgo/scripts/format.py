#!/usr/bin/env python3
"""format.py — Parse DuckDuckGo HTML search results into JSON or YAML.

Usage:
    python3 format.py --format json|yaml <html-file>

Reads HTML from a file (produced by search.sh via scrapling) and extracts
search result fields using only Python builtins (html.parser).

Output fields per result (only present if available in the HTML):
    title   — Text of the result title link (.result__a)
    url     — href of the result title link
    domain  — Text of the result URL display (.result__url)
    snippet — Plain text of the result snippet (.result__snippet), <b> tags stripped

JSON output is compact (no indentation). Missing fields are omitted entirely.
"""

import html
import json
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
        # Track which <a> tag depth we're capturing (handles nested <a>)
        self._capture_a_depth = -1

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
        self._capture_a_depth = -1

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "a":
            if "result__a" in cls:
                self.result["url"] = attrs_dict.get("href", "")
                self._capture_text = "title"
                self._text_parts = []
                self._capture_a_depth = 0
            elif "result__url" in cls:
                self._capture_text = "domain"
                self._text_parts = []
                self._capture_a_depth = 0
            elif "result__snippet" in cls:
                self._capture_text = "snippet"
                self._text_parts = []
                self._capture_a_depth = 0

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_text:
            self._flush_text()

    def handle_data(self, data):
        if self._capture_text:
            self._text_parts.append(data)


def parse_html(html_content):
    """Parse DuckDuckGo HTML and return list of result dicts.

    Scrapling isolates .web-result divs, so we split on that class to get
    individual result blocks, then parse each one independently.
    """
    results = []
    # Split into individual result blocks
    # Each block starts with 'class="... web-result ..."'
    block_pattern = re.compile(r'class="[^"]*\bweb-result\b[^"]*"')
    split_parts = block_pattern.split(html_content)

    # Reconstruct blocks: the pattern matches are in even indices after first
    # split_parts[0] is before first match, then alternating [non-match, match, non-match, ...]
    # Actually re.split keeps the delimiters when using a capturing group
    block_pattern_with_capture = re.compile(r'(class="[^"]*\bweb-result\b[^"]*")')
    parts = block_pattern_with_capture.split(html_content)

    # parts[0] is before first match
    # parts[1] is first class attr, parts[2] is content after it
    # We need to find the full <div ...> tags. Let's use a simpler approach:
    # Find all occurrences of web-result and extract the div blocks between them.

    # Simpler: use regex to find each complete .web-result div block
    # Match from <div ...web-result...> to the matching </div>
    # Since scrapling output is flat (no nested web-result), we can split by
    # looking for the start of each web-result div.

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


def format_json(results):
    """Format results as compact JSON (no indentation).

    Only includes fields that have non-empty values.
    """
    clean = []
    for r in results:
        entry = {}
        for key in ("title", "url", "domain", "snippet"):
            val = r.get(key)
            if val:
                entry[key] = val
        clean.append(entry)
    return json.dumps(clean, ensure_ascii=False, separators=(",", ":"))


def format_yaml(results):
    """Format results as simple YAML.

    Uses only builtins — no PyYAML dependency. Produces a clean list of
    mappings, one result per block.
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
    if len(sys.argv) < 3:
        print("Usage: format.py --format json|yaml <html-file>", file=sys.stderr)
        sys.exit(1)

    fmt = None
    filepath = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--format":
            if i + 1 >= len(args):
                print("Error: --format requires a value (json|yaml)", file=sys.stderr)
                sys.exit(1)
            fmt = args[i + 1]
            i += 2
        else:
            filepath = args[i]
            i += 1

    if not fmt or fmt not in ("json", "yaml"):
        print(f"Error: Invalid format '{fmt}'. Must be json or yaml.", file=sys.stderr)
        sys.exit(1)

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

    if fmt == "json":
        print(format_json(results))
    elif fmt == "yaml":
        print(format_yaml(results), end="")


if __name__ == "__main__":
    main()
