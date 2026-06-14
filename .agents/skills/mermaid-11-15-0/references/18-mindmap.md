# Mindmap Reference

## Description

Mindmaps visually organize information into hierarchies. A central concept branches into major ideas, which further branch into sub-ideas. Hierarchy is defined by indentation.

> **Note:** Experimental — syntax may change in future releases. Icon integration is experimental.

## Basic Syntax

```mermaid
mindmap
    Root
        Branch A
            Sub-branch 1
            Sub-branch 2
        Branch B
            Sub-branch 3
```

Hierarchy is determined by indentation level (spaces or tabs).

## Node Shapes

| Syntax | Shape |
|--------|-------|
| `Root` | Default |
| `Root["Text"]` | Rectangle |
| `Root("Text")` | Rounded rectangle |
| `Root(("Text"))` | Circle |
| `Root(["Text"])` | Flag/parallelogram |
| `Root{"Text"}` | Rhombus/diamond |
| `Root[[Text]]` | Parallelogram |

## Icons

```mermaid
mindmap
    Root
        Branch
            ::icon(fa fa-book)
            Item with icon
```

Icon syntax: `::icon(icon_pack icon_name)` — uses iconify packs.

## Styling

```mermaid
mindmap
    root((Mindmap))
        Research
            On effectiveness
            On creation
    style Research fill:#f9f,stroke:#333
```

## Examples

### Basic Mindmap

```mermaid
mindmap
  root((mindmap))
    Origins
      Long history
      Popularisation
        Tony Buzan
    Research
      Effectiveness
      Automatic creation
        Creative techniques
        Strategic planning
    Tools
      Pen and paper
      Mermaid
```

### Project Planning

```mermaid
mindmap
    root((Project))
        Planning
            Requirements
            Timeline
            Budget
        Development
            Frontend
                Components
                Styles
            Backend
                API
                Database
        Testing
            Unit tests
            Integration tests
            E2E tests
        Deployment
            Staging
            Production
```

### With Icons

```mermaid
mindmap
    root((Tech Stack))
        Frontend
            ::icon(fa fa-code)
            React
            TypeScript
        Backend
            ::icon(fa fa-server)
            Node.js
            PostgreSQL
        DevOps
            ::icon(fa fa-cogs)
            Docker
            Kubernetes
```
