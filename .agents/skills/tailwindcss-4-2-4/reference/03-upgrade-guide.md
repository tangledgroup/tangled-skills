# Upgrade Guide

Migrating from Tailwind CSS v3 to v4 involves several breaking changes. The official upgrade tool handles most of the migration automatically.

## Using the Upgrade Tool

```bash
npx @tailwindcss/upgrade
```

The tool automates dependency updates, config file migration to CSS, and template file changes. Requires Node.js 20+. Run in a new branch and review the diff carefully.

## Key Breaking Changes

### Configuration: JavaScript to CSS

**v3 (JavaScript config):**
```js
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        brand: {
          500: "#1d4ed8",
        },
      },
      fontFamily: {
        display: ["Satoshi", "sans-serif"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
}
```

**v4 (CSS-based):**
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@theme {
  --color-brand-500: oklch(0.45 0.21 260);
  --font-display: "Satoshi", sans-serif;
}

@source "../node_modules/@my-company/ui-lib";
```

### PostCSS Plugin Package Rename

**v3:**
```js
// postcss.config.js
module.exports = {
  plugins: {
    "postcss-import": {},
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**v4:**
```js
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

Note: `postcss-import` and `autoprefixer` are no longer needed — Tailwind v4 handles imports and vendor prefixing automatically.

### Vite Plugin Migration

**v3 (via PostCSS):**
```js
// vite.config.js
import tailwindcss from "tailwindcss"
import autoprefixer from "autoprefixer"

export default {
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer()],
    },
  },
}
```

**v4 (dedicated Vite plugin):**
```js
// vite.config.js
import { defineConfig } from "vite"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [tailwindcss()],
})
```

### CLI Package Rename

**v3:**
```bash
npx tailwindcss -i input.css -o output.css
```

**v4:**
```bash
npx @tailwindcss/cli -i input.css -o output.css
```

### Color Palette Changes

- `gray` is now an alias for `stone` (was `gray` = neutral grays)
- Default colors use OKLCH color space internally
- Some color shade values shifted slightly due to color space conversion
- `lightBlue` renamed to `sky`
- `warmGray` → `stone`, `trueGray` → `neutral`, `coolGray` → `gray`, `blueGray` → `slate`

### Removed Directives

The following v3 directives are no longer used:

- `@tailwind base` — replaced by automatic Preflight injection
- `@tailwind components` — use `@layer components` directly
- `@tailwind utilities` — replaced by automatic utility generation
- `@screen` — use responsive variants (`sm:`, `md:`, etc.)

### Theme Extension Syntax

**v3:**
```js
theme: {
  extend: {
    spacing: {
      "128": "32rem",
    },
  },
}
```

**v4:**
```css
@theme {
  --spacing-128: 32rem;
}
```

### Plugin System

**v3:**
```js
// tailwind.config.js
plugins: [
  require("@tailwindcss/forms"),
  require("@tailwindcss/typography"),
]
```

**v4:**
```css
@import "tailwindcss";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/typography";
```

### Content Detection

**v3 (explicit content config):**
```js
content: [
  "./src/**/*.{html,js,jsx,ts,tsx}",
  "./templates/**/*.hbs",
]
```

**v4 (automatic detection + @source for extras):**
```css
@import "tailwindcss";
@source "../node_modules/@my-company/ui-lib";
```

Tailwind v4 automatically detects source files. Use `@source` only for paths outside automatic detection.

### Browser Support

- **v3:** Supports older browsers (IE 11 with polyfills)
- **v4:** Safari 16.4+, Chrome 111+, Firefox 128+

v4 depends on modern CSS features: `@property`, `color-mix()`, cascade layers, `:has()`. If you need older browser support, stay on v3.

### Arbitrary Value Syntax Changes

**v3:**
```html
<div class="bg-[rgb(255,0,0)]">...</div>
```

**v4:**
```html
<div class="bg-(--my-color)">...</div>
<!-- shorthand for bg-[var(--my-color)] -->
```

The `()` syntax is a new shorthand for CSS variable references in arbitrary values.

### New Features in v4

- CSS-based configuration via `@theme`
- Lightning CSS engine (faster builds)
- OKLCH color space by default
- Cascade layer support (`@layer`)
- Container queries (`@container`, `@sm:`)
- Child/sibling selectors (`*:[&>*>]:`)
- `@custom-variant` for custom variants
- `@utility` for custom utilities
- Automatic content detection
- Built-in import and vendor prefixing
- Zero runtime overhead
- Improved developer experience with better IntelliSense support

## Migration Checklist

1. Run `npx @tailwindcss/upgrade`
2. Review the generated diff
3. Test all pages in the browser
4. Verify responsive breakpoints work correctly
5. Check dark mode styling
6. Validate custom theme tokens
7. Confirm plugin functionality
8. Test build output size
9. Verify CSS linting passes (install Tailwind CSS language mode for your editor)
