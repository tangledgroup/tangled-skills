# Configuration & Theming

## Contents
- Overview
- View Properties
- Event Properties
- Mark Properties
- Style Properties
- Axis Config
- Legend Config
- Title Config
- Projection Config
- Scale Range Config
- Locale

## Overview

A **config** object defines default visual values to theme a visualization. It can be:
1. Passed to `vega.parse(spec, config)` as a second argument
2. Included as a top-level `config` property in the spec itself (takes precedence)

```json
{
  "width": 500,
  "height": 200,
  "config": {
    "axis": {"grid": true, "gridColor": "#dedede"}
  }
}
```

## View Properties

Top-level config properties for view defaults.

| Property | Type | Description |
|----------|------|-------------|
| `autosize` | String / Object | Default autosize: `"pad"`, `"fit"`, `"none"` (signal support ≥5.10) |
| `background` | Color / Signal | Background color or null for transparent (≥5.10) |
| `description` | String | Default aria-label for the view (≥5.10) |
| `padding` | Number / Object / Signal | Default padding (signal support ≥5.10) |
| `width` / `height` | Number / Signal | Default dimensions (≥5.10) |
| `group` | Object | Default mark properties for top-level group mark |
| `locale` | Object | Locale definitions for number/date formatting |
| `lineBreak` | String / Signal | Line break delimiter for text marks (≥5.10) |

### Locale Example
```json
"locale": {
  "number": {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["", " €"]},
  "time": {"days": ["Sonntag", "Montag", ...], "months": ["Januar", ...]}
}
```

## Event Properties

| Property | Type | Description |
|----------|------|-------------|
| `bind` | String | Input binding: `"any"` (default), `"container"`, `"none"` (≥5.5) |
| `defaults` | Object | `{prevent: true}` or `{allow: ["wheel"]}` for default behavior control |
| `globalCursor` | Boolean | Set cursor on entire document body (default: false, ≥5.13) |
| `selector` | Boolean / String[] | Allow CSS selector event listeners (≥5.5) |
| `timer` | Boolean | Permit timer events (default: true, ≥5.5) |
| `view` | Boolean / String[] | Permit view event listeners (default: true, ≥5.5) |
| `window` | Boolean / String[] | Permit window event listeners (default: true, ≥5.5) |

## Mark Properties

Define defaults per mark type. Global defaults via `"mark"` property; specific types override global.

```json
{
  "symbol": {"fill": "steelblue", "size": 64},
  "mark": {"opacity": 0.8}
}
```

**Note:** Built-in config includes default fill/stroke for many mark types. Setting `"mark"` fill/stroke may be overridden by built-in type-specific defaults.

## Style Properties

Named style collections applied via `style` directive in marks.

| Built-in Style | Applies To |
|---------------|------------|
| `guide-label` | Axis and legend labels |
| `guide-title` | Axis and legend titles |
| `group-title` | Chart and header titles |

```json
"style": {
  "square": {"shape": "square", "strokeWidth": 2}
}
```

Style settings are overridden by axis/legend/title config properties.

## Axis Config

Default settings for axes under `"axis"` property. Specific types override general:
- `"axisX"` / `"axisY"` — orientation-based
- `"axisLeft"` / `"axisTop"` / etc. — more specific
- `"axisBand"` — band scale type (most specific)

Key properties: `bandPosition`, `domain`/`domainColor`/`domainWidth`, `grid`/`gridColor`/`gridWidth`, `labels`/`labelColor`/`labelFontSize`/`labelOverlap`, `ticks`/`tickSize`/`tickColor`, `title`/`titleFont`/`titleFontSize`, `translate` (≥5.8), `zindex` (≥5.11).

### Axis Config Example
```json
{
  "axis": {"labelColor": "#ccc"},
  "axisBottom": {"labelAngle": -90}
}
```

## Legend Config

Default settings under `"legend"` property.

Key properties: `clipHeight`, `columns`, `columnPadding`, `rowPadding`, `cornerRadius`, `fillColor`, `gradientLength`, `gradientThickness`, `labelColor`/`labelFontSize`/`labelOverlap`, `offset`, `orient`, `padding`, `strokeColor`, `symbolFillColor`/`symbolSize`/`symbolType`, `tickCount`, `titleFont`/`titleFontSize`, `zindex`.

### Legend Layout (≥5.0)
```json
"legend": {
  "layout": {
    "bottom": {"anchor": "middle", "direction": "vertical", "center": true, "margin": 2}
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `anchor` | String | Placement relative to axis: `"start"` (default), `"middle"`, `"end"` |
| `bounds` | String | Bounding box: `"flush"` (default) or `"full"` |
| `center` | Boolean | Center legends within layout area |
| `direction` | String | Layout direction: `"horizontal"` or `"vertical"` |
| `margin` | Number | Pixels between consecutive legends with same orient |
| `offset` | Number | Offset from chart body |

## Title Config

Defaults under `"title"` property.

| Property | Type | Description |
|----------|------|-------------|
| `align` / `anchor` | String | Text alignment and anchor position |
| `angle` | Number | Rotation in degrees |
| `baseline` | String | Vertical text baseline |
| `color` | Color | Text color |
| `dx` / `dy` | Number | Offset from title coordinates (≥5.2) |
| `font` / `fontSize` / `fontStyle` / `fontWeight` | Various | Font styling (≥5.0 for style) |
| `frame` | String | Reference frame: `"bounds"` or `"group"` |
| `limit` | Number | Max title length in pixels |
| `lineHeight` | Number | Multi-line height (≥5.7) |
| `offset` | Number | Offset from chart body and axes |

## Projection Config

Default projection settings under `"projection"` property.

| Property | Type | Description |
|----------|------|-------------|
| `clipAngle` | Number | Clipping circle radius in degrees |
| `clipExtent` | Array[] | Viewport pixel bounds |
| `scale` | Number | Scale factor |
| `translate` | Number[] | Translation offset [tx, ty] |
| `center` | Number[] | Center longitude/latitude |
| `rotate` | Number[] | Rotation angles [lambda, phi, gamma] |
| `parallels` | Number[] | Standard parallels for conic projections |
| `pointRadius` | Number | Default radius for Point/MultiPoint (default: 4.5) |
| `precision` | Number | Adaptive resampling threshold |

## Scale Range Config

Default scale range values under `"scaleRange"` property.

| Property | Type | Description |
|----------|------|-------------|
| `bandAlign` | String | Default band scale alignment (default: 0.5) |
| `bandPaddingInner` / `bandPaddingOuter` | Number | Band padding defaults |
| `pointPadding` | Number | Point scale padding default |
| `colorScheme` | String / Object | Default color scheme for `"category"`, `"ordinal"`, `"ramp"`, `"diverging"` range types |
