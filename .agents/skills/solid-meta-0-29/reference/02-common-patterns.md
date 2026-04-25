# Solid Meta 0.29 - Common Patterns

Real-world usage patterns and examples for managing document head tags in SolidJS applications.

## Dynamic Page Titles

### Route-Based Titles

Use dynamic titles based on the current route:

```tsx
import { Title } from '@solidjs/meta';
import { useLocation } from '@solidjs/router';

function Layout() {
  const location = useLocation();
  
  const getPageTitle = () => {
    switch(location.pathname) {
      case '/about': return 'About Us';
      case '/contact': return 'Contact';
      case '/products': return 'Products';
      default: return 'Home';
    }
  };

  return (
    <div>
      <Title>{getPageTitle()} - My Site</Title>
      <nav><!-- navigation --></nav>
      <Outlet />
    </div>
  );
}
```

### Component Hierarchy Titles

Leverage cascading behavior for nested titles:

```tsx
<MetaProvider>
  {/* Default site title */}
  <Title>My Website</Title>
  
  <Layout>
    <Section>
      {/* Overrides default with section-specific title */}
      <Title>Products - My Website</Title>
      <ProductList />
    </Section>
    
    <Section>
      {/* Another override for different section */}
      <Title>About - My Website</Title>
      <AboutContent />
    </Section>
  </Layout>
</MetaProvider>
```

### Dynamic Content Titles

Generate titles from data:

```tsx
import { createResource } from 'solid-js';
import { Title } from '@solidjs/meta';

function ArticlePage({ id }) {
  const [article] = createResource(() => fetchArticle(id));

  return (
    <div>
      {/* Title updates when article loads */}
      <Title>{() => article()?.title || 'Loading...'}</Title>
      
      <Show when={article()} fallback={<Loading />}>
        {(a) => <h1>{a.title}</h1>}
      </Show>
    </div>
  );
}
```

---

## SEO Meta Tags

### Basic SEO Setup

```tsx
import { Meta, Title } from '@solidjs/meta';

function Page() {
  return (
    <>
      <Title>Page Title - Site Name</Title>
      <Meta name="description" content="Brief page description (155-160 chars)" />
      <Meta name="robots" content="index, follow" />
      <Link rel="canonical" href="https://example.com/current-page" />
    </>
  );
}
```

### Open Graph Tags

```tsx
import { Meta } from '@solidjs/meta';

function SocialMeta() {
  return (
    <>
      <Meta property="og:title" content="Page Title" />
      <Meta property="og:description" content="Page description" />
      <Meta property="og:image" content="https://example.com/image.jpg" />
      <Meta property="og:url" content="https://example.com/page" />
      <Meta property="og:type" content="website" />
      
      {/* Twitter Card */}
      <Meta name="twitter:card" content="summary_large_image" />
      <Meta name="twitter:title" content="Page Title" />
      <Meta name="twitter:description" content="Page description" />
      <Meta name="twitter:image" content="https://example.com/image.jpg" />
    </>
  );
}
```

### Dynamic Social Meta

```tsx
import { createSignal } from 'solid-js';
import { Meta } from '@solidjs/meta';

function ProductPage({ productId }) {
  const [product] = createResource(async () => {
    const res = await fetch(`/api/products/${productId}`);
    return res.json();
  });

  return (
    <div>
      <Meta 
        property="og:title" 
        // Access reactive data in prop
        // Note: May need to use createEffect for complex cases
      />
      <Meta 
        property="og:image" 
        content={() => product()?.image || '/default.jpg'} 
      />
    </div>
  );
}
```

---

## Theme Switching

### Dark/Light Mode Meta Tags

```tsx
import { createSignal } from 'solid-js';
import { Meta } from '@solidjs/meta';

function ThemeProvider() {
  const [theme, setTheme] = createSignal('light');

  return (
    <div class={theme()}>
      {/* Theme color for mobile browsers */}
      <Meta 
        name="theme-color" 
        content={() => theme() === 'dark' ? '#000' : '#fff'} 
      />
      
      <button onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
        Toggle Theme
      </button>
    </div>
  );
}
```

### Multiple Theme Colors

Different colors for different contexts:

```tsx
import { Meta } from '@solidjs/meta';

function ThemeMeta() {
  return (
    <>
      {/* Light mode theme color */}
      <Meta 
        name="theme-color" 
        media="(prefers-color-scheme: light)" 
        content="#ffffff" 
      />
      
      {/* Dark mode theme color */}
      <Meta 
        name="theme-color" 
        media="(prefers-color-scheme: dark)" 
        content="#000000" 
      />
      
      {/* Custom theme class */}
      <Meta 
        name="theme-color" 
        media="(prefers-color-scheme: light) and (data-theme=blue)" 
        content="#3b82f6" 
      />
    </>
  );
}
```

---

## Favicon Management

### Multiple Icon Sizes

