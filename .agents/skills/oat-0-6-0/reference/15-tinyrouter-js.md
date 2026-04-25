# TinyRouter.js - Frontend Routing

A tiny (~950 bytes minified+gzipped), zero-dependency JavaScript library for client-side routing on top of the browser's `window.history` API. Ideal for simple vanilla JS single-page applications and use with AlpineJS.

[**View Demo**](https://knadh.github.io/tinyrouter.js/demo) | [**GitHub**](https://github.com/knadh/tinyrouter.js)

## Features

- Dynamic route parameters using `{param}` syntax
- Route grouping with shared handlers
- Before/after handler hooks for each route and globally
- Automatic optional binding to `<a>` tags for navigation
- Zero dependencies, ~950 bytes minified+gzipped

## Installation

### npm

```bash
npm install @knadh/tinyrouter
```

### CDN / ES Module

```html
<script type="module">
  import router from 'https://unpkg.com/@knadh/tinyrouter';
</script>
```

### Direct Download

Download from [GitHub releases](https://github.com/knadh/tinyrouter.js/releases) or use the demo source as reference.

## Basic Usage

### Create Router and Register Routes

```javascript
import router from '@knadh/tinyrouter';

// Create router instance with default handler for 404s
const r = router.new({
  defaultHandler: (ctx) => {
    console.log('Route not found', ctx.location.pathname);
    document.body.innerHTML = '<h1>404 - Not Found</h1>';
  }
});

// Register routes
r.on('/', (ctx) => {
  document.body.innerHTML = '<h1>Home Page</h1>';
});

r.on('/users/{id}', (ctx) => {
  const userId = ctx.params.id;
  document.body.innerHTML = `<h1>User Profile: ${userId}</h1>`;
});

// Initialize router
r.ready();
```

### Dynamic Routes with Multiple Parameters

```javascript
r.on('/posts/{year}/{month}/{day}', (ctx) => {
  const { year, month, day } = ctx.params;
  document.body.innerHTML = `
    <h1>Post</h1>
    <p>Date: ${year}-${month}-${day}</p>
  `;
});

r.on('/users/{userId}/posts/{postId}', (ctx) => {
  const { userId, postId } = ctx.params;
  console.log(`User ${userId}, Post ${postId}`);
});
```

## Advanced Usage

### Routes with Before/After Hooks

```javascript
// Route with before/on/after handlers
r.on('/posts/{id}', {
  before: (ctx) => {
    console.log('Before post handler, loading data...');
    // Return false to cancel route
    return true;
  },
  on: (ctx) => {
    console.log('Post content', ctx.params.id);
    document.body.innerHTML = `<h1>Post ${ctx.params.id}</h1>`;
  },
  after: (ctx) => {
    console.log('After post handler, analytics...');
    // Scroll to top
    window.scrollTo(0, 0);
  }
});
```

### Route Groups with Shared Prefix and Handlers

```javascript
// Create admin group with authentication check
const admin = r.group('/admin', {
  before: (ctx) => {
    // Check if user is authenticated
    const isAuthenticated = localStorage.getItem('isAdmin') === 'true';
    if (!isAuthenticated) {
      r.navigate('/login');
      return false; // Cancel navigation
    }
    return true;
  }
});

// All routes in this group are prefixed with /admin
// and the before() callback runs for all of them
admin.on('/dashboard', (ctx) => {
  document.body.innerHTML = '<h1>Admin Dashboard</h1>';
});

admin.on('/users/{id}', (ctx) => {
  const userId = ctx.params.id;
  document.body.innerHTML = `<h1>Edit User: ${userId}</h1>`;
});

admin.on('/settings', (ctx) => {
  document.body.innerHTML = '<h1>Admin Settings</h1>';
});
```

### Global Before/After Handlers

```javascript
// Runs before EVERY route's before/on/after handlers
r.beforeEach((ctx) => {
  console.log('Global beforeEach:', ctx.path, ctx.location.pathname);
  
  // Example: Track all page views
  analytics.trackPageView(ctx.path);
  
  // Return false to cancel all navigation
  return true;
});

// Runs after EVERY route's before/on/after handlers
r.afterEach((ctx) => {
  console.log('Global afterEach:', ctx.path);
  
  // Example: Update document title
  document.title = getPageTitle(ctx.path) + ' - My App';
  
  // Scroll to top on every navigation
  window.scrollTo(0, 0);
});

// Execution order:
// global beforeEach -> group before -> route before -> on -> route after -> group after -> global afterEach
```

Multiple `beforeEach` and `afterEach` handlers can be registered; they run in the order they were added.

## Navigation

### Programmatic Navigation

```javascript
// Navigate to a new route (pushes to history)
r.navigate('/users/42');

// Navigate with query parameters
r.navigate('/search', { q: 'oat', page: 1 });

// Navigate with hash
r.navigate('/page', {}, 'section1');

// Full navigation with all options
r.navigate('/users/42', { filter: 'active' }, 'settings', true);
// Parameters: path, query (object), hash, pushState (boolean)

// Replace current history entry instead of pushing
r.replace('/contact');
```

### Link Binding with data-route

Add the `data-route` attribute to links for automatic navigation without page reload:

```html
<a href="/users/42" data-route>View User 42</a>
<a href="/search?q=oat" data-route>Search "oat"</a>
```

Or bind programmatically to a parent element:

```javascript
// Bind all elements with data-route inside the nav element
r.bind(document.querySelector('nav'));
```

## Context Object

Every handler receives a context object with useful information:

```javascript
r.on('/users/{id}', (ctx) => {
  console.log(ctx.path);           // "/users/42"
  console.log(ctx.location);       // Full Location object
  console.log(ctx.location.pathname); // "/users/42"
  console.log(ctx.params);         // { id: "42" }
  console.log.ctx.query);          // Parsed query params object
  console.log(ctx.hash);           // URL hash (if any)
});
```

## Real-World Example: Single Page Application

```javascript
import router from '@knadh/tinyrouter';

const r = router.new({
  defaultHandler: (ctx) => {
    document.body.innerHTML = `
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <a href="/" data-route>Go Home</a>
    `;
  }
});

// Global handlers
r.beforeEach((ctx) => {
  // Show loading spinner
  document.body.innerHTML = '<div class="loading">Loading...</div>';
});

r.afterEach((ctx) => {
  // Update title
  document.title = ctx.pageTitle || 'My SPA';
  window.scrollTo(0, 0);
});

// Routes
r.on('/', (ctx) => {
  document.body.innerHTML = `
    <h1>Welcome Home</h1>
    <nav>
      <a href="/about" data-route>About</a> |
      <a href="/users/1" data-route>User 1</a> |
      <a href="/posts" data-route>Posts</a>
    </nav>
  `;
});

r.on('/about', (ctx) => {
  document.body.innerHTML = `
    <h1>About Us</h1>
    <p>This is a tiny SPA built with tinyrouter.js</p>
    <a href="/" data-route>Back Home</a>
  `;
});

r.on('/users/{id}', (ctx) => {
  const userId = ctx.params.id;
  // Fetch user data
  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(user => {
      document.body.innerHTML = `
        <h1>User: ${user.name}</h1>
        <p>Email: ${user.email}</p>
        <a href="/" data-route>Back Home</a>
      `;
    });
});

r.on('/posts', (ctx) => {
  const page = ctx.query.page || 1;
  document.body.innerHTML = `
    <h1>Posts (Page ${page})</h1>
    <ul>
      <li><a href="/posts/1" data-route>Post 1</a></li>
      <li><a href="/posts/2" data-route>Post 2</a></li>
    </ul>
  `;
});

// Initialize
r.ready();
```

## Integration with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Oat + TinyRouter</title>
  <link rel="stylesheet" href="oat.min.css">
</head>
<body>
  <nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3);">
    <a href="/" data-route class="logo">My App</a>
    <div class="hstack gap-3">
      <a href="/products" data-route>Products</a>
      <a href="/about" data-route>About</a>
      <a href="/contact" data-route>Contact</a>
    </div>
  </nav>
  
  <main id="app" style="padding: var(--space-6);"></main>
  
  <script src="oat.min.js" defer></script>
  <script type="module">
    import router from 'https://unpkg.com/@knadh/tinyrouter';
    
    const r = router.new({
      defaultHandler: (ctx) => {
        document.getElementById('app').innerHTML = `
          <article class="card">
            <h1>404 - Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <button onclick="window.location.href='/'">Go Home</button>
          </article>
        `;
      }
    });
    
    r.on('/', (ctx) => {
      document.getElementById('app').innerHTML = `
        <h1>Welcome</h1>
        <p>This is a single-page app using Oat UI and TinyRouter.</p>
        <div class="grid">
          <div class="col-4">
            <article class="card">
              <h3>Products</h3>
              <p>Browse our products</p>
              <button onclick="r.navigate('/products')">View Products</button>
            </article>
          </div>
          <div class="col-4">
            <article class="card">
              <h3>About</h3>
              <p>Learn more about us</p>
              <button onclick="r.navigate('/about')">Learn More</button>
            </article>
          </div>
        </div>
      `;
    });
    
    r.on('/products', (ctx) => {
      document.getElementById('app').innerHTML = `
        <h1>Products</h1>
        <div class="grid">
          <div class="col-4">
            <article class="card">
              <h3>Product 1</h3>
              <button onclick="r.navigate('/products/1')">View Details</button>
            </article>
          </div>
        </div>
      `;
    });
    
    r.on('/products/{id}', (ctx) => {
      document.getElementById('app').innerHTML = `
        <h1>Product ${ctx.params.id}</h1>
        <p>Details for product ${ctx.params.id}</p>
        <button onclick="r.navigate('/products')">Back to Products</button>
      `;
    });
    
    r.on('/about', (ctx) => {
      document.getElementById('app').innerHTML = `
        <h1>About Us</h1>
        <p>We build tiny, zero-dependency JavaScript libraries.</p>
      `;
    });
    
    r.on('/contact', (ctx) => {
      document.getElementById('app').innerHTML = `
        <h1>Contact</h1>
        <form>
          <label data-field>
            Email
            <input type="email" required />
          </label>
          <button type="submit">Send Message</button>
        </form>
      `;
    });
    
    // Initialize
    r.ready();
  </script>
</body>
</html>
```

## API Reference

| Method | Description |
|--------|-------------|
| `router.new(options)` | Creates a new router instance. Options include `defaultHandler` for 404s |
| `r.on(path, handler)` | Registers a route handler (can be function or object with before/on/after) |
| `r.group(prefix, handlers)` | Creates a group of routes with common prefix and shared handlers |
| `r.ready()` | Initializes the router and handles initial page load |
| `r.navigate(path, query, hash, pushState)` | Navigates to a new route |
| `r.replace(path, query, hash)` | Replaces current history entry |
| `r.bind(parent)` | Binds navigate() onclick to all elements with `data-route` inside parent |
| `r.beforeEach(handler)` | Registers global before navigation handler |
| `r.afterEach(handler)` | Registers global after navigation handler |

## Options

```javascript
const r = router.new({
  // Default handler for unmatched routes
  defaultHandler: (ctx) => {
    console.log('404:', ctx.location.pathname);
  }
});
```

See the source code for additional options.

## Browser Support

- Modern browsers with History API support
- Chrome, Firefox, Safari, Edge (latest versions)
- Graceful degradation: links work without JavaScript

## Best Practices

### DO

- Use semantic URLs (`/users/123` not `/u?id=123`)
- Handle 404s with `defaultHandler`
- Update document title in `afterEach` hook
- Scroll to top on navigation
- Use for simple SPAs and progressive enhancement

### DON'T

- Use for complex state management
- Store sensitive data in URLs
- Forget to handle browser back/forward buttons
- Nest routes deeply (keep flat structure)

## Limitations

- No built-in code splitting or lazy loading
- No nested route rendering (use composition instead)
- No built-in authentication (implement in hooks)
- Manual SSR implementation needed

## Comparison with Other Routers

| Feature | TinyRouter | React Router | Vue Router |
|---------|-----------|--------------|------------|
| Size | ~950B | ~40KB+ | ~40KB+ |
| Dependencies | 0 | React | Vue |
| Framework Required | No | Yes | Yes |
| Learning Curve | Minimal | Moderate | Moderate |

Licensed under the MIT License.
