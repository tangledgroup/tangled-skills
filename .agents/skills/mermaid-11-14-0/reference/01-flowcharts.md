# Flowcharts

> **Source:** https://github.com/mermaid-js/mermaid/blob/mermaid%4011.14.0/docs/syntax/flowchart.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Basic Syntax

Flowcharts are composed of **nodes** (geometric shapes) and **edges** (arrows or lines).

```mermaid
flowchart LR
    id
```

### Direction

| Value | Description |
|-------|-------------|
| `TB` | Top to bottom |
| `TD` | Top-down (same as TB) |
| `BT` | Bottom to top |
| `RL` | Right to left |
| `LR` | Left to right |

```mermaid
flowchart TD
    Start --> Stop
```

### Node Shapes

| Shape | Syntax | Example |
|-------|--------|---------|
| Rectangle (default) | `id[text]` or just `id` | `A[Process]` |
| Rounded | `id(text)` | `B(Start)` |
| Stadium | `id([text])` | `C([Database])` |
| Subroutine | `id[[text]]` | `D[[Subroutine]]` |
| Cylinder | `id[(text)]` | `E[(DB)]` |
| Circle | `id((text))` | `F((Start))` |
| Rhombus/Decision | `id{text}` | `G{Yes/No?}` |
| Hexagon | `id{{text}}` | `H{{Prepare}}` |
| Parallelogram | `id[/text/]` or `\text\` | `I[/Input/]` |
| Trapezoid | `A[/text\]` or `B[\text/]` | — |
| Double circle | `id(((text)))` | `J(((End)))` |

### Unicode & Markdown in Labels

```mermaid
flowchart LR
    id["This ❤ Unicode"]
    markdown["`**Bold** _italic_`"]
```

## Expanded Node Shapes (v11.3.0+)

Mermaid supports 30+ semantic shapes via the `@{ shape: ... }` syntax:

```mermaid
flowchart TD
    A@{ shape: rect, label: "Process" }
    B@{ shape: diamond, label: "Decision" }
    C@{ shape: cyl, label: "Database" }
    D@{ shape: doc, label: "Document" }
    E@{ shape: cloud, label: "External" }
```

Key shapes: `rect`, `rounded`, `stadium`, `subproc`, `cyl`, `circle`, `diamond`, `hex`, `lean-r`, `lean-l`, `trap-b`, `trap-t`, `flip-tri`, `sl-rect`, `hourglass`, `bolt`, `brace`, `braces`, `lin-rect`, `div-rect`, `docs`, `procs`, `st-rect`, `tag-rect`, `tag-doc`, `lin-doc`, `fr-rect`, `bow-rect`, `notch-rect`, `curv-trap`, `das`, `lin-cyl`, `tri`, `win-pane`, `f-circ`, `notch-pent`, `flag`, `cross-circ`, `text`, `odd`.

### Icon & Image Shapes (v11.3.0+)

```mermaid
flowchart TD
    A@{ icon: "fa:user", form: "square", label: "User", pos: "t", h: 60 }
    B@{ img: "https://example.com/logo.png", label: "Logo", h: 60, constraint: "on" }
```

## Edges & Links

### Arrow Types

| Syntax | Description |
|--------|-------------|
| `---` | Open line (no arrow) |
| `-->` | Dotted with arrow |
| `-->` | Solid with arrow |
| `-x` / `--x` | Cross at end |
| `-)` / `--)` | Open/async arrow |
| `-.->` | Dotted line |
| `==>` | Thick line |
| `--o` / `--x` | Circle/cross edge |
| `<-->` | Bidirectional |

### Text on Edges

```mermaid
flowchart LR
    A -->|text| B
    A -- "This is text" --> B
```

### Edge IDs & Animation (v11.10.0+)

```mermaid
flowchart LR
    A e1@==> B
    e1@{ animate: true, animation: fast }
    e2@{ curve: linear }
```

### Minimum Link Length

Add extra dashes for longer links: `----` (2 ranks), `-----` (3 ranks). Use `===` or `-. ` for thick/dotted variants.

## Subgraphs

```mermaid
flowchart TB
    c1 --> a2
    subgraph one
        a1 --> a2
    end
    subgraph two
        b1 --> b2
    end
    one --> two
```

Subgraph direction can be set with `direction TB` inside. If any node links to the outside, the subgraph inherits the parent direction.

## Styling & Classes

### classDef

```mermaid
flowchart LR
    A:::someclass --> B
    classDef someclass fill:#f96,stroke:#333
```

### style statement

```mermaid
flowchart LR
    id1(Start) --> id2(Stop)
    style id1 fill:#f9f,stroke:#333,stroke-width:4px
    style id2 fill:#bbf,stroke:#f66,stroke-width:2px
```

### linkStyle

```
linkStyle 3 stroke:#ff3,stroke-width:4px,color:red;
linkStyle 1,2,7 color:blue;
```

### FontAwesome Icons

```mermaid
flowchart TD
    B["fa:fa-twitter for peace"]
    B --> C[fa:fa-ban forbidden]
    B --> D(fa:fa-spinner)
```

Register custom packs via `mermaid.registerIconPacks()`. Use prefix `fak:` for Font Awesome custom kits.

## Interaction (securityLevel: 'loose')

```mermaid
flowchart LR
    A --> B
    click A callback "Tooltip"
    click B "https://www.github.com" "Link tooltip" _blank
    click C call callback()
    click D href "https://www.github.com"
```

## Markdown Strings (htmlLabels: false)

```mermaid
flowchart LR
subgraph "One"
  a("`The **cat** in the hat`") --> b{{"`The **dog**`"}}
end
```

Text auto-wraps; use `<br>` for manual breaks or set `markdownAutoWrap: false`.

## Renderer

Default: dagre. Alternative: elk (better for large/complex diagrams).

```yaml
config:
  flowchart:
    defaultRenderer: "elk"
```

ELK options:
- `considerModelOrder`: `"NONE"` | `"NODES_AND_EDGES"` | `"PREFER_EDGES"` | `"PREFER_NODES"`
- `cycleBreakingStrategy`: `"GREEDY"` | `"DEPTH_FIRST"` | `"INTERACTIVE"` | `"MODEL_ORDER"` | `"GREEDY_MODEL_ORDER"`
- `mergeEdges`: boolean
- `forceNodeModelOrder`: boolean
- `nodePlacementStrategy`: `"SIMPLE"` | `"NETWORK_SIMPLEX"` | `"LINEAR_SEGMENTS"` | `"BRANDES_KOEPF"`
