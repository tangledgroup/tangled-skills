# Actions Components

## Button

Buttons allow the user to take actions. The `btn` class can be applied to `<button>`, `<a>`, or `<input>` elements.

### Class Names

- **component**: `btn`
- **color**: `btn-neutral`, `btn-primary`, `btn-secondary`, `btn-accent`, `btn-info`, `btn-success`, `btn-warning`, `btn-error`
- **style**: `btn-outline`, `btn-dash`, `btn-soft`, `btn-ghost`, `btn-link`
- **behavior**: `btn-active`, `btn-disabled`
- **size**: `btn-xs`, `btn-sm`, `btn-md`, `btn-lg`, `btn-xl`
- **modifier**: `btn-wide`, `btn-block`, `btn-square`, `btn-circle`

### Syntax

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-outline btn-secondary">Outline</button>
<button class="btn btn-sm btn-success">Small Success</button>
<a href="/page" class="btn btn-ghost">Link Button</a>
<input type="submit" class="btn btn-neutral" value="Submit" />
```

### Rules

- Pick one from each category (color, style, behavior, size, modifier)
- To disable with a class, use `tabindex="-1" role="button" aria-disabled="true"`
- Buttons can contain icons before or after text

## Dropdown

Dropdowns open a menu or any element when triggered. Three activation methods are supported.

### Class Names

- **component**: `dropdown`
- **part**: `dropdown-content`
- **placement**: `dropdown-start`, `dropdown-center`, `dropdown-end`, `dropdown-top`, `dropdown-bottom`, `dropdown-left`, `dropdown-right`
- **modifier**: `dropdown-hover`, `dropdown-open`, `dropdown-close`

### Syntax

Using `<details>` and `<summary>` (recommended, no JS):

```html
<details class="dropdown">
  <summary>Click me</summary>
  <ul class="dropdown-content menu bg-base-100 rounded-box w-52 p-2 shadow">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
  </ul>
</details>
```

Using Popover API:

```html
<button popovertarget="my-dropdown" style="anchor-name:--my-anchor">Open</button>
<ul class="dropdown-content menu bg-base-100 rounded-box w-52 p-2 shadow"
    popover id="my-dropdown" style="position-anchor:--my-anchor">
  <li><a>Item 1</a></li>
</ul>
```

Using CSS focus:

```html
<div class="dropdown">
  <div tabindex="0" role="button">Button</div>
  <ul tabindex="-1" class="dropdown-content">Content</ul>
</div>
```

### Rules

- Replace IDs and anchor names with unique values
- Content can be any HTML element, not just `<ul>`
- For CSS focus dropdowns, use `tabindex="0"` and `role="button"` on the trigger

## FAB / Speed Dial

Floating Action Button stays in the bottom corner. Clicking it reveals additional action buttons.

### Class Names

- **component**: `fab`
- **part**: `fab-close`, `fab-main-action`
- **modifier**: `fab-flower`

### Syntax

Simple FAB:

```html
<div class="fab">
  <button class="btn btn-lg btn-circle">+</button>
</div>
```

FAB with speed dial buttons:

```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">+</div>
  <button class="btn btn-lg btn-circle">1</button>
  <button class="btn btn-lg btn-circle">2</button>
  <button class="btn btn-lg btn-circle">3</button>
</div>
```

FAB with close button:

```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">+</div>
  <div class="fab-close">Close <span class="btn btn-circle btn-lg btn-error">✕</span></div>
  <button class="btn btn-lg btn-circle">1</button>
  <button class="btn btn-lg btn-circle">2</button>
</div>
```

FAB Flower (quarter-circle arrangement):

```html
<div class="fab fab-flower">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">+</div>
  <button class="fab-main-action btn btn-circle btn-lg">★</button>
  <button class="btn btn-lg btn-circle">1</button>
  <button class="btn btn-lg btn-circle">2</button>
</div>
```

### Rules

- The first child is the trigger button (visible when FAB is closed)
- Subsequent children are the action buttons (appear when open)
- Use `tabindex="0" role="button"` on the trigger for focus-based activation
- For flower layout with labels, wrap buttons in `<div class="tooltip tooltip-left" data-tip="Label">`

## Modal

Dialog boxes that overlay page content.

### Class Names

- **component**: `modal`
- **part**: `modal-box`, `modal-action`, `modal-backdrop`, `modal-toggle`
- **modifier**: `modal-open`
- **placement**: `modal-top`, `modal-middle`, `modal-bottom`, `modal-start`, `modal-end`

### Syntax

Using `<dialog>` element (recommended):

```html
<button onclick="my_modal.showModal()">Open modal</button>
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3 class="text-lg font-bold">Title</h3>
    <p class="py-4">Modal content here.</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop"><button>close</button></form>
</dialog>
```

Using checkbox (legacy, no JS):

```html
<label for="my-modal" class="btn">Open modal</label>
<input type="checkbox" id="my-modal" class="modal-toggle" />
<div class="modal">
  <div class="modal-box">Content</div>
  <label class="modal-backdrop" for="my-modal">Close</label>
</div>
```

Using anchor links (legacy):

```html
<a href="#my-modal" class="btn">Open</a>
<div class="modal" id="my-modal">
  <div class="modal-box">Content</div>
</div>
```

### Rules

- Use unique IDs for each modal
- Add `tabindex="0"` to make modal focusable
- For `<dialog>` modals, use `<form method="dialog">` for closing with submit

## Swap

Toggle visibility between two elements using a checkbox or class name.

### Class Names

- **component**: `swap`
- **part**: `swap-on`, `swap-off`, `swap-indeterminate`
- **modifier**: `swap-active`
- **style**: `swap-rotate`, `swap-flip`

### Syntax

Using checkbox:

```html
<label class="swap swap-rotate">
  <input type="checkbox" />
  <div class="swap-on">🌙</div>
  <div class="swap-off">☀️</div>
</label>
```

Using class name (controlled by JS):

```html
<div class="swap swap-flip">
  <div class="swap-on">On</div>
  <div class="swap-off">Off</div>
</div>
```

### Rules

- Use a hidden checkbox or add/remove `swap-active` class via JS
- `swap-indeterminate` shows content when checkbox is in indeterminate state
- `swap-rotate` and `swap-flip` add transition animations

## Theme Controller

Automatically sets the page theme based on a checked input's value attribute.

### Class Names

- **component**: `theme-controller`

### Syntax

```html
<input type="checkbox" value="dark" class="theme-controller" />
<input type="radio" name="theme" value="cupcake" class="theme-controller" />
<input type="radio" name="theme" value="dracula" class="theme-controller" checked />
```

### Rules

- The `value` attribute must be a valid daisyUI theme name
- Works with both checkbox and radio inputs
- When checked, the page adopts that theme automatically
