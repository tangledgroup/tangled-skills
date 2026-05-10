# Dynamic Components (JavaScript / Web Components)

These components require the OAT JavaScript bundle (`oat.min.js`). They use Web Components and native browser APIs.

## Dialog

Uses native `<dialog>` element with `commandfor`/`command` attributes for opening/closing. Zero-JS interaction pattern (with Safari polyfill in base.js).

```html
<button commandfor="my-dialog" command="show-modal">Open Dialog</button>
<dialog id="my-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Dialog Title</h3>
      <p>Description text.</p>
    </header>
    <div>
      <p>Dialog content here. Any HTML is allowed.</p>
    </div>
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

**Key attributes**:
- `commandfor="id"` — Target element ID (on trigger button)
- `command="show-modal"` — Opens dialog as modal
- `command="close"` — Closes the target dialog
- `closedby="any"` — Allows closing by clicking backdrop or pressing Escape
- `form method="dialog"` — Required for native form submission inside dialogs

**Styling**: Fixed position, centered, max-width 32rem, max-height 85vh. Animated opacity + scale transition. Backdrop fades in with semi-transparent black. Header/footer/content sections auto-padded.

### Dialog with Form Fields

```html
<dialog id="edit-dialog">
  <form method="dialog">
    <header><h3>Edit Profile</h3></header>
    <div class="vstack">
      <label>Name <input name="name" required></label>
      <label>Email <input name="email" type="email"></label>
    </div>
    <footer>
      <button type="button" commandfor="edit-dialog" command="close" class="outline">Cancel</button>
      <button value="save">Save</button>
    </footer>
  </form>
</dialog>
```

### Handling Return Value

```javascript
const dialog = document.querySelector("#my-dialog");
dialog.addEventListener('close', (e) => {
  console.log(dialog.returnValue); // "confirm" or "save"
});
```

Or inline: `<dialog id="my-dialog" onclose="console.log(this.returnValue)">`

### command/commandfor Polyfill

OAT includes a polyfill for Safari which lacks native `command`/`commandfor` support. The polyfill listens for clicks on `button[commandfor]` and calls `showModal()`/`close()` on the target `<dialog>`.

---

## Dropdown

Web Component `<ot-dropdown>` wrapping the native Popover API. Provides positioning, keyboard navigation, and ARIA state management.

```html
<ot-dropdown>
  <button popovertarget="my-menu" class="outline">
    Options
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m6 9 6 6 6-6" />
    </svg>
  </button>
  <menu popover id="my-menu">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <button role="menuitem">Help</button>
    <hr>
    <button role="menuitem">Logout</button>
  </menu>
</ot-dropdown>
```

**Key attributes**:
- `popovertarget="id"` — Target popover element ID (on trigger)
- `popover` — Marks the target as a popover element
- `role="menuitem"` — On each menu item button for keyboard navigation
- `<hr>` — Separator between menu sections

**Keyboard navigation**: ArrowUp/ArrowDown to navigate items, Home/End for first/last. Focus returns to trigger on close.

**Positioning**: Automatically positioned below trigger. Flips above if it would overflow viewport bottom. Shifts left if it would overflow right edge. Repositions on scroll and resize.

### Popover Card

Dropdown can show any popover element, not just menus:

```html
<ot-dropdown>
  <button popovertarget="confirm-popover" class="outline">Confirm</button>
  <article class="card" popover id="confirm-popover">
    <header>
      <h4>Are you sure?</h4>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button class="outline small" popovertarget="confirm-popover">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm-popover">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

---

## Tabs

Web Component `<ot-tabs>` providing keyboard navigation and ARIA state management for tabbed interfaces.

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab">Password</button>
    <button role="tab">Notifications</button>
  </div>
  <div role="tabpanel">
    <h3>Account Settings</h3>
    <p>Manage your account.</p>
  </div>
  <div role="tabpanel">
    <h3>Password Settings</h3>
    <p>Change your password.</p>
  </div>
  <div role="tabpanel">
    <h3>Notification Settings</h3>
    <p>Configure notifications.</p>
  </div>
</ot-tabs>
```

**Structure**: One `[role="tablist"]` container with `[role="tab"]` buttons, followed by matching `[role="tabpanel"]` elements. Panel count must match tab count (ordered).

**ARIA management**: OtTabs automatically generates IDs, sets `aria-controls`, `aria-labelledby`, `aria-selected`, and `tabindex` on init.

**Keyboard navigation**: ArrowLeft/ArrowRight to switch tabs with focus following.

**Events**: Fires `ot-tab-change` custom event on tab switch:

```javascript
document.querySelector('ot-tabs').addEventListener('ot-tab-change', (e) => {
  console.log('Tab index:', e.detail.index);
  console.log('Tab element:', e.detail.tab);
});
```

**Programmatic control**:

```javascript
const tabs = document.querySelector('ot-tabs');
tabs.activeIndex = 2; // Switch to third tab
console.log(tabs.activeIndex); // Get current tab index
```

---

## Toast

JavaScript API for notification toasts. Exposed via `window.ot.toast`.

### Text Toasts

```javascript
// Simple message
ot.toast('Action completed successfully');

// With title
ot.toast('Changes saved', 'Success');

// With options
ot.toast('Something went wrong', 'Error', {
  variant: 'danger',
  placement: 'bottom-center'
});
```

### Options

| Option | Default | Values |
|--------|---------|--------|
| `variant` | `''` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | `'top-left'`, `'top-center'`, `'top-right'`, `'bottom-left'`, `'bottom-center'`, `'bottom-right'` |
| `duration` | `4000` | Milliseconds (0 = persistent, manual dismiss only) |

### Custom Markup Toasts

```javascript
// From a template element
ot.toast.el(document.querySelector('#my-template'), { duration: 8000 });

// From a dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content.</p>';
ot.toast.el(el);
```

Template example:

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000 })">
  Show custom toast
</button>
```

Templates are cloned before display, so they can be reused.

### Clearing Toasts

```javascript
ot.toast.clear();              // Clear all toasts everywhere
ot.toast.clear('top-right');   // Clear only top-right placement
```

### Behavior

- Toasts auto-dismiss after `duration` ms (default 4000)
- Hovering a toast pauses the auto-dismiss timer
- Resuming hover restarts the timer
- Animated slide-in entry and collapse exit
- Stacked vertically in placement containers
- Uses native Popover API for container positioning

---

## Tooltip

Progressive enhancement of the native `title` attribute. Converts `title` to styled `data-tooltip` attributes via MutationObserver.

```html
<button title="Save your changes">Save</button>
<button title="Delete" data-variant="danger">Delete</button>
<a href="#" title="View profile">Profile</a>
```

**Placement**: Default is `top`. Override with `data-tooltip-placement`:

```html
<button title="On top">Top</button>
<button title="Below" data-tooltip-placement="bottom">Bottom</button>
<button title="Left" data-tooltip-placement="left">Left</button>
<button title="Right" data-tooltip-placement="right">Right</button>
```

**Placements**: `top` (default), `bottom`, `left`, `right`.

**Behavior**:
- JS converts `title` → `data-tooltip` and removes the native title
- Adds `aria-label` if not present
- Shows on `:hover` and `:focus-visible` with 700ms delay
- Smooth opacity + transform transition
- Pure CSS rendering (no JS positioning at show time)
- Works progressively: native `title` works without JS

**Replaced elements**: For `<img>`, `<iframe>`, etc., wrap in a parent with the `title`:

```html
<span title="Logo"><img src="logo.svg" height="32" /></span>
```
