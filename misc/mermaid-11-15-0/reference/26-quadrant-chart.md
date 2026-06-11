# Quadrant Chart

## Contents
- Axes and Quadrants
- Points
- Configuration
- Theme Variables

## Overview

Quadrant charts plot data points on a 2D grid divided into four quadrants.

```mermaid
quadrantChart
    title Reach vs Engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 Expand
    quadrant-2 Promote
    quadrant-3 Re-evaluate
    quadrant-4 Improve
    Campaign A: [0.3, 0.6]
    Campaign B: [0.78, 0.34]
```

## Axes and Quadrants

### X-Axis

```
x-axis Left Label --> Right Label
x-axis Single Label         ' left only
```

### Y-Axis

```
y-axis Bottom Label --> Top Label
y-axis Single Label         ' bottom only
```

### Quadrant Labels

| Keyword | Position |
|---|---|
| `quadrant-1` | Top right |
| `quadrant-2` | Top left |
| `quadrant-3` | Bottom left |
| `quadrant-4` | Bottom right |

## Points

Plot points with `<label>: [x, y]`. X and Y values range from 0 to 1.

```
Point A: [0.75, 0.80]    ' top right quadrant
Point B: [0.25, 0.15]    ' bottom left quadrant
```

## Configuration

```mermaid
---
config:
  quadrantChart:
    chartWidth: 500
    chartHeight: 500
    titleFontSize: 20
    pointRadius: 5
    xAxisPosition: top
    yAxisPosition: left
---
quadrantChart
    x-axis A --> B
    Point: [0.5, 0.5]
```

## Theme Variables

```mermaid
---
config:
  themeVariables:
    quadrantChart:
      quadrant1Fill: '#c8e6c9'
      quadrant2Fill: '#bbdefb'
      quadrant3Fill: '#fff9c4'
      quadrant4Fill: '#ffcdd2'
      quadrantPointFill: '#333'
---
quadrantChart
    x-axis A --> B
    y-axis C --> D
    Point: [0.5, 0.5]
```
