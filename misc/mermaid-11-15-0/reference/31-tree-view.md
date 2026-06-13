# Tree View Diagram

## Contents
- Syntax (Indentation)
- Configuration
- Theme Variables

## Overview

Tree view diagrams represent hierarchical data as directory-like structures. Available since v11.14.0.

```mermaid
treeView-beta
    "packages"
        "mermaid"
            "src"
        "parser"
```

## Syntax

Hierarchy is defined entirely by indentation. Quoted strings represent folder/file names.

```mermaid
treeView-beta
    "project"
        "src"
            "index.js"
            "utils.js"
        "docs"
            "README.md"
        "package.json"
```

## Configuration

```mermaid
---
config:
  treeView:
    rowIndent: 80
    lineThickness: 3
---
treeView-beta
    "root"
        "child"
```

| Option | Default | Description |
|---|---|---|
| `rowIndent` | auto | Horizontal spacing between levels |
| `lineThickness` | auto | Thickness of connector lines |

## Theme Variables

```mermaid
---
config:
  themeVariables:
    treeView:
      labelFontSize: '20px'
      labelColor: '#333'
      lineColor: '#999'
---
treeView-beta
    "root"
        "child"
```
