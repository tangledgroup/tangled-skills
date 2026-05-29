# Workbooks

## Contents
- Creating and Loading Workbooks
- Sheet Management
- Saving Workbooks
- Workbook Properties

## Creating and Loading Workbooks

### Create a new workbook

```python
from openpyxl import Workbook

wb = Workbook()  # Creates workbook with one active worksheet
ws = wb.active
```

### Load an existing workbook

```python
from openpyxl import load_workbook

# Default: preserves formulae
wb = load_workbook("file.xlsx")

# Read computed values instead of formulae
wb = load_workbook("file.xlsx", data_only=True)

# Preserve VBA elements (not editable, just preserved)
wb = load_workbook("file.xlsm", keep_vba=True)

# Read-only mode for large files (see 08-performance-and-modes.md)
wb = load_workbook("large.xlsx", read_only=True)

# Preserve rich-text formatting in cells
wb = load_workbook("file.xlsx", rich_text=True)

# Preserve cached data from external workbooks
wb = load_workbook("file.xlsx", keep_links=True)
```

**Loading flags:**
- `data_only` — cells with formulae show last computed value instead of formula string
- `keep_vba` — preserve Visual Basic elements (default: False, they are dropped)
- `read_only` — lazy loading, much less memory, not all features available
- `rich_text` — preserve rich-text formatting in cells (default: False)
- `keep_links` — preserve external workbook cached data

## Sheet Management

### Create worksheets

```python
# Insert at end (default)
ws1 = wb.create_sheet("Monthly")

# Insert at first position
ws2 = wb.create_sheet("Summary", 0)

# Insert at penultimate position
ws3 = wb.create_sheet("Appendix", -1)
```

New sheets get auto-names: Sheet, Sheet1, Sheet2, … Change with `ws.title`:

```python
ws.title = "New Title"
```

### Access worksheets

```python
# By name
ws = wb["New Title"]

# Active (first by default)
ws = wb.active

# All sheet names
print(wb.sheetnames)  # ['Summary', 'Monthly', 'Appendix']

# Iterate all worksheets
for sheet in wb:
    print(sheet.title)
```

### Delete and copy worksheets

```python
# Delete
del wb["Old Sheet"]

# Copy within same workbook (cells, styles, hyperlinks, comments only — not images/charts)
source = wb.active
target = wb.copy_worksheet(source)
```

**Limitations:** Cannot copy worksheets between workbooks. Cannot copy in read-only or write-only mode.

## Saving Workbooks

### Save to file

```python
wb.save("output.xlsx")
```

Overwrites without warning. Extension is not enforced, but non-standard extensions may cause issues opening in Excel.

### Save as template

```python
wb = load_workbook("document.xlsx")
wb.template = True
wb.save("template.xltx")
```

### Save as stream (for web apps)

```python
from tempfile import NamedTemporaryFile
from openpyxl import Workbook

wb = Workbook()
with NamedTemporaryFile() as tmp:
    wb.save(tmp.name)
    tmp.seek(0)
    stream = tmp.read()
```

### XLSM and VBA caveats

- Loading `.xlsm` without `keep_vba=True` drops VBA code
- Saving a non-VBA workbook as `.xlsm` produces a file Excel may reject
- Loading `.xltm` with `keep_vba=True` then saving as `.xlsm` also fails
- Match extension to content type

## Workbook Properties

### Document properties

```python
wb.properties.title = "Monthly Report"
wb.properties.author = "Data Team"
wb.properties.description = "Q4 sales data"
wb.properties.subject = "Sales"
wb.properties.keywords = "sales, quarterly"
wb.properties.category = "Reports"
```

### Custom document properties

```python
from openpyxl.packaging.custom import StringProperty, IntProperty, BoolProperty

wb.custom_doc_props.append(StringProperty(name="Department", value="Finance"))
wb.custom_doc_props.append(IntProperty(name="Version", value=2))
wb.custom_doc_props.append(BoolProperty(name="Reviewed", value=True))

# Iterate
for prop in wb.custom_doc_props.props:
    print(f"{prop.name}: {prop.value}")

# Delete
del wb.custom_doc_props["Department"]
```

### Date system (epoch)

```python
import openpyxl.utils.datetime as dt

# Check current date system
if wb.epoch == dt.CALENDAR_WINDOWS_1900:
    print("Using 1900 date system")

# Switch to Mac 1904
wb.epoch = dt.CALENDAR_MAC_1904
```

### ISO dates

```python
wb.iso_dates = True  # Store dates as ISO 8601 strings instead of serial numbers
```
