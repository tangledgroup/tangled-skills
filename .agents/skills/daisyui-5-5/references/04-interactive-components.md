# DaisyUI Interactive Components

This guide covers interactive components in DaisyUI 5.5 including buttons, modals, dropdowns, accordions, tabs, tooltips, and popovers.

## Button

### Basic Buttons

```html
<button class="btn">Default Button</button>
```

### Button Colors

```html
<button class="btn btn-neutral">Neutral</button>
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-info">Info</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-warning">Warning</button>
<button class="btn btn-error">Error</button>
```

### Button Styles

| Style | Class | Description |
|-------|-------|-------------|
| Solid (default) | `btn` | Filled button |
| Outline | `btn-outline` | Bordered button |
| Dash | `btn-dash` | Dashed border |
| Soft | `btn-soft` | Subtle background |
| Ghost | `btn-ghost` | No background |
| Link | `btn-link` | Text link style |

```html
<button class="btn btn-primary btn-outline">Outline Primary</button>
<button class="btn btn-success btn-soft">Soft Success</button>
<button class="btn btn-error btn-ghost">Ghost Error</button>
<button class="btn btn-link">Link Button</button>
```

### Button Sizes

| Size | Class |
|------|-------|
| Extra Small | `btn-xs` |
| Small | `btn-sm` |
| Medium | `btn-md` |
| Large | `btn-lg` |
| Extra Large | `btn-xl` |

```html
<button class="btn btn-sm">Small</button>
<button class="btn btn-md">Medium</button>
<button class="btn btn-lg">Large</button>
```

### Button Modifiers

```html
<!-- Full width -->
<button class="btn btn-block">Full Width</button>

<!-- Wide button -->
<button class="btn btn-wide">Wide Button</button>

<!-- Square button -->
<button class="btn btn-square">🔘</button>

<!-- Circle button -->
<button class="btn btn-circle">○</button>

<!-- Active state -->
<button class="btn btn-active">Active</button>

<!-- Disabled -->
<button class="btn" disabled>Disabled</button>
```

### Button with Icons

```html
<!-- Icon before text -->
<button class="btn">
  ← Back
</button>

<!-- Icon after text -->
<button class="btn">
  Next →
</button>

<!-- Icon only -->
<button class="btn btn-circle">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
    <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM18.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z" />
  </svg>
</button>

<!-- Loading state -->
<button class="btn">
  <span class="loading loading-spinner"></span>
  Loading...
</button>
```

### Button Group (Join)

```html
<div class="join">
  <button class="join-item btn">←</button>
  <button class="join-item btn">1</button>
  <button class="join-item btn">2</button>
  <button class="join-item btn">3</button>
  <button class="join-item btn">→</button>
</div>
```

## Modal

### HTML Dialog Element (Recommended)

```html
<button class="btn" onclick="my_modal_1.showModal()">
  Open modal
</button>

<dialog id="my_modal_1" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
    <p class="py-4">Modal content goes here.</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

### Modal with Checkbox (Legacy)

```html
<input type="checkbox" id="my_modal_2" class="modal-toggle" />
<label for="my_modal_2" class="btn">Open modal</label>

<div class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
    <p class="py-4">Modal content.</p>
    <div class="modal-action">
      <label for="my_modal_2" class="btn">Close</label>
    </div>
  </div>
  <label class="modal-backdrop" for="my_modal_2">Close</label>
</div>
```

### Modal Placement

```html
<!-- Top -->
<dialog class="modal modal-top">
  <div class="modal-box">Top modal</div>
</dialog>

<!-- Middle (default) -->
<dialog class="modal modal-middle">
  <div class="modal-box">Middle modal</div>
</dialog>

<!-- Bottom -->
<dialog class="modal modal-bottom">
  <div class="modal-box">Bottom modal</div>
</dialog>

<!-- Start (left) -->
<dialog class="modal modal-start">
  <div class="modal-box">Left modal</div>
</dialog>

<!-- End (right) -->
<dialog class="modal modal-end">
  <div class="modal-box">Right modal</div>
</dialog>
```

### Modal with Form

```html
<dialog id="form_modal" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Contact Form</h3>
    <form class="space-y-4 p-4">
      <input type="text" class="input input-bordered w-full" placeholder="Name" />
      <input type="email" class="input input-bordered w-full" placeholder="Email" />
      <textarea class="textarea textarea-bordered w-full" placeholder="Message"></textarea>
      <div class="modal-action">
        <button type="submit" class="btn btn-primary">Send</button>
        <form method="dialog">
          <button class="btn">Cancel</button>
        </form>
      </div>
    </form>
  </div>
