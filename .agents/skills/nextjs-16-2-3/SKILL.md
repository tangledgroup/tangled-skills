---
name: nextjs-16-2-3
description: A skill for building production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router support, server/client components, routing, data fetching, caching, API routes, and deployment capabilities. Use when creating modern web applications requiring SSR/SSG/ISR, optimal performance, SEO-friendly rendering, TypeScript support, and full-stack JavaScript development with built-in optimizations for production.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - nextjs
  - react
  - web-development
  - ssr
  - ssg
  - fullstack
  - typescript
  - app-router
category: development
required_environment_variables: []
---

# Next.js 16.2.3


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for building production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router support, server/client components, routing, data fetching, caching, API routes, and deployment capabilities. Use when creating modern web applications requiring SSR/SSG/ISR, optimal performance, SEO-friendly rendering, TypeScript support, and full-stack JavaScript development with built-in optimizations for production.

Next.js is the React framework for production-ready web applications. It provides routing, rendering modes (SSR/SSG/ISR), data fetching, caching, API routes, and deployment tools out of the box. Next.js 16.2.3 includes the App Router (recommended) and Pages Router (legacy), with support for Server Components, Client Components, and full-stack development.

**Key capabilities:**
- App Router with file-based routing and nested layouts
- React Server Components (RSC) by default
- Multiple rendering modes: SSR, SSG, ISR, CSR
- Built-in data fetching and caching strategies
- API routes for backend functionality
- Image optimization and font optimization
- TypeScript support out of the box
- Zero-configuration deployment to Vercel or any host

## When to Use

- Building production React applications with optimal performance
- Creating SEO-friendly websites with server-side rendering
- Developing full-stack applications with API routes
- Needing hybrid static/dynamic content (ISR)
- Building SaaS platforms, e-commerce sites, or content-heavy apps
- Requiring TypeScript support and type safety
- Deploying to Vercel or any Node.js host
- Creating progressive web apps (PWAs)

## Setup

### System Requirements

- **Node.js:** 20.9 or higher
- **Operating Systems:** macOS, Windows (including WSL), Linux
- **Supported Browsers:** Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+

### Installation with create-next-app

**Quick start with recommended defaults:**

```bash
# Using npm
npx create-next-app@latest my-app --yes
cd my-app
npm run dev

# Using pnpm
pnpm create next-app@latest my-app --yes
cd my-app
pnpm dev

# Using yarn
yarn create next-app@latest my-app --yes
cd my-app
yarn dev

# Using bun
bun create next-app@latest my-app --yes
cd my-app
bun dev
```

The `--yes` flag skips prompts and enables: TypeScript, Tailwind CSS, ESLint, App Router, Turbopack, import alias `@/*`, and includes `AGENTS.md` for coding agents.

**Custom installation with prompts:**

```bash
npx create-next-app@latest my-app
```

Prompts include:
- TypeScript: Yes/No
- Linter: ESLint/Biome/None
- React Compiler: Yes/No
- Tailwind CSS: Yes/No
- App Router: Yes/No
- Import alias: `@/*` or custom

See [Installation Guide](references/01-installation.md) for detailed setup instructions.

## Quick Start

### Project Structure (App Router)

```
my-app/
├── app/                    # App Router directory
│   ├── layout.tsx          # Root layout (wraps all pages)
│   ├── page.tsx            # Home page (/)
│   ├── loading.tsx         # Loading UI for route group
│   ├── error.tsx           # Error boundary for route group
│   └── api/
│       └── users/
│           └── route.ts    # API route handler (GET, POST, etc.)
├── public/                 # Static files
├── package.json
└── tsconfig.json
```

### Hello World Application

**app/page.tsx (Server Component):**
```tsx
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <h1>Hello, Next.js 16.2.3!</h1>
      <p>Building with App Router and Server Components</p>
    </main>
  )
}
```

**app/layout.tsx (Root Layout):**
```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

Run the development server:
```bash
npm run dev
# Visit http://localhost:3000
```

See [Project Structure](references/02-project-structure.md) for detailed file conventions.

### Server vs Client Components

Next.js 16 uses React Server Components by default in the App Router.

**Server Component (default):**
```tsx
// app/products/page.tsx
async function ProductsPage() {
  const products = await fetch('https://api.example.com/products')
    .then(res => res.json())
  
  return (
    <ul>
      {products.map(product => (
        <li key={product.id}>{product.name}</li>
      ))}
    </ul>
  )
}

export default ProductsPage
```

**Client Component (with interactivity):**
```tsx
'use client'  // Required directive at top of file

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  )
}
```

See [Server and Client Components](references/03-server-client-components.md) for comprehensive guide.

### Data Fetching

**Fetch data in Server Components:**
```tsx
// app/products/[id]/page.tsx
interface PageProps {
  params: { id: string }
  searchParams: { sort: string }
}

export default async function ProductPage({ params, searchParams }: PageProps) {
  const product = await fetch(`https://api.example.com/products/${params.id}`, {
    next: { revalidate: 3600 }  // Revalidate every hour (ISR)
  }).then(res => res.json())
  
  return <div>{product.name}</div>
}
```

See [Data Fetching](references/04-data-fetching.md) for caching strategies and patterns.

### Routing and Navigation

**Define routes with file system:**
```
app/
├── page.tsx              # /
├── about/
│   └── page.tsx          # /about
└── products/
    ├── page.tsx          # /products
    └── [id]/
        └── page.tsx      # /products/[id]
