# Performance and Modes

## Contents
- Read-Only Mode
- Write-Only Mode
- Memory Considerations
- Performance Tips

## Read-Only Mode

Use for large files where you only need to read data. Uses lazy loading with near-constant memory consumption.

```python
from openpyxl import load_workbook

wb = load_workbook("large_file.xlsx", read_only=True)
ws = wb["big_data"]

for row in ws.rows:
    for cell in row:
        print(cell.value)

wb.close()  # MUST close explicitly
```

**Key constraints:**
- Cells are `ReadOnlyCell` objects, not regular `Cell` — limited attributes
- `iter_cols()` and `ws.columns` are **not available**
- Charts, images, comments not accessible
- Must call `wb.close()` to release file handles
- Worksheet dimensions depend on what the creating application wrote; use `ws.calculate_dimension()` to check

### Fixing incorrect dimensions

Some applications set worksheet dimensions incorrectly:

```python
ws.reset_dimensions()  # Recalculate max_row and max_column
```

## Write-Only Mode

Use for generating large files with constant memory usage. Can only append rows sequentially.

```python
from openpyxl import Workbook

wb = Workbook(write_only=True)
ws = wb.create_sheet()  # Must create sheet explicitly — no default sheet

for i in range(10000):
    ws.append([i, f"row {i}", i * 2])

wb.save("large_output.xlsx")
```

**Key constraints:**
- No default worksheet — must call `create_sheet()` first
- Only `append()` for adding rows — no random cell access via `cell()` or indexing
- Can only be saved **once** — subsequent saves raise `WorkbookAlreadySaved`
- Everything before cell data (freeze panes, column widths) must be set before appending
- `iter_rows()` not available

### Styled cells in write-only mode

Use `WriteOnlyCell` for styled cells:

```python
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font
from openpyxl.comments import Comment

wb = Workbook(write_only=True)
ws = wb.create_sheet()

cell = WriteOnlyCell(ws, value="Hello World")
cell.font = Font(name='Courier', size=36)
cell.comment = Comment("A comment", "Author")

ws.append([cell, 3.14, None])
wb.save("styled_writeonly.xlsx")
```

### Setting properties before data

```python
wb = Workbook(write_only=True)
ws = wb.create_sheet()

# Set these BEFORE appending any rows
ws.freeze_panes = 'A2'
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15

# Then append data
for row in data:
    ws.append(row)

wb.save("output.xlsx")
```

## Memory Considerations

Standard mode uses approximately **50x the original file size** in memory (e.g., 2.5 GB for a 50 MB Excel file). Use read-only or write-only modes to avoid this:

| Mode | Memory | Read | Write | Features |
|------|--------|------|-------|----------|
| Standard | ~50x file size | Full | Full | All features |
| Read-only | Near constant | Limited | No | Data only, no charts/images |
| Write-only | <10 MB | No | Sequential append | Basic styling via WriteOnlyCell |

## Performance Tips

- **Install lxml** — significantly improves write performance for large files
- **Use write-only mode** when generating large files — avoids building full in-memory workbook
- **Use read-only mode** when processing large files — opens almost immediately, suitable for multiprocessing
- **Avoid iterating cells** you don't need — accessing cells creates them in memory
- **Use `values_only=True`** in `iter_rows()` when you only need data
- **Install defusedxml** when reading untrusted files to guard against XML attacks
- **Parallelize reads** — open multiple read-only instances of the same file across processes
