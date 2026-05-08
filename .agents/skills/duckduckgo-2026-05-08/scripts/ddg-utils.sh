#!/usr/bin/env bash
# ddg-utils.sh — DuckDuckGo search utility library
#
# Source this file to access DDG helper functions. Do not execute directly.
#
# Fetch Architecture:
#   Three HTTP backends are supported, tried in priority order:
#     1. scrapling (default) — anti-bot, JS rendering, Safari impersonation
#     2. curl            — enhanced browser headers, HTTP/2
#     3. wget            — fallback, mirrors curl behavior
#
#   ddg_http_fetch() auto-detects and caches the best available backend.
#   Use DDG_HTTP_BACKEND env var or --backend CLI flag to force a specific one.
#
# Output Formats:
#   json      — Raw JSON from the API (curl/wget only, never scrapling)
#   html      — HTML endpoint converted to markdown (pandoc for curl/wget, native for scrapling)
#   markdown  — Alias for html output (always markdown)
#
# Functions:
#   URL Encoding:
#     ddg_encode_query  <query>       — URL-encode a search query string
#
#   URL Builders:
#     ddg_json_url      <query> [opts] — Build JSON API URL
#     ddg_html_url      <query>        — Build HTML endpoint URL
#
#   Backend Fetchers (low-level, each tries one tool):
#     ddg_scrapling_fetch <url>        — Fetch via scrapling (anti-bot, JS)
#     ddg_curl_fetch      <url>        — Fetch via curl (enhanced headers)
#     ddg_wget_fetch      <url>        — Fetch via wget (fallback)
#
#   High-Level Fetch (auto-selects best backend):
#     ddg_http_fetch      <url>        — Auto-detect and fetch (scrapling > curl > wget)
#
#   HTML Filtering:
#     ddg_extract_web_results  — Extract .web-result elements from DDG HTML stdin
#
#   Format Conversion:
#     ddg_convert_html_to_md  — Convert raw HTML stdin to markdown via pandoc
#
#   Convenience Fetchers (use ddg_http_fetch internally):
#     ddg_fetch_json    <query> [opts] — Fetch JSON API response (stdout)
#     ddg_fetch_html    <query>        — Fetch HTML → markdown (pandoc or scrapling native)
#
#   jq Filter Functions (read JSON from stdin):
#     ddg_summary       — Extract heading + abstract + source
#     ddg_results       [N]            — Extract result links (default all, or top N)
#     ddg_related       [N]            — Extract related topics (default all, or top N)
#     ddg_definition    — Extract dictionary definition fields
#     ddg_full          [N]            — Full structured summary from stdin JSON
#     ddg_check         — Check if stdin JSON has abstract/results/related
#
# Constants:
#   DDG_JSON_BASE       — Base URL for JSON API (http://api.duckduckgo.com/)
#   DDG_HTML_BASE       — Base URL for HTML endpoint (https://duckduckgo.com/html/)
#   DDG_TIMEOUT         — Default fetch timeout in seconds (15)
#   DDG_HTTP_BACKEND    — Force specific backend: scrapling, curl, wget (default: auto)
#   DDG_OUTPUT_FORMAT   — Output format: json, html, markdown (default: json)
#   DDG_PRETTY_JSON     — Prettify JSON output via jq (set to 1 to enable)
#
# Error handling:
#   All functions exit with non-zero status on failure and print error to stderr.
#   ddg_fetch_* functions return raw response on stdout; check $? for success.

# ── Guard against direct execution ──────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Error: ddg-utils.sh is a library. Source it, don't execute it." >&2
  echo "Usage: source scripts/ddg-utils.sh" >&2
  exit 1
fi

