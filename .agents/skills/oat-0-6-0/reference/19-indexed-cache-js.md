# Indexed-Cache.js - Static Asset Caching in IndexedDB

A tiny JavaScript library that "sideloads" static assets (script, link, and img tags) using the fetch() API and caches them in IndexedDB for long-term storage. Eliminates dependency on browser cache and reduces HTTP requests on subsequent page loads.

[**GitHub**](https://github.com/knadh/indexed-cache) | [**npm**](https://www.npmjs.com/package/@knadh/indexed-cache)

## Use Cases

This library is designed for **very specific scenarios**. Consider using it if several of these apply:

- Large static files (JS, CSS) that rarely change
- High traffic from returning users who access pages with the same assets frequently
- Mobile webview environments where browser cache gets evicted due to OS pressure
- Bandwidth optimization is a concern
- Service Workers aren't an option (e.g., mobile webviews)

> **Important**: This is not a general-purpose caching solution. For most websites, standard browser caching or Service Workers are better options.

## How It Works

1. Static assets are marked with `data-src` instead of `src`/`href`
2. Indexed-Cache fetches these assets using the fetch() API
3. Assets are stored as Blobs in IndexedDB
4. On subsequent visits, assets are loaded from IndexedDB instead of HTTP requests
5. Unlike browser cache, IndexedDB is not automatically cleared by the browser

## Features

- Supports `<script>`, `<link>`, and `<img>` tags
- Respects `defer`/`async` attributes on scripts
- Per-tag cache invalidation with TTL (expiry date)
- Per-tag cache invalidation with hash change
- ES6 modules and legacy bundle support

## Installation

### npm

```bash
npm install @knadh/indexed-cache
```

### CDN (ES Module)

```html
<script type="module">
  import IndexedCache from 'https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.esm.min.js';
</script>
```

### CDN (Legacy)

```html
<script src="https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.legacy.min.js" nomodule></script>
```

## Basic Usage

### Mark Assets for Caching

Change `src`/`href` to `data-src` and add a unique `data-key`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Indexed Cache Demo</title>
  
  <!-- CSS file with caching -->
  <link rel="stylesheet" type="text/css"
    data-key="main-styles"
    data-src="/css/main.css" />
  
  <!-- JavaScript bundle with caching -->
  <script data-key="app-bundle" data-src="/js/app.js"></script>
</head>
<body>
  <h1>My Application</h1>
  
  <!-- Regular script (not cached) -->
  <script src="/js/inline.js"></script>
  
  <!-- Image with caching -->
  <img data-key="hero-image" 
       data-src="/images/hero.png" 
       alt="Hero" />
  
  <!-- Initialize indexed-cache at the end -->
  <script src="https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.min.js" nomodule></script>
  <script>
    const ic = new IndexedCache();
    ic.init().then(function() {
      ic.load();
    }).catch(function(err) {
      console.log("Error loading indexed-cache:", err);
    });
  </script>
</body>
</html>
```

### Cache Invalidation with Hash

Change the `data-hash` value when the file changes to force re-caching:

```html
<!-- Hash from build system or version control -->
<script data-key="app-bundle" 
        data-src="/js/app.bundle.js" 
        data-hash="a1b2c3d4e5f6"></script>

<img data-key="logo" 
     data-src="/images/logo.png" 
     data-hash="v2.1.0" />
```

When the hash changes, Indexed-Cache will refetch and re-cache the asset.

### Cache Invalidation with Expiry

Set an expiry date after which the cache is invalidated:

```html
<script data-key="analytics" 
        data-src="/js/analytics.js" 
        data-expiry="2029-12-31T23:59:59Z"></script>

<link rel="stylesheet" 
      data-key="theme" 
      data-src="/css/theme.css" 
      data-expiry="2025-06-01T00:00:00Z" />
```

### Combined Hash and Expiry

```html
<script data-key="main-bundle" 
        data-src="/js/main.js" 
        data-hash="build-12345"
        data-expiry="2029-12-31T23:59:59Z">
</script>
```

The asset is re-fetched if either the hash changes OR the expiry is crossed.

## Advanced Usage

### ES Module with Conditional Loading

Load modern (ESM) and legacy bundles based on browser support:

```html
<head>
  <!-- Modern browsers (ES modules) -->
  <script type="module">
    import IndexedCache from 'https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.esm.min.js';
    
    const ic = new IndexedCache();
    ic.init().then(function() {
      ic.load();
    }).catch(function(err) {
      console.log("Error:", err);
    });
  </script>
  
  <!-- Legacy browsers (no ES modules) -->
  <script src="https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.legacy.min.js" nomodule></script>
  <script nomodule>
    const ic = new IndexedCache();
    ic.init().then(function() {
      ic.load();
      // Trigger load event for scripts that depend on it
      document.dispatchEvent(new Event('load'));
    }).catch(function(err) {
      console.log("Error:", err);
    });
  </script>
</head>
```

### Custom Configuration

```javascript
const ic = new IndexedCache({
  // Tags to process (default: ["script", "img", "link"])
  tags: ["script", "link"],
  
  // Database name (default: "indexed-cache")
  dbName: "my-app-cache",
  
  // Store name (default: "objects")
  storeName: "assets",
  
  // Prune unused cache entries (default: false)
  // If true, removes cached items not found on current page
  prune: false,
  
  // Skip caching entirely (default: false)
  // Forces HTTP fetch every time - useful for debugging
  debug: false
});

ic.init().then(function() {
  ic.load();
});
```

### Manual Asset Loading

```javascript
const ic = new IndexedCache();

await ic.init();

// Load specific asset by key
const blob = await ic.get('app-bundle');
if (blob) {
  const url = URL.createObjectURL(blob);
  const script = document.createElement('script');
  script.src = url;
  document.head.appendChild(script);
}

// Check if asset is cached
const isCached = await ic.has('main-styles');

// Remove asset from cache
await ic.remove('old-bundle');

// Clear entire cache
await ic.clear();
```

### Progress Callbacks

```javascript
const ic = new IndexedCache();

await ic.init();

ic.load({
  onProgress: (total, loaded, currentKey) => {
    console.log(`Loading ${loaded}/${total} assets, current: ${currentKey}`);
    
    // Update progress bar
    const percent = (loaded / total) * 100;
    document.getElementById('progress').value = percent;
  },
  
  onComplete: () => {
    console.log('All assets loaded');
    document.getElementById('loader').style.display = 'none';
  },
  
  onError: (key, error) => {
    console.error(`Failed to load ${key}:`, error);
  }
});
```

## Important Considerations

### CORS Requirements

Since Indexed-Cache uses fetch(), all assets must be served with proper CORS headers:

```
Access-Control-Allow-Origin: *
```

Or your specific domain.

### First-Paint Flash

Scripts and styles load after HTML is fetched and rendered, which may cause a brief flash. Handle this by:

1. Showing a loading indicator
2. Using critical CSS inline
3. Deferring non-essential content

### Inline Script Tags

**Important**: Ensure no whitespace between opening and closing script tags:

```html
<!-- CORRECT - No space between tags -->
<script data-src="file.js" data-key="key"></script>

<!-- WRONG - Space will be executed as inline script -->
<script data-src="file.js" data-key="key">
</script>
```

### document.onload Event

Scripts that rely on `document.onload` won't trigger automatically. Manually dispatch the event:

```javascript
const ic = new IndexedCache();
ic.init().then(function() {
  ic.load();
  
  // Trigger load event for scripts that depend on it
  document.dispatchEvent(new Event('load'));
});
```

## Complete Example with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Oat UI with Indexed Cache</title>
  
  <!-- Oat CSS (cached) -->
  <link rel="stylesheet" 
        data-key="oat-css" 
        data-src="https://unpkg.com/@knadh/oat/oat.min.css"
        data-hash="v0.6.0" />
  
  <!-- Custom styles (cached) -->
  <link rel="stylesheet" 
        data-key="custom-styles" 
        data-src="/css/custom.css"
        data-hash="build-abc123" />
  
  <style>
    /* Critical CSS for initial render */
    body {
      opacity: 0;
      transition: opacity 0.3s;
    }
    body.loaded {
      opacity: 1;
    }
    #loader {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 18px;
    }
  </style>
</head>
<body>
  <div id="loader">Loading...</div>
  
  <nav data-topnav>
    <div class="row">
      <div class="col-4 branding">
        <a href="/" class="logo">My App</a>
      </div>
    </div>
  </nav>
  
  <main style="padding: var(--space-6);">
    <h1>Welcome</h1>
    <p>This page uses Indexed-Cache for static assets.</p>
  </main>
  
  <!-- Oat JS (cached) -->
  <script data-key="oat-js" 
          data-src="https://unpkg.com/@knadh/oat/oat.min.js"
          data-hash="v0.6.0"></script>
  
  <!-- App JS (cached) -->
  <script data-key="app-js" 
          data-src="/js/app.js"
          data-hash="build-xyz789"></script>
  
  <!-- Indexed Cache (NOT cached - load fresh every time) -->
  <script type="module">
    import IndexedCache from 'https://unpkg.com/@knadh/indexed-cache@0.4.3/dist/indexed-cache.esm.min.js';
    
    const ic = new IndexedCache({
      dbName: 'oat-app-cache',
      prune: false
    });
    
    ic.init().then(function() {
      ic.load({
        onProgress: (total, loaded) => {
          console.log(`Loaded ${loaded}/${total} assets`);
        },
        onComplete: () => {
          // Hide loader
          document.getElementById('loader').style.display = 'none';
          document.body.classList.add('loaded');
          
          // Trigger load event
          document.dispatchEvent(new Event('load'));
        }
      });
    }).catch(function(err) {
      console.error("IndexedCache error:", err);
      document.getElementById('loader').textContent = 'Load error';
    });
  </script>
</body>
</html>
```

## Browser Compatibility

- Requires ES6 support (for modern bundle)
- Requires IndexedDB support
- Modern browsers: Chrome, Firefox, Safari, Edge
- Legacy bundle available for older browsers

### Supported Browsers

| Browser | Version | Bundle |
|---------|---------|--------|
| Chrome | 49+ | ESM / Legacy |
| Firefox | 51+ | ESM / Legacy |
| Safari | 10.1+ | ESM / Legacy |
| Edge | 16+ | ESM / Legacy |
| iOS Safari | 10.3+ | ESM / Legacy |
| Android Chrome | 49+ | ESM / Legacy |

## API Reference

### Constructor

```javascript
new IndexedCache(options)
```

**Options:**
- `tags`: Array of tag names to process (default: `["script", "img", "link"]`)
- `dbName`: IndexedDB database name (default: `"indexed-cache"`)
- `storeName`: IndexedDB store name (default: `"objects"`)
- `prune`: Remove unused cache entries (default: `false`)
- `debug`: Skip caching, always fetch from HTTP (default: `false`)

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `init()` | Initialize IndexedDB connection | Promise |
| `load(options)` | Load all cached assets | Promise |
| `get(key)` | Get asset blob by key | Promise&lt;Blob&gt; |
| `has(key)` | Check if key exists in cache | Promise&lt;boolean&gt; |
| `remove(key)` | Remove asset from cache | Promise |
| `clear()` | Clear entire cache | Promise |

### Load Options

```javascript
ic.load({
  onProgress: (total, loaded, currentKey) => {},
  onComplete: () => {},
  onError: (key, error) => {}
});
```

## Troubleshooting

### Assets Not Loading

1. Check browser console for errors
2. Verify CORS headers on asset URLs
3. Ensure `data-src` and `data-key` are set correctly
4. Check IndexedDB in browser dev tools

### Cache Not Invalidating

1. Change `data-hash` value
2. Set earlier `data-expiry` date
3. Clear IndexedDB manually in dev tools
4. Use `debug: true` to test HTTP fetching

### Scripts Not Executing

1. Ensure no whitespace in empty script tags
2. Dispatch `load` event manually if needed
3. Check script load order
4. Verify `defer`/`async` attributes are preserved

## Limitations

- Requires CORS-enabled servers
- First-page load may be slower (fetch + cache)
- Not suitable for frequently-changing assets
- IndexedDB quota limits (~50-80% of disk space)
- No automatic cache versioning (use hash/expiry)
- May cause flash of unstyled content

## When NOT to Use

- Small websites with few returning visitors
- Assets that change frequently
- When Service Workers are an option
- When bandwidth is not a concern
- For single-page applications with dynamic assets

## Related Libraries

- **tinyrouter.js**: Client-side routing
- **dragmove.js**: Draggable elements
- **floatype.js**: Floating autocomplete

Licensed under the MIT License.
