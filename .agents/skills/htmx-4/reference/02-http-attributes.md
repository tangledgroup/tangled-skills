# HTTP Attributes Reference

## HTTP Method Attributes

htmx provides attributes for each HTTP method. Each triggers a request with the specified method when the default trigger fires (click for most elements, submit for forms, change for inputs).

### `hx-get`

Makes a GET request. Does not include form data by default.

```html
<!-- Simple GET request -->
<a hx-get="/data" hx-swap="innerHTML">Load Data</a>

<!-- GET with query parameters from element -->
<button hx-get="/search?q=htmx" hx-target="#results">Search</button>

<!-- GET with additional values -->
<a hx-get="/user" hx-vals='{ "token": "abc123" }'>Profile</a>
```

### `hx-post`

Makes a POST request. Includes form data if inside a form.

```html
<!-- POST from form -->
<form hx-post="/submit" hx-swap="outerHTML">
  <input name="username" placeholder="Username">
  <button type="submit">Submit</button>
</form>

<!-- POST from button with values -->
<button hx-post="/like" hx-vals='{ "postId": 42 }'>Like</button>
```

### `hx-put`

Makes a PUT request for updating resources.

```html
<form hx-put="/user/123" hx-swap="none" hx-target="#user-info">
  <input name="email" value="new@email.com">
  <button type="submit">Update</button>
</form>
```

### `hx-patch`

Makes a PATCH request for partial updates.

```html
<button hx-patch="/post/45" hx-vals='{ "status": "published" }'>
  Publish
</button>
```

### `hx-delete`

Makes a DELETE request. Does not include form data by default (changed in htmx 4).

```html
<!-- DELETE without form data -->
<button hx-delete="/item/7">Delete Item</button>

<!-- DELETE with explicit form inclusion -->
<form>
  <button hx-delete="/item" hx-include="closest form">Delete All</button>
</form>
```

**Note:** In htmx 4, `hx-delete` no longer includes enclosing form inputs. Use `hx-include="closest form"` to restore this behavior.

## Flexible Method Specification

### `hx-method`

Specify HTTP method dynamically:

```html
<!-- Dynamic method based on state -->
<button hx-post="/item" hx-method="put">Update</button>

<!-- With action URL -->
<form hx-action="/users" hx-method="post">
  <input name="email">
  <button type="submit">Create User</button>
</form>
```

### `hx-action`

Specify the request URL separately from method:

```html
<!-- Separate URL and method -->
<button hx-action="/api/users" hx-method="post" hx-vals='{ "name": "John" }'>
  Add User
</button>
```

Useful when method or URL is determined dynamically via JavaScript.

## Request Configuration

### `hx-config`

Per-element request configuration using JSON or key:value syntax:

```html
<!-- JSON syntax -->
<button hx-post="/api/data" hx-config='{"timeout": 5000, "headers": { "X-Custom": "value" }}'>
  Fetch Data
</button>

<!-- Key:value syntax -->
<form hx-post="/submit" hx-config="timeout:10s headers:X-Custom-Token:abc123">
  <button type="submit">Submit</button>
</form>
```

Supported config keys:
- `timeout`: Request timeout in ms
- `headers`: Custom headers object
- `credentials`: "omit", "same-origin", or "include"
- `validate`: Boolean to enable/disable validation
- `target`: Override target selector
- `swap`: Override swap style
- `select`: Response selection CSS selector

### `hx-headers`

Add custom request headers:

```html
<!-- Static header -->
<button hx-post="/api/data" hx-headers='{"X-API-Key": "secret123"}'>
  Fetch
</button>

<!-- Dynamic header from JavaScript -->
<form hx-post="/submit" hx-headers='js:{ "X-CSRF-Token": getCsrfToken() }'>
  <button type="submit">Submit</button>
</form>
```

### `hx-include`

Include additional elements' values in the request:

