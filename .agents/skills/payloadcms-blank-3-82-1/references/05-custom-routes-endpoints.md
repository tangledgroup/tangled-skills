# Custom Routes and Endpoints

Complete guide to creating custom API routes, endpoints, and integrating with Payload's Local API in Next.js App Router.

## Next.js Route Handlers

### Basic Route Handler Structure

**Location:** `src/app/api/[route]/route.ts`

```typescript
// src/app/api/hello/route.ts
import { getPayload } from 'payload'
import config from '@payload-config'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  
  // Your logic here
  
  return Response.json({
    message: 'Hello from custom route!',
  })
}

export const POST = async (request: Request) => {
  const payload = await getPayload({ config })
  const body = await request.json()
  
  // Process request
  
  return Response.json({ success: true }, { status: 201 })
}
```

**HTTP Method Exports:**
- `GET` - Read operations
- `POST` - Create operations
- `PUT` - Full update operations
- `PATCH` - Partial update operations
- `DELETE` - Delete operations
- `OPTIONS` - CORS preflight (usually auto-handled)

### Route Parameters

**Dynamic routes:** `src/app/api/users/[id]/route.ts`

```typescript
export const GET = async (request: Request, { params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params // Destructure from Promise
  
  const payload = await getPayload({ config })
  const user = await payload.findByID({
    collection: 'users',
    id,
  })
  
  if (!user) {
    return Response.json({ error: 'User not found' }, { status: 404 })
  }
  
  return Response.json(user)
}
```

**Multiple parameters:** `src/app/api/collections/[collection]/[id]/route.ts`

```typescript
export const GET = async (request: Request, { params }: { params: Promise<{ collection: string; id: string }> }) => {
  const { collection, id } = await params
  
  // Validate collection name (security!)
  const allowedCollections = ['posts', 'pages', 'products']
  if (!allowedCollections.includes(collection)) {
    return Response.json({ error: 'Invalid collection' }, { status: 400 })
  }
  
  const payload = await getPayload({ config })
  const doc = await payload.findByID({ collection, id })
  
  return Response.json(doc)
}
```

### Query Parameters

```typescript
export const GET = async (request: Request) => {
  const url = new URL(request.url)
  const searchParams = url.searchParams
  
  const limit = parseInt(searchParams.get('limit') || '10')
  const page = parseInt(searchParams.get('page') || '1')
  const sortBy = searchParams.get('sortBy') || 'createdAt'
  const sortOrder = searchParams.get('sortOrder') || 'desc'
  
  const payload = await getPayload({ config })
  const posts = await payload.find({
    collection: 'posts',
    limit,
    page,
    sort: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
  })
  
  return Response.json(posts)
}
```

## Authentication in Routes

### Getting User from Request

```typescript
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  
  // Get authenticated user from cookies/headers
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // User is authenticated
  return Response.json({ user })
}
```

### Role-Based Authorization

```typescript
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // Check for admin role
  if (!user.roles?.includes('admin')) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }
  
  // Admin-only operation
  const sensitiveData = await payload.find({
    collection: 'sensitive-documents',
  })
  
  return Response.json(sensitiveData)
}
```

### Reusable Auth Middleware Pattern

```typescript
// src/middleware/requireAuth.ts
import { PayloadRequest } from 'payload'

export async function requireAuth(request: Request) {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return { error: { message: 'Unauthorized', status: 401 } }
  }
  
  return { user }
}

export async function requireRole(request: Request, requiredRole: string) {
  const auth = await requireAuth(request)
  
  if ('error' in auth) {
    return auth
  }
  
  if (!auth.user.roles?.includes(requiredRole)) {
    return { error: { message: 'Forbidden', status: 403 } }
  }
  
  return { user: auth.user }
}

// Usage in routes:
export const GET = async (request: Request) => {
  const auth = await requireRole(request, 'admin')
  
  if ('error' in auth) {
    return Response.json(auth.error.message, { status: auth.error.status })
  }
  
  // User is authenticated with required role
}
```

## Local API Usage in Routes

### Basic CRUD Operations

**Create:**

```typescript
export const POST = async (request: Request) => {
  const payload = await getPayload({ config })
  const body = await request.json()
  
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  try {
    const doc = await payload.create({
      collection: 'posts',
      data: {
        ...body,
        author: user.id, // Auto-set author
      },
      req: { user } as any, // Pass request context for hooks
    })
    
    return Response.json(doc, { status: 201 })
  } catch (error) {
    return Response.json({ error: error.message }, { status: 400 })
  }
}
```

**Read:**

