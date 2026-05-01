# Hooks and Lifecycle

## Document-Level Hooks

Document hooks run at the collection or global level for every CRUD operation.

### Create and Update Hooks

**beforeValidate** — runs before validation, can modify incoming data:

```typescript
hooks: {
  beforeValidate: [
    async ({ data, operation }) => {
      if (operation === 'create' && !data.slug) {
        return { ...data, slug: generateSlug(data.title) }
      }
      return data
    },
  ],
},
```

**beforeChange** — runs after validation but before saving to the database:

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation, originalDoc }) => {
      if (operation === 'update') {
        // Log changes
        console.log('Changed from', originalDoc?.title, 'to', data.title)
      }
      return data
    },
  ],
},
```

**afterChange** — runs after the document is saved, receives both the input data and resulting doc:

```typescript
hooks: {
  afterChange: [
    async ({ doc, previousDoc, operation }) => {
      if (operation === 'create') {
        // Trigger welcome email
        await sendWelcomeEmail(doc.email)
      }
      if (doc._status === 'published' && previousDoc?._status !== 'published') {
        // Revalidate Next.js cache
        await revalidateTag(`post-${doc.id}`)
      }
    },
  ],
},
```

**beforeRead** — runs before the document is returned, can transform data:

```typescript
hooks: {
  beforeRead: [
    ({ doc }) => {
      // Remove sensitive fields from response
      const { password, ...safeDoc } = doc
      return safeDoc
    },
  ],
},
```

**afterRead** — runs after reading, useful for populating related data:

```typescript
hooks: {
  afterRead: [
    async ({ doc, req }) => {
      // Populate author data from a restricted collection
      if (doc.author) {
        const author = await req.payload.findByID({
          collection: 'users',
          id: doc.author,
          depth: 0,
        })
        return { ...doc, populatedAuthor: author }
      }
      return doc
    },
  ],
},
```

### Delete Hooks

**beforeDelete** — runs before deletion:

```typescript
hooks: {
  beforeDelete: [
    async ({ id, req }) => {
      // Archive the document before deleting
      const doc = await req.payload.findByID({ collection: 'posts', id })
      await req.payload.create({
        collection: 'archived-posts',
        data: { ...doc, archivedAt: new Date() },
      })
    },
  ],
},
```

**afterDelete** — runs after deletion:

```typescript
hooks: {
  afterDelete: [
    async ({ doc, id }) => {
      // Clean up related resources
      await deleteRelatedCache(id)
    },
  ],
},
```

### Before/After Operation Hooks

These wrap the entire operation including all other hooks:

```typescript
hooks: {
  beforeOperation: [
    async ({ operation, args }) => {
      console.log(`Starting ${operation}`)
      // Can modify query args before the operation runs
      return args
    },
  ],
  afterOperation: [
    async ({ operation, result }) => {
      console.log(`${operation} complete`, result.totalDocs)
      // Can modify the result returned to the caller
      return result
    },
  ],
},
```

### AfterError Hook

Handles errors from any operation:

```typescript
hooks: {
  afterError: [
    ({ error, req }) => {
      console.error('Operation error:', error.message)
      // Return custom error response
      return {
        response: { errors: [{ message: 'Something went wrong' }] },
        status: 500,
      }
    },
  ],
},
```

## Field-Level Hooks

Field hooks run for individual fields and can transform field values.

### Available Field Hooks

- **beforeValidate** — before field validation
- **beforeChange** — after validation, before saving
- **afterChange** — after saving
- **afterRead** — when reading the document
- **beforeDuplicate** — when duplicating a document

### Field Hook Example

```typescript
{
  name: 'slug',
  type: 'text',
  hooks: {
    beforeValidate: [
      ({ value, siblingData, operation }) => {
        if (operation === 'create' && !value) {
          return generateSlug(siblingData.title)
        }
        return value
      },
    ],
    beforeChange: [
      ({ value }) => value?.toLowerCase().replace(/\s+/g, '-'),
    ],
  },
}
```

### Field Hook Arguments

Field hooks receive a `FieldHookArgs` object:

```typescript
type FieldHookArgs = {
  value: any              // Current field value
  siblingData: object     // Sibling field values
  originalDoc?: Document  // Original document (update operations)
  operation?: 'create' | 'update' | 'read' | 'delete'
  req: PayloadRequest
  data?: Partial<Document> // Full document data
  previousValue?: any     // Previous value (beforeChange, afterChange)
  previousSiblingDoc?: object // Previous sibling data
}
```

## Auth-Specific Hooks

Collections with `auth: true` support additional hooks:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  hooks: {
    beforeLogin: [({ user, req }) => {
      // Run before login completes
    }],
    afterLogin: [({ user, token, req }) => {
      // Run after login, receive the JWT token
    }],
    afterLogout: [({ req }) => {
      // Run after logout
    }],
    afterMe: [({ response, req }) => {
      // Run after /me endpoint
    }],
    afterRefresh: [({ token, exp, req }) => {
      // Run after token refresh
    }],
    afterForgotPassword: [({ req }) => {
      // Run after forgot password email is sent
    }],
  },
}
```

