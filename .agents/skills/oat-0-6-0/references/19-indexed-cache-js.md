# IndexedCache.js - Browser Asset Caching

A tiny (~2.1KB) JavaScript library for sideloading static assets and caching them in IndexedDB for long-term storage.

## Overview

Cache static assets (images, fonts, CSS, JS) in the browser's IndexedDB for offline access and faster subsequent loads.

## Installation

### CDN
```html
<script src="https://unpkg.com/indexed-cache"></script>
```

### Download
```bash
wget https://raw.githubusercontent.com/knadh/indexed-cache/master/dist/indexed-cache.min.js
```

## Basic Usage

### Cache Assets

```javascript
const cache = new IndexedCache('my-app-cache', '1.0');

// Cache individual files
cache.cache('/images/logo.png');
cache.cache('/fonts/inter.woff2');
cache.cache('/css/styles.css');

// Cache multiple files
cache.cache([
  '/images/logo.png',
  '/images/banner.jpg',
  '/fonts/inter.woff2'
]);
```

### Check if Cached

```javascript
cache.isCached('/images/logo.png').then(cached => {
  if (cached) {
    console.log('File is cached');
  }
});
```

### Get Cached File

```javascript
cache.get('/images/logo.png').then(blob => {
  const url = URL.createObjectURL(blob);
  document.querySelector('#logo').src = url;
});
```

## Advanced Usage

### Cache with Metadata

```javascript
cache.cache('/images/photo.jpg', {
  metadata: {
    width: 1920,
    height: 1080,
    photographer: 'John Doe'
  }
});
```

### Get with Metadata

```javascript
cache.getWithMetadata('/images/photo.jpg').then(({ blob, metadata }) => {
  const url = URL.createObjectURL(blob);
  console.log('Metadata:', metadata);
});
```

### Clear Cache

```javascript
// Clear specific file
cache.remove('/images/old.png');

// Clear all cache
cache.clear();
```

## Version Management

```javascript
// Create cache with version
const cache = new IndexedCache('app-cache', '2.0');

// Check cache version
cache.version.then(v => console.log('Cache version:', v));

// Migrate between versions
cache.onUpgrade = (oldVersion, newVersion) => {
  console.log(`Upgrading from ${oldVersion} to ${newVersion}`);
  
  // Clear old cache or migrate data
  if (oldVersion < '1.5') {
    cache.clear();
  }
};
```

## Preload Assets on Startup

```javascript
const cache = new IndexedCache('app-cache', '1.0');

// List of critical assets to preload
const criticalAssets = [
  '/images/logo.png',
  '/fonts/inter.woff2',
  '/css/critical.css'
];

// Cache on app load
Promise.all(criticalAssets.map(url => cache.cache(url)))
  .then(() => console.log('Critical assets cached'))
  .catch(err => console.error('Cache failed:', err));
```

## Use Cached or Fallback

```javascript
async function loadImage(src) {
  try {
    // Try cached version first
    const blob = await cache.get(src);
    return URL.createObjectURL(blob);
  } catch (e) {
    // Fall back to network
    console.log('Not cached, loading from network');
    
    // Cache for next time
    cache.cache(src).catch(() => {});
    
    return src;
  }
}

// Usage
const imgUrl = await loadImage('/images/photo.jpg');
document.querySelector('img').src = imgUrl;
```

## Progress Tracking

```javascript
const cache = new IndexedCache('app-cache', '1.0');

const urls = ['/a.png', '/b.png', '/c.png'];
let cachedCount = 0;

urls.forEach((url, i) => {
  cache.cache(url)
    .then(() => {
      cachedCount++;
      const progress = (cachedCount / urls.length) * 100;
      console.log(`Cache progress: ${progress.toFixed(0)}%`);
      
      if (cachedCount === urls.length) {
        console.log('All assets cached!');
      }
    })
    .catch(err => console.error('Failed to cache:', url));
});
```

## Integration with Oat UI

