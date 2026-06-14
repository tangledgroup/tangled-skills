# Geoshape Mark Reference

The `geoshape` mark renders geographic features from TopoJSON or GeoJSON data. Used for choropleth maps, regional visualizations, and spatial overlays.

## Choropleth Map (US Counties)

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 500,
  "height": 300,
  "description": "Choropleth of US county unemployment rates.",
  "data": {
    "url": "data/us-10m.json",
    "format": {"type": "topojson", "feature": "counties"}
  },
  "transform": [{
    "lookup": "id",
    "from": {
      "data": {"url": "data/unemployment.tsv"},
      "key": "id",
      "fields": ["rate"]
    }
  }],
  "projection": {"type": "albersUsa"},
  "mark": "geoshape",
  "encoding": {
    "color": {"field": "rate", "type": "quantitative"}
  }
}
```

## World Map with Projection

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 500,
  "height": 300,
  "description": "World map with equirectangular projection.",
  "data": {
    "url": "data/world-110m.json",
    "format": {"type": "topojson", "feature": "countries"}
  },
  "projection": {"type": "equirectangular"},
  "mark": "geoshape",
  "encoding": {
    "color": {"value": "#ccc"},
    "stroke": {"value": "#fff"}
  }
}
```

## Map with Point Overlays

Layer point marks on a geoshape base:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 500,
  "height": 300,
  "description": "Map with earthquake points.",
  "layer": [
    {
      "data": {
        "url": "data/world-110m.json",
        "format": {"type": "topojson", "feature": "countries"}
      },
      "projection": {"type": "equirectangular"},
      "mark": "geoshape",
      "encoding": {
        "color": {"value": "#eee"},
        "stroke": {"value": "#ccc"}
      }
    },
    {
      "data": {"url": "data/earthquakes.tsv"},
      "projection": {"type": "equirectangular"},
      "mark": "circle",
      "encoding": {
        "longitude": {"field": "Longitude", "type": "quantitative"},
        "latitude": {"field": "Latitude", "type": "quantitative"},
        "size": {"field": "Magnitude", "type": "quantitative"},
        "color": {"field": "Magnitude", "type": "quantitative"}
      }
    }
  ]
}
```

## Graticule (Grid Lines)

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "width": 500,
  "height": 300,
  "description": "Graticule grid overlay.",
  "data": {"graticule": null},
  "projection": {"type": "equirectangular"},
  "mark": "geoshape",
  "encoding": {
    "stroke": {"value": "#ddd"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `color` | Fill color (choropleth encoding) |
| `stroke` | Border color |
| `opacity` | Transparency |

## Projection Types

| Type | Description |
|---|---|
| `albersUsa` | US-focused Albers projection (default for US maps) |
| `equirectangular` | Simple lat/lon grid |
| `mercator` | Web map standard |
| `orthographic` | Globe view |
| `azimuthalEqualArea` | Equal-area circular projection |
| `conicEqualArea` | Conic equal-area (good for mid-latitudes) |

## Projection Properties

| Property | Default | Description |
|---|---|---|
| `rotate` | `[0, 0, 0]` | Rotation in degrees `[λ, φ, γ]` |
| `center` | `[0, 0]` | Center point `[lon, lat]` |
| `scale` | auto | Scale factor |
| `translate` | auto | Translation offset |

## Gotchas

- Geoshape data requires TopoJSON or GeoJSON format. Use `"format": {"type": "topojson", "feature": "<collection>"}` for TopoJSON.
- The `projection` property is required — without it, geoshape has no coordinate mapping.
- For choropleth maps, join external data using the `lookup` transform on a unique key (e.g., FIPS code).
- Graticule data (`{"graticule": null}`) generates latitude/longitude grid lines automatically.
- Point overlays on maps use `longitude`/`latitude` encoding channels, not `x`/`y`.
