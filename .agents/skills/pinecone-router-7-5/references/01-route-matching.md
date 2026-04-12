# Route Matching in Pinecone Router 7.5

This reference covers route pattern syntax, parameter types, matching rules, and advanced routing patterns for Pinecone Router v7.5.

## Declaring Routes

Routes are declared using the `x-route` directive on `<template>` elements:

```html
<div x-data="router()">
  <template x-route="/"></template>
  <template x-route="/about"></template>
  <template x-route="/users/:id"></template>
</div>
```

## Segment Types

Pinecone Router supports seven segment types for flexible route matching:

### Literal Segments

Matches exact path segments:

```html
<!-- Matches: /about, /about/ -->
<!-- Does not match: /contact, /about-us -->
<template x-route="/about"></template>

<!-- Matches: /users/settings -->
<!-- Does not match: /users/profile, /settings -->
<template x-route="/users/settings"></template>
```

### Named Parameters

Captures a single path segment into a named parameter:

```html
<!-- Matches: /john, /123, /any-single-segment -->
<!-- Does not match: /john/doe, / -->
<template x-route="/user/:name" x-template>
  <h1>User: <span x-text="$params.name"></span></h1>
</template>
```

Access parameters via:
- `$params.name` in Alpine templates
- `context.params.name` in handlers
- `PineconeRouter.context.params.name` in JavaScript

### Optional Parameters

Matches routes with or without the parameter:

```html
<!-- Matches: /profile, /profile/john -->
<!-- Does not match: /profile/john/settings -->
<template x-route="/profile/:name?" x-template>
  <h1>
    <span x-text="$params.name ? 'User: ' + $params.name : 'Public Profile'"></span>
  </h1>
</template>
```

Multiple optional parameters:

```html
<!-- Matches: /settings, /settings/theme, /settings/theme/dark -->
<template x-route="/settings/:page?/:theme?"></template>
```

### Rest Parameters (One or More)

Captures one or more path segments:

```html
<!-- Matches: /files/docs, /files/docs/readme.txt, /files/a/b/c/d -->
<!-- Does not match: /files -->
<template x-route="/files/:path+" x-template>
  <h1>Files: <span x-text="$params.path"></span></h1>
</template>
```

The rest parameter captures remaining segments as a slash-separated string.

### Wildcard Parameters (Zero or More)

Captures zero or more path segments:

```html
<!-- Matches: /api, /api/users, /api/users/123/posts -->
<template x-route="/api/:rest*" x-template>
  <h1>API Path: <span x-text="$params.rest || 'root'"></span></h1>
</template>
```

### Suffix Matching

Matches segments with specific file extensions:

```html
<!-- Matches: /videos/avatar.mp4, /movies/trailer.mp4 -->
<!-- Does not match: /videos/avatar.mov, /videos/avatar -->
<template x-route="/videos/:title.mp4" x-template>
  <video src="/videos/<span x-text="$params.title"></span>.mp4"></video>
</template>
```

### Suffix Pattern Matching

Matches segments with multiple possible extensions using regex alternation:

```html
<!-- Matches: /videos/avatar.mp4, /videos/trailer.mov -->
<!-- Does not match: /videos/avatar.avi, /videos/avatar -->
<template x-route="/videos/:title.(mp4|mov)" x-template>
  <video src="/videos/<span x-text="$params.title"></span>.<span x-text="$params.ext"></span>">
  </video>
</template>
```

The extension is captured in a separate `ext` parameter.

## Matching Rules

### Case Insensitivity

All route matching is case-insensitive:

```html
<template x-route="/about"></template>
<!-- Matches: /about, /About, /ABOUT, /AbOuT -->
```

### Trailing Slash Normalization

Trailing slashes are automatically normalized:

```html
<template x-route="/contact"></template>
<!-- Matches: /contact, /contact/ -->
```

### Parameter Name Extraction

Parameters follow the pattern `:name` where `name` is any word character sequence:

| Pattern | Captured Param | Example Match | Param Value |
|---------|--------------|---------------|-------------|
| `/:id` | `id` | `/123` | `"123"` |
| `/:userId/posts` | `userId` | `/john/posts` | `"john"` |
| `/:category.:ext` | `category`, `ext` | `/docs.pdf` | `category="docs"`, `ext="pdf"` |

