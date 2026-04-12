# DaisyUI Advanced Patterns

This guide covers advanced customization, overrides, responsive design patterns, and best practices for DaisyUI 5.5.

## Customization Techniques

### Overriding Component Styles

#### Using Important (!) Modifier

When Tailwind utilities don't override component styles due to specificity:

```html
<!-- Force background color -->
<button class="btn bg-red-500!">Red Button</button>

<!-- Force text color -->
<div class="badge badge-primary text-white!">White Text</div>

<!-- Force multiple properties -->
<div class="card bg-gradient-to-br from-blue-500 to-purple-600! text-white!">
  Gradient Card
</div>
```

#### Using Tailwind Utilities

Prefer adding utilities over using `!`:

```html
<!-- Custom padding -->
<button class="btn px-8 py-3">Extra Padded Button</button>

<!-- Custom spacing -->
<div class="alert my-4 space-y-2">
  <span>Alert with custom spacing</span>
</div>

<!-- Custom rounded corners -->
<div class="card rounded-3xl shadow-xl">
  <div class="card-body">Rounded Card</div>
</div>
```

#### Using CSS Variables

Customize individual components with CSS variables:

```html
<div class="card" style="--radius-box:1rem;">
  <div class="card-body">Card with custom radius</div>
</div>

<button class="btn" style="--border:2px;">
  Button with thicker border
</button>
```

### Custom Component Creation

#### Building on DaisyUI Base

Create custom components using DaisyUI and Tailwind:

```html
<!-- Custom feature card -->
<div class="bg-base-100 rounded-xl p-6 shadow-lg border border-base-200 hover:shadow-xl transition-shadow">
  <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  </div>
  <h3 class="text-xl font-bold mb-2">Fast Performance</h3>
  <p class="text-base-content/70">Optimized for speed and efficiency.</p>
</div>
```

#### Creating Reusable Patterns

```html
<!-- Custom stat card -->
<div class="stats-stat bg-base-100 rounded-xl p-4 shadow-md">
  <div class="flex items-center justify-between">
    <div>
      <p class="text-sm text-base-content/70">Total Revenue</p>
      <p class="text-2xl font-bold">$12,345</p>
    </div>
    <div class="badge badge-success gap-1">
      ↑ 12%
    </div>
  </div>
</div>
```

## Responsive Design Patterns

### Mobile-First Approach

Start with mobile styles, then add breakpoints:

```html
<!-- Stack on mobile, side-by-side on desktop -->
<div class="card card-side w-full md:w-96 lg:w-96 bg-base-100 shadow-xl">
  <figure class="md:h-48">
    <img src="https://picsum.photos/400/300" alt="" />
  </figure>
  <div class="card-body">
    <h2 class="card-title">Responsive Card</h2>
    <p>Stacked on mobile, side layout on desktop.</p>
  </div>
</div>
```

### Responsive Navigation

```html
<div class="navbar bg-base-100">
  <div class="navbar-start">
    <!-- Mobile menu toggle -->
    <div class="dropdown lg:hidden">
      <div tabindex="0" role="button" class="btn btn-ghost">
        ☰ Menu
      </div>
      <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
        <li><a>Home</a></li>
        <li><a>About</a></li>
        <li><a>Contact</a></li>
      </ul>
    </div>
    
    <a class="btn btn-ghost text-xl">Brand</a>
  </div>
  
  <!-- Desktop menu -->
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

### Responsive Grid Layouts

```html
<!-- 1 column → 2 columns → 3 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card bg-base-100 shadow-xl">Card 1</div>
  <div class="card bg-base-100 shadow-xl">Card 2</div>
  <div class="card bg-base-100 shadow-xl">Card 3</div>
  <div class="card bg-base-100 shadow-xl">Card 4</div>
  <div class="card bg-base-100 shadow-xl">Card 5</div>
  <div class="card bg-base-100 shadow-xl">Card 6</div>
</div>
```

### Responsive Forms

```html
<form class="space-y-4">
  <!-- Stack on mobile, side-by-side on desktop -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="form-control">
      <label class="label">
        <span class="label-text">First Name</span>
      </label>
      <input type="text" class="input input-bordered" placeholder="John" />
    </div>
    
    <div class="form-control">
      <label class="label">
        <span class="label-text">Last Name</span>
      </label>
      <input type="text" class="input input-bordered" placeholder="Doe" />
    </div>
  </div>
  
  <!-- Full width on all screens -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Email</span>
    </label>
    <input type="email" class="input input-bordered" placeholder="john@example.com" />
  </div>
  
  <button type="submit" class="btn btn-primary w-full md:w-auto">
    Submit
  </button>
