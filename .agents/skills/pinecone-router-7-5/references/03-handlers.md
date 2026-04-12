# Handlers in Pinecone Router 7.5

This reference covers route handlers, async operations, data passing between handlers, global handlers, cancellation patterns, and authentication guards for Pinecone Router v7.5.

## Handler Basics

Handlers are functions that execute when a route is matched, allowing you to run logic before template rendering:

```html
<template x-route="/user/:id" x-handler="loadUser">
  <div x-template>/user-profile.html</div>
</template>
```

### Handler Declaration Methods

#### Function Name Reference

```html
<template x-route="/about" x-handler="showAbout"></template>

<script>
  Alpine.data('router', () => ({
    showAbout(context, controller) {
      console.log('About page handler running')
    }
  }))
</script>
```

#### Anonymous Function

```html
<template 
  x-route="/redirect-home" 
  x-handler="(ctx) => $router.navigate('/')">
</template>
```

#### Array of Handlers

Multiple handlers execute in order:

```html
<template x-route="/post/:id" x-handler="[checkAuth, loadPost, trackView]"></template>

<script>
  Alpine.data('router', () => ({
    checkAuth(context, controller) {
      if (!userLoggedIn) {
        this.$router.navigate('/login')
        return // Stop handler chain
      }
    },
    loadPost(context, controller) {
      return fetch(`/api/posts/${context.params.id}`).then(r => r.json())
    },
    trackView(context, controller) {
      analytics.track('post_view', { postId: context.params.id })
    }
  }))
</script>
```

## Handler Arguments

Every handler receives two arguments:

### 1. Context Object

Contains route information and data from previous handlers:

```typescript
interface HandlerContext<T = unknown> {
  readonly path: string           // Current path (e.g., "/users/john")
  readonly route: Route           // Matched route object
  readonly params: Record<string, string | undefined>  // Route parameters
  readonly data: T                // Data returned by previous handler
}
```

**Usage:**
```javascript
function handler(context, controller) {
  console.log('Path:', context.path)           // "/users/john"
  console.log('Route:', context.route.path)    // "/users/:username"
  console.log('Params:', context.params)       // { username: "john" }
  console.log('Data:', context.data)           // Data from previous handler
}
```

### 2. AbortController

Allows cancellation of async operations when user navigates away:

```javascript
async function handler(context, controller) {
  try {
    const response = await fetch('/api/data', {
      signal: controller.signal  // Pass abort signal
    })
    const data = await response.json()
    return data
  } catch (error) {
    if (error.name === 'AbortError') {
      // User navigated away, safely ignore
      return
    }
    throw error  // Re-throw other errors
  }
}
```

**Controller methods:**
- `controller.signal`: AbortSignal to pass to async operations
- `controller.abort()`: Cancel subsequent handlers in the chain

## Async Handlers

All handlers are automatically awaited, enabling sequential async operations:

### Sequential Data Fetching

```html
<template x-route="/post/:id" x-handler="[fetchPost, processPost, renderPost]"></template>

<script>
  Alpine.data('router', () => ({
    async fetchPost(context, controller) {
      const response = await fetch(`/api/posts/${context.params.id}`, {
        signal: controller.signal
      })
      return await response.json()  // Return value passed to next handler
    },
    
    async processPost(context, controller) {
      const post = context.data  // Data from fetchPost
      
      if (!post) {
        this.$router.navigate('/not-found')
        return
      }
      
      // Enrich post with additional data
      const author = await fetch(`/api/users/${post.authorId}`, {
        signal: controller.signal
      }).then(r => r.json())
      
      return { ...post, author }  // Pass enriched data to next handler
    },
    
    renderPost(context, controller) {
      const post = context.data  // Enriched post from processPost
      
      document.querySelector('#app').innerHTML = `
        <h1>${post.title}</h1>
        <p>By: ${post.author.name}</p>
        <div>${post.content}</div>
      `
    }
  }))
</script>
```

### Error Handling in Async Handlers

```javascript
async function handler(context, controller) {
  try {
    const response = await fetch('/api/data', {
      signal: controller.signal
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    if (error.name === 'AbortError') {
      // User navigated away, ignore
      console.log('Fetch aborted')
      return
    }
    
    // Handle error: abort to prevent template rendering
    console.error('Fetch failed:', error)
    controller.abort()  // Stop handler chain, don't render template
    
    // Or redirect instead
    // this.$router.navigate('/error')
  }
}
```

