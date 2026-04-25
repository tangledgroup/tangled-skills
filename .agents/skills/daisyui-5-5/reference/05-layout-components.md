# DaisyUI Layout Components

This guide covers layout components in DaisyUI 5.5 including navbar, footer, drawer, hero, and other structural elements.

## Navbar

### Basic Navbar

```html
<div class="navbar bg-base-100">
  <div class="navbar-start">
    <div class="dropdown">
      <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
        </svg>
      </div>
      <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
        <li><a>Home</a></li>
        <li><a>About</a></li>
        <li><a>Contact</a></li>
      </ul>
    </div>
    <a class="btn btn-ghost text-xl">Logo</a>
  </div>
  
  <div class="navbar-center hidden lg:flex">
    <ul class="menu menu-horizontal px-1">
      <li><a>Home</a></li>
      <li><a>About</a></li>
      <li><a>Contact</a></li>
    </ul>
  </div>
  
  <div class="navbar-end">
    <button class="btn btn-primary">Sign Up</button>
  </div>
</div>
```

### Navbar Sections

```html
<div class="navbar">
  <!-- Left side -->
  <div class="navbar-start">
    <a class="btn btn-ghost text-xl">Brand</a>
  </div>
  
  <!-- Center -->
  <div class="navbar-center">
    <ul class="menu menu-horizontal">
      <li><a>Link 1</a></li>
      <li><a>Link 2</a></li>
    </ul>
  </div>
  
  <!-- Right side -->
  <div class="navbar-end">
    <button class="btn">Action</button>
  </div>
</div>
```

### Navbar with Search

```html
<div class="navbar bg-base-100">
  <div class="navbar-start">
    <a class="btn btn-ghost text-xl">Brand</a>
  </div>
  
  <div class="navbar-center">
    <div class="form-control">
      <input type="text" placeholder="Search" class="input input-bordered w-24 md:w-auto" />
    </div>
  </div>
  
  <div class="navbar-end">
    <button class="btn">Login</button>
  </div>
</div>
```

### Sticky Navbar

```html
<div class="navbar bg-base-100 sticky top-0 z-50 shadow-sm">
  <div class="navbar-start">
    <a class="btn btn-ghost text-xl">Brand</a>
  </div>
  <div class="navbar-end">
    <button class="btn">Action</button>
  </div>
</div>
```

## Footer

### Basic Footer

```html
<footer class="footer p-10 bg-neutral text-neutral-content">
  <nav>
    <h6 class="footer-title">Services</h6> 
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
    <a class="link link-hover">Marketing</a>
    <a class="link link-hover">Advertisement</a>
  </nav>
  
  <nav>
    <h6 class="footer-title">Company</h6>
    <a class="link link-hover">About us</a>
    <a class="link link-hover">Contact</a>
    <a class="link link-hover">Jobs</a>
    <a class="link link-hover">Press kit</a>
  </nav>
  
  <nav>
    <h6 class="footer-title">Legal</h6>
    <a class="link link-hover">Terms of use</a>
    <a class="link link-hover">Privacy policy</a>
    <a class="link link-hover">Cookie policy</a>
  </nav>
  
  <nav>
    <h6 class="footer-title">Social</h6>
    <div class="grid grid-flow-col gap-4">
      <a class="link link-hover">Twitter</a>
      <a class="link link-hover">Instagram</a>
      <a class="link link-hover">Facebook</a>
    </div>
  </nav>
</footer>
```

### Simple Footer

```html
<footer class="footer items-center p-4 bg-base-300 text-base-content">
  <aside class="items-center grid-flow-col">
    <p>Copyright © 2024 - All right reserved by Example Corp.</p>
  </aside>
  
  <nav class="netwrokss items-center grid-flow-col gap-4">
    <a class="link link-hover">About us</a>
    <a class="link link-hover">Contact</a>
    <a class="link link-hover">Terms of Use</a>
  </nav>
</footer>
```

### Footer with Logo

```html
<footer class="footer footer-center p-10 bg-base-200 text-base-content rounded-t-xl">
  <aside>
    <p>Copyright © 2024 - All right reserved by Example Corp.</p>
  </aside>
</footer>
```

### Footer Modifiers

```html
<!-- Vertical footer -->
<footer class="footer footer-vertical">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a>Branding</a>
    <a>Design</a>
  </nav>
</footer>

<!-- Horizontal footer (default) -->
<footer class="footer footer-horizontal">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a>Branding</a>
  </nav>
</footer>

<!-- Centered footer -->
<footer class="footer footer-center">
  <p>Centered content</p>
</footer>
```

