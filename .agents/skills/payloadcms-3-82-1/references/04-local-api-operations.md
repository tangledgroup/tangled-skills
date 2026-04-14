# Local API Operations Reference

Complete guide to programmatic database operations using Payload's Local API with proper security practices and transaction management.

## Getting Payload Instance

### In API Routes (Next.js)

```typescript
// app/api/posts/route.ts
import { getPayload } from 'payload'
import config from '@payload-config'

export async function GET() {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
  })
  
  return Response.json(posts)
}
```

### In Server Components

```typescript
// app/page.tsx
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function Page() {
  const payload = await getPayload({ config })
  
  const { docs } = await payload.find({
    collection: 'posts',
    limit: 10,
  })
  
  return (
    <div>
      {docs.map(post => (
        <h1 key={post.id}>{post.title}</h1>
      ))}
    </div>
  )
}
```

### In Custom Endpoints

```typescript
import type { Endpoint } from 'payload'

export const customEndpoint: Endpoint = {
  path: '/api/custom/posts',
  method: 'get',
  handler: async (req) => {
    // Use req.payload in endpoints (already initialized)
    const posts = await req.payload.find({
      collection: 'posts',
    })
    
    return Response.json(posts)
  },
}
```

### In Hooks

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    afterChange: [
      async ({ doc, req }) => {
        // Use req.payload in hooks (maintains transaction context)
        await req.payload.create({
          collection: 'audit-log',
          data: {
            action: 'post_created',
            documentId: doc.id,
          },
          req, // CRITICAL: Pass req for transaction safety
        })
      },
    ],
  },
}
```

## ⚠️ Security Critical Patterns

### Access Control Enforcement

**Most common security vulnerability - ALWAYS enforce access control:**

```typescript
// ❌ SECURITY BUG: Access control bypassed (runs as admin)
await payload.find({
  collection: 'posts',
  user: someUser, // Ignored without overrideAccess: false!
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
  // No user passed, overrideAccess defaults to true (admin privileges)
})
```

**Rule**: When passing `user` to Local API, ALWAYS set `overrideAccess: false`

### Transaction Safety

**Maintain atomicity in nested operations:**

```typescript
// ❌ DATA CORRUPTION: Separate transaction
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
        req, // Maintains atomicity with parent operation
      })
    },
  ],
}
```

**Rule**: ALWAYS pass `req` to nested operations in hooks

### Prevent Infinite Loops

**Use context flags to prevent recursive hook execution:**

```typescript
// ❌ INFINITE LOOP
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        req,
      }) // Triggers afterChange again!
    },
  ],
}

// ✅ SAFE: Use context flag
hooks: {
  afterChange: [
    async ({ doc, req, context }) => {
      if (context.skipHooks) return

      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        context: { skipHooks: true }, // Prevent recursion
        req,
      })
    },
  ],
}
```

## Find Operations

### Basic Find

```typescript
const result = await payload.find({
  collection: 'posts',
})

// Result structure
{
  docs: Post[],     // Array of documents
  totalDocs: number,
  offset: number,
  limit: number,
  hasNextPage: boolean,
}
```

### Find with Query

```typescript
const posts = await payload.find({
  collection: 'posts',
  where: {
    and: [
      { status: { equals: 'published' } },
      { 'author.name': { contains: 'john' } },
    ],
  },
})
```

### Pagination

```typescript
const page = 1
const limit = 10

const posts = await payload.find({
  collection: 'posts',
  page,
  limit,
})

// Access pagination info
console.log(posts.totalDocs)     // Total matching documents
console.log(posts.hasNextPage)   // Whether more pages exist
```

### Sorting

```typescript
// Single field sort
const posts = await payload.find({
  collection: 'posts',
  sort: '-createdAt', // Descending (use '-' prefix)
})

// Multiple fields (not directly supported, use custom logic)
```

### Field Selection

Limit returned fields for performance:

```typescript
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    author: true, // Include relationship
    createdAt: true,
  },
})
```

### Relationship Population

Control relationship depth with `depth` parameter:

```typescript
// Default depth is 2
const posts = await payload.find({
  collection: 'posts',
  depth: 2, // Populate relationships up to 2 levels deep
})

// Depth 0 - return only IDs
const posts = await payload.find({
  collection: 'posts',
  depth: 0, // author: { relationTo: 'users', value: '64f12345...' }
})

// Max depth to prevent over-fetching
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only populate direct relationships
  maxDepth: 1, // Never go deeper than 1 level
})
```

### Draft Reads

Access draft versions when enabled:

```typescript
// Read published version (default)
const post = await payload.findByID({
  collection: 'posts',
  id: '123',
})

// Read draft version if available
const draftPost = await payload.findByID({
  collection: 'posts',
  id: '123',
  draft: true, // Return draft if exists, otherwise published
})
```

## Find by ID

### Basic Find by ID

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: '64f1234567890abcdef12345', // MongoDB ObjectId or number for PostgreSQL
})

// With relationship population
const post = await payload.findByID({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  depth: 2,
})
```

### Error Handling

