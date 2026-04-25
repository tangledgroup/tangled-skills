# Routing and Navigation

## File-Based Routing

Next.js uses the file system to define routes.

### Basic Routes

```
app/
├── page.tsx              # /
├── about/
│   └── page.tsx          # /about
└── contact/
    └── page.tsx          # /contact
```

### Nested Routes

```
app/
└── blog/
    ├── page.tsx          # /blog
    └── posts/
        └── page.tsx      # /blog/posts
```

## Dynamic Routes

### Single Dynamic Segment

```
app/
└── products/
    └── [id]/
        └── page.tsx      # /products/123
```

```tsx
// app/products/[id]/page.tsx
interface Props {
  params: { id: string }
}

export default async function ProductPage({ params }: Props) {
  const product = await getProduct(params.id)
  return <div>{product.name}</div>
}
```

### Multiple Dynamic Segments

```
app/
└── shop/
    └── [category]/
        └── [product]/
            └── page.tsx  # /shop/electronics/iphone
```

### Catch-all Routes

```
app/
└── docs/
    └── [...slug]/
        └── page.tsx      # /docs/getting-started/installation
```

```tsx
interface Props {
  params: { slug: string[] }
}

export default function DocsPage({ params }: Props) {
  return <div>Path: {params.slug.join('/')}</div>
}
```

### Optional Catch-all

```
app/
└── shop/
    └── [...slug]/
        └── page.tsx      # /shop, /shop/a, /shop/a/b
```

## Navigation

### Link Component

```tsx
import Link from 'next/link'

<Link href="/about">About</Link>
<Link href={`/products/${id}`}>Product {id}</Link>
```

**Props:**
- `href` - Destination URL
- `passHref` - Pass raw href to child
- `replace` - Replace current history entry
- `scroll` - Scroll to top on navigation
- `prefetch` - Prefetch on hover (default: true)

### Programmatic Navigation

```tsx
'use client'

import { useRouter } from 'next/navigation'

export default function Component() {
  const router = useRouter()
  
  const handleNavigate = () => {
    router.push('/about')
    router.replace('/contact')
    router.back()
    router.forward()
    router.refresh()
  }
}
```

## Route Groups

Group routes without creating URL segments:

```
app/
├── (marketing)/
│   ├── page.tsx          # /
│   └── about/
│       └── page.tsx      # /about
│
└── (dashboard)/
    └── settings/
        └── page.tsx      # /settings
```

## Layouts in Routes

### Root Layout

```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  )
}
```

### Nested Layouts

```tsx
// app/blog/layout.tsx
export default function BlogLayout({ children }) {
  return (
    <div>
      <BlogSidebar />
      {children}
    </div>
  )
}
```

## Loading States

### Default Loading

```tsx
// app/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

### Route-Specific Loading

```tsx
// app/products/loading.tsx
export default function ProductsLoading() {
  return (
    <div className="skeleton">
      {[1,2,3].map(i => <div key={i} className="card-skeleton" />)}
    </div>
  )
}
```

## Error Handling

### Error Boundary

```tsx
// app/error.tsx
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Error</h2>
      <pre>{error.message}</pre>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Custom 404 Page

```tsx
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h1>404 - Not Found</h1>
      <Link href="/">Go Home</Link>
    </div>
  )
}
```

## Search Parameters

Access URL query parameters:

```tsx
// app/search/page.tsx
interface Props {
  searchParams: { q: string }
}

export default async function SearchPage({ searchParams }: Props) {
  const results = await searchFor(searchParams.q)
  
  return (
    <div>
      <h1>Results for: {searchParams.q}</h1>
      {results.map(r => <div key={r.id}>{r.title}</div>)}
    </div>
  )
}
```

## Intercept Routes

Intercept navigation to show content in current view:

```
app/
├── shop/
│   └── page.tsx          # /shop
└── (./shop)/
    └── [product]/
        └── page.tsx      # Intercepts, shows modal
```

## Best Practices

1. **Use meaningful route names** - Clear URL structure
2. **Implement loading states** - Better UX during navigation
3. **Add error boundaries** - Graceful error handling
4. **Type your params** - Define interfaces for type safety
5. **Use Link component** - Client-side navigation, prefetching
6. **Organize with groups** - Keep structure clean with `(groups)`
