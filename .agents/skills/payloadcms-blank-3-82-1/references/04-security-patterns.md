# Security Patterns

**CRITICAL SECURITY GUIDE**: Essential security patterns, access control implementation, and best practices for Payload CMS blank template. Read this before implementing any authentication or authorization logic.

## Critical Security Rules

### Rule 1: Local API Access Control (MOST IMPORTANT)

**The Problem:**
Payload's Local API bypasses access control by default for administrative operations. This is intentional for admin panel functionality but creates security vulnerabilities when not handled correctly.

**❌ VULNERABLE CODE:**

```typescript
// SECURITY BUG: Access control completely bypassed!
async function getUserPosts(userId: string) {
  const user = await payload.findByID({
    collection: 'users',
    id: userId,
  })

  // This runs with ADMIN privileges, ignoring all access control!
  const posts = await payload.find({
    collection: 'posts',
    user: user, // Passing user does NOT enforce their permissions
  })

  return posts
}
```

**What happens:**
- Even if `Posts` collection has `read: adminOnly` access control
- This query will return ALL posts because it runs as admin
- The `user` parameter is used for context only, not permission enforcement

**✅ SECURE CODE:**

```typescript
// CORRECT: Explicitly enforce user permissions
async function getUserPosts(userId: string) {
  const user = await payload.findByID({
    collection: 'users',
    id: userId,
  })

  // overrideAccess: false enforces the user's access control
  const posts = await payload.find({
    collection: 'posts',
    user: user,
    overrideAccess: false, // REQUIRED to enforce permissions
  })

  return posts
}
```

**Key Points:**
- **Default behavior**: `overrideAccess` defaults to `true` (bypasses access control)
- **Secure behavior**: Set `overrideAccess: false` when you want to enforce user permissions
- **Admin operations**: Omit `user` parameter entirely for true admin operations

**When to use each:**

```typescript
// Admin operation (intentional bypass)
async function adminGetAllPosts() {
  const posts = await payload.find({
    collection: 'posts',
    // No user parameter, overrideAccess defaults to true
    // Runs with full admin privileges
  })
}

// User-specific operation (enforce permissions)
async function getUserPosts(req: PayloadRequest) {
  const posts = await payload.find({
    collection: 'posts',
    user: req.user,
    overrideAccess: false, // Enforce this user's permissions
  })
}

// Public operation (no auth)
async function getPublishedPosts() {
  const posts = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    // No user, runs as admin but query filters to published only
  })
}
```

### Rule 2: Transaction Safety in Hooks

**The Problem:**
Operations performed in hooks run in separate transactions unless you pass the request object. This can lead to data corruption when related operations should be atomic.

**❌ DATA CORRUPTION RISK:**

```typescript
export const Orders: CollectionConfig = {
  slug: 'orders',
  hooks: {
    afterChange: [
      async ({ doc, req }) => {
        // BUG: This runs in a SEPARATE transaction!
        // If this fails, the order is still created (data inconsistency)
        await req.payload.create({
          collection: 'order-notifications',
          data: { orderId: doc.id, type: 'created' },
          // Missing req parameter!
        })
      },
    ],
  },
}
```

**What happens:**
1. Order is created successfully
2. Hook tries to create notification in separate transaction
3. Notification creation fails (database error, validation error, etc.)
4. Order exists but notification doesn't (inconsistent state)
5. Cannot rollback order creation

**✅ ATOMIC OPERATION:**

```typescript
export const Orders: CollectionConfig = {
  slug: 'orders',
  hooks: {
    afterChange: [
      async ({ doc, req }) => {
        // CORRECT: Pass req to maintain transaction atomicity
        await req.payload.create({
          collection: 'order-notifications',
          data: { orderId: doc.id, type: 'created' },
          req, // Same transaction as parent operation
        })
      },
    ],
  },
}
```

**Key Points:**
- **Always pass `req`** to nested Payload operations in hooks
- **MongoDB transactions** require replica set configuration
- **PostgreSQL transactions** work out of the box
- **Test failure scenarios** to ensure rollbacks work correctly

### Rule 3: Prevent Infinite Hook Loops

**The Problem:**
Operations in hooks can trigger the same hooks, creating infinite recursion.