</dialog>
```

## Dropdown

### Using Details/Summary

```html
<div class="dropdown">
  <details>
    <summary class="btn">Dropdown</summary>
    <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] p-2 shadow w-52">
      <li><a>Item 1</a></li>
      <li><a>Item 2</a></li>
      <li><a>Item 3</a></li>
    </ul>
  </details>
</div>
```

### Using Popover API

```html
<div class="dropdown">
  <button id="dropdown_button" class="btn" popovertarget="my_popover">
    Dropdown
  </button>
  <ul id="my_popover" popover class="menu dropdown-content bg-base-100 rounded-box z-[1] p-2 shadow w-52">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
    <li><a>Item 3</a></li>
  </ul>
</div>
```

### Using CSS Focus

```html
<div class="dropdown">
  <div tabindex="0" role="button" class="btn">
    Dropdown
  </div>
  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] p-2 shadow w-52">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
    <li><a>Item 3</a></li>
  </ul>
</div>
```

### Dropdown Placement

```html
<!-- Top alignment -->
<div class="dropdown dropdown-top">
  <div tabindex="0" role="button" class="btn">Top</div>
  <ul class="menu dropdown-content">
    <li><a>Item 1</a></li>
  </ul>
</div>

<!-- Bottom (default) -->
<div class="dropdown dropdown-bottom">
  <div tabindex="0" role="button" class="btn">Bottom</div>
  <ul class="menu dropdown-content">
    <li><a>Item 1</a></li>
  </ul>
</div>

<!-- Left alignment -->
<div class="dropdown dropdown-left">
  <div tabindex="0" role="button" class="btn">Left</div>
  <ul class="menu dropdown-content">
    <li><a>Item 1</a></li>
  </ul>
</div>

<!-- Right alignment -->
<div class="dropdown dropdown-right">
  <div tabindex="0" role="button" class="btn">Right</div>
  <ul class="menu dropdown-content">
    <li><a>Item 1</a></li>
  </ul>
</div>

<!-- Horizontal positions -->
<div class="dropdown dropdown-start">
  <div tabindex="0" role="button" class="btn">Start</div>
  <ul class="menu dropdown-content"><li><a>Item</a></li>
  </ul>
</div>

<div class="dropdown dropdown-center">
  <div tabindex="0" role="button" class="btn">Center</div>
  <ul class="menu dropdown-content"><li><a>Item</a></li>
  </ul>
</div>

<div class="dropdown dropdown-end">
  <div tabindex="0" role="button" class="btn">End</div>
  <ul class="menu dropdown-content"><li><a>Item</a></li>
  </ul>
</div>
```

### Hover Dropdown

```html
<div class="dropdown dropdown-hover">
  <div tabindex="0" role="button" class="btn">Hover me</div>
  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] p-2 shadow w-52">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
  </ul>
</div>
```

## Accordion (Collapse)

### Basic Collapse

```html
<div class="collapse collapse-arrow bg-base-200">
  <input type="radio" name="my-accordion-3" aria-hidden="true" role="tab" />
  <div class="collapse-title text-xl font-medium">
    Click me to expand
  </div>
  <div class="collapse-content">
    <p>Accordion content goes here.</p>
  </div>
</div>
```

### Accordion Group (Only One Open)

```html
<div class="accordion space-y-2">
  <!-- Item 1 -->
  <div class="collapse collapse-arrow bg-base-200">
    <input type="radio" name="accordion" aria-hidden="true" role="tab" checked="checked" />
    <div class="collapse-title text-xl font-medium">Item 1</div>
    <div class="collapse-content">
      <p>Content for item 1.</p>
    </div>
  </div>
  
  <!-- Item 2 -->
  <div class="collapse collapse-arrow bg-base-200">
    <input type="radio" name="accordion" aria-hidden="true" role="tab" />
    <div class="collapse-title text-xl font-medium">Item 2</div>
    <div class="collapse-content">
      <p>Content for item 2.</p>
    </div>
  </div>
  
  <!-- Item 3 -->
  <div class="collapse collapse-arrow bg-base-200">
    <input type="radio" name="accordion" aria-hidden="true" role="tab" />
    <div class="collapse-title text-xl font-medium">Item 3</div>
    <div class="collapse-content">
      <p>Content for item 3.</p>
    </div>
  </div>
