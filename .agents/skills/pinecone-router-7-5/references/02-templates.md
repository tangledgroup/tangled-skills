# Templates in Pinecone Router 7.5

This reference covers inline templates, external templates, modifiers, embedded scripts, and the x-run directive for Pinecone Router v7.5.

## Inline Templates

Inline templates render content directly within the route declaration using an empty `x-template` attribute:

```html
<template x-route="/" x-template>
  <h1>Welcome to the Home Page</h1>
  <p>This content is rendered inline.</p>
</template>
```

### How Inline Templates Work

- Content is inserted into the DOM after the `<template>` element (similar to `x-if`)
- Template re-renders when route is matched again after visiting another route
- Embedded Alpine components and data work normally
- Multiple root elements are supported

### Multiple Root Elements

```html
<template x-route="/dashboard" x-template>
  <header><nav>Dashboard Navigation</nav></header>
  <main>
    <h1>Dashboard</h1>
    <stats-widget></stats-widget>
  </main>
  <footer>Last updated: <span x-text="new Date()"></span></footer>
</template>
```

All root elements are inserted sequentially after the template tag.

### Inline Templates with Target

Render inline templates into a specific target element using `.target` modifier:

```html
<template x-route="/about" x-template.target.app>
  <h1>About Us</h1>
  <p>Company information goes here.</p>
</template>

<div id="app">
  <!-- Template content renders here -->
</div>
```

## External Templates

External templates load HTML content from URLs, enabling content separation and reuse:

### Single External Template

```html
<template x-route="/contact" x-template="/templates/contact.html"></template>
```

When the route matches, Pinecone Router fetches `/templates/contact.html` and inserts its content.

### Multiple External Templates

Include multiple template files by passing an array:

```html
<template 
  x-route="/dashboard" 
  x-template="['/templates/header.html', '/templates/dashboard.html', '/templates/footer.html']"
></template>
```

Templates are fetched and rendered in order.

### Template File Structure

`/templates/contact.html`:
```html
<div x-data="contactForm()">
  <h1>Contact Us</h1>
  <form @submit.prevent="submit">
    <label>Name: <input x-model="name" required></label>
    <label>Email: <input x-model="email" type="email" required></label>
    <label>Message: <textarea x-model="message" required></textarea></label>
    <button type="submit">Send</button>
  </form>
  <div x-show="submitted" class="success">Thank you for contacting us!</div>
</div>

<script>
  Alpine.data('contactForm', () => ({
    name: '',
    email: '',
    message: '',
    submitted: false,
    async submit() {
      await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.name, email: this.email, message: this.message })
      })
      this.submitted = true
    }
  }))
</script>
```

## Template Modifiers

### `.target` Modifier

Specify a target element ID for template rendering:

```html
<!-- Render into element with id="main" -->
<template x-route="/products" x-template.target.main="/products.html"></template>

<div id="main">
  <!-- Products template renders here -->
</div>
```

**Global default target:**
```javascript
window.PineconeRouter.settings({ targetID: 'app' })
// All templates without explicit .target use #app
```

### `.preload` Modifier

Preload templates after initial page load at low priority:

```html
<!-- Preload 404 template immediately -->
<template x-route="notfound" x-template.preload="/404.html"></template>

<!-- Preload multiple templates -->
<template 
  x-route="/settings" 
  x-template.preload="['/settings/header.html', '/settings/content.html']"
></template>
```

**Benefits:**
- Faster navigation to preloaded routes (no fetch delay)
- Low priority doesn't block initial page load
- Templates cached in memory after first fetch

**Global preload setting:**
```javascript
window.PineconeRouter.settings({ preload: true })
// All templates preloaded automatically
```

### `.interpolate` Modifier

Use route parameters in template URLs:

```html
<!-- On /docs/guide, fetches /api/templates/docs/guide.html -->
<!-- On /docs/api, fetches /api/templates/docs/api.html -->
<template 
  x-route="/docs/:page" 
  x-template.interpolate="/api/templates/docs/:page.html"
></template>
```

