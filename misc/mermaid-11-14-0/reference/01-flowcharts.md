# Flowcharts and Graphs

Flowcharts are composed of **nodes** (geometric shapes) and **edges** (arrows or lines). The `flowchart` keyword is preferred over the legacy `graph` keyword, though both work.

## Direction

Declare flow direction with a keyword after `flowchart`:

- `TB` — Top to bottom (default)
- `TD` — Top-down (same as TB)
- `BT` — Bottom to top
- `RL` — Right to left
- `LR` — Left to right

```mermaid
flowchart LR
  Start --> Stop
```

## Node Shapes

### Basic Shapes (bracket syntax)

- **Default (rectangle)**: `id` or `id[Text]`
- **Rounded**: `id(Text)`
- **Stadium**: `id([Text])`
- **Subroutine**: `id([[Text]])`
- **Cylinder (database)**: `id[(Text)]`
- **Circle**: `id((Text))`
- **Double circle**: `id(((Text)))`
- **Rhombus (decision)**: `id{Text}`
- **Hexagon**: `id{{Text}}`
- **Parallelogram**: `id[/Text/]` or `id[\Text\]`
- **Trapezoid**: `id[/Text\]`
- **Trapezoid alt**: `id[\Text/]`
- **Asymmetric**: `id>Text]`

### Expanded Shapes (v11.3.0+)

Mermaid 11 introduced 30+ new shapes via the `@{ shape: ... }` syntax:

```mermaid
flowchart TD
  A@{ shape: rect, label: "Process" }
  B@{ shape: rounded, label: "Event" }
  C@{ shape: stadium, label: "Terminal" }
  D@{ shape: subproc, label: "Subprocess" }
  E@{ shape: cyl, label: "Database" }
  F@{ shape: circle, label: "Start" }
  G@{ shape: diamond, label: "Decision" }
  H@{ shape: hex, label: "Prepare" }
  I@{ shape: lean-r, label: "I/O" }
  J@{ shape: datastore, label: "Datastore" }
  K@{ shape: trap-b, label: "Priority" }
  L@{ shape: trap-t, label: "Manual" }
  M@{ shape: dbl-circ, label: "Stop" }
```

**Available shapes and aliases:**

- `rect` / `process` / `proc` — Standard process
- `rounded` / `event` — Event (rounded rectangle)
- `stadium` / `terminal` / `pill` — Terminal point
- `subproc` / `subprocess` / `framed-rectangle` — Subprocess
- `cyl` / `cylinder` / `database` / `db` — Database
- `circle` / `circ` — Start (circle)
- `sm-circ` / `small-circle` / `start` — Small start
- `diamond` / `decision` / `question` / `diam` — Decision
- `hex` / `hexagon` / `prepare` — Prepare conditional
- `lean-r` / `lean-right` / `in-out` — Data input/output
- `lean-l` / `lean-left` / `out-in` — Data output/input
- `datastore` / `data-store` — Data store
- `trap-b` / `trapezoid` / `priority` — Priority action
- `trap-t` / `trapezoid-top` / `manual` — Manual operation
- `dbl-circ` / `double-circle` — Stop
- `fr-circ` / `framed-circle` / `stop` — Stop
- `fork` / `join` — Fork/Join
- `f-circ` / `filled-circle` / `junction` — Junction
- `doc` / `document` — Document
- `docs` / `documents` / `stacked-document` — Multi-document
- `st-rect` / `stacked-rectangle` / `procs` — Multi-process
- `cloud` — Cloud
- `notch-rect` / `card` — Card
- `delay` — Delay (half-rounded)
- `h-cyl` / `horizontal-cylinder` / `das` — Direct access storage
- `lin-cyl` / `lined-cylinder` / `disk` — Disk storage
- `curv-trap` / `curved-trapezoid` / `display` — Display
- `div-rect` / `divided-process` — Divided process
- `tri` / `triangle` / `extract` — Extract
- `win-pane` / `window-pane` / `internal-storage` — Internal storage
- `flip-tri` / `flipped-triangle` / `manual-file` — Manual file
- `sl-rect` / `sloped-rectangle` / `manual-input` — Manual input
- `lin-doc` / `lined-document` — Lined document
- `lin-rect` / `lined-process` / `shaded-process` — Lined process
- `notch-pent` / `notched-pentagon` / `loop-limit` — Loop limit
- `bow-rect` / `bow-tie-rectangle` / `stored-data` — Stored data
- `tag-doc` / `tagged-document` — Tagged document
- `tag-rect` / `tagged-process` — Tagged process
- `cross-circ` / `crossed-circle` / `summary` — Summary
- `brace` / `brace-l` / `comment` — Comment
- `brace-r` — Comment right
- `braces` — Comment both sides
- `hourglass` / `collate` — Collate
- `bolt` / `lightning-bolt` / `com-link` — Communication link
- `flag` / `paper-tape` — Paper tape
- `text` — Text block
- `bang` — Bang
- `odd` — Odd shape

