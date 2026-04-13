# htmx Request Attributes Reference

This reference covers all HTTP method attributes and request-related attributes in htmx 2.x.

## HTTP Method Attributes

These attributes define the type of HTTP request to make when an element is triggered.

### hx-get

Issues a GET request to the specified URL.

```html
<!-- Basic GET request -->
<button hx-get="/api/data">Load Data</button>

<!-- With target -->
<a hx-get="/articles/123" hx-target="#article-content">
    Read Article
</a>

<!-- GET with query parameters from form -->
<form hx-get="/search">
    <input name="q" placeholder="Search...">
    <button type="submit">Search</button>
</form>
```

**Parameters sent:** Query string in URL (e.g., `/api/data?id=123&name=test`)

### hx-post

Issues a POST request to the specified URL.

```html
<!-- Basic POST -->
<button hx-post="/api/users">Add User</button>

<!-- POST with form data -->
<form hx-post="/api/comments" hx-target="#comments">
    <textarea name="body" required></textarea>
    <button type="submit">Comment</button>
</form>

<!-- POST with additional values -->
<button hx-post="/api/like" 
        hx-vals='{"post_id": 123, "user_id": 456}'>
    Like
</button>
```

**Parameters sent:** Request body (application/x-www-form-urlencoded or multipart/form-data)

### hx-put

Issues a PUT request to replace a resource.

```html
<!-- Update entire resource -->
<button hx-put="/api/users/123"
        hx-vals='{"name": "John", "email": "john@example.com"}'>
    Update User
</button>

<!-- PUT with form -->
<form hx-put="/api/posts/456">
    <input name="title" value="Updated Title">
    <input name="content" value="Updated content">
    <button type="submit">Update Post</button>
</form>
```

**Parameters sent:** Request body (typically JSON with hx-ext="json-enc")

### hx-patch

Issues a PATCH request for partial updates.

```html
<!-- Partial update -->
<button hx-patch="/api/users/123"
        hx-vals='{"status": "active"}'>
    Activate User
</button>

<!-- Toggle feature flag -->
<button hx-patch="/api/settings"
        hx-vals='{"dark_mode": true}'>
    Enable Dark Mode
</button>
```

**Parameters sent:** Request body with fields to update

### hx-delete

Issues a DELETE request to remove a resource.

```html
<!-- Delete with confirmation -->
<button hx-delete="/api/users/123" 
        hx-confirm="Are you sure you want to delete this user?">
    Delete User
</button>

<!-- Delete row in table -->
<td>
    <button type="button" 
            hx-delete="/api/items/{{ item.id }}"
            hx-swap="outerHTML"
            class="delete-btn">
        ✕
    </button>
</td>

<!-- Batch delete -->
<form hx-delete="/api/users/batch">
    <input type="hidden" name="ids[]" value="1,2,3">
    <button type="submit" hx-confirm="Delete selected users?">
        Delete Selected
    </button>
</form>
```

**Parameters sent:** Query string or request body (implementation-dependent)

## Request Control Attributes

### hx-trigger

Specifies when the request should be triggered.

```html
<!-- Default trigger (click for buttons, submit for forms, change for inputs) -->
<button hx-get="/data">Click me</button>

<!-- Custom event trigger -->
<div hx-get="/track" hx-trigger="mouseenter">Hover me</div>

<!-- Multiple triggers -->
<div hx-get="/update" 
     hx-trigger="click, keyup from:body[key=='Escape']">
    Update
</div>

<!-- Polling every 5 seconds -->
<div hx-get="/notifications" 
     hx-trigger="every 5s"
     hx-target="#notification-area">
    Notifications
</div>

<!-- Trigger on load -->
<div hx-get="/init" hx-trigger="load once">Initialize</div>

<!-- Trigger when element scrolls into view -->
<div hx-get="/lazy-content" 
     hx-trigger="revealed"
     hx-swap="outerHTML">
    <img src="placeholder.jpg" alt="Loading...">
</div>

<!-- Trigger with delay (debounce) -->
<input name="search" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:300ms"
       placeholder="Search...">

<!-- Trigger with throttle -->
<div hx-get="/position" 
     hx-trigger="scroll throttle:100ms">
    Content
</div>
```

**Trigger modifiers:**
- `once` - Trigger only once
- `changed` - Only trigger if value changed
- `delay:Xms` - Wait X milliseconds after event before triggering
- `throttle:Xms` - Throttle events to once per X milliseconds
- `from:selector` - Listen for event on different element
- `filter[expression]` - Only trigger if JavaScript expression is true

