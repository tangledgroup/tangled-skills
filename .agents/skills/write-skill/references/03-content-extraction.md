# Content Extraction and Processing

This reference covers content extraction workflows including PDF processing, HTML conversion, and data extraction patterns from crawled content.

## PDF Document Processing

When URLs point to PDF documents or local PDFs are provided, extract text with layout preservation using the best available method.

### Complete PDF to Text Workflow

```bash
# Download PDF (if URL provided)
curl -sL "https://example.com/documentation.pdf" > /tmp/document.pdf

# Verify download succeeded
if [ ! -s /tmp/document.pdf ]; then
  echo "ERROR: Failed to download PDF or file is empty"
  exit 1
fi

echo "PDF downloaded: $(ls -lh /tmp/document.pdf | awk '{print $5}')"

# Extract text with best available method
if [ "$PDFTOTEXT_AVAILABLE" = true ]; then
  # Poppler pdftotext: BEST quality, preserves layout and columns
  # NOTE: Install poppler-utils for optimal PDF extraction: sudo apt install poppler-utils
  echo "Using pdftotext (best quality with layout preservation)"
  pdftotext -layout /tmp/document.pdf /tmp/extracted_text.txt
  cat /tmp/extracted_text.txt
  
elif [ "$GHOSTSCRIPT_AVAILABLE" = true ]; then
  # Ghostscript: BASIC text extraction (does NOT preserve layout)
  # NOTE: Install ghostscript for PDF support: sudo apt install ghostscript
  # NOTE: txtwrite device extracts text but does not maintain physical layout like pdftotext -layout
  echo "Using ghostscript (basic text extraction, no layout preservation)"
  gs -q -sDEVICE=txtwrite -o /tmp/extracted_text.txt /tmp/document.pdf 2>/dev/null
  
  if [ ! -s /tmp/extracted_text.txt ]; then
    # Alternative ghostscript approach: convert PDF and try pdftotext
    echo "Primary extraction failed, trying PDF conversion..."
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
  echo "Trying Python PDF extraction libraries..."
  
  python3 << 'PYTHON_SCRIPT' 2>/dev/null > /tmp/extracted_text.txt
try:
    from pdfminer.high_level import extract_text
    text = extract_text('/tmp/document.pdf', layout=True)
    print(text)
    exit(0)
except ImportError:
    pass
except Exception as e:
    pass

try:
    from pdf2txt1 import PDFPageError
    from pdf2txt1 import PDFTextExtractionConsumer
    from pdf2txt1.layout import LAParams
    from pdf2txt1.pdf.Page import Page
    
    with open('/tmp/document.pdf', 'rb') as f:
        import pdf2txt1
        text = pdf2txt1.process_file(f, laparams=LAParams(layout_mode=True))
        print(text)
        exit(0)
except ImportError:
    pass
except Exception as e:
    pass
PYTHON_SCRIPT
    
  if [ -s /tmp/extracted_text.txt ]; then
    echo "Python extraction succeeded"
    cat /tmp/extracted_text.txt
  else
    echo "Python extraction failed, using basic string extraction"
    # Final fallback: basic string extraction
    strings /tmp/document.pdf | grep -v '^$' > /tmp/extracted_text.txt
    cat /tmp/extracted_text.txt
  fi
  
else
  # Last resort: basic string extraction (POOR quality but functional)
  # NOTE: Installing poppler-utils or ghostscript greatly improves PDF processing
  echo "WARNING: No PDF tools available, using basic string extraction"
  strings /tmp/document.pdf | grep -v '^$' > /tmp/extracted_text.txt
  cat /tmp/extracted_text.txt
fi

# Post-process extracted text
echo ""
echo "=== Extracted Text Statistics ==="
wc -l /tmp/extracted_text.txt
wc -w /tmp/extracted_text.txt
```

### PDF Extraction Quality Priority

| Method | Tool Required | Layout Preservation | Quality | Use Case |
|--------|--------------|---------------------|---------|----------|
| pdftotext -layout | poppler-utils | Yes (columns, tables) | BEST | API references, technical docs |
| pdfminer.six | Python library | Yes (basic layout) | GOOD | When poppler unavailable |
| pdf2txt1 | Python library | Yes (basic layout) | GOOD | Alternative Python option |
| ghostscript txtwrite | ghostscript | No | BASIC | Fallback when others fail |
| strings command | None | No | POOR | Last resort extraction |