## Links Between Nodes

### Arrow Types

- `-->` — Solid line with arrowhead
- `---` — Open link (no arrow)
- `-.->` — Dotted line with arrow
- `-.-` — Dotted line without arrow
- `==>` — Thick line with arrow
- `===` — Thick line without arrow
- `~~~` — Invisible link (for layout control)
- `--o` — Circle edge
- `--x` — Cross edge
- `o--o` — Multi-directional circle
- `<-->` — Bidirectional
- `x--x` — Multi-directional cross

### Text on Links

```mermaid
flowchart LR
  A-->|text|B
  C -- text --> D
  E -. text .-> F
  G == text ==> H
```

### Link Length

Add extra dashes to make links span more ranks:

```mermaid
flowchart TD
  A --> B
  B ---->|longer link| C
```

### Chaining Links

```mermaid
flowchart LR
  A -- text --> B -- text2 --> C
  a --> b & c --> d
  A & B --> C & D
```

## Edge IDs and Animations (v11+)

Assign IDs to edges with `@` prefix, then animate them:

```mermaid
flowchart LR
  A e1@--> B
  e1@{ animation: fast }
```

Or via classDef:

```mermaid
flowchart LR
  A e1@--> B
  classDef animate stroke-dasharray: 9,5,stroke-dashoffset: 900,animation: dash 25s linear infinite;
  class e1 animate
```

## Subgraphs

Group nodes into subgraphs with optional direction override:

```mermaid
flowchart TB
  c1-->a2
  subgraph one
    a1-->a2
  end
  subgraph two
    b1-->b2
  end
  one --> two
```

With explicit ID and title:

```mermaid
flowchart TB
  subgraph ide1 [Section One]
    a1-->a2
  end
```

Direction override within subgraph:

```mermaid
flowchart LR
  subgraph TOP
    direction TB
    top --> bottom
  end
```

> **Note**: If any subgraph node links to the outside, the subgraph inherits the parent graph's direction.

## Markdown Strings

Use backticks for markdown-formatted labels (requires `htmlLabels: false`):

```mermaid
---
config:
  htmlLabels: false
---
flowchart LR
  a["`The **cat** in the hat`"] --> b["`Line 1\nLine 2`"]
```

Auto-wrap can be disabled with `markdownAutoWrap: false`.

## Interaction

Bind click events to nodes (requires `securityLevel: 'loose'`):

```mermaid
flowchart LR
  A[Click me]
  click A callback "Click description"
  click B call someFunction()
```

## Styling and Classes

Apply styles using `style` or `classDef`/`class`:

```mermaid
flowchart LR
  A --> B
  style A fill:#f9f,stroke:#333,stroke-width:4px
  classDef done fill:#9f9,stroke:#333;
  class B done
```

## FontAwesome Icons

Prefix text with `fa:` for icons:

```mermaid
flowchart LR
  A[fa:fa-home Home] --> B[fa:fa-ban Forbidden]
```

Also supports `fab:`, `fal:`, `far:`, `fas:` prefixes.

## Special Characters

Wrap text in quotes to handle special characters:

```mermaid
flowchart LR
  id1["This is the (text) in the box"]
  id2["Text with 'quotes'"]
```

Use entity codes: `#quot;`, `#35;` (for #), etc.

> **Warning**: The word `end` in lowercase breaks flowcharts. Use `End`, `END`, or quotes `"end"`.
> **Warning**: Starting a node with `o` or `x` creates circle/cross edges. Add a space or capitalize.