**❌ INFINITE LOOP:**

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    afterChange: [
      async ({ doc, req }) => {
        // BUG: This triggers afterChange again!
        await req.payload.update({
          collection: 'posts',
          id: doc.id,
          data: { viewCount: (doc.viewCount || 0) + 1 },
          req,
        })
      },
    ],
  },
}
```

**What happens:**
1. Post is updated
2. afterChange hook runs
3. Hook updates the same post
4. afterChange hook runs again
5. Infinite loop → stack overflow or database exhaustion

**✅ SAFE PATTERN with Context Flag:**

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    afterChange: [
      async ({ doc, req, context }) => {
        // Check context flag to prevent loops
        if (context.skipHooks) {
          return doc
        }

        // Update with context flag to skip hooks
        await req.payload.update({
          collection: 'posts',
          id: doc.id,
          data: { viewCount: (doc.viewCount || 0) + 1 },
          context: { skipHooks: true }, // Prevent recursive hooks
          req,
        })
      },
    ],
  },
}
```

**Alternative: Use beforeChange for computed fields:**

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation, doc }) => {
      // Only increment on read operations, not writes
      if (operation === 'read') {
        data.viewCount = (doc?.viewCount || 0) + 1
      }
      return data
    },
  ],
}
```

## Access Control Implementation

### Collection-Level Access Control

Access control functions determine who can perform operations on entire documents.

**Access Function Signature:**

```typescript
import type { Access } from 'payload'

const accessFunction: Access = async ({
  req,       // Payload request object (includes user, payload, context)
  id,        // Document ID (undefined for create/list operations)
  doc,       // Document data (undefined for create operations)
  data,      // Incoming data (only for create/update operations)
}) => {
  // Return values:
  // true    - Allow operation
  // false   - Deny operation
  // {}      - Query constraint (row-level security)
}
```

**Return Value Types:**

```typescript
// Boolean: Allow or deny all documents
const adminOnly: Access = ({ req: { user } }) => {
  return user?.roles?.includes('admin')
}

// Query: Row-level security (filter documents)
const ownDocumentsOnly: Access = ({ req: { user } }) => {
  if (!user) return false
  if (user.roles?.includes('admin')) return true
  
  // User can only see documents where author = their ID
  return { author: { equals: user.id } }
}
```

### Common Access Control Patterns

**1. Anyone (Public Access):**

```typescript
export const anyone: Access = () => true
```

**2. Authenticated Users Only:**

```typescript
export const authenticated: Access = ({ req: { user } }) => {
  return Boolean(user)
}
```

**3. Admin Only:**

```typescript
export const adminOnly: Access = ({ req: { user } }) => {
  return user?.roles?.includes('admin')
}
```

**4. Admin or Document Owner:**

```typescript
export const adminOrSelf: Access = ({ req: { user }, doc }) => {
  // Admins can access all documents
  if (user?.roles?.includes('admin')) return true
  
  // Users can access their own documents
  if (!user || !doc) return false
  return user.id === doc.id
}
```

**5. Row-Level Security (Own Documents):**

```typescript
export const ownDocumentsOnly: Access = ({ req: { user } }) => {
  // No user = no access
  if (!user) return false
  
  // Admins see everything
  if (user.roles?.includes('admin')) return true
  
  // Editors see all documents
  if (user.roles?.includes('editor')) return true
  
  // Regular users see only their own
  return { author: { equals: user.id } }
}
```

**6. Published or Authenticated:**

```typescript
export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  // Authenticated users see everything (including drafts)
  if (user) return true
  
  // Public sees only published documents
  return { _status: { equals: 'published' } }
}
```

**7. Role-Based with Query Constraint:**

```typescript
export const roleBasedAccess: Access = ({ req: { user } }) => {
  if (!user) return false
  
  // Admins see all
  if (user.roles?.includes('admin')) return true
  
  // Team leads see their team's documents
  if (user.roles?.includes('team-lead')) {
    return { team: { equals: user.team } }
  }
  
  // Members see only their own
  return { author: { equals: user.id } }
}
```

### Field-Level Access Control

Field-level access controls determine who can read or modify specific fields.

**IMPORTANT:** Field access functions **only return boolean**, not query constraints.

```typescript
{
  name: 'salary',
  type: 'number',
  access: {
    // Who can read this field?
    read: ({ req: { user }, doc }) => {
      // Users can read their own salary
      if (user?.id === doc?.id) return true
      
      // HR and admins can read all salaries
      return user?.roles?.some(r => ['admin', 'hr'].includes(r))
    },
    
    // Who can update this field?
    update: ({ req: { user } }) => {
      // Only HR can update salaries
      return user?.roles?.includes('hr')
    },
  },
}
```

**Field Access Examples:**

```typescript
// Hide sensitive field from non-admins
{
  name: 'internalNotes',
  type: 'textarea',
  access: {
    read: ({ req: { user } }) => user?.roles?.includes('admin'),
    update: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
}

// Users can create password but not read/update it
{
  name: 'password',
  type: 'text',
  access: {
    read: () => false, // Never expose password
    update: ({ req: { user }, operation }) => {
      // Can set on create, admins can update
      return operation === 'create' || user?.roles?.includes('admin')
    },
  },
}

// Read-only field for regular users
{
  name: 'approvedBy',
  type: 'relationship',
  relationTo: 'users',
  access: {
    read: () => true, // Everyone can read
    update: ({ req: { user } }) => {
      // Only managers can approve
      return user?.roles?.includes('manager')
    },
  },
}
```

## Implementing RBAC (Role-Based Access Control)

### Step 1: Add Roles to Users Collection

```typescript
// src/collections/Users.ts
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true, // Users can have multiple roles
      options: [
        { label: 'Administrator', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'Contributor', value: 'contributor' },
        { label: 'Member', value: 'member' },
      ],
      defaultValue: ['member'],
      required: true,
      saveToJWT: true, // CRITICAL: Include in JWT for fast access checks
    },
  ],
}
```

**Why `saveToJWT: true`:**
- Roles are included in JWT token
- Access control can check roles without database query
- Improves performance significantly
- Reduces database load on every request

### Step 2: Create Reusable Access Control Functions

```typescript
// src/access/checkRoles.ts
import type { Access } from 'payload'

