# Integration Patterns

## Contents
- Browser CDN
- Bundlers (Webpack/Rollup)
- Observable Notebooks
- CSP Mode
- Spec Patches
- Themes
- Custom Loaders and Credentials
- Signal Binding
- Error Handling

## Browser CDN

Include Vega, Vega-Lite, and Vega-Embed as `<script>` tags. The global `vegaEmbed` function is available immediately:

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@7"></script>
```

```js
var spec = {
  $schema: 'https://vega.github.io/schema/vega-lite/v6.json',
  data: { url: 'https://example.com/data.json' },
  mark: 'bar',
  encoding: { x: { field: 'x', type: 'quantitative' }, y: { aggregate: 'count', type: 'quantitative' } }
};

vegaEmbed('#chart', spec).then(function(result) {
  // Access result.view for programmatic interaction
}).catch(console.error);
```

**Note:** Internet Explorer does not support ES6 Promises — include a polyfill.

## Bundlers (Webpack/Rollup)

Import from npm and bundle with your toolchain:

```ts
import embed from 'vega-embed';

// Must also install peer dependencies
// npm install vega vega-lite
```

The package exports:
- **ESM:** `./build/embed.js` (via `exports.types` / `exports.default`)
- **UMD:** `./build/vega-embed.min.js` (via `unpkg` / `jsdelivr`)

TypeScript types are available at `./build/embed.d.ts`.

## Observable Notebooks

Use the `container()` function, which returns an HTML element with a `value` property:

```js
embed = require('vega-embed@7');
viewof view = embed.container(spec);
```

The default export acts as a wrapper that auto-selects between `embed()` and `container()` based on arguments: if the first argument looks like a DOM selector or element, it calls `embed()`; otherwise it calls `container()`.

## CSP Mode

Enable CSP-compliant expression evaluation using AST mode:

```ts
const result = await embed('#chart', spec, {
  ast: true
});
```

This generates an Abstract Syntax Tree instead of native expressions and uses an interpreter. Slower than native evaluation but avoids `eval()`, making it compatible with strict Content Security Policies.

Optionally provide a custom interpreter:

```ts
import { expressionInterpreter } from 'vega-interpreter';

const result = await embed('#chart', spec, {
  ast: true,
  expr: expressionInterpreter
});
```

## Spec Patches

Modify specs before rendering using JSON-Patch RFC6902:

```ts
// Using a patch function
const result = await embed('#chart', spec, {
  patch: (vgSpec) => {
    vgSpec.data[0].format = { ...vgSpec.data[0].format, parse: { date: 'date' } };
    return vgSpec;
  }
});

// Using JSON-Patch array
const result = await embed('#chart', spec, {
  patch: [
    { op: 'add', path: '/config/scale-range', value: ['steelblue', 'orange'] }
  ]
});

// Loading a patch from URL
const result = await embed('#chart', spec, {
  patch: 'https://example.com/patch.json'
});
```

For Vega-Lite specs, the compiled Vega spec is patched (not the original Vega-Lite spec).

## Themes

Apply pre-built themes from [vega-themes](https://github.com/vega/vega-themes):

```ts
import * as themes from 'vega-themes';
// Available: 'default', 'ggplot2', 'helix', 'quantum', etc.

const result = await embed('#chart', spec, {
  theme: 'ggplot2'
});
```

Themes are merged with any `config` option (config takes priority).

**Warning:** Themes are experimental and may change in minor version updates.

## Custom Loaders and Credentials

By default, the Vega loader does not send cookies/credentials with data requests:

```ts
// Send credentials for same-origin data
const result = await embed('#chart', spec, {
  loader: { http: { credentials: 'same-origin' } }
});

// Set a base URL for relative data paths
const result = await embed('#chart', spec, {
  loader: { baseURL: 'https://api.example.com/' }
});
```

## Signal Binding

Bind Vega signals to HTML input elements. Specify the binding container element:

```html
<div id="vis">
  <label>Points: <input type="range" min="100" max="1000" value="500"></label>
</div>
```

```ts
const result = await embed('#vis', spec, {
  bind: '#vis'
});
```

The specified element should contain input elements that map to signal names in the spec.

## Error Handling

Always handle rejection from the `embed()` promise:

```ts
try {
  const result = await embed('#chart', spec);
} catch (err) {
  console.error('Failed to embed visualization:', err);
}
```

Common errors:
- Container element not found (`"selector does not exist"`)
- Invalid spec JSON
- Schema version mismatch (logged as warnings, not errors)
- Loader/network failures when fetching remote specs

## Cleanup

Always call `finalize()` when the chart is no longer needed to prevent memory leaks:

```ts
const result = await embed('#chart', spec);
// ... later, when removing the chart:
result.finalize();
```

This unregisters timers, removes event listeners on external DOM elements, and calls `view.finalize()`.
