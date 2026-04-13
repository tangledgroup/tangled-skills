# htmx Common Patterns and Examples

This reference covers common UI patterns and real-world usage examples for htmx 2.x.

## Form Patterns

### Inline Validation

Validate form fields as user types:

```html
<form id="registration-form">
    <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username">
        <span id="username-feedback" class="feedback"></span>
    </div>
    
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email">
        <span id="email-feedback" class="feedback"></span>
    </div>
    
    <button type="submit" hx-post="/register" 
            hx-target="#registration-form"
            hx-swap="outerHTML">
        Register
    </button>
</form>

<!-- Validate individual fields -->
<input name="username" 
       id="username"
       hx-post="/validate/username"
       hx-trigger="blur changed, input changed delay:500ms"
       hx-target="#username-feedback"
       hx-swap="innerHTML">
       Enter username
</input>
<span id="username-feedback"></span>
```

### Multi-Step Forms

Create wizard-style forms:

```html
<form id="multi-step-form" hx-post="/submit">
    <!-- Step 1 -->
    <div id="step-1" class="step active">
        <h2>Personal Information</h2>
        <input name="first_name" placeholder="First Name">
        <input name="last_name" placeholder="Last Name">
        <button type="button" hx-get="/step-2" 
                hx-target="#form-content" 
                hx-swap="innerHTML">
            Next
        </button>
    </div>
    
    <!-- Step 2 -->
    <div id="step-2" class="step" style="display:none">
        <h2>Contact Information</h2>
        <input name="email" type="email">
        <input name="phone" type="tel">
        <button type="button" hx-get="/step-1" 
                hx-target="#form-content" 
                hx-swap="innerHTML">
            Back
        </button>
        <button type="submit" hx-post="/submit">Submit</button>
    </div>
</form>
```

### File Upload with Progress

```html
<form hx-post="/upload" 
      hx-encoding="multipart/form-data"
      hx-target="#upload-result">
    <input type="file" name="file" id="file-input" required>
    
    <!-- Progress bar -->
    <div class="progress">
        <div id="upload-progress" class="progress-bar" style="width: 0%"></div>
    </div>
    
    <button type="submit">Upload</button>
</form>

<div id="upload-result"></div>
```

Server returns progress updates via polling or SSE.

### Dynamic Form Fields

Add/remove fields dynamically:

```html
<form hx-post="/submit">
    <div id="items-container">
        <div class="item-field">
            <input name="items[]" placeholder="Item 1">
            <button type="button" class="remove-item" 
                    hx-delete="/remove-field"
                    hx-vals='{"index": 0}'
                    hx-swap="outerHTML">
                Remove
            </button>
        </div>
    </div>
    
    <button type="button" 
            hx-get="/add-field"
            hx-target="#items-container"
            hx-swap="beforeend">
        Add Item
    </button>
    
    <button type="submit">Submit</button>
</form>
```

## Navigation Patterns

### Tab Interfaces

Switch between tab contents:

```html
<!-- Tab navigation -->
<nav class="tabs">
    <button class="tab active" 
            hx-get="/tab/content/1"
            hx-target="#tab-content"
            hx-swap="innerHTML"
            hx-push-url="/tab/1"
            onclick="htmx.takeClass(this, 'active')">
        Tab 1
    </button>
    <button class="tab" 
            hx-get="/tab/content/2"
            hx-target="#tab-content"
            hx-swap="innerHTML"
            hx-push-url="/tab/2"
            onclick="htmx.takeClass(this, 'active')">
        Tab 2
    </button>
    <button class="tab" 
            hx-get="/tab/content/3"
            hx-target="#tab-content"
            hx-swap="innerHTML"
            hx-push-url="/tab/3"
            onclick="htmx.takeClass(this, 'active')">
        Tab 3
    </button>
</nav>

<!-- Tab content -->
<div id="tab-content">
    <!-- Content loaded here -->
</div>
```

### Accordion / Collapsible Sections

```html
<details class="accordion">
    <summary>Section 1</summary>
    <div class="content">
        <p>Content for section 1...</p>
    </div>
</details>

<details class="accordion">
    <summary>Section 2 (Lazy Load)</summary>
    <div class="content" 
         hx-get="/section-2-content"
         hx-trigger="click from:summary"
         hx-swap="innerHTML">
        <p>Loading...</p>
    </div>
</details>
```

### Breadcrumb Navigation

Dynamic breadcrumbs based on current path:

```html
<nav aria-label="breadcrumb">
    <ol id="breadcrumbs">
        <li><a href="/">Home</a></li>
        <li hx-get="/current-breadcrumb" 
            hx-trigger="load, htmx:afterSwap from:body"
            hx-swap="innerHTML">
            <!-- Dynamic breadcrumbs loaded here -->
        </li>
    </ol>
</nav>
```

## Data Display Patterns

### Infinite Scroll

Load more content as user scrolls:

```html
<div id="posts-container">
    <div class="posts">
        <!-- Initial posts -->
    </div>
    
    <!-- Loader that triggers when revealed -->
    <div hx-get="/posts?page=2"
         hx-trigger="revealed"
         hx-swap="beforeend reveal:100px"
         hx-target="#posts-container"
         class="loader">
        <p>Loading more posts...</p>
    </div>
</div>
```

Server returns new posts plus updated loader with next page.

### Pagination

Traditional pagination with htmx:

```html
<div id="content">
    <!-- Paginated content -->
</div>

<nav class="pagination" aria-label="Pages">
    <a href="/page/1" 
       hx-get="/page/1"
       hx-target="#content"
       hx-push-url="true"
       class="page-link">
        1
    </a>
    <a href="/page/2" 
       hx-get="/page/2"
       hx-target="#content"
       hx-push-url="true"
       class="page-link active">
        2
    </a>
    <a href="/page/3" 
       hx-get="/page/3"
       hx-target="#content"
       hx-push-url="true"
       class="page-link">
        3
    </a>
</nav>
```

### Live Search / Autocomplete

Real-time search as user types:

```html
<input type="text" 
       id="search-input"
       name="q"
       hx-get="/search"
       hx-trigger="input changed delay:300ms"
       hx-target="#search-results"
       placeholder="Search...">

<div id="search-results" class="dropdown">
    <!-- Results appear here -->
</div>

<!-- Close results on outside click -->
<div hx-get="" 
     hx-trigger="click from:body not:#search-input, click from:#search-results"
     hx-target="#search-results"
     hx-swap="innerHTML">
</div>
```

### Sortable Tables

Click headers to sort:

```html
<table>
    <thead>
        <tr>
            <th>
                <a href="#" 
                   hx-get="/table?sort=name&order=asc"
                   hx-target="#table-body"
                   hx-push-url="true">
                    Name
                </a>
            </th>
            <th>
                <a href="#" 
                   hx-get="/table?sort=date&order=desc"
                   hx-target="#table-body"
                   hx-push-url="true">
                    Date
                </a>
            </th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="table-body">
        <!-- Table rows -->
    </tbody>
</table>
```

### Filterable Lists

Filter items with dropdowns:

```html
<select name="category" 
        hx-get="/products"
        hx-target="#product-list"
        hx-push-url="true"
        onchange="this.form.requestSubmit()">
    <option value="">All Categories</option>
    <option value="electronics">Electronics</option>
    <option value="clothing">Clothing</option>
</select>

<div id="product-list">
    <!-- Products -->
</div>
```

## Interactive Elements

### Modal Dialogs

Open modal with htmx:

```html
<!-- Trigger button -->
<button hx-get="/modal/content" 
        hx-target="#modal"
        hx-swap="innerHTML"
        onclick="document.getElementById('modal').showModal()">
    Open Modal
</button>

<!-- Modal element (HTML5 dialog) -->
<dialog id="modal">
    <div id="modal-content">
        <!-- Content loaded here -->
    </div>
    
    <form method="dialog">
        <button type="submit">Close</button>
    </form>
</dialog>
```

### Toast Notifications

Show temporary notifications:

```html
<!-- Container for toasts -->
<div id="toast-container" class="toasts"></div>

<!-- Action that triggers toast -->
<button hx-post="/action" 
        hx-swap="none">
    Perform Action
</button>
```

Server response includes OOB swap:

```html
<!-- Server returns -->
<div id="toast-container" hx-swap-oob="beforeend">
    <div class="toast success fade-out">
        Action completed successfully!
    </div>
</div>
```

### Context Menus

Right-click context menu:

```html
<div id="context-target" 
     oncontextmenu="showContextMenu(event)">
    Right-click me
</div>

<div id="context-menu" class="context-menu" style="display:none">
    <a href="#" hx-get="/action1" hx-swap="none">Action 1</a>
    <a href="#" hx-get="/action2" hx-swap="none">Action 2</a>
    <a href="#" hx-delete="/delete" hx-confirm="Delete?">Delete</a>
</div>

<script>
function showContextMenu(e) {
    e.preventDefault();
    const menu = document.getElementById('context-menu');
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.style.display = 'block';
    
    // Hide on click elsewhere
    setTimeout(() => {
        document.addEventListener('click', hideMenu, {once: true});
    }, 0);
}

function hideMenu() {
    document.getElementById('context-menu').style.display = 'none';
}
</script>
```

### Drag and Drop

Simple drag operations:

```html
<div id="droppable-area" 
     hx-post="/drop"
     hx-trigger="drop"
     hx-vals="js:{data: draggedData}">
    Drop items here
</div>

<div draggable="true" 
     ondragstart="draggedData = {id: 123, name: 'Item'}">
    Drag me
</div>
```

## Real-time Features

### Live Chat

WebSocket-based chat:

```html
<div hx-ws="connect:/chat">
    
    <!-- Message list -->
    <div id="messages">
        <div hx-trigger="ws-message"
             hx-swap="beforeend">
            <!-- Messages appear here -->
        </div>
    </div>
    
    <!-- Input form -->
    <form hx-ws="send" 
          hx-disabled-elt="this">
        <input name="message" placeholder="Type a message..." required>
        <button type="submit">Send</button>
    </form>
    
    <!-- User status -->
    <div id="users" 
         hx-trigger='ws-[{"type": "users"}]'
         hx-swap="innerHTML">
        Connected users...
    </div>
</div>
```

### Live Updates with SSE

Server pushes updates:

```html
<div hx-sse-connect="/live-updates">
    
    <!-- Stats update -->
    <div hx-trigger="sse:stats"
         hx-get="/current-stats"
         hx-target="#stats-panel">
        Loading stats...
    </div>
    
    <div id="stats-panel">
        <!-- Stats displayed here -->
    </div>
    
    <!-- Notifications -->
    <div hx-trigger="sse:notification"
         hx-swap="beforeend">
        <!-- Notifications appear here -->
    </div>
</div>
```

### Progress Indicators

Show progress for long operations:

```html
<button hx-post="/generate-report" 
        hx-target="#report-result"
        hx-indicator="#progress-bar">
    Generate Report
</button>

<div id="progress-bar" class="htmx-indicator">
    <div class="progress">
        <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
    </div>
    <span id="progress-text">0%</span>
</div>

<!-- Poll for progress -->
<div id="progress-poller" 
     hx-get="/report-progress"
     hx-trigger="every 1s"
     hx-swap="none"
     style="display:none">
</div>
```

## CRUD Operations

### Create with Inline Form

```html
<button hx-get="/new-item-form" 
        hx-target="#inline-form"
        hx-swap="innerHTML">
    Add New Item
</button>

<div id="inline-form">
    <!-- Form loaded here -->
</div>
```

### Edit in Place

Click to edit content:

```html
<div class="editable" id="post-123">
    <span class="content">Post content...</span>
    
    <button class="edit-btn" 
            hx-get="/edit/123"
            hx-target="#post-123"
            hx-swap="outerHTML">
        Edit
    </button>
</div>
```

Server returns edit form:

```html
<!-- Server response -->
<form id="post-123" 
      hx-post="/update/123"
      hx-target="#post-123"
      hx-swap="outerHTML">
    <input name="content" value="Post content...">
    <button type="submit">Save</button>
    <button type="button" hx-get="/view/123" 
            hx-target="#post-123" 
            hx-swap="outerHTML">
        Cancel
    </button>
</form>
```

### Delete with Confirmation

```html
<button hx-delete="/items/123" 
        hx-confirm="Are you sure you want to delete this item?"
        hx-swap="outerHTML"
        class="delete-btn">
    Delete
</button>
```

Or with custom confirmation dialog:

```html
<button hx-delete="/items/123" 
        hx-target="#item-123"
        hx-swap="outerHTML"
        id="delete-btn-123">
    Delete
</button>

<script>
document.body.addEventListener('htmx:confirm', (event) => {
    if (event.detail.target.id === 'delete-btn-123') {
        event.preventDefault();
        
        // Custom confirmation
        if (confirm('This will permanently delete the item. Continue?')) {
            event.detail.issueRequest(true);
        }
    }
});
</script>
```

### Bulk Operations

Select and operate on multiple items:

```html
<table>
    <thead>
        <tr>
            <th><input type="checkbox" id="select-all"></th>
            <th>Name</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="items-body">
        <tr>
            <td><input type="checkbox" name="selected[]" value="1" class="item-checkbox"></td>
            <td>Item 1</td>
            <td><button class="delete-btn">Delete</button></td>
        </tr>
    </tbody>
</table>

<button hx-post="/bulk-delete" 
        hx-vals="js:{ids: getSelectedIds()}"
        hx-confirm="Delete selected items?"
        id="bulk-delete">
    Delete Selected
</button>

<script>
function getSelectedIds() {
    return Array.from(document.querySelectorAll('.item-checkbox:checked'))
        .map(cb => cb.value);
}
</script>
```

## State Management

### URL State with hx-push-url

Keep URL in sync with application state:

```html
<!-- Filter that updates URL -->
<select name="status" 
        hx-get="/tasks"
        hx-target="#task-list"
        hx-push-url="true">
    <option value="all">All Tasks</option>
    <option value="pending">Pending</option>
    <option value="done">Done</option>
</select>

<div id="task-list">
    <!-- Tasks -->
</div>
```

Browser back/forward works automatically.

### Temporary State with hx-replace-url

Update URL without adding history:

```html
<!-- Search that doesn't add to history -->
<input name="q" 
       hx-get="/search"
       hx-target="#results"
       hx-replace-url="true"
       placeholder="Search...">
```

## Next Steps

- [Migration Guide](11-migration-v1-to-v2.md) - Upgrading from htmx 1.x
- [Security Best Practices](12-security-best-practices.md) - Security guidance
- [Performance Optimization](13-performance-optimization.md) - Performance tips
