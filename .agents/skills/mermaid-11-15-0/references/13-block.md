# Block Diagrams

Manual-layout diagrams with full author control over block positioning. Unlike flowcharts, blocks don't auto-reposition.

## Basic syntax

```
block
    columns 3        %% Number of columns
    a b c d          %% Blocks fill left-to-right, wrap to next row
```

Space-separated blocks on a line are placed in columns.

## Block shapes

| Syntax | Shape |
| --- | --- |
| `a` or `a["Label"]` | Rectangle (default) |
| `a("Label")` | Rounded rectangle |
| `a(["Label"])` | Stadium/pill |
| `a[["Label"]]` | Subroutine |
| `a(("Label"))` | Double circle |
| `a[/"Label"/]` | Parallelogram |
| `a[/Label\]` | Trapezoid |
| `a{"Label"}` | Rhombus/diamond |
| `a{{"Label"}}` | Hexagon |
| `a>"Label"]` | Asymmetric |
| `a("Label")` | Cylinder (database) |
| `a<["Label"]>(down)` | Arrow pointing down |

## Block groups

```
block:ID
    A
    B["Wide block"]
    C
end
ID --> D
```

Groups have an id and can be connected like individual blocks. Use `columns N` inside groups.

## Connectors

```
A --> B
A --o B
A <--> B
A ==> B
```

Same arrow types as flowcharts.

## Spacing

```
space           %% Empty block for spacing
space:2         %% Multiple spaces
```

## Styling

```
style B fill:#969,stroke:#333,stroke-width:4px
classDef highlight fill:#f96
cssClass "B" highlight
```

## Troubleshooting

- **Incorrect linking**: Ensure connector syntax uses `-->` or `--` between valid block ids.
- **Overlapping blocks**: Add `space` or `space:2` between crowded blocks to force padding.
- **Nested groups not rendering**: Close every `group` with `end`; nesting depth is limited.
- **Missing shapes**: Only the listed shape keywords are recognized — check spelling.
