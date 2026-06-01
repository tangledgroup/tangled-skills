# Rule Marks

Rule marks represent each data point as a line segment. They span the complete width or height of a view, or can be ranged between two positions.

## Basic Syntax

```json
{
  "data": {"url": "data/stocks.csv"},
  "mark": "rule",
  "encoding": {
    "y": {"field": "price", "aggregate": "mean"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

## Rule Mark Properties

Rule marks support all standard mark properties (color, stroke, opacity, etc.) but no special properties beyond those.

## Chart Patterns

### Width-Spanning Rules (Horizontal)

Only `y` encoding — rules span full width:

```json
{
  "data": {"url": "data/stocks.csv"},
  "mark": "rule",
  "encoding": {
    "y": {"field": "price", "aggregate": "mean"},
    "size": {"value": 2},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

### Height-Spanning Rules (Vertical)

Only `x` encoding — rules span full height:

```json
{
  "mark": "rule",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "color": {"value": "red"}
  }
}
```

### Rules as Annotations

Commonly used in layer compositions to show reference lines:

```json
{
  "layer": [
    {
      "mark": "line",
      "encoding": {"x": {"field": "date"}, "y": {"field": "price"}, "color": {"field": "symbol"}}
    },
    {
      "mark": "rule",
      "encoding": {
        "y": {"aggregate": "mean", "field": "price"},
        "color": {"field": "symbol"}
      }
    }
  ]
}
```

### Global Mean on Histogram

```json
{
  "layer": [
    {
      "mark": "bar",
      "encoding": {"x": {"field": "value", "bin": true}, "y": {"aggregate": "count"}}
    },
    {
      "mark": "rule",
      "encoding": {"x": {"aggregate": "mean", "field": "value"}, "color": {"value": "red"}}
    }
  ]
}
```

### Ranged Rules (Extent Lines)

Use `x`/`x2` or `y`/`y2` for ranged rules:

```json
{
  "mark": "rule",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "min", "type": "quantitative"},
    "y2": {"field": "max"}
  }
}
```

### Error Bars with Rules

Show confidence intervals:

```json
{
  "layer": [
    {
      "mark": "point",
      "encoding": {"x": {"field": "category"}, "y": {"aggregate": "mean", "field": "value"}}
    },
    {
      "mark": "rule",
      "encoding": {
        "x": {"field": "category"},
        "y": {"aggregate": "ci0", "field": "value"},
        "y2": {"aggregate": "ci1"}
      }
    }
  ]
}
```

### Standard Deviation Error Bars

```json
{
  "layer": [
    {
      "mark": "point",
      "encoding": {"x": {"field": "category"}, "y": {"aggregate": "mean", "field": "value"}}
    },
    {
      "mark": "rule",
      "encoding": {
        "x": {"field": "category"},
        "y": {"aggregate": "stdevd", "field": "value"},
        "y2": {"aggregate": "stdevu"}
      }
    }
  ]
}
```

### Rule Config

```json
{
  "config": {
    "rule": {"strokeWidth": 2, "strokeDash": [6, 3]}
  }
}
```
