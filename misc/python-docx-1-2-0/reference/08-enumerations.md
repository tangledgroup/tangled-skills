# Enumerations

## Contents
- Text Alignment
- Tab Stops
- Line Spacing and Underline
- Section and Page Layout
- Style Types
- Table Formatting
- Color

## Text Alignment

### WD_ALIGN_PARAGRAPH (from `docx.enum.text`)

Paragraph horizontal alignment:

| Value | Description |
|-------|-------------|
| `LEFT` (0) | Left-aligned |
| `CENTER` (1) | Centered |
| `RIGHT` (2) | Right-aligned |
| `JUSTIFY` (3) | Justified (both edges) |
| `DISTRIBUTE` (4) | Distributed spacing |
| `HIGH_ASIAN_DISTRIBUTE` (5) | High-Asian distributed |
| `MEDIAL_CENTER` (6) | Medial center |

### WD_UNDERLINE (from `docx.enum.text`)

Underline styles:

| Value | Description |
|-------|-------------|
| `SINGLE` (0) | Single line |
| `WORDS` (1) | Underline words only |
| `DOUBLE` (2) | Double line |
| `DOTTED` (4) | Dotted |
| `THICK` (5) | Thick line |
| `SINGLE_WORD` (7) | Single, words only |
| `WORD_REPEAT` (8) | Repeated word underline |
| `DOUBLE_WORD` (9) | Double, words only |
| `DASH` (10) | Dashed |
| `DOT_DASH` (12) | Dot-dash |
| `DOT_DOT_DASH` (13) | Dot-dot-dash |
| `HEAVY` (14) | Heavy line |
| `DASH_HEAVY` (15) | Dashed heavy |
| `LONG_DASH` (16) | Long dash |
| `HEAVY_DOTTED` (17) | Heavy dotted |
| `HEAVY_DOT_DASH` (18) | Heavy dot-dash |
| `HEAVY_DOT_DOT_DASH` (19) | Heavy dot-dot-dash |

## Tab Stops

### WD_TAB_ALIGNMENT (from `docx.enum.text`)

| Value | Description |
|-------|-------------|
| `CLEAR` (0) | Clear all tab stops |
| `LEFT` (1) | Left-aligned |
| `CENTER` (2) | Centered |
| `RIGHT` (3) | Right-aligned |
| `DECIMAL` (4) | Decimal point aligned |
| `BAR` (5) | Vertical bar |

### WD_TAB_LEADER (from `docx.enum.text`)

| Value | Description |
|-------|-------------|
| `NONE` (0) | Spaces (default) |
| `DOTS` (1) | Dotted line |
| `HYPHENS` (2) | Hyphen characters |
| `UNDERSCORE` (3) | Underscore characters |
| `MIDDLE_DOTS` (4) | Middle dot characters |
| `HEAVY` (5) | Solid heavy line |
| `HIDDEN` (6) | Hidden (spaces in DTP) |

## Line Spacing and Underline

### WD_LINE_SPACING (from `docx.enum.text`)

Line spacing rules:

| Value | Description |
|-------|-------------|
| `AUTO` (0) | Auto (default) |
| `AT_LEAST` (1) | At least specified value |
| `EXACTLY` (4) | Exactly specified value |
| `SINGLE` (5) | Single spacing |
| `ONE_POINT_FIVE` (6) | 1.5 line spacing |
| `DOUBLE` (7) | Double spacing |
| `MULTIPLE` (5) | Multiple of line height (set with float) |

## Section and Page Layout

### WD_SECTION_START (from `docx.enum.section`)

Section break types:

| Value | Description |
|-------|-------------|
| `CONTINUOUS` (1) | Continuous (no page break) |
| `NEW_PAGE` (2) | New page |
| `EVEN_PAGE` (3) | Next even-numbered page |
| `ODD_PAGE` (4) | Next odd-numbered page |

### WD_ORIENT (from `docx.enum.section`)

