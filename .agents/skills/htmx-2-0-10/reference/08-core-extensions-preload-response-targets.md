# Core Extensions: preload and response-targets

## preload Extension

Preloads HTML fragments into the browser cache before the user requests them, making subsequent interactions appear nearly instantaneous.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-preload@2.1.2"></script>
<body hx-ext="preload">
```

Or via npm: `npm install htmx-ext-preload`

### Usage

Add `preload` attribute to links and `hx-get` elements:

```html
<body hx-ext="preload">
  <a href="/server/1" preload>Preloaded on mousedown</a>
  <button hx-get="/server/2" preload>Preloaded with htmx headers</button>
  
  <!-- NOT preloaded — missing preload attribute -->
  <a href="/server/3">Normal link</a>
  
  <!-- NOT preloaded — POST not supported for preloading -->
  <a hx-post="/server/4" preload>POST ignored</a>
</body>
```

### Behavior

- Default trigger: `mousedown` event (gives ~100-200ms head start)
- Only works with GET requests (`href` links and `hx-get`)
- Response is cached in browser; subsequent request uses cache

### Configuration

```javascript
htmx.config.preload.defaultTrigger = 'mouseover';  // or 'mousedown' (default)
htmx.config.preload.delay = 300;                     // ms delay after trigger before fetching
```

### ⚠️ Warning

Preloading too many resources wastes bandwidth and server capacity. Use judiciously on high-traffic navigation links only.

---

## response-targets Extension

Route responses to different DOM targets based on HTTP status code.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-response-targets@2.0.4"></script>
<body hx-ext="response-targets">
```

Or via npm: `npm install htmx-ext-response-targets`

### Attributes

| Attribute | Description |
|-----------|-------------|
| `hx-target-[CODE]` | Target for specific HTTP status code |
| `hx-target-error` | Target for all 4xx and 5xx responses |

### Usage

```html
<form hx-post="/save"
      hx-target="#result"
      hx-target-409="#conflict-error"
      hx-target-500="#server-error"
      hx-target-error="#error-banner">
  <input name="name" />
  <button type="submit">Save</button>
</form>

<div id="result"></div>
<div id="conflict-error" class="hidden"></div>
<div id="server-error" class="hidden"></div>
<div id="error-banner" class="hidden"></div>
```

### Target Values

Same extended selector syntax as `hx-target`:

| Value | Description |
|-------|-------------|
| CSS selector | `#element-id`, `.class-name` |
| `this` | The element with the attribute |
| `closest <selector>` | Closest ancestor |
| `find <selector>` | First descendant |
| `next <selector>` | Next sibling |
| `previous <selector>` | Previous sibling |

```html
<button hx-post="/action"
        hx-target="#output"
        hx-target-error="closest .error-container">
  Submit
</button>
```

### Wildcard Codes

Use wildcard character at end of code:

```html
<form hx-post="/api"
      hx-target-4xx="#client-errors"    <!-- matches 400-499 -->
      hx-target-5xx="#server-errors">   <!-- matches 500-599 -->
</form>
```

### Configuration

```javascript
// Ignore HX-Retarget header when hx-target-* is present
htmx.config.responseTargets.overrideOnRetarget = false;
```

When `HX-Retarget` response header is received, it normally disables extension lookups. Set config to `false` to keep `hx-target-*` active.

### Example: Inline Form Validation

```html
<form hx-post="/register"
      hx-target="#success-message"
      hx-target-422="#validation-errors"
      hx-target-error="#generic-error">
  <input name="email" type="email" required />
  <input name="password" type="password" required />
  <button type="submit">Register</button>
</form>

<div id="success-message"></div>
<div id="validation-errors"></div>
<div id="generic-error"></div>
```

Server returns:
- `200` → success message in `#success-message`
- `422` → validation errors in `#validation-errors`
- `500` → generic error in `#generic-error`
