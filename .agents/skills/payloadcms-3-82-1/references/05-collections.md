# Collections Guide

Collections are the core building blocks of Payload CMS. They define content types with type-safe schemas, access control, hooks, and custom behavior.

## Basic Collection Structure

```typescript title="src/collections/Posts.ts"
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  // Unique identifier (plural, lowercase)
  slug: 'posts',
  
  // Admin panel configuration
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
    description: 'Manage blog posts and articles',
    hidden: false,
    useAsTitle: 'title',
  },
  
  // Access control (see Access Control guide)
  access: {
    read: ({ req }) => true,
    create: ({ req }) => req.user?.roles?.includes('admin'),
    update: ({ req }) => true,
    delete: ({ req }) => true,
  },
  
  // Fields definition
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
  ],
  
  // Enable timestamps (createdAt, updatedAt)
  timestamps: true,
  
  // Version control for drafts
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
}
```

## Collection Options

### Slug

The slug is a unique identifier for the collection. It determines:
- API endpoint: `/api/posts`
- Database collection name
- Import path in config

**Rules:**
- Must be lowercase
- Use plural form (e.g., `posts`, not `post`)
- Alphanumeric with hyphens only
- Must be unique across all collections

### Admin Configuration

```typescript
admin: {
  // Field used as document title in UI
  useAsTitle: 'title',
  
  // Default columns shown in list view
  defaultColumns: ['title', 'author', 'status', 'createdAt'],
  
  // Description shown in collection selector
  description: 'Manage blog posts',
  
  // Hide from admin panel
  hidden: false,
  
  // Custom grouping in sidebar
  group: 'Content',
  
  // Prevent deletion
  preventDelete: false,
  
  // Enable preview mode
  preview: (data) => `/${data.slug}`,
}
```

### Grouping Collections

Organize collections in the admin sidebar:

```typescript
// posts.ts
admin: { group: 'Content' }

// pages.ts
admin: { group: 'Content' }

// products.ts
admin: { group: 'Ecommerce' }

// orders.ts
admin: { group: 'Ecommerce' }
```

## Hooks

Hooks allow you to run custom logic at specific points in the document lifecycle.

### Available Hook Types

- `beforeValidate` - Before field validation
- `beforeChange` - Before saving to database
- `afterChange` - After saving to database
- `beforeRead` - Before fetching from database
- `afterRead` - After fetching from database
- `beforeDelete` - Before deleting from database
- `afterDelete` - After deleting from database

### Hook Context

All hooks receive a context object:

```typescript
{
  value: any,           // Field value (field-level hooks)
  data: Record<string, any>,  // All field values
  siblingData: Record<string, any>,  // Sibling fields
  doc: Doc,             // Full document
  req: PayloadRequest,  // Request object
  collection: CollectionConfig,
  operation: 'create' | 'update' | 'read' | 'delete',
}
```

### Before Change Hook

```typescript
fields: [
  {
    name: 'slug',
    type: 'text',
    hooks: {
      beforeChange: [
        async ({ value, siblingData, operation }) => {
          // Auto-generate slug from title on create
          if (!value && operation === 'create' && siblingData.title) {
            return siblingData.title
              .toLowerCase()
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-|-$/g, '')
          }
          return value
        },
      ],
    },
  },
]
```

### After Change Hook - Transaction Safety

**CRITICAL**: Always pass `req` to maintain transaction safety:

```typescript
// ❌ WRONG: Separate transaction (data corruption risk)
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

// ✅ CORRECT: Same transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        req, // Pass req for atomic operation
      })
    },
  ],
}
```

### After Read Hook

```typescript
fields: [
  {
    name: 'fullName',
    type: 'text',
    virtual: true,
    hooks: {
      afterRead: [
        ({ siblingData }) => {
          return `${siblingData.firstName} ${siblingData.lastName}`
        },
      ],
    },
  },
]
```

## Validation

### Field-Level Validation

