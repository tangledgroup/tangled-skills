# Access Control

## Role System

The template uses a two-role system: `admin` and `customer`. Roles are stored as a hasMany select field on users with `saveToJWT: true` for efficient access checks without database lookups.

### Role Checking Utility

```typescript
// src/access/utilities.ts
import type { User } from '@/payload-types'

export const checkRole = (allRoles: User['roles'] = [], user?: User | null): boolean => {
  if (user && allRoles) {
    return allRoles.some((role) =>
      user?.roles?.some((individualRole) => individualRole === role)
    )
  }
  return false
}
```

## Access Control Functions

### adminOnly

Denies all access unless the user has the `admin` role:

```typescript
export const adminOnly: Access = ({ req: { user } }) => {
  if (user) return checkRole(['admin'], user)
  return false
}
```

Used for: page create/update/delete, product admin operations, transaction access, form submissions admin.

### adminOrPublishedStatus

Allows full access for admins; restricts non-admins to published content only:

```typescript
export const adminOrPublishedStatus: Access = ({ req: { user } }) => {
  if (user && checkRole(['admin'], user)) return true
  return { _status: { equals: 'published' } }
}
```

Used for: pages read, products read (public sees only published).

### adminOrSelf

Allows admins full access; allows users to access their own document:

```typescript
export const adminOrSelf: Access = ({ req: { user } }) => {
  if (user && checkRole(['admin'], user)) return true
  if (user?.id) return { id: { equals: user.id } }
  return false
}
```

Used for: users read/update (customers can view and update their own profile).

### isDocumentOwner

Checks document ownership via the `customer` field:

```typescript
export const isDocumentOwner: Access = ({ req }) => {
  if (req.user && checkRole(['admin'], req.user)) return true
  if (req.user?.id) return { customer: { equals: req.user.id } }
  return false
}
```

Used for: carts (customers access their own cart), addresses (customers access their own addresses).

### adminOrCustomerOwner

Similar to `isDocumentOwner` but explicitly uses the `customer` field name:

```typescript
export const adminOrCustomerOwner: Access = ({ req: { user } }) => {
  if (user && checkRole(['admin'], user)) return true
  if (user?.id) return { customer: { equals: user.id } }
  return false
}
```

### publicAccess

Unrestricted access:

```typescript
export const publicAccess: Access = () => true
```

Used for: user registration (public can create accounts).

### adminOnlyFieldAccess

Field-level access restricted to admins only:

```typescript
export const adminOnlyFieldAccess: FieldAccess = ({ req: { user } }) =>
  user ? checkRole(['admin'], req.user) : false
```

Used for: user roles field (only admins can read/write roles).

## Access Control by Collection

### Users

| Operation | Access |
|-----------|--------|
| admin | admin role only |
| create | public (self-registration) |
| read | admin or self |
| update | admin or self |
| delete | admin only |
| unlock | admin only |

Roles field: admin-only at field level (create, read, update).

First user is automatically assigned `admin` role via `ensureFirstUserIsAdmin` beforeChange hook.

### Pages

| Operation | Access |
|-----------|--------|
| create | admin only |
| read | admin or published status |
| update | admin only |
| delete | admin only |

### Products / Variants

| Operation | Access |
|-----------|--------|
| create | admin only |
| read | admin or published status |
| update | admin only |
| delete | admin only |

### Carts

| Operation | Access |
|-----------|--------|
| read | customer owns cart OR guest with valid secret |
| update | same as read |
| create | authenticated or guest (when allowGuestCarts enabled) |
| delete | admin only |

### Addresses

| Operation | Access |
|-----------|--------|
| read | customer owns address |
| update | customer owns address |
| create | authenticated user |
| delete | customer owns address |

### Orders

| Operation | Access |
|-----------|--------|
| read | admin, or customer owns order, or guest with valid accessToken + email |
| update | admin only |
| delete | admin only |

### Transactions

| Operation | Access |
|-----------|--------|
| read | admin only |
| update | admin only |
| delete | admin only |

## Access Config for Plugin

The ecommerce plugin requires these access functions to be provided:

```typescript
ecommercePlugin({
  access: {
    isAdmin,              // Required — checks admin role
    isDocumentOwner,      // Required — checks customer field ownership
    adminOnlyFieldAccess, // Required — field-level admin restriction
    adminOrPublishedStatus, // Required — published content filtering
    customerOnlyFieldAccess, // Optional — customer-only field access
    isAuthenticated,      // Optional — any authenticated user
    isCustomer,           // Optional — non-admin authenticated user
    publicAccess,         // Optional — unrestricted access
  },
})
```

## Security Best Practices

1. Always set `overrideAccess: false` when passing `user` to Local API calls
2. Use `saveToJWT: true` on roles field to avoid database lookups in access checks
3. Field-level access returns boolean only (no query constraints)
4. Default to restrictive access, gradually add permissions
5. Never trust client-provided data — validate on the server
6. Pass `req` to nested operations in hooks to maintain transaction atomicity