# ── Constants ────────────────────────────────────────────────────────────────
# HTTP API uses http (not https) per DuckDuckGo's public endpoint
DDG_JSON_BASE="${DDG_JSON_BASE:-http://api.duckduckgo.com/}"
# HTML endpoint uses https
DDG_HTML_BASE="${DDG_HTML_BASE:-https://duckduckgo.com/html/}"
# 15-second timeout balances reliability against hanging on slow connections
DDG_TIMEOUT="${DDG_TIMEOUT:-15}"
# Safari 17.5 on macOS — matches real browser fingerprint for anti-bot evasion
DDG_USER_AGENT="${DDG_USER_AGENT:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15}"
# Backend auto-detection cache — set to scrapling/curl/wget to force
# Default is scrapling (anti-bot, native .md output); falls back via auto-detect if unavailable
DDG_HTTP_BACKEND="${DDG_HTTP_BACKEND:-scrapling}"
# Output format: json, html, markdown (default: html → markdown)
DDG_OUTPUT_FORMAT="${DDG_OUTPUT_FORMAT:-html}"
# Prettify JSON output via jq (set to 1 to enable)
DDG_PRETTY_JSON="${DDG_PRETTY_JSON:-0}"
# Internal: resolved backend after first detection
_DDG_RESOLVED_BACKEND=""

# ── URL Encoding ─────────────────────────────────────────────────────────────

# ddg_encode_query <query>
#   Percent-encode a search query string for use in URLs.
#   Uses python3 urllib.parse.quote (always available on systems with python3).
#   Outputs encoded string to stdout.
#   Exit 1 if python3 is not available.
ddg_encode_query() {
  local query="$1"
  if [[ -z "$query" ]]; then
    echo "Error: ddg_encode_query requires a non-empty query argument" >&2
    return 1
  fi

  local encoded
  encoded=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$query" 2>/dev/null)
  if [[ $? -ne 0 ]]; then
    echo "Error: python3 is required for URL encoding but is not available" >&2
    return 1
  fi
  printf '%s' "$encoded"
}

# ── URL Builders ─────────────────────────────────────────────────────────────

# ddg_json_url <query> [no_redirect=0|1] [skip_disambig=0|1] [dl=lang] [ka=w]
#   Build a DuckDuckGo JSON API URL with optional parameters.
#   Outputs the full URL to stdout.
#   Exit 1 if query is empty or encoding fails.
ddg_json_url() {
  local query="$1"
  shift

  local encoded
  encoded=$(ddg_encode_query "$query") || return 1

  local url="${DDG_JSON_BASE}?q=${encoded}&format=json"

  # Parse optional named parameters
  while [[ $# -gt 0 ]]; do
    case "$1" in
      no_redirect|no_redirect=*)
        local val="${1#no_redirect=}"
        [[ -z "$val" ]] && val="1"
        url+="&no_redirect=${val}"
        ;;
      skip_disambig|skip_disambig=*)
        local val="${1#skip_disambig=}"
        [[ -z "$val" ]] && val="1"
        url+="&skip_disambig=${val}"
        ;;
      dl=*)
        url+="&dl=${1#dl=}"
        ;;
      ka=*)
        url+="&ka=${1#ka=}"
        ;;
      *)
        echo "Error: ddg_json_url unknown option '$1'" >&2
        return 1
        ;;
    esac
    shift
  done

  printf '%s' "$url"
}

# ddg_html_url <query>
#   Build a DuckDuckGo HTML endpoint URL.
#   Outputs the full URL to stdout.
#   Exit 1 if query is empty or encoding fails.
ddg_html_url() {
  local query="$1"
  if [[ -z "$query" ]]; then
    echo "Error: ddg_html_url requires a non-empty query argument" >&2
    return 1
  fi

  local encoded
  encoded=$(ddg_encode_query "$query") || return 1

  printf '%s' "${DDG_HTML_BASE}?q=${encoded}"
}

# ── Backend Fetchers (low-level) ─────────────────────────────────────────────
# Each function fetches a URL using one specific tool.
# All return raw body to stdout and exit code from the underlying tool.
# On HTTP >= 400, prints error to stderr and returns 1.

