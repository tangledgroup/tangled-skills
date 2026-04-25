# Oat UI - Utilities and Helper Classes

Official utility classes from Oat UI. See the [original utilities.css](https://github.com/knadh/oat/blob/master/src/css/utilities.css) for the complete source.

## Overview

Oat provides a minimal set of utility classes for common layout and styling needs. These are designed to work seamlessly with Oat's semantic components without requiring custom CSS.

**Source**: https://raw.githubusercontent.com/knadh/oat/master/src/css/utilities.css

## Text Alignment

Control text alignment within elements:

```html
<p class="align-left">Aligned to the left (start)</p>
<p class="align-center">Centered text</p>
<p class="align-right">Aligned to the right (end)</p>
```

**CSS:**
```css
.align-left { text-align: start; }
.align-center { text-align: center; }
.align-right { text-align: end; }
```

## Text Color Variants

Muted text colors for secondary content:

```html
<p class="text-light">This text is muted (var(--muted-foreground))</p>
<p class="text-lighter">This text is even lighter (var(--faint-foreground))</p>
```

**CSS:**
```css
.text-light { color: var(--muted-foreground); }
.text-lighter { color: var(--faint-foreground); }
```

## Flexbox Utilities

### Basic Flex Display

```html
<div class="flex">Flex container</div>
<div class="flex-col">Flex column (vertical)</div>
```

**CSS:**
```css
.flex { display: flex; }
.flex-col { flex-direction: column; }
```

### Alignment in Flex Containers

```html
<div class="flex items-center">
  <!-- Children are vertically centered -->
</div>

<div class="flex justify-center">
  <!-- Children are horizontally centered -->
</div>

<div class="flex justify-between">
  <!-- Children spread with space between -->
</div>

<div class="flex justify-end">
  <!-- Children aligned to the end -->
</div>
```

**CSS:**
```css
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
```

### HStack and VStack (Bootstrap-inspired)

Pre-configured flex containers for common layouts:

**HStack (Horizontal Stack)**
```html
<div class="hstack">
  <button>Save</button>
  <button class="outline">Cancel</button>
  <span class="text-light">Last saved 2min ago</span>
</div>
```

- Display: flex
- Align items: center
- Gap: var(--space-3) (12px)
- Flex wrap: wrap
- Auto height
- Children margins reset to 0

**VStack (Vertical Stack)**
```html
<div class="vstack">
  <h2>Title</h2>
  <p>Description text</p>
  <button>Primary Action</button>
</div>
```

- Display: flex
- Flex direction: column
- Gap: var(--space-3) (12px)

**CSS:**
```css
.hstack {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  align-content: flex-start;
  height: auto;

  > * {
    margin: 0;
  }
}

.vstack {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
```

## Gap Utilities

Control spacing between flex/grid children:

```html
<div class="hstack gap-1">
  <!-- Gap: 4px -->
  <span>Item 1</span>
  <span>Item 2</span>
</div>

<div class="hstack gap-2">
  <!-- Gap: 8px -->
  <span>Item 1</span>
  <span>Item 2</span>
</div>

<div class="hstack gap-4">
  <!-- Gap: 16px -->
  <span>Item 1</span>
  <span>Item 2</span>
</div>
```

**CSS:**
```css
.gap-1 { gap: var(--space-1); }  /* 4px */
.gap-2 { gap: var(--space-2); }  /* 8px */
.gap-4 { gap: var(--space-4); }  /* 16px */
```

## Margin Utilities

Block-start and block-end margins (logical properties):

```html
<div class="mt-2">Margin top: 8px</div>
<div class="mt-4">Margin top: 16px</div>
<div class="mt-6">Margin top: 24px</div>

<div class="mb-2">Margin bottom: 8px</div>
<div class="mb-4">Margin bottom: 16px</div>
<div class="mb-6">Margin bottom: 24px</div>
```

**CSS:**
```css
.mt-2 { margin-block-start: var(--space-2); }  /* 8px */
.mt-4 { margin-block-start: var(--space-4); }  /* 16px */
.mt-6 { margin-block-start: var(--space-6); }  /* 24px */

.mb-2 { margin-block-end: var(--space-2); }  /* 8px */
.mb-4 { margin-block-end: var(--space-4); }  /* 16px */
.mb-6 { margin-block-end: var(--space-6); }  /* 24px */
```

## Padding Utilities

```html
<div class="p-4">Padding all sides: 16px</div>
```

**CSS:**
```css
.p-4 { padding: var(--space-4); }  /* 16px */
```

## Width Utilities

```html
<div class="w-100">Width: 100%</div>
```

**CSS:**
```css
.w-100 { width: 100%; }
```

## Unstyled Lists and Links

Remove default styling from lists and links:

```html
<ul class="unstyled">
  <li><a href="#" class="unstyled">No bullets, no underline</a></li>
  <li><a href="#" class="unstyled">Clean navigation items</a></li>
</ul>
```

**CSS:**
```css
:is(ul, ol, a).unstyled {
  list-style: none;
  text-decoration: none;
  padding: 0;
}
```

## Complete utilities.css Source

```css
@layer utilities {
  .align-left { text-align: start; }
  .align-center { text-align: center; }
  .align-right { text-align: end; }
  .text-light { color: var(--muted-foreground); }
  .text-lighter { color: var(--faint-foreground); }

  .flex { display: flex; }
  .flex-col { flex-direction: column; }
  .items-center { align-items: center; }
  .justify-center { justify-content: center; }
  .justify-between { justify-content: space-between; }
  .justify-end { justify-content: flex-end; }

  /* Bootstrap inspired. */
  .hstack {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
    align-content: flex-start;
    height: auto;

    > * {
      margin: 0;
    }
  }
  .vstack {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .gap-1 { gap: var(--space-1); }
  .gap-2 { gap: var(--space-2); }
  .gap-4 { gap: var(--space-4); }

  .mt-2 { margin-block-start: var(--space-2); }
  .mt-4 { margin-block-start: var(--space-4); }
  .mt-6 { margin-block-start: var(--space-6); }

  .mb-2 { margin-block-end: var(--space-2); }
  .mb-4 { margin-block-end: var(--space-4); }
  .mb-6 { margin-block-end: var(--space-6); }
  .p-4 { padding: var(--space-4); }

  .w-100 { width: 100%; }

  :is(ul, ol, a).unstyled {
    list-style: none;
    text-decoration: none;
    padding: 0;
  }
}
```

## Practical Examples

### Navigation Bar

```html
<nav data-topnav class="hstack justify-between">
  <div class="hstack">
    <a href="/" class="logo">My App</a>
  </div>
  
  <ul class="unstyled hstack">
    <li><a href="/about" class="unstyled">About</a></li>
    <li><a href="/products" class="unstyled">Products</a></li>
    <li><a href="/contact" class="unstyled">Contact</a></li>
  </ul>
</nav>
```

### Card Header with Actions

```html
<header class="hstack justify-between items-center mb-4">
  <div>
    <h2>Dashboard</h2>
    <p class="text-light">Welcome back, John</p>
  </div>
  <button class="outline small">Settings</button>
</header>
```

### Form Actions Footer

```html
<footer class="hstack justify-end gap-2 mt-6">
  <button type="button" class="outline">Cancel</button>
  <button type="submit">Save Changes</button>
</footer>
```

### Vertical Stack of Cards

```html
<div class="vstack">
  <article class="card">
    <h3>First Card</h3>
    <p>Content here</p>
  </article>
  
  <article class="card">
    <h3>Second Card</h3>
    <p>Content here</p>
  </article>
  
  <article class="card">
    <h3>Third Card</h3>
    <p>Content here</p>
  </article>
</div>
```

### Centered Content

```html
<div class="align-center p-4">
  <h2 class="mb-2">Welcome</h2>
  <p class="text-light mb-4">Thank you for visiting</p>
  <button>Get Started</button>
</div>
```

### Inline Badge and Button

```html
<div class="hstack items-center gap-2">
  <span>Status:</span>
  <span class="badge success">Active</span>
  <button class="outline small">Edit</button>
</div>
```

### Two Column Form Row

```html
<div class="hstack gap-4">
  <div class="flex-1">
    <label data-field>
      First Name
      <input type="text" placeholder="John" />
    </label>
  </div>
  
  <div class="flex-1">
    <label data-field>
      Last Name
      <input type="text" placeholder="Doe" />
    </label>
  </div>
</div>
```

**Note**: `flex-1` is standard CSS, not an Oat utility class.

## Custom Utilities

Extend Oat's utilities with your own CSS:

```css
@layer utilities {
  /* Additional spacing */
  .mt-8 { margin-block-start: var(--space-8); }
  .mb-8 { margin-block-end: var(--space-8); }
  .p-8 { padding: var(--space-8); }
  
  /* Custom text utilities */
  .text-small { font-size: var(--text-7); }
  .text-large { font-size: var(--text-3); }
  
  /* Flex center shortcut */
  .flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  /* Additional width utilities */
  .w-auto { width: auto; }
  .w-half { width: 50%; }
}
```

**Important**: Wrap custom utilities in `@layer utilities` to maintain proper cascade order.

## Space Scale Reference

Oat uses a consistent spacing scale based on CSS variables:

| Variable | Size | Common Use |
|----------|------|------------|
| `--space-1` | 4px | Tight spacing |
| `--space-2` | 8px | Small gaps |
| `--space-3` | 12px | Default hstack/vstack gap |
| `--space-4` | 16px | Standard padding/margin |
| `--space-6` | 24px | Large spacing |
| `--space-8` | 32px | Section spacing |
| `--space-10` | 40px | Large sections |
| `--space-12` | 48px | Hero sections |

## Best Practices

### DO

- Use `hstack` and `vstack` for common layouts
- Leverage `gap` instead of margins between children
- Use logical properties (`margin-block-start` instead of `margin-top`)
- Keep utility classes minimal and focused
- Extend utilities in `@layer utilities` for custom needs

### DON'T

- Overuse utility classes (use components when possible)
- Create duplicate utilities that Oat already provides
- Forget to wrap custom utilities in `@layer utilities`
- Use utilities for complex component styling

## Comparison with Other Frameworks

| Feature | Oat | Tailwind | Bootstrap |
|---------|-----|----------|-----------|
| Philosophy | Minimal, semantic | Utility-first | Component-first |
| Flex utilities | `hstack`, `vstack` | `flex`, `flex-col` | `.d-flex` |
| Spacing scale | 9 steps | 100+ steps | 5 steps |
| Customization | CSS variables | Build-time | Sass variables |
| Bundle size | ~6KB | ~100KB+ | ~50KB+ |

Oat's approach is intentionally minimal - use utilities for quick adjustments, but rely on semantic components for structure.

## Browser Support

All utility classes use modern CSS features:
- Logical properties (`margin-block-start`, `margin-block-end`)
- CSS custom properties (variables)
- CSS layers (`@layer`)

Supported in all modern browsers. For IE11 support, use the legacy build with polyfills.
