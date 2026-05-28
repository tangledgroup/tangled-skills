# UX Patterns

Common user interface patterns implemented with htmx. Each pattern includes complete HTML examples.

## Active Search

Search as the user types, with debounced requests:

```html
<input name="q"
       hx-get="/search"
       hx-trigger="input changed delay:300ms, click"
       hx-target="#results"
       hx-indicator="#spinner" />
<div id="results"></div>
<span id="spinner" class="htmx-indicator">Searching...</span>
```

## Click to Edit

Inline editing of a value:

```html
<span id="name-display">John</span>
<button hx-get="/edit/name"
        hx-target="#name-display"
        hx-swap="outerHTML">Edit</button>
```

Server returns a form:
```html
<form id="name-display" hx-post="/save/name"
      hx-target="#name-display" hx-swap="outerHTML">
  <input name="name" value="John" />
  <button type="submit">Save</button>
</form>
```

## Bulk Update

Check multiple rows, submit all at once:

```html
<form hx-post="/bulk-update" hx-target="#table-body">
  <tbody id="table-body">
    <tr>
      <td><input type="checkbox" name="ids" value="1" /></td>
      <td>Item 1</td>
    </tr>
    <tr>
      <td><input type="checkbox" name="ids" value="2" /></td>
      <td>Item 2</td>
    </tr>
  </tbody>
  <button type="submit">Archive Selected</button>
</form>
```

## Click to Load

Load more rows on demand:

```html
<div id="items">
  <!-- Initial items -->
</div>
<button hx-get="/items?page=2"
        hx-target="#items"
        hx-swap="beforeend"
        hx-on::after-request="this.querySelector('a').textContent='Page 3'">
  Load More
</button>
```

## Delete Row

Remove a table row with AJAX:

```html
<tr id="row-1">
  <td>Item Name</td>
  <td>
    <button hx-delete="/items/1"
            hx-confirm="Delete this item?"
            hx-swap="outerHTML"
            hx-target="closest tr">
      Delete
    </button>
  </td>
</tr>
```

## Edit Row

Inline row editing:

```html
<tr id="row-1">
  <td>Item Name</td>
  <td>
    <button hx-get="/items/1/edit"
            hx-target="closest tr"
            hx-swap="outerHTML">
      Edit
    </button>
  </td>
</tr>
```

Server returns the row with a form inside.

## Lazy Loading

Load content when it enters the viewport:

```html
<div hx-get="/heavy-content"
     hx-trigger="revealed"
     hx-swap="innerHTML"
     hx-on::before-request="this.innerHTML='Loading...'">
  <!-- Loaded when scrolled into view -->
</div>
```

## Inline Validation

Validate fields as the user types:

```html
<form id="registration">
  <input name="username"
         hx-post="/validate/username"
         hx-trigger="change delay:300ms, blur"
         hx-target="#username-error"
         hx-indicator="#username-spinner" />
  <span id="username-error"></span>
  <span id="username-spinner" class="htmx-indicator">Checking...</span>

  <input name="email"
         hx-post="/validate/email"
         hx-trigger="change delay:300ms, blur"
         hx-target="#email-error" />
  <span id="email-error"></span>
</form>
```

## Infinite Scroll

Continuously load more content as user scrolls:

```html
<div id="feed">
  <!-- Initial items -->
</div>
<div hx-get="/feed?page=2"
     hx-trigger="revealed"
     hx-swap="beforeend"
     hx-target="#feed">
  Loading more...
</div>
```

Server response includes the new items AND a new "loader" div at the end for the next page.

## Progress Bar

Show upload progress:

```html
<form hx-post="/upload"
      hx-encoding="multipart/form-data"
      hx-on::progress="evt.detail.loaded/evt.detail.total * 100 + '%'">
  <input type="file" name="file" required />
  <progress id="progress" value="0" max="100"></progress>
  <button type="submit">Upload</button>
</form>
```

## Value Select (Dependent Dropdowns)

Second dropdown depends on first:

```html
<select name="country"
        hx-get="/states"
        hx-trigger="change"
        hx-target="#states">
  <option value="us">United States</option>
  <option value="ca">Canada</option>
</select>

<select name="state" id="states">
  <option>Select a country first</option>
</select>
```

## File Upload with Progress

```html
<form hx-post="/upload"
      hx-encoding="multipart/form-data"
      hx-target="#result"
      hx-swap="innerHTML"
      hx-on::progress="document.getElementById('bar').value = Math.round(evt.detail.loaded/evt.detail.total*100)">
  <input type="file" name="file" required />
  <progress id="bar" value="0" max="100"></progress>
  <button type="submit" hx-disable>Upload</button>
</form>
<div id="result"></div>
```

## Preserving File Inputs After Errors

