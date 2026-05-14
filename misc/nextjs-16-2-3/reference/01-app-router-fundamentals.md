# App Router Fundamentals

## Project Structure

Next.js uses file-system based routing. Folders define URL segments, and special files within those folders define the UI and behavior for each route.

Top-level folders:

- `app/` — App Router (recommended)
- `pages/` — Pages Router (legacy, still supported)
- `public/` — Static assets served at the base URL
- `src/` — Optional source directory

Top-level files:

- `next.config.js` or `next.config.ts` — Next.js configuration
- `proxy.ts` — Request proxy (renamed from middleware in v16)
- `.env`, `.env.local`, `.env.production`, `.env.development` — Environment variables
- `instrumentation.ts` — OpenTelemetry and instrumentation
- `tsconfig.json` or `jsconfig.json` — TypeScript/JavaScript configuration
- `eslint.config.mjs` — ESLint configuration

## Pages

A page is UI rendered on a specific route. Create a page by adding a `page.js` or `page.tsx` file inside the `app` directory and default exporting a React component:

```tsx
// app/page.tsx
export default function Page() {
  return <h1>Hello Next.js!</h1>
}
```

Nested folders create nested routes:

- `app/page.tsx` → `/`
- `app/blog/page.tsx` → `/blog`
- `app/blog/authors/page.tsx` → `/blog/authors`

## Layouts

A layout is UI shared between multiple pages. On navigation, layouts preserve state, remain interactive, and do not rerender. Define a layout by default exporting a React component from a `layout.js` or `layout.tsx` file:

```tsx
// app/layout.tsx
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

The root layout (at the top of `app/`) is required and must contain `<html>` and `<body>` tags. Layouts accept a `children` prop that contains pages or nested layouts.

Layout components receive:

- `children` (required) — The child route segment content
- `params` (optional) — Dynamic route parameters as a Promise
- `searchParams` (optional) — URL query parameters as a Promise

## Linking and Navigation

Use the `<Link>` component from `next/link` for client-side navigation between pages:

```tsx
import Link from 'next/link'

export default function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/blog">Blog</Link>
      <Link href="/about">About</Link>
    </nav>
  )
}
```

`<Link>` enables:

- Client-side navigation without full page reloads
- Prefetching of linked pages in the viewport
- Turbopack-powered instant transitions

For programmatic navigation, use `router.push()` from `next/navigation`:

```tsx
'use client'
import { useRouter } from 'next/navigation'

export default function Component() {
  const router = useRouter()
  return <button onClick={() => router.push('/blog')}>Go to Blog</button>
}
```

## Loading UI

Create a `loading.js` file in the same folder as your page to show a loading state while data is being fetched:

```tsx
// app/blog/loading.tsx
export default function Loading() {
  return <div>Loading posts...</div>
}
```

This wraps the entire page with a Suspense boundary automatically.

## Error Handling

Create an `error.js` file to define an error boundary for a route segment:

```tsx
// app/blog/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
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

For global errors that cover the entire app, use `global-error.tsx`.

## Not Found UI

Create a `not-found.js` file to render a custom 404 page:

```tsx
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  )
}
```

## Route Groups and Private Folders

Route groups `(group)` organize code without affecting the URL:

```
app/(marketing)/page.tsx     → /
app/(shop)/cart/page.tsx     → /cart
```

Private folders prefixed with `_` are not routable and are safe for colocating utilities:

```
app/blog/_components/Post.tsx   → not a route
app/blog/_lib/data.ts           → not a route
```

## Component Hierarchy

Within a route segment, the component hierarchy from outermost to innermost is:

1. `layout.js` — Outermost, wraps everything
2. `template.js` — Re-rendered on navigation
3. `error.js` — Error boundary
4. `loading.js` — Loading state
5. `not-found.js` — 404 state
6. `page.js` — The page content
