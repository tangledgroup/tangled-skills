# Geographic Charts

Geographic visualizations use `geoshape` marks for regions and `longitude`/`latitude` channels for points, lines, and text. All geographic data is projected via cartographic projections.

## Basic Syntax

```json
{
  "data": {"url": "data/us-10m.json", "format": {"type": "topojson", "feature": "counties"}},
  "projection": {"type": "albersUsa"},
  "mark": "geoshape",
  "encoding": {
    "color": {"field": "rate", "type": "quantitative"}
  }
}
```

## Projection

Projections map longitude/latitude to x/y pixel coordinates. Specified at unit spec level alongside encoding.

### Projection Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | Projection type (see table below) |
| `center` | [number, number] | Center point [lon, lat] |
| `clipAngle` | number | Clipping radius in degrees |
| `clipExtent` | [[number,number],[number,number]] | Viewport bounds |
| `fit` | string | Fit type (`"features"`, `"bounds"`, etc.) |
| `parallels` | [number, number] | Standard parallels for conic projections |
| `pointRadius` | number | Default point radius |
| `precision` | number | Precision for spherical projection |
| `rotate` | [number, number, number] | Rotation [λ, φ, γ] |
| `scale` | number | Scale factor |
| `translate` | [number, number] | Translation [x, y] |

### Projection Types

| Type | Description |
|------|-------------|
| `albers` | Albers' equal-area conic (US-centric) |
| `albersUsa` | US composite (lower 48 + Alaska + Hawaii) |
| `azimuthalEqualArea` | Azimuthal equal-area |
| `azimuthalEquidistant` | Azimuthal equidistant |
| `conicConformal` | Conic conformal |
| `conicEqualArea` | Albers' equal-area conic |
| `conicEquidistant` | Conic equidistant |
| `equalEarth` | Equal Earth (Šavrič et al.) |
| `equirectangular` | Plate carrée (direct lon/lat) |
| `gnomonic` | Gnomonic |
| `identity` | Identity (no projection, supports `reflectX`/`reflectY`) |
| `mercator` | Spherical Mercator |
| `orthographic` | Orthographic (globe view) |
| `stereographic` | Stereographic |
| `transverseMercator` | Transverse Mercator |

### Implicit Projections

Projections are auto-added for:
- Any `geoshape` mark
- Encodings with `geojson` type fields
- Encodings using `latitude`/`longitude` channels

### Custom Projection

```json
{
  "projection": {
    "type": "albersUsa",
    "scale": 3000,
    "translate": [1200, 700]
  }
}
```

## Geoshape Marks

`geoshape` renders GeoJSON geometry projected to pixels.

### Choropleth Map

Color regions by data values:

```json
{
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

### Graticule (Grid Lines)

```json
{
  "data": {"graticule": true},
  "projection": {"type": "orthographic"},
  "mark": "geoshape"
}
```

### Sphere (Globe Background)

```json
{
  "projection": {"type": "orthographic", "scale": 100, "translate": [100, 100]},
  "layer": [
    {"data": {"sphere": true}, "mark": {"type": "geoshape", "fill": "aliceblue"}},
    {"data": {"graticule": true}, "mark": {"type": "geoshape", "stroke": "black", "strokeWidth": 0.5}}
  ]
}
```

## Geographic Points and Circles

Use `longitude`/`latitude` channels with any mark type:

### Point Map

```json
{
  "data": {"url": "data/airports.csv"},
  "projection": {"type": "albersUsa"},
  "mark": "circle",
  "encoding": {
    "longitude": {"field": "longitude", "type": "quantitative"},
    "latitude": {"field": "latitude", "type": "quantitative"},
    "size": {"value": 10}
  }
}
```

### Colored Geo Circles

```json
{
  "data": {"url": "data/zipcodes.csv"},
  "transform": [{"calculate": "substring(datum.zip_code, 0, 1)", "as": "digit"}],
  "projection": {"type": "albersUsa"},
  "mark": "circle",
  "encoding": {
    "longitude": {"field": "longitude"},
    "latitude": {"field": "latitude"},
    "size": {"value": 1},
    "color": {"field": "digit", "type": "nominal"}
  }
}
```

## Geographic Lines

Connect geographic points with lines:

```json
{
  "data": {"values": [
    {"airport": "SEA", "order": 1}, {"airport": "SFO", "order": 2}, {"airport": "JFK", "order": 8}
  ]},
  "transform": [{
    "lookup": "airport",
    "from": {
      "data": {"url": "data/airports.csv"},
      "key": "iata",
      "fields": ["latitude", "longitude"]
    }
  }],
  "projection": {"type": "albersUsa"},
  "mark": "line",
  "encoding": {
    "longitude": {"field": "longitude"},
    "latitude": {"field": "latitude"},
    "order": {"field": "order"}
  }
}
```

## Layered Geographic Visualizations

Combine geoshape backgrounds with points/lines/text:

### Map with Points

```json
{
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
        "longitude": {"field": "longitude"},
        "latitude": {"field": "latitude"},
        "size": {"value": 10},
        "color": {"value": "steelblue"}
      }
    }
  ]
}
```

### Map with Text Labels

```json
{
  "projection": {"type": "albersUsa"},
  "layer": [
    {
      "data": {"url": "data/us-10m.json", "format": {"type": "topojson", "feature": "states"}},
      "mark": {"type": "geoshape", "fill": "lightgray", "stroke": "white"}
    },
    {
      "data": {"url": "data/us-state-capitals.json"},
      "encoding": {"longitude": {"field": "lon"}, "latitude": {"field": "lat"}},
      "layer": [
        {"mark": {"type": "circle", "color": "orange"}},
        {"mark": {"type": "text", "dy": -10}, "encoding": {"text": {"field": "city"}}}
      ]
    }
  ]
}
```

## Trellis Maps (Faceted Geo)

Row/column faceting with geographic data:

```json
{
  "data": {"url": "data/income.json"},
  "transform": [{
    "lookup": "id",
    "from": {
      "data": {"url": "data/us-10m.json", "format": {"type": "topojson", "feature": "states"}},
      "key": "id"
    },
    "as": "geo"
  }],
  "projection": {"type": "albersUsa"},
  "mark": "geoshape",
  "encoding": {
    "shape": {"field": "geo", "type": "geojson"},
    "color": {"field": "pct", "type": "quantitative"},
    "row": {"field": "group"}
  }
}
```

## Repeat Geo Maps

Use `repeat` with independent color scales:

```json
{
  "repeat": {"row": ["population", "engineers", "hurricanes"]},
  "resolve": {"scale": {"color": "independent"}},
  "spec": {
    "data": {"url": "data/population_engineers_hurricanes.csv"},
    "transform": [{"lookup": "id", "from": {"data": {"url": "data/us-10m.json", "format": {"type": "topojson", "feature": "states"}}, "key": "id"}, "as": "geo"}],
    "projection": {"type": "albersUsa"},
    "mark": "geoshape",
    "encoding": {
      "shape": {"field": "geo", "type": "geojson"},
      "color": {"field": {"repeat": "row"}, "type": "quantitative"}
    }
  }
}
```

## Geo Channels

| Channel | Description |
|---------|-------------|
| `longitude` / `latitude` | Primary geographic position |
| `longitude2` / `latitude2` | Secondary position for ranged marks |

## Geoshape Config

```json
{
  "config": {
    "geoshape": {"fill": "#ddd", "stroke": "white", "strokeWidth": 0.5}
  }
}
```
