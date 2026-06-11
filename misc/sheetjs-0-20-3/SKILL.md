---
name: sheetjs-0-20-3
description: Spreadsheet data toolkit for reading, writing, and converting 40+ file formats including XLSX, CSV, JSON, HTML, ODS. Use when working with spreadsheet files, converting between data formats, exporting tabular data to Excel, or importing legacy workbook formats in browser or Node.js environments.
---

# SheetJS 0.20.3

## Overview

SheetJS Community Edition is a JavaScript spreadsheet data toolkit for reading, writing, and converting spreadsheet files across **40+ file formats**. It runs in browsers, Node.js, Deno, Bun, and other JavaScript environments. The library provides a unified in-memory data model (Common Spreadsheet Format) that abstracts away format-specific details, enabling seamless data conversion between spreadsheet formats, JSON, CSV, HTML tables, and arrays.

Key capabilities:
- **Read** XLSX, XLSB, XLS, ODS, CSV, JSON, HTML, Numbers, DBF, Lotus 1-2-3, Quattro Pro, and more
- **Write** XLSX, XLSB, XLML, CSV, TSV, HTML, RTF, SYLK, DIF, DBF, ODS, FODS
- **Convert** between any supported format via the unified CSF data model
- **Extract** data as JSON objects, arrays of arrays, CSV strings, or HTML tables
- **Export** HTML TABLE elements to XLSX files
- **All processing is local** — no data sent to third parties, no telemetry

## When to Use

- Converting between spreadsheet formats (e.g., XLS to XLSX, ODS to CSV)
- Exporting tabular data from APIs or databases to Excel files
- Importing legacy `.xls` or `.numbers` files in a web application
- Reading HTML TABLE elements and converting to spreadsheet files
- Processing CSV/TSV data with spreadsheet format support
- Batch processing multiple workbook sheets across formats
- Building spreadsheet-aware features in Node.js, Deno, Bun, or browser apps

## Core Concepts

### The Common Spreadsheet Format (CSF)

SheetJS uses a plain JavaScript object model — no classes or prototypes. This makes it compatible with Web Workers' structured clone algorithm. Every structure is a simple object with keys and values.

A **workbook** (`wb`) contains:
- `wb.SheetNames` — ordered list of sheet names
- `wb.Sheets` — object mapping sheet names to worksheet objects
- `wb.Props` / `wb.Custprops` — file properties
- `wb.Workbook` — workbook-level attributes (defined names, views, VBA)

A **worksheet** (`ws`) is a plain object where:
- Keys not starting with `!` are A1-style addresses mapping to cell objects
- `ws["!ref"]` — the used range (e.g., `"A1:C10"`)
- `ws["!data"]` — dense mode array storage (when `dense: true` option used)

A **cell** object has:
- `t` — type: `b` (boolean), `e` (error), `n` (number), `d` (date), `s` (string), `z` (stub)
- `v` — underlying value
- `z` — number format string
- `w` — formatted text
- `f` — formula as A1-style string

### Library Access

```javascript
// Browser (standalone script)
// XLSX is available as a global variable

// Node.js (CommonJS)
var XLSX = require("xlsx");

// Frameworks / Bundlers (ESM)
import * as XLSX from "xlsx";
```

### Core Workflow: Read → Transform → Write

```javascript
// 1. Read/parse a file
var wb = XLSX.read(data, {type: "array"});  // or type: "binary", "base64", "string", "buffer"

// 2. Access data
var sheetName = wb.SheetNames[0];
var ws = wb.Sheets[sheetName];

// 3. Extract data in desired format
var jsonData = XLSX.utils.sheet_to_json(ws);
var csvData = XLSX.utils.sheet_to_csv(ws);
var htmlData = XLSX.utils.sheet_to_html(ws);

// 4. Write/export
XLSX.writeFile(wb, "output.xlsx");
```

### Creating a Workbook from Scratch

```javascript
// From Array of Arrays
var ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Age"],
  ["Alice", 30],
  ["Bob", 25]
]);
var wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, "People");
XLSX.writeFile(wb, "people.xlsx");

// From Array of Objects
var ws = XLSX.utils.json_to_sheet([
  { Name: "Alice", Age: 30 },
  { Name: "Bob", Age: 25 }
]);
var wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, "People");
XLSX.writeFile(wb, "people.xlsx");
```

### Exporting HTML TABLE to XLSX

```javascript
// Create workbook from existing HTML table element
var wb = XLSX.utils.table_to_book(document.getElementById("myTable"));
XLSX.writeFile(wb, "export.xlsx");
```

## Installation

### Node.js (npm/pnpm/yarn)

```bash
npm i --save https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz
```

### Browser (Standalone Script)

```html
<script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js"></script>
```

### Deno

```typescript
import * as XLSX from "https://esm.sh/sheetjs@0.20.3/stable/xlsx/xlsx.mjs";
```

### Bun

```javascript
// Bun supports Node.js CommonJS modules directly
const XLSX = require("xlsx");
```

## Usage Examples

### Export JSON API Data to XLSX

```javascript
const response = await fetch("https://api.example.com/users");
const users = await response.json();

const ws = XLSX.utils.json_to_sheet(users);
const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, "Users");
XLSX.writeFile(wb, "users.xlsx");
```

### Read Legacy XLS File and Export to CSV

```javascript
const fileBuffer = await fs.promises.readFile("legacy.xls");
const wb = XLSX.read(fileBuffer, {type: "buffer"});

wb.SheetNames.forEach(name => {
  const ws = wb.Sheets[name];
  const csv = XLSX.utils.sheet_to_csv(ws);
  console.log(`Sheet "${name}":`, csv);
});
```

### Convert HTML Table to Spreadsheet

```javascript
// Read from DOM table
const wb = XLSX.utils.table_to_book(document.getElementById("dataTable"), {raw: true});
XLSX.writeFile(wb, "table-export.xlsx");
```

### Dense Mode for Large Worksheets

```javascript
const wb = XLSX.read(data, {type: "array", dense: true});
const ws = wb.Sheets[wb.SheetNames[0]];

// Access cell at row 5, column 2 (0-indexed)
const cell = ws["!data"][5]?.[2];
```

## Advanced Topics

**Data Model (CSF)**: Deep dive into cell, sheet, and workbook objects — [Data Model](reference/01-data-model.md)
**API Reference**: Complete function documentation for read, write, and streaming — [API Reference](reference/02-api-reference.md)
**Utilities**: sheet_to_json, sheet_to_csv, aoa_to_sheet, json_to_sheet, table_to_book and more — [Utilities](reference/03-utilities.md)
**File Formats**: Supported formats, range limits, constellation libraries — [File Formats](reference/04-file-formats.md)
