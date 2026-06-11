# Tables

## Contents
- Creating Tables
- Accessing Cells
- Adding Rows and Columns
- Merged Cells and Layout Grid
- Omitted Cells
- Nested Tables
- Table Styles

## Creating Tables

```python
table = document.add_table(rows=2, cols=3)
```

Creates a table with the specified dimensions at the end of the document. Optionally apply a style:

```python
table = document.add_table(rows=1, cols=3, style='LightShading-Accent1')
```

## Accessing Cells

### By index (row, col)

```python
cell = table.cell(0, 1)   # Row 0, Column 1
cell.text = 'Value'
```

Zero-based indexing. This is the simplest access method for uniform tables.

### Via rows and cells

```python
for row in table.rows:
    for cell in row.cells:
        print(cell.text)
```

Both `table.rows` and `row.cells` support indexed access and iteration.

### Via columns

```python
for col in table.columns:
    for cell in col.cells:
        print(cell.text)
```

### Counts

```python
row_count = len(table.rows)
col_count = len(table.columns)
```

## Adding Rows and Columns

### Adding rows incrementally

```python
table = document.add_table(rows=1, cols=3)

# Populate header row
heading_cells = table.rows[0].cells
heading_cells[0].text = 'Name'
heading_cells[1].text = 'Value'
heading_cells[2].text = 'Status'

# Add data rows
for name, value, status in data:
    row_cells = table.add_row().cells
    row_cells[0].text = name
    row_cells[1].text = str(value)
    row_cells[2].text = status
```

### Adding columns

```python
new_col = table.add_column()
```

Rarely needed in practice.

## Merged Cells and Layout Grid

Word tables support merged cells, which breaks the uniform grid assumption. Understanding the **layout grid** is essential for correct reading of arbitrary tables.

### The layout grid concept

Every table has an invisible uniform layout grid. Each cell occupies one or more whole layout-grid positions. A merged cell spans multiple grid positions but is a single `_Cell` object.

### How python-docx handles merged cells

By default, `row.cells` **approximates** uniform tables by repeating the merged cell's value for each layout position it occupies:

```
Visual table:          Approximated as:
+---+---+---+          +---+---+---+
|   a   | b |    ->     | a | a | b |
+---+---+---+          +---+---+---+
| c | d | e |    ->     | c | d | e |
+---+---+---+          +---+---+---+
```

This approximation works for most extraction scenarios. For exact cell boundaries, inspect the underlying XML or use `_Cell` properties directly.

## Omitted Cells

Word allows cells to be omitted from the beginning or end (but not the middle) of a row. Common in tables with row headers and column headers but no top-left cell.

```python
# Check for omitted cells
grid_cols_before = row.grid_cols_before   # Omitted at start
grid_cols_after = row.grid_cols_after     # Omitted at end
```

Omitted cells are **not** empty cells — they represent unoccupied layout positions with no `_Cell` object. When extracting data into a uniform matrix, yield empty strings for omitted positions:

```python
def iter_row_cell_texts(row):
    for _ in range(row.grid_cols_before):
        yield ""
    for cell in row.cells:
        yield cell.text
    for _ in range(row.grid_cols_after):
        yield ""
```

## Nested Tables

Table cells can contain other tables (and paragraphs). Access nested content:

### Via Cell.tables

```python
for inner_table in cell.tables:
    # Process nested table
    for row in inner_table.rows:
        for c in row.cells:
            print(c.text)
```

### Via iter_inner_content()

```python
for item in cell.iter_inner_content():
    if hasattr(item, 'text'):
        # Paragraph inside cell
        print(f"Para: {item.text}")
    else:
        # Table inside cell
        print(f"Nested table with {len(item.rows)} rows")
```

`iter_inner_content()` preserves document order of paragraphs and tables within the cell.

## Table Styles

Apply a pre-formatted Word table style by name:

```python
table.style = 'LightShading-Accent1'
```

The style name is formed by removing spaces from the name shown in Word's table style gallery. Common styles available in the default template:

- `Table Grid` — basic grid lines
- `Light Shading Accent 1`–`6` — subtle shading
- `Medium Shading 1`/`2` Accent variants — medium contrast
- `Dark List Accent 1`–`6` — high contrast
- `Colorful Grid`/`List`/`Shading` Accent variants — vibrant
- `Light Grid Accent 1`–`6` — light grid lines
- `Medium Grid 1`/`2`/`3` Accent variants — medium grid

Apply style at creation time:

```python
table = document.add_table(rows=2, cols=2, style='Table Grid')
```
