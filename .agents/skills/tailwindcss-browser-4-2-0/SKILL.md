---
name: tailwindcss-browser-4-2-0
description: A skill for using Tailwind CSS v4.2 browser build (@tailwindcss/browser) that enables in-browser Tailwind compilation without a build step. Use when prototyping, creating documentation sites, building static pages, or learning Tailwind CSS without setting up Node.js tooling.
version: "4.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - css
  - tailwind
  - browser
  - prototyping
  - no-build
  - static-sites
  - cdn
category: development

external_references:
  - https://www.npmjs.com/package/@tailwindcss/browser
  - https://github.com/tailwindlabs/tailwindcss
---

# Tailwind CSS Browser Build v4.2

## Overview

The `@tailwindcss/browser` package is the in-browser build of Tailwind CSS v4.2. It compiles Tailwind utility classes directly in the browser at runtime — no Node.js, no bundler, no build step required. You include it via a `<script>` tag or ES module import, write your HTML with Tailwind classes, and the browser generates the needed CSS on the fly.

The package ships as a single global JavaScript file (`dist/index.global.js`, ~271KB uncompressed) that:

- Scans the DOM for elements with `class` attributes
- Collects all class names used on the page
- Compiles only the Tailwind utilities actually referenced
- Injects the resulting CSS into a `<style>` tag in `<head>`
- Watches for DOM mutations and re-compiles incrementally when classes change

This is distinct from the standard `tailwindcss` npm package which requires a build step (Vite, PostCSS, CLI). The browser build is designed for zero-config usage where you want Tailwind utilities available immediately in any HTML file.

## When to Use

- Prototyping interfaces rapidly without project scaffolding
- Building static documentation or markdown-rendered sites
- Creating single-file HTML demos or email templates with live editing
- Learning Tailwind CSS utility classes interactively
- Embedding Tailwind in environments where Node.js tooling is unavailable
- Adding Tailwind to existing static HTML pages without a build pipeline

**Do not use for production applications** that need optimized CSS bundles, critical CSS extraction, or tree-shaking of unused utilities at build time. For those cases, use the standard `tailwindcss` package with Vite, PostCSS, or the CLI.

## How It Works

### Core Mechanism

The browser build uses a special MIME type `text/tailwindcss` to identify `<style>` blocks that contain Tailwind CSS source. On page load:

1. All `<style type="text/tailwindcss">` elements are read and concatenated
2. If no `@import` is found, `@import "tailwindcss";` is prepended automatically
3. The CSS is parsed through Tailwind's Oxide engine (Rust-compiled via WASM)
4. The DOM is scanned for all class names on `[class]` elements
5. Only the utilities matching those class names are compiled
6. Generated CSS is injected into a `<style>` element appended to `<head>`

### Mutation Observing

Two `MutationObserver` instances keep styles in sync:

- **Full rebuild trigger**: Watches for `<style type="text/tailwindcss">` elements being added, removed, or modified. Any change triggers a full re-compile including re-reading all Tailwind CSS source.
- **Incremental rebuild trigger**: Watches the entire document tree for new elements with classes or class attribute changes on `<html>`. Triggers incremental utility compilation using only newly discovered classes.

### Performance Markers

The build uses `performance.mark()` and `performance.measure()` to track timing:

- `Create compiler` — total time to initialize the Tailwind compiler
- `Reading Stylesheets` — time to collect all `text/tailwindcss` style blocks
- `Compile CSS` — time to parse and configure the design system
- `Build #N (full|incremental)` — time for each compilation cycle
- `Collect classes` — time to scan DOM for class names
- `Build utilities` — time to generate CSS from collected classes

View these in browser DevTools → Performance or via `performance.getEntriesByType("measure")`.

## Usage

### Basic Setup

The simplest usage is a single `<style>` block with `type="text/tailwindcss"`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Tailwind Browser Build</title>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js"></script>
</head>
<body>
  <h1 class="text-3xl font-bold text-blue-600">Hello Tailwind</h1>
  <p class="mt-4 text-gray-600 max-w-prose">
    This page uses Tailwind CSS compiled entirely in the browser.
  </p>
</body>
</html>
```

No configuration needed. The script auto-detects classes on the page and generates the required CSS.

### CDN Sources

Load from any major CDN:

- **jsDelivr**: `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js`
- **unpkg**: `https://unpkg.com/@tailwindcss/browser@4/dist/index.global.js`
- **esm.sh**: `https://esm.sh/@tailwindcss/browser@4`

