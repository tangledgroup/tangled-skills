---
name: pandoc-3-9-0-2
description: Universal document converter supporting 50+ input formats (Markdown, HTML, LaTeX, docx, EPUB, Org, RST, AsciiDoc) and 60+ output formats including PDF. Provides metadata blocks, citations, math rendering, templates, Lua filters, and custom readers/writers. Use when converting between document formats, generating PDFs from markup, transforming Markdown to HTML/LaTeX/Word, processing bibliographic citations, or building document conversion pipelines.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pandoc
  - document-converter
  - markdown
  - latex
  - pdf
  - epub
  - filters
category: tooling
external_references:
  - https://pandoc.org/
  - https://github.com/jgm/pandoc/tree/3.9.0.2
---

# Pandoc 3.9.0.2

## Overview

Pandoc is a Haskell library and command-line tool for converting between markup formats. It parses input into an intermediate abstract syntax tree (AST), optionally runs filters to transform the AST, then writes to the target format. This modular design means adding a format requires only a new reader or writer.

Conversions from pandoc's Markdown aspire to be lossless; conversions from more expressive formats (LaTeX, HTML) can be lossy since pandoc's internal representation is simpler than those formats.

## When to Use

- Converting between document formats (Markdown ↔ HTML ↔ LaTeX ↔ docx ↔ EPUB)
- Generating PDFs from Markdown or other markup
- Processing documents with citations and bibliographies
- Transforming Jupyter notebooks, Org mode, or wiki markup
- Building automated document conversion pipelines
- Using Lua filters for custom AST transformations
- Creating custom readers or writers for proprietary formats

## Core Concepts

### Pipeline Architecture

```
INPUT --reader--> AST [--filter--> AST] --writer--> OUTPUT
```

Pandoc reads input into a format-agnostic AST, optionally passes it through filters, then writes to the target format. This allows any-to-any conversion without writing pairwise converters.

### Format Specification

Use `-f/--from` for input and `-t/--to` for output:

```bash
pandoc -f markdown -t html input.md -o output.html
pandoc -f latex -t docx paper.tex -o paper.docx
```

If omitted, pandoc guesses formats from file extensions. Default input is Markdown; default output is HTML (to stdout).

### Standalone vs Fragment

By default, pandoc produces a document fragment. Use `-s/--standalone` for complete documents with headers/footers:

```bash
pandoc -s input.md -o output.html    # Full HTML with <head>, <body>
pandoc input.md                       # Fragment only
```

The `-s` flag is automatic for `pdf`, `epub`, `docx`, and `odt`.

### Metadata Blocks

YAML metadata blocks provide document-level data (title, author, abstract, custom variables):

```markdown
---
title: "My Document"
author:
  - Author One
  - Author Two
date: 2024-01-15
abstract: |
  This is the abstract.
...
```

Metadata fields become template variables in standalone output. Multiple metadata blocks are merged; later values override earlier ones for duplicate keys.

### PDF Generation

Specify a `.pdf` output file. Pandoc defaults to LaTeX as the intermediate format:

```bash
pandoc input.md -o output.pdf
pandoc input.md -t context -o output.pdf       # ConTeXt engine
pandoc input.md -t html --pdf-engine=weasyprint -o output.pdf  # HTML engine
```

Requires a PDF engine (pdflatex, xelatex, lualatex, or alternatives) installed separately.

### Extensions

Enable or disable format extensions with `+EXTENSION` or `-EXTENSION`:

```bash
pandoc -f markdown+tables+footnotes -t html
pandoc -f markdown-smart -t latex    # Disable smart quote conversion
```

Common Markdown extensions: `tables`, `footnotes`, `citations`, `smart`, `yaml_metadata_block`, `auto_identifiers`, `raw_html`, `raw_tex`, `task_lists`, `attributes`.

## Usage Examples

### Basic Conversions

```bash
# Markdown to HTML
pandoc -s input.md -o output.html

# LaTeX to docx
pandoc paper.tex -o paper.docx

# HTML to Markdown
pandoc -f html -t markdown page.html -o page.md

# Multiple files concatenated
pandoc chap1.md chap2.md chap3.md -s -o book.html

# Markdown to PDF (via LaTeX)
pandoc report.md -o report.pdf
```

### With Metadata and Variables

```bash
pandoc input.md -s -V title="Custom Title" -V author="Jane Doe" -o output.html
pandoc input.md --metadata-file=meta.yaml -s -o output.html
```

### Reading from URLs

```bash
pandoc -f html -t markdown https://example.com
```

### Defaults Files

Create `defaults.yaml` to store common options:

```yaml
from: markdown
to: html
standalone: true
output-file: output.html
metadata:
  title: "Default Title"
```

```bash
pandoc -d defaults.yaml input.md
```

## Advanced Topics

**Input Formats**: Readers for Markdown variants, HTML, LaTeX, docx, EPUB, Org, RST, and more → [Input Formats](reference/01-input-formats.md)

**Output Formats**: Writers for HTML, LaTeX, PDF, docx, EPUB, slides, plain text, and more → [Output Formats](reference/02-output-formats.md)

**Command Reference**: CLI options, templates, variables, defaults files, writer-specific settings → [Command Reference](reference/03-command-reference.md)

**Pandoc's Markdown**: Extended Markdown syntax including tables, math, citations, footnotes, raw TeX/HTML → [Pandoc's Markdown](reference/04-pandoc-markdown.md)

**Filters and Lua**: JSON filters, Lua filters, custom readers/writers, AST manipulation → [Filters and Lua](reference/05-filters-and-lua.md)
