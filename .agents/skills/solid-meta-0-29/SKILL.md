---
name: solid-meta-0-29
description: A skill for managing document head tags in SolidJS applications with @solidjs/meta v0.29, providing asynchronous SSR-ready Document Head management including Title, Meta, Link, Style, Base, and Stylesheet components with MetaProvider context.
version: "0.29.7"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - solidjs
  - meta-tags
  - ssr
  - document-head
  - seo
  - server-side-rendering
category: development
required_environment_variables: []

external_references:
  - https://github.com/solidjs/solid/tree/main/packages/dom
  - https://www.npmjs.com/package/@solidjs/meta
---

# Solid Meta 0.29


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for managing document head tags in SolidJS applications with @solidjs/meta v0.29, providing asynchronous SSR-ready Document Head management including Title, Meta, Link, Style, Base, and Stylesheet components with MetaProvider context.

Solid Meta is an asynchronous SSR-ready Document Head management library for SolidJS applications. It allows you to define `document.head` tags at any level of your component hierarchy, making it easy to manage contextual metadata like titles, meta tags, stylesheets, and links throughout your application.

Based on [React Head](https://github.com/tizmagik/react-head), this library has no dependencies and seamlessly integrates with SolidJS's asynchronous rendering model.

## When to Use

- Managing SEO metadata (title, description, Open Graph tags) in SolidJS applications
- Implementing server-side rendering (SSR) with dynamic head tags
- Adding conditional meta tags based on component state or route
- Managing stylesheets and favicon links across pages
- Building SPAs that need to update document head on navigation
- Working with SolidStart projects requiring meta tag management

## Setup

### Installation

```bash
npm i @solidjs/meta
# or
pnpm add @solidjs/meta
# or
yarn add @solidjs/meta
```

**Version compatibility:**
- Solid 1.8.4+: Use `@solidjs/meta` v0.29.x (current)
- Solid 1.0: Use `@solidjs/meta` v0.27.x or greater
- Solid 0.x: Use `@solidjs/meta` v0.26.x

### Core Components

The library exports the following components:

| Component | Purpose | Element Type |
|-----------|---------|--------------|
| `<MetaProvider />` | Context provider (required wrapper) | - |
| `<Title />` | Document title | `<title>` |
| `<Meta />` | Meta tags | `<meta>` |
| `<Link />` | Link tags (stylesheets, icons) | `<link>` |
| `<Style />` | Inline styles | `<style>` |
| `<Base />` | Base URL | `<base>` |
| `<Stylesheet />` | Stylesheet link helper | `<link rel="stylesheet">` |

See [Component API Reference](references/01-component-api.md) for detailed usage.

## Quick Start

### SolidStart Setup (Recommended)

Wrap your app with `<MetaProvider />` inside the `root` of the `<Router />` component:

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
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

### Server-Side Rendering Setup

For custom SSR setups, wrap your app with `<MetaProvider />` and use `getAssets()` from `solid-js/web`:

```tsx
// entry-server.tsx
import { renderToString, getAssets } from 'solid-js/web';
import { MetaProvider } from '@solidjs/meta';
import App from './App';

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

### Client-Side Usage

Use head tag components anywhere in your component tree:

```tsx
import { MetaProvider, Title, Link, Meta } from '@solidjs/meta';

const Page = () => (
  <MetaProvider>
    <div>
      <Title>My Page Title</Title>
      <Meta name="description" content="Page description" />
      <Link rel="canonical" href="https://example.com/page" />
      {/* ... page content */}
    </div>
  </MetaProvider>
);
```

See [Common Patterns](references/02-common-patterns.md) for real-world usage examples.

## Reference Files

- [`references/01-component-api.md`](references/01-component-api.md) - Complete API reference for all components and props
- [`references/02-common-patterns.md`](references/02-common-patterns.md) - Common patterns: dynamic titles, conditional meta tags, theme switching
- [`references/03-server-rendering.md`](references/03-server-rendering.md) - SSR setup, hydration, and SolidStart integration
- [`references/04-troubleshooting.md`](references/04-troubleshooting.md) - Common issues, errors, and debugging tips

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/solid-meta-0-29/`). All paths are relative to this directory.

## How It Works

1. **Provider Setup**: Wrap your app with `<MetaProvider />` to establish context
2. **Tag Injection**: Render head tag components (`<Title />`, `<Meta />`, etc.) anywhere in your component tree
3. **Server Collection**: During SSR, tags are collected and injected via `getAssets()` or automatic rendering
4. **Client Hydration**: On the client, server-generated tags (marked with `data-sm` attribute) are removed and replaced with client-rendered tags
5. **SPA Navigation**: For SPAs, subsequent page loads update head tags as components mount/unmount

### Cascading Behavior

Certain tags have special "cascading" behavior where only the last instance is rendered:

- `<Title />`: Only the last title in the tree is shown
- `<Meta />`: Meta tags with the same `name` or `property` attribute cascade (last one wins)
- Other tags (`<Link />`, `<Style />`, `<Base />`) are all rendered

See [Component API Reference](references/01-component-api.md) for detailed behavior.

## Troubleshooting

### Common Issues

**Error: `<MetaProvider /> should be in the tree`**
- Ensure your component tree is wrapped with `<MetaProvider />`
- Check that you're importing from `@solidjs/meta`, not another package

**Title tags not updating**
- Only one `<Title />` can be active at a time (last one wins)
- Avoid adding normal `<title>` tags in server files as they override `@solidjs/meta`

**Meta tags duplicating**
- Meta tags with the same `name` or `property` cascade by design
- Add additional attributes (like `media`) to create distinct tags

**SSR hydration mismatch**
- Ensure `getAssets()` is called in your server HTML template
- Don't manually add `<title>` tags in server entry files

See [Troubleshooting Guide](references/04-troubleshooting.md) for more solutions.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
