# Oat UI - Introduction

## Philosophy and Design Principles

Oat was created out of frustration with the over-engineered bloat, complexity, and dependency-hell of modern JavaScript UI libraries and frameworks. The goal is a simple, minimal, vanilla, standards-based UI library that can be used long-term without worrying about JavaScript ecosystem instability.

### Core Values

1. **Ultra-Lightweight**: ~6KB CSS + ~2.2KB JS (minified + gzipped). That's it.
2. **Zero Dependencies**: Fully standalone with no dependencies on any JS or CSS frameworks or libraries. No Node.js ecosystem requirements.
3. **Semantic HTML First**: Native elements like `<button>`, `<input>`, `<dialog>` and semantic attributes like `role="button"` are styled directly without classes.
4. **Accessibility Built-in**: Semantic HTML and ARIA roles used throughout. Proper keyboard navigation support for all components.
5. **No Build Required**: Just include the CSS and JS files. No bundlers, compilers, or build steps needed.

## What Makes Oat Different

### Class-Pollution Free

Most UI libraries require extensive class names on every element:

```html
<!-- Other libraries -->
<button class="btn btn-primary btn-lg btn-icon">
  <span class="btn-icon"><svg>...</svg></span>
  <span class="btn-text">Save</span>
</button>

<!-- Oat -->
<button>Save</button>
```

Oat forces best practices by styling semantic HTML directly, reducing markup class pollution.

### Contextual Styling

Elements are styled based on their semantic context:

- Buttons inside forms get form-appropriate styling
- Links in navigation get nav-appropriate styling
- Inputs in labels get proper association and focus states

### Automatic Dark Mode

Oat automatically picks up dark theme based on system preferences using `prefers-color-scheme`. No JavaScript required.

## Feature Set

### What's Included

- **20+ Components**: Buttons, forms, dialogs, dropdowns, tabs, tables, cards, grids, and more
- **Full Typography System**: Headings, paragraphs, lists, code blocks, blockquotes
- **Form Elements**: All input types with automatic styling and validation states
- **Interactive Components**: Dialogs, dropdowns, tabs using Web Components
- **Feedback UI**: Alerts, toasts, progress bars, spinners, skeleton loaders
- **Layout Tools**: 12-column grid system, sidebar layouts, cards
- **Utilities**: Helper classes for spacing, flexbox, alignment

### What's Not Included

- JavaScript frameworks (React, Vue, Angular, etc.)
- CSS preprocessors (Sass, Less, Stylus)
- Build tools or bundlers
- Icon libraries (use your own SVG icons)
- Font libraries (uses system fonts by default)

## Technical Approach

### Vanilla JavaScript Only

All dynamic components use vanilla JavaScript and Web Components. No framework abstractions:

```javascript
// Tabs component - pure Web Component
class OtTabs extends HTMLElement {
  connectedCallback() {
    // Minimal JS for tab switching
  }
}
customElements.define('ot-tabs', OtTabs);
```

### Native HTML Features

Oat leverages modern HTML features that work without JavaScript:

- `<details>` and `<summary>` for accordions
- `<dialog>` for modals with native focus trapping
- `popover` attribute for dropdowns
- `commandfor` and `command` attributes for dialog control

### CSS Variables for Theming

All colors, spacing, and design tokens are CSS variables:

```css
:root {
  --primary: rgb(24 24 27);
  --primary-foreground: rgb(250 250 250);
  --background: rgb(255 255 255);
  --foreground: rgb(9 9 11);
  /* ... 30+ variables */
}
```

Override any variable to customize the theme.

## Browser Support

Oat supports modern browsers with good HTML/CSS support:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

No IE11 support (by design - keeps bundle size minimal).

## Performance Characteristics

### Bundle Size

- **CSS**: 6KB gzipped
- **JS**: 2.2KB gzipped
- **Total**: ~8KB

For comparison, many popular UI libraries are 100-500KB+ even minified.

### No Runtime Overhead

- No virtual DOM diffing
- No event delegation overhead
- No framework initialization
- Native browser rendering

### Critical CSS

All CSS is critical - no code splitting needed. Styles apply immediately on page load.

## Use Cases

### Ideal For

- Internal tools and dashboards
- Documentation sites
- Small to medium web applications
- Progressive Web Apps (PWAs)
- Projects where bundle size matters
- Teams wanting to avoid JavaScript framework complexity

### Less Ideal For

- Large-scale enterprise applications needing complex state management
- Projects already invested in React/Vue/Angular ecosystems
- Applications requiring highly customized animations
- Teams needing extensive component variant libraries

## Learning Curve

Oat has minimal learning curve:

1. **Day 1**: Include CSS/JS files, start writing semantic HTML
2. **Hour 1**: Learn component patterns (dialogs, dropdowns, tabs)
3. **Day 2**: Customize theme with CSS variables
4. **Week 1**: Master all components and utilities

No build configuration, no component imports, no framework concepts to learn.

## Comparison with Alternatives

| Feature | Oat | Bootstrap | Tailwind | shadcn/ui |
|---------|-----|-----------|----------|-----------|
| Bundle Size | ~8KB | ~150KB | Variable | ~50KB+ |
| Dependencies | 0 | jQuery (optional) | PostCSS | React + deps |
| Build Required | No | No | Yes | Yes |
| Semantic HTML | Yes | Classes | Utilities | React components |
| Dark Mode | Auto | Manual | Manual | Manual |
| Accessibility | Built-in | Partial | Manual | Built-in |

## Getting Started Path

1. **Quick Start**: Include CDN links in HTML file
2. **Explore Components**: Visit https://oat.ink/components
3. **Try Demo**: Play with live examples at https://oat.ink/demo
4. **Read Recipes**: See composable patterns in references/13-recipes.md
5. **Customize Theme**: Override CSS variables per references/03-customization.md

## Community and Support

- **Documentation**: https://oat.ink
- **GitHub Issues**: https://github.com/knadh/oat/issues
- **Source Code**: https://github.com/knadh/oat

The library is maintained by Kailash Nadh (@knadh) with contributions welcome via pull requests.

## Version Status

**Current: 0.6.0** (pre-v1)

Breaking changes may occur until v1.0 release. The API and component structure are stable but not guaranteed immutable.
