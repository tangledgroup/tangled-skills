---
name: solid-meta-0-29-0
description: Manages document head tags in SolidJS applications with @solidjs/meta v0.29, providing SSR-ready Document Head management including Title, Meta, Link, Style, Base, and Stylesheet components with MetaProvider. Use when building SolidJS applications requiring dynamic head tag control, SEO meta tags, or managing document title/stylesheets across routes.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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

Asynchronous SSR-ready Document Head management for SolidJS. Based on [react-head](https://github.com/tizmagik/react-head), it allows defining `document.head` tags anywhere in the component hierarchy — similar to react-helmet but built for SolidJS's fine-grained reactivity model.

Provides six head tag components (`Title`, `Meta`, `Link`, `Style`, `Base`, `Stylesheet`) and a single context provider (`MetaProvider`). On the server, tags are collected via Solid's `useAssets` API and injected into `<head>`. On the client, server-generated tags (marked with `data-sm`) are removed in favor of client-rendered tags.

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

`<title>` and `<meta>` are "cascading" — only the last instance with a matching key is rendered. The key for `<title>` is just the tag name. For `<meta>`, the key is derived from `name` or `property` attributes. Deeper components override shallower ones, enabling per-route overrides.

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

On the server, tags are collected and serialized via `useAssets` with `data-sm` markers. On the client, during hydration, `MetaProvider` removes all `[data-sm]` elements from `<head>` before rendering client-side tags, preventing duplicates.

## Usage Examples

### Basic Client-Side Setup

```tsx
import { MetaProvider, Title, Link, Meta } from "@solidjs/meta";

const App = () => (
  <MetaProvider>
    <Title>Title of page</Title>
    <Link rel="canonical" href="http://solidjs.com/" />
    <Meta name="description" content="A SolidJS application" />
    <div class="Home">{/* page content */}</div>
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
```

### Dynamic Title with Signals

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
      <Show when={visible()}><Title>Dynamic</Title></Show>
      <button onClick={() => setVisible(v => !v)}>Toggle</button>
    </>
  );
}
```

### Server-Side Rendering Setup

For custom SSR (non-SolidStart), wrap with `<MetaProvider>` and use `getAssets`:

```tsx
import { renderToString, getAssets } from "solid-js/web";
import { MetaProvider } from "@solidjs/meta";
import App from "./App";

const app = renderToString(() => (
  <MetaProvider><App /></MetaProvider>
));

res.send(`<!doctype html><html><head>${getAssets()}</head><body><div id="root">${app}</div></body></html>`);
```

If you render `<head>` using SolidJS JSX on the server, tags are injected automatically without `getAssets`.

### Open Graph and Social Meta Tags

```tsx
<Meta property="og:title" content="My Page Title" />
<Meta property="og:type" content="website" />
<Meta property="og:image" content="https://example.com/og-image.png" />
<Meta name="twitter:card" content="summary_large_image" />
```

### Stylesheets and Inline Styles

```tsx
import { Link, Style, Stylesheet } from "@solidjs/meta";

<MetaProvider>
  <Stylesheet href="https://fonts.googleapis.com/css2?family=Inter" />
  <Link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <Style>{`body { margin: 0; font-family: Inter, sans-serif; }`}</Style>
</MetaProvider>
```

### Base Tag

```tsx
<MetaProvider>
  <Base href="/my-app/" />
</MetaProvider>
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
      <Show when={show()} fallback={<Comp2 />}><Comp1 /></Show>
    </MetaProvider>
  );
}
```

## Advanced Topics

**Component API**: Full reference for all components, context, hooks, and types → [Component API](reference/01-component-api.md)

**SSR Patterns**: Cascading internals, XSS protection, hydration behavior, Googlebot compatibility, performance, behavioral guidelines → [SSR Patterns](reference/02-ssr-patterns.md)