export function checkRoles(allowedRoles: string[]): Access {
  return ({ req: { user } }) => {
    if (!user) return false
    return allowedRoles.some(role => user.roles?.includes(role))
  }
}

// src/access/adminOnly.ts
import { checkRoles } from './checkRoles'

export const adminOnly = checkRoles(['admin'])

// src/access/editorOrAbove.ts
import { checkRoles } from './checkRoles'

export const editorOrAbove = checkRoles(['admin', 'editor'])
```

### Step 3: Apply Access Control to Collections

```typescript
// src/collections/Posts.ts
import { adminOnly, editorOrAbove, authenticatedOrPublished } from '@/access'

export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: authenticatedOrPublished,
    create: editorOrAbove,
    update: ({ req: { user }, doc }) => {
      // Admins and editors can update any post
      if (user?.roles?.some(r => ['admin', 'editor'].includes(r))) {
        return true
      }
      
      // Contributors can only update their own drafts
      if (user?.roles?.includes('contributor')) {
        if (!doc) return true // Can create
        return doc.author === user.id && doc.status === 'draft'
      }
      
      return false
    },
    delete: adminOnly,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { 
      name: 'content', 
      type: 'richText',
      // Field-level access control
      access: {
        read: ({ req: { user } }) => {
          // Only editors and above can see full content
          return user?.roles?.some(r => ['admin', 'editor'].includes(r))
        },
      },
    },
  ],
}
```

## Secure API Routes

### Custom Route with Authentication

```typescript
// src/app/api/protected/route.ts
import { getPayload } from 'payload'
import config from '@payload-config'
import { APIError } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  
  // Get authentication from cookies/headers
  const { user } = await payload.auth({ request })
  
  // Require authentication
  if (!user) {
    throw new APIError('Unauthorized', 401)
  }
  
  // Check specific role
  if (!user.roles?.includes('admin')) {
    throw new APIError('Forbidden', 403)
  }
  
  // Secure operation with access control enforced
  const sensitiveData = await payload.find({
    collection: 'sensitive-documents',
    user, // Pass user for context
    overrideAccess: false, // Enforce their permissions
  })
  
  return Response.json(sensitiveData)
}
```

### Custom Route with Role-Based Access

```typescript
// src/app/api/reports/route.ts
export const GET = async (request: Request) => {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ request })
  
  if (!user) {
    throw new APIError('Unauthorized', 401)
  }
  
  let reports
  
  // Role-based query logic
  if (user.roles?.includes('admin')) {
    // Admins see all reports
    reports = await payload.find({
      collection: 'reports',
      overrideAccess: false,
    })
  } else if (user.roles?.includes('manager')) {
    // Managers see their team's reports
    reports = await payload.find({
      collection: 'reports',
      where: { team: { equals: user.team } },
      overrideAccess: false,
    })
  } else {
    throw new APIError('Forbidden', 403)
  }
  
  return Response.json(reports)
}
```

## Secure Server Components

### Checking Authentication in Server Components

```typescript
// src/app/(frontend)/dashboard/page.tsx
import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function DashboardPage() {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ headers: await headers() })
  
  // Require authentication
  if (!user) {
    redirect('/login')
  }
  
  // Fetch user-specific data with access control enforced
  const documents = await payload.find({
    collection: 'documents',
    user,
    overrideAccess: false, // CRITICAL: Enforce permissions
  })
  
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome back, {user.email}</p>
      {/* Render documents */}
    </div>
  )
}
```

### Conditional Rendering Based on Roles

```typescript
export default async function Page() {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ headers: await headers() })
  
  const isAdmin = user?.roles?.includes('admin')
  const isEditor = user?.roles?.includes('editor')
  
  return (
    <div>
      <main>
        {/* Content visible to all authenticated users */}
        {user && <p>Welcome, {user.email}</p>}
        
        {/* Editor-only content */}
        {isEditor && (
          <section>
            <h2>Editor Tools</h2>
            {/* Editor-specific features */}
          </section>
        )}
        
        {/* Admin-only content */}
        {isAdmin && (
          <section>
            <h2>Admin Panel</h2>
            {/* Admin-specific features */}
          </section>
        )}
      </main>
    </div>
  )
}
```

## Security Best Practices

### 1. Never Trust Client Data

```typescript
// ❌ DON'T: Trust client-provided role
hooks: {
  beforeChange: [
    async ({ data }) => {
      // Client could send this!
      data.roles = data.roles || ['admin']
    },
  ],
}

