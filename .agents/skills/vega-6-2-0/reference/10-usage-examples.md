# Usage Examples

## Contents
- Simple Bar Chart
- Line Chart with Multiple Series
- Scatterplot with Color Encoding
- Interactive Tooltips
- Stacked Bar Chart
- Histogram with Bin Transform

## Simple Bar Chart

A basic bar chart showing values for categories.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 400,
  "height": 200,
  "padding": 5,
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "A", "value": 28},
        {"category": "B", "value": 55},
        {"category": "C", "value": 43},
        {"category": "D", "value": 91},
        {"category": "E", "value": 81},
        {"category": "F", "value": 53}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": "value"},
      "range": "height"
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category"},
          "width": {"scale": "xscale"},
          "y": {"scale": "yscale", "field": "value"},
          "y2": {"scale": "yscale", "value": 0},
          "fill": {"value": "steelblue"}
        },
        "hover": {
          "fill": {"value": "darkblue"}
        }
      }
    }
  ]
}
```

## Line Chart with Multiple Series

A line chart showing values over time for multiple categories.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 600,
  "height": 300,
  "padding": 5,
  "data": [
    {
      "name": "table",
      "values": [
        {"date": "2020-01-01", "category": "A", "value": 30},
        {"date": "2020-02-01", "category": "A", "value": 45},
        {"date": "2020-03-01", "category": "A", "value": 35},
        {"date": "2020-01-01", "category": "B", "value": 20},
        {"date": "2020-02-01", "category": "B", "value": 35},
        {"date": "2020-03-01", "category": "B", "value": 50}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "time",
      "domain": {"data": "table", "field": "date"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": "value"},
      "range": "height"
    },
    {
      "name": "color",
      "type": "ordinal",
      "domain": {"data": "table", "field": "category"},
      "range": {"scheme": "category10"}
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "legends": [
    {"fill": "color", "title": "Category"}
  ],
  "marks": [
    {
      "type": "line",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "date"},
          "y": {"scale": "yscale", "field": "value"},
          "stroke": {"scale": "color", "field": "category"}
        }
      }
    }
  ]
}
```

## Scatterplot with Color Encoding

A scatterplot showing relationships between two numeric fields, colored by category.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 500,
  "height": 400,
  "padding": 20,
  "data": [
    {
      "name": "table",
      "values": [
        {"x": 10, "y": 20, "category": "A"},
        {"x": 15, "y": 30, "category": "B"},
        {"x": 25, "y": 10, "category": "A"},
        {"x": 30, "y": 40, "category": "C"},
        {"x": 40, "y": 25, "category": "B"},
        {"x": 50, "y": 35, "category": "A"}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "linear",
      "domain": {"data": "table", "field": "x"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": "y"},
      "range": "height"
    },
    {
      "name": "color",
      "type": "ordinal",
      "domain": {"data": "table", "field": "category"},
      "range": {"scheme": "category20"}
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale", "title": "X Axis"},
    {"orient": "left", "scale": "yscale", "title": "Y Axis"}
  ],
  "marks": [
    {
      "type": "symbol",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "x"},
          "y": {"scale": "yscale", "field": "y"},
          "fill": {"scale": "color", "field": "category"},
          "size": {"value": 100},
          "stroke": {"value": "white"},
          "strokeWidth": {"value": 2}
        }
      }
    }
  ]
}
```

## Interactive Tooltips

A bar chart with interactive tooltips showing detailed information on hover.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 500,
  "height": 300,
  "padding": 5,
  "signals": [
    {
      "name": "tooltip",
      "value": {},
      "on": [
        {
          "events": "@rect:mouseover",
          "update": "datum"
        },
        {
          "events": "@rect:mouseout",
          "update": "{}"
        }
      ]
    }
  ],
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "A", "value": 28, "detail": "Detailed info for A"},
        {"category": "B", "value": 55, "detail": "Detailed info for B"},
        {"category": "C", "value": 43, "detail": "Detailed info for C"}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": "value"},
      "range": "height"
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "marks": [
    {
      "name": "rect",
      "type": "rect",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category"},
          "width": {"scale": "xscale"},
          "y": {"scale": "yscale", "field": "value"},
          "y2": {"scale": "yscale", "value": 0},
          "fill": {"value": "steelblue"}
        }
      }
    }
  ]
}
```

Then use the View API tooltip handler:

```javascript
view.tooltip((handler, event, item, value) => {
  if (!value.category) return;
  const text = `${value.category}: ${value.value}\n${value.detail}`;
  // Use browser's built-in tooltip
  return text;
});
```

## Stacked Bar Chart

A stacked bar chart using the `stack` transform.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 500,
  "height": 300,
  "padding": 5,
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "X", "group": "A", "value": 28},
        {"category": "X", "group": "B", "value": 15},
        {"category": "Y", "group": "A", "value": 45},
        {"category": "Y", "group": "B", "value": 30},
        {"category": "Z", "group": "A", "value": 35},
        {"category": "Z", "group": "B", "value": 20}
      ],
      "transform": [
        {
          "type": "stack",
          "field": "value",
          "groupby": ["category"],
          "sort": {"field": "group"},
          "offset": "zero"
        }
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": ["y0", "y1"]},
      "range": "height"
    },
    {
      "name": "color",
      "type": "ordinal",
      "domain": {"data": "table", "field": "group"},
      "range": {"scheme": "category20"}
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "legends": [
    {"fill": "color", "title": "Group"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category"},
          "width": {"scale": "xscale"},
          "y": {"scale": "yscale", "field": "y1"},
          "y2": {"scale": "yscale", "field": "y0"},
          "fill": {"scale": "color", "field": "group"}
        }
      }
    }
  ]
}
```

## Histogram with Bin Transform

A histogram using the `bin` transform to discretize numeric values.

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 500,
  "height": 300,
  "padding": 5,
  "data": [
    {
      "name": "source",
      "values": [4.2, 5.1, 3.8, 7.2, 6.5, 4.9, 8.1, 5.5, 3.2, 6.8,
               7.0, 4.5, 5.8, 3.9, 6.2, 7.5, 4.0, 5.0, 6.0, 8.0]
    },
    {
      "name": "binned",
      "source": "source",
      "transform": [
        {"type": "bin", "field": "data", "extent": [0, 10], "bins": 5},
        {"type": "window", "ops": ["count"], "as": ["count"]}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "linear",
      "domain": {"data": "binned", "fields": ["x0", "x1"]},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "binned", "field": "count"},
      "range": "height"
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale", "title": "Value"},
    {"orient": "left", "scale": "yscale", "title": "Count"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "binned"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "x0"},
          "width": {
            "scale": "xscale",
            "signal": "bandwidth('xscale')"
          },
          "y": {"scale": "yscale", "field": "count"},
          "y2": {"scale": "yscale", "value": 0},
          "fill": {"value": "steelblue"}
        }
      }
    }
  ]
}
```
