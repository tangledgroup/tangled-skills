# TinyRouter.js - Frontend Routing

A tiny (~950 bytes), zero-dependency JavaScript library for frontend routing using `window.history`.

## Overview

TinyRouter provides simple client-side routing without framework dependencies. Perfect for single-page applications or progressive enhancement.

## Installation

### CDN

```html
<script src="https://unpkg.com/tinyrouter.js"></script>
```

### Download

```bash
wget https://raw.githubusercontent.com/knadh/tinyrouter.js/master/dist/tinyrouter.min.js
```

### npm

```bash
npm install tinyrouter.js
```

## Basic Usage

### Define Routes

```javascript
const router = new TinyRouter({
  '/': () => {
    document.body.innerHTML = '<h1>Home Page</h1>';
  },
  
  '/about': () => {
    document.body.innerHTML = '<h1>About Us</h1>';
  },
  
  '/contact': () => {
    document.body.innerHTML = '<h1>Contact</h1>';
  }
});

router.start();
```

### Dynamic Routes

```javascript
const router = new TinyRouter({
  '/users/:id': (params) => {
    const userId = params.id;
    document.body.innerHTML = `<h1>User: ${userId}</h1>`;
  },
  
  '/posts/:year/:month/:day': (params) => {
    document.body.innerHTML = `
      <h1>Post</h1>
      <p>Date: ${params.year}-${params.month}-${params.day}</p>
    `;
  }
});

router.start();
```

### Route with Query Parameters

```javascript
const router = new TinyRouter({
  '/search': (params, query) => {
    const q = query.q || '';
    const page = query.page || 1;
    
    document.body.innerHTML = `
      <h1>Search Results for "${q}"</h1>
      <p>Page: ${page}</p>
    `;
  }
});

router.start();
```

## Navigation

### Programmatic Navigation

```javascript
// Navigate to route
router.navigate('/about');

// Navigate with query params
router.navigate('/search?q=oat&page=2');

// Replace current history entry
router.replace('/contact');
```

### Link Elements Work Automatically

```html
<a href="/about">About</a>
<a href="/users/123">User 123</a>
<a href="/search?q=test">Search</a>
```

No JavaScript needed - links work natively!

## Advanced Features

### Wildcard Routes

```javascript
const router = new TinyRouter({
  '/api/*': (params) => {
    const path = params.rest; // Everything after /api/
    console.log('API path:', path);
  },
  
  '*': (params) => {
    // 404 handler
    document.body.innerHTML = '<h1>404 - Not Found</h1>';
  }
});
```

### Route Groups

```javascript
const adminRoutes = {
  '/admin/users': () => { /* ... */ },
  '/admin/settings': () => { /* ... */ },
  '/admin/*': () => { /* ... */ }
};

const router = new TinyRouter({
  '/': () => { /* Home */ },
  ...adminRoutes // Spread routes
});
```

### Before Navigation Hook

```javascript
const router = new TinyRouter({
  '/protected': () => {
    document.body.innerHTML = '<h1>Protected Page</h1>';
  }
}, {
  before: (to, from) => {
    // Check authentication
    if (to.path.startsWith('/protected') && !isLoggedIn()) {
      router.replace('/login');
      return false; // Cancel navigation
    }
    return true; // Allow navigation
  }
});
```

### After Navigation Hook

```javascript
const router = new TinyRouter(routes, {
  after: (to, from) => {
    // Scroll to top
    window.scrollTo(0, 0);
    
    // Update document title
    document.title = to.pageTitle || 'My App';
    
    // Analytics tracking
    ga('send', 'pageview', to.path);
  }
});
```

## Route Metadata

```javascript
const router = new TinyRouter({
  '/': {
    handler: () => { /* ... */ },
    title: 'Home'
  },
  
  '/about': {
    handler: () => { /* ... */ },
    title: 'About Us',
    auth: true // Custom metadata
  }
});
```

## Current Route Info

```javascript
// Get current route
const current = router.current;
console.log(current.path);    // "/users/123"
console.log_current.params);  // { id: "123" }
console.log(current.query);   // { page: "1" }
```

## Options

