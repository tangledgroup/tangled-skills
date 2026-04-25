# Oat UI - Third-Party Extensions

Community-built extensions that add new components and features to Oat. Listed on https://oat.ink/extensions/

## Official Extensions

### oat-chips by @someshkar

**Chip/tag component with dismissible filters, colors, and toggle selection.**

- **Size**: ~1KB gzipped
- **Repository**: https://github.com/someshkar/oat-chips
- **Demo**: https://oat-chips.somesh.dev
- **npm**: https://www.npmjs.com/package/@someshkar/oat-chips

#### Features

- Simple chip/tag components
- Dismissible filters with close button
- Color variants: default, success, warning, danger
- Outline style for subtler appearance
- Toggle selection with `aria-pressed`
- Keyboard accessible
- Works with Oat's design system

#### Installation

**CDN (Fastest)**

```html
<link rel="stylesheet" href="https://unpkg.com/@someshkar/oat-chips/dist/chip.min.css">
<script src="https://unpkg.com/@someshkar/oat-chips/dist/chip.min.js" defer></script>
```

**npm**

```bash
npm install @someshkar/oat-chips
```

```javascript
import '@someshkar/oat-chips/dist/chip.min.css';
import '@someshkar/oat-chips/dist/chip.min.js';
```

**bun**

```bash
bun install @someshkar/oat-chips
```

```javascript
import '@someshkar/oat-chips/dist/chip.min.css';
import '@someshkar/oat-chips/dist/chip.min.js';
```

**Download**

```bash
wget https://raw.githubusercontent.com/someshkar/oat-chips/main/dist/chip.min.css
wget https://raw.githubusercontent.com/someshkar/oat-chips/main/dist/chip.min.js
```

#### Basic Usage

**Simple Tags**

```html
<button class="chip">Design</button>
<button class="chip">Development</button>
<button class="chip">Product</button>
```

**Dismissible Filters**

```html
<button class="chip">
  <span>Status: Active</span>
  <span class="chip-close" aria-label="Remove filter">×</span>
</button>

<button class="chip">
  <span>Priority: High</span>
  <span class="chip-close" aria-label="Remove filter">×</span>
</button>
```

Click the × to dismiss the chip.

**Color Variants**

```html
<button class="chip">Default</button>
<button class="chip success">Success</button>
<button class="chip warning">Warning</button>
<button class="chip danger">Danger</button>
```

**Outline Style**

```html
<button class="chip outline">Documentation</button>
<button class="chip outline success">Tests Pass</button>
<button class="chip outline warning">Needs QA</button>
```

**Toggle Selection**

```html
<div role="group" aria-label="Filter by category">
  <button class="chip" aria-pressed="true">All Projects</button>
  <button class="chip" aria-pressed="false">Active</button>
  <button class="chip" aria-pressed="false">Archived</button>
</div>
```

Click to toggle between selected and unselected states.

**Mixed Usage**

```html
<div role="group" aria-label="Active filters">
  <button class="chip">
    <span>Type: Bug</span>
    <span class="chip-close" aria-label="Remove">×</span>
  </button>
  <button class="chip danger" aria-pressed="true">P0 Critical</button>
  <button class="chip outline">Frontend</button>
</div>
```

#### Styling

Chips automatically use Oat's CSS variables for theming. Custom styling:

```css
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.chip {
  /* Inherits from chip.min.css */
  /* Can be overridden if needed */
}
```

#### Integration with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Oat + Chips</title>
  <link rel="stylesheet" href="oat.min.css">
  <link rel="stylesheet" href="chip.min.css">
</head>
<body>
  <div class="container" style="padding: var(--space-6);">
    <h1>Filter by Tags</h1>
    
    <div class="chip-group" role="group" aria-label="Active filters">
      <button class="chip">
        <span>Status: Active</span>
        <span class="chip-close" aria-label="Remove">×</span>
      </button>
      <button class="chip success" aria-pressed="true">High Priority</button>
      <button class="chip outline">Backend</button>
    </div>
    
    <article class="card" style="margin-top: var(--space-4);">
      <h3>Filtered Results</h3>
      <p>Showing items matching active filters</p>
    </article>
  </div>
  
  <script src="oat.min.js" defer></script>
  <script src="chip.min.js" defer></script>
