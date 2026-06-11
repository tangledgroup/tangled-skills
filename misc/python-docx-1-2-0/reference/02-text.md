# Text Formatting

## Contents
- Paragraphs
- Runs and Character Formatting
- Font Properties
- ParagraphFormat Properties
- Tab Stops
- Hyperlinks

## Paragraphs

### Adding paragraphs

```python
paragraph = document.add_paragraph('Lorem ipsum dolor sit amet.')
```

Returns the newly created `Paragraph` at the end of the document. Optionally specify a style:

```python
paragraph = document.add_paragraph('List item', style='List Bullet')
```

### Inserting before an existing paragraph

```python
prior = paragraph.insert_paragraph_before('Inserted text')
```

Use this to insert content in the middle of a document rather than appending at the end.

### Empty paragraphs

```python
paragraph = document.add_paragraph()
```

Creates an empty paragraph with no runs. Build content by adding runs:

```python
paragraph.add_run('First run ')
paragraph.add_run('Second run')
```

### Accessing paragraph text

```python
text = paragraph.text        # Full text of all runs concatenated
runs = paragraph.runs         # List of Run objects in the paragraph
```

## Runs and Character Formatting

A `Run` is a contiguous span of text with uniform character formatting. All text in a paragraph must be within runs. Different formatting requires separate runs.

### Adding runs

```python
paragraph = document.add_paragraph('Normal text, ')
run = paragraph.add_run('bold text.')
run.bold = True
```

Spaces are not automatically inserted between runs — include them explicitly:

```python
paragraph.add_run('Hello ')
paragraph.add_run('World')
# Result: "Hello World" (space in first run)
```

### Character formatting on runs

Apply formatting directly to a `Run` object or chain off `add_run()`:

```python
paragraph.add_run('bold').bold = True
paragraph.add_run(' italic').italic = True
paragraph.add_run(' underline').underline = True
paragraph.add_run(' strike').strike = True
paragraph.add_run(' superscript').superscript = True
paragraph.add_run(' subscript').subscript = True
paragraph.add_run(' all caps').all_caps = True
paragraph.add_run(' small caps').small_caps = True
```

All character formatting properties are **tri-state** (`True`/`False`/`None`). `None` means inherit from the style hierarchy.

## Font Properties

Access via `run.font`. The `Font` object controls typeface, size, color, and all character-level formatting.

### Typeface and size

```python
from docx.shared import Pt

font = run.font
font.name = 'Calibri'
font.size = Pt(12)
```

### Font color (RGB)

```python
from docx.shared import RGBColor

font.color.rgb = RGBColor(0x42, 0x24, 0xE9)
```

### Font color (theme)

```python
from docx.enum.dml import MSO_THEME_COLOR

font.color.theme_color = MSO_THEME_COLOR.ACCENT_1
```

### Inspecting font color

```python
color_type = font.color.type        # MSO_COLOR_TYPE.RGB or .THEME or .AUTO or None
if color_type == MSO_COLOR_TYPE.RGB:
    print(font.color.rgb)           # RGBColor(0x42, 0x24, 0xe9)
elif color_type == MSO_COLOR_TYPE.THEME:
    print(font.color.theme_color)   # e.g. ACCENT_1 (5)
```

### Resetting to inherited

```python
font.color.rgb = None               # Restore inherited color
font.bold = None                    # Restore inherited bold
```

### Complete Font properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Typeface name, e.g. `'Calibri'` |
| `size` | Length | Font size, e.g. `Pt(12)` |
| `bold` | bool/None | Bold formatting |
| `italic` | bool/None | Italic formatting |
| `underline` | bool/None/enum | Underline; `True`=single, or `WD_UNDERLINE.*` value |
| `strike` | bool/None | Strikethrough |
| `double_strike` | bool/None | Double strikethrough |
| `superscript` | bool/None | Superscript |
| `subscript` | bool/None | Subscript |
| `all_caps` | bool/None | All caps |
| `small_caps` | bool/None | Small caps |
| `shadow` | bool/None | Shadow effect |
| `outline` | bool/None | Outline effect |
| `emboss` | bool/None | Emboss effect |
| `impress` | bool/None | Impress (engrave) effect |
| `hidden` | bool/None | Hidden text |
| `color` | ColorFormat | Font color (see above) |

## ParagraphFormat Properties

Access via `paragraph.paragraph_format`. Controls block-level layout.

### Alignment

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

fmt = paragraph.paragraph_format
fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER
# Options: LEFT, CENTER, RIGHT, JUSTIFY, BOTH
```

### Indentation

```python
from docx.shared import Inches

fmt.left_indent = Inches(0.5)
fmt.right_indent = Inches(0.25)
fmt.first_line_indent = Inches(-0.25)   # Hanging indent (negative)
# fmt.first_line_indent = Inches(0.3)   # First-line indent (positive)
```

### Spacing between paragraphs

```python
from docx.shared import Pt

fmt.space_before = Pt(12)
fmt.space_after = Pt(6)
```

Spacing is collapsed: the gap between two paragraphs is `max(prev.space_after, next.space_before)`.

### Line spacing

```python
# Absolute spacing
fmt.line_spacing = Pt(18)
# Relative spacing (multiple of line height)
fmt.line_spacing = 1.5
# Rule is auto-set: EXACTLY for Length, MULTIPLE for float
```

### Pagination control

```python
fmt.keep_together = True       # Keep entire paragraph on one page
fmt.keep_with_next = True      # Keep with following paragraph
fmt.page_break_before = True   # Start paragraph on new page
fmt.widow_control = True       # Avoid orphan/widow lines
```

All four are tri-state (`True`/`False`/`None`).

## Tab Stops

Access via `paragraph.paragraph_format.tab_stops`. Controls rendering of `\t` characters in paragraph text.

### Adding tab stops

```python
from docx.shared import Inches
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

tab_stops = paragraph.paragraph_format.tab_stops
tab_stops.add_tab_stop(Inches(1.5))
tab_stops.add_tab_stop(Inches(3.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
```

### Alignment options

`WD_TAB_ALIGNMENT`: `LEFT`, `RIGHT`, `CENTER`, `DECIMAL`, `BAR`

### Leader options

`WD_TAB_LEADER`: `NONE`, `DOTS`, `HYPHENS`, `UNDERSCORE`, `MIDDLE_DOTS`, `HEAVY`, `HIDDEN`

### Accessing existing tab stops

```python
for tab_stop in tab_stops:
    print(f"Position: {tab_stop.position.inches}in, "
          f"Align: {tab_stop.alignment}, Leader: {tab_stop.leader}")
```

## Hyperlinks

Add hyperlinks to a paragraph's runs. The `Hyperlink` object wraps a run with a URL.

```python
from docx.shared import Inches
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml.etree import QName
from docx.oxml.ns import qn

paragraph = document.add_paragraph()
run = paragraph.add_run('Click here')

# Add hyperlink
r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
hyperlink = OxmlElement('w:hyperlink')
hyperlink.set(qn('r:id'), r_id)
new_run = copy.deepcopy(run._element)
hyperlink.append(new_run)
paragraph._element.append(hyperlink)
```

Note: Hyperlink creation requires low-level OOXML manipulation. The `Document` and `Paragraph` objects do not have a high-level `add_hyperlink()` method in python-docx 1.2.0.
