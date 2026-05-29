# Styles and Formatting

## Contents
- Font Styles
- Fills (Solid, Pattern, Gradient)
- Borders
- Alignment
- Cell Protection
- Named Styles vs Cell Styles
- Colors (aRGB, Indexed, Theme)
- Number Formats
- Page Setup
- Builtin Styles

## Font Styles

```python
from openpyxl.styles import Font

ft = Font(
    name='Calibri',     # Font name
    size=12,            # Size in points
    bold=True,
    italic=False,
    underline='single',  # 'none', 'single', 'double', 'singleAccounting', 'doubleAccounting'
    strike=True,        # Strikethrough
    color='FF000000',   # aRGB color
    vertAlign='superscript'  # 'baseline', 'superscript', 'subscript'
)

ws['A1'].font = ft
```

## Fills (Solid, Pattern, Gradient)

```python
from openpyxl.styles import PatternFill, GradientFill, Fill

# Solid fill
solid_fill = PatternFill(start_color='DDDDDD',
                         end_color='DDDDDD',
                         fill_type='solid')
ws['A1'].fill = solid_fill

# Pattern fill
pattern_fill = PatternFill(fill_type='darkGray',
                           start_color='FF0000',
                           end_color='00FF00')

# Gradient fill
gradient = GradientFill(stop=('000000', 'FFFFFF'))
ws['A1'].fill = gradient
```

## Borders

```python
from openpyxl.styles import Border, Side

thin = Side(border_style='thin', color='000000')
double = Side(border_style='double', color='FF0000')

border = Border(top=double, left=thin, right=thin, bottom=double)
ws['A1'].border = border
```

Common border styles: `thin`, `medium`, `thick`, `dotted`, `dashed`, `dash_dot`, `double`, `slantDashDot`.

## Alignment

```python
from openpyxl.styles import Alignment

align = Alignment(
    horizontal='center',   # 'left', 'center', 'right', 'justify', 'fill', 'centerContinuous', 'distributed', 'general'
    vertical='center',     # 'top', 'center', 'bottom', 'justify', 'distributed'
    text_rotation=0,       # Degrees (0-180), or 90/45/-45 for special angles
    wrap_text=True,
    shrink_to_fit=False,
    indent=2
)
ws['A1'].alignment = align
```

## Cell Protection

```python
from openpyxl.styles import Protection

prot = Protection(locked=True, hidden=False)
ws['A1'].protection = prot
```

`locked` prevents modification when sheet protection is enabled. `hidden` conceals formulas in the formula bar. Default: `locked=True`.

## Named Styles vs Cell Styles

### Cell styles (immutable after assignment)

Once assigned to a cell, a style object cannot be modified. Reassign to change:

```python
from openpyxl.styles import Font

ft = Font(color="FF0000")
ws['A1'].font = ft
# ws['A1'].font.italic = True  # NOT allowed
ws['A1'].font = Font(color="FF0000", italic=True)  # Reassign instead
```

Copy styles to create variants:

```python
from copy import copy
ft2 = copy(ft)
ft2.name = "Tahoma"
```

### Named styles (registered templates)

Named styles are registered with the workbook and referenced by name:

```python
from openpyxl.styles import NamedStyle, Font, Border, Side

highlight = NamedStyle(name="highlight")
highlight.font = Font(bold=True, size=20)
bd = Side(style='thick', color="000000")
highlight.border = Border(left=bd, top=bd, right=bd, bottom=bd)

# Register (or auto-register on first cell assignment)
wb.add_named_style(highlight)

# Apply by name
ws['A1'].style = highlight
ws['D5'].style = 'highlight'
```

## Colors (aRGB, Indexed, Theme)

Use aRGB colors for reliability. Format: `AARRGGBB` (alpha + RGB hex).

```python
from openpyxl.styles import Font
font = Font(color="FF0000")  # Red — alpha 'FF' prepended automatically

# Full aRGB
font = Font(color="00FF0000")  # Same red

# Indexed (legacy, depends on workbook/application defaults)
from openpyxl.colors import Color
c = Color(indexed=32)

# Theme colors (depends on workbook theme)
c = Color(theme=6, tint=0.5)
```

## Number Formats

```python
ws['A1'].number_format = '0.00'           # 2 decimal places
ws['A2'].number_format = '#,##0'          # Comma-separated thousands
ws['A3'].number_format = '0%'            # Percentage
ws['A4'].number_format = '$#,##0.00'     # Currency
ws['A5'].number_format = 'yyyy-mm-dd'    # Date
```

Datetime values are auto-formatted on assignment. Check with `cell.number_format`.

Built-in format IDs exist for common patterns (General, 0, 0.00, #,##0, etc.).

## Page Setup

```python
ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_setup.fitToHeight = 0
ws.page_setup.fitToWidth = 1
```

Paper size aliases: `PAPERSIZE_LETTER`, `PAPERSIZE_A4`, `PAPERSIZE_A5`, `PAPERSIZE_TABLOID`, etc. See `openpyxl.worksheet.worksheet` for full list.

## Builtin Styles

Predefined styles available by English name only:

- **Number formats:** `Comma`, `Comma [0]`, `Currency`, `Currency [0]`, `Percent`
- **Informative:** `Calculation`, `Total`, `Note`, `Warning Text`, `Explanatory Text`
- **Text styles:** `Title`, `Headline 1-4`, `Hyperlink`, `Followed Hyperlink`, `Linked Cell`
- **Comparisons:** `Input`, `Output`, `Check Cell`, `Good`, `Bad`, `Neutral`
- **Highlights:** `Accent1-6` with `20%`, `40%`, `60%` variants
- **Pandas:** `Pandas` (for DataFrame styling)

```python
ws['A1'].style = 'Title'
ws['B1'].style = 'Currency'
```