```typescript
try {
  const post = await payload.findByID({
    collection: 'posts',
    id: 'invalid-id',
  })
} catch (error) {
  if (error.name === 'NotFoundError') {
    console.log('Document not found')
  }
}
```

## Create Operations

### Basic Create

```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'New Post',
    content: '<p>Post content</p>',
    status: 'draft',
  },
})
```

### Create with Relationships

```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'New Post',
    author: '64f1234567890abcdef12345', // User ID
    categories: ['64f111', '64f222'], // Array of category IDs
  },
  depth: 1, // Populate relationships in response
})
```

### Create Draft

Bypass required field validation for drafts:

```typescript
const draftPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'Draft Post',
    // Other required fields can be omitted
  },
  draft: true, // Skip required field validation
})
```

### Create with Access Control

Enforce user permissions during creation:

```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'User Post',
    content: 'Post content',
  },
  user: currentUser, // User context
  overrideAccess: false, // Enforce access control
})
```

## Update Operations

### Update by ID

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  data: {
    status: 'published',
  },
})
```

### Partial Update

Only update specified fields:

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  data: {
    title: 'Updated Title',
    // Other fields remain unchanged
  },
})
```

### Update with Access Control

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  data: { status: 'published' },
  user: currentUser,
  overrideAccess: false, // Enforce user permissions
})
```

### Update with Hooks Control

Skip hooks to prevent infinite loops:

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  data: { views: currentViews + 1 },
  context: { skipHooks: true }, // Prevent hook recursion
  req,
})
```

## Delete Operations

### Basic Delete

```typescript
const deletedPost = await payload.delete({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
})
```

### Delete with Access Control

```typescript
const deletedPost = await payload.delete({
  collection: 'posts',
  id: '64f1234567890abcdef12345',
  user: currentUser,
  overrideAccess: false, // Enforce delete permissions
})
```

### Cascade Delete

Delete related documents:

```typescript
hooks: {
  beforeDelete: [
    async ({ req, id }) => {
      // Delete all comments for this post
      await req.payload.delete({
        collection: 'comments',
        where: { post: { equals: id } },
        req, // Maintain transaction
      })
    },
  ],
}
```

## Document Operations

### Count Documents

```typescript
const count = await payload.count({
  collection: 'posts',
  where: {
    status: { equals: 'published' },
  },
})

// Returns: { totalDocs: 42 }
```

### Bulk Operations

Multiple documents in one operation:

```typescript
// Find many and process
const { docs } = await payload.find({
  collection: 'posts',
  where: { status: { equals: 'draft' } },
  limit: 100,
})

// Update each document
for (const post of docs) {
  await payload.update({
    collection: 'posts',
    id: post.id,
    data: { status: 'published' },
    req, // Maintain transaction context
  })
}
```

## Query Operators

### Basic Operators

```typescript
// Equals (default)
{ status: 'published' }
{ status: { equals: 'published' } }

// Not equals
{ status: { not_equals: 'draft' } }

// Contains (case-insensitive substring)
{ title: { contains: 'payload' } }

// Like (all words must be present)
{ description: { like: 'cms headless' } }

// Greater than / less than
{ price: { greater_than: 100 } }
{ price: { greater_than_equal: 100 } }
{ age: { less_than: 65 } }
{ age: { less_than_equal: 65 } }
```

### Array Operators

```typescript
// In array (value is in list)
{ category: { in: ['tech', 'news', 'updates'] } }

// Not in array
{ status: { not_in: ['draft', 'archived'] } }

// Near me (array contains value)
{ tags: { near: 'javascript' } }

// All (array contains all values)
{ roles: { all: ['editor', 'author'] } }
```

### Existence Operators

```typescript
// Field exists and is not null
{ author: { exists: true } }

// Field does not exist or is null
{ author: { exists: false } }
```

### Geospatial Operators

```typescript
// Near coordinates (latitude, longitude, distance in meters)
{ location: { near: [-122.4194, 37.7749, 10000] } }

// Within polygon
{ location: { within: { type: 'Polygon', coordinates: [...] } } }
```

### Date Operators

```typescript
// Between dates
{
  publishedAt: {
    greater_than_equal: '2024-01-01T00:00:00.000Z',
    less_than_equal: '2024-12-31T23:59:59.999Z',
  }
}

// Before/after
{ publishedAt: { less_than: new Date().toISOString() } }
```

## Complex Queries

### AND Logic

```typescript
const posts = await payload.find({
  collection: 'posts',
  where: {
    and: [
      { status: { equals: 'published' } },
      { featured: { equals: true } },
      { 'author.name': { contains: 'john' } },
    ],
  },
})
```

### OR Logic

```typescript
const posts = await payload.find({
  collection: 'posts',
  where: {
    or: [
      { status: { equals: 'published' } },
      { author: { equals: currentUser.id } },
    ],
  },
})
```

### Nested Queries

Query nested field values:

```typescript
// Query group fields
const posts = await payload.find({
  collection: 'posts',
  where: {
    'seo.metaTitle': { contains: 'payload' },
  },
})

// Query array fields
const posts = await payload.find({
  collection: 'posts',
  where: {
    'tags': { near: 'javascript' },
  },
})

// Query relationship fields
const posts = await payload.find({
  collection: 'posts',
  where: {
    'author.name': { equals: 'John Doe' },
  },
})
```

## Version Operations

### Get Versions

Retrieve document versions:

```typescript
const versions = await payload.versions.getVersions({
  collection: 'posts',
  where: { docID: { equals: postID } },
})

// Returns array of versions with version data
```

### Restore Version

Restore a specific version:

```typescript
const restoredDoc = await payload.versions.restoreVersion({
  collection: 'posts',
  versionID: '64f1234567890abcdef12345',
})
```

## Global Operations

### Find Global

```typescript
const header = await payload.findGlobal({
  slug: 'header',
})
```

### Update Global

```typescript
const updatedHeader = await payload.updateGlobal({
  slug: 'header',
  data: {
    navItems: [
      { label: 'Home', url: '/' },
      { label: 'About', url: '/about' },
    ],
  },
})
```

## Context and Options

### Using Context

Pass custom data through operation chain:

```typescript
const post = await payload.create({
  collection: 'posts',
  data: { title: 'New Post' },
  context: {
    skipNotifications: true,
    userId: currentUser.id,
    source: 'admin-panel',
  },
})

// Access context in hooks
hooks: {
  afterChange: [
    async ({ doc, context }) => {
      if (!context.skipNotifications) {
        await sendNotification(doc)
      }
    },
  ],
}
```

### Request Context

Use req.context for shared data:

```typescript
// Cache expensive lookups in request context
const getUserPermissions = async (req) => {
  if (!req.context.userPermissions) {
    req.context.userPermissions = await fetchUserPermissions(req.user)
  }
  return req.context.userPermissions
}
```

## Error Handling

### Try-Catch Pattern

```typescript
try {
  const post = await payload.findByID({
    collection: 'posts',
    id: 'invalid-id',
  })
} catch (error) {
  if (error.name === 'NotFoundError') {
    console.log('Document not found')
    return Response.json({ error: 'Not found' }, { status: 404 })
  }
  
  if (error.name === 'ValidationError') {
    console.log('Validation failed:', error.data)
    return Response.json({ error: error.message }, { status: 400 })
  }
  
  // Unexpected error
  console.error('Unexpected error:', error)
  return Response.json({ error: 'Internal server error' }, { status: 500 })
}
```

### Common Error Types

- `NotFoundError`: Document doesn't exist
- `ValidationError`: Data validation failed
- `UnauthorizedError`: Access control denied
- `DuplicateError`: Unique constraint violated
- `ForbiddenError`: Insufficient permissions

## Performance Optimization

### Use Select for Large Documents

```typescript
// Only fetch needed fields
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    createdAt: true,
  },
})
```

### Limit Relationship Depth

```typescript
// Prevent over-fetching
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only direct relationships
  maxDepth: 2, // Never go deeper than 2 levels
})
```

### Index Frequently Queried Fields

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'status', type: 'select', index: true },
    { name: 'slug', type: 'text', unique: true, index: true },
  ],
}
```

### Batch Operations

Process multiple documents efficiently:

```typescript
// Process in batches to avoid memory issues
const processInBatches = async (collection, where, batchSize = 100) => {
  let offset = 0
  let hasMore = true
  
  while (hasMore) {
    const { docs, totalDocs } = await payload.find({
      collection,
      where,
      limit: batchSize,
      offset,
    })
    
    for (const doc of docs) {
      await processDocument(doc)
    }
    
    hasMore = offset + docs.length < totalDocs
    offset += batchSize
  }
}
```

## Transaction Management

### MongoDB Transactions

Require replica set configuration:

```typescript
// Start transaction
await req.payload.db.session.withTransaction(async () => {
  const post = await req.payload.create({
    collection: 'posts',
    data: { title: 'New Post' },
    req,
  })
  
  await req.payload.create({
    collection: 'audit-log',
    data: { action: 'post_created', documentId: post.id },
    req,
  })
  
  // All operations commit together or rollback on error
})
```

### PostgreSQL Transactions

Automatic transaction support:

```typescript
// Operations within hooks automatically share transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      // This runs in same transaction as parent operation
      await req.payload.create({
        collection: 'audit-log',
        data: { action: 'post_created' },
        req, // Pass req to maintain transaction
      })
    },
  ],
}
```

## Best Practices

1. **Always enforce access control**: Set `overrideAccess: false` when passing `user`
2. **Maintain transactions**: Always pass `req` to nested operations in hooks
3. **Prevent infinite loops**: Use context flags to stop recursive hook execution
4. **Limit relationship depth**: Use `depth` and `maxDepth` to prevent over-fetching
5. **Use field selection**: Only fetch needed fields with `select`
6. **Handle errors gracefully**: Catch specific error types and provide meaningful messages
7. **Index query fields**: Add indexes to frequently queried fields
8. **Batch large operations**: Process documents in batches to avoid memory issues
