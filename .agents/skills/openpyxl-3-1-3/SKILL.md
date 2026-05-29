---
name: openpyxl-3-1-3
description: Complete toolkit for openpyxl 3.1.3 providing Excel xlsx/xlsm/xltx/xltm file creation, reading, writing, styling, charts, conditional formatting, data validation, tables, filters, and Pandas integration. Use when building Python programs that need to generate, modify, or read Microsoft Excel spreadsheets programmatically.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - openpyxl
  - excel
  - xlsx
  - spreadsheet
  - python
  - data-export
category: library
external_references:
  - https://github.com/soxhub/openpyxl
  - https://openpyxl.readthedocs.io/en/stable/#documentation
---

# openpyxl 3.1.3

## Overview

openpyxl is a Python library for reading and writing Excel 2010+ files in the Office Open XML format (`.xlsx`, `.xlsm`, `.xltx`, `.xltm`). It provides full control over workbook structure, cell data, styles, charts, conditional formatting, data validation, tables, filters, images, and more.

**Key classes:**
- `Workbook` — top-level container for worksheets
- `Worksheet` — individual sheet within a workbook
- `Cell` — single cell with value, style, and formula support

openpyxl follows the OOXML specification closely. It does not evaluate formulas, filter data, or sort rows — those operations happen in Excel itself. openpyxl writes the instructions; Excel executes them.

## When to Use

- Creating Excel files from Python data (reports, exports, templates)
- Reading and extracting data from existing `.xlsx` files
- Applying styles, charts, conditional formatting, or data validation to spreadsheets
- Generating large datasets with optimized read-only or write-only modes
- Converting between Pandas DataFrames and Excel worksheets
- Adding images, comments, hyperlinks, or page setup to workbooks

## Installation / Setup

```bash
pip install openpyxl
```

Optional dependencies:
- `pillow` — required for inserting images (`pip install pillow`)
- `lxml` — improves performance when creating large files
- `defusedxml` — guards against XML-based attacks when reading untrusted files

## Usage Examples

### Create and save a workbook

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Sales"

# Write data row by row
ws.append(["Product", "Q1", "Q2", "Q3"])
ws.append(["Widget A", 100, 150, 200])
ws.append(["Widget B", 80, 120, 95])

wb.save("sales.xlsx")
```

### Read an existing workbook

```python
from openpyxl import load_workbook

wb = load_workbook("sales.xlsx")
ws = wb.active

for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)
```

### Quick chart

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.title = "Quarterly Sales"
chart.y_axis.title = "Units"
data = Reference(ws, min_col=2, min_row=1, max_row=3, max_col=4)
cats = Reference(ws, min_col=1, min_row=2, max_row=3)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, "E2")
wb.save("sales_with_chart.xlsx")
```

## Advanced Topics

**Workbooks**: Workbook creation, loading flags, sheet management, saving modes, document properties → [Workbooks](reference/01-workbooks.md)

**Cells and Data**: Cell access patterns, range iteration, data appending, row/column operations, coordinate utilities → [Cells and Data](reference/02-cells-and-data.md)

**Styles and Formatting**: Fonts, fills, borders, alignment, named styles, number formats, page setup → [Styles and Formatting](reference/03-styles-and-formatting.md)

**Charts**: All chart types (bar, line, pie, scatter, bubble, area, doughnut, radar, stock, surface), axes, layout, patterns → [Charts](reference/04-charts.md)

**Conditional Formatting**: ColorScale, IconSet, DataBar, CellIsRule, FormulaRule, expression rules → [Conditional Formatting](reference/05-conditional-formatting.md)

**Worksheet Features**: Merging, data validation, auto-filters, tables, comments, hyperlinks, protection, print settings, pivot tables, formulas, datetime handling → [Worksheet Features](reference/06-worksheet-features.md)

**Images and Drawings**: Image insertion, drawing anchors, rich text in cells → [Images and Drawings](reference/07-images-and-drawings.md)

**Performance and Modes**: Read-only mode, write-only mode, memory considerations, parallelization → [Performance and Modes](reference/08-performance-and-modes.md)

**Pandas Integration**: DataFrame to worksheet, worksheet to DataFrame, NumPy type support → [Pandas Integration](reference/09-pandas-integration.md)