```typescript
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  
  const url = new URL(request.url)
  const id = url.searchParams.get('id')
  
  if (id) {
    // Get by ID
    const doc = await payload.findByID({
      collection: 'posts',
      id,
      depth: 2, // Populate relationships
    })
    
    if (!doc) {
      return Response.json({ error: 'Not found' }, { status: 404 })
    }
    
    return Response.json(doc)
  } else {
    // List all
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const page = parseInt(url.searchParams.get('page') || '1')
    
    const docs = await payload.find({
      collection: 'posts',
      limit,
      page,
      depth: 2,
    })
    
    return Response.json(docs)
  }
}
```

**Update:**

```typescript
export const PATCH = async (request: Request, { params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params
  
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const body = await request.json()
  
  // Check if user can update this document
  const doc = await payload.findByID({
    collection: 'posts',
    id,
  })
  
  if (!doc) {
    return Response.json({ error: 'Not found' }, { status: 404 })
  }
  
  // Only author or admin can update
  if (doc.author !== user.id && !user.roles?.includes('admin')) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }
  
  const updated = await payload.update({
    collection: 'posts',
    id,
    data: body,
  })
  
  return Response.json(updated)
}
```

**Delete:**

```typescript
export const DELETE = async (request: Request, { params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params
  
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user?.roles?.includes('admin')) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }
  
  await payload.delete({
    collection: 'posts',
    id,
  })
  
  return Response.json({ success: true })
}
```

### Query Operations

**Search with filters:**

```typescript
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  const url = new URL(request.url)
  
  const search = url.searchParams.get('search')
  const status = url.searchParams.get('status')
  const author = url.searchParams.get('author')
  
  const where: any = {}
  
  // Build query dynamically
  if (search) {
    where.title = { contains: search }
  }
  
  if (status) {
    where._status = { equals: status }
  }
  
  if (author) {
    where.author = { equals: author }
  }
  
  const posts = await payload.find({
    collection: 'posts',
    where: Object.keys(where).length > 0 ? where : undefined,
    depth: 2,
  })
  
  return Response.json(posts)
}
```

**Complex queries with AND/OR:**

```typescript
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  
  // Find published posts OR drafts by current user
  const { user } = await payload.auth({ request })
  
  const where = user ? {
    or: [
      { _status: { equals: 'published' } },
      { 
        and: [
          { _status: { equals: 'draft' } },
          { author: { equals: user.id } }
        ]
      }
    ]
  } : {
    _status: { equals: 'published' }
  }
  
  const posts = await payload.find({
    collection: 'posts',
    where,
  })
  
  return Response.json(posts)
}
```

See [Local API Usage](06-local-api-usage.md) for complete query patterns.

## Custom Endpoints Configuration

Payload also supports custom endpoints defined in the config (alternative to Next.js routes).

### Adding Custom Endpoint to Config

```typescript
// src/payload.config.ts
import type { Endpoint } from 'payload'

const customEndpoint: Endpoint = {
  path: '/api/custom-webhook',
  method: 'post',
  handler: async (req) => {
    // req has full Payload request context
    // req.payload - Local API
    // req.user - Authenticated user
    // req.headers, req.body, etc.
    
    const { event, data } = req.body
    
    // Process webhook
    if (event === 'user.created') {
      await sendWelcomeEmail(data.email)
    }
    
    return Response.json({ received: true })
  },
  middleware: [], // Optional middleware
}

export default buildConfig({
  // ...
  endpoints: [customEndpoint],
})
```

### Protected Custom Endpoint

```typescript
const protectedEndpoint: Endpoint = {
  path: '/api/admin-stats',
  method: 'get',
  middleware: [
    // Add authentication middleware
    async (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' })
      }
      
      if (!req.user.roles?.includes('admin')) {
        return res.status(403).json({ error: 'Forbidden' })
      }
      
      next()
    },
  ],
  handler: async (req) => {
    const stats = await calculateStats(req.payload)
    return Response.json(stats)
  },
}
```

**Note:** Custom endpoints in config use Express-style handlers. For new projects, prefer Next.js route handlers for better type safety and integration.

## Error Handling

### Standard Error Responses

```typescript
export const GET = async (request: Request) => {
  try {
    const payload = await getPayload({ config })
    const data = await fetchData(payload)
    
    return Response.json(data)
  } catch (error) {
    if (error instanceof Error) {
      // Known error types
      if (error.message === 'Document not found') {
        return Response.json(
          { error: 'Not found' },
          { status: 404 }
        )
      }
      
      // Validation errors
      if (error.name === 'ValidationError') {
        return Response.json(
          { error: error.message },
          { status: 400 }
        )
      }
    }
    
    // Unknown error
    console.error('Route error:', error)
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### Using Payload APIError

```typescript
import { APIError } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    throw new APIError('Unauthorized', 401)
  }
  
  const doc = await payload.findByID({
    collection: 'posts',
    id: '123',
  })
  
  if (!doc) {
    throw new APIError('Document not found', 404)
  }
  
  return Response.json(doc)
}
```

## CORS Configuration

For routes that need to accept requests from other origins:

```typescript
export const OPTIONS = () => {
  return Response.json(null, {
    headers: {
      'Access-Control-Allow-Origin': 'https://your-frontend.com',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400', // 24 hours
    },
  })
}

