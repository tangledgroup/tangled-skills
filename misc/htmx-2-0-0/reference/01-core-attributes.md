# Core Attributes

## AJAX Request Attributes

These attributes issue HTTP requests directly from HTML elements:

**`hx-get`** — Issues a GET request to the given URL.

```html
<button hx-get="/messages">Load Messages</button>
```

**`hx-post`** — Issues a POST request to the given URL.

```html
<button hx-post="/clicked" hx-target="#parent-div" hx-swap="outerHTML">
    Click Me!
</button>
```

**`hx-put`** — Issues a PUT request.

**`hx-patch`** — Issues a PATCH request.

**`hx-delete`** — Issues a DELETE request.

All five follow the same pattern: `<element hx-{verb}="/url">`. The element issues a request of the specified type when triggered.

## Triggers (`hx-trigger`)

By default, requests fire on the "natural" event of an element:

- `input`, `textarea`, `select` → `change` event
- `form` → `submit` event
- everything else → `click` event

Override with `hx-trigger`:

```html
<div hx-post="/mouse_entered" hx-trigger="mouseenter">
    [Here Mouse, Mouse!]
</div>
```

### Trigger Modifiers

Append modifiers after the event name:

- **`once`** — Fire only once
- **`changed`** — Only fire if the element value has changed
- **`delay:<time>`** — Wait before firing; reset on each new event (e.g., `delay:500ms`)
- **`throttle:<time>`** — Discard events during the throttle window
- **`from:<CSS selector>`** — Listen on a different element

```html
<input type="text" name="q"
       hx-get="/search"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#results"
       placeholder="Search...">
<div id="results"></div>
```

Multiple triggers separated by commas:

```html
<input hx-post="/save" hx-trigger="blur, click">
```

### Trigger Filters

Use square brackets with a JavaScript expression:

```html
<div hx-get="/clicked" hx-trigger="click[ctrlKey]">
    Control Click Me
</div>
```

Properties resolve against the triggering event first, then global scope. `this` is set to the current element.

### Special Events

- **`load`** — Fires once when the element is first loaded
- **`revealed`** — Fires once when the element scrolls into the viewport
- **`intersect`** — Fires on intersection with optional `root:<selector>` and `threshold:<float>` options

### Polling

Use `every` for periodic requests:

```html
<div hx-get="/news" hx-trigger="every 2s"></div>
```

Respond with HTTP 286 to stop polling.

### Load Polling

An element replaces itself with the response, creating a self-sustaining poll:

```html
<div hx-get="/messages"
     hx-trigger="load delay:1s"
     hx-swap="outerHTML">
</div>
```

If `/messages` returns the same pattern, polling continues. Useful for progress bars and termination-based polling.

## Targets (`hx-target`)

Direct the response to a different element using a CSS selector:

```html
<input type="text" name="q"
       hx-get="/search"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#search-results">
<div id="search-results"></div>
```

### Extended CSS Selectors

- **`this`** — The element the attribute is on
- **`closest <selector>`** — Closest ancestor matching the selector (or self)
- **`next <selector>`** — Next sibling matching the selector
- **`previous <selector>`** — Previous sibling matching the selector
- **`find <selector>`** — First descendant matching the selector

```html
<tr>
    <td><button hx-delete="/row" hx-target="closest tr" hx-swap="outerHTML">Delete</button></td>
</tr>
```

Selectors may also be wrapped in `<` and `/>` for hyperscript-style query literals.

## Swapping (`hx-swap`)

Controls how response content is inserted into the DOM:

- **`innerHTML`** — Default. Puts content inside the target element
- **`outerHTML`** — Replaces the entire target element
- **`afterbegin`** — Prepends content before the first child
- **`beforebegin`** — Inserts content before the target
- **`beforeend`** — Appends content after the last child
- **`afterend`** — Inserts content after the target
- **`delete`** — Deletes the target regardless of response
- **`none`** — No swap (OOB swaps and response headers still processed)

### Morph Swaps

Morphing merges new content into the existing DOM, preserving focus, video state, etc. Available via extensions:

- **Idiomorph** — Created by the htmx team
- **Morphdom Swap** — Based on the morphdom library
- **Alpine-morph** — Plays well with Alpine.js

### View Transitions

Use the experimental View Transitions API for animated DOM transitions:

- Set `htmx.config.globalViewTransitions = true` for all swaps
- Use `transition:true` in `hx-swap`
- Catch `htmx:beforeTransition` and call `preventDefault()` to cancel

### Swap Options

Append modifiers after the swap style, colon-separated:

```html
<button hx-post="/like" hx-swap="outerHTML ignoreTitle:true">Like</button>
```

Available options:

- **`transition`** — `true`/`false`, use View Transitions API
- **`swap`** — Delay between clearing old content and inserting new (e.g., `100ms`)
- **`settle`** — Delay between insertion and settling (e.g., `100ms`)
- **`ignoreTitle`** — `true` to skip updating document title from `<title>` in response
- **`scroll`** — `top` or `bottom`, scroll target to its top/bottom
- **`show`** — `top` or `bottom`, scroll target's top/bottom into view

## Synchronization (`hx-sync`)

Coordinate requests between elements to avoid race conditions:

```html
<form hx-post="/store">
    <input id="title" name="title" type="text"
           hx-post="/validate"
           hx-trigger="change"
           hx-sync="closest form:abort">
    <button type="submit">Submit</button>
</form>
```

`hx-sync="closest form:abort"` aborts the input's validation request if the form submits. Programmatic cancellation uses `htmx.trigger('#element', 'htmx:abort')`.

## Request Indicators (`hx-indicator`)

Show loading indicators during requests. Elements with class `htmx-indicator` are hidden by default (opacity: 0) and revealed when `htmx-request` class is present on a parent.

```html
<button hx-get="/click">
    Click Me!
    <img class="htmx-indicator" src="/spinner.gif" alt="Loading...">
</button>
```

Target a different element with `hx-indicator="#indicator"`. Use `hx-disabled-elt` to disable elements during requests.

## Parameters (`hx-params`, `hx-vals`, `hx-include`)

**`hx-params`** — Filter which parameters are included:

```html
<button hx-post="/search" hx-params="not q, include:*">Search</button>
```

**`hx-vals`** — Add JSON values to the request:

```html
<button hx-post="/example" hx-vals='{"auth_token": "abc123"}'>Submit</button>
```

Supports `js:` prefix for dynamic values (requires `allowEval: true`).

**`hx-include`** — Include additional form data by CSS selector:

```html
<div id="user-data">
    <input name="userId" value="42">
</div>
<button hx-post="/action" hx-include="#user-data">Action</button>
```

## Confirming (`hx-confirm`, `hx-prompt`)

**`hx-confirm`** — Show a confirm dialog before the request:

```html
<button hx-delete="/item/5" hx-confirm="Are you sure?">Delete</button>
```

**`hx-prompt`** — Show a prompt dialog, value sent as a parameter:

```html
<button hx-post="/rename" hx-prompt="Enter new name:">Rename</button>
```

## Attribute Inheritance

Child elements inherit htmx attributes from parents. Control inheritance with:

- **`hx-inherit`** — Explicitly enable specific attribute inheritance
- **`hx-disinherit`** — Disable specific attribute inheritance
- **`htmx.config.disableInheritance`** — Globally disable (then use `hx-inherit` to opt-in)

## The `data-` Prefix

All htmx attributes work with the `data-` prefix for valid HTML:

```html
<a data-hx-post="/click">Click Me!</a>
```
