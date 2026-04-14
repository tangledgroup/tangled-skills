# API Integration

This reference documents REST API, GraphQL API, Local API, and custom route patterns for Payload CMS 3.82.1. The blank template auto-generates API endpoints for all collections and provides multiple ways to interact with data programmatically.

## REST API

### Auto-Generated Endpoints

Payload automatically creates REST endpoints for each collection at `/api/{slug}`:

```
GET    /api/posts           - List documents
GET    /api/posts/:id       - Get single document
POST   /api/posts           - Create document
PUT    /api/posts/:id       - Replace document
PATCH  /api/posts/:id       - Update document
DELETE /api/posts/:id       - Delete document
```

### Authentication Endpoints

For auth-enabled collections (e.g., `users`):

```
POST   /api/users/login                - User login
POST   /api/users/logout               - User logout
POST   /api/users/forgot-password      - Request password reset
POST   /api/users/reset-password       - Reset password with token
POST   /api/users/verify               - Verify email address
GET    /api/users/me                   - Get current user
```

### List Documents

```bash
# Basic list
curl http://localhost:3000/api/posts

# With pagination
curl "http://localhost:3000/api/posts?limit=10&page=2"

# With sorting
curl "http://localhost:3000/api/posts?sort=-createdAt"

# With filtering
curl "http://localhost:3000/api/posts?where[status]=published"

# With population (relationships)
curl "http://localhost:3000/api/posts?depth=1&populate[author]=true"
```

### Query Parameters

**Pagination:**
```
?limit=20&page=1
```

**Sorting:**
```
?sort=title              # Ascending
?sort=-createdAt         # Descending (negative)
?sort=[["title","asc"],["createdAt","desc"]]  # Multiple fields
```

**Filtering:**
```
# Exact match
?where[status]=published

# Array contains
?where[tags]=news

# Comparison operators
?where[price][equals]=99.99
?where[price][greater_than]=50
?where[price][less_than]=100

# Text matching
?where[title][contains]=hello
?where[title][like]=%hello%
?where[title][exists]=true

# Date filtering
?where[publishedAt][gte]=2024-01-01T00:00:00.000Z
?where[publishedAt][lte]=2024-12-31T23:59:59.999Z

# Nested filtering
?where[author][email]=john@example.com

# OR conditions
?where[status][$or]=[published,archived]
```

**Population (Relationships):**
```
# Populate all relationships one level deep
?depth=1

# Specific fields from related docs
?depth=1&populate[author]=true&populate[category]=true

# Nested population (2 levels)
?depth=2

# Limit populated fields
?fields=title,author,createdAt
```

### Get Single Document

```bash
curl http://localhost:3000/api/posts/64f1a2b3c4d5e6f7g8h9i0j1
```

With population:
```bash
curl "http://localhost:3000/api/posts/64f1a2b3c4d5e6f7g8h9i0j1?depth=1"
```

### Create Document

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "<p>Hello World</p>",
    "status": "draft"
  }'
```

### Update Document

**Full replacement (PUT):**
```bash
curl -X PUT http://localhost:3000/api/posts/64f1a2b3c4d5e6f7g8h9i0j1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "<p>Updated content</p>",
    "status": "published"
  }'
```

**Partial update (PATCH):**
```bash
curl -X PATCH http://localhost:3000/api/posts/64f1a2b3c4d5e6f7g8h9i0j1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title"
  }'
```

### Delete Document

```bash
curl -X DELETE http://localhost:3000/api/posts/64f1a2b3c4d5e6f7g8h9i0j1
```

### Authentication Headers

**Cookie-based (browser):**
```javascript
// Cookies set automatically after login
const response = await fetch('/api/posts')
```

**Bearer token (API clients):**
```bash
curl http://localhost:3000/api/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**API key (if enabled):**
```bash
curl http://localhost:3000/api/posts \
  -H "X-API-Key: YOUR_API_KEY"
```

## GraphQL API

### Endpoint

GraphQL is available at `/api/graphql` with Playground UI at `/graphql`.

### Basic Queries

**List documents:**
```graphql
query {
  posts(limit: 10, where: { status: { equals: "published" } }) {
    docs {
      id
      title
      slug
      createdAt
      author {
        email
        name
      }
    }
    totalDocs
    page
    pagingCounter
    totalPages
  }
}
```

