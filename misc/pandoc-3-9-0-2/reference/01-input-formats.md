# Input Formats

## Contents
- Markdown Variants
- Office and Word Processing
- Web Formats
- TeX and Typesetting
- E-book Formats
- Wiki and PIM Formats
- Documentation and Technical
- Bibliography Formats
- Data and AST Formats
- Extension Control

## Markdown Variants

| Format | Description |
|--------|-------------|
| `markdown` | Pandoc's Markdown (default input) with all extensions |
| `commonmark` | Strict CommonMark spec, no extensions |
| `commonmark_x` | CommonMark with pandoc extensions |
| `gfm` | GitHub-Flavored Markdown (tables, strikethrough, task lists) |
| `markdown_strict` | Original unextended Markdown |
| `markdown_mmd` | MultiMarkdown |
| `markdown_phpextra` | PHP Markdown Extra |

Use `gfm` for GitHub/Codeberg content. Use `markdown` (default) for full pandoc features. Avoid deprecated `markdown_github`.

## Office and Word Processing

- **`docx`** — Microsoft Word .docx (Office Open XML). Preserves headings, lists, tables, images, footnotes, and basic styling. Complex layouts may not convert perfectly.
- **`odt`** — OpenDocument Text (LibreOffice/OpenOffice). Similar preservation to docx.
- **`pptx`** — PowerPoint presentations. Reads slides as sections with content.
- **`xlsx`** — Excel spreadsheets. Imported as a table.
- **`csv`** — CSV tables (RFC 4180).
- **`tsv`** — Tab-separated values tables.

## Web Formats

- **`html`** — HTML/XHTML input. Reads full documents or fragments. Supports inline CSS for styling hints.
- **`mediawiki`** — MediaWiki markup (Wikimedia wiki syntax).
- **`dokuwiki`** — DokuWiki markup.
- **`jira`** — Jira/Confluence wiki markup.
- **`textile`** — Textile markup language.
- **`vimwiki`** — Vimwiki markup.
- **`tikiwiki`** — TikiWiki markup.
- **`twiki`** — TWiki markup.
- **`creole`** — Creole 1.0 wiki syntax.

## TeX and Typesetting

- **`latex`** — LaTeX documents. Reads sections, lists, tables, math, verbatim blocks, citations, and footnotes. Complex macros may not convert perfectly.
- **`man`** — roff man page format.
- **`mdoc`** — mdoc manual page markup (BSD).
- **`context`** — Not a reader; ConTeXt is output-only.
- **`typst`** — Typst documents (read support).

## E-book Formats

- **`epub`** — EPUB 2 and 3 e-books. Reads chapter structure, metadata, images, and embedded CSS.
- **`fb2`** — FictionBook2 e-book format (Russian e-book standard).

## Wiki and PIM Formats

- **`org`** — Emacs Org mode. Full support for headings, lists, tables, code blocks, LaTeX fragments, and properties. Extensions: `citations`, `fancy_lists`, `element_citations`, `smart_quotes`, `special_strings`.
- **`muse`** — GNU Muse wiki markup. Extensions: `styles`, `amuse`.
- **`opml`** — OPML outline format (outliner/outline processor markup).

## Documentation and Technical

- **`rst`** — reStructuredText (Sphinx/Docutils). Reads sections, lists, tables, code blocks, and substitution references.
- **`asciidoc`** — AsciiDoc markup (AsciiDoctor dialect).
- **`docbook`** — DocBook 4 and 5 XML documents.
- **`haddock`** — Haddock Haskell documentation markup.
- **`pod`** — Perl Plain Old Documentation.
- **`djot`** — Djot markup (strict, unambiguous Markdown alternative).
- **`t2t`** — txt2tags markup.
- **`jats`** / **`bits`** — JATS XML / BITS XML (NIH journal article tagging).

## Bibliography Formats

- **`bibtex`** — BibTeX bibliography files (.bib).
- **`biblatex`** — BibLaTeX bibliography files.
- **`csljson`** — CSL JSON bibliography format (used by Zotero, Mendeley).
- **`endnotexml`** — EndNote XML bibliography export.
- **`ris`** — RIS bibliography format (Reference Manager).

## Data and AST Formats

- **`json`** — JSON representation of pandoc's native AST. Use for programmatic inspection or as filter input/output.
- **`xml`** — XML representation of pandoc's native AST.
- **`native`** — Native Haskell data format (for debugging).
- **`ipynb`** — Jupyter notebook (.ipynb). Reads cells as paragraphs with code blocks. Metadata from notebook becomes document metadata.

## Extension Control

Append `+EXTENSION` or `-EXTENSION` to any format name to control features:

```bash
pandoc -f markdown+tables+footnotes+citations input.md
pandoc -f markdown-smart input.md          # Disable smart quotes
pandoc -f latex+raw_html input.tex         # Enable raw HTML in LaTeX
```

List available extensions:

```bash
pandoc --list-extensions                  # Default (Markdown)
pandoc --list-extensions=latex            # For a specific format
```

Key Markdown extensions:

| Extension | Description | Default |
|-----------|-------------|---------|
| `yaml_metadata_block` | YAML front matter metadata | On |
| `pandoc_title_block` | Traditional `% title` block | On |
| `tables` | Grid and pipe tables | On |
| `footnotes` | Numbered footnotes | On |
| `citations` | Pandoc citation syntax | On |
| `smart` | Smart typographic quotes/dashes | On |
| `raw_html` | Raw HTML tags in Markdown | On |
| `raw_tex` | Raw LaTeX/TeX in Markdown | On |
| `auto_identifiers` | Auto-generate heading IDs from text | On |
| `attributes` | Key-value attributes on elements | On |
| `task_lists` | GitHub-style task list checkboxes | Off |
| `fancy_lists` | Explicit list numbering/bullet styles | Off |
| `wikilinks_title_after_pipe` | WikiLink syntax with title after \| | Off |
