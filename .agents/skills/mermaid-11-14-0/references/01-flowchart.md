# Flowchart Syntax

Flowcharts are composed of **nodes** (geometric shapes) and **edges** (arrows or lines).

## Basic Structure

```mermaid
flowchart LR
    id
```

Directions: `TB` (top-down), `TD` (top-down same as TB), `BT` (bottom-top), `RL` (right-left), `LR` (left-right)

> Tip: `graph` can be used instead of `flowchart`.

> Warning: The word "end" in all lowercase breaks flowcharts. Use "End" or "END".
> Warning: "o" or "x" as first letter of a connected node creates circle/cross edges. Add space before (e.g., "dev--- ops").

## Node Shapes

| Syntax | Shape | Example |
|---|---|---|
| `id` | Rectangle (default) | `A` |
| `id[Text]` | Rounded rectangle | `id1[This is text]` |
| `id(Round)` | Round edges | `id1(This is round)` |
| `id([Stadium])` | Stadium | `id1([Stadium shape])` |
| `id[[Subroutine]]` | Subroutine | `id1[[Subroutine]]` |
| `id[(Database)]` | Cylinder/Database | `id1[(Database)]` |
| `id((Circle))` | Circle | `id1((Circle text))` |
| `id{Diamond}` | Rhombus/Decision | `id1{{Decision?}}` |
| `id{{Hexagon}}` | Hexagon | `id1{{Hexagon}}` |
| `id1>Input]` | Asymmetric (lean right) | `id1>Input text]` |
| `id1[/Parallelogram/]` | Parallelogram | `id1[/Data/]` |
| `id1[\\Parallelogram alt\]` | Parallelogram alt | `B[\\Text\]` |
| `A[/Trapezoid\\]` | Trapezoid | `A[/Christmas\\]` |
| `B[\\Trapezoid alt/]` | Trapezoid alt | `B[\\Go shopping/]` |
| `id1(((Double circle)))` | Double circle | `id1(((Double)))` |

### Unicode & Markdown in Labels

```mermaid
flowchart LR
    id["This ❤ Unicode"]
    markdown["`This **is** _Markdown_`"]
```

## Links Between Nodes

### Arrow Types

| Syntax | Type |
|---|---|
| `A --> B` | Solid arrow |
| `A --- B` | Open/dashed line |
| `A ==> B` | Thick arrow |
| `A -.-> B` | Dotted line |
| `A -.- B` | Dotted with space |
| `A ~~> B` | Curved arrow |

### Labeled Edges

```mermaid
flowchart LR
    A-- This is text ---B
    A---|This is text|B
    A-->|text|B
    A-- text -->B
    A -.->|dotted| B
    A == Label == B
    A <===> B
    A <== B
```

### Arrowhead Modifiers

Append to the arrow head: `o` (circle), `x` (cross), `o-x` (combined)

```mermaid
flowchart LR
    A -->o B
    A --x> B
    A o--o B
```

### Multi-directional Arrows

```mermaid
flowchart LR
    A === Link === B
    A <===> B
```

## Subgraphs

### Basic Subgraph

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
    two --> c2
```

### Named Subgraph with ID

```mermaid
flowchart TB
    subgraph ide1 [one]
        a1-->a2
    end
```

### Direction in Subgraphs

Subgraphs can override the parent direction:

```mermaid
flowchart LR
  subgraph TOP
    direction TB
    subgraph B1
        direction RL
        i1 -->f1
    end
    subgraph B2
        direction BT
        i2 -->f2
    end
  end
  A --> TOP --> B
```

### Nested Subgraphs

```mermaid
flowchart TB
    subgraph cluster["Cluster with style"]
        direction TB
        A --> B
    end
    C --> cluster
    style cluster fill:#f9f,stroke:#333,stroke-width:2px
```

## Interaction (Click Events)

Requires `securityLevel='loose'` or `'antiscript'`.

### Click to URL

```mermaid
flowchart LR
    A-->B
    B-->C
    click A "https://www.github.com" "Open GitHub" _blank
    click B href "https://www.github.com" "Tooltip" _self
```

### Click to JavaScript Callback

```html
<script>
  window.callback = function () {
    alert('A callback was triggered');
  };
</script>
```

```mermaid
flowchart LR
    A-->B
    click A callback "Tooltip for a callback"
    click C call callback() "Tooltip"
```

Click syntax: `click nodeId url [tooltip] [target]`

Target options: `_self`, `_blank`, `_parent`, `_top`.

## FontAwesome Icons

Use syntax `fa:#icon class name#`:

