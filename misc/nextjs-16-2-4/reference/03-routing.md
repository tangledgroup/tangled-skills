# Routing

## Dynamic Route Segments

Create dynamic segments by wrapping a folder name in square brackets: `[folderName]`.

```tsx
// app/blog/[slug]/page.tsx
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return <div>My Post: {slug}</div>
}
```

Route patterns:

- `[slug]` — Single dynamic segment: `/blog/my-post`
- `[...slug]` — Catch-all: `/shop/clothing`, `/shop/clothing/shirts`
- `[[...slug]]` — Optional catch-all: `/docs`, `/docs/layouts-and-pages`

## Parallel Routes

Parallel Routes allow you to simultaneously render one or more pages within the same layout. Created using named slots with the `@folder` convention:

```
app/
  layout.tsx
  page.tsx
  @team/
    page.tsx
  @analytics/
    page.tsx
```

Slots are passed as props to the parent layout:

```tsx
// app/layout.tsx
export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <>
      {children}
      {team}
      {analytics}
    </>
  )
}
```

Slots do not affect the URL structure. Use `default.js` as a fallback for unmatched slots.

## Intercepting Routes

Intercepting routes let you render a page within the current view while displaying a different URL. Useful for modals, drawers, or inline navigation:

```
app/
  @modal/
    (.)blog/[slug]/page.tsx   — intercepts /blog/[slug]
    (..)checkout/page.tsx     — intercepts /checkout at parent level
```

The `(.)` prefix intercepts at the current level, `(..)` at the parent level.

## Route Groups

Route groups `(group-name)` organize code without affecting the URL:

```
app/(marketing)/page.tsx   → /
app/(marketing)/about/page.tsx  → /about
app/(shop)/cart/page.tsx   → /cart
app/(shop)/products/page.tsx  → /products
```

Use route groups to apply different layouts to different sections of your app without changing the URL structure.

## Proxy (formerly Middleware)

The `proxy.js` file runs code on the server before a request is completed. In Next.js 16, `middleware.js` has been deprecated and renamed to `proxy.js`.

Create `proxy.ts` at the project root (same level as `app/` or `pages/`):

```ts
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = {
  matcher: '/about/:path*',
}
```

Proxy capabilities:

- **Rewrites** — Route requests to different internal paths
- **Redirects** — Send users to different URLs
- **Headers** — Modify request and response headers
- **Cookies** — Read and set cookies
- **Response modification** — Alter the response body

### Matcher Configuration

The `matcher` option targets specific paths:

```ts
export const config = {
  matcher: ['/about/:path*', '/dashboard/:path*'],
}
```

Complex matching with conditions:

```ts
export const config = {
  matcher: [
    {
      source: '/api/:path*',
      locale: false,
      has: [
        { type: 'header', key: 'Authorization' },
        { type: 'query', key: 'userId' },
      ],
      missing: [{ type: 'cookie', key: 'session' }],
    },
  ],
}
```

Without a matcher, proxy runs on every request including static files. Use negative patterns to exclude paths:

```ts
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
}
```

### Migration from Middleware

Automatically migrate from `middleware.js` to `proxy.js`:

```bash
npx @next/codemod@canary middleware-to-proxy .
```

## Route Segment Config

Export configuration options from any route segment file:

```tsx
// Control rendering behavior
export const dynamic = 'force-dynamic'   // Always render at request time
export const dynamic = 'force-static'    // Prerender at build time
export const dynamic = 'auto'            // Default: infer from data sources

// Control revalidation
export const revalidate = 3600           // Revalidate every hour (seconds)
export const revalidate = false          // Never revalidate
export const revalidate = 'error'        // Revalidate on error

// Control dynamic param generation
export const dynamicParams = true        // Allow non-generated params (404 fallback)
export const dynamicParams = false       // Only allow generated params

// Runtime
export const runtime = 'nodejs'          // Node.js runtime (default)
export const runtime = 'edge'            // Edge runtime

// Maximum duration for serverless functions
export const maxDuration = 60            // Seconds

// Preferred region for edge runtime
export const preferredRegion = 'iad1'    // AWS region
```

## Navigation APIs

Programmatic navigation from `next/navigation`:

```tsx
'use client'
import { useRouter, usePathname, useSearchParams } from 'next/navigation'

export default function Component() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  return (
    <div>
      <p>Current path: {pathname}</p>
      <button onClick={() => router.push('/new-path')}>Navigate</button>
      <button onClick={() => router.replace('/replace')}>Replace</button>
      <button onClick={() => router.back()}>Back</button>
      <button onClick={() => router.forward()}>Forward</button>
      <button onClick={() => router.refresh()}>Refresh</button>
    </div>
  )
}
```

## generateStaticParams

Pre-generate routes for dynamic segments at build time:

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then((res) =>
    res.json()
  )

  return posts.map((post) => ({
    slug: post.slug,
  }))
}

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return <div>Post: {slug}</div>
}
```
