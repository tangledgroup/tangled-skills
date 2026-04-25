# Solid Meta 0.29 - Component API Reference

Complete reference for all components exported by `@solidjs/meta`.

## MetaProvider

Required context provider that must wrap your application or component tree.

```tsx
import { MetaProvider } from '@solidjs/meta';

<MetaProvider>
  <YourApp />
</MetaProvider>
```

### Props

No props required. Children are the only required content.

### Behavior

- Establishes context for all head tag components
- On server: Collects tags and makes them available via `getAssets()` from `solid-js/web`
- On client: Removes SSR-generated tags (marked with `data-sm` attribute) and manages dynamic updates

---

## Title

Sets the document title. Only the last `<Title />` in the component tree is rendered.

```tsx
import { Title } from '@solidjs/meta';

<Title>My Page Title</Title>
```

### Props

All standard `HTMLTitleElement` attributes from SolidJS JSX:

```tsx
<Title 
  id="title"
  className=""
  // ... other HTMLTitleElement props
>
  Title text content
</Title>
```

### Cascading Behavior

When multiple `<Title />` components exist in the tree, only the **last one** is rendered. This enables child components to override parent titles:

```tsx
<MetaProvider>
  <Title>Default Site Title</Title>
  <Layout>
    {/* Default title shown here */}
    <Page>
      <Title>Specific Page - Site Title</Title>
      {/* "Specific Page - Site Title" is shown, overriding default */}
    </Page>
  </Layout>
</MetaProvider>
```

### Security

Title content is automatically escaped to prevent XSS:

```tsx
// This will be escaped in the output
<Title>{'Hello</title><script>alert("xss")</script>'}</Title>
// Renders as: <title>Hello&lt;/title&gt;&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;</title>
```

---

## Meta

Adds `<meta>` tags to the document head.

```tsx
import { Meta } from '@solidjs/meta';

// Basic meta tag
<Meta name="description" content="Page description" />

// Open Graph
<Meta property="og:title" content="Page Title" />
<Meta property="og:image" content="https://example.com/image.jpg" />

// Charset
<Meta charset="utf-8" />

// HTTP-equiv
<Meta httpEquiv="refresh" content="30;url=https://example.com" />
```

### Props

All standard `HTMLMetaElement` attributes from SolidJS JSX:

```tsx
<Meta
  name="description"      // Meta name attribute
  content="..."           // Meta content
  property="og:title"     // Open Graph/Schema.org property
  charset="utf-8"         // Character encoding
  httpEquiv="refresh"     // HTTP equivalent
  media="(prefers-color-scheme: dark)"  // Media query
  id=""
  className=""
  // ... other HTMLMetaElement props
/>
```

### Cascading Behavior

Meta tags with the same `name` or `property` attribute cascade (last one wins):

```tsx
<MetaProvider>
  <Meta name="description" content="Default description" />
  <Page>
    <Meta name="description" content="Specific page description" />
    {/* Only "Specific page description" is rendered */}
  </Page>
</MetaProvider>
```

### Distinct Meta Tags

Add additional attributes to create multiple meta tags with the same name:

```tsx
// Theme color for light and dark modes
<Meta name="theme-color" media="(prefers-color-scheme: light)" content="#fff" />
<Meta name="theme-color" media="(prefers-color-scheme: dark)" content="#000" />
// Both tags are rendered because they have different media attributes
```

### Property vs Name

The `property` and `name` attributes are treated equivalently for cascading purposes:

```tsx
<Meta property="name1">Meta 1</Meta>
<Meta property="name1">Meta 2</Meta>  // Replaces Meta 1
<Meta name="name1">Meta 3</Meta>      // Replaces Meta 2 (treated as same key)
```

---

## Link

Adds `<link>` tags to the document head.

```tsx
import { Link } from '@solidjs/meta';

// Favicon
<Link rel="icon" href="/favicon.ico" />

// Stylesheet
<Link rel="stylesheet" href="/styles.css" />

// Canonical URL
<Link rel="canonical" href="https://example.com/page" />

// Preconnect
<Link rel="preconnect" href="https://fonts.googleapis.com" />
```

