# Solid Meta 0.29 - Server-Side Rendering

Complete guide to SSR setup, hydration, and integration with SolidStart and custom server configurations.

## How SSR Works with Solid Meta

### Tag Collection Process

1. **Server Side**: During `renderToString()`, all head tags are collected into an internal array
2. **Asset Extraction**: Tags are made available via `getAssets()` from `solid-js/web`
3. **HTML Injection**: Server injects collected tags into the `<head>` element
4. **Client Hydration**: Client removes SSR tags (marked with `data-sm` attribute) and manages dynamic updates

### Data Flow

```
Server Rendering:
  <MetaProvider>
    <Title>Page Title</Title>
    <Meta name="description" content="..." />
  </MetaProvider>
       ↓
  Tags collected in internal array
       ↓
  getAssets() returns HTML string
       ↓
  Injected into server HTML template
       ↓
  Sent to browser with data-sm attributes

Client Hydration:
  Browser receives HTML with SSR tags
       ↓
  MetaProvider initialized on client
       ↓
  SSR tags (data-sm) removed
       ↓
  Client renders same components
       ↓
  Fresh tags inserted dynamically
```

---

## SolidStart Integration

SolidStart provides built-in support for `@solidjs/meta`.

### Basic Setup

**app.tsx**
```tsx
// @refresh reload
import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start";
import { Suspense } from "solid-js";
import "./app.css";

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          {/* Optional fallback title */}
          <Title>SolidStart App</Title>
          
          {/* Navigation or layout */}
          <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
          </nav>
          
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

### Route-Specific Meta Tags

With file-based routing, add meta tags directly in route files:

**routes/index.tsx**
```tsx
import { Title, Meta } from "@solidjs/meta";

export default function Index() {
  return (
    <main>
      <Title>Home - My App</Title>
      <Meta name="description" content="Welcome to our homepage" />
      
      <h1>Welcome Home</h1>
      {/* ... content */}
    </main>
  );
}
```

**routes/about.tsx**
```tsx
import { Title, Meta } from "@solidjs/meta";

export default function About() {
  return (
    <main>
      <Title>About Us - My App</Title>
      <Meta name="description" content="Learn about our company" />
      <Meta property="og:image" content="/about-hero.jpg" />
      
      <h1>About Us</h1>
      {/* ... content */}
    </main>
  );
}
```

### Layout with Default Meta

**routes/__root.tsx**
```tsx
import { Title, Meta } from "@solidjs/meta";
import { A, useLocation } from "@solidjs/router";
import { Component, Suspense } from "solid-js";

export default function Root() {
  const location = useLocation();

  return (
    <document>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body>
        <MetaProvider>
          {/* Default meta tags for all routes */}
          <Meta name="robots" content="index, follow" />
          <Meta property="og:site_name" content="My App" />
          
          <div class="app">
            <nav>
              <A href="/">Home</A>
              <A href="/about">About</A>
            </nav>
            
            <Suspense>
              <Outlet />
            </Suspense>
          </div>
        </MetaProvider>
      </body>
    </document>
  );
}
```

---

## Custom SSR Setup

For custom server setups without SolidStart, manual configuration is required.

### Server-Side Configuration

**entry-server.tsx**
```tsx
import { renderToString, getAssets } from 'solid-js/web';
import { MetaProvider } from '@solidjs/meta';
import App from './App';

export default function render(req, res) {
  // Render the app with MetaProvider
  const appHtml = renderToString(() => (
    <MetaProvider>
      <App />
    </MetaProvider>
  ));

  // Send complete HTML with assets injected
  res.send(`
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        <!-- Solid Meta injects tags here via getAssets() -->
        ${getAssets()}
        
        <!-- Other head content -->
        <link rel="stylesheet" href="/main.css" />
      </head>
      <body>
        <div id="root">${appHtml}</div>
        
        <!-- Client-side hydration script -->
        <script src="/main.js" type="module"></script>
      </body>
    </html>
  `);
}
```

### Important: Avoid Manual Title Tags

**DO NOT add `<title>` tags in server files:**

```tsx
// ❌ WRONG - This overrides @solidjs/meta
res.send(`
  <!doctype html>
  <html>
    <head>
      <title>Static Title</title>  <!-- Don't do this! -->
      ${getAssets()}
    </head>
    <!-- ... -->
  </html>
`);

// ✅ CORRECT - Let @solidjs/meta handle titles
res.send(`
  <!doctype html>
  <html>
    <head>
      ${getAssets()}  <!-- Title comes from here -->
    </head>
    <!-- ... -->
  </html>
`);
```

---

## Client-Side Setup

Client-side requires no special configuration beyond the standard SolidJS setup.

### Entry Client

**entry-client.tsx**
```tsx
import { mount, hydrate } from 'solid-js/web';
import { MetaProvider } from '@solidjs/meta';
import App from './App';

const render = document.getElementById('root');

// Check if we're hydrating SSR content or mounting fresh
if (render.dataset.hydrated === "true") {
  hydrate(() => (
    <MetaProvider>
      <App />
    </MetaProvider>
  ), render);
} else {
  mount(() => (
    <MetaProvider>
      <App />
    </MetaProvider>
  ), render);
}
```

### SPA Navigation

For SPAs without SSR, `<MetaProvider>` still works to manage head tags:

```tsx
import { mount } from 'solid-js/web';
import { MetaProvider, Title } from '@solidjs/meta';
import App from './App';

