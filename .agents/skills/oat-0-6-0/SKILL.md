---
name: oat-0-6-0
description: Ultra-lightweight semantic UI component library (~8KB CSS + JS, zero dependencies) that styles HTML elements by default without classes. Provides 27 components including buttons, forms, cards, dialogs, tabs, dropdowns, toasts, tooltips, grids, and sidebar layouts with automatic light/dark mode. Use when building web applications with minimal CSS/JS footprint, semantic-first markup, no build tools, or when replacing heavier frameworks like Bootstrap or Tailwind for simple UI needs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - javascript
  - css
  - frontend
  - ui-components
  - semantic-html
  - web-components
  - lightweight
  - zero-dependency
  - theming
  - responsive
category: frontend-development
external_references:
  - https://oat.ink/
  - https://github.com/knadh/oat/tree/v0.6.0
---

# OAT v0.6.0

## Overview

OAT is an ultra-lightweight HTML + CSS + JS UI component library with zero dependencies. At approximately 8KB minified (CSS and JS combined), it provides most commonly needed UI components while keeping the bundle tiny.

**Core philosophy: semantic-first.** OAT styles HTML elements based on their semantics, not class names. A `<button>` is styled as a button, a `<table>` as a table, a `<details>` as an accordion — no classes required. This forces best practices and eliminates markup class pollution. Dynamic components use Web Components (`<ot-tabs>`, `<ot-dropdown>`) with minimal JavaScript built on native browser APIs (Popover API, `<dialog>`, `<menu>`).

OAT uses CSS `@layer` cascade layers for predictable style organization, CSS custom properties for complete theming, and `light-dark()` for automatic system dark mode. It supports progressive enhancement — tooltips work with native `title` even without JavaScript.

## When to Use

- Building web applications where bundle size matters (internal tools, documentation sites, lightweight dashboards)
- Projects that prefer semantic HTML over class-heavy markup
- Replacing Bootstrap, Bulma, or other heavier CSS frameworks
- Applications needing automatic light/dark mode without extra configuration
- Prototyping or small projects without build tooling
- When you want components that work with plain HTML and minimal JS

## Installation and Setup

### CDN (quickest start)

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

Use `defer` on the script to ensure it runs after DOM parsing (required for tooltip enhancement and Web Component registration).

### npm

```bash
npm install @knadh/oat
```

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

For selective inclusion, import individual files from `@knadh/oat/css` and `@knadh/oat/js`.

### Direct download

```shell
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

## Basic Usage

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="oat.min.css">
</head>
<body>
  <h1>Hello World</h1>
  <p>This paragraph is styled automatically.</p>
  <button>Click me</button>
  <script src="oat.min.js" defer></script>
</body>
</html>
```

No classes needed. Headings, paragraphs, buttons, forms, tables — all styled by default.

## Core Concepts

### Semantic HTML Styling

OAT targets elements by their HTML tag or role, not by class:

- `<button>` → Styled button
- `<table>` with `<thead>`/`<tbody>` → Styled data table
- `<details>`/`<summary>` → Accordion
- `<dialog>` → Modal dialog
- `<progress>` → Progress bar
- `<meter>` → Gauge meter
- `role="alert"` → Alert banner
- `role="switch"` on checkbox → Toggle switch
- `aria-busy="true"` → Loading spinner

This means your markup is cleaner, more accessible, and works even if OAT CSS fails to load (browser defaults apply).

### CSS Cascade Layers

OAT organizes styles into 5 cascade layers for predictable specificity:

```css
@layer theme, base, components, animations, utilities;
```

1. **theme** — CSS variable definitions in `:root`
2. **base** — Reset, typography, form elements
3. **components** — Component-specific styles
4. **animations** — Keyframes and transitions
5. **utilities** — Helper classes

Your custom CSS (without `@layer`) always wins over all OAT layers.

### CSS Variable Theming

Every visual property is a CSS custom property. Override in your own CSS:

```css
:root {
  --primary: #6366f1;
  --radius-medium: 0.5rem;
}
```

See reference/03-theme-and-customization.md for the complete variable catalog (50+ variables covering colors, spacing, typography, shadows, and transitions).

### Progressive Enhancement

- Tooltips work with native `title` attribute even without JavaScript
- JavaScript enhances `title` → styled `data-tooltip` via MutationObserver
- Dialog uses `commandfor`/`command` attributes (Safari polyfill included)
- Dropdowns use native Popover API
- All animations respect `prefers-reduced-motion: reduce`

### Dark Mode

Automatic via `color-scheme: light dark` and `light-dark()` CSS function. Force dark mode with `data-theme="dark"` on `<body>`. Customize dark theme by scoping overrides in `[data-theme="dark"] { ... }`.

## Component Quick Reference

### Static Components (CSS only, no JS required)

