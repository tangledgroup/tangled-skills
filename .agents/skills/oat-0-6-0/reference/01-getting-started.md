# Getting Started with OAT v0.6.0

## What is OAT

OAT is an ultra-lightweight, zero-dependency HTML + CSS + JS UI component library. It styles semantic HTML elements by default — no classes needed for basic styling. At approximately 8KB minified (CSS + JS combined), it includes most commonly needed UI components with automatic light/dark mode support via `color-scheme` and `light-dark()`.

Core philosophy: **semantic-first**. Elements are styled contextually based on their HTML semantics, not class names. A `<button>` is a button, a `<table>` is a table — OAT styles them automatically. Dynamic components use Web Components (`<ot-tabs>`, `<ot-dropdown>`) and minimal JavaScript.

## Installation

### CDN (quickest)

Include the minified CSS and JS directly in your HTML:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

The `defer` attribute ensures the script runs after DOM parsing, which is required for the tooltip enhancement and Web Component registration.

### npm / yarn

```bash
npm install @knadh/oat
```

Then import in your project:

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Or import individual files for selective inclusion:

```js
import '@knadh/oat/css/00-base.css';
import '@knadh/oat/css/01-theme.css';
import '@knadh/oat/css/button.css';
// ... other component CSS files
```

### Direct download

```shell
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

Then include locally:

```html
<link rel="stylesheet" href="./oat.min.css">
<script src="./oat.min.js" defer></script>
```

## Basic HTML Template

OAT styles semantic HTML by default. No classes needed:

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

## Dark Mode

OAT has built-in automatic dark mode via the CSS `color-scheme: light dark` declaration and `light-dark()` color function. The browser automatically applies the dark palette when the system preference is set to dark mode.

To explicitly force dark mode, add `data-theme="dark"` to `<body>`:

```html
<body data-theme="dark">
```

To customize the dark theme, scope your CSS variable overrides inside `[data-theme="dark"]`:

```css
[data-theme="dark"] {
  --primary: #6366f1;
  --background: #0f172a;
  /* ... other variables */
}
```

## Selective Component Inclusion

While OAT is tiny enough to include entirely, you can pick and choose components. The required base files are:

- `00-base.css` — Reset, typography, base element styles
- `01-theme.css` — CSS variable definitions (colors, spacing, etc.)
- `base.js` — OtBase Web Component class and command/commandfor polyfill

After these, include only the component CSS/JS files you need:

```js
import '@knadh/oat/css/00-base.css';
import '@knadh/oat/css/01-theme.css';
import '@knadh/oat/css/button.css';
import '@knadh/oat/css/card.css';
// ... your custom CSS after this
```

## Local Development (for contributing to OAT)

### Requirements

- [zola](https://github.com/getzola/zola/releases) — Static site generator for the docs/demo
- [esbuild](https://esbuild.github.io/) — Bundling and minification of CSS/JS

### Running

```bash
git clone https://github.com/knadh/oat.git
cd oat/docs && zola serve   # Docs at http://localhost:1111
# In another terminal:
cd oat && make dist          # Build CSS + JS after changes
```

The demo site auto-updates with CSS/JS changes when `make dist` is run.
