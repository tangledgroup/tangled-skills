# Events and Scripting

## Event Lifecycle

htmx fires events throughout the request lifecycle. All events are fired in both camelCase and kebab-case (e.g., `htmx:afterSwap` and `htmx:after-swap`).

### Request Phase

- **`htmx:beforeRequest`** — Before an AJAX request is made
- **`htmx:configRequest`** — Customize parameters and headers before the request
- **`htmx:beforeSend`** — Just before the request is sent
- **`htmx:afterRequest`** — After the request completes (success or failure)

### Response Phase

- **`htmx:beforeOnLoad`** — Before any response processing
- **`htmx:afterOnLoad`** — After successful response processing
- **`htmx:beforeSwap`** — Before swapping, allows configuring the swap
- **`htmx:afterSwap`** — After new content is swapped in
- **`htmx:beforeSettle`** — Before settling (attribute transitions)
- **`htmx:afterSettle`** — After DOM has settled

### Load Events

- **`htmx:load`** — Fired when new content is added to the DOM

### Error Events

- **`htmx:responseError`** — Non-200/300 response code
- **`htmx:sendError`** — Network error preventing request
- **`htmx:timeout`** — Request timeout
- **`htmx:swapError`** — Error during swap phase
- **`htmx:targetError`** — Invalid target specified

### History Events

- **`htmx:historyRestore`** — History restoration action
- **`htmx:beforeHistorySave`** — Before saving to history cache
- **`htmx:historyCacheHit`** / **`htmx:historyCacheMiss`** — Cache hit/miss
- **`htmx:pushedIntoHistory`** / **`htmx:replacedInHistory`** — URL pushed/replaced

### Validation Events

- **`htmx:validation:validate`** — Before element validation
- **`htmx:validation:failed`** — Element failed validation
- **`htmx:validation:halted`** — Request halted due to validation

### XHR Progress Events

- **`htmx:xhr:loadstart`** — AJAX request starts
- **`htmx:xhr:progress`** — Periodic progress updates
- **`htmx:xhr:loadend`** — AJAX request ends
- **`htmx:xhr:abort`** — AJAX request aborted

## Listening for Events

Using `addEventListener`:

```js
document.body.addEventListener('htmx:load', function(evt) {
    myLib.init(evt.detail.elt);
});
```

Using htmx helper:

```js
htmx.on('htmx:load', function(evt) {
    myLib.init(evt.detail.elt);
});
```

Remove listeners with `htmx.off()`.

## Initializing 3rd-Party Libraries

The `htmx.onLoad()` helper is the standard pattern for initializing content after htmx swaps it into the DOM:

```js
htmx.onLoad(function(content) {
    var sortables = content.querySelectorAll('.sortable');
    for (var i = 0; i < sortables.length; i++) {
        new Sortable(sortables[i], {
            animation: 150,
            ghostClass: 'blue-background-class'
        });
    }
});
```

This ensures initialization runs only on newly loaded content, not the entire document.

## Configuring Requests with Events

Handle `htmx:configRequest` to modify parameters and headers:

```js
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.parameters['auth_token'] = getAuthToken();
    evt.detail.headers['Authentication-Token'] = getAuthToken();
});
```

## Modifying Swap Behavior

Handle `htmx:beforeSwap` to customize swapping:

```js
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if (evt.detail.xhr.status === 404) {
        alert('Error: Could Not Find Resource');
        evt.detail.shouldSwap = false;
    } else if (evt.detail.xhr.status === 422) {
        // Allow 422 to swap (form validation response)
        evt.detail.isError = false;
    }
});
```

## The `hx-on:` Attributes

HTML's `on*` attributes only support a fixed set of DOM events. `hx-on:*` responds to any event, preserving Locality of Behavior:

```html
<button hx-on:click="alert('You clicked me!')">
    Click Me!
</button>
```

Syntax: `hx-on:` followed by the event name (use kebab-case for htmx events since HTML attributes are case-insensitive):

```html
<button hx-post="/example"
        hx-on:htmx:config-request="event.detail.parameters.example = 'Hello!'">
    Post Me!
</button>
```

Reset user input after successful requests:

```html
<input name="query"
       hx-post="/search"
       hx-on::htmx:after-request="if(event.detail.successful) this.value = ''">
```

Note: `hx-on::` (double colon) targets the element itself without bubbling.

## 3rd-Party JavaScript Integration

If a library fires DOM events, use them as htmx triggers:

```html
<form class="sortable" hx-post="/items" hx-trigger="end">
    <div>Item 1</div>
    <div>Item 2</div>
</form>
```

SortableJS fires an "end" event when dragging completes, triggering the htmx POST.

## Processing Dynamically Added Content

When JavaScript adds content with htmx attributes to the DOM, call `htmx.process()`:

```js
let myDiv = document.getElementById('my-div');
fetch('http://example.com/data.html')
    .then(response => response.text())
    .then(data => {
        myDiv.innerHTML = data;
        htmx.process(myDiv);
    });
```

This is also needed when content comes from Alpine.js `<template x-if>` blocks or similar conditional rendering.

## Logging and Debugging

Log all htmx events:

```js
htmx.logAll();
```

Custom logger:

```js
htmx.logger = function(elt, event, data) {
    console.log(event, elt, data);
};
```

Monitor events on an element from the browser console:

```js
monitorEvents(htmx.find('#theElement'));
```

## JavaScript API Reference

Key methods on the `htmx` global:

- **`htmx.ajax(verb, path, target)`** — Issue an htmx-style AJAX request programmatically
- **`htmx.on(eventName, handler)`** — Create an event listener
- **`htmx.off(eventName, handler)`** — Remove an event listener
- **`htmx.onLoad(handler)`** — Register handler for `htmx:load` events
- **`htmx.process(elt)`** — Process an element and its children for htmx behavior
- **`htmx.swap(target, content, swapSpec)`** — Perform swapping of HTML content
- **`htmx.trigger(elt, eventName, detail)`** — Trigger an event on an element
- **`htmx.values(elt)`** — Get input values associated with an element
- **`htmx.find(selector)`** / **`htmx.findAll(selector)`** — Find elements
- **`htmx.addClass()`** / **`htmx.removeClass()`** / **`htmx.toggleClass()`** / **`htmx.takeClass()`** — Class manipulation
- **`htmx.remove(elt)`** — Remove an element
- **`htmx.closest(elt, selector)`** — Find closest matching ancestor
- **`htmx.parseInterval(str)`** — Parse interval string to milliseconds
- **`htmx.defineExtension(name, ext)`** — Define a custom extension
- **`htmx.logAll()`** — Install logger for all events
