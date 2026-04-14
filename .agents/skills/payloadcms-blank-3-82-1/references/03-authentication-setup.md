# Authentication Setup

This reference documents authentication configuration, access control patterns, and security best practices for Payload CMS 3.82.1. The blank template includes a basic Users collection with auth enabled - this guide covers extending and customizing authentication.

## Basic Authentication Configuration

### Default Users Collection

The blank template provides a minimal auth-enabled Users collection:

```typescript
// src/collections/Users.ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',
  },
  auth: true,  // Enables authentication
  fields: [
    // Email and password fields added automatically
  ],
}
```

### Auto-Generated Fields

When `auth: true` is set, Payload automatically adds:

1. **`email`** (text) - Email address for login
2. **`password`** (password) - Hashed password storage
3. **`resetPasswordToken`** (text) - Password reset tokens
4. **`resetPasswordExpiration`** (date) - Token expiration

You can extend with custom fields:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: {
    useAsTitle: 'email',
  },
  fields: [
    // Auto-generated fields (don't redefine)
    {
      name: 'name',
      type: 'text',
      required: true,
    },
    {
      name: 'role',
      type: 'select',
      options: [
        { label: 'Administrator', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'User', value: 'user' },
      ],
      defaultValue: 'user',
      required: true,
    },
    {
      name: 'avatar',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'bio',
      type: 'textarea',
      rows: 3,
    },
  ],
}
```

## Admin Panel Configuration

### Setting Auth Collection for Admin

In `payload.config.ts`:

```typescript
export default buildConfig({
  admin: {
    user: 'users',  // Slug of auth-enabled collection
  },
  collections: [Users, Media],
  // ... other config
})
```

Only users from this collection can access the admin panel at `/admin`.

## Access Control

### Collection-Level Access

Define who can read, create, update, and delete documents:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    // Who can view documents in list/detail views
    read: ({ req }) => {
      // Allow logged-in users to read
      return !!req.user
    },
    
    // Who can create new documents
    create: ({ req }) => {
      // Only editors and admins can create
      return ['editor', 'admin'].includes(req.user?.role)
    },
    
    // Who can update documents
    update: ({ req, data }) => {
      // Users can only update their own posts
      if (!req.user) return false
      
      // Admins can update anything
      if (req.user.role === 'admin') return true
      
      // Others can only update their own
      return req.user.id === data.id
    },
    
    // Who can delete documents
    delete: ({ req, data }) => {
      // Only admins can delete
      return req.user?.role === 'admin'
    },
  },
  fields: [/* ... */],
}
```

### Access Control Context

Access functions receive a context object:

```typescript
access: {
  read: ({ req, data, query, depth }) => {
    // req - Request object with user, headers, etc.
    // data - Document data (for update/delete)
    // query - Query parameters (for read)
    // depth - Population depth
    
    return true // or false
  },
}
```

### Field-Level Access

Control access to individual fields:

```typescript
{
  name: 'salary',
  type: 'number',
  access: {
    // Who can read this field
    read: ({ req, data }) => {
      // Only HR and managers can see salary
      return ['hr', 'manager'].includes(req.user?.role)
    },
    
    // Who can edit this field
    update: ({ req }) => {
      // Only HR can modify salary
      return req.user?.role === 'hr'
    },
  },
}
```

### Hiding Fields from Admin

```typescript
{
  name: 'internalNotes',
  type: 'textarea',
  admin: {
    hidden: ({ req }) => {
      // Hide from non-admin users
      return req.user?.role !== 'admin'
    },
  },
}
```

## Authentication Hooks

### Before Login Hook

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  hooks: {
    beforeLogin: [
      async ({ doc, req }) => {
        // Check if account is active
        if (!doc.active) {
          throw new Error('Account is not active. Please contact support.')
        }
        
        // Log login attempt
        await logLoginAttempt({ userId: doc.id, ip: req.ip })
        
        return doc
      },
    ],
  },
  fields: [/* ... */],
}
```

### Before Change Hook (Password Updates)

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation, req }) => {
      // Send email notification on password change
      if (operation === 'update' && data.password) {
        await sendPasswordChangeEmail({ 
          userId: req.user.id,
          email: req.user.email 
        })
      }
      
      return data
    },
  ],
}
```

## Role-Based Access Control (RBAC)

### Defining Roles

```typescript
type UserRole = 'admin' | 'editor' | 'author' | 'subscriber'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    {
      name: 'role',
      type: 'select',
      options: [
        { label: 'Administrator', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'Author', value: 'author' },
        { label: 'Subscriber', value: 'subscriber' },
      ],
      defaultValue: 'subscriber',
      required: true,
    },
  ],
}
```

### Permission Helper Functions

Create reusable permission checks:

```typescript
// src/lib/permissions.ts
import type { Access } from 'payload'

type Context = {
  req: {
    user?: {
      id: string
      role: UserRole
    }
  }
  data?: any
}

export const canReadPost: Access = ({ req }) => {
  // Everyone can read published posts
  return true
}

export const canEditPost: Access = ({ req, data }) => {
  if (!req.user) return false
  
  // Admins can edit anything
  if (req.user.role === 'admin') return true
  
  // Editors can edit all posts
  if (req.user.role === 'editor') return true
  
  // Authors can only edit their own
  if (req.user.role === 'author') {
    return req.user.id === data?.author
  }
  
  return false
}

export const canDeletePost: Access = ({ req }) => {
  // Only admins and editors can delete
  return ['admin', 'editor'].includes(req.user?.role)
}
```

