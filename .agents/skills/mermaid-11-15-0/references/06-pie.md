# Pie Charts

Circular statistical graphics divided into slices to illustrate numerical proportions.

## Syntax

```
pie showData          %% Optional: show data values after legend
    title "Title"     %% Optional title
    "Label 1" : 386
    "Label 2" : 85
    "Label 3" : 15
```

- Values must be **positive numbers > 0** (zero and negative cause errors)
- Slices ordered clockwise in declaration order
- `showData` renders actual values after legend text

## Configuration

```yaml
---
config:
  pie:
    textPosition: 0.5          %% Position of labels (0.0 to 1.0, default ~0.75)
  themeVariables:
    pieOuterStrokeWidth: "5px"
    pieOuterStrokeColor: "#333"
    pieOpacity: 0.8
---
```

## Theme variables

| Variable | Description |
| --- | --- |
| `pie1`–`pie12` | Fill colors for slices (cycle after 12) |
| `pieTitleTextSize` | Title text size (default: 25px) |
| `pieTitleTextColor` | Title color |
| `pieSectionTextSize` | Section label size (default: 17px) |
| `pieSectionTextColor` | Section label color |
| `pieLegendTextSize` | Legend text size (default: 17px) |
| `pieLegendTextColor` | Legend text color |
| `pieStrokeColor` | Slice border color (default: black) |
| `pieStrokeWidth` | Slice border width (default: 2px) |
| `pieOuterStrokeWidth` | Outer circle border width (default: 2px) |
| `pieOuterStrokeColor` | Outer circle border color (default: black) |
| `pieOpacity` | Slice opacity (default: 0.7) |