### Responsive Footer

```html
<footer class="footer p-10 bg-neutral text-neutral-content sm:footer-horizontal">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
  </nav>
  
  <nav>
    <h6 class="footer-title">Company</h6>
    <a class="link link-hover">About</a>
    <a class="link link-hover">Contact</a>
  </nav>
</footer>
```

## Drawer (Sidebar)

### Basic Drawer

```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  
  <!-- Main content -->
  <div class="drawer-content flex flex-col">
    <navbar>Navbar content</navbar>
    <main class="flex-1">Page content</main>
    <footer>Footer content</footer>
  </div>
  
  <!-- Sidebar -->
  <div class="drawer-side">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label> 
    <ul class="menu p-4 w-64 min-h-full bg-base-200 text-base-content">
      <li><a>🏠 Home</a></li>
      <li><a>⚙️ Settings</a></li>
      <li><a>👤 Profile</a></li>
    </ul>
  </div>
</div>
```

### Drawer Toggle Button

```html
<div class="drawer">
  <input id="drawer" type="checkbox" class="drawer-toggle" />
  
  <div class="drawer-content flex flex-col">
    <div class="w-full navbar bg-base-100">
      <div class="flex-none lg:hidden">
        <label for="drawer" aria-label="open sidebar" class="btn btn-square btn-ghost">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </label>
      </div>
      <div class="flex-1 px-2 mx-2">
        <span class="text-xl font-bold">Brand</span>
      </div>
    </div>
    
    <main class="flex-1">Content</main>
  </div>
  
  <div class="drawer-side">
    <label for="drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-64 min-h-full bg-base-200 text-base-content">
      <li><a>Home</a></li>
      <li><a>About</a></li>
      <li><a>Contact</a></li>
    </ul>
  </div>
</div>
```

### Always Visible Sidebar (Desktop)

```html
<div class="drawer lg:drawer-open">
  <input id="sidebar" type="checkbox" class="drawer-toggle" />
  
  <div class="drawer-content flex flex-col">
    <main class="flex-1 p-4">Main content</main>
  </div>
  
  <div class="drawer-side">
    <label for="sidebar" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-64 min-h-full bg-base-200 text-base-content">
      <li><a>Home</a></li>
      <li><a>Settings</a></li>
    </ul>
  </div>
</div>
```

### Collapsible Sidebar with Icons

```html
<div class="drawer lg:drawer-open">
  <input id="collapsible-sidebar" type="checkbox" class="drawer-toggle" />
  
  <div class="drawer-content flex flex-col">
    <main class="flex-1 p-4">Content</main>
  </div>
  
  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="collapsible-sidebar" aria-label="close sidebar" class="drawer-overlay"></label>
    
    <div class="is-drawer-close:w-20 is-drawer-open:w-64 bg-base-200 text-base-content flex flex-col items-start min-h-full p-4">
      <ul class="menu w-full">
        <li>
          <a>
            🏠
            <span class="is-drawer-close:hidden">Home</span>
          </a>
        </li>
        <li>
          <a>
            ⚙️
            <span class="is-drawer-close:hidden">Settings</span>
          </a>
        </li>
        <li>
          <a>
            👤
            <span class="is-drawer-close:hidden">Profile</span>
          </a>
        </li>
      </ul>
      
      <!-- Toggle button -->
      <div class="mt-auto p-2">
        <label for="collapsible-sidebar" class="btn btn-sm is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Toggle sidebar">
          ↔️
        </label>
      </div>
    </div>
  </div>
</div>
```

### Drawer Placement

```html
<!-- Left sidebar (default) -->
<div class="drawer">
  <input type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">Content</div>
  <div class="drawer-side">Sidebar</div>
</div>

<!-- Right sidebar -->
<div class="drawer drawer-end">
  <input type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">Content</div>
  <div class="drawer-side">Sidebar</div>
</div>
```

### Drawer States

```html
<!-- Always open -->
<div class="drawer drawer-open">
  <input type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">Content</div>
  <div class="drawer-side">Sidebar</div>
</div>

<!-- Responsive: open on large screens -->
<div class="drawer lg:drawer-open">
  <input type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">Content</div>
  <div class="drawer-side">Sidebar</div>
</div>
```

## Hero

### Basic Hero

```html
<div class="hero min-h-screen bg-base-200">
  <div class="hero-content text-center">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold">Hello!</h1>
      <p class="py-6">Welcome to our website. We create beautiful interfaces with DaisyUI.</p>
      <button class="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>
```

### Hero with Background Image

