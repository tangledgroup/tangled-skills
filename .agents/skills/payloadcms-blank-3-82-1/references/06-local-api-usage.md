# Local API Usage

Complete guide to using Payload's Local API for database operations, queries, and data manipulation in server-side code.

## Getting Payload Instance

### In Next.js Route Handlers

```typescript
import { getPayload } from 'payload'
import config from '@payload-config'

export const GET = async () => {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
  })
  
  return Response.json(posts)
}
```

### In Server Components

```typescript
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function PostsPage() {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
  })
  
  return (
    <div>
      {posts.docs.map(post => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  )
}
```

### In Hooks and Access Control

The Payload instance is available via `req.payload`:

```typescript
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      // Use req.payload for database operations
      await req.payload.create({
        collection: 'audit-log',
        data: { documentId: doc.id },
        req, // Pass req for transaction safety
      })
    },
  ],
}
```

### In Custom Endpoints

```typescript
const customEndpoint: Endpoint = {
  path: '/api/custom',
  handler: async (req) => {
    // req.payload is available directly
    const docs = await req.payload.find({
      collection: 'posts',
    })
    
    return Response.json(docs)
  },
}
```

## CRUD Operations

### Create Documents

**Basic create:**

```typescript
const post = await payload.create({
  collection: 'posts',
  data: {
    title: 'My First Post',
    content: 'Post content here...',
    status: 'draft',
  },
})
```

**Create with authentication context:**

```typescript
const { user } = await payload.auth({ request })

const post = await payload.create({
  collection: 'posts',
  data: {
    title: 'User Post',
    author: user.id, // Auto-set author
  },
  req: { user }, // Pass request context for hooks
})
```

**Create draft (skip validation):**

```typescript
const draft = await payload.create({
  collection: 'posts',
  data: { title: 'Draft Post' },
  draft: true, // Skips required field validation
})
```

**Create with file upload:**

```typescript
import { readFileSync } from 'fs'

const buffer = readFileSync('/path/to/image.jpg')

const media = await payload.create({
  collection: 'media',
  data: {
    alt: 'Uploaded image',
  },
  file: {
    buffer,
    mimetype: 'image/jpeg',
    originalFilename: 'image.jpg',
  },
})
```

### Read Documents

**Find by ID:**

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: 'cmjxkexample123',
  
  // Optional: populate relationships
  depth: 2, // Depth of relationship population (default: 2)
  
  // Optional: return draft version
  draft: true,
})
```

**Find multiple documents:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  
  // Pagination
  limit: 10, // Results per page (default: 10)
  page: 1,   // Page number (default: 1)
  
  // Sorting
  sort: '-createdAt', // Sort by field (negative for descending)
  
  // Populate relationships
  depth: 2,
  
  // Select specific fields
  select: {
    title: true,
    slug: true,
    author: true,
  },
})

// Response structure:
{
  docs: Post[],     // Array of documents
  hasNextPage: bool,
  hasPrevPage: bool,
  limit: number,
  nextPage: number | null,
  page: number,
  pagingCounter: number,
  prevPage: number | null,
  totalDocs: number,
  totalPages: number,
}
```

