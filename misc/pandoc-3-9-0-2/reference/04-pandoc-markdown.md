# Pandoc's Markdown

## Contents
- Headings
- Paragraphs and Line Breaks
- Lists
- Tables
- Block Quotes and Code Blocks
- Footnotes
- Citations
- Math
- Raw HTML and TeX
- Attributes
- Metadata Blocks
- Typography (Smart Quotes)
- Links and Images

## Headings

### ATX-style

```markdown
# Level 1
## Level 2
### Level 3
```

### Setext-style

```markdown
Level 1
=======

Level 2
-------
```

### Heading Attributes

Add identifiers, classes, and key-value pairs:

```markdown
# My Heading {#my-id .custom-class key="value"}
```

In HTML, this produces `<h1 id="my-id" class="custom-class" key="value">`. Use `{#-}` to suppress auto-generated identifiers.

### Auto Identifiers

With `+auto_identifiers` (default on), pandoc generates IDs from heading text: lowercase, spaces to hyphens, non-alphanumeric removed. Control style with the extension variant (`gfm_auto_identifiers`, `ascii_identifiers`).

## Paragraphs and Line Breaks

Paragraphs are separated by blank lines. For hard line breaks within a paragraph:

- Trailing backslash: `line one\`
- Two or more trailing spaces: `line one  `
- Blank line between lines (creates separate paragraphs)
- `+escaped_line_breaks` extension: single backslash anywhere

## Lists

### Ordered Lists

```markdown
1. First item
2. Second item
   1. Nested item
   2. Another nested
```

With `+fancy_lists`, control numbering style:

```markdown
(1) Numbered in parens
a) Lowercase alpha
A) Uppercase alpha
i) Lowercase roman
I) Uppercase roman
-  Bullet (dash)
*  Bullet (asterisk)
```

### Definition Lists

```markdown
Term 1
:   Definition 1

Term 2
:   Definition 2a
:   Definition 2b (multiple definitions)
```

## Tables

### Pipe Tables

```markdown
| Right | Left | Center | Default |
|------:|:-----|:------:|---------|
|   12  |  12  |   12   |  12     |
|  123  |  123 |   123  |  123    |
```

Column alignment set by `:` in the separator row.

### Grid Tables (ASCII)

```
+----------+----------+
| Header 1 | Header 2 |
+==========+==========+
| Cell 1   | Cell 2   |
+----------+----------+
| Cell 3   | Cell 4   |
+----------+----------+
```

Uses `+`, `-`, `|` for borders and `=` to separate header from body.

### Simple Tables

```
--------  ---------
Flavors   Prices
--------  ---------
Chocolate $1.00

Vanilla   $1.10
--------  ---------
```

## Block Quotes and Code Blocks

### Block Quotes

```markdown
> This is a block quote.
>
> Multiple paragraphs supported.
```

### Indented Code Blocks

Four-space or one-tab indentation:

````markdown
    code here
    more code
````

With `--indented-code-classes=hashtag`, lines starting with `%` set classes:

````markdown
    % python
    print("hello")
````

### Fenced Code Blocks

```bash
pandoc command here
```

With language identifier for syntax highlighting:

```python
def hello():
    print("world")