```mermaid
flowchart TD
    B["fa:fa-twitter for peace"]
    B-->C[fa:fa-ban forbidden]
    B-->D(fa:fa-spinner)
    B-->E(A fa:fa-camera-retro perhaps?)
```

Supported prefixes: `fa`, `fab`, `fas`, `far`, `fal`, `fad`.

Requires Font Awesome CSS on the page, or registered icon packs via `mermaid.registerIconPacks()`.

## Styling and Classes

### Class-based Styling

```mermaid
flowchart LR
    classDef red fill:#f96,stroke:#333,stroke-width:2px;
    classDef green fill:#9f9,stroke:#333;
    A[Start] --> B{Decision}
    B -->|Yes| C[Done]
    B -->|No| D[Retry]
    class B red;
    class C green;
```

### Inline Styling

```mermaid
flowchart LR
    A[Start] --> B[End]
    style A fill:#f96,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff
```

### Styling Edges

```mermaid
flowchart LR
    A --> B
    linkStyle 0 stroke:red,stroke-width:2px;
```

## Configuration

### Renderer

Default renderer is `dagre`. Can switch to `elk` for complex diagrams:

```javascript
{
    flowchart: {
        defaultRenderer: "elk",
        htmlLabels: true,
        curve: 'basis',  // linear | basis | monotoneX | cardinal
        diagramPadding: 8,
        useMaxWidth: false,
        handDrawnSeed: 0,
        width: 1000
    }
}
```

## New Shapes in v11.3.0+

Mermaid introduced 30+ new shapes using the `@{ shape: name, label: "Text" }` syntax:

### Shape Reference Table (v11.3.0+)

| Shape Name | Short Name | Description |
|---|---|---|
| `rect` | `proc`, `process`, `rectangle` | Standard process |
| `rounded` | `event` | Event/rounded rectangle |
| `stadium` | `pill`, `terminal` | Terminal point |
| `subproc` | `framed-rectangle`, `subroutine` | Subprocess |
| `cyl` | `cylinder`, `database`, `db` | Database storage |
| `circle` | `circ`, `start`, `small-circle` | Start point |
| `diamond` | `decision`, `question` | Decision step |
| `hex` | `hexagon`, `prepare` | Prepare/condition |
| `cloud` | — | Cloud shape |
| `bolt` | `com-link`, `lightning-bolt` | Communication link |
| `brace` / `brace-r` / `braces` | — | Comment/curly brace |
| `doc` / `document` | — | Document |
| `docs` / `st-doc` / `stacked-document` | — | Multiple documents |
| `lin-cyl` / `disk` | — | Disk storage |
| `h-cyl` / `das` | — | Direct access storage |
| `lin-rect` / `shaded-process` | — | Lined process |
| `st-rect` / `procs` / `processes` | — | Multiple processes |
| `div-rect` / `div-proc` | — | Divided process |
| `bow-rect` / `stored-data` | — | Stored data |
| `tag-rect` / `tag-proc` | — | Tagged process |
| `lin-doc` / `lined-document` | — | Lined document |
| `notch-rect` / `card` / `notched-rectangle` | — | Card shape |
| `curv-trap` / `display` | — | Curved trapezoid/display |
| `notch-pent` / `loop-limit` | — | Loop limit step |
| `sl-rect` / `manual-input` | — | Manual input |
| `trap-t` / `inv-trapezoid` / `manual` | — | Manual task |
| `trap-b` / `priority` / `trapezoid` | — | Priority action |
| `flip-tri` / `manual-file` | — | Manual file |
| `tri` / `extract` | — | Extraction |
| `fork` / `join` | — | Fork/join in process flow |
| `win-pane` / `internal-storage` | — | Internal storage |
| `f-circ` / `filled-circle`, `junction` | — | Junction point |
| `cross-circ` / `summary` | — | Summary |
| `tag-doc` / `tagged-document` | — | Tagged document |
| `delay` / `half-rounded-rectangle` | — | Delay |
| `odd` | — | Odd shape |
| `text` / `text-block` | — | Text block |

Usage: `Node@{ shape: name, label: "Text" }`

## Special Characters That Break Syntax

| Character/Word | Cause | Fix |
|---|---|---|
| `end` (lowercase) | Keyword conflict in flowcharts | Use "End", "END", or wrap in quotes |
| `o` or `x` at node start | Creates circle/cross edge | Add space before: `"dev --- ops"` |
| `%%{}%%` in comments | Confuses with directives | Avoid "{}" inside `%%` comments |
