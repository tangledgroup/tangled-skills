# Class-less Version

## Overview

Pico provides a `.classless` variant where zero CSS classes are needed for basic layouts. In this version, `<header>`, `<main>`, and `<footer>` inside `<body>` automatically act as containers — no `class="container"` required.

## CDN Variants

**Centered viewport (default classless):**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css">
```

**Fluid viewport:**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.fluid.classless.min.css">
```

## Semantic Containers

In the classless version, these CSS selectors define containers:

```css
body > header,
body > main,
body > footer {
  /* container styles */
}
```

This means the following two pages produce identical styling:

**With `pico.min.css`:**
```html
<body>
  <main class="container">
    <h1>Hello, world!</h1>
  </main>
</body>
```

**With `pico.classless.min.css`:**
```html
<body>
  <main>
    <h1>Hello, world!</h1>
  </main>
</body>
```

## Custom Root Container (Sass)

For frameworks like React, Gatsby, or Next.js where content renders inside a `#root` div, customize the root element:

```scss
@use "pico" with (
  $semantic-root-element: "#root",
  $enable-semantic-container: true,
  $enable-classes: false
);
```

This compiles containers targeting `#root > header`, `#root > main`, `#root > footer`.

## When to Use Class-less

- Pure HTML projects with no build step
- Maximum minimalism — zero class attributes in markup
- Documentation sites and simple landing pages
- When you want `<header>`, `<main>`, `<footer>` to auto-contain

## Limitations

- `.container` and `.container-fluid` classes are not available
- Button variants (`.secondary`, `.contrast`) are not available
- Grid class (`.grid`) is not available
- All component helper classes are disabled
- Use the standard version when you need these features
