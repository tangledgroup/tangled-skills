# Tool Detection and Negotiation

This reference covers tool detection, negotiation strategies, and fallback mechanisms for the write-skill workflow.

## Optional Enhancement Tools

Before processing content, check for optional tools that improve conversion quality. **These tools are not required** - the skill works without them, but produces better results when available.

### Why Detect These Tools

- **pandoc/pandoc-bin**: Converts HTML/CSS to clean markdown (preserves structure, removes CSS clutter)
- **pdftotext (poppler-utils)**: Extracts text from PDFs with layout preservation
- **ghostscript (gs)**: Alternative PDF text extraction

### Detection Commands

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

# Log detected tools
echo "=== Tool Detection Results ==="
[ -n "$PANDOC_CMD" ] && echo "✓ HTML conversion: $PANDOC_CMD" || echo "✗ HTML conversion: not available (will use basic extraction)"
[ "$PDFTOTEXT_AVAILABLE" = true ] && echo "✓ PDF extraction: pdftotext (best quality)" || echo "✗ PDF extraction: pdftotext not available"
[ "$GHOSTSCRIPT_AVAILABLE" = true ] && echo "✓ PDF fallback: ghostscript" || echo "✗ PDF fallback: ghostscript not available"
```

**Important:** Tool detection never fails the skill. All features work without these tools using fallback methods.

## Agent Tool Negotiation

Always start by checking which tools the **agent** has available (not asking the user).

### Preferred Tool Hierarchy

1. **bash with curl** - Primary method for web fetching and file operations
2. **web_search/web_fetch tools** - If available, use as alternative
3. **read tool** - For reading local files and directories
4. **write tool** - For creating generated skill files

### Tool Detection Approach

```bash
# Test if bash/curl works (preferred)
echo "=== Testing Primary Tools ==="

if curl --version &>/dev/null; then
  echo "✓ curl available (primary web fetching)"
  CURL_AVAILABLE=true
else
  echo "✗ curl not available"
  CURL_AVAILABLE=false
fi

if command -v bash &>/dev/null; then
  echo "✓ bash available (script execution)"
  BASH_AVAILABLE=true
else
  echo "✗ bash not available"
  BASH_AVAILABLE=false
fi

# Check for file access commands
for cmd in find grep cat ls head tail wc; do
  if command -v $cmd &>/dev/null; then
    echo "✓ $cmd available"
  else
    echo "✗ $cmd not available"
  fi
done

# Check for file access
if [ -d "./target-directory" ]; then
  ls -la ./target-directory
fi
```

### Fallback Strategy

Apply this decision tree when tools are unavailable:

```bash
# Tool negotiation logic
if [ "$BASH_AVAILABLE" = true ] && [ "$CURL_AVAILABLE" = true ]; then
  # Preferred path: bash with curl
  echo "Using bash/curl for web fetching and file operations"
  USE_BASH_CURL=true
  
elif command -v web_fetch &>/dev/null; then
  # Alternative: specialized web tools
  echo "Using web_fetch tool for URL access"
  USE_WEB_TOOLS=true
  
elif command -v web_search &>/dev/null; then
  # Alternative: search-based discovery
  echo "Using web_search tool for content discovery"
  USE_WEB_SEARCH=true
  
else
  # Last resort: read tool only
  echo "WARNING: Limited to read/write tools only"
  echo "URL crawling will not be possible without curl or web tools"
  USE_READ_ONLY=true
fi
```

**Fallback rules:**
- If web_search/web_fetch tools exist, use them
- Otherwise, **always default to bash with curl** for URL crawling
- Use bash `find`, `grep`, `cat` for directory analysis
- Never assume tool availability - test first

## Installation Guide for Optional Tools

### pandoc (HTML → Markdown Conversion)

**Purpose:** Converts crawled HTML/CSS to clean markdown while preserving document structure.

**Install commands:**
```bash
# Debian/Ubuntu
sudo apt install pandoc

# macOS
brew install pandoc
# Or via cargo (often newer version)
cargo install pandoc-bin

# Arch Linux
sudo pacman -S pandoc
# Or AUR package with more formats
yay -S pandoc-bin

# Fedora
sudo dnf install pandoc

# openSUSE
sudo zypper install pandoc
```

**Benefits:**
- Preserves document structure (headings, lists, tables, code blocks)
- Removes CSS clutter that confuses LLMs
- Handles complex layouts better than text extraction
- Converts HTML entities properly

### poppler-utils (PDF Text Extraction)

**Purpose:** Best quality PDF text extraction with layout and column preservation.

**Install commands:**
```bash
# Debian/Ubuntu
sudo apt install poppler-utils

# macOS
brew install poppler

# Arch Linux
sudo pacman -S poppler

# Fedora
sudo dnf install poppler-utils

# openSUSE
sudo zypper install poppler
```

**Benefits:**
- Maintains column layouts and tables
- Preserves document formatting
- Highest quality text extraction available
- Command: `pdftotext -layout input.pdf output.txt`

### ghostscript (PDF Fallback)

**Purpose:** Alternative PDF processor when poppler unavailable.

**Install commands:**
```bash
# Debian/Ubuntu
sudo apt install ghostscript

# macOS
brew install ghostscript

# Arch Linux
sudo pacman -S ghostscript

# Fedora
sudo dnf install ghostscript

# openSUSE
sudo zypper install ghostscript
```

**Benefits:**
- Basic text extraction fallback when poppler unavailable
- Widely available on most systems
- Command: `gs -sDEVICE=txtwrite -o output.txt input.pdf`

**Note:** Ghostscript's txtwrite device extracts text but does NOT preserve layout/columns like pdftotext -layout.

## Quality Priority Matrix

| Operation | Best Tool | Good Alternative | Basic Fallback |
|-----------|-----------|------------------|----------------|
| HTML → Markdown | pandoc/pandoc-bin | python beautifulsoup4 | sed tag stripping |
| PDF → Text (layout) | pdftotext -layout | pdfminer.six (Python) | ghostscript txtwrite |
| PDF → Text (basic) | pdftotext | ghostscript | strings command |
| Web fetching | curl | web_fetch tool | wget |
| Directory scanning | find/grep | read tool loops | manual listing |

## Error Handling

When tools are unavailable, provide clear feedback:

```bash
# Graceful degradation with informative messages
if [ -z "$PANDOC_CMD" ]; then
  echo "NOTE: pandoc not installed. HTML conversion will use basic extraction."
  echo "      Install pandoc for better structure preservation:"
  echo "      - Debian/Ubuntu: sudo apt install pandoc"
  echo "      - macOS: brew install pandoc"
fi

if [ "$PDFTOTEXT_AVAILABLE" = false ] && [ "$GHOSTSCRIPT_AVAILABLE" = false ]; then
  echo "WARNING: No PDF extraction tools found. PDF processing will use basic string extraction."
  echo "         Install poppler-utils for best quality:"
  echo "         - Debian/Ubuntu: sudo apt install poppler-utils"
  echo "         - macOS: brew install poppler"
fi

# Never fail the skill, just log limitations
echo "=== Continuing with available tools ==="
```

## Summary

- **Always detect tools first** before processing content
- **Never block on missing tools** - use fallback methods
- **Log what's available** so users understand quality limitations
- **Prefer bash/curl** for web operations when available
- **Install optional tools** for best results (pandoc, poppler-utils)

See [Content Extraction](03-content-extraction.md) for how these tools are used in processing workflows.
