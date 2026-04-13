# Local API Guide

The Payload Local API allows you to interact with your CMS directly from server-side code. It's type-safe, supports transactions, and provides full access to all Payload functionality.

## CRITICAL SECURITY PATTERNS

### 1. Access Control in Local API (MOST IMPORTANT)

```typescript
// ❌ SECURITY BUG: Access control bypassed
await payload.find({
  collection: 'posts',
  user: someUser, // Ignored! Operation runs with ADMIN privileges
})

// ✅ SECURE: Enforces user permissions
await payload.find({
  collection: 'posts',
  user: someUser,
  overrideAccess: false, // REQUIRED when passing user
})

// ✅ Administrative operation (intentional bypass)
await payload.find({
  collection: 'posts',
  // No user - overrideAccess defaults to true for admin operations
})
```

**Golden Rule**: When passing `user` to Local API, ALWAYS set `overrideAccess: false`

### 2. Transaction Safety in Hooks

```typescript
// ❌ DATA CORRUPTION RISK: Separate transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        // Missing req - runs in separate transaction!
      })
    },
  ],
}

// ✅ ATOMIC: Same transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        req, // Pass req for atomic operation
      })
    },
  ],
}
```

**Rule**: Always pass `req` to nested operations in hooks to maintain transaction integrity.

## Basic Operations

### Initialize Payload

```typescript
import payload from 'payload'

await payload.init({
  // config options
})

// Now you can use payload.find(), payload.create(), etc.
```

### Create Document

```typescript
const post = await payload.create({
  collection: 'posts',
  data: {
    title: 'My Post',
    content: 'Hello world',
    author: userId,
  },
  req, // Optional: for access control and transactions
})
```

### Find Documents

```typescript
// Basic query
const posts = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 1,
})

// With where clause
const publishedPosts = await payload.find({
  collection: 'posts',
  where: {
    status: { equals: 'published' },
  },
})

// With sorting
const recentPosts = await payload.find({
  collection: 'posts',
  sort: '-createdAt',
})

// With user context (enforces access control)
const userPosts = await payload.find({
  collection: 'posts',
  user: req.user,
  overrideAccess: false, // CRITICAL!
})
```

### Update Document

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: postId,
  data: {
    title: 'Updated Title',
  },
  req,
})
```

### Delete Document

```typescript
await payload.delete({
  collection: 'posts',
  id: postId,
  req,
})
```

## Query Operations

### Where Clause Operators

```typescript
// Equality
where: { status: { equals: 'published' } }

// Inequality
where: { status: { not_in: ['draft', 'archived'] } }

// Comparison
where: { price: { greater_than: 100 } }
where: { age: { less_than: 18 } }

// Contains (text search)
where: { title: { like: 'hello' } }

// Array operations
where: { categories: { in: ['tech', 'news'] } }
where: { tags: { contains: 'javascript' } }

// Logical operators
where: {
  or: [
    { status: { equals: 'published' } },
    { status: { equals: 'featured' } },
  ],
}

where: {
  and: [
    { status: { equals: 'published' } },
    { price: { less_than: 100 } },
  ],
}
```

### Population (Depth)

```typescript
// Populate relationships up to 2 levels deep
const posts = await payload.find({
  collection: 'posts',
  depth: 2,
})

// Post -> Author (depth 1)
// Post -> Author -> Roles (depth 2)
```

### Pagination

```typescript
const result = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 1,
})

// Result structure:
{
  docs: Post[],
  hasNextPage: boolean,
  hasPrevPage: boolean,
  nextPage: number | null,
  page: number,
  prevPage: number | null,
  totalDocs: number,
  totalPages: number,
}
```

### Count Documents

```typescript
const count = await payload.count({
  collection: 'posts',
  where: { status: { equals: 'published' } },
})

console.log(count.totalDocs) // 42
```

## Transactions

### Explicit Transactions

```typescript
async function createOrderWithTransaction(data) {
  const session = await payload.db.beginTransaction()
  
  try {
    // Create order
    const order = await payload.create({
      collection: 'orders',
      data,
      req: { ...req, context: { transactionID: session.id } },
    })
    
    // Create order items
    for (const item of data.items) {
      await payload.create({
        collection: 'order-items',
        data: { order: order.id, ...item },
        req: { ...req, context: { transactionID: session.id } },
      })
    }
    
    // Commit transaction
    await payload.db.commitTransaction(session)
    
    return order
  } catch (error) {
    // Rollback on error
    await payload.db.rollbackTransaction(session)
    throw error
  }
}
```

### Hook Transactions (Automatic)

When you pass `req` in hooks, operations are automatically part of the same transaction:

```typescript
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      // This is atomic with the parent operation
      await req.payload.create({
        collection: 'audit-log',
        data: { 
          docId: doc.id,
          action: 'update' 
        },
        req, // Pass req for same transaction
      })
    },
  ],
}
```

## Local API in Next.js Routes

### GET Route (Read)

```typescript title="app/api/posts/route.ts"
import { getPayload } from 'payload'
import { config as payloadConfig } from '@/payload.config'