| Component | Trigger | Key Attributes/Classes | Variants |
|-----------|---------|----------------------|----------|
| Accordion | `<details>` / `<summary>` | `name` for grouping | — |
| Alert | `[role="alert"]` | `data-variant="success\|warning\|error\|danger"` | success, warning, error, danger |
| Avatar | `<figure data-variant="avatar">` | `.small`, `.large`, `role="group"` | small, default, large |
| Badge | `.badge` | `.secondary`, `.outline`, `.success`, `.warning`, `.danger` | secondary, outline, success, warning, danger |
| Breadcrumb | `<nav>` + `<ol class="unstyled hstack">` | `aria-current="page"` | — |
| Button | `<button>`, `<a class="button">` | `data-variant="secondary\|danger"`, `.outline`, `.ghost` | secondary, danger, outline, ghost |
| Button Sizes | — | `.small`, `.large`, `.icon` | small, default, large, icon |
| Button Group | `<menu class="buttons">` + `<li><button>` | — | — |
| Card | `.card` (on `<article>`) | — | — |
| Meter | `<meter>` | `min`, `max`, `low`, `high`, `optimum` | — |
| Pagination | `<nav>` + `<menu class="buttons">` | `aria-current="page"`, `.small`, `.outline` | — |
| Progress | `<progress>` | `value`, `max` | — |
| Skeleton | `[role="status"].skeleton` | `.line`, `.box` | line, box |
| Spinner | `[aria-busy="true"]` | `data-spinner="small\|large\|overlay"` | small, default, large, overlay |
| Switch | `<input type="checkbox" role="switch">` | — | — |
| Table | `<table>` + `.table` wrapper | `<thead>`, `<tbody>` | — |

### Dynamic Components (require oat.min.js)

| Component | Element | JS API / Events | Key Features |
|-----------|---------|----------------|-------------|
| Dialog | `<dialog>` + `commandfor`/`command` | `dialog.returnValue`, `close` event | Focus trapping, backdrop, Escape close, Safari polyfill |
| Dropdown | `<ot-dropdown>` + `[popover]` | — | Auto-positioning, flip on overflow, keyboard nav (ArrowUp/Down/Home/End) |
| Tabs | `<ot-tabs>` + `[role="tablist"]` | `activeIndex` getter/setter, `ot-tab-change` event | ARIA management, ArrowLeft/Right nav |
| Toast | — | `ot.toast(msg, title?, opts?)`, `ot.toast.el(el, opts?)`, `ot.toast.clear(placement?)` | 6 placements, 3 variants, auto-dismiss, hover pause, custom HTML |
| Tooltip | `[title]` → `[data-tooltip]` | `data-tooltip-placement="top\|bottom\|left\|right"` | 700ms delay, progressive enhancement |

## Theming and Customization

### Override CSS Variables

Create a custom CSS file and include it **after** OAT's CSS:

```html
<link rel="stylesheet" href="oat.min.css">
<link rel="stylesheet" href="my-theme.css">
```

```css
/* my-theme.css */
:root {
  --primary: #6366f1;
  --primary-foreground: #ffffff;
  --radius-medium: 0.5rem;
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

### Dark Mode Customization

```css
[data-theme="dark"] {
  --primary: #818cf8;
  --background: #0f172a;
  --card: #1e293b;
}
```

### Selective Inclusion

For minimal bundles, include only what you need. Required base files:

- `00-base.css` — Reset and typography
- `01-theme.css` — CSS variables
- `base.js` — OtBase class and polyfills

Then add component files as needed:

```js
import '@knadh/oat/css/00-base.css';
import '@knadh/oat/css/01-theme.css';
import '@knadh/oat/css/button.css';
import '@knadh/oat/css/card.css';
import '@knadh/oat/js/base.js';
```

## Layout and Forms

### Grid System

12-column responsive grid using CSS Grid:

```html
<div class="container">
  <div class="row">
    <div class="col-4">Sidebar</div>
    <div class="col-8">Main content</div>
  </div>
  <div class="row">
    <div class="col-3">A</div>
    <div class="col-6">B</div>
    <div class="col-3">C</div>
  </div>
</div>
```

Classes: `.container`, `.row`, `.col-{1-12}`, `.offset-{1-6}`, `.col-end`. At 768px and below, columns stack to full width.

### Form Elements

All form elements styled automatically. Wrap in `<label data-field>` for proper spacing and hint support:

```html
<label data-field>
  Email
  <input type="email" placeholder="you@example.com" />
</label>
```

Supported inputs: text, email, password, url, date, datetime-local, file, range, checkbox, radio, select, textarea.

### Input Groups

Combine inputs with `fieldset.group`:

```html
<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

### Validation Errors

Use `data-field="error"` to reveal error messages:

```html
<div data-field="error">
  <label for="email">Email</label>
  <input type="email" id="email" aria-invalid="true" value="bad" />
  <div class="error" role="status">Invalid email address.</div>
</div>
```

### Sidebar Layout

Responsive admin layout with sticky sidebar:

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle class="outline">&#9776;</button>
    <span>App Name</span>
  </nav>
  <aside data-sidebar>
    <header>Logo</header>
    <nav><ul><li><a href="#">Home</a></li></ul></nav>
    <footer><button class="outline">Logout</button></footer>
  </aside>
  <main>Page content here.</main>
