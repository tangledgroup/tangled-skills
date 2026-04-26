# Templates

## Inline Templates

Add an empty `x-template` attribute to render the template element's children when the route matches. Content is inserted after the `<template>` tag (similar to `x-if` behavior):

```html
<template x-route="/" x-template>
  <h1>Home Page</h1>
  <p>Multiple root elements are supported.</p>
</template>
```

## External Templates

Specify one or more URLs to fetch HTML content from:

```html
<!-- Single template -->
<template x-route="/" x-template="/views/home.html"></template>

<!-- Multiple templates (fetched and concatenated) -->
<template x-route="/dashboard" x-template="['/views/header.html', '/views/body.html']"></template>
```

Templates are cached in memory after first load and cleared on page reload. Fetch failures dispatch a `pinecone:fetch-error` event on `document`.

## Template Modifiers

### `.target` — Render Into a Specific Element

Render template content inside an element by ID instead of after the `<template>` tag:

```html
<template x-route="/profile/:id" x-template.target.app="/views/profile.html"></template>
<div id="app"></div>
```

Set a global default target in [Settings](reference/05-settings.md) with `targetID`:

```javascript
PineconeRouter.settings({ targetID: 'app' })
```

### `.preload` — Preload After First Page Load

Fetch templates at low priority after the initial page renders, without waiting for the route to be matched:

```html
<template x-route="notfound" x-template.preload="/404.html"></template>
<template x-route="/profile/:id" x-template.preload.target.app="/profile.html"></template>
```

Enable globally in [Settings](reference/05-settings.md) with `preload: true`. Note: `.preload` cannot be combined with `.interpolate`.

### `.interpolate` — Route Params in Template URLs

Replace named params in template URLs with current route param values:

```html
<template x-route="/dynamic/:name" x-template.interpolate="/api/pages/:name.html"></template>
<!-- Visiting /dynamic/foo fetches /api/pages/foo.html -->
<!-- Visiting /dynamic/bar fetches /api/pages/bar.html -->
```

## Combining Modifiers

Modifiers can be chained in any order:

```html
<template x-route="/profile/:id" x-template.preload.target.app="/views/profile.html"></template>
```

## Embedded Scripts

External templates can include `<script>` tags that execute when the route is matched. The script has access to Alpine.js data and magic helpers:

```html
<!-- /views/hello.html -->
<div x-data="hello" x-effect="onParamChange">
  <h1>Dynamic Page</h1>
  <p x-text="message"></p>
</div>
<script>
  Alpine.data('hello', () => ({
    message: 'Hello',
    onParamChange() {
      // Runs when $params change on the same route
      if (this.$params.slug) {
        console.log('Slug changed to:', this.$params.slug)
      }
    },
  }))
</script>
```

Important behaviors:

- Templates do **not** re-render when only params change on the same route. `init()` runs once until the user navigates away and returns.
- Use `x-effect` or `$watch` to react to param changes within the same route.
- Multiple root elements and multiple `<script>` tags are supported in a single template file.

## The `x-run` Directive

Control when embedded scripts execute:

### `x-run.once` — Run Once Per Route

Execute the script only once per route visit, even if the route is revisited:

```html
<script x-run.once>
  // Runs once per route, useful for library initialization
  ChartJS.initialize()
</script>
```

Add an `id` to run once globally across all routes:

```html
<script x-run.once id="analytics-init">
  // Runs only once ever, even if included in multiple route templates
  Analytics.init()
</script>
```

### `x-run:on="condition"` — Conditional Execution

Run the script only when a condition evaluates to true:

```html
<script x-run:on="$router.context.route?.path === '/profile'">
  // Only runs on /profile route, even if template is shared
</script>
```

The condition has access to the Alpine.js data scope of both the template element and the target element.

### Combining Both

```html
<script x-run.once:on="$params.isAdmin">
  // Runs once only when the admin param is truthy
</script>
```

## Template Lifecycle

1. Route matches → handlers execute (if any)
2. Previous route's template content is hidden
3. Current route's template is shown (inline rendered or external fetched then rendered)
4. Embedded scripts execute (respecting `x-run` conditions)
5. `pinecone:end` event fires (after templates render, or immediately if no templates)

Templates remain visible while async handlers run — the previous page stays on screen during data loading rather than showing a blank state.
