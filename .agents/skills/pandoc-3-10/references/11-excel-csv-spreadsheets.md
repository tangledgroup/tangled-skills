# Excel, CSV, and Spreadsheet Reference

Pandoc 3.10 supports reading Excel (xlsx), CSV, and TSV files as input. These are **input-only formats** — pandoc cannot write to xlsx, csv, or tsv.

## Format Direction Matrix

| Format | Input | Output | Notes |
|---|---|---|---|
| `xlsx` | Yes | No | All sheets converted; no built-in sheet selection |
| `csv` | Yes | No | Single table per file |
| `tsv` | Yes | No | Single table per file (tab-separated) |

## Excel (xlsx)

### How Sheets Are Handled

Each worksheet in an xlsx file becomes:
1. A **level-2 heading** with the sheet name: `## <sheet-name> {#sheet-N}`
2. A **pipe table** where the first row is the header and remaining rows are data
3. Empty sheets produce only the heading (no table)
4. Trailing empty rows are automatically filtered out

```
Input xlsx (3 sheets):
  Sheet "Sales"    →  ## Sales {#sheet-1}  +  pipe table
  Sheet "Inventory"→  ## Inventory {#sheet-2} + pipe table
  Sheet "Empty"    →  ## Empty {#sheet-3}     (no table)
```

### Basic Conversions

```bash
# All sheets → Markdown
pandoc -f xlsx -t markdown data.xlsx -o data.md

# All sheets → HTML
pandoc -f xlsx -t html data.xlsx -o data.html

# All sheets → LaTeX (longtable per sheet)
pandoc -f xlsx -t latex data.xlsx -o data.tex

# All sheets → plain text
pandoc -f xlsx -t plain data.xlsx

# All sheets → JSON AST
pandoc -f xlsx -t json data.xlsx | python3 -m json.tool
```

### Cell Formatting

- **Bold cells**: Rendered as `**bold**` in markdown, `<strong>` in HTML, `\textbf{}` in LaTeX
- **Italic cells**: Rendered as `*italic*` in markdown, `<em>` in HTML, `\textit{}` in LaTeX
- **Numbers**: Converted to string representation (e.g., `39767.0`, `1.0e-3`)
- **Empty cells**: Preserved as empty table cells

### Inspecting Sheets via JSON AST

```bash
# See all sheet names and structure
pandoc -f xlsx -t json data.xlsx | python3 -c "
import json, sys
doc = json.load(sys.stdin)
for block in doc['blocks']:
    if block['t'] == 'Header':
        name = ''.join(c['c'] for c in block['c'][2])
        print(f'Sheet: {name}')
    elif block['t'] == 'Table':
        print(f'  → Has table data')
"
```

### Selecting Specific Sheets (Lua Filters)

Pandoc has no built-in `--sheet` option. Use Lua filters to select sheets.

#### Filter: Keep Only Non-Empty Sheets

Save as `filter-empty-sheets.lua`:

```lua
function Pandoc(doc)
  local new_blocks = pandoc.List:new{}
  for i = 1, #doc.blocks do
    local block = doc.blocks[i]
    if block.t == "Header" and block.level == 2 then
      local next_block = doc.blocks[i + 1]
      if next_block and next_block.t == "Table" then
        new_blocks:insert(block)
        new_blocks:insert(next_block)
      end
    end
  end
  return pandoc.Pandoc(new_blocks)
end
```

```bash
pandoc -f xlsx --lua-filter=filter-empty-sheets.lua data.xlsx -t markdown
```

#### Filter: Select a Named Sheet

Save as `select-sheet.lua`:

