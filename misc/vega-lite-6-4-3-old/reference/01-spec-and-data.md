# Spec and Data

## Contents

- Specification Structure
- Top-Level Properties
- Single View Specification
- Data Sources
- Format Options
- Data Generators
- Named Datasets

## Specification Structure

Vega-Lite specifications are JSON objects. The compiler compiles them into
lower-level Vega specifications for rendering. Every spec should include
`$schema` pointing to the JSON schema for editor validation and autocomplete.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": { ... },
  "mark": "bar",
  "encoding": { ... }
}
```

### Spec Types

| Type | Description |
|------|-------------|
| Single View | One mark type with encoding |
| Layer (`layer`) | Multiple marks sharing data/view |
| Facet (`facet`/`row`/`column`) | Trellis/small multiples |
| Concat (`hconcat`/`vconcat`/`concat`) | Side-by-side or stacked views |
| Repeat (`repeat`) | Iterate encoding across fields |

## Top-Level Properties

Properties available on all top-level specifications:

| Property | Type | Description |
|----------|------|-------------|
| `$schema` | String | JSON schema URL (use `v6.json` for v6) |
| `background` | Color | Canvas background color. Default: `"white"` |
| `padding` | Number \| Object | Padding from canvas edge to data rect. Default: `5`. Object form: `{"left": 5, "top": 5, "right": 5, "bottom": 5}` |
| `autosize` | String \| Object | How size is determined. `"pad"` (default), `"fit"`, or `"none"`. Object values can specify `type`, `resize`, `contains` |
| `config` | Config | Top-level configuration object |
| `usermeta` | Object | Custom metadata passed to Vega, ignored by Vega-Lite |

Properties available on all specifications (including nested):

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | Name for later reference |
| `description` | String | Comment/description |
| `title` | TitleParams | Plot title |
| `data` | Data | **Required.** Data source. Set to `null` to ignore parent data |
| `transform` | Transform[] | Array of data transformations |
| `params` | Parameter[] | Parameters for variables and selections |

Layout properties (facet, concat, repeat):

| Property | Type | Description |
|----------|------|-------------|
| `align` | String \| Object | Grid alignment: `"all"` (default), `"each"`, `"none"`. Object: `{"row": ..., "column": ...}` |
| `bounds` | String | Bounds method: `"full"` (default) or `"flush"` |
| `center` | Boolean \| Object | Center subviews. Default: `false` |
| `spacing` | Number \| Object | Spacing between sub-views. Default from config (`20`) |

## Single View Specification

A single view spec describes one mark type and its encoding:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": { ... },
  "transform": [ ... ],
  "mark": "bar",
  "encoding": { ... },
  "width": 400,
  "height": 300,
  "view": { ... },
  "projection": { ... }
}
```

### Width and Height

- For continuous x-field: `width` should be a number
- For discrete x-field: `width` can be a number or `{step: number}` (width per step)
- Set to `"container"` for responsive sizing
- Same rules apply for `height` with y-field

### View Background

The `view` property defines the data rectangle background:

| Property | Type | Description |
|----------|------|-------------|
| `style` | String \| String[] | Style name(s). Default: `"cell"` |
| `fill` | Color | Fill color. Default: `undefined` (transparent) |
| `stroke` | Color | Stroke color. Default: `"#ddd"` |
| `opacity` | Number | Overall opacity. Default: `0.7` for non-aggregate point/circle/square/tick, `1` otherwise |
| `cornerRadius` | Number | Rounded corner radius in pixels |

## Data Sources

Vega-Lite uses tabular data (collections of records with named fields).

### Inline Data

Embed data directly using `values`:

```json
{
  "data": {
    "values": [
      {"a": "A", "b": 28},
      {"a": "B", "b": 55},
      {"a": "C", "b": 43}
    ]
  }
}
```

Arrays of primitive values are mapped to `{"data": value}` objects.

### Data from URL

Load data from a remote or local URL:

```json
{
  "data": {
    "url": "data/cars.json"
  }
}
```

Format is inferred from file extension. Override with `format`:

```json
{
  "data": {
    "url": "data/weather.csv",
    "format": {"type": "csv"}
  }
}
```

### Named Data Sources

Reference data bound at runtime via Vega's View API:

```json
{
  "data": {"name": "myData"}
}
```

### Multiple Data Sources

Use `datasets` for top-level named data, or inline data objects within transforms/layers:

```json
{
  "datasets": {
    "table1": [{"x": 1, "y": 2}, {"x": 2, "y": 3}]
  },
  "data": {"name": "table1"},
  ...
}
```

## Format Options

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | Format: `"json"` (default), `"csv"`, `"tsv"`, `"dsv"`, `"topojson"`, `"stats"`, `"table"` |
| `property` | String | For topojson, the feature property name (e.g., `"counties"`) |
| `parse` | Object \| String | For CSV/TSV: field-to-type mapping (`{"date": "date"}`) or `"all"` to auto-parse all fields |
| `delimiter` | String | Custom delimiter for `"dsv"` format |

## Data Generators

Generate data programmatically without external files.

### Sequence Generator

```json
{
  "data": {
    "name": "table",
    "values": {"sequence": {"start": 0, "stop": 10, "step": 0.5}}
  }
}
```

### Sphere Generator

Generates a GeoJSON sphere object (useful for maps):

```json
{
  "data": {"name": "sphere", "sphere": true}
}
```

### Graticule Generator

Generates a GeoJSON graticule (grid lines for maps):

```json
{
  "data": {"name": "graticule", "graticule": true}
}
```

## Named Datasets

Vega-Lite includes built-in datasets accessible via relative paths:

- `data/cars.json` — Car attributes (Horsepower, MPG, Cylinders, Origin)
- `data/seattle-weather.csv` — Seattle weather (date, temp_max, temp_min, precipitation, weather)
- `data/weather.csv` — Multi-city weather
- `data/movies.json` — Movie data (IMDB Rating, Rotten Tomatoes, Gross)
- `data/stocks.csv` — Stock prices (date, symbol, price)
- `data/barley.json` — Barley yield by site and year
- `data/penguins.json` — Penguin measurements
- `data/population.json` — US population by age, sex, year
- `data/unemployment-across-industries.json` — Unemployment time series
- `data/us-10m.json` — US TopoJSON (states, counties)
- `data/airports.csv` — Airport locations
- `data/zipcodes.csv` — US zipcode coordinates
- `data/gapminder-health-income.csv` — Global health/income data
- `data/flights-2k.json` — Flight data
- `data/unemployment.tsv` — County unemployment rates
