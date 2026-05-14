# API and Backend

## Route Handlers

Route Handlers allow you to create custom request handlers using the Web Request and Response APIs. Define them in a `route.js` or `route.ts` file inside the `app` directory:

```ts
// app/api/route.ts
export async function GET(request: Request) {
  return Response.json({ message: 'Hello from Next.js' })
}

export async function POST(request: Request) {
  const body = await request.json()
  return Response.json({ received: body }, { status: 201 })
}
```

Supported HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, and `OPTIONS`. Unsupported methods return `405 Method Not Allowed`.

Route Handlers cannot coexist with a `page.js` at the same route segment level.

### Extended APIs

Next.js provides `NextRequest` and `NextResponse` for convenient helpers:

```ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const id = searchParams.get('id')

  return NextResponse.json({ id })
}
```

### Caching Route Handlers

Route Handlers are not cached by default. For `GET` methods, opt into caching:

```ts
export const dynamic = 'force-static'

export async function GET() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()
  return Response.json({ data: json })
}
```

With Cache Components enabled, `GET` Route Handlers follow the same prerendering model as pages — they run at request time by default and can be prerendered when they don't access uncached or runtime data.

## Server Actions

Server Actions let you run server-side logic directly from React components. Mark functions with `"use server"`:

```ts
// app/actions.ts
'use server'

export async function deletePost(id: string) {
  await db.delete('posts', { where: { id } })
}

export async function updatePost(data: FormData) {
  const title = data.get('title') as string
  await db.update('posts', { title })
}
```

Use from Client Components with `useActionState`:

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
      <input name="title" />
      <textarea name="content" />
      <button disabled={pending}>Submit</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

Or use the `form` action prop directly in Server Components:

```tsx
import { deletePost } from '@/app/actions'

export default function Page() {
  return (
    <form action={deletePost}>
      <button type="submit">Delete</button>
    </form>
  )
}
```

## Environment Variables

Next.js loads environment variables from `.env` files into `process.env`:

```bash
# .env.local
DB_HOST=localhost
DB_USER=myuser
DB_PASS=mypassword
```

File precedence:

- `.env` — Default, loaded in all environments
- `.env.local` — Local overrides (should be gitignored)
- `.env.development` — Development environment
- `.env.production` — Production environment
- `.env.test` — Test environment

### Client-side variables

Prefix with `NEXT_PUBLIC_` to bundle for the browser:

```bash
NEXT_PUBLIC_API_URL=https://api.example.com
```

Access in any component:

```tsx
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

Non-prefixed variables are only available on the server side.

## Proxy Configuration

The `proxy.ts` file (renamed from `middleware.ts` in v16) runs before routes are rendered:

```ts
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function proxy(request: NextRequest) {
  // Authentication check
  const session = request.cookies.get('session')

  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Add custom headers
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'value')
  return response
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

Common proxy patterns:

- **Rewrites**: `NextResponse.rewrite(new URL('/internal-path', request.url))`
- **Redirects**: `NextResponse.redirect(new URL('/target', request.url))`
- **Cookies**: `request.cookies.get('name')` / `response.cookies.set('name', 'value')`
- **Headers**: `response.headers.set('key', 'value')`

## Error Handling APIs

### Expected errors

Model expected errors as return values rather than throwing:

```ts
'use server'

export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title')
  if (!title) {
    return { message: 'Title is required' }
  }
  // ... create post
  return { message: 'Post created' }
}
```

### Unexpected errors

Use `catchError` for unexpected errors:

```tsx
import { catchError } from 'next/error'

try {
  await riskyOperation()
} catch (error) {
  catchError(error)
  // Handle or rethrow
}
```

### Navigation errors

Programmatic navigation for error states:

```tsx
import { notFound, redirect, permanentRedirect } from 'next/navigation'

export async function Page({ params }) {
  const post = await getPost((await params).id)

  if (!post) {
    notFound()
  }

  if (!post.published) {
    redirect('/drafts')
  }

  return <article>{post.content}</article>
}
```

## Instrumentation

Use `instrumentation.ts` for OpenTelemetry and monitoring:

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { NodeSDK } = require('@opentelemetry/sdk-node')
    const sdk = new NodeSDK({
      // OpenTelemetry configuration
    })
    sdk.start()
  }
}
```
