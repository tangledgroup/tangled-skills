# Community Extensions: UI

Extensions for managing loading states, CSS classes, element manipulation, and DOM morphing.

## loading-states

Manage loading indicators, disable elements, and toggle CSS classes during requests.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-loading-states@2.0.0/loading-states.js"></script>
```

### Default CSS
```css
[data-loading] { display: none; }
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| `data-loading` | Show element during request. Value sets display style: `"block"`, `"flex"`, `"inline-block"` |
| `data-loading-class="<classes>"` | Add classes during request, remove after |
| `data-loading-class-remove="<classes>"` | Remove classes during request, add back after |
| `data-loading-disable` | Disable element during request |
| `data-loading-aria-busy` | Add `aria-busy="true"` during request |
| `data-loading-delay="<ms>"` | Delay before applying loading state (default: 200ms) |
| `data-loading-target="<selector>"` | Apply loading state to different target element |
| `data-loading-path="<path>"` | Only apply for requests matching this path |
| `data-loading-states` | Scope boundary — only process elements within this container |

### Examples

```html
<div hx-ext="loading-states">
  <!-- Show loading text -->
  <div data-loading>Loading...</div>

  <!-- Show loading with flex display -->
  <div data-loading="flex"><span>⏳</span></div>

  <!-- Add opacity class during request -->
  <div data-loading-class="opacity-50 pointer-events-none">
    Content that fades during request
  </div>

  <!-- Remove background during request -->
  <div class="bg-gray-100" data-loading-class-remove="bg-gray-100">
    Background removed during request
  </div>

  <!-- Disable button -->
  <button data-loading-disable>Submit</button>

  <!-- Delay loading state by 1 second -->
  <button data-loading-disable data-loading-delay="1000">Submit</button>

  <!-- Target different element for loading -->
  <form hx-post="/save" data-loading-target="#spinner" data-loading-class-remove="hidden">
    <button data-loading-disable>Save</button>
  </form>
  <div id="spinner" class="hidden">Loading...</div>

  <!-- Scope loading states -->
  <div data-loading-states>
    <div hx-get="/data"></div>
    <div data-loading>Loading...</div>
  </div>
</div>
```

---

## class-tools

Manipulate CSS classes with timing for animations and transitions.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-class-tools@2.0.1/class-tools.js"></script>
```

### Usage

```html
<div hx-ext="class-tools">
  <!-- Add class "foo" after 100ms -->
  <div classes="add foo"></div>

  <!-- Remove class "bar" after 1s -->
  <div class="bar" classes="remove bar:1s"></div>

  <!-- Sequential: remove bar after 1s, then add foo 1s later -->
  <div class="bar" classes="remove bar:1s, add foo:1s"></div>

  <!-- Parallel: both after 1s (separated by &) -->
  <div class="bar" classes="remove bar:1s & add foo:1s"></div>

  <!-- Toggle class every 1s -->
  <div classes="toggle foo:1s"></div>
</div>
```

### Syntax

- Runs separated by `&` (parallel) or `,` (sequential within run)
- Operations: `add`, `remove`, `toggle`
- Delay: `:<time>` (e.g., `:100ms`, `:1s`)
- Default delay: 100ms

### OOB Class Manipulation

```html
<!-- In server response, surgically apply classes to #my-element -->
<div hx-swap-oob="beforeend: #my-element">
  <div hx-ext="class-tools"
       apply-parent-classes="add flash-green, remove flash-green:10s">
  </div>
</div>
```

The element self-removes after scheduling parent class changes.

---

## attribute-tools

Similar to class-tools but for arbitrary HTML attributes.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-attribute-tools@2.0.0/attribute-tools.js"></script>
```

### Usage
```html
<div hx-ext="attribute-tools">
  <div attributes='add title:"Hello", data-id:42'></div>
  <div data-attributes='remove title:1s'></div>
</div>
```

---

## multi-swap

Swap multiple elements from a single response, each with its own swap method.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-multi-swap@2.0.0/multi-swap.js"></script>
```

### Usage
```html
<div hx-ext="multi-swap"
     hx-get="/dashboard"
     hx-target="#clock #notifications #main-content">
</div>
```

Server response includes elements with matching IDs. Each can specify its own swap style via `hx-swap-oob`.

### Per-Element Swap Methods

```html
<!-- Server response: -->
<div id="clock" hx-swap-oob="innerHTML">3:00 PM</div>
<div id="notifications" hx-swap-oob="beforeend"><p>New!</p></div>
<div id="main-content" hx-swap-oob="morph">...</div>
```

---

## remove-me

Remove an element after a specified time interval.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-remove-me@2.0.0/remove-me.js"></script>
```

### Usage
```html
<div hx-ext="remove-me" remove-me="5s">
  This disappears after 5 seconds
</div>

<!-- With fade-out -->
<div hx-ext="remove-me" remove-me="3s" classes="opacity-100, opacity-0:2.9s">
  Fades out then removed
</div>
```

---

## morphdom-swap

Alternative DOM morphing using the morphdom library.

### Installation
```html
<script src="https://unpkg.com/morphdom@2.6.1/dist/morphdom-umd.min.js"></script>
<script src="https://unpkg.com/htmx-ext-morphdom-swap@2.0.0/morphdom-swap.js"></script>
```

### Usage
```html
<div hx-ext="morphdom-swap"
     hx-get="/data"
     hx-swap="morphdom">
</div>
```

Provides `morphdom` as a swap strategy. Similar to idiomorph but uses the morphdom algorithm.

---

## alpine-morph

Use Alpine.js's built-in morph plugin as htmx swap strategy. Preserves Alpine component state during swaps.

### Installation
```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx-ext-alpine-morph@2.0.0/alpine-morph.js"></script>
```

### Usage
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

Preserves Alpine reactivity and component state across htmx swaps. Essential when entire Alpine components are replaced by htmx responses.
