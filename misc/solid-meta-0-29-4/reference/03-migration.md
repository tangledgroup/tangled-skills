# Migration Guide (v0.29.0 → v0.29.4)

## Breaking Changes

### MetaProvider No Longer Accepts `tags` Prop

In v0.29.0, `MetaProvider` accepted an optional `tags?: Array<TagDescription>` prop for passing pre-collected server-side tags. This was removed in v0.29.4.

**Before (v0.29.0):**
```tsx
<MetaProvider tags={serverTags}>
  <App />
</MetaProvider>
```

**After (v0.29.4):**
```tsx
<MetaProvider>
  <App />
</MetaProvider>
```

Server-side tag collection is now handled internally without the `tags` prop.

### Removed `solid-js/web` Module Augmentation

The module augmentation for `RequestEvent.solidMeta` was removed from `solid-js/web`. If your code referenced `getRequestEvent().solidMeta`, update to use the standard SSR flow:

**Before (v0.29.0):**
```tsx
import { getRequestEvent } from "solid-js/web";
const event = getRequestEvent();
const metaContext = event?.solidMeta;
```

**After (v0.29.4):**
Use `useHead()` hook or the component API directly. The internal server provider is initialized automatically by `MetaProvider`.

## Bug Fixes

### Array Children Concatenation

Children passed as arrays are now joined with an empty string instead of comma-separated concatenation. This fixes edge cases where title content rendered with unwanted commas.

### ParentNode Safety Check

Tag cleanup now checks `parentNode` before attempting DOM removal, preventing errors when elements have already been detached.

## Behavioral Guidelines

### Think Before Coding
- Always wrap with `<MetaProvider>` before using any head components
- Remember that `<title>` and `<meta>` cascade (last wins), while `<link>`, `<style>`, `<base>` do not
- For SolidStart, place `MetaProvider` inside the router's `root` prop, not outside

### Simplicity First
- Use `<Stylesheet>` for simple stylesheet links instead of `<Link rel="stylesheet" .../>`
- Use `<Meta property="og:...">` for Open Graph tags — `property` is treated as `name` internally
- For per-route meta, just render components in the route — no special hooks needed

### Common Pitfalls
- Do not add `<title>` in server HTML templates — it overrides `@solidjs/meta`
- Without `MetaProvider`, all head components throw an error
- `<Meta name="x">` and `<Meta property="x">` are treated as the same key (both cascade against each other)
