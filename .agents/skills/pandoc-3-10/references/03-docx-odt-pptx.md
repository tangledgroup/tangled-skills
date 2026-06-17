# Microsoft Office and OpenDocument Reference

Detailed reference for converting to and from Microsoft Word (docx), LibreOffice/OpenDocument (odt), and PowerPoint (pptx).

## Microsoft Word (docx)

### Basic Conversions

```bash
# Markdown → docx
pandoc -o document.docx document.md

# docx → Markdown (bi-directional)
pandoc -f docx -t markdown document.docx -o document.md

# docx → HTML
pandoc -f docx -t html document.docx -o document.html

# docx → PDF (via LaTeX)
pandoc -f docx -o document.pdf document.docx

# Multiple Markdown files → single docx
pandoc -o report.docx intro.md body.md conclusion.md
```

### Custom Styling with Reference Documents

Pandoc uses a `reference.docx` to determine styles, margins, page size, headers, and footers.

```bash
# Extract default reference docx
pandoc -o custom-reference.docx --print-default-data-file reference.docx

# Use custom reference for styling
pandoc -o styled.docx document.md --reference-doc=custom-reference.docx

# Reference from user data directory (auto-detected)
mkdir -p ~/.local/share/pandoc
cp custom-reference.docx ~/.local/share/pandoc/reference.docx
pandoc -o styled.docx document.md  # auto-uses reference.docx
```

### Paragraph Styles Recognized by Pandoc

When modifying `reference.docx`, these paragraph styles are used:

| Style name | Purpose |
|---|---|
| Normal / Body Text | Default body text |
| First Paragraph | First paragraph of a section |
| Compact | Compact body text |
| Title | Document title |
| Subtitle | Document subtitle |
| Author | Author name |
| Date | Document date |
| Abstract / AbstractTitle | Abstract section |
| Heading 1–9 | Section headings (levels 1–9) |
| Block Text | Block quotes |
| Footnote Block Text | Block quotes in footnotes |
| Source Code | Code blocks |
| Footnote Text | Footnote content |
| Definition Term / Definition | Definition lists |
| Caption / Table Caption / Image Caption | Captions |
| Figure / Captioned Figure | Figures |
| Bibliography | Bibliography section |
| TOC Heading | Table of contents heading |

### Character Styles Recognized

| Style name | Purpose |
|---|---|
| Default Paragraph Font | Default inline style |
| Verbatim Char | Inline code |
| Footnote Reference | Footnote markers |
| Hyperlink | Links |
| Section Number | Section numbering |

### Table Style

- `Table` — applied to all tables

### docx-Specific Options

```bash
# Specify reference docx
pandoc --reference-doc=template.docx -o out.docx input.md

# Extract images as links (not embedded)
pandoc -f docx -t markdown --extract-media=./images document.docx

# Preserve docx lists style
pandoc -f docx -t markdown --wrap=none document.docx
```

### docx Citations Extension

When the `citations` extension is enabled for docx input, pandoc can parse citation markup embedded in Word documents:

```bash
pandoc -f docx+citations -t latex --citeproc document.docx
```

## OpenDocument Text (odt)

### Basic Conversions

```bash
# Markdown → ODT
pandoc -o document.odt document.md

# ODT → Markdown (bi-directional)
pandoc -f odt -t markdown document.odt -o document.md

# ODT → HTML
pandoc -f odt -t html document.odt -o document.html

# ODT → PDF (via LaTeX)
pandoc -f odt -o document.pdf document.odt

# ODT → docx
pandoc -f odt -t docx document.odt -o document.docx
```

### Custom Styling with Reference Documents

```bash
# Extract default reference ODT
pandoc -o custom-reference.odt --print-default-data-file reference.odt

# Use custom reference for styling
pandoc -o styled.odt document.md --reference-doc=custom-reference.odt

# Reference from user data directory
cp custom-reference.odt ~/.local/share/pandoc/reference.odt
pandoc -o styled.odt document.md  # auto-uses reference.odt
```

### ODT-Specific Options

```bash
# Link images instead of embedding
pandoc -t odt --link-images -o document.odt input.md

# Extract media from ODT
pandoc -f odt -t markdown --extract-media=./images document.odt
```

### ODT Math Rendering

Math in ODT output is rendered using MathML when possible. For complex formulas, verify the output in LibreOffice as rendering fidelity varies.

## PowerPoint (pptx)

### Basic Conversions

```bash
# Markdown → PowerPoint
pandoc -o presentation.pptx slides.md

# PowerPoint → Markdown (bi-directional)
pandoc -f pptx -t markdown presentation.pptx -o slides.md

# HTML slides → PowerPoint
pandoc -f html -t pptx slides.html -o presentation.pptx
```

### Slide Structure

PowerPoint presentations are structured from headings:

```markdown
# Title Slide

Subtitle and author info

## Section Title

Content on this slide...

### Sub-slide

More detailed content...

---

Manual slide break (use --slide-level=0)
```

### Custom Templates

```bash
# Use a PowerPoint template
pandoc -o presentation.pptx slides.md --reference-doc=template.pptx
```

Templates must contain layouts named:
- `Title Slide`
- `Title and Content`

Microsoft PowerPoint 2013+ templates (`.pptx` or `.potx`) are known to work.

### Slide Level Control

```bash
# Headings at level 2 create slides
pandoc -o presentation.pptx slides.md --slide-level=2

# Manual slide breaks only (no automatic heading-based splits)
pandoc -o presentation.pptx slides.md --slide-level=0
```

## Common Options for Office Formats

### Extracting Media

```bash
# Extract images and embedded files
pandoc -f docx -t markdown --extract-media=./media document.docx

# Specify media directory
pandoc -f pptx -t markdown --extract-media=./slides-media presentation.pptx
```

### Top-Level Division

```bash
# Treat top-level headings as chapters (adds section breaks in docx)
pandoc -t docx --top-level-division=chapter input.md -o output.docx

# Treat as parts
pandoc -t docx --top-level-division=part input.md -o output.docx
```

### Numbered Sections

```bash
# Number section headings in docx
pandoc -t docx --number-sections input.md -o output.docx

# With custom offset (first heading = 6)
pandoc -t docx --number-sections --number-offset=5 input.md -o output.docx
```

## Conversion Quality Notes

- **docx → markdown**: Preserves headings, paragraphs, lists, tables, images, links. Complex formatting (text boxes, smart art, charts) is lost.
- **odt → markdown**: Similar to docx. MathML in ODT converts to LaTeX math delimiters.
- **pptx → markdown**: Extracts text content and structure. Speaker notes are included. Animations and transitions are lost.
- **markdown → docx/odt**: High fidelity for standard elements. Custom styles via reference documents.
- **Cross-format (docx ↔ odt)**: Structure preserved, style mapping may differ between Office suites.
