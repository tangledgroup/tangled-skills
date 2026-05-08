# Configurable Constants

## Contents
- Environment Variables

## Environment Variables

Set these environment variables before sourcing or running scripts:

```bash
DDG_JSON_BASE=http://api.duckduckgo.com/   # JSON API base URL (default)
DDG_HTML_BASE=https://duckduckgo.com/html/  # HTML endpoint base URL (default)
DDG_TIMEOUT=15                              # Fetch timeout in seconds (default)
DDG_HTTP_BACKEND=scrapling                  # Force backend: scrapling (default), auto, curl, wget
DDG_OUTPUT_FORMAT=html                      # Output format: html (default), json, markdown
DDG_PRETTY_JSON=0                           # Prettify JSON via jq (1 = yes)
```