### hx-target

Specifies where to put the response.

```html
<!-- Target by ID -->
<button hx-get="/content" hx-target="#content-area">Load</button>

<!-- Target "this" element -->
<button hx-get="/toggle" hx-target="this">Toggle</button>

<!-- Target closest ancestor -->
<td>
    <button hx-get="/row-data" hx-target="closest tr">Update Row</button>
</td>

<!-- Target next element -->
<button hx-get="/help-text" hx-target="next p">Show Help</button>

<!-- Target previous element -->
<div hx-get="/label" hx-target="previous label">Update Label</div>

<!-- Find descendant -->
<div hx-get="/list-item" hx-target="find ul">Add Item</div>

<!-- No target (defaults to triggering element) -->
<button hx-get="/result">Result appears here</button>
```

**Extended selectors:**
- `this` - The element with the attribute
- `closest selector` - Closest ancestor matching selector
- `next selector` - Next sibling matching selector
- `previous selector` - Previous sibling matching selector
- `find selector` - First descendant matching selector

### hx-swap

Controls how the response is inserted into the DOM.

```html
<!-- Default: replace innerHTML -->
<div hx-get="/content" id="target">Loading...</div>

<!-- Replace entire element -->
<div hx-get="/card" hx-swap="outerHTML">Card</div>

<!-- Insert at different positions -->
<ul id="list">
    <li>Existing</li>
</ul>
<button hx-get="/li" hx-target="#list" hx-swap="beforeend">Append</button>
<button hx-get="/li" hx-target="#list" hx-swap="afterbegin">Prepend</button>

<!-- Insert around target -->
<div id="main">Content</div>
<button hx-get="/sidebar" hx-target="#main" hx-swap="beforebegin">Add Before</button>
<button hx-get="/footer" hx-target="#main" hx-swap="afterend">Add After</button>

<!-- Delete target regardless of response -->
<div id="temp" hx-get="/process" hx-swap="delete">Temporary</div>

<!-- Don't swap (use OOB swaps only) -->
<button hx-post="/update-status" hx-swap="none">Update</button>

<!-- With swap options -->
<div hx-get="/content" 
     hx-swap="innerHTML swap:100ms settle:200ms">
    Loading...
</div>

<!-- With scrolling -->
<div hx-get="/long-content" 
     hx-swap="innerHTML scroll:top">
    Load Content
</div>

<!-- Show target in view -->
<div hx-get="/modal-content" 
     hx-swap="innerHTML show:bottom">
    Open Modal
</div>

<!-- Morph swap (requires extension) -->
<div hx-ext="morphdom-swap"
     hx-get="/content"
     hx-swap="morphdom">
    Content
</div>
```

**Swap styles:**
- `innerHTML` - Replace element's innerHTML (default)
- `outerHTML` - Replace entire element
- `beforebegin` - Insert before target
- `afterbegin` - Insert at start of target
- `beforeend` - Insert at end of target
- `afterend` - Insert after target
- `delete` - Delete target element
- `none` - Don't swap content

**Swap modifiers:**
- `swap:Xms` - Delay before swapping
- `settle:Xms` - Delay after swapping
- `scroll:top|bottom` - Scroll target to top/bottom
- `show:top|bottom` - Show target top/bottom in viewport
- `focusScroll:true|false` - Whether focused element scrolls into view
- `transition:true|false` - Use View Transitions API

### hx-select

Select specific content from the response using a CSS selector.

```html
<!-- Extract specific element from response -->
<button hx-get="/article" 
        hx-select="#article-content"
        hx-target="#main">
    Load Article
</button>

<!-- Response HTML -->
<!-- 
<div id="page">
    <nav>...</nav>
    <div id="article-content">Article text</div>
    <footer>...</footer>
</div>
-->
<!-- Only #article-content is swapped into #main -->

<!-- Select multiple elements -->
<button hx-get="/items" 
        hx-select=".item"
        hx-target="#list">
    Load Items
</button>
```

### hx-select-oob

Select elements for out-of-band swaps by selector.

```html
<!-- Trigger element -->
<button hx-post="/submit" 
        hx-select-oob="#message, #counter">
    Submit
</button>

<!-- Response includes OOB elements -->
<div id="message" hx-swap-oob="true">Success!</div>
<div id="counter" hx-swap-oob="true">Count: 5</div>
<div>Main response content</div>
```

See [Out-of-Band Swaps](05-oob-swaps.md) for detailed OOB swap documentation.

## Value Resolution Attributes

### hx-vals

