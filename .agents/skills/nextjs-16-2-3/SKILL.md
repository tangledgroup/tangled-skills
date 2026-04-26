---
name: nextjs-16-2-3
description: A skill for building production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router support, server/client components, routing, data fetching, caching, API routes, and deployment capabilities. Use when creating modern web applications requiring SSR/SSG/ISR, optimal performance, SEO-friendly rendering, TypeScript support, and full-stack JavaScript development with built-in optimizations for production.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "16.2.3"
tags:
  - react
  - nextjs
  - ssr
  - ssg
  - fullstack
  - typescript
  - app-router
  - server-components
category: framework
external_references:
  - https://nextjs.org/docs
  - https://github.com/vercel/next.js
---

# Next.js 16.2.3

## Overview

Next.js is a React framework for building full-stack web applications. You use React Components to build user interfaces, and Next.js for additional features and optimizations. It automatically configures lower-level tools like bundlers and compilers so you can focus on building your product and shipping quickly.

Whether you're an individual developer or part of a larger team, Next.js helps you build interactive, dynamic, and fast React applications. Used by some of the world's largest companies, it extends the latest React features and integrates powerful Rust-based JavaScript tooling for the fastest builds.

## When to Use

- Building full-stack web applications with React
- Projects requiring server-side rendering (SSR) or static site generation (SSG)
- Applications needing SEO-friendly pages with automatic metadata management
- APIs and backend-for-frontend patterns using Route Handlers
- Projects benefiting from file-system based routing
- Applications requiring image optimization, font loading, and CSS handling out of the box
- Deployments to Vercel, Node.js servers, Docker containers, or edge platforms

## Core Concepts

Next.js 16 has two routers:

- **App Router** — The newer router supporting React Server Components, streaming, and the `app/` directory convention. Uses React canary releases built-in (including all stable React 19 changes).
- **Pages Router** — The original router, still supported and being improved. Uses the React version from your `package.json`.

Key architectural pillars:

- **File-system routing** — Folders and files define routes
- **Server Components** — Fetch data and render UI on the server by default
- **Client Components** — Add interactivity with `"use client"` directive
- **Caching** — Built-in data caching with `use cache` directive and Cache Components
- **Streaming** — Progressive rendering of uncached data via `<Suspense>`
- **Turbopack** — Rust-based incremental bundler built into Next.js

## Installation / Setup

Minimum Node.js version: 20.9+. Supported operating systems: macOS, Windows (including WSL), and Linux.

Supported browsers: Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+.

Create a new app with the CLI:

```bash
npx create-next-app@latest my-app --yes
cd my-app
npm run dev
```

The `--yes` flag skips prompts using defaults: TypeScript, Tailwind CSS, ESLint, App Router, and Turbopack. Without it, you can customize settings including linter choice (ESLint or Biome), React Compiler, `src/` directory, and import aliases.

For manual installation:

```bash
npm i next@latest react@latest react-dom@latest
```

Add scripts to `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

## Advanced Topics

**App Router Fundamentals**: Layouts, pages, navigation, and project structure → [App Router Fundamentals](reference/01-app-router-fundamentals.md)

**Server and Client Components**: React Server Components, Client Components, data fetching, and streaming → [Server and Client Components](reference/02-server-and-client-components.md)

**Routing**: Dynamic routes, parallel routes, intercepting routes, route groups, and proxy → [Routing](reference/03-routing.md)

**Data Caching and Revalidation**: Cache Components, `use cache`, `cacheLife`, `cacheTag`, and revalidation strategies → [Data Caching and Revalidation](reference/04-data-caching-and-revalidation.md)

**API and Backend**: Route Handlers, Server Actions, environment variables, and proxy configuration → [API and Backend](reference/05-api-and-backend.md)

**Metadata and SEO**: Static and dynamic metadata, OG images, sitemaps, and robots → [Metadata and SEO](reference/06-metadata-and-seo.md)

**Styling and Assets**: CSS, Tailwind CSS, Image optimization, and Font loading → [Styling and Assets](reference/07-styling-and-assets.md)

**Deployment**: Node.js servers, Docker, static export, adapters, and platform deployment → [Deployment](reference/08-deployment.md)
