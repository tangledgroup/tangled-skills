# Validation and Security

## HTML5 Validation Integration

htmx integrates with the HTML5 Validation API. It will not issue a request for a form if a validatable input is invalid. This applies to both AJAX requests and WebSocket sends.

Non-form elements do not validate by default. Enable validation with `hx-validate="true"`:

```html
<input name="email" type="email"
       hx-post="/validate"
       hx-trigger="blur"
       hx-validate="true">
```

### Validation Events

- **`htmx:validation:validate`** — Before `checkValidity()` is called. Hook in custom validation.
- **`htmx:validation:failed`** — When `checkValidity()` returns false.
- **`htmx:validation:halted`** — Request not issued due to validation errors. Check `event.detail.errors` for specifics.

### Custom Validation Example

```html
<form id="example-form" hx-post="/test">
    <input name="example"
           onkeyup="this.setCustomValidity('')"
           hx-on::htmx:validation:validate="
               if(this.value != 'foo') {
                   this.setCustomValidity('Please enter the value foo');
                   htmx.find('#example-form').reportValidity();
               }
           ">
</form>
```

### Reporting Validation Errors

By default, htmx does not auto-report validation errors to users (for backwards compatibility). Enable to match browser form behavior:

```js
htmx.config.reportValidityOfForms = true;
```

**Always re-validate on the server.** Client-side validation can be bypassed.

## Security

### Rule 1: Escape All User Content

Do not trust user input. Escape all third-party, untrusted content injected into your site to prevent XSS attacks. Most server-side templating languages support automatic escaping.

When injecting raw HTML (via `raw()` or similar), scrub it including removing `hx-*` and `data-hx-*` attributes, and inline `<script>` tags. Whitelist allowed attributes and tags rather than blacklisting disallowed ones.

### `hx-disable`

Prevent htmx processing on an element and all its children:

```html
<div hx-disable>
    <!-- Raw user content here; htmx attributes are ignored -->
</div>
```

This cannot be overridden by injecting further content — if `hx-disable` exists anywhere in the parent hierarchy, child elements are not processed.

### `hx-history`

Prevent sensitive data from being stored in the history cache:

```html
<div hx-history="false">
    <!-- Sensitive content not cached -->
</div>
```

### Security Configuration Options

- **`htmx.config.selfRequestsOnly`** — Default `true`. Only allow requests to the same domain as the current document.
- **`htmx.config.allowScriptTags`** — Default `true`. Set to `false` to prevent processing `<script>` tags in loaded content.
- **`htmx.config.historyCacheSize`** — Set to `0` to disable localStorage caching entirely.
- **`htmx.config.allowEval`** — Default `true`. Set to `false` to disable eval-dependent features:
  - Event filters (`hx-trigger="click[expr]"`)
  - `hx-on:` attributes
  - `hx-vals` with `js:` prefix
  - `hx-headers` with `js:` prefix

### URL Validation Event

Allow requests to specific domains beyond the current host using `htmx:validateUrl`:

```js
document.body.addEventListener('htmx:validateUrl', function(evt) {
    if (!evt.detail.sameHost && evt.detail.url.hostname !== 'myserver.com') {
        evt.preventDefault();
    }
});
```

### Content Security Policy

Use CSP headers for layered security:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self';">
```

This restricts connections to the origin domain, complementing `htmx.config.selfRequestsOnly`.

### CSRF Prevention

Add CSRF tokens globally via `hx-headers` on `<html>` or `<body>`:

```html
<html lang="en" hx-headers='{"X-CSRF-TOKEN": "token_here"}'>
```

Or use hidden form inputs (preferred, supported by most web frameworks):

```html
<form hx-post="/action">
    <input type="hidden" name="csrf_token" value="token_here">
    ...
</form>
```

Note: `hx-boost` does not update `<html>` or `<body>`. When using boost, place CSRF tokens on elements that will be replaced.

## CSS Classes

htmx applies these classes during request lifecycle:

- **`htmx-request`** — Applied to the requesting element (or `hx-indicator` target) while a request is in flight
- **`htmx-added`** — Applied to new content before swap, removed after settling
- **`htmx-swapping`** — Applied before content swap, removed after swap
- **`htmx-settling`** — Applied after content swap, removed after settling
- **`htmx-indicator`** — Hidden by default (opacity: 0), revealed when `htmx-request` is present on a parent

Custom indicator CSS:

```css
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline; }
.htmx-request.htmx-indicator { display: inline; }
```

## Configuration Reference

Key configuration options accessible via `htmx.config`:

- **`historyEnabled`** — `true`, useful to disable for testing
- **`historyCacheSize`** — `10`
- **`refreshOnHistoryMiss`** — `false`, full page refresh on history miss if `true`
- **`defaultSwapStyle`** — `'innerHTML'`
- **`defaultSwapDelay`** — `0`
- **`defaultSettleDelay`** — `20`
- **`includeIndicatorStyles`** — `true`
- **`indicatorClass`** — `'htmx-indicator'`
- **`requestClass`** — `'htmx-request'`
- **`addedClass`** — `'htmx-added'`
- **`settlingClass`** — `'htmx-settling'`
- **`swappingClass`** — `'htmx-swapping'`
- **`allowEval`** — `true`
- **`allowScriptTags`** — `true`
- **`inlineScriptNonce`** — `''`
- **`inlineStyleNonce`** — `''`
- **`attributesToSettle`** — `['class', 'style', 'width', 'height']`
- **`wsReconnectDelay`** — `'full-jitter'`
- **`wsBinaryType`** — `'blob'`
- **`disableSelector`** — `'[hx-disable], [data-hx-disable]'`
- **`withCredentials`** — `false`
- **`timeout`** — `0` (milliseconds)
- **`scrollBehavior`** — `'instant'` (also `'smooth'`, `'auto'`)
- **`defaultFocusScroll`** — `false`
- **`getCacheBusterParam`** — `false`
- **`globalViewTransitions`** — `false`
- **`methodsThatUseUrlParams`** — `['get', 'delete']`
- **`selfRequestsOnly`** — `true`
- **`ignoreTitle`** — `false`
- **`disableInheritance`** — `false`
- **`scrollIntoViewOnBoost`** — `true`
- **`triggerSpecsCache`** — `null`
- **`responseHandling`** — Default response code handling array
- **`allowNestedOobSwaps`** — `true`
- **`historyRestoreAsHxRequest`** — `true`
- **`reportValidityOfForms`** — `false`

Configure via `<meta>` tag:

```html
<meta name="htmx-config" content='{"defaultSwapStyle":"outerHTML"}'>
```
