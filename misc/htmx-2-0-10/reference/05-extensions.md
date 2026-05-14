# Extensions

htmx 2.x moved all extensions out of core into separate packages. Extensions customize library behavior and are enabled via the `hx-ext` attribute.

## Core Extensions

Supported by the htmx development team:

- **head-support** — Merges `<head>` tag information (styles, meta tags) in htmx requests
- **htmx-1-compat** — Restores htmx 1.x defaults and functionality
- **idiomorph** — Morph swap strategy using the Idiomorph algorithm
- **preload** — Preload content for better performance
- **response-targets** — Target elements based on HTTP response codes (e.g., 404)
- **sse** — Server-Sent Events support
- **ws** — WebSocket support

## Installing Extensions

Via CDN (load core htmx first, then extensions):

```html
<head>
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-response-targets@2.0.4/dist/response-targets.min.js"></script>
</head>
<body hx-ext="response-targets">
    ...
</body>
```

Unminified versions are available by removing `.min` from the filename.

Enable extensions on specific elements or globally:

```html
<!-- On a specific element -->
<div hx-ext="preload">
    <a href="/page">Preloaded link</a>
</div>

<!-- Globally on body -->
<body hx-ext="head-support, response-targets">
```

## Custom Extension API

Define custom extensions with `htmx.defineExtension()`:

```js
htmx.defineExtension('my-extension', {
    init: function(api) {
        // Called when htmx starts up
        // api gives access to internal htmx functions
    },
    onEvent: function(name, evt) {
        // Handle htmx events
        return true;
    },
    transformResponse: function(text, xhr, elt) {
        // Transform response text before swapping
        return text;
    },
    isInlineSwap: functionswapStyleName) {
        // Return true if this swap style should be handled inline
        return false;
    },
    handleSwap: functionswapStyle, target, fragment, settleInfo) {
        // Custom swap logic
        // Return true to indicate swap was handled
        return false;
    }
});
```

Enable with `hx-ext="my-extension"` on any element.

## Removing Extensions

```js
htmx.removeExtension('extension-name');
```

## Finding Extensions

Browse all available extensions on the [htmx Extensions page](https://htmx.org/extensions). Community extensions cover use cases like:

- **debug** — Debugging output
- **json-enc** — JSON request encoding
- **multi-swap** — Multiple target swaps from one response
- **path-deps** — Reload elements with matching paths
- **ajax-mobsync** — MobX synchronization
- **class-tools** — Class manipulation utilities
- **loader** — Loading indicator management
