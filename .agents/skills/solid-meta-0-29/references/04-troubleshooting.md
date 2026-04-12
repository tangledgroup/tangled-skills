# Solid Meta 0.29 - Troubleshooting Guide

Common issues, errors, and debugging techniques for @solidjs/meta.

## Common Errors

### Error: `<MetaProvider /> should be in the tree`

**Cause:** Head tag components (`<Title />`, `<Meta />`, etc.) are used without wrapping with `<MetaProvider>`.

**Solution:**
```tsx
// ❌ WRONG
function App() {
  return (
    <div>
      <Title>Page Title</Title>  {/* Error! */}
    </div>
  );
}

// ✅ CORRECT
import { MetaProvider } from '@solidjs/meta';

function App() {
  return (
    <MetaProvider>
      <div>
        <Title>Page Title</Title>  {/* Works! */}
      </div>
    </MetaProvider>
  );
}
```

**In Nested Components:**
Ensure `<MetaProvider>` is in the parent hierarchy:

```tsx
// App.tsx
<MetaProvider>
  <Layout>
    <Page />  {/* Can use Title, Meta, etc. here */}
  </Layout>
</MetaProvider>
```

---

### Multiple Title Tags in DOM

**Symptom:** Browser shows multiple `<title>` tags or console warnings.

**Causes:**
1. Manual `<title>` tag in server HTML template
2. Multiple `<Title>` components without proper cascading
3. Duplicate `<MetaProvider>` instances

**Solution 1: Remove Manual Title Tags**
```tsx
// ❌ WRONG - entry-server.tsx
res.send(`
  <!doctype html>
  <html>
    <head>
      <title>My Site</title>  {/* Remove this! */}
      ${getAssets()}
    </head>
  </html>
`);

// ✅ CORRECT
res.send(`
  <!doctype html>
  <html>
    <head>
      ${getAssets()}  {/* Title comes from here */}
    </head>
  </html>
`);
```

**Solution 2: Understand Cascading**
Multiple `<Title>` components are expected - only the last renders:

```tsx
<MetaProvider>
  <Title>Default</Title>
  <Page>
    <Title>Specific</Title>  {/* Only "Specific" is shown */}
  </Page>
</MetaProvider>
```

This is **correct behavior** - cascading allows child components to override parent titles.

---

### Meta Tags Not Updating

**Symptom:** Changing props on `<Meta>` doesn't reflect in the DOM.

**Cause:** SolidJS reactivity not triggered or meta tags with same key colliding.

**Solution 1: Ensure Reactive Props**
```tsx
// ❌ WRONG - prop is not reactive
const description = "Static description";

<Meta name="description" content={description} />

// ✅ CORRECT - use signal or function
const [description, setDescription] = createSignal("Initial");

<Meta name="description" content={() => description()} />
// or
<Meta name="description" content={description()} />
```

**Solution 2: Distinct Meta Keys**
Meta tags with same `name` or `property` cascade. Add distinguishing attributes:

```tsx
// ❌ Only second tag renders (same name)
<Meta name="description" content="First" />
<Meta name="description" content="Second" />  {/* Only this shows */}

// ✅ Both render (different media attributes)
<Meta name="description" media="screen" content="For screen" />
<Meta name="description" media="print" content="For print" />
```

---

### Tags Not Appearing in Server HTML

**Symptom:** Meta tags appear on client but not in server-rendered HTML.

**Checklist:**
1. ✅ `<MetaProvider>` wraps app on server side
2. ✅ `getAssets()` is called in server template
3. ✅ No manual `<title>` tags overriding meta
4. ✅ Components rendering meta are executed during SSR

**Debug Steps:**
```tsx
// entry-server.tsx
import { renderToString, getAssets } from 'solid-js/web';
import { MetaProvider } from '@solidjs/meta';

const appHtml = renderToString(() => (
  <MetaProvider>
    <App />
  </MetaProvider>
));

const assets = getAssets();

// Debug: Check what was collected
console.log('Collected meta tags:', assets);

if (!assets || !assets.includes('<title')) {
  console.error('No meta tags collected! Check MetaProvider and component tree.');
}

res.send(`
  <!doctype html>
  <html>
    <head>
      ${assets}
    </head>
    <body><div id="root">${appHtml}</div></body>
  </html>
`);
```

---

### Hydration Mismatch Warnings

**Symptom:** Console shows hydration mismatch or extra tags after client loads.

**Causes:**
1. Different component tree on server vs client
2. Missing `<MetaProvider>` on client side
3. Conditional rendering differs between server and client

**Solution 1: Ensure Identical Trees**
```tsx
// Server (entry-server.tsx)
renderToString(() => (
  <MetaProvider>
    <App />
  </MetaProvider>
));

// Client (entry-client.tsx)
hydrate(() => (
  <MetaProvider>  {/* Must have MetaProvider here too */}
    <App />
  </MetaProvider>
), document.getElementById('root'));
```

**Solution 2: Handle isServer Differences**
```tsx
import { isServer } from 'solid-js/web';

function ConditionalContent() {
  // ✅ Safe - uses isServer check consistently
  return (
    <>
      <Show when={!isServer}>
        <ClientOnlyComponent />
      </Show>
    </>
  );
}
```

---

### Title Content Not Escaped

**Symptom:** HTML in title content renders instead of displaying as text.

**Note:** Solid Meta **automatically escapes** title content for security:

```tsx
<Title>{'Hello</title><script>alert("xss")</script>'}</Title>
// Renders as (escaped):
// <title>Hello&lt;/title&gt;&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;</title>
```

This is **correct and expected behavior** to prevent XSS attacks.

