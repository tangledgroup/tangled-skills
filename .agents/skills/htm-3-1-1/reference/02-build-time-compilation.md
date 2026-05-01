# Build-Time Compilation

## Overview

While htm's main selling point is zero-transpilation runtime usage, `babel-plugin-htm` allows you to compile htm tagged templates into hyperscript calls at build time. This eliminates the ~600 byte runtime cost entirely — achieving **0 bytes** for htm in production builds.

The typical workflow is: develop with htm's runtime tagged templates for rapid iteration, then compile them away for production.

## babel-plugin-htm

### Setup

Add the plugin to your Babel configuration (`.babelrc`, `babel.config.js`, or `"babel"` field in `package.json`):

```js
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement"
    }]
  ]
}
```

### Basic Transformation

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output (compiled to hyperscript):
React.createElement("div", { id: "foo" }, "hello ", you)
```

### Configuration Options

#### `pragma` (default: `"h"`)

Specifies the target hyperscript function to compile elements to:

```js
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement"
    }]
  ]
}
```

Dotted paths are supported:

```js
{ "pragma": "h" }                    // h("div", ...)
{ "pragma": "React.createElement" }  // React.createElement("div", ...)
```

#### `tag` (default: `"html"`)

By default, only tagged templates with the tag function named `html` are processed. Use a different name:

```js
{
  "plugins": [
    ["htm", {
      "tag": "myCustomHtmlFunction"
    }]
  ]
}
```

The tag name can also be a regex pattern:

```js
{ "tag": "/^html$/" }
```

#### `import` (default: `false`)

Auto-import the pragma function. Off by default.

As a string — imports the pragma directly:

```js
{
  "plugins": [
    ["htm", {
      "tag": "$$html",
      "import": "htm/preact"
    }]
  ]
}
```

This produces:

```js
// Input:
import { html as $$html } from 'htm/preact';
export default $$html`<div id="foo">hello ${you}</div>`

// Output:
import { h } from 'preact';
import { html as $$html } from 'htm/preact';
export default h("div", { id: "foo" }, "hello ", you)
```

As an object — custom module and export:

```js
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement",
      "tag": "$$html",
      "import": {
        "module": "react",
        "export": "default"
      }
    }]
  ]
}
```

Produces:

```js
import React from 'react';
export default React.createElement("div", { id: "foo" }, "hello ", you)
```

#### `useBuiltIns` (default: `false`)

Controls how prop spreads (`<a ...${b}>`) are transformed. By default, Babel's `_extends` helper is used. Set to `true` to use native `Object.assign`:

```js
{ "useBuiltIns": true }
// <a ...${b}> becomes Object.assign({}, b)
```

#### `useNativeSpread` (default: `false`)

Use object spread syntax `{ ...a, ...b }` instead of Babel's `_extends` helper for prop spreads. Takes precedence over `useBuiltIns`:

```js
{ "useNativeSpread": true }
// <a ...${b} x=y> becomes { ...b, x: 'y' }
```

#### `variableArity` (default: `true`)

When `true` (default), output matches JSX: `h(type, props, ...children)` with variable argument count.

When `false`, always passes exactly 3 arguments with children as an array:

```js
// With variableArity: false
html`<div />`          // h('div', null, [])
html`<div a />`        // h('div', { a: true }, [])
html`<div>b</div>`     // h('div', null, ['b'])
```

#### `pragma: false` — Plain Object Output

Setting pragma to `false` outputs plain objects instead of function calls:

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output:
{ tag: "div", props: { id: "foo" }, children: ["hello ", you] }
```

#### `monomorphic` — Uniform Object Shape

Like `pragma: false` but converts all inline text to objects with a consistent shape:

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output:
{
  type: 1, tag: "div", props: { id: "foo" }, text: null, children: [
    { type: 3, tag: null, props: null, text: "hello ", children: null },
    you
  ]
}
```

## The `treeify` Helper

htm exports a `treeify` function that converts the internal build representation into a more convenient tree structure for analysis and transformation:

```js
import { treeify, build } from 'htm/build';

const result = treeify(build`<div href="1${a}"><${x} /></div>`, [X, Y, Z]);
// Returns:
// {
//   tag: 'div',
//   props: [{ href: ["1", X] }, Y],
//   children: [{ tag: Z, props: [], children: [] }]
// }
```

This is primarily useful for writing custom transforms or tooling that analyzes htm templates.

## Development vs Production Strategy

A common pattern is to use htm's runtime during development and compile it away in production:

1. **Development**: Use `htm/preact` or `htm/react` bindings directly — no build step needed
2. **Production**: Add `babel-plugin-htm` to your build pipeline to compile templates to hyperscript calls, reducing bundle size by ~600 bytes

This gives you the best of both worlds: rapid development without tooling, and optimized production builds.
