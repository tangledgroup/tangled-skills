# Pie Chart Reference

## Description

Pie charts illustrate numerical proportions as circular slices. Arc length, central angle, and area of each slice are proportional to the quantity it represents.

> **Warning:** Values must be positive numbers greater than zero. Negative values and zero cause errors.

## Basic Syntax

```mermaid
pie title Pets Adopted by Volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

## Options

| Option | Description |
|--------|-------------|
| `title` | Chart title (optional) | `title My Pie Chart` |
| `showData` | Show data values after legend text (optional) | |

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `textPosition` | Axial position of labels (0.0=center, 1.0=edge) | `0.75` |
| `pieOuterStrokeWidth` | Outer stroke width | `"2px"` |

## Examples

### Basic Pie Chart

```mermaid
pie title Key Elements in Product X
    "Calcium" : 42.96
    "Potassium" : 50.05
    "Magnesium" : 10.01
    "Iron" : 5
```

### With showData

```mermaid
pie showData
    title Browser Usage
    "Chrome" : 43
    "Firefox" : 18
    "Safari" : 15
    "Edge" : 12
    "Other" : 12
```

### With Custom Styling

```mermaid
---
config:
  pie:
    textPosition: 0.5
  themeVariables:
    pieOuterStrokeWidth: "5px"
---
pie title Market Share
    "Company A" : 35
    "Company B" : 25
    "Company C" : 20
    "Others" : 20
```
