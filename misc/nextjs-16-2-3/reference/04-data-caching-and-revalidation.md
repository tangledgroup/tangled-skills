# Data Caching and Revalidation

## Cache Components

Enable Cache Components in `next.config.ts`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

With Cache Components enabled, caching uses the `use cache` directive and related APIs.

## The `use cache` Directive

The `"use cache"` directive caches the return value of async functions and components at two levels:

### Data-level caching

Cache a function that fetches or computes data:

```tsx
// app/lib/data.ts
import { cacheLife } from 'next/cache'

export async function getUsers() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM users')
}
```

Arguments and closed-over values automatically become part of the cache key, enabling personalized or parameterized cached content.

### UI-level caching

Cache an entire component, page, or layout:

```tsx
// app/page.tsx
import { cacheLife } from 'next/cache'

export default async function Page() {
  'use cache'
  cacheLife('hours')

  const users = await db.query('SELECT * FROM users')

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

If you add `"use cache"` at the top of a file, all exported functions in the file will be cached.

## Streaming Uncached Data

For components requiring fresh data on every request, do not use `"use cache"`. Instead, wrap with `<Suspense>`:

```tsx
import { Suspense } from 'react'

async function LatestPosts() {
  const data = await fetch('https://api.example.com/posts')
  const posts = await data.json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}

export default function Page() {
  return (
    <>
      <h1>My Blog</h1>
      <Suspense fallback={<p>Loading posts...</p>}>
        <LatestPosts />
      </Suspense>
    </>
  )
}
```

## cacheLife

Controls how long cached data remains valid. Use inside a `use cache` scope:

```tsx
'use cache'
cacheLife('hours')
```

Built-in profiles:

- `seconds` — stale: 0, revalidate: 1s, expire: 60s
- `minutes` — stale: 5m, revalidate: 1m, expire: 1h
- `hours` — stale: 5m, revalidate: 1h, expire: 1d
- `days` — stale: 5m, revalidate: 1d, expire: 1w
- `weeks` — stale: 5m, revalidate: 1w, expire: 30d
- `max` — stale: 5m, revalidate: 30d, expire: ~indefinite

Custom configuration for fine-grained control:

```tsx
'use cache'
cacheLife({
  stale: 3600,     // 1 hour until considered stale
  revalidate: 7200, // 2 hours until revalidated
  expire: 86400,   // 1 day until expired
})
```

Short-lived caches (`seconds` profile, `revalidate: 0`, or `expire` under 5 minutes) are automatically excluded from prerenders and become dynamic holes.

## cacheTag

Tag cached data for on-demand invalidation:

```tsx
import { cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheTag('products')
  return db.query('SELECT * FROM products')
}
```

## Revalidation Strategies

### On-demand revalidation with tags

Invalidate cached data after a mutation:

```tsx
import { revalidateTag } from 'next/cache'

// After a mutation, invalidate all caches tagged 'products'
await revalidateTag('products')
```

### Path-based revalidation

Revalidate by URL path:

```tsx
import { revalidatePath } from 'next/cache'

// Revalidate a specific page
await revalidatePath('/blog')

// Revalidate all pages under /blog
await revalidatePath('/blog', 'layout')
```

### updateTag

Update the tag value for time-based tracking:

```tsx
import { updateTag } from 'next/cache'

// Update tag with current timestamp
await updateTag('products', Date.now())
```

## Previous Caching Model (without Cache Components)

When `cacheComponents` is not enabled, use route segment config exports:

```tsx
// Force static rendering
export const dynamic = 'force-static'

// Force dynamic rendering
export const dynamic = 'force-dynamic'

// Time-based revalidation (seconds)
export const revalidate = 3600

// Never revalidate
export const revalidate = false

// Revalidate on error
export const revalidate = 'error'
```

With `fetch`, use cache options:

```tsx
// Cache indefinitely until manually revalidated
const res = await fetch(url, { cache: 'force-cache' })

// Always fetch fresh data
const res = await fetch(url, { cache: 'no-store' })

// Tag for revalidation
const res = await fetch(url, {
  next: { tags: ['products'] },
})
```
