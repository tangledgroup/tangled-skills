# API Reference

## Contents
- Document Object
- Paragraph Object
- ParagraphFormat Object
- Run Object
- Font Object
- Table, Row, Column, Cell Objects
- Section Object
- Header and Footer Objects
- Styles and Style Objects
- TabStops and.TabStop Objects
- ColorFormat Object

## Document Object

### Constructor

```python
Document(docx: str | IO[bytes] | None = None) -> Document
```

`None` or omitted loads the built-in default template. String path opens existing file. File-like object opens from stream.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_paragraph(text='', style=None)` | `Paragraph` | Add paragraph at end of document |
| `add_heading(text='', level=1)` | `Paragraph` | Add heading (level 0=Title, 1-9=Heading N) |
| `add_page_break()` | `Paragraph` | Insert hard page break |
| `add_table(rows, cols, style=None)` | `Table` | Add table with given dimensions |
| `add_picture(path_or_stream, width=None, height=None)` | `InlineShape` | Add inline picture |
| `add_section(start_type=NEW_PAGE)` | `Section` | Add new section |
| `add_comment(runs, text='', author='', initials='')` | `Comment` | Add comment anchored to runs |
| `save(path_or_stream)` | None | Save to file path or stream |
| `iter_inner_content()` | Iterator | Yield Paragraph/Table in document order |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `paragraphs` | list[Paragraph] | All top-level paragraphs |
| `tables` | list[Table] | All top-level tables |
| `sections` | Sections | Document sections collection |
| `styles` | Styles | Document styles collection |
| `comments` | Comments | Comments collection |
| `inline_shapes` | InlineShapes | Inline shapes collection |
| `core_properties` | CoreProperties | Dublin Core metadata |
| `settings` | Settings | Document-level settings |
| `part` | DocumentPart | Low-level document part |

## Paragraph Object

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Full text of all runs concatenated |
| `runs` | list[Run] | Run objects in the paragraph |
| `style` | ParagraphStyle/str | Applied paragraph style (read/write) |
| `paragraph_format` | ParagraphFormat | Block-level formatting |
| `_element` | CT_P | Low-level XML element |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_run(text='', style=None)` | `Run` | Add a run to the paragraph |
| `insert_paragraph_before(text='', style=None)` | `Paragraph` | Insert paragraph before this one |

## ParagraphFormat Object

Access via `paragraph.paragraph_format`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `alignment` | WD_ALIGN_PARAGRAPH/None | Horizontal alignment |
| `left_indent` | Length/None | Left indentation |
| `right_indent` | Length/None | Right indentation |
| `first_line_indent` | Length/None | First-line indent (negative=hanging) |
| `space_before` | Length/None | Space before paragraph |
| `space_after` | Length/None | Space after paragraph |
| `line_spacing` | Length or float/None | Line spacing (absolute or multiple) |
| `line_spacing_rule` | WD_LINE_SPACING/None | Spacing rule (auto-set with line_spacing) |
| `keep_together` | bool/None | Keep paragraph on one page |
| `keep_with_next` | bool/None | Keep with following paragraph |
| `page_break_before` | bool/None | Start on new page |
| `widow_control` | bool/None | Avoid orphan/widow lines |
| `tab_stops` | TabStops | Tab stops collection |

