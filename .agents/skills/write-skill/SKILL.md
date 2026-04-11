---
name: write-skill
description: Generate fine-grained agent skills from minimal prompts, complex requirements, URL documentation crawling, and directory analysis. Uses available agent tools to research and create spec-compliant skills.
version: "0.2.0"
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

When user provides documentation URLs, crawl using **bash/curl as primary method**:

**Preferred: bash with curl**
```bash
# Fetch main page
curl -s "https://docs.example.com"

# Extract links and follow recursively (respect robots.txt)
curl -s "https://docs.example.com/guide" | grep -oP 'href="\K[^"]*'

# Handle pagination or multi-page docs
for page in 1 2 3; do
  curl -s "https://docs.example.com/api?page=$page"
done

# Check robots.txt before crawling
curl -s "https://docs.example.com/robots.txt"
```

**HTML to Markdown Conversion** (when crawling HTML pages):
```bash
# Fetch HTML content
curl -sL "https://docs.example.com/guide" > /tmp/fetched_content.html

# Convert to clean markdown if pandoc available
if [ -n "$PANDOC_CMD" ]; then
  # Pandoc preserves structure: headings, lists, tables, code blocks
  $PANDOC_CMD -f html -t markdown --wrap=auto /tmp/fetched_content.html > /tmp/converted_content.md
  # Use the clean markdown for LLM processing
  cat /tmp/converted_content.md
else
  # Fallback: basic HTML tag stripping (loses some structure)
  # NOTE: Installing pandoc or pandoc-bin improves conversion quality significantly
  sed 's/<[^>]*>//g' /tmp/fetched_content.html | tr -s ' \n' > /tmp/converted_content.txt
  cat /tmp/converted_content.txt
fi
```

**Benefits of pandoc conversion:**
- Preserves document structure (headings, lists, tables)
- Removes CSS clutter that confuses LLMs
- Handles complex layouts better than text extraction
- Converts HTML entities properly

**Alternative: web_search/web_fetch tools (if available)**
```
web_search: "service-name API documentation examples"
web_fetch: "https://docs.example.com/guide"
```

**Priority order:**
1. Try bash/curl first (most reliable)
2. Fall back to web_search/web_fetch if curl fails
3. Never skip research just because specialized tools missing

### 2b. PDF Document Processing (If PDFs Encountered)

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

### 3. Directory Analysis (If Paths Provided)

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

### 4. Auto-Detection Heuristics

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

### 5. Skill Generation Template

Generate the skill with this structure (references only, no scripts/templates):

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

## Reference Files

- `{baseDir}/references/01-<topic>-overview.md` - <high-level introduction>
- `{baseDir}/references/02-<topic>-commands.md` - <command syntax and examples>
- `{baseDir}/references/03-<topic>-configuration.md` - <config patterns and options>
- `{baseDir}/references/04-<topic>-troubleshooting.md` - <common issues and solutions>

**Note:** Use numbered prefixes (`01-`, `02-`, `03-`) to ensure consistent file ordering across different systems.

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/<skill-name>/`). All paths in the generated skill should be relative to this directory.

## Troubleshooting

<Common issues from docs>
```

**Note:** Generated skills use `references/` directory only. Reference files should be numbered with 2-digit prefixes (`01-`, `02-`, etc.) for consistent ordering. Do not create `scripts/` or `templates/` directories.

### 6. Validation Checklist

Before finalizing, verify:

- [ ] Name matches intended directory name (lowercase, hyphens only)
- [ ] Name matches regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] Description is 1-1024 characters
- [ ] Description includes both WHAT and WHEN
- [ ] `license: MIT` is present
- [ ] `author: Your Name <email@example.com>` is present (unless user specified otherwise)
- [ ] `version: "0.2.0"` is present
- [ ] No XML tags in YAML frontmatter
- [ ] Reference files organized in `references/` only (no scripts/templates)
- [ ] **Reference files use numbered prefixes** (`01-`, `02-`, `03-`) for consistent ordering
- [ ] SKILL.md body under 500 lines (split to references if longer)
- [ ] HTML content converted to clean markdown when pandoc available
- [ ] PDF content properly extracted using best available method
- [ ] Optional tool detection completed and logged

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

### Example 2: With URL Research

```
User: "Create a skill for GitHub Actions. Check https://docs.github.com/en/actions"

Agent:
1. Tests bash/curl availability (preferred)
2. Crawls with curl:
   - curl -s "https://docs.github.com/en/actions"
   - Extracts workflow examples, action syntax, CI patterns
3. Discovers required env vars (GH_TOKEN, etc.)
4. Generates complete skill with references/ containing docs
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

### Example 4: Complex Requirements

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

```
.agents/skills/<skill-name>/
├── SKILL.md              # Main skill file (generated)
└── references/           # Extracted documentation only
    ├── 01-api-guide.md
    ├── 02-best-practices.md
    └── 03-command-reference.md
```

**Note:** Only `SKILL.md` and `references/` directory are created. Reference files should use numbered prefixes (`01-`, `02-`, etc.) for consistent ordering. If not explicitly asked, do not create or populate `scripts/` or `templates/` directories.

## Important Notes

1. **Check agent tools first** - Test available tools (bash/curl preferred), don't ask user
2. **Prefer bash/curl** - Use bash with curl for web fetching and file operations as primary method
3. **Fallback gracefully** - If web_search/web_fetch tools exist, use them; otherwise default to curl
4. **Respect rate limits** - Add delays between URL requests
5. **Follow robots.txt** - Check before crawling sites
6. **Validate output** - Run checklist before presenting generated skill
7. **Default metadata** - Always use `license: MIT`, `author: Your Name <email@example.com>`, `version: "0.2.0"` unless user specifies otherwise
8. **Progressive disclosure** - Keep SKILL.md under 500 lines, move details to references/
9. **User review** - Always present generated skill for user approval before writing
10. **References only** - Generate skills with `references/` directory only (no scripts/templates)
11. **Numbered reference files** - Use 2-digit prefixes (`01-`, `02-`, `03-`) for consistent file ordering across systems
12. **Optional conversion tools** - pandoc/pandoc-bin and poppler-utils/ghostscript improve content processing but are not required
13. **Tool detection is non-blocking** - Skill always works, just better with optional tools installed

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
