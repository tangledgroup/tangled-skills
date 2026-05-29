# Images and Drawings

## Contents
- Inserting Images
- Drawing Anchors
- Rich Text in Cells

## Inserting Images

Requires `pillow` (`pip install pillow`). Supports JPEG, PNG, BMP, and other formats Pillow handles.

```python
from openpyxl import Workbook
from openpyxl.drawing.image import Image

wb = Workbook()
ws = wb.active
ws['A1'] = 'Logo below'

img = Image('logo.png')
ws.add_image(img, 'A1')  # Anchor image to cell A1

# Resize
img.width = 200
img.height = 100

wb.save('with_logo.xlsx')
```

Images are anchored to the top-left of the specified cell by default. Multiple images can be added to the same cell — they stack visually.

## Drawing Anchors

openpyxl supports three anchor types for positioning drawings (images, charts):

- **OneCellAnchor** — image position and size defined relative to one cell
- **TwoCellAnchor** — image anchored by two cells (top-left and bottom-right)
- **AbsoluteAnchor** — image positioned in absolute EMU (English Metric Units) coordinates

For most use cases, `ws.add_image(img, anchor_cell)` with a cell reference is sufficient. For precise positioning:

```python
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor
from openpyxl.drawing.image import Image

img = Image('logo.png')
anchor = OneCellAnchor(img)
anchor._from = 'A1'
ws.addDrawing(anchor)
```

### Unit conversions

Use `openpyxl.utils.units` for converting between measurement systems:

```python
from openpyxl.utils import units

units.EMU_to_cm(914400)     # EMU to centimeters
units.cm_to_EMU(5)          # Centimeters to EMU
units.pixels_to_EMU(100)    # Pixels to EMU
units.points_to_pixels(72)  # Points to pixels
```

## Rich Text in Cells

Rich text allows per-fragment formatting within a single cell. Enable with `rich_text=True` when loading workbooks.

```python
from openpyxl.cell.text import InlineFont
from openpyxl.cell.rich_text import TextBlock, CellRichText

# Create styled fragments
bold_font = InlineFont(b=True)
red_font = InlineFont(color='00FF0000')

rich = CellRichText(
    'Normal text ',
    TextBlock(bold_font, 'bold part'),
    ' and ',
    TextBlock(red_font, 'red part')
)

ws['A1'] = rich
```

### InlineFont

`InlineFont` is similar to `Font` but uses `rFont` instead of `name`:

```python
inline_font = InlineFont(
    rFont='Calibri',   # Font name (note: rFont, not name)
    sz=22,             # Size in 1/144 inch units (integer)
    b=True,            # Bold
    i=False,           # Italic
    u='single',        # Underline
    strike=False,      # Strikethrough
    color='00FF0000'   # aRGB color
)
```

Convert existing `Font` objects to `InlineFont`:

```python
from openpyxl.styles import Font
font = Font(name='Calibri', size=11, bold=True, color='00FF0000')
inline_font = InlineFont(font)  # Initialize from Font
```

### Editing rich text

```python
# Get list of text fragments
fragments = rich.as_list()
# ['Normal text ', 'bold part', ' and ', 'red part']

# Edit a fragment
rich[3].text = "modified"
str(rich)  # 'Normal text bold part and modified'
```

`CellRichText` is derived from `list` — use list operations (`append`, indexing, iteration). No whitespace is auto-inserted between elements.

### Assignment

```python
ws['A1'] = rich_string   # Rich text cell
ws['A2'] = 'Simple string'  # Plain text alongside
```