# ddg_scrapling_fetch <url>
#   Fetch URL via scrapling (uvx) with Safari impersonation.
#   Uses .md output extension so scrapling converts HTML to clean markdown.
#   Writes to a temp file, outputs content to stdout, cleans up.
#   Best for: anti-bot evasion, JS-rendered pages, CAPTCHA-heavy sites.
#   Note: NOT suitable for raw JSON API responses (use curl/wget instead).
#   Requires: uvx (Rust-based Python package runner).
ddg_scrapling_fetch() {
  local url="$1"
  if [[ -z "$url" ]]; then
    echo "Error: ddg_scrapling_fetch requires a URL argument" >&2
    return 1
  fi

  if ! command -v uvx &>/dev/null; then
    echo "Error: scrapling backend requires 'uvx' but it is not available" >&2
    return 1
  fi

  local tmpfile
  tmpfile=$(mktemp /tmp/ddg-scrape-XXXXXX.md) || {
    echo "Error: failed to create temp file for scrapling" >&2
    return 1
  }

  # Cleanup on exit (normal, interrupt, or error)
  trap "rm -f '$tmpfile'" EXIT

  uvx 'scrapling[shell]' extract get "$url" "$tmpfile" \
    --impersonate safari \
    --ai-targeted \
    --css-selector '.web-result' >/dev/null

  local rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "Error: scrapling fetch failed (exit code $rc) for URL: $url" >&2
    return 1
  fi

  if [[ ! -s "$tmpfile" ]]; then
    echo "Error: scrapling returned empty content for URL: $url" >&2
    return 1
  fi

  cat "$tmpfile"
  rm -f "$tmpfile"
  trap - EXIT
}