```html
<div class="hero min-h-screen">
  <div class="hero-overlay bg-opacity-60"></div>
  <img src="https://picsum.photos/1920/1080" alt="Background" class="absolute inset-0 w-full h-full object-cover" />
  
  <div class="hero-content text-center text-neutral-content">
    <div class="max-w-md">
      <h1 class="mb-5 text-5xl font-bold">Hero Title</h1>
      <p class="mb-5">This is a hero with a background image and overlay.</p>
      <button class="btn btn-primary">Call to Action</button>
    </div>
  </div>
</div>
```

### Hero with Gradient

```html
<div class="hero min-h-screen bg-gradient-to-b from-primary to-secondary">
  <div class="hero-content text-center text-neutral-content">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold">Gradient Hero</h1>
      <p class="py-6">Beautiful gradient background.</p>
      <button class="btn btn-outline">Learn More</button>
    </div>
  </div>
</div>
```

### Hero with Card

```html
<div class="hero min-h-screen bg-base-200">
  <div class="hero-content flex-col lg:flex-row-reverse">
    <img src="https://picsum.photos/600/400" alt="Product" class="max-w-sm rounded-lg shadow-2xl" />
    
    <div class="text-left">
      <h1 class="text-5xl font-bold">Product Name</h1>
      <p class="py-6">Discover amazing features that will transform your workflow.</p>
      <button class="btn btn-primary">Learn More</button>
    </div>
  </div>
</div>
```

### Full Screen Hero

```html
<div class="hero min-h-screen bg-base-300">
  <div class="hero-content text-center">
    <div class="max-w-2xl">
      <h1 class="text-6xl font-bold mb-4">Big Title</h1>
      <p class="text-xl mb-8">This is a paragraph describing the big title above.</p>
      <div class="space-x-4">
        <button class="btn btn-primary btn-lg">Primary Action</button>
        <button class="btn btn-outline btn-lg">Secondary</button>
      </div>
    </div>
  </div>
</div>
```

## Container

### Basic Container

```html
<div class="container mx-auto px-4">
  <div class="hero min-h-screen">
    <div class="hero-content">
      <h1>Container Content</h1>
    </div>
  </div>
</div>
```

### Responsive Container

```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <!-- Content -->
</div>
```

## Breadcrumbs

### Basic Breadcrumbs

```html
<ul class="breadcrumbs">
  <li><a>Home</a></li>
  <li><a>Products</a></li>
  <li><a class="text-primary">Item Name</a></li>
</ul>
```

### Breadcrumbs with Icons

```html
<ul class="breadcrumbs">
  <li>
    <a>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    </a>
  </li>
  <li><a>Products</a></li>
  <li>Item Name</li>
</ul>
```

### Breadcrumbs with Separator

```html
<ul class="breadcrumbs">
  <li><a>Home</a></li>
  <li><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></li>
  <li>Products</li>
</ul>
```

## Pagination

### Basic Pagination

```html
<div class="join">
  <button class="join-item btn btn-sm">←</button>
  <button class="join-item btn btn-sm btn-active">1</button>
  <button class="join-item btn btn-sm">2</button>
  <button class="join-item btn btn-sm">3</button>
  <button class="join-item btn btn-sm">→</button>
</div>
```

### Pagination with Links

```html
<div class="join">
  <a class="join-item btn btn-sm">←</a>
  <a class="join-item btn btn-sm btn-active">1</a>
  <a class="join-item btn btn-sm">2</a>
  <a class="join-item btn btn-sm">3</a>
  <a class="join-item btn btn-sm">→</a>
</div>
```

### Vertical Pagination

```html
<div class="join join-vertical">
  <button class="join-item btn">↑</button>
  <button class="join-item btn btn-active">1</button>
  <button class="join-item btn">2</button>
  <button class="join-item btn">3</button>
  <button class="join-item btn">↓</button>
</div>
```

## Divider

### Basic Divider

```html
<div class="divider">TEXT</div>
```

### Divider without Text

```html
<div class="divider"></div>
```

### Divider Colors

```html
<div class="divider divider-primary">Primary</div>
<div class="divider divider-secondary">Secondary</div>
<div class="divider divider-accent">Accent</div>
<div class="divider divider-success">Success</div>
```

### Divider Placement

```html
<!-- Text start -->
<div class="divider divider-start">Start</div>

<!-- Text center (default) -->
<div class="divider divider-center">Center</div>

<!-- Text end -->
<div class="divider divider-end">End</div>
```

### Vertical Divider

```html
<div class="flex gap-4">
  <div>Content 1</div>
  <div class="divider divider-vertical"></div>
  <div>Content 2</div>
</div>
```

## Stack

