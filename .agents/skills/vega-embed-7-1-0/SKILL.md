---
name: vega-embed-7-1-0
description: 'Embed interactive Vega and Vega-Lite visualizations into web pages. Load specs from URLs or JSON objects, render with SVG or Canvas, add export/source actions, apply themes, tooltips, patches, and custom renderers. Use when embedding interactive data visualizations in browser applications via CDN or bundlers.

  '
---

# Vega-Embed 7.1.0

## Overview

Vega-Embed makes it easy to embed interactive [Vega](https://vega.github.io/vega) and [Vega-Lite](https://vega.github.io/vega-lite) visualizations into web pages. It handles loading specs (from URLs, JSON objects, or inline text), compiling Vega-Lite to Vega, rendering via SVG or Canvas, and providing built-in action links (Export PNG/SVG, View Source, Open in Editor).

Key capabilities: auto-detect spec type from `$schema` or structure, apply themes from vega-themes, customize tooltips via vega-tooltip, patch specs with JSON-Patch RFC6902, support CSP-compliant AST evaluation, and clean up resources via `finalize()`.

## When to Use

- Embedding a Vega or Vega-Lite chart in a web page (browser or bundler)
- Adding interactive action links (export, view source, open in editor) to an embedded visualization
- Applying pre-built themes from vega-themes to a chart
- Loading a spec from a remote URL with custom loader options (credentials, base URL)
- Integrating Vega visualizations into Observable notebooks

## Quick Start

### Browser CDN

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@7"></script>
  </head>
  <body>
    <div id="vis"></div>
    <script>
      var spec = 'https://example.com/chart.vg.json';
      vegaEmbed('#vis', spec)
        .then(function (result) { console.log(result.view); })
        .catch(console.error);
    </script>
  </body>
</html>
```

### NPM + Bundler

```ts
import embed from 'vega-embed';

const spec = {
  $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
  data: { url: 'data/cars.json' },
  mark: 'bar',
  encoding: { x: { field: 'Origin', type: 'nominal' }, y: { aggregate: 'count', type: 'quantitative' } }
};

const result = await embed('#vis', spec);
console.log(result.view, result.spec, result.vgSpec);
```

## Embed Function

The primary entry point is `embed(el, spec, opts)`:

| Argument | Type | Description |
|----------|------|-------------|
| `el` | `string \| HTMLElement` | CSS selector or DOM element for the chart container |
| `spec` | `string \| object` | URL string to a Vega/Vega-Lite JSON spec, or a parsed spec object |
| `opts` | `EmbedOptions` | Optional configuration (see [Options Reference](reference/02-options-reference.md)) |

Returns a `Promise<Result>`:

| Property | Type | Description |
|----------|------|-------------|
| `view` | `Vega View` | The instantiated Vega view instance |
| `spec` | `object` | Copy of the parsed input spec |
| `vgSpec` | `object` | The compiled Vega spec (after Vega-Lite compilation and patches) |
| `finalize` | `() => void` | Clean up: unregisters timers, removes event listeners, calls `view.finalize()` |

## Container Function

The `container(spec, opts)` function creates a promise to an HTML `<div>` element with a `value` property holding the Vega View. Designed for [Observable](https://observablehq.com/) notebooks:

```ts
import embed from 'vega-embed';
const wrapper = await embed.container(spec);
console.log(wrapper.value); // Vega View instance
```

## Options Overview

Vega-Embed accepts many options. Key categories:

- **Spec type**: `mode` (force `"vega"` or `"vega-lite"`)
- **Styling**: `theme` (from vega-themes), `defaultStyle`, `forceActionsMenu`
- **View config**: `renderer` (`"svg"` or `"canvas"`), `width`, `height`, `padding`, `logLevel`, `logger`
- **Actions menu**: `actions` boolean/object controlling export/source/compiled/editor links
- **Data loading**: `loader` (custom loader or options like `credentials: 'same-origin'`)
- **Spec modification**: `patch` (JSON-Patch array, function, or URL), `config` (Vega/Vega-Lite config)
- **Tooltips**: `tooltip` (handler, options object, or boolean)
- **Interactivity**: `hover`, `bind` (signal binding element)
- **Localization**: `formatLocale`, `timeFormatLocale`
- **Extensibility**: `expressionFunctions`, `ast` (CSP mode), `expr` (custom interpreter), `viewClass`
- **i18n**: action text translations (`COMPILED_ACTION`, `EDITOR_ACTION`, etc.)

See [Options Reference](reference/02-options-reference.md) for complete option types and defaults.

## Dependencies

- **Peer**: `vega` (any), `vega-lite` (any) — must be installed separately
- **Runtime deps**: `fast-json-patch`, `json-stringify-pretty-compact`, `semver`, `tslib`, `vega-interpreter`, `vega-schema-url-parser`, `vega-themes@3.0.0`, `vega-tooltip@1.0.0`

## Advanced Topics

**API Reference**: Full function signatures, types, and return values → [API Reference](reference/01-api-reference.md)

**Options Deep Dive**: All options organized by category with types, defaults, and examples → [Options Reference](reference/02-options-reference.md)

**Integration Patterns**: CDN, bundlers, Observable, CSP mode, patches, themes → [Integration Patterns](reference/03-integration-patterns.md)