**Use cases:**
- API-generated HTML based on route params
- Dynamic content from CMS
- Locale-specific templates: `/locale/:lang/:page.html`

**Important:** `.interpolate` cannot be combined with `.preload` (URLs unknown at preload time).

### Combining Modifiers

Modifiers can be chained in any order (except `.preload` + `.interpolate`):

```html
<!-- Preload and render into #app -->
<template x-route="/about" x-template.preload.target.app="/about.html"></template>

<!-- Interpolate URL and render into #content -->
<template 
  x-route="/user/:id/profile" 
  x-template.interpolate.target.content="/users/:id/profile.html"
></template>
```

## Embedded Scripts

Templates can include `<script>` elements that execute when the route is matched:

### Basic Embedded Script

`/template.html`:
```html
<div x-data="productList" x-init="fetchProducts">
  <h1>Products</h1>
  <ul>
    <template x-for="product in products" :key="product.id">
      <li x-text="product.name"></li>
    </template>
  </ul>
</div>

<script>
  Alpine.data('productList', () => ({
    products: [],
    async fetchProducts() {
      const response = await fetch('/api/products')
      this.products = await response.json()
    }
  }))
</script>
```

### Script Execution Behavior

- Scripts run when route is first matched
- Scripts run again when revisiting the route after navigation away
- Scripts have access to Alpine.js data stack of template and target elements
- Multiple scripts in a template execute in document order

### Scripts with x-run Directive (v7.5+)

The `x-run` directive controls script execution conditions:

#### `x-run.once` - Execute Once Per Route

Run script only once per route, even on revisits:

```html
<script x-run.once>
  // Initialize chart library once per route
  Chart.defaults.global.responsive = true
  console.log('Chart defaults set for this route')
</script>
```

**Use cases:**
- Library initialization (Charts, Maps, Editors)
- One-time setup per route
- Expensive computations that don't need re-running

#### `x-run.once` with ID - Execute Once Globally

Run script only once across all routes:

```html
<script x-run.once id="analytics-init">
  // Initialize analytics once even if template used on multiple routes
  window.analytics.track('page_view', { path: location.pathname })
</script>
```

If the same script (by ID) appears in multiple templates, it runs only once total.

#### `x-run:on="condition"` - Conditional Execution

Execute script only when condition evaluates to true:

```html
<script x-run:on="$router.context.route === '/admin'">
  // Only run on admin route, even if template shared
  initializeAdminTools()
</script>

<script x-run:on="$params.userId !== undefined">
  // Only run when userId parameter exists
  fetchUserData($params.userId)
</script>
```

**Condition context:**
- Has access to Alpine.js data stack of template element
- Has access to Alpine.js data stack of target element (if set)
- Can use `$router`, `$params`, `$history` magic helpers

#### Combining `x-run.once` and `x-run:on`

```html
<!-- Check condition, run once if true -->
<script x-run.once:on="$router.context.route === '/dashboard' && $params.role === 'admin'">
  initializeAdminDashboard()
</script>
```

Script runs only once if condition is true on first evaluation.

### Multiple Scripts in Template

```html
<div x-data="app"></div>

<!-- Script 1: Define Alpine data -->
<script>
  Alpine.data('counter', () => ({
    count: 0,
    increment() { this.count++ }
  }))
</script>

<!-- Script 2: Initialize only on specific route -->
<script x-run:on="$router.context.route === '/counter'">
  console.log('Counter route initialized')
</script>

<!-- Script 3: One-time setup -->
<script x-run.once>
  // Setup that runs once per route visit
  document.title = 'Counter App'
</script>
```

## Template Caching

Pinecone Router automatically caches fetched templates:

- Templates cached in memory after first fetch
- Cache cleared on browser page reload
- Interpolated templates cached by resolved URL
- Preloaded templates stay in cache for instant navigation

**Manual cache clearing:** Not exposed in public API (intentionally simple)

## Template Error Handling