</div>
```

### Multiple Independent Accordions

```html
<!-- Accordion group 1 -->
<div class="collapse collapse-arrow">
  <input type="radio" name="group1" aria-hidden="true" />
  <div class="collapse-title">Group 1 - Item 1</div>
  <div class="collapse-content">Content 1</div>
</div>

<!-- Accordion group 2 -->
<div class="collapse collapse-arrow">
  <input type="radio" name="group2" aria-hidden="true" />
  <div class="collapse-title">Group 2 - Item 1</div>
  <div class="collapse-content">Content 2</div>
</div>
```

### Collapse Modifiers

```html
<!-- Arrow indicator -->
<div class="collapse collapse-arrow">
  <input type="radio" name="my-accordion-1" aria-hidden="true" />
  <div class="collapse-title">Arrow</div>
  <div class="collapse-content">Content</div>
</div>

<!-- Plus indicator -->
<div class="collapse collapse-plus">
  <input type="radio" name="my-accordion-2" aria-hidden="true" />
  <div class="collapse-title">Plus</div>
  <div class="collapse-content">Content</div>
</div>

<!-- Open by default -->
<div class="collapse collapse-open">
  <input type="radio" name="my-accordion-3" aria-hidden="true" />
  <div class="collapse-title">Open</div>
  <div class="collapse-content">Content</div>
</div>

<!-- Close indicator -->
<div class="collapse collapse-close">
  <input type="radio" name="my-accordion-4" aria-hidden="true" />
  <div class="collapse-title">Close</div>
  <div class="collapse-content">Content</div>
</div>
```

### Using Details/Summary

```html
<details class="collapse collapse-arrow bg-base-200">
  <summary class="collapse-title text-xl font-medium">
    Click me to expand
  </summary>
  <div class="collapse-content">
    <p>Content here.</p>
  </div>
</details>
```

## Tabs

### Basic Tabs (Buttons)

```html
<div class="tabs tabs-boxed">
  <a class="tab tab-active">One</a>
  <a class="tab">Two</a>
  <a class="tab">Three</a>
</div>
```

### Tabs with Radio Inputs

```html
<div class="tabs">
  <input type="radio" name="my_tabs_1" role="tab" class="tab tab-active" aria-selected="true" checked />
  <div class="tab-content bg-base-200 p-4 rounded-b-lg">Tab 1 Content</div>
  
  <input type="radio" name="my_tabs_1" role="tab" class="tab" aria-selected="false" />
  <div class="tab-content bg-base-200 p-4 rounded-b-lg">Tab 2 Content</div>
  
  <input type="radio" name="my_tabs_1" role="tab" class="tab" aria-selected="false" />
  <div class="tab-content bg-base-200 p-4 rounded-b-lg">Tab 3 Content</div>
</div>
```

### Tab Styles

```html
<!-- Boxed tabs -->
<div class="tabs tabs-box">
  <a class="tab tab-active">One</a>
  <a class="tab">Two</a>
</div>

<!-- Bordered tabs -->
<div class="tabs tabs-border">
  <a class="tab tab-active">One</a>
  <a class="tab">Two</a>
</div>

<!-- Lift tabs (underline lifts on hover) -->
<div class="tabs tabs-lift">
  <a class="tab tab-active">One</a>
  <a class="tab">Two</a>
</div>
```

### Tab Placement

```html
<!-- Top (default) -->
<div class="tabs tabs-top">
  <a class="tab tab-active">Top</a>
  <a class="tab">Tab</a>
</div>

<!-- Bottom -->
<div class="tabs tabs-bottom">
  <a class="tab tab-active">Bottom</a>
  <a class="tab">Tab</a>
</div>
```

### Tab Modifiers

```html
<!-- Active tab -->
<a class="tab tab-active">Active</a>

<!-- Disabled tab -->
<a class="tab tab-disabled" aria-disabled="true">Disabled</a>
```

## Tooltip

### Basic Tooltip

```html
<div class="tooltip" data-tip="Hover me">
  <button class="btn">Hover for tooltip</button>
</div>
```

### Tooltip Placement

```html
<!-- Top (default) -->
<div class="tooltip tooltip-top" data-tip="Top">
  <button class="btn">Top</button>
</div>

<!-- Bottom -->
<div class="tooltip tooltip-bottom" data-tip="Bottom">
  <button class="btn">Bottom</button>
</div>

<!-- Left -->
<div class="tooltip tooltip-left" data-tip="Left">
  <button class="btn">Left</button>
</div>

<!-- Right -->
<div class="tooltip tooltip-right" data-tip="Right">
  <button class="btn">Right</button>
