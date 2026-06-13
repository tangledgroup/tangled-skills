# Comments and Shapes

## Contents
- Comment Anatomy
- Adding Comments
- Rich Content in Comments
- Accessing Comments
- Inline Shapes and Pictures

## Comment Anatomy

Each comment has two parts:

- **Comment reference (anchor)** — the range of text in the document that the comment is attached to. Delimited by `<w:commentRangeStart/>` and `<w:commentRangeEnd/>` markers at run boundaries.
- **Comment content** — the actual comment text, stored separately in `word/comments.xml`. Can contain rich content: paragraphs, runs with formatting, images, tables.

Comments can only be added to the main document body — not in headers, footers, or within other comments.

## Adding Comments

```python
from docx import Document

document = Document()
paragraph = document.add_paragraph("Hello, world!")

comment = document.add_comment(
    runs=paragraph.runs,
    text="I have this to say about that",
    author="Steve Canny",
    initials="SC",
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `runs` | Run or sequence | The run(s) the comment anchors to. Only first and last are used. Can span paragraphs. |
| `text` | str | Simple comment text content (default `''`) |
| `author` | str | Author name (required attribute, defaults to `''`) |
| `initials` | str | Author initials (defaults to `''`) |

### Comment properties

```python
comment.id          # Unique integer ID
comment.author      # Author string
comment.initials    # Initials string
comment.date        # datetime (UTC) when comment was added
comment.text        # Full text content
```

## Rich Content in Comments

Comments are block-item containers — they can hold paragraphs, tables, and formatted runs:

```python
paragraph = document.add_paragraph("The rain in Spain.")
comment = document.add_comment(runs=paragraph.runs, text="")

# Add rich content to the comment's paragraph
cmt_para = comment.paragraphs[0]
cmt_para.add_run("Please finish this thought. ")
cmt_para.add_run("falls mainly in the plain.").bold = True
```

The first paragraph of a comment contains an annotation reference run — leave it intact and add new runs after it.

## Accessing Comments

```python
comments = document.comments
count = len(comments)

# Access by ID
comment = comments.get(0)
```

### Updating metadata

```python
comment.author = "John Smith"
comment.initials = "JS"
```

The `date` property is read-only (set at creation time).

## Inline Shapes and Pictures

### Adding pictures

```python
from docx.shared import Inches

# From file path
document.add_picture('image.png')

# With explicit size
document.add_picture('image.png', width=Inches(1.5))
document.add_picture('image.png', height=Cm(3))
```

Specify only `width` or `height` to preserve aspect ratio. If neither is specified, the image appears at native size (calculated as pixels/dpi, defaulting to 72 dpi).

### From file-like object

```python
from io import BytesIO

with open('photo.jpg', 'rb') as f:
    document.add_picture(f, width=Inches(2))
```

### Inline shapes collection

Access all inline shapes in a document:

```python
shapes = document.inline_shapes
for shape in shapes:
    print(shape.width, shape.height)
```

Inline shapes behave like character glyphs — they flow with text and wrap to new lines. python-docx 1.2.0 supports only inline pictures; floating (anchored) shapes are not supported for creation.

### Picture sizing notes

- `Inches(n)`, `Cm(n)`, `Pt(n)` helpers from `docx.shared` convert to EMU internally
- These objects support arithmetic: `Inches(3) / count` works as expected
- Raw integer values are in EMU (914,400 per inch) — passing a bare integer like `width=2` produces an extremely tiny image
