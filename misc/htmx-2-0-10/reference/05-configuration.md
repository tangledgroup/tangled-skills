# Configuration

All htmx 2.0.10 configuration variables, meta tag configuration, and response handling options.

## Config Variables

Set via `htmx.config.<key>` or `<meta name="hx-<key>" content="<value>">`.

### History

| Key | Default | Description |
|-----|---------|-------------|
| `historyEnabled` | `true` | Enable history push/replace on AJAX requests |
| `historyCacheSize` | `10` | Number of pages stored in history cache |
| `refreshOnHistoryMiss` | `false` | Full page reload on history cache miss |
| `htmx:confirm` | — | Global confirm handler (function returning boolean) |

### Request/Response

| Key | Default | Description |
|-----|---------|-------------|
| `defaultSwapStyle` | `"innerHTML"` | Default swap style |
| `defaultSwapDelay` | `0` | Default swap delay in ms |
| `defaultSettleDelay` | `0` | Default settle delay in ms |
| `defaultTimeout` | `0` | Request timeout in ms (0 = no timeout) |
| `useTemplateFragments` | `false` | Parse responses as `<template>` fragments |
| `allowEval` | `true` | Allow evaluating expressions in `hx-vars` |
| `allowScriptTags` | `true` | Allow `<script>` tags in responses |
| `inlineScriptNonce` | `""` | Nonce for inline scripts |
| `selfRequestsOnly` | `true` | Only allow requests to same origin (htmx 2 default) |
| `ignoreTitle` | `false` | Don't update `<title>` from responses |
| `clearBarOnCacheMiss` | `false` | Clear address bar on history cache miss |

### Security

| Key | Default | Description |
|-----|---------|-------------|
| `withCredentials` | `false` | Send cookies with cross-origin requests |
| `timeout` | `0` | Default timeout for all requests |
| `wsReconnectDelay` | `"full-jitter"` | WebSocket reconnect delay strategy |

### WebSocket Config

| Key | Default | Description |
|-----|---------|-------------|
| `wsReconnectDelay` | `"full-jitter"` | `"full-jitter"`, `"fixed"`, or custom function `(retries) => ms` |

### View Transitions

| Key | Default | Description |
|-----|---------|-------------|
| `viewTransitionsEnabled` | `false` | Enable View Transitions API on swaps |

### Debugging

| Key | Default | Description |
|-----|---------|-------------|
| `requestClass` | `"htmx-request"` | Class added to element during request |
| `addedClass` | `"htmx-added"` | Class added to new elements before settling |
| `settlingClass` | `"htmx-settling"` | Class during settle phase |
| `swappingClass` | `"htmx-swapping"` | Class during swap phase |

### Internal

| Key | Default | Description |
|-----|---------|-------------|
| `allowNestedOobSwaps` | `true` | Allow OOB swaps inside OOB swaps |
| `disableInheritance` | `false` | Disable all attribute inheritance |
| `scrollBehavior` | `"instant"` | Scroll behavior (`"smooth"` or `"instant"`) |
| `defaultFocusScroll` | `false` | Scroll focused element into view |
| `cacheErrorsForMinutes` | `10` | How long to cache error responses |
| `returnXHR` | `false` | Return XHR object from ajax() |
| `extendResponseTransformer` | `function(ajaxHead, xhr, elt)` | Custom response transformer |
| `transformResponse` | `null` | Custom response text transformer function |
| `axisScroll` | `false` | Use axis-specific scrolling |
| `triggerSpecsCache` | `null` | Cache for trigger spec parsing |
| `getCacheBusterParam` | `false` | Append `?__htmx=` with timestamp to GET requests |
| `urlAction` | `"replace"` | URL action on boost (`"replace"` or `"push"`) |
| `globalViewTransitions` | `false` | Enable view transitions globally |
| `methodsThatUseUrlParams` | `["get","post","put","patch","delete"]` | Methods that encode params in URL |
| `urlEncoding` | `null` | Custom URL encoding function |
| `wsConfigs` | `[]` | Array of WebSocket config objects |
| `pathDepsUrlEncode` | `true` | URL-encode path dependency values |
| `onlyUseInputFrom` | `[<form>, <body>]` | Elements to collect input from for requests |
| `scrollIntoViewOnInvalidHmxError` | `true` | Scroll to invalid field on validation error |
| `prompt` | `null` | Custom prompt function |
| `confirm` | `null` | Custom confirm function |
| `disableDebug` | `false` | Disable debug output |

## Meta Tag Configuration

Set config via HTML meta tags (no JavaScript needed):

```html
<meta name="hx-history-cache-size" content="20" />
<meta name="hx-default-swap-style" content="outerHTML" />
<meta name="hx-allow-script-tags" content="false" />
<meta name="hx-self-requests-only" content="false" />
<meta name="hx-history-enabled" content="false" />
```

Meta tag names use `hx-` prefix with kebab-case.

## Response Handling Configuration

Configure how htmx handles different HTTP response codes:

```javascript
htmx.config.responseHandling = [
  { code: "20.", action: "swap" },       // 2xx → swap
  { code: "130-399", action: "swap" },    // range → swap
  { code: "400-494", action: "error" },   // 4xx (except 495+) → error
  { code: "495-498", action: "swap" },    // specific range → swap
  { code: "499-599", action: "error" },   // 5xx → error
  { code: "info", action: "ignore" },     // informational → ignore
  { code: "error", action: "error" }      // catch-all errors
];
```

| Action | Description |
|--------|-------------|
| `swap` | Swap the response into the target |
| `error` | Fire `htmx:responseError`, do not swap |
| `ignore` | Silently ignore the response |
| `noop-on-404` | Don't swap on 404, but don't error either |

## Custom Confirm/Prompt

```javascript
// Global custom confirm
htmx.config.confirm = function(message) {
  return window.confirm(message);
};

// Per-request confirm via hx-confirm or hx-request
<button hx-delete="/item" hx-confirm="Delete this item?">Delete</button>
```

## Custom Transform Response

Transform response text before parsing:

```javascript
htmx.config.transformResponse = function(text, xhr, elt) {
  // Strip HTML comments
  return text.replace(/<!--[\s\S]*?-->/g, '');
};
```
