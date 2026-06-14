# Mindmaps

Hierarchical idea organization with indentation-based syntax.

## Syntax

```
mindmap
  root((Central Idea))
    Branch 1
      Sub-branch 1.1
      Sub-branch 1.2
        Deep level
    Branch 2
      ::icon(fa fa-book)
      Item with icon
```

## Node shapes

| Syntax | Shape |
| --- | --- |
| `root((text))` | Circle (default root) |
| `node(text)` | Rounded rectangle |
| `node[text]` | Rectangle |
| `node{text}` | Rhombus |
| `node[[text]]` | Subroutine |
| Plain text | Default shape |

## Icons

```
::icon(fa fa-book)
::icon(fa fa-star)
```

Place icon directive on its own line, indented to the target node level. Requires FontAwesome CSS or registered icon pack.

## Markdown in labels

Use `<br/>` for line breaks within node text.
