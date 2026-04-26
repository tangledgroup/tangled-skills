# Route Matching & Parameters

## Declaring Routes

Routes are declared with the `x-route` directive on `<template>` elements:

```html
<div x-data="app">
  <template x-route="/"></template>
  <template x-route="/about"></template>
  <template x-route="/users/:id"></template>
  <template x-route="notfound"></template>
</div>
```

Routes can also be [added programmatically](reference/06-programmatic-api.md) with `PineconeRouter.add()`.

## Segment Types

### Literal Segments

Match an exact path segment:

```html
<template x-route="/about"></template>
<!-- Matches: /about, /About (case-insensitive), /about/ (trailing slash normalized) -->
<!-- Does not match: /about-us, /contact -->
```

### Named Parameters (`:name`)

Match a single path segment and capture its value:

```html
<template x-route="/users/:id"></template>
<!-- Matches: /users/42, /users/john -->
<!-- Access: $params.id → "42" or "john" -->
<!-- Does not match: /users/, /users/42/profile -->
```

### Optional Parameters (`:name?`)

Match zero or one path segment:

```html
<template x-route="/profile/:name?"></template>
<!-- Matches: /profile, /profile/john -->
<!-- Access: $params.name → undefined or "john" -->
<!-- Does not match: /profile/john/settings -->
```

### Rest Parameters (`:name+`)

Match one or more path segments:

```html
<template x-route="/files/:path+"></template>
<!-- Matches: /files/docs, /files/docs/readme.txt, /files/a/b/c -->
<!-- Does not match: /files -->
```

### Wildcard Parameters (`:name*`)

Match zero or more path segments:

```html
<template x-route="/docs/:path*"></template>
<!-- Matches: /docs, /docs/guide, /docs/guide/intro.md -->
```

### Suffix Matching (`:name.ext`)

Match a segment with a specific file extension:

```html
<template x-route="/videos/:title.mp4"></template>
<!-- Matches: /videos/avatar.mp4 -->
<!-- Access: $params.title → "avatar" -->
<!-- Does not match: /videos/avatar.mov, /videos/avatar -->
```

### Suffix Pattern Matching (`:name.(ext1|ext2)`)

Match a segment with one of several file extensions:

```html
<template x-route="/videos/:title.(mp4|mov|webm)"></template>
<!-- Matches: /videos/trailer.mp4, /videos/clip.mov -->
<!-- Does not match: /videos/trailer.avi -->
```

## Accessing Parameters

Three ways to access route params:

1. **`$params` magic helper** — from within Alpine.js component templates:
   ```html
   <span x-text="$params.id"></span>
   ```

2. **`context.params`** — from within [handlers](reference/03-handlers.md):
   ```javascript
   handler(context, controller) {
     const id = context.params.id
   }
   ```

3. **`PineconeRouter.context.params`** — from anywhere in JavaScript:
   ```javascript
   const params = window.PineconeRouter.context.params
   ```

## Matching Behavior

- **Case-insensitive**: `/About` and `/about` match the same route.
- **Trailing slash normalized**: `/about` and `/about/` are equivalent.
- **First match wins**: Routes are checked in insertion order; the first matching route handles the request.
- **Query strings ignored**: Query parameters (`?foo=bar`) do not affect route matching. Access them via `window.location.search`.
- **Hash fragments ignored**: Hash fragments (`#section`) do not affect route matching unless hash routing is enabled.

## The `notfound` Route

A default `notfound` route exists automatically. Override it by declaring:

```html
<template x-route="notfound" x-template="/404.html"></template>
```

The `notfound` route is the only route key that can be updated without throwing a duplicate error when added programmatically.