## Data Passing Between Handlers

Return values from handlers are passed to the next handler via `context.data`:

### Single Return Value

```javascript
function firstHandler(context, controller) {
  return { userId: context.params.id, timestamp: Date.now() }
}

function secondHandler(context, controller) {
  // context.data = { userId: "123", timestamp: 1234567890 }
  const { userId, timestamp } = context.data
  console.log('User:', userId, 'at', new Date(timestamp))
}
```

### Chaining Multiple Async Operations

```javascript
async function fetchUserData(context, controller) {
  const response = await fetch(`/api/users/${context.params.id}`, {
    signal: controller.signal
  })
  return await response.json()
}

async function fetchUserPosts(context, controller) {
  const user = context.data  // From fetchUserData
  
  const response = await fetch(`/api/users/${user.id}/posts`, {
    signal: controller.signal
  })
  const posts = await response.json()
  
  return { ...user, posts }  // Combine and pass forward
}

function renderUserProfile(context, controller) {
  const { user, posts } = context.data  // From fetchUserPosts
  
  // Render with combined data
  document.querySelector('#app').innerHTML = `
    <h1>${user.name}</h1>
    <ul>
      ${posts.map(post => `<li>${post.title}</li>`).join('')}
    </ul>
  `
}
```

## Global Handlers

Global handlers run on every route match, useful for authentication, analytics, and logging:

### Declaring Global Handlers

#### Via x-handler.global Directive

```html
<div x-data="router()" x-handler.global="[logRoute, checkAuth]">
  <template x-route="/" x-handler="home"></template>
  <template x-route="/about" x-handler="about"></template>
</div>

<script>
  Alpine.data('router', () => ({
    logRoute(context, controller) {
      console.log('Navigated to:', context.path)
      analytics.pageView(context.path)
    },
    checkAuth(context, controller) {
      const publicRoutes = ['/', '/login', '/register']
      if (!publicRoutes.includes(context.path) && !isLoggedIn()) {
        this.$router.navigate('/login')
      }
    }
  }))
</script>
```

#### Via Settings

```javascript
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({
    globalHandlers: [
      (context, controller) => {
        console.log('Global handler 1:', context.path)
      },
      (context, controller) => {
        // Check authentication
        if (requiresAuth(context.path) && !userLoggedIn) {
          window.PineconeRouter.navigate('/login')
        }
      }
    ]
  })
})
```

### Global Handler Execution Order

1. Global handlers execute first (in declaration order)
2. Route-specific handlers execute second (in declaration order)

```html
<div x-handler.global="[global1, global2]">
  <template x-route="/test" x-handler="[route1, route2]"></template>
</div>
```

**Execution order:** `global1` → `global2` → `route1` → `route2`

## Cancellation Patterns

### Stopping Handler Chain with Redirect

Navigation cancels all ongoing handlers:

```javascript
function checkAuth(context, controller) {
  if (!userLoggedIn) {
    // This cancels remaining handlers and navigates
    this.$router.navigate('/login')
    return
  }
  // Handlers continue if user is logged in
}
```

### Stopping Handler Chain with Abort

Use `controller.abort()` to cancel without navigation:

```javascript
function validateData(context, controller) {
  if (context.data.invalid) {
    console.log('Invalid data, aborting')
    controller.abort()  // Stop handlers, don't render template
    return
  }
  // Continue with valid data
}
```

**Use cases for abort:**
- Show error message without redirecting
- Display fallback content via JavaScript
- Log error and stop processing

### Checking Abort Status

```javascript
async function longRunningHandler(context, controller) {
  // Check before starting
  if (controller.signal.aborted) {
    return
  }
  
  // Pass signal to async operations
  const response = await fetch('/api/slow-endpoint', {
    signal: controller.signal
  })
  
  // Check after each operation
  if (controller.signal.aborted) {
    console.log('Operation cancelled')
    return
  }
  
  const data = await response.json()
  
  // Final check before using data
  if (!controller.signal.aborted) {
    processData(data)
  }
}
```

## Authentication Guards

### Simple Auth Guard

```javascript
function authGuard(context, controller) {
  const publicRoutes = ['/', '/login', '/register', '/forgot-password']
  
  if (!publicRoutes.includes(context.path) && !session.isLoggedIn) {
    // Store intended destination
    session.intendedPath = context.path
    this.$router.navigate('/login')
  }
}
```

### Role-Based Access Control

