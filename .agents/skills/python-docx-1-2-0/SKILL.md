---
name: python-docx-1-2-0
description: Complete toolkit for python-docx 1.2.0, a Python library for creating, reading, and updating Microsoft Word (.docx) files. Covers document manipulation, text formatting with paragraphs and runs, table creation with merged cells, section layout and page margins, header/footer management, style system (paragraph, character, table, latent), comments, inline shapes/pictures, core properties, and all enumerations. Use when building Python programs that generate Word documents, automate report creation, fill document templates, or extract content from .docx files.
---

# python-docx 1.2.0

## Overview

`python-docx` is a Python library for creating, reading, and updating Microsoft Word 2007+ (`.docx`) files. It operates on the Office Open XML (OOXML) format, providing an object-oriented API that mirrors Word's document model: documents contain sections, paragraphs contain runs, tables contain rows and cells.

Install with `pip install python-docx`. No additional system dependencies beyond `lxml` (installed automatically).

## When to Use

- Generating Word documents programmatically from Python
- Creating reports, invoices, certificates, or letters with consistent formatting
- Filling document templates with dynamic data
- Extracting text, tables, or structural information from existing `.docx` files
- Batch processing multiple Word documents
- Adding comments, headers/footers, or modifying page layout in bulk

## Installation

```bash
pip install python-docx
```

Requires Python 3.8+ and `lxml` (auto-installed as dependency).

## Core Concepts

### Block-Level vs Inline Objects

Word documents have a two-layer hierarchy:

- **Block-level objects** flow between page margins: `Paragraph`, `Table`, inline pictures. Added via `Document.add_*()` methods.
- **Inline objects** live inside block containers: `Run` (text with character formatting). A paragraph contains one or more runs; all text in a paragraph must be within a run.

### The Style System

Styles are the primary mechanism for consistent formatting. Styles must be **defined in the document** before they can be applied — applying an undefined style is silently ignored by Word.

- **Paragraph styles** — block-level formatting (indentation, spacing, alignment)
- **Character styles** — run-level formatting (font, size, bold, color)
- **Table styles** — pre-formatted table appearances
- **Latent styles** — built-in Word styles not yet defined in the document; controlled via `document.styles.latent_styles`

The default template includes common styles: `Normal`, `Heading 1`–`9`, `List Bullet`, `List Number`, `Intense Quote`, `No Spacing`, `Title`, and many table styles.

### Length Units

Internally, python-docx uses **English Metric Units (EMU)** — 914,400 per inch. Always use the helper classes from `docx.shared`:

```python
from docx.shared import Inches, Cm, Pt, Emu
width = Inches(1.5)   # 1.5 inches
size = Pt(12)          # 12 point font
margin = Cm(2.54)      # 2.54 cm
```

### Tri-State Properties

Many formatting properties are **tri-state**: `True` (on), `False` (off), or `None` (inherit from style hierarchy). Assigning `None` removes direct formatting and restores inheritance. This applies to bold, italic, underline, alignment, indentation, and many others.

## Usage Examples

### Creating a document from scratch

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

document = Document()

# Title and heading
document.add_heading('Quarterly Report', level=0)
document.add_heading('Sales Summary', level=1)

# Paragraph with mixed formatting
p = document.add_paragraph('Revenue this quarter was ')
p.add_run('$1.2M').bold = True
p.add_run(', an increase of ')
p.add_run('15%').italic = True
p.add_run(' over last quarter.')

# Bullet list
document.add_paragraph('Product A', style='List Bullet')
document.add_paragraph('Product B', style='List Bullet')
document.add_paragraph('Product C', style='List Bullet')

# Table with data
table = document.add_table(rows=1, cols=3, style='LightShading-Accent1')
hdr = table.rows[0].cells
hdr[0].text = 'Product'
hdr[1].text = 'Revenue'
hdr[2].text = 'Growth'

for product, revenue, growth in [
    ('Product A', '$500K', '20%'),
    ('Product B', '$400K', '10%'),
    ('Product C', '$300K', '5%'),
]:
    row = table.add_row().cells
    row[0].text = product
    row[1].text = revenue
    row[2].text = growth

# Save
document.save('quarterly-report.docx')
```

### Opening and modifying an existing document

```python
from docx import Document

doc = Document('template.docx')

# Access and modify paragraphs
for para in doc.paragraphs:
    if 'PLACEHOLDER' in para.text:
        para.text = para.text.replace('PLACEHOLDER', 'Actual Value')

# Add content at the end
doc.add_paragraph('Generated on 2025-01-15', style='Normal')
doc.save('output.docx')
```

### Setting document metadata

```python
from docx import Document
from datetime import datetime

doc = Document()
props = doc.core_properties
props.title = 'Annual Report 2025'
props.author = 'Finance Department'
props.subject = 'Financial Results'
props.keywords = 'annual, report, finance, 2025'
props.category = 'Financial Report'
props.created = datetime(2025, 1, 1)
```

## Advanced Topics

**Documents**: Opening, saving (path or stream), CoreProperties metadata, Settings, traversing document body → [Documents](reference/01-documents.md)

**Text Formatting**: Paragraphs, Runs, Font properties, alignment, indentation, spacing, tab stops, hyperlinks, character formatting → [Text](reference/02-text.md)

**Tables**: Creating tables, cell access, merged cells, layout grid, omitted cells, nested tables, table styles → [Tables](reference/03-tables.md)

**Sections and Layout**: Page dimensions, orientation, margins, headers/footers, multi-section documents, zoned headers → [Sections and Layout](reference/04-sections-and-layout.md)

**Styles**: Accessing/applying styles, custom styles, style inheritance, latent styles, behavioral properties, default template styles → [Styles](reference/05-styles.md)

**Comments and Shapes**: Adding comments, rich comment content, inline shapes, pictures with sizing → [Comments and Shapes](reference/06-comments-and-shapes.md)

**API Reference**: Complete method and property listings for Document, Paragraph, Run, Table, Section, Style objects → [API Reference](reference/07-api-reference.md)

**Enumerations**: All enum classes — alignment, spacing, underline, section start, style type, orientation, color, etc. → [Enumerations](reference/08-enumerations.md)