**Find with query filters:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  where: {
    and: [
      { _status: { equals: 'published' } },
      { author: { equals: 'user-id-123' } },
    ],
  },
})
```

See [Query Operators](#query-operators) for complete operator reference.

### Update Documents

**Update by ID:**

```typescript
const updated = await payload.update({
  collection: 'posts',
  id: 'cmjxkexample123',
  data: {
    title: 'Updated Title',
    status: 'published',
  },
})
```

**Update with authentication:**

```typescript
const updated = await payload.update({
  collection: 'posts',
  id: 'cmjxkexample123',
  data: { status: 'published' },
  req: { user }, // Pass request context
})
```

**Update draft:**

```typescript
const draft = await payload.update({
  collection: 'posts',
  id: 'cmjxkexample123',
  data: { content: 'Updated content' },
  draft: true, // Update draft version only
})
```

### Delete Documents

**Delete by ID:**

```typescript
await payload.delete({
  collection: 'posts',
  id: 'cmjxkexample123',
})
```

**Delete with authentication:**

```typescript
await payload.delete({
  collection: 'posts',
  id: 'cmjxkexample123',
  req: { user },
})
```

## Query Operators

### Basic Operators

**Equals:**

```typescript
{ status: { equals: 'published' } }
{ author: { equals: 'user-id-123' } }
```

**Not Equals:**

```typescript
{ status: { not_equals: 'draft' } }
```

**Contains (case-insensitive):**

```typescript
{ title: { contains: 'payload' } }
{ content: { contains: 'tutorial' } }
```

**Like (all words must be present):**

```typescript
{ description: { like: 'cms headless' } }
```

**Greater Than / Less Than:**

```typescript
{ price: { greater_than: 100 } }
{ age: { less_than: 65 } }
{ views: { greater_than_equal: 1000 } }
{ score: { less_than_equal: 90 } }
```

**In Array:**

```typescript
{ category: { in: ['tech', 'news', 'sports'] } }
{ status: { in: ['published', 'scheduled'] } }
```

**Not In Array:**

```typescript
{ status: { not_in: ['draft', 'archived'] } }
```

**Exists:**

```typescript
{ coverImage: { exists: true } }   // Has value
{ comments: { exists: false } }    // No value
```

### Date Operators

**Before / After:**

```typescript
{ publishedAt: { less_than: '2024-01-01T00:00:00.000Z' } }
{ createdAt: { greater_than: '2024-01-01T00:00:00.000Z' } }

// Or use Date objects
{ publishedAt: { less_than: new Date('2024-01-01') } }
```

**Between:**

```typescript
{
  and: [
    { createdAt: { greater_than_equal: '2024-01-01' } },
    { createdAt: { less_than_equal: '2024-12-31' } },
  ]
}
```

### Array Operators

**Contains (array field):**

```typescript
{ tags: { contains: 'javascript' } } // Array contains value
{ categories: { equals: ['tech', 'news'] } } // Exact match
```

### Geospatial Operators

**Near (coordinates + distance in meters):**

```typescript
{
  location: {
    near: [-122.4194, 37.7749, 10000] // [longitude, latitude, radius]
  }
}
```

**Within polygon:**

```typescript
{
  location: {
    within: {
      type: 'Polygon',
      coordinates: [[
        [-122.5, 37.7],
        [-122.4, 37.7],
        [-122.4, 37.8],
        [-122.5, 37.8],
        [-122.5, 37.7],
      ]],
    },
  }
}
```

### Logical Operators

**AND (all conditions must be true):**

```typescript
{
  and: [
    { status: { equals: 'published' } },
    { featured: { equals: true } },
    { 'author.name': { contains: 'john' } },
  ]
}
```

**OR (any condition can be true):**

```typescript
{
  or: [
    { status: { equals: 'published' } },
    { author: { equals: user.id } },
  ]
}
```

**NOT (negate condition):**

```typescript
{
  not: {
    status: { equals: 'draft' }
  }
}
```

**Complex combinations:**

```typescript
{
  and: [
    { 
      or: [
        { status: { equals: 'published' } },
        { author: { equals: user.id } },
      ]
    },
    { featured: { equals: true } },
  ]
}
```

### Nested Field Queries

**Dot notation for nested fields:**

```typescript
// Query group fields
{ 'address.city': { equals: 'New York' } }
{ 'settings.public': { equals: true } }

// Query relationship fields
{ 'author.email': { contains: '@company.com' } }
{ 'author.roles': { contains: 'admin' } }

// Query array fields
{ 'tags.0': { equals: 'javascript' } } // First tag
```

## Relationship Population

### Depth Parameter

The `depth` parameter controls how many levels of relationships to populate:

```typescript
// depth: 0 - No population (default for performance)
const posts = await payload.find({
  collection: 'posts',
  depth: 0, // Returns IDs only: { author: 'user-id-123' }
})

// depth: 1 - Populate one level
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Populates author: { author: { id, email, ... } }
})

// depth: 2 - Populate two levels (default)
const posts = await payload.find({
  collection: 'posts',
  depth: 2, // Populates author and author's relationships
})
```

### Select Specific Fields

Limit returned fields for performance:

```typescript
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    excerpt: true,
    author: {
      id: true,
      name: true,
      avatar: true,
    },
  },
})
```

## Advanced Queries

### Count Documents

```typescript
const count = await payload.count({
  collection: 'posts',
  where: {
    status: { equals: 'published' },
  },
})

