# Configuration

Mermaid configuration covers themes, frontmatter config, directives (deprecated), layouts, CLI, and accessibility.

## Configuration layers (applied in order)

1. Default configuration (built-in)
2. Site-level `mermaid.initialize()` overrides
3. Diagram frontmatter `config:` block (v10.5.0+, **preferred**)
4. Directives `%%{init: {...}}%%` (deprecated)

## Frontmatter config (preferred)

```yaml
---
title: My Diagram
config:
  theme: forest
  themeVariables:
    primaryColor: "#BB2528"
    primaryTextColor: "#fff"
  flowchart:
    curve: cardinal
---
flowchart TD
    A --> B
```

## Directives (deprecated)

```
%%{init: { "theme": "dark", "flowchart": { "curve": "linear" } } }%%
```

Still works but frontmatter is preferred. Multiple directives merge (last value wins for duplicates).

## Themes

| Theme | Description |
| --- | --- |
| `default` | Standard light theme |
| `neutral` | Black and white, print-friendly |
| `dark` | Dark mode |
| `forest` | Green shades |
| `base` | Only modifiable theme (use with `themeVariables`) |

### Theme variables

Use with `theme: base` for full customization.

```yaml
config:
  theme: base
  themeVariables:
    primaryColor: "#BB2528"
    primaryTextColor: "#fff"
    primaryBorderColor: "#7C0000"
    lineColor: "#F8B229"
    secondaryColor: "#006100"
    tertiaryColor: "#fff"
    fontFamily: "trebuchet ms, verdana, arial"
    fontSize: 16px
    background: "#f4f4f4"
```

### Diagram-specific theme variables

- **Flowchart**: `nodeBorder`, `clusterBkg`, `clusterBorder`, `defaultLinkColor`, `titleColor`, `edgeLabelBackground`, `nodeTextColor`
- **Sequence**: `actorBkg`, `actorBorder`, `actorTextColor`, `signalColor`, `activationBkgColor`, etc.
- **Pie**: `pie1`–`pie12`, `pieTitleTextSize`, `pieOpacity`, `pieStrokeColor`, etc.
- **Gantt**: `taskTextLightColor`, `taskTextDarkColor`, `gridLineStartColor`, etc.
- **GitGraph**: `git0`–`git7`, `gitBranchLabel0`–`gitBranchLabel7`, `commitLabelColor`, etc.

## Layout algorithms

```yaml
config:
  layout: elk        %% elk, dagre (default), cose-bilkent, tidy-tree
```

| Layout | Best for |
| --- | --- |
| `dagre` (default) | Layered graphs, standard flowcharts |
| `elk` | Large/complex diagrams |
| `cose-bilkent` | Force-directed layouts |
| `tidy-tree` | Hierarchical/tree structures |

## CLI

```bash
npx @mermaid-js/mermaid-cli -i input.mmd -o output.svg
npx @mermaid-js/mermaid-cli -i input.mmd -o output.png -w 1200
npx @mermaid-js/mermaid-cli -i input.mmd -o output.pdf
```

## Accessibility

```
accTitle: Accessible title for screen readers
accDescr: Longer accessible description
```

Place inside diagram code. Supported in state diagrams, flowcharts, and others.

## Security

```yaml
config:
  securityLevel: "loose"    %% Enable click events, HTML labels
```

| Level | Description |
| --- | --- |
| `strict` (default) | No scripts, no external links in click events |
| `loose` | Allows click callbacks and href links |

## Common global config options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `startOnLoad` | boolean | `true` | Auto-render on page load |
| `theme` | string | `"default"` | Diagram theme |
| `fontFamily` | string | `"trebuchet ms"` | Font family |
| `fontSize` | number | 16 | Font size |
| `htmlLabels` | boolean | `true` | Use HTML labels (set `false` for markdown strings) |
| `logLevel` | number | 5 | 1=debug, 2=info, 3=warn, 4=error, 5=fatal only |
| `securityLevel` | string | `"strict"` | Security level |
| `flowchart` | object | — | Flowchart-specific config |
| `sequence` | object | — | Sequence diagram config |
| `gantt` | object | — | Gantt chart config |
| `class` | object | — | Class diagram config |