</form>
```

### Responsive Tables

```html
<!-- Scrollable on mobile -->
<div class="overflow-x-auto">
  <table class="table">
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
        <td>John Doe</td>
        <td>john@example.com</td>
        <td>Developer</td>
        <td><span class="badge badge-success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>

<!-- Card-based layout on mobile -->
<div class="overflow-x-auto md:hidden">
  <div class="card bg-base-100 shadow-xl mb-4">
    <div class="card-body p-4">
      <h3 class="card-title text-sm">John Doe</h3>
      <p class="text-sm">john@example.com</p>
      <p class="text-sm">Role: Developer</p>
      <span class="badge badge-success">Active</span>
    </div>
  </div>
</div>
```

## Theme Customization

### Creating Custom Themes

```css
@plugin "daisyui/theme" {
  name: "corporate";
  default: true;
  
  /* Professional blue theme */
  --color-base-100: #ffffff;
  --color-base-200: #f8fafc;
  --color-base-300: #e2e8f0;
  --color-base-content: #0f172a;
  
  --color-primary: #2563eb;
  --color-primary-content: #ffffff;
  
  --color-secondary: #4f46e5;
  --color-secondary-content: #ffffff;
  
  --color-accent: #06b6d4;
  --color-accent-content: #ffffff;
  
  --color-neutral: #64748b;
  --color-neutral-content: #ffffff;
  
  --color-info: #0ea5e9;
  --color-info-content: #ffffff;
  
  --color-success: #10b981;
  --color-success-content: #ffffff;
  
  --color-warning: #f59e0b;
  --color-warning-content: #0f172a;
  
  --color-error: #ef4444;
  --color-error-content: #ffffff;
  
  /* Rounded corners */
  --radius-selector: 0.375rem;
  --radius-field: 0.375rem;
  --radius-box: 0.5rem;
}
```

### OKLCH Colors for Better Gamut

```css
@plugin "daisyui/theme" {
  name: "modern";
  default: true;
  
  /* OKLCH provides wider color gamut */
  --color-base-100: oklch(100% 0 0);
  --color-base-200: oklch(98% 0.01 240);
  --color-base-300: oklch(95% 0.02 240);
  --color-base-content: oklch(20% 0.03 240);
  
  --color-primary: oklch(60% 0.25 250);
  --color-primary-content: oklch(98% 0.01 250);
  
  --color-secondary: oklch(65% 0.2 180);
  --color-secondary-content: oklch(98% 0.01 180);
  
  --color-accent: oklch(70% 0.2 120);
  --color-accent-content: oklch(20% 0.05 120);
  
  --color-neutral: oklch(50% 0.02 240);
  --color-neutral-content: oklch(98% 0.01 240);
  
  --color-info: oklch(70% 0.18 220);
  --color-info-content: oklch(98% 0.01 220);
  
  --color-success: oklch(65% 0.2 140);
  --color-success-content: oklch(98% 0.01 140);
  
  --color-warning: oklch(80% 0.22 80);
  --color-warning-content: oklch(20% 0.05 80);
  
  --color-error: oklch(60% 0.25 25);
  --color-error-content: oklch(98% 0.01 25);
}
```

### Dark Mode Theme

```css
@plugin "daisyui/theme" {
  name: "mydark";
  prefersdark: true;
  
  --color-base-100: #0f172a;
  --color-base-200: #1e293b;
  --color-base-300: #334155;
  --color-base-content: #f1f5f9;
  
  --color-primary: #3b82f6;
  --color-primary-content: #ffffff;
  
  --color-secondary: #8b5cf6;
  --color-secondary-content: #ffffff;
  
  --color-accent: #ec4899;
  --color-accent-content: #ffffff;
  
  --color-neutral: #94a3b8;
  --color-neutral-content: #ffffff;
  
  --color-info: #06b6d4;
  --color-info-content: #ffffff;
  
  --color-success: #10b981;
  --color-success-content: #ffffff;
  
  --color-warning: #f59e0b;
  --color-warning-content: #0f172a;
  
  --color-error: #ef4444;
  --color-error-content: #ffffff;
}
```

## Component Composition Patterns

### Card with Multiple Elements

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure class="relative">
    <img src="https://picsum.photos/400/300" alt="" />
    <div class="absolute top-2 right-2 badge badge-primary">New</div>
  </figure>
  
  <div class="card-body">
    <div class="flex items-start justify-between">
      <div>
        <h2 class="card-title">Product Name</h2>
        <p class="text-sm text-base-content/70">SKU: 12345</p>
      </div>
      <div class="badge badge-success">In Stock</div>
    </div>
    
    <p>Description of the product goes here.</p>
    
    <div class="flex items-center justify-between mt-4">
      <div class="text-2xl font-bold">$99.99</div>
      <div class="rating rating-sm">
        <input type="radio" name="rating" class="rating-hidden" />
        <input type="radio" name="rating" class="rating bg-primary" checked />
        <input type="radio" name="rating" class="rating bg-primary" checked />
        <input type="radio" name="rating" class="rating bg-primary" checked />
        <input type="radio" name="rating" class="rating bg-primary" checked />
        <input type="radio" name="rating" class="rating bg-primary" />
      </div>
    </div>
    
    <div class="card-actions justify-end">
      <button class="btn btn-ghost btn-sm">View Details</button>
      <button class="btn btn-primary btn-sm">Add to Cart</button>
    </div>
  </div>
</div>
```

