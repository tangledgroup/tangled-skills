---
name: write-skill
description: Generate fine-grained agent skills from minimal prompts, complex requirements, URL documentation crawling, and directory analysis. Uses available agent tools to research and create spec-compliant skills.
version: "0.4.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - skill-generation
  - automation
  - meta-skill
category: tooling
---

# write-skill

A meta-skill that generates other agent skills by analyzing user requirements, crawling documentation URLs, and examining codebases. Uses your available agent tools (read, bash, web_search, etc.) to research and create complete, spec-compliant skills.

## When to Use

Load this skill when:
- User asks to "create a skill" or "generate a skill" for a specific task/domain
- User provides URLs to documentation that should be analyzed
- User wants to extract workflows from existing codebases/projects
- User describes complex requirements that should become a reusable skill
- You need to quickly bootstrap skills from minimal descriptions

## How It Works

### 0. Optional Tool Detection (Enhancement Check)

Before processing content, check for optional tools that improve conversion quality. **These tools are not required** - the skill works without them, but produces better results when available.

**Why detect these tools:**
- **pandoc/pandoc-bin**: Converts HTML/CSS to clean markdown (preserves structure, removes CSS clutter)
- **pdftotext (poppler-utils)**: Extracts text from PDFs with layout preservation
- **ghostscript (gs)**: Alternative PDF text extraction

**Detection commands:**
```bash
# Check for pandoc family (HTML → Markdown conversion)
PANDOC_CMD=""
if command -v pandoc &>/dev/null; then
  PANDOC_CMD="pandoc"
elif command -v pandoc-bin &>/dev/null; then
  PANDOC_CMD="pandoc-bin"
fi
# NOTE: If pandoc/pandoc-bin is installed, HTML content will be converted to clean markdown
# Without pandoc, basic text extraction is used (may lose formatting and structure)

# Check for poppler-utils (PDF → Text with layout)
PDFTOTEXT_AVAILABLE=false
if command -v pdftotext &>/dev/null; then
  PDFTOTEXT_AVAILABLE=true
fi
# NOTE: If poppler-utils is installed, PDFs are extracted with layout preservation
# Without it, fallback methods are used (may lose column structure)

# Check for ghostscript (PDF → Text alternative)
GHOSTSCRIPT_AVAILABLE=false
if command -v gs &>/dev/null; then
  GHOSTSCRIPT_AVAILABLE=true
fi
# NOTE: If ghostscript is installed, it serves as PDF extraction fallback
# Ghostscript's txtwrite device extracts text but does NOT preserve layout
# Without it, basic string extraction is used for PDFs
```

**Important:** Tool detection never fails the skill. All features work without these tools using fallback methods.

### 1. Tool Negotiation (First Step)

Always start by checking which tools the **agent** has available (not asking the user):

**Preferred tool hierarchy:**
1. **bash with curl** - Primary method for web fetching and file operations
2. **web_search/web_fetch tools** - If available, use as alternative
3. **read tool** - For reading local files and directories
4. **write tool** - For creating generated skill files

**Tool detection approach:**
```bash
# Test if bash/curl works (preferred)
curl --version

# Check for file access
ls -la ./target-directory
```

**Fallback strategy:**
- If web_search/web_fetch tools exist, use them
- Otherwise, **always default to bash with curl** for URL crawling
- Use bash `find`, `grep`, `cat` for directory analysis
- Never assume tool availability - test first

### 2. URL Research (If URLs Provided)

When user provides documentation URLs, perform **comprehensive domain crawling** to discover all related pages. Use **bash/curl as primary method** with systematic exploration strategies.

#### 2a. Extract Base Domain

First, extract the base domain from the provided URL to identify same-domain/subdomain URLs:

```bash
# Extract base domain (e.g., "docs.example.com" from "https://docs.example.com/guide")
BASE_URL="https://docs.example.com/guide"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
echo "Crawling domain: $BASE_DOMAIN"

# For subdomain matching (include *.example.com)
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$' || echo "$BASE_DOMAIN")
echo "Root domain pattern: *.$ROOT_DOMAIN or $BASE_DOMAIN"
```

#### 2b. Breadth-First Search (BFS) - Wide Coverage

**Use BFS when:** User wants comprehensive coverage of all documentation pages at similar depth levels.

