# htmx Performance Optimization

This reference covers performance tuning and optimization techniques for htmx 2.x applications.

## Loading & Caching

### Enable Browser Caching

Cache static assets including htmx itself:

```python
# Flask - set cache headers for static files
@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response
```

### Use CDN for htmx Library

Load htmx from CDN with long cache:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" 
        integrity="sha384-..." 
        crossorigin="anonymous">
</script>
```

### Preload Critical Resources

```html
<!-- Preload htmx if not in critical path -->
<link rel="preload" href="/static/htmx.min.js" as="script">

<!-- Preload extension scripts -->
<link rel="preload" href="/static/ext/ws.js" as="script">
```

### Leverage htmx Preload Extension

Preload content user is likely to request:

```html
<script src="https://unpkg.com/htmx.org/dist/ext/preload.js"></script>

<!-- Preload on hover -->
<a href="/article/123" 
   hx-get="/article/123"
   hx-ext="preload"
   hx-trigger="hover 1s">
    Read Article
</a>

<!-- Preload next page in sequence -->
<a href="/page/2" 
   hx-get="/page/2"
   hx-ext="preload"
   hx-trigger="revealed">
    Next Page
</a>
```

## Request Optimization

### Reduce Request Frequency with Throttling

Avoid excessive requests:

```html
<!-- Bad: fires on every keyup -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup">
       Search...
</input>

<!-- Good: throttled -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:300ms">
       Search...
</input>
```

### Cancel Redundant Requests

Use `hx-sync` to cancel in-flight requests:

```html
<!-- Cancel previous search request -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:300ms"
       hx-sync="#results @cancel"
       hx-target="#results">
       Search...
</input>
```

### Batch Operations

Combine multiple operations into single request:

```html
<!-- Bad: multiple requests -->
<button hx-post="/like">Like</button>
<button hx-post="/share">Share</button>
<button hx-post="/bookmark">Bookmark</button>

<!-- Good: single request -->
<form hx-post="/bulk-actions">
    <input type="hidden" name="actions" value="like,share,bookmark">
    <button type="submit">Save All</button>
</form>
```

### Use Conditional Requests

Implement ETag/If-None-Match:

```python
# Flask - support conditional requests
@app.route('/article/<id>')
def get_article(id):
    article = get_article(id)
    etag = generate_etag(article)
    
    if request.headers.get('If-None-Match') == etag:
        return '', 304  # Not Modified
    
    response = make_response(render_template('article.html', article=article))
    response.headers['ETag'] = etag
    return response
```

## Response Optimization

### Return Minimal HTML

Send only what's needed:

```html
<!-- Bad: full page in response -->
<!DOCTYPE html>
<html>
<head><title>...</title></head>
<body>
    <nav>...</nav>
    <div id="content">...</div>
    <footer>...</footer>
</body>
</html>

<!-- Good: just the fragment -->
<div class="article">
    <h2>{{ article.title }}</h2>
    <div>{{ article.body }}</div>
</div>
```

### Use OOB Swaps Efficiently

Update multiple elements in single response:

```html
<!-- Single request updates multiple areas -->
<button hx-post="/update-dashboard">
    Refresh Dashboard
</button>

<!-- Server returns -->
<div id="user-count" hx-swap-oob="innerHTML">125</div>
<div id="notifications" hx-swap-oob="innerHTML">5 new</div>
<div id="recent-activity" hx-swap-oob="innerHTML">...</div>
```

### Compress Responses

Enable gzip/brotli compression:

```python
# Flask - enable compression
from flask_compress import Compress

compress = Compress()
compress.init_app(app)

# Or with Werkzeug
@app.after_request
def compress_response(response):
    if response.content_length > 500:
        response.headers['Content-Encoding'] = 'gzip'
    return response
```

### Defer Non-Critical Updates

Use `hx-swap` delays for non-urgent content:

```html
<!-- Delay swap for non-critical content -->
<div hx-get="/analytics" 
     hx-trigger="load delay:2s"
     hx-swap="innerHTML swap:500ms">
    Loading analytics...
</div>
```

## DOM Manipulation Optimization

### Use Appropriate Swap Style

Choose fastest swap for your use case:

```html
<!-- innerHTML is fastest -->
<div hx-get="/content" 
     hx-swap="innerHTML">
    Fast
</div>

<!-- outerHTML causes more reflows -->
<div hx-get="/content" 
     hx-swap="outerHTML">
    Slower
