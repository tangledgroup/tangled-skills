---
name: mermaid-11-14-0
description: Complete Mermaid 11.14.0 toolkit for creating diagrams and visualizations using text-based syntax including flowcharts, sequence diagrams, class diagrams, state diagrams, Gantt charts, ER diagrams, pie charts, mindmaps, C4 diagrams, block diagrams, timeline, kanban, sankey, radar, venn, treeview, treemap, architecture, ishikawa, use case, quadrant chart, xychart, waveform plot, zenuml, packet, and wardley maps. Use when generating diagram code, explaining Mermaid syntax, configuring rendering, customizing themes, accessibility, icons, math, or integrating Mermaid into web applications and documentation workflows.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.2"
tags:
  - diagrams
  - visualization
  - flowchart
  - sequence-diagram
  - class-diagram
  - state-diagram
  - gantt
  - mermaid
category: visualization
external_references:
  - https://mermaid.js.org/
  - https://github.com/mermaid-js/mermaid/tree/mermaid%4011.14.0/docs
---

# Mermaid 11.14.0

## Overview

Mermaid is a JavaScript-based diagramming and charting tool that renders Markdown-inspired text definitions to create and modify complex diagrams dynamically. Its main purpose is to help documentation catch up with development — solving the "Doc-Rot" problem where diagrams become outdated because they are hard to maintain.

Mermaid supports 30+ diagram types including flowcharts, sequence diagrams, class diagrams, state diagrams, Gantt charts, ER diagrams, pie charts, mindmaps, C4 diagrams, architecture diagrams, timeline, kanban, sankey, radar, venn, packet, wardley maps, and more. All rendered as SVG, PNG, or Markdown.

## When to Use

- Generating diagram code for documentation, READMEs, wikis, or presentations
- Explaining system architecture, workflows, or data models visually
- Creating interactive diagrams in web applications via the JavaScript API
- Integrating diagrams into CI/CD pipelines, static site generators, or markdown processors
- Migrating from PlantUML or other diagram tools to Mermaid syntax

## Core Concepts

### Diagram Types Overview

Mermaid organizes diagrams into these categories:

**Flow & Structure:** Flowchart, Class, State, Sequence, Architecture, C4, Requirement, GitGraph
**Data & Charts:** XY Chart, Pie, Quadrant, Radar, Sankey, Venn, Packet
**Process & Timeline:** Gantt, Timeline, Kanban, User Journey, Mindmap, Ishikawa (Fishbone)
**Specialized:** ZenUML, Wardley Maps

### Getting Started

The simplest Mermaid diagram uses a code block with the `mermaid` language tag:

````markdown
```mermaid
flowchart LR
  A --> B
```
````

Or embed directly in HTML with `<pre class="mermaid">`:

```html
<pre class="mermaid">
graph TD
  Start --> Stop
</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

### Mermaid JavaScript API

The modern API uses `mermaid.initialize()` for configuration and `mermaid.run()` for rendering:

```javascript
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
});

// Render all .mermaid elements
await mermaid.run();

// Or render specific elements
await mermaid.run({ querySelector: '.my-diagrams' });

// Programmatic rendering
const { svg, bindFunctions } = await mermaid.render(
  'my-id',
  'graph TD; A-->B'
);
```

### Configuration via Frontmatter

Diagram-specific config uses YAML frontmatter:

````markdown
---
config:
  theme: 'forest'
  flowchart:
    curve: 'basis'
---
```mermaid
flowchart LR
  A --> B
```
````

### Themes

Built-in themes: `default`, `base`, `dark`, `forest`, `neutral`, `neo`, `neo-dark`, `redux`, `redux-dark`, `redux-color`, `redux-dark-color`, `null`.

Only the `base` theme is customizable via `themeVariables`:

````markdown
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#BB2528'
    primaryTextColor: '#fff'
    lineColor: '#F8B229'
---
```mermaid
graph TD
  A --> B
```
````

### Security Levels

| Level | Behavior |
|-------|----------|
| `strict` (default) | HTML tags encoded, click disabled |
| `antiscript` | HTML allowed except `<script>`, click enabled |
| `loose` | Full HTML allowed, click enabled |
| `sandbox` | Renders in sandboxed iframe |

Change with: `mermaid.initialize({ securityLevel: 'loose' })`.

### Icons

Font Awesome icons via `fa:fa-icon-name` syntax. Register custom icon packs from [iconify.design](https://iconify.design/) using `mermaid.registerIconPacks()`. Architecture diagrams support 200,000+ icons via the registered pack prefix (e.g., `logos:aws-lambda`).

## References

- [Reference: Flowcharts](references/01-flowcharts.md)
- [Reference: Sequence Diagrams](references/02-sequence-diagrams.md)
- [Reference: Class & State Diagrams](references/03-class-and-state-diagrams.md)
- [Reference: Data Charts](references/04-data-charts.md)
- [Reference: Process & Timeline Diagrams](references/05-process-and-timeline.md)
- [Reference: Architecture, C4 & Specialized Diagrams](references/06-architecture-c4-specialized.md)
- [Reference: Configuration & Theming](references/07-configuration-and-theming.md)
- [Reference: API & Integration](references/08-api-and-integration.md)

## Installation

### CDN
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

### npm
```bash
npm install mermaid
# or
yarn add mermaid
# or
pnpm add mermaid
```

### Mermaid CLI
```bash
npx @mermaid-js/mermaid-cli input.mmd -o output.png
```

### Mermaid Live Editor
Visit [https://mermaid.live](https://mermaid.live) for interactive editing.

## Advanced Topics

- [Tiny Mermaid](https://github.com/mermaid-js/mermaid/tree/develop/packages/tiny) — smaller bundle (~half size, no mindmap/architecture/KaTeX/lazy loading)
- [Mermaid Chart](https://mermaid.ai/) — web-based editor with AI diagramming and collaboration
- [Community Integrations](https://mermaid.js.org/ecosystem/integrations-community.html) — plugins for VS Code, JetBrains, ChatGPT, PowerPoint, Word

## References

- Official documentation: https://mermaid.js.org/
- GitHub repository: https://github.com/mermaid-js/mermaid
- Mermaid Live Editor: https://mermaid.live
- CDN: https://www.jsdelivr.com/package/npm/mermaid
- Bundle size: https://bundlephobia.com/package/mermaid