```

**Navigate between pages:**
```tsx
import Link from 'next/link'

<Link href="/about">About Us</Link>
<Link href={`/products/${productId}`}>View Product</Link>
```

See [Routing Guide](references/05-routing.md) for advanced patterns.

### API Routes

**Create API endpoint:**
```tsx
// app/api/products/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const products = await fetchProductsFromDatabase()
  return NextResponse.json(products)
}

export async function POST(request: Request) {
  const body = await request.json()
  const product = await createProduct(body)
  return NextResponse.json(product, { status: 201 })
}
```

See [Route Handlers](references/06-api-routes.md) for full API reference.

### Styling with CSS Modules or Tailwind

**CSS Modules:**
```tsx
// app/page.tsx
import styles from './page.module.css'

export default function Home() {
  return <h1 className={styles.title}>Hello</h1>
}
```

**Tailwind CSS:**
```tsx
export default function Home() {
  return <h1 className="text-4xl font-bold text-center">Hello</h1>
}
```

## Common Operations

### Creating a New Route

1. Create a new folder or `page.tsx` file in `app/`
2. Export a default component
3. Access at the corresponding URL

```bash
# Create contact page
touch app/contact/page.tsx
```

```tsx
// app/contact/page.tsx
export default function ContactPage() {
  return <h1>Contact Us</h1>
}
```

### Adding Dynamic Routes

```tsx
// app/products/[slug]/page.tsx
interface Props {
  params: { slug: string }
}

export default async function ProductPage({ params }: Props) {
  const product = await getProductBySlug(params.slug)
  return <div>{product.name}</div>
}
```

### Implementing Loading States

```tsx
// app/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

### Error Handling

```tsx
// app/error.tsx
'use client'

export default function Error({ error, reset }: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Optimizing Images

```tsx
import Image from 'next/image'

export default function ProductImage() {
  return (
    <Image
      src="/product.jpg"
      alt="Product"
      width={400}
      height={300}
      priority  // For above-the-fold images
    />
  )
}
```

### Deploying to Production

```bash
# Build for production
npm run build

# Start production server
npm start

# Deploy to Vercel (recommended)
vercel deploy --prod
```

See [Deploying](references/07-deployment.md) for platform-specific guides.

## Reference Files

- [`references/01-installation.md`](references/01-installation.md) - Complete installation guide, system requirements, and create-next-app options
- [`references/02-project-structure.md`](references/02-project-structure.md) - App Router file conventions, directory structure, and organization patterns
- [`references/03-server-client-components.md`](references/03-server-client-components.md) - Server Components vs Client Components, when to use each, and interop patterns
- [`references/04-data-fetching.md`](references/04-data-fetching.md) - Data fetching strategies, caching (fetch API), revalidation, and ISR
- [`references/05-routing.md`](references/05-routing.md) - File-based routing, dynamic routes, layout nesting, loading states, error boundaries
- [`references/06-api-routes.md`](references/06-api-routes.md) - Route handlers, HTTP methods, request/response handling, API best practices
- [`references/07-deployment.md`](references/07-deployment.md) - Production builds, Vercel deployment, self-hosting, and optimization tips

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/nextjs-16-2-3/`). All paths are relative to this directory.

## Troubleshooting

### Common Issues

**Module not found errors:**
- Check import paths use correct aliases (`@/*` for root)
- Ensure TypeScript paths are configured in `tsconfig.json`
- Restart dev server after adding new files

**Hydration mismatch:**
- Ensure Server and Client components render identical HTML initially
- Avoid using `window`, `document`, or browser APIs in Server Components
- Use `'use client'` for components needing browser APIs

**Build errors:**
- Clear `.next` cache: `rm -rf .next && npm run dev`
- Check Node.js version is 20.9+
- Verify all dependencies are installed: `npm install`

**Image optimization issues:**
- Ensure `images` domain is configured in `next.config.js` for remote images
- Check image dimensions are provided or use `fill` prop

See [Deployment Guide](references/07-deployment.md) for production troubleshooting.

### Pages Router vs App Router

**App Router (Recommended for new projects):**
- Uses `app/` directory
- Server Components by default
- Nested layouts, loading states, error boundaries
- Route handlers for API routes
- Better performance with streaming and partial prerendering

**Pages Router (Legacy, still supported):**
- Uses `pages/` directory
- Client-side rendering by default
- `getServerSideProps`, `getStaticProps` for data fetching
- API routes in `pages/api/`
- Mature ecosystem with extensive third-party support

See [Installation Guide](references/01-installation.md) for choosing between routers.

## Additional Resources

- **Official Documentation:** https://nextjs.org/docs
- **GitHub Repository:** https://github.com/vercel/next.js
- **Discord Community:** https://discord.gg/nextjs
- **Twitter:** @nextjs
- **Learn Course:** https://nextjs.org/learn

## Best Practices

1. **Use Server Components by default** - Only use `'use client'` when necessary for interactivity
2. **Leverage caching** - Use `revalidate` option for ISR on dynamic content
3. **Optimize images** - Always use `next/image` for automatic optimization
4. **TypeScript** - Enable TypeScript for type safety and better DX
5. **Code splitting** - Next.js does this automatically with dynamic imports
6. **Environment variables** - Prefix with `NEXT_PUBLIC_` for client access
7. **Error boundaries** - Implement `error.tsx` for graceful error handling
8. **Loading states** - Use `loading.tsx` for improved UX during data fetching

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
