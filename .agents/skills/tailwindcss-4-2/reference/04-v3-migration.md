# v3 to v4 Migration Guide

This guide helps you migrate from Tailwind CSS v3 to v4, covering breaking changes, new features, and migration strategies.

## Key Changes Overview

### Major Architectural Changes

1. **No JavaScript Config**: `tailwind.config.js` replaced with CSS `@theme` directive
2. **New Import System**: `@tailwind` directives replaced with `@import`
3. **CSS-Based Plugins**: Custom plugins now use CSS instead of JavaScript
4. **OKLCH Colors**: Default color palette uses OKLCH color space
5. **Cascade Layers**: Built-in layer management for better specificity control

## Migration Steps

### Step 1: Update Dependencies

```bash
# Remove v3 packages
npm uninstall tailwindcss@3 postcss autoprefixer

# Install v4 packages
npm install -D tailwindcss @tailwindcss/postcss
# or for Vite
npm install -D tailwindcss @tailwindcss/vite
```

### Step 2: Replace Configuration File

**Before (v3 - tailwind.config.js):**
```js
module.exports = {
  content: ['./src/**/*.{html,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#10b981',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
```

**After (v4 - src/theme.css):**
```css
@theme {
  --color-primary: oklch(0.6 0.2 250); /* Convert from hex */
  --color-secondary: oklch(0.7 0.15 150);
  
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
}
```

### Step 3: Update CSS Entry Point

**Before (v3):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**After (v4):**
```css
@import 'tailwindcss';
```

Or with explicit layers:
```css
@layer theme, base, components, utilities;

@import 'tailwindcss/theme' layer(theme);
@import 'tailwindcss/preflight' layer(base);
@import 'tailwindcss/utilities' layer(utilities);
```

### Step 4: Update Build Configuration

**PostCSS (v3):**
```js
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**PostCSS (v4):**
```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

**Vite (v3):**
```js
// vite.config.js
import tailwindcss from 'tailwindcss'

export default defineConfig({
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer()],
    },
  },
})
```

**Vite (v4):**
```js
// vite.config.js
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

## Configuration Migration

### Colors

**v3 JavaScript:**
```js
theme: {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      900: '#1e3a8a',
    },
  }
}
```

**v4 CSS:**
```css
@theme {
  --color-primary-50: oklch(0.97 0.01 250);
  --color-primary-100: oklch(0.94 0.02 250);
  --color-primary-500: oklch(0.6 0.2 250);
  --color-primary-900: oklch(0.25 0.1 250);
}
```

### Fonts

**v3:**
```js
theme: {
  extend: {
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
      heading: ['Playfair Display', 'serif'],
    },
  }
}
```

**v4:**
```css
@theme {
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-heading: 'Playfair Display', ui-serif, Georgia, serif;
}
```

Usage:
```html
<p class="font-sans">Sans-serif</p>
<h1 class="font-heading">Heading font</h1>
```

### Spacing

**v3:**
```js
theme: {
  extend: {
    spacing: {
      '3xl': '48rem',
      '4xl': '56rem',
    }
  }
}
```

**v4:**
```css
@theme {
  --spacing-3xl: 48rem;
  --spacing-4xl: 56rem;
}
```

### Breakpoints

**v3:**
```js
theme: {
  screens: {
    'sm': '640px',
    'md': '768px',
    'lg': '1024px',
    'xl': '1280px',
    '2xl': '1536px',
    '3xl': '1920px', // Custom
  }
}
```

**v4:**
```css
@theme {
  --breakpoint-3xl: 1920px;
}
```

### Shadows

**v3:**
```js
theme: {
  extend: {
    boxShadow: {
      'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
    }
  }
}
```

**v4:**
```css
@theme {
  --shadow-glow: 0 0 20px rgb(59 130 246 / 0.5);
}
```

Usage:
```html
<div class="shadow-glow">Glow effect</div>
```

## Plugin Migration

### Official Plugins

**v3:**
```js
plugins: [
  require('@tailwindcss/forms'),
  require('@tailwindcss/typography'),
  require('@tailwindcss/aspect-ratio'),
]
```

**v4:** Most official plugins are now built-in! The following utilities are included by default:
- Form styles (use `class="form-input"` etc.)
- Typography plugin (`prose` class)
- Aspect ratio utilities

### Custom Plugins

**v3 JavaScript Plugin:**
```js
// tailwind.config.js
module.exports = {
  plugins: [
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
        },
        '.scrollbar-hide::-webkit-scrollbar': {
          'display': 'none',
        },
      }
      addUtilities(newUtilities)
    }
  ]
}
```

**v4 CSS Plugin:**
```css
@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

Or create a separate file:

**src/plugins/scrollbar.css:**
```css
@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@utility scrollbar-hide::-webkit-scrollbar {
  display: none;
}
```

Then import it:
```css
@import 'tailwindcss';
@import './plugins/scrollbar.css';
```

## Breaking Changes

### Removed Utilities

Some v3 utilities have been removed or renamed:

| v3 Utility | v4 Replacement |
|------------|----------------|
| `container` | Use `max-w-screen-xl mx-auto px-4` or custom component |
| `leading-normal` (1.5) | Still available, check theme |
| `tracking-normal` (0) | Still available |
| `border-{color}` | Use `border-{color}` (same, but color values changed) |

### Changed Defaults

**Border Radius:**
- v3: `rounded` = 0.25rem
- v4: `rounded` = 0.25rem (same, but more granular scale with xs, sm, md, lg, xl, 2xl, 3xl, 4xl)

