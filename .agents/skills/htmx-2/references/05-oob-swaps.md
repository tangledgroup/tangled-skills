# htmx Out-of-Band Swaps

This reference covers out-of-band (OOB) swaps for updating multiple elements from a single response.

## OOB Swap Fundamentals

Out-of-band swaps allow you to update elements anywhere in the DOM, not just the target element. Elements in the server response marked with `hx-swap-oob` are swapped into the page independently.

### Basic Syntax

```html
<!-- Server response includes OOB elements -->
<div id="message-area" hx-swap-oob="true">Success!</div>
<div id="counter" hx-swap-oob="innerHTML">5</div>
<div>Main response content for primary target</div>
```

### How It Works

1. Client makes request with `hx-target="#main"`
2. Server returns HTML with multiple elements
3. Elements with `hx-swap-oob` are swapped to matching IDs
4. Remaining content goes to `hx-target`

```html
<!-- Client side -->
<div id="message-area"></div>
<div id="counter">0</div>
<div id="main">
    <button hx-post="/submit" 
            hx-target="#main"
            hx-select-oob="#message-area, #counter">
        Submit
    </button>
</div>

<!-- Server response -->
<div id="message-area" hx-swap-oob="true">Submission successful!</div>
<div id="counter" hx-swap-oob="innerHTML">1</div>
<div>Form processed. <a href="/new">Submit another?</a></div>
```

## OOB Swap Attributes

### hx-swap-oob="true"

Default OOB swap (uses innerHTML):

```html
<!-- Response element -->
<div id="notification" hx-swap-oob="true">
    <div class="alert">Action completed!</div>
</div>

<!-- Client element is replaced entirely -->
<div id="notification"></div>
<!-- becomes -->
<div id="notification">
    <div class="alert">Action completed!</div>
</div>
```

### hx-swap-oob="outerHTML"

Replace entire target element:

```html
<!-- Response -->
<div id="user-row" hx-swap-oob="outerHTML">
    <tr id="user-row" class="updated">
        <td>John Doe</td>
        <td>john@example.com</td>
        <td>Active</td>
    </tr>
</div>

<!-- Entire row element is replaced -->
```

### hx-swap-oob="innerHTML"

Replace only inner content:

```html
<!-- Response -->
<div id="status-badge" hx-swap-oob="innerHTML">
    Active
</div>

<!-- Client element keeps attributes -->
<span id="status-badge" class="badge">Inactive</span>
<!-- becomes -->
<span id="status-badge" class="badge">Active</span>
```

### Other Swap Styles

All standard swap styles work with OOB:

```html
<!-- Append to element -->
<li id="new-item" hx-swap-oob="beforeend">New Item</li>

<!-- Prepend to element -->
<li id="first-item" hx-swap-oob="afterbegin">First Item</li>

<!-- Insert before element -->
<div id="sidebar" hx-swap-oob="beforebegin">Sidebar</div>

<!-- Insert after element -->
<footer id="footer" hx-swap-oob="afterend">Footer</footer>

<!-- Delete element -->
<div id="loading-spinner" hx-swap-oob="delete"></div>
```

## hx-select-oob

Select OOB elements by CSS selector instead of ID:

```html
<!-- Client side -->
<button hx-post="/update" 
        hx-select-oob=".flash-message, #counter">
    Update
</button>

<!-- Server response -->
<div class="flash-message success">Updated!</div>
<div id="counter" hx-swap-oob="true">5</div>
```

**Use cases:**
- Multiple elements with same class
- When ID is not available
- Dynamic element selection

## Common OOB Patterns

### Flash Messages

Show success/error messages anywhere on page:

```html
<!-- Layout includes message container -->
<div id="flash-messages"></div>

<!-- Any form can update it -->
<form hx-post="/submit" 
      hx-target="#form-result">
    <button type="submit">Submit</button>
</form>

<!-- Server response -->
<div id="flash-messages" hx-swap-oob="innerHTML">
    <div class="alert alert-success">Form submitted successfully!</div>
</div>
<div>Form processing complete.</div>
```

### Update Multiple Widgets

Update several independent components:

```html
<!-- Client has multiple widgets -->
<div id="user-count">Users: 100</div>
<div id="server-status">Online</div>
<div id="last-update">2 min ago</div>

<!-- Single request updates all -->
<button hx-get="/dashboard-stats" 
        hx-target="#main-chart">
    Refresh Dashboard
</button>

<!-- Server response -->
<div id="user-count" hx-swap-oob="innerHTML">Users: 105</div>
<div id="server-status" hx-swap-oob="innerHTML">Busy</div>
<div id="last-update" hx-swap-oob="innerHTML">Now</div>
<div>New chart data...</div>
```

