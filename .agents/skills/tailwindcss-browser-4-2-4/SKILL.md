---
name: tailwindcss-browser-4-2-4
description: In-browser Tailwind CSS v4.2 build (@tailwindcss/browser) that compiles utility classes at runtime without a build step. Use when prototyping, creating documentation sites, building static pages, or learning Tailwind CSS without setting up Node.js tooling. Not for production applications requiring optimized CSS bundles.
version: "0.1.0"
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

# Tailwind CSS Browser Build v4.2.4

## Overview

The `@tailwindcss/browser` package is the in-browser build of Tailwind CSS v4.2. It compiles Tailwind utility classes directly in the browser at runtime — no Node.js, no bundler, no build step. Include via `<script>` tag, write HTML with Tailwind classes, and the browser generates needed CSS on the fly.

The package ships as a single global JS file (~271KB uncompressed) that scans the DOM for class names, compiles only referenced utilities, injects CSS into `<head>`, and watches for DOM mutations to re-compile incrementally.

**Do not use for production applications** requiring optimized CSS bundles, critical CSS extraction, or tree-shaking. Use the standard `tailwindcss` package with Vite/PostCSS/CLI for those cases.

## When to Use

- Prototyping interfaces rapidly without project scaffolding
- Building static documentation or markdown-rendered sites
- Creating single-file HTML demos or email templates with live editing
- Learning Tailwind CSS utility classes interactively
- Embedding Tailwind where Node.js tooling is unavailable
- Adding Tailwind to existing static HTML pages without a build pipeline

## How It Works

### Core Mechanism

The browser build uses `text/tailwindcss` MIME type to identify `<style>` blocks with Tailwind CSS source. On page load:

1. All `<style type="text/tailwindcss">` elements are read and concatenated
2. If no `@import` found, `@import "tailwindcss";` is prepended automatically
3. CSS parsed through Tailwind's Oxide engine (Rust-compiled via WASM)
4. DOM scanned for all class names on `[class]` elements
5. Only matching utilities are compiled
6. Generated CSS injected into `<style>` in `<head>`

### Mutation Observing

Two `MutationObserver` instances keep styles in sync:

- **Full rebuild trigger**: Watches for `<style type="text/tailwindcss">` elements being added, removed, or modified
- **Incremental rebuild trigger**: Watches document tree for new elements with classes or class changes on `<html>`

### Performance Markers

Uses `performance.mark()`/`performance.measure()` for: `Create compiler`, `Reading Stylesheets`, `Compile CSS`, `Build #N (full|incremental)`, `Collect classes`, `Build utilities`. View in DevTools → Performance.

## Usage

### Basic Setup

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
    Tailwind CSS compiled entirely in the browser.
  </p>
</body>
</html>
```

No configuration needed. Script auto-detects classes and generates CSS.

### CDN Sources

- **jsDelivr**: `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js`
- **unpkg**: `https://unpkg.com/@tailwindcss/browser@4/dist/index.global.js`
- **esm.sh**: `https://esm.sh/@tailwindcss/browser@4`

Pin to specific version: `.../browser@4.2.4/dist/index.global.js`

### Customizing with text/tailwindcss Style Blocks

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

The `@theme` directive extends Tailwind's design tokens (`--color-*`, `--font-*`, `--spacing-*`, `--breakpoint-*`, `--radius-*`, `--shadow-*`). The `@utility` directive creates custom utility classes.

### Theme Reference Mode

Import another stylesheet's theme without emitting its CSS:

```html
<style type="text/tailwindcss">
  @import "./other.css" theme(reference);
</style>
```

Browser build only supports built-in virtual modules: `tailwindcss`, `tailwindcss/preflight`, `tailwindcss/theme`, `tailwindcss/utilities`. External file imports are not supported.

### Disabling Preflight

```html
<style type="text/tailwindcss">
  @import "tailwindcss/utilities";
</style>
```

Imports only utilities, skipping preflight and theme defaults.

### Using with Frameworks

**Alpine.js + Tailwind:**

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.2.4/dist/index.global.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3"></script>

<div x-data="{ open: false }">
  <button @click="open = !open" class="px-4 py-2 bg-blue-500 text-white rounded">Toggle</button>
  <div x-show="open" class="mt-2 p-4 bg-gray-100 rounded">Content</div>
</div>
```

**htmx + Tailwind:**

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.2.4/dist/index.global.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2"></script>

<button hx-get="/api/data" hx-target="#result" class="px-4 py-2 bg-green-500 text-white rounded">Load</button>
<div id="result" class="mt-4 p-4 border rounded"></div>
```

Mutation observer automatically picks up new classes from framework interactions.

## Advanced Topics

**Advanced Patterns**: Dynamic themes, multiple style blocks, media queries, preloading, limitations, comparison with standard build → [Advanced Patterns](reference/01-advanced-patterns.md)

**Migration & Troubleshooting**: v3 migration guide, FOUC fixes, dynamic class issues, theme debugging, OKLCH compatibility → [Migration & Troubleshooting](reference/02-migration-troubleshooting.md)