// Returns: { totalDocs: number }
```

### Find One Document

```typescript
const post = await payload.findOne({
  collection: 'posts',
  where: {
    slug: { equals: 'my-post-slug' },
  },
})
```

### Sort Documents

**Single field:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  sort: 'createdAt', // Ascending (default)
  
  // Or descending
  sort: '-createdAt',
})
```

**Multiple fields:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  sort: ['author', 'title'], // Sort by author, then title
  
  // Mixed order
  sort: ['-status', 'title'], // Status descending, title ascending
})
```

### Pagination

**Using page/limit:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 2, // Second page
})

// Navigate pages
if (posts.hasNextPage) {
  const nextPage = await payload.find({
    collection: 'posts',
    limit: 10,
    page: posts.nextPage,
  })
}
```

**Using skip/limit:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  limit: 10,
  skip: 20, // Skip first 20 results
})
```

## Working with Drafts and Versions

### Create Draft

```typescript
const draft = await payload.create({
  collection: 'posts',
  data: {
    title: 'Draft Post',
    // Required fields can be omitted when draft: true
  },
  draft: true,
})
```

### Read Draft

```typescript
// Get published version (default)
const published = await payload.findByID({
  collection: 'posts',
  id: '123',
})

// Get draft version if available
const draft = await payload.findByID({
  collection: 'posts',
  id: '123',
  draft: true,
})
```

### Publish Draft

```typescript
const published = await payload.update({
  collection: 'posts',
  id: '123',
  data: {
    _status: 'published', // Change status to publish
  },
})
```

### Get Version History

```typescript
const versions = await payload.findVersions({
  collection: 'posts',
  where: {
    parent: { equals: 'post-id-123' },
  },
})

// Restore a version
const restored = await payload.restoreVersion({
  collection: 'posts',
  id: 'version-id-456',
})
```

## Authentication Operations

### Check Authentication

```typescript
const { user } = await payload.auth({
  headers, // Or request object
})

if (user) {
  console.log('User is authenticated:', user.email)
} else {
  console.log('User is not authenticated')
}
```

### Get User by ID

```typescript
const user = await payload.findByID({
  collection: 'users',
  id: 'user-id-123',
})
```

### Access Control Enforcement

**Enforce user permissions:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  user, // Pass authenticated user
  overrideAccess: false, // CRITICAL: Enforce their permissions
})
```

**Admin operation (bypass access control):**

```typescript
const allPosts = await payload.find({
  collection: 'posts',
  // No user parameter, runs as admin
  // overrideAccess defaults to true
})
```

See [Security Patterns](04-security-patterns.md) for critical access control guidance.

## Transactions

### MongoDB Transactions

Requires replica set configuration:

```typescript
const result = await payload.executeTransaction(async (tx) => {
  const payloadTx = tx.payload
  
  // All operations in same transaction
  const post = await payloadTx.create({
    collection: 'posts',
    data: { title: 'Transaction Post' },
  })
  
  const comment = await payloadTx.create({
    collection: 'comments',
    data: { post: post.id, text: 'Auto-comment' },
  })
  
  return { post, comment }
})
```

### PostgreSQL Transactions

Work out of the box:

```typescript
const result = await payload.executeTransaction(async (tx) => {
  const payloadTx = tx.payload
  
  // Atomic operations
  const user = await payloadTx.create({
    collection: 'users',
    data: { email: 'test@example.com' },
  })
  
  const profile = await payloadTx.create({
    collection: 'profiles',
    data: { user: user.id, bio: 'Hello' },
  })
  
  return { user, profile }
})
```

## Bulk Operations

### Batch Create

```typescript
const posts = await Promise.all(
  [
    { title: 'Post 1', content: 'Content 1' },
    { title: 'Post 2', content: 'Content 2' },
    { title: 'Post 3', content: 'Content 3' },
  ].map(data =>
    payload.create({
      collection: 'posts',
      data,
    })
  )
)
```

### Batch Update

```typescript
const postIds = ['id1', 'id2', 'id3']

await Promise.all(
  postIds.map(id =>
    payload.update({
      collection: 'posts',
      id,
      data: { featured: true },
    })
  )
)
```

