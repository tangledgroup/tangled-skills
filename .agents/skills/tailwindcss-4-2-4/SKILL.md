---
name: tailwindcss-4-2-4
description: A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration via @theme, OKLCH color space, cascade layers, and Lightning CSS optimization. Use when building responsive web interfaces, customizing design systems, adding utility-class styling to HTML, or migrating from Tailwind v3.
version: "4.2.4"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - css
  - tailwind
  - styling
  - frontend
  - utility-first
  - responsive-design
  - design-tokens
category: development
external_references:
  - https://tailwindcss.com/docs
  - https://github.com/tailwindlabs/tailwindcss
---

# Tailwind CSS 4.2

## Overview

Tailwind CSS is a utility-first CSS framework for rapidly building custom user interfaces. It works by scanning all HTML files, JavaScript components, and templates for class names, then generating the corresponding styles into a static CSS file — fast, flexible, reliable, with zero runtime.

Version 4.x introduces a ground-up rewrite with CSS-based configuration (no `tailwind.config.js`), Lightning CSS as the engine, OKLCH color space by default, cascade layer support (`@layer`), and significantly improved performance. The framework targets modern browsers: Safari 16.4+, Chrome 111+, Firefox 128+.

## When to Use

- Building responsive web interfaces with utility-first CSS classes
- Customizing design systems through CSS-based `@theme` tokens
- Adding hover, focus, and state-based styling directly in HTML
- Migrating projects from Tailwind v3 to v4
- Creating dark mode variants with the `dark:` prefix
- Using arbitrary values for one-off styles without leaving HTML
- Integrating Tailwind with Vite, PostCSS, or CLI build tools

## Core Concepts

### Utility-First Approach

Style elements by combining many single-purpose presentational classes directly in markup:

```html
<div class="mx-auto flex max-w-sm items-center gap-x-4 rounded-xl bg-white p-6 shadow-lg">
  <img class="size-12 shrink-0" src="/logo.svg" alt="Logo" />
  <div>
    <h3 class="text-xl font-medium text-black">You have a new message!</h3>
  </div>
</div>
```

Benefits over traditional CSS: faster development, safer changes (each utility affects only its element), easier maintenance, more portable code, and bounded CSS file growth.

### Theme Variables

Design tokens are defined as CSS variables using the `@theme` directive — not in a JavaScript config file:

```css
@import "tailwindcss";

@theme {
  --font-display: "Satoshi", sans-serif;
  --color-mint-500: oklch(0.72 0.11 178);
  --breakpoint-3xl: 120rem;
}
```

Theme variables in the `--font-*` namespace generate `font-*` utilities, `--color-*` generates color utilities, `--breakpoint-*` adds responsive breakpoints, and so on. They also expose as regular CSS variables for use in arbitrary values or inline styles.

### State Variants

Every utility can be applied conditionally by prefixing with a variant:

```html
<button class="bg-sky-500 hover:bg-sky-700 focus:ring-2 active:bg-sky-800">
  Save changes
</button>
```

Variants include pseudo-classes (`:hover`, `:focus`, `:first-child`), pseudo-elements (`::before`, `::after`), media queries (responsive breakpoints, dark mode), attribute selectors (`[dir="rtl"]`), and child selectors. Variants stack: `dark:md:hover:bg-fuchsia-600`.

### Responsive Design

Mobile-first breakpoint system with five defaults:

- `sm:` — `@media (width >= 40rem)` (640px)
- `md:` — `@media (width >= 48rem)` (768px)
- `lg:` — `@media (width >= 64rem)` (1024px)
- `xl:` — `@media (width >= 80rem)` (1280px)
- `2xl:` — `@media (width >= 96rem)` (1536px)

Unprefixed utilities apply to all screen sizes. Prefixed utilities apply at that breakpoint and above.

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- ... -->
</div>
```

### Arbitrary Values

Use square bracket notation for one-off values without defining theme tokens:

```html
<div class="top-[117px] bg-[#bada55] text-[22px]">...</div>
<div class="[mask-type:luminance] hover:[mask-type:alpha]">...</div>
<div class="fill-(--my-brand-color)">...</div>
```

CSS variable shorthand: `(--my-var)` expands to `var(--my-var)`.

## Installation / Setup

### Vite (Recommended)

```bash
npm create vite@latest my-project
cd my-project
npm install tailwindcss @tailwindcss/vite
```

Add the plugin to `vite.config.js`:

```js
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

Import in your CSS entry file:

```css
@import "tailwindcss";
```

### PostCSS

```bash
npm install tailwindcss @tailwindcss/postcss
```

```js
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

### CLI

```bash
npx @tailwindcss/cli -i input.css -o output.css
```

### CDN (Prototyping)

Use the Play CDN for rapid prototyping without a build step:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

## Usage Examples

### Responsive Card Component

```html
<div class="mx-auto max-w-md overflow-hidden rounded-xl bg-white shadow-md md:max-w-2xl">
  <div class="md:flex">
    <div class="md:shrink-0">
      <img class="h-48 w-full object-cover md:h-full md:w-48" src="building.jpg" alt="Building" />
    </div>
    <div class="p-8">
      <h2 class="text-lg font-bold text-gray-900">Modern Architecture</h2>
      <p class="mt-2 text-sm text-gray-500">Clean lines and natural materials.</p>
    </div>
  </div>
</div>
```

### Dark Mode Support

```html
<div class="bg-white dark:bg-gray-800 rounded-lg px-6 py-8 shadow-xl ring ring-gray-900/5">
  <span class="inline-flex items-center justify-center rounded-md bg-indigo-500 p-2">
    <!-- icon -->
  </span>
  <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">Title</h3>
  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Description text.</p>
</div>
```

Toggle dark mode with a custom variant:

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
```

### Custom Theme with OKLCH Colors

```css
@import "tailwindcss";

@theme {
  --font-display: "Satoshi", sans-serif;
  --breakpoint-3xl: 120rem;
  --color-avocado-100: oklch(0.99 0 0);
  --color-avocado-500: oklch(0.84 0.18 117.09);
  --color-avocado-900: oklch(0.26 0.05 112.46);
  --shadow-float: 0 0 0 1px oklch(0 0 0 / 0.05), 0 20px 40px oklch(0 0 0 / 0.15);
}
```

Then use `font-display`, `bg-avocado-500`, and `shadow-float` as utility classes.

### Color Opacity

```html
<div class="bg-sky-500/10"></div>
<div class="bg-sky-500/75"></div>
<div class="bg-pink-500/[71.37%]"></div>
<div class="bg-cyan-400/(--my-alpha-value)"></div>
```

### Custom Utilities

```css
@utility tab-4 {
  tab-size: 4;
}

@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
```

## Advanced Topics

**Functions and Directives**: Complete reference for `@theme`, `@layer`, `@utility`, `@variant`, `@custom-variant`, `@apply`, `@source` → [Functions and Directives](reference/01-functions-and-directives.md)

**Utility Reference**: Full listing of all utility categories — spacing, layout, typography, colors, backgrounds, borders, effects, filters, transforms, transitions, animations, interactivity, SVG, and accessibility → [Utility Reference](reference/02-utility-reference.md)

**Migration from v3 to v4**: Breaking changes, config migration, PostCSS to Vite plugin, CLI package rename, color palette updates → [Upgrade Guide](reference/03-upgrade-guide.md)
