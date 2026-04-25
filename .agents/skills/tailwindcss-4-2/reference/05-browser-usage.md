# Browser Usage Guide - @tailwindcss/browser

This guide covers using Tailwind CSS v4 directly in the browser with `@tailwindcss/browser`, enabling rapid prototyping and development without any build step, compilation, or bundler.

## Overview

The `@tailwindcss/browser` package allows you to use Tailwind CSS utilities directly in HTML files by including a JavaScript bundle that:
- Scans the DOM for utility classes
- Compiles only the classes found on the page
- Injects the resulting CSS into a `<style>` tag
- Watches for DOM changes and recompiles incrementally

### When to Use

**Perfect for:**
- Rapid prototyping and mockups
- Documentation sites with code examples
- Learning and experimentation
- Static sites where build tools are impractical
- Quick demos and proofs of concept
- Email template testing

**Not recommended for:**
- Production applications (use CLI/bundler instead)
- Large-scale sites with many classes
- Single-page apps with frequent dynamic content
- Performance-critical applications
- Projects requiring custom plugins

## Installation Methods

### CDN (Recommended)

Include the script tag in your HTML `<head>`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tailwind CSS Browser</title>
  
  <!-- Include Tailwind CSS browser build -->
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

### Specific Version

Pin to a specific version for stability:

```html
<script src="https://unpkg.com/@tailwindcss/browser@4.2.2"></script>
```

### Local Installation

Install via npm and include locally:

```bash
npm install @tailwindcss/browser
```

```html
<script src="./node_modules/@tailwindcss/browser/dist/index.global.js"></script>
```

## How It Works

The browser build operates in these steps:

1. **Scans the DOM** for all elements with class attributes
2. **Collects unique classes** found on the page
3. **Compiles CSS** for only those classes (tree-shaking)
4. **Injects styles** into a `<style>` tag in `<head>`
5. **Watches for changes** via MutationObserver
6. **Recompiles incrementally** when new classes appear

### Performance Instrumentation

The build includes performance markers visible in browser devtools:

1. Open DevTools (F12)
2. Go to **Performance** tab
3. Record page load
4. Look for Tailwind CSS markers:
   - `Create compiler` - Initial setup time
   - `Reading Stylesheets` - Parsing custom theme CSS
   - `Compile CSS` - Creating the compiler instance
   - `Collect classes` - Scanning DOM for classes
   - `Build utilities` - Generating final CSS
   - `Build #N (full/incremental)` - Rebuild events

Each marker includes metadata like class count and CSS size.

## Custom Theming

Use `<style type="text/tailwindcss">` to define custom themes and components:

### Basic Theme

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
  
  <!-- Custom theme -->
  <style type="text/tailwindcss">
    @theme {
      --color-brand: oklch(0.6 0.2 250);
      --color-brand-hover: oklch(0.55 0.22 250);
      --font-display: 'Inter', sans-serif;
    }
  </style>
</head>
<body>
  <h1 class="font-display text-4xl">Custom Font</h1>
  <button class="bg-brand text-white px-4 py-2 rounded hover:bg-brand-hover">
    Brand Button
  </button>
</body>
</html>
```

### Component Styles

Define reusable component classes:

```html
<style type="text/tailwindcss">
  @layer components {
    .btn-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.5rem 1rem;
      font-weight: 500;
      border-radius: 0.375rem;
      background-color: var(--color-brand-500);
      color: white;
      transition: all 0.15s ease;
    }
    
    .btn-primary:hover {
      background-color: var(--color-brand-600);
    }
    
    .card {
      background: white;
      border-radius: 0.5rem;
      box-shadow: 0 4px 6px rgb(0 0 0 / 0.1);
      overflow: hidden;
    }
    
    .card-header {
      padding: 1rem 1.5rem;
      border-bottom: 1px solid var(--color-gray-200);
    }
    
    .card-body {
      padding: 1.5rem;
    }
  }
</style>
```

Usage:
```html
<button class="btn-primary">Primary Button</button>

<div class="card">
  <div class="card-header">Card Title</div>
  <div class="card-body">Card content</div>
