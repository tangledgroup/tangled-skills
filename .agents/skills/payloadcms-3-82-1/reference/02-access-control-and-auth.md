# Access Control and Authentication

## Access Control Overview

Payload provides three levels of access control:

1. **Collection-level** — control create, read, update, delete operations
2. **Field-level** — control read/write per field
3. **Document-level** — return a Where query to filter which documents are visible

Access functions receive an `AccessArgs` object with `req` (containing the authenticated user), `id`, and `data`.

### Access Result Types

Return one of:

- `true` — full access
- `false` — deny access
- A `Where` query object — partial access, filtering documents

```typescript
import type { Access } from 'payload'

// Full access for authenticated users
export const authenticated: Access = ({ req: { user } }) => Boolean(user)

// Public read, authenticated write
export const publicRead: Access = ({ req: { user } }) => {
  return !!user  // true if logged in
}

// Document-level filtering
export const ownDocsOnly: Access = ({ req: { user }, id }) => {
  if (!user) return false
  if (user.role === 'admin') return true
  return { createdBy: { equals: user.id } }
}
```

### Collection-Level Access

```typescript
export const Pages: CollectionConfig = {
  slug: 'pages',
  access: {
    create: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
    delete: authenticated,
  },
}
```

### Field-Level Access

```typescript
{
  name: 'internalNotes',
  type: 'textarea',
  access: {
    read: ({ req: { user } }) => user?.role === 'admin',
    create: ({ req: { user } }) => user?.role === 'admin',
    update: ({ req: { user } }) => user?.role === 'admin',
  },
}
```

### Complex Access Patterns

**Role-based access with tenant filtering:**

```typescript
export const tenantAccess: Access = ({ req: { user } }) => {
  if (!user) return false
  if (user.role === 'admin') return true
  return { tenant: { in: user.tenants } }
}
```

**Published content access:**

```typescript
export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  if (user) return true
  return { _status: { equals: 'published' } }
}
```

## Authentication

### Enabling Auth on a Collection

Set `auth: true` on any collection to enable built-in authentication:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: { useAsTitle: 'email' },
  fields: [
    {
      name: 'role',
      type: 'select',
      options: ['admin', 'editor', 'author'],
      required: true,
      defaultValue: 'author',
    },
  ],
}
```

This automatically adds `email`, `password`, and account lockout fields.

### Auth Configuration Options

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    token: {
      // Custom cookie name
      cookieName: 'my-app-token',
      // Extend JWT expiry (default: 1 day)
      maxAge: 3600 * 24 * 7,
    },
    // Enable API key authentication
    apiKey: {
      saltLength: 16,
      // Field name for the API key hash (default: 'api_key')
      permissions: ({ req }) => ({
        // Define what the API key can access
        collections: { users: { read: true } },
      }),
    },
    // Deep populate user data on login
    depth: 1,
    // Lock out account after failed attempts
    maxLoginAttempts: 5,
    lockTime: 15 * 60 * 1000, // 15 minutes
    // Custom verify email and forgot password emails
    verify: {
      generateEmailHTML: ({ token, user }) => `<a href="${token}">Verify</a>`,
      generateEmailSubject: () => 'Verify your email',
    },
    forgotPassword: {
      generateEmailHTML: ({ token }) => `<a href="${token}">Reset</a>`,
      generateEmailSubject: () => 'Reset your password',
    },
  },
}
```

### Auth Hooks

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  hooks: {
    beforeLogin: [({ user }) => console.log('User logged in:', user.id)],
    afterLogin: [({ user, token }) => console.log('Token issued')],
    afterLogout: [() => console.log('User logged out')],
    afterMe: [({ response }) => console.log('Me endpoint called')],
    afterRefresh: [({ token }) => console.log('Token refreshed')],
    afterForgotPassword: [() => console.log('Password reset email sent')],
  },
}
```

### Custom Auth Strategies

Implement custom authentication strategies:

```typescript
import type { AuthStrategy } from 'payload'

// API Key strategy (built-in, also available as JWT)
import { APIKeyAuthentication } from 'payload'
import { JWTAuthentication } from 'payload'

// Custom strategy
const customAuthStrategy: AuthStrategy = {
  name: 'custom',
  authenticate: async ({ headers, payload }) => {
    const apiKey = headers.get('x-api-key')
    if (!apiKey) return { user: null }

    const user = await payload.find({
      collection: 'users',
      where: { apiKey: { equals: apiKey } },
    })

    return { user: user.docs[0] || null }
  },
}
```

Register in config:

```typescript
export default buildConfig({
  auth: {
    strategies: [JWTAuthentication, APIKeyAuthentication, customAuthStrategy],
  },
  // ...
})
```

### JWT Configuration

Configure JWT order and options:

```typescript
export default buildConfig({
  auth: {
    // Order of JWT retrieval methods
    jwtOrder: ['JWT', 'Bearer', 'cookie'],
  },
  // Cookie prefix for JWT cookies
  cookiePrefix: 'payload',
  // Secret for signing JWTs (also required at root level)
  secret: process.env.PAYLOAD_SECRET,
})
```

### Using Auth in Server Components

```typescript
import { getPayload } from 'payload'
import type { TypedUser } from 'payload'

export async function getCurrentUser() {
  const payload = await getPayload({ config: configPromise })

  // In a Next.js server component, use the Next.js headers/cookies
  // to extract the JWT and authenticate
  const { user } = await payload.auth({
    headers: new Headers({
      cookie: cookies().toString(),
    }),
  })

  return user
}
```

### Permissions Object

The `Permissions` type defines what a user can access:

```typescript
type Permissions = {
  canAccessAdmin: boolean
  collections: {
    [slug: string]: {
      create?: true
      delete?: true
      read?: true
      readVersions?: true
      unlock?: true  // auth-enabled collections only
      update?: true
      fields: {
        [fieldName: string]: {
          create?: true
          read?: true
          update?: true
          fields?: { [subField: string]: any }
        }
      }
    }
  }
  globals: {
    [slug: string]: {
      read?: true
      readVersions?: true
      update?: true
      fields: { [fieldName: string]: any }
    }
  }
}
```

Access the current user's permissions via `req.permissions` in hooks and access functions.

## Security Best Practices

- Always set `PAYLOAD_SECRET` as an environment variable
- Use HTTP-only cookies for JWT storage (default behavior)
- Enable CSRF protection by configuring `csrf` origins in the config
- Set CORS origins explicitly rather than using wildcard
- Use field-level access control to protect sensitive fields
- Implement account lockout for brute-force protection
- Use `overrideAccess: true` only when necessary and audit its usage
