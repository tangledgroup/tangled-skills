# Server and Client Components

## Overview

By default, layouts and pages in Next.js are Server Components. This lets you fetch data and render UI on the server, optionally cache results, and stream them to the client. When you need interactivity or browser APIs, use Client Components.

## Server Components

Use Server Components when you need to:

- Fetch data from databases or APIs close to the source
- Use API keys, tokens, and secrets without exposing them to the client
- Reduce JavaScript sent to the browser
- Improve First Contentful Paint (FCP) and stream content progressively

Server Components are async functions that can use `await` directly:

```tsx
// app/blog/page.tsx — Server Component (default)
import { db } from '@/lib/db'

export default async function Page() {
  const posts = await db.query('SELECT * FROM posts')
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

## Client Components

Use Client Components when you need:

- State and event handlers (`useState`, `onClick`, `onChange`)
- Lifecycle effects (`useEffect`)
- Browser-only APIs (`localStorage`, `window`, `navigator.geolocation`)
- Custom hooks

Create a Client Component by adding `"use client"` at the top of the file, above imports:

```tsx
// app/ui/counter.tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return (
    <div>
      <p>{count} likes</p>
      <button onClick={() => setCount(count + 1)}>Like</button>
    </div>
  )
}
```

## Composing Server and Client Components

The recommended pattern is to keep most of your app as Server Components and use Client Components for interactive pieces:

```tsx
// app/[id]/page.tsx — Server Component
import LikeButton from '@/app/ui/like-button'
import { getPost } from '@/lib/data'

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const post = await getPost(id)

  return (
    <div>
      <h1>{post.title}</h1>
      <LikeButton likes={post.likes} />
    </div>
  )
}
```

```tsx
// app/ui/like-button.tsx — Client Component
'use client'

import { useState } from 'react'

export default function LikeButton({ likes }: { likes: number }) {
  const [count, setCount] = useState(likes)
  return (
    <button onClick={() => setCount(count + 1)}>
      {count} likes
    </button>
  )
}
```

## How Rendering Works

### On the server

Next.js orchestrates rendering by route segments:

- Server Components are rendered into the React Server Component Payload (RSC Payload) — a compact binary representation of the rendered tree
- Client Components and the RSC Payload are used to prerender HTML

### On the client (first load)

1. HTML is shown immediately as a fast non-interactive preview
2. RSC Payload reconciles Client and Server Component trees
3. JavaScript hydrates Client Components to make the app interactive

### Subsequent navigations

- The RSC Payload is prefetched and cached for instant navigation
- Client Components are rendered entirely on the client

## Data Fetching

### With the fetch API

In Server Components, use `fetch` directly with `await`:

```tsx
export default async function Page() {
  const data = await fetch('https://api.vercel.app/blog')
  const posts = await data.json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

Identical `fetch` requests in a React component tree are memoized by default. `fetch` requests are not cached by default — use `use cache` to cache results, or wrap in `<Suspense>` to stream fresh data.

### With an ORM or database

Since Server Components run on the server, credentials and query logic are never included in the client bundle:

```tsx
import { db, posts } from '@/lib/db'

export default async function Page() {
  const allPosts = await db.select().from(posts)
  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

## Streaming

For slow data requests, break the page into chunks and progressively send them from server to client.

### With loading.js

Create a `loading.js` file to stream the entire page:

```tsx
// app/blog/loading.tsx
export default function Loading() {
  return <div>Loading posts...</div>
}
```

### With Suspense

Wrap specific components with `<Suspense>` for fine-grained streaming:

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

## Server Functions (Actions)

Server Functions let you run server-side logic directly from Client Components using the `"use server"` directive:

```tsx
// app/actions.ts
'use server'

export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')

  const res = await fetch('https://api.vercel.app/posts', {
    method: 'POST',
    body: { title, content },
  })

  if (!res.ok) {
    return { message: 'Failed to create post' }
  }
  return { message: 'Post created successfully' }
}
```

Use with `useActionState` in a Client Component:

```tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

export function Form() {
  const [state, formAction, pending] = useActionState(
    createPost,
    { message: '' }
  )

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      <textarea name="content" placeholder="Content" />
      <button disabled={pending}>Submit</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

## Accessing Dynamic Params in Client Components

In a Client Component page, use the `use` API to unwrap params:

```tsx
'use client'
import { use } from 'react'

export default function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = use(params)
  return <div>Post: {slug}</div>
}
```
