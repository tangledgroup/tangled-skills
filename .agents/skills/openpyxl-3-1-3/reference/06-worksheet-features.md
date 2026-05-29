# Worksheet Features

## Contents
- Data Validation
- AutoFilters and Sorting
- Tables
- Comments
- Hyperlinks
- Worksheet Protection
- Print Settings
- Pivot Tables (Read Support)
- Formulas
- Defined Names
- Worksheet Properties and Views
- DateTime Handling

## Data Validation

Constraints are written to the file but not enforced by openpyxl — Excel evaluates them.

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(type="list", formula1='"Dog,Cat,Bat"', allow_blank=True)
dv.error = 'Your entry is not in the list'
dv.errorTitle = 'Invalid Entry'
dv.prompt = 'Please select from the list'
dv.promptTitle = 'List Selection'
ws.add_data_validation(dv)
dv.add('A1:A10')

# Whole number above 100
dv = DataValidation(type="whole", operator="greaterThan", formula1=100)
ws.add_data_validation(dv)
dv.add('B1:B20')

# Decimal between 0 and 1
dv = DataValidation(type="decimal", operator="between", formula1=0, formula2=1)
ws.add_data_validation(dv)

# Date validation
dv = DataValidation(type="date")
ws.add_data_validation(dv)

# Text length at most 15
dv = DataValidation(type="textLength", operator="lessThanOrEqual", formula1=15)
ws.add_data_validation(dv)

# Cell range dropdown (use quote_sheetname for spaces in names)
from openpyxl.utils import quote_sheetname
dv = DataValidation(type="list",
    formula1=f"{quote_sheetname(ws.title)}!$B$1:$B$10")
ws.add_data_validation(dv)

# Custom formula rule
dv = DataValidation(type="custom", formula1="=SOMEFORMULA")
ws.add_data_validation(dv)
```

Validations without any cell ranges are ignored when saving.

## AutoFilters and Sorting

Filters and sorts are written to the file but **not executed** — Excel applies them.

```python
from openpyxl.worksheet.filters import FilterColumn, Filters

filters = ws.auto_filter
filters.ref = "A1:B15"

col = FilterColumn(colId=0)  # Column A (zero-based index within range)
col.filters = Filters(filter=["Kiwi", "Apple", "Mango"])
filters.filterColumn.append(col)

# Add sort condition
ws.auto_filter.add_sort_condition("B2:B15")
```

### Advanced filters

```python
from openpyxl.worksheet.filters import CustomFilter, CustomFilters, StringFilter, DateGroupItem

# Custom numeric filter (value < 10 OR value > 90)
flt1 = CustomFilter(operator="lessThan", val=10)
flt2 = CustomFilter(operator="greaterThan", val=90)
cfs = CustomFilters(customFilter=[flt1, flt2])
col = FilterColumn(colId=2, customFilters=cfs)  # Third column in range
filters.filterColumn.append(col)

# Combine with AND: cfs.and_ = True

# String filter (contains, startsWith, endsWith)
fil = StringFilter("contains", "xml", exclude=True)

# Date grouping
df1 = DateGroupItem(month=3, dateTimeGrouping="month")
col.filters.dateGroupItem.append(df1)
```

StringFilter operators: `contains`, `startswith`, `endswith`, `wildcard`. Wildcards: `*` (any chars), `?` (single char), `~` (escape).

## Tables

Tables reference groups of cells with automatic headers and filters.

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

ws.append(["Fruit", "2011", "2012", "2013", "2014"])
for row in data:
    ws.append(row)

tab = Table(displayName="Table1", ref="A1:E5")
style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
tab.tableStyleInfo = style
ws.add_table(tab)
```

**Notes:** Table names must be unique. Headers and column headings must be strings. Filters are added automatically with headers. In write-only mode, add column headings manually.

### Table operations

```python
# Access tables
ws.tables["Table1"]          # By name
ws.tables["A1:D10"]         # By range
for table in ws.tables.values():
    print(table)
del ws.tables["Table1"]      # Delete
len(ws.tables)               # Count
```

## Comments

```python
from openpyxl.comments import Comment

comment = Comment("This is the comment text", "Author Name")
ws["A1"].comment = comment

# Set dimensions (in pixels)
comment.width = 300
comment.height = 50

# Convert from points to pixels
from openpyxl.utils import units
comment.width = units.points_to_pixels(300)
```

Assigning the same Comment object to multiple cells creates automatic copies. Formatting information (font, dimensions) is lost when reading existing files. Comments not supported in read-only mode.

## Hyperlinks

