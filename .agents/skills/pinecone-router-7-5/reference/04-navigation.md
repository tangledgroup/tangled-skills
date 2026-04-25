# Navigation in Pinecone Router 7.5

This reference covers programmatic navigation, navigation history management, browser integration, events, loading states, and link handling for Pinecone Router v7.5.

## Programmatic Navigation

Navigate to routes from JavaScript using the `$router` magic helper or `PineconeRouter` object:

### Basic Navigation

```javascript
// From Alpine component
this.$router.navigate('/about')

// From anywhere in Alpine template
<button @click="$router.navigate('/contact')">Contact</button>

// From global JavaScript
window.PineconeRouter.navigate('/dashboard')

// Using Alpine global
Alpine.$router.navigate('/settings')
```

### Navigation with Parameters

```javascript
// Navigate with route parameters
this.$router.navigate('/user/john')
this.$router.navigate('/posts/123/comments')

// Build paths dynamically
const username = 'jane'
this.$router.navigate(`/user/${username}`)

// With query parameters (manually added)
this.$router.navigate('/search?query=alpine&sort=date')
```

### Navigation Returns Promise

All navigation methods return promises that resolve when handlers complete:

```javascript
async function handleNavigation() {
  try {
    await this.$router.navigate('/expensive-route')
    console.log('Navigation completed, handlers finished')
  } catch (error) {
    console.error('Navigation failed:', error)
  }
}
```

## Navigation History

Pinecone Router maintains its own navigation history independent of browser history:

### Accessing Navigation History

```javascript
// From Alpine component via $history magic helper
$history.entries     // Array of visited paths
$history.index       // Current position in history
$history.canGoBack() // Boolean: can navigate back?
$history.canGoForward() // Boolean: can navigate forward?

// From global JavaScript
window.PineconeRouter.history.entries
window.PineconeRouter.history.index
```

### Back and Forward Navigation

```html
<div x-data="{ }">
  <button 
    @click="$history.back()" 
    :disabled="!$history.canGoBack()">
    Back
  </button>
  
  <button 
    @click="$history.forward()" 
    :disabled="!$history.canGoForward()">
    Forward
  </button>
  
  <p>History: <span x-text="$history.entries.join(' → ')"></span></p>
  <p>Current index: <span x-text="$history.index + 1"></span> of <span x-text="$history.entries.length"></span></p>
</div>
```

### Navigate to Specific History Position

```javascript
// Go to specific position in history
$history.to(2)  // Navigate to third entry (0-indexed)

// Custom history navigation UI
<div x-data="{ }" x-init="$watch('$history.index', updateBreadcrumbs)">
  <nav>
    <template x-for="(entry, index) in $history.entries" :key="index">
      <button 
        @click="$history.to(index)"
        :class="{ active: index === $history.index }"
        x-text="entry">
      </button>
    </template>
  </nav>
</div>
```

### History Behavior

**Duplicates are filtered:**
```javascript
// Navigation sequence: / → /about → / → /contact
$history.entries  // ['/', '/about', '/contact'] (duplicate '/' removed)
```

**Redirects don't add to history:**
```javascript
// If /old redirects to /new in a handler:
this.$router.navigate('/old')
// Handler: this.$router.navigate('/new')
$history.entries  // [..., '/new'] (/old not added)
```

**Branching after back navigation:**
```javascript
// Navigate: / → /a → /b → /c
$history.back()  // Now at /a, index = 1

// New navigation from /a:
this.$router.navigate('/d')
$history.entries  // ['/', '/a', '/d'] (/b and /c removed)
```

## Browser History Integration

Pinecone Router automatically syncs with browser history via `pushState`:

### Default Behavior (pushState enabled)

```javascript
// Each navigation updates browser URL
this.$router.navigate('/about')  // URL becomes example.com/about

// Browser back button works automatically
// PineconeRouter.history and browser history stay in sync
```

### Disabling pushState

Prevent browser URL changes while keeping internal navigation:

```javascript
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({ pushState: false })
})
```

**Use cases:**
- Testing/navigation without URL changes
- Modal-based "pages" that don't need URL updates
- Custom URL management strategies

**Note:** Browser back button won't work when `pushState: false`. Use `$history.back()` instead.

### Hash Routing Mode

Enable hash-based routing for server-less deployments:

```javascript
window.PineconeRouter.settings({ hash: true })
```

**URL format:**
- Normal routing: `example.com/about`
- Hash routing: `example.com/#/about`

