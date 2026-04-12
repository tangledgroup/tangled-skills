# Oat UI - Third-Party Extensions

Community-built extensions that add new components and features to Oat.

## Official Extensions

### oat-chips by @someshkar

**Chip/tag component with dismissible filters, colors, and toggle selection.**

- **Size**: ~1KB gzipped
- **Repository**: https://github.com/someshkar/oat-chips
- **Demo**: https://oat-chips.somesh.dev

#### Features

- Dismissible chip components
- Multiple color variants
- Toggle selection state
- Keyboard accessible
- Works with Oat's design system

#### Installation

```html
<script src="https://unpkg.com/@someshkar/oat-chips/dist/chips.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/@someshkar/oat-chips/dist/chips.min.css">
```

#### Usage

```html
<div class="oat-chips">
  <div class="chip" data-color="primary">
    JavaScript
    <button class="chip-dismiss" aria-label="Remove JavaScript">×</button>
  </div>
  
  <div class="chip" data-color="success">
    Python
    <button class="chip-dismiss" aria-label="Remove Python">×</button>
  </div>
  
  <div class="chip" data-color="warning">
    Rust
    <button class="chip-dismiss" aria-label="Remove Rust">×</button>
  </div>
</div>

<script src="oat-chips.min.js"></script>
```

#### Toggle Chips

```html
<div class="oat-chips toggle">
  <label class="chip">
    <input type="checkbox" name="tags" value="javascript" checked>
    <span>JavaScript</span>
    <button class="chip-dismiss">×</button>
  </label>
  
  <label class="chip">
    <input type="checkbox" name="tags" value="python">
    <span>Python</span>
    <button class="chip-dismiss">×</button>
  </label>
  
  <label class="chip">
    <input type="checkbox" name="tags" value="rust">
    <span>Rust</span>
    <button class="chip-dismiss">×</button>
  </label>
</div>
```

#### Options

```javascript
const chips = new OatChips('.oat-chips', {
  // Color variants: primary, success, warning, danger, secondary
  defaultColor: 'primary',
  
  // Animation duration in ms
  animationDuration: 200,
  
  // Callback when chip is dismissed
  onDismiss: (chip, value) => {
    console.log('Dismissed:', value);
  },
  
  // Callback when chip is toggled
  onToggle: (chip, checked, value) => {
    console.log('Toggled:', value, checked);
  }
});
```

---

### oat-animate by @dharmeshgurnani

**Lightweight animation extension with declarative triggers and reduced-motion support.**

- **Size**: ~1KB gzipped
- **Repository**: https://github.com/dharmeshgurnani/oat-animate
- **Demo**: https://oat-animate.dharmeshgurnani.com

#### Features

- Declarative animation triggers (`ot-animate`)
- Multiple trigger types: `on-load`, `on-hover`, `in-view`
- Automatic reduced-motion support
- Fade, slide, scale animations
- Stagger animations for lists

#### Installation

```html
<script src="https://unpkg.com/@dharmeshgurnani/oat-animate/dist/animate.min.js"></script>
```

#### Usage

##### On Load Animation

```html
<article class="card" ot-animate="fade-in">
  <h3>Fades in on load</h3>
  <p>This card animates when the page loads.</p>
</article>
```

##### On Hover Animation

```html
<article class="card" ot-animate="scale-on-hover">
  <h3>Scales on hover</h3>
  <p>Hover over this card to see it scale up.</p>
</article>
```

##### In View Animation (Scroll)

```html
<section>
  <article class="card" ot-animate="slide-in-view" data-direction="left">
    <h3>Slides in from left</h3>
  </article>
  
  <article class="card" ot-animate="slide-in-view" data-direction="right">
    <h3>Slides in from right</h3>
  </article>
  
  <article class="card" ot-animate="slide-in-view" data-direction="up">
    <h3>Slides in from bottom</h3>
  </article>
</section>
```

##### Staggered Animations

```html
<ul ot-animate="stagger-fade" data-delay="100">
  <li>Item 1</li>
  <li>Item 2</li>
  <li>Item 3</li>
  <li>Item 4</li>
</ul>
```

Each item fades in with a 100ms delay between them.

#### Animation Types

- `fade-in`: Fade from transparent
- `fade-out`: Fade to transparent
- `slide-in-view`: Slide when element enters viewport
- `scale-on-hover`: Scale up on hover
- `stagger-fade`: Staggered fade for lists
- `bounce`: Bounce in animation
- `zoom-in`: Zoom scale in

#### Options

```javascript
OatAnimate.init({
  // Respect prefers-reduced-motion
  respectReducedMotion: true,
  
  // Default animation duration
  duration: 300,
  
  // Easing function
  easing: 'ease-out',
  
  // Animation threshold for in-view (0-1)
  threshold: 0.1,
  
  // Callback when animation starts
  onStart: (element, animation) => {
    console.log('Animating:', element);
  },
  
  // Callback when animation completes
  onComplete: (element, animation) => {
    console.log('Animation complete');
  }
});
```

#### Reduced Motion Support

Automatically detects `prefers-reduced-motion` and disables animations:

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

#### Custom Animations

```javascript
OatAnimate.register('custom-fade', {
  keyframes: [
    { opacity: 0, transform: 'translateY(20px)' },
    { opacity: 1, transform: 'translateY(0)' }
  ],
  options: {
    duration: 500,
    easing: 'ease-out'
  }
});

// Usage
<div ot-animate="custom-fade">Custom animation</div>
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

## Community Extensions

Check the GitHub repository for community-contributed extensions:

https://github.com/knadh/oat#extensions

## Building Extensions

### Accessing Oat Utilities

```javascript
// Access Oat namespace
const ot = window.ot;

// Show toast notification
ot.toast('Extension loaded', 'Success', { variant: 'success' });
```

### Using Oat CSS Variables

```css
.my-extension {
  background: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
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
  background: var(--card);
  color: var(--card-foreground);
}

[data-theme="dark"] .my-extension {
  /* Dark mode overrides if needed */
  background: var(--muted);
}
```

## Resources

- **Oat Documentation**: https://oat.ink
- **Oat GitHub**: https://github.com/knadh/oat
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

Happy extending!
