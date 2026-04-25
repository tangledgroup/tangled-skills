# Oat UI - Layout Components

Cards, grids, sidebars, and layout utilities.

## Cards

### Basic Card

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description or subtitle.</p>
  </header>
  
  <p>This is the card content. It can contain any HTML elements.</p>
  
  <footer class="hstack justify-end gap-2">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

### Card with Image

```html
<article class="card">
  <img src="/image.jpg" alt="Card image" style="width: 100%; border-radius: var(--radius-md) var(--radius-md) 0 0;" />
  
  <div style="padding: var(--space-4);">
    <h3>Article Title</h3>
    <p class="text-light">Published on January 15, 2024</p>
    <p>This is the article excerpt or summary.</p>
  </div>
  
  <footer style="padding: var(--space-4); border-top: 1px solid var(--border);">
    <button class="outline small">Read More</button>
  </footer>
</article>
```

### Card with Badge

```html
<article class="card">
  <header class="hstack justify-between items-start">
    <div>
      <h3>Task Title</h3>
      <p class="text-light">Due tomorrow</p>
    </div>
    <span class="badge warning">High Priority</span>
  </header>
  
  <p>Task description and details go here.</p>
</article>
```

### Interactive Card

```html
<article class="card" tabindex="0" style="cursor: pointer;">
  <header>
    <h3>Clickable Card</h3>
  </header>
  
  <p>This entire card is clickable and focusable.</p>
  
  <footer>
    <button>View Details</button>
  </footer>
</article>
```

## Grid System

### Basic Grid Layout

```html
<div class="container">
  <div class="row">
    <div class="col-4">4 columns</div>
    <div class="col-4">4 columns</div>
    <div class="col-4">4 columns</div>
  </div>
  
  <div class="row">
    <div class="col-6">6 columns</div>
    <div class="col-6">6 columns</div>
  </div>
  
  <div class="row">
    <div class="col-3">3 columns</div>
    <div class="col-6">6 columns</div>
    <div class="col-3">3 columns</div>
  </div>
</div>
```

### Grid with Gaps

```html
<div class="container">
  <div class="row" style="gap: var(--space-4);">
    <div class="col-4">
      <article class="card">Card 1</article>
    </div>
    <div class="col-4">
      <article class="card">Card 2</article>
    </div>
    <div class="col-4">
      <article class="card">Card 3</article>
    </div>
  </div>
</div>
```

### Grid with Offsets

```html
<div class="container">
  <div class="row">
    <div class="col-4 offset-4">Centered 4 columns</div>
  </div>
  
  <div class="row">
    <div class="col-3 offset-1">Offset by 1</div>
    <div class="col-6">6 columns</div>
  </div>
</div>
```

### Responsive Grid

```html
<div class="container">
  <div class="row">
    <div class="col-12 col-md-6 col-lg-4">
      <article class="card">Responsive Card</article>
    </div>
    <div class="col-12 col-md-6 col-lg-4">
      <article class="card">Responsive Card</article>
    </div>
    <div class="col-12 col-md-6 col-lg-4">
      <article class="card">Responsive Card</article>
    </div>
  </div>
</div>
```

```css
/* Add breakpoint classes */
@media (min-width: 768px) {
  .col-md-6 { flex: 0 0 50%; max-width: 50%; }
}

@media (min-width: 1024px) {
  .col-lg-4 { flex: 0 0 33.333%; max-width: 33.333%; }
}
```

## Sidebar Layout

### Basic Sidebar

```html
<body data-sidebar-layout>
  <aside data-sidebar>
    <nav>
      <ul>
        <li><a href="/" aria-current="page">Dashboard</a></li>
        <li><a href="/users">Users</a></li>
        <li><a href="/settings">Settings</a></li>
      </ul>
    </nav>
    
    <footer>
      <button class="outline" style="width: 100%;">Logout</button>
    </footer>
  </aside>
  
  <main>
    <div style="padding: var(--space-6);">
      <h1>Main Content</h1>
      <p>This content scrolls while sidebar stays fixed.</p>
    </div>
  </main>
</body>
```

### Sidebar with Nested Menu

```html
<aside data-sidebar>
  <header>
    <strong>My App</strong>
  </header>
  
  <nav>
    <ul>
      <li><a href="/">Dashboard</a></li>
      
      <li>
        <details open>
          <summary>Settings</summary>
          <ul>
            <li><a href="/settings/general">General</a></li>
            <li><a href="/settings/security">Security</a></li>
            <li><a href="/settings/billing">Billing</a></li>
          </ul>
        </details>
      </li>
      
      <li><a href="/help">Help</a></li>
    </ul>
  </nav>
  
  <footer>
    <button class="outline" style="width: 100%;">Logout</button>
  </footer>
</aside>
```

### Sidebar with Top Navigation

```html
<body data-sidebar-layout>
  <!-- Full-width top nav -->
  <nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3) var(--space-4);">
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <strong>App Name</strong>
    <figure data-variant="avatar" aria-label="User">
      <img src="/avatar.svg" alt="" />
    </figure>
  </nav>
  
  <aside data-sidebar>
    <!-- Sidebar content -->
  </aside>
  
  <main>
    <!-- Main content -->
  </main>
</body>
```

### Always-Collapsible Sidebar

```html
<body data-sidebar-layout="always">
  <nav data-topnav>
    <button data-sidebar-toggle>☰</button>
    <span>App Name</span>
  </nav>
  
  <aside data-sidebar>
    <!-- Sidebar always collapsible -->
  </aside>
  
  <main>
    <!-- Content -->
  </main>
</body>
```

