# Sankey Diagram Reference

## Description

Sankey diagrams visualize flows from one set of values to another. Nodes represent entities; links (with thickness proportional to value) show the flow between them. Syntax is close to CSV.

> **Note:** Experimental diagram — syntax may evolve in future releases.

## Basic Syntax

```mermaid
sankey
    A, B, 10
    B, C, 5
    B, D, 5
```

Each line: `source_node, target_node, value`

## Node Labels with Spaces

Use quotes for labels containing spaces:

```mermaid
sankey
    "Agricultural waste", Bio-conversion, 124.7
    Bio-conversion, Liquid, 0.6
    Bio-conversion, Losses, 26.9
```

## Styling Links

```mermaid
sankey
    A, B, 10
    A, C, 5
    style 0 stroke:#ff0000
    style 1 stroke:#00ff00
```

Link indices are zero-based in the order they appear.

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nodeAlignment` | Alignment: `left`, `right`, `justify`, `center` | `justify` |
| `nodeWidth` | Width of nodes | `15` |
| `nodePadding` | Padding between nodes | `10` |
| `linkColor` | Color mode: `source`, `target`, `gradient`, `horizontal-gradient`, `constant` | `gradient` |
| `showValues` | Show flow values on links | `true` |

## Examples

### Energy Flow

```mermaid
sankey
    Coal reserves, Coal, 64
    Coal imports, Coal, 12
    Coal, Solid, 76
    Gas imports, Gas, 41
    Gas reserves, Gas, 82
    Gas, Thermal generation, 152
    Oil imports, Oil, 504
    Oil reserves, Oil, 108
    Oil, Liquid, 612
    Nuclear, Thermal generation, 840
    Solid, Industry, 30
    Solid, Losses, 10
    Liquid, Road transport, 136
    Liquid, International shipping, 129
    Liquid, Industry, 121
```

### Simple Flow

```mermaid
sankey
    Source A, Process 1, 50
    Source B, Process 1, 30
    Source C, Process 2, 40
    Process 1, Output X, 45
    Process 1, Output Y, 35
    Process 2, Output X, 25
    Process 2, Output Z, 15
```

### With Custom Config

```mermaid
---
config:
  sankey:
    showValues: false
    nodeAlignment: center
---
sankey
    "Raw Materials", Manufacturing, 100
    Manufacturing, "Quality Check", 85
    "Quality Check", Packaging, 75
    "Quality Check", Rework, 10
    Rework, "Quality Check", 8
    Packaging, Distribution, 73
    Distribution, Customers, 70
```
