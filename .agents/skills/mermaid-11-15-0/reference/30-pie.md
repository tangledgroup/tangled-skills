# Pie Chart

## Contents
- Syntax
- showData
- Configuration

## Overview

Pie charts display proportional data as circular slices.

```mermaid
pie title Pets Adopted
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

## Syntax

- Start with `pie` keyword
- Optional `showData` to display values after legend
- Optional `title "text"`
- Slices: `"label" : value` (positive numbers only, up to 2 decimal places)

```mermaid
pie showData
    title Budget Split
    "Engineering" : 50.5
    "Marketing" : 30.2
    "Operations" : 19.3
```

Negative values are not allowed.

## Configuration

```mermaid
---
config:
  pie:
    textPosition: 0.5
  themeVariables:
    pieOuterStrokeWidth: "5px"
    pie1: "#ff6384"
    pie2: "#36a2eb"
---
pie
    "A" : 50
    "B" : 50
```

`textPosition` controls radial position of labels (0.0 = center, 1.0 = edge).
