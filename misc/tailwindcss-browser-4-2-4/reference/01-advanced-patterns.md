# Advanced Patterns and Limitations

## Contents
- Dynamic Theme Switching
- Multiple Style Blocks
- Conditional Styles with CSS Media Queries
- Combining with Inline Styles
- Preloading the Script
- Limitations
- Comparison with Standard Build

## Dynamic Theme Switching

Use JavaScript to modify `@theme` values at runtime by updating the `text/tailwindcss` style block:

```html
<style type="text/tailwindcss" id="tw-theme">
  @theme {
    --color-primary: oklch(0.6 0.2 250);
  }
</style>

<script>
  function setTheme(hue) {
    document.getElementById('tw-theme').textContent =
      `@theme {\n  --color-primary: oklch(0.6 0.2 ${hue});\n}`;
  }
</script>
```

Changing the style block content triggers a full recompile via the MutationObserver.

## Multiple Style Blocks

You can have multiple `<style type="text/tailwindcss">` blocks — they are concatenated in document order:

```html
<style type="text/tailwindcss">
  @theme {
    --color-primary: blue;
  }
</style>

<style type="text/tailwindcss">
  @utility text-gradient {
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
  }
</style>
```

## Conditional Styles with CSS Media Queries

Use standard CSS media queries inside `text/tailwindcss` blocks:

```html
<style type="text/tailwindcss">
  @theme {
    --color-bg-light: oklch(1 0 0);
    --color-bg-dark: oklch(0.2 0 0);
  }

  @media (prefers-color-scheme: dark) {
    @theme {
      --color-bg-light: oklch(0.2 0 0);
      --color-bg-dark: oklch(1 0 0);
    }
  }
</style>
```

## Combining with Inline Styles

The browser build compiles only classes found on elements. Inline `style` attributes work independently:

```html
<div class="p-4 rounded-lg" style="background: linear-gradient(to right, #6366f1, #8b5cf6);">
  <h2 class="text-white font-bold">Gradient Card</h2>
</div>
```

## Preloading the Script

Reduce initial compile time by preloading the script:

```html
<head>
  <link rel="preload" as="script"
        href="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.2.4/dist/index.global.js">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.2.4/dist/index.global.js"></script>
</head>
```

## Limitations

### No Plugin or Config File Support

The browser build does not support:

- JavaScript plugin files (`@plugin "some-plugin"`)
- Configuration files (`tailwind.config.js`, `tailwind.config.ts`)
- Content path scanning (it scans the DOM instead)
- External stylesheet imports beyond the built-in virtual modules

Attempting to use plugins or config files throws: `The browser build does not support plugins or config files.`

### No Source Maps for Custom CSS

The compiler supports source map generation internally, but the browser build injects CSS directly into a `<style>` tag without source map attachment. Debug custom `@theme` values by inspecting the injected stylesheet in DevTools.

### Performance Considerations

- **Initial page load**: Compiler must parse all Tailwind CSS and scan the DOM before injecting styles
- **Large class sets**: Pages using hundreds of unique Tailwind classes generate larger injected stylesheets
- **Mutation overhead**: Every DOM change that adds or modifies classes triggers incremental recompilation
- **No CSS caching**: Generated CSS exists only in the `<style>` tag — not cached across page loads

### Browser Compatibility

Requires: ES modules, `MutationObserver`, `performance.mark()`, CSS cascade layers (`@layer`), OKLCH color space, CSS custom properties.

Supported in: Chrome 120+, Firefox 128+, Safari 17.4+, Edge 120+.

## Comparison with Standard Build

| Feature | Browser Build | Standard Build (Vite/PostCSS) |
|---------|---------------|-------------------------------|
| Build step | None | Required |
| CSS generation | Runtime (in browser) | Build-time |
| Plugin support | No | Yes |
| Config file | No (CSS-only via `@theme`) | Yes (`tailwind.config.js`) |
| Source maps | No | Yes |
| Purging unused CSS | Automatic (DOM-based) | Content-path based |
| CDN usage | Primary method | Not applicable |
| Production ready | No | Yes |
| Bundle size | ~271KB JS at runtime | Optimized CSS only |