```python
from openpyxl.worksheet.hyperlink import Hyperlink

ws['A1'].value = "Google"
ws['A1'].hyperlink = Hyperlink(ref="https://www.google.com", tooltip="Go to Google")
```

## Worksheet Protection

Sheet protection may be enabled with or without a password. Only provides basic security — data is not encrypted.

```python
# Enable without password (users can disable freely)
ws.protection.sheet = True
# Or
ws.protection.enable()
ws.protection.disable()

# With password
ws.protection.password = 'secret'

# Granular control via SheetProtection attributes
ws.protection.selectLockedCells = False
ws.protection.formatCells = False
```

## Print Settings

### Print options

```python
ws.print_options.horizontalCentered = True
ws.print_options.verticalCentered = True
```

### Headers and footers

```python
ws.oddHeader.left.text = "Page &[Page] of &N"
ws.oddHeader.left.size = 14
ws.oddHeader.left.font = "Tahoma,Bold"
ws.oddHeader.left.color = "CC3366"

# Also: evenHeader, evenFooter, firstHeader, firstFooter
```

### Print titles and area

```python
ws.print_title_cols = 'A:B'   # Repeat columns A-B on every page
ws.print_title_rows = '1:1'   # Repeat row 1 on every page
ws.print_area = 'A1:F10'      # Only print this range
```

### Page layout

```python
ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
ws.page_setup.paperSize = ws.PAPERSIZE_A5
```

### Page breaks

```python
ws.row_breaks.add(10)    # Break before row 10
ws.column_breaks.add('F')  # Break before column F
```

## Pivot Tables (Read Support)

openpyxl preserves pivot tables when reading/writing but does not support creating them. Access via `ws._pivots`:

```python
from openpyxl import load_workbook
wb = load_workbook("campaign.xlsx")
ws = wb["Results"]
pivot = ws._pivots[0]
pivot.cache.refreshOnLoad = True
```

## Formulas

```python
# Simple formula (English names, comma-separated)
ws["A1"] = "=SUM(B1:B10)"

# Array formula (assign to top-left cell of range)
from openpyxl.worksheet.formula import ArrayFormula
ws["E2"] = ArrayFormula("E2:E11", "=SUM(C2:C11*D2:D11)")

# Check for array formulas
for cell, rng in ws.array_formulae.items():
    print(f"{cell}: {rng}")

# Check if a function is known
from openpyxl.utils import FORMULAE
print("HEX2DEC" in FORMULAE)  # True
```

openpyxl never evaluates formulas. Unknown functions need `_xlfn.` prefix.

## Defined Names

```python
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import quote_sheetname, absolute_coordinate

# Global definition
ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate('A1:A5')}"
defn = DefinedName("my_range", attr_text=ref)
wb.defined_names["my_range"] = defn

# Worksheet-scoped definition
ws.defined_names.add(DefinedName("local_name", attr_text=ref))

# Access
defn = wb.defined_names["my_range"]
for title, coord in defn.destinations:
    ws = wb[title]
    print(ws[coord])
```

Cell references in defined names must use absolute coordinates and include the worksheet name.

## Worksheet Properties and Views

```python
# Sheet properties
ws.sheet_properties.tabColor = "1072BA"
ws.sheet_properties.filterMode = False

# Page setup properties
from openpyxl.worksheet.properties import PageSetupProperties
ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True, autoPageBreaks=False)

# Outline settings
ws.sheet_properties.outlinePr.summaryBelow = False

# Worksheet view
ws.sheet_view.zoomScale = 85       # 85% zoom
ws.sheet_view.showFormulas = True
ws.sheet_view.tabSelected = True

# Freeze panes
ws.freeze_panes = 'A2'             # Freeze top row
ws.freeze_panes = 'B1'             # Freeze first column

# Group (outline) rows/columns
ws.column_dimensions.group('A', 'D', hidden=True)
ws.row_dimensions.group(1, 10, hidden=True)
```

## DateTime Handling

- Excel stores dates as serial numbers (1900 or 1904 epoch) or ISO 8601 strings
- openpyxl auto-converts between Python `datetime` and Excel formats
- No timezone support — use naive datetime objects only
- Max precision: milliseconds
- Not suitable for dates before 1900

```python
import datetime
ws['A1'] = datetime.datetime(2010, 7, 21)

# ISO 8601 storage
wb.iso_dates = True

# Check/set date system
import openpyxl.utils.datetime as dt
print(wb.epoch)  # CALENDAR_WINDOWS_1900 or CALENDAR_MAC_1904
wb.epoch = dt.CALENDAR_MAC_1904

# timedelta → stored as [h]:mm:ss format
ws['B1'] = datetime.timedelta(hours=2, minutes=30)
```
