# Components Reference

Complete reference for all Oat UI components with usage examples.

## Typography

Base text elements are styled automatically. No classes needed.

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>
<p>This is a paragraph with <strong>bold text</strong>, <em>italic text</em>, and <a href="#">a link</a>.</p>
<p>Here's some <code>inline code</code> and a code block:</p>
<pre><code>function hello() { console.log('Hello, World!'); }</code></pre>
<blockquote>This is a blockquote. It's styled automatically.</blockquote>
<hr>
<ul>
  <li>Unordered list item 1</li>
  <li>Unordered list item 2</li>
</ul>
<ol>
  <li>Ordered list item 1</li>
  <li>Ordered list item 2</li>
</ol>
```

## Accordion

Use native `<details>` and `<summary>` for collapsible content. Add `name` attribute to group accordions (only one open at a time, like radio buttons).

```html
<details>
  <summary>What is Oat?</summary>
  <p>Oat is a minimal, semantic-first UI component library with zero dependencies.</p>
</details>
<details>
  <summary>How do I use it?</summary>
  <p>Include the CSS and JS files, then write semantic HTML.</p>
</details>

<!-- Grouped: only one open at a time -->
<details name="faq">
  <summary>First option</summary>
  <p>Content for first.</p>
</details>
<details name="faq">
  <summary>Second option</summary>
  <p>Content for second.</p>
</details>
```

## Alert

Use `role="alert"` for alert styling. Set `data-variant` for color variants.

```html
<div role="alert" data-variant="success">
  <strong>Success!</strong> Your changes have been saved.
</div>
<div role="alert" data-variant="warning">
  <strong>Warning!</strong> Please review before continuing.
</div>
<div role="alert">
  <strong>Info</strong> This is a default alert message.
</div>
<div role="alert" data-variant="error">
  <strong>Error!</strong> Something went wrong.
</div>
```

Variants: `success`, `warning`, `error` (default: info/neutral).

## Avatar

Use `<figure data-variant="avatar">` with an `<img>` tag, or text initials with `<abbr>`.

```html
<!-- Image avatar -->
<figure data-variant="avatar" class="small" aria-label="Jane Doe">
  <img src="/avatar.svg" alt="" />
</figure>

<!-- Initials avatar -->
<figure data-variant="avatar" aria-label="Oat">
  <abbr title="Jane Doe">JD</abbr>
</figure>

<!-- Sizes: small (default), large -->
<figure data-variant="avatar" class="large" aria-label="Jane Doe">
  <img src="/avatar.svg" alt="" />
</figure>
```

**Avatar group:** Wrap avatars in `<figure data-variant="avatar" role="group">` for grouped avatars. Add `.small` or `.large` to the group container to control all child sizes.

```html
<figure data-variant="avatar" role="group" class="small" aria-label="Team members">
  <figure data-variant="avatar" aria-label="Jane Doe"><img src="/a.svg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="John Smith"><img src="/b.svg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="Alex Lee"><img src="/c.svg" alt="" /></figure>
</figure>
```

## Badge

Use `.badge` with `data-variant` for color variants. `.outline` is a style modifier.

```html
<span class="badge">Default</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge outline">Outline</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
```

## Breadcrumb

Use a semantic `<nav>` with an ordered list and `aria-current="page"` for the active item.

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-7)">
    <li><a href="#" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#" class="unstyled">Projects</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#" class="unstyled" aria-current="page"><strong>Current</strong></a></li>
  </ol>
</nav>
```

## Button

The `<button>` element is styled by default. Use `data-variant` for semantic variants and classes for visual styles.

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button data-variant="danger" class="outline">Danger Outline</button>
<button class="ghost">Ghost</button>
<button disabled>Disabled</button>
```

**Sizes:** Use `.small` or `.large`.

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
<a href="#" class="button">Hyperlink styled as button</a>
```

**Button group:** Wrap buttons in `<menu class="buttons">` for connected buttons.

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

Variants: `secondary`, `danger` (default: primary).
Styles: `outline`, `ghost`.

## Card

