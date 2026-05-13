# ☑ Plan: DuckDuckGo Search Skill

**Depends On:** NONE
**Created:** 2026-05-13T21:19:00Z
**Updated:** 2026-05-13T21:19:00Z
**Current Phase:** ☑ Phase 3
**Current Task:** ☑ Task 3.3

## ☑ Phase 1 Planning

- ☑ Task 1.1 Define skill scope and output structure
  - Simple skill (single SKILL.md) — single domain, no natural subtopic split
  - Scripts explicitly requested: `scripts/search.sh` and `scripts/format.py`
  - Output formats: markdown (default), html, json, yaml — all from HTML API via scrapling

- ☑ Task 1.2 Design search.sh interface
  - Accepts query string and optional format flag (`--format md|html|json|yaml`)
  - Calls `uvx 'scrapling[shell]' extract get` against DuckDuckGo HTML endpoint
  - Pipes/scatters output to `format.py` for json/yaml transforms
  - For markdown: scrapling's `--ai-targeted` already produces clean markdown
  - For html: pass through raw HTML from scrapling
  - Temp file cleanup handled by search.sh

- ☑ Task 1.3 Design format.py interface
  - Reads HTML from stdin or temp file path argument
  - Accepts `--format json|yaml` flag
  - Parses HTML using builtins only (`html.parser`, no BeautifulSoup)
  - Extracts fields per result: title, url, snippet, domain (from available HTML structure)
  - Outputs compact JSON (no indentation) or YAML
  - Fields from DDG JSON API studied but only returned if available in HTML parse

## ☑ Phase 2 Implementation

- ☑ Task 2.1 Write scripts/search.sh (depends on: Task 1.2)
  - Bash script using `uvx 'scrapling[shell]' extract get`
  - URL encode query, construct DuckDuckGo HTML endpoint URL
  - Default: output markdown via scrapling's `--ai-targeted` flag to stdout
  - HTML mode: save to temp file, pass through raw
  - JSON/YAML mode: save HTML to temp file, pipe to format.py
  - Clean up temp files on exit (trap)

- ☑ Task 2.2 Write scripts/format.py (depends on: Task 1.3 , Task 2.1)
  - Python script using only builtins: `html.parser`, `json`, `sys`, `urllib.parse`
  - Parse HTML with `HTMLParser` to extract `.web-result` blocks
  - Extract per result: title (`.result__a`), url (href), snippet (`.result__snippet` text)
  - Output JSON: compact single-line array of objects, omit missing fields
  - Output YAML: simple key-value format per result

- ☑ Task 2.3 Write SKILL.md (depends on: Task 2.1 , Task 2.2)
  - YAML header with proper name, description, tags
  - Overview, When to Use, Usage Examples sections
  - Document all four output modes with copy-pasteable examples
  - Script execution intent explicit: "Run search.sh" not "see for reference"

## ☑ Phase 3 Validation

- ☑ Task 3.1 Run structural validator (depends on: Task 2.3)
  - `bash scripts/validate-skill.sh .agents/skills/duckduckgo`

- ☑ Task 3.2 LLM judgment review (depends on: Task 3.1)
  - Check content accuracy, no hallucination
  - Verify script paths use forward slashes
  - Confirm execution intent is clear
  - Check YAML header validity

- ☑ Task 3.3 Regenerate README.md skills table (depends on: Task 3.2)
  - `bash scripts/gen-skills-table.sh`
