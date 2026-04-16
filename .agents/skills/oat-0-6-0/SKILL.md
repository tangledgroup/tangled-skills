---
name: oat-0-6-0
description: Ultra-lightweight semantic UI component library with zero dependencies (~8KB). Use when building web applications with vanilla HTML/CSS/JS, needing accessible components without framework overhead or build tools.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - ui-library
  - css-framework
  - semantic-html
  - zero-dependency
  - webcomponents
  - accessible
  - lightweight
  - vanilla-js
category: frontend
required_environment_variables: []
---

# Oat UI 0.6.0

Ultra-lightweight HTML + CSS semantic UI component library with zero dependencies. ~6KB CSS and ~2.2KB JS (minified + gzipped). No framework, build tools, or dev complexity required.

## When to Use

- Building web applications with vanilla HTML/CSS/JS
- Needing accessible, semantic components without framework overhead
- Projects requiring minimal bundle size (< 10KB total)
- Avoiding Node.js ecosystem dependencies and build tools
- Creating responsive UIs with automatic dark mode support
- Preferring native HTML elements over custom classes

## Quick Start

### CDN Installation (Fastest)

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

### npm Installation

```bash
npm install @knadh/oat
```

```javascript
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

### Download Files

```bash
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

## Basic Usage

Oat styles semantic HTML elements automatically. No classes needed for basic styling:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="oat.min.css">
  <script src="oat.min.js" defer></script>
</head>
<body>
  <h1>Hello World</h1>
  <p>This paragraph is styled automatically.</p>
  <button>Click me</button>
</body>
</html>
```

## Core Principles

- **Semantic HTML First**: Native elements like `<button>`, `<input>`, `<dialog>` are styled directly without classes
- **Zero Dependencies**: No JavaScript frameworks, CSS preprocessors, or build tools required
- **Accessibility Built-in**: ARIA roles and keyboard navigation work out of the box
- **Automatic Dark Mode**: Picks up system preferences automatically
- **Web Components**: Dynamic components use minimal vanilla JavaScript

## Component Overview

Oat provides 20+ components covering common UI patterns:

### Layout & Structure
- Grid system (12-column responsive)
- Sidebar layouts with mobile toggle
- Cards and containers

### Form Elements
- Inputs, textareas, selects with automatic styling
- Field validation and error states
- Checkboxes, radio buttons, range sliders
- File uploads and date/time pickers

### Interactive Components
- Dialogs (zero-JS modals using `<dialog>`)
- Dropdowns with popover support
- Tabs with Web Components
- Accordions using native `<details>`

### Feedback & Status
- Alerts (success, warning, error)
- Progress bars and meters
- Spinners and skeleton loaders
- Toast notifications

### Navigation
- Buttons with variants and groups
- Pagination
- Breadcrumbs
- Badges

### Data Display
- Tables with responsive containers
- Avatars (individual and grouped)
- Typography system

### Utilities
- Tooltips with placement options
- Switch toggles
- Helper classes for spacing, alignment, flexbox

## Reference Files

Comprehensive documentation organized by topic:

### Core Documentation
- [`references/01-introduction.md`](references/01-introduction.md) - Philosophy, features, and design principles
- [`references/02-installation.md`](references/02-installation.md) - CDN, npm, download options and setup
- [`references/03-customization.md`](references/03-customization.md) - CSS variables, theming, dark mode customization

### Component Documentation
- [`references/04-typography.md`](references/04-typography.md) - Headings, paragraphs, lists, code blocks
- [`references/05-buttons.md`](references/05-buttons.md) - Button variants, sizes, groups, and states
- [`references/06-forms.md`](references/06-forms.md) - Input fields, validation, error states, fieldsets
- [`references/07-dialogs.md`](references/07-dialogs.md) - Modal dialogs, forms in dialogs, return values
- [`references/08-dropdowns-tabs.md`](references/08-dropdowns-tabs.md) - Dropdown menus, popover dropdowns, tab components
- [`references/09-layout-components.md`](references/09-layout-components.md) - Cards, grids, sidebars, containers
- [`references/10-feedback-components.md`](references/10-feedback-components.md) - Alerts, toasts, progress, spinners, skeletons
- [`references/11-data-display.md`](references/11-data-display.md) - Tables, avatars, badges, meters
- [`references/12-navigation.md`](references/12-navigation.md) - Breadcrumbs, pagination, navigation patterns

### Advanced Topics
- [`references/13-recipes.md`](references/13-recipes.md) - Composable widget examples (split buttons, form cards, stats cards)
- [`references/14-utilities.md`](references/14-utilities.md) - Helper classes for spacing, flexbox, alignment

### Ecosystem
- [`references/15-tinyrouter-js.md`](references/15-tinyrouter-js.md) - Frontend routing (~950 bytes)
- [`references/16-highlighted-input-js.md`](references/16-highlighted-input-js.md) - Keyword highlighting in inputs (~450 bytes)
- [`references/17-floatype-js.md`](references/17-floatype-js.md) - Floating autocomplete for textareas (~1200 bytes)
- [`references/18-dragmove-js.md`](references/18-dragmove-js.md) - Draggable DOM elements (~500 bytes)
- [`references/19-indexed-cache-js.md`](references/19-indexed-cache-js.md) - Static asset caching in IndexedDB (~2.1KB)
- [`references/20-extensions.md`](references/20-extensions.md) - Third-party extensions (oat-chips, oat-animate)

## Common Patterns

### Button with Icon

```html
<button>
  Save
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
  </svg>
</button>
```

### Form with Validation

```html
<form>
  <label data-field>
    Email
    <input type="email" required />
  </label>
  
  <label data-field>
    Password
    <input type="password" aria-describedby="password-hint" />
    <small id="password-hint" data-hint>Minimum 8 characters</small>
  </label>
  
  <button type="submit">Submit</button>
</form>
```

### Error State

```html
<div data-field="error">
  <label for="email">Email</label>
  <input type="email" id="email" aria-invalid="true" aria-describedby="error-msg" />
  <div id="error-msg" class="error" role="status">Please enter a valid email.</div>
</div>
```

### Modal Dialog

```html
<button commandfor="my-dialog" command="show-modal">Open Dialog</button>

<dialog id="my-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Confirm Action</h3>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

## Troubleshooting

### Styles Not Applying
- Ensure CSS file loads before page content
- Check for conflicting CSS in your project
- Verify `defer` attribute on script tag

### Dark Mode Issues
- Dark mode auto-detects system preferences via `prefers-color-scheme`
- Force dark mode: add `data-theme="dark"` to `<body>`
- Customize dark theme variables in `[data-theme="dark"] { ... }`

### Component Not Working
- Verify oat.min.js is loaded with `defer` attribute
- Check browser console for JavaScript errors
- Ensure semantic HTML structure matches documentation

### Custom Theme Overriding
- Include custom CSS **after** oat.min.css
- Use `!important` sparingly; CSS variables should override cleanly

## Resources

- **Official Documentation**: https://oat.ink
- **GitHub Repository**: https://github.com/knadh/oat
- **npm Package**: https://www.npmjs.com/package/@knadh/oat
- **Live Demo**: https://oat.ink/demo

## Version Notes

**Current version: 0.6.0** (pre-v1, breaking changes possible until v1.0)

For detailed information on any topic, see the reference files listed above. Each component and feature has comprehensive documentation with examples in the `references/` directory.
