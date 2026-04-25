# API Routes (Route Handlers)

## Overview

Route handlers define API endpoints in the App Router using `route.ts` files.

## Basic Route Handler

```tsx
// app/api/hello/route.ts
import { NextResponse } from 'next/server'

export function GET() {
  return NextResponse.json({ message: 'Hello!' })
}
```

Access at: `GET /api/hello`

## HTTP Methods

### GET Request

```tsx
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const page = searchParams.get('page') || '1'
  
  const users = await getUsers({ page })
  
  return NextResponse.json(users)
}
```

### POST Request

```tsx
export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    // Validate input
    if (!body.email || !body.password) {
      return NextResponse.json(
        { error: 'Missing fields' },
        { status: 400 }
      )
    }
    
    const user = await createUser(body)
    
    return NextResponse.json(user, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### PUT/PATCH Request

```tsx
export async function PUT(request: Request, { params }: { params: { id: string } }) {
  const body = await request.json()
  const user = await updateUser(params.id, body)
  
  return NextResponse.json(user)
}
```

### DELETE Request

```tsx
export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  await deleteUser(params.id)
  
  return NextResponse.json({ success: true })
}
```

## Dynamic Route Handlers

```tsx
// app/api/users/[id]/route.ts
import { NextResponse } from 'next/server'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const user = await getUser(params.id)
  
  if (!user) {
    return NextResponse.json(
      { error: 'User not found' },
      { status: 404 }
    )
  }
  
  return NextResponse.json(user)
}

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  await deleteUser(params.id)
  return NextResponse.json({ deleted: true })
}
```

## Response Types

### JSON Response

```tsx
return NextResponse.json(data)
return NextResponse.json(data, { status: 201 })
return NextResponse.json(data, { status: 200, headers: { 'X-Custom': 'value' } })
```

### Text Response

```tsx
return new Response('Hello', { status: 200 })
```

### Redirect

```tsx
return NextResponse.redirect(new URL('/dashboard', request.url))
return NextResponse.rewrite(new URL('/internal', request.url))
```

### Cookies

```tsx
const response = NextResponse.json({ success: true })
response.cookies.set('session', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  maxAge: 60 * 60 * 24, // 1 day
  path: '/',
})
return response
```

## Request Headers

```tsx
export async function POST(request: Request) {
  const authorization = request.headers.get('authorization')
  const contentType = request.headers.get('content-type')
  
  // Verify auth
  if (!authorization?.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const token = authorization.split(' ')[1]
  const user = await verifyToken(token)
  
  // Process request
  const body = await request.json()
  // ...
}
```

## File Uploads

```tsx
// app/api/upload/route.ts
export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File
  
  if (!file) {
    return NextResponse.json({ error: 'No file' }, { status: 400 })
  }
  
  // Save file
  const buffer = await file.arrayBuffer()
  await saveFile(buffer, file.name)
  
  return NextResponse.json({ success: true })
}
```

## Rate Limiting

```tsx
// app/api/search/route.ts
import { Ratelimit } from '@upstash/ratelimit'

const ratelimit = new Ratelimit({
  redis,
  limiter: SlidingWindow.fixedWindow(10, '1 m'),
})

export async function GET(request: Request) {
  const ip = request.headers.get('x-forwarded-for')
  const { success, limit, reset, remaining } = await ratelimit.limit(`rate_${ip}`)
  
  if (!success) {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    )
  }
  
  // Add rate limit headers
  const response = NextResponse.json({ results: [] })
  response.headers.set('X-RateLimit-Limit', limit.toString())
  response.headers.set('X-RateLimit-Remaining', remaining.toString())
  response.headers.set('X-RateLimit-Reset', reset.toString())
  
  return response
}
```

## Error Handling

```tsx
export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    if (!isValid(body)) {
      return NextResponse.json(
        { error: 'Invalid input' },
        { status: 400 }
      )
    }
    
    const result = await processData(body)
    return NextResponse.json(result)
    
  } catch (error) {
    console.error('API Error:', error)
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

## Authentication

```tsx
// app/api/protected/route.ts
import { auth } from '@/auth'

export async function GET(request: Request) {
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  const data = await getProtectedData(session.user.id)
  return NextResponse.json(data)
}
```

## Best Practices

1. **Validate all input** - Never trust client data
2. **Use proper status codes** - 200, 201, 400, 401, 404, 500
3. **Implement rate limiting** - Prevent abuse
4. **Handle errors gracefully** - Don't expose internal details
5. **Add CORS headers** - For cross-origin requests
6. **Type your handlers** - Define request/response types
7. **Log appropriately** - Track usage and errors
8. **Use environment variables** - Never hardcode secrets