```javascript
function roleGuard(context, controller) {
  const routeRoles = {
    '/admin': ['admin'],
    '/moderator': ['admin', 'moderator'],
    '/user/:id': ['admin', 'moderator', 'user']
  }
  
  const requiredRoles = routeRoles[context.route.path]
  if (requiredRoles && !requiredRoles.includes(user.role)) {
    controller.abort()
    showUnauthorizedError()
  }
}

function dynamicRoleGuard(context, controller) {
  // Check routes with parameters
  if (context.route.path === '/user/:id') {
    const userId = context.params.id
    if (userId !== user.id && user.role !== 'admin') {
      controller.abort()
      this.$router.navigate('/unauthorized')
    }
  }
}
```

### Async Authentication Check

```javascript
async function asyncAuthGuard(context, controller) {
  try {
    // Validate token with server
    const response = await fetch('/api/auth/validate', {
      signal: controller.signal
    })
    
    if (!response.ok) {
      // Token invalid or expired
      localStorage.removeItem('token')
      this.$router.navigate('/login')
      return
    }
    
    const { user } = await response.json()
    currentUser = user
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('Auth validation failed:', error)
      controller.abort()
    }
  }
}
```

### Protected Route Pattern

```html
<template x-route="/dashboard" x-handler="[asyncAuthGuard, loadDashboard]"></template>
<template x-route="/settings" x-handler="[asyncAuthGuard, loadSettings]"></template>
<template x-route="/admin/*" x-handler="[adminGuard, loadAdmin]"></template>
```

## Data Fetching Patterns

### Parallel Data Fetching

```javascript
async function parallelFetch(context, controller) {
  const promises = [
    fetch(`/api/users/${context.params.id}`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => ({ user: data })),
    
    fetch(`/api/users/${context.params.id}/posts`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => ({ posts: data })),
    
    fetch(`/api/users/${context.params.id}/notifications`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => ({ notifications: data }))
  ]
  
  // Wait for all or handle partial failures
  const results = await Promise.allSettled(promises)
  
  const data = {}
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      Object.assign(data, result.value)
    } else {
      console.error(`Fetch ${index} failed:`, result.reason)
    }
  })
  
  return data
}
```

### Conditional Data Fetching

```javascript
async function conditionalFetch(context, controller) {
  let data
  
  if (context.params.id) {
    // Fetch specific resource
    const response = await fetch(`/api/items/${context.params.id}`, {
      signal: controller.signal
    })
    data = await response.json()
  } else {
    // Fetch list
    const response = await fetch('/api/items', {
      signal: controller.signal
    })
    data = await response.json()
  }
  
  return data
}
```

### Cached Data Pattern

```javascript
const dataCache = new Map()

async function cachedFetch(context, controller) {
  const cacheKey = context.path
  
  // Return cached data if fresh (< 1 minute old)
  const cached = dataCache.get(cacheKey)
  if (cached && Date.now() - cached.timestamp < 60000) {
    return cached.data
  }
  
  // Fetch new data
  const response = await fetch(`/api/data?path=${encodeURIComponent(context.path)}`, {
    signal: controller.signal
  })
  const data = await response.json()
  
  // Update cache
  dataCache.set(cacheKey, { data, timestamp: Date.now() })
  
  return data
}
```

## Handler Error Handling

### Try-Catch in Async Handlers

```javascript
async function handler(context, controller) {
  try {
    const data = await fetchData(context.params.id, controller.signal)
    return data
  } catch (error) {
    if (error.name === 'AbortError') {
      // User navigated away, silently ignore
      return
    }
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      // Network error
      controller.abort()
      showNetworkError()
      return
    }
    
    // Unexpected error
    console.error('Handler error:', error)
    controller.abort()
    this.$router.navigate('/error')
  }
}
```

### Error Boundary Pattern

```javascript
function errorBoundary(context, controller) {
  return async (originalHandler) => {
    try {
      return await originalHandler(context, controller)
    } catch (error) {
      if (error.name === 'AbortError') throw error
      
      console.error('Route handler error:', error)
      
      // Show error UI instead of crashing
      document.querySelector('#app').innerHTML = `
        <div class="error">
          <h1>Something went wrong</h1>
          <p>${error.message}</p>
          <button @click="$router.navigate('/')">Go Home</button>
        </div>
      `
      
      controller.abort()
    }
  }
}
```

## Notfound Handler

Custom handler for 404 routes:

