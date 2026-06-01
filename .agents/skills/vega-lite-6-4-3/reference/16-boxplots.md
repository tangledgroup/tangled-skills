# Boxplots

Boxplot is a composite mark that summarizes distributions using summary statistics: median, quartiles, whiskers, and outliers.

## Basic Syntax

```json
{
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

## Boxplot Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `extent` | number \| string | Whisker extent multiplier (default `1.5`) or `"min-max"` |
| `orient` | string | `"vertical"` or `"horizontal"` |
| `size` | number | Box width/height in pixels |
| `color` | string | Color applied to box and outlier points |
| `opacity` | number | Opacity applied to whole boxplot |

### Sub-mark Properties

Customize individual parts of the boxplot:

| Property | Type | Description |
|----------|------|-------------|
| `box` | object | Mark properties for the box (IQR region) |
| `median` | object | Mark properties for the median tick |
| `whisker` | object | Mark properties for the whisker rules |
| `outliers` | object | Mark properties for outlier points |
| `ticks` | boolean \| object | End ticks on whiskers (`true` or mark properties) |

## Boxplot Config

```json
{
  "config": {
    "boxplot": {
      "size": 14,
      "extent": 1.5,
      "box": {"fill": "#4682b4"},
      "median": {"color": "red"},
      "whisker": {"strokeWidth": 1.5},
      "outliers": {"filled": true}
    }
  }
}
```

**Note**: `color`, `opacity`, and `orient` are not supported in config.

## Boxplot Types

### Tukey Boxplot (Default)

Whiskers span `[Q1 - k * IQR, Q3 + k * IQR]`. Points beyond whiskers are outliers. Default `extent` is `1.5`.

```json
{
  "mark": {"type": "boxplot", "extent": 1.5}
}
```

### Min-Max Boxplot

Whiskers extend to min and max values. No outliers displayed.

```json
{
  "mark": {"type": "boxplot", "extent": "min-max"}
}
```

## Dimension & Orientation

### 1D Horizontal Boxplot

Continuous field on x-axis:

```json
{
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

### 1D Vertical Boxplot

Continuous field on y-axis:

```json
{
  "mark": "boxplot",
  "encoding": {
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

### 2D Boxplot (Categorical + Continuous)

Break down distributions by category:

```json
{
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Species", "type": "nominal"},
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}},
    "color": {"field": "Species", "type": "nominal", "legend": null}
  }
}
```

### Grouped Boxplots

Use `xOffset` for grouped boxplots:

```json
{
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Cylinders", "type": "nominal"},
    "y": {"field": "Acceleration", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"},
    "xOffset": {"field": "Origin", "type": "nominal"}
  }
}
```

## Customizing Parts

### Custom Median and Ticks

```json
{
  "mark": {
    "type": "boxplot",
    "extent": 1.5,
    "median": {"color": "red"},
    "ticks": true
  }
}
```

### Color and Size Encodings

`size` applies to box and median tick. `color` applies to box and outliers:

```json
{
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Body Mass (g)", "type": "quantitative"},
    "y": {"field": "Species", "type": "nominal"},
    "size": {"value": 10},
    "color": {"value": "teal"}
  }
}
```

## Tooltips

### Aggregated Tooltip (Box/Whisker)

Aggregated tooltip replaces tooltips on box and whisker marks:

```json
{
  "encoding": {
    "tooltip": {"field": "Body Mass (g)", "aggregate": "mean"}
  }
}
```

### Non-Aggregated Tooltip (Outliers)

Unaggregated tooltip replaces tooltips on outlier marks:

```json
{
  "encoding": {
    "tooltip": {"field": "Body Mass (g)", "type": "quantitative"}
  }
}
```

## Invalid Data Handling

Filter out invalid values:

```json
{
  "mark": {"type": "boxplot", "invalid": "filter"}
}
```

Other options: `"break"` (gaps), `"show"` (render with default encoding).

## Pre-Aggregated Boxplots (Layer Composition)

When data is pre-calculated, build boxplots manually with layers:

```json
{
  "data": {"values": [
    {"Species": "Adelie", "lower": 2850, "q1": 3350, "median": 3700, "q3": 4000, "upper": 4775, "outliers": []}
  ]},
  "encoding": {"y": {"field": "Species", "type": "nominal"}},
  "layer": [
    {
      "mark": "rule",
      "encoding": {
        "x": {"field": "lower", "type": "quantitative", "scale": {"zero": false}},
        "x2": {"field": "upper"}
      }
    },
    {
      "mark": {"type": "bar", "size": 14},
      "encoding": {
        "x": {"field": "q1"}, "x2": {"field": "q3"},
        "color": {"field": "Species", "type": "nominal", "legend": null}
      }
    },
    {
      "mark": {"type": "tick", "color": "white", "size": 14},
      "encoding": {"x": {"field": "median", "type": "quantitative"}}
    },
    {
      "transform": [{"flatten": ["outliers"]}],
      "mark": {"type": "point", "style": "boxplot-outliers"},
      "encoding": {"x": {"field": "outliers", "type": "quantitative"}}
    }
  ]
}
```

## Composite Mark Expansion

Under the hood, boxplot expands into a layered plot with:
- Rule marks for whiskers
- Bar mark for the box (Q1 to Q3)
- Tick mark for median
- Point marks for outliers
