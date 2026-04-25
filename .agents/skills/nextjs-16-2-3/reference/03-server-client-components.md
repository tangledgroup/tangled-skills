# Server Components vs Client Components

## Overview

Next.js 16 uses React Server Components (RSC) by default in the App Router. Understanding when to use Server vs Client components is crucial for optimal performance and functionality.

## Server Components (Default)

**What they are:** Components that render exclusively on the server, sending HTML to the client.

**Benefits:**
- ✅ Zero bundle size (not sent to client)
- ✅ Direct access to backend resources (database, file system)
- ✅ Automatic code splitting
- ✅ Improved security (secrets never exposed)
- ✅ Better SEO (full HTML sent to client)

**Limitations:**
- ❌ No interactivity (no `useState`, `useEffect`)
- ❌ No browser APIs (`window`, `document`)
- ❌ No React hooks
- ❌ No event handlers (`onClick`, `onChange`)

### When to Use Server Components

1. **Fetching data directly:**
```tsx
// app/products/page.tsx (Server Component)
export default async function ProductsPage() {
  const products = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 }
  }).then(res => res.json())
  
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}
```

2. **Accessing backend resources:**
```tsx
// app/dashboard/page.tsx
import { db } from '@/lib/db'

export default async function Dashboard() {
  const stats = await db.stats.findMany()
  
  return <div>{/* render stats */}</div>
}
```

3. **Heavy computations:**
```tsx
// app/reports/page.tsx
import { processReport } from '@/lib/heavy-computation'

export default async function ReportPage() {
  const data = await processReport() // Runs on server
  
  return <div>{/* render report */}</div>
}
```

4. **Keeping secrets safe:**
```tsx
// app/admin/page.tsx
import { getAdminData } from '@/lib/admin' // Uses DB credentials

export default async function AdminPage() {
  const data = await getAdminData() // Credentials never exposed
  
  return <div>{/* sensitive data */}</div>
}
```

## Client Components

**What they are:** Components that render on both server and client, with interactivity.

**How to create:** Add `'use client'` directive at the top of the file.

```tsx
'use client'

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

**Benefits:**
- ✅ Full React interactivity
- ✅ Access to browser APIs
- ✅ State management with hooks
- ✅ Event handlers work

**Limitations:**
- ❌ Added bundle size (sent to client)
- ❌ Hydration required (slightly slower initial load)
- ❌ Cannot directly access backend resources

### When to Use Client Components

1. **Adding interactivity:**
```tsx
'use client'

import { useState } from 'react'