```lua
local sheet_name = nil

function Pandoc(doc)
  local new_blocks = pandoc.List:new{}
  local in_target = false

  for i = 1, #doc.blocks do
    local block = doc.blocks[i]
    if block.t == "Header" and block.level == 2 then
      local name = pandoc.utils.stringify(block)
      if sheet_name and name == sheet_name then
        in_target = true
        new_blocks:insert(block)
      else
        in_target = false
      end
    elseif in_target then
      new_blocks:insert(block)
    end
  end

  return pandoc.Pandoc(pandoc.List:new(new_blocks))
end

Meta = function(meta)
  if meta["sheet-name"] then
    sheet_name = pandoc.utils.stringify(meta["sheet-name"])
  end
  return meta
end
```

```bash
# Extract only the "Sales" sheet
pandoc -f xlsx --lua-filter=select-sheet.lua \
  -M sheet-name="Sales" data.xlsx -t markdown
```

### Known Limitations

- **xlsx is input-only** — cannot write Excel files. For output, use markdown tables, HTML tables, or CSV via external tools.
- **No built-in sheet selection** — must use Lua filters to extract specific sheets.
- **Path bug with some generated xlsx files** — files created by openpyxl (Python) may fail with `Entry not found: xl//xl/worksheets/sheet1.xml` due to absolute paths in workbook relationships. Files from Excel/LibreOffice work correctly.
- **Merged cells not supported** — each cell is treated independently; merged cell content appears in the top-left cell only.
- **Formulas not evaluated** — only displayed values are read, not formula results.
- **Charts, images, comments ignored** — only cell data and basic formatting (bold/italic) are extracted.

## CSV Input

### Basic Usage

```bash
# CSV → Markdown (simple table)
pandoc -f csv -t markdown data.csv

# CSV → HTML
pandoc -f csv -t html data.csv

# CSV → LaTeX
pandoc -f csv -t latex data.csv
```

### Example

Input `data.csv`:
```csv
Name,Age,City,Salary
Alice,30,New York,75000
Bob,25,London,65000
Charlie,35,Tokyo,85000
```

Output (markdown):
```
  Name      Age   City       Salary
  --------- ----- ---------- --------
  Alice     30    New York   75000
  Bob       25    London     65000
  Charlie   35    Tokyo      85000
```

### Limitations

- **CSV is input-only** — cannot write CSV files.
- **Single table per file** — each CSV file produces one table.
- **No header row option** — first row is always treated as the header.
- **No delimiter option** — always comma-separated. Use TSV for tab-delimited data.

## TSV Input

### Basic Usage

```bash
# TSV → Markdown (simple table)
pandoc -f tsv -t markdown data.tsv

# TSV → HTML
pandoc -f tsv -t html data.tsv
```

TSV behaves identically to CSV but uses tab characters as delimiters instead of commas. Same limitations apply (input-only, single table, first row = header).

## Converting Tables Back to Spreadsheet-Readable Formats

Since pandoc cannot output xlsx/csv/tsv, use these alternatives:

```bash
# Markdown table → HTML table (openable in Excel/LibreOffice)
pandoc -f markdown -t html document.md -o tables.html

# Extract tables from any format as HTML
pandoc -f docx -t html document.docx -o tables.html

# Use Python to convert CSV output
pandoc -f xlsx -t json data.xlsx | python3 -c "
import json, csv, sys
doc = json.load(sys.stdin)
for block in doc['blocks']:
    if block['t'] == 'Table':
        # Extract and write as CSV
        writer = csv.writer(sys.stdout)
        # ... parse table structure ...
"

# Use LibreOffice to convert HTML to xlsx
pandoc -f xlsx -t html data.xlsx -o data.html
libreoffice --headless --convert-to xlsx data.html
```

## Conversion Quality Summary

| Source → Target | Quality | Notes |
|---|---|---|
| xlsx → markdown | Good | Tables, bold/italic preserved; all sheets included |
| xlsx → HTML | Good | Clean `<table>` elements with proper `<thead>/<tbody>` |
| xlsx → LaTeX | Good | `longtable` format, `\textbf{}` for bold cells |
| xlsx → plain text | Good | Aligned columns, formatting stripped |
| csv → markdown | Good | Simple pipe table, first row = header |
| tsv → markdown | Good | Same as CSV but tab-delimited input |
