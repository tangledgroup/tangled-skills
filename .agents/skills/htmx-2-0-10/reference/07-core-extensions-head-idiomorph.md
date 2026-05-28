# Core Extensions: head-support and idiomorph

## head-support Extension

Provides merging of `<head>` tag content (styles, scripts, meta, title) in htmx responses. Essential for `hx-boost` full-page navigation patterns.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-head-support@2.0.5"></script>
<body hx-ext="head-support">
```

Or via npm: `npm install htmx-ext-head-support`

### Usage

Install on `<body>`. All responses containing a `<head>` tag are automatically processed.

```html
<body hx-ext="head-support">
  <a href="/page2" hx-boost="true">Navigate</a>
</body>
```

### Merge Behavior

**For boosted requests** (full page responses):
- `<title>` — replaced
- `<link rel="stylesheet">` — merged by `href` (new added, removed if absent in response)
- `<link>` (other) — merged by all attributes
- `<meta>` — merged by `name` or `property` attribute
- `<script>` — merged by `src` (new added, removed if absent)
- Other elements — replaced

**For non-boosted requests** (partial responses):
- `<title>` — replaced
- `<link>`, `<meta>`, `<script>` — appended (not removed)

### Example

Server returns full HTML:
```html
<html>
<head>
  <title>New Page Title</title>
  <link rel="stylesheet" href="/new-style.css" />
  <meta name="description" content="New description" />
</head>
<body>
  <div id="content">New content</div>
</body>
</html>
```

htmx extracts the `<head>` content and merges it, then swaps the body content.

---

## idiomorph Extension

DOM morphing algorithm that reuses existing DOM nodes when possible, producing smoother transitions than standard innerHTML/outerHTML swaps.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://unpkg.com/idiomorph@0.7.4/dist/idiomorph-ext.min.js"></script>
<body hx-ext="morph">
```

Or via npm: `npm install idiomorph`

### Swap Strategies

| Strategy | Description |
|----------|-------------|
| `morph` / `morph:outerHTML` | Morph the target element and its children |
| `morph:innerHTML` | Morph only inner children, leave target element untouched |

```html
<button hx-get="/example" hx-swap="morph">Morph Outer HTML</button>
<button hx-get="/example" hx-swap="morph:outerHTML">Same as morph</button>
<button hx-get="/example" hx-swap="morph:innerHTML">Morph Inner Only</button>
```

### When to Use Morph

- Preserving form input state during partial updates
- Smooth transitions where elements have the same ID but different content
- Reducing flicker compared to standard innerHTML swaps
- Maintaining focus on form fields across updates

### Configuration

Idiomorph accepts options via the swap style:

```html
<div hx-get="/data" hx-swap="morph:innerHTML"></div>
```

Morph preserves DOM nodes by matching on:
1. Element ID (primary key)
2. Element tag name + class list
3. Position within parent

This means event listeners, input values, and scroll positions are preserved when nodes are reused.

### Comparison with Standard Swaps

| Feature | innerHTML | morph |
|---------|-----------|-------|
| Node reuse | No (destroys and recreates) | Yes (reuses matching nodes) |
| Event listeners | Lost on replaced nodes | Preserved on reused nodes |
| Form values | Lost | Preserved on reused inputs |
| Scroll position | Lost | Preserved on reused elements |
| Performance | Fast for small DOM | Slightly slower, better UX |