Use `class="card"` for a visual box-like card look.

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description goes here.</p>
  </header>
  <p>This is the card content. It can contain any HTML.</p>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

## Dialog

Fully semantic, zero-JS dynamic dialog with `<dialog>`. Use `commandfor` and `command="show-modal"` attributes on an element to open a target dialog. Focus trapping, z-placement, and keyboard shortcuts work out of the box.

```html
<button commandfor="demo-dialog" command="show-modal">Open dialog</button>
<dialog id="demo-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Title</h3>
      <p>This is a dialog description.</p>
    </header>
    <div>
      <p>Dialog content goes here.</p>
      <p>Click outside or press Escape to close.</p>
    </div>
    <footer>
      <button type="button" commandfor="demo-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

**With form fields:**

```html
<button commandfor="form-dialog" command="show-modal">Open form dialog</button>
<dialog id="form-dialog">
  <form method="dialog">
    <header><h3>Edit form</h3></header>
    <div class="vstack">
      <label>Name <input name="name" required></label>
      <label>Email <input name="email" type="email"></label>
    </div>
    <footer>
      <button type="button" commandfor="form-dialog" command="close" class="outline">Cancel</button>
      <button value="save">Save</button>
    </footer>
  </form>
</dialog>
```

**Handling return value:** Listen to the native `close` event.

```javascript
const dialog = document.querySelector("#demo-dialog");
dialog.addEventListener('close', (e) => {
  console.log(dialog.returnValue); // "confirm"
});
```

Or use `onclose` inline:

```html
<dialog id="my-dialog" onclose="console.log(this.returnValue)">
```

**Safari polyfill:** Oat includes a polyfill for `command`/`commandfor` attributes (not supported in Safari). The JS bundle handles this automatically.

## Dropdown

Wrap in `<ot-dropdown>`. Uses the native Popover API with `popovertarget` on the trigger and `popover` on the target. WebComponent provides positioning, keyboard navigation, and ARIA state management.

```html
<ot-dropdown>
  <button popovertarget="demo-menu" class="outline">
    Options
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m6 9 6 6 6-6" />
    </svg>
  </button>
  <menu popover id="demo-menu">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <button role="menuitem">Help</button>
    <hr>
    <button role="menuitem">Logout</button>
  </menu>
</ot-dropdown>
```

**Popover dropdown:** `<ot-dropdown>` can also wrap non-menu popover elements.

```html
<ot-dropdown>
  <button popovertarget="confirm-popover" class="outline">Confirm</button>
  <article class="card" popover id="confirm-popover">
    <header>
      <h4>Are you sure?</h4>
      <p>This action cannot be undone.</p>
    </header>
    <br />
    <footer>
      <button class="outline small" popovertarget="confirm-popover">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm-popover">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

## Form Elements

Form elements are styled automatically. Wrap inputs in `<label>` for proper association. Use `data-field` on the label for field-level styling with hint support.

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>
  <label data-field>
    Email
    <input type="email" placeholder="you@example.com" />
  </label>
  <label data-field>
    Password
    <input type="password" placeholder="Password" aria-describedby="password-hint" />
    <small id="password-hint" data-hint>This is a small hint</small>
  </label>
  <div data-field>
    <label>Select</label>
    <select aria-label="Select an option">
      <option value="">Select an option</option>
      <option value="a">Option A</option>
      <option value="b">Option B</option>
    </select>
  </div>
  <label data-field>
    Message
    <textarea placeholder="Your message..."></textarea>
  </label>
  <label data-field>
    Disabled
    <input type="text" placeholder="Disabled" disabled />
  </label>
  <label data-field>
    File<br />
    <input type="file" />
  </label>
  <label data-field>
    Date and time
    <input type="datetime-local" />
  </label>
</form>
```

**Validation states:** Add `.error` class to a `<div>` with `role="status"` for validation error display.

```html
<div data-field>
  <label>Email <input type="email" aria-describedby="error-message" /></label>
  <div id="error-message" class="error" role="status">Please enter a valid email address.</div>
