# Tree View Reference

## Description

Tree views represent hierarchical data in a directory-like structure. Structure depends only on indentation.

> **Note:** Uses `treeView-beta` keyword — experimental, syntax may evolve. (v11.14.0+)

## Basic Syntax

```mermaid
treeView-beta
    "packages"
        "mermaid"
            "src"
        "parser"
```

- Hierarchy defined by indentation (spaces or tabs)
- All items use quoted strings

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `rowIndent` | Horizontal indent per level | `40` |
| `lineThickness` | Thickness of connector lines | `1` |
| `labelFontSize` | Font size for labels | `"14px"` |
| `labelColor` | Color of labels | `#000` |
| `lineColor` | Color of connector lines | `#000` |

## Examples

### Project Structure

```mermaid
treeView-beta
    "my-project"
        "src"
            "components"
                "Header.mdx"
                "Footer.mdx"
            "pages"
                "index.tsx"
                "about.tsx"
        "public"
            "favicon.ico"
        "package.json"
        "README.md"
```

### With Custom Styling

```mermaid
---
config:
    treeView:
        rowIndent: 80
        lineThickness: 3
    themeVariables:
        treeView:
            labelFontSize: '20px'
            labelColor: '#FF0000'
            lineColor: '#00FF00'
---
treeView-beta
    "root"
        "folder-a"
            "file-1.txt"
            "file-2.txt"
        "folder-b"
            "sub-folder"
                "deep-file.md"
        "config.yaml"
```