</body>
</html>
```

---

### oat-animate by @dharmeshgurnani

**Lightweight CSS animation extension with declarative triggers and reduced-motion support.**

- **Size**: ~0.9KB gzipped (2.7KB minified)
- **Repository**: https://github.com/dharmeshgurnani/oat-animate
- **Demo**: https://oat-animate.dharmeshgurnani.com
- **npm**: https://www.npmjs.com/package/oat-animate

#### Features

- Declarative animation triggers via `ot-animate` attribute
- Three trigger types: on-load, on-hover, in-view
- 10+ built-in animations (fade, slide, zoom, bounce, etc.)
- Automatic reduced-motion support for accessibility
- CSS variable customization (duration, delay, easing)
- Combine multiple animations on single element
- Zero JavaScript dependencies

#### Installation

**CDN (Fastest)**

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ots-animate@latest/dist/oat-animate.min.css">
<script src="https://cdn.jsdelivr.net/npm/ots-animate@latest/dist/oat-animate.min.js"></script>
```

**npm**

```bash
npm install oat-animate
```

```javascript
import 'oat-animate/dist/oat-animate.min.css';
import 'oat-animate/dist/oat-animate.min.js';
```

#### Available Animations

- `fade-up` - Fades in while moving upward
- `fade-down` - Fades in while moving downward
- `zoom-in` - Scales up from smaller size
- `slide-left` - Slides in from right
- `slide-right` - Slides in from left
- `pop` - Quick bounce scale effect
- `bounce` - Bouncing movement
- `flip-in` - 3D flip effect
- `pulse` - Pulsing scale animation (loops)
- `shake` - Horizontal shake effect

#### Usage

**On Load Animation**

Animation plays when page loads:

```html
<div ot-animate="fade-up">
  <h3>Fades in on load</h3>
  <p>This content animates when the page loads.</p>
</div>
```

**On Hover Animation**

Animation plays on mouse hover:

```html
<button ot-animate="hover:pop">
  Hover me for pop effect
</button>

<article class="card" ot-animate="hover:zoom-in">
  <h3>Zooms on hover</h3>
</article>
```

**In View Animation (Scroll)**

Animation plays when element scrolls into viewport:

```html
<section ot-animate="view:fade-up">
  <h3>Fades in when visible</h3>
</section>

<article class="card" ot-animate="view:slide-left">
  <h3>Slides from left</h3>
</article>

<article class="card" ot-animate="view:slide-right">
  <h3>Slides from right</h3>
</article>
```

**Multiple Animations**

Combine multiple triggers on a single element:

```html
<div ot-animate="fade-up hover:zoom-in">
  Fades in on load, zooms on hover
</div>

<article class="card" ot-animate="view:fade-up hover:pop">
  <h3>Multiple effects</h3>
</article>
```

#### Customization

Customize animation timing with CSS variables:

```html
<!-- Inline customization -->
<div ot-animate="fade-up" style="--ot-duration: 1.5s; --ot-delay: 0.5s;">
  Slow and delayed animation
</div>
```

**Available CSS Variables:**

- `--ot-duration` (default: `0.6s`) - Animation duration
- `--ot-delay` (default: `0s`) - Animation delay
- `--ot-easing` (default: `ease`) - Easing function

**Global Customization:**

```css
/* Apply to all animations */
:root {
  --ot-duration: 0.8s;
  --ot-easing: ease-out;
}

/* Or target specific elements */
.slow-animation {
  --ot-duration: 1.2s;
}

.fast-animation {
  --ot-duration: 0.3s;
}
```

#### Reduced Motion Support

Automatically respects `prefers-reduced-motion` system preference:

```css
@media (prefers-reduced-motion: reduce) {
  [ot-animate] {
    animation: none !important;
    transition: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
```

No additional configuration needed - accessibility is built-in.

#### Integration with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Oat + Animate</title>
  <link rel="stylesheet" href="oat.min.css">
  <link rel="stylesheet" href="oat-animate.min.css">
</head>
<body>
  <div class="container" style="padding: var(--space-6);">
    <h1 ot-animate="fade-up">Animated Dashboard</h1>
    
    <div class="grid">
      <div class="col-4">
        <article class="card" ot-animate="view:fade-up" style="--ot-delay: 0s;">
          <h3>📊 Statistics</h3>
          <p>View your metrics</p>
        </article>
      </div>
      
      <div class="col-4">
        <article class="card" ot-animate="view:fade-up" style="--ot-delay: 0.1s;">
          <h3>📝 Activity</h3>
          <p>Recent actions</p>
        </article>
      </div>
      
      <div class="col-4">
        <article class="card" ot-animate="view:fade-up" style="--ot-delay: 0.2s;">
          <h3>⚙️ Settings</h3>
          <p>Configure options</p>
        </article>
      </div>
    </div>
    
    <div style="margin-top: var(--space-6);">
      <button ot-animate="hover:pop" class="primary">
        Primary Action
      </button>
      <button ot-animate="hover:zoom-in" class="outline">
        Secondary Action
      </button>
    </div>
  </div>
  
  <script src="oat.min.js" defer></script>
  <script src="oat-animate.min.js"></script>
