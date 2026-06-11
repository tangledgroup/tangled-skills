# Transforms

## Contents
- Overview
- Basic Transforms
- Geographic & Spatial Transforms
- Layout Transforms
- Hierarchy Transforms
- Cross-Filter Transforms

## Overview

Transforms process a data stream to filter data, calculate new fields, or derive new data streams.

**Placement:**
- In `data[].transform` — applied to backing data before mark encoding
- In `marks[].transform` — post-encoding transforms on scenegraph items (only non-generating/non-filtering transforms)

All transforms require a `type` property. Some transforms (`bin`, `extent`, `crossfilter`) can bind their state to a signal via the `signal` property.

```json
{
  "data": [
    {
      "name": "table",
      "transform": [
        { "type": "filter", "expr": "datum.value > 5" },
        { "type": "stack", "field": "value", "groupby": ["category"] }
      ]
    }
  ]
}
```

## Basic Transforms

Process streams of data objects.

| Transform | Description |
|-----------|-------------|
| `aggregate` | Group and summarize a data stream |
| `bin` | Discretize numeric values into uniform bins |
| `collect` | Collect and sort all data objects in a stream |
| `countpattern` | Count frequency of patterns in text strings |
| `cross` | Cross-product of a data stream with itself |
| `density` | Generate values from a probability distribution |
| `dotbin` | Density binning for dot plots (≥5.7) |
| `extent` | Compute min/max over a data stream |
| `filter` | Filter using a predicate expression |
| `flatten` | Map array fields to objects, one per entry (≥3.1) |
| `fold` | Collapse selected fields into key/value properties |
| `formula` | Extend objects with derived fields via formula expression |
| `identifier` | Assign unique key values to data objects |
| `kde` | Estimate smoothed densities for numeric values (≥5.4) |
| `impute` | Impute missing values |
| `joinaggregate` | Extend objects with calculated aggregate values |
| `loess` | Fit smoothed trend line via local regression (≥5.4) |
| `lookup` | Extend objects by looking up keys on another stream |
| `pivot` | Pivot unique values to new aggregate fields (≥3.2) |
| `project` | Generate derived objects with selected fields |
| `quantile` | Calculate sample quantile values (≥5.7) |
| `regression` | Fit regression models (≥5.4) |
| `sample` | Randomly sample data objects |
| `sequence` | Generate a stream of numeric values |
| `timeunit` | Discretize date-time into time unit bins (≥5.8) |
| `window` | Calculate over ordered groups: ranking, running totals |

## Geographic & Spatial Transforms

Model spatial data, cartographic projection, and geographic guides.

| Transform | Description |
|-----------|-------------|
| `contour` | **Deprecated.** Model spatial distribution using discrete levels |
| `geojson` | Consolidate geographic data into a GeoJSON feature collection |
| `geopath` | Map GeoJSON features to SVG path strings |
| `geopoint` | Map (longitude, latitude) to (x, y) points |
| `geoshape` | Map GeoJSON features to a shape instance for procedural drawing |
| `graticule` | Generate reference grid for cartographic maps |
| `heatmap` | Generate heatmap images for raster grid data (≥5.8) |
| `isocontour` | Generate level set contours for raster grid data (≥5.8) |
| `kde2d` | Estimate 2D densities as output raster grids (≥5.8) |

## Layout Transforms

Calculate spatial coordinates to achieve various layouts.

| Transform | Description |
|-----------|-------------|
| `force` | Compute force-directed layout via physical simulation |
| `label` | Compute text position and opacity to label a chart (≥5.16) |
| `linkpath` | Route visual links between node elements |
| `pie` | Compute angular layout for pie/donut charts |
| `stack` | Compute stacked layouts for groups of values |
| `voronoi` | Compute a Voronoi diagram for a set of points |
| `wordcloud` | Compute word cloud layout of text strings |

## Hierarchy Transforms

Process hierarchy (tree) data and perform tree layout.

| Transform | Description |
|-----------|-------------|
| `nest` | Generate a tree structure by grouping objects by field values |
| `stratify` | Generate a tree structure using explicit key values |
| `treelinks` | Generate link data objects for a tree structure |
| `pack` | Tree layout based on circular enclosure |
| `partition` | Tree layout based on spatial adjacency of nodes |
| `tree` | Tree layout for a node-link diagram |
| `treemap` | Tree layout based on recursive rectangular subdivision |

## Cross-Filter Transforms

Support fast incremental filtering of multi-dimensional data.

| Transform | Description |
|-----------|-------------|
| `crossfilter` | Maintain a filter mask for multiple dimensional queries |
| `resolvefilter` | Resolve crossfilter output to generate filtered data streams |

## Custom Transforms

Custom transformations can be added via Vega's Extensibility API. See the [Transformations](https://vega.github.io/vega/docs/api/extensibility/#transform) section of the API documentation.
