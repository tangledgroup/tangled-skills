# Layout Components

## Divider

Visual separator, vertical or horizontal.

### Class Names

- **component**: `divider`
- **color**: `divider-neutral`, `divider-primary`, `divider-secondary`, `divider-accent`, `divider-success`, `divider-warning`, `divider-info`, `divider-error`
- **direction**: `divider-vertical`, `divider-horizontal`
- **placement**: `divider-start`, `divider-end`

### Syntax

```html
<div class="divider">OR</div>
<div class="divider divider-primary"></div>
<div class="divider divider-dash divider-secondary">Section</div>
```

### Rules

- Omit text content for a blank divider line
- `divider-vertical` renders the divider as a vertical rule between inline elements

## Drawer

Grid layout with a show/hide sidebar on left or right side.

### Class Names

- **component**: `drawer`
- **part**: `drawer-toggle`, `drawer-content`, `drawer-side`, `drawer-overlay`
- **placement**: `drawer-end`
- **modifier**: `drawer-open`
- **variant**: `is-drawer-open:`, `is-drawer-close:`

### Syntax

Basic drawer with toggle button:

```html
<div class="drawer">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col items-center justify-center min-h-screen">
    <h1>Page Content</h1>
    <label for="my-drawer" class="btn drawer-button">Open drawer</label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <li><a>Item 1</a></li>
      <li><a>Item 2</a></li>
    </ul>
  </div>
</div>
```

Always-open on large screens:

```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- Page content -->
  </div>
  <div class="drawer-side">
    <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <li><a>Sidebar Item 1</a></li>
      <li><a>Sidebar Item 2</a></li>
    </ul>
  </div>
</div>
```

Collapsible icon sidebar (icons-only when closed):

```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer-3" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content"><!-- Page content --></div>
  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer-3" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="is-drawer-close:w-14 is-drawer-open:w-64 bg-base-200 flex flex-col items-start min-h-full">
      <ul class="menu w-full grow">
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Home">
            🏠 <span class="is-drawer-close:hidden">Homepage</span>
          </button>
        </li>
      </ul>
      <div class="m-2">
        <label for="my-drawer-3" class="btn btn-ghost btn-circle drawer-button">↔️</label>
      </div>
    </div>
  </div>
</div>
```

### Rules

- `id` is required on the `drawer-toggle` checkbox input
- Use `<label for="id">` to open/close the drawer
- `lg:drawer-open` keeps sidebar visible on large screens
- All page content (navbar, footer, etc.) must be inside `drawer-content`
- `is-drawer-open:` and `is-drawer-close:` variant prefixes conditionally apply styles based on drawer state

## Footer

Page footer with logo, copyright, and navigation links.

### Class Names

- **component**: `footer`
- **part**: `footer-title`
- **placement**: `footer-center`
- **direction**: `footer-horizontal`, `footer-vertical`

### Syntax

```html
<footer class="footer bg-base-200 text-base-content p-4">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
    <a class="link link-hover">Marketing</a>
  </nav>
  <nav>
    <h6 class="footer-title">Company</h6>
    <a class="link link-hover">About us</a>
    <a class="link link-hover">Contact</a>
  </nav>
  <nav>
    <h6 class="footer-title">Legal</h6>
    <a class="link link-hover">Terms of use</a>
    <a class="link link-hover">Privacy policy</a>
  </nav>
</footer>
```

### Rules

- Use `sm:footer-horizontal` for responsive layout (vertical on mobile, horizontal on desktop)
- Convention: use `base-200` for background color

## Hero

Large featured section with optional overlay and content area.

### Class Names

- **component**: `hero`
- **part**: `hero-content`, `hero-overlay`

### Syntax

```html
<div class="hero min-h-screen" style="background-image: url(/bg.jpg);">
  <div class="hero-overlay bg-black/40"></div>
  <div class="hero-content text-neutral-content text-center">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold">Hello there</h1>
      <p class="py-6">Hero description text goes here.</p>
      <button class="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>
```

### Rules

- Use `hero-overlay` inside hero to darken background images
- Content goes in `hero-content`

## Indicator

Positions elements on the corner of another element (badges, notifications).

### Class Names

- **component**: `indicator`
- **part**: `indicator-item`
- **placement**: `indicator-start`, `indicator-center`, `indicator-end`, `indicator-top`, `indicator-middle`, `indicator-bottom`

### Syntax

```html
<div class="indicator">
  <span class="indicator-item badge badge-secondary">3</span>
  <div class="bg-base-100 w-32 h-32 rounded-box"></div>
</div>

<!-- Multiple indicators -->
<div class="indicator">
  <span class="indicator-item indicator-top indicator-start badge">New</span>
  <span class="indicator-item indicator-bottom indicator-end badge badge-error">!</span>
  <div class="bg-base-100 w-32 h-32 rounded-box"></div>
</div>
```

### Rules

- All `indicator-item` elements must come before the main content
- Default placement is `indicator-end indicator-top` (top-right corner)

## Join

Groups multiple items together, applying border radius to first and last child.

### Class Names

- **component**: `join`, `join-item`
- **direction**: `join-vertical`, `join-horizontal`

### Syntax

```html
<div class="join">
  <button class="join-item btn">One</button>
  <button class="join-item btn">Two</button>
  <button class="join-item btn">Three</button>
</div>

<!-- Join with input -->
<div class="join w-full">
  <input class="input join-item w-full" placeholder="Search..." />
  <button class="btn join-item btn-primary">Search</button>
</div>
```

### Rules

- Any direct child of `join` is grouped together
- Elements with `join-item` class are explicitly affected
- Use `lg:join-horizontal` for responsive layouts

## Mask

Crops element content to predefined shapes.

### Class Names

- **component**: `mask`
- **style**: `mask-squircle`, `mask-heart`, `mask-hexagon`, `mask-hexagon-2`, `mask-decagon`, `mask-pentagon`, `mask-diamond`, `mask-square`, `mask-circle`, `mask-star`, `mask-star-2`, `mask-triangle`, `mask-triangle-2`, `mask-triangle-3`, `mask-triangle-4`
- **modifier**: `mask-half-1`, `mask-half-2`

### Syntax

```html
<img class="mask mask-heart w-52" src="/image.jpg" alt="Heart shape" />
<img class="mask mask-star w-40" src="/image.jpg" alt="Star shape" />
<div class="mask mask-circle w-32 h-32 bg-primary"></div>
```

### Rules

- A style modifier is required (e.g., `mask-heart`, `mask-circle`)
- Works on any element, not just images
- Set custom sizes with `w-*` and `h-*`

## Stack

Visually layers elements on top of each other with offset.

### Class Names

- **component**: `stack`
- **modifier**: `stack-top`, `stack-bottom`, `stack-start`, `stack-end`

### Syntax

```html
<div class="stack">
  <div class="bg-base-300 w-64 h-64 rounded-box"></div>
  <div class="bg-base-100 w-64 h-64 rounded-box"></div>
  <div class="bg-primary w-64 h-64 rounded-box"></div>
</div>

<!-- Stack with avatars -->
<div class="stack stack-horizontal">
  <div class="avatar"><div class="w-12"><img src="/a.jpg" /></div></div>
  <div class="avatar"><div class="w-12"><img src="/b.jpg" /></div></div>
  <div class="avatar"><div class="w-12"><img src="/c.jpg" /></div></div>
</div>
```

### Rules

- Use `w-*` and `h-*` to make all items the same size for proper stacking
- Modifiers control which direction the stack layers from