**Shadows:**
- v3: Used RGBA colors
- v4: Uses modern color syntax with OKLCH support

**Font Sizes:**
- v3: Font sizes had hardcoded line heights
- v4: Uses `--text-{size}--line-height` variables for better customization

### Color Space Changes

**v3 RGB/Hex Colors:**
```css
/* In config */
primary: '#3b82f6'
```

**v4 OKLCH Colors:**
```css
@theme {
  --color-primary: oklch(0.6 0.2 250);
}
```

To convert colors, use online tools or browser devtools. The built-in Tailwind palette is already in OKLCH.

## Content Scanning Changes

### v3 Configuration Required

```js
module.exports = {
  content: [
    './src/**/*.{html,js,ts,jsx,tsx}',
    './app/**/*.{vue,svelte}',
  ]
}
```

### v4 Automatic Scanning

No configuration needed! Tailwind v4 automatically scans:
- All `.html`, `.htm` files
- All `.js`, `.jsx`, `.ts`, `.tsx` files
- All `.vue`, `.svelte` files
- All `.md`, `.mdx` files

In the current working directory by default.

### Custom Scan Paths (PostCSS)

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {
      base: path.resolve(__dirname, './src'),
    },
  },
}
```

## Common Migration Issues

### Issue 1: Utilities Not Applying

**Problem:** After migration, utility classes don't work.

**Solution:**
1. Ensure you're using `@import 'tailwindcss'` not `@tailwind`
2. Check that the build process is running
3. Verify CSS file path in HTML `<link>` tag
4. Clear browser cache and rebuild

### Issue 2: Custom Colors Missing

**Problem:** Custom colors from config don't generate utilities.

**Solution:** Make sure theme is defined before import:

```css
/* Wrong order */
@import 'tailwindcss';
@theme { --color-brand: blue; }

/* Correct order */
@theme { --color-brand: blue; }
@import 'tailwindcss';
```

Or in same file:

```css
@theme {
  --color-brand: oklch(0.6 0.2 250);
}

@layer base, components, utilities;
@import 'tailwindcss' layer(utilities);
```

### Issue 3: Component Styles Overridden

**Problem:** Custom component styles are overridden by utilities.

**Solution:** Use cascade layers properly:

```css
@layer theme, base, components, utilities;

@import 'tailwindcss/theme' layer(theme);
@import 'tailwindcss/preflight' layer(base);
@import 'tailwindcss/utilities' layer(utilities);

@layer components {
  .btn-primary {
    background-color: var(--color-brand);
    color: white;
  }
}
```

### Issue 4: Plugin Not Working

**Problem:** Custom plugin utilities don't generate.

**Solution:** Ensure plugin CSS is imported after Tailwind:

```css
@import 'tailwindcss';
@import './plugins/custom.css';
```

And plugin uses `@layer utilities` or `@utility`:

```css
/* plugins/custom.css */
@layer utilities {
  .custom-utility {
    /* styles */
  }
}
```

## Performance Improvements

### Tree Shaking

v4 has better tree shaking. Only used utilities are included in the final CSS.

### Lightning CSS

Production builds automatically use Lightning CSS for:
- Minification
- Property normalization
- Value optimization

Enable/disable in Vite:
```js
export default defineConfig({
  plugins: [
    tailwindcss({
      optimize: { minify: false }, // Disable minification
    }),
  ],
})
```

### Smaller Bundle Size

v4 produces smaller CSS files due to:
- Better minification with Lightning CSS
- More efficient utility generation
- No JavaScript overhead

## Testing Your Migration

### 1. Visual Regression Testing

Compare key pages before and after migration:
```bash
npm install -D @percy/cli
npx percy snapshot localhost:3000
```

### 2. CSS Diffing

Check for missing styles:
```bash
# Build both versions
npm run build:v3
npm run build:v4

# Compare output
diff -r dist-v3/dist dist-v4/dist
```

### 3. Utility Coverage

Ensure all utilities are still available:
```html
<!-- Test file with common utilities -->
<div class="flex items-center justify-center p-4 m-2">
  <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
    Test Button
  </button>
</div>
```

## Rollback Strategy

Keep v3 available during migration:

```bash
# Keep v3 in separate branch
git checkout -b migrate-to-v4
# Make changes, test thoroughly
# If issues, revert and fix
git checkout main
```

Or use npm aliases temporarily:
```json
{
  "dependencies": {
    "tailwindcss-v3": "npm:tailwindcss@3",
    "tailwindcss": "npm:tailwindcss@4"
  }
}
```

## Resources

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [v4 Release Notes](https://github.com/tailwindlabs/tailwindcss/releases)
- [Migration Guide on Tailwind Website](https://tailwindcss.com/docs/3-to-4-upgrade-guide)
- [OKLCH Color Converter](https://oklch.com/)

## Summary Checklist

- [ ] Updated dependencies to v4 packages
- [ ] Replaced `tailwind.config.js` with `@theme` directive
- [ ] Changed `@tailwind` to `@import` in CSS
- [ ] Updated PostCSS/Vite configuration
- [ ] Converted custom colors to OKLCH (optional but recommended)
- [ ] Migrated custom plugins to CSS
- [ ] Removed content configuration (auto-scanning enabled)
- [ ] Tested all components visually
- [ ] Verified responsive utilities work
- [ ] Checked dark mode functionality
- [ ] Measured bundle size improvement