## Run Object

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Text content of the run |
| `bold` | bool/None | Bold formatting |
| `italic` | bool/None | Italic formatting |
| `underline` | bool/None/enum | Underline style |
| `font` | Font | Character formatting object (read-only) |
| `style` | CharacterStyle/str | Applied character style |
| `_element` | CT_R | Low-level XML element |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_break()` | None | Insert line break within run |

## Font Object

Access via `run.font` or `style.font`. Read-only property on Run/Style.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str/None | Typeface name |
| `size` | Length/None | Font size |
| `bold` | bool/None | Bold |
| `italic` | bool/None | Italic |
| `underline` | bool/None/enum | Underline (True=single, WD_UNDERLINE.* for others) |
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
| `color` | ColorFormat | Font color (read-only) |

## Table, Row, Column, Cell Objects

### Table

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `rows` | _Rows | Collection of rows |
| `columns` | _Columns | Collection of columns |
| `style` | _TableStyle/str/None | Applied table style |
| `cell(row, col)` | _Cell | Cell at (row, col) zero-based |
| `add_row()` | _Row | Add row at end |
| `add_column()` | _Column | Add column at end |
| `columns` | _Columns | Columns collection |

### Row

| Property | Type | Description |
|----------|------|-------------|
| `cells` | list[_Cell] | Cells in this row |
| `grid_span` | int | Number of layout columns spanned |
| `height` | Length | Row height |
| `height_rule` | WD_ROW_HEIGHT_RULE | Height rule (EXACTLY, AT_LEAST, None) |

### Cell

| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Full text content (read/write) |
| `width` | Length | Cell width |
| `height` | Length | Cell height |
| `paragraphs` | list[Paragraph] | Paragraphs in the cell |
| `tables` | list[Table] | Nested tables in the cell |
| `vertical_alignment` | WD_CELL_VERTICAL_ALIGNMENT/None | Vertical alignment |
| `add_paragraph(text='', style=None)` | Paragraph | Add paragraph to cell |
| `iter_inner_content()` | Iterator | Yield Paragraph/Table in cell order |

## Section Object

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `start_type` | WD_SECTION_START | Section break type |
| `orientation` | WD_ORIENT | PORTRAIT or LANDSCAPE |
| `page_width` | Length | Page width |
| `page_height` | Length | Page height |
| `left_margin` | Length | Left margin |
| `right_margin` | Length | Right margin |
| `top_margin` | Length | Top margin |
| `bottom_margin` | Length | Bottom margin |
| `gutter` | Length | Gutter margin (binding space) |
| `header_distance` | Length | Distance from top edge to header |
| `footer_distance` | Length | Distance from bottom edge to footer |
| `header` | _Header | Section header (read-only) |
| `footer` | _Footer | Section footer (read-only) |

## Header and Footer Objects

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_linked_to_previous` | bool | `True` = inherits from previous section |
| `paragraphs` | list[Paragraph] | Paragraphs in header/footer |
| `tables` | list[Table] | Tables in header/footer |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_paragraph(text='', style=None)` | Paragraph | Add paragraph to header/footer |
| `add_run(text='')` | Run | (via paragraphs) Add run |

## Styles and Style Objects

### Styles Collection

| Method | Returns | Description |
|--------|---------|-------------|
| `styles[name]` | BaseStyle | Get style by name |
| `add_style(name, type)` | Style | Add custom style |
| `len(styles)` | int | Count of defined styles |
| `iter` | Iterator[BaseStyle] | Iterate all styles |
| `latent_styles` | LatentStyles | Latent styles collection (read-only) |

### BaseStyle (common to all style types)

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Style name |
| `type` | WD_STYLE_TYPE | Style type |
| `style_id` | str | Internal ID (auto-generated, avoid using) |
| `hidden` | bool/None | Hidden from UI |
| `quick_style` | bool/None | Show in style gallery |
| `priority` | int | Sort order in UI |
| `locked` | bool/None | Locked from editing |
| `unhide_when_used` | bool/None | Auto-unhide on use |
| `base_style` | BaseStyle/None | Parent style for inheritance |
| `font` | Font | Character formatting (read-only) |
| `delete()` | None | Remove style from document |

### ParagraphStyle (extends BaseStyle)

| Property | Type | Description |
|----------|------|-------------|
| `paragraph_format` | ParagraphFormat | Block formatting (read-only) |
| `next_paragraph_style` | ParagraphStyle/None | Style for next paragraph |

## TabStops and.TabStop Objects

### TabStops Collection

| Method | Returns | Description |
|--------|---------|-------------|
| `add_tab_stop(position, alignment=None, leader=None)` | TabStop | Add tab stop |
| `tab_stops[i]` | TabStop | Indexed access |
| `len(tab_stops)` | int | Count |
| `iter` | Iterator[TabStop] | Iterate |

### TabStop

| Property | Type | Description |
|----------|------|-------------|
| `position` | Length | Tab stop position |
| `alignment` | WD_TAB_ALIGNMENT | Alignment type |
| `leader` | WD_TAB_LEADER | Leader character |

## ColorFormat Object

Access via `font.color`. Read-only property.

| Property | Type | Description |
|----------|------|-------------|
| `type` | MSO_COLOR_TYPE/None | RGB, THEME, AUTO, or None |
| `rgb` | RGBColor/None | Set/get RGB color |
| `theme_color` | MSO_THEME_COLOR_INDEX/None | Set/get theme color |
