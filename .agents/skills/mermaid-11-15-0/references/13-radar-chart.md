# Radar Chart Reference

## Description

Radar charts (also called spider, star, or Kiviat diagrams) plot low-dimensional data in circular format. Useful for comparing entities across multiple dimensions — performance metrics, skill profiles, product comparisons.

> **Note:** Uses `radar-beta` keyword — experimental, syntax may evolve.

## Basic Syntax

```mermaid
radar-beta
    axis A, B, C, D, E
    curve c1{1, 2, 3, 4, 5}
    curve c2{5, 4, 3, 2, 1}
```

## Axes

Define one or more axis lines:

```mermaid
radar-beta
    axis m["Math"], s["Science"], e["English"]
    axis h["History"], g["Geography"]
```

- Bare identifiers: `axis A, B, C`
- Labeled: `axis a["Label 1"], b["Label 2"]`

## Curves

Define data curves with values matching the axis order:

```mermaid
radar-beta
    curve alice{85, 90, 80, 70, 75}
    curve bob{70, 75, 85, 80, 90}
```

### Labeled Curves

```mermaid
radar-beta
    curve a["Alice"]{85, 90, 80, 70, 75}
    curve b["Bob"]{70, 75, 85, 80, 90}
```

## Min / Max

Set the scale range:

```mermaid
radar-beta
    max 100
    min 0
```

## Examples

### Student Grades

```mermaid
radar-beta
    title "Grades"
    axis m["Math"], s["Science"], e["English"]
    axis h["History"], g["Geography"], a["Art"]
    curve alice["Alice"]{85, 90, 80, 70, 75, 90}
    curve bob["Bob"]{70, 75, 85, 80, 90, 85}
    max 100
    min 0
```

### Skill Comparison

```mermaid
radar-beta
    title "Developer Skills"
    axis js["JavaScript"], py["Python"], sql["SQL"]
    axis devops["DevOps"], design["UI/UX"]
    curve senior["Senior"]{90, 80, 85, 75, 60}
    curve junior["Junior"]{50, 45, 40, 30, 55}
    max 100
    min 0
```

### Product Features

```mermaid
radar-beta
    title "Product Comparison"
    axis price["Price"], quality["Quality"], support["Support"]
    axis speed["Speed"], reliability["Reliability"]
    curve productA["Product A"]{8, 7, 9, 6, 8}
    curve productB["Product B"]{6, 9, 7, 9, 7}
    max 10
    min 0
```
