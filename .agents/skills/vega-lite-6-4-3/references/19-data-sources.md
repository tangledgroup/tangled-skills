# Data Sources Reference

Vega-Lite supports multiple data source formats. Data can be inline, loaded from URLs, or referenced by name.

## Inline Data

Embed data directly in the spec:

```vega-lite
"data": {
  "values": [
    {"category": "A", "value": 4},
    {"category": "B", "value": 6},
    {"category": "C", "value": 10}
  ]
}
```

## URL Data (CSV, TSV, JSON)

Load external data files:

```vega-lite
"data": {"url": "data/cars.json"}
```

```vega-lite
"data": {"url": "data/population.csv"}
```

```vega-lite
"data": {"url": "data/unemployment.tsv"}
```

## TopoJSON Features

For geographic data, extract features from TopoJSON:

```vega-lite
"data": {
  "url": "data/us-10m.json",
  "format": {"type": "topojson", "feature": "counties"}
}
```

## GeoJSON

```vega-lite
"data": {
  "url": "data/world.geojson",
  "format": {"type": "geojson"}
}
```

## Graticule (Grid Lines)

Generate latitude/longitude grid lines:

```vega-lite
"data": {"graticule": null}
```

## Sequence Data

Generate a sequence of values:

```vega-lite
"data": {
  "sequence": {"start": 0, "stop": 100, "step": 5}
}
```

## Named Data Sources (Shared Across Layers)

Define data once and reference by name:

```vega-lite
{
  "data": {"name": "cars", "url": "data/cars.json"},
  "layer": [
    {
      "mark": "circle",
      "encoding": {
        "x": {"field": "Horsepower"},
        "y": {"field": "Miles_per_Gallon"}
      }
    },
    {
      "mark": "line",
      "encoding": {
        "x": {"field": "Horsepower", "bin": true},
        "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}
      }
    }
  ]
}
```

## Multiple Data Sources (Layer)

Each layer can have its own data:

```vega-lite
{
  "layer": [
    {
      "data": {"url": "data/world-110m.json", "format": {"type": "topojson", "feature": "countries"}},
      "mark": "geoshape"
    },
    {
      "data": {"url": "data/earthquakes.tsv"},
      "mark": "circle",
      "encoding": {
        "longitude": {"field": "Longitude"},
        "latitude": {"field": "Latitude"}
      }
    }
  ]
}
```

## Data Lookup (Join)

Join external data to geographic features:

```vega-lite
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
}]
```

## Sample Transform

Limit data size for performance:

```vega-lite
"transform": [{"sample": 5000}]
```

## Format Property

| Property | Description |
|---|---|
| `type` | File format (`json`, `csv`, `tsv`, `topojson`, `geojson`) |
| `feature` | TopoJSON feature collection name |
| `parse` | Column type parsing (`"col": "number"`, `"col": "date"`) |
| `property` | GeoJSON property to extract |

## Gotchas

- Relative URLs resolve against the embedding page's origin, not the spec file location.
- CSV/TSV files are auto-parsed; use `format.parse` to override type detection.
- TopoJSON requires the `feature` property to specify which collection to extract.
- For large datasets, use `"sample"` transform or server-side filtering to limit data volume.
- Named data sources (`"name": "cars"`) are shared across all layers in a spec, avoiding redundant loading.
