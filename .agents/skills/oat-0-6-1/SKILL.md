---
name: oat-0-6-1
description: Ultra-lightweight semantic UI component library with zero dependencies (~8KB). Use when building web applications with vanilla HTML/CSS/JS, needing accessible components without framework overhead or build tools.
version: "0.6.1"
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
external_references:
  - https://oat.ink
  - https://github.com/knadh/oat
---

# Oat UI 0.6.1

## Overview

Oat is an ultra-lightweight HTML + CSS + minimal JS semantic UI component library with zero dependencies. At approximately **6KB CSS** and **2.2KB JS** (minified + gzipped), it provides most commonly needed UI components without any framework, build step, or Node.js ecosystem complexity.

Key characteristics:

- **Semantic HTML first** — native elements like `<button>`, `<input>`, `<dialog>` and semantic attributes like `role="button"` are styled directly without classes
- **Zero dependencies** — fully standalone, no JS or CSS framework requirements
- **Accessibility built-in** — ARIA roles, keyboard navigation, and semantic markup throughout
- **CSS cascade layers** — uses `@layer` for clean style isolation
- **Automatic dark mode** — picks up system preferences via `color-scheme: light dark` and `light-dark()` values
- **WebComponents for dynamic behavior** — dropdowns, tabs use minimal JS; most styling is pure CSS
- **shadcn-inspired aesthetic** — clean, modern look and feel

Published under MIT license by Kailash Nadh. Currently sub-v1 and subject to breaking changes.

## When to Use

- Building web applications with vanilla HTML/CSS/JS (no framework)
- Needing accessible UI components without framework overhead
- Creating documentation sites, admin panels, or internal tools where minimal bundle size matters
- Wrapping web interfaces in native windows (e.g., pywebview)
- Projects that must avoid Node.js build toolchains
- Migrating away from heavy CSS frameworks to reduce class pollution

## Installation / Setup

Three methods to include Oat:

**CDN (simplest):**

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

**npm:**

```bash
npm install @knadh/oat
```

```javascript
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Or import individual files from `@knadh/oat/css` and `@knadh/oat/js`.

**Download:**

```bash
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

Then include locally:

```html
<link rel="stylesheet" href="./oat.min.css">
<script src="./oat.min.js" defer></script>
```

## Basic Usage

Oat styles semantic HTML elements by default. No classes needed for basic styling:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="oat.css">
  <script src="oat.js" defer></script>
</head>
<body>
  <h1>Hello World</h1>
  <p>This paragraph is styled automatically.</p>
  <button>Click me</button>
</body>
</html>
```

## Core Concepts

**Semantic styling without classes:** Most Oat components work by styling native HTML elements and ARIA attributes directly. A `<button>` gets button styles automatically. `role="alert"` on a `<div>` gives alert styling. No utility classes needed for basic usage.

**CSS cascade layers:** Oat uses `@layer` to organize styles into `theme`, `base`, `components`, `animations`, and `utilities`. This means custom CSS can override cleanly without specificity wars.

**CSS variables for theming:** Every color, spacing, radius, font size, and shadow is a CSS variable on `:root`. Override in your own stylesheet loaded after Oat's CSS.

**Progressive enhancement for tooltips:** The `title` attribute works natively without JS. When oat.min.js loads, it converts `title` to styled `data-tooltip` attributes with smooth transitions.

**WebComponents for dynamic components:** Only dropdowns (`<ot-dropdown>`) and tabs (`<ot-tabs>`) require JavaScript. Toast notifications use the global `ot.toast()` API. Everything else is pure CSS.

## Customization

All properties are CSS variables defined in theme.css. Override by redefining them in a CSS file included after Oat's CSS:

```css
:root {
  --primary: #6366f1;
  --primary-foreground: #ffffff;
  --radius-medium: 0.5rem;
}
```

**Dark mode:** Add `data-theme="dark"` to `<body>` or scope overrides inside `[data-theme="dark"] { ... }`. Oat uses `light-dark()` for automatic system preference detection.

**Selective inclusion:** Instead of the full bundle, include individual CSS files from `@knadh/oat/css/`:

Must-include base files:
- `00-base.css`
- `01-theme.css`
- `base.js`

Then add component-specific CSS and JS as needed.

## Advanced Topics

**All Components**: Typography, accordion, alert, avatar, badge, breadcrumb, button, card, dialog, dropdown, form elements, meter, pagination, progress, spinner, skeleton, sidebar, switch, table, tabs, tooltip, toast, grid → [Components Reference](reference/01-components.md)

**CSS Variables and Theming**: Complete variable reference, dark mode setup, custom themes → [Theming Reference](reference/02-theming.md)

**JavaScript API and Extensions**: Toast API, WebComponent details, third-party extensions → [JS API and Extensions](reference/03-js-api-extensions.md)
