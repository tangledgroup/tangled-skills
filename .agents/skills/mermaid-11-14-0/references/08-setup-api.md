# Setup & API Reference

## Installation

### npm / yarn / pnpm

```bash
npm install mermaid        # or
yarn add mermaid           # or
pnpm add mermaid
```

Requirements: Node >= 16

### CDN

```
https://cdn.jsdelivr.net/npm/mermaid@11/dist/
```

### Mermaid Tiny

~half the size (no mindmap, architecture, KaTeX, or lazy loading):
https://github.com/mermaid-js/mermaid/tree/develop/packages/tiny

## Basic HTML Integration

```html
<!doctype html>
<html lang="en">
  <body>
    <pre class="mermaid">
graph LR
    A --> B
    </pre>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true });
    </script>
  </body>
</html>
```

## API Methods

### mermaid.initialize(config)

Initialize Mermaid with configuration. Called **only once**.

```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    securityLevel: 'strict',
});
```

### mermaid.render(id, graphDefinition)

Render a diagram and return SVG. Returns `{ svg, bindFunctions }`.

```javascript
const { svg, bindFunctions } = await mermaid.render('my-graph-id', `
graph TD
    A --> B
`);
document.getElementById('container').innerHTML = svg;
// Bind events after DOM insertion
if (bindFunctions) bindFunctions(document.getElementById('my-graph-id'));
```

> The id must be unique per diagram.

### mermaid.run(config)

Preferred rendering method (v10+). Renders all `.mermaid` elements by default.

```javascript
mermaid.initialize({ startOnLoad: false });

// Render specific selector
await mermaid.run({ querySelector: '.my-diagrams' });

// Render specific nodes
await mermaid.run({
    nodes: [document.getElementById('graph1')]
});

// Suppress errors
await mermaid.run({ suppressErrors: true });
```

### mermaid.parse(text, parseOptions)

Validate diagram syntax without rendering.

```javascript
const result = await mermaid.parse(`sequenceDiagram
    Alice->>Bob: Hello`);
if (result) {
    console.log('Valid:', result.diagramType);
} else {
    console.log('Invalid');
}
```

Returns `{ diagramType: string }` on success, `false` on error.

### mermaid.detectType(text)

Detect the type of diagram from text.

```javascript
const type = mermaid.detectType(`sequenceDiagram
    Alice->>Bob: Hello`);
console.log(type); // 'sequence'
```

Throws `UnknownDiagramError` if no type matches.

## TypeScript Interfaces

### MermaidConfig

```typescript
interface MermaidConfig {
    startOnLoad?: boolean;
    theme?: 'default' | 'neutral' | 'dark' | 'forest' | 'base';
    securityLevel?: 'strict' | 'loose' | 'antiscript' | 'sandbox';
    fontFamily?: string;
    fontSize?: string;
    flowchart?: {
        htmlLabels?: boolean;
        curve?: 'linear' | 'basis' | 'monotoneX' | 'cardinal';
        diagramPadding?: number;
        useMaxWidth?: boolean;
    };
    sequence?: {
        width?: number;
        height?: number;
        messageAlign?: 'left' | 'center' | 'right';
        mirrorActors?: boolean;
        useMaxWidth?: boolean;
    };
    // ... many more options
}
```

### RenderResult

```typescript
interface RenderResult {
    svg: string;
    bindFunctions?: (element: Element) => void;
}
```

### ParseResult

```typescript
interface ParseResult {
    diagramType: string;
}
```

## Security Level Details

| Level | HTML Tags | Click Events | Rendering Method |
|---|---|---|---|
| `strict` (default) | Encoded as text | Disabled | Normal SVG |
| `antiscript` | Allowed (except `<script>`) | Enabled | Normal SVG |
| `loose` | Allowed | Enabled | Normal SVG |
| `sandbox` | Isolated in iframe | Blocked | Sandboxed iframe |

## mermaid.run() Configuration

```typescript
interface RunOptions {
    querySelector?: string | Element;
    nodes?: (Element | NodeListOf<Node>)[];
    suppressErrors?: boolean;
}
```

## Markdown Integration

### With marked.js Renderer

```javascript
const renderer = new marked.Renderer();
renderer.code = function(code, language) {
    if (code.match(/^sequenceDiagram/) || code.match(/^graph/)) {
        return '<pre class="mermaid">' + code + '</pre>';
    }
    return '<pre><code>' + code + '</code></pre>';
};
```

### With GitHub Flavored Markdown

GitHub natively supports Mermaid in markdown code blocks with `mermaid` language tag.

## Webpack Integration

Mermaid fully supports webpack bundling. See the [webpack demo](https://github.com/mermaidjs/mermaid-webpack-demo) for a working example.

```javascript
import mermaid from 'mermaid';
mermaid.initialize({ startOnLoad: false });
```

## Ecosystem Tools

| Tool | Purpose |
|---|---|
| [Mermaid Live Editor](https://mermaid.live) | Online editor and playground |
| [Mermaid CLI (mmdc)](https://github.com/mermaid-js/mermaid-cli) | Command-line rendering to SVG/PNG |
| [GitHub Actions](https://github.com/mermaid-js/mermaid#with-github-actions) | Auto-render diagrams in CI |
| VS Code extensions | Preview in editor |
| Obsidian plugin | Use in notes |
| Docusaurus plugin | Integrate in docs site |
| MkDocs plugin | Integrate in MkDocs |
