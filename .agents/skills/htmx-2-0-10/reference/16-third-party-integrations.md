# Third-Party Integrations

Patterns for using htmx alongside other JavaScript libraries and frameworks.

## Alpine.js

Alpine.js and htmx complement each other well — htmx handles server communication, Alpine handles reactivity and UI state.

### Basic Integration

```html
<div x-data="{ open: false }">
  <button @click="open = true"
          hx-get="/modal-content"
          hx-target="#modal-body">
    Open Modal
  </button>

  <div x-show="open" id="modal">
    <div id="modal-body"></div>
    <button @click="open = false">Close</button>
  </div>
</div>
```

### htmx.process() with Alpine

After htmx swaps content containing Alpine directives, call `htmx.process()` is automatic. For dynamic content:

```html
<div x-data="{ items: [] }"
     hx-get="/items"
     hx-trigger="load">
  <template x-for="item in items" :key="item.id">
    <div x-text="item.name"></div>
  </template>
</div>
```

### Preserving Alpine State with Morph

Use the `alpine-morph` extension to preserve Alpine component state during htmx swaps:

```html
<div hx-ext="alpine-morph"
     x-data="{ count: 0 }">
  <button hx-get="/update"
          hx-swap="alpine-morph"
          @click="count++">
    Count: <span x-text="count"></span>
  </button>
</div>
```

### Event Interoperability

```html
<!-- Alpine triggers htmx -->
<button @click="$dispatch('htmx:trigger', { target: '#search-results' })">
  Search
</button>

<!-- htmx triggers Alpine -->
<div hx-on::after-swap="$dispatch('alpine:update')">
  Content
</div>
```

---

## jQuery

Use jQuery's event system and DOM helpers alongside htmx.

### Event Handling

```javascript
// Listen to htmx events with jQuery
$(document).on('htmx:afterRequest', function(evt) {
  console.log('Request done:', evt.originalEvent.detail.path);
});

// Initialize plugins after htmx swap
htmx.onLoad(function(elt) {
  $(elt).find('.datepicker').datepicker();
  $(elt).find('.tooltip').tooltip();
});
```

### DOM Manipulation

```javascript
// Use jQuery to trigger htmx events
$('#button').on('click', function() {
  htmx.trigger('#target', 'htmx:request');
});

// Modify request with jQuery
$(document).on('htmx:configRequest', function(evt) {
  evt.originalEvent.detail.headers['X-CSRF'] = $('meta[name=csrf]').attr('content');
});
```

---

## hyperscript

hyperscript pairs naturally with htmx for event-driven scripting without JavaScript.

### Basic Pairing

```html
<button _="on click from #trigger
       send htmx-request to this
       then set my text to 'Loading...'
       on htmx:afterRequest
       set my text to 'Done'">
  Load Data
</button>
```

### Event-Driven Patterns

```html
<div _="on htmx:afterSwap from #form
       if the target contains '.error'
       then flash me red
       else flash me green">
  Status
</div>
```

---

## Vanilla JavaScript

Standard patterns for integrating custom JS with htmx.

### Initializing After Swap

```javascript
htmx.onLoad('.chart-container', function(elt) {
  new Chart(elt.querySelector('canvas'), { /* config */ });
});
```

### Cleanup Before History Save

```javascript
document.body.addEventListener('htmx:beforeHistorySave', function() {
  // Destroy chart instances before saving snapshot
  document.querySelectorAll('.chart-container').forEach(function(el) {
    if (el._chart) el._chart.destroy();
  });
});

document.body.addEventListener('htmx:afterHistoryRestore', function() {
  // Re-initialize after restore
  htmx.onLoad('.chart-container', function(elt) {
    elt._chart = new Chart(elt.querySelector('canvas'), { /* config */ });
  });
});
```

---

## SortableJS

Drag-and-drop sorting with automatic server sync.

### Basic Setup