**Benefits:**
- No server configuration required
- Works on any static hosting
- Shareable URLs with hash fragments

**Note:** When using hash routing, `basePath` is only added to template URLs, not navigation paths.

## Events

Pinecone Router dispatches custom events for lifecycle hooks:

### Loading Events

```javascript
// Navigation/loading starts
document.addEventListener('pinecone:start', (event) => {
  console.log('Navigation started')
  NProgress.start()  // Show loading indicator
})

// Navigation/loading completes
document.addEventListener('pinecone:end', (event) => {
  console.log('Navigation completed')
  NProgress.done()  // Hide loading indicator
})

// Template fetch error
document.addEventListener('pinecone:fetch-error', (event) => {
  console.error('Template fetch failed:', event.detail)
  // Show error UI or fallback content
})
```

### Using Events in Alpine.js

```html
<div 
  @pinecone:start.document="loading = true"
  @pinecone:end.document="loading = false"
  @pinecone:fetch-error.document="handleFetchError">
  
  <template x-if="loading">
    <div class="loader">Loading...</div>
  </template>
</div>

<script>
  Alpine.data('app', () => ({
    loading: false,
    handleFetchError(event) {
      console.error('Fetch error:', event.detail)
      this.showError('Failed to load page')
    }
  }))
</script>
```

### Event Usage with nProgress

```javascript
import NProgress from 'nprogress'

document.addEventListener('pinecone:start', () => NProgress.start())
document.addEventListener('pinecone:end', () => NProgress.done())
document.addEventListener('pinecone:fetch-error', () => NProgress.done())
```

## Loading State

Access the reactive loading state via `$router.loading`:

### Template-Based Loading Indicator

```html
<div x-data="{ }">
  <template x-if="$router.loading">
    <div class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>
  </template>
  
  <template x-if="!$router.loading">
    <main><!-- Page content --></main>
  </template>
</div>
```

### Component-Based Loading

```html
<div x-data="{ }">
  <loading-spinner :visible="$router.loading"></loading-spinner>
  
  <main x-show="!$router.loading">
    <!-- Page content -->
  </main>
</div>
```

### Watch Loading Changes

```javascript
Alpine.data('app', () => ({
  init() {
    this.$watch('$router.loading', (loading) => {
      if (loading) {
        this.startLoadingEffects()
      } else {
        this.stopLoadingEffects()
      }
    })
  },
  startLoadingEffects() {
    // Blur background, show skeleton screens, etc.
  },
  stopLoadingEffects() {
    // Restore normal state
  }
}))
```

## Link Handling

Pinecone Router automatically intercepts anchor tag clicks for client-side navigation:

### Automatic Link Interception

By default, all `<a>` tags with valid `href` attributes are intercepted:

```html
<!-- These links use client-side navigation (no page reload) -->
<a href="/about">About</a>
<a href="/user/john">John's Profile</a>
<a href="/posts?category=tech">Tech Posts</a>
```

### Disabling Interception on Specific Links

Add `native` or `data-native` attribute to bypass router:

```html
<!-- These links cause full page reload -->
<a href="/about" native>About (reload)</a>
<a href="https://external-site.com" data-native>External Link</a>
<a href="/download/file.pdf" native>Download File</a>
```

**Use cases for native links:**
- External site links
- File downloads
- Form submissions
- Actions requiring page reload

### Global Link Handling Control

Disable automatic interception globally:

```javascript
window.PineconeRouter.settings({ handleClicks: false })
```

When disabled, only links with `x-link` attribute use client-side navigation:

```html
<!-- With handleClicks: false -->
<a href="/about">Reloads page</a>
<a href="/contact" x-link>Client-side navigation</a>
```

### Link Event Handling

```javascript
// Custom link click handling
document.addEventListener('click', (event) => {
  const link = event.target.closest('a')
  if (link && link.href) {
    console.log('Link clicked:', link.href)
    
    // Prevent default (if you want custom handling)
    // event.preventDefault()
    // Custom navigation logic...
  }
})
```

## Context Object

Access current route information via the context object:

### Accessing Context

```javascript
// From Alpine component
$router.context.path      // Current path string
$router.context.route     // Matched Route object (or undefined)
$router.context.params    // Route parameters as object

// From global JavaScript
window.PineconeRouter.context.path
window.PineconeRouter.context.route
window.PineconeRouter.context.params

// From handlers (use provided context, not global)
function handler(context, controller) {
  context.path     // Current path
  context.route    // Matched route
  context.params   // Route parameters
}
```

