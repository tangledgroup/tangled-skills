# Tailwind CSS v4 Core Concepts

This reference covers the fundamental architectural changes in Tailwind CSS v4, including cascade layers, the @theme directive, and how the framework processes styles.

## Architecture Overview

Tailwind v4 represents a complete redesign from the ground up:

- **CSS-based configuration**: No more JavaScript config files
- **Native cascade layers**: Built-in CSS layer management
- **Lightning CSS integration**: High-performance parsing and minification
- **Simplified plugin system**: CSS-based plugins instead of JavaScript

## Cascade Layers

Tailwind v4 uses CSS cascade layers (`@layer`) to organize styles with proper specificity control.

### Layer Order

```css
@layer theme, base, components, utilities;
```

The order matters - later layers can override earlier ones:

1. **theme**: Custom property definitions (CSS variables)
2. **base**: Base/reset styles (preflight)
3. **components**: Component classes you define
4. **utilities**: Tailwind utility classes

### Using Layers

```css
/* Define layer order first */
@layer theme, base, components, utilities;

/* Import Tailwind layers */
@import 'tailwindcss/theme' layer(theme);
@import 'tailwindcss/preflight' layer(base);
@import 'tailwindcss/utilities' layer(utilities);

/* Your component styles */
@layer components {
  .btn-primary {
    background-color: var(--color-blue-500);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
  }
}
```

### Why Cascade Layers Matter

- **Predictable specificity**: Utilities always win over components
- **No !important needed**: Proper cascade order handles overrides
- **Cleaner CSS**: Browser's native layer system instead of hacks

## The @theme Directive

The `@theme` directive replaces the old `tailwind.config.js` file. All configuration is now done in CSS.

### Basic Theme

```css
@theme {
  /* Custom colors */
  --color-brand: oklch(0.6 0.2 250);
  --color-brand-hover: oklch(0.55 0.22 250);
  
  /* Custom fonts */
  --font-display: 'Inter', ui-sans-serif, system-ui, sans-serif;
  
  /* Custom spacing */
  --spacing-xl: 24rem;
  --spacing-2xl: 32rem;
  
  /* Custom breakpoints */
  --breakpoint-3xl: 1200px;
}
```

### Theme Modes

#### Default Theme (Generates Utilities)
```css
@theme {
  --color-primary: oklch(0.6 0.2 250);
  /* Generates: bg-primary, text-primary, border-primary, etc. */
}
```

#### Reference Theme (No Utilities)
```css
@theme reference {
  --color-logo: oklch(0.7 0.15 260);
  /* Does NOT generate utilities - for internal use only */
}

/* Use with --theme() function */
.logo {
  color: var(--theme(--color-logo, blue));
}
```

#### Inline Theme (Component-Scoped)
```css
@theme inline {
  --color-card-bg: oklch(0.95 0 0);
}

.card {
  background-color: var(--color-card-bg);
}
```

### Merging with Default Theme

```css
@theme {
  /* Extends default spacing scale */
  --spacing-3xl: 48rem;
  --spacing-4xl: 56rem;
  
  /* Overrides default color */
  --color-blue-500: oklch(0.62 0.24 255);
}
```

## OKLCH Color Space

Tailwind v4 uses OKLCH (Oklab-based) as the default color space for better color interpolation and perceptual uniformity.

### OKLCH Format

```css
oklch(Lightness Chroma Hue)
```

- **Lightness**: 0 (black) to 1 (white)
- **Chroma**: 0 (gray) to ~0.4 (vibrant)
- **Hue**: 0-360 degrees

### Examples

```css
@theme {
  /* Vibrant blue */
  --color-primary: oklch(0.6 0.25 250);
  
  /* Muted gray-blue */
  --color-secondary: oklch(0.7 0.05 250);
  
  /* Pure gray (chroma = 0) */
  --color-gray: oklch(0.5 0 0);
}
```

### Converting RGB/Hex to OKLCH

Use online tools or CSS:
```css
/* Modern browsers support color() function */
@theme {
  --color-custom: color(srgb 0.5 0.3 0.8);
}
```

### Built-in Color Palette

Tailwind v4 includes these color families in OKLCH:
- Red, Orange, Amber, Yellow, Lime, Green, Emerald, Teal, Cyan, Sky, Blue, Indigo, Violet, Purple, Fuchsia, Pink, Rose
- Neutral, Zinc, Slate, Stone, Gray

Each has shades 50-950 plus black/white.

## Preflight (Reset)

Preflight is Tailwind's modern CSS reset, now in the `base` layer.

```css
@import 'tailwindcss/preflight' layer(base);
```

Key resets include:
- Box-sizing: border-box on all elements
- Removed default margins and padding
- Consistent line-height (1.5)
- Default sans-serif font family
- Disabled tap highlights on iOS

### Customizing Preflight

Override specific resets in your own base layer:

```css
@layer base {
  html {
    font-size: 18px; /* Override default 16px */
  }
  
  body {
    -webkit-font-smoothing: antialiased;
  }
}
```

## Content Scanning

Tailwind v4 automatically scans your project for class names. No content configuration needed.

### How It Works

The PostCSS/Vite plugins scan these file extensions by default:
- `.html`, `.htm`
- `.js`, `.jsx`, `.ts`, `.tsx`
- `.vue`, `.svelte`
- `.md`, `.mdx`

### Custom File Paths (PostCSS)

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

## Lightning CSS Integration

Lightning CSS is integrated for production optimization.

### Automatic Optimization

By default:
- Development (`NODE_ENV=development`): No minification
- Production (`NODE_ENV=production`): Full optimization

### Manual Control (Vite)

```js
// vite.config.js
export default defineConfig({
  plugins: [
    tailwindcss({
      // Disable all optimization
      optimize: false,
      
      // Enable but skip minification
      optimize: { minify: false },
      
      // Full optimization (default in production)
      optimize: true,
    }),
  ],
})
```

### Manual Control (PostCSS)

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {
      optimize: false, // Disable Lightning CSS
    },
  },
}
```

## Container Queries

Tailwind v4 has first-class container query support.

### Basic Usage

```css
@container (min-width: 40rem) {
  .container-text {
    font-size: 1.25rem;
  }
}
```

### With Tailwind Utilities

```html
<div class="container-inline">
  <div class="text-base container:text-lg lg:text-xl">
    Responsive to container size
  </div>
</div>
```

### Named Containers

```css
@theme {
  --container-sidebar: 16rem;
}

@container sidebar (min-width: var(--container-sidebar)) {
  .expanded-view {
    display: block;
  }
}
```

## Performance Considerations

### Tree Shaking

Only used utilities are included in the final CSS. Unused classes are automatically removed.

### Build Optimization

- Enable Lightning CSS for production builds
- Use `@theme reference` for internal variables (no utility generation)
- Keep component styles in `@layer components` for proper specificity

### CDN Usage Warning

The CDN build includes all utilities (~200KB). Only use for:
- Prototyping and development
- Documentation sites
- Small projects where build setup is impractical

For production, always use the CLI or bundler integration.
