# Treemap Reference

## Description

Treemaps display hierarchical data as nested rectangles. Each branch is a rectangle tiled with smaller rectangles for sub-branches. Rectangle sizes are proportional to their values, making it easy to compare proportions within hierarchies.

> **Note:** Uses `treemap-beta` keyword — experimental, syntax may evolve.

## Basic Syntax

```mermaid
treemap-beta
    "Section 1"
        "Leaf 1.1": 12
        "Section 1.2"
            "Leaf 1.2.1": 12
    "Section 2"
        "Leaf 2.1": 20
        "Leaf 2.2": 25
```

## Node Definition

| Type | Syntax | Description |
|------|--------|-------------|
| Section (parent) | `"Name"` | Container node, no value |
| Leaf (with value) | `"Name": value` | Terminal node with numeric value |
| Hierarchy | Indentation | Spaces or tabs define nesting level |

## Styling

Use `:::class` syntax for styling nodes:

```mermaid
treemap-beta
    "Section A"
        "Item 1": 10 :::good
        "Item 2": 5 :::bad
    classDef good fill:#9f6
    classDef bad fill:#f96
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `padding` | Padding between rectangles | `2` |
| `reflectPadding` | Reflect padding on all sides | `false` |
| `clickValue` | Click behavior value | — |

## Examples

### File System

```mermaid
treemap-beta
    "Project"
        "src"
            "components": 35
            "utils": 15
            "styles": 10
        "tests": 20
        "docs": 12
        "config": 8
```

### Budget Breakdown

```mermaid
treemap-beta
    "Company Budget"
        "Engineering"
            "Salaries": 500
            "Tools": 50
            "Training": 30
        "Marketing"
            "Ads": 200
            "Content": 80
            "Events": 40
        "Operations"
            "Office": 100
            "Travel": 25
            "Supplies": 15
```

### With Styling

```mermaid
treemap-beta
    "Categories"
        "Revenue"
            "Product A": 40 :::high
            "Product B": 25 :::medium
            "Product C": 10 :::low
        "Expenses"
            "Salaries": 30 :::high
            "Marketing": 15 :::medium
            "Overhead": 5 :::low
    classDef high fill:#9f6,stroke:#333
    classDef medium fill:#ff9,stroke:#333
    classDef low fill:#f96,stroke:#333
```