If you need literal HTML entities:
```tsx
<Title>{'Hello & World'}</Title>  {/* Renders: Hello &amp; World */}
```

---

## Debugging Techniques

### Inspect Collected Tags

Add debug logging to see what tags are being collected:

```tsx
// Create a debug wrapper
function DebugMetaProvider(props) {
  const originalContext = useContext(MetaContext);
  
  // Log when tags are added (requires patching or custom provider)
  // For production, use browser DevTools instead
  
  return <MetaProvider>{props.children}</MetaProvider>;
}
```

### Browser DevTools Inspection

**Check Server HTML:**
1. View Page Source (`Ctrl+U` or `Cmd+Option+U`)
2. Look for meta tags with `data-sm` attribute:
   ```html
   <title data-sm="0-0-0-0">Page Title</title>
   <meta data-sm="0-0-1-0" name="description" content="...">
   ```

**Check Live DOM:**
1. Open DevTools Elements panel
2. Inspect `<head>` element
3. Tags should exist without `data-sm` after hydration:
   ```html
   <head>
     <title>Page Title</title>
     <meta name="description" content="...">
   </head>
   ```

### Network Tab Verification

For SSR apps, check the initial HTML response:

1. Open DevTools Network tab
2. Reload page
3. Click on main document request
4. Inspect Response tab for meta tags in HTML

---

## Version-Specific Issues

### Solid 1.x Compatibility

**Issue:** Using old version with Solid 1.x

**Solution:**
```bash
# For Solid 1.8.4+
npm install @solidjs/meta@^0.29.0

# For Solid 1.0.x
npm install @solidjs/meta@^0.27.0

# For Solid 0.x
npm install @solidjs/meta@^0.26.0
```

### Changes in v0.29.7

**Refactored `renderTags` to use `flattenChildren`:**
- Improves handling of nested children in title/style tags
- May affect custom components using `useHead` directly

**Migration:**
```tsx
// Old (still works but may have issues with nested content)
<Title>{getDynamicTitle()}</Title>

// New (recommended for complex cases)
<Title>{() => getDynamicTitle()}</Title>
```

### Changes in v0.29.6

**Fixed removing one `<title>` renders all previous `<title>s`:**
- Previous versions had a bug where removing a title would show all prior titles
- v0.29.6+ correctly shows only the last active title

If upgrading from < 0.29.6, test title cascading behavior.

---

## Performance Issues

### Excessive Re-renders

**Symptom:** Page feels slow or janky when meta tags update.

**Cause:** Meta tag components triggering unnecessary re-renders.

**Solution:** Memoize stable values:

```tsx
import { memo, createMemo } from 'solid-js';

function OptimizedMeta() {
  const [data] = createResource(fetchData);
  
  // Memoize the content to prevent unnecessary updates
  const description = createMemo(() => data()?.description || 'Default');
  
  return (
    <Meta name="description" content={description} />
  );
}
```

### Large Style Tags

**Symptom:** Inline styles causing layout shifts or slow rendering.

**Solution:** Move non-critical CSS to external files:

```tsx
// ❌ Avoid large inline styles
<Style>{`/* 1000+ lines of CSS */`}</Style>

// ✅ Use for critical CSS only
<Style>{`.critical { /* above-the-fold only */ }`}</Style>
<Stylesheet href="/main.css" />  {/* Rest in file */}
```

---

## Type Errors (TypeScript)

### Missing Type Definitions

**Error:** `Cannot find module '@solidjs/meta'`

**Solution:**
```bash
npm install --save-dev @types/solid-js
# or ensure you have the latest solid-js types
```

### Prop Type Mismatches

**Error:** Type mismatch on component props.

**Solution:** Use correct type assertions:

```tsx
// Title accepts HTMLTitleElement attributes
<Title class="title-class">  {/* Not className in JSX */}
  My Title
</Title>

// Meta accepts HTMLMetaElement attributes  
<Meta 
  name="description" 
  content={stringValue}  // Must be string
/>

// Link accepts HTMLLinkElement attributes
<Link 
  rel="stylesheet"  // Must be valid rel value
  href={stringValue}  // Must be string
/>
```

---

## Browser Compatibility

### Older Browsers

Solid Meta works in all browsers supported by SolidJS. For IE11 or older browsers:

1. Ensure polyfills for `document.head` (rarely needed)
2. Test hydration behavior thoroughly
3. Consider feature detection for critical meta tags

### Bot Crawlers

Some crawlers (like Googlebot) have limited JavaScript support:

**Ensure SSR is working:**
1. Verify meta tags appear in server HTML response
2. Use `robots.txt` to guide crawler behavior
3. Test with tools like Google's Rich Results Test

```tsx
// Important for SEO - ensure these render on server
<MetaProvider>
  <Title>Page Title</Title>
  <Meta name="description" content="..." />
  <Meta property="og:title" content="..." />
</MetaProvider>
```

---

## Getting Help

### Check Documentation

1. Official docs: https://docs.solidjs.com/solid-meta/
2. GitHub README: https://github.com/solidjs/solid-meta
3. Changelog: https://github.com/solidjs/solid-meta/blob/main/CHANGELOG.md

### Report Issues

If you encounter a bug:

1. Check existing issues: https://github.com/solidjs/solid-meta/issues
2. Create minimal reproduction example
3. Include:
   - `@solidjs/meta` version
   - SolidJS version
   - Browser/Environment details
   - Steps to reproduce

### Community Resources

- SolidJS Discord: https://discord.com/invite/solidjs
- SolidJS GitHub Discussions: https://github.com/solidjs/solid-js/discussions
- Stack Overflow tag: `[solidjs]`
