# Migration Guide and Troubleshooting

## Contents
- Migration from Tailwind v3
- Troubleshooting

## Migration from Tailwind v3

When migrating a v3 project to the browser build of v4:

1. **Remove `tailwind.config.js`** — configuration moves into `@theme` blocks in `<style type="text/tailwindcss">`
2. **Replace `@tailwind base/components/utilities`** with `@import "tailwindcss"` (or specific imports)
3. **Move custom colors** from `theme.extend.colors` to `@theme { --color-* }`
4. **Move custom fonts** from `theme.extend.fontFamily` to `@theme { --font-* }`
5. **Replace arbitrary values** where possible with named theme tokens
6. **Check for removed utilities** — some v3 utilities were renamed or removed in v4

Example migration:

```html
<!-- Before (v3 with build step) -->
<!-- tailwind.config.js: { theme: { extend: { colors: { brand: '#6366f1' } } } } -->
<div class="bg-brand text-white">...</div>

<!-- After (v4 browser build) -->
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.65 0.25 250);
  }
</style>
<div class="bg-brand text-white">...</div>
```

## Troubleshooting

### Styles Not Applying

Check that the script loads before the DOM renders:

```html
<head>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js"></script>
</head>
```

If loading in `<body>` or with `defer`, the initial class scan may miss elements. The mutation observer will catch them on next DOM change, but there can be a flash of unstyled content.

### Flash of Unstyled Content (FOUC)

The browser compiles CSS after the script executes. To minimize FOUC:

- Load the script in `<head>` before any body content
- Use `preload` hint for the script
- Consider critical CSS inline for above-the-fold content

### Classes Added Dynamically Not Styling

The mutation observer watches for:

- New elements added to the DOM with `class` attributes
- Changes to the `class` attribute on existing elements
- Changes to `<html>` element's class

If you're using `classList.add()` or setting `element.className`, the observer should detect it. If styles don't update, check that the mutation is happening on an observed subtree (the entire `document.documentElement` is observed).

### Custom Theme Not Taking Effect

Ensure the `text/tailwindcss` style block uses correct CSS custom property names:

```html
<!-- Correct -->
<style type="text/tailwindcss">
  @theme {
    --color-myblue: oklch(0.5 0.2 240);
  }
</style>
<div class="bg-myblue">Works</div>

<!-- Wrong — missing --color- prefix -->
<style type="text/tailwindcss">
  @theme {
    myblue: oklch(0.5 0.2 240);
  }
</style>
```

### OKLCH Color Support

The default Tailwind theme uses OKLCH color values. If your browser doesn't support OKLCH, colors will fall back to the nearest supported value. Check support with:

```js
CSS.supports('color', 'oklch(0.5 0.2 240)')
```

For broader compatibility, define theme colors in hex or rgb:

```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: #6366f1;
  }
</style>
```