**Strategy:** Discover all links from current level before going deeper. Good for mapping entire documentation structure.

```bash
#!/bin/bash
# BFS Crawler: Explore all pages at each depth level before going deeper

BASE_URL="https://docs.example.com"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
MAX_DEPTH=3
MAX_PAGES=50
VISITED_FILE="/tmp/bfs_visited_$$"
QUEUE_FILE="/tmp/bfs_queue_$$"
RESULTS_DIR="/tmp/bfs_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE" "$QUEUE_FILE"

# Initialize queue with base URL
echo "$BASE_URL|0" >> "$QUEUE_FILE"  # URL|depth

crawl_bfs() {
    local page_count=0
    
    while [ -s "$QUEUE_FILE" ] && [ $page_count -lt $MAX_PAGES ]; do
        # Dequeue first item (FIFO for BFS)
        current=$(head -1 "$QUEUE_FILE")
        sed -i '1d' "$QUEUE_FILE"
        
        url=$(echo "$current" | cut -d'|' -f1)
        depth=$(echo "$current" | cut -d'|' -f2)
        
        # Skip if exceeds max depth
        [ $depth -ge $MAX_DEPTH ] && continue
        
        # Skip if already visited
        grep -qF "$url" "$VISITED_FILE" 2>/dev/null && continue
        echo "$url" >> "$VISITED_FILE"
        
        # Check if URL is from same domain
        url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\.${BASE_DOMAIN#.*})"; then
            continue  # Skip external domains
        fi
        
        echo "[BFS Depth $depth] Fetching: $url"
        
        # Fetch and save content
        curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
        page_count=$((page_count + 1))
        
        # Extract same-domain links and add to queue
        curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*' | while read -r link; do
            # Convert relative to absolute URLs
            if [[ "$link" == http* ]]; then
                full_url="$link"
            elif [[ "$link" == /* ]]; then
                full_url="https://$url_domain$link"
            else
                full_url="https://$url_domain$link"
            fi
            
            # Only queue same-domain URLs not yet visited
            link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
            if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\.${BASE_DOMAIN#.*})"; then
                if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                    new_depth=$((depth + 1))
                    echo "$full_url|$new_depth" >> "$QUEUE_FILE"
                fi
            fi
        done
        
        # Rate limiting: respect robots.txt and be polite
        sleep 0.5
    done
    
    echo "BFS complete: $page_count pages crawled"
}

crawl_bfs
```

**BFS Benefits:**
- Discovers documentation structure breadth-first
- Finds all top-level sections before diving deep
- Good for understanding overall documentation organization
- Prevents getting stuck in deep rabbit holes

#### 2c. Depth-First Search (DFS) - Deep Exploration

**Use DFS when:** User wants complete coverage of specific topic branches, following related content deeply.

**Strategy:** Follow each link chain to its fullest depth before backtracking. Good for comprehensive topic coverage.

```bash
#!/bin/bash
# DFS Crawler: Explore each branch deeply before moving to next

BASE_URL="https://docs.example.com/guide"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
MAX_DEPTH=5
MAX_PAGES=100
VISITED_FILE="/tmp/dfs_visited_$$"
RESULTS_DIR="/tmp/dfs_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE"

crawl_dfs() {
    local url="$1"
    local depth="${2:-0}"
    local page_count=$(wc -l < "$VISITED_FILE")
    
    # Stop conditions
    [ $depth -ge $MAX_DEPTH ] && return
    [ $page_count -ge $MAX_PAGES ] && return
    
    # Skip if already visited
    grep -qF "$url" "$VISITED_FILE" 2>/dev/null && return
    echo "$url" >> "$VISITED_FILE"
    
    # Check if URL is from same domain
    url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
    if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\.${BASE_DOMAIN#.*})"; then
        return  # Skip external domains
    fi
    
    echo "[DFS Depth $depth] Fetching: $url"
    
    # Fetch and save content
    curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
    
    # Extract same-domain links
    local links=$(curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*')
    
    # Process links in reverse order (so first link is processed first in recursion)
    echo "$links" | tac | while read -r link; do
        # Convert relative to absolute URLs
        if [[ "$link" == http* ]]; then
            full_url="$link"
        elif [[ "$link" == /* ]]; then
            full_url="https://$url_domain$link"
        else
            full_url="https://$url_domain$link"
        fi
        
        # Only recurse into same-domain URLs
        link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\.${BASE_DOMAIN#.*})"; then
            if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                new_depth=$((depth + 1))
                crawl_dfs "$full_url" $new_depth
            fi
        fi
    done
    
    # Rate limiting
    sleep 0.3
}

crawl_dfs "$BASE_URL" 0
echo "DFS complete: $(wc -l < "$VISITED_FILE") pages crawled"
```