### Basic Stack

```html
<div class="stack">
  <button class="btn btn-primary">Button 1</button>
  <button class="btn btn-secondary">Button 2</button>
  <button class="btn btn-accent">Button 3</button>
</div>
```

### Stack Placement

```html
<!-- Top -->
<div class="stack stack-top">
  <div>Top item</div>
  <div>Bottom item</div>
</div>

<!-- Bottom -->
<div class="stack stack-bottom">
  <div>Bottom item</div>
  <div>Top item</div>
</div>

<!-- Start (left) -->
<div class="stack stack-start">
  <div>Left item</div>
  <div>Right item</div>
</div>

<!-- End (right) -->
<div class="stack stack-end">
  <div>Right item</div>
  <div>Left item</div>
</div>
```

## Layout Best Practices

1. **Use semantic HTML** - `<nav>` for navigation, `<main>` for content, `<footer>` for footer
2. **Make layouts responsive** - Use Tailwind breakpoints (`sm:`, `md:`, `lg:`)
3. **Ensure keyboard navigation** - All interactive elements should be focusable
4. **Provide skip links** - Allow keyboard users to skip to main content
5. **Test on multiple devices** - Verify layout works on mobile, tablet, and desktop
6. **Use proper heading hierarchy** - H1 for page title, H2-H6 for sections
7. **Consider accessibility** - Use ARIA labels for icon-only buttons

## Common Layout Patterns

### Full Page Layout

```html
<div class="drawer lg:drawer-open">
  <input id="sidebar" type="checkbox" class="drawer-toggle" />
  
  <div class="drawer-content flex flex-col">
    <!-- Navbar -->
    <div class="navbar bg-base-100 shadow-sm">
      <div class="navbar-start">
        <label for="sidebar" class="btn btn-ghost lg:hidden">☰</label>
        <a class="btn btn-ghost text-xl">Brand</a>
      </div>
      <div class="navbar-end">
        <button class="btn btn-primary">Login</button>
      </div>
    </div>
    
    <!-- Breadcrumbs -->
    <div class="bg-base-200 p-4">
      <ul class="breadcrumbs">
        <li><a>Home</a></li>
        <li>Current Page</li>
      </ul>
    </div>
    
    <!-- Main Content -->
    <main class="flex-1 container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-4">Page Title</h1>
      <p>Page content goes here.</p>
    </main>
    
    <!-- Footer -->
    <footer class="footer p-10 bg-base-300 text-base-content">
      <nav>
        <h6 class="footer-title">Links</h6>
        <a class="link">About</a>
        <a class="link">Contact</a>
      </nav>
    </footer>
  </div>
  
  <!-- Sidebar -->
  <div class="drawer-side">
    <label for="sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-64 min-h-full bg-base-100 text-base-content">
      <li><a>🏠 Home</a></li>
      <li><a>⚙️ Settings</a></li>
      <li><a>👤 Profile</a></li>
    </ul>
  </div>
</div>
```

### Dashboard Layout

```html
<div class="flex h-screen bg-base-200">
  <!-- Sidebar -->
  <aside class="w-64 bg-base-100 hidden lg:block">
    <div class="p-4">
      <h1 class="text-xl font-bold">Dashboard</h1>
    </div>
    <ul class="menu p-4">
      <li><a class="menu-active">📊 Overview</a></li>
      <li><a>👥 Users</a></li>
      <li><a>⚙️ Settings</a></li>
    </ul>
  </aside>
  
  <!-- Main Content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Top bar -->
    <header class="navbar bg-base-100 shadow-sm">
      <div class="navbar-end">
        <button class="btn btn-ghost lg:hidden">☰</button>
        <div class="avatar">
          <div class="w-8 rounded-full">
            <img src="https://picsum.photos/40" alt="User" />
          </div>
        </div>
      </div>
    </header>
    
    <!-- Content -->
    <main class="flex-1 overflow-y-auto p-6">
      <h1 class="text-2xl font-bold mb-4">Overview</h1>
      
      <!-- Stats -->
      <div class="stats shadow w-full mb-6">
        <div class="stat">
          <div class="stat-title">Total Users</div>
          <div class="stat-value">1,234</div>
        </div>
        <div class="stat">
          <div class="stat-title">Revenue</div>
          <div class="stat-value">$12,345</div>
        </div>
      </div>
      
      <!-- Content cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="card bg-base-100 shadow-xl">Card 1</div>
        <div class="card bg-base-100 shadow-xl">Card 2</div>
        <div class="card bg-base-100 shadow-xl">Card 3</div>
      </div>
    </main>
  </div>
</div>
```
