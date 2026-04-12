# Oat UI - Navigation Components

Breadcrumbs, pagination, and navigation patterns.

## Breadcrumbs

### Basic Breadcrumb

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-2);">
    <li><a href="/" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="/products" class="unstyled">Products</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="/products/widgets" class="unstyled">Widgets</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="/products/widgets/premium" class="unstyled" aria-current="page"><strong>Premium</strong></a></li>
  </ol>
</nav>
```

### Breadcrumb with Icons

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-2);">
    <li>
      <a href="/" class="unstyled hstack items-center gap-1">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        Home
      </a>
    </li>
    <li aria-hidden="true">›</li>
    <li><a href="/docs" class="unstyled">Docs</a></li>
    <li aria-hidden="true">›</li>
    <li><span aria-current="page"><strong>Getting Started</strong></span></li>
  </ol>
</nav>
```

## Pagination

### Basic Pagination

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="?page=1" class="button outline small">&larr; Previous</a></li>
    <li><a href="?page=1" class="button outline small">1</a></li>
    <li><a href="?page=2" class="button outline small">2</a></li>
    <li><a href="?page=3" class="button small" aria-current="page">3</a></li>
    <li><a href="?page=4" class="button outline small">4</a></li>
    <li><a href="?page=5" class="button outline small">5</a></li>
    <li><a href="?page=4" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

### Pagination with Page Count

```html
<nav aria-label="Pagination" class="hstack justify-between items-center">
  <p class="text-light small">Showing 21-40 of 125 results</p>
  
  <menu class="buttons">
    <li><a href="?page=1" class="button outline small">First</a></li>
    <li><a href="?page=2" class="button outline small">&larr;</a></li>
    <li><a href="?page=3" class="button small" aria-current="page">3</a></li>
    <li><a href="?page=4" class="button outline small">&rarr;</a></li>
    <li><a href="?page=7" class="button outline small">Last</a></li>
  </menu>
</nav>
```

### Simplified Pagination

```html
<nav aria-label="Pagination" class="hstack justify-between items-center">
  <a href="?page=2" class="button outline small">&larr; Previous</a>
  <span class="text-light">Page 3 of 10</span>
  <a href="?page=4" class="button outline small">Next &rarr;</a>
</nav>
```

## Tab Navigation

See [`references/08-dropdowns-tabs.md`](references/08-dropdowns-tabs.md) for detailed tab component documentation.

## Sidebar Navigation

See [`references/09-layout-components.md`](references/09-layout-components.md) for sidebar navigation patterns.

## Top Navigation Bar

### Basic Top Nav

```html
<nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3) var(--space-4);">
  <a href="/" class="unstyled">
    <strong style="font-size: var(--text-5);">App Name</strong>
  </a>
  
  <ul class="hstack unstyled" style="gap: var(--space-4);">
    <li><a href="/features" class="unstyled">Features</a></li>
    <li><a href="/pricing" class="unstyled">Pricing</a></li>
    <li><a href="/about" class="unstyled">About</a></li>
  </ul>
  
  <div class="hstack gap-2">
    <a href="/login" class="button outline small">Login</a>
    <a href="/signup" class="button small">Sign Up</a>
  </div>
</nav>
```

### Top Nav with Dropdown

```html
<nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3) var(--space-4);">
  <strong>App Name</strong>
  
  <div class="hstack gap-4">
    <ot-dropdown>
      <button popovertarget="products-menu" class="unstyled">Products ▾</button>
      <menu popover id="products-menu">
        <button role="menuitem">Product A</button>
        <button role="menuitem">Product B</button>
        <button role="menuitem">Product C</button>
      </menu>
    </ot-dropdown>
    
    <a href="/docs" class="unstyled">Docs</a>
    <a href="/pricing" class="unstyled">Pricing</a>
  </div>
  
  <figure data-variant="avatar" aria-label="User menu">
    <img src="/avatar.jpg" alt="" />
  </figure>
</nav>
```

### Responsive Mobile Nav

```html
<nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3) var(--space-4);">
  <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
  
  <strong>App Name</strong>
  
  <!-- Hidden on mobile, shown in sidebar -->
  <div class="hidden-mobile hstack gap-4">
    <a href="/features" class="unstyled">Features</a>
    <a href="/pricing" class="unstyled">Pricing</a>
  </div>
  
  <figure data-variant="avatar" aria-label="User">
    <img src="/avatar.jpg" alt="" />
  </figure>
</nav>

<aside data-sidebar>
  <nav>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/features">Features</a></li>
      <li><a href="/pricing">Pricing</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
</aside>

<style>
@media (min-width: 768px) {
  .hidden-mobile { display: flex; }
}
@media (max-width: 767px) {
  .hidden-mobile { display: none; }
}
</style>
```