Page orientation:

| Value | Description |
|-------|-------------|
| `PORTRAIT` (0) | Portrait (default) |
| `LANDSCAPE` (1) | Landscape |

## Style Types

### WD_STYLE_TYPE (from `docx.enum.style`)

| Value | Description |
|-------|-------------|
| `NOT_USER_DEFINED` (0) | Not user-defined |
| `PARAGRAPH` (1) | Paragraph style |
| `CHARACTER` (2) | Character style |
| `TABLE` (3) | Table style |
| `NUMBERING` (4) | Numbering style |

### WD_BUILTIN_STYLE (from `docx.enum.style`)

Built-in style identifiers. Common values:

| Value | Style Name |
|-------|-----------|
| `NORMAL` | Normal |
| `HEADING_1`–`HEADING_9` | Heading 1 through 9 |
| `TITLE` | Title |
| `SUBTITLE` | Subtitle |
| `LIST_BULLET` | List Bullet |
| `LIST_NUMBER` | List Number |
| `INTENSE_QUOTE` | Intense Quote |
| `NO_SPACING` | No Spacing |
| `BODY_TEXT` | Body Text |

## Table Formatting

### WD_CELL_VERTICAL_ALIGNMENT (from `docx.enum.table`)

| Value | Description |
|-------|-------------|
| `TOP` (1) | Top-aligned |
| `CENTER` (2) | Centered vertically |
| `BOTTOM` (3) | Bottom-aligned |

### WD_ROW_HEIGHT_RULE (from `docx.enum.table`)

| Value | Description |
|-------|-------------|
| `AT_LEAST` (1) | Minimum height |
| `EXACTLY` (2) | Exact height |

### WD_TABLE_ALIGNMENT (from `docx.enum.table`)

Row/table alignment:

| Value | Description |
|-------|-------------|
| `LEFT` (0) | Left-aligned |
| `CENTER` (1) | Centered |
| `RIGHT` (2) | Right-aligned |

### WD_TABLE_DIRECTION (from `docx.enum.table`)

| Value | Description |
|-------|-------------|
| `FORWARD` (0) | Left-to-right (default) |
| `BACKWARD` (1) | Right-to-left |

## Color

### MSO_COLOR_TYPE (from `docx.enum.dml`)

Color type for `ColorFormat`:

| Value | Description |
|-------|-------------|
| `AUTO` (0) | Auto (application-determined, usually black) |
| `RGB` (1) | Explicit RGB color |
| `THEME` (2) | Theme color |

### MSO_THEME_COLOR_INDEX (from `docx.enum.dml`)

Theme color indices:

| Value | Description |
|-------|-------------|
| `NOT_BUILD_IN` (-1) | Not a built-in theme color |
| `DARK_1` (0) | Dark 1 |
| `LIGHT_1` (1) | Light 1 |
| `DARK_2` (2) | Dark 2 |
| `LIGHT_2` (3) | Light 2 |
| `ACCENT_1` (4) | Accent 1 |
| `ACCENT_2` (5) | Accent 2 |
| `ACCENT_3` (6) | Accent 3 |
| `ACCENT_4` (7) | Accent 4 |
| `ACCENT_5` (8) | Accent 5 |
| `ACCENT_6` (9) | Accent 6 |
| `HIGHLIGHT_1` (10) | Hyperlink |
| `HIGHLIGHT_2` (11) | Followed hyperlink |

### WD_COLOR_INDEX (from `docx.enum.dml`)

Legacy color index values (used in older documents):

| Value | Description |
|-------|-------------|
| `AUTO` (0) | Auto |
| `BLACK` (1) | Black |
| `WHITE` (2) | White |
| `RED` (3) | Red |
| `BRIGHTGREEN` (4) | Bright green |
| `BLUE` (5) | Blue |
| `DARKBLUE` (12) | Dark blue |
| `YELLOW` (11) | Yellow |
| ... and more palette colors |