## Complex Route Patterns

### Multiple Parameters

```html
<!-- Matches: /users/john/posts/123 -->
<template x-route="/users/:username/posts/:postId" x-template>
  <h1>Post <span x-text="$params.postId"></span> by <span x-text="$params.username"></span></h1>
</template>
```

### Mixed Segment Types

```html
<!-- Matches: /api/v1/users, /api/v2/users, /api/v1/users/123/profile -->
<template x-route="/api/:version/users/:id?:rest*" x-template>
  <p>API v<span x-text="$params.version"></span>, User: <span x-text="$params.id || 'all'"></span></p>
</template>
```

### File Downloads with Patterns

```html
<!-- Matches: /downloads/report.pdf, /downloads/image.png -->
<template x-route="/downloads/:filename.(pdf|png|jpg)" x-handler="downloadHandler" x-template>
  <a :href="'/files/' + $params.filename + '.' + $params.ext">Download</a>
</template>
```

## Named Routes

Routes can have explicit names for reference:

### Declarative Named Routes

```html
<!-- Route name: 'homepage' -->
<template x-route:name="homepage" x-route="/" x-template>
  <h1>Home</h1>
</template>

<!-- Route name: 'user-profile' -->
<template x-route:name="user-profile" x-route="/:username" x-template>
  <h1>Profile: <span x-text="$params.username"></span></h1>
</template>
```

### Programmatic Named Routes

```javascript
window.PineconeRouter.add('/about', { 
  name: 'about-page',
  templates: ['/about.html']
})
```

### Accessing Route Names

```javascript
function handler(context, controller) {
  console.log('Current route name:', context.route.name)
  // Falls back to path if no name provided
}
```

## Notfound Route

The special `notfound` route handles unmatched paths:

```html
<!-- Override default 404 behavior -->
<template x-route="notfound" x-handler="notFoundHandler" x-template>
  <h1>404 - Page Not Found</h1>
  <p>The page you're looking for doesn't exist.</p>
  <a href="/">Go Home</a>
</template>
```

Default behavior logs an error to console. Always define a custom notfound route for production.

## Route Priority

Routes are matched in declaration order. More specific routes should be declared before general ones:

```html
<!-- Correct order -->
<template x-route="/users/admin"></template>        <!-- Specific: literal 'admin' -->
<template x-route="/users/:username"></template>    <!-- General: any username -->

<!-- Incorrect order - /users/admin would match as :username='admin' -->
<template x-route="/users/:username"></template>
<template x-route="/users/admin"></template>         <!-- Never reached -->
```

## Programmatic Route Matching

Use `PineconeRouter.match()` to check routes without navigation:

```javascript
// Check if a path matches any route
const result = window.PineconeRouter.match('/users/john')
if (result.route) {
  console.log('Matched route:', result.route.path)
  console.log('Parameters:', result.params)
  // { username: 'john' }
}
```

Returns `{ route: Route, params: Record<string, string> }` or `{ route: undefined, params: {} }`.

## Base Path Integration

When `Settings.basePath` is configured, it's automatically prepended to routes:

```javascript
// Configure base path
window.PineconeRouter.settings({ basePath: '/app' })
```

```html
<!-- Actually matches: /app/about -->
<template x-route="/about" x-template>
  <h1>About</h1>
</template>

<!-- Actually matches: /app/users/:username -->
<template x-route="/users/:username" x-template>
  <h1>User: <span x-text="$params.username"></span></h1>
</template>
```

This simplifies routing for applications mounted under subdirectories.

## Hash Routing Mode

When hash routing is enabled, routes match against the hash portion:

```javascript
window.PineconeRouter.settings({ hash: true })
```

```html
<!-- Matches: #/, #/about -->
<template x-route="/" x-template><h1>Home</h1></template>
<template x-route="/about" x-template><h1>About</h1></template>
```

URLs become `example.com/#/about` instead of `example.com/about`.

## Common Patterns

### RESTful API Routes

