# Local API and Queries

## The Payload Instance

Initialize the Payload instance to use the Local API:

```typescript
import { getPayload } from 'payload'
import configPromise from '@/payload.config'

const payload = await getPayload({ config: configPromise })
```

In Next.js server components, you can also use `initPayloadFromNextReq` for request-scoped instances with locale and user context.

## Core Operations

### Find (List Documents)

```typescript
const result = await payload.find({
  collection: 'posts',
  where: { _status: { equals: 'published' } },
  limit: 10,
  page: 1,
  sort: '-publishedAt',
  depth: 2,
  locale: 'en',
})

// Returns PaginatedDocs<T>
console.log(result.docs)    // Array of documents
console.log(result.totalDocs) // Total matching count
console.log(result.hasNextPage) // Boolean
```

### Find by ID

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: '123abc',
  depth: 2,
})
```

### Create

```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'Hello World',
    slug: 'hello-world',
    content: { /* rich text JSON */ },
  },
})
```

### Update

```typescript
const updated = await payload.update({
  collection: 'posts',
  id: '123abc',
  data: { title: 'Updated Title' },
})
```

### Delete

```typescript
const deleted = await payload.delete({
  collection: 'posts',
  id: '123abc',
})
```

### Count

```typescript
const count = await payload.count({
  collection: 'posts',
  where: { _status: { equals: 'published' } },
})
// Returns { totalDocs: number }
```

## The Where Query System

The `Where` type supports nested queries with operators:

```typescript
type Where = {
  [key: string]: Where[] | WhereField
  and?: Where[]
  or?: Where[]
}

type WhereField = {
  [operator in Operator]?: JsonValue
}
```

### Available Operators

- `equals` — exact match
- `not_equals` — not equal
- `contains` — substring match
- `exists` — field exists (pass `true` or `false`)
- `like` — SQL LIKE pattern
- `all` — array contains all values
- `in` — value in array
- `not_in` — value not in array
- `greater_than` / `less_than` — numeric/date comparison
- `greater_than_equal` / `less_than_equal` — inclusive comparison

### Query Examples

**Simple equality:**

```typescript
where: { title: { equals: 'Hello World' } }
```

**Multiple conditions (AND):**

```typescript
where: {
  title: { contains: 'hello' },
  _status: { equals: 'published' },
}
```

**Explicit AND/OR:**

```typescript
where: {
  or: [
    { title: { equals: 'Draft 1' } },
    { and: [{ category: { equals: 'news' } }, { _status: { equals: 'published' } }] },
  ],
}
```

**Relationship queries:**

```typescript
// Find posts in a specific category
where: { categories: { equals: 'category-id-123' } }

// With polymorphic relationships
where: { link: { equals: { value: 'page-id', relationTo: 'pages' } } }
```

**Numeric/date ranges:**

```typescript
where: {
  price: { greater_than_equal: 10, less_than_equal: 100 },
  publishedAt: { greater_than_equal: '2024-01-01' },
}
```

**Array operations:**

```typescript
// Find documents where tags array contains 'featured'
where: { tags: { in: ['featured'] } }

// Find where ALL tags match
where: { tags: { all: ['news', 'featured'] } }
```

**Existence checks:**

```typescript
where: { author: { exists: true } }
```

## Depth and Population

The `depth` parameter controls how deeply related documents are populated:

- `depth: 0` — no population, relationships return IDs only
- `depth: 1` — populate one level of relationships
- `depth: 2` (default) — populate two levels
- Configured globally via `config.defaultDepth`

```typescript
const posts = await payload.find({
  collection: 'posts',
  depth: 2, // Populates author and categories with their relations
})
```

## Select / Projection

Use `select` to limit which fields are returned:

```typescript
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    meta: {
      image: true,
      description: true,
    },
  },
})
```

## Pagination

```typescript
const result = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 2,
  pagination: true, // set to false to disable
})

console.log(result.docs)        // Array of documents
console.log(result.totalDocs)   // Total matching
console.log(result.totalPages)  // Total pages
console.log(result.page)        // Current page
console.log(result.hasPrevPage) // Boolean
console.log(result.hasNextPage) // Boolean
```

## Sorting

```typescript
sort: '-publishedAt'          // Descending
sort: 'title'                 // Ascending
sort: ['-createdAt', 'title'] // Multi-field sort
```

## Joins

Joins provide reverse relationship queries:

```typescript
// In a Users collection, find all posts by this user
const user = await payload.findByID({
  collection: 'users',
  id: userId,
  joins: {
    postsByAuthor: {
      limit: 10,
      sort: '-publishedAt',
      where: { _status: { equals: 'published' } },
    },
  },
})
```

## Transactions

Wrap multiple operations in a transaction:

```typescript
await payload.transaction(async (transactionPayload) => {
  const post = await transactionPayload.create({
    collection: 'posts',
    data: { title: 'New Post' },
  })

  await transactionPayload.create({
    collection: 'post-tags',
    data: { post: post.id, tag: 'news' },
  })

  // If any operation throws, all are rolled back
})
```

## Global Operations

```typescript
// Read a global
const header = await payload.findGlobal({ slug: 'header' })

// Update a global
await payload.updateGlobal({
  slug: 'header',
  data: { navItems: [...] },
})
```

## Draft Queries

Query draft documents:

```typescript
const drafts = await payload.find({
  collection: 'posts',
  draft: true,
  where: { _status: { in: ['draft', 'published'] } },
})
```

## Version Operations

```typescript
// Find document versions
const versions = await payload.findVersions({
  collection: 'posts',
  where: { 'version.createdAt': { greater_than: '2024-01-01' } },
})

// Find a specific version
const version = await payload.findVersionByID({
  collection: 'posts',
  id: versionId,
})

// Restore a version
const restored = await payload.restoreVersion({
  collection: 'posts',
  id: versionId,
})
```

## Auth Operations

```typescript
// Login
const { token, user } = await payload.login({
  collection: 'users',
  data: { email: 'user@example.com', password: 'password123' },
})

// Get current user from headers
const { user } = await payload.auth({
  headers: requestHeaders,
})

// Forgot password
await payload.forgotPassword({
  collection: 'users',
  data: { email: 'user@example.com' },
})

// Reset password
await payload.resetPassword({
  collection: 'users',
  data: { token: resetToken, password: 'newPassword', passwordConfirm: 'newPassword' },
})
```

## Data Loader

Deduplicate relationship queries within a single request:

```typescript
// In hooks, use req.payloadDataLoader.find
const relatedPosts = await req.payloadDataLoader.find({
  collection: 'posts',
  where: { categories: { equals: categoryId } },
})
```

## Query Performance Tips

- Use `select` to limit returned fields
- Set appropriate `depth` (0 when you don't need populated relations)
- Use `defaultPopulate` on collections for common relation patterns
- Index frequently queried fields with `indexed: true`
- Use the Data Loader in hooks to avoid N+1 queries
- Prefer `findByID` over `find` with ID filter for single documents