### Fetch Errors

When template fetching fails, `pinecone:fetch-error` event is dispatched:

```javascript
document.addEventListener('pinecone:fetch-error', (event) => {
  console.error('Template fetch failed:', event.detail)
  // Show error UI or fallback content
})
```

**Common causes:**
- 404 Not Found (incorrect URL path)
- 403 Forbidden (CORS or authentication)
- Network errors (offline, server down)
- Invalid HTML response

### Fallback Strategies

#### Inline Fallback Content

```html
<template x-route="/external" x-template="/external.html">
  <!-- Fallback content if fetch fails -->
  <div class="error">
    <p>Content unavailable. Please try again later.</p>
    <button @click="$router.navigate('/')">Go Home</button>
  </div>
</template>
```

#### Programmatic Error Handling

```javascript
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({
    fetchOptions: {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  })
})

document.addEventListener('pinecone:fetch-error', (event) => {
  if (event.detail.status === 401) {
    // Redirect to login on auth error
    window.PineconeRouter.navigate('/login')
  }
})
```

## Template Scope and Data Access

### Accessing Route Parameters in Templates

```html
<template x-route="/user/:id" x-template="/user-profile.html"></template>
```

`/user-profile.html`:
```html
<div x-data="profile(<span x-text="$params.id"></span>)">
  <h1>User Profile</h1>
  <p>User ID: <span x-text="$params.id"></span></p>
</div>
```

### Target Element Data Scope

When using `.target` modifier, templates access target element's data scope:

```html
<template x-route="/details" x-template.target.product="/details.html"></template>

<div id="product" x-data="{ name: 'Widget', price: 9.99 }">
  <!-- /details.html can access this.name and this.price -->
</div>
```

`/details.html`:
```html
<h1><span x-text="name"></span></h1>
<p>Price: $<span x-text="price"></span></p>
```

## Reactive Updates with Parameters

Templates don't automatically re-render when parameters change on the same route. Use `x-effect` or `$watch`:

```html
<template x-route="/search/:query" x-template>
  <div x-data="searchResults">
    <h1>Results for: <span x-text="$params.query"></span></h1>
    <div x-effect="fetchResults">
      <template x-if="loading">Loading...</template>
      <template x-if="!loading">
        <ul>
          <template x-for="result in results" :key="result.id">
            <li x-text="result.title"></li>
          </template>
        </ul>
      </template>
    </div>
  </div>
</template>

<script>
  Alpine.data('searchResults', () => ({
    loading: false,
    results: [],
    async fetchResults() {
      if (!this.$params.query) return
      
      this.loading = true
      try {
        const response = await fetch(`/api/search?q=${this.$params.query}`)
        this.results = await response.json()
      } finally {
        this.loading = false
      }
    }
  }))
</script>
```

## Best Practices

### Template Organization

```
/templates/
  /layouts/
    header.html
    footer.html
  /pages/
    home.html
    about.html
    contact.html
  /components/
    navbar.html
    sidebar.html
    modal.html
```

### Reusable Layout Pattern

```html
<!-- Common layout with page-specific content -->
<template 
  x-route="/" 
  x-template="['/templates/layouts/header.html', '/templates/pages/home.html', '/templates/layouts/footer.html']"
></template>

<template 
  x-route="/about" 
  x-template="['/templates/layouts/header.html', '/templates/pages/about.html', '/templates/layouts/footer.html']"
></template>
```

### Performance Optimization

1. **Preload critical templates:**
```html
<template x-route="notfound" x-template.preload="/404.html"></template>
<template x-route="/login" x-template.preload="/login.html"></template>
```

2. **Use inline templates for simple routes:**
```html
<template x-route="/loading" x-template>
  <div class="spinner">Loading...</div>
</template>
```

3. **Set fetch priorities globally:**
```javascript
window.PineconeRouter.settings({
  fetchOptions: {
    priority: 'high' // For critical templates
  }
})
```

### Security Considerations