export async function GET(request: Request) {
  const payload = await getPayload({ config: payloadConfig })
  const { searchParams } = new URL(request.url)
  const page = parseInt(searchParams.get('page') || '1')
  
  const posts = await payload.find({
    collection: 'posts',
    depth: 2,
    limit: 10,
    page,
    where: {
      status: { equals: 'published' },
    },
  })
  
  return Response.json(posts)
}
```

### POST Route (Create)

```typescript title="app/api/posts/route.ts"
import { getPayload } from 'payload'
import { config as payloadConfig } from '@/payload.config'

export async function POST(request: Request) {
  const payload = await getPayload({ config: payloadConfig })
  const data = await request.json()
  
  const post = await payload.create({
    collection: 'posts',
    data,
    req, // Pass request for access control
  })
  
  return Response.json(post, { status: 201 })
}
```

### With Authentication

```typescript title="app/api/posts/route.ts"
import { getPayloadHMR } from '@payloadcms/next/utilities'

export async function GET(request: Request) {
  const payload = await getPayloadHMR({ config: payloadConfig })
  
  // Verify authentication
  const token = request.headers.get('Authorization')?.replace('Bearer ', '')
  const { user } = await payload.authenticate({ token })
  
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // Fetch with user context (enforces access control)
  const posts = await payload.find({
    collection: 'posts',
    user,
    overrideAccess: false, // CRITICAL!
  })
  
  return Response.json(posts)
}
```

## Globals API

### Get Global

```typescript
const siteConfig = await payload.findGlobal({
  slug: 'site-config',
})
```

### Update Global

```typescript
const updated = await payload.updateGlobal({
  slug: 'site-config',
  data: {
    siteName: 'My Site',
  },
})
```

## Drafts and Versions

### Create Draft

```typescript
const draft = await payload.create({
  collection: 'posts',
  data: {
    title: 'My Post',
    content: '...',
    _status: 'draft',
  },
  draft: true, // Save as draft
})
```

### Publish Draft

```typescript
const published = await payload.updateVersion({
  collection: 'posts',
  id: postId,
  data: {
    _status: 'published',
  },
  draft: false,
})
```

### Get Latest Version

```typescript
const latest = await payload.findOne({
  collection: 'posts',
  id: postId,
  draft: true, // Include drafts
})
```

## Common Patterns

### Fetch with User Permissions

```typescript
// In Next.js route handler
export async function GET(request: Request) {
  const payload = await getPayloadHMR({ config: payloadConfig })
  
  // Authenticate user
  const token = request.headers.get('Authorization')?.replace('Bearer ', '')
  const authResult = await payload.authenticate({ token })
  
  // Fetch with access control
  const docs = await payload.find({
    collection: 'posts',
    user: authResult.user,
    overrideAccess: false, // Enforce permissions!
  })
  
  return Response.json(docs)
}
```

### Bulk Operations

```typescript
// Create multiple documents in transaction
async function createBulkPosts(postsData) {
  const results = []
  
  for (const postData of postsData) {
    const post = await payload.create({
      collection: 'posts',
      data: postData,
      req,
    })
    results.push(post)
  }
  
  return results
}
```

### Conditional Access Control

```typescript
// Admin sees all, users see only their own
const posts = await payload.find({
  collection: 'posts',
  user: req.user,
  overrideAccess: false,
  where: req.user?.roles?.includes('admin') 
    ? {} // No filter for admins
    : { author: { equals: req.user.id } }, // Filter for regular users
})
```

## Error Handling

### Try-Catch Pattern

```typescript
try {
  const post = await payload.create({
    collection: 'posts',
    data: postData,
  })
} catch (error) {
  if (error.name === 'ValidationError') {
    // Handle validation errors
    console.error('Validation failed:', error.errors)
  } else if (error.name === 'DuplicateKeyError') {
    // Handle duplicate key
    console.error('Document already exists')
  } else {
    // Handle other errors
    console.error('Unexpected error:', error)
  }
}
```

### Validation Errors

```typescript
try {
  await payload.create({
    collection: 'posts',
    data: { title: '' }, // Missing required field
  })
} catch (error) {
  // error.errors contains validation details
  console.log(error.errors)
}
```

## Performance Tips

1. **Use `depth` parameter** to limit relationship population
2. **Add indexes** to frequently queried fields
3. **Use projections** to fetch only needed fields
4. **Enable caching** for read-heavy operations
5. **Batch operations** when possible
6. **Use transactions** for related operations

## Troubleshooting

### Access Control Not Working

**Problem**: Local API bypassing access control

**Solution**: Always set `overrideAccess: false` when passing user:
```typescript
await payload.find({
  collection: 'posts',
  user: req.user,
  overrideAccess: false, // Required!
})
```

### Transaction Not Rolling Back

**Problem**: Operations not rolling back on error

**Solution**: Ensure you pass `req` to all nested operations and properly catch errors.

### Type Errors

**Problem**: TypeScript doesn't recognize types

**Solution**: Run `bun run generate:types` after schema changes.
