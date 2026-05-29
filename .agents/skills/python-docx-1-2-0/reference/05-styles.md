# Styles

## Contents
- Style Types
- Accessing and Applying Styles
- Adding Custom Styles
- Style Inheritance
- Style Behavior Properties
- Latent Styles
- Default Template Styles

## Style Types

Word has four style types, each applied to different content:

| Type | Applied to | Enum value |
|------|-----------|------------|
| Paragraph | `Paragraph` objects | `WD_STYLE_TYPE.PARAGRAPH (1)` |
| Character | `Run` objects | `WD_STYLE_TYPE.CHARACTER (2)` |
| Table | `Table` objects | `WD_STYLE_TYPE.TABLE (3)` |
| Numbering | List formatting | `WD_STYLE_TYPE.NUMBERING (4)` |

## Accessing and Applying Styles

### Access styles collection

```python
styles = document.styles
style = styles['Normal']
```

Styles are accessed by name using dictionary-style syntax. Built-in styles use their **English names** regardless of the Word UI language (e.g., always `'Heading 1'`, not localized names).

### Apply at creation time

```python
# By name
paragraph = document.add_paragraph('Text', style='List Bullet')

# By style object
heading_style = document.styles['Heading 1']
paragraph = document.add_paragraph('Title', style=heading_style)
```

### Apply after creation

```python
paragraph.style = 'Heading 1'
run.style = 'Emphasis'
table.style = 'LightShading-Accent1'
```

### List all styles of a type

```python
from docx.enum.style import WD_STYLE_TYPE

paragraph_styles = [
    s for s in document.styles
    if s.type == WD_STYLE_TYPE.PARAGRAPH
]
```

## Adding Custom Styles

```python
from docx.enum.style import WD_STYLE_TYPE

style = document.styles.add_style('Citation', WD_STYLE_TYPE.PARAGRAPH)
style.base_style = document.styles['Normal']
```

### Set character formatting on a style

```python
font = style.font
font.name = 'Times New Roman'
font.size = Pt(10)
font.italic = True
```

### Set paragraph formatting on a style

```python
from docx.shared import Inches, Pt

fmt = style.paragraph_format
fmt.left_indent = Inches(0.25)
fmt.first_line_indent = Inches(-0.25)   # Hanging indent
fmt.space_before = Pt(12)
fmt.widow_control = True
```

### Delete a style

```python
document.styles['Citation'].delete()
```

Deleting a style removes its definition but does not affect content that already uses it. That content reverts to the default style (e.g., `Normal` for paragraphs).

## Style Inheritance

Styles can inherit from other styles via `base_style`:

```python
style.base_style = document.styles['Normal']
```

This forms an inheritance hierarchy. Properties not set on a child style are inherited from its base. Setting a property to `None` on the child restores inheritance.

### next_paragraph_style

Controls which style is applied to new paragraphs inserted after a paragraph of this style:

```python
document.styles['Heading 1'].next_paragraph_style = document.styles['Body Text']
```

Useful so that after typing a heading, the next paragraph automatically reverts to body text style. Reset with `None` or the style itself.

## Style Behavior Properties

Five properties control how a style appears in the Word UI:

| Property | Type | Description |
|----------|------|-------------|
| `hidden` | bool/None | `False` = visible in recommended list |
| `quick_style` | bool/None | `True` = appears in style gallery |
| `priority` | int | Sort order in style lists (lower = first) |
| `locked` | bool/None | `True` = hidden when formatting restrictions on |
| `unhide_when_used` | bool/None | `True` = auto-unhides on first use |

### Display a style in the style gallery

```python
style = document.styles['Body Text']
style.hidden = False
style.quick_style = True
style.priority = 1
```

### Remove from style gallery

```python
style = document.styles['Normal']
style.hidden = False
style.quick_style = False
```

## Latent Styles

Latent styles define the behavior of built-in Word styles that are not yet defined in the document. They control whether a built-in style appears in the UI when first used.

### Access latent styles

```python
latent_styles = document.styles.latent_styles
count = len(latent_styles)          # e.g. 161

# Iterate
for ls in latent_styles:
    print(ls.name, ls.priority)

# Dictionary access
quote_style = latent_styles['Quote']
```

### Change defaults

```python
latent_styles.default_to_locked = True
```

Defaults apply to all built-in styles without explicit latent definitions.

### Add a latent style definition

```python
ls = latent_styles.add_latent_style('List Bullet')
ls.hidden = False
ls.priority = 2
ls.quick_style = True
```

### Delete a latent style definition

```python
latent_styles['Light Grid'].delete()
```

## Default Template Styles

The built-in default template includes these styles. If using a custom template, ensure needed styles are applied at least once before saving.

### Paragraph styles (34)

`Normal`, `Body Text`, `Body Text 2`, `Body Text 3`, `Caption`, `Heading 1`–`9`, `Intense Quote`, `List`, `List 2`, `List 3`, `List Bullet`, `List Bullet 2`, `List Bullet 3`, `List Continue`, `List Continue 2`, `List Continue 3`, `List Number`, `List Number 2`, `List Number 3`, `List Paragraph`, `Macro Text`, `No Spacing`, `Quote`, `Subtitle`, `TOCHeading`, `Title`

### Character styles (24)

`Body Text Char`, `Body Text 2 Char`, `Body Text 3 Char`, `Book Title`, `Default Paragraph Font`, `Emphasis`, `Heading 1 Char`–`9 Char`, `Intense Emphasis`, `Intense Quote Char`, `Intense Reference`, `Macro Text Char`, `Quote Char`, `Strong`, `Subtitle Char`, `Subtle Emphasis`, `Subtle Reference`, `Title Char`

### Table styles (81)

`Table Normal`, `Table Grid`, `Colorful Grid`/`List`/`Shading` + Accent 1–6, `Dark List` + Accent 1–6, `Light Grid`/`List`/`Shading` + Accent 1–6, `Medium Grid 1`/`2`/`3` + Accent 1–6, `Medium List 1`/`2` + Accent 1–6, `Medium Shading 1`/`2` + Accent 1–6