</div>
```

### Tooltip with Custom Content

```html
<div class="tooltip" data-tip="<strong>Bold</strong> and <em>italic</em> text">
  <button class="btn">Rich tooltip</button>
</div>
```

## Popover

### Basic Popover (Popover API)

```html
<button popovertarget="my_popover" class="btn">
  Open popover
</button>

<div id="my_popover" popover class="p-4 bg-base-200 rounded shadow-xl">
  <h3 class="font-bold">Popover Title</h3>
  <p>Popover content goes here.</p>
  <button popovertarget="my_popover" class="btn btn-sm mt-2">
    Close
  </button>
</div>
```

### Popover Placement

```html
<button popovertarget="popover1" class="btn">Popover</button>
<div id="popover1" popover class="p-4 bg-base-200 rounded shadow-xl absolute">
  Content
</div>
```

## Menu

### Basic Menu

```html
<ul class="menu bg-base-200 rounded-box w-52">
  <li><a>Item 1</a></li>
  <li><a>Item 2</a></li>
  <li><a>Item 3</a></li>
</ul>
```

### Menu with Icons

```html
<ul class="menu bg-base-200 rounded-box w-52">
  <li>
    <a>
      🏠 Home
    </a>
  </li>
  <li>
    <a>
      ⚙️ Settings
    </a>
  </li>
  <li>
    <a>
      👤 Profile
    </a>
  </li>
</ul>
```

### Menu with Dropdown

```html
<ul class="menu bg-base-200 rounded-box w-52">
  <li>
    <details>
      <summary>Parent</summary>
      <ul class="menu-dropdown">
        <li><a>Submenu 1</a></li>
        <li><a>Submenu 2</a></li>
      </ul>
    </details>
  </li>
  <li><a>Item</a></li>
</ul>
```

### Menu States

```html
<ul class="menu bg-base-200 rounded-box w-52">
  <li><a class="menu-active">Active Item</a></li>
  <li><a>Normal Item</a></li>
  <li><a class="menu-disabled" tabindex="-1" aria-disabled="true">Disabled</a></li>
</ul>
```

### Menu with Title

```html
<ul class="menu bg-base-200 rounded-box w-52">
  <li><h2 class="menu-title">Menu Title</h2></li>
  <li><a>Item 1</a></li>
  <li><a>Item 2</a></li>
</ul>
```

### Horizontal Menu

```html
<ul class="menu menu-horizontal bg-base-200 rounded-box">
  <li><a>Home</a></li>
  <li><a>About</a></li>
  <li><a>Services</a></li>
  <li><a>Contact</a></li>
</ul>
```

### Menu Sizes

```html
<ul class="menu menu-sm bg-base-200 rounded-box w-52">
  <li><a>Small Menu</a></li>
</ul>

<ul class="menu menu-lg bg-base-200 rounded-box w-52">
  <li><a>Large Menu</a></li>
</ul>
```

## Component Best Practices

1. **Use semantic HTML** - Buttons should be `<button>` elements, navigation in `<nav>`
2. **Maintain keyboard accessibility** - All interactive components support Tab navigation
3. **Provide focus indicators** - DaisyUI includes focus styles by default
4. **Use ARIA attributes** - Add `role`, `aria-label`, `aria-expanded` where needed
5. **Test on mobile** - Ensure touch targets are large enough (minimum 44px)
6. **Consider reduced motion** - Some users prefer animations disabled
7. **Provide close mechanisms** - Modals and popovers should have clear close buttons

## Accessibility Examples

```html
<!-- Accessible button with icon -->
<button class="btn btn-ghost" aria-label="Close dialog">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
  </svg>
</button>

<!-- Accessible dropdown -->
<div class="dropdown">
  <div tabindex="0" role="button" aria-expanded="false" class="btn">
    Menu
  </div>
  <ul class="menu dropdown-content" role="menu">
    <li><a role="menuitem">Item 1</a></li>
    <li><a role="menuitem">Item 2</a></li>
  </ul>
</div>

<!-- Accessible modal -->
<dialog id="modal" class="modal" role="alertdialog" aria-labelledby="modal-title" aria-describedby="modal-desc">
  <div class="modal-box">
    <h3 id="modal-title" class="font-bold text-lg">Confirmation</h3>
    <p id="modal-desc" class="py-4">Are you sure you want to proceed?</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Cancel</button>
        <button class="btn btn-primary">Confirm</button>
      </form>
    </div>
  </div>
</dialog>
```