export default function SearchInput() {
  const [query, setQuery] = useState('')
  
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

2. **Using browser APIs:**
```tsx
'use client'

import { useEffect } from 'react'

export default function Geolocation() {
  const [location, setLocation] = useState(null)
  
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(pos => {
      setLocation(pos.coords)
    })
  }, [])
  
  return <div>{/* location data */}</div>
}
```

3. **Managing complex state:**
```tsx
'use client'

import { useState, useCallback } from 'react'

export default function ShoppingCart() {
  const [items, setItems] = useState([])
  
  const addItem = useCallback((item) => {
    setItems(prev => [...prev, item])
  }, [])
  
  return (
    <div>
      {items.map(item => <CartItem key={item.id} item={item} />)}
      <button onClick={() => addItem(newItem)}>Add</button>
    </div>
  )
}
```

4. **Using third-party libraries:**
```tsx
'use client'

import dynamic from 'next/dynamic'

// Libraries that depend on window/document
const Chart = dynamic(() => import('react-chartjs-2'), { ssr: false })

export default function Analytics() {
  return <Chart data={data} />
}
```

## Component Composition Patterns

### Pattern 1: Server Component with Client Child

Most common pattern - fetch data in server, interactive child component.

```tsx
// app/products/page.tsx (Server Component)
import { getProduct } from '@/lib/products'
import ProductActions from './ProductActions' // Client component

export default async function ProductPage({ params }) {
  const product = await getProduct(params.id)
  
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <ProductActions productId={product.id} />
    </div>
  )
}
```

```tsx
// app/products/ProductActions.tsx (Client Component)
'use client'

import { useState } from 'react'

export default function ProductActions({ productId }) {
  const [quantity, setQuantity] = useState(1)
  
  return (
    <div>
      <input 
        type="number" 
        value={quantity}
        onChange={(e) => setQuantity(Number(e.target.value))}
      />
      <button onClick={() => addToCart(productId, quantity)}>
        Add to Cart
      </button>
    </div>
  )
}
```

### Pattern 2: Server Component Wrapper

Server component fetches data, passes to client component.

```tsx
// app/form/page.tsx (Server Component)
import { getFormData } from '@/lib/data'
import FormComponent from './FormComponent' // Client component

export default async function FormPage() {
  const initialData = await getFormData()
  
  return <FormComponent initialData={initialData} />
}
```

```tsx
// app/form/FormComponent.tsx (Client Component)
'use client'

import { useState } from 'react'

export default function FormComponent({ initialData }) {
  const [data, setData] = useState(initialData)
  
  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      // Handle submission
    }}>
      <input value={data.value} onChange={(e) => setData({...data, value: e.target.value})} />
      <button type="submit">Submit</button>
    </form>
  )
}
```

### Pattern 3: Mixed Component Tree

Mix server and client components in the same tree.

```tsx
// app/dashboard/page.tsx (Server Component)
import StatsOverview from '@/components/StatsOverview' // Server
import LiveUpdates from '@/components/LiveUpdates'     // Client
import UserList from '@/components/UserList'           // Server

export default async function Dashboard() {
  return (
    <div>
      <StatsOverview />      // Server - fetches stats
      <LiveUpdates />        // Client - WebSocket updates
      <UserList />           // Server - queries database
    </div>
  )
}
```

## Common Pitfalls

### ❌ Using hooks in Server Components

```tsx
// ERROR: This will fail!
export default function BadServerComponent() {
  const [state, setState] = useState(0) // Cannot use hooks
  
  return <div>{state}</div>
}
```

**Fix:** Add `'use client'` or remove hooks.

### ❌ Accessing window in Server Components

```tsx
// ERROR: window is undefined on server
export default function BadComponent() {
  const width = window.innerWidth // Fails!
  
  return <div>Width: {width}</div>
}
```

**Fix:** Use Client Component or get dimension server-side.

### ❌ Exposing secrets in props to Client Components

```tsx
// BAD: Secret exposed to client bundle
import { DB_PASSWORD } from '@/env'
import ClientWidget from './ClientWidget'

export default function Page() {
  return <ClientWidget password={DB_PASSWORD} /> // Leaked!
}
```

**Fix:** Fetch data in Server Component, pass only results.

```tsx
// GOOD: Secret stays on server
import { getPublicData } from '@/lib/data' // Internally uses DB_PASSWORD

export default async function Page() {
  const data = await getPublicData()
  return <ClientWidget data={data} /> // Safe!
}
```

## Decision Tree

```
Need interactivity (useState, onClick)?
├─ Yes → Client Component ('use client')
└─ No → Can use Server Component
   
   Need browser APIs (window, document)?
   ├─ Yes → Client Component
   └─ No → Can use Server Component
      
      Need to fetch data?
      ├─ Yes → Server Component (direct access)
      └─ No → Either works
         
         Contains secrets?
         ├─ Yes → Server Component only
         └─ No → Either works
```

## Best Practices

1. **Default to Server Components** - Only use Client when needed
2. **Push interactivity down** - Keep server components dumb, client components interactive
3. **Colocate components** - Put related components in same folder
4. **Type your props** - Always define interfaces for component props
5. **Test both environments** - Ensure components work in SSR and CSR

## Migration Tips

### From Pages Router to App Router

**Before (Pages Router):**
```tsx
// pages/product.tsx
import { useState } from 'react'

export async function getServerSideProps() {
  const product = await fetchProduct()
  return { props: { product } }
}

export default function Product({ product }) {
  const [cart, setCart] = useState([])
  // Mixed SSR and client state
}
```

**After (App Router):**
```tsx
// app/product/page.tsx (Server Component)
import CartActions from './CartActions' // Client component

export default async function ProductPage() {
  const product = await fetchProduct()
  
  return (
    <div>
      <h1>{product.name}</h1>
      <CartActions productId={product.id} />
    </div>
  )
}
```

```tsx
// app/product/CartActions.tsx (Client Component)
'use client'

import { useState } from 'react'

export default function CartActions({ productId }) {
  const [cart, setCart] = useState([])
  // Pure client interactivity
}
```