### Form Validation Feedback

Show inline validation errors:

```html
<!-- Form with error containers -->
<form hx-post="/register" 
      hx-target="#registration-form">
    <div>
        <input name="username" id="username">
        <span id="username-error" class="error"></span>
    </div>
    <div>
        <input name="email" id="email">
        <span id="email-error" class="error"></span>
    </div>
    <button type="submit">Register</button>
</form>

<!-- Server response with errors -->
<span id="username-error" hx-swap-oob="innerHTML">
    <span class="error">Username already taken</span>
</span>
<span id="email-error" hx-swap-oob="innerHTML">
    <span class="error">Invalid email format</span>
</span>
<div>Please fix the errors above.</div>
```

### Update Navigation State

Update active menu items:

```html
<!-- Navigation -->
<nav id="main-nav">
    <a href="/dashboard" class="nav-link">Dashboard</a>
    <a href="/settings" class="nav-link">Settings</a>
</nav>

<!-- Content area -->
<div id="main-content">
    <button hx-get="/settings/profile" 
            hx-target="#main-content">
        Load Profile
    </button>
</div>

<!-- Server response updates nav -->
<a href="/dashboard" class="nav-link">Dashboard</a>
<a href="/settings" class="nav-link active" hx-swap-oob="true">Settings</a>
<div>Profile content...</div>
```

### Progress Indicators

Update progress during long operations:

```html
<!-- Progress bar -->
<div id="progress-bar" class="progress">
    <div class="progress-fill" style="width: 0%"></div>
</div>
<div id="progress-text">0%</div>

<!-- Start long operation -->
<button hx-post="/generate-report" 
        hx-trigger="click once"
        hx-target="#results">
    Generate Report
</button>

<!-- Server uses polling or SSE to update progress -->
<div id="progress-bar" hx-swap-oob="innerHTML">
    <div class="progress">
        <div class="progress-fill" style="width: 25%"></div>
    </div>
</div>
<div id="progress-text" hx-swap-oob="innerHTML">25%</div>
```

### Counter Updates

Update counters across page:

```html
<!-- Counters in header -->
<span id="cart-count">3</span> items in cart
<span id="notification-count">5</span> notifications

<!-- Add to cart -->
<button hx-post="/add-to-cart" 
        hx-vals='{"product_id": 123}'>
    Add to Cart
</button>

<!-- Response updates counters -->
<span id="cart-count" hx-swap-oob="innerHTML">4</span>
<span id="notification-count" hx-swap-oob="innerHTML">6</span>
<div class="toast">Item added to cart!</div>
```

## Nested OOB Swaps

OOB swaps can be nested within responses:

```html
<!-- Enable nested OOB swaps -->
<script>
    htmx.config.allowNestedOobSwaps = true;
</script>

<!-- Server response -->
<div id="main-content">
    <div id="sidebar" hx-swap-oob="true">
        Sidebar content
        <div id="nested-widget" hx-swap-oob="true">
            Nested widget
        </div>
    </div>
</div>
```

**Configuration:**
```javascript
// Enable nested OOB swaps (default: true)
htmx.config.allowNestedOobSwaps = true;
```

## OOB Swap Events

htmx fires specific events for OOB swaps:

### htmx:oobBeforeSwap

Triggered before OOB swap:

```javascript
document.body.addEventListener('htmx:oobBeforeSwap', (event) => {
    console.log('OOB swap starting:', {
        target: event.detail.target,
        fragment: event.detail.fragment
    });
    
    // Cancel this OOB swap
    // event.detail.shouldSwap = false;
});
```

### htmx:oobAfterSwap

Triggered after OOB swap:

```javascript
document.body.addEventListener('htmx:oobAfterSwap', (event) => {
    console.log('OOB swap complete:', event.detail.elt);
    
    // Initialize third-party libraries on new content
    if (event.detail.elt.querySelector('.tooltip')) {
        Tooltip.init(event.detail.elt);
    }
});
```

### htmx:oobErrorNoTarget

Triggered when OOB target not found:

```javascript
document.body.addEventListener('htmx:oobErrorNoTarget', (event) => {
    console.warn('OOB target not found:', event.detail.target);
    console.log('Content that would have been swapped:', event.detail.content);
});
```

## Advanced OOB Patterns

### Conditional OOB Swaps

Include OOB elements conditionally:

```html
<!-- Server-side template logic -->
{% if user.is_new %}
<div id="welcome-banner" hx-swap-oob="true">
    <div class="banner">Welcome! Complete your profile.</div>
</div>
{% endif %}

{% if has_errors %}
<div id="error-summary" hx-swap-oob="innerHTML">
    <ul>
        {% for error in errors %}
        <li>{{ error }}</li>
        {% endfor %}
    </ul>
</div>
{% endif %}
```