### What PDFs Typically Contain

- API reference documentation
- Technical specifications
- Whitepapers and guides
- Installation manuals
- Configuration examples

## HTML to Markdown Conversion

When crawling HTML pages, convert to clean markdown for better LLM processing.

### Batch Conversion Script

```bash
# Batch convert all crawled HTML files to markdown
RESULTS_DIR="/tmp/crawl_results"
CONVERSION_LOG="/tmp/conversion_log.txt"

> "$CONVERSION_LOG"  # Clear log file

for html_file in "$RESULTS_DIR"/*.html; do
    [ ! -f "$html_file" ] && continue
    
    basename=$(basename "$html_file" .html)
    output_md="$RESULTS_DIR/${basename}.md"
    output_txt="$RESULTS_DIR/${basename}.txt"
    
    echo "Processing: $basename"
    
    if [ -n "$PANDOC_CMD" ]; then
        # Pandoc preserves structure: headings, lists, tables, code blocks
        if $PANDOC_CMD -f html -t markdown --wrap=auto "$html_file" > "$output_md" 2>/dev/null; then
            echo "  ✓ Converted with pandoc: $(wc -l < "$output_md") lines"
            echo "$basename: pandoc ($(wc -l < "$output_md") lines)" >> "$CONVERSION_LOG"
        else
            echo "  ✗ Pandoc failed, using fallback"
            # Fallback on error
            sed 's/<[^>]*>//g' "$html_file" | tr -s ' \n' > "$output_txt"
            echo "$basename: basic ($(wc -l < "$output_txt") lines)" >> "$CONVERSION_LOG"
        fi
    else
        # Fallback: basic HTML tag stripping (loses some structure)
        sed 's/<[^>]*>//g' "$html_file" | tr -s ' \n' > "$output_txt"
        echo "  ✓ Converted with basic extraction: $(wc -l < "$output_txt") lines"
        echo "$basename: basic ($(wc -l < "$output_txt") lines)" >> "$CONVERSION_LOG"
    fi
done

echo ""
echo "=== Conversion Summary ==="
cat "$CONVERSION_LOG"
echo ""
echo "Total files processed: $(wc -l < "$CONVERSION_LOG")"
```

### Benefits of pandoc Conversion

- Preserves document structure (headings, lists, tables)
- Removes CSS clutter that confuses LLMs
- Handles complex layouts better than text extraction
- Converts HTML entities properly
- Supports multiple input/output formats

### Advanced pandoc Options

```bash
# Basic conversion (preserves most structure)
pandoc -f html -t markdown --wrap=auto input.html > output.md

# With GFM (GitHub Flavored Markdown) for tables and better formatting
pandoc -f html -t gfm --wrap=auto input.html > output.md

# Strip comments and clean up
pandoc -f html -t markdown --strip-comments --wrap=auto input.html > output.md

# With metadata extraction
pandoc -f html -t markdown --extract-media=images input.html > output.md

# Batch with error handling
for file in *.html; do
  pandoc -f html -t markdown --wrap=auto "$file" > "${file%.html}.md" 2>/dev/null && \
    echo "✓ $file" || echo "✗ $file failed"
done
```

## What to Extract from Crawled Content

From all crawled pages (HTML or PDF), extract these key elements:

### Command Syntax and Examples

