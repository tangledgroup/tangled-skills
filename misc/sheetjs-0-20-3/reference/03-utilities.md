# Utilities

## Contents
- Arrays of Data
  - Array of Arrays Input
  - Array of Objects Input
  - Array Output
- HTML
  - HTML Table Input
  - HTML Table Output
- CSV and Text
- Array of Formulae
- Workbook Helpers

Utilities are in the `XLSX.utils` object. They fall into two categories:

**Data Packaging (Input)**: Create worksheets/workbooks from rows of data
**Data Extraction (Output)**: Extract data from worksheets to friendlier structures

## Arrays of Data

### Array of Arrays Input

#### `XLSX.utils.aoa_to_sheet(aoa, opts)`

Converts an array of arrays of JS values to a worksheet.

```javascript
var ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Age"],
  ["Alice", 30],
  ["Bob", 25]
]);
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `dateNF` | `"mm/dd/yy"` | Date format in string output |
| `cellDates` | `false` | Store dates as type `d` (default: `n`) |
| `sheetStubs` | `false` | Create `z` type cells for `null` values |
| `nullError` | `false` | Emit `#NULL!` error cells for `null` |
| `UTC` | `false` | Interpret dates using UTC methods |
| `dense` | `false` | Emit dense sheets |

Values: Numbers/Booleans/Strings stored as corresponding types. Date objects → Date cells or date codes. Array holes/`undefined` skipped. `null` → stub or error (per options). Cell objects used as-is.

#### `XLSX.utils.sheet_add_aoa(ws, aoa, opts)`

Adds data from an array of arrays to an existing worksheet.

```javascript
XLSX.utils.sheet_add_aoa(ws, [["extra", 1]], {origin: "A5"});
```

**Additional option:** `origin` — cell address or `{c, r}` for starting position.

### Array of Objects Input

#### `XLSX.utils.json_to_sheet(aoo, opts)`

Converts an array of JS objects to a worksheet. First row is interpreted as headers.

```javascript
var ws = XLSX.utils.json_to_sheet([
  { Name: "Alice", Age: 30 },
  { Name: "Bob", Age: 25 }
]);
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `header` | — | Array of keys to use as columns (order matters) |
| `skipHeader` | `false` | Skip header row |
| `FS` | `","` | Field separator for array output |
| `RS` | `"\n"` | Record separator for array output |
| `range` | — | Start writing at specified range |
| `dense` | `false` | Emit dense sheets |

#### `XLSX.utils.sheet_add_json(ws, aoo, opts)`

Adds data from an array of objects to an existing worksheet.

```javascript
XLSX.utils.sheet_add_json(ws, [{Name: "Charlie", Age: 35}], {origin: "A5"});
```

### Array Output

#### `XLSX.utils.sheet_to_json(ws, opts)`

Converts a worksheet to an array of JSON objects (uses first row as headers).

```javascript
var rows = XLSX.utils.sheet_to_json(ws);
// [{Name: "Alice", Age: 30}, {Name: "Bob", Age: 25}]
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `header` | `1` | `1` = array of arrays, `"A"` = array of objects, `[...]` = custom keys |
| `raw` | `true` | Return underlying values (`false` → formatted text from `w`) |
| `defval` | — | Default value for missing cells |
| `range` | — | Limit to specified range (e.g., `"A1:C10"`) |
| `blankrows` | `true` | Include blank rows |
| `dateNF` | `"mm/dd/yy"` | Date format for string output |
| `cellDates` | `false` | Return Date objects instead of number codes |

**Header modes:**
- `header: 1` → `[["Alice", 30], ["Bob", 25]]` (array of arrays)
- `header: "A"` → `[{Name: "Alice", Age: 30}]` (array of objects, uses first row as keys)
- `header: ["First", "Years"]` → `[{First: "Alice", Years: 30}]` (custom keys)

## HTML

### HTML Table Input

#### `XLSX.utils.table_to_sheet(elt, opts)`

Converts a DOM TABLE element to a worksheet. Numbers are parsed; other data stored as strings.

```javascript
var ws = XLSX.utils.table_to_sheet(document.getElementById("myTable"));
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `raw` | — | Every cell holds raw strings |
| `dateNF` | `"m/d/yy"` | Date format for string output |
| `cellDates` | `false` | Store dates as type `d` |
| `sheetRows` | `0` | If >0, read only first N rows |
| `display` | `false` | Skip hidden rows/cells |
| `UTC` | `false` | Interpret dates as UTC |

#### `XLSX.utils.table_to_book(elt, opts)`

Converts a DOM TABLE element to a minimal workbook.

```javascript
var wb = XLSX.utils.table_to_book(document.getElementById("myTable"));
XLSX.writeFile(wb, "table-export.xlsx");
```

#### `XLSX.utils.sheet_add_dom(ws, elt, opts)`

Adds data from a DOM TABLE element to an existing worksheet.

### HTML Table Output

#### `XLSX.utils.sheet_to_html(ws, opts)`

Generates an HTML string from a worksheet.

```javascript
var html = XLSX.utils.sheet_to_html(ws, {id: "myTable"});
document.getElementById("container").innerHTML = html;
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `id` | — | Set `id` attribute on TABLE element |
| `editable` | `false` | Set `contenteditable="true"` on every TD |
| `header` | — | Override header content |
| `footer` | — | Override footer content |

Generated TD elements include data attributes:
- `data-t` — Cell type override
- `data-v` — Cell value override
- `data-z` — Number format override

## CSV and Text

#### `XLSX.utils.sheet_to_csv(ws, opts)`

Generates delimiter-separated-values output. Default field separator is comma.

```javascript
var csv = XLSX.utils.sheet_to_csv(ws);
var tsv = XLSX.utils.sheet_to_csv(ws, {FS: "\t"});
```

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `FS` | `","` | Field separator delimiter |
| `RS` | `"\n"` | Record separator delimiter |
| `dateNF` | `"mm/dd/yy"` | Date format in string output |
| `strip` | `false` | Remove trailing field separators |
| `blankrows` | `true` | Include blank lines in output |
| `skipHidden` | `false` | Skip hidden rows/columns |
| `forceQuotes` | `false` | Force quotes around all fields |

Fields containing the separator are automatically quoted. `forceQuotes` wraps all cells.

#### `XLSX.utils.sheet_to_txt(ws, opts)`

Generates UTF-16 formatted text (tab-separated by default).

```javascript
var txt = XLSX.utils.sheet_to_txt(ws);
```

Same options as `sheet_to_csv`. Output encoded in CP1200 with UTF-16 BOM if encoding supported.

## Array of Formulae

#### `XLSX.utils.sheet_to_formulae(ws)`

Generates a list of formulae or cell value assignments.

```javascript
var formulas = XLSX.utils.sheet_to_formulae(ws);
// [{c: "A1", t: "n", v: 5}, {c: "B1", f: "=SUM(A1,A2)"}]
```

## Workbook Helpers

#### `XLSX.utils.book_new()`

Creates a new empty workbook object.

```javascript
var wb = XLSX.utils.book_new();
```

#### `XLSX.utils.book_append_sheet(wb, ws, name)`

Adds a worksheet to a workbook.

```javascript
XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
```

#### `XLSX.utils.book_delete_sheet(wb, name)`

Removes a worksheet from a workbook.

#### `XLSX.utils.format_cell(cell, opts)`

Generates the text value for a cell using number formats. Returns formatted string or `null` if no format available.

```javascript
var formatted = XLSX.utils.format_cell(cell);
```

#### `XLSX.utils.sheet_set_array_formula(ws, range, formula)`

Adds an array formula to a worksheet.
