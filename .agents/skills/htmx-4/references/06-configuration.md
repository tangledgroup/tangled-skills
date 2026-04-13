# Configuration Reference

## Global Configuration

Configure htmx globally via `htmx.config` object:

```javascript
// Set configuration before htmx processes elements
htmx.config.defaultSwapStyle = 'innerHTML';
htmx.config.timeout = 10000;
```

## Configuration Options

### Request Behavior

| Option | Default | Description |
|--------|---------|-------------|
| `defaultSwap` | `'innerHTML'` | Default swap style for all requests |
| `defaultSwapDelay` | Removed in 4.x | Use `delay:` in `hx-swap` instead |
| `defaultSettleDelay` | `1` (ms) | Delay between swap and settle |
| `defaultTimeout` | `60000` (ms) | Request timeout (0 = no timeout) |
| `includeIndicatorCSS` | `true` | Include default indicator styles |

```javascript
// Custom defaults
htmx.config.defaultSwap = 'outerHTML';
htmx.config.defaultSettleDelay = 10;
htmx.config.defaultTimeout = 30000;
htmx.config.includeIndicatorCSS = false;
```

### History Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `history` | `true` | Enable history (`"reload"` or `false`) |

```javascript
// Full page reload on history navigation
htmx.config.history = "reload";

// Disable history entirely
htmx.config.history = false;

// Default: fetch and swap into body
htmx.config.history = true;
```

**Note:** htmx 4 no longer caches pages in localStorage. Pages re-fetch on back navigation.

### Attribute Inheritance

| Option | Default | Description |
|--------|---------|-------------|
| `implicitInheritance` | `false` | Implicit attribute inheritance (htmx 2 style) |

```javascript
// Restore htmx 2 implicit inheritance
htmx.config.implicitInheritance = true;
```

Or use `:inherited` modifier explicitly (recommended for htmx 4).

### Response Handling

| Option | Default | Description |
|--------|---------|-------------|
| `noSwap` | `[204, 304]` | Status codes that don't swap |
| `responseHandling` | Removed in 4.x | Use `hx-status` instead |

```javascript
// Don't swap error responses (htmx 2 behavior)
htmx.config.noSwap = [204, 304, '4xx', '5xx'];

// Custom no-swap codes
htmx.config.noSwap = [204, 304, 401, 403];
```

### Fetch Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `mode` | `'same-origin'` | Fetch mode (replaces `selfRequestsOnly`) |

```javascript
// Allow cross-origin requests
htmx.config.mode = 'cors';

// Other modes: 'no-cors', 'omit', 'same-origin'
htmx.config.mode = 'no-cors';
```

### Security

| Option | Default | Description |
|--------|---------|-------------|
| `inlineScriptNonce` | `''` | Nonce for inline scripts (CSP) |
| `inlineStyleNonce` | `''` | Nonce for inline styles (CPS) |

```javascript
// Set nonce for CSP compliance
htmx.config.inlineScriptNonce = document.querySelector('script[nonce]').nonce;
htmx.config.inlineStyleNonce = document.querySelector('style[nonce]').nonce;
```

### Extensions

| Option | Default | Description |
|--------|---------|-------------|
| `extensions` | `''` | Comma-separated list of allowed extension names |

```javascript
// Restrict which extensions can load
htmx.config.extensions = 'sse,ws,preload';
```

Or via meta tag:

```html
<meta name="htmx-config" content='{"extensions": "sse, ws"}'>
```

### View Transitions

| Option | Default | Description |
|--------|---------|-------------|
| `transitions` | `false` | Enable View Transitions API |

```javascript
// Enable view transitions globally
htmx.config.transitions = true;
```

Or per-element with `hx-swap="innerHTML transition:true"`.

### Morph Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `morphIgnore` | `''` | CSS selector for elements to ignore during morph |
| `morphSkip` | `''` | CSS selector for elements to skip during morph |
| `morphSkipChildren` | `''` | CSS selector for elements whose children to skip |
| `morphScanLimit` | undefined | Max elements to scan during morph matching |

```javascript
// Preserve certain elements during morph
htmx.config.morphIgnore = '.preserve-state';
htmx.config.morphSkip = '.skip-update';
htmx.config.morphSkipChildren = '.static-content';
htmx.config.morphScanLimit = 1000;
```

### Logging and Debugging

| Option | Default | Description |
|--------|---------|-------------|
| `logAll` | `false` | Log all htmx events to console |

```javascript
// Enable comprehensive logging
htmx.config.logAll = true;
```

Alternative:

```javascript
htmx.logAll();  // Enable
htmx.logNone();  // Disable
```

### JSX Compatibility

| Option | Default | Description |
|--------|---------|-------------|
| `metaCharacter` | `':'` | Separator character in attribute/event names |

```javascript
// Use hyphen instead of colon (for JSX frameworks)
htmx.config.metaCharacter = '-';

// Now use hx-ws-connect instead of hx-ws:connect
// And hx-confirm-inherited instead of hx-confirm:inherited
```

### CSS Class Names