The toggle button remains visible on all screen sizes.

## Container and Row

### Max Width Containers

```html
<div class="container">
  <!-- Content maxed at 1200px -->
</div>

<div class="container-fluid">
  <!-- Full width with padding -->
</div>
```

### Row Spacing

```html
<div class="row" style="gap: var(--space-4);">
  <div class="col-6">Column 1</div>
  <div class="col-6">Column 2</div>
</div>
```

## Stack Utilities

### Horizontal Stack (Flex Row)

```html
<div class="hstack gap-2">
  <button>Cancel</button>
  <button>Save</button>
</div>

<div class="hstack justify-between items-center">
  <h3>Title</h3>
  <button class="outline small">Edit</button>
</div>
```

### Vertical Stack (Flex Column)

```html
<div class="vstack gap-3">
  <label data-field><input type="text" /></label>
  <label data-field><input type="email" /></label>
  <label data-field><input type="password" /></label>
</div>
```

### Stack Alignment

```html
<div class="hstack items-center gap-2">
  <!-- Vertically centered -->
</div>

<div class="hstack justify-center">
  <!-- Horizontally centered -->
</div>

<div class="hstack justify-between">
  <!-- Space between -->
</div>

<div class="hstack justify-end">
  <!-- Right aligned -->
</div>
```

## Spacing Utilities

### Margin

```html
<div class="mt-4">Margin top: 16px</div>
<div class="mb-8">Margin bottom: 32px</div>
<div class="mx-4">Margin horizontal: 16px</div>
<div class="my-2">Margin vertical: 8px</div>
```

### Padding

```html
<div class="p-4">Padding all: 16px</div>
<div class="px-6">Padding horizontal: 24px</div>
<div class="py-3">Padding vertical: 12px</div>
<div class="pt-8">Padding top: 32px</div>
```

### Gap

```html
<div class="hstack gap-2">Gap: 8px</div>
<div class="vstack gap-4">Gap: 16px</div>
```

## Width and Height

```html
<div class="w-full">Width: 100%</div>
<div class="w-auto">Width: auto</div>
<div class="min-w-0">Min-width: 0</div>
<div class="max-w-screen">Max-width: screen</div>

<div class="h-full">Height: 100%</div>
<div class="h-screen">Height: 100vh</div>
```

## Common Layout Patterns

### Dashboard Grid

```html
<div class="container">
  <!-- Stats row -->
  <div class="row" style="gap: var(--space-4); margin-bottom: var(--space-6);">
    <div class="col-4">
      <article class="card">
        <h4>Revenue</h4>
        <h2>$42,200</h2>
      </article>
    </div>
    <div class="col-4">
      <article class="card">
        <h4>Users</h4>
        <h2>1,234</h2>
      </article>
    </div>
    <div class="col-4">
      <article class="card">
        <h4>Tickets</h4>
        <h2>14</h2>
      </article>
    </div>
  </div>
  
  <!-- Main content -->
  <div class="row" style="gap: var(--space-4);">
    <div class="col-8">
      <article class="card">
        <header><h3>Recent Activity</h3></header>
        <!-- Content -->
      </article>
    </div>
    <div class="col-4">
      <article class="card">
        <header><h3>Notifications</h3></header>
        <!-- Content -->
      </article>
    </div>
  </div>
</div>
```

### Profile Page Layout

```html
<div class="container">
  <div class="row" style="gap: var(--space-6);">
    <!-- Sidebar with profile info -->
    <div class="col-4">
      <article class="card align-center">
        <figure data-variant="avatar" class="large" style="margin-bottom: var(--space-3);">
          <img src="/avatar.jpg" alt="Profile" />
        </figure>
        <h3>John Doe</h3>
        <p class="text-light">john@example.com</p>
      </article>
    </div>
    
    <!-- Main content with tabs -->
    <div class="col-8">
      <ot-tabs>
        <div role="tablist">
          <button role="tab">Posts</button>
          <button role="tab">About</button>
          <button role="tab">Photos</button>
        </div>
        
        <div role="tabpanel"><!-- Posts --></div>
        <div role="tabpanel"><!-- About --></div>
        <div role="tabpanel"><!-- Photos --></div>
      </ot-tabs>
    </div>
  </div>
</div>
```

### Form in Card

```html
<article class="card" style="max-width: 500px;">
  <header>
    <h3>Login</h3>
    <p class="text-light">Sign in to your account</p>
  </header>
  
  <div class="mt-4">
    <label data-field>
      Email
      <input type="email" />
    </label>
    
    <label data-field>
      Password
      <input type="password" />
    </label>
  </div>
  
  <footer class="mt-4">
    <button style="width: 100%;">Sign In</button>
  </footer>
</article>
```

## Responsive Behavior

### Mobile-First Sidebar

Sidebar automatically becomes slide-out overlay on mobile devices. Add `data-sidebar-toggle` button to control it.

### Stack on Mobile

Grid columns stack vertically on small screens by default.

```css
/* Default: stacked on mobile */
.col-* { flex: 0 0 100%; max-width: 100%; }

/* Tablet and up */
@media (min-width: 768px) {
  .col-6 { flex: 0 0 50%; max-width: 50%; }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .col-4 { flex: 0 0 33.333%; max-width: 33.333%; }
}
```