### Form with Validation States

```html
<form class="space-y-4 max-w-md">
  <!-- Success state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Email</span>
    </label>
    <input 
      type="email" 
      class="input input-bordered input-success" 
      value="valid@email.com"
    />
    <label class="label">
      <span class="label-text-alt text-success flex items-center gap-1">
        ✓ Valid email address
      </span>
    </label>
  </div>
  
  <!-- Error state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Password</span>
    </label>
    <input 
      type="password" 
      class="input input-bordered input-error" 
      placeholder="Enter password"
    />
    <label class="label">
      <span class="label-text-alt text-error flex items-center gap-1">
        ✗ Password is required
      </span>
    </label>
  </div>
  
  <!-- Warning state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Username</span>
    </label>
    <input 
      type="text" 
      class="input input-bordered input-warning" 
      value="taken_username"
    />
    <label class="label">
      <span class="label-text-alt text-warning flex items-center gap-1">
        ⚠ Username already taken
      </span>
    </label>
  </div>
  
  <!-- Loading state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Verification Code</span>
    </label>
    <div class="join">
      <input type="text" class="join-item input text-center" maxlength="1" />
      <input type="text" class="join-item input text-center" maxlength="1" />
      <input type="text" class="join-item input text-center" maxlength="1" />
      <input type="text" class="join-item input text-center" maxlength="1" />
    </div>
  </div>
  
  <button type="submit" class="btn btn-primary w-full">
    <span class="loading loading-spinner hidden" id="loading"></span>
    <span id="submit-text">Submit</span>
  </button>
</form>
```

### Dashboard Widget

```html
<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="card-title text-lg">Revenue Overview</h3>
      <select class="select select-bordered select-sm">
        <option>Last 7 days</option>
        <option>Last 30 days</option>
        <option>Last 90 days</option>
      </select>
    </div>
    
    <div class="flex items-end gap-2 mb-4">
      <div class="text-3xl font-bold">$12,345</div>
      <div class="badge badge-success gap-1 mb-1">↑ 12.5%</div>
    </div>
    
    <!-- Chart placeholder -->
    <div class="h-40 bg-base-200 rounded-lg flex items-center justify-center">
      <span class="text-base-content/50">Chart goes here</span>
    </div>
    
    <div class="card-actions justify-end mt-4">
      <button class="btn btn-sm btn-ghost">View Report</button>
      <button class="btn btn-sm btn-primary">Export</button>
    </div>
  </div>
</div>
```

## Accessibility Enhancements

### Focus Management

```html
<!-- Visible focus rings -->
<button class="btn btn-primary focus:ring-2 focus:ring-offset-2">
  Focused Button
</button>

<!-- Skip link for keyboard users -->
<a href="#main-content" class="sr-only focus:not-sr-only focus:btn focus:btn-primary focus:absolute focus:top-4 focus:left-4 z-50">
  Skip to main content
</a>
```

### Screen Reader Support

```html
<!-- Visually hidden but accessible -->
<span class="sr-only">Important information for screen readers</span>

<!-- Live regions for dynamic content -->
<div class="alert alert-success" role="alert" aria-live="polite">
  <span>Form submitted successfully!</span>
</div>

<!-- Describedby for additional context -->
<input 
  type="text" 
  class="input input-bordered" 
  id="username"
  aria-describedby="username-help"
/>
<p id="username-help" class="text-sm text-base-content/70">
  Must be 3-20 characters, letters and numbers only.
</p>
```