### Context Usage Examples

```html
<div x-data="{ }">
  <p>Current path: <span x-text="$router.context.path"></span></p>
  <p>Route pattern: <span x-text="$router.context.route?.path || 'N/A'"></span></p>
  <p>Route name: <span x-text="$router.context.route?.name || 'N/A'"></span></p>
  <p>Parameters: <span x-text="JSON.stringify($router.context.params)"></span></p>
</div>
```

### Context in Templates

```html
<template x-route="/user/:username" x-template>
  <div x-data="{ }">
    <h1>Profile: <span x-text="$params.username"></span></h1>
    <address x-text="$router.context.path"></address>
  </div>
</template>
```

## Match Method

Check if a path matches any route without navigating:

### Basic Route Matching

```javascript
// Check if path matches a route
const result = window.PineconeRouter.match('/users/john')

if (result.route) {
  console.log('Matched route:', result.route.path)  // "/users/:username"
  console.log('Route name:', result.route.name)     // "user-profile" or path
  console.log('Parameters:', result.params)         // { username: "john" }
} else {
  console.log('No matching route found')
}
```

### Validation Use Case

```javascript
function validateNavigation(path) {
  const result = window.PineconeRouter.match(path)
  
  if (!result.route) {
    alert('Route not found: ' + path)
    return false
  }
  
  // Check parameter requirements
  if (result.params.requiredParam === undefined) {
    alert('Missing required parameter')
    return false
  }
  
  return true
}

// Usage
if (validateNavigation('/users/john')) {
  this.$router.navigate('/users/john')
}
```

### Link Pre-validation

```html
<a 
  href="/test" 
  @click.prevent="checkAndNavigate($event)">
  Test Link
</a>

<script>
  Alpine.data('app', () => ({
    checkAndNavigate(event) {
      const path = event.target.href.split('#')[0]
      const result = this.$router.match(path)
      
      if (result.route) {
        console.log('Valid route, navigating...')
        this.$router.navigate(path)
      } else {
        console.log('Invalid route, opening in new tab')
        window.open(path, '_blank')
      }
    }
  }))
</script>
```

## Base Path Integration

When `basePath` is configured, it's automatically prepended to navigation:

```javascript
window.PineconeRouter.settings({ basePath: '/app' })
```

```javascript
// Navigation automatically includes base path
this.$router.navigate('/about')  // Actually navigates to /app/about

// Links work the same way
<a href="/contact">Contact</a>  // Navigates to /app/contact

// Template URLs also include basePath
<template x-route="/" x-template="/home.html"></template>
<!-- Fetches: /app/home.html -->
```

**Benefits:**
- Simplified route declarations for subdirectory apps
- Easy deployment path changes (update one setting)
- Consistent URL structure

## Initial Page Load

Pinecone Router automatically handles initial page load:

### First Load Behavior

1. Router reads current URL/path on initialization
2. Matches path against registered routes
3. Executes matched route's handlers
4. Renders matched route's template
5. Adds path to navigation history

```javascript
// On page load at /about:
// 1. Route "/about" is matched
// 2. Handlers for "/about" execute
// 3. Template for "/about" renders
// 4. Navigation history: ['/about']
// 5. Browser history synced (if pushState enabled)
```

### Custom Initialization

```javascript
document.addEventListener('alpine:init', () => {
  // Configure router before Alpine starts
  window.PineconeRouter.settings({
    targetID: 'app',
    preload: true
  })
  
  // Add programmatic routes
  window.PineconeRouter.add('/custom', {
    templates: ['/custom.html'],
    handlers: [customHandler]
  })
})

Alpine.start()  // Router initializes here
```

## Navigation Patterns

### Dynamic Path Building

```javascript
// Build paths with parameters
const userId = 123
const postId = 456
this.$router.navigate(`/users/${userId}/posts/${postId}`)

// With query parameters
const searchQuery = 'alpine'
const sortBy = 'date'
this.$router.navigate(`/search?q=${encodeURIComponent(searchQuery)}&sort=${sortBy}`)

// Conditional path segments
const path = ['/products']
if (category) path.push(category)
if (filter) path.push(filter)
this.$router.navigate(path.join('/'))
```

### Navigation with State

```javascript
// Store state before navigation
function navigateWithState(path, state) {
  sessionStorage.setItem('navigationState', JSON.stringify(state))
  this.$router.navigate(path)
}

// Retrieve state on target route
function handler(context, controller) {
  const state = JSON.parse(sessionStorage.getItem('navigationState') || '{}')
  sessionStorage.removeItem('navigationState')
  
  // Use state for initialization
  initializeWithState(state)
}
```