**DFS Benefits:**
- Follows topic threads to completion
- Captures deeply nested documentation
- Good for tutorials with sequential pages
- Ensures complete coverage of specific branches

#### 2d. Hybrid Approach (Recommended)

**Use hybrid when:** Best results - combine BFS for structure discovery with DFS for deep topic coverage.

```bash
#!/bin/bash
# HYBRID Crawler: BFS for top-level, DFS for important sections

BASE_URL="https://docs.example.com"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
VISITED_FILE="/tmp/hybrid_visited_$$"
RESULTS_DIR="/tmp/hybrid_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE"

# Phase 1: BFS to discover main sections (depth 0-2)
echo "=== Phase 1: BFS for structure discovery ==="
# ... (use BFS code from above with MAX_DEPTH=2)

# Phase 2: DFS into important sections
echo "=== Phase 2: DFS for deep coverage ==="
# Identify key sections from BFS results
for section in /guide /api /tutorial /examples; do
    if [ -f "$RESULTS_DIR/*$section*" ]; then
        echo "Deep diving into: $section"
        # ... (use DFS code from above starting from section URL)
    fi
done
```

**HTML to Markdown Conversion** (when crawling HTML pages):
```bash
# Batch convert all crawled HTML files to markdown
for html_file in "$RESULTS_DIR"/*.html; do
    basename=$(basename "$html_file" .html)
    
    if [ -n "$PANDOC_CMD" ]; then
        # Pandoc preserves structure: headings, lists, tables, code blocks
        $PANDOC_CMD -f html -t markdown --wrap=auto "$html_file" > "$RESULTS_DIR/${basename}.md" 2>/dev/null
    else
        # Fallback: basic HTML tag stripping (loses some structure)
        sed 's/<[^>]*>//g' "$html_file" | tr -s ' \n' > "$RESULTS_DIR/${basename}.txt"
    fi
done
```

**Benefits of pandoc conversion:**
- Preserves document structure (headings, lists, tables)
- Removes CSS clutter that confuses LLMs
- Handles complex layouts better than text extraction
- Converts HTML entities properly

#### 2e. Robots.txt and Rate Limiting

**Always check robots.txt before crawling:**
```bash
# Check if crawling is allowed
ROBOTS_URL="https://$BASE_DOMAIN/robots.txt"
curl -s "$ROBOTS_URL" > /tmp/robots.txt

# Parse disallow rules (simple check)
if grep -q "Disallow: /" /tmp/robots.txt; then
    echo "WARNING: Site disallows crawling entire site"
elif grep -q "Disallow:" /tmp/robots.txt; then
    echo "NOTE: Some paths are disallowed:"
    grep "Disallow:" /tmp/robots.txt
fi

# Check for crawl-delay
crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9]+' /tmp/robots.txt || echo "1")
echo "Using crawl delay: ${crawl_delay}s"
```

**Rate limiting best practices:**
```bash
# Be polite: add delays between requests
sleep 0.5  # Between BFS level requests
sleep 0.3  # Between DFS recursive calls

# Respect Crawl-delay from robots.txt
crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9.]+' /tmp/robots.txt 2>/dev/null || echo "0.5")
sleep "$crawl_delay"
```

**Alternative: web_search/web_fetch tools (if available)**
```
web_search: "service-name API documentation examples site:docs.example.com"
web_fetch: "https://docs.example.com/guide"
```

**Priority order for crawling:**
1. Try bash/curl with BFS+DFS hybrid approach (most comprehensive)
2. Fall back to web_search/web_fetch if curl fails
3. Never skip research just because specialized tools missing

### 2f. What to Extract from Crawled Content

From all crawled pages, extract:
- Command syntax and examples
- Configuration patterns (YAML, JSON, env vars)
- Authentication methods and required credentials
- Rate limits and constraints
- Error handling patterns
- Troubleshooting guides
- API endpoints and usage examples
- Best practices and recommendations

