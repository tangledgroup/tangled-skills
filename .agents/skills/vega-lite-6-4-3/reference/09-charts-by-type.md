# Charts by Type

## Contents

- Bar Charts
- Histograms
- Scatter and Strip Plots
- Line Charts
- Area Charts
- Circular Plots (Pie / Donut)
- Table and Heatmap
- Composite Marks (Box Plot, Error Bars)
- Layered Plots
- Multi-View Displays (Facet, Concat, Repeat)
- Maps (Geographic Displays)
- Interactive Charts
- Advanced Calculations

## Bar Charts

### Simple Bar Chart

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {
    "values": [
      {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
      {"a": "D", "b": 91}, {"a": "E", "b": 81}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "a", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "b", "type": "quantitative"}
  }
}
```

### Stacked Bar Chart

```json
{
  "data": {"url": "data/seattle-weather.csv"},
  "mark": "bar",
  "encoding": {
    "x": {"timeUnit": "month", "field": "date", "type": "ordinal"},
    "y": {"aggregate": "count", "type": "quantitative"},
    "color": {"field": "weather", "type": "nominal"}
  }
}
```

Stacking is automatic for `bar` marks with an unaggregated non-position field (here `weather`).

### Grouped Bar Chart

Use `xOffset` or `yOffset` for grouping within categories:

```json
{
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"},
    {"calculate": "datum.sex == 2 ? 'Female' : 'Male'", "as": "gender"}],
  "width": {"step": 17},
  "mark": "bar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "sum", "field": "people"},
    "xOffset": {"field": "gender", "type": "nominal"},
    "color": {"field": "gender", "type": "nominal"}
  }
}
```

### Gantt Chart (Ranged Bars)

Use `x` and `x2` for start/end ranges:

```json
{
  "data": {
    "values": [
      {"task": "A", "start": 1, "end": 3},
      {"task": "B", "start": 3, "end": 8},
      {"task": "C", "start": 8, "end": 10}
    ]
  },
  "mark": "bar",
  "encoding": {
    "y": {"field": "task", "type": "ordinal"},
    "x": {"field": "start", "type": "quantitative"},
    "x2": {"field": "end"}
  }
}
```

### Bar Chart with Labels

Layer a `text` mark over `bar`:

```json
{
  "data": {
    "values": [{"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43}]
  },
  "encoding": {
    "y": {"field": "a", "type": "nominal"},
    "x": {"field": "b", "type": "quantitative", "scale": {"domain": [0, 60]}}
  },
  "layer": [
    {"mark": "bar"},
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {"text": {"field": "b", "type": "quantitative"}}
    }
  ]
}
```

## Histograms

### Basic Histogram

```json
{
  "data": {"url": "data/movies.json"},
  "mark": "bar",
  "encoding": {
    "x": {"bin": true, "field": "IMDB Rating"},
    "y": {"aggregate": "count"}
  }
}
```

### Log-Scaled Histogram

Use `calculate` transform with `log`, then bin:

```json
{
  "data": {
    "values": [{"x": 0.01}, {"x": 0.1}, {"x": 1}, {"x": 10}, {"x": 100}, {"x": 500}]
  },
  "transform": [
    {"calculate": "log(datum.x)/log(10)", "as": "log_x"},
    {"bin": true, "field": "log_x", "as": ["bin_start", "bin_end"]},
    {"calculate": "pow(10, datum.bin_start)", "as": "x1"},
    {"calculate": "pow(10, datum.bin_end)", "as": "x2"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "x1", "scale": {"type": "log", "base": 10}},
    "x2": {"field": "x2"},
    "y": {"aggregate": "count"}
  }
}
```

### 2D Histogram Heatmap

```json
{
  "data": {"url": "data/movies.json"},
  "transform": [
    {"filter": {"and": [{"field": "IMDB Rating", "valid": true},
                        {"field": "Rotten Tomatoes Rating", "valid": true}]}}
  ],
  "mark": "rect",
  "width": 300, "height": 200,
  "encoding": {
    "x": {"bin": {"maxbins": 60}, "field": "IMDB Rating", "type": "quantitative"},
    "y": {"bin": {"maxbins": 40}, "field": "Rotten Tomatoes Rating", "type": "quantitative"},
    "color": {"aggregate": "count", "type": "quantitative"}
  },
  "config": {"view": {"stroke": "transparent"}}
}
```

## Scatter and Strip Plots

### Scatter Plot

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Bubble Plot

Add `size` channel:

```json
{
  "data": {"url": "data/gapminder-health-income.csv"},
  "width": 500, "height": 300,
  "params": [{"name": "view", "select": "interval", "bind": "scales"}],
  "mark": "circle",
  "encoding": {
    "x": {"field": "income", "scale": {"type": "log"}},
    "y": {"field": "health", "type": "quantitative", "scale": {"zero": false}},
    "size": {"field": "population", "type": "quantitative"},
    "color": {"value": "#000"}
  }
}
```

### Strip Plot (Tick Mark)

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Cylinders", "type": "ordinal"}
  }
}
```

## Line Charts

### Basic Line Chart

```json
{
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

### Multi-Series Line Chart

Use `color` channel for grouping:

```json
{
  "data": {"url": "data/stocks.csv"},
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

### Slope Graph

```json
{
  "data": {"url": "data/barley.json"},
  "mark": "line",
  "width": {"step": 50},
  "encoding": {
    "x": {"field": "year", "type": "ordinal", "scale": {"padding": 0.5}},
    "y": {"aggregate": "median", "field": "yield", "type": "quantitative"},
    "color": {"field": "site", "type": "nominal"}
  }
}
```

### Trail Chart (Varying Stroke Width)

Use `trail` mark instead of `line` for varying size:

```json
{
  "data": {"url": "data/stocks.csv"},
  "mark": "trail",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "size": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

## Area Charts

### Basic Area Chart

```json
{
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date", "axis": {"format": "%Y"}},
    "y": {"aggregate": "sum", "field": "count"},
    "color": {"field": "series", "scale": {"scheme": "category20b"}}
  }
}
```

### Stacked Area Chart

Same as basic — stacking is automatic with unaggregated `color` field.

### Streamgraph

Use `stack: "center"`:

```json
{
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count", "stack": "center"},
    "color": {"field": "series"}
  }
}
```

### Density Plot

```json
{
  "data": {"url": "data/movies.json"},
  "width": 400, "height": 100,
  "transform": [{"density": "IMDB Rating", "bandwidth": 0.3}],
  "mark": "area",
  "encoding": {
    "x": {"field": "value", "title": "IMDB Rating", "type": "quantitative"},
    "y": {"field": "density", "type": "quantitative"}
  }
}
```

## Circular Plots (Pie / Donut)

### Pie Chart

```json
{
  "data": {
    "values": [
      {"category": "A", "value": 4}, {"category": "B", "value": 6},
      {"category": "C", "value": 10}, {"category": "D", "value": 3}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Donut Chart

Set `innerRadius`:

```json
{
  "data": {
    "values": [
      {"category": "A", "value": 4}, {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "mark": {"type": "arc", "innerRadius": 50},
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Pie Chart with Labels

Layer `text` mark with polar `radius`:

```json
{
  "data": {
    "values": [
      {"category": "a", "value": 4}, {"category": "b", "value": 6},
      {"category": "c", "value": 10}
    ]
  },
  "encoding": {
    "theta": {"field": "value", "type": "quantitative", "stack": true},
    "color": {"field": "category", "type": "nominal", "legend": null}
  },
  "layer": [
    {"mark": {"type": "arc", "outerRadius": 80}},
    {
      "mark": {"type": "text", "radius": 90},
      "encoding": {"text": {"field": "category", "type": "nominal"}}
    }
  ]
}
```

## Table and Heatmap

### Heatmap

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "y": {"field": "Origin", "type": "nominal"},
    "x": {"field": "Cylinders", "type": "ordinal"},
    "color": {"aggregate": "mean", "field": "Horsepower"}
  },
  "config": {"axis": {"grid": true, "tickBand": "extent"}}
}
```

### Weather Heatmap (Temporal)

```json
{
  "data": {"url": "data/weather.csv"},
  "mark": "rect",
  "encoding": {
    "y": {"timeUnit": "month", "field": "date", "type": "ordinal"},
    "x": {"timeUnit": "day", "field": "date", "type": "ordinal"},
    "color": {"aggregate": "mean", "field": "temp_max"}
  },
  "config": {"view": {"stroke": null}}
}
```

## Composite Marks

### Box Plot

```json
{
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Species", "type": "nominal"},
    "color": {"field": "Species", "type": "nominal", "legend": null},
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

### Error Bars with Confidence Interval

Layer `point` + `errorbar`:

```json
{
  "data": {"url": "data/barley.json"},
  "encoding": {"y": {"field": "variety", "type": "ordinal"}},
  "layer": [
    {
      "mark": {"type": "point", "filled": true},
      "encoding": {
        "x": {"aggregate": "mean", "field": "yield", "type": "quantitative",
              "scale": {"zero": false}, "title": "Barley Yield"},
        "color": {"value": "black"}
      }
    },
    {
      "mark": {"type": "errorbar", "extent": "ci"},
      "encoding": {
        "x": {"field": "yield", "type": "quantitative", "title": "Barley Yield"}
      }
    }
  ]
}
```

## Layered Plots

### Candlestick Chart

Layer `rule` (high-low wick) + `bar` (open-close body):

```json
{
  "data": {"url": "data/ohlc.json"},
  "width": 400,
  "encoding": {
    "x": {"field": "date", "type": "temporal", "axis": {"format": "%m/%d", "labelAngle": -45}},
    "y": {"type": "quantitative", "scale": {"zero": false}},
    "color": {
      "condition": {"test": "datum.open < datum.close", "value": "#06982d"},
      "value": "#ae1325"
    }
  },
  "layer": [
    {"mark": "rule", "encoding": {"y": {"field": "low"}, "y2": {"field": "high"}}},
    {"mark": "bar", "encoding": {"y": {"field": "open"}, "y2": {"field": "close"}}}
  ]
}
```

### Dual-Axis Chart

Use `resolve: {"scale": {"y": "independent"}}`:

```json
{
  "data": {"url": "data/weather.csv"},
  "transform": [{"filter": "datum.location == \"Seattle\""}],
  "encoding": {"x": {"timeUnit": "month", "field": "date", "axis": {"format": "%b"}}},
  "layer": [
    {
      "mark": {"type": "area", "opacity": 0.3, "color": "#85C5A6"},
      "encoding": {
        "y": {"aggregate": "average", "field": "temp_max", "scale": {"domain": [0, 30]},
              "title": "Temp (°C)", "axis": {"titleColor": "#85C5A6"}},
        "y2": {"aggregate": "average", "field": "temp_min"}
      }
    },
    {
      "mark": {"type": "line", "stroke": "#85A9C5", "interpolate": "monotone"},
      "encoding": {
        "y": {"aggregate": "average", "field": "precipitation",
              "title": "Precip (in)", "axis": {"titleColor": "#85A9C5"}}
      }
    }
  ],
  "resolve": {"scale": {"y": "independent"}}
}
```

## Multi-View Displays

### Faceted (Trellis) Scatter Plot

```json
{
  "data": {"url": "data/movies.json"},
  "mark": "point",
  "encoding": {
    "facet": {"field": "MPAA Rating", "type": "ordinal", "columns": 2},
    "x": {"field": "Worldwide Gross", "type": "quantitative"},
    "y": {"field": "US DVD Sales", "type": "quantitative"}
  }
}
```

### Trellis Bar Chart (Row Facet)

```json
{
  "data": {"url": "data/population.json"},
  "transform": [
    {"filter": "datum.year == 2000"},
    {"calculate": "datum.sex == 2 ? 'Female' : 'Male'", "as": "gender"}
  ],
  "width": {"step": 17},
  "mark": "bar",
  "encoding": {
    "row": {"field": "gender"},
    "y": {"aggregate": "sum", "field": "people"},
    "x": {"field": "age"},
    "color": {"field": "gender", "scale": {"range": ["#675193", "#ca8861"]}}
  }
}
```

### Vertical Concatenation

```json
{
  "data": {"url": "data/weather.csv"},
  "transform": [{"filter": "datum.location === 'Seattle'"}],
  "vconcat": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"timeUnit": "month", "field": "date", "type": "ordinal"},
        "y": {"aggregate": "mean", "field": "precipitation"}
      }
    },
    {
      "mark": "point",
      "encoding": {
        "x": {"field": "temp_min", "bin": true},
        "y": {"field": "temp_max", "bin": true},
        "size": {"aggregate": "count"}
      }
    }
  ]
}
```

### Repeat (Column)

```json
{
  "data": {"url": "data/movies.json"},
  "repeat": {"column": ["US Gross", "Worldwide Gross"]},
  "spec": {
    "mark": "bar",
    "encoding": {
      "x": {"bin": true, "field": {"repeat": "column"}},
      "y": {"aggregate": "count"}
    }
  }
}
```

### Repeat (Layer)

```json
{
  "data": {"url": "data/movies.json"},
  "repeat": {"layer": ["US Gross", "Worldwide Gross"]},
  "spec": {
    "mark": "line",
    "encoding": {
      "x": {"bin": true, "field": "IMDB Rating", "type": "quantitative"},
      "y": {"aggregate": "mean", "field": {"repeat": "layer"}, "type": "quantitative"},
      "color": {"datum": {"repeat": "layer"}, "type": "nominal"}
    }
  }
}
```

### Marginal Histograms (Nested Concat)

```json
{
  "data": {"url": "data/movies.json"},
  "spacing": 15, "bounds": "flush",
  "vconcat": [
    {
      "mark": "bar", "height": 60,
      "encoding": {
        "x": {"bin": true, "field": "IMDB Rating", "axis": null},
        "y": {"aggregate": "count", "scale": {"domain": [0, 1000]}}
      }
    },
    {
      "spacing": 15, "bounds": "flush",
      "hconcat": [
        {
          "mark": "rect",
          "encoding": {
            "x": {"bin": true, "field": "IMDB Rating"},
            "y": {"bin": true, "field": "Rotten Tomatoes Rating"},
            "color": {"aggregate": "count"}
          }
        },
        {
          "mark": "bar", "width": 60,
          "encoding": {
            "y": {"bin": true, "field": "Rotten Tomatoes Rating", "axis": null},
            "x": {"aggregate": "count", "scale": {"domain": [0, 1000]}}
          }
        }
      ]
    }
  ],
  "config": {"view": {"stroke": "transparent"}}
}
```

## Maps (Geographic Displays)

### Choropleth Map

```json
{
  "width": 500, "height": 300,
  "data": {
    "url": "data/us-10m.json",
    "format": {"type": "topojson", "feature": "counties"}
  },
  "transform": [
    {
      "lookup": "id",
      "from": {
        "data": {"url": "data/unemployment.tsv"},
        "key": "id",
        "fields": ["rate"]
      }
    }
  ],
  "projection": {"type": "albersUsa"},
  "mark": "geoshape",
  "encoding": {
    "color": {"field": "rate", "type": "quantitative"}
  }
}
```

### Dot Map (One Point per Location)

```json
{
  "width": 500, "height": 300,
  "data": {"url": "data/zipcodes.csv"},
  "transform": [{"calculate": "substring(datum.zip_code, 0, 1)", "as": "digit"}],
  "projection": {"type": "albersUsa"},
  "mark": "circle",
  "encoding": {
    "longitude": {"field": "longitude", "type": "quantitative"},
    "latitude": {"field": "latitude", "type": "quantitative"},
    "size": {"value": 1},
    "color": {"field": "digit", "type": "nominal"}
  }
}
```

### Layered Map (Geoshape + Points)

```json
{
  "width": 500, "height": 300,
  "layer": [
    {
      "data": {"url": "data/us-10m.json", "format": {"type": "topojson", "feature": "states"}},
      "projection": {"type": "albersUsa"},
      "mark": {"type": "geoshape", "fill": "lightgray", "stroke": "white"}
    },
    {
      "data": {"url": "data/airports.csv"},
      "projection": {"type": "albersUsa"},
      "mark": "circle",
      "encoding": {
        "longitude": {"field": "longitude", "type": "quantitative"},
        "latitude": {"field": "latitude", "type": "quantitative"},
        "size": {"value": 10},
        "color": {"value": "steelblue"}
      }
    }
  ]
}
```

## Interactive Charts

### Brush Highlight

```json
{
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "brush", "select": "interval",
     "value": {"x": [55, 160], "y": [13, 37]}}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "brush", "field": "Cylinders", "type": "ordinal"},
      "value": "grey"
    }
  }
}
```

### Hover Highlight with Click Selection

```json
{
  "data": {
    "values": [
      {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43}
    ]
  },
  "params": [
    {"name": "highlight", "select": {"type": "point", "on": "pointerover"}},
    {"name": "select", "select": "point"}
  ],
  "mark": {"type": "bar", "fill": "#4C78A8", "stroke": "black"},
  "encoding": {
    "x": {"field": "a", "type": "ordinal"},
    "y": {"field": "b", "type": "quantitative"},
    "fillOpacity": {"condition": {"param": "select", "value": 1}, "value": 0.3},
    "strokeWidth": {
      "condition": [
        {"param": "select", "empty": false, "value": 2},
        {"param": "highlight", "empty": false, "value": 1}
      ],
      "value": 0
    }
  },
  "config": {"scale": {"bandPaddingInner": 0.2}}
}
```

### Pan and Zoom

```json
{
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "grid", "select": "interval", "bind": "scales"}
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative", "scale": {"domain": [75, 150]}},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"domain": [20, 40]}},
    "size": {"field": "Cylinders", "type": "quantitative"}
  }
}
```

### Crossfilter (Multi-View Filtering)

```json
{
  "data": {"url": "data/flights-2k.json", "format": {"parse": {"date": "date"}}},
  "transform": [{"calculate": "hours(datum.date)", "as": "time"}],
  "repeat": {"column": ["distance", "delay", "time"]},
  "spec": {
    "layer": [
      {
        "params": [
          {"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}
        ],
        "transform": [{"filter": {"param": "brush"}}],
        "mark": "bar",
        "encoding": {
          "x": {"field": {"repeat": "column"}, "bin": {"maxbins": 20}},
          "y": {"aggregate": "count", "axis": null}
        }
      }
    ]
  }
}
```

### Dynamic Color Legend

```json
{
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "filter", "select": {"type": "point", "fields": ["Origin"]}, "bind": "legend"}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "filter", "field": "Origin", "type": "nominal"},
      "value": "#ddd"
    }
  }
}
```

## Advanced Calculations

### Waterfall Chart

Uses `window` transform for running totals:

```json
{
  "data": {
    "values": [
      {"label": "Begin", "amount": 4000},
      {"label": "Jan", "amount": 1707}, {"label": "Feb", "amount": -1425},
      {"label": "Mar", "amount": -1030}, {"label": "Apr", "amount": 1812}
    ]
  },
  "width": 800, "height": 450,
  "transform": [
    {"window": [{"op": "sum", "field": "amount", "as": "sum"}]},
    {"window": [{"op": "lead", "field": "label", "as": "lead"}]},
    {"calculate": "datum.lead === null ? datum.label : datum.lead", "as": "lead"},
    {"calculate": "datum.label === 'End' ? 0 : datum.sum - datum.amount", "as": "previous_sum"},
    {"calculate": "datum.label === 'End' ? datum.sum : datum.amount", "as": "amount"}
  ],
  "encoding": {
    "x": {"field": "label", "type": "ordinal", "sort": null, "axis": {"labelAngle": 0}}
  },
  "layer": [
    {
      "mark": {"type": "bar", "size": 45},
      "encoding": {
        "y": {"field": "previous_sum", "type": "quantitative"},
        "y2": {"field": "sum"},
        "color": {
          "condition": [
            {"test": "datum.label === 'Begin' || datum.label === 'End'", "value": "#f7e0b6"},
            {"test": "datum.sum < datum.previous_sum", "value": "#f78a64"}
          ],
          "value": "#93c4aa"
        }
      }
    },
    {
      "mark": {"type": "text", "fontWeight": "bold", "baseline": "middle"},
      "encoding": {
        "y": {"field": "sum", "type": "quantitative"},
        "text": {"field": "sum", "type": "nominal"}
      }
    }
  ]
}
```

### Parallel Coordinate Plot

Uses `fold` + `joinaggregate` to normalize multiple dimensions:

```json
{
  "data": {"url": "data/penguins.json"},
  "width": 600, "height": 300,
  "transform": [
    {"filter": "datum['Beak Length (mm)']"},
    {"window": [{"op": "count", "as": "index"}]},
    {"fold": ["Beak Length (mm)", "Beak Depth (mm)", "Flipper Length (mm)", "Body Mass (g)"]},
    {"joinaggregate": [
      {"op": "min", "field": "value", "as": "min"},
      {"op": "max", "field": "value", "as": "max"}
    ], "groupby": ["key"]},
    {"calculate": "(datum.value - datum.min) / (datum.max - datum.min)", "as": "norm_val"}
  ],
  "layer": [
    {
      "mark": {"type": "rule", "color": "#ccc"},
      "encoding": {"detail": {"aggregate": "count"}, "x": {"field": "key"}}
    },
    {
      "mark": "line",
      "encoding": {
        "color": {"field": "Species", "type": "nominal"},
        "detail": {"field": "index", "type": "nominal"},
        "opacity": {"value": 0.3},
        "x": {"field": "key", "type": "nominal"},
        "y": {"field": "norm_val", "type": "quantitative", "axis": null}
      }
    }
  ],
  "config": {
    "axisX": {"domain": false, "labelAngle": 0, "tickColor": "#ccc", "title": null},
    "view": {"stroke": null}
  }
}
```

### Percentage of Total (Join Aggregate)

```json
{
  "data": {"url": "data/cars.json"},
  "transform": [
    {"joinaggregate": [{"op": "count", "as": "total"}]},
    {"calculate": "100 * 1 / datum.total", "as": "percent"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"field": "percent", "type": "quantitative", "title": "% of Total"}
  }
}
```

### Difference from Average

```json
{
  "data": {"url": "data/barley.json"},
  "transform": [
    {"joinaggregate": [{"op": "mean", "field": "yield", "as": "avgYield"}]},
    {"calculate": "datum.yield - datum.avgYield", "as": "diff"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "site", "type": "nominal"},
    "y": {"field": "diff", "type": "quantitative", "title": "Difference from Average"}
  }
}
```

### Top-K with Window Rank

```json
{
  "data": {"url": "data/cars.json"},
  "transform": [
    {
      "aggregate": [{"op": "count", "as": "count"}],
      "groupby": ["Origin"]
    },
    {"window": [{"op": "rank", "field": "count", "as": "rank"}]},
    {"filter": "datum.rank <= 3"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"field": "count", "type": "quantitative"}
  }
}
```

### Linear Regression Overlay

```json
{
  "data": {"url": "data/cars.json"},
  "layer": [
    {"mark": "point", "encoding": {
      "x": {"field": "Horsepower", "type": "quantitative"},
      "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
    }},
    {
      "mark": "line",
      "transform": [
        {"regression": "Miles_per_Gallon", "on": "Horsepower", "method": "linear"}
      ],
      "encoding": {
        "x": {"field": "Horsepower", "type": "quantitative"},
        "y": {"field": "regression_Miles_per_Gallon", "type": "quantitative"}
      }
    }
  ]
}
```

### QQ Plot (Quantile-Quantile)

```json
{
  "data": {"url": "data/movies.json"},
  "transform": [
    {"quantile": "IMDB Rating", "as": ["q1", "v1"]},
    {"quantile": "Rotten Tomatoes Rating", "as": ["q2", "v2"]}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "v1", "type": "quantitative", "title": "IMDB Rating Quantile"},
    "y": {"field": "v2", "type": "quantitative", "title": "Rotten Tomatoes Quantile"}
  }
}
```

### Ternary Chart

Three-variable composition chart using calculated positions:

```json
{
  "data": {"url": "data/penguins.json"},
  "transform": [
    {"filter": "datum['Culmen Length (mm)']"},
    {"calculate": "datum['Culmen Length (mm)'] / (datum['Culmen Length (mm)'] + datum['Culmen Depth (mm)'] + datum['Flipper Length (mm)'])", "as": "x"},
    {"calculate": "datum['Culmen Depth (mm)'] / (datum['Culmen Length (mm)'] + datum['Culmen Depth (mm)'] + datum['Flipper Length (mm)'])", "as": "y"}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "x", "type": "quantitative", "scale": {"domain": [0, 1]}},
    "y": {"field": "y", "type": "quantitative", "scale": {"domain": [0, 1]}},
    "color": {"field": "Species", "type": "nominal"}
  }
}
```