**Get single document:**
```graphql
query {
  post(id: "64f1a2b3c4d5e6f7g8h9i0j1") {
    id
    title
    content
    author {
      email
    }
  }
}
```

**Create document:**
```graphql
mutation {
  posts(
    data: {
      title: "New Post"
      slug: "new-post"
      status: "draft"
    }
  ) {
    id
    title
    createdAt
  }
}
```

**Update document:**
```graphql
mutation {
  posts(
    id: "64f1a2b3c4d5e6f7g8h9i0j1"
    data: {
      title: "Updated Title"
    }
  ) {
    id
    title
    updatedAt
  }
}
```

**Delete document:**
```graphql
mutation {
  deletePost(id: "64f1a2b3c4d5e6f7g8h9i0j1") {
    id
    title
  }
}
```

### Authentication Queries

**Login:**
```graphql
mutation {
  loginUser(email: "user@example.com", password: "password123") {
    token
    user {
      id
      email
      role
    }
  }
}
```

**Get current user:**
```graphql
query {
  me {
    user {
      id
      email
      role
    }
  }
}
```

### GraphQL Variables

Use variables for dynamic queries:

```graphql
query GetPosts($status: String, $limit: Int) {
  posts(limit: $limit, where: { status: { equals: $status } }) {
    docs {
      id
      title
    }
    totalDocs
  }
}
```

Variables:
```json
{
  "status": "published",
  "limit": 20
}
```

### GraphQL with Client Libraries

**Using Apollo Client:**
```typescript
import { ApolloClient, InMemoryCache, gql, createHttpLink } from '@apollo/client'

const client = new ApolloClient({
  link: createHttpLink({
    uri: '/api/graphql',
    credentials: 'include', // Send cookies
  }),
  cache: new InMemoryCache(),
})

const GET_POSTS = gql`
  query GetPosts($limit: Int) {
    posts(limit: $limit) {
      docs {
        id
        title
        slug
      }
    }
  }
`

const { data } = await client.query({
  query: GET_POSTS,
  variables: { limit: 10 },
})
```

## Local API (Server-Side)

The Local API is used within Payload config, custom routes, and server-side code. It bypasses HTTP and works directly with the Payload instance.

### Getting Payload Instance

```typescript
import configPromise from '@payload-config'
import { getPayload } from 'payload'

const payload = await getPayload({
  config: configPromise,
})
```

### Find Documents

```typescript
// Basic find
const posts = await payload.find({
  collection: 'posts',
  limit: 10,
  page: 1,
})

// With filtering
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

// With population
const postsWithAuthors = await payload.find({
  collection: 'posts',
  depth: 1, // Populate relationships
})

// Access results
console.log(posts.docs)       // Array of documents
console.log(posts.totalDocs)  // Total count
console.log(posts.page)       // Current page
```

### Find One Document

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: '64f1a2b3c4d5e6f7g8h9i0j1',
  depth: 1, // Populate relationships
})
```

### Create Document

```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'New Post',
    content: '<p>Content</p>',
    status: 'draft',
  },
})
```

With authentication context:
```typescript
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'New Post',
  },
  req, // Pass request for access control
})
```

### Update Document

```typescript
const updatedPost = await payload.update({
  collection: 'posts',
  id: '64f1a2b3c4d5e6f7g8h9i0j1',
  data: {
    title: 'Updated Title',
  },
})
```

### Delete Document

```typescript
const deletedPost = await payload.delete({
  collection: 'posts',
  id: '64f1a2b3c4d5e6f7g8h9i0j1',
})
```

### Count Documents

```typescript
const count = await payload.count({
  collection: 'posts',
  where: {
    status: { equals: 'published' },
  },
})

console.log(count.totalDocs)
```

### Authentication with Local API

```typescript
// Check authentication from request
const { user } = await payload.auth({ req })

if (!user) {
  throw new Error('Unauthorized')
}

// Use authenticated context
const posts = await payload.find({
  collection: 'posts',
  user, // Access control uses this user
})
```

## Custom Routes

### Next.js App Router Routes

Create custom API routes in `src/app/`:

**Basic route:**
```typescript
// src/app/api/custom/route.ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
    where: {
      status: { equals: 'published' },
    },
  })
  
  return Response.json({ 
    success: true,
    data: posts.docs 
  })
}