Add static values to the request.

```html
<!-- Static JSON values -->
<button hx-post="/api/like"
        hx-vals='{"post_id": 123, "type": "like"}'>
    Like
</button>

<!-- Multiple values -->
<button hx-delete="/api/item"
        hx-vals='{"id": 456, "confirm": true}'>
    Delete
</button>

<!-- Combined with form values -->
<form id="user-form">
    <input name="name" value="John">
</form>
<button hx-post="/api/update"
        hx-vals='{"user_id": 123}'
        hx-include="#user-form">
    Update <!-- Sends: name=John, user_id=123 -->
</button>
```

### hx-vars

Add dynamic values from JavaScript expressions.

```html
<!-- Function call -->
<button hx-post="/api/track"
        hx-vars="{event: getEventName(), timestamp: Date.now()}">
    Track Event
</button>

<!-- Access global variables -->
<button hx-post="/api/user"
        hx-vars="{user_id: currentUser.id}">
    Update User
</button>

<!-- Element property -->
<input id="search-input" name="q">
<button hx-get="/search"
        hx-vars="{exact: document.getElementById('search-input').value.length > 3}">
    Search
</button>

<!-- Combined with hx-vals -->
<button hx-post="/api/action"
        hx-vals='{"action": "save"}'
        hx-vars="{timestamp: Date.now(), user_id: currentUser.id}">
    Save
</button>
```

**Note:** Requires `htmx.config.allowEval = true` (default).

### hx-include

Include values from additional elements.

```html
<!-- Include specific element -->
<input name="query" id="search-input">
<button hx-get="/search" hx-include="#search-input">
    Search
</button>

<!-- Include form -->
<form id="filters">
    <input name="category" value="electronics">
    <input name="min_price" value="10">
</form>
<button hx-get="/products" hx-include="#filters">
    Show Products
</button>

<!-- Include multiple elements -->
<button hx-post="/submit" 
        hx-include="#form1, #form2, input[name='global_id']">
    Submit
</button>
```

### hx-exclude

Exclude values from the request.

```html
<!-- Exclude specific inputs -->
<form hx-post="/submit">
    <input name="data" value="important">
    <input name="debug_token" value="exclude_me">
    <button type="submit" hx-exclude="input[name='debug_token']">
        Submit
    </button>
</form>

<!-- Exclude by class -->
<button hx-post="/api" 
        hx-exclude=".internal-field">
    Submit
</button>
```

### hx-params

Filter which parameters to include.

```html
<!-- Only include specific params -->
<form hx-post="/submit">
    <input name="important" value="yes">
    <input name="unimportant" value="no">
    <button type="submit" hx-params="important">
        Submit <!-- Only sends: important=yes -->
    </button>
</form>

<!-- Exclude specific params -->
<button hx-post="/api" 
        hx-params="not:exclude_this,exclude_that">
    Submit
</button>

<!-- Wildcard inclusion -->
<button hx-post="/api" 
        hx-params="data_*">
    Submit <!-- Sends all params starting with "data_" -->
</button>
```

## Request Configuration Attributes

### hx-header / hx-headers

Add custom HTTP headers.

```html
<!-- Single header -->
<button hx-get="/api/data" 
        hx-header="X-Custom-Header: custom-value">
    Fetch Data
</button>

<!-- Multiple headers -->
<button hx-post="/api/secure"
        hx-headers="X-API-Key: abc123&#10;X-Request-ID: req-456">
    Secure Request
</button>

<!-- Dynamic header from JavaScript -->
<button hx-post="/api"
        hx-headers="X-CSRF-Token: getCSRFToken()">
    Submit
</button>
```

### hx-request

Configure request behavior.

```html
<!-- Set request timeout -->
<button hx-get="/slow-endpoint" 
        hx-request='{"timeout": 10000}'>
    Fetch (10s timeout)
</button>

<!-- Disable validation -->
<form hx-post="/submit" 
      hx-request='{"validate": false}'>
    <input name="required" required>
    <button type="submit">Submit Without Validation</button>
</form>

<!-- Set custom verb (advanced) -->
<button hx-get="/resource"
        hx-request='{"verb": "HEAD"}'>
    HEAD Request
</button>
```

**Options:**
- `timeout` - Request timeout in milliseconds
- `validate` - Whether to validate form inputs (boolean)
- `verb` - Override HTTP verb (advanced usage)

### hx-prompt

Prompt user for input before request.