</div>

<!-- Morph swaps are slowest but preserve state -->
<div hx-ext="idiomorph"
     hx-get="/content"
     hx-swap="morph">
    Slowest but preserves state
</div>
```

### Minimize Reflows

Batch DOM changes:

```html
<!-- Update multiple elements in single response -->
<button hx-post="/update-row">
    Update
</button>

<!-- Server returns all updates at once -->
<td id="name" hx-swap-oob="innerHTML">New Name</td>
<td id="status" hx-swap-oob="innerHTML">Active</td>
<td id="date" hx-swap-oob="innerHTML">2024-01-01</td>
```

### Avoid Large DOM Updates

Paginate or lazy load large lists:

```html
<!-- Bad: load all 1000 items at once -->
<div hx-get="/items?limit=1000">All Items</div>

<!-- Good: infinite scroll -->
<div id="items-container">
    <div hx-get="/items?page=1&limit=20" 
         hx-swap="innerHTML">
        <!-- First 20 items -->
    </div>
    <div hx-get="/items?page=2&limit=20"
         hx-trigger="revealed"
         hx-swap="beforeend reveal:100px">
        Loading more...
    </div>
</div>
```

### Use Virtual Scrolling for Large Lists

For very large lists, implement virtual scrolling:

```javascript
// Only render visible items
function renderVisibleItems(items, viewport) {
    const startIndex = Math.floor(viewport.scrollTop / itemHeight);
    const endIndex = startIndex + Math.ceil(viewport.height / itemHeight) + 2;
    
    return items.slice(startIndex, endIndex).map(item => `
        <div class="item">${item.name}</div>
    `).join('');
}
```

## Trigger Optimization

### Use Efficient Triggers

Choose appropriate trigger events:

```html
<!-- Bad: fires too frequently -->
<div hx-get="/track" 
     hx-trigger="mousemove">
    Track mouse
</div>

<!-- Good: throttled -->
<div hx-get="/track" 
     hx-trigger="mousemove throttle:100ms">
    Track mouse
</div>
```

### Lazy Load with Intersection Observer

Use `revealed` trigger for below-fold content:

```html
<!-- Load only when visible -->
<div hx-get="/ads/bottom" 
     hx-trigger="revealed once"
     hx-swap="outerHTML">
    <img src="placeholder.jpg" alt="Ad placeholder">
</div>
```

### Debounce Frequent Updates

```html
<!-- Search with debounce -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="input changed delay:500ms"
       hx-target="#results">
       Type to search...
</input>
```

## History & Caching

### Optimize History Cache Size

Adjust based on usage patterns:

```javascript
// Default is 10 pages
htmx.config.historyCacheSize = 20; // For navigation-heavy apps

// Or disable if not needed
htmx.config.historyEnabled = false;
```

### Use hx-push-url Selectively

Only push URLs that need browser navigation:

```html
<!-- Good: meaningful URL changes -->
<button hx-get="/articles/123" 
        hx-push-url="/articles/123">
    Read Article
</button>

<!-- Bad: unnecessary history entries -->
<button hx-post="/like" 
        hx-push-url="true">  <!-- Don't do this -->
    Like
</button>
```

### Prefer hx-replace-url for Searches

Avoid polluting history with search queries:

```html
<input name="q" 
       hx-get="/search"
       hx-target="#results"
       hx-replace-url="true">  <!-- Replaces current URL -->
       Search...
</input>
```

## Extension Performance

### Load Extensions Lazily

Only load extensions when needed:

```javascript
// Load WebSocket extension only if chat is visible
if (document.querySelector('[hx-ws]')) {
    const script = document.createElement('script');
    script.src = '/static/ext/ws.js';
    document.head.appendChild(script);
}
```

### Use Built-in Features Over Extensions

Prefer core features when possible:

```html
<!-- Good: use built-in hx-disabled-elt -->
<button hx-post="/submit" 
        hx-disabled-elt="this">
    Submit
</button>

<!-- Less efficient: loading-states extension -->
<button hx-post="/submit" 
        hx-ext="loading-states"
        loading-class="disabled">
    Submit