</div>
```

### Multiple Theme Blocks

You can have multiple `<style type="text/tailwindcss">` blocks:

```html
<style type="text/tailwindcss">
  @theme {
    --color-primary: oklch(0.6 0.2 250);
  }
</style>

<style type="text/tailwindcss">
  @theme {
    --color-secondary: oklch(0.7 0.15 150);
  }
  
  @layer components {
    .alert {
      padding: 1rem;
      border-radius: 0.375rem;
    }
    
    .alert-success {
      background-color: oklch(0.8 0.1 150);
      color: oklch(0.3 0.1 150);
    }
  }
</style>
```

### Auto-Import Behavior

If your `<style type="text/tailwindcss">` doesn't include `@import`, the browser build automatically adds `@import "tailwindcss"`:

```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: blue;
  }
</style>
<!-- Automatically becomes: @import "tailwindcss"; @theme { ... } -->
```

### Explicit Layer Imports

You can import specific Tailwind layers:

```html
<style type="text/tailwindcss">
  @import "tailwindcss/theme";
  @import "tailwindcss/preflight";
  @import "tailwindcss/utilities";
  
  @theme {
    --color-custom: blue;
  }
</style>
```

Supported imports:
- `tailwindcss` or `tailwindcss/index.css`
- `tailwindcss/preflight` or `tailwindcss/preflight.css`
- `tailwindcss/theme` or `tailwindcss/theme.css`
- `tailwindcss/utilities` or `tailwindcss/utilities.css`

## Complete Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tailwind CSS v4 Browser Demo</title>
  
  <!-- Tailwind CSS browser build -->
  <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
  
  <!-- Custom theme and components -->
  <style type="text/tailwindcss">
    @theme {
      /* Brand colors */
      --color-brand-50: oklch(0.97 0.01 250);
      --color-brand-100: oklch(0.94 0.02 250);
      --color-brand-500: oklch(0.6 0.2 250);
      --color-brand-600: oklch(0.55 0.22 250);
      --color-brand-900: oklch(0.25 0.1 250);
      
      /* Custom font */
      --font-display: 'Inter', ui-sans-serif, system-ui, sans-serif;
      
      /* Extended spacing */
      --spacing-3xl: 48rem;
    }
    
    @layer components {
      .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border-radius: 0.375rem;
        transition: all 0.15s ease;
      }
      
      .btn-brand {
        background-color: var(--color-brand-500);
        color: white;
      }
      
      .btn-brand:hover {
        background-color: var(--color-brand-600);
      }
      
      .card {
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgb(0 0 0 / 0.1);
        overflow: hidden;
      }
      
      .card-header {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--color-gray-200);
      }
      
      .card-body {
        padding: 1.5rem;
      }
    }
  </style>
</head>
<body class="bg-gray-50 min-h-screen">
  <div class="max-w-4xl mx-auto px-4 py-12">
    <h1 class="font-display text-5xl font-bold text-brand-900 mb-4">
      Tailwind CSS v4 Browser
    </h1>
    <p class="text-xl text-gray-600 mb-8">
      Using Tailwind CSS directly in the browser without any build step.
    </p>
    
    <div class="grid md:grid-cols-2 gap-6">
      <div class="card">
        <div class="card-header">
          <h2 class="text-xl font-semibold">Custom Components</h2>
        </div>
        <div class="card-body">
          <button class="btn btn-brand">Brand Button</button>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="text-xl font-semibold">Responsive Design</h2>
        </div>
        <div class="card-body">
          <div class="bg-brand-50 md:bg-brand-100 p-4 rounded">
            Background changes at md breakpoint
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-8 card">
      <div class="card-header">
        <h2 class="text-xl font-semibold">Dark Mode</h2>
      </div>
      <div class="card-body">
        <div class="bg-white dark:bg-gray-900 text-black dark:text-white p-4 rounded">
          Toggle dark mode in browser settings to see this change
        </div>
      </div>
    </div>
  </div>
</body>
</html>
```

## Limitations

### No Plugin Support

The browser build does not support custom plugins or configuration files:

```html
<!-- This will NOT work -->
<style type="text/tailwindcss">
  @plugin "./my-plugin.css";
</style>
```

Error: `The browser build does not support plugins or config files.`

**Workaround:** Define component styles directly in `@layer components` instead of using plugins.

### No External @import

You cannot import external CSS files:

```html
<!-- This will NOT work -->
<style type="text/tailwindcss">
  @import "./custom.css";
</style>
```

Error: `The browser build does not support @import for "..."`

Only Tailwind's built-in layers can be imported (listed above).

### Performance Considerations

**Initial Load:**
- JavaScript must parse and compile CSS before styles apply
- Visible flash of unstyled content possible on slow connections

**Large Pages:**
- More classes = longer compilation time
- Compilation happens on each page load

**Dynamic Content:**
- Each DOM change triggers incremental recompilation
- Frequent updates can cause performance overhead

**For Production:**
Use the CLI or bundler integration which:
- Pre-compiles all CSS at build time
- Produces smaller, optimized bundles
- No runtime JavaScript overhead
- Better caching and CDN delivery

## Migration from v3 Play CDN

### Tailwind CSS v3

```html
<script src="https://cdn.tailwindcss.com"></script>

<!-- Custom config (JavaScript) -->
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          brand: '#3b82f6',
        },
      },
    },
  }
</script>
```

### Tailwind CSS v4

```html
<script src="https://unpkg.com/@tailwindcss/browser@4"></script>

<!-- Custom theme (CSS) -->
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.6 0.2 250);
  }
</style>
```

**Key Changes:**
- v4 uses OKLCH colors by default (convert from hex/RGB)
- Configuration is CSS-based, not JavaScript
- New utility classes and removed deprecated ones
- Better performance with incremental compilation

## Troubleshooting

### Styles Not Applying

**Problem:** Utility classes don't seem to work.

**Solutions:**
1. **Check script loaded**: Open DevTools Console, look for errors
2. **Verify script placement**: Should be in `<head>` before body content
3. **Check for typos**: Utility class names must be exact
4. **Clear cache**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
5. **Wait for compilation**: Styles apply after JavaScript runs

### Custom Theme Not Working

**Problem:** Custom colors or components don't work.

**Solutions:**
1. **Use correct type attribute**: Must be `type="text/tailwindcss"` (not `type="text/css"`)
2. **Place in `<head>`**: Theme should be before body content
3. **Check syntax**: Use CSS `@theme` directive, not JavaScript config
4. **Verify variable names**: Must follow naming conventions (`--color-*`, `--font-*`, etc.)

### Performance Issues

**Problem:** Page feels slow or stuttery.

**Solutions:**
1. **Reduce class count**: Fewer unique classes = faster compilation
2. **Check DevTools Performance tab**: Look for compilation bottlenecks
3. **Use production build**: For real apps, use CLI/bundler instead
4. **Consider caching**: Static sites can be cached after first load

### Common Errors

**Error: "The browser build does not support plugins or config files"**
- Remove `@plugin` directives from your CSS
- Use inline `@theme` and `@layer components` instead

**Error: "The browser build does not support @import for '...'"**
- Only import from `tailwindcss/*` paths
- Cannot import external CSS files
- Move custom styles to `<style type="text/tailwindcss">` blocks

**Error: Script doesn't load from CDN**
- Check internet connection
- Try different CDN: `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4/dist/index.global.js`
- Verify URL is correct and version exists

## Advanced Usage

### Dynamic Class Injection

The browser build automatically detects new classes added to the DOM:

```javascript
// Add element with new classes dynamically
const btn = document.createElement('button');
btn.className = 'px-4 py-2 bg-green-500 text-white rounded';
document.body.appendChild(btn);

// Browser build will automatically compile and apply these classes
```

### Conditional Rendering

Works seamlessly with conditional rendering:

```html
<div id="dynamic-content"></div>

<script>
  // Show/hide content based on condition
  function toggleContent() {
    const container = document.getElementById('dynamic-content');
    if (container.classList.contains('hidden')) {
      container.classList.remove('hidden');
      container.innerHTML = '<p class="text-blue-500">Now visible!</p>';
    } else {
      container.classList.add('hidden');
    }
  }
</script>
```