```html
<ul id="sortable" class="sortable-list">
  <li data-id="1">Item 1</li>
  <li data-id="2">Item 2</li>
  <li data-id="3">Item 3</li>
</ul>

<script src="https://cdn.jsdelivr.net/npm/sortablejs@1/Sortable.min.js"></script>
<script>
htmx.onLoad(function(elt) {
  var el = elt.querySelector('.sortable-list');
  if (el && !el._sortableInit) {
    el._sortableInit = true;
    new Sortable(el, {
      animation: 150,
      onEnd: function(evt) {
        // Build order from DOM
        var order = [];
        el.querySelectorAll('li').forEach(function(li) {
          order.push(li.getAttribute('data-id'));
        });

        // Send to server
        htmx.ajax('POST', '/reorder', {
          values: { order: order.join(',') },
          target: el,
          swap: 'none'
        });
      }
    });
  }
});
</script>
```

### With Hidden Inputs

```html
<form hx-post="/reorder" hx-trigger="end from:.sortable-list">
  <ul class="sortable-list">
    <li data-id="1"><input type="hidden" name="order[]" value="1" />Item 1</li>
    <li data-id="2"><input type="hidden" name="order[]" value="2" />Item 2</li>
  </ul>
  <button type="submit">Save Order</button>
</form>
```

---

## Web Components

htmx works with Web Components (custom elements and shadow DOM).

### Custom Elements

```html
<my-card hx-get="/card-data"
         hx-trigger="load"
         hx-target="find .content">
  <div class="content"></div>
</my-card>
```

### Shadow DOM

htmx attributes inside shadow DOM need `htmx.process()` called after the element upgrades:

```javascript
class MyComponent extends HTMLElement {
  connectedCallback() {
    const shadow = this.attachShadow({ mode: 'open' });
    shadow.innerHTML = `
      <button hx-get="/data" hx-target="find #output">Load</button>
      <div id="output"></div>
    `;
    // Activate htmx inside shadow DOM
    htmx.process(shadow.root);
  }
}
customElements.define('my-component', MyComponent);
```

### After Template Rendering

When using `<template>` elements:

```javascript
const template = document.getElementById('my-template');
const clone = template.content.cloneNode(true);
document.body.appendChild(clone);
htmx.process(clone); // Activate htmx in cloned content
```

---

## SweetAlert2

Custom confirmation dialogs with htmx.

```html
<button hx-delete="/item/1"
        hx-confirm="true"
        id="delete-btn">
  Delete
</button>

<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<script>
document.body.addEventListener('htmx:confirm', function(evt) {
  evt.preventDefault();
  Swal.fire({
    title: 'Are you sure?',
    text: 'This cannot be undone',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Delete'
  }).then(function(result) {
    if (result.isConfirmed) {
      evt.detail.issueRequest();
    }
  });
});
</script>
```

---

## Tom Select

Rich select/dropdown with htmx history support.

```html
<select name="tags" class="tom-select">
  <option value="htmx">htmx</option>
  <option value="web">web</option>
</select>

<script src="https://cdn.jsdelivr.net/npm/tom-select@2/dist/tom-select.complete.min.js"></script>
<script>
// Initialize
document.querySelectorAll('.tom-select').forEach(function(el) {
  new TomSelect(el, { /* options */ });
});

// Cleanup before history save
document.body.addEventListener('htmx:beforeHistorySave', function() {
  document.querySelectorAll('.tom-select').forEach(function(el) {
    if (el.tomselect) el.tomselect.destroy();
  });
});

// Re-initialize after history restore
document.body.addEventListener('htmx:afterHistoryRestore', function() {
  document.querySelectorAll('.tom-select').forEach(function(el) {
    if (!el.tomselect) {
      new TomSelect(el, { /* options */ });
    }
  });
});
</script>
```

---

## Integration Checklist

When integrating any third-party library with htmx:

1. **Initialize after swap**: Use `htmx.onLoad(selector, callback)` to init on swapped content
2. **Cleanup for history**: Destroy instances in `htmx:beforeHistorySave`
3. **Re-init after restore**: Re-create instances in `htmx:afterHistoryRestore`
4. **Process shadow DOM**: Call `htmx.process(element)` for Web Components
5. **Event bridge**: Use `htmx.trigger()` and custom events to communicate between libraries
6. **Avoid conflicts**: Don't use jQuery's AJAX if htmx handles the request; use htmx events instead