```typescript
fields: [
  {
    name: 'email',
    type: 'text',
    required: true,
    validate: (value) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value) ? true : 'Invalid email address'
    },
  },
  {
    name: 'age',
    type: 'number',
    validate: (value) => {
      if (value < 0) return 'Age cannot be negative'
      if (value > 150) return 'Invalid age'
      return true
    },
  },
]
```

### Cross-Field Validation

Use `beforeChange` hook for complex validation:

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation }) => {
      if (operation === 'create' && !data.password) {
        throw new Error('Password is required')
      }
      
      if (data.endDate && data.startDate && data.endDate < data.startDate) {
        throw new Error('End date must be after start date')
      }
      
      return data
    },
  ],
}
```

## Relationships

### Basic Relationship

```typescript
fields: [
  {
    name: 'author',
    type: 'relationship',
    relationTo: 'users',
    required: true,
  },
  {
    name: 'categories',
    type: 'relationship',
    relationTo: 'categories',
    hasMany: true,
  },
]
```

### Polymorphic Relationships

```typescript
fields: [
  {
    name: 'relatedDocuments',
    type: 'relationship',
    relationTo: ['posts', 'pages', 'products'],
    hasMany: true,
  },
]
```

### Relationship with Filtering

```typescript
fields: [
  {
    name: 'category',
    type: 'relationship',
    relationTo: 'categories',
    filterOptions: ({ data }) => {
      // Only show active categories
      return { active: { equals: true } }
    },
  },
]
```

### Populate Relationships

Automatically populate related documents:

```typescript
fields: [
  {
    name: 'author',
    type: 'relationship',
    relationTo: 'users',
    admin: {
      position: 'sidebar',
    },
  },
]

// In collection config
versions: {
  drafts: true,
}

// Query with populate
const posts = await payload.find({
  collection: 'posts',
  overrideAccess: false,
  user: req.user,
  depth: 2, // Populate relationships up to 2 levels deep
})
```

## Upload Fields

### Basic Upload

```typescript
fields: [
  {
    name: 'coverImage',
    type: 'upload',
    relationTo: 'media',
    required: true,
  },
]
```

### Multiple Uploads

```typescript
fields: [
  {
    name: 'gallery',
    type: 'upload',
    relationTo: 'media',
    hasMany: true,
  },
]
```

## Array and Block Fields

### Array Field

```typescript
fields: [
  {
    name: 'teamMembers',
    type: 'array',
    fields: [
      { name: 'name', type: 'text', required: true },
      { name: 'role', type: 'text' },
      { name: 'avatar', type: 'upload', relationTo: 'media' },
    ],
  },
]
```

### Block Field (Content Builder)

```typescript
fields: [
  {
    name: 'layout',
    type: 'blocks',
    blocks: [
      {
        slug: 'hero',
        labels: {
          singular: 'Hero',
          plural: 'Hero Sections',
        },
        fields: [
          { name: 'title', type: 'text', required: true },
          { name: 'subtitle', type: 'text' },
          { name: 'backgroundImage', type: 'upload', relationTo: 'media' },
        ],
      },
      {
        slug: 'content',
        labels: {
          singular: 'Content',
          plural: 'Content Sections',
        },
        fields: [
          { name: 'content', type: 'richText' },
          { name: 'align', type: 'select', options: ['left', 'center', 'right'] },
        ],
      },
      {
        slug: 'gallery',
        labels: {
          singular: 'Gallery',
          plural: 'Galleries',
        },
        fields: [
          { name: 'images', type: 'upload', relationTo: 'media', hasMany: true },
          { name: 'columns', type: 'number', min: 1, max: 4, defaultValue: 3 },
        ],
      },
    ],
  },
]
```

## Group and Tab Fields

### Group Field

```typescript
fields: [
  {
    name: 'seo',
    type: 'group',
    fields: [
      { name: 'title', type: 'text' },
      { name: 'description', type: 'text' },
      { name: 'keywords', type: 'text', hasMany: true },
    ],
  },
]