</div>
```

**Checkbox and radio:** Standard `<input type="checkbox">` and `<input type="radio">` are styled automatically.

## Meter

Use the native `<meter>` element for values within a known range. Browser shows colors based on `low`/`high`/`optimum` attributes.

```html
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

## Pagination

Reuses existing button and `<menu>` components. No special markup.

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#" class="button outline small">&larr; Previous</a></li>
    <li><a href="#" class="button outline small">1</a></li>
    <li><a href="#" class="button outline small">2</a></li>
    <li><a href="#" class="button small" aria-current="page">3</a></li>
    <li><a href="#" class="button outline small">4</a></li>
    <li><a href="#" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

## Progress

Use the native `<progress>` element.

```html
<progress value="60" max="100"></progress>
<progress value="30" max="100"></progress>
<progress value="90" max="100"></progress>
```

## Spinner

Use `aria-busy="true"` on any element to show a loading indicator. Size with `data-spinner`.

```html
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="large"></div>
<button aria-busy="true" data-spinner="small" disabled>Loading</button>
```

**Overlay spinner:** Adding `data-spinner="overlay"` dims the container contents and overlays the spinner on top.

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <header><h3>Card Title</h3></header>
  <p>This content is dimmed while loading.</p>
</article>
```

Sizes: `small`, default, `large`. Add `overlay` for container overlay mode.

## Skeleton

Use `.skeleton` with `role="status"` for loading placeholders. Add `.line` for text or `.box` for images.

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

**Skeleton card layout:**

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-6);">
  <div role="status" class="skeleton box"></div>
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 60%"></div>
  </div>
</article>
```

## Sidebar

Use `data-sidebar-layout` on a container (typically `<body>`) with `<aside data-sidebar>` for the sidebar and `<main>` for content. The sidebar stays sticky while main content scrolls. On mobile, it becomes a slide-out overlay toggled by `[data-sidebar-toggle]`.

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">&#9776;</button>
    <span>App Name</span>
  </nav>
  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Users</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#">General</a></li>
              <li><a href="#">Security</a></li>
              <li><a href="#">Billing</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer>
      <button class="outline small" style="width: 100%;">Logout</button>
    </footer>
  </aside>
  <main>
    <div style="padding: var(--space-3)">Main page content.</div>
  </main>
</body>
```

**Sidebar attributes:**

- `data-sidebar-layout` — Container grid layout wrapper (sidebar + main), typically `<body>`
- `data-sidebar-layout="always"` — Always-collapsible sidebar (toggle visible on all screen sizes)
- `data-topnav` — Full-width top nav element (optional, spans full width above sidebar)
- `data-sidebar` — Sticky sidebar element (`<aside>`)
- `data-sidebar-toggle` — Button that toggles sidebar (mobile overlay and always mode collapse)
- `data-sidebar-open` — Applied to layout when sidebar is open

## Switch

Add `role="switch"` to a checkbox for toggle switch styling.

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked> Confabulation
</label>
<label>
  <input type="checkbox" role="switch" disabled> Disabled off
</label>
```

## Table

Tables are styled by default. Use `<thead>` and `<tbody>` tags. Wrap in `class="table"` container for horizontal scrollbar on small screens.

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Alice Johnson</td>
        <td>alice@example.com</td>
        <td>Admin</td>
        <td><span class="badge" data-variant="success">Active</span></td>
      </tr>
      <tr>
        <td>Bob Smith</td>
        <td>bob@example.com</td>
        <td>Editor</td>
        <td><span class="badge">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

## Tabs

Wrap tab buttons and panels in `<ot-tabs>`. WebComponent provides keyboard navigation and ARIA state management. Uses `role="tablist"`, `role="tab"`, and `role="tabpanel"`.

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab">Password</button>
    <button role="tab">Notifications</button>
  </div>
  <div role="tabpanel">
    <h3>Account Settings</h3>
    <p>Manage your account information here.</p>
  </div>
  <div role="tabpanel">
    <h3>Password Settings</h3>
    <p>Change your password here.</p>
  </div>
  <div role="tabpanel">
    <h3>Notification Settings</h3>
    <p>Configure your notification preferences.</p>
  </div>
