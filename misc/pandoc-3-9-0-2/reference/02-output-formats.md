# Output Formats

## Contents
- Web Formats
- TeX and Typesetting
- Office and Word Processing
- E-book Formats
- Plain Text and Terminal
- Slide Shows
- Wiki Formats
- Documentation Formats
- XML and Data Formats
- PDF Generation
- Bibliography Outputs

## Web Formats

- **`html`** / **`html5`** — HTML5/XHTML polyglot markup. Default output when writing to stdout. Supports embedded CSS, math rendering (MathJax/KaTeX), syntax highlighting, and table of contents.
- **`html4`** — XHTML 1.0 Transitional.
- **`chunkedhtml`** — Zip archive of multiple linked HTML files (for large documents split into sections).
- **`ansi`** — Plain text with ANSI escape codes for terminal viewing (colors, bold).

## TeX and Typesetting

- **`latex`** — LaTeX output. Supports full document structure including sections, lists, tables, math, figures, footnotes, and citations. Uses default template with configurable packages.
- **`beamer`** — LaTeX Beamer slide show format. Heading levels map to frames/subsections/sections.
- **`context`** — ConTeXt typesetting system output.
- **`ms`** — roff ms macro package (UNIX manual formatting).
- **`man`** — roff man page format. Extracts title and section from pandoc title block.
- **`texinfo`** — GNU Texinfo format (for info pages and manuals).
- **`typst`** — Typst typesetting language output. Extensions: `citations`.

## Office and Word Processing

- **`docx`** — Microsoft Word .docx. Preserves document structure, headings, lists, tables, images, and code blocks. Uses `reference.docx` from data directory for styling. Not directed to stdout unless forced with `-o -`.
- **`odt`** — OpenDocument Text (LibreOffice). Similar to docx. Uses `reference.odt` for styling.
- **`pptx`** — PowerPoint slide show. Heading levels map to slides/sections. Uses `reference.pptx` for styling.

## E-book Formats

- **`epub`** / **`epub3`** — EPUB v3 e-book. Includes cover image, navigation, and embedded CSS. Supports metadata fields: `cover`, `lang`, `rights`, `source`, `creator`, `contributor`.
- **`epub2`** — EPUB v2 (older standard).
- **`fb2`** — FictionBook2 e-book format.

## Plain Text and Terminal

- **`plain`** — Plain text with no formatting. Strips all markup, preserves paragraph structure.
- **`markdown`** — Pandoc's Markdown output (round-trip friendly from pandoc Markdown input).
- **`commonmark`** — Strict CommonMark output.
- **`commonmark_x`** — CommonMark with extensions.
- **`gfm`** — GitHub-Flavored Markdown output.
- **`markdown_mmd`** — MultiMarkdown output.
- **`markdown_phpextra`** — PHP Markdown Extra output.
- **`markdown_strict`** — Original unextended Markdown.
- **`markua`** — Markua markup (Leanpub).

## Slide Shows

Pandoc supports multiple HTML-based and LaTeX-based slide formats. Slide structure is determined by heading levels: top-level headings create slides, second-level create sub-slides.

### HTML Slide Formats

| Format | Framework |
|--------|-----------|
| `slideous` | Slideous (HTML + JS) |
| `slidy` | W3C Slidy |
| `dzslides` | DZSlides (HTML5) |
| `revealjs` | reveal.js (modern, feature-rich) |
| `s5` | S5 (classic) |

### LaTeX Slide Formats

- **`beamer`** — LaTeX Beamer. Supports slide attributes: `{.fragile}`, `{.allowframebreaks}`, `frameoptions="squeeze,shrink"`.

### Slide Control in Markdown

```markdown
# Slide Title

Content here.

^ ^   # New slide (pause/overlay)
```

Use horizontal rules or level-1 headings to create new slides. Use `^ ^` for pauses within a slide.

## Wiki Formats

- **`mediawiki`** — MediaWiki markup.
- **`dokuwiki`** — DokuWiki markup.
- **`jira`** — Jira/Confluence wiki markup.
- **`xwiki`** — XWiki markup.
- **`zimwiki`** — ZimWiki markup.

## Documentation Formats

- **`rst`** — reStructuredText (Sphinx). Generates sections, lists, tables, and code blocks.
- **`asciidoc`** — Modern AsciiDoc (AsciiDoctor).
- **`asciidoc_legacy`** — Legacy AsciiDoc (asciidoc-py).
- **`haddock`** — Haskell Haddock documentation.
- **`vimdoc`** — Vim help file format.
- **`textile`** — Textile markup.
- **`djot`** — Djot markup.
- **`bbcode`** — BBCode (forum markup). Variants: `bbcode_fluxbb`, `bbcode_phpbb`, `bbcode_steam`, `bbcode_hubzilla`, `bbcode_xenforo`.

## XML and Data Formats

- **`docbook`** / **`docbook4`** — DocBook 4 XML.
- **`docbook5`** — DocBook 5 XML.
- **`jats`** / **`jats_archiving`** — JATS Archiving and Interchange Tag Set.
- **`jats_articleauthoring`** — JATS Article Authoring Tag Set.
- **`jats_publishing`** — JATS Journal Publishing Tag Set.
- **`opendocument`** — OpenDocument XML.
- **`tei`** — TEI Simple XML.
- **`xml`** — XML version of pandoc's native AST.
- **`json`** — JSON version of pandoc's native AST.
- **`icml`** — Adobe InDesign ICML.

## PDF Generation

Specify `.pdf` extension on output. Pandoc generates an intermediate format then compiles to PDF:

```bash
# Default: Markdown → LaTeX → PDF (pdflatex)
pandoc input.md -o output.pdf

# Use xelatex for better Unicode/font support
pandoc input.md -o output.pdf --pdf-engine=xelatex

# Use lualatex
pandoc input.md -o output.pdf --pdf-engine=lualatex

# HTML → PDF via WeasyPrint
pandoc input.md -t html --pdf-engine=weasyprint -o output.pdf

# HTML → PDF via wkhtmltopdf
pandoc input.md -t html --pdf-engine=wkhtmltopdf -o output.pdf

# ConTeXt → PDF
pandoc input.md -t context --pdf-engine=context -o output.pdf

# roff ms → PDF via a2ps
pandoc input.md -t ms --pdf-engine=a2ps -o output.pdf
```

Common PDF engines: `pdflatex`, `xelatex`, `lualatex`, `wkhtmltopdf`, `weasyprint`, `prince`, `context`. Engines must be installed separately.

## Bibliography Outputs

- **`bibtex`** — BibTeX .bib format.
- **`biblatex`** — BibLaTeX bibliography format.
- **`csljson`** — CSL JSON bibliography format.