### 3. PDF Document Processing (If PDFs Encountered)

When URLs point to PDF documents or local PDFs are provided, extract text with layout preservation:

**PDF to Text workflow:**
```bash
# Download PDF (if URL provided)
curl -sL "https://example.com/documentation.pdf" > /tmp/document.pdf

# Extract text with best available method
if [ "$PDFTOTEXT_AVAILABLE" = true ]; then
  # Poppler pdftotext: BEST quality, preserves layout and columns
  # NOTE: Install poppler-utils for optimal PDF extraction: sudo apt install poppler-utils
  pdftotext -layout /tmp/document.pdf /tmp/extracted_text.txt
  cat /tmp/extracted_text.txt
  
elif [ "$GHOSTSCRIPT_AVAILABLE" = true ]; then
  # Ghostscript: BASIC text extraction (does NOT preserve layout)
  # NOTE: Install ghostscript for PDF support: sudo apt install ghostscript
  # NOTE: txtwrite device extracts text but does not maintain physical layout like pdftotext -layout
  gs -q -sDEVICE=txtwrite -o /tmp/extracted_text.txt /tmp/document.pdf 2>/dev/null
  if [ ! -s /tmp/extracted_text.txt ]; then
    # Alternative ghostscript approach: convert PDF and try pdftotext
    gs -q -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -sOutputFile=/tmp/temp.pdf /tmp/document.pdf
    if command -v pdftotext &>/dev/null; then
      # If pdftotext is available, use it with layout preservation
      pdftotext -layout /tmp/temp.pdf /tmp/extracted_text.txt 2>/dev/null
    else
      strings /tmp/document.pdf | grep -v '^$' > /tmp/extracted_text.txt
    fi
  fi
  cat /tmp/extracted_text.txt
  
elif command -v python3 &>/dev/null; then
  # Python pdfminer.six or pdf2txt1: ACCEPTABLE quality (if library installed)
  # NOTE: Install with: pip install pdfminer.six or pip install pdf2txt1
  python3 << 'PYTHON_SCRIPT' 2>/dev/null > /tmp/extracted_text.txt
try:
    from pdfminer.high_level import extract_text
    text = extract_text('/tmp/document.pdf', layout=True)
    print(text)
except ImportError:
    pass
except Exception as e:
    pass
PYTHON_SCRIPT
  if [ -s /tmp/extracted_text.txt ]; then
    cat /tmp/extracted_text.txt
  else
    # Final fallback: basic string extraction
    strings /tmp/document.pdf | grep -v '^$' > /tmp/extracted_text.txt
    cat /tmp/extracted_text.txt
  fi
else
  # Last resort: basic string extraction (POOR quality but functional)
  # NOTE: Installing poppler-utils or ghostscript greatly improves PDF processing
  strings /tmp/document.pdf | grep -v '^$' > /tmp/extracted_text.txt
  cat /tmp/extracted_text.txt
fi
```

**PDF extraction quality priority:**
1. **pdftotext (poppler-utils)** with `-layout` flag - BEST: maintains columns and formatting
2. **Python pdfminer/pdf2txt** libraries - GOOD: acceptable text extraction with layout support
3. **ghostscript** with txtwrite device - BASIC: extracts text but does NOT preserve layout/columns
4. **strings command** - POOR: basic extraction, loses all formatting

**What PDFs typically contain:**
- API reference documentation
- Technical specifications
- Whitepapers and guides
- Installation manuals
- Configuration examples

**What to extract from HTML/PDF content:**
- Command syntax and examples
- Configuration patterns (YAML, JSON, env vars)
- Authentication methods and required credentials
- Rate limits and constraints
- Error handling patterns
- Troubleshooting guides

### 4. Directory Analysis (If Paths Provided)

When user provides directories to analyze, use **bash commands as primary method**:

**Preferred: bash with find/grep/cat**
```bash
# Find all relevant files
find ./project -name "*.yaml" -o -name "*.yml" -o -name "Dockerfile" -o -name "Makefile"

# List directory structure
find ./project -type f | head -50

# Search for patterns across files
grep -r "API_KEY\|SECRET\|TOKEN" ./project --include="*.js" --include="*.py"

# Read specific files
cat ./project/package.json
cat ./project/Dockerfile
head -100 ./project/README.md

# Count file types for context
find ./project -type f -name "*.js" | wc -l
```

