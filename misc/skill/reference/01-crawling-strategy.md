# Crawling Strategy

## Contents
- URL Crawling
- Filesystem Path Crawling
- Mixed Sources
- Custom Instructions Override
- URL Handling Tools

## URL Crawling

Recursively follow all links within the same domain and subdomains:

1. Fetch and parse the initial URL
2. Extract all relative links from the page
3. For each link, check if it resolves to the same domain or subdomain:
   - Same domain (`example.com`) → include
   - Subdomain (`api.example.com`) → include
   - Different domain (`other.com`) → skip, note as external
4. Fetch each included URL using the appropriate tool
5. Repeat for every fetched page (depth-first)
6. Track visited URLs to prevent cycles

**Domain matching:** Base domain strips `www.` prefix. Include subdomains; exclude different domains. Do not follow login pages, auth flows, or authenticated API endpoints.

**Cycle prevention:**
- Maintain a visited URL set
- Skip already-visited URLs
- Maximum depth: 5 levels from initial URL
- Maximum pages: 50 per crawl

## Filesystem Path Crawling

Recursively visit all files and directories:

1. Read the initial path (file or directory)
2. If file → analyze content directly
3. If directory → list entries
4. For each entry:
   - Directory → recurse
   - File → check analyzable extension, then read
5. Repeat for all nested directories

**Analyzable extensions:**

- **Markdown**: `.md`, `.mdx`, `.markdown`, `.mkd` — direct read (`.md` and `.mdx` are treated identically)
- **RST/Docs**: `.rst`, `.adoc` — direct read. For `.rst` sources (common in Python docs), you may need to read many files to reconstruct the hierarchical document structure before synthesizing skill content
- **Text**: `.txt` — direct read
- **HTML**: `.html`, `.htm` — `pandoc -f html -t markdown`, fallback raw
- **PDF**: `.pdf` — `pdftotext -layout` or `gs`
- **Config**: `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg` — direct read
- **Scripts**: `.sh`, `.bash`, `.py`, `.c`, `.h`, `.cpp`, `.rs`, `.go`, `.js`, `.ts` — direct read
- **Man pages**: `.1`–`.9` — direct read

**Skip rules:**
- Binary files (`.png`, `.jpg`, `.gif`, `.zip`, `.tar`, `.gz`, `.whl`, `.pyc`, `.so`, `.dll`, `.exe`)
- Hidden files/directories (`.` prefix) unless explicitly requested
- Version control dirs (`.git/`, `.svn/`, `.hg/`) always
- **Do not skip by size** — large files may be complex text documents

## Mixed Sources

When both URLs and filesystem paths are provided:
1. Process independently in parallel
2. Merge collected content, deduplicating by URL or path
3. Prefer the most specific/authoritative source on overlap
4. Note external links encountered (skipped per domain rules)

## Custom Instructions Override

Default recursive crawling can be overridden:

```
"Just analyze this one page" → skip recursion
"Only look at src/ and docs/" → apply path filters
"Follow 3 pages max" → override depth/limit
```

Always prioritize user instructions. Document any deviations from default behavior.

## URL Handling Tools

- **`.md` / `.mdx` (GitHub raw)**: `curl -sL` — parse Markdown (treat identically)
- **`.rst`**: `curl -sL` — direct read; reconstruct hierarchy from multiple files if needed
- **Man pages (`.en`)**: `curl -sL` — extract text
- **PDF (`.pdf`)**: `pdftotext -layout` or `gs` — rendered text
- **Static HTML**: `pandoc -f html -t markdown` first, fallback raw — clean Markdown
- **SPA-rendered**: note limitation — available text only
