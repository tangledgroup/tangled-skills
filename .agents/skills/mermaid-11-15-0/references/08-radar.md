# Radar Charts (v11.6.0+)

Multi-axis circular charts for comparing entities across dimensions. Also known as spider, star, or Kiviat diagrams.

## Syntax

```
radar-beta
    title "Skills"
    axis m["Math"]
    axis s["Science"]
    axis e["English"]
    curve alice["Alice"]{85, 90, 80}
    curve bob["Bob"]{70, 75, 85}

    max 100
    min 0
```

## Details

### Axes

Each axis has an id and optional display label in brackets. Multiple axes can be on one line.

```
axis m["Math"], s["Science"], e["English"]
```

### Curves

Each curve has an id, optional label, and values in braces matching axis order.

```
curve alice["Alice"]{85, 90, 80, 70}
curve bob["Bob"]{70, 75, 85, 80}
```

### Graticule style

```
graticule polygon   %% Polygon grid lines
graticule circle    %% Circular grid lines (default)
```

### Scale

```
max 100
min 0
```

Defaults to auto-scaling if not specified.

## Configuration

Under the `radar` config key:

| Option          | Type   | Default  | Description                          |
|-----------------|--------|----------|--------------------------------------|
| `width`         | number | `600`    | Diagram width                        |
| `height`        | number | `600`    | Diagram height                       |
| `marginTop`     | number | `50`     | Top margin                           |
| `marginBottom`  | number | `50`     | Bottom margin                        |
| `marginLeft`    | number | `50`     | Left margin                          |
| `marginRight`   | number | `50`     | Right margin                         |
| `axisScaleFactor` | number | `1`  | Scale factor for the axis            |
| `axisLabelFactor` | number | `1.05` | Axis label position factor           |
| `curveTension`  | number | `0.17`   | Tension for rounded curves           |

```yaml
---
config:
  radar:
    width: 800
    height: 600
    curveTension: 0.3
---
```

## Theme variables

Use `cScale0` through `cScale12` to set curve colors (theme-dependent defaults):

```yaml
---
config:
  themeVariables:
    cScale0: "#FF0000"
    cScale1: "#00FF00"
---
```
