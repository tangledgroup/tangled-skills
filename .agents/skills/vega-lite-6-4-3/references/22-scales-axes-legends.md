# Scales, Axes, Legends, and Config Reference

Scales map data values to visual positions. Axes and legends display scale information. Config sets global defaults.

## Scale Types by Data Type

| Data Type | Available Scales |
|---|---|
| `quantitative` | `linear` (default), `log`, `sqrt`, `pow`, `symlog` |
| `ordinal` | `ordinal` (default), `point`, `band`, `quantile`, `quantize`, `threshold` |
| `nominal` | `ordinal` (default), `point`, `band`, `hash` |
| `temporal` | `temporal` (default), `utc` |

## Scale Configuration

```vega-lite
"encoding": {
  "x": {
    "field": "Horsepower",
    "type": "quantitative",
    "scale": {
      "type": "log",
      "domain": [0, 300],
      "nice": true
    }
  },
  "y": {
    "field": "Miles_per_Gallon",
    "type": "quantitative",
    "scale": {"zero": false}
  }
}
```

## Common Scale Properties

| Property | Description |
|---|---|
| `type` | Scale type (`linear`, `log`, `band`, `point`, etc.) |
| `domain` | Data domain `[min, max]` or array of values |
| `range` | Visual range (usually auto-derived) |
| `zero` | Include zero in quantitative scales (default: `true`) |
| `nice` | Round domain to nice numbers (default: `true`) |
| `clamp` | Clamp values outside domain (default: `false`) |
| `padding` | Padding for band scales |
| `round` | Round output values (default: `true`) |

## Axis Configuration

```vega-lite
"encoding": {
  "x": {
    "field": "date",
    "type": "temporal",
    "axis": {
      "format": "%Y-%m",
      "labelAngle": -45,
      "title": "Date",
      "grid": false,
      "tickCount": 10
    }
  }
}
```

### Common Axis Properties

| Property | Default | Description |
|---|---|---|
| `title` | field name | Axis label text |
| `format` | auto | Tick label format (d3 format string) |
| `labelAngle` | `0` | Label rotation in degrees |
| `grid` | varies | Show grid lines (`true`/`false`) |
| `tickCount` | auto | Approximate number of ticks |
| `domain` | `true` | Show axis domain line |
| `orient` | auto | Axis position (`top`, `bottom`, `left`, `right`) |
| `tickBand` | — | Tick band alignment (`"extent"` fills full band) |

## Legend Configuration

```vega-lite
"encoding": {
  "color": {
    "field": "Origin",
    "type": "nominal",
    "legend": {
      "title": "Car Origin",
      "orient": "right",
      "labelFontSize": 12,
      "symbolSize": 100
    }
  }
}
```

### Common Legend Properties

| Property | Default | Description |
|---|---|---|
| `title` | field name | Legend title text |
| `orient` | auto | Position (`top`, `bottom`, `left`, `right`) |
| `labelFontSize` | `11` | Label font size |
| `symbolSize` | `75` | Symbol area for size legends |
| `gradientLength` | `300` | Gradient length for continuous legends |
| `gradientThickness` | `12` | Gradient thickness |
| `offset` | `0` | Offset from axis |

## Config (Global Defaults)

```vega-lite
"config": {
  "view": {"stroke": null},
  "axis": {"grid": true, "labelFontSize": 12},
  "axisX": {"domain": true},
  "axisY": {"domain": true},
  "legend": {"labelFontSize": 12},
  "style": {
    "bar": {"cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3}
  },
  "mark": {"tooltip": true}
}
```

### Config Sections

| Section | Description |
|---|---|
| `view` | View container styling |
| `axis` | Default axis properties |
| `axisX`, `axisY` | Axis-specific overrides |
| `legend` | Default legend properties |
| `style` | Style collections (mark-specific defaults) |
| `mark` | Default mark properties |
| `bar`, `line`, `point`, etc. | Mark-specific config |

## Style Config

Define named style collections:

```vega-lite
"config": {
  "style": {
    "myBar": {"cornerRadiusTopLeft": 5, "cornerRadiusTopRight": 5},
    "minimalPoint": {"filled": false, "strokeWidth": 1}
  }
}
```

Apply styles to marks:

```vega-lite
"mark": {"type": "bar", "style": "myBar"}
```

Multiple styles (later overrides earlier):

```vega-lite
"mark": {"type": "bar", "style": ["bar", "myBar"]}
```

## Resolve (Independent Scales in Composition)

In concatenated/faceted views, control scale sharing:

```vega-lite
{
  "hconcat": [...],
  "resolve": {
    "scale": {"y": "independent"},
    "legend": {"color": "independent"}
  }
}
```

Options: `"shared"` (default in facet), `"independent"`.

## Gotchas

- Set `"scale": {"zero": false}` when zero is not meaningful (stock prices, temperature differences).
- Band scales (`band`, `point`) are for ordinal/nominal data; `linear`/`log` for quantitative.
- Axis `format` uses d3 format strings: `%Y` (year), `%b` (month abbr), `.2f` (2 decimal places), `$,.0f` (currency).
- Config style names are additive — `"style": ["bar", "custom"]` applies both `config.style.bar` and `config.style.custom`.
- In facet views, scales are shared by default. Use `"resolve": {"scale": {"y": "independent"}}` for independent axes.
- Legend `orient` positions the legend relative to the plot area, not the page.
