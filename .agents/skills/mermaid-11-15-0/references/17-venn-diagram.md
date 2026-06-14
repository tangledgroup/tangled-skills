# Venn Diagram Reference

## Description

Venn diagrams show relationships between sets using overlapping circles. Sets, unions, and text nodes can be styled individually.

> **Note:** Uses `venn-beta` keyword — experimental, syntax may evolve. (v11.12.3+)

## Basic Syntax

```mermaid
venn-beta
    set A
    set B
    union A,B
```

## Sets

### Simple Set

```mermaid
venn-beta
    set A
```

### Set with Label

```mermaid
venn-beta
    set A["Alpha"]
```

### Set with Size

```mermaid
venn-beta
    set A["Alpha"]:20
    set B["Beta"]:12
```

## Unions

Define overlaps between sets:

```mermaid
venn-beta
    union A,B["Overlap"]
    union A,B:3          %% With size
```

- Identifiers in `union` must be defined by earlier `set` lines
- Multiple sets: `union A,B,C`

## Text Nodes

Place labels inside sets or unions using indented `text` lines:

```mermaid
venn-beta
    set A["Frontend"]
        text A1["React"]
        text A2["Design Systems"]
    set B["Backend"]
        text B1["API"]
    union A,B["Shared"]
        text AB1["OpenAPI"]
```

## Styling

```mermaid
venn-beta
    set A["Alpha"]:20
    set B["Beta"]:12
    union A,B["AB"]:3
    style A fill:#ff6b6b
    style B fill:#6b6bff
    style A,B color:#333
```

### Style Properties

| Property | Description |
|----------|-------------|
| `fill` | Fill color |
| `color` | Text color |
| `stroke` | Stroke color |
| `stroke-width` | Stroke width |
| `fill-opacity` | Fill opacity |

## Examples

### Team Skills

```mermaid
venn-beta
    title "Team Overlap"
    set Frontend
    set Backend
    set DevOps
    union Frontend,Backend["Full Stack"]
    union Backend,DevOps["Platform"]
    union Frontend,DevOps["UI Ops"]
```

### With Sizes and Text

```mermaid
venn-beta
    set A["React"]:20
        text A1["Components"]
        text A2["Hooks"]
    set B["Vue"]:12
        text B1["Composition API"]
    union A,B["Shared Concepts"]:3
        text AB1["Reactivity"]
    style A fill:#ff6b6b,fill-opacity:0.3
    style B fill:#6b6bff,fill-opacity:0.3
```

### Three-Set Diagram

```mermaid
venn-beta
    title "Categories"
    set Science
    set Technology
    set Engineering
    union Science,Technology["SciTech"]
    union Technology,Engineering["TechEng"]
    union Science,Engineering["SciEng"]
```