</button>
```

## Network Optimization

### Use Service Workers for Offline Support

Cache htmx responses:

```javascript
// service-worker.js
self.addEventListener('fetch', (event) => {
    if (event.request.headers.get('HX-Request') === 'true') {
        event.respondWith(
            caches.open('htmx-cache').then((cache) => {
                return cache.match(event.request).then((response) => {
                    return response || fetch(event.request).then((response) => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                });
            })
        );
    }
});
```

### Implement Request Prioritization

Use `hx-trigger` delays to prioritize:

```html
<!-- Critical content loads immediately -->
<div hx-get="/main-content" 
     hx-trigger="load">
    Main Content
</div>

<!-- Non-critical loads after delay -->
<div hx-get="/recommendations" 
     hx-trigger="load delay:1s">
    Recommendations
</div>

<!-- Lowest priority -->
<div hx-get="/analytics" 
     hx-trigger="load delay:3s">
    Analytics
</div>
```

### Reduce Payload Size

Minimize response size:

```html
<!-- Remove unnecessary whitespace in templates -->
{% include 'compact_template.html' %}

<!-- Use partials for specific content -->
<div hx-get="/partials/header">Header</div>
<div hx-get="/partials/footer">Footer</div>
```

## Monitoring & Debugging

### Enable Performance Monitoring

```javascript
// Log request timing
document.body.addEventListener('htmx:beforeRequest', (event) => {
    event.detail.startTime = performance.now();
});

document.body.addEventListener('htmx:afterRequest', (event) => {
    const duration = performance.now() - event.detail.requestConfig.startTime;
    console.log(`Request to ${event.detail.requestConfig.path} took ${duration.toFixed(2)}ms`);
});
```

### Track Slow Requests

```javascript
const slowRequests = [];

document.body.addEventListener('htmx:afterRequest', (event) => {
    const duration = event.detail.requestConfig.duration || 0;
    if (duration > 1000) {  // Slower than 1 second
        slowRequests.push({
            path: event.detail.requestConfig.path,
            duration: duration,
            timestamp: Date.now()
        });
        
        if (slowRequests.length > 100) {
            slowRequests.shift();
        }
        
        console.warn('Slow request:', slowRequests[slowRequests.length - 1]);
    }
});
```

### Use htmx Logging for Debugging

```javascript
// Enable comprehensive logging in development
if (process.env.NODE_ENV === 'development') {
    htmx.logAll();
}

// Custom logger with performance data
htmx.logger = function(elt, eventName, detail) {
    if (eventName.includes('Request')) {
        console.log(`[${eventName}] ${detail.requestConfig.path}`, {
            duration: detail.requestConfig.duration,
            status: detail.xhr?.status
        });
    }
};
```

## Performance Checklist

- [ ] Enable response compression (gzip/brotli)
- [ ] Set appropriate cache headers
- [ ] Use CDN for htmx library
- [ ] Implement request throttling/debouncing
- [ ] Cancel redundant requests with hx-sync
- [ ] Return minimal HTML fragments
- [ ] Use OOB swaps for multiple updates
- [ ] Lazy load below-fold content
- [ ] Optimize history cache size
- [ ] Choose appropriate swap styles
- [ ] Monitor slow requests
- [ ] Enable performance logging in development
- [ ] Use preload extension for likely navigation
- [ ] Minimize DOM reflows
- [ ] Batch operations when possible

## Advanced Techniques

### Predictive Preloading

Preload based on user behavior:

```javascript
// Track user patterns and preload likely next pages
const userPatterns = [];

document.body.addEventListener('htmx:afterRequest', (event) => {
    userPatterns.push(event.detail.requestConfig.path);
    
    // If user viewing article, preload related articles
    if (event.detail.requestConfig.path.startsWith('/articles/')) {
        preloadRelatedArticles();
    }
});

function preloadRelatedArticles() {
    fetch('/api/related-articles', {
        headers: { 'X-Preload': 'true' }
    });
}
```

### Progressive Enhancement Fallback

Ensure fast initial load:

```html
<!-- Content visible immediately -->
<div id="comments">
    <p>Loading comments...</p>
</div>

<!-- Enhanced with htmx -->
<div id="comments" 
     hx-get="/comments"
     hx-trigger="load delay:500ms"
     hx-swap="innerHTML">
    <p>Loading comments...</p>
</div>
```

## Resources

- [htmx Performance Essay](https://htmx.org/essays/performance/)
- [Web Performance Best Practices](https://web.dev/fast/)
- [HTTP Caching Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

## Next Steps

- [Common Patterns](10-common-patterns.md) - Optimized pattern implementations
- [Security Best Practices](12-security-best-practices.md) - Security guidance
- [Events and API Reference](08-events-api.md) - Complete API documentation
