# Access Control & Authentication Reference

Complete guide to security patterns, role-based access control (RBAC), and authentication in Payload CMS v3.82.1.

## Security Critical Patterns

### ⚠️ CRITICAL: Local API Access Control

**Most common security vulnerability in Payload applications:**

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
  // No user passed, overrideAccess defaults to true (admin privileges)
})
```

**Rule**: When passing `user` to Local API, ALWAYS set `overrideAccess: false`

### ⚠️ CRITICAL: Transaction Safety in Hooks

**Data corruption risk when missing req parameter:**

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

### ⚠️ CRITICAL: Prevent Infinite Hook Loops

**Infinite recursion when updating in hooks:**

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

## Access Control Fundamentals

Access control in Payload operates at two levels:
- **Collection-level**: Controls who can read/create/update/delete documents
- **Field-level**: Controls who can read/write specific fields within documents

### Access Control Return Types

Access functions can return three types of values:

| Return Type | Behavior |
|-------------|----------|
| `true` | Full access granted |
| `false` | Access denied |
| `{ query }` | Row-level security (query constraint) |

## Collection-Level Access Control

### Basic Access Patterns

```typescript
import type { Access } from 'payload'

// Anyone can access (public)
export const anyone: Access = () => true

// Authenticated users only
export const authenticated: Access = ({ req: { user } }) => Boolean(user)

// Admins only
export const adminOnly: Access = ({ req: { user } }) => {
  return user?.roles?.includes('admin')
}

// Owner or admin
export const ownerOrAdmin: Access = ({ req: { user }, doc }) => {
  if (!user) return false
  if (user.roles?.includes('admin')) return true
  return user.id === doc?.id
}
```

### Row-Level Security (Query Constraints)

Return a query object to filter documents based on user context:

```typescript
// Users see only their own posts, admins see all
const ownPostsOnly: Access = ({ req: { user } }) => {
  if (!user) return false // No access for unauthenticated
  
  if (user?.roles?.includes('admin')) return true // Admins see everything
  
  // Regular users see only documents where author matches their ID
  return {
    author: { equals: user.id },
  }
}

export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: ownPostsOnly,
    update: ownPostsOnly,
    delete: adminOnly,
  },
  fields: [
    { name: 'author', type: 'relationship', relationTo: 'users' },
  ],
}
```

### Async Access Control

Perform database lookups for complex permission checks:

```typescript
// Project-based access control
const projectMemberAccess: Access = async ({ req, id }) => {
  const { user, payload } = req

  if (!user) return false
  if (user.roles?.includes('admin')) return true

  // Fetch the document to check membership
  const project = await payload.findByID({
    collection: 'projects',
    id: id as string,
    depth: 0, // Don't populate relationships for performance
  })

  // Check if user is a member of the project
  return project.members?.includes(user.id)
}
```

### Operation-Specific Access

Different permissions for each operation:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    // Who can view documents (list and single)
    read: ({ req: { user } }) => {
      if (!user) return { _status: { equals: 'published' } } // Public sees published only
      if (user.roles?.includes('admin')) return true
      return { author: { equals: user.id } }
    },
    
    // Who can create new documents
    create: ({ req: { user } }) => Boolean(user),
    
    // Who can update documents
    update: ({ req: { user }, doc }) => {
      if (!user) return false
      if (user.roles?.includes('admin')) return true
      return user.id === doc?.author
    },
    
    // Who can delete documents
    delete: ({ req: { user } }) => {
      return user?.roles?.includes('admin')
    },
  },
}
```

### Access Control Context

Access functions receive rich context:

```typescript
const complexAccess: Access = async ({ 
  req,      // Request object with user, payload, context
  id,       // Document ID (for read/update/delete)
  doc,      // Existing document (for update/delete)
  data,     // Incoming data (for create/update)
  siblingData, // Other fields in the document (field-level only)
}) => {
  const { user, payload, context } = req
  
  // Access other collections
  const userProjects = await payload.find({
    collection: 'projects',
    where: { members: { equals: user.id } },
  })
  
  return true
}
```

## Field-Level Access Control

Field-level access controls visibility and editability of individual fields.

### Boolean-Only Returns

**Important**: Field-level access can ONLY return `true` or `false` (no query constraints):

