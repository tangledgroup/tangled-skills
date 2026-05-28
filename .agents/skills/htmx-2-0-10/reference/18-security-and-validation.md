# Security and Validation

Input validation, security best practices, and attribute inheritance control.

## HTML5 Validation Integration

htmx integrates with the browser's native Validation API.

### hx-validate

Force form validation before sending:

```html
<form hx-post="/save" hx-validate="true">
  <input name="email" type="email" required />
  <input name="age" type="number" min="18" />
  <button type="submit">Submit</button>
</form>
```

By default, htmx validates forms on submit. `hx-validate="true"` forces validation even on non-submit triggers.

### Validation with Non-Form Elements

```html
<input name="username"
       hx-post="/check"
       hx-trigger="blur"
       hx-validate="true"
       required
       minlength="3" />
```

### reportValidityOfForms

htmx calls `reportValidity()` on forms before requests. You can customize:

```javascript
// Disable automatic validation
htmx.config.scrollIntoViewOnInvalidHmxError = false;
```

### Custom Validation with hx-on

```html
<form hx-post="/save"
      hx-on::before-request="if(this.querySelector('input').value.length < 3) { htmx.abort(this); }">
  <input name="name" />
  <button type="submit">Save</button>
</form>
```

## Validation Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:validation:validate` | During validation of each field | `name`, `valid`, `value`, `elt`, `error` |
| `htmx:validation:failed` | Field validation failed | `name`, `valid`, `value`, `elt`, `error`, `errors` |
| `htmx:validation:halted` | Request halted due to validation failure | `elt`, `errors` |
| `htmx:validation:warn` | Validation warning (non-blocking) | `name`, `message`, `elt` |

```javascript
document.body.addEventListener('htmx:validation:halted', function(evt) {
  console.log('Validation errors:', evt.detail.errors);
  // Show custom error UI
});
```

## Security Best Practices

### Escaping User Content

Always escape user-provided content on the server before including in HTML responses. htmx swaps raw HTML — the server is responsible for escaping.

### hx-disable

Disable elements during requests to prevent double-submission:

```html
<button hx-post="/charge" hx-disable>Pay Now</button>
```

### Self-Requests-Only

htmx 2 defaults to `selfRequestsOnly = true`, blocking cross-origin requests:

```javascript
// Allow cross-origin (default in htmx 1)
htmx.config.selfRequestsOnly = false;
```

### allowScriptTags

Control whether `<script>` tags in responses are executed:

```javascript
// Disable script execution in responses (recommended for untrusted content)
htmx.config.allowScriptTags = false;
```

### allowEval

Control `hx-vars` JavaScript expression evaluation:

```javascript
// Disable eval (secure default for untrusted environments)
htmx.config.allowEval = false;
```

### htmx:validateUrl Event

Validate URLs before requests are sent:

```javascript
document.body.addEventListener('htmx:validateUrl', function(evt) {
  if (!evt.detail.path.startsWith('/api/')) {
    evt.detail.valid = false;
  }
});
```

Returns `detail.valid = false` to block the request.

### CSRF Prevention

Use `hx-headers` to add CSRF tokens:

```html
<meta name="csrf-token" content="abc123" />

<button hx-post="/action"
        hx-headers='{"X-CSRF-Token": document.querySelector("meta[name=csrf-token]").content}'>
  Submit
</button>
```

Or globally:

```javascript
document.body.addEventListener('htmx:configRequest', function(evt) {
  evt.detail.headers['X-CSRF-Token'] =
    document.querySelector('meta[name=csrf-token]').content;
});
```

### Content Security Policy (CSP)

For inline scripts in htmx responses, use nonce:

```javascript
htmx.config.inlineScriptNonce = 'your-csp-nonce-here';
```

Or use the `safe-nonce` extension.

## Inheritance Control

htmx attributes inherit from parent elements by default. Control this with:

### hx-disinherit

Prevent specific attributes from inheriting:

```html
<div hx-target="#global-result">
  <button hx-get="/data"
          hx-disinherit="hx-target"
          hx-target="#local-result">
    Uses local target, not inherited
  </button>
</div>

<!-- Disinherit all -->
<button hx-get="/data" hx-disinherit="*">
  No inheritance at all
</button>
```

### hx-inherit

Explicitly specify which attributes to inherit:

```html
<div hx-target="#result" hx-swap="outerHTML">
  <button hx-get="/data"
          hx-inherit="hx-target:hx-swap">
    Inherits target but not swap
  </button>
</div>
```

### Disable All Inheritance

```javascript
htmx.config.disableInheritance = true;
```

### Inheritance Hierarchy

By default, these attributes inherit:
- `hx-headers`, `hx-params`, `hx-preserve`, `hx-target`, `hx-swap`,
  `hx-select`, `hx-select-oob`, `hx-indicator`, `hx-push-url`,
  `hx-swap-oob`, `hx-sync`, `hx-on*`, `hx-vals`, `hx-vars`,
  `hx-disabled-elt`, `hx-disable`, `hx-encoding`, `hx-request`,
  `hx-history`, `hx-history-elt`, `hx-inherit`, `hx-disinherit`
