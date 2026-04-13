# Data Fetching and Caching

## Overview

Next.js provides multiple data fetching strategies with built-in caching for optimal performance.

## Fetch in Server Components

### Basic Fetch

```tsx
// app/products/page.tsx
export default async function ProductsPage() {
  const res = await fetch('https://api.example.com/products')
  const products = await res.json()
  
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}
```

### Caching Strategies

**Default: Cached (Static Generation)**
```tsx
const res = await fetch('https://api.example.com/products')
// Default: cached indefinitely, revalidated on each request
```

**Force Cache:**
```tsx
const res = await fetch('https://api.example.com/products', {
  cache: 'force-cache'
})
```

**No Store (Fresh on every request):**
```tsx
const res = await fetch('https://api.example.com/products', {
  cache: 'no-store'
})
```

**Reload (Skip cache, fetch fresh):**
```tsx
const res = await fetch('https://api.example.com/products', {
  cache: 'reload'
})
```

**Default Cache (Use Next.js default):**
```tsx
const res = await fetch('https://api.example.com/products', {
  cache: 'default-cache'
})
```

### Incremental Static Regeneration (ISR)

Revalidate data after a time interval:

```tsx
export default async function ProductsPage() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 } // Revalidate every hour
  })
  const products = await res.json()
  
  return <ProductList products={products} />
}
```

**Revalidation options:**
- `revalidate: 3600` - Time-based (seconds)
- `revalidate: true` - On-demand (using Route Handlers)
- `tags: ['products']` - Tag-based revalidation

### Tag-Based Revalidation

```tsx
// Fetch with tags
const res = await fetch('https://api.example.com/products', {
  next: { tags: ['products'] }
})

// Later, revalidate by tag
import { revalidateTag } from 'next/cache'

export async function POST() {
  await revalidateTag('products')
  return new Response('Revalidated')
}
```

### Path-Based Revalidation

```tsx
import { revalidatePath } from 'next/cache'

export async function POST() {
  await revalidatePath('/products')
  return new Response('Revalidated')
}
```

## Fetch in Client Components

### Using useEffect

```tsx
'use client'

import { useState, useEffect } from 'react'

export default function ProductsClient() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetch('https://api.example.com/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        setLoading(false)
      })
  }, [])
  
  if (loading) return <div>Loading...</div>
  
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>
}
```

### Using SWR or React Query

```tsx
'use client'

import useSWR from 'swr'

const fetcher = url => fetch(url).then(res => res.json())

export default function ProductsSWR() {
  const { data, error, isLoading } = useSWR(
    'https://api.example.com/products',
    fetcher
  )
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error</div>
  
  return <ul>{data.map(p => <li key={p.id}>{p.name}</li>)}</ul>
}
```

## Data Passing Patterns

### Server to Client via Props

```tsx
// app/page.tsx (Server)
import { getProducts } from '@/lib/data'
import ProductList from './ProductList' // Client component

export default async function Page() {
  const products = await getProducts()
  
  return <ProductList products={products} />
}
```

```tsx
// app/ProductList.tsx (Client)
'use client'

export default function ProductList({ products }) {
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}
```

### Using Actions for Mutations

```tsx
// app/actions.ts
'use server'

export async function addProduct(data) {
  const result = await db.products.create({ data })
  revalidatePath('/products')
  return result
}
```

```tsx
// app/products/page.tsx (Client)
'use client'

import { addProduct } from '@/app/actions'

export default function AddForm() {
  const handleSubmit = async (formData) => {
    await addProduct(Object.fromEntries(formData))
  }
  
  return (
    <form action={handleSubmit}>
      <input name="name" />
      <button type="submit">Add</button>
    </form>
  )
}
```

## Error Handling

### Try/Catch in Server Components

```tsx
export default async function Page() {
  try {
    const res = await fetch('https://api.example.com/data')
    if (!res.ok) throw new Error('Failed to fetch')
    const data = await res.json()
    return <DataDisplay data={data} />
  } catch (error) {
    return <div>Error loading data</div>
  }
}
```

### Using error.tsx Boundary

Create `error.tsx` in same directory to catch all errors in route segment.

## Best Practices

1. **Fetch in Server Components** - Reduces bundle size, better security
2. **Use caching strategically** - ISR for frequently updated content
3. **Implement loading states** - Use `loading.tsx` for UX
4. **Handle errors gracefully** - Use `error.tsx` boundaries
5. **Type your data** - Define interfaces for fetched data
6. **Use tags for revalidation** - More granular than path-based

## Comparison Table

| Strategy | When to Use | Bundle Size | SEO | Freshness |
|----------|-------------|-------------|-----|-----------|
| Static Generation | Rarely changing content | ✅ Low | ✅ Best | ❌ Stale until revalidate |
| ISR (revalidate: N) | Frequently updated | ✅ Low | ✅ Best | ⚠️ Up to N seconds stale |
| SSR (no-store) | User-specific data | ⚠️ Medium | ⚠️ Good | ✅ Fresh |
| CSR (useEffect) | Highly dynamic | ❌ High | ❌ Poor | ✅ Fresh |