```html
<template x-route="notfound" x-handler="handleNotFound" x-template>
  <h1>404 - Page Not Found</h1>
  <p>The page you're looking for doesn't exist.</p>
  <a href="/">Return Home</a>
</template>

<script>
  Alpine.data('router', () => ({
    handleNotFound(context, controller) {
      // Log 404 for analytics
      analytics.track('page_not_found', {
        path: context.path,
        referredFrom: document.referrer
      })
      
      // Check if user might have meant a similar route
      const similarRoutes = findSimilarRoutes(context.path)
      if (similarRoutes.length > 0) {
        showDidYouMean(similarRoutes)
      }
    }
  }))
</script>
```

## Best Practices

### Handler Organization

Keep handlers focused and single-purpose:

```javascript
// Good: Single responsibility
function checkAuth(context, controller) { /* ... */ }
function loadData(context, controller) { /* ... */ }
function renderPage(context, controller) { /* ... */ }

<template x-route="/page" x-handler="[checkAuth, loadData, renderPage]"></template>

// Avoid: Multiple concerns in one handler
function doEverything(context, controller) {
  // Check auth
  // Fetch data
  // Transform data
  // Render HTML
  // Track analytics
  // Update cache
}
```

### Reusable Handler Factories

```javascript
function createFetchHandler(urlBuilder) {
  return async function(context, controller) {
    const url = urlBuilder(context.params)
    const response = await fetch(url, { signal: controller.signal })
    return await response.json()
  }
}

// Usage
<template x-route="/user/:id" x-handler="createFetchHandler(params => `/api/users/${params.id}`)"></template>
```

### Performance Considerations

1. **Cancel unnecessary fetches:** Always use `controller.signal`
2. **Cache frequently accessed data:** Reduce redundant API calls
3. **Debounce rapid navigation:** Prevent handler storms
4. **Use preload for critical routes:** Reduce perceived latency

## Troubleshooting

### Handler Not Executing

1. **Check function is in Alpine data scope:**
```javascript
Alpine.data('router', () => ({
  myHandler(context, controller) {
    console.log('Handler called')  // Should appear in console
  }
}))
```

2. **Verify handler name matches:**
```html
<!-- Handler name must match exactly -->
<template x-route="/test" x-handler="myHandler"></template>
```

### Async Handler Not Waiting

Handlers are automatically awaited, but ensure you're returning promises:

```javascript
// Wrong: Not returning promise
async function handler(context, controller) {
  fetch('/api/data').then(r => r.json())  // Promise not returned
}

// Correct: Return the promise
async function handler(context, controller) {
  return await fetch('/api/data').then(r => r.json())
}
```

### Data Not Passing Between Handlers

Ensure handlers return values:

```javascript
// Wrong: No return
function firstHandler(context, controller) {
  this.data = { value: 42 }  // Doesn't pass to next handler
}

// Correct: Return value
function firstHandler(context, controller) {
  return { value: 42 }  // Passed via context.data to next handler
}

function secondHandler(context, controller) {
  console.log(context.data.value)  // 42
}
```

### AbortError Not Handled

Always check for AbortError in async handlers:

```javascript
// Wrong: Treats abort as error
async function handler(context, controller) {
  const data = await fetch('/api/data', { signal: controller.signal }).then(r => r.json())
  return data
}

// Correct: Handle abort gracefully
async function handler(context, controller) {
  try {
    const response = await fetch('/api/data', { signal: controller.signal })
    return await response.json()
  } catch (error) {
    if (error.name === 'AbortError') return  // Silently ignore
    throw error  // Re-throw other errors
  }
}
```

## TypeScript Types

```typescript
import type { Handler, HandlerContext } from 'pinecone-router'

// Basic handler type
const myHandler: Handler<unknown, string> = (
  context: HandlerContext<unknown>,
  controller: AbortController
): string => {
  return `Hello ${context.params.name}`
}

// Async handler returning data
async function fetchData(
  context: HandlerContext<unknown>,
  controller: AbortController
): Promise<UserData> {
  const response = await fetch(`/api/user/${context.params.id}`, {
    signal: controller.signal
  })
  return response.json()
}

// Handler chain with typed data
async function handler1(
  context: HandlerContext<unknown>,
  controller: AbortController
): Promise<User> {
  // Fetch user
  return user
}

async function handler2(
  context: HandlerContext<User>,  // Receives User from handler1
  controller: AbortController
): Promise<UserWithPosts> {
  // Enrich with posts
  return { ...context.data, posts }
}
```
