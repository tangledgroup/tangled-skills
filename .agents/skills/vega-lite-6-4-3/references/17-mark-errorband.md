# Errorband Mark Reference

The `errorband` composite mark renders shaded confidence bands around aggregate values. Unlike `errorbar` (discrete bars), `errorband` creates continuous filled regions.

## Basic Error Band

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error band showing confidence intervals.",
  "data": {"url": "data/cars.json"},
  "mark": {
    "type": "errorband",
    "extent": "ci",
    "borders": true
  },
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {
      "field": "Miles_per_Gallon",
      "type": "quantitative",
      "scale": {"zero": false},
      "title": "Miles per Gallon (95% CIs)"
    }
  }
}
```

## Error Band with Line Overlay

Layer a line through the center of the band:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error band with mean line.",
  "data": {"url": "data/cars.json"},
  "layer": [
    {
      "mark": {"type": "errorband", "extent": "ci"},
      "encoding": {
        "x": {"timeUnit": "yearmonth", "field": "Year"},
        "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"zero": false}}
      }
    },
    {
      "mark": "line",
      "encoding": {
        "x": {"timeUnit": "yearmonth", "field": "Year"},
        "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}
      }
    }
  ]
}
```

## Error Band with Stdev Extent

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error band with standard deviation.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorband", "extent": {"stdev": 1}},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

## Colored Error Bands

Add color grouping:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bands by origin.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorband", "extent": "ci"},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"zero": false}},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position (x typically temporal for continuous bands) |
| `color` | Band color per group |
| `opacity` | Transparency of the band fill |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `extent` | `"ci"` | Error extent (`"ci"`, `{"stdev": N}`, `{"iqr": true}`) |
| `borders` | `false` | Show border outline around the band |
| `fillOpacity` | `0.2` | Opacity of the band fill |

## Gotchas

- Errorband is a composite mark — it compiles to layered area marks showing upper/lower bounds.
- Set `"scale": {"zero": false}` on the y-axis when confidence intervals don't meaningfully include zero.
- The `borders` property adds an outline around the band, useful for visibility.
- Errorband works best with temporal x-axes where continuous bands make sense.
- For discrete categories, use `errorbar` instead of `errorband`.
