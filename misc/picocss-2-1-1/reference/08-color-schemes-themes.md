# Color Schemes and Themes

## Light and Dark Modes

Pico ships with two accessible, neutral color schemes: light (default) and dark.

**Automatic detection:** The dark scheme activates automatically when the user's system preference is `prefers-color-scheme: dark`. No JavaScript needed.

**Manual override:** Use the `data-theme` attribute on `<html>` or any element:

```html
<html data-theme="light">
```

```html
<html data-theme="dark">
```

## Scoped Color Schemes

Apply color schemes to specific elements for mixed-light-dark layouts:

```html
<body>
  <article data-theme="dark">
    <h2>Dark section in light page</h2>
  </article>
  <section data-theme="light">
    <h2>Light section override</h2>
  </section>
</body>
```

CSS variables for the color scheme are assigned on every HTML tag. Elements like `<a>`, `<button>`, `<table>`, `<input>`, `<textarea>`, `<select>`, `<article>`, `<dialog>`, and `<progress>` automatically adapt to the scoped theme.

For some elements, explicitly set `background-color` and `color`:

```css
section {
  background-color: var(--pico-background-color);
  color: var(--pico-color);
}
```

## Precompiled Color Themes

Pico v2 ships with 20 handcrafted color themes, each available in light and dark variants (100+ combinations total).

**Available themes:** amber, azure, blue, cyan, fuchsia, green, grey, indigo, jade, lime, orange, pink, pumpkin, purple, red, sand, slate, violet, yellow, zinc.

**CDN usage:**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/indigo/pico.min.css">
```

**Sass usage:**
```scss
@use "pico" with (
  $theme-color: "indigo"
);
```

## Version Picker

Pico provides a version picker tool at `/docs/version-picker` to help select the ideal variant (standard, classless, fluid, theme) for your project.

## Color Scheme CSS Variables

Each color scheme defines its own set of CSS variables. Key differences between light and dark:

**Light mode defaults:**
- `--pico-background-color: #fff`
- `--pico-color: #374151`
- `--pico-primary: #0172ad`

**Dark mode defaults:**
- `--pico-background-color: #181c25`
- `--pico-color: #c9cfd6`
- `--pico-primary: #01aaff`

All themed variables follow the same naming pattern — only values change between schemes.
