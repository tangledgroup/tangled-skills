# Command Reference

## Contents
- Core Options
- Reader Options
- Writer Options
- Citation Rendering
- Math Rendering
- Templates
- Variables
- Defaults Files
- Data Directory
- Utility Commands

## Core Options

| Option | Description |
|--------|-------------|
| `-f FORMAT` / `--from=FORMAT` | Input format |
| `-t FORMAT` / `--to=FORMAT` | Output format |
| `-o FILE` / `--output=FILE` | Output file (`-` for stdout) |
| `-s` / `--standalone` | Full document with header/footer |
| `--sandbox` | Limit IO to specified files (security) |
| `--verbose` | Debug output |
| `--quiet` | Suppress warnings |
| `--fail-if-warnings` | Exit with error on warnings |
| `--log=FILE` | JSON log output |

## Reader Options

| Option | Description |
|--------|-------------|
| `--shift-heading-level-by=N` | Shift heading levels (positive or negative integer) |
| `--indented-code-classes=CLASSES` | Default classes for indented code blocks |
| `--default-image-extension=EXT` | Append extension to image paths if missing |
| `--track-changes=accept`/`reject`/`all` | Handle docx tracked changes |
| `--file-scope` | Parse each file individually (instead of concatenating) |
| `--preserve-tabs` | Keep tabs instead of converting to spaces |
| `--tab-stop=N` | Tab stop position (default: 4) |

## Writer Options

| Option | Description |
|--------|-------------|
| `--template=FILE` | Custom template file |
| `-V KEY=VAL` / `--variable=KEY=VAL` | Set template variable |
| `--variable-json=KEY:JSON` | Set variable from JSON value |
| `--wrap=auto\|none\|preserve` | Text wrapping mode |
| `--columns=N` | Characters per line (default: 72) |
| `--indent` | Indent paragraphs with spaces |
| `--tab-stop=N` | Tab stop for output |
| `--eol=crlf\|lf\|native` | Line endings |
| `--dpi=N` | DPI for pixel-to-inch conversion (default: 96) |
| `-D FORMAT` / `--print-default-template=FORMAT` | Print default template |

### Top-Level Division

Control the HTML `<div>` wrapper around document body:

```bash
pandoc -s --section-divs input.md -o output.html     # Wrap sections in <div>
pandoc -s --top-level-division=chapter input.md       # Use <chapter> tags
```

Options: `chapter`, `section`, `none`.

### Syntax Highlighting

```bash
pandoc --syntax-highlighting pygments input.md -o output.html
pandoc --highlight-style monochrome input.md -o output.html
```

Engines: `pygments`, `skylighting` (default), `codesnippet`, `native`. List styles with `--list-highlight-styles`.

### Incremental Lists

```bash
pandoc --incrementals input.md -t revealjs -o slides.html    # All lists incremental
pandoc --incrementals=chapter input.md -t revealjs           # Only top-level lists
```

### Listing Tables

```bash
pandoc --listings input.tex -o output.pdf    # Use LaTeX listings package for code
```

## Citation Rendering

| Option | Description |
|--------|-------------|
| `--cite-method=natbib` | Use natbib package (LaTeX) |
| `--cite-method=biblatex` | Use biblatex (LaTeX) |
| `--cite-method=note` | Render citations as footnotes |
| `--cite-method=author-year` | Author-year in-text citations |
| `--cite-method=numeric` | Numbered citations (default) |
| `--citation-abbreviations=file.yml` | Custom abbreviation file |
| `--csl=file.csl` | Citation Style Locator file |
| `--bibliography=file.bib` | Bibliography file(s) |
| `--bibliography-citekey-key=KEY` | Field used as cite key in non-bibtex bibliographies |

```bash
pandoc paper.md --cite-method=author-year \
  --csl=apa.csl --bibliography=refs.bib \
  -s -o paper.html
```

## Math Rendering

HTML math rendering options:

| Option | Description |
|--------|-------------|
| `--webtex=URL` | Use Google Charts or other web service for math images |
| `--mathjax` | Use MathJax (default for HTML) |
| `--mathjax=URL` | Custom MathJax URL |
| `--katex` | Use KaTeX JavaScript library |
| `--katex=URL` | Custom KaTeX URL |
| `--webtex` | Use web-based TeX rendering |
| `--gladtex` | Use gladTeX iOS app |
| `--mhchem` | Include mhchem support with mathjs |
| `--mathml` | Use MathML (native browser math) |

## Templates

Templates control standalone document structure. Syntax uses `{{variable}}` interpolation:

```html
<!DOCTYPE html>
<html>
<head>
  <title>{{title}}</title>
</head>
<body>
  {{<body>}}
</body>
</html>
```

### Template Features

- **Variables**: `{{var}}` — insert variable value
- **Conditionals**: `{{#var}}...{{/var}}` — include block if var is truthy
- **For loops**: `{{#var}}{{item}}{{/var}}` — iterate over lists
- **Pipes**: `{{var|escape}}` — apply filter function
- **Partials**: `{{>partial_name}}` — include another template
- **Comments**: `<%-- comment --%>`

### Template Resolution

1. `--template=FILE` — explicit path
2. `templates/` in user data directory
3. System default templates

Print defaults: `pandoc -D html`, `pandoc -D latex`.

Place custom templates in the user data directory (`~/.local/share/pandoc/templates/` on Linux, found via `pandoc --version`).

## Variables

Set via `-V key=value`, metadata fields, or defaults files. Key variables by format:

### HTML Variables

| Variable | Description |
|----------|-------------|
| `title` | Document title (in `<title>` tag) |
| `author` | Author name(s) |
| `date` | Publication date |
| `lang` | HTML `lang` attribute |
| `subtitle` | Subtitle heading |
| `abstract` | Abstract/summary block |
| `description` | Meta description |

### LaTeX Variables

| Variable | Description |
|----------|-------------|
| `documentclass` | LaTeX document class (default: `article`) |
| `classoption` | Document class options |
| `geometry` | Page geometry settings |
| `linestretch` | Line spacing |
| `mainfont` | Main font (for xelatex/lualatex) |
| `sansfont`, `monofont` | Alternative fonts |
| `colorlinks` | Enable colored hyperlinks |
| `links-as-notes` | Render links as footnotes |
| `numbersections` | Number section headings |
| `biblio-title` | Bibliography section title |
| `thanks` | Title footnote |

## Defaults Files

YAML/JSON files that store default option settings. Use `-d defaults.yaml`:

```yaml
from: markdown
to: html
standalone: true
output-file: output.html
metadata:
  title: "Default Title"
  author: "Author Name"
variables:
  documentclass: article
  geometry: margin=1in
filters:
  - pandoc-citeproc
bibliography: refs.bib
```

Search order: working directory, then `defaults/` in user data directory. `.yaml` extension is added if missing. Command-line options override defaults file settings.

## Data Directory

User data directory location (found via `pandoc --version`):

- **Linux/macOS**: `$XDG_DATA_HOME/pandoc` or `~/.local/share/pandoc`
- **Windows**: `%APPDATA%\pandoc`

Override with `--data-dir=DIRECTORY`.

Key subdirectories:

| Directory | Contents |
|-----------|----------|
| `templates/` | Custom default templates |
| `filters/` | Lua filters (auto-searched) |
| `reference.odt` | Reference document for ODT styling |
| `reference.docx` | Reference document for docx styling |
| `epub.css` | Default EPUB stylesheet |

Print system data files:

```bash
pandoc --print-default-data-file=templates/html.html
pandoc --print-default-data-file=creole.lua
```

## Utility Commands

```bash
pandoc --version                              # Version and data directory info
pandoc --help                                  # Usage message
pandoc --list-input-formats                    # Supported input formats
pandoc --list-output-formats                   # Supported output formats
pandoc --list-extensions                        # Markdown extensions
pandoc --list-highlight-languages              # Syntax highlighting languages
pandoc --list-highlight-styles                 # Highlighting theme styles
pandoc --bash-completion                       # Generate bash completion script
```