These options were removed in htmx 4. Use custom CSS with standard class names:

- `htmx-request`: Element with active request
- `htmx-added`: Newly added element
- `htmx-swapping`: Element being swapped
- `htmx-settling`: Element settling after swap

```css
/* Customize appearance */
.htmx-request { opacity: 0.5; }
.htmx-added { animation: fade-in 0.3s; }
```

## Meta Tag Configuration

Configure htmx via `<meta>` tag (useful when script must load before config):

```html
<head>
  <meta name="htmx-config" content='{"defaultTimeout": 10000, "includeIndicatorCSS": false}'>
  <script src="/htmx.min.js"></script>
</head>
```

Supported options:
- `defaultTimeout`
- `includeIndicatorCSS`
- `extensions`
- `inlineScriptNonce`
- `inlineStyleNonce`
- Any other config option

## Environment Variable Configuration

For server-side rendering or build-time configuration:

```html
<script>
  // Set config from environment variables
  htmx.config.defaultTimeout = parseInt(HTMX_TIMEOUT || '60000');
  htmx.config.inlineScriptNonce = '{{ .Nonce }}';
</script>
<script src="/htmx.min.js"></script>
```

## Per-Element Configuration

Use `hx-config` attribute for element-specific overrides:

```html
<!-- JSON syntax -->
<button hx-post="/api/data" 
        hx-config='{"timeout": 5000, "headers": {"X-Custom": "value"}}'>
  Fetch Data
</button>

<!-- Key:value syntax -->
<form hx-post="/submit" 
      hx-config="timeout:10s headers:X-API-Key:secret validate:false">
  <button type="submit">Submit</button>
</form>
```

Supported keys in `hx-config`:
- `timeout`: Request timeout in ms
- `headers`: Custom headers object
- `credentials`: "omit", "same-origin", or "include"
- `validate`: Boolean to enable/disable validation
- `target`: Override target selector
- `swap`: Override swap style
- `select`: Response selection CSS selector

## Removed Configuration (htmx 2 → 4)

These options were removed in htmx 4:

| htmx 2 Option | Status | Alternative |
|---------------|--------|-------------|
| `addedClass` | Removed | Use `.htmx-added` class |
| `allowEval` | Removed | Not needed |
| `allowNestedOobSwaps` | Removed | Always allowed |
| `allowScriptTags` | Removed | Use nonce instead |
| `attributesToSettle` | Removed | Internal implementation |
| `defaultSwapDelay` | Removed | Use `delay:` in `hx-swap` |
| `disableSelector` | Removed | Use `hx-ignore` attribute |
| `getCacheBusterParam` | Removed | Not needed |
| `historyCacheSize` | Removed | No localStorage caching |
| `ignoreTitle` | Partially removed | Use `ignoreTitle:true` in `hx-swap` |
| `methodsThatUseUrlParams` | Removed | Internal implementation |
| `refreshOnHistoryMiss` | Removed | Always re-fetches |
| `responseHandling` | Removed | Use `hx-status` and `noSwap` |
| `scrollBehavior` | Removed | Use `show:` in `hx-swap` |
| `scrollIntoViewOnBoost` | Removed | Not needed |
| `selfRequestsOnly` | Removed | Use `mode` instead |
| `settlingClass` | Removed | Use `.htmx-settling` class |
| `swappingClass` | Removed | Use `.htmx-swapping` class |
| `triggerSpecsCache` | Removed | Internal implementation |
| `useTemplateFragments` | Removed | Not needed |
| `withCredentials` | Removed | Use `hx-config` with `credentials` |
| `wsBinaryType` | Removed | Set on socket directly |
| `wsReconnectDelay` | Removed | Use `sseReconnectDelay` |

## Migration Checklist for Configuration

When migrating from htmx 2.x:

1. **Set explicit inheritance**: Remove `implicitInheritance = true` or add `:inherited` modifiers
2. **Update timeout**: Set `defaultTimeout` if relying on unlimited timeout
3. **Configure error handling**: Set `noSwap` if not wanting to swap 4xx/5xx responses
4. **Replace removed options**: Map old config to new alternatives
5. **Update class names**: Change custom class selectors to new standard names
6. **Test history behavior**: Verify back navigation works as expected
7. **Verify CSP compliance**: Set nonces if using strict CSP

## Best Practices

### Production Configuration

```javascript
// Production settings
htmx.config.defaultTimeout = 30000;  // 30 second timeout
htmx.config.logAll = false;  // Disable logging
htmx.config.inlineScriptNonce = getNonce();  // CSP compliance
htmx.config.extensions = 'sse,ws';  // Whitelist extensions
```

### Development Configuration

```javascript
// Development settings
htmx.config.defaultTimeout = 60000;  // Longer timeout for debugging
htmx.config.logAll = true;  // Enable comprehensive logging
htmx.config.inlineScriptNonce = '';  // No nonce needed locally
```

### Testing Configuration

```javascript
// Test settings
htmx.config.history = false;  // Disable history in tests
htmx.config.defaultSettleDelay = 0;  // Immediate settling for faster tests
```
