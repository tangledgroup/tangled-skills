# Sankey Diagram

## Contents
- Syntax (CSV-like)
- Node Names with Commas
- Configuration

## Overview

Sankey diagrams visualize flows from one set of values to another. Available since v10.3.0. Experimental — syntax may change.

```mermaid
sankey
    Coal,Electricity,50
    Gas,Electricity,30
    Solar,Electricity,20
    Electricity,Homes,60
    Electricity,Industry,40
```

## Syntax

CSV-like format: `source,target,value`

Each line defines a link. Nodes are inferred from the source/target names.

```mermaid
sankey
    A,B,10
    A,C,5
    B,D,8
    C,D,5
```

### Node Names with Commas

Wrap names containing commas in single quotes:

```mermaid
sankey
    'Agricultural waste',Bio-conversion,124.7
    Bio-conversion,Liquid,0.6
```

## Configuration

```mermaid
---
config:
  sankey:
    showValues: false
    linkColor: gradient
    nodeAlignment: justify
---
sankey
    A,B,10
    B,C,5
```

| Option | Default | Description |
|---|---|---|
| `showValues` | true | Show flow values on links |
| `linkColor` | gradient | 'gradient', 'source', or 'target' |
| `nodeAlignment` | justify | Alignment: 'left', 'right', 'justify', 'center' |
