# Data Model (Common Spreadsheet Format)

## Contents
- Cell Objects
- Sheet Objects
- Workbook Object
- Addresses and Ranges
- Spreadsheet Features Overview

## Cell Objects

Cell objects are plain JS objects with keys following this convention:

| Key | Description |
| --- | --- |
| `t` | cell type (required) |
| `v` | underlying value |
| `z` | number format string |
| `w` | formatted text |
| `f` | formula as A1-Style string |
| `F` | range of enclosing array if array formula |
| `D` | true if dynamic array formula |
| `l` | cell hyperlink / tooltip |
| `c` | cell comments |
| `r` | rich text encoding |
| `h` | HTML rendering of rich text |
| `s` | style/theme of the cell |

### Cell Types

| Type | Description |
| --- | --- |
| `b` | Boolean: JS `boolean` (`true`/`false`) |
| `e` | Error: numeric error code, `w` holds common name |
| `n` | Number: JS `number` (includes dates as number codes) |
| `d` | Date: JS `Date` object or ISO 8601 string (requires `cellDates` option) |
| `s` | Text: JS `string`, written as text |
| `z` | Stub: blank cell with metadata, ignored by utilities |

### Content vs Presentation

Spreadsheets separate content from presentation. A cell displaying `$3.50`:

```javascript
var cell = {
  t: "n",     // numeric cell
  v: 3.5,     // underlying value
  z: "$0.00", // number format
  w: "$3.50"  // formatted text
};
```

Parsers generate formatted text at parse time by default. Use options to preserve number formats.

## Sheet Objects

### Generic Sheet Object

Sheets are plain JavaScript objects. Keys not starting with `!` are A1-style addresses mapping to cell objects.

**Worksheet Range**: `ws["!ref"]` stores the A1-style range (e.g., `"A1:C10"`). Functions use this to determine the processed area. Cells outside the range are ignored.

```javascript
var ws = {
  "!ref": "A1:B2",  // range is A1:B2
  "A1": { t: "s", v: "SheetJS" },  // included
  "A3": { t: "n", v: 5433795 }     // ignored (outside range)
};
```

### Cell Storage Modes

**Sparse mode** (default): `sheet[ref]` returns the cell object at A1 address.

**Dense mode** (`dense: true` option): Cells stored in `sheet["!data"][R][C]` array (0-indexed). More memory-efficient for large worksheets in modern environments.

```javascript
// Dense mode access
var cell = ws["!data"]?.[6]?.[1];  // row 6, column 1

// Loop across worksheet with dense support
const { decode_range, encode_cell } = XLSX.utils;
function log_all_cells(ws) {
  var range = decode_range(ws["!ref"]);
  var dense = ws["!data"] != null;
  for(var R = 0; R <= range.e.r; ++R) {
    for(var C = 0; C <= range.e.c; ++C) {
      var cell = dense ? ws["!data"]?.[R]?.[C] : ws[encode_cell({r:R, c:C})];
      console.log(R, C, cell);
    }
  }
}
```

### Sheet Types

Excel supports 4 sheet types: worksheets (normal), chartsheets (charts), macrosheets (legacy macros), dialogsheets (legacy dialogs).

## Workbook Object

A workbook object `wb` represents a collection of worksheets and metadata:

| Property | Description |
| --- | --- |
| `wb.SheetNames` | Ordered list of sheet names |
| `wb.Sheets` | Object mapping sheet names to worksheet objects |
| `wb.Props` | Standard file properties (Title, Subject, Author, etc.) |
| `wb.Custprops` | Custom properties |
| `wb.Workbook` | Workbook-level attributes |
| `wb.bookType` | Determined book type when reading a file |

### Workbook-Level Attributes (`wb.Workbook`)

- **Defined Names**: `wb.Workbook.Names` — array of defined name objects
- **Workbook Views**: `wb.Workbook.Views` — array with `RTL` (right-to-left display)
- **Properties**: `wb.Workbook.WBProps` — `CodeName`, `date1904` (epoch system), `filterPrivacy`
- **Sheet Metadata**: `wb.Workbook.Sheets` — array of sheet metadata (`Hidden`, `CodeName`)

## Addresses and Ranges

### Row/Column Numbering

| Concept | Convention | Example |
| --- | --- | --- |
| Ordinal (user-facing) | 1-indexed | Row 1, Column A |
| SheetJS internal | 0-indexed | Row 0, Column 0 |

### Cell Addresses

**A1-Style**: Column label + row label. E.g., `C4` = third column, fourth row.

**SheetJS cell address object**: `{c: C, r: R}` where C and R are 0-indexed. E.g., `B5` → `{c: 1, r: 4}`.

### Cell Ranges

**A1-Style**: `"C2:D4"` = top-left to bottom-right inclusive.

**SheetJS range object**: `{s: S, e: E}` where S and E are cell address objects. E.g., `A3:B7` → `{s:{c:0, r:2}, e:{c:1, r:6}}`.

**Column range**: `{s:{c:0, r:0}, e:{c:0, r:1048575}}` for `A:A`.

**Row range**: `{s:{c:0, r:0}, e:{c:16383, r:0}}` for `1:1`.

### Address Utilities (`XLSX.utils`)

```javascript
// Column operations
var col_index = XLSX.utils.decode_col("D");   // 3
var col_name  = XLSX.utils.encode_col(3);     // "D"

// Row operations
var row_index = XLSX.utils.decode_row("4");    // 3
var row_label = XLSX.utils.encode_row(3);      // "4"

// Cell operations
var addr      = XLSX.utils.decode_cell("B5");  // {c:1, r:4}
var cell_str  = XLSX.utils.encode_cell(addr);  // "B5"

// Range operations
var range     = XLSX.utils.decode_range("A3:C10");  // {s:{c:0,r:2}, e:{c:2,r:9}}
var range_str = XLSX.utils.encode_range(range);      // "A3:C10"
```

## Spreadsheet Features Overview

SheetJS supports these spreadsheet features across file formats (details in source docs):

- **Dates and Times**: Epoch-based storage, 1900/1904 date systems
- **Formulae**: A1-style strings in `cell.f`, array formulas, dynamic arrays
- **Hyperlinks**: External links stored in `cell.l.Target`
- **Cell Comments**: Stored in `cell.c`
- **Defined Names**: Workbook-level named ranges in `wb.Workbook.Names`
- **Number Formats**: ECMA-376 format codes via `XLSX.SSF`
- **VBA and Macros**: Code names for workbooks and sheets
- **Row/Column Properties**: Width, height, hidden state
- **Sheet Visibility**: Hidden, very hidden, visible states
- **Merged Cells**: Range objects in worksheet metadata
- **File Properties**: Standard and custom document properties