```html
<!-- Simple prompt -->
<button hx-post="/rename" 
        hx-prompt="Enter new name:"
        hx-target="#name-display">
    Rename
</button>

<!-- Prompt value sent as parameter -->
<button hx-delete="/api/item" 
        hx-prompt="Type 'DELETE' to confirm:">
    Delete Item
</button>
<!-- Response can use the prompt value via server-side templating -->
```

The prompt text is sent to the server with parameter name `_prompt`.

### hx-confirm

Confirm action before request.

```html
<!-- Simple confirmation -->
<button hx-delete="/api/user/123" 
        hx-confirm="Are you sure you want to delete this user?">
    Delete User
</button>

<!-- Custom message -->
<button hx-post="/api/critical"
        hx-confirm="This action cannot be undone. Continue?">
    Critical Action
</button>

<!-- Dynamic confirmation -->
<button hx-delete="/api/item"
        hx-confirm="Delete item: ${item_name}?">
    Delete
</button>
```

**Note:** Uses browser's native `window.confirm()`. For custom dialogs, use the `htmx:confirm` event.

### hx-validate

Control form validation behavior.

```html
<!-- Force validation (default for forms) -->
<form hx-post="/submit" hx-validate="true">
    <input name="email" type="email" required>
    <button type="submit">Submit</button>
</form>

<!-- Disable validation -->
<button hx-post="/submit" 
        hx-validate="false"
        hx-include="#my-form">
    Submit Without Validation
</button>
```

## Synchronization Attributes

### hx-sync

Coordinate multiple requests.

```html
<!-- Cancel previous request to same target -->
<input name="q" 
       hx-get="/search" 
       hx-sync="#results @cancel"
       hx-target="#results"
       placeholder="Search...">

<!-- Stop processing if another request in progress -->
<button hx-post="/save" 
        hx-sync="closest form #stop">
    Save
</button>

<!-- Wait for other requests to complete -->
<button hx-get="/data" 
        hx-sync="#other-request #wait">
    Load Data
</button>

<!-- Abort previous and continue -->
<div hx-get="/update" 
     hx-sync="this @abort">
    Update
</div>
```

**Sync modes:**
- `@cancel` - Cancel pending request
- `@abort` - Abort pending request
- `#stop` - Stop processing new requests
- `#wait` - Wait for other request to complete

## History Attributes

### hx-push-url

Push URL to browser history after request.

```html
<!-- Push true (uses trigger element's path) -->
<button hx-get="/articles/123" 
        hx-push-url="true">
    Read Article
</button>

<!-- Push custom URL -->
<button hx-get="/load-dashboard" 
        hx-push-url="/dashboard">
    Dashboard
</button>

<!-- Push with query params -->
<button hx-get="/filtered-list" 
        hx-push-url="/list?category=electronics">
    Filter List
</button>
```

### hx-replace-url

Replace current URL in browser history.

```html
<!-- Replace URL without adding history entry -->
<button hx-get="/update-view" 
        hx-replace-url="/updated-view">
    Update View
</button>
```

## Indicator Attributes

### hx-indicator

Specify element to show as loading indicator.

```html
<!-- Indicator on triggering element -->
<button hx-get="/data">
    Load Data
    <img src="spinner.gif" class="htmx-indicator">
</button>

<!-- Indicator on separate element -->
<button hx-get="/data" 
        hx-indicator="#loading-spinner">
    Load Data
</button>
<div id="loading-spinner" class="htmx-indicator">
    <img src="spinner.gif" alt="Loading...">
</div>

<!-- Multiple indicators -->
<button hx-get="/data" 
        hx-indicator=".global-spinner, #local-spinner">
    Load Data
</button>
```

**Default CSS:**
```css
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator { display: inline; }
```

### hx-disabled-elt

Disable elements during request.

```html
<!-- Disable triggering element -->
<button hx-post="/submit" 
        hx-disabled-elt="this">
    Submit
</button>

<!-- Disable specific elements -->
<button hx-post="/submit" 
        hx-disabled-elt="#submit-btn, #cancel-btn">
    Submit
</button>

<!-- Disable all buttons in form -->
<form hx-post="/submit" 
      hx-disabled-elt="button[type='submit']">
    <button type="submit">Submit</button>
    <button type="submit">Save & New</button>
</form>
```

## Next Steps

- [Triggers and Events](03-triggers-and-events.md) - Complete trigger system documentation
- [Swapping](04-swapping.md) - Detailed swap modes and options
- [Out-of-Band Swaps](05-oob-swaps.md) - OOB swap patterns
- [Common Patterns](10-common-patterns.md) - Real-world examples