# ddg_curl_fetch <url>
#   Fetch URL via curl with enhanced browser-like headers.
#   Uses HTTP/2, Safari 17.5 UA, full Sec-Fetch-* headers, and Accept-Encoding.
#   Best for: fast, reliable fetching when scrapling is unavailable.
#   Requires: curl (with HTTP/2 support).
ddg_curl_fetch() {
  local url="$1"
  if [[ -z "$url" ]]; then
    echo "Error: ddg_curl_fetch requires a URL argument" >&2
    return 1
  fi

  local response
  response=$(curl -sL \
    --compressed \
    --http2 \
    --max-time "$DDG_TIMEOUT" \
    -A "$DDG_USER_AGENT" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: en-US,en;q=0.9" \
    -H "Accept-Encoding: gzip, deflate, br" \
    -H "Connection: keep-alive" \
    -H "Upgrade-Insecure-Requests: 1" \
    -H "Sec-Fetch-Dest: document" \
    -H "Sec-Fetch-Mode: navigate" \
    -H "Sec-Fetch-Site: none" \
    -H "Sec-Fetch-User: ?1" \
    -H "Priority: u=0, i" \
    -w '\n%{http_code}' \
    "$url" 2>/dev/null)

  local rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "Error: curl fetch failed (exit code $rc) for URL: $url" >&2
    return 1
  fi

  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')

  if [[ "$http_code" -ge 400 ]] 2>/dev/null; then
    echo "Error: HTTP ${http_code} from curl for URL: $url" >&2
    return 1
  fi

  printf '%s' "$body"
}

# ddg_wget_fetch <url>
#   Fetch URL via wget, mirroring curl's behavior as closely as possible.
#   Uses same UA and key headers for consistency across backends.
#   Best for: systems where curl is unavailable (rare fallback).
#   Requires: wget.
ddg_wget_fetch() {
  local url="$1"
  if [[ -z "$url" ]]; then
    echo "Error: ddg_wget_fetch requires a URL argument" >&2
    return 1
  fi

  local tmpfile
  tmpfile=$(mktemp /tmp/ddg-wget-XXXXXX) || {
    echo "Error: failed to create temp file for wget" >&2
    return 1
  }

  # Cleanup on exit
  trap "rm -f '$tmpfile'" EXIT

  # wget mirrors curl behavior:
  #   -q              = quiet (like curl -s)
  #   -O $tmpfile     = write to temp file (like curl's stdout capture)
  #   --user-agent    = same Safari UA as curl backend
  #   --header        = mirror curl's Accept, Accept-Language, Connection headers
  #                     (wget does not support Sec-Fetch-* or Priority headers)
  #   --timeout       = connection timeout (mirrors curl --max-time)
  #   --tries=1       = single attempt, no retries (mirrors curl default)
  #   --no-check-certificate = follow redirects like curl -L
  wget -q \
    -O "$tmpfile" \
    --user-agent="$DDG_USER_AGENT" \
    --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    --header="Accept-Language: en-US,en;q=0.9" \
    --header="Connection: keep-alive" \
    --timeout="$DDG_TIMEOUT" \
    --tries=1 \
    "$url" 2>/dev/null

  local rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "Error: wget fetch failed (exit code $rc) for URL: $url" >&2
    rm -f "$tmpfile"
    trap - EXIT
    return 1
  fi

  if [[ ! -s "$tmpfile" ]]; then
    echo "Error: wget returned empty content for URL: $url" >&2
    rm -f "$tmpfile"
    trap - EXIT
    return 1
  fi

  cat "$tmpfile"
  rm -f "$tmpfile"
  trap - EXIT
}

# ── High-Level Fetch (auto-selects best backend) ─────────────────────────────

# _ddg_resolve_backend
#   Detect the best available fetch backend and cache it in _DDG_RESOLVED_BACKEND.
#   Priority order: scrapling > curl > wget
#   If DDG_HTTP_BACKEND is set to a specific value, use that (or error if unavailable).
_ddg_resolve_backend() {
  # Already resolved — skip
  if [[ -n "$_DDG_RESOLVED_BACKEND" ]]; then
    return 0
  fi

  # User forced a specific backend
  if [[ "$DDG_HTTP_BACKEND" != "auto" ]]; then
    case "$DDG_HTTP_BACKEND" in
      scrapling)
        if command -v uvx &>/dev/null; then
          _DDG_RESOLVED_BACKEND="scrapling"
        else
          echo "Error: forced backend 'scrapling' requires 'uvx' which is not available" >&2
          return 1
        fi
        ;;
      curl)
        if command -v curl &>/dev/null; then
          _DDG_RESOLVED_BACKEND="curl"
        else
          echo "Error: forced backend 'curl' is not available" >&2
          return 1
        fi
        ;;
      wget)
        if command -v wget &>/dev/null; then
          _DDG_RESOLVED_BACKEND="wget"
        else
          echo "Error: forced backend 'wget' is not available" >&2
          return 1
        fi
        ;;
      *)
        echo "Error: unknown backend '$DDG_HTTP_BACKEND' (valid: scrapling, curl, wget, auto)" >&2
        return 1
        ;;
    esac
    echo "Info: using forced backend '${_DDG_RESOLVED_BACKEND}'" >&2
    return 0
  fi

  # Auto-detect: try in priority order (scrapling > curl > wget)
  if command -v uvx &>/dev/null; then
    _DDG_RESOLVED_BACKEND="scrapling"
  elif command -v curl &>/dev/null; then
    _DDG_RESOLVED_BACKEND="curl"
  elif command -v wget &>/dev/null; then
    _DDG_RESOLVED_BACKEND="wget"
  else
    echo "Error: no fetch backend available (need curl, wget, or uvx for scrapling)" >&2
    return 1
  fi

  echo "Info: auto-detected backend '${_DDG_RESOLVED_BACKEND}'" >&2
}

# ddg_http_fetch <url>
#   Fetch a URL using the best available backend.
#   Auto-detects on first call: scrapling > curl > wget
#   Cache result in _DDG_RESOLVED_BACKEND for subsequent calls.
#   Set DDG_HTTP_BACKEND env var to force a specific backend.
#   Outputs raw body to stdout.
#   Exit 1 if no backend is available or fetch fails.
ddg_http_fetch() {
  local url="$1"
  if [[ -z "$url" ]]; then
    echo "Error: ddg_http_fetch requires a URL argument" >&2
    return 1
  fi

  _ddg_resolve_backend || return 1

  case "$_DDG_RESOLVED_BACKEND" in
    scrapling) ddg_scrapling_fetch "$url" ;;
    curl)      ddg_curl_fetch "$url" ;;
    wget)      ddg_wget_fetch "$url" ;;
  esac
}

# ── HTML Filtering ───────────────────────────────────────────────────────────