```

With attributes:

``` {.python #my-code .special name="example"}
print("hello")
```

## Footnotes

### Inline Footnotes

```markdown
Here is a footnote reference.[^1]

[^1]: This is the footnote text.
```

### Bracketed Footnotes (ordered)

```markdown
Like this.[^]

[^]: First bracketed footnote.
[^]: Second bracketed footnote.
```

## Citations

Citation syntax (requires `+citations` extension, default on):

```markdown
As Smith argues (Smith 2020, p. 5), this is true.

See also @smith2020 and @jones2019[p. 12].

Multiple: [@smith2020; @jones2019; @lee2021].

With prefix: (@@smith2020, see also).
```

### Citation Modes

| Prefix | Mode | Example |
|--------|------|---------|
| (none) | Author in text | `Smith (2020)` |
| `@` | Parenthetical | `(Smith 2020)` |
| `@@` | Author-note with prefix | `see Smith (2020)` |

### Citation Modifications

Append in square brackets after cite key:

```markdown
@smith2020[p.5]      # Specific page
@smith2020[see]      # Prefix modifier
@smith2020[see p.5]  # Both
~@smith2020           # Negate (did NOT argue this)
```

### Bibliography Processing

```bash
pandoc paper.md \
  --cite-method=author-year \
  --csl=apa.csl \
  --bibliography=refs.bib \
  -s -o paper.html
```

Bibliography formats: `.bib` (BibTeX), `.json` (CSL JSON), `.yaml`/`.xml` (via citeproc).

## Math

### Inline Math

Single dollar signs: `$E = mc^2$`

### Display Math

Double dollar signs:

```markdown
$$
\int_0^\infty \frac{1}{1+x^2} dx = \frac{\pi}{2}
$$
```

### LaTeX Environments

```markdown
\[
  E = mc^2
\]

\begin{equation}
  \nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}
\end{equation}
```

### TeX Macros

Define macros in metadata or with `--template`:

```markdown
---
header-includes: |
  \newcommand{\R}{\mathbb{R}}
---
```

## Raw HTML and TeX

### Raw HTML (requires `+raw_html`, default on)

```markdown
This is <strong>bold</strong> and this is a <div>raw div</div>.
```

### Raw TeX (requires `+raw_tex`, default on)

```markdown
Here is some raw LaTeX: $\alpha$ and \textbf{bold text}.
```

Raw TeX is passed through to LaTeX, ConTeXt, and Texinfo output. In HTML output, raw TeX appears inside `<span class="raw tex">` or is processed by math rendering.

### Raw Attribute for Code Blocks

Force code block content as raw markup in specific formats:

````markdown
``` {.html}
<div>This renders as raw HTML in HTML output</div>
```
````

## Attributes

Attributes attach metadata to blocks and spans:

### On Headings

```markdown
# Heading {#id .class1 .class2 key="value"}
```

### On Code Blocks

````markdown
``` {.python .lineno startFrom="10" href="https://example.com"}
print("hello")
```
````

### On Paragraphs and Block Quotes

```markdown
[.warning]
> This is a styled block quote.
```

### On Spans (inline)

Use backticks with attribute:

````markdown
`text{#id .class key="value"}`
````

### On Figures and Tables

```markdown
![Caption](image.png){#fig:myfig width=80%}
```

## Metadata Blocks

### YAML Metadata Block (requires `+yaml_metadata_block`, default on)

```markdown
---
title: "Document Title"
author:
  - Author One
  - Author Two
date: 2024-01-15
abstract: |
  Abstract text here.
keywords: [pandoc, markdown]
...
```

Fields ending in `_` are ignored by pandoc (reserved for external processors). Multiple blocks merge; later values override earlier ones for duplicate keys.

### Pandoc Title Block (requires `+pandoc_title_block`, default on)

```markdown
% Title
% Author One; Author Two
% 2024-01-15
```

Lines starting with `%` at the very beginning of the document. Multi-line titles use continuation with leading space.

## Typography (Smart Quotes)

With `+smart` (default on), pandoc converts:

| Input | Output |
|-------|--------|
| `"quotes"` | "quotes" |
| `'apostrophes'` | 'apostrophes' |
| `--` | – (en dash) |
| `---` | — (em dash) |
| `...` | … (ellipsis) |
| `1-2` | 1–2 (en dash for ranges) |

## Links and Images

### Standard Links

```markdown
[link text](https://example.com "title")
```

### Auto Links

```markdown
<https://example.com>
<email@example.com>
```

### Images

```markdown
![alt text](image.png "optional title")
```

With attributes for width/height:

```markdown
![Diagram](diagram.png){width=50% height=200px}
```

### Internal Cross-References

With `+auto_identifiers`, reference headings by ID:

```markdown
See [Section Name](#section-name) for details.
```

### Wikilinks (with extension)

```markdown
[[Page Name]]
[[Page Name|Display Text]]
[[Page Name|Display Text|class]]
```
