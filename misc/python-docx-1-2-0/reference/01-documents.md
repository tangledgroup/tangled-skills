# Documents

## Contents
- Opening Documents
- Saving Documents
- Core Properties
- Traversing Document Content
- Document Settings

## Opening Documents

### Blank document (default template)

```python
from docx import Document

document = Document()
```

Creates a new document from the built-in default template, which includes common paragraph styles, character styles, and table styles.

### Open existing document by path

```python
document = Document('existing-file.docx')
```

Only Word 2007+ `.docx` files are supported. Older `.doc` files are not compatible. The file is loaded into memory; saving with the same path overwrites silently.

### Open from file-like object (stream)

```python
from docx import Document
from io import BytesIO

with open('source.docx', 'rb') as f:
    document = Document(f)
```

Useful for loading documents from databases, network connections, or in-memory buffers without filesystem interaction.

## Saving Documents

### Save to path

```python
document.save('output.docx')
```

Overwrites existing files silently. Use a different path to preserve the original.

### Save to stream

```python
from io import BytesIO

buffer = BytesIO()
document.save(buffer)
buffer.seek(0)
# buffer now contains the .docx bytes
```

Useful for returning documents in web responses, storing in databases, or piping between processes.

## Core Properties

Access document metadata (Dublin Core properties) via `document.core_properties`. Properties are read/write and persist on save.

```python
props = document.core_properties
props.title = 'Quarterly Report'
props.author = 'Jane Doe'
props.subject = 'Financial Results'
props.keywords = 'quarterly, report, finance'
props.category = 'Report'
props.comments = 'Draft version for review'
props.content_status = 'draft'
```

### Available properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | str | Name of the resource (max 255 chars) |
| `author` | str | Primary responsible entity |
| `subject` | str | Topic of content |
| `keywords` | str | Search terms |
| `description` / `comments` | str | Account of content |
| `category` | str | Content categorization |
| `content_status` | str | Completion status, e.g. `'draft'` |
| `created` | datetime | Initial creation time (UTC) |
| `modified` | datetime | Last modification time (UTC) |
| `last_modified_by` | str | Name of last modifier |
| `last_printed` | datetime | Last print time (UTC) |
| `revision` | int | Revision number (not auto-incremented by python-docx) |
| `identifier` | str | Unambiguous reference, e.g. ISBN |
| `language` | str | Document language |
| `version` | str | Free-form version string |

String properties return `''` if not set. Date properties return `None` if not set.

## Traversing Document Content

### Access paragraphs

```python
for paragraph in document.paragraphs:
    print(paragraph.text)
```

Returns all top-level paragraphs in document order. Paragraphs within revision marks (`<w:ins>`, `<w:del>`) are excluded.

### Access tables

```python
for table in document.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

Returns only top-level tables. Tables nested inside cells are not included. Use `cell.iter_inner_content()` to access nested content.

### Iterate all block-level content

```python
for item in document.iter_inner_content():
    if hasattr(item, 'text'):
        # Paragraph
        print(f"Paragraph: {item.text}")
    else:
        # Table
        print(f"Table with {len(item.rows)} rows")
```

`iter_inner_content()` yields `Paragraph` and `Table` objects in document order. Use this for uniform traversal of mixed content.

## Document Settings

Access document-level settings via `document.settings`. This provides programmatic access to the document's settings part (`word/settings1.xml`).

```python
settings = document.settings
```

The Settings object exposes configuration options that control document behavior, including compatibility settings and protection options. Consult the [API Reference](reference/07-api-reference.md) for available properties.
