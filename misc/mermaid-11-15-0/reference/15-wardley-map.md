# Wardley Map

## Contents
- Coordinate System
- Components and Anchors
- Decorators
- Links
- Evolution (evolve)
- Regions
- Notes
- Configuration
- Limitations

## Overview

Wardley Maps visualize business strategy by mapping value chains along visibility (Y-axis) and evolution (X-axis). Available since v11.14.0.

```mermaid
wardley-beta
title Tea Shop Value Chain
component CupOfTea [0.79, 0.61]
component Tea [0.63, 0.81]
component Kettle [0.43, 0.35]
CupOfTea -> Tea
CupOfTea -> Kettle
```

## Coordinate System

Coordinates use `[visibility, evolution]` format (OWM format), **not** `(x, y)`:
- **Visibility** (1st value): 0.0–1.0, bottom to top
- **Evolution** (2nd value): 0.0–1.0, left to right

```mermaid
wardley-beta
    component Infrastructure [0.30, 0.20]
    component Product [0.70, 0.60]
```

## Components and Anchors

### Component

```mermaid
wardley-beta
    component API [0.60, 0.70]
    component DB [0.40, 0.85] label [-50, 10]
```

Names with hyphens work without quoting. Quote only if name starts with non-letter or contains unsupported characters.

### Anchor

Anchors represent users/customers (bold labels):

```mermaid
wardley-beta
    anchor Customer [0.90, 0.95]
    component Service [0.70, 0.75]
    Customer -> Service
```

## Decorators

Add visual markers to components:

| Decorator | Symbol |
|---|---|
| `(star)` | Star |
| `(exclamation)` | Exclamation mark |
| `(question)` | Question mark |

```mermaid
wardley-beta
    component API [0.60, 0.70] (star)
    component Risk [0.40, 0.30] (exclamation)
```

## Links

Connect components and anchors:

```mermaid
wardley-beta
    A -> B          ' solid arrow
    A -.-> B        ' dashed arrow
    A ==> B         ' thick arrow
```

## Evolution

Move a component along the evolution axis with `evolve`:

```mermaid
wardley-beta
    component Kettle [0.43, 0.35]
    evolve Kettle 0.62
```

## Regions

Define colored regions on the map:

```mermaid
wardley-beta
    region "Custom Built" 0.0, 0.3, 1.0
    region "Comprised" 0.3, 0.6, 1.0
    region "Product" 0.6, 0.8, 1.0
    region "Utility" 0.8, 1.0, 1.0
```

Format: `region "name" startEvolution endEvolution visibilityHeight`

## Notes

Add annotations:

```mermaid
wardley-beta
    note "Standardising power allows faster evolution" [0.30, 0.49]
```

## Configuration

```mermaid
---
config:
  wardley:
    size: [1100, 600]
    xLabel: "Evolution"
    yLabel: "Visibility"
    showRegions: true
---
wardley-beta
    component A [0.5, 0.5]
```

## Limitations

- Beta feature — syntax may change in future releases
- No animation support
- Limited styling options compared to flowcharts
