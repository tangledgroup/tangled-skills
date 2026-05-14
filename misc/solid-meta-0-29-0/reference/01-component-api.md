# Component API Reference

## Contents
- Components
- Context and Hooks
- Types

## Components

**`<MetaProvider>`** — Context provider (required). Wraps the application or router root. All head tag components must be descendants of a `MetaProvider`. Renders its children unchanged; manages head tag state through context.

**`<Title>`** — Renders `<title>` in document head. Accepts `JSX.HTMLAttributes<HTMLTitleElement>`. Children are escaped to prevent XSS. Only one title is visible at a time (last wins by cascade order).

**`<Meta>`** — Renders `<meta>` in document head. Accepts `JSX.MetaHTMLAttributes<HTMLMetaElement>`. Supports `name`, `property`, `http-equiv`, `content`, `charset`, `media` attributes. Tags with matching `name` or `property` cascade (last wins).

**`<Link>`** — Renders `<link>` in document head. Accepts `JSX.LinkHTMLAttributes<HTMLLinkElement>`. Non-cascading — all instances render. Used for stylesheets, favicons, preconnect hints, canonical URLs.

**`<Style>`** — Renders `<style>` in document head. Accepts `JSX.StyleHTMLAttributes<HTMLStyleElement>`. Children are rendered as-is (not escaped). Non-cascading — all instances render.

**`<Base>`** — Renders `<base>` in document head. Accepts `JSX.BaseHTMLAttributes<HTMLBaseElement>`. Non-cascading. Sets the base URL for all relative links.

**`<Stylesheet>`** — Convenience wrapper around `<Link rel="stylesheet" {...props} />`. Accepts `Omit<JSX.LinkHTMLAttributes<HTMLLinkElement>, "rel">`. The `rel="stylesheet"` is set automatically.

## Context and Hooks

**`MetaContext`** — SolidJS context object (`createContext<MetaContextType>()`). Exported for advanced use cases. Contains:

- `addTag(tag: TagDescription): number` — Register a head tag
- `removeTag(tag: TagDescription, index: number): void` — Unregister a head tag

**`useHead(tagDesc: TagDescription)`** — Low-level hook for custom head tag components. Manages the lifecycle (add on mount, remove on cleanup) through `createRenderEffect` and `onCleanup`. Throws if called outside `MetaProvider`.

```tsx
import { useHead, createUniqueId } from "@solidjs/meta";

function CustomHead() {
  useHead({
    tag: "meta",
    props: { name: "custom", content: "value" },
    id: createUniqueId(),
  });
  return null;
}
```

## Types

**`TagDescription`** — Internal interface for head tag descriptions:

```ts
interface TagDescription {
  tag: string;           // HTML tag name: "title", "meta", "link", etc.
  props: Record<string, unknown>;  // HTML attributes
  setting?: { close?: boolean; escape?: boolean };
  id: string;            // Unique identifier (use createUniqueId())
  name?: string;         // For cascading key derivation
  ref?: Element;         // DOM element reference (internal)
}
```

**`MetaContextType`** — The context value type:

```ts
interface MetaContextType {
  addTag: (tag: TagDescription) => number;
  removeTag: (tag: TagDescription, index: number): void;
}
```