## Stepper/Progress Navigation

### Basic Stepper

```html
<ol class="unstyled hstack" style="counter-reset: step;">
  <li class="hstack items-center gap-2" style="counter-increment: step;">
    <span style="background: var(--primary); color: var(--primary-foreground); width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: var(--text-2);">1</span>
    <strong>Account</strong>
  </li>
  <span>→</span>
  <li class="hstack items-center gap-2" style="opacity: 0.6;">
    <span style="background: var(--border); color: var(--foreground); width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: var(--text-2);">2</span>
    <span>Details</span>
  </li>
  <span>→</span>
  <li class="hstack items-center gap-2" style="opacity: 0.6;">
    <span style="background: var(--border); color: var(--foreground); width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: var(--text-2);">3</span>
    <span>Review</span>
  </li>
</ol>
```

### Stepper with Status

```html
<div class="vstack gap-4" style="max-width: 500px;">
  <!-- Step 1: Complete -->
  <div class="hstack gap-3">
    <div style="color: var(--success);">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    </div>
    <div style="flex: 1;">
      <strong>Account Information</strong>
      <p class="text-light small">Completed</p>
    </div>
  </div>
  
  <!-- Step 2: Current -->
  <div class="hstack gap-3">
    <div style="background: var(--primary); color: var(--primary-foreground); width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">2</div>
    <div style="flex: 1;">
      <strong>Shipping Details</strong>
      <p class="text-light small">Current step</p>
    </div>
  </div>
  
  <!-- Step 3: Pending -->
  <div class="hstack gap-3" style="opacity: 0.6;">
    <div style="background: var(--border); color: var(--foreground); width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">3</div>
    <div style="flex: 1;">
      <strong>Review & Confirm</strong>
      <p class="text-light small">Pending</p>
    </div>
  </div>
</div>
```

## Navigation Patterns

### Card-Based Navigation

```html
<div class="grid">
  <div class="col-4">
    <article class="card" style="cursor: pointer; text-align: center; padding: var(--space-6);">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="margin-bottom: var(--space-3);">
        <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
      </svg>
      <h4>Dashboard</h4>
      <p class="text-light">View your overview</p>
    </article>
  </div>
  
  <div class="col-4">
    <article class="card" style="cursor: pointer; text-align: center; padding: var(--space-6);">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="margin-bottom: var(--space-3);">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
      <h4>Users</h4>
      <p class="text-light">Manage users</p>
    </article>
  </div>
  
  <div class="col-4">
    <article class="card" style="cursor: pointer; text-align: center; padding: var(--space-6);">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="margin-bottom: var(--space-3);">
        <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21"/>
      </svg>
      <h4>Settings</h4>
      <p class="text-light">Configure app</p>
    </article>
  </div>
</div>
```

### Quick Actions Bar

```html
<div class="hstack gap-2" style="padding: var(--space-3); background: var(--card); border-radius: var(--radius-md); box-shadow: var(--shadow-sm);">
  <button class="small hstack items-center gap-1">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
    New Item
  </button>
  <button class="outline small">Export</button>
  <button class="outline small">Import</button>
  <div style="flex: 1;"></div>
  <button class="outline small">View All</button>
</div>
```

## Accessibility

### Current Page Indication

```html
<li><a href="/current" aria-current="page">Current Page</a></li>
```

### Keyboard Navigation

All navigation elements should be focusable and navigable with Tab key.

### Skip Links

```html
<a href="#main-content" class="skip-link" style="position: absolute; top: -40px; left: 0; padding: var(--space-2); background: var(--primary); color: var(--primary-foreground);">Skip to main content</a>

<main id="main-content">
  <!-- Content -->
</main>

<style>
.skip-link:focus {
  top: var(--space-2);
}
</style>
```

## Best Practices

### Breadcrumbs

- DO place near top of page
- DO make last item non-link (current page)
- DON'T show on homepage
- DON't make too deep (max 5-6 levels)

### Pagination

- DO show context ("Page 3 of 10")
- DO highlight current page
- DON'T show too many page numbers (use ellipsis)
- DON't require pagination for < 20 items

### Navigation Consistency

- DO keep nav in same position across pages
- DO indicate current section
- DO use clear, descriptive labels
- DON't hide primary navigation