```html
<article class="card">
  <header>
    <h3>Offline-Ready App</h3>
    <p class="text-light">Assets cached for offline use</p>
  </header>
  
  <div style="margin: var(--space-4) 0;">
    <progress id="cache-progress" value="0" max="100"></progress>
    <p class="text-light small mt-2"><span id="cache-status">Initializing...</span></p>
  </div>
  
  <footer>
    <button id="cache-btn">Cache Assets</button>
    <button id="clear-btn" class="outline">Clear Cache</button>
  </footer>
</article>

<script src="oat.min.js" defer></script>
<script src="indexed-cache.min.js" defer></script>
<script>
const cache = new IndexedCache('oat-app', '1.0');

const assets = [
  '/images/logo.png',
  '/images/avatar.svg',
  '/fonts/custom.woff2'
];

document.getElementById('cache-btn').addEventListener('click', async () => {
  const progress = document.getElementById('cache-progress');
  const status = document.getElementById('cache-status');
  
  let completed = 0;
  
  for (const asset of assets) {
    try {
      await cache.cache(asset);
      completed++;
      progress.value = (completed / assets.length) * 100;
      status.textContent = `Caching: ${completed}/${assets.length}`;
    } catch (err) {
      console.error('Failed to cache:', asset);
    }
  }
  
  status.textContent = 'All assets cached!';
  ot.toast('Assets cached successfully', 'Done', { variant: 'success' });
});

document.getElementById('clear-btn').addEventListener('click', () => {
  cache.clear();
  document.getElementById('cache-progress').value = 0;
  document.getElementById('cache-status').textContent = 'Cache cleared';
  ot.toast('Cache cleared', 'Info');
});

// Check cache status on load
async function checkCache() {
  let cachedCount = 0;
  
  for (const asset of assets) {
    if (await cache.isCached(asset)) {
      cachedCount++;
    }
  }
  
  const progress = document.getElementById('cache-progress');
  const status = document.getElementById('cache-status');
  
  progress.value = (cachedCount / assets.length) * 100;
  status.textContent = `${cachedCount}/${assets.length} assets cached`;
}

checkCache();
</script>
```

## PWA Integration

```javascript
// Cache assets for offline use in PWA
const cache = new IndexedCache('pwa-cache', '1.0');

// In service worker registration
navigator.serviceWorker.register('/sw.js').then(() => {
  // Cache critical assets
  cache.cache([
    '/offline.html',
    '/images/icon.png',
    '/app.js'
  ]);
});

// Handle offline state
window.addEventListener('offline', () => {
  ot.toast('You are now offline', 'Notice', { 
    variant: 'warning',
    duration: 0 // Persistent
  });
});

window.addEventListener('online', () => {
  ot.toast('Back online', 'Notice', { variant: 'success' });
});
```

## Image Lazy Loading with Cache

```javascript
async function lazyLoadImage(img) {
  const src = img.dataset.src;
  
  try {
    // Try cache first
    const blob = await cache.get(src);
    img.src = URL.createObjectURL(blob);
  } catch (e) {
    // Load from network and cache
    img.src = src;
    
    img.onload = () => {
      cache.cache(src).catch(() => {});
    };
  }
  
  img.removeAttribute('data-src');
}

// Observe images
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      lazyLoadImage(entry.target);
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  observer.observe(img);
});
```

## Options

```javascript
new IndexedCache(databaseName, version, {
  // Debug mode (logs operations)
  debug: false,
  
  // Called on cache upgrade
  onUpgrade: (oldVersion, newVersion) => {
    // Migration logic
  },
  
  // Called when file is cached
  onCached: (url) => {
    console.log('Cached:', url);
  },
  
  // Called when cache fails
  onError: (url, error) => {
    console.error('Cache error:', url, error);
  }
});
```

## Best Practices

### DO

- Version your cache for updates
- Cache critical assets on app init
- Provide fallback for uncached assets
- Clear old cache versions during upgrades
- Track cache progress for UX

### DON'T

- Cache large files without consideration
- Forget to handle cache failures
- Cache dynamic content that changes frequently
- Store sensitive data in cache
- Skip version management

## Browser Support

- Chrome, Firefox, Safari, Edge (modern versions)
- Requires IndexedDB support
- Graceful degradation for unsupported browsers

## Tips

1. Use cache versions to force refresh when assets change
2. Cache critical assets first for better offline UX
3. Show loading state while checking cache
4. Consider cache size limits (browsers may evict old data)
5. Combine with Service Workers for full offline support

Perfect for PWAs, offline-first apps, or any web app that needs to work reliably even with poor connectivity!
