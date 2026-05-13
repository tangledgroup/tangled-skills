# ☑ Plan: Write Scrapling 0.4.8 Agent Skill

**Depends On:** NONE
**Created:** 2026-05-13T00:00:00Z
**Updated:** 2026-05-13T00:00:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.4

## ☑ Phase 1 Analysis and Planning

- ☑ Task 1.1 Crawl remaining documentation sources — read `docs/fetching/dynamic.md`, `docs/spiders/advanced.md`, `docs/spiders/sessions.md`, `docs/spiders/proxy-blocking.md`, `docs/spiders/requests-responses.md`, `docs/cli/extract-commands.md`, `docs/cli/interactive-shell.md`, `docs/benchmarks.md`, `docs/tutorials/migrating_from_beautifulsoup.md`, and `docs/development/` files
- ☑ Task 1.2 Map the full documentation structure into skill sections — determine which topics belong in SKILL.md vs. reference files, based on distinct subdomains (parsing, fetching, spiders, adaptive, CLI/MCP)
- ☑ Task 1.3 Decide simple vs. complex output structure — assess whether content warrants splitting into reference files (likely complex given 5+ distinct domains)

## ☑ Phase 2 Write SKILL.md

- ☑ Task 2.1 Draft YAML header — name `scrapling-0-4-8`, description with WHAT/WHEN, tags, category `library`, external references to GitHub repo and docs URL (depends on: Task 1.2)
- ☑ Task 2.2 Write Overview section — what Scrapling is, key differentiators (adaptive scraping, anti-bot bypass, spider framework), quick-start code examples
- ☑ Task 2.3 Write When to Use section — specific trigger scenarios (HTML parsing, fetching with anti-bot bypass, building crawlers, MCP integration)
- ☑ Task 2.4 Write Installation / Setup section — pip install commands for base, fetchers, ai, shell extras; `scrapling install` for browser deps; Docker option
- ☑ Task 2.5 Write Core Concepts section — Selector/Selectors/Response classes, TextHandler, five selection methods (CSS, XPath, text, regex, filters), find_similar
- ☑ Task 2.6 Write Usage Examples section — copy-pasteable examples covering parsing, fetching with each fetcher type, basic spider
- ☑ Task 2.7 Write Advanced Topics navigation hub — link to reference files for each subdomain

## ☑ Phase 3 Write Reference Files

- ☑ Task 3.1 Write `reference/01-parsing.md` — Selector class deep dive, Selectors list operations, TextHandler methods, AttributesHandler, traversal (parent/children/siblings/below_elements), generate selectors (depends on: Task 2.5)
- ☑ Task 3.2 Write `reference/02-fetchers.md` — Fetcher (HTTP/curl_cffi), DynamicFetcher (Playwright/Chromium), StealthyFetcher (anti-bot bypass), session classes, ProxyRotator, Response object properties, argument reference tables (depends on: Task 2.6)
- ☑ Task 3.3 Write `reference/03-adaptive-scraping.md` — adaptive feature mechanics (save/match phases), auto_save/adaptive arguments, manual save/retrieve/relocate, adaptive_domain, storage system overview (depends on: Task 2.5)
- ☑ Task 3.4 Write `reference/04-spiders.md` — Spider class, start_urls, async parse callbacks, response.follow(), CrawlResult, streaming mode, pause/resume with crawldir, concurrency control, robots.txt, allowed_domains, session routing, blocked request detection, development mode cache (depends on: Task 2.6)
- ☑ Task 3.5 Write `reference/05-cli-and-mcp.md` — CLI overview (shell, extract commands, install), MCP server setup (Claude Desktop/Code/Cursor), MCP tools reference (get/fetch/stealthy_fetch/bulk variants/screenshot/session management), prompt injection protection

## ☑ Phase 4 Validate and Finalize

- ☑ Task 4.1 Run structural validator — `bash .agents/skills/skman/scripts/validate-skill.sh .agents/skills/scrapling-0-4-8` (depends on: Task 3.5)
- ☑ Task 4.2 LLM judgment review — check content accuracy against sources, no hallucinated features, consistent terminology, concise writing, single recommended approaches, proper forward-slash paths
- ☑ Task 4.3 Fix any validation errors or content issues
- ☑ Task 4.4 Regenerate README.md skills table — `bash .agents/skills/skman/scripts/gen-skills-table.sh` (depends on: Task 4.3)
