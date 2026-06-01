# Getting Started and Deployment

## Contents
- Diagram Syntax Overview
- Ways to Use Mermaid
- CDN Integration
- npm Package Installation
- JavaScript API Usage
- mermaid.run() (v10+)
- Security Levels
- Tiny Mermaid
- Integrations

## Diagram Syntax Overview

All diagrams begin with a type-declaration keyword, followed by the diagram body. Line comments use `%%`:

```mermaid
flowchart LR
    %% This is a comment
    A --> B
```

Unknown words and misspellings break diagrams; parameters silently fail. The word `end` in lowercase breaks flowcharts — capitalize or quote it.

## Ways to Use Mermaid

1. **Live Editor** — <https://mermaid.live> — instant preview, export PNG/SVG/Markdown
2. **Mermaid Chart Editor** — <https://mermaid.ai> — AI-assisted, collaboration, storage
3. **Native Markdown Support** — GitHub, GitLab, Azure DevOps, Gitea, Obsidian, Doctave (use ` ```mermaid ` code blocks)
4. **JavaScript API** — embed in web pages via CDN or npm
5. **npm Dependency** — `npm install mermaid`, use with bundlers

## CDN Integration

```html
<pre class="mermaid">
flowchart LR
    A --> B
</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

Each diagram needs its own `<pre class="mermaid">` tag. The `initialize()` call triggers rendering.

## npm Package Installation

Requirements: Node.js >= 16.

```bash
npm install mermaid
# or
yarn add mermaid
# or
pnpm add mermaid
```

## JavaScript API Usage

### Basic Render

```javascript
import mermaid from 'mermaid';
mermaid.initialize({ startOnLoad: false });

const { svg, bindFunctions } = await mermaid.render('myId', 'graph TB\na-->b');
element.innerHTML = svg;
if (bindFunctions) bindFunctions(element);
```

### Detect Diagram Type

```javascript
const type = mermaid.detectType('sequenceDiagram\nA->>B: Hello');
// Returns: 'sequence'
```

### Parse Without Rendering

```javascript
const result = await mermaid.parse(text, { suppressErrors: true });
// Returns { diagramType: string } or false
```

Custom error handler:

```javascript
mermaid.parseError = function (err, hash) {
  console.error('Parse error:', err);
};
```

## mermaid.run() (v10+)

Preferred method for complex integrations. By default called automatically when document is ready.

```javascript
mermaid.initialize({ startOnLoad: false });

// Render by CSS selector
await mermaid.run({ querySelector: '.my-diagrams' });

// Render specific nodes
await mermaid.run({ nodes: [document.getElementById('a'), document.getElementById('b')] });

// Suppress errors
await mermaid.run({ suppressErrors: true });
```

> `mermaid.init()` is deprecated in v10. Use `mermaid.run()` instead.

## Security Levels

| Level | HTML in Text | Click Events | Notes |
|---|---|---|---|
| `strict` (default) | Encoded | Disabled | Safe for untrusted content |
| `antiscript` | Allowed (no `<script>`) | Enabled | Removes script tags |
| `loose` | Fully allowed | Enabled | Trust all content |
| `sandbox` | Sandboxed iframe | Limited | Beta, prevents JS execution |

Set via `mermaid.initialize({ securityLevel: 'loose' })`. Click events and HTML tags require non-strict levels.

## Tiny Mermaid

Smaller bundle (~half the size). Does not support: Mindmap Diagrams, Architecture Diagrams, KaTeX rendering, or lazy loading. Use when these features are not needed.

## Integrations

Mermaid is natively supported by GitHub, GitLab, Azure DevOps, Gitea, Obsidian, and many others. Community integrations exist for Atlassian (Confluence/Jira), GitBook, Notion, VS Code, JetBrains IDEs, PowerPoint, Word, Jupyter, and more. See the [Mermaid Chart Plugins](https://mermaid.ai/plugins) page and [Community Integrations](https://mermaid.js.org/ecosystem/integrations-community.html) for full lists.