```bash
# Look for code blocks and command patterns
grep -oP '```(?:bash|sh|console|terminal)?\s*\K[^`]*' extracted_text.md | head -20

# Extract CLI commands
grep -oP '[a-z]+\s+(?:--[\w-]+[=\s][\"\']?[^\s\"\']+[\"\']?\s*)+' extracted_text.md

# Find command flags and options
grep -oP '\-\-[a-z][\w-]*' extracted_text.md | sort | uniq -c | sort -rn
```

### Configuration Patterns

```bash
# YAML configuration examples
grep -oP '```(?:yaml|yml)\s*\K[^`]*' extracted_text.md

# JSON configuration examples
grep -oP '```(?:json)\s*\K[^`]*' extracted_text.md

# Environment variables
grep -oP '(?:process\.env|os\.environ|getenv)\s*\(\s*[\"\']\K[^\s\"\']+|[A-Z]+_[A-Z0-9]+' extracted_text.md

# Config file patterns
grep -oP '\.(?:yaml|yml|json|toml|ini|cfg|conf)\b' extracted_text.md | sort | uniq -c
```

### Authentication Methods

```bash
# Look for auth-related content
grep -iE '(api.?key|secret|token|auth|credential|password|bearer)' extracted_text.md

# Extract auth header patterns
grep -oP 'Authorization:\s*\K[^\\n]+' extracted_text.md

# Find OAuth flows
grep -iE '(oauth|openid|jwt|bearer|basic.*auth)' extracted_text.md
```

### Rate Limits and Constraints

```bash
# Look for rate limit mentions
grep -iE '(rate.?limit|throttl|quota|limit.*request|per.?second?|per.?minute?|per.?hour?|per.?day?)' extracted_text.md

# Extract numeric limits
grep -oP '\d+\s*(?:requests?|calls?|ops?)\s*(?:per|/)\s*(?:second|minute|hour|day)' extracted_text.md
```

### Error Handling Patterns

```bash
# Look for error codes and messages
grep -oP '(?:Error|ERROR|error):\s*\K[^\n]+' extracted_text.md

# HTTP status codes
grep -oP '\b(?:4[0-9]{2}|5[0-9]{2})\b' extracted_text.md | sort | uniq -c

# Troubleshooting sections
grep -iE '(troubleshoot|debug|diagnose|common.?issue|known.?issue)' extracted_text.md
```

### API Endpoints and Usage Examples

```bash
# Extract URL patterns
grep -oP 'https?://[^\s"\'>]+' extracted_text.md | grep -v '^https?://(www\.)?'

# HTTP methods and paths
grep -oP '(?:GET|POST|PUT|DELETE|PATCH)\s+\K/[\w/,-]+' extracted_text.md

# cURL examples
grep -oP 'curl\s+\K[^\n]+' extracted_text.md
```

## Content Quality Assessment

After extraction, assess content quality:

```bash
# Check for sufficient content
line_count=$(wc -l < /tmp/extracted_text.txt)
if [ $line_count -lt 50 ]; then
  echo "WARNING: Extracted content is very short ($line_count lines)"
  echo "         May need manual review or alternative extraction method"
elif [ $line_count -lt 200 ]; then
  echo "NOTE: Extracted content is moderate ($line_count lines)"
else
  echo "✓ Good content volume: $line_count lines"
fi

# Check for code examples
code_blocks=$(grep -c '```' /tmp/extracted_text.txt 2>/dev/null || echo "0")
echo "Code blocks found: $code_blocks"

# Check for headings (structure indicator)
headings=$(grep -c '^#' /tmp/extracted_text.txt 2>/dev/null || echo "0")
echo "Headings found: $headings"

# Check for lists (structured content)
list_items=$(grep -c '^\s*[-*]' /tmp/extracted_text.txt 2>/dev/null || echo "0")
echo "List items found: $list_items"
```

## Post-Processing and Cleanup

```bash
# Remove duplicate lines (common in bad extractions)
sort /tmp/extracted_text.txt | uniq > /tmp/cleaned_text.txt

# Remove excessive whitespace
sed -i '/^\s*$/d' /tmp/cleaned_text.txt  # Remove blank lines
sed -i 's/[[:space:]]\+/\n/g' /tmp/cleaned_text.txt  # Normalize whitespace

# Split large files into logical sections (if needed)
if [ $(wc -l < /tmp/cleaned_text.txt) -gt 1000 ]; then
  echo "Large file detected, splitting by headings..."
  csplit -f /tmp/section_ -z /tmp/cleaned_text.txt '/^# /' '{*}' 2>/dev/null
  echo "Split into $(ls section_* 2>/dev/null | wc -l) sections"
fi

# Cleanup temporary files
rm -f /tmp/document.pdf /tmp/extracted_text.txt /tmp/temp.pdf
```

## Summary

- **PDFs**: Use pdftotext -layout (poppler-utils) for best quality with layout preservation
- **HTML**: Use pandoc for structure-preserving conversion to markdown
- **Extraction**: Focus on commands, configs, auth methods, rate limits, errors, and API endpoints
- **Quality**: Assess extracted content volume and structure before proceeding
- **Fallback**: Always have fallback methods (ghostscript, strings) when preferred tools unavailable

See [Tool Detection](01-tool-detection.md) for installation instructions for optional tools.
