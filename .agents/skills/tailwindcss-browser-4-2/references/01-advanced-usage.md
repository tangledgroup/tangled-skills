# tailwindcss-browser-4-2 - Advanced Usage

This reference covers advanced topics, complete examples, and detailed configuration.

## Advanced Features

### JavaScript Configuration

Configure Tailwind via global variable before the script loads:

```html
<head>
  <script>
    window.tailwindcss = {
      // Enable important selector
      important: false,
      
      // Prefix for all utilities (prevents conflicts)
      prefix: '',
      
      // Dark mode strategy: 'media' | 'class' | 'selector'
      darkMode: 'media',
      
      // Custom theme extensions
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#f0f9ff',
              500: '#0ea5e9',
              900: '#0c4a6e'
            }
          }
        }
      }
    }
  </script>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
```

### Source Content Specification

Tell Tailwind where to scan for class names:

```html
<script>
  window.tailwindcss = {
    content: [
      './pages/**/*.html',
      '{app,components}/**/*.{js,ts,jsx,tsx}'
    ]
  }
</script>
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

### Variants and Pseudo-classes

All standard Tailwind variants work:

```html
<!-- Hover states -->
<div class="hover:bg-blue-500">Hover me</div>

<!-- Focus states -->
<input class="focus:ring-2 focus:ring-blue-500" />

<!-- Active states -->
<button class="active:scale-95">Click me</button>

<!-- Group variants -->
<div class="group">
  <span class="group-hover:text-blue-500">Hover parent</span>
</div>

<!-- Peer variants -->
<input class="peer" />
<label class="peer-placeholder-shown:text-gray-400">Label</label>

<!-- Dark mode -->
<div class="dark:bg-gray-800">Dark background</div>

<!-- Responsive breakpoints -->
<div class="w-full md:w-1/2 lg:w-1/3">Responsive width</div>
```

### OKLCH Color Space

Tailwind v4 uses OKLCH color space by default for better color accuracy:

```html
<!-- All standard colors use OKLCH internally -->
<div class="bg-blue-500 text-white">Blue uses OKLch</div>

<!-- Custom OKLCH colors -->
<style type="text/tailwindcss">
  @theme {
    --color-custom: oklch(60% 0.2 250);
  }
</style>
<div class="bg-custom">Custom OKLCH color</div>
```

## Performance Considerations

### Production vs Development

**Browser build is ideal for:**
- Prototyping and development
- Documentation sites with low traffic
- Internal tools and dashboards
- Learning and experimentation

**Consider a build step for production when:**
- High-traffic public websites
- Need optimal CSS bundle size
- Require advanced optimizations
- Building complex web applications

### Performance Tips

1. **Minimize custom theme**: Large `@theme` blocks increase compilation time
2. **Use CDN caching**: Leverage CDN cache headers for the script
3. **Consider inlining critical CSS**: For above-the-fold content
4. **Monitor Web Worker usage**: Browser build uses Web Workers which may have overhead

### Bundle Size

The browser build includes all Tailwind utilities (~100KB gzipped). Unused utilities are purged at runtime, but the initial download includes everything.

## Integration Examples

### With Hotwire/Turbo

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <script src="https://unpkg.com/@hotwired/turbo@7.3.0/dist/turbo.es2017-umd.js"></script>
</head>
<body>
  <div data-turbo-frame="main">
    <nav class="bg-gray-800 text-white p-4">
      <a href="/home" class="px-4 py-2 hover:bg-gray-700 rounded">Home</a>
      <a href="/about" class="px-4 py-2 hover:bg-gray-700 rounded">About</a>
    </nav>
    <main class="p-8">
      <h1 class="text-3xl font-bold">Turbo Powered Page</h1>
    </main>
  </div>
</body>
</html>
```

### With Alpine.js

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>
  <div x-data="{ open: false }">
    <button 
      @click="open = !open"
      class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
    >
      Toggle Dropdown
    </button>
    
    <div x-show="open" class="mt-2 p-4 bg-gray-100 rounded">
      <p>Dropdown content with Tailwind styling</p>
    </div>
  </div>
</body>
</html>
```

### With Vanilla JavaScript

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-50 min-h-screen">
  <div id="app" class="max-w-4xl mx-auto p-8">
    <h1 class="text-4xl font-bold text-gray-900 mb-6">Dynamic Content</h1>
    <div id="content" class="space-y-4"></div>
  </div>

  <script>
    // Dynamic content with Tailwind classes
    const items = [
      { title: 'Item 1', desc: 'First item description' },
      { title: 'Item 2', desc: 'Second item description' }
    ];
    
    const container = document.getElementById('content');
    items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'bg-white p-6 rounded-lg shadow-md';
      div.innerHTML = `
        <h2 class="text-xl font-semibold text-gray-900">${item.title}</h2>
        <p class="text-gray-600 mt-2">${item.desc}</p>
      `;
      container.appendChild(div);
    });
  </script>
</body>
</html>
```

## Troubleshooting

### Utilities Not Applying

**Check the script is loaded before content:**
```html
<head>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
```

**Verify no typos in class names:**
```html
<!-- Wrong -->
<div class="txr-4xl">Should be text-4xl</div>

<!-- Correct -->
<div class="text-4xl">Properly sized text</div>
```

### Custom Theme Not Working

**Ensure `@theme` is in a style block with correct type:**
```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.6 0.2 260);
  }
</style>
```

Not:
```html
<!-- Wrong - missing type attribute -->
<style>
  @theme { ... }
</style>
```

### Build Errors in Console

**Check for invalid CSS syntax:**
```html
<style type="text/tailwindcss">
  /* Valid */
  @theme { --color-brand: oklch(0.6 0.2 260); }
  
  /* Invalid - missing semicolon */
  @theme { --color-brand: oklch(0.6 0.2 260) }
</style>
```

### Performance Issues

**For production sites with many utilities, consider:**
1. Using a build step instead of browser compilation
2. Reducing the number of unique utility classes
3. Implementing code splitting for large applications

## Migration from Build Step

Moving from Node.js build to browser:

**Before (with build):**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```css
/* input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**After (browser only):**
```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

No configuration files needed. Move `tailwind.config.js` settings to:
```html
<script>
  window.tailwindcss = {
    theme: { /* your config */ }
  }
</script>
```

## Best Practices

1. **Use for prototyping, not production**: Browser build is great for development but consider a build step for high-traffic sites
2. **Leverage CDN caching**: The script benefits from CDN cache headers
3. **Keep custom themes minimal**: Large theme extensions increase compilation time
4. **Test in target browsers**: Ensure Web Worker support in your audience's browsers
5. **Monitor performance**: Use browser dev tools to check compilation times

## Reference

- **Package**: @tailwindcss/browser@4
- **NPM**: https://www.npmjs.com/package/@tailwindcss/browser
- **GitHub**: https://github.com/tailwindlabs/tailwindcss/tree/main/packages/%40tailwindcss-browser
- **CDN**: https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4

## Limitations

- Requires Web Worker support (not available in all contexts)
- All utilities downloaded initially (~100KB gzipped)
- Runtime compilation adds overhead on page load
- Not suitable for server-side rendering
- Limited customization compared to full build setup
- Cannot use plugins that require Node.js APIs
