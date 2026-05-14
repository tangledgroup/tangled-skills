# HTTP Headers

## Request Headers

htmx automatically adds these headers to every AJAX request:

**`HX-Request: true`** — Always present. Detect htmx requests on the server.

```python
# Python example
if request.headers.get('HX-Request') == 'true':
    return render_template('fragment.html')  # Return HTML fragment
else:
    return render_template('full_page.html')  # Return full page
```

**`HX-Target`** — The `id` of the target element (if it has one).

**`HX-Trigger-Name`** — The `name` of the triggered element (if it has one).

**`HX-Trigger`** — The `id` of the triggered element (if it has one).

**`HX-Boosted`** — Present when the request is from an `hx-boost` element.

**`HX-Current-URL`** — The current URL of the browser.

**`HX-History-Restore-Request`** — Set to `"true"` when the request is for history restoration after a cache miss.

**`HX-Prompt`** — The user's response to an `hx-prompt` dialog.

### Adding Custom Headers

Use `hx-headers` with JSON:

```html
<button hx-post="/api" hx-headers='{"X-Custom": "value"}'>Submit</button>
```

Or via events:

```js
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['Authorization'] = 'Bearer ' + getToken();
});
```

Place `hx-headers` on `<html>` or `<body>` for global headers (useful for CSRF tokens):

```html
<body hx-headers='{"X-CSRF-TOKEN": "token_value"}'>
```

Note: `hx-boost` does not update `<html>` or `<body>`, so place CSRF tokens on elements that will be replaced, or use hidden form inputs.

## Response Headers

htmx processes these special response headers from the server:

**`HX-Redirect`** — Client-side redirect to a new location (full page reload):

```
HX-Redirect: /new-page
```

**`HX-Refresh`** — Full page refresh when set to `"true"`:

```
HX-Refresh: true
```

**`HX-Location`** — Client-side redirect without full reload (uses htmx internal navigation):

```
HX-Location: /new-page
```

**`HX-Push-Url`** — Push a URL into the history stack. Set to `"true"` to push the request URL, or provide a specific URL:

```
HX-Push-Url: /items/42
```

**`HX-Replace-Url`** — Replace the current URL in the location bar:

```
HX-Replace-Url: /items/42
```

**`HX-Trigger`** — Trigger client-side events. Supports responding to other triggered events:

```
HX-Trigger: myEventName
HX-Trigger: after-me,myEventName
```

**`HX-Trigger-After-Swap`** — Trigger events after the swap step.

**`HX-Trigger-After-Settle`** — Trigger events after the settle step.

**`HX-Retarget`** — CSS selector to update the target of the content update:

```
HX-Retarget: #actual-target
```

**`HX-Reselect`** — CSS selector overriding `hx-select` on the triggering element:

```
HX-Reselect: #different-content
```

**`HX-Reswap`** — Override the swap style for this response:

```
HX-Reswap: outerHTML
```

## Response Handling Configuration

htmx handles different HTTP status codes by default:

- **204** — No Content. Nothing swapped, not an error.
- **2xx / 3xx** — Swapped into the target (not errors).
- **4xx / 5xx** — Not swapped, treated as errors. `htmx:responseError` fired.
- **Other** — Not swapped.

Customize via `htmx.config.responseHandling`:

```js
htmx.config.responseHandling = [
    {code: '204', swap: false},           // 204 - no swap, not error
    {code: '[23]..', swap: true},         // 2xx/3xx - swap, not error
    {code: '[45]..', swap: false, error: true},  // 4xx/5xx - no swap, error
    {code: '...', swap: false}            // catch-all
];
```

Each entry's `code` is treated as a regular expression against the response status code. Fields:

- **`code`** — Regex string matching response codes
- **`swap`** — Whether to swap the response into the DOM
- **`error`** — Whether to treat the response as an error (fires `htmx:responseError`)

## Caching

htmx works with standard HTTP caching. Key considerations:

- If your server renders different content based on `HX-Request` header, use `Vary: HX-Request` so cache keys differ for full-page vs fragment responses
- Set `htmx.config.getCacheBusterParam = true` to append a cache-busting parameter to GET requests (alternative to `Vary`)
- Always disable `htmx.config.historyRestoreAsHxRequest` when using `HX-Request` to conditionally return partials, so history full-page requests are not cached with fragment responses