mount(() => (
  <MetaProvider>
    <Title>My SPA</Title>
    <App />
  </MetaProvider>
), document.getElementById('root'));
```

---

## Hydration Details

### How Hydration Works

1. **Server renders** HTML with tags marked with `data-sm="unique-id"` attribute
2. **Client receives** HTML with these marked tags in `<head>`
3. **MetaProvider initializes** on client and finds all `data-sm` tags
4. **SSR tags are removed** from document head
5. **Client components render** and insert fresh tags

### Example Hydration Flow

**Server Output:**
```html
<head>
  <title data-sm="0-0-0-0">Page Title</title>
  <meta data-sm="0-0-1-0" name="description" content="Description">
  <link data-sm="0-0-2-0" rel="icon" href="/favicon.ico">
</head>
```

**After Client Hydration:**
```html
<head>
  <title>Page Title</title>
  <meta name="description" content="Description">
  <link rel="icon" href="/favicon.ico">
</head>
```

### Manual Hydration Script (If Needed)

For some setups, you may need a hydration script:

**hydration-script.ts**
```ts
export function hydrationScript() {
  const script = document.createElement('script');
  script.id = 'solid-meta-hydration';
  script.textContent = `
    (function() {
      var ssrTags = document.head.querySelectorAll('[data-sm]');
      Array.prototype.forEach.call(ssrTags, function(tag) {
        tag.parentNode.removeChild(tag);
      });
    })();
  `;
  document.head.appendChild(script);
}

export function removeScript() {
  const script = document.getElementById('solid-meta-hydration');
  if (script) script.remove();
}
```

---

## Advanced SSR Patterns

### Dynamic Meta from API

**routes/post/[id].tsx**
```tsx
import { Title, Meta } from "@solidjs/meta";
import { createResource } from "solid-js";
import { useParams } from "@solidjs/router";

export default function PostPage() {
  const params = useParams();
  
  // Fetch post data
  const [post] = createResource(
    () => params.id,
    async (id) => fetch(`/api/posts/${id}`).then(r => r.json())
  );

  return (
    <article>
      {/* Title updates when resource loads */}
      <Title>
        {() => post()?.title || `Post #${params.id} - My Blog`}
      </Title>
      
      {/* Meta tags from loaded data */}
      <Meta 
        name="description" 
        content={() => post()?.excerpt || 'Loading...'} 
      />
      <Meta 
        property="og:image" 
        content={() => post()?.featuredImage || '/default.jpg'} 
      />
      
      <Show when={post()} fallback={<p>Loading...</p>}>
        {(p) => (
          <>
            <h1>{p.title}</h1>
            <img src={p.featuredImage} alt={p.title} />
            <div>{p.content}</div>
          </>
        )}
      </Show>
    </article>
  );
}
```

### Route Data with Meta

Using SolidStart's route data loading:

**routes/products/[slug].tsx**
```tsx
import { Title, Meta } from "@solidjs/meta";
import { useRouteData } from "@solidjs/start";

export async function route(data) {
  const slug = data.params.slug;
  const product = await getProductBySlug(slug);
  
  return { product };
}

export default function ProductPage() {
  const data = useRouteData() as { product: Product };

  return (
    <div>
      <Title>{data.product.name} - Store</Title>
      <Meta name="description" content={data.product.description} />
      <Meta property="og:image" content={data.product.image} />
      
      <h1>{data.product.name}</h1>
      <p>${data.product.price}</p>
    </div>
  );
}
```

### Conditional SSR Meta

```tsx
import { createSignal } from 'solid-js';
import { Meta } from '@solidjs/meta';
import { isServer } from 'solid-js/web';

function ConditionalMeta() {
  const [view, setView] = createSignal('default');

  return (
    <>
      {/* Different meta based on view state */}
      <Meta 
        name="application-state" 
        content={() => view()} 
      />
      
      {/* Server-only meta */}
      {isServer && <Meta name="rendered-at" content={new Date().toISOString()} />}
      
      <button onClick={() => setView('expanded')}>Expand</button>
    </>
  );
}
```

---

## Troubleshooting SSR Issues

### Tags Not Appearing in Server HTML

**Check:**
1. `getAssets()` is called in server template
2. `<MetaProvider>` wraps the app on server
3. No manual `<title>` tags overriding meta

**Debug:**
```tsx
// In server render, add logging
const appHtml = renderToString(() => {
  console.log('Rendering with MetaProvider');
  return (
    <MetaProvider>
      <App />
    </MetaProvider>
  );
});

const assets = getAssets();
console.log('Collected assets:', assets);  // Should show meta tags
```

### Hydration Mismatch Warnings

**Causes:**
- Client and server rendering different meta tags
- Missing `<MetaProvider>` on client side

**Fix:**
Ensure identical component tree on both server and client:

```tsx
// Both server and client should have:
<MetaProvider>
  <App />
</MetaProvider>
```

### Multiple Title Tags

If you see multiple `<title>` tags in the DOM:

1. Check for manual `<title>` in server template (remove it)
2. Ensure only one `<Title>` component is active at a time
3. Verify no duplicate `<MetaProvider>` instances

---

## Performance Considerations

### Critical CSS

Inline critical CSS using `<Style>`:

```tsx
import { Style } from '@solidjs/meta';

function CriticalStyles() {
  return (
    <Style>{`
      /* Above-the-fold styles only */
      .header { /* ... */ }
      .hero { /* ... */ }
    `}</Style>
  );
}
```

### Preload Important Resources

```tsx
import { Link } from '@solidjs/meta';

function Preloads() {
  return (
    <>
      <Link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      <Link rel="preconnect" href="https://api.example.com" />
    </>
  );
}
```