```html
<!-- GET /api/users -->
<template x-route="/api/users" x-handler="fetchUsers"></template>

<!-- GET /api/users/:id -->
<template x-route="/api/users/:id" x-handler="fetchUser"></template>

<!-- GET /api/users/:id/posts -->
<template x-route="/api/users/:userId/posts" x-handler="fetchUserPosts"></template>

<!-- GET /api/users/:id/posts/:postId -->
<template x-route="/api/users/:userId/posts/:postId" x-handler="fetchUserPost"></template>
```

### Blog with Categories

```html
<!-- Blog home -->
<template x-route="/blog" x-template><h1>All Posts</h1></template>

<!-- Category listing -->
<template x-route="/blog/:category" x-template>
  <h1>Category: <span x-text="$params.category"></span></h1>
</template>

<!-- Individual post -->
<template x-route="/blog/:category/:slug" x-template>
  <h1><span x-text="$params.slug"></span></h1>
  <p>Category: <span x-text="$params.category"></span></p>
</template>

<!-- Post with year/month archive -->
<template x-route="/blog/:year/:month/:slug" x-template>
  <article x-data="post(<span x-text="$params.slug"></span>)">
    <h1><span x-text="title"></span></h1>
    <time x-text="$params.year + '-' + $params.month"></time>
  </article>
</template>
```

### File Browser

```html
<!-- Root directory -->
<template x-route="/files" x-template><h1>File Browser</h1></template>

<!-- Navigate through directories -->
<template x-route="/files/:path+" x-template>
  <nav>
    <ol breadcrumbs x-text="$params.path"></ol>
  </nav>
  <div file-list x-data="files('$params.path')"></div>
</template>

<!-- View specific file -->
<template x-route="/files/:path+/view/:filename.(pdf|png|jpg|txt)" x-template>
  <file-viewer :file="$params.filename" :ext="$params.ext"></file-viewer>
</template>
```

### Multi-tenant Application

```html
<!-- Tenant-specific routes -->
<template x-route="/:tenant/dashboard" x-handler="checkTenantAuth" x-template>
  <dashboard :tenant="$params.tenant"></dashboard>
</template>

<template x-route="/:tenant/settings/:page?" x-handler="checkTenantAuth" x-template>
  <settings :tenant="$params.tenant" :page="$params.page"></settings>
</template>

<!-- Shared routes (no tenant) -->
<template x-route="/login" x-template><login-form></login-form></template>
<template x-route="/register" x-template><register-form></register-form></template>
```

## Troubleshooting

### Route Not Matching

1. **Check segment count**: `/:name` matches exactly one segment, not `/john/doe`
2. **Verify order**: Specific routes before general ones
3. **Case sensitivity**: Matching is case-insensitive, but parameter access is case-sensitive
4. **Trailing slashes**: Both `/about` and `/about/` work identically

### Parameter Not Captured

1. **Correct syntax**: Use `:paramName` (colon prefix required)
2. **Valid names**: Parameter names must be word characters (`\w+`)
3. **Access method**: Use `$params.paramName` in templates, `context.params.paramName` in handlers

### Optional Parameter Issues

1. **Order matters**: Optional params should be at the end
2. **Multiple optionals**: Each adds another optional level
3. **Check undefined**: Optional params may be `undefined` if not matched

```javascript
function handler(context, controller) {
  const optionalParam = context.params.optional
  if (optionalParam === undefined) {
    // Handle missing parameter
  }
}
```

### Rest Parameter Edge Cases

1. **Minimum one segment**: `:path+` requires at least one segment
2. **Captures as string**: Multiple segments joined with `/`
3. **Use wildcard for zero-or-more**: `:path*` matches empty paths

## TypeScript Types

```typescript
import type { Route, MatchResult } from 'pinecone-router'

// Route matching result
const result: MatchResult = {
  username: 'john',
  postId: '123'
}

// Route object
const route: Route = {
  path: '/users/:username/posts/:postId',
  pattern: RegExp,
  name: 'user-post',
  handlers: [],
  templates: [],
  match(path: string): MatchResult
}
```

## Migration from v6 to v7

### Parameter Access Changes

**v6:**
```javascript
function handler(context) {
  const name = context.params.name
}
```

**v7 (same, but context also includes route object):**
```javascript
function handler(context, controller) {
  const name = context.params.name
  const routePath = context.route.path
}
```

### Inline Template Syntax

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

See the upgrade guide for complete migration details.