```javascript
const router = new TinyRouter(routes, {
  // Base path for all routes
  base: '/app',
  
  // Called before navigation (return false to cancel)
  before: (to, from) => true,
  
  // Called after navigation completes
  after: (to, from) => {},
  
  // Handle browser back/forward buttons
  handleHistory: true,
  
  // Initial path to start at
  initialPath: '/'
});
```

## Browser History API Integration

TinyRouter automatically uses the History API:

```javascript
// Push new state (creates history entry)
router.navigate('/about');

// Replace current state (no new history entry)
router.replace('/contact');

// Go back in history
history.back();

// Go forward in history
history.forward();
```

## Real-world Example

```javascript
const routes = {
  '/': () => renderHome(),
  
  '/products': () => renderProducts(),
  
  '/products/:id': (params) => {
    return renderProduct(params.id);
  },
  
  '/cart': () => renderCart(),
  
  '/checkout': () => {
    if (!isLoggedIn()) {
      router.replace('/login?redirect=/checkout');
      return false;
    }
    return renderCheckout();
  },
  
  '/account/orders': () => renderOrders(),
  
  '/account/*': () => renderAccountSettings(),
  
  '*': () => render404()
};

const router = new TinyRouter(routes, {
  base: '/',
  
  before: (to, from) => {
    // Analytics
    console.log(`Navigating from ${from.path} to ${to.path}`);
    
    // Auth check
    if (to.path.startsWith('/account') && !isLoggedIn()) {
      router.replace('/login?redirect=' + encodeURIComponent(to.path));
      return false;
    }
    
    return true;
  },
  
  after: (to, from) => {
    // Scroll to top on navigation
    window.scrollTo(0, 0);
    
    // Update title
    document.title = getPageTitle(to.path) + ' - My Shop';
  }
});

// Start router
router.start();

// Helper functions
function renderHome() { /* ... */ }
function renderProducts() { /* ... */ }
function renderProduct(id) { /* ... */ }
// etc.
```

## Integration with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="stylesheet" href="oat.min.css">
</head>
<body>
  <!-- Navigation -->
  <nav data-topnav class="hstack justify-between items-center" style="padding: var(--space-3);">
    <a href="/">My App</a>
    <div class="hstack gap-3">
      <a href="/products">Products</a>
      <a href="/about">About</a>
      <a href="/contact">Contact</a>
    </div>
  </nav>
  
  <!-- Main content (rendered by router) -->
  <main id="app" style="padding: var(--space-6);"></main>
  
  <script src="oat.min.js" defer></script>
  <script src="tinyrouter.min.js" defer></script>
  <script>
    const routes = {
      '/': () => `
        <h1>Welcome</h1>
        <p>This is the home page.</p>
        <button onclick="router.navigate('/products')">View Products</button>
      `,
      
      '/products': () => `
        <h1>Products</h1>
        <div class="grid">
          <div class="col-4">
            <article class="card">
              <h3>Product 1</h3>
              <button onclick="router.navigate('/products/1')">View Details</button>
            </article>
          </div>
        </div>
      `,
      
      '/products/:id': (params) => `
        <h1>Product ${params.id}</h1>
        <p>Details for product ${params.id}</p>
        <button onclick="router.navigate('/products')">Back</button>
      `
    };
    
    const router = new TinyRouter(routes);
    router.start();
  </script>
</body>
</html>
```

## Browser Support

- Chrome, Firefox, Safari, Edge (modern versions)
- Requires History API support
- Graceful degradation for non-JS browsers

## Comparison with Other Routers

| Feature | TinyRouter | React Router | Vue Router |
|---------|-----------|--------------|------------|
| Size | ~950B | ~40KB+ | ~40KB+ |
| Dependencies | 0 | React | Vue |
| Framework Required | No | Yes | Yes |
| SSR Support | Manual | Built-in | Built-in |

## Best Practices

### DO

- Use semantic URLs (`/users/123` not `/u?id=123`)
- Handle 404s with wildcard route
- Update document title in `after` hook
- Scroll to top on navigation
- Use for simple SPAs and progressive enhancement

### DON'T

- Use for complex state management
- Store sensitive data in URL
- Forget to handle browser back button
- Nest routes deeply (keep flat structure)

## Limitations

- No built-in code splitting
- No route lazy loading
- No nested routes (use composition instead)
- No built-in authentication
- Manual SSR implementation needed

For most simple to medium SPAs, TinyRouter provides all the routing you need with minimal overhead!
