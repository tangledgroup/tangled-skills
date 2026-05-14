# Navigation Components

## Breadcrumbs

Navigation trail showing the current page location within a hierarchy.

### Class Names

- **component**: `breadcrumbs`

### Syntax

```html
<div class="breadcrumbs text-sm">
  <ul>
    <li><a>Home</a></li>
    <li><a>Products</a></li>
    <li>Current Page</li>
  </ul>
</div>
```

### Rules

- Can contain icons inside links
- Scrolls horizontally when list exceeds container width (set `max-width`)

## Dock

Bottom navigation bar that sticks to the bottom of the screen.

### Class Names

- **component**: `dock`
- **part**: `dock-label`
- **modifier**: `dock-active`
- **size**: `dock-xs`, `dock-sm`, `dock-md`, `dock-lg`, `dock-xl`

### Syntax

```html
<div class="dock dock-lg">
  <button class="dock-active">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
    <span class="dock-label">Home</span>
  </button>
  <button>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
    <span class="dock-label">Settings</span>
  </button>
</div>
```

### Rules

- Add `<meta name="viewport" content="viewport-fit=cover">` for iOS responsiveness
- Use `dock-active` on the currently selected button

## Link

Adds underline styling to anchor elements.

### Class Names

- **component**: `link`
- **style**: `link-hover`
- **color**: `link-neutral`, `link-primary`, `link-secondary`, `link-accent`, `link-success`, `link-info`, `link-warning`, `link-error`

### Syntax

```html
<a href="/page" class="link link-primary">Click here</a>
<a href="/page" class="link link-hover">Hover to see underline</a>
```

## Menu

Vertical or horizontal list of navigation links.

### Class Names

- **component**: `menu`
- **part**: `menu-title`, `menu-dropdown`, `menu-dropdown-toggle`
- **modifier**: `menu-disabled`, `menu-active`, `menu-focus`, `menu-dropdown-show`
- **size**: `menu-xs`, `menu-sm`, `menu-md`, `menu-lg`, `menu-xl`
- **direction**: `menu-vertical`, `menu-horizontal`

### Syntax

Vertical menu:

```html
<ul class="menu bg-base-200 w-80 p-4">
  <li><details>
    <summary>Parent</summary>
    <ul>
      <li><a>Child 1</a></li>
      <li><a>Child 2</a></li>
    </ul>
  </details></li>
  <li><a class="menu-active">Active Item</a></li>
  <li><a>Another Item</a></li>
</ul>
```

Horizontal menu:

```html
<ul class="menu menu-horizontal bg-base-200 p-4">
  <li><a>Home</a></li>
  <li><a>About</a></li>
  <li><a>Contact</a></li>
</ul>
```

### Rules

- Use `lg:menu-horizontal` for responsive horizontal layout on larger screens
- `<details>` tags create collapsible submenus
- `menu-title` for section headers within the menu

## Navbar

Top navigation bar with start, center, and end sections.

### Class Names

- **component**: `navbar`
- **part**: `navbar-start`, `navbar-center`, `navbar-end`

### Syntax

```html
<div class="navbar bg-base-100 shadow-sm">
  <div class="navbar-start">
    <a class="btn btn-ghost text-xl">Logo</a>
  </div>
  <div class="navbar-center">
    <a class="link link-hover">Center Link</a>
  </div>
  <div class="navbar-end">
    <button class="btn btn-ghost btn-circle">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
    </button>
  </div>
</div>
```

### Rules

- Use `base-200` for background color as a convention
- Any content can go inside each section

## Pagination

Page navigation using grouped buttons. Built on the Join component.

### Class Names

Uses `join` and `join-item` classes (see Join component).

### Syntax

```html
<div class="join">
  <button class="join-item btn">«</button>
  <button class="join-item btn">1</button>
  <button class="join-item btn btn-active">2</button>
  <button class="join-item btn">3</button>
  <button class="join-item btn">»</button>
</div>
```

## Steps

Visual process stepper showing sequential stages.

### Class Names

- **component**: `steps`
- **part**: `step`, `step-icon`
- **color**: `step-neutral`, `step-primary`, `step-secondary`, `step-accent`, `step-info`, `step-success`, `step-warning`, `step-error`
- **direction**: `steps-vertical`, `steps-horizontal`

### Syntax

```html
<ul class="steps steps-horizontal w-full">
  <li class="step step-primary" data-content="✓">Account</li>
  <li class="step step-primary" data-content="✓">Personal</li>
  <li class="step step-primary">Address</li>
  <li>Reviews</li>
</ul>
```

### Rules

- Add `step-primary` (or other color) to mark a step as active/completed
- Use `data-content="{value}"` on `<li>` to display custom content in the step indicator
- Add icons with `step-icon` class inside steps

## Tab

Tabbed navigation interface.

### Class Names

- **component**: `tabs`
- **part**: `tab`, `tab-content`
- **style**: `tabs-box`, `tabs-border`, `tabs-lift`
- **modifier**: `tab-active`, `tab-disabled`
- **placement**: `tabs-top`, `tabs-bottom`

### Syntax

Using buttons:

```html
<div role="tablist" class="tabs tabs-bordered">
  <button role="tab" class="tab tab-active">Tab 1</button>
  <button role="tab" class="tab">Tab 2</button>
  <button role="tab" class="tab tab-disabled">Tab 3</button>
</div>
```

Using radio inputs (enables tab content panels):

```html
<div role="tablist" class="tabs tabs-boxed">
  <input type="radio" name="my_tabs" class="tab tab-active" aria-label="Tab 1" checked />
  <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-6">Content 1</div>
  <input type="radio" name="my_tabs" class="tab" aria-label="Tab 2" />
  <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-6">Content 2</div>
</div>
```

### Rules

- Radio inputs enable click-to-switch tab content panels
- If tabs have a background, every tab gets rounded top corners