1. **Sanitize user input in interpolated URLs:**
```javascript
function handler(context, controller) {
  // Validate parameter before allowing template interpolation
  if (!/^[\w-]+$/.test(context.params.page)) {
    this.$router.navigate('/invalid-path')
  }
}
```

2. **Use CORS headers for external templates:**
```javascript
window.PineconeRouter.settings({
  fetchOptions: {
    mode: 'cors',
    credentials: 'same-origin'
  }
})
```

3. **Escape dynamic content in templates:**
```html
<!-- Alpine automatically escapes x-text -->
<p x-text="$params.userInput"></p>

<!-- Be careful with x-html -->
<div x-html="sanitizedContent"></div>
```

## Troubleshooting

### Template Not Rendering

1. **Check `x-template` directive is present:**
```html
<!-- Wrong - missing x-template -->
<template x-route="/about">
  <h1>About</h1>
</template>

<!-- Correct -->
<template x-route="/about" x-template>
  <h1>About</h1>
</template>
```

2. **Verify target element exists:**
```html
<!-- Target #app must exist in DOM -->
<template x-route="/" x-template.target.app>Content</template>
<div id="app"></div>
```

3. **Check external template URL:**
- Open browser DevTools Network tab
- Look for failed fetch requests
- Verify path is correct (relative to server root)

### Embedded Script Not Running

1. **Ensure script is inside template:**
```html
<template x-route="/" x-template>
  <div x-data="app"></div>
  <script>
    Alpine.data('app', () => ({ message: 'Hello' }))
  </script>
</template>
```

2. **Check script execution conditions:**
```html
<!-- This only runs on /dashboard route -->
<script x-run:on="$router.context.route === '/dashboard'">
  console.log('Dashboard initialized')
</script>
```

### Interpolation Not Working

1. **Ensure `.interpolate` modifier is present:**
```html
<!-- Wrong - :page not replaced -->
<template x-route="/docs/:page" x-template="/docs/:page.html"></template>

<!-- Correct -->
<template x-route="/docs/:page" x-template.interpolate="/docs/:page.html"></template>
```

2. **Parameter name must match exactly:**
```html
<!-- Route param is 'page', template uses 'slug' - won't work -->
<template x-route="/docs/:page" x-template.interpolate="/docs/:slug.html"></template>

<!-- Correct - both use 'page' -->
<template x-route="/docs/:page" x-template.interpolate="/docs/:page.html"></template>
```

### Preload Not Working

1. **Preload happens after initial load:**
```javascript
// Preload starts after first route renders
console.log('Page loaded, preloading other templates...')
```

2. **Cannot preload interpolated templates:**
```html
<!-- Won't work - URL unknown at preload time -->
<template x-route="/user/:id" x-template.preload.interpolate="/users/:id.html"></template>

<!-- Workaround: preload common templates separately -->
<template x-route="/user/:id" x-template.interpolate="/users/:id.html"></template>
<template x-id="preload-default" x-template.preload="/users/default.html"></template>
```

## Migration from v6 to v7

### Inline Template Syntax Change

**v6:**
```html
<template x-route="/">
  <h1>Home</h1>
</template>
```

**v7 (requires explicit x-template):**
```html
<template x-route="/" x-template>
  <h1>Home</h1>
</template>
```

### Multiple Root Elements

**v6:** Only single root element allowed

**v7:** Multiple root elements supported:
```html
<template x-route="/" x-template>
  <header>Header</header>
  <main>Main Content</main>
  <footer>Footer</footer>
</template>
```

### Target ID Setting Rename

**v6:**
```javascript
window.PineconeRouter.settings({ templateTargetId: 'app' })
```

**v7:**
```javascript
window.PineconeRouter.settings({ targetID: 'app' })
```

## TypeScript Types

```typescript
import type { RouteOptions } from 'pinecone-router'

const routeOptions: RouteOptions = {
  templates: ['/header.html', '/content.html'],
  targetID: 'app',
  preload: true,
  interpolate: false,
  handlers: []
}
```
