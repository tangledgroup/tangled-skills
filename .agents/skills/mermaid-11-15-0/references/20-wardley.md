# Wardley Maps (v11.14.0+)

Strategic maps positioning components along visibility and evolution axes.

## Syntax

```mermaid
wardley-beta
    title "Tea Shop Value Chain"

    anchor Business [0.95, 0.63]
    component CupOfTea [0.79, 0.61]
    component Tea [0.63, 0.81]
    component Kettle [0.43, 0.35]

    Business -> CupOfTea
    CupOfTea -> Tea
    Tea -> Kettle

    evolve Kettle 0.62       %% Show evolution path
    note "Comment" [0.30, 0.49]
```

## Elements

### Anchors (value chain root)

```
anchor Business [visibility, evolution]
```

Anchors are the starting point of value chains (user-facing outcomes).

### Components

```
component Name [y, x]
```

- `y` (visibility): 0.0 = infrastructure, 1.0 = user-facing
- `x` (evolution): 0.0 = genesis/novel, 1.0 = commodity/utility

### Connections

```
Parent -> Child
```

Shows dependency/relationship between components.

### Evolution paths

```
evolve ComponentName 0.75
```

Draws an arrow showing where a component is evolving toward.

### Notes

```
note "Comment text" [y, x]
```

Positioned annotations on the map.

### Decorators

Append `(decorator)` after a component to mark strategic properties:

| Decorator | Symbol | Meaning |
| --- | --- | --- |
| `(inertia)` | ⚠ | Resistant to change |
| `(build)` | △ | Build in-house |
| `(buy)` | ◇ | Buy from market |
| `(outsource)` | □ | Outsource |
| `(market)` | ○ | Market-driven |

```
component Legacy [0.45, 0.40] (inertia)
component NewPlatform [0.65, 0.45] (build)
```

## Advanced features

### Label positioning

Fine-tune label placement with `label [offsetX, offsetY]`:

```
component Name [y, x] label [-20, 10]
```

Negative X moves left, positive X moves right. Negative Y moves up, positive Y moves down.

### Custom canvas size

```
wardley-beta
  title Custom Size
  size [800, 1000]
```

## Evolution stages

| Stage | X range | Description |
| --- | --- | --- |
| Genesis | 0.0–0.2 | Novel, unknown |
| Custom | 0.2–0.4 | Built specifically |
| Product | 0.4–0.6 | Reusable offerings |
| Commodity | 0.6–0.8 | Standardized, competitive |
| Utility | 0.8–1.0 | Expected, ubiquitous |

## Gotchas

- Hand-drawn mode (`look: handDrawn`) is not supported — uses a custom D3 renderer.
- Supports standard Mermaid theme system for styling.