</body>
```

Use `data-sidebar-layout="always"` for always-collapsible sidebar at all screen sizes. Mobile (&le;768px): sidebar becomes slide-out overlay.

## JavaScript API

### Toast Notifications

```javascript
// Text toast
ot.toast('Saved successfully', 'Success', { variant: 'success' });
ot.toast('Error occurred', 'Oops', { variant: 'danger', placement: 'bottom-center' });
ot.toast('Warning message', '', { variant: 'warning', duration: 6000 });

// Custom HTML toast
ot.toast.el(document.querySelector('#my-template'), { duration: 8000, placement: 'top-center' });

// Clear toasts
ot.toast.clear();              // All placements
ot.toast.clear('top-right');   // Specific placement
```

**Options**: `variant` (`'success'`, `'danger'`, `'warning'`), `placement` (6 positions, default `'top-right'`), `duration` (ms, default 4000, 0 = persistent).

### Tabs Programmatic Control

```javascript
const tabs = document.querySelector('ot-tabs');
tabs.activeIndex = 2; // Switch to third tab
console.log(tabs.activeIndex); // Current index

tabs.addEventListener('ot-tab-change', (e) => {
  console.log('Switched to tab:', e.detail.index);
});
```

### Dialog Return Value

```javascript
const dialog = document.querySelector('#my-dialog');
dialog.addEventListener('close', () => {
  console.log(dialog.returnValue); // Value of the submitted button
});
```

### OtBase (Web Component Base Class)

All OAT Web Components extend `OtBase` which provides:

- `connectedCallback` / `disconnectedCallback` lifecycle
- `handleEvent(event)` — Central event handler with auto-cleanup (`this.onclick`, etc.)
- `keyNav(event, idx, len, prevKey, nextKey, homeEnd)` — Roving keyboard navigation helper
- `emit(name, detail)` — Fire custom events
- `$(selector)` / `$$(selector)` — Query helpers
- `uid()` — Unique ID generator

## Recipes and Extensions

### Common Patterns

- **Split button**: `<menu class="buttons">` + `<ot-dropdown>` for primary action + overflow menu
- **Form card**: `<article class="card">` wrapping form fields with header/footer
- **Empty state**: Card with `.align-center`, muted text, and CTA button
- **Stats dashboard**: Grid of cards with badges, metrics, and progress/meter bars

See reference/08-recipes-and-patterns.md for full markup examples.

### Community Extensions

- **oat-chips** — Chip/tag component (~1KB gzipped)
- **oat-animate** — Declarative animation triggers (~1KB gzipped)

### Companion Libraries (same author, zero-dependency)

- **tinyrouter.js** (~950B) — Frontend routing
- **highlighted-input.js** (~450B) — Keyword highlighting in inputs
- **floatype.js** (~1.2KB) — Floating autocomplete
- **dragmove.js** (~500B) — Draggable elements
- **indexed-cache.js** (~2.1KB) — IndexedDB asset caching

## Utility Classes

| Category | Classes |
|----------|---------|
| Flexbox | `.flex`, `.flex-col`, `.items-center`, `.justify-center`, `.justify-between`, `.justify-end` |
| Stacks | `.hstack` (horizontal with gap), `.vstack` (vertical with gap) |
| Alignment | `.align-left`, `.align-center`, `.align-right` |
| Text | `.text-light`, `.text-lighter` |
| Gaps | `.gap-1`, `.gap-2`, `.gap-4` |
| Margins | `.mt-2`, `.mt-4`, `.mt-6`, `.mb-2`, `.mb-4`, `.mb-6` |
| Padding | `.p-4` |
| Width | `.w-100` |
| Reset | `.unstyled` (removes list styles and link decoration) |

## Advanced Topics

**Getting Started**: Installation methods, basic template, dark mode, selective inclusion → [Getting Started](reference/01-getting-started.md)
**Typography and Base**: Cascade layers, reset defaults, heading scale, code/blockquote/lists → [Typography and Base](reference/02-typography-and-base.md)
**Theme Variables**: Complete CSS variable catalog (50+ variables) with override patterns → [Theme and Customization](reference/03-theme-and-customization.md)
**Static Components**: 14 CSS-only components (accordion, alert, avatar, badge, button, card, etc.) → [Static Components](reference/04-components-static.md)
**Dynamic Components**: Dialog, dropdown, tabs, toast API, tooltip enhancement with full JS details → [Dynamic Components](reference/05-components-dynamic.md)
**Layout and Forms**: 12-column grid, form elements, input groups, validation, sidebar layout → [Layout and Forms](reference/06-layout-and-forms.md)
**Utilities and Helpers**: Flexbox, stacks, margins, animation classes, reduced motion → [Utilities and Helpers](reference/07-utilities-and-helpers.md)
**Recipes and Extensions**: Composable patterns, community extensions, companion libraries → [Recipes and Patterns](reference/08-recipes-and-patterns.md)

## Browser Support

OAT uses modern CSS features including `@layer`, `light-dark()`, `color-mix()`, `@starting-style`, nested CSS rules, and the Popover API. These require modern browsers (Chrome 120+, Firefox 128+, Safari 17.4+). The `commandfor`/`command` polyfill provides dialog support in Safari versions lacking native command API support.
