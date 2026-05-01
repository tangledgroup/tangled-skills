# Cascading and SSR Internals

## How Cascading Works Internally

Cascading uses a `Map` keyed by tag name + serialized allowed properties. For `<title>`, the key is just `"title"` (no properties considered). For `<meta>`, the key includes `name` or `property` (normalized — `property` maps to `name`). When a new cascading tag is added, it pushes onto an instances array and removes the previous instance's DOM element. When removed, it restores the previous instance.

Non-cascading tags (`link`, `style`, `base`) are simply added/removed from `<head>` without tracking — all coexist.

## XSS Protection

`<Title>` children are escaped using Solid's `escape()` function. Attribute values in SSR output are also escaped. This prevents injection attacks through title or meta content:

```tsx
// Renders safely: <title>Hello&lt;/title&gt;...</title>
<Title>{'Hello</title><script>alert("xss")</script><title> World'}</Title>
```

## Hydration Behavior

During SSR, each tag gets a `data-sm="<id>"` attribute. On the client, `MetaProvider`'s initialization queries all `[data-sm]` elements and removes them from `<head>` before rendering client-side replacements. This ensures no duplicate tags after hydration.

The check `!sharedConfig.context` determines if we're in hydration mode — when truthy, SSR tags are present and should be cleaned up.

## Googlebot Compatibility

The library uses `Array.prototype.forEach.call()` instead of `NodeList.forEach` for removing SSR tags, because Googlebot's DOM implementation does not support `NodeList.prototype.forEach`.

## Performance Characteristics

- Tags use `createRenderEffect` for reactive updates — only re-render when tracked signals change
- DOM elements are reused when possible (element with matching `data-sm` id is repurposed)
- `spread()` from `solid-js/web` applies props efficiently with fine-grained updates
- No global state — each `MetaProvider` instance maintains its own tag registry

## v0.29.4 Internal Changes

### ParentNode Safety Check

Tag cleanup now checks `lastVisited.ref.parentNode` before attempting removal, preventing errors when the element has already been detached from the DOM tree.

### Array Children Fix

Children that arrive as arrays are now joined with an empty string (`children.join("")`) instead of relying on JavaScript's default comma-separated concatenation. This fixes edge cases where title content could render with unwanted commas.