# ddg_extract_web_results
#   Extract only .web-result div elements from DuckDuckGo HTML search results.
#   Reads raw HTML from stdin, outputs filtered HTML to stdout containing only
#   the search result blocks (titles, URLs, snippets). Strips nav, footer, ads,
#   and other page chrome that would add noise when converting to markdown.
#   Uses python3 html.parser (stdlib, no extra deps) for robust parsing of
#   potentially malformed HTML from the browser.
#   Streams directly (no bash variable capture) to handle large HTML pages.
#   Exit 1 if python3 is unavailable or extraction yields zero results.
ddg_extract_web_results() {
  if ! command -v python3 &>/dev/null; then
    echo "Error: ddg_extract_web_results requires 'python3' but it is not available" >&2
    return 1
  fi

  # python3 html.parser extracts <div class="...web-result ..."> blocks from stdin.
  # It handles malformed HTML gracefully (unclosed tags, nested attributes).
  # Streams directly to stdout — no intermediate bash variable needed.
  python3 -c '
import sys
from html.parser import HTMLParser

class _WebResultExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._depth = 0
        self._capturing = False
        self._count = 0
        self._buf = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if "web-result" in cls.split() and self._depth == 0:
            self._capturing = True
            self._buf = []
        if self._capturing:
            self._depth += 1
            attr_str = " ".join(f"{k}=\"{v}\"" for k, v in attrs if v is not None)
            self._buf.append(f"<{tag} {attr_str}>")

    def handle_endtag(self, tag):
        if self._capturing:
            self._depth -= 1
            self._buf.append(f"</{tag}>")
            if self._depth == 0:
                self._capturing = False
                self._count += 1
                sys.stdout.write("".join(self._buf))
                sys.stdout.write("\n")

    def handle_data(self, data):
        if self._capturing:
            self._buf.append(data)

    def handle_startendtag(self, tag, attrs):
        if self._capturing:
            attr_str = " ".join(f"{k}=\"{v}\"" for k, v in attrs if v is not None)
            self._buf.append(f"<{tag} {attr_str}/>")

html = sys.stdin.read()
p = _WebResultExtractor()
p.feed(html)
if p._count == 0:
    print("Warning: no .web-result elements found in HTML", file=sys.stderr)
    sys.exit(1)
'
}

# ── Format Conversion ────────────────────────────────────────────────────────

# ddg_convert_html_to_md
#   Convert raw HTML from stdin to markdown via pandoc.
#   If pandoc is unavailable, returns raw HTML with a warning on stderr.
#   Outputs markdown to stdout.
ddg_convert_html_to_md() {
  if command -v pandoc &>/dev/null; then
    pandoc -f html -t markdown 2>/dev/null
  else
    echo "Warning: pandoc not found, returning raw HTML instead of markdown" >&2
    cat
  fi
}

# ── Convenience Fetchers (use ddg_http_fetch internally) ─────────────────────

# ddg_fetch_json <query> [opts...]
#   Fetch DuckDuckGo JSON API response for the given query.
#   Passes optional arguments through to ddg_json_url.
#   Uses curl or wget only (scrapling transforms JSON and breaks parsing).
#   Auto-detects: curl > wget. Set DDG_HTTP_BACKEND=curl or wget to force.
#   Outputs raw JSON to stdout on success.
#   Exit 1 if fetch fails (network error, timeout, HTTP error).
ddg_fetch_json() {
  local query="$1"
  shift

  local url
  url=$(ddg_json_url "$query" "$@") || return 1

  # JSON API requires raw bytes — scrapling transforms content and breaks JSON.
  # Force curl or wget for JSON fetching.
  if [[ "${DDG_HTTP_BACKEND:-auto}" == "scrapling" ]]; then
    echo "Info: JSON API requires raw response, falling back from scrapling to curl/wget" >&2
  fi

  local json
  if command -v curl &>/dev/null; then
    json=$(ddg_curl_fetch "$url") || return 1
  elif command -v wget &>/dev/null; then
    json=$(ddg_wget_fetch "$url") || return 1
  else
    echo "Error: no fetch backend available for JSON API (need curl or wget)" >&2
    return 1
  fi

  printf '%s' "$json"
}

