---
name: solid-meta-0-29
description: Manages document head tags in SolidJS applications with @solidjs/meta v0.29, providing asynchronous SSR-ready Document Head management including Title, Meta, Link, Style, Base, and Stylesheet components with MetaProvider context. Use when building SolidJS applications that require dynamic `<head>` tag control, SEO meta tags, server-side rendered head content, or managing document title/stylesheets across routes in a SolidJS SPA or SSR setup.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.29.0"
tags:
  - solidjs
  - meta-tags
  - document-head
  - ssr
  - seo
category: frontend
external_references:
  - https://github.com/solidjs/solid-meta
  - https://www.npmjs.com/package/@solidjs/meta
---

# @solidjs/meta v0.29

## Overview

Asynchronous SSR-ready Document Head management for SolidJS. Based on [react-head](https://github.com/tizmagik/react-head), it allows you to define `document.head` tags anywhere in your component hierarchy — similar to react-helmet but built for SolidJS's fine-grained reactivity model.

The library provides six head tag components (`Title`, `Meta`, `Link`, `Style`, `Base`, `Stylesheet`) and a single context provider (`MetaProvider`). On the server, tags are collected via Solid's `useAssets` API and injected into the HTML `<head>`. On the client, server-generated tags (marked with `data-sm` attributes) are removed in favor of client-rendered tags so SPAs work correctly across navigation.

## When to Use

- Setting dynamic page titles in a SolidJS SPA or SSR application
- Managing SEO meta tags (`og:`, `twitter:`, description, canonical URLs)
- Injecting stylesheets or inline `<style>` blocks conditionally
- Building SolidStart applications with per-route head management
- Replacing react-helmet patterns when migrating to SolidJS
- Any scenario where head tag information is only available deep in the component tree

## Installation / Setup

```bash
npm i @solidjs/meta
```

Requires `solid-js >= 1.8.4` as a peer dependency. Zero additional dependencies.

## Core Concepts

### MetaProvider Context

All head tag components require `<MetaProvider>` somewhere above them in the component tree. It creates a `MetaContext` with `addTag` and `removeTag` operations. Without it, any head component throws: `<MetaProvider /> should be in the tree`.

```tsx
import { MetaProvider, Title } from "@solidjs/meta";

function App() {
  return (
    <MetaProvider>
      <Title>My App</Title>
      {/* rest of app */}
    </MetaProvider>
  );
}
```

### Cascading Tags

`<title>` and `<meta>` are "cascading" — only the last instance with a matching key is rendered. The key for `<title>` is just the tag name (so only one title exists). For `<meta>`, the key is derived from `name` or `property` attributes. This means deeper components in the tree override shallower ones, enabling per-route overrides.

```tsx
// Title 3 wins — only <title>Title 3</title> appears in <head>
<MetaProvider>
  <Title>Title 1</Title>
  <Title>Title 2</Title>
  <Title>Title 3</Title>
</MetaProvider>
```

For `<meta>`, tags with the same `name` or `property` cascade (last wins), but tags with different attributes coexist:

```tsx
// Both render — different `media` values create distinct keys
<Meta name="theme-color" media="(prefers-color-scheme: light)" content="#fff" />
<Meta name="theme-color" media="(prefers-color-scheme: dark)" content="#000" />
```

### Non-Cascading Tags

`<link>`, `<style>`, `<base>` are non-cascading — all instances render. Multiple `<Link>` tags for different stylesheets or favicons all appear in `<head>`.

### SSR Hydration

On the server, tags are collected into an internal array and serialized via `useAssets` with `data-sm` markers. On the client, during hydration, `MetaProvider` removes all `[data-sm]` elements from `<head>` before rendering client-side tags. This prevents duplicate head tags after hydration.

## Usage Examples

### Basic Client-Side Setup

```tsx
import { MetaProvider, Title, Link, Meta } from "@solidjs/meta";

const App = () => (
  <MetaProvider>
    <Title>Title of page</Title>
    <Link rel="canonical" href="http://solidjs.com/" />
    <Meta name="description" content="A SolidJS application" />
    <div class="Home">
      {/* page content */}
    </div>
  </MetaProvider>
);
```

### SolidStart Setup

Wrap the app with `<MetaProvider>` inside the `root` prop of `<Router>`:

```tsx
// app.tsx
import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start";
import { Suspense } from "solid-js";

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>SolidStart - Basic</Title>
          <a href="/">Index</a>
          <a href="/about">About</a>
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

> **Important:** Do not add any normal `<title>` tags in server files (e.g., `entry-server.tsx`), as they would override `@solidjs/meta`'s functionality.

### Per-Route Meta Tags

Each route component can define its own head tags. Deeper tags cascade over shallower ones:

```tsx
// routes/index.tsx
import { Title, Meta } from "@solidjs/meta";

export default function Index() {
  return (
    <>
      <Title>Home - My App</Title>
      <Meta name="description" content="The home page" />
      <h1>Welcome</h1>
    </>
  );
}

// routes/about.tsx
import { Title, Meta } from "@solidjs/meta";

export default function About() {
  return (
    <>
      <Title>About - My App</Title>
      <Meta name="description" content="About this application" />
      <h1>About Us</h1>
    </>
  );
}
```

### Dynamic Title with Signals

SolidJS reactivity integrates naturally — titles update when signals change:

```tsx
import { createSignal } from "solid-js";
import { Title } from "@solidjs/meta";

function Page() {
  const [count, setCount] = createSignal(0);
  return (
    <>
      <Title>Counter: {count()}</Title>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </>
  );
}
```

### Conditional Meta with Show

```tsx
import { createSignal } from "solid-js";
import { Show } from "solid-js/web";
import { Title } from "@solidjs/meta";

function Page() {
  const [visible, setVisible] = createSignal(false);
  return (
    <>
      <Title>Static</Title>
      <Show when={visible()}>
        <Title>Dynamic</Title>
      </Show>
      <button onClick={() => setVisible(v => !v)}>Toggle</button>
    </>
  );
}
```

When `visible` is true, "Dynamic" cascades over "Static". When false, "Static" reappears.

### Server-Side Rendering Setup

For custom SSR (non-SolidStart), wrap the app with `<MetaProvider>` and use `getAssets`:

```tsx
import { renderToString, getAssets } from "solid-js/web";
import { MetaProvider } from "@solidjs/meta";
import App from "./App";

const app = renderToString(() => (
  <MetaProvider>
    <App />
  </MetaProvider>
));

res.send(`
  <!doctype html>
  <html>
    <head>
      ${getAssets()}
    </head>
    <body>
      <div id="root">${app}</div>
    </body>
  </html>
`);
```

If you render `<head>` using SolidJS JSX on the server (e.g., a `<Head>` component), tags are injected automatically without `getAssets`.

### Open Graph and Social Meta Tags

Use `property` attribute for Open Graph tags (treated equivalently to `name` for cascading):

```tsx
<Meta property="og:title" content="My Page Title" />
<Meta property="og:type" content="website" />
<Meta property="og:image" content="https://example.com/og-image.png" />
<Meta name="twitter:card" content="summary_large_image" />
```

### Stylesheets and Inline Styles

```tsx
import { Link, Style, Stylesheet } from "@solidjs/meta";

function App() {
  return (
    <MetaProvider>
      {/* Stylesheet is a convenience wrapper: <Link rel="stylesheet" {...props} /> */}
      <Stylesheet href="https://fonts.googleapis.com/css2?family=Inter" />

      {/* Full control with Link */}
      <Link rel="icon" href="/favicon.ico" type="image/x-icon" />
      <Link rel="preconnect" href="https://fonts.gstatic.com" />

      {/* Inline styles */}
      <Style>{`
        body { margin: 0; font-family: Inter, sans-serif; }
      `}</Style>
    </MetaProvider>
  );
}
```

### Base Tag

```tsx
import { Base } from "@solidjs/meta";

function App() {
  return (
    <MetaProvider>
      <Base href="/my-app/" />
      {/* all relative URLs resolve against /my-app/ */}
    </MetaProvider>
  );
}
```

### Lazy-Loaded Route Components

Head tags in lazy-loaded components work correctly with Solid's async loading:

```tsx
import { lazy } from "solid-js";
import { Show } from "solid-js/web";
import { MetaProvider, Title } from "@solidjs/meta";

const Comp1 = lazy(async () => import("./Comp1"));
const Comp2 = lazy(async () => import("./Comp2"));

function App() {
  const [show, setShow] = createSignal(true);
  return (
    <MetaProvider>
      <Title>Default</Title>
      <Show when={show()} fallback={<Comp2 />}>
        <Comp1 />
      </Show>
    </MetaProvider>
  );
}
```

Each lazy component can define its own `<Title>` and `<Meta>` that cascade properly.

## API Reference

### Components

**`<MetaProvider>`** — Context provider (required). Wraps the application or router root. All head tag components must be descendants of a `MetaProvider`. Renders its children unchanged; manages head tag state through context.

**`<Title>`** — Renders `<title>` in document head. Accepts `JSX.HTMLAttributes<HTMLTitleElement>`. Children are escaped to prevent XSS. Only one title is visible at a time (last wins by cascade order).

**`<Meta>`** — Renders `<meta>` in document head. Accepts `JSX.MetaHTMLAttributes<HTMLMetaElement>`. Supports `name`, `property`, `http-equiv`, `content`, `charset`, `media` attributes. Tags with matching `name` or `property` cascade (last wins).

**`<Link>`** — Renders `<link>` in document head. Accepts `JSX.LinkHTMLAttributes<HTMLLinkElement>`. Non-cascading — all instances render. Used for stylesheets, favicons, preconnect hints, canonical URLs.

**`<Style>`** — Renders `<style>` in document head. Accepts `JSX.StyleHTMLAttributes<HTMLStyleElement>`. Children are rendered as-is (not escaped). Non-cascading — all instances render.

**`<Base>`** — Renders `<base>` in document head. Accepts `JSX.BaseHTMLAttributes<HTMLBaseElement>`. Non-cascading. Sets the base URL for all relative links.

**`<Stylesheet>`** — Convenience wrapper around `<Link rel="stylesheet" {...props} />`. Accepts `Omit<JSX.LinkHTMLAttributes<HTMLLinkElement>, "rel">`. The `rel="stylesheet"` is set automatically.

### Context and Hooks

**`MetaContext`** — SolidJS context object (`createContext<MetaContextType>()`). Exported for advanced use cases. Contains:

- `addTag(tag: TagDescription): number` — Register a head tag
- `removeTag(tag: TagDescription, index: number): void` — Unregister a head tag

**`useHead(tagDesc: TagDescription)`** — Low-level hook for custom head tag components. Manages the lifecycle (add on mount, remove on cleanup) through `createRenderEffect` and `onCleanup`. Throws if called outside `MetaProvider`.

```tsx
import { useHead, createUniqueId } from "@solidjs/meta";
import { createMemo } from "solid-js";

function CustomHead() {
  useHead({
    tag: "meta",
    props: { name: "custom", content: "value" },
    id: createUniqueId(),
  });
  return null;
}
```

### Types

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

## Advanced Topics

### How Cascading Works Internally

Cascading uses a `Map` keyed by tag name + serialized allowed properties. For `<title>`, the key is just `"title"` (no properties considered). For `<meta>`, the key includes `name` or `property` (normalized — `property` maps to `name`). When a new cascading tag is added, it pushes onto an instances array and removes the previous instance's DOM element. When removed, it restores the previous instance.

Non-cascading tags (`link`, `style`, `base`) are simply added/removed from `<head>` without tracking — all coexist.

### XSS Protection

`<Title>` children are escaped using Solid's `escape()` function. Attribute values in SSR output are also escaped. This prevents injection attacks through title or meta content:

```tsx
// Renders safely: <title>Hello&lt;/title&gt;...</title>
<Title>{'Hello</title><script>alert("xss")</script><title> World'}</Title>
```

### Hydration Behavior

During SSR, each tag gets a `data-sm="<id>"` attribute. On the client, `MetaProvider`'s initialization queries all `[data-sm]` elements and removes them from `<head>` before rendering client-side replacements. This ensures no duplicate tags after hydration.

The check `!sharedConfig.context` determines if we're in hydration mode — when truthy, SSR tags are present and should be cleaned up.

### Googlebot Compatibility

The library uses `Array.prototype.forEach.call()` instead of `NodeList.forEach` for removing SSR tags, because Googlebot's DOM implementation does not support `NodeList.prototype.forEach`.

### Performance Characteristics

- Tags use `createRenderEffect` for reactive updates — only re-render when tracked signals change
- DOM elements are reused when possible (element with matching `data-sm` id is repurposed)
- `spread()` from `solid-js/web` applies props efficiently with fine-grained updates
- No global state — each `MetaProvider` instance maintains its own tag registry

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