Pin to a specific version for stability:

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.2.4/dist/index.global.js"></script>
```

### Customizing with text/tailwindcss Style Blocks

Use `<style type="text/tailwindcss">` blocks to add custom CSS configuration:

```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.65 0.25 250);
    --font-display: "Georgia", serif;
    --spacing-18: "4.5rem";
  }

  @utility card-shadow {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  }
</style>
```

The `@theme` directive extends Tailwind's design tokens:

- `--color-*` — adds color utilities (`bg-brand`, `text-brand`)
- `--font-*` — adds font family utilities
- `--spacing-*` — adds spacing utilities
- `--breakpoint-*` — adds responsive breakpoints
- `--radius-*` — adds border radius utilities
- `--shadow-*` — adds box shadow utilities

The `@utility` directive creates custom utility classes.

### Theme Reference Mode

Import another stylesheet's theme without emitting its CSS:

```html
<style type="text/tailwindcss">
  @import "./other.css" theme(reference);
</style>
```

Note: The browser build only supports importing the built-in virtual modules:

- `tailwindcss` — full Tailwind (theme + preflight + utilities)
- `tailwindcss/preflight` — reset styles only
- `tailwindcss/theme` — theme CSS variables only
- `tailwindcss/utilities` — utility layer only

External file imports (`@import "./file.css"`) are not supported in the browser build.

### Disabling Preflight

Tailwind's preflight (CSS reset) is included by default. To disable it:

```html
<style type="text/tailwindcss">
  @import "tailwindcss/utilities";
</style>
```

This imports only the utilities layer, skipping preflight and theme defaults.

### Using with Frameworks

The browser build works alongside any framework since it operates purely in the DOM:

**Alpine.js + Tailwind browser build:**

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3"></script>

<div x-data="{ open: false }">
  <button @click="open = !open" class="px-4 py-2 bg-blue-500 text-white rounded">
    Toggle
  </button>
  <div x-show="open" class="mt-2 p-4 bg-gray-100 rounded">
    Content appears here
  </div>
</div>
```

**htmx + Tailwind browser build:**

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2"></script>

<button hx-get="/api/data" hx-target="#result"
        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
  Load Data
</button>
<div id="result" class="mt-4 p-4 border rounded"></div>
```

The mutation observer automatically picks up new classes added by framework interactions.

## Limitations

### No Plugin or Config File Support

The browser build does not support:

- JavaScript plugin files (`@plugin "some-plugin"`)
- Configuration files (`tailwind.config.js`, `tailwind.config.ts`)
- Content path scanning (it scans the DOM instead)
- External stylesheet imports beyond the built-in virtual modules

Attempting to use plugins or config files throws an error:

```
The browser build does not support plugins or config files.
```

### No Source Maps for Custom CSS

While the compiler supports source map generation internally, the browser build injects CSS directly into a `<style>` tag without source map attachment. Debugging custom `@theme` values requires inspecting the injected stylesheet in DevTools.

### Performance Considerations

- **Initial page load**: The compiler must parse all Tailwind CSS and scan the DOM before injecting styles. This adds time to first paint, especially on pages with many elements.
- **Large class sets**: Pages using hundreds of unique Tailwind classes will generate larger injected stylesheets.
- **Mutation overhead**: Every DOM change that adds or modifies classes triggers incremental recompilation. Heavy dynamic content may cause noticeable recompile cycles.
- **No CSS caching**: The generated CSS exists only in the `<style>` tag — it is not cached across page loads like a pre-built CSS file would be.

### Browser Compatibility

The browser build requires modern browser features:

- ES modules or global script execution
- `MutationObserver` API
- `performance.mark()` / `performance.measure()`
- CSS cascade layers (`@layer`)
- OKLCH color space (for the default theme)
- Custom properties (CSS variables)

Supported in all modern browsers (Chrome 120+, Firefox 128+, Safari 17.4+, Edge 120+).

## Advanced Patterns

### Dynamic Theme Switching

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

### Multiple Style Blocks

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

### Conditional Styles with CSS Media Queries

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

### Combining with Inline Styles

The browser build compiles only classes found on elements. Inline `style` attributes work independently:

```html
<div class="p-4 rounded-lg" style="background: linear-gradient(to right, #6366f1, #8b5cf6);">
  <h2 class="text-white font-bold">Gradient Card</h2>
</div>
```

### Preloading the Script

Reduce initial compile time by preloading the script:

```html
<head>
  <link rel="preload" as="script"
        href="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js"></script>
</head>
```

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