### Keyboard Navigation

```html
<!-- Focusable custom element -->
<div 
  tabindex="0" 
  role="button" 
  class="btn btn-primary"
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Custom Button
</div>

<!-- Arrow key navigation for menu -->
<ul class="menu" role="menu">
  <li role="none">
    <a role="menuitem" href="#">Item 1</a>
  </li>
  <li role="none">
    <a role="menuitem" href="#">Item 2</a>
  </li>
</ul>
```

### Form Accessibility

```html
<!-- Required field indicator -->
<label class="label">
  <span class="label-text">Email <span class="text-error" aria-hidden="true">*</span><span class="sr-only">(required)</span></span>
</label>
<input type="email" required class="input input-bordered" aria-required="true" />

<!-- Error summary -->
<div role="alert" aria-live="assertive" class="alert alert-error mb-4">
  <h2 class="font-bold">Please fix these errors:</h2>
  <ul class="mt-2 space-y-1">
    <li><a href="#email" class="link link-error">Email is invalid</a></li>
    <li><a href="#password" class="link link-error">Password is too short</a></li>
  </ul>
</div>
```

## Performance Optimization

### Reduce Bundle Size

Include only needed components:

```css
@plugin "daisyui" {
  include: button, alert, card, input, modal, navbar, footer;
}
```

Exclude unused components:

```css
@plugin "daisyui" {
  exclude: mockup-phone, mockup-browser, mockup-window, calendar;
}
```

### Lazy Load Heavy Components

```html
<!-- Load modal content on demand -->
<dialog id="heavy-modal" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Heavy Content</h3>
    <!-- Load expensive content here -->
  </div>
</dialog>
```

### Critical CSS

Include critical component styles inlined:

```html
<style>
  /* Critical navbar and hero styles */
  .navbar { display: flex; align-items: center; padding: 1rem; }
  .hero { min-height: 50vh; display: flex; align-items: center; }
</style>
```

## Common Issues and Solutions

### Issue: Styles Not Applying

**Solution:** Check build configuration

```css
/* Ensure correct order */
@import "tailwindcss";
@plugin "daisyui";
```

### Issue: Colors Not Changing with Theme

**Solution:** Use semantic colors instead of Tailwind colors

```html
<!-- Wrong -->
<div class="bg-blue-500 text-white">Static</div>

<!-- Correct -->
<div class="bg-primary text-primary-content">Themed</div>
```

### Issue: Component Overridden by Custom CSS

**Solution:** Use important or increase specificity

```html
<!-- Use important -->
<button class="btn bg-red-500!">Red Button</button>

<!-- Or use more specific selector in CSS */
.btn.custom-btn {
  background-color: red;
}
```

### Issue: Modal Not Closing

**Solution:** Ensure proper dialog structure

```html
<dialog id="modal" class="modal">
  <div class="modal-box">
    <h3>Modal</h3>
    <!-- Close button must be inside form with method="dialog" -->
    <form method="dialog">
      <button class="btn">Close</button>
    </form>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

### Issue: Dropdown Not Working

**Solution:** Check for proper structure and tabindex

```html
<div class="dropdown">
  <!-- Button needs tabindex for keyboard interaction -->
  <div tabindex="0" role="button" class="btn">
    Dropdown
  </div>
  <!-- Content must be direct child -->
  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] p-2 shadow w-52">
    <li><a>Item 1</a></li>
  </ul>
</div>
```

## Best Practices Summary

1. **Use semantic colors** - Let themes control appearance
2. **Mobile-first design** - Start with mobile, enhance for desktop
3. **Accessibility first** - Include ARIA attributes and keyboard support
4. **Performance matters** - Include only needed components
5. **Consistent patterns** - Reuse component compositions
6. **Test thoroughly** - Check on multiple devices and browsers
7. **Document customizations** - Keep track of overrides and custom themes
8. **Follow DaisyUI conventions** - Use class names as intended
9. **Leverage Tailwind utilities** - For fine-tuning without custom CSS
10. **Keep it maintainable** - Avoid excessive `!` important declarations

## Resources

- [DaisyUI Documentation](https://daisyui.com)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [DaisyUI Theme Generator](https://daisyui.com/theme-generator/)
- [Refactoring UI Book](https://refactoringui.com)
- [Web Accessibility Initiative](https://www.w3.org/WAI/)
