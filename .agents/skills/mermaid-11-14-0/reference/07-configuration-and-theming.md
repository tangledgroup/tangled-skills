# Configuration & Theming

> **Source:** https://github.com/mermaid-js/mermaid/blob/mermaid%4011.14.0/docs/config/theming.md, docs/config/usage.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## MermaidConfig Interface

Key configuration options available via `mermaid.initialize()`:

### Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `theme` | string | `'default'` | Theme name or `'null'` for no theme |
| `look` | string | — | `'neo'`, `'classic'`, `'handDrawn'` |
| `startOnLoad` | boolean | `true` | Auto-render on page load |
| `securityLevel` | string | `'strict'` | Trust level for parsed diagrams |
| `fontFamily` | string | — | CSS font-family for diagram text |
| `altFontFamily` | string | — | Fallback font |
| `fontSize` | number | 16 | Font size in pixels |
| `logLevel` | number/string | — | Logging level (`'trace'`–`'fatal'`) |
| `htmlLabels` | boolean | true | Use HTML tags for labels |
| `arrowMarkerAbsolute` | boolean | false | Arrow marker path type |
| `handDrawnSeed` | number | 0 | Seed for hand-drawn look |
| `maxTextSize` | number | — | Max text diagram size |
| `maxEdges` | number | — | Max edges in a graph |
| `deterministicIds` | boolean | false | Deterministic node IDs for git |
| `deterministicIDSeed` | string | — | Seed for deterministic IDs |
| `suppressErrorRendering` | boolean | false | Hide 'Syntax error' diagram |
| `secure` | string[] | — | Keys only settable via initialize() |

### Diagram-Specific Config

Each diagram type has its own config object:
- `flowchart`, `sequence`, `state`, `class`, `er`, `pie`, `quadrantChart`, `xyChart`, `gantt`, `journey`, `timeline`, `gitGraph`, `c4`, `architecture`, `mindmap`, `sankey`, `packet`, `kanban`, `ishikawa`, `requirement`, `radar`, `venn`, `treeView`, `block`

### Math Options

| Option | Type | Description |
|--------|------|-------------|
| `legacyMathML` | boolean | Use KaTeX fallback for browsers without MathML |
| `forceLegacyMathML` | boolean | Force KaTeX stylesheet regardless of browser support |

## Available Themes

| Theme | Description |
|-------|-------------|
| `default` | Default theme |
| `base` | Only modifiable theme — use for custom themes |
| `dark` | Dark mode |
| `forest` | Green shades |
| `neutral` | Black & white, print-friendly |
| `neo` / `neo-dark` | Neo look |
| `redux` / `redux-dark` / `redux-color` / `redux-dark-color` | Redux theme variants |
| `null` | No theme applied |

## Theme Variables

### Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `darkMode` | false | Affects derived color calculation |
| `background` | #f4f4f4 | Background for items |
| `fontFamily` | trebuchet ms, verdana, arial | Font family |
| `fontSize` | 16px | Font size |
| `primaryColor` | #fff4dd | Node background; other colors derived |
| `primaryTextColor` | calculated | Text in primary nodes |
| `secondaryColor` | derived from primary | — |
| `tertiaryColor` | derived from primary | — |
| `lineColor` | derived from background | Link/edge color |
| `noteBkgColor` | #fff5ad | Note background |
| `noteTextColor` | #333 | Note text |
| `errorBkgColor` | tertiaryColor | Error message background |

### Flowchart Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `nodeBorder` | primaryBorderColor | Node border color |
| `clusterBkg` | tertiaryColor | Subgraph background |
| `clusterBorder` | tertiaryBorderColor | Subgraph border |
| `defaultLinkColor` | lineColor | Default edge color |
| `titleColor` | tertiaryTextColor | Title color |
| `edgeLabelBackground` | derived from secondary | Edge label bg |
| `nodeTextColor` | primaryTextColor | Text inside nodes |

### Sequence Diagram Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `actorBkg` | mainBkg | Actor background |
| `actorBorder` | primaryBorderColor | Actor border |
| `signalColor` | textColor | Signal line color |
| `activationBkgColor` | secondaryColor | Activation bar bg |
| `sequenceNumberColor` | derived from lineColor | Sequence numbers |

### Pie Chart Variables

`pie1`–`pie12`, `pieTitleTextSize`, `pieTitleTextColor`, `pieSectionTextSize`, `pieStrokeWidth`, `pieOuterStrokeWidth`, `pieOpacity`.

### User Journey Variables

`fillType0`–`fillType7` for section fills.

## Custom Theme Example

```yaml
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#BB2528'
    primaryTextColor: '#fff'
    primaryBorderColor: '#7C0000'
    lineColor: '#F8B229'
    secondaryColor: '#006100'
    tertiaryColor: '#fff'
    darkMode: false
---
```

## Diagram-Level Configuration

### Flowchart Curve

```yaml
config:
  flowchart:
    curve: 'basis'  # basis, bumpX, bumpY, cardinal, catmullRom, linear, monotoneX, monotoneY, natural, step, stepAfter, stepBefore
    defaultRenderer: 'dagre'  # or 'elk'
```

### Gantt

```yaml
config:
  gantt:
    # gantt-specific options
```

### XY Chart

```yaml
config:
  xyChart:
    width: 800
    height: 600
    showDataLabel: true
```

## Security Levels

| Level | HTML Tags | Click/Scripts | Description |
|-------|-----------|---------------|-------------|
| `strict` | Encoded | Disabled | Default, safest |
| `antiscript` | Allowed (no `<script>`) | Enabled | Allows most HTML |
| `loose` | All allowed | Enabled | Full trust |
| `sandbox` | Sandboxed iframe | Restricted | Renders in iframe |

```javascript
mermaid.initialize({ securityLevel: 'loose' });
```

## Init Directives

Diagram-level init via directive:

````markdown
%%{initialize: {"startOnLoad": true, logLevel: "fatal" }}%%
```mermaid
graph TD
  A --> B
```
````

Or frontmatter:

````markdown
---
config:
  theme: 'dark'
  logLevel: 'warn'
---
```mermaid
graph TD
  A --> B
```
````