# ddg_fetch_html <query>
#   Fetch DuckDuckGo HTML endpoint and convert to markdown.
#   Uses ddg_http_fetch() which auto-selects the best backend (scrapling > curl > wget).
#   Output is always markdown:
#     - scrapling: native .md output via --ai-targeted + --css-selector '.web-result'
#     - curl/wget: raw HTML → extract .web-result elements → pandoc → markdown
#   If pandoc is unavailable and backend is curl/wget, returns raw HTML with warning.
#   Exit 1 if fetch fails (network error, timeout, HTTP error).
ddg_fetch_html() {
  local query="$1"
  if [[ -z "$query" ]]; then
    echo "Error: ddg_fetch_html requires a non-empty query argument" >&2
    return 1
  fi

  local url
  url=$(ddg_html_url "$query") || return 1

  # Resolve backend to know whether we need pandoc conversion
  _ddg_resolve_backend || return 1

  case "$_DDG_RESOLVED_BACKEND" in
    scrapling)
      # Scrapling natively outputs markdown (.md extension + --ai-targeted)
      ddg_scrapling_fetch "$url"
      ;;
    curl)
      # Fetch raw HTML → extract .web-result elements → pandoc → markdown
      local html
      html=$(ddg_curl_fetch "$url") || return 1
      echo "$html" | ddg_extract_web_results | ddg_convert_html_to_md
      ;;
    wget)
      # Fetch raw HTML → extract .web-result elements → pandoc → markdown
      local html
      html=$(ddg_wget_fetch "$url") || return 1
      echo "$html" | ddg_extract_web_results | ddg_convert_html_to_md
      ;;
  esac
}

# ── jq Filter Functions (read JSON from stdin) ───────────────────────────────

# ddg_summary
#   Read JSON API response from stdin, output heading + abstract + source.
#   Outputs compact JSON object to stdout.
ddg_summary() {
  jq -c '{heading: .Heading, abstract: .AbstractText, source: .AbstractSource, url: .AbstractURL}'
}

# ddg_results [N]
#   Read JSON API response from stdin, output result links array.
#   Optional N limits to top N results (default: all).
#   Outputs compact JSON array to stdout.
ddg_results() {
  local limit="${1:-}"
  if [[ -n "$limit" ]]; then
    jq -c "[.Results[:${limit}][]? | {text: .Text, url: .FirstURL}]"
  else
    jq -c '[.Results[]? | {text: .Text, url: .FirstURL}]'
  fi
}

# ddg_related [N]
#   Read JSON API response from stdin, output related topics array.
#   Optional N limits to top N topics (default: 5).
#   Outputs compact JSON array to stdout.
ddg_related() {
  local limit="${1:-5}"
  jq -c "[.RelatedTopics[:${limit}][]? | {text: .Text, url: .FirstURL}]"
}

# ddg_definition
#   Read JSON API response from stdin, output dictionary definition fields.
#   Outputs compact JSON object to stdout.
ddg_definition() {
  jq -c '{word: .Heading, definition: .Definition, source: .DefinitionSource, url: .DefinitionURL}'
}

# ddg_full [N]
#   Read JSON API response from stdin, output full structured summary.
#   Optional N limits related topics (default: 5).
#   Outputs pretty-printed JSON object to stdout.
ddg_full() {
  local limit="${1:-5}"
  jq "{
    heading: .Heading,
    abstract: .AbstractText,
    source: .AbstractSource,
    url: .AbstractURL,
    entity: .Entity,
    official_site: .OfficialWebsite,
    results: [.Results[]? | {text: .Text, url: .FirstURL}],
    related: [.RelatedTopics[:${limit}][]? | {text: .Text, url: .FirstURL}]
  }"
}

# ddg_check
#   Read JSON API response from stdin, output existence checks.
#   Outputs compact JSON with boolean fields to stdout.
ddg_check() {
  jq -c '{has_abstract: (.AbstractText | length > 0), has_results: (.Results | length > 0), has_related: (.RelatedTopics | length > 0), type: .Type}'
}