</ot-tabs>
```

The WebComponent emits `ot-tab-change` custom event with `{ index, tab }` detail. Programmatically set active tab via `activeIndex` property.

## Tooltip

Use the standard `title` attribute on any element to render a tooltip with smooth transition. Replaced elements like `<img>`, `<iframe>` need to be wrapped in a parent with the `title` attribute. Add `data-tooltip-placement` to position the tooltip (default: `top`).

```html
<button title="Save your changes">Save</button>
<button title="Delete this item" data-variant="danger">Delete</button>
<a href="#" title="View your profile">Profile</a>
<span title="Images need a parent with title"><img src="/logo.svg" height="32" /></span>

<button title="On top">Top</button>
<button title="Below" data-tooltip-placement="bottom">Bottom</button>
<button title="On the left" data-tooltip-placement="left">Left</button>
<button title="On the right" data-tooltip-placement="right">Right</button>
```

Placements: `top` (default), `bottom`, `left`, `right`.

## Toast

Show toast notifications with `ot.toast(message, title?, options?)`.

```html
<button onclick="ot.toast('Action completed successfully', 'All good', { variant: 'success' })">Success</button>
<button onclick="ot.toast('Something went wrong', 'Oops', { variant: 'danger', placement: 'top-left' })" data-variant="danger">Danger</button>
<button onclick="ot.toast('Please review this warning', 'Warning', { variant: 'warning', placement: 'bottom-right' })" class="outline">Warning</button>
<button onclick="ot.toast('New notification', 'For your attention', { placement: 'top-center' })">Info</button>
```

**Placements:** `top-left`, `top-center`, `top-right` (default), `bottom-left`, `bottom-center`, `bottom-right`.

**Options:**

- `variant` — `'success'`, `'danger'`, `'warning'` (default: `''`)
- `placement` — position on screen (default: `'top-right'`)
- `duration` — auto-dismiss in ms, 0 = persistent (default: `4000`)

**Custom markup:** Use `ot.toast.el(element, options?)` to show toasts with custom HTML content. Element is cloned before display, so templates can be reused.

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000 })">
  Toast with action
</button>
```

**Dynamic element:**

```javascript
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content here</p>';
ot.toast.el(el);
```

**Clearing toasts:**

```javascript
ot.toast.clear();              // Clear all
ot.toast.clear('top-right');   // Clear specific placement
```

## Grid

A 12-column grid system using CSS grid. Use `.container`, `.row`, and `.col` classes. Column widths use `.col-{n}` where n is 1-12. Supports `offset-{n}` for gutters and `col-end` to push remaining columns to the end.

```html
<div class="container">
  <div class="row">
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
  </div>
  <div class="row">
    <div class="col-6">col-6</div>
    <div class="col-6">col-6</div>
  </div>
  <div class="row">
    <div class="col-4 offset-2">col-4 offset-2</div>
    <div class="col-4">col-4</div>
  </div>
  <div class="row">
    <div class="col-3">col-3</div>
    <div class="col-4 col-end">col-4 col-end</div>
  </div>
</div>
```

## Utilities and Helpers

Commonly used utility classes:

**Text alignment:**
- `.align-left`, `.align-center`, `.align-right`
- `.text-light` — muted text color
- `.text-lighter` — faint text color

**Flexbox helpers:**
- `.flex` — `display: flex`
- `.flex-col` — `flex-direction: column`
- `.items-center` — `align-items: center`
- `.justify-center`, `.justify-between`, `.justify-end`
- `.hstack` — horizontal flex with gap (Bootstrap-inspired)
- `.vstack` — vertical flex with gap

**Spacing:**
- `.gap-1`, `.gap-2`, `.gap-4`
- `.mt-2`, `.mt-4`, `.mt-6` — margin top
- `.mb-2`, `.mb-4`, `.mb-6` — margin bottom
- `.p-4` — padding

**Other:**
- `.w-100` — `width: 100%`
- `.unstyled` — removes list styles, text decoration, and padding from `ul`, `ol`, `a`
