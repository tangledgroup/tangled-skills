# Filters and Lua

## Contents
- Filter Architecture
- JSON Filters
- Lua Filters
- Lua Filter Structure
- Pandoc Lua API
- Custom Readers
- Custom Writers
- Reproducible Builds

## Filter Architecture

Pandoc filters transform the AST between reading and writing:

```
INPUT --reader--> AST --filter--> AST --writer--> OUTPUT
```

Two filter types:

| Type | Language | Performance | Dependencies |
|------|----------|-------------|--------------|
| **JSON filters** | Any | Slower (JSON serialization) | External interpreter + JSON library |
| **Lua filters** | Lua 5.4 | Fast (native, no JSON) | None (built into pandoc) |

Filters are applied in command-line order. Lua filters are preferred for performance and portability.

## JSON Filters

JSON filters read a JSON AST from stdin and write a modified JSON AST to stdout. Use `--filter` to invoke:

```bash
# Using the built-in citeproc filter
pandoc paper.md --filter pandoc-citeproc -s -o paper.html

# Manual pipeline
pandoc -t json input.md | my-filter.py | pandoc -f json -s -o output.html
```

### JSON AST Format

The JSON representation mirrors pandoc's Haskell data types:

```json
{
  "type": "Pandoc",
  "meta": {
    "title": {"type": "Str", "text": "Hello"}
  },
  "blocks": [
    {
      "type": "Para",
      "content": [
        {"type": "Str", "text": "Hello"},
        {"type": "Space"},
        {"type": "Emph", "content": [{"type": "Str", "text": "world"}]}
      ]
    }
  ]
}
```

View AST: `pandoc -t json input.md`

### Popular JSON Filter Tools

- **pandoc-citeproc** — Built-in citation processing
- **pandoc-crossref** — Cross-references for figures, tables, equations
- **pandoc-fignos** / **pandoc-tablenos** — Numbering filters
- **pandoc-include-code** — Include code files in documents
- **python-markdown-math** — Math processing
- **hashtag** — Social media link expansion

## Lua Filters

Lua filters use the embedded Lua 5.4 interpreter. No external dependencies required.

### Basic Structure

A Lua filter is a table mapping element names to transformation functions:

```lua
return {
  Strong = function(elem)
    return pandoc.SmallCaps(elem.content)
  end,
}
```

Or equivalently (top-level functions auto-collected):

```lua
function Strong(elem)
  return pandoc.SmallCaps(elem.content)
end
```

### Invoking Lua Filters

```bash
pandoc --lua-filter=smallcaps.lua input.md -o output.html
```

Multiple filters applied in order:

```bash
pandoc --lua-filter=a.lua --lua-filter=b.lua input.md
```

Filters in the user data directory `filters/` subdirectory are auto-searched.

### Walk Method

For complex transformations, use `pandoc.walk()` to traverse the AST:

```lua
local pandoc = require 'pandoc'

return {
  {
    Meta = function(meta)
      -- Process metadata first
      return meta
    end,
  },
  {
    Para = function(para)
      -- Then process paragraphs
      return para
    end,
  },
}
```

### AST Transformation Examples

**Remove all images:**

```lua
return {
  Image = function(img)
    return img.caption    -- Replace image with its caption
  end,
}
```

**Add class to all code blocks:**

```lua
return {
  CodeBlock = function(cb)
    table.insert(cb.classes, 'highlighted')
    return cb
  end,
}
```

**Convert headings to definition list terms:**

```lua
return {
  Header = function(hdr)
    local term = pandoc.Plain(hdr.content)
    local def = pandoc.DefinitionList{{term, {pandoc.Definition(pandoc.Plain{}))}}}
    return def
  end,
}
```

**Strip all attributes from links:**

```lua
return {
  Link = function(link)
    link.attributes = pandoc.Attr()
    return link
  end,
}
```

## Pandoc Lua API

### AST Element Constructors

Create pandoc AST elements in Lua:

| Constructor | Description |
|-------------|-------------|
| `pandoc.Pandoc(blocks)` | Root document |
| `pandoc.Para(content)` | Paragraph |
| `pandoc.Plain(content)` | Plain text block |
| `pandoc.Heading(level, attr, content)` | Heading |
| `pandoc.Str(text)` | Text string |
| `pandoc.Space` | Space character |
| `pandoc.LineBreak` | Hard line break |
| `pandoc.Emph(content)` | Emphasis (italic) |
| `pandoc.Strong(content)` | Strong emphasis (bold) |
| `pandoc.Link(content, src, title, attr)` | Hyperlink |
| `pandoc.Image(content, src, title, attr)` | Image |
| `pandoc.CodeBlock(content, classes, attr)` | Code block |
| `pandoc.Code(text, classes, attr)` | Inline code |
| `pandoc.BlockQuote(blocks)` | Block quote |
| `pandoc.OrderedList(indent, start, items)` | Ordered list |
| `pandoc.BulletList(items)` | Bullet list |
| `pandoc.DefinitionList(items)` | Definition list |
| `pandoc.Table(attr, captions, cols, rows)` | Table |
| `pandoc.Cite(content, citations)` | Citation |
| `pandoc.Math(type, text)` | Math (Inline/Display) |
| `pandoc.SmallCaps(content)` | Small caps |
| `pandoc.Span(content, attr)` | Inline span with attributes |
| `pandoc.Div(blocks, attr)` | Block-level div with attributes |

### Attributes

```lua
local attr = pandoc.Attr('id', {'class1', 'class2'}, {key='value'})
local heading = pandoc.Heading(1, attr, {pandoc.Str("Title")})
```

### Read/Write from Lua

```lua
-- Read a document
local doc = pandoc.read(input, 'markdown')

-- Write to format
local output = pandoc.write(doc, 'html')
```

### Format Version

```lua
print(pandoc.version.major)  -- e.g., 3
print(pandoc.version.minor)  -- e.g., 9
```

## Custom Readers

Custom readers are Lua scripts defining a `Reader` function:

```lua
function Reader(input)
  -- Parse input string, return pandoc AST
  local doc = pandoc.Pandoc{}
  for line in input:gmatch('[^\r\n]+') do
    table.insert(doc.blocks, pandoc.Para{pandoc.Str(line)})
  end
  return doc
end
```

With reader options access:

```lua
function Reader(input, options)
  -- options.tabs, options.reader_options available
  return pandoc.Pandoc{}
end
```

Invoke: `pandoc -f my_reader.lua input.txt -t html`

The `lpeg` parsing library is available by default. See built-in readers: `pandoc --print-default-data-file creole.lua`.

## Custom Writers

Custom writers define rendering functions for each AST element:

```lua
function Para(elem)
  return "<p>" .. elem.content .. "</p>\n"
end

function Str(elem)
  return elem.text
end

function Space(elem)
  return " "
end
```

Invoke: `pandoc -t my_writer.lua input.md`

Custom writers have no default template. Use `--template` manually with `--standalone`. See `djot-writer.lua` for a full example.

## Reproducible Builds

Set `SOURCE_DATE_EPOCH` to fix timestamps in output:

```bash
export SOURCE_DATE_EPOCH=1700000000
pandoc input.md -o output.epub    # Fixed build timestamp
```

For LaTeX PDFs, set `pdf-trailer-id` in metadata or leave undefined (auto-hashed from `SOURCE_DATE_EPOCH`).