</body>
</html>
```

#### Staggered Animations

Create stagger effects with delay increments:

```html
<ul style="list-style: none; padding: 0;">
  <li ot-animate="view:fade-up" style="--ot-delay: 0s;">Item 1</li>
  <li ot-animate="view:fade-up" style="--ot-delay: 0.1s;">Item 2</li>
  <li ot-animate="view:fade-up" style="--ot-delay: 0.2s;">Item 3</li>
  <li ot-animate="view:fade-up" style="--ot-delay: 0.3s;">Item 4</li>
</ul>
```

#### Advanced Examples

**Hero Section with Animations**

```html
<header style="padding: var(--space-12) var(--space-6); text-align: center;">
  <h1 ot-animate="fade-up">Welcome to Our Platform</h1>
  <p ot-animate="view:fade-up" style="--ot-delay: 0.2s;">
    Build beautiful interfaces with Oat UI
  </p>
  <div ot-animate="view:fade-up" style="--ot-delay: 0.4s;">
    <button ot-animate="hover:pop" class="primary">Get Started</button>
    <button ot-animate="hover:zoom-in" class="outline">Learn More</button>
  </div>
</header>
```

**Card Grid with Hover Effects**

```html
<div class="grid">
  <div class="col-4">
    <article class="card" ot-animate="view:slide-right hover:pop">
      <h3>Feature One</h3>
      <p>Description here</p>
    </article>
  </div>
  
  <div class="col-4">
    <article class="card" ot-animate="view:fade-up hover:zoom-in">
      <h3>Feature Two</h3>
      <p>Description here</p>
    </article>
  </div>
  
  <div class="col-4">
    <article class="card" ot-animate="view:slide-left hover:pop">
      <h3>Feature Three</h3>
      <p>Description here</p>
    </article>
  </div>
</div>
```

---

## Adding Your Extension

To list your extension on the Oat website:

1. Create a GitHub repository with your extension
2. Include clear documentation and examples
3. Open a PR to https://github.com/knadh/oat
4. Add your extension to the extensions page

### Extension Guidelines

- **Zero dependencies**: No external libraries required
- **Minimal size**: Keep bundle size under 5KB gzipped
- **Oat-compatible**: Use Oat's design tokens and patterns
- **Accessible**: Follow WCAG guidelines
- **Well-documented**: Include usage examples
- **MIT licensed**: Open source and free to use

### Recommended Structure

```
oat-extension-name/
├── dist/
│   ├── extension.min.js
│   └── extension.min.css (if applicable)
├── src/
│   ├── index.js
│   └── styles.css
├── examples/
│   └── demo.html
├── README.md
└── package.json
```

## Building Extensions

### Using Oat CSS Variables

```css
.my-extension {
  background: var(--card-background, var(--background));
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.my-button {
  background: var(--primary);
  color: var(--primary-foreground);
}
```

### Dark Mode Support

```css
.my-extension {
  /* Light mode (default) */
  background: var(--card-background);
  color: var(--text-color);
}

/* Automatic dark mode via CSS variables */
/* No extra code needed if using Oat variables */
```

### Accessing Oat Utilities

```javascript
// Access Oat namespace if available
const ot = window.ot;

// Show toast notification (if oat.min.js loaded)
if (ot && ot.toast) {
  ot.toast('Extension loaded', 'Success', { variant: 'success' });
}
```

## Community Extensions

Check the GitHub repository for community-contributed extensions:

https://github.com/knadh/oat#extensions

## Resources

- **Oat Documentation**: https://oat.ink
- **Oat GitHub**: https://github.com/knadh/oat
- **Oat Extensions Page**: https://oat.ink/extensions
- **Component Examples**: https://oat.ink/components

## Contributing

When building extensions:

1. Follow Oat's semantic HTML approach
2. Use CSS variables for theming
3. Support dark mode automatically
4. Ensure keyboard accessibility
5. Keep JavaScript minimal
6. Test in multiple browsers
7. Provide clear documentation
8. Include working demos

Happy extending!