```typescript
{
  name: 'salary',
  type: 'number',
  access: {
    // Who can read this field
    read: ({ req: { user }, doc }) => {
      // Users can read own salary
      if (user?.id === doc?.id) return true
      
      // HR and admins can read all salaries
      return user?.roles?.some(role => ['admin', 'hr'].includes(role))
    },
    
    // Who can update this field
    update: ({ req: { user } }) => {
      // Only HR can update salaries
      return user?.roles?.includes('hr')
    },
  },
}
```

### Conditional Field Visibility

Hide sensitive fields based on user roles:

```typescript
{
  name: 'internalNotes',
  type: 'textarea',
  admin: {
    hidden: ({ req: { user } }) => {
      // Hide from non-admin users
      return !user?.roles?.includes('admin')
    },
  },
  access: {
    read: ({ req: { user } }) => {
      return user?.roles?.includes('admin')
    },
  },
}
```

### Field Access Examples

**Email visibility**:
```typescript
{
  name: 'email',
  type: 'email',
  access: {
    read: ({ req: { user }, doc }) => {
      if (!user) return false // Unauthenticated can't see emails
      if (user.id === doc.id) return true // Can see own email
      return user.roles?.includes('admin') // Admins see all
    },
  },
}
```

**Admin-only fields**:
```typescript
{
  name: 'seoMetadata',
  type: 'group',
  access: {
    read: ({ req: { user } }) => user?.roles?.includes('admin'),
    update: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
  fields: [
    { name: 'metaTitle', type: 'text' },
    { name: 'metaDescription', type: 'textarea' },
  ],
}
```

## Authentication Setup

### Basic Authentication Collection

Enable authentication on a collection:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true, // Enable authentication
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'avatar', type: 'upload', relationTo: 'media' },
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      options: ['admin', 'editor', 'user'],
      defaultValue: ['user'],
      required: true,
      saveToJWT: true, // Include in JWT for fast access checks
    },
  ],
}
```

### Admin User Configuration

Specify which collection provides admin panel authentication:

```typescript
export default buildConfig({
  admin: {
    user: 'users', // Collection slug for admin login
  },
  collections: [Users, Posts],
})
```

### JWT Token Configuration

Customize JWT token behavior:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    cookieOptions: {
      domain: 'yourdomain.com',
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
    },
    jwtExpiration: 60 * 60 * 24 * 7, // 7 days in seconds
    verify: async (token) => {
      // Custom token verification
      return true
    },
  },
}
```

### Role-Based Access Control (RBAC)

Implement roles with JWT storage for performance:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      options: ['admin', 'editor', 'user'],
      defaultValue: ['user'],
      required: true,
      saveToJWT: true, // CRITICAL: Include in JWT to avoid DB lookups
      access: {
        // Only admins can modify roles
        update: ({ req: { user } }) => user?.roles?.includes('admin'),
      },
    },
  ],
}
```

**Access function using JWT roles**:
```typescript
const adminOnly: Access = ({ req: { user } }) => {
  // Fast check from JWT (no database query needed)
  return user?.roles?.includes('admin')
}
```

### Custom Authentication Strategies

Add OAuth or other auth providers:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    provider: async (args) => {
      // Custom authentication logic
      return {
        userId: args.email,
        refreshToken: '',
        user: await payload.findByID({
          collection: 'users',
          id: args.email,
        }),
      }
    },
  },
}
```

## Common Access Control Patterns

### Published vs Draft Content

Control visibility based on publication status:

```typescript
export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  if (user) return true // Authenticated users see everything
  
  // Public sees only published content
  return { _status: { equals: 'published' } }
}

export const Posts: CollectionConfig = {
  slug: 'posts',
  versions: {
    drafts: {
      autosave: true,
    },
  },
  access: {
    read: authenticatedOrPublished,
  },
  fields: [
    {
      name: '_status',
      type: 'select',
      options: ['draft', 'published'],
      defaultValue: 'draft',
    },
  ],
}
```

### Multi-Tenant Access Control

Isolate data by organization/tenant:

```typescript
// Tenant-based row-level security
const tenantIsolation: Access = ({ req: { user } }) => {
  if (!user) return false
  
  if (user.roles?.includes('admin')) return true // Super admin sees all
  
  // Users only see documents in their tenant
  return {
    tenant: { equals: user.tenant },
  }
}

// Tenant field on user collection
{
  name: 'tenant',
  type: 'relationship',
  relationTo: 'organizations',
  required: true,
  saveToJWT: true, // Include in JWT for fast filtering
}
```

### Hierarchical Permissions

Role hierarchy with inheritance:

```typescript
// Role hierarchy definition
const roleHierarchy = {
  admin: ['admin', 'editor', 'user'],
  editor: ['editor', 'user'],
  user: ['user'],
}

const hasPermission: Access = ({ req: { user }, doc }) => {
  if (!user) return false
  
  const userRole = user.roles?.[0] || 'user'
  const requiredRoles = doc?.requiredPermissions || ['user']
  
  // Check if user's role is in the allowed list
  return roleHierarchy[userRole]?.some(role => 
    requiredRoles.includes(role)
  )
}
```

### Time-Based Access Control

Restrict access based on time windows:

```typescript
const timeBasedAccess: Access = async ({ req, id }) => {
  const { user, payload } = req
  
  if (!user) return false
  
  // Fetch document to check time constraints
  const doc = await payload.findByID({
    collection: 'surveys',
    id: id as string,
  })
  
  const now = new Date()
  const startTime = new Date(doc.startTime)
  const endTime = new Date(doc.endTime)
  
  // Check if current time is within allowed window
  return now >= startTime && now <= endTime
}
```

### Cross-Collection Access Control

Check permissions across multiple collections:

```typescript
const projectDocumentAccess: Access = async ({ req, id }) => {
  const { user, payload } = req
  
  if (!user) return false
  if (user.roles?.includes('admin')) return true
  
  // Find which project this document belongs to
  const document = await payload.findByID({
    collection: 'documents',
    id: id as string,
    depth: 1, // Populate project relationship
  })
  
  if (!document.project) return false
  
  // Check if user is a member of the project
  const project = await payload.findByID({
    collection: 'projects',
    id: document.project,
    depth: 0,
  })
  
  return project.members?.includes(user.id)
}
```

## Authentication Best Practices

### Password Security

Payload uses bcrypt by default for password hashing:

```typescript
// Default behavior - no configuration needed
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    { name: 'email', type: 'email', required: true, unique: true },
    { name: 'password', type: 'text', required: true }, // Auto-hashed with bcrypt
  ],
}
```

### Email Verification

Require email verification on signup:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    verifyUserEmail: true, // Send verification email on signup
  },
  fields: [
    {
      name: 'verified',
      type: 'checkbox',
      access: {
        read: ({ req: { user } }) => user?.id === doc?.id,
      },
    },
  ],
}
```

### Rate Limiting

Implement rate limiting for login attempts (use external middleware):

```typescript
// Example with Express rate limiter
import rateLimit from 'express-rate-limit'

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many login attempts, please try again later',
})

app.use('/api/users/login', loginLimiter)
```

### Session Management

Configure cookie-based sessions:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    cookies: {
      expiration: 60 * 60 * 24 * 30, // 30 days
      refreshExpiration: 60 * 60 * 24 * 365, // 1 year
    },
  },
}
```

## Testing Access Control

### Local API Testing

Test access control with different user contexts:

```typescript
// Test as admin
const adminResults = await payload.find({
  collection: 'posts',
  user: adminUser,
  overrideAccess: false, // Enforce access control
})

// Test as regular user
const userResults = await payload.find({
  collection: 'posts',
  user: regularUser,
  overrideAccess: false,
})

// Test as unauthenticated
const publicResults = await payload.find({
  collection: 'posts',
  overrideAccess: false, // No user, access control still enforced
})
```

### Unit Testing Access Functions

```typescript
import { adminOnly, ownPostsOnly } from './access'

describe('Access Control', () => {
  it('should allow admins to access', () => {
    const result = adminOnly({
      req: { user: { roles: ['admin'] } },
    })
    expect(result).toBe(true)
  })
  
  it('should deny non-admins', () => {
    const result = adminOnly({
      req: { user: { roles: ['user'] } },
    })
    expect(result).toBe(false)
  })
})
```

## Troubleshooting Access Control

### Common Issues

**Access control not working in Local API:**
- Ensure `overrideAccess: false` is set when passing `user`
- Check that user object has correct structure

**Field access returning wrong type:**
- Field access can only return boolean (no query constraints)
- Use collection-level access for row-level security

**Performance issues with async access:**
- Use `saveToJWT: true` for frequently checked fields
- Cache expensive lookups in `req.context`
- Set `depth: 0` when fetching documents in access functions

**Users can't see their own documents:**
- Check query constraint syntax in access function
- Ensure relationship fields are properly indexed
- Verify user ID matches document author field type