### Props

All standard `HTMLLinkElement` attributes from SolidJS JSX:

```tsx
<Link
  rel="stylesheet"        // Relationship type (required)
  href="/styles.css"      // URL
  hreflang="en"           // Language
  media="print"           // Media query
  type="text/css"         // MIME type
  sizes="180x180"         // Icon sizes
  id=""
  className=""
  // ... other HTMLLinkElement props
/>
```

### Behavior

All `<Link />` tags are rendered (no cascading). Multiple links can coexist:

```tsx
<MetaProvider>
  <Link rel="icon" href="/favicon-32.png" sizes="32x32" />
  <Link rel="icon" href="/favicon-16.png" sizes="16x16" />
  <Link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  {/* All three links are rendered */}
</MetaProvider>
```

---

## Style

Adds inline `<style>` tags to the document head.

```tsx
import { Style } from '@solidjs/meta';

<Style>{`
  body {
    margin: 0;
    font-family: sans-serif;
  }
`}</Style>
```

### Props

All standard `HTMLStyleElement` attributes from SolidJS JSX:

```tsx
<Style
  media="print"           // Media query
  type="text/css"         // MIME type (default: text/css)
  id=""
  className=""
  // ... other HTMLStyleElement props
>
  {cssString}
</Style>
```

### Behavior

All `<Style />` tags are rendered. Useful for critical CSS or dynamic styles:

```tsx
<MetaProvider>
  <Style>{`body { margin: 0; }`}</Style>
  <Style media="print">{`.no-print { display: none; }`}</Style>
  {/* Both style tags are rendered */}
</MetaProvider>
```

---

## Base

Sets the base URL for all relative URLs in the document.

```tsx
import { Base } from '@solidjs/meta';

<Base href="https://example.com/" />
```

### Props

All standard `HTMLBaseElement` attributes from SolidJS JSX:

```tsx
<Base
  href="https://example.com/"  // Base URL (required)
  target="_blank"              // Default target for links
/>
```

### Behavior

Only one `<base>` tag should exist per document. Multiple `<Base />` components cascade (last one wins), similar to `<Title />`.

---

## Stylesheet

Helper component that adds a stylesheet link with `rel="stylesheet"` automatically.

```tsx
import { Stylesheet } from '@solidjs/meta';

<Stylesheet href="/styles.css" />
// Equivalent to: <Link rel="stylesheet" href="/styles.css" />
```

### Props

All `HTMLLinkElement` attributes except `rel` (which is set to `"stylesheet"` automatically):

```tsx
<Stylesheet
  href="/styles.css"      // Stylesheet URL (required)
  media="screen"          // Media query
  type="text/css"         // MIME type
  id=""
  className=""
  // ... other HTMLLinkElement props except rel
/>
```

### Usage Example

```tsx
<MetaProvider>
  <Stylesheet href="/critical.css" />
  <Stylesheet href="/main.css" media="screen" />
  <Stylesheet href="/print.css" media="print" />
</MetaProvider>
```

---

## useHead (Low-Level API)

For advanced usage, you can directly manipulate head tags using the `useHead` hook.

```tsx
import { useHead } from '@solidjs/meta';

function CustomHeadTag() {
  useHead({
    tag: 'meta',
    props: { name: 'custom', content: 'value' },
    id: createUniqueId(),
    get name() { return 'custom'; }
  });
  return null;
}
```

### TagDescription Interface

```typescript
interface TagDescription {
  tag: string;                    // HTML tag name ('title', 'meta', 'link', etc.)
  props: Record<string, unknown>; // Tag attributes
  setting?: { 
    close?: boolean;              // Whether tag needs closing (title, style)
    escape?: boolean;             // Whether content should be escaped
  };
  id: string;                     // Unique identifier
  name?: string;                  // For cascading (meta tags)
  ref?: Element;                  // DOM element reference (internal use)
}
```

**Note:** For most use cases, the high-level components (`<Title />`, `<Meta />`, etc.) are recommended over `useHead`.