### OOB with Polling

Update elements via polling:

```html
<!-- Polling element -->
<div hx-get="/status" 
     hx-trigger="every 5s"
     hx-swap="none">
</div>

<!-- Server response updates multiple elements -->
<div id="status-indicator" hx-swap-oob="innerHTML">● Online</div>
<div id="user-count" hx-swap-oob="innerHTML">125 users</div>
<div id="last-update" hx-swap-oob="innerHTML">{{ now }}</div>
```

### OOB Cleanup

Remove elements with OOB delete:

```html
<!-- Loading indicator -->
<div id="loading-spinner" class="spinner"></div>

<!-- Server response removes it -->
<div id="loading-spinner" hx-swap-oob="delete"></div>
<div>Content loaded!</div>
```

### Replace Entire Section

Use outerHTML for complete replacement:

```html
<!-- Original table row -->
<tr id="user-123">
    <td>John Doe</td>
    <td>Inactive</td>
    <td>
        <button hx-post="/activate/123" 
                hx-target="#user-123"
                hx-swap="outerHTML">
            Activate
        </button>
    </td>
</tr>

<!-- Server response -->
<tr id="user-123" class="active" hx-swap-oob="outerHTML">
    <td>John Doe</td>
    <td>Active</td>
    <td>
        <button hx-post="/deactivate/123">Deactivate</button>
    </td>
</tr>
```

## OOB Best Practices

### Use IDs for OOB Targets

Always use stable IDs for OOB elements:

```html
<!-- Good: Stable ID -->
<div id="flash-messages" hx-swap-oob="true">Message</div>

<!-- Bad: Dynamic ID that might not match -->
<div id="message-{{ timestamp }}" hx-swap-oob="true">Message</div>
```

### Keep OOB Content Minimal

OOB elements should contain only what's needed:

```html
<!-- Good: Minimal OOB content -->
<div id="counter" hx-swap-oob="innerHTML">5</div>

<!-- Bad: Excessive markup -->
<div id="counter" hx-swap-oob="outerHTML">
    <div class="counter-wrapper">
        <span class="counter-label">Count:</span>
        <span class="counter-value">5</span>
        <div class="counter-decoration"></div>
    </div>
</div>
```

### Handle Missing Targets Gracefully

Log when OOB targets don't exist:

```javascript
document.body.addEventListener('htmx:oobErrorNoTarget', (event) => {
    console.warn(`OOB swap failed: target "${event.detail.target}" not found`);
    
    // Optionally store content for later
    // or notify user of issue
});
```

### Test OOB Swaps Independently

Verify OOB elements work in isolation:

```html
<!-- Test each OOB element separately -->
<button hx-get="/test-oob" 
        hx-swap="none">
    Test OOB
</button>

<!-- Response should work even if main target doesn't exist -->
<div id="widget-1" hx-swap-oob="true">Widget 1</div>
<div id="widget-2" hx-swap-oob="true">Widget 2</div>
```

## Troubleshooting

### OOB Element Not Swapping

**Check:**
1. ID matches exactly (case-sensitive)
2. Element exists in DOM at swap time
3. `hx-swap-oob` attribute is present
4. No JavaScript errors

```javascript
// Debug OOB swaps
document.body.addEventListener('htmx:oobBeforeSwap', (event) => {
    console.log('OOB swap attempt:', {
        selector: event.detail.target,
        found: document.querySelector(event.detail.target),
        fragment: event.detail.fragment
    });
});
```

### Multiple OOB Elements with Same ID

Only first match is swapped:

```html
<!-- Only FIRST #counter is updated -->
<div id="counter">0</div>
<div id="counter">1</div>  <!-- Duplicate ID (invalid HTML) -->

<!-- Use classes instead -->
<div class="counter">0</div>
<div class="counter">1</div>

<!-- Server updates all with selector -->
<div class="counter" hx-swap-oob="innerHTML" hx-select-oob=".counter">5</div>
```

### OOB Swap Order

OOB swaps happen in document order:

```html
<!-- Swapped in this order -->
<div id="first" hx-swap-oob="true">1</div>
<div id="second" hx-swap-oob="true">2</div>
<div id="third" hx-swap-oob="true">3</div>
```

## Next Steps

- [WebSockets and SSE](06-websockets-sse.md) - Real-time updates
- [Server Responses](09-server-responses.md) - Response headers and patterns
- [Common Patterns](10-common-patterns.md) - Complete UI patterns with OOB swaps
