# API Reference

## Contents
- Library Access
- Parsing Functions
- Writing Functions
- Parse Options
- Write Options
- Platform-Specific Functions
  - NodeJS Streaming
  - ESM Helpers

## Library Access

Using standalone scripts, `XLSX` is added to the `window` or global object.

```javascript
// Node.js (CommonJS)
var XLSX = require("xlsx");

// Frameworks / Bundlers (ESM)
import * as XLSX from "xlsx";
```

## Parsing Functions

### `XLSX.read(data, read_opts)`

Attempts to parse `data` and return a workbook object.

**Data types for `type` option**:
- `"binary"` — binary string (default)
- `"base64"` — base64-encoded string
- `"string"` — text string (for CSV/HTML input)
- `"buffer"` — Node.js Buffer (Node.js only)
- `"array"` — Array of byte values
- `"arrayBuffer"` — ArrayBuffer (browser)

```javascript
var wb = XLSX.read(data, {type: "array"});
```

### `XLSX.readFile(filename, read_opts)`

Reads `filename` from disk and parses. Node.js only.

```javascript
var wb = XLSX.readFile("input.xlsx");
```

### Parse Options

| Option | Default | Description |
| --- | --- | --- |
| `type` | `"binary"` | Input data type |
| `cellFormula` | `true` | Parse cell formulas |
| `cellStyles` | `false` | Parse cell styles (affects hidden row/col settings) |
| `cellNF` | `false` | Parse number format strings |
| `cellDates` | `false` | Store dates as Date objects (default: number codes) |
| `bookSST` | `false` | Parse shared string table |
| `bookSheets` | `false` | Return sheet metadata instead of parsed sheets |
| `bookVBA` | `false` | Parse VBA macros |
| `dense` | `false` | Generate dense worksheet arrays |
| `password` | `null` | Password for encrypted files |
| `raw` | `false` | Return raw string values instead of parsed types |

## Writing Functions

### `XLSX.write(wb, write_opts)`

Writes the workbook `wb` and returns a formatted string or buffer.

```javascript
var buf = XLSX.write(wb, {type: "buffer", bookType: "xlsx"});
```

### `XLSX.writeXLSX(wb, write_opts)`

Explicitly writes the workbook in XLSX format.

### `XLSX.writeFile(wb, filename, write_opts)`

Writes `wb` to `filename` on disk. In browsers, forces a client-side download.

```javascript
XLSX.writeFile(wb, "output.xlsx");
```

### `XLSX.writeFileXLSX(wb, filename, write_opts)`

Explicitly writes an XLSX file.

### `XLSX.writeFileAsync(filename, wb, o, cb)`

Asynchronous file write. If `o` is omitted, the third argument is the callback.

### Write Options

| Option | Default | Description |
| --- | --- | --- |
| `type` | `"binary"` | Output format: `"binary"`, `"base64"`, `"buffer"`, `"file"` |
| `bookType` | `"xlsx"` | Output format: `"xlsx"`, `"xlsm"`, `"xlsb"`, `"xml"`, `"csv"`, `"txt"`, `"html"`, `"slk"`, `"dif"`, `"dbf"`, `"rtf"`, `"ods"`, `"fods"` |
| `bookSST` | `false` | Generate shared string table |
| `bookVBA` | `false` | Include VBA macro container |
| `cellFormula` | `"cache"` | Formula output: `"cache"` (cached), `"plain"` (raw), `false` (omit) |
| `cellDates` | `false` | Store dates as date codes instead of Date objects |
| `stringCells` | `false` | Write all values as raw strings |
| `compression` | `false` | Use compression for XML-based formats |

## Platform-Specific Functions

### NodeJS Streaming Write Functions (`XLSX.stream`)

Streaming write functions for Node.js streams:

| Function | Description |
| --- | --- |
| `XLSX.stream.to_csv(sheet, opts)` | Streams CSV rows |
| `XLSX.stream.to_html(sheet, opts)` | Streams HTML table incrementally |
| `XLSX.stream.to_json(sheet, opts)` | Streams JS objects (object-mode stream) |
| `XLSX.stream.to_xlml(book, opts)` | Streams SpreadsheetML2003 workbook |

```javascript
const ws = XLSX.utils.aoa_to_sheet(data);
const stream = XLSX.stream.to_csv(ws);
stream.pipe(fs.createWriteStream("output.csv"));
```

### ESM Helpers

The `mjs` build does not import dependencies automatically. Manually set:

```javascript
import * as cptable from "cptable";
import * as fs from "fs";

XLSX.set_cptable(cptable);  // Codepage support for XLS/text parsing
XLSX.set_fs(fs);            // Node.js ESM support for readFile/writeFile

// Optional: stream.Readable for streaming operations
XLSX.utils.set_readable(Readable);
```

## Miscellaneous

- `XLSX.version` — Library version string (`"0.20.3"`)
- `XLSX.SSF` — Embedded number formatting library (ECMA-376 format codes)
- `XLSX.CFB` — Embedded container file processing library (OLE/ZIP)
