---
name: tailwindcss-browser-4-2
description: A skill for using Tailwind CSS v4.2 browser build (@tailwindcss/browser) that enables in-browser Tailwind compilation without a build step. Use when prototyping, creating documentation sites, building static pages, or learning Tailwind CSS without setting up Node.js tooling.
version: "0.2.0"
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
---

# Tailwind CSS Browser v4.2

Tailwind CSS Browser is a specialized build of Tailwind CSS v4.2 that compiles utility classes directly in the browser using Web Workers. This enables using Tailwind without any build step, Node.js, or configuration files—perfect for rapid prototyping, documentation sites, static pages, and learning.

## When to Use

- Rapidly prototyping UI components without build tooling
- Creating documentation sites with live code examples
- Building static HTML pages quickly
- Learning Tailwind CSS without setup overhead
- Embedded in CMS platforms or website builders
- Hotwire/Turbo-based applications
- Simple landing pages and marketing sites

## Setup

### CDN Usage (Recommended)

Add the script tag to your HTML `<head>`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tailwind Browser</title>
  
  <!-- Tailwind CSS Browser Build -->
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body>
  <h1 class="text-4xl font-bold text-blue-600">Hello World!</h1>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click me
  </button>
</body>
</html>
```

### Alternative CDN Providers

**unpkg:**
```html
<script src="https://unpkg.com/@tailwindcss/browser@4"></script>
```

**esm.sh:**
```html
<script type="module">
  import '@tailwindcss/browser'
</script>
```

### Local Installation

Download the browser build and serve it locally:

```bash
# Install via npm
npm install @tailwindcss/browser
```

Then reference the compiled file:
```html
<script src="./node_modules/@tailwindcss/browser/dist/index.global.js"></script>
```

Or download directly from npmjs.org:
1. Visit https://www.npmjs.com/package/@tailwindcss/browser
2. Click "Code" button to view package contents
3. Download `dist/index.global.js`
4. Place in your project and reference locally

## Quick Start Examples

### Basic Button Component

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-100 p-8">
  <div class="flex gap-4">
    <button class="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors shadow-md">
      Primary Button
    </button>
    <button class="px-6 py-3 border-2 border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors">
      Secondary Button
    </button>
  </div>
</body>
</html>
```

### Responsive Navigation

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-white">
  <nav class="border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <span class="text-xl font-bold text-gray-900">Logo</span>
          <div class="hidden md:flex ml-10 space-x-8">
            <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">Services</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">Contact</a>
          </div>
        </div>
        <div class="flex items-center">
          <button class="p-2 rounded-md text-gray-400 hover:text-gray-500 md:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </nav>
</body>
</html>
```

### Dark Mode Support

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-white dark:bg-gray-900 min-h-screen">
  <div class="max-w-md mx-auto p-8">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Dark Mode Card
      </h2>
      <p class="text-gray-600 dark:text-gray-300">
        This card automatically switches between light and dark themes.
      </p>
      <button class="mt-4 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded">
        Action Button
      </button>
    </div>
  </div>
</body>
</html>
```

## Customization

### Custom Theme Variables

Extend Tailwind's theme using CSS custom properties:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <style type="text/tailwindcss">
    @theme {
      --color-brand-primary: oklch(0.6 0.25 260);
      --color-brand-secondary: oklch(0.7 0.15 180);
      --font-display: 'Inter', sans-serif;
      --spacing-px: 1px;
    }
  </style>
</head>
<body>
  <h1 class="font-display text-4xl text-brand-primary">
    Custom Brand Colors
  </h1>
  <button class="bg-brand-secondary text-white px-6 py-3 rounded-lg">
    Secondary Action
  </button>
</body>
</html>
```

### Preflight Reset Override

Disable Tailwind's preflight reset if needed:

```html
<style type="text/tailwindcss">
  @layer base {
    /* Your custom base styles */
    body {
      font-family: system-ui, -apple-system, sans-serif;
    }
  }
</style>
```

### Custom Utilities

Define custom utility classes:

```html
<style type="text/tailwindcss">
  @utility button-primary {
    @apply px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors;
  }
  
  @utility card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
</style>
```

Usage:
```html
<button class="button-primary">Custom Button</button>
<div class="card">Card Component</div>
```

## See Also

- [Advanced Usage and Examples](references/01-advanced-usage.md) - Complete examples, advanced patterns, and troubleshooting
