# Cells and Data

## Contents
- Accessing Cells
- Assigning Values
- Range Access and Iteration
- Appending Data
- Row and Column Operations
- Coordinate Utilities

## Accessing Cells

Cells are created on first access. A new worksheet contains no cells until accessed.

### Single cell by coordinate

```python
c = ws['A4']           # Returns or creates cell at A4
ws['A4'] = 4           # Direct assignment
```

### Single cell by row/column index

```python
d = ws.cell(row=4, column=2, value=10)
value = d.value
```

**Warning:** Iterating cells without assigning values creates them all in memory. Avoid scanning ranges:

```python
# BAD — creates 10,000 empty cells
for x in range(1, 101):
    for y in range(1, 101):
        ws.cell(row=x, column=y)
```

## Assigning Values

Python types are automatically converted:

```python
ws['A1'] = 'hello, world'       # str
ws['A2'] = 3.14                  # float
ws['A3'] = 42                    # int
ws['A4'] = True                  # bool

import datetime
ws['A5'] = datetime.datetime(2010, 7, 21)  # datetime → auto-formatted
```

Formulas are stored as strings (English names, comma-separated arguments):

```python
ws['A6'] = '=SUM(1, 1)'
ws['B1'] = '=VLOOKUP(A1, D:E, 2, FALSE)'
```

**Note:** openpyxl never evaluates formulas. Use English function names with commas (not semicolons).

## Range Access and Iteration

### Slicing

```python
# Cell range
cell_range = ws['A1:C2']

# Single column
colC = ws['C']

# Column range
col_range = ws['C:D']

# Single row
row10 = ws[10]

# Row range
row_range = ws[5:10]
```

### iter_rows / iter_cols

```python
# Iterate rows
for row in ws.iter_rows(min_row=1, max_col=3, max_row=2):
    for cell in row:
        print(cell)  # <Cell Sheet.A1>, <Cell Sheet.B1>, ...

# Values only
for row in ws.iter_rows(min_row=1, max_col=3, max_row=2, values_only=True):
    print(row)  # (None, None, None)
```

`iter_cols()` is not available in read-only mode.

### rows / columns properties

```python
# All rows as tuples of Cell objects
for row in ws.rows:
    for cell in row:
        print(cell.value)

# All columns — NOT available in read-only mode
for col in ws.columns:
    for cell in col:
        print(cell.value)
```

### values property

Returns just values, no Cell objects:

```python
for row in ws.values:
    for value in row:
        print(value)
```

## Appending Data

Append rows as iterables:

```python
ws.append([1, 2, 3])
ws.append(["Name", "Age", "City"])
ws.append({"A": "Alice", "B": 30})  # dict with column letters

# From a list of lists
data = [
    ["Product", "Q1", "Q2"],
    ["Widget A", 100, 150],
    ["Widget B", 80, 120],
]
for row in data:
    ws.append(row)
```

## Row and Column Operations

### Insert/delete rows and columns

```python
ws.insert_rows(7)      # Insert 1 row before row 7
ws.insert_rows(7, 3)   # Insert 3 rows before row 7
ws.delete_rows(7)       # Delete row 7
ws.delete_cols(6, 3)    # Delete columns F:H (3 cols starting at col 6)
```

**Note:** openpyxl does not update formula references, tables, or charts when rows/columns are inserted or deleted. Client code must manage dependencies.

### Move ranges

```python
# Move cells up 1 row, right 2 columns (overwrites existing cells)
ws.move_range("D4:F10", rows=-1, cols=2)

# With formula translation
ws.move_range("G4:H10", rows=1, cols=1, translate=True)
```

`translate=True` adjusts relative references in formulas within the moved range only. References from other cells are not updated.

### Merge/unmerge cells

```python
ws.merge_cells('A2:D2')
ws.unmerge_cells('A2:D2')

# Or with coordinates
ws.merge_cells(start_row=2, start_column=1, end_row=4, end_column=4)
ws.unmerge_cells(start_row=2, start_column=1, end_row=4, end_column=4)
```

All cells except the top-left are removed when merged. The top-left cell holds the value and formatting.

## Coordinate Utilities

```python
from openpyxl.utils import get_column_letter, column_index_from_string

get_column_letter(1)        # 'A'
get_column_letter(702)      # 'AAA'
column_index_from_string('A')  # 1
column_index_from_string('Z')  # 26

from openpyxl.utils import quote_sheetname, absolute_coordinate
quote_sheetname("My Sheet")   # "'My Sheet'"
absolute_coordinate('A1')     # '$A$1'
```