// ✅ DO: Set defaults server-side
fields: [
  {
    name: 'roles',
    type: 'select',
    options: ['admin', 'editor', 'member'],
    defaultValue: ['member'], // Server-enforced default
    access: {
      update: adminOnly, // Only admins can modify roles
    },
  },
]
```

### 2. Use Principle of Least Privilege

```typescript
// Start with restrictive access
access: {
  read: adminOnly,
  create: adminOnly,
  update: adminOnly,
  delete: adminOnly,
}

// Gradually add permissions as needed
access: {
  read: authenticatedOrPublished, // Public can read published
  create: editorOrAbove,          // Editors can create
  update: adminOrSelf,            // Users can update own
  delete: adminOnly,              // Only admins delete
}
```

### 3. Validate All Input

```typescript
hooks: {
  beforeValidate: [
    async ({ data }) => {
      // Sanitize and validate input
      if (data.email) {
        data.email = data.email.toLowerCase().trim()
      }
      
      // Validate email format
      if (data.email && !/\S+@\S+\.\S+/.test(data.email)) {
        throw new Error('Invalid email format')
      }
      
      return data
    },
  ],
}
```

### 4. Audit Sensitive Operations

```typescript
hooks: {
  afterChange: [
    async ({ doc, req, operation, previousDoc }) => {
      // Log sensitive operations
      await req.payload.create({
        collection: 'audit-log',
        data: {
          operation,
          collection: 'users',
          documentId: doc.id,
          changedBy: req.user?.id,
          changes: {
            from: previousDoc,
            to: doc,
          },
          timestamp: new Date(),
        },
        req, // Maintain transaction
      })
    },
  ],
}
```

### 5. Secure File Uploads

```typescript
export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    mimeTypes: ['image/*'], // Restrict to images only
  },
  access: {
    read: () => true, // Public can view
    create: authenticated, // Only authenticated can upload
    delete: adminOnly, // Only admins can delete
  },
}
```

## Testing Access Control

### Integration Test Example

```typescript
// tests/int/access-control.int.spec.ts
import { describe, it, expect, beforeAll } from 'vitest'
import { getPayload } from 'payload'
import config from '@/payload.config'

describe('Access Control', () => {
  let payload
  let adminUser
  let regularUser
  
  beforeAll(async () => {
    payload = await getPayload({ config })
    
    // Create test users
    adminUser = await payload.create({
      collection: 'users',
      data: { email: 'admin@test.com', password: 'test', roles: ['admin'] },
    })
    
    regularUser = await payload.create({
      collection: 'users',
      data: { email: 'user@test.com', password: 'test', roles: ['member'] },
    })
  })
  
  it('should allow admin to read all documents', async () => {
    const docs = await payload.find({
      collection: 'posts',
      user: adminUser,
      overrideAccess: false,
    })
    
    expect(docs.docs).toBeDefined()
  })
  
  it('should restrict regular user to own documents', async () => {
    const docs = await payload.find({
      collection: 'posts',
      user: regularUser,
      overrideAccess: false,
    })
    
    // All returned docs should belong to regularUser
    docs.docs.forEach(doc => {
      expect(doc.author).toBe(regularUser.id)
    })
  })
  
  it('should deny unauthenticated access', async () => {
    const docs = await payload.find({
      collection: 'posts',
      // No user parameter
      overrideAccess: false,
    })
    
    expect(docs.docs).toHaveLength(0)
  })
})
```

See [Testing Setup](07-testing.md) for complete testing patterns.
