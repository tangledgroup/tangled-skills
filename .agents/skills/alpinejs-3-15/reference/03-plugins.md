# Plugins

All official plugins follow the same installation pattern. Load them before Alpine's core script (CDN) or register with `Alpine.plugin()` (module).

## Installation Pattern

**CDN** (load before Alpine core):
```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/<plugin>@3.x.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**NPM**:
```js
import Alpine from 'alpinejs'
import plugin from '@alpinejs/<plugin>'
Alpine.plugin(plugin)
Alpine.start()
```

---

## Mask Plugin

Automatically formats text input as the user types. Useful for phone numbers, credit cards, dates, etc.

```html
<input x-mask="999-999-9999" x-model="phone">
```

Dynamic masks with function:
```html
<input x-mask="($input) => $input.startsWith('+') ? '+9 9999 9999' : '999-999-9999'" x-model="phone">
```

Mask characters:
- `9` — any digit (0-9)
- `a` — any letter (a-z, A-Z)
- `*` — alphanumeric
- `S` — uppercase letter only
- `s` — lowercase letter only
- Any literal character passes through as-is

---

## Intersect Plugin

Wrapper for Intersection Observer API. Triggers expressions when elements enter/leave the viewport.

```html
<div x-data="{ shown: false }" x-intersect="shown = true">
    <div x-show="shown" x-transition>I'm in the viewport!</div>
</div>
```

**Modifiers**:
- `.once` — only trigger on first intersection
- `.off` — trigger when element leaves viewport
- `.threshold.50%` — trigger at 50% visibility

```html
<div x-intersect.once="loaded = true">...</div>
<div x-intersect.off="visible = false">...</div>
```

---

## Resize Plugin

Wrapper for Resize Observer API. Triggers when an element changes size.

```html
<div x-data="{ width: 0, height: 0 }"
     x-resize="width = $width; height = $height">
    <span x-text="width + 'x' + height"></span>
</div>
```

Provides `$width` and `$height` magic properties in the expression.

---

## Persist Plugin

Persist Alpine state across page loads using `localStorage`.

```html
<div x-data="{ count: $persist(0) }">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

**Custom key**:

```html
<div x-data="{ count: $persist(0, 'my-counter') }">
```

**Custom storage adapter**:

```js
document.addEventListener('alpine:init', () => {
    Alpine.magic('persist', (value, key) => {
        return Alpine.$persist(value, key, sessionStorage)
    })
})
```

---

## Collapse Plugin

Smoothly animate height when showing/hiding elements. Use with `x-show`.

```html
<div x-data="{ expanded: false }">
    <button @click="expanded = !expanded">Toggle</button>
    <div x-show="expanded" x-collapse>
        Content that collapses smoothly...
    </div>
</div>
```

**Modifiers**:
- `.duration.400ms` — custom animation duration
- `.min.80px` — minimum height when collapsed

```html
<div x-show="open" x-collapse.duration.300ms.min.50px>
```

---

## Focus Plugin (formerly Trap)

Manage focus within the page. Built on the Tabbable library.

**x-trap**: Trap keyboard focus inside an element:

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    <div x-trap="open" x-show="open">
        <!-- Tab key cycles through focusable elements inside this div -->
        <input>
        <button @click="open = false">Close</button>
    </div>
</div>
```

**Modifiers**:
- `.noautofocus` — prevent auto-focusing the first element
- `.inert` — add `aria-inert` to content outside the trap
- `.noreturnfocus` — don't return focus to the triggering element on release

**$focus()**: Programmatically focus elements:

```html
<div x-init="$nextTick(() => $focus($refs.input))">
    <input x-ref="input">
</div>
```

---

## Anchor Plugin

Position an element relative to another using Floating UI. Useful for dropdowns, tooltips, popovers.

```html
<div x-data="{ open: false }">
    <button x-ref="trigger" @click="open = !open">Menu</button>
    <div x-anchor="$refs.trigger" x-show="open">
        Dropdown contents...
    </div>
</div>
```

**Placement modifiers**: `.start`, `.end`, `.flip`, `.skew`, `.shift`

```html
<div x-anchor.end="$refs.trigger" x-show="open">Right-aligned dropdown</div>
<div x-anchor.flip="$refs.trigger" x-show="open">Auto-flips if no room</div>
```

---

## Morph Plugin

Replace an element's HTML while preserving Alpine and browser state. Core utility for HTMX-like server-driven UI.

```html
<div x-ref="content">
    Initial content
</div>

<button x-data @click="fetch('/new-content.html').then(r => r.text()).then(html => {
    Alpine.morph($refs.content, html)
})">
    Update Content
</button>
```

Morph preserves form input values, Alpine component state, and event listeners on unchanged elements.

---

## Sort Plugin

Drag-and-drop reordering of list items. Built on SortableJS.

```html
<ul x-data x-sort @sort="items = $event.detail">
    <template x-for="item in items" :key="item.id">
        <li x-text="item.name"></li>
    </template>
</ul>
```

**Options via x-bind**:

```html
<ul x-data x-sort x-bind="sortOptions">
```

```js
// In Alpine.data or script
const sortOptions = {
    'x-sort-handle': '.drag-handle',  // drag handle selector
    'x-sort-group': 'shared-name',     // allow cross-list dragging
}
```