## Hook Execution Order

1. `beforeOperation` (document)
2. `beforeValidate` (document)
3. `beforeValidate` (field, for each field)
4. Validation runs
5. `beforeChange` (document)
6. `beforeChange` (field, for each field)
7. Database write
8. `afterChange` (field, for each field)
9. `afterChange` (document)
10. `afterOperation` (document)

For read operations:

1. `beforeOperation` (document)
2. Database read
3. `beforeRead` (document)
4. `afterRead` (field, for each field)
5. `afterRead` (document)
6. `afterOperation` (document)

## Context Passing

Use `req.context` to pass data between hooks:

```typescript
// In a beforeChange hook
hooks: {
  beforeChange: [
    ({ data, req }) => {
      req.context.skipValidation = true
      return data
    },
  ],
  afterChange: [
    ({ doc, req }) => {
      if (req.context.skipValidation) {
        console.log('Validation was skipped')
      }
    },
  ],
}
```

## Common Hook Patterns

### Populate Related Data

```typescript
// In a Posts collection, populate author details from restricted Users collection
{
  name: 'populatedAuthors',
  type: 'array',
  access: { update: () => false },
  fields: [
    { name: 'id', type: 'text' },
    { name: 'name', type: 'text' },
    { name: 'avatar', type: 'upload', relationTo: 'media' },
  ],
}

// Hook to populate it
hooks: {
  afterRead: [
    async ({ doc, req }) => {
      if (doc.authors) {
        const populatedAuthors = await Promise.all(
          doc.authors.map(async (author) => {
            const user = await req.payload.findByID({
              collection: 'users',
              id: typeof author === 'object' ? author.value : author,
              depth: 0,
              select: { id: true, name: true, avatar: true },
            })
            return user ? { id: user.id, name: user.name, avatar: user.avatar } : null
          })
        )
        return { ...doc, populatedAuthors: populatedAuthors.filter(Boolean) }
      }
      return doc
    },
  ],
}
```

### Auto-populate Published Date

```typescript
hooks: {
  beforeChange: [
    ({ data, operation }) => {
      if (data._status === 'published' && !data.publishedAt) {
        return { ...data, publishedAt: new Date() }
      }
      return data
    },
  ],
}
```

### Next.js Cache Revalidation

```typescript
import { revalidateTag } from 'next/cache'

export const revalidatePage = async ({ doc, previousDoc, operation }) => {
  if (operation === 'create' || operation === 'update') {
    revalidateTag(`page-${doc.slug}`)
    revalidateTag('pages-list')
  }
  if (operation === 'delete' && previousDoc) {
    revalidateTag(`page-${previousDoc.slug}`)
    revalidateTag('pages-list')
  }
}
```
