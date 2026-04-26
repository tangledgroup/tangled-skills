# Navigation History

## Overview

Pinecone Router maintains an independent navigation history stack, separate from the browser's `history` API. It tracks all visited paths and provides back/forward navigation methods.

Access via:

- `$history` magic helper in Alpine templates
- `PineconeRouter.history` in JavaScript

## History Rules

The history stack excludes:

- **Duplicates**: Navigating to the current path does not create a new entry
- **Redirects**: If a handler redirects from `/old` to `/new`, only `/new` is recorded
- **Failed navigations**: Aborted handlers do not update history

When navigating back and then clicking a new link, all forward entries are trimmed before appending the new path (standard browser-like behavior).

## API

### `$history.entries`

Array of visited paths in order:

```html
<!-- Display navigation trail -->
<template x-for="path in $history.entries" :key="path">
  <span x-text="path"></span>
</template>
```

### `$history.index`

Current position in the history stack (zero-indexed):

```html
<span x-text="$history.index + ' of ' + ($history.entries.length - 1)"></span>
```

### `$history.back()`

Navigate to the previous path:

```html
<button @click="$history.back()">Back</button>
```

### `$history.forward()`

Navigate to the next path (after going back):

```html
<button @click="$history.forward()">Forward</button>
```

### `$history.canGoBack()` / `$history.canGoForward()`

Check if navigation is possible:

```html
<button :disabled="!$history.canGoBack()" @click="$history.back()">Back</button>
<button :disabled="!$history.canGoForward()" @click="$history.forward()">Forward</button>
```

### `$history.to(index)`

Navigate to a specific position in the history:

```javascript
$history.to(0)  // Go to first visited page
```

## Browser vs Pinecone History

Pinecone Router updates both the browser `history` API (via `pushState`) and its own internal stack. The built-in history can be used even when `Settings.pushState` is disabled, allowing navigation without URL changes:

```javascript
// Disable browser URL updates but keep internal history
PineconeRouter.settings({ pushState: false })

// Still use $history.back() / $history.forward()
```

## JavaScript Access

```javascript
const history = window.PineconeRouter.history

console.log(history.entries)   // ['/home', '/about', '/profile/42']
console.log(history.index)     // 2
history.back()                 // Navigate to /about
history.to(0)                  // Navigate to /home
```
