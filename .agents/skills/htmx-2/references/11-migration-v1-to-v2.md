# htmx 1.x to 2.x Migration Guide

This guide covers migrating from htmx 1.x to htmx 2.x.

## Breaking Changes Overview

htmx 2.x maintains high backwards compatibility, but several changes require attention:

### Extensions Moved Out of Core

All extensions are now distributed separately:

**Before (1.x):**
```html
<script src="https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js"></script>
<!-- Extensions bundled with core -->
```

**After (2.x):**
```html
<script src="https://unpkg.com/htmx.org@2.0.8/dist/htmx.min.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/ws.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/sse.js"></script>
```

**Action Required:** Explicitly load needed extensions.

### Module Support

New module-specific distribution files:

```html
<!-- ESM Modules -->
<script type="module">
    import htmx from 'https://unpkg.com/htmx.org@2.0.8/dist/htmx.esm.js';
</script>

<!-- AMD Modules -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/htmx.amd.js"></script>

<!-- CommonJS (Node.js) -->
const htmx = require('htmx.org');

<!-- Browser (unchanged) -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/htmx.min.js"></script>
```

### hx-on Attribute Syntax Changed

Event handler syntax now uses colons:

**Before (1.x):**
```html
<button hx-get="/info" 
        hx-on="htmx:beforeRequest: alert('before');
               htmx:afterRequest: alert('after');">
    Get Info
</button>
```

**After (2.x):**
```html
<button hx-get="/info" 
        hx-on::before-request="alert('before')"
        hx-on::after-request="alert('after')">
    Get Info
</button>
```

**Key changes:**
- Use `hx-on::event-name` syntax (double colon)
- Event names use kebab-case (`before-request` not `beforeRequest`)
- One event per attribute

### Default Configuration Changes

Several defaults changed in 2.x:

#### Scroll Behavior

**Before:** Smooth scrolling by default
**After:** Instant scrolling by default

```javascript
// Revert to 1.x smooth scrolling
htmx.config.scrollBehavior = 'smooth';
```

#### DELETE Request Parameters

**Before:** DELETE used form-encoded body
**After:** DELETE uses URL parameters (per HTTP spec)

```javascript
// Revert to 1.x behavior
htmx.config.methodsThatUseUrlParams = ['get'];
```

#### Cross-Origin Requests

**Before:** Cross-origin requests allowed by default
**After:** Same-origin only by default

```javascript
// Enable cross-origin requests
htmx.config.selfRequestsOnly = false;
```

### API Changes

#### htmx.makeFragment()

Now always returns `DocumentFragment`:

**Before (1.x):** Could return Element or DocumentFragment
**After (2.x):** Always returns DocumentFragment

```javascript
const fragment = htmx.makeFragment('<div>Content</div>');
// Always a DocumentFragment in 2.x
```

#### Extension API: selectAndSwap Removed

Replaced with `swap` method:

**Before (1.x):**
```javascript
api.selectAndSwap(element, html);
```

**After (2.x):**
```javascript
let target = api.getTarget(element);
let swapSpec = api.getSwapSpecification(element);
api.swap(target, html, swapSpec);
```

### IE Support Removed

htmx 2.x does not support Internet Explorer:

- If IE11 support required, stay on htmx 1.x (https://v1.htmx.org)
- htmx 1.x will continue to be maintained for IE support

## Migration Checklist

### 1. Update Script Tags

```html
<!-- Old -->
<script src="https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js"></script>

<!-- New -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/htmx.min.js"></script>
```

### 2. Add Required Extensions

Identify and add extensions you use:

```html
<!-- Load needed extensions -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/ws.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/sse.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/json-enc.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/idiomorph.js"></script>
```

### 3. Update hx-on Attributes

Find and update all `hx-on` attributes:

**Search for:** `hx-on="`
**Replace with:** `hx-on::event-name="`

```html
<!-- Before -->
<div hx-on="htmx:load: init(); htmx:afterRequest: log();">

<!-- After -->
<div hx-on::load="init()" 
     hx-on::after-request="log()">
```

### 4. Review Configuration Defaults

Check if you rely on changed defaults:

```javascript
// Add to your initialization if needed
htmx.config.scrollBehavior = 'smooth';        // If using smooth scroll
htmx.config.selfRequestsOnly = false;         // If making cross-origin requests
htmx.config.methodsThatUseUrlParams = ['get']; // If DELETE needs body
```

### 5. Update Extension Code

If you have custom extensions:

```javascript
// Old API
api.selectAndSwap(elt, html);

// New API
let target = api.getTarget(elt);
let swapSpec = api.getSwapSpecification(elt);
api.swap(target, html, swapSpec);
```

### 6. Test Critical Flows

Test these scenarios:
- Form submissions
- AJAX requests (GET, POST, PUT, PATCH, DELETE)
- WebSocket connections (if used)
- SSE connections (if used)
- Browser back/forward navigation
- File uploads
- Extensions in use

## Compatibility Extension

Use `htmx-1-compat` extension for gradual migration:

```html
<!-- Load compatibility extension -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/ext/htmx-1-compat.js"></script>

<!-- Apply to entire page -->
<body hx-ext="htmx-1-compat">
    <!-- Behaves like htmx 1.x -->
</body>
```

Or apply selectively:

```html
<!-- Only specific section uses 1.x behavior -->
<div hx-ext="htmx-1-compat">
    <!-- Legacy code here -->
</div>
```

## Common Migration Issues

### Extensions Not Loading

**Problem:** WebSocket/SSE not working after upgrade

**Solution:** Explicitly load extensions:

```html
<!-- Must load extensions AFTER htmx core -->
<script src="htmx.min.js"></script>
<script src="ext/ws.js"></script>
<script src="ext/sse.js"></script>
```

### Cross-Origin Requests Failing

**Problem:** 403 errors on cross-origin requests

**Solution:** Enable cross-origin requests:

```javascript
htmx.config.selfRequestsOnly = false;
```

### DELETE Requests Breaking

**Problem:** DELETE parameters not sent correctly

**Solution:** Revert to form-encoded body:

```javascript
htmx.config.methodsThatUseUrlParams = ['get'];
```

### Smooth Scrolling Disappeared

**Problem:** Page jumps instead of smooth scrolling

**Solution:** Re-enable smooth scroll:

```javascript
htmx.config.scrollBehavior = 'smooth';
```

### hx-on Events Not Firing

**Problem:** Event handlers not working

**Solution:** Update to new syntax:

```html
<!-- Wrong -->
<hx-on="htmx:beforeRequest: ...">

<!-- Correct -->
<hx-on::before-request="...">
```

## Upgrade Path Recommendation

### Phase 1: Preparation

1. Audit current htmx usage
2. List all extensions in use
3. Identify custom extensions
4. Document non-default configurations

### Phase 2: Staged Migration

1. Add `htmx-1-compat` extension
2. Upgrade to htmx 2.x core
3. Load 2.x versions of extensions
4. Test with compatibility layer

### Phase 3: Remove Compatibility

1. Update `hx-on` attributes
2. Remove `htmx-1-compat` extension
3. Add any needed configuration overrides
4. Full testing

### Phase 4: Cleanup

1. Remove old htmx 1.x references
2. Update documentation
3. Train team on 2.x features

## New Features to Leverage

After migrating, consider using 2.x improvements:

### View Transitions API

```html
<!-- Smooth page transitions -->
<button hx-get="/toggle-view" 
        hx-swap="innerHTML transition:true">
    Toggle View
</button>
```

### Improved OOB Swaps

```html
<!-- Nested OOB swaps enabled by default -->
<div id="parent" hx-swap-oob="true">
    <div id="child" hx-swap-oob="true">Child</div>
</div>
```

### Better Error Handling

```javascript
// Configure response handling
htmx.config.responseHandling = [
    { code: '422', swap: 'innerHTML', error: false }
];
```

### Enhanced Configuration

```javascript
// More granular control
htmx.config.triggerSpecsCache = {}; // Enable trigger caching
htmx.config.reportValidityOfForms = true; // Better form validation
```

## Rollback Plan

If issues arise, rollback to 1.x:

```html
<!-- Revert script tag -->
<script src="https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js"></script>

<!-- Remove extension scripts -->
<!-- Remove hx-ext="htmx-1-compat" attributes -->
```

## Resources

- [htmx 2.x Documentation](https://htmx.org/docs/)
- [htmx 1.x Documentation (Archive)](https://v1.htmx.org)
- [htmx 2.0 Release Notes](https://htmx.org/posts/2024-06-17-htmx-2-0-0-is-released/)
- [Migration Guide on htmx.org](https://htmx.org/migration-guide-htmx-1/)

## Next Steps

- [Security Best Practices](12-security-best-practices.md) - Security guidance
- [Performance Optimization](13-performance-optimization.md) - Performance tips
- [Common Patterns](10-common-patterns.md) - Modern patterns using 2.x features