// Add CORS headers to all responses
export const GET = async (request: Request) => {
  const response = await fetchData()
  
  return Response.json(response, {
    headers: {
      'Access-Control-Allow-Origin': 'https://your-frontend.com',
    },
  })
}
```

**Note:** For production, consider using a CORS middleware package or Next.js middleware.

## Streaming Responses

### Server-Sent Events (SSE)

```typescript
export const GET = async (request: Request) => {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    start: async (controller) => {
      const payload = await getPayload({ config })
      
      // Send initial message
      controller.enqueue(encoder.encode('data: Starting...\n\n'))
      
      // Stream updates
      const posts = await payload.find({
        collection: 'posts',
        limit: 10,
      })
      
      posts.docs.forEach((post, index) => {
        setTimeout(() => {
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify(post)}\n\n`)
          )
        }, index * 1000)
      })
      
      // Close stream
      setTimeout(() => {
        controller.enqueue(encoder.encode('event: done\ndata: {}\n\n'))
        controller.close()
      }, posts.docs.length * 1000)
    },
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

## File Upload Routes

### Handling File Uploads

```typescript
export const POST = async (request: Request) => {
  const formData = await request.formData()
  const file = formData.get('file') as File
  
  if (!file) {
    return Response.json({ error: 'No file provided' }, { status: 400 })
  }
  
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // Convert File to Buffer for Payload
  const arrayBuffer = await file.arrayBuffer()
  const buffer = Buffer.from(arrayBuffer)
  
  // Upload to media collection
  const media = await payload.create({
    collection: 'media',
    data: {
      alt: file.name,
    },
    file: {
      buffer,
      mimetype: file.type,
      originalFilename: file.name,
    },
  })
  
  return Response.json(media, { status: 201 })
}
```

## Rate Limiting

### Simple Rate Limiting with Cookies

```typescript
import { cookies } from 'next/headers'

export const POST = async (request: Request) => {
  const cookieStore = await cookies()
  const requestCount = parseInt(cookieStore.get('request-count')?.value || '0')
  
  if (requestCount >= 10) {
    return Response.json({ error: 'Rate limit exceeded' }, { status: 429 })
  }
  
  // Process request
  const result = await processData()
  
  // Increment counter
  cookieStore.set('request-count', String(requestCount + 1), {
    maxAge: 60, // Reset after 60 seconds
  })
  
  return Response.json(result)
}
```

**For production:** Use Redis-based rate limiting or a dedicated service like Upstash.

## Best Practices

### 1. Validate Input

```typescript
import { z } from 'zod'

const PostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(1),
  status: z.enum(['draft', 'published']).optional(),
})

export const POST = async (request: Request) => {
  const body = await request.json()
  
  const validation = PostSchema.safeParse(body)
  if (!validation.success) {
    return Response.json(
      { error: validation.error.errors },
      { status: 400 }
    )
  }
  
  // Safe to use validation.data
}
```

### 2. Use Proper Status Codes

- `200 OK` - Successful GET, PATCH, PUT
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input/validation error
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `429 Too Many Requests` - Rate limited
- `500 Internal Server Error` - Server error

### 3. Log Important Operations

```typescript
export const DELETE = async (request: Request, { params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params
  
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  // Log deletion for audit trail
  console.log(`User ${user?.id} deleting post ${id}`)
  
  // Or create audit log entry
  await payload.create({
    collection: 'audit-log',
    data: {
      action: 'delete',
      collection: 'posts',
      documentId: id,
      userId: user?.id,
    },
  })
  
  await payload.delete({ collection: 'posts', id })
  return Response.json({ success: true })
}
```

### 4. Sanitize Output

```typescript
export const GET = async (request: Request) => {
  const user = await fetchUser()
  
  // Don't expose sensitive fields
  return Response.json({
    id: user.id,
    email: user.email,
    name: user.name,
    // Exclude: password, roles, refreshToken, etc.
  })
}
```

### 5. Document Your API

```typescript
/**
 * @route GET /api/posts
 * @description Get all published posts
 * @query {string} search - Search in title and content
 * @query {number} limit - Results per page (default: 10)
 * @query {number} page - Page number (default: 1)
 * @returns {object} List of posts with pagination
 */
export const GET = async (request: Request) => {
  // ...
}
```

See [Local API Usage](06-local-api-usage.md) for more Local API patterns and query examples.