export const POST = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  const body = await request.json()
  
  const doc = await payload.create({
    collection: 'posts',
    data: body,
  })
  
  return Response.json(doc, { status: 201 })
}
```

**Route with parameters:**
```typescript
// src/app/api/posts/[id]/route.ts
import type { NextRequest } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const payload = await getPayload({ config: configPromise })
  
  const post = await payload.findByID({
    collection: 'posts',
    id: params.id,
  })
  
  if (!post) {
    return Response.json(
      { error: 'Not found' },
      { status: 404 }
    )
  }
  
  return Response.json(post)
}
```

**Route with authentication:**
```typescript
// src/app/api/protected/route.ts
export const GET = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  
  // Check auth
  const { user } = await payload.auth({ req: request })
  
  if (!user) {
    return Response.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  // User-specific data
  const posts = await payload.find({
    collection: 'posts',
    where: {
      author: { equals: user.id },
    },
  })
  
  return Response.json({ posts })
}
```

### Dynamic Routes

**Catch-all routes:**
```typescript
// src/app/api/[collection]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { collection: string } }
) {
  const payload = await getPayload({ config: configPromise })
  
  // Validate collection slug (security!)
  const allowedCollections = ['posts', 'pages', 'media']
  if (!allowedCollections.includes(params.collection)) {
    return Response.json(
      { error: 'Invalid collection' },
      { status: 400 }
    )
  }
  
  const docs = await payload.find({
    collection: params.collection,
    limit: 10,
  })
  
  return Response.json(docs)
}
```

## Client-Side Integration

### Using Fetch API

```typescript
// Basic fetch
const response = await fetch('/api/posts')
const data = await response.json()

// With authentication (cookies automatic in browser)
const protectedResponse = await fetch('/api/protected')

// POST request
const newPost = await fetch('/api/posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'New Post',
    content: '<p>Content</p>',
  }),
})

const result = await newPost.json()
```

### Using Axios

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Send cookies
})

// GET
const posts = await api.get('/posts')

// POST
const newPost = await api.post('/posts', {
  title: 'New Post',
})

// With custom headers
const response = await api.get('/protected', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
```

### Server Components (Next.js)

```typescript
// src/app/page.tsx
import { getPayload } from 'payload'
import config from '@/payload.config'

export default async function HomePage() {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
    where: {
      status: { equals: 'published' },
    },
  })
  
  return (
    <div>
      {posts.docs.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
        </article>
      ))}
    </div>
  )
}
```

## Error Handling

### REST API Errors

Payload returns standardized error responses:

```json
{
  "error": true,
  "errors": [
    {
      "message": "Validation failed",
      "name": "ValidationError",
      "data": {
        "title": "Title is required"
      }
    }
  ]
}
```

HTTP status codes:
- `400` - Validation error
- `401` - Unauthorized
- `403` - Forbidden (access denied)
- `404` - Not found
- `500` - Server error

### GraphQL Errors

```json
{
  "data": {
    "posts": null
  },
  "errors": [
    {
      "message": "Validation failed",
      "locations": [{ "line": 3, "column": 5 }],
      "path": ["posts"]
    }
  ]
}
```

### Local API Errors

Throw standard JavaScript errors:

```typescript
try {
  const post = await payload.findByID({
    collection: 'posts',
    id: invalidId,
  })
} catch (error) {
  if (error.name === 'NotFound') {
    // Handle not found
  } else if (error.name === 'Unauthorized') {
    // Handle auth error
  } else {
    // Generic error
  }
}
```

## Best Practices

### Security

1. **Validate all inputs** - Never trust client data
2. **Use access control** - Define permissions for every collection
3. **Sanitize user input** - Especially rich text content
4. **Rate limit APIs** - Prevent abuse
5. **Use HTTPS in production** - Encrypt all traffic

### Performance

1. **Limit query results** - Always use `limit` parameter
2. **Use pagination** - For large datasets
3. **Select specific fields** - Use `fields` parameter to reduce payload
4. **Cache responses** - Implement CDN or server-side caching
5. **Use indexes** - Add database indexes for frequently queried fields

### Error Handling

1. **Check response status** - Always validate HTTP status
2. **Handle errors gracefully** - Show user-friendly messages
3. **Log errors server-side** - For debugging
4. **Timeout requests** - Prevent hanging calls

See [Deployment and Config](06-deployment-and-config.md) for production API considerations.