**Alternative: read tool (if bash unavailable)**
```
Read file: ./project/package.json
Read file: ./project/Dockerfile
Read file: ./project/.github/workflows/ci.yml
Read file: ./project/README.md
```

**What to discover:**
- Environment variables used (`grep -r "process.env\|os.environ"`)
- API endpoints and service calls
- Dependencies (package.json, requirements.txt, go.mod)
- CI/CD workflows (.github/workflows, Makefile targets)
- Configuration templates
- Helper scripts and utilities

### 5. Auto-Detection Heuristics

Apply these patterns when analyzing content:

| Pattern Found | Interpretation | Action |
|--------------|----------------|--------|
| `API_KEY`, `SECRET`, `TOKEN`, `AUTH` | Required credentials | Add to `required_environment_variables` |
| `curl https://`, `fetch('https://` | API endpoints | Document in usage examples |
| `npm install`, `pip install`, `go get` | Dependencies | Add to Setup section |
| `.yaml`, `.yml`, `.json` configs | Configuration patterns | Document in references/ |
| `.md` documentation files | Reference content | Save to `references/` directory |
| Shell scripts, Makefiles | Helper workflows | Document commands in references/ |
| Rate limit headers/docs | API constraints | Add notes to SKILL.md |

### 6. Auto-Detect Simple vs Complex Skills

Before generating, estimate the total content size. This determines whether to create a **simple skill** (single file) or **complex skill** (multi-file with references).

**Decision criteria:**
- **Simple skills**: Focused on one specific task, all content fits comfortably in SKILL.md (< 400 lines)
- **Complex skills**: Cover multiple topics/extensive knowledge areas, exceed ~400 lines when fully documented, benefit from modular organization and progressive disclosure

**Estimation approach:**
1. Count the number of distinct topics discovered during research
2. Estimate content volume based on documentation depth
3. If 3+ major topics OR estimated output > 400 lines → use complex structure
4. Otherwise → use simple structure

### 6a. Simple Skills Structure

For focused, single-task skills (< 400 lines):

```
my-skill/
└── SKILL.md          # All content inline, no references directory
```

**Template for simple skills:**

```yaml
---
name: <skill-name>
description: <what it does> + <when to use it>
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - <auto-generated-tag-1>
  - <auto-generated-tag-2>
category: <inferred-or-specified>
required_environment_variables:
  - name: <VAR_NAME>
    prompt: "<user-friendly prompt>"
    help: "<where to get it>"
    required_for: "full functionality"
---

# <Skill Name>

<Brief overview>

## When to Use

- <trigger-1>
- <trigger-2>

## Setup

<Prerequisites and installation from discovered deps>

## Usage

### <Common Operation 1>
<Steps with examples from crawled docs>

### <Common Operation 2>
<More examples>

## Troubleshooting

<Common issues from docs>
```

**Key points for simple skills:**
- No `references/` directory needed
- All content inline in SKILL.md
- Keep focused on one specific task or workflow
- No progressive disclosure required

### 6b. Complex Skills Structure

For multi-topic, extensive knowledge areas (> 400 lines):

```
my-skill/
├── SKILL.md              # Overview + navigation hub (keep under 500 lines)
└── references/
    ├── 01-core-concepts.md
    ├── 02-advanced-workflow.md
    ├── 03-api-reference.md
    └── 04-troubleshooting.md
```

**Template for complex skills:**

```yaml
---
name: <skill-name>
description: <what it does> + <when to use it>
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - <auto-generated-tag-1>
  - <auto-generated-tag-2>
category: <inferred-or-specified>
required_environment_variables:
  - name: <VAR_NAME>
    prompt: "<user-friendly prompt>"
    help: "<where to get it>"
    required_for: "full functionality"
---

# <Skill Name>

<Brief overview of what this skill does>

## When to Use

- <trigger-1>
- <trigger-2>

## Setup

<Prerequisites and installation from discovered deps>

## Quick Start

### <Common Operation 1>
<High-level steps with link to detailed reference>
See [Core Concepts](references/01-core-concepts.md) for detailed explanation.

### <Common Operation 2>
<More examples with links>
Refer to [Advanced Workflow](references/02-advanced-workflow.md) for complex scenarios.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - <high-level introduction>
- [`references/02-advanced-workflow.md`](references/02-advanced-workflow.md) - <command syntax and examples>
- [`references/03-api-reference.md`](references/03-api-reference.md) - <config patterns and options>
- [`references/04-troubleshooting.md`](references/04-troubleshooting.md) - <common issues and solutions>

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/<skill-name>/`). All paths in the generated skill should be relative to this directory.