### Batch Delete

```typescript
const postIds = ['id1', 'id2', 'id3']

await Promise.all(
  postIds.map(id =>
    payload.delete({
      collection: 'posts',
      id,
    })
  )
)
```

## Performance Optimization

### Use Select to Limit Fields

```typescript
// Bad: Returns all fields
const posts = await payload.find({
  collection: 'posts',
})

// Good: Only return needed fields
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    excerpt: true,
  },
})
```

### Limit Depth for Relationships

```typescript
// Bad: Deep population can be slow
const posts = await payload.find({
  collection: 'posts',
  depth: 10, // Very deep!
})

// Good: Limit to necessary depth
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only author, not author's relationships
})
```

### Index Frequently Queried Fields

Define indexes in collection config:

```typescript
{
  name: 'slug',
  type: 'text',
  index: true, // Database index for faster queries
}

{
  name: 'status',
  type: 'select',
  index: true,
}
```

### Use Pagination

Always paginate list queries:

```typescript
const posts = await payload.find({
  collection: 'posts',
  limit: 10, // Never fetch all without limit
  page: 1,
})
```

### Cache Expensive Queries

```typescript
import { cache } from 'react'

const getPublishedPosts = cache(async () => {
  const payload = await getPayload({ config })
  
  return payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    limit: 50,
  })
})

// In component
const posts = await getPublishedPosts()
```

## Error Handling

### Handle Not Found

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: '123',
})

if (!post) {
  throw new Error('Post not found')
}
```

### Handle Validation Errors

```typescript
try {
  const post = await payload.create({
    collection: 'posts',
    data: { title: '' }, // Missing required field
  })
} catch (error) {
  if (error.name === 'ValidationError') {
    console.log('Validation failed:', error.message)
  } else {
    throw error
  }
}
```

### Handle Access Errors

```typescript
try {
  const secret = await payload.findByID({
    collection: 'secrets',
    id: '123',
    user,
    overrideAccess: false,
  })
} catch (error) {
  if (error.name === 'Forbidden') {
    console.log('User does not have permission')
  }
}
```

## Common Patterns

### Get User's Documents

```typescript
async function getUserPosts(userId: string) {
  const payload = await getPayload({ config })
  
  return payload.find({
    collection: 'posts',
    where: { author: { equals: userId } },
    sort: '-createdAt',
  })
}
```

### Search Documents

```typescript
async function searchPosts(query: string) {
  const payload = await getPayload({ config })
  
  return payload.find({
    collection: 'posts',
    where: {
      or: [
        { title: { contains: query } },
        { content: { contains: query } },
        { excerpt: { contains: query } },
      ],
    },
    limit: 20,
  })
}
```

### Get Related Documents

```typescript
async function getRelatedPosts(currentPostId: string, tagIds: string[]) {
  const payload = await getPayload({ config })
  
  return payload.find({
    collection: 'posts',
    where: {
      and: [
        { id: { not_equals: currentPostId } },
        { tags: { in: tagIds } },
        { _status: { equals: 'published' } },
      ],
    },
    sort: '-createdAt',
    limit: 5,
  })
}
```

### Count by Status

```typescript
async function getPostStats() {
  const payload = await getPayload({ config })
  
  const [published, drafts, archived] = await Promise.all([
    payload.count({
      collection: 'posts',
      where: { _status: { equals: 'published' } },
    }),
    payload.count({
      collection: 'posts',
      where: { _status: { equals: 'draft' } },
    }),
    payload.count({
      collection: 'posts',
      where: { _status: { equals: 'archived' } },
    }),
  ])
  
  return { published, drafts, archived }
}
```

## Type Safety

### Import Generated Types

```typescript
import type { Post, User } from '@/payload-types'

async function getPost(id: string): Promise<Post | null> {
  const payload = await getPayload({ config })
  
  return payload.findByID({
    collection: 'posts',
    id,
  })
}
```

### Type Guards for Optional Fields

```typescript
import type { Post } from '@/payload-types'

function displayAuthor(post: Post) {
  if ('author' in post && post.author) {
    // TypeScript knows author exists
    console.log(post.author.email)
  }
}
```

See [Collection Configuration](03-collection-configuration.md) for type generation details.
