# Venn Diagrams, Treemaps, Tree Views, and Wardley Maps

## Venn Diagrams

Set overlap visualization.

### Basic Syntax

```mermaid
venn
  title Venn Diagram Example
  {A} : 10
  {B} : 8
  {A & B} : 3
```

- Sets defined with `{setName}`
- Overlaps defined with `&` operator
- Values determine area proportions

### Multiple Sets

```mermaid
venn
  title Three Set Venn
  {A} : 5
  {B} : 4
  {C} : 3
  {A & B} : 2
  {A & C} : 1
  {B & C} : 1
  {A & B & C} : 0.5
```

## Treemaps

Hierarchical tree visualization using nested rectangles.

### Basic Syntax

```mermaid
treemap
  title Disk Usage
  root{
    dev{
      npm: 17.5MB
      node_modules: 120MB
    }
    docs{
      readme: 1KB
      guide: 50KB
    }
  }
```

- Nested `{}` define hierarchy
- Leaf nodes have numeric sizes with units (B, KB, MB, GB)

## Tree Views

Folder/structure tree visualization.

### Basic Syntax

```mermaid
tree
  Root
    Child1
      Grandchild1
      Grandchild2
    Child2
      Grandchild3
```

- Indentation defines hierarchy
- Simple text labels for nodes

## Wardley Maps

Strategic positioning maps showing components by evolution stage and visibility.

### Basic Syntax

```mermaid
wardley
  title Wardley Map Example
  xAxis "Visibility: " --> "Visible" "Invisible <--"
  yAxis "Evolution: " --> "Genome" "Culture <--"
  grids 4, 3

  component Genome, Utility, [0.5, 0.2]
  component Culture, Product, [0.7, 0.6]
```

- `xAxis` — Horizontal axis labels
- `yAxis` — Vertical axis labels
- `grids <cols>, <rows>` — Grid divisions
- `component name, type, [x, y]` — Component placement (0-1 coordinates)