## Troubleshooting

<Common issues from docs, or link to references/04-troubleshooting.md>
```

**Reference file naming conventions:**
- Number sequentially: `01-`, `02-`, `03-` for ordered loading
- Use hyphens and lowercase: `api-reference.md` not `API_Reference.md`
- One topic per file for fine-grained context management
- Keep each reference file focused (200-400 lines ideal)

**Use relative links in main file:**
```markdown
See [Core Concepts](references/01-core-concepts.md) for detailed explanation.
```

**Key points for complex skills:**
- SKILL.md acts as overview + navigation hub (keep under 500 lines)
- Move detailed content to `references/` files
- Use progressive disclosure: high-level in main, details in references
- Include APIs, frameworks, or tools with many use cases
- Split extensive topics across multiple reference files

**Note:** Generated skills use `references/` directory only (for complex skills). Reference files should be numbered with 2-digit prefixes (`01-`, `02-`, etc.) for consistent ordering. Do not create `scripts/` or `templates/` directories.

### 7. Validation Checklist

Before finalizing a skill, verify all items apply:

**Frontmatter (Required for All Skills):**
- [ ] `name` matches parent directory exactly (lowercase, hyphens only)
- [ ] `name` passes regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] `description` is 1-1024 characters
- [ ] `description` uses third person (no "I", "you", "we")
- [ ] `description` includes both WHAT the skill does and WHEN to use it
- [ ] No XML tags in any frontmatter values
- [ ] `license: MIT` is present (or user-specified license)
- [ ] `author: Your Name <email@example.com>` is present (unless user specified otherwise)
- [ ] `version: "0.x.0"` is present (e.g., `"0.2.0"`)
- [ ] `tags:` array includes relevant keywords (auto-generated or user-specified)
- [ ] `category:` field specifies skill category (e.g., `tooling`, `development`, `devops`)
- [ ] Compatibility lists target platforms (if applicable for hermes filtering)

**Structure (Simple Skills < 400 lines):**
- [ ] All content inline in SKILL.md (no references directory)
- [ ] Focused on one specific task or workflow
- [ ] Total line count under 400 lines
- [ ] No unnecessary sections or empty headings

**Structure (Complex Skills > 400 lines):**
- [ ] Main SKILL.md acts as overview + navigation hub (under 500 lines)
- [ ] Reference files organized in `references/` directory only (no scripts/templates)
- [ ] Reference files use numbered prefixes (`01-`, `02-`, `03-`) for consistent ordering
- [ ] Reference files use lowercase with hyphens (e.g., `api-reference.md` not `API_Reference.md`)
- [ ] All relative links resolve correctly: `[Topic](references/01-topic.md)`
- [ ] Each reference file focused on single topic (200-400 lines ideal)
- [ ] Progressive disclosure applied (high-level in SKILL.md, details in references/)
- [ ] Complex skills have clear navigation with descriptive link text

**Content Quality (Required for All Skills):**
- [ ] Third-person throughout entire document (Claude requirement)
- [ ] Actionable instructions with concrete examples
- [ ] Clear trigger conditions in "When to Use" section
- [ ] No marketing fluff or vague statements
- [ ] Code snippets are complete, valid, and tested
- [ ] Configuration patterns shown with real values (not placeholders like `<your-key>`)
- [ ] Error handling and troubleshooting included where relevant
- [ ] Dependencies and prerequisites clearly documented

**Content Processing (If URL/Directory Research Performed):**
- [ ] HTML content converted to clean markdown when pandoc available
- [ ] PDF content properly extracted using best available method (pdftotext > ghostscript > strings)
- [ ] Optional tool detection completed and logged (pandoc, poppler-utils, ghostscript)
- [ ] robots.txt checked before crawling domains
- [ ] Rate limiting applied during URL fetching (respect crawl-delay)
- [ ] Same-domain/subdomain URLs discovered using BFS/DFS strategies
- [ ] Extracted content organized into logical reference files

## Interaction Examples

### Example 1: Minimal Prompt

```
User: "Create a skill for managing Docker containers"