```html
<form hx-post="/upload"
      hx-encoding="multipart/form-data"
      hx-target="#result"
      hx-preserve="input[type=file]">
  <input type="file" name="file" />
  <button type="submit">Upload</button>
</form>
<div id="result"></div>
```

`hx-preserve` keeps the file input value even after the response swaps in.

## Reset User Input

Clear form after successful submission:

```html
<form hx-post="/submit"
      hx-target="#result"
      hx-on::after-request="if(evt.detail.successful) this.reset()">
  <input name="message" />
  <button type="submit">Send</button>
</form>
```

## Browser Dialogs (confirm/prompt)

```html
<!-- Confirm dialog -->
<button hx-delete="/item/1"
        hx-confirm="Are you sure you want to delete?">
  Delete
</button>

<!-- Prompt dialog -->
<button hx-post="/rename"
        hx-prompt="Enter new name:"
        hx-target="#result">
  Rename
</button>
```

## Modal Dialogs (Custom)

```html
<!-- Trigger -->
<button hx-get="/item/1/details"
        hx-target="#modal-body"
        hx-on::after-request="document.getElementById('modal').classList.remove('hidden')">
  View Details
</button>

<!-- Modal -->
<div id="modal" class="hidden fixed inset-0 bg-black/50">
  <div class="bg-white p-4 rounded">
    <div id="modal-body"></div>
    <button hx-on:click="document.getElementById('modal').classList.add('hidden')">
      Close
    </button>
  </div>
</div>
```

## Tabs (HATEOAS)

```html
<div id="tab-content">
  <!-- Content loaded by tab click -->
</div>

<nav>
  <a href="/tab1"
     hx-get="/tab1"
     hx-target="#tab-content"
     hx-push-url="true"
     class="tab active">Tab 1</a>
  <a href="/tab2"
     hx-get="/tab2"
     hx-target="#tab-content"
     hx-push-url="true"
     class="tab">Tab 2</a>
</nav>
```

## Tabs (JavaScript)

```html
<div id="tab-content"></div>

<button hx-on:click="htmx.trigger('#tab1-link', 'click')">Tab 1</button>
<a id="tab1-link"
   href="#"
   hx-get="/tab1"
   hx-target="#tab-content"
   class="hidden">Tab 1</a>
```

## Keyboard Shortcuts

```html
<div hx-on:keydown-document="if(evt.key==='n' && evt.ctrlKey) { evt.preventDefault(); htmx.trigger('#new-btn', 'click'); }">
  <button id="new-btn"
          hx-get="/new-item"
          hx-target="#container">
    New Item (Ctrl+N)
  </button>
</div>
```

## Drag and Drop / Sortable

```html
<ul id="sortable" class="sortable-list">
  <li data-id="1">Item 1</li>
  <li data-id="2">Item 2</li>
</ul>

<script>
htmx.onLoad(function(elt) {
  var sortableElt = elt.querySelector('.sortable-list');
  if (sortableElt) {
    var sortable = new Sortable(sortableElt, {
      onEnd: function() {
        var order = sortable.toArray();
        htmx.ajax('POST', '/reorder', {
          values: { order: order.join(',') },
          target: sortableElt
        });
      }
    });
  }
});
</script>
```

## Updating Other Content (OOB)

```html
<form hx-post="/save" hx-target="#main-content">
  <input name="name" />
  <button type="submit">Save</button>
</form>

<div id="main-content"></div>
<div id="notification-area"></div>
```

Server response:
```html
<div id="main-content">Saved!</div>
<div id="notification-area" hx-swap-oob="true">Item saved successfully</div>
```

## Custom Confirm

```html
<button hx-delete="/item/1"
        hx-on::before-request="if(!await customConfirm('Delete?')) htmx.abort(this)">
  Delete
</button>

<script>
async function customConfirm(msg) {
  // SweetAlert2 or any custom dialog
  return confirm(msg);
}
</script>
```

## Async Authentication

```html
<button hx-post="/api/secure"
        hx-headers='{"Authorization": "Bearer " + getAuthToken()}'
        hx-target="#result">
  Secure Action
</button>

<script>
function getAuthToken() {
  return localStorage.getItem('auth_token');
}

// Refresh token on 401
document.body.addEventListener('htmx:responseError', function(evt) {
  if (evt.detail.xhr.status === 401) {
    refreshToken().then(function() {
      // Retry the request
      htmx.ajax(evt.detail.elt.getAttribute('hx-post'),
                evt.detail.elt, { target: '#result' });
    });
  }
});
</script>
```

## Web Components Integration

```html
<my-component hx-on::connected-callback="htmx.process(this)">
  <button hx-get="/data"
          hx-target="find #output">
    Load Data
  </button>
  <div id="output"></div>
</my-component>
```

Call `htmx.process(element)` after rendering web component templates to activate htmx attributes inside shadow DOM.