```html
<!-- Include global fields -->
<form hx-post="/submit" hx-include="#global-fields">
  <input name="item" value="test">
  <button type="submit">Submit</button>
</form>

<div id="global-fields" style="display:none">
  <input name="userId" value="123">
  <input name="token" value="abc">
</div>

<!-- Include closest form -->
<button hx-delete="/item" hx-include="closest form">Delete with Form Data</button>

<!-- Multiple includes -->
<form hx-post="/order" hx-include="#user-info, #cart-items">
  <button type="submit">Checkout</button>
</form>
```

## Request Values

### `hx-vals`

Add or override values sent with the request:

```html
<!-- Static values (JSON) -->
<button hx-post="/like" hx-vals='{ "postId": 42, "type": "like" }'>
  Like Post
</button>

<!-- Dynamic values from JavaScript -->
<button hx-post="/track" hx-vals='js:{ "timestamp": Date.now(), "path": window.location.pathname }'>
  Track
</button>

<!-- Mix static and dynamic -->
<form hx-post="/search" hx-vals='{ "source": "sidebar", "timestamp": js:Date.now() }'>
  <input name="q" placeholder="Search">
  <button type="submit">Search</button>
</form>
```

**Migration note:** In htmx 2, `hx-vars` was used for this purpose. Use `hx-vals` with `js:` prefix instead.

## Encoding and Content Type

### `hx-encoding`

Specify how form data is encoded:

```html
<!-- Default: application/x-www-form-urlencoded -->
<form hx-post="/submit">
  <input name="field" value="value">
</form>

<!-- multipart/form-data for file uploads -->
<form hx-post="/upload" hx-encoding="multipart/form-data">
  <input type="file" name="attachment">
  <button type="submit">Upload</button>
</form>

<!-- application/json -->
<form hx-post="/api/data" hx-encoding="application/json">
  <input name="name" value="John">
  <button type="submit">Submit</button>
</form>
```

For JSON encoding, htmx automatically converts form data to JSON object.

## Request Synchronization

### `hx-sync`

Control how multiple requests from the same element or sibling elements are handled:

```html
<!-- Abort previous request before starting new one -->
<input hx-get="/search" hx-trigger="input changed delay:500ms" hx-sync="this">

<!-- Abort all siblings' requests -->
<button hx-post="/action" hx-sync="closest .form-group">Submit</button>

<!-- Stop following redirects from previous request -->
<a hx-get="/page" hx-sync="stop">Load Page</a>

<!-- Queue the request -->
<button hx-post="/process" hx-sync="queue">Process</button>
```

Options:
- `this`: Abort request on same element
- `selector`: Abort requests on matching elements
- `none`: Don't abort (default)
- `stop`: Stop following redirects
- `drop`: Drop new request if one is in flight
- `queue`: Queue the request

## Validation

### `hx-validate`

Control form validation behavior:

```html
<!-- Enable validation (default for forms) -->
<form hx-post="/submit" hx-validate="true">
  <input name="email" type="email" required>
  <button type="submit">Submit</button>
</form>

<!-- Disable validation -->
<button hx-post="/quick-action" hx-validate="false">
  Quick Action
</button>
```

htmx uses native browser validation when enabled. Form won't submit if validation fails.

## Confirm Dialogs

### `hx-confirm`

Show confirmation dialog before request:

```html
<!-- Simple confirm -->
<button hx-delete="/item/1" hx-confirm="Are you sure you want to delete this item?">
  Delete
</button>

<!-- Custom message with OK/Cancel labels -->
<a hx-post="/dangerous" hx-confirm="Warning: This action cannot be undone. Proceed?|Yes, proceed|Cancel">
  Dangerous Action
</a>

<!-- Dynamic confirm from JavaScript -->
<button hx-delete="/item" hx-confirm='js:confirmDelete(this)'>
  Delete
</button>

<script>
function confirmDelete(element) {
  const itemId = element.dataset.id;
  return `Delete item #${itemId}? This cannot be undone.`;
}
</script>
```

### Inherited Confirm

Use `:inherited` to apply confirm to multiple elements:

```html
<div hx-confirm:inherited="Are you sure?|Yes|No">
  <button hx-delete="/item/1">Delete 1</button>
  <button hx-delete="/item/2">Delete 2</button>
  <button hx-delete="/item/3">Delete 3</button>