Agent (with write-skill):
1. Checks available tools (bash/curl preferred)
2. Uses curl to fetch: https://docs.docker.com/cli/
3. Extracts common commands and patterns
4. Generates skill with references/ containing docs
5. Validates and presents for review
```

### Example 2: With URL Research (BFS Crawling)

```
User: "Create a skill for GitHub Actions. Check https://docs.github.com/en/actions"

Agent:
1. Tests bash/curl availability (preferred)
2. Extracts base domain: docs.github.com
3. Runs BFS crawl (depth 0-2) to discover all /en/actions/* pages:
   - Discovers: /actions, /actions/quickstart, /actions/reference, etc.
   - Follows same-domain links only (*.docs.github.com)
   - Fetches ~50 related pages across documentation
4. Runs DFS on key sections (/actions/reference/) for deep coverage
5. Converts all HTML to markdown (pandoc if available)
6. Discovers required env vars (GH_TOKEN, etc.)
7. Generates complete skill with references/ containing organized docs:
   - references/01-quickstart.md
   - references/02-workflow-syntax.md  
   - references/03-api-reference.md
```

### Example 3: With Directory Analysis

```
User: "Create a skill for our deployment workflow. Analyze ./infra and ./deploy-scripts"

Agent:
1. Uses bash commands for analysis:
   - find ./infra -name "*.yaml" (discovers K8s manifests)
   - cat ./deploy-scripts/deploy.sh (discovers deployment steps)
   - grep -r "SECRET\|KEY\|TOKEN" ./infra (discovers required env vars)
2. Generates skill with:
   - references/ containing extracted documentation
   - required_environment_variables from analysis
```

### Example 4: Comprehensive Domain Crawling (Hybrid BFS+DFS)

```
User: "Create a skill for Kubernetes. Crawl all docs at https://kubernetes.io/docs/"

Agent:
1. Extracts base domain: kubernetes.io
2. Phase 1 - BFS (depth 0-2): Discovers main documentation structure
   - /docs/concepts/, /docs/tasks/, /docs/reference/, /docs/tutorials/
   - Fetches all top-level sections (~30 pages)
3. Phase 2 - DFS: Deep dives into critical sections
   - Deep crawl of /docs/reference/kubernetes-api/ (all API objects)
   - Deep crawl of /docs/tasks/ (all task guides)
   - Follows subdomains: *.kubernetes.io
4. Respects robots.txt and rate limits (crawl-delay: 1s)
5. Converts all HTML to clean markdown
6. Generates comprehensive skill with organized references:
   - references/01-core-concepts.md
   - references/02-api-reference.md (from deep API crawl)
   - references/03-common-tasks.md
   - references/04-troubleshooting.md
```

### Example 5: Complex Requirements

```
User: "I need a skill that:
- Deploys to Kubernetes using Helm
- Reads configs from values.yaml files
- Handles secrets via external-secrets operator
- Monitors deployments with Prometheus"

Agent:
1. Tests bash/curl availability (preferred)
2. Researches each component with curl:
   - curl https://helm.sh/docs/ (Helm deployment patterns)
   - curl https://external-secrets.io/ (secrets operator setup)
   - curl https://prometheus.io/docs/ (monitoring configs)
3. Generates comprehensive skill covering all requirements
4. Creates references/ with extracted documentation
```

## Output Structure

Generated skills are created in `.agents/skills/<skill-name>/`:

**Simple skills (< 400 lines):**
```
.agents/skills/<skill-name>/
└── SKILL.md              # All content inline, no references directory
```

**Complex skills (> 400 lines):**
```
.agents/skills/<skill-name>/
├── SKILL.md              # Main skill file (overview + navigation hub)
└── references/           # Extracted documentation only
    ├── 01-api-guide.md
    ├── 02-best-practices.md
    └── 03-command-reference.md
```

**Note:** Only `SKILL.md` and optionally `references/` directory are created (for complex skills). Reference files should use numbered prefixes (`01-`, `02-`, etc.) for consistent ordering. If not explicitly asked, do not create or populate `scripts/` or `templates/` directories.

## Important Notes

1. **Check agent tools first** - Test available tools (bash/curl preferred), don't ask user
2. **Prefer bash/curl** - Use bash with curl for web fetching and file operations as primary method
3. **Fallback gracefully** - If web_search/web_fetch tools exist, use them; otherwise default to curl
4. **Respect rate limits** - Add delays between URL requests
5. **Follow robots.txt** - Check before crawling sites
6. **Validate output** - Run checklist before presenting generated skill
7. **Default metadata** - Always use `license: MIT`, `author: Your Name <email@example.com>`, `version: "0.2.0"` unless user specifies otherwise
8. **Auto-detect simple vs complex** - Estimate content size; use single-file for < 400 lines, multi-file with references for > 400 lines
9. **Progressive disclosure for complex skills** - Keep SKILL.md under 500 lines as overview hub, move details to references/
10. **User review** - Always present generated skill for user approval before writing
11. **References only** - Generate skills with `references/` directory only (no scripts/templates)
12. **Numbered reference files** - Use 2-digit prefixes (`01-`, `02-`, `03-`) for consistent file ordering across systems
13. **Reference file naming** - Use lowercase with hyphens: `api-reference.md` not `API_Reference.md`
14. **Relative links in main file** - Use `[Topic](references/01-topic.md)` format
15. **Optional conversion tools** - pandoc/pandoc-bin and poppler-utils/ghostscript improve content processing but are not required
16. **Tool detection is non-blocking** - Skill always works, just better with optional tools installed
17. **Third-person descriptions** - Use third person throughout (Claude requirement)
18. **No XML in frontmatter** - Never include XML tags in YAML frontmatter values
19. **Cross-platform awareness** - Generate skills compatible with pi, opencode, claude, and hermes

## Cross-Platform Notes

Generated skills should be compatible across these platforms:

**pi:** Implements Agent Skills standard with lenient validation; warns on violations but loads skill anyway.

**opencode:** Strict validation; skills with missing `description` are not loaded. Unknown frontmatter fields ignored.

**claude:** Requires third-person descriptions; rejects XML tags in frontmatter; tests across Haiku/Sonnet/Opus models.

**hermes:** Supports platform-specific filtering, conditional activation based on tools, and environment variable passthrough for sandboxes.

## Limitations

- Tool availability depends on agent configuration (bash/curl assumed available)
- URL crawling depth limited by time/bandwidth preferences
- Directory analysis limited to files user allows reading
- Cannot execute discovered scripts, only analyze and reference them
- Generated skills should be tested before production use
- **HTML conversion quality** - Best with pandoc/pandoc-bin installed; basic text extraction used otherwise
- **PDF extraction quality** - Best with poppler-utils (pdftotext -layout) for layout preservation; ghostscript provides basic text extraction without layout; basic string extraction works without either

## Optional Tools for Enhanced Processing

This skill works everywhere, but produces better results when these optional tools are installed:

### HTML to Markdown Conversion
- **pandoc** or **pandoc-bin**: Converts crawled HTML/CSS to clean markdown
  - Install (Debian/Ubuntu): `sudo apt install pandoc`
  - Install (macOS): `brew install pandoc` or `cargo install pandoc-bin`
  - Install (Arch): `sudo pacman -S pandoc` or `yay -S pandoc-bin`
  - **Benefit**: Preserves document structure (headings, lists, tables, code blocks), removes CSS clutter

### PDF Text Extraction
- **poppler-utils** (provides `pdftotext`): Best quality PDF text extraction with layout preservation
  - Install (Debian/Ubuntu): `sudo apt install poppler-utils`
  - Install (macOS): `brew install poppler`
  - Install (Arch): `sudo pacman -S poppler`
  - **Benefit**: Maintains column layouts, tables, and document formatting
  
- **ghostscript** (`gs`): Alternative PDF processor
  - Install (Debian/Ubuntu): `sudo apt install ghostscript`
  - Install (macOS): `brew install ghostscript`
  - Install (Arch): `sudo pacman -S ghostscript`
  - **Benefit**: Basic text extraction fallback when poppler unavailable; txtwrite device extracts text but does NOT preserve layout/columns

Without these tools, the skill uses basic text extraction which may lose formatting and structure but remains functional.
