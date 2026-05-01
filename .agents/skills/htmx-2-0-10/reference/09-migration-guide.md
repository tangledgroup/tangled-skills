# Migration Guide (1.x to 2.x)

## Overview

htmx 2.x is the current major version. Version 1.x continues to be maintained for IE11 compatibility at [v1.htmx.org](https://v1.htmx.org). Most migrations require minimal changes due to htmx's strong backwards compatibility commitment.

## Module Builds

htmx 2 provides module-type specific files:

- **ESM**: `/dist/htmx.esm.js`
- **AMD**: `/dist/htmx.amd.js`
- **CJS**: `/dist/htmx.cjs.js`
- **Browser global**: `/dist/htmx.js` (unchanged)

## Extensions Moved Out of Core

All extensions are distributed as separate packages. Many 1.x extensions work with htmx 2, but you must upgrade the SSE extension to the 2.x version. It is recommended to upgrade all extensions.

If using legacy `hx-ws` and `hx-sse` attributes (inline in core), migrate to the extension versions.

Load extensions separately:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-sse@2.0.0/dist/sse.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.0/dist/ws.js"></script>
```

## `hx-on` Attribute Format Change

Convert `hx-on` (single colon, multiple events in one attribute) to `hx-on:` (separate attributes per event):

**Before (1.x):**
```html
<button hx-get="/info"
        hx-on="htmx:beforeRequest: alert('Making a request!')
               htmx:afterRequest: alert('Done!')">
    Get Info!
</button>
```

**After (2.x):**
```html
<button hx-get="/info"
        hx-on:htmx:before-request="alert('Making a request!')"
        hx-on:htmx:after-request="alert('Done!')">
    Get Info!
</button>
```

Use kebab-case for event names because HTML attributes are case-insensitive.

## Default Behavior Changes

### Scroll Behavior

1.x defaulted to smooth scrolling. 2.x defaults to instant. Revert if needed:

```js
htmx.config.scrollBehavior = 'smooth';
```

### DELETE Request Encoding

1.x sent DELETE with form-encoded body. 2.x sends DELETE with URL parameters (per spec, like GET). Revert if needed:

```js
htmx.config.methodsThatUseUrlParams = ['get'];
```

### Self-Requests Only

2.x defaults `selfRequestsOnly` to `true` (1.x default was `false`). Allow cross-domain requests:

```js
htmx.config.selfRequestsOnly = false;
```

## API Changes

### `htmx.makeFragment()`

Now always returns a `DocumentFragment` rather than either an `Element` or `DocumentFragment`.

### `selectAndSwap` Removed (Extension Authors)

The internal `selectAndSwap` method was removed. Use `swap` instead:

```js
let content = '<div>Hello world</div>';
let target = api.getTarget(elt);
let swapSpec = api.getSwapSpecification(elt);
api.swap(target, content, swapSpec);
```

### IE Support Dropped

IE11 is no longer supported in htmx 2.x. Use htmx 1.x for IE11 compatibility.

## Using the Compat Extension

The `htmx-1-compat` extension restores 1.x defaults and functionality:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-htmx-1-compat@2.0.0/dist/htmx-1-compat.js"></script>
<body hx-ext="htmx-1-compat">
```

This is useful for gradual migration — enable it globally, then remove it as you update individual components.