</div>
```

## Disabling Elements During Request

### `hx-disable`

Disable specified elements while request is in flight (replaces `hx-disabled-elt` from htmx 2):

```html
<!-- Disable submit button during request -->
<form hx-post="/submit" hx-disable="button[type=submit]">
  <input name="data">
  <button type="submit">Submit</button>
</form>

<!-- Disable specific element by ID -->
<button hx-post="/process" hx-disable="#reset-btn">Process</button>

<!-- Disable all buttons in form -->
<form hx-post="/submit" hx-disable="button, input[type=submit]">
  <button type="submit">Submit</button>
  <button type="reset">Reset</button>
</form>
```

**Migration note:** In htmx 2, `hx-disable` meant "ignore htmx processing". That's now `hx-ignore`. The name `hx-disable` now does what `hx-disabled-elt` did.

## Ignoring htmx Processing

### `hx-ignore`

Prevent htmx from processing an element (replaces `hx-disable` from htmx 2):

```html
<!-- This link won't trigger htmx request -->
<a href="/page" hx-get="/api/page" hx-ignore="true">Regular Link</a>

<!-- Ignore all htmx attributes on this element and children -->
<div hx-ignore="true">
  <button hx-post="/action">This won't work</button>
</div>
```

## Boosting Regular Links and Forms

### `hx-boost`

Make regular links and forms use htmx without adding individual attributes:

```html
<!-- Boost all links and forms in this section -->
<div hx-boost="true">
  <a href="/page1">Page 1</a>
  <a href="/page2">Page 2</a>
  <form action="/search"><input name="q"></form>
</div>

<!-- Boost with custom target -->
<main hx-boost="true" hx-target:inherited="#main-content">
  <nav>
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
  </nav>
</main>
```

Boosted elements:
- Use `hx-get` for links, `hx-post` (or original method) for forms
- Swap response into body by default (or inherited target)
- Update browser history automatically

## Request Headers

htmx automatically adds these headers to requests:

| Header | Value | Description |
|--------|-------|-------------|
| `HX-Request` | `true` | Identifies request as htmx |
| `HX-Current-URL` | Current URL | Page URL when request triggered |
| `HX-Target` | `tagName#id` | Target element selector |
| `HX-Trigger` | `tagName#id` | Triggering element selector |
| `HX-Trigger-Name` | Name attribute | Name of triggering element (if present) |
| `HX-Request-Type` | `"full"` or `"partial"` | Request type indicator |
| `Accept` | `text/html` | Explicitly request HTML response |

**Migration note:** In htmx 4, `HX-Trigger` and `HX-Target` format changed to `tagName#id`. `HX-Trigger-Name` is removed.

## Response Headers

Server can send these headers to control htmx behavior:

| Header | Effect |
|--------|--------|
| `HX-Redirect` | Redirect to URL |
| `HX-Refresh` | Refresh current page |
| `HX-Location` | Client-side redirect with content |
| `HX-Push-Url` | Push URL to history |
| `HX-Replace-Url` | Replace current history entry |
| `HX-Trigger` | Trigger client events |
| `HX-Reselect` | Override `hx-select` |
| `HX-Retarget` | Override target |
| `HX-Reswap` | Override swap style |

Example server response (Express.js):

```javascript
res.setHeader('HX-Trigger', 'search-complete');
res.setHeader('HX-Push-Url', '/results?q=htmx');
res.send(`
  <div id="results">
    <p>Found ${count} results</p>
  </div>
`);
```
