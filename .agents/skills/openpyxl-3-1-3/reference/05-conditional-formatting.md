# Conditional Formatting

## Contents
- Adding Rules to a Range
- Builtin Formats (ColorScale, IconSet, DataBar)
- Standard Rules (CellIsRule, FormulaRule)
- Expression Rules
- Highlighting Entire Rows

## Adding Rules to a Range

```python
from openpyxl.formatting.rule import ColorScaleRule

ws.conditional_formatting.add('A1:A10',
    ColorScaleRule(start_type='min', start_color='AA0000',
                   end_type='max', end_color='00AA00'))
```

Rules are applied to a cell range string. Multiple rules can target the same or different ranges.

## Builtin Formats (ColorScale, IconSet, DataBar)

### ColorScaleRule

Two or three color gradients across a range:

```python
# Two-color scale
ws.conditional_formatting.add('A1:A10',
    ColorScaleRule(start_type='min', start_color='AA0000',
                   end_type='max', end_color='00AA00'))

# Three-color scale with percentiles
ws.conditional_formatting.add('B1:B10',
    ColorScaleRule(start_type='percentile', start_value=10, start_color='AA0000',
                   mid_type='percentile', mid_value=50, mid_color='0000AA',
                   end_type='percentile', end_value=90, end_color='00AA00'))
```

Type options: `num`, `percent`, `max`, `min`, `formula`, `percentile`.

### IconSetRule

Display icons based on value thresholds:

```python
from openpyxl.formatting.rule import IconSetRule

rule = IconSetRule('5Arrows', 'percent', [10, 20, 30, 40, 50],
                   showValue=None, percent=None, reverse=None)
ws.conditional_formatting.add('A1:A20', rule)
```

Available icon sets: `3Arrows`, `3ArrowsGray`, `3Flags`, `3TrafficLights1`, `3TrafficLights2`, `3Signs`, `3Symbols`, `3Symbols2`, `4Arrows`, `4ArrowsGray`, `4RedToBlack`, `4Rating`, `4TrafficLights`, `5Arrows`, `5ArrowsGray`, `5Rating`, `5Quarters`.

### DataBarRule

In-cell bar charts showing relative magnitude:

```python
from openpyxl.formatting.rule import DataBarRule

rule = DataBarRule(start_type='percentile', start_value=10,
                   end_type='percentile', end_value=90,
                   color="FF638EC6", showValue=None)
ws.conditional_formatting.add('C1:C20', rule)
```

## Standard Rules (CellIsRule, FormulaRule)

### CellIsRule

Compare cell values against conditions:

```python
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill

red_fill = PatternFill(start_color='EE1111', end_color='EE1111', fill_type='solid')

# Less than reference cell
ws.conditional_formatting.add('C2:C10',
    CellIsRule(operator='lessThan', formula=['C$1'], stopIfTrue=True, fill=red_fill))

# Between two values
ws.conditional_formatting.add('D2:D10',
    CellIsRule(operator='between', formula=['1', '5'], stopIfTrue=True, fill=red_fill))
```

Operators: `lessThan`, `greaterThan`, `between`, `notBetween`, `equal`, `notEqual`, `containsText`, `notContains`, `beginsWith`, `endsWith`.

### FormulaRule

Arbitrary Excel formulas for conditional logic:

```python
from openpyxl.formatting.rule import FormulaRule

# Highlight blank cells
ws.conditional_formatting.add('E1:E10',
    FormulaRule(formula=['ISBLANK(E1)'], stopIfTrue=True, fill=red_fill))

# With font and border styling
from openpyxl.styles import Font, Border
my_font = Font()
my_border = Border()
ws.conditional_formatting.add('E1:E10',
    FormulaRule(formula=['E1=0'], font=my_font, border=my_border, fill=red_fill))
```

### Highlighting text

```python
from openpyxl.formatting.rule import Rule
from openpyxl.styles import Font
from openpyxl.styles.differential import DifferentialStyle

red_text = Font(color="9C0006")
red_fill = PatternFill(bgColor="FFC7CE")
dxf = DifferentialStyle(font=red_text, fill=red_fill)

rule = Rule(type="containsText", operator="containsText", text="highlight", dxf=dxf)
rule.formula = ['NOT(ISERROR(SEARCH("highlight",A1)))']
ws.conditional_formatting.add('A1:F40', rule)
```

## Expression Rules

For complex conditions across multiple columns:

```python
from openpyxl.formatting.rule import Rule
from openpyxl.styles import PatternFill
from openpyxl.styles.differential import DifferentialStyle

red_fill = PatternFill(bgColor="FFC7CE")
dxf = DifferentialStyle(fill=red_fill)

r = Rule(type="expression", dxf=dxf, stopIfTrue=True)
r.formula = ['$A2="Microsoft"']  # Absolute column, relative row
ws.conditional_formatting.add("A1:C10", r)
```

**Key:** Use absolute column reference (`$A`) and relative row number so the formula applies correctly across the range.

## stopIfTrue

Set `stopIfTrue=True` to prevent subsequent rules from being evaluated when a rule matches. Default is `False` (all rules are evaluated).
