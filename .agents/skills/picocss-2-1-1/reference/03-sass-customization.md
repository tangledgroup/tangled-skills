# Sass Customization

## Overview

Pico is built with Sass. Compiling your own version lets you include only required modules, change settings, and customize without overriding CSS styles. Never modify Pico's core files directly — keep custom code separate so updates are conflict-free.

## Import Methods

**Standard @use (with load path):**
```scss
@use "pico";
```

Compile with:
```bash
sass --load-path=node_modules/@picocss/pico/scss/ styles.scss output.css
```

**With Webpack + sass-loader or React:**
```scss
@use "@picocss/pico/scss/pico";
```

The bundler auto-resolves `node_modules`.

## Settings Reference

Override defaults with `@use "pico" with ( ... )`:

### Theme Color
```scss
$theme-color: "azure" !default;
```
Available themes: amber, azure, blue, cyan, fuchsia, green, grey, indigo, jade, lime, orange, pink, pumpkin, purple, red, sand, slate, violet, yellow, zinc.

### CSS Variable Prefix
```scss
$css-var-prefix: "--pico-" !default;
```
Must start with `--`.

### Semantic Container
```scss
$semantic-root-element: "body" !default;
$enable-semantic-container: false !default;
$enable-viewport: true !default;
```
- `$semantic-root-element` — root element for targeting `<header>`, `<main>`, `<footer>`
- `$enable-semantic-container` — enable landmark elements as containers (classless mode)
- `$enable-viewport` — centered viewport for landmarks; fluid if disabled

### Responsive Features
```scss
$enable-responsive-spacings: false !default;
$enable-responsive-typography: true !default;
```
- `$enable-responsive-spacings` — responsive padding on `<header>`, `<main>`, `<footer>`, `<section>`, `<article>`
- `$enable-responsive-typography` — fluid font sizes across breakpoints (enabled by default)

### Classes and Transitions
```scss
$enable-classes: true !default;
$enable-transitions: true !default;
$enable-important: true !default;
```
- `$enable-classes` — disable for classless version
- `$enable-transitions` — hover/focus transitions
- `$enable-important` — use `!important` in overrides

### Parent Selector
```scss
$parent-selector: "" !default;
```
Optional wrapper selector. If set, all HTML tag rules are scoped inside it (`:root` is not wrapped).

### Breakpoints
```scss
$breakpoints: (
  sm: (breakpoint: 576px, viewport: 510px, root-font-size: 106.25%),
  md: (breakpoint: 768px, viewport: 700px, root-font-size: 112.5%),
  lg: (breakpoint: 1024px, viewport: 950px, root-font-size: 118.75%),
  xl: (breakpoint: 1280px, viewport: 1200px, root-font-size: 125%),
  xxl: (breakpoint: 1536px, viewport: 1450px, root-font-size: 131.25%),
);
```

## Modules

Control which CSS modules are compiled via `$modules`:

```scss
$modules: (
  // Theme
  "themes/default": true,

  // Layout
  "layout/document": true,
  "layout/landmarks": true,
  "layout/container": true,
  "layout/section": true,
  "layout/grid": true,
  "layout/overflow-auto": true,

  // Content
  "content/link": true,
  "content/typography": true,
  "content/embedded": true,
  "content/button": true,
  "content/table": true,
  "content/code": true,
  "content/figure": true,
  "content/misc": true,

  // Forms
  "forms/basics": true,
  "forms/checkbox-radio-switch": true,
  "forms/input-color": true,
  "forms/input-date": true,
  "forms/input-file": true,
  "forms/input-range": true,
  "forms/input-search": true,

  // Components
  "components/accordion": true,
  "components/card": true,
  "components/dropdown": true,
  "components/group": true,
  "components/loading": true,
  "components/modal": true,
  "components/nav": true,
  "components/progress": true,
  "components/tooltip": true,

  // Utilities
  "utilities/accessibility": true,
  "utilities/reduce-motion": true,
);
```

Set any module to `false` to exclude it from the build, reducing output size.

## Complete Customization Example

```scss
@use "pico" with (
  $theme-color: "indigo",
  $enable-responsive-spacings: true,
  $enable-classes: true,
  $modules: (
    "components/modal": false,
    "components/tooltip": false,
  )
);
```

## Precompiled Themes

Pico ships with 20 precompiled color themes (amber, azure, blue, cyan, fuchsia, green, grey, indigo, jade, lime, orange, pink, pumpkin, purple, red, sand, slate, violet, yellow, zinc), each with light and dark variants available via CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/indigo/pico.min.css">
```
