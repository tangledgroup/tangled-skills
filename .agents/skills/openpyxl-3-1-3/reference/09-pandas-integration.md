# Pandas Integration

## Contents
- Writing DataFrames to Worksheets
- Styling DataFrame Output
- Streaming DataFrames (Write-Only Mode)
- Reading Worksheets into DataFrames
- NumPy Type Support

## Writing DataFrames to Worksheets

Use `dataframe_to_rows()` to convert a DataFrame into iterable rows:

```python
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

wb = Workbook()
ws = wb.active

for r in dataframe_to_rows(df, index=True, header=True):
    ws.append(r)

wb.save("output.xlsx")
```

Parameters:
- `index=True` — include DataFrame index as first column
- `header=True` — include column names as first row

## Styling DataFrame Output

Apply the builtin `Pandas` style to highlight headers and index:

```python
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

wb = Workbook()
ws = wb.active

for r in dataframe_to_rows(df, index=True, header=True):
    ws.append(r)

# Style the first column (index) and first row (header)
for cell in ws['A'] + ws[1]:
    cell.style = 'Pandas'

wb.save("styled_output.xlsx")
```

## Streaming DataFrames (Write-Only Mode)

For large DataFrames, use write-only mode with `WriteOnlyCell` for styled headers:

```python
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.utils.dataframe import dataframe_to_rows

wb = Workbook(write_only=True)
ws = wb.create_sheet()

cell = WriteOnlyCell(ws)
cell.style = 'Pandas'

def format_first_row(row, cell):
    for c in row:
        cell.value = c
        yield cell

rows = dataframe_to_rows(df)
first_row = format_first_row(next(rows), cell)
ws.append(first_row)

for row in rows:
    row = list(row)
    cell.value = row[0]
    row[0] = cell
    ws.append(row)

wb.save("streamed_output.xlsx")
```

## Reading Worksheets into DataFrames

### Simple (no headers/index)

```python
import pandas as pd
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active
df = pd.DataFrame(ws.values)
```

### With headers and index

For files created from DataFrames (with headers and index columns):

```python
import pandas as pd
from itertools import islice
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active

data = ws.values
cols = next(data)[1:]        # Skip index column, get header
data = list(data)
idx = [r[0] for r in data]   # First column is index
data = (islice(r, 1, None) for r in data)  # Skip first column
df = pd.DataFrame(data, index=idx, columns=cols)
```

### Alternative: pandas built-in

pandas has its own Excel I/O that can use openpyxl as engine:

```python
import pandas as pd

# Read
df = pd.read_excel("data.xlsx", engine='openpyxl')

# Write (uses openpyxl internally)
df.to_excel("output.xlsx", engine='openpyxl', index=True)
```

Use `dataframe_to_rows()` when you need more control over formatting, multiple sheets, or streaming.

## NumPy Type Support

openpyxl has built-in support for NumPy types:

- `numpy.float64`, `numpy.float32` — stored as float
- `numpy.int64`, `numpy.int32` — stored as int
- `numpy.bool_` — stored as bool
- `pandas.Timestamp` — stored as datetime

NumPy arrays in DataFrames are handled automatically through `dataframe_to_rows()`.
