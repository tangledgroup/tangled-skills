---
name: tailwindcss-4-2
description: A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration, OKLCH color space, cascade layers, and Lightning CSS optimization. Use when building responsive web interfaces, customizing design systems, or migrating from Tailwind v3.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - css
  - tailwind
  - styling
  - frontend
  - utility-first
  - responsive-design
category: development

external_references:
  - https://tailwindcss.com/docs
  - https://github.com/tailwindlabs/tailwindcss
---

# Tailwind CSS v4.2


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration, OKLCH color space, cascade layers, and Lightning CSS optimization. Use when building responsive web interfaces, customizing design systems, or migrating from Tailwind v3.

Tailwind CSS v4.2 is a utility-first CSS framework for rapidly building custom user interfaces without leaving HTML. Version 4 introduces a completely redesigned architecture with CSS-based configuration, native cascade layers, OKLCH color space support, and integrated Lightning CSS optimization.

## When to Use

- Building responsive web interfaces with utility classes
- Creating design systems with custom themes
- Migrating projects from Tailwind CSS v3 to v4
- Prototyping quickly with CDN-based setup
- Customizing default spacing, colors, fonts, and breakpoints
- Using modern build tools (Vite, PostCSS, CLI)

## Setup

### Installation Options

**Browser Build (No Build Step Required)**
Perfect for prototyping, documentation, learning, and static sites:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
</head>
<body>
  <h1 class="text-4xl font-bold text-blue-600">Hello World!</h1>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click me
  </button>
</body>
</html>
```

See [Browser Usage Guide](references/05-browser-usage.md) for comprehensive in-browser usage documentation.

**CLI Tool**
```bash
npm install -D @tailwindcss/cli
npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch
```

**Vite Integration**
```bash
npm install -D tailwindcss @tailwindcss/vite
```

```js
// vite.config.js
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [tailwindcss()]
})
```

**PostCSS Integration**
```bash
npm install -D tailwindcss @tailwindcss/postcss
```

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

### Basic Usage

Create an input CSS file with the Tailwind imports:

```css
/* src/input.css */
@import 'tailwindcss';
```

Or use explicit cascade layers:

```css
@layer theme, base, components, utilities;

@import 'tailwindcss/theme' layer(theme);
@import 'tailwindcss/preflight' layer(base);
@import 'tailwindcss/utilities' layer(utilities);
```

## Quick Start

### Hello World Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="./dist/output.css">
</head>
<body class="bg-gray-50 min-h-screen">
  <div class="flex items-center justify-center min-h-screen">
    <button class="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors shadow-md">
      Hello World
    </button>
  </div>
</body>
</html>
```

See [Core Concepts](references/01-core-concepts.md) for detailed explanation of the v4 architecture.

Refer to [Theming & Customization](references/02-theming-customization.md) for custom design systems.

Consult [Utility Reference](references/03-utility-reference.md) for complete utility documentation.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - v4 architecture, cascade layers, and @theme directive
- [`references/02-theming-customization.md`](references/02-theming-customization.md) - Custom themes, OKLCH colors, and configuration patterns
- [`references/03-utility-reference.md`](references/03-utility-reference.md) - Complete utility class reference with examples
- [`references/04-v3-migration.md`](references/04-v3-migration.md) - Migration guide from Tailwind CSS v3 to v4
- [`references/05-browser-usage.md`](references/05-browser-usage.md) - In-browser usage with @tailwindcss/browser (no build step)

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/tailwindcss-4-2/`). All paths are relative to this directory.

## Common Patterns

### Responsive Design
```html
<div class="w-full md:w-1/2 lg:w-1/3">Responsive width</div>
<div class="hidden md:block">Hidden on mobile, visible on medium+</div>
```

### Dark Mode
```html
<div class="bg-white dark:bg-gray-800 text-black dark:text-white">
  Dark mode aware content
</div>
```

### Custom Theme
```css
@theme {
  --color-brand: oklch(0.6 0.2 250);
  --font-display: 'Inter', sans-serif;
}
```

Then use in HTML:
```html
<button class="bg-brand text-white">Brand Button</button>
```

See [Theming & Customization](references/02-theming-customization.md) for advanced patterns.

## Troubleshooting

### Utilities Not Applying
- Ensure build process is running and watching files
- Check that input CSS includes `@import 'tailwindcss'`
- Verify content files are in the correct directory (auto-scanned)

### Custom Theme Not Working
- Use `@theme` directive, not JavaScript config
- Place theme definitions before component styles
- Reference variables with `--theme(--custom-var, fallback)`

### Build Issues
- Clear cache: remove `node_modules/.cache`
- Ensure Tailwind v4 packages are installed (`tailwindcss@^4`)
- Check for conflicting PostCSS plugins

See [v3 Migration Guide](references/04-v3-migration.md) for upgrade-related issues.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