```tsx
import { Link } from '@solidjs/meta';

function FaviconSet() {
  return (
    <>
      {/* Standard favicon */}
      <Link rel="icon" href="/favicon.ico" />
      
      {/* PNG favicons */}
      <Link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png" />
      <Link rel="icon" href="/favicon-16.png" sizes="16x16" type="image/png" />
      
      {/* Apple Touch Icon */}
      <Link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180" />
      
      {/* Android Chrome */}
      <Link rel="icon" href="/android-chrome-192.png" sizes="192x192" type="image/png" />
      <Link rel="icon" href="/android-chrome-512.png" sizes="512x512" type="image/png" />
      
      {/* MS Tiles */}
      <Meta name="msapplication-TileColor" content="#da532c" />
      <Meta name="msapplication-TileImage" content="/mstile-144x144.png" />
    </>
  );
}
```

---

## Conditional Meta Tags

### Environment-Based Tags

```tsx
import { Meta } from '@solidjs/meta';
import { isServer } from 'solid-js/web';

function EnvMeta() {
  const env = import.meta.env.PROD ? 'production' : 'development';
  
  return (
    <>
      <Meta name="env" content={env} />
      
      {/* Only in development */}
      <Show when={!import.meta.env.PROD}>
        <Meta name="debug" content="true" />
      </Show>
    </>
  );
}
```

### Feature Flags

```tsx
import { createSignal } from 'solid-js';
import { Meta, Style } from '@solidjs/meta';

function FeatureFlags() {
  const [flags, setFlags] = createSignal({ darkMode: false, beta: true });

  return (
    <>
      <Meta name="feature:dark-mode" content={() => String(flags().darkMode)} />
      <Meta name="feature:beta" content={() => String(flags().beta)} />
      
      {/* Dynamic critical CSS based on features */}
      <Style>{() => flags().darkMode ? 'body { background: #000; }' : ''}</Style>
    </>
  );
}
```

---

## Preloading and Prefetching

### Critical Resources

```tsx
import { Link } from '@solidjs/meta';

function PreloadCritical() {
  return (
    <>
      {/* Preload critical CSS */}
      <Link rel="preload" href="/critical.css" as="style" />
      
      {/* Preload fonts */}
      <Link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      
      {/* Preconnect to third-party domains */}
      <Link rel="preconnect" href="https://fonts.googleapis.com" />
      <Link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      
      {/* Prefetch next page */}
      <Link rel="prefetch" href="/next-page-data.json" as="fetch" />
    </>
  );
}
```

---

## Structured Data (JSON-LD)

### Schema.org Markup

```tsx
import { Style } from '@solidjs/meta';

function StructuredData({ product }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": product.name,
    "description": product.description,
    "image": product.image,
    "offers": {
      "@type": "Offer",
      "price": product.price,
      "priceCurrency": "USD"
    }
  };

  return (
    <Style type="application/ld+json">
      {JSON.stringify(jsonLd)}
    </Style>
  );
}
```

### Dynamic Structured Data

```tsx
import { createResource } from 'solid-js';
import { Style } from '@solidjs/meta';

function ArticleStructuredData({ articleId }) {
  const [article] = createResource(() => fetch(`/api/articles/${articleId}`));

  return (
    <Style type="application/ld+json">
      {() => JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article()?.title,
        "author": {
          "@type": "Person",
          "name": article()?.author.name
        },
        "datePublished": article()?.publishedAt,
        "image": article()?.featuredImage
      })}
    </Style>
  );
}
```

---

## Error Handling and Fallbacks

### Safe Meta Tags

```tsx
import { Meta, Title } from '@solidjs/meta';
import { createResource } from 'solid-js';

function SafeMeta({ postId }) {
  const [post, { error }] = createResource(() => fetchPost(postId));

  return (
    <>
      {/* Fallback title if loading or error */}
      <Title>
        {() => error ? 'Error Loading Post' : post()?.title || 'Loading...'}
      </Title>
      
      {/* Only add meta if we have data */}
      <Show when={post()} fallback={<Meta name="status" content="loading" />}>
        {(p) => (
          <>
            <Meta name="description" content={p.excerpt} />
            <Meta property="og:image" content={p.image} />
          </>
        )}
      </Show>
    </>
  );
}
```

---

## Performance Optimizations

### Critical CSS Inlining

```tsx
import { Style } from '@solidjs/meta';

function CriticalCSS() {
  // Inline critical CSS for above-the-fold content
  return (
    <Style>{`
      /* Critical above-the-fold styles */
      .hero { /* ... */ }
      .nav { /* ... */ }
      
      /* Non-critical styles loaded separately */
    `}</Style>
  );
}
```

### Conditional Stylesheets

```tsx
import { createSignal } from 'solid-js';
import { Stylesheet } from '@solidjs/meta';

function ThemeStylesheets() {
  const [theme, setTheme] = createSignal('light');

  return (
    <>
      {/* Base styles */}
      <Stylesheet href="/base.css" />
      
      {/* Theme-specific styles */}
      <Stylesheet 
        href={() => theme() === 'dark' ? '/dark-theme.css' : '/light-theme.css'} 
      />
    </>
  );
}
```