Usage in collection:

```typescript
import { canReadPost, canEditPost, canDeletePost } from '@/lib/permissions'

export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: canReadPost,
    update: canEditPost,
    delete: canDeletePost,
  },
  fields: [/* ... */],
}
```

## Password Reset

### Default Behavior

Payload provides built-in password reset functionality:

1. POST `/api/users/forgot-password` - Send reset email
2. POST `/api/users/reset-password` - Reset with token

### Customizing Password Reset Emails

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    verifyUserEmail: true,  // Require email verification
    useAPIKey: false,
    tokens: true,           // Enable token-based auth
    
    // Custom password reset strategy
    forgotPassword: async ({ req, doc }) => {
      // Generate reset token
      const token = generateResetToken()
      
      // Save token to database
      await req.payload.update({
        collection: 'users',
        id: doc.id,
        data: {
          resetPasswordToken: hashToken(token),
          resetPasswordExpiration: new Date(Date.now() + 3600000), // 1 hour
        },
      })
      
      // Send custom email
      await sendPasswordResetEmail({
        email: doc.email,
        token,
        emailTemplate: 'custom-reset-template',
      })
    },
  },
  fields: [/* ... */],
}
```

## Token-Based Authentication

### API Key Authentication

Enable API key auth for programmatic access:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    useAPIKey: true,
    apiKeyFieldName: 'apiKey',
  },
  fields: [
    {
      name: 'apiKey',
      type: 'text',
      admin: {
        hidden: true,  // Don't show in admin
      },
    },
  ],
}
```

### JWT Token Configuration

```typescript
export default buildConfig({
  // ... other config
  
  // JWT configuration
  secret: process.env.PAYLOAD_SECRET,
  
  // Cookie settings
  cookies: {
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24 * 7, // 1 week
  },
})
```

## Authentication in Custom Routes

### Using Local API with Auth

```typescript
// src/app/api/protected/route.ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  
  // Check authentication
  const { user } = await payload.auth({ req: request })
  
  if (!user) {
    return Response.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  // User is authenticated - proceed
  const posts = await payload.find({
    collection: 'posts',
    user,  // Pass user for access control
  })
  
  return Response.json({ posts })
}
```

### Auth Headers in Requests

Payload accepts auth via:
1. **Cookies** (default for browser requests)
2. **Authorization header** (Bearer token)
3. **API key header** (if enabled)

```typescript
// Client-side authenticated request
const response = await fetch('/api/posts', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
```

## Email Verification

### Enabling Email Verification

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    verifyUserEmail: true,  // Require verification before login
    
    // Custom verification email
    verifyUserEmail: async ({ req, doc }) => {
      const token = generateVerificationToken()
      
      // Save token
      await req.payload.update({
        collection: 'users',
        id: doc.id,
        data: {
          verifyUserToken: hashToken(token),
          verifyUserExpiration: new Date(Date.now() + 86400000), // 24 hours
        },
      })
      
      // Send email
      await sendVerificationEmail({
        email: doc.email,
        token,
      })
    },
  },
  fields: [/* ... */],
}
```

## Security Best Practices

### Password Requirements

Enforce strong passwords:

```typescript
hooks: {
  beforeValidate: [
    ({ data }) => {
      if (data.password) {
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
        
        if (!passwordRegex.test(data.password)) {
          throw new Error(
            'Password must be at least 8 characters and contain uppercase, lowercase, number, and special character'
          )
        }
      }
      
      return data
    },
  ],
}
```

### Rate Limiting

Implement rate limiting for auth endpoints:

```typescript
// Use a library like express-rate-limit or implement in custom routes
import rateLimit from 'express-rate-limit'

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many login attempts, please try again later',
})
```

### Session Security

```typescript
export default buildConfig({
  cookies: {
    sameSite: 'strict',  // 'lax' | 'strict' | 'none'
    secure: true,        // HTTPS only in production
    httpOnly: true,      // Prevent JavaScript access
    maxAge: 60 * 60 * 24, // 24 hours
  },
})
```

### Sensitive Field Protection

```typescript
{
  name: 'password',
  type: 'text',
  admin: {
    hidden: true,  // Never show in admin
  },
  access: {
    read: () => false,  // Never return in API responses
  },
}
```

## Common Patterns

### Multi-Role User System

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    {
      name: 'roles',
      type: 'relationship',
      relationTo: 'roles',
      hasMany: true,
      required: true,
      defaultValue: ['user'],
    },
  ],
}

export const Roles: CollectionConfig = {
  slug: 'roles',
  access: {
    read: ({ req }) => req.user?.role === 'admin',
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
    },
    {
      name: 'permissions',
      type: 'array',
      fields: [
        {
          name: 'resource',
          type: 'text',
        },
        {
          name: 'action',
          type: 'select',
          options: ['read', 'create', 'update', 'delete'],
        },
      ],
    },
  ],
}
```

### Organization-Based Access

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: ({ req }) => {
      // Only users in same organization can read
      if (!req.user?.organization) return false
      
      return {
        organization: { equals: req.user.organization },
      }
    },
  },
  fields: [
    {
      name: 'organization',
      type: 'relationship',
      relationTo: 'organizations',
      required: true,
    },
  ],
}
```

See [API Integration](05-api-integration.md) for authenticated API patterns.