### Integration with Frameworks

Works with vanilla JavaScript and frameworks:

**React (CDN):**
```html
<script src="https://unpkg.com/@tailwindcss/browser@4"></script>
<script src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>

<div id="root"></div>

<script>
  const { createElement: h } = React;
  const { render } = ReactDOM;
  
  function App() {
    return h('div', { className: 'p-4 bg-gray-100' },
      h('h1', { className: 'text-2xl font-bold' }, 'Hello React!')
    );
  }
  
  render(h(App), document.getElementById('root'));
</script>
```

**Vue (CDN):**
```html
<script src="https://unpkg.com/@tailwindcss/browser@4"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<div id="app">
  <h1 class="text-2xl font-bold">{{ message }}</h1>
  <button class="px-4 py-2 bg-blue-500 text-white rounded" @click="count++">
    Count: {{ count }}
  </button>
</div>

<script>
  const { createApp } = Vue;
  
  createApp({
    data() {
      return {
        message: 'Hello Vue!',
        count: 0
      }
    }
  }).mount('#app');
</script>
```

## Best Practices

### 1. Keep Theme Organized

```html
<style type="text/tailwindcss">
  /* Colors */
  @theme {
    --color-brand-500: oklch(0.6 0.2 250);
    --color-brand-600: oklch(0.55 0.22 250);
  }
  
  /* Typography */
  @theme {
    --font-display: 'Inter', sans-serif;
  }
  
  /* Components */
  @layer components {
    .btn-primary { /* ... */ }
    .card { /* ... */ }
  }
</style>
```

### 2. Use Semantic Component Names

```html
<style type="text/tailwindcss">
  @layer components {
    /* Good: semantic */
    .btn-primary { /* ... */ }
    .card-header { /* ... */ }
    
    /* Avoid: implementation-specific */
    .blue-button-with-shadow { /* ... */ }
  }
</style>
```

### 3. Document Custom Classes

```html
<style type="text/tailwindcss">
  /* 
   * Brand button - primary call-to-action
   * Usage: <button class="btn-brand">Click</button>
   */
  @layer components {
    .btn-brand {
      background-color: var(--color-brand-500);
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
    }
    
    .btn-brand:hover {
      background-color: var(--color-brand-600);
    }
  }
</style>
```

### 4. Minimize Custom Theme for Production

For production sites, consider moving to a build process:
- Pre-compile CSS for better performance
- Smaller bundle sizes
- Better caching strategies
- No runtime JavaScript overhead

## API Reference

### Script Tag

```html
<script src="https://unpkg.com/@tailwindcss/browser@4"></script>
```

No configuration options available - the script auto-initializes.

### Style Tag Requirements

Custom styles must use:

```html
<style type="text/tailwindcss">
  /* Your Tailwind CSS */
</style>
```

The `type="text/tailwindcss"` attribute is **required** for the browser build to recognize and process the content.

### Supported Directives

Inside `<style type="text/tailwindcss">`:

- `@import` - Import Tailwind layers (limited to `tailwindcss/*` paths)
- `@theme` - Define custom theme values (generates utilities)
- `@theme reference` - Reference-only theme values (no utilities)
- `@theme inline` - Component-scoped theme values
- `@layer` - Define layer order and component styles
- `@utility` - Create custom utilities (in `@layer utilities`)

### Not Supported

- `@plugin` - Plugin system not available in browser build
- External `@import` - Cannot import custom CSS files
- JavaScript configuration - All config must be in CSS
- Custom module loading - No support for loading external modules

## Resources

- [@tailwindcss/browser on npm](https://www.npmjs.com/package/@tailwindcss/browser)
- [Browser package on GitHub](https://github.com/tailwindlabs/tailwindcss/tree/main/packages/@tailwindcss-browser)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [OKLCH Color Converter](https://oklch.com/)
- [Playground](https://play.tailwindcss.com/) - Test utilities online
