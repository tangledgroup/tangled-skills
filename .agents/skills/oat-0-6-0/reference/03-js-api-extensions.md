# JavaScript API and Extensions

Reference for Oat's JavaScript APIs, WebComponent internals, and third-party extensions.

## Global API

Oat exposes a global `window.ot` object with the following methods:

### Toast Notifications

```javascript
// Show a text toast
ot.toast(message, title?, options?)

// Show a toast with custom HTML element
ot.toast.el(element, options?)

// Clear toasts
ot.toast.clear(placement?)
```

**Toast options:**

- `variant` — `'success'`, `'danger'`, `'warning'` (default: `''`)
- `placement` — `'top-left'`, `'top-center'`, `'top-right'` (default), `'bottom-left'`, `'bottom-center'`, `'bottom-right'`
- `duration` — Auto-dismiss in milliseconds, 0 = persistent (default: `4000`)

**Examples:**

```javascript
// Simple toast
ot.toast('Saved!');

// Toast with title
ot.toast('Action completed successfully', 'All good');

// Toast with options
ot.toast('Something went wrong', 'Error', {
  variant: 'danger',
  placement: 'bottom-center'
});

// Custom HTML from a template element
ot.toast.el(document.querySelector('#my-template'), {
  duration: 8000,
  placement: 'bottom-center'
});

// Dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content</p>';
ot.toast.el(el);

// Clear all toasts
ot.toast.clear();

// Clear specific placement
ot.toast.clear('top-right');
```

Toast behavior:
- Pauses auto-dismiss on hover
- Elements are cloned before display (templates can be reused)
- Uses Popover API for positioning
- Animated enter/exit transitions

## WebComponents

Oat registers two custom elements:

### `<ot-dropdown>`

Dropdown component using the native Popover API. Provides automatic positioning, viewport overflow detection, keyboard navigation (ArrowUp/ArrowDown/Home/End), and ARIA state management.

**Structure:**

```html
<ot-dropdown>
  <button popovertarget="menu-id">Trigger</button>
  <menu popover id="menu-id">
    <button role="menuitem">Item 1</button>
    <button role="menuitem">Item 2</button>
  </menu>
</ot-dropdown>
```

**Behavior:**
- Positions dropdown relative to trigger
- Flips position if menu overflows viewport
- Repositions on scroll and resize
- Sets `aria-expanded` on trigger
- Focuses first menu item on open
- Returns focus to trigger on close
- Supports any popover content (not just `<menu>`)

### `<ot-tabs>`

Tabs component with keyboard navigation and ARIA state management.

**Structure:**

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Tab 1</button>
    <button role="tab">Tab 2</button>
  </div>
  <div role="tabpanel">Content 1</div>
  <div role="tabpanel">Content 2</div>
</ot-tabs>
```

**Behavior:**
- Generates unique IDs for tab/panel pairing
- Sets `aria-controls` and `aria-labelledby` automatically
- Keyboard navigation: ArrowLeft/ArrowRight between tabs
- Emits `ot-tab-change` custom event with `{ index, tab }` detail

**Programmatic API:**

```javascript
const tabs = document.querySelector('ot-tabs');

// Get active tab index
const idx = tabs.activeIndex;

// Set active tab
tabs.activeIndex = 2;

// Listen for changes
tabs.addEventListener('ot-tab-change', (e) => {
  console.log('Tab changed to:', e.detail.index);
});
```

## Tooltip Enhancement

Oat's tooltip system is a progressive enhancement. The native `title` attribute works without JavaScript. When `oat.min.js` loads, it:

1. Converts all `title` attributes to `data-tooltip` for custom styling
2. Adds `aria-label` if not present
3. Removes the original `title` to prevent double tooltips
4. Uses `MutationObserver` to handle dynamically added elements
5. Respects `data-tooltip-placement` for positioning (`top`, `bottom`, `left`, `right`)

## Sidebar Toggle

The sidebar toggle is handled by a simple click listener (not a WebComponent). When `[data-sidebar-toggle]` is clicked, it toggles `data-sidebar-open` on the closest `[data-sidebar-layout]` container. On mobile (≤768px), clicking outside the sidebar dismisses it.

## Polyfills

**Command API polyfill:** Oat includes a polyfill for `command`/`commandfor` attributes (used by dialog triggers) which are not supported in Safari:

```javascript
// Polyfill handles:
// button[commandfor="dialog-id"][command="show-modal"] → dialog.showModal()
// button[commandfor="dialog-id"][command="close"] → dialog.close()
```

**Dialog touch shim:** Prevents dialog backdrop clicks from bleeding through on touch devices.

## Base WebComponent Class

All Oat WebComponents extend `OtBase`, which provides:

- Lifecycle management (`connectedCallback`, `disconnectedCallback`)
- One-time initialization guard
- Central event handler pattern (`handleEvent` → `on{eventType}`)
- Keyboard navigation helper (`keyNav`)
- Custom event emitter (`emit`)
- Scoped query helpers (`$`, `$$`)
- Unique ID generator (`uid`)

## Source File Structure

**CSS files (in `src/css/`):**

- `00-base.css` — Cascade layer declarations, reset, base element styles
- `01-theme.css` — CSS variable definitions (colors, spacing, typography)
- `accordion.css` — `<details>`/`<summary>` styling
- `alert.css` — `[role="alert"]` styling
- `animations.css` — Animation keyframes
- `avatar.css` — Avatar component
- `badge.css` — Badge component
- `button.css` — Button variants and sizes
- `card.css` — Card component
- `dialog.css` — Dialog/modal styling
- `dropdown.css` — Dropdown popover styling
- `form.css` — Form element styling
- `grid.css` — 12-column grid system
- `progress.css` — Progress bar styling
- `sidebar.css` — Sidebar layout
- `skeleton.css` — Skeleton loading placeholders
- `spinner.css` — Loading spinner
- `table.css` — Table styling
- `tabs.css` — Tabs styling
- `toast.css` — Toast notification styling
- `tooltip.css` — Tooltip styling
- `utilities.css` — Utility helper classes

**JS files (in `src/js/`):**

- `base.js` — OtBase class and polyfills
- `dropdown.js` — `<ot-dropdown>` WebComponent
- `tabs.js` — `<ot-tabs>` WebComponent
- `tooltip.js` — Title-to-tooltip enhancement
- `sidebar.js` — Sidebar toggle handler
- `toast.js` — Toast notification API
- `index.js` — Entry point, registers `window.ot` APIs

## Third-Party Extensions

**oat-chips:** Chip/tag component with dismissible filters, colors, and toggle selection. ~1KB gzipped.

**oat-animate:** Lightweight animation extension with declarative `ot-animate` triggers (`on-load`, `hover`, `in-view`) and reduced-motion support. ~1KB gzipped.

Extensions are developed by the community. Open a PR on the Oat repository to list new extensions.