// Access: doc.seo.title
```

### Tab Field

```typescript
fields: [
  {
    name: 'settings',
    type: 'tab',
    fields: [
      { name: 'published', type: 'checkbox' },
      { name: 'featured', type: 'checkbox' },
    ],
  },
]

// Access: doc.published (flattened)
```

### Named Tabs

```typescript
fields: [
  {
    name: 'content',
    type: 'tab',
    fields: [
      { name: 'title', type: 'text' },
      { name: 'body', type: 'richText' },
    ],
  },
  {
    name: 'metadata',
    type: 'tab',
    fields: [
      { name: 'author', type: 'relationship', relationTo: 'users' },
      { name: 'publishedAt', type: 'date' },
    ],
  },
]

// Access: doc.content.title, doc.metadata.author
```

## Localization

Enable multi-language support:

```typescript
// In payload.config.ts
 localization: {
  locales: [
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Spanish' },
    { code: 'fr', label: 'French' },
  ],
  defaultLocale: 'en',
  fallback: true,
}

// In collection
fields: [
  { name: 'title', type: 'text', localized: true },
  { name: 'content', type: 'richText', localized: true },
  { name: 'slug', type: 'text' }, // Not localized
]
```

Access localized content:
```typescript
const post = await payload.find({
  collection: 'posts',
  locale: 'es', // Fetch Spanish version
})
```

## Versions and Drafts

### Enable Versioning

```typescript
versions: {
  drafts: true,
  maxPerDoc: 10,
  autosave: true,
}
```

### Save as Draft

```typescript
// Create draft
const draft = await payload.create({
  collection: 'posts',
  data: { title: 'My Post', content: '...' },
  draft: true,
})

// Publish draft
const published = await payload.updateVersion({
  collection: 'posts',
  id: draft.id,
  draft: false,
})
```

### Query Drafts

```typescript
// Get all (including drafts)
const allPosts = await payload.find({
  collection: 'posts',
  overrideAccess: false,
  user: req.user,
})

// Get published only
const published = await payload.find({
  collection: 'posts',
  where: { _status: { equals: 'published' } },
})
```

## Common Patterns

### Auto-increment ID

```typescript
fields: [
  {
    name: 'order',
    type: 'number',
    hooks: {
      beforeChange: [
        async ({ req }) => {
          const { docs } = await payload.find({
            collection: req.collection.slug,
            sort: 'order',
            limit: 1,
            depth: 0,
          })
          
          const lastOrder = docs[0]?.order || 0
          return lastOrder + 1
        },
      ],
    },
  },
]
```

### Unique Slug Generation

```typescript
import { slugField } from 'payload'

fields: [
  { name: 'title', type: 'text' },
  slugField({ 
    fieldToUse: 'title',
    length: 50,
  }),
]
```

### Status Field

```typescript
fields: [
  {
    name: 'status',
    type: 'select',
    options: [
      { label: 'Draft', value: 'draft' },
      { label: 'Published', value: 'published' },
      { label: 'Archived', value: 'archived' },
    ],
    defaultValue: 'draft',
    required: true,
  },
]
```

## Performance Tips

1. **Use `depth` parameter** to control relationship population depth
2. **Index frequently queried fields** with `index: true`
3. **Use `limit` and pagination** for large datasets
4. **Enable caching** for read-heavy collections
5. **Use projections** to fetch only needed fields

## Troubleshooting

### Collection Not Showing Up

- Check slug is unique
- Verify collection is added to config array
- Ensure `hidden: false` in admin config
- Run `bun run build` to rebuild import map

### Hook Not Firing

- Verify hook name matches lifecycle event
- Check hook is in correct location (field-level vs collection-level)
- Ensure async hooks are properly awaited

### Type Errors

- Run `bun run generate:types` after schema changes
- Check imports from `payload-types`
- Verify field names match exactly