### Redirect Pattern

```javascript
function redirectHandler(context, controller) {
  // Check conditions
  if (user.role === 'admin') {
    this.$router.navigate('/admin/dashboard')
    return
  }
  
  if (user.role === 'user') {
    this.$router.navigate('/user/dashboard')
    return
  }
  
  this.$router.navigate('/login')
}
```

## Troubleshooting

### Navigation Not Working

1. **Check router is initialized:**
```javascript
console.log(window.PineconeRouter)  // Should exist
console.log(Alpine.$router)  // Should exist after Alpine.start()
```

2. **Verify route exists:**
```javascript
const result = window.PineconeRouter.match('/about')
console.log(result.route)  // Should not be undefined
```

3. **Check for handler errors:**
```javascript
// Add logging to handlers
function handler(context, controller) {
  console.log('Handler executing:', context.path)
  // ... handler logic
}
```

### History Not Syncing

1. **Verify pushState is enabled:**
```javascript
console.log(window.PineconeRouter.settings().pushState)  // Should be true
```

2. **Check browser supports History API:**
```javascript
console.log('History API supported:', !!window.history.pushState)
```

### Events Not Firing

1. **Ensure event listener is added before navigation:**
```javascript
// Wrong: Listener added after navigation
this.$router.navigate('/about')
document.addEventListener('pinecone:start', handler)  // Too late!

// Correct: Listener added during init
document.addEventListener('alpine:init', () => {
  document.addEventListener('pinecone:start', handler)
})
```

2. **Check event target:**
```javascript
// Events dispatched on document
document.addEventListener('pinecone:start', handler)  // Correct
window.addEventListener('pinecone:start', handler)    // Also works
element.addEventListener('pinecone:start', handler)   // Won't work (unless using capture)
```

### Hash Routing Issues

1. **Ensure hash routing is enabled:**
```javascript
window.PineconeRouter.settings({ hash: true })
```

2. **Check URL format:**
- Should be: `example.com/#/about`
- Not: `example.com/about`

3. **Initial load with hash:**
```javascript
// On page load at example.com/#/about
// Router should match "/about" route (hash portion only)
```

### Loading State Stuck

1. **Check for unhandled handler errors:**
```javascript
async function handler(context, controller) {
  try {
    // Async operation
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('Handler error:', error)
      controller.abort()  // Stop loading state
    }
  }
}
```

2. **Verify handlers complete:**
```javascript
function handler(context, controller) {
  console.log('Handler start')
  // ... logic
  console.log('Handler end')  // Should appear in console
}
```

## Best Practices

### Loading Indicators

Always provide visual feedback during navigation:

```html
<div x-data="{ }">
  <div x-show="$router.loading" class="loading-indicator">
    <span class="spinner"></span>
    <p>Loading...</p>
  </div>
</div>
```

### History Button States

Disable back/forward buttons when navigation not possible:

```html
<button 
  @click="$history.back()" 
  :disabled="!$history.canGoBack()"
  :class="{ disabled: !$history.canGoBack() }">
  Back
</button>
```

### External Link Detection

Open external links in new tab:

```html
<a 
  href="/about" 
  :target="isExternal(href) ? '_blank' : '_self'"
  :rel="isExternal(href) ? 'noopener noreferrer' : ''">
  Link Text
</a>

<script>
  Alpine.data('app', () => ({
    isExternal(href) {
      return href.startsWith('http') && !href.startsWith(window.location.origin)
    }
  }))
</script>
```

### Graceful Fallback for JavaScript Disabled

```html
<nav>
  <!-- These links work without JavaScript -->
  <a href="/about">About</a>
  <a href="/contact">Contact</a>
</nav>

<!-- Pinecone Router enhances them with client-side navigation when JS is enabled -->
```

## TypeScript Types

```typescript
import type { NavigationHistory, Context } from 'pinecone-router'

// Navigation history
const history: NavigationHistory = {
  index: number,
  entries: string[],
  canGoBack(): boolean,
  canGoForward(): boolean,
  back(): void,
  forward(): void,
  to(index: number): void
}

// Context object
const context: Context = {
  readonly path: string,
  readonly route?: Route,
  readonly params: Record<string, string | undefined>
}

// Match result
const matchResult = window.PineconeRouter.match('/users/john')
// Type: { route: Route, params: Record<string, string | undefined> }
```
