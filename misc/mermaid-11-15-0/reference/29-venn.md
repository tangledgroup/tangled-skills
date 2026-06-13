# Venn Diagram

## Contents
- Sets and Unions
- Labels and Sizes
- Text Nodes

## Overview

Venn diagrams show set relationships using overlapping circles. Available since v11.12.3. Experimental.

```mermaid
venn-beta
    title "Team Overlap"
    set Frontend
    set Backend
    union Frontend,Backend["APIs"]
```

## Sets and Unions

- `set` defines a single set
- `union` defines overlap of two or more sets (must be defined first)

```mermaid
venn-beta
    set A
    set B
    set C
    union A,B["AB"]
    union A,C["AC"]
    union A,B,C["ABC"]
```

## Labels and Sizes

Use `["label"]` for display labels, `:N` for sizes:

```mermaid
venn-beta
    set A["Alpha"]:20
    set B["Beta"]:12
    union A,B["Overlap"]:3
```

## Text Nodes

Place text inside sets or unions with indented `text`:

```mermaid
venn-beta
    set A["Set A"]
        text "Item in A"
    set B["Set B"]
    union A,B["AB"]
        text "Shared item"
```
