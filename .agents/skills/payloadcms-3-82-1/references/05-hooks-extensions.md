# Hooks & Extensions Reference

Complete guide to lifecycle hooks and plugin development in Payload CMS v3.82.1 for extending functionality and automating workflows.

## Hook Overview

Payload provides lifecycle hooks at multiple levels:
- **Collection Hooks**: Run on create, read, update, delete operations
- **Field Hooks**: Run on individual field validation and changes

### Hook Execution Order

```
1. beforeValidate  → Data formatting and normalization
2. validate        → Custom validation logic
3. beforeChange    → Business logic and data transformation
4. Database write  → Actual data persistence
5. afterChange     → Side effects (notifications, caching, etc.)
6. afterRead       → Computed fields and data enrichment
```

## Collection Hooks

### beforeValidate Hook

Runs first, before any validation. Use for data formatting and normalization:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    beforeValidate: [
      async ({ data, operation, req }) => {
        // Auto-generate slug from title if not provided
        if (operation === 'create' && data?.title && !data.slug) {
          data.slug = slugify(data.title)
        }
        
        // Normalize email addresses
        if (data?.email) {
          data.email = data.email.toLowerCase().trim()
        }
        
        return data
      },
    ],
  },
}
```

**Use Cases**:
- Auto-generate slugs from titles
- Normalize data formats (emails, phone numbers)
- Set default values conditionally
- Transform incoming data structure

### beforeChange Hook

Runs after validation, before database write. Use for business logic:

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation, req, originalDoc }) => {
      // Set published date when publishing
      if (operation === 'update' && data?.status === 'published') {
        data.publishedAt = new Date()
        data.publishedBy = req.user?.id
      }
      
      // Track status changes
      if (operation === 'update' && originalDoc) {
        if (originalDoc.status !== data.status) {
          data.statusHistory = [
            ...(originalDoc.statusHistory || []),
            {
              from: originalDoc.status,
              to: data.status,
              changedAt: new Date(),
              changedBy: req.user?.id,
            },
          ]
        }
      }
      
      return data
    },
  ],
}
```

**Use Cases**:
- Set timestamps on status changes
- Calculate derived values
- Implement business rules
- Track audit information

### afterChange Hook

Runs after database write. Use for side effects:

```typescript
hooks: {
  afterChange: [
    async ({ doc, req, operation, previousDoc, context }) => {
      // Prevent infinite loops with context flag
      if (context.skipNotification) return
      
      // Send notification on create
      if (operation === 'create') {
        await sendEmail({
          to: doc.author.email,
          subject: 'Post Created',
          body: `Your post "${doc.title}" has been created.`,
        })
      }
      
      // Notify on publish
      if (operation === 'update' && doc.status === 'published' && previousDoc.status !== 'published') {
        await notifySubscribers({
          post: doc,
          action: 'published',
        })
      }
      
      // Invalidate cache
      await invalidateCache(`post:${doc.id}`)
      
      return doc
    },
  ],
}
```

**Use Cases**:
- Send notifications and emails
- Invalidate caches
- Trigger webhooks
- Update search indexes
- Create audit log entries

### afterRead Hook

Runs after reading documents. Use for computed fields and data enrichment:

```typescript
hooks: {
  afterRead: [
    async ({ doc, req }) => {
      // Add computed word count
      if (doc.content) {
        doc.wordCount = doc.content.split(/\s+/).length
      }
      
      // Add reading time estimate
      if (doc.wordCount) {
        doc.readingTime = Math.ceil(doc.wordCount / 200) // 200 words per minute
      }
      
      // Mask sensitive data for non-admin users
      if (req.user && !req.user.roles?.includes('admin')) {
        delete doc.internalNotes
        delete doc.analyticData
      }
      
      return doc
    },
  ],
}
```

**Use Cases**:
- Add computed/calculated fields
- Enrich data from external sources
- Mask sensitive data based on permissions
- Format data for API responses

### beforeDelete Hook

Runs before document deletion. Use for cleanup and cascade deletes:

```typescript
hooks: {
  beforeDelete: [
    async ({ req, id }) => {
      // Cascade delete related comments
      await req.payload.delete({
        collection: 'comments',
        where: { post: { equals: id } },
        req, // CRITICAL: Pass req for transaction safety
      })
      
      // Delete associated media files
      const doc = await req.payload.findByID({
        collection: 'posts',
        id,
        depth: 0,
      })
      
      if (doc.coverImage) {
        await deleteFromFileSystem(doc.coverImage)
      }
      
      // Log deletion for audit trail
      await req.payload.create({
        collection: 'audit-log',
        data: {
          action: 'post_deleted',
          documentId: id,
          deletedBy: req.user?.id,
        },
        req,
      })
    },
  ],
}
```

**Use Cases**:
- Cascade delete related documents
- Clean up file system resources
- Send deletion notifications
- Create audit trail entries

## Field Hooks

Field hooks run on individual fields and receive field-specific context:

```typescript
{
  name: 'slug',
  type: 'text',
  hooks: {
    beforeValidate: [
      ({ value, siblingData, operation }) => {
        // Auto-generate from title if empty
        if (!value && operation === 'create' && siblingData.title) {
          return slugify(siblingData.title)
        }
        return value
      },
    ],
  },
}
```

### Field Hook Context

Field hooks receive different context than collection hooks:

```typescript
{
  name: 'email',
  type: 'email',
  hooks: {
    beforeValidate: [
      ({ value, siblingData, data, operation, req }) => {
        // value: Current field value
        // siblingData: Other fields in the same document
        // data: Full document data (null in some operations)
        // operation: 'create' | 'update'
        // req: Request object with user, payload, context
        
        return value.toLowerCase().trim()
      },
    ],
  },
}
```

## Critical Hook Patterns

### ⚠️ Transaction Safety

**ALWAYS pass `req` to nested operations in hooks:**

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
        req, // Maintains atomicity
      })
    },
  ],
}
```

### ⚠️ Prevent Infinite Loops

**Use context flags to prevent recursive hook execution:**

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

## Common Hook Recipes

### Auto-Generate Slugs

```typescript
import { slugField } from 'payload'

// Using built-in slugField
export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'title', type: 'text', required: true },
    slugField({ fieldToUse: 'title' }),
  ],
}

// Custom slug generation with hooks
{
  name: 'slug',
  type: 'text',
  unique: true,
  hooks: {
    beforeValidate: [
      async ({ value, siblingData, operation, req }) => {
        if (operation === 'create' && !value && siblingData.title) {
          let slug = slugify(siblingData.title)
          const originalSlug = slug
          let counter = 1
          
          // Ensure uniqueness
          while (await slugExists(req, 'posts', slug)) {
            slug = `${originalSlug}-${counter}`
            counter++
          }
          
          return slug
        }
        return value
      },
    ],
  },
}
```

### Track Document History

```typescript
hooks: {
  beforeChange: [
    async ({ data, operation, originalDoc, req }) => {
      if (operation === 'update' && originalDoc) {
        // Track which fields changed
        const changes = {}
        let hasChanges = false
        
        for (const key of Object.keys(data)) {
          if (originalDoc[key] !== data[key]) {
            changes[key] = {
              from: originalDoc[key],
              to: data[key],
            }
            hasChanges = true
          }
        }
        
        if (hasChanges) {
          const history = originalDoc.changeHistory || []
          data.changeHistory = [
            ...history,
            {
              changedAt: new Date(),
              changedBy: req.user?.id,
              changes,
            },
          ]
        }
      }
      
      return data
    },
  ],
}
```

### Send Email Notifications

```typescript
hooks: {
  afterChange: [
    async ({ doc, operation, previousDoc, req }) => {
      // Skip if context flag set
      if (req.context?.skipNotifications) return
      
      // New post notification
      if (operation === 'create' && doc.notifyAuthor) {
        await sendEmail({
          to: doc.author.email,
          subject: `New Post: ${doc.title}`,
          template: 'new-post',
          data: { post: doc },
        })
      }
      
      // Status change notification
      if (operation === 'update' && previousDoc) {
        if (previousDoc.status !== doc.status) {
          await sendEmail({
            to: doc.author.email,
            subject: `Status Changed: ${doc.title}`,
            template: 'status-change',
            data: {
              post: doc,
              oldStatus: previousDoc.status,
              newStatus: doc.status,
            },
          })
        }
      }
      
      return doc
    },
  ],
}
```

### Cache Invalidation

```typescript
hooks: {
  afterChange: [
    async ({ doc, operation, req }) => {
      // Invalidate document-specific cache
      await redis.del(`post:${doc.id}`)
      
      // Invalidate list cache
      await redis.del('posts:list')
      
      // If author changed, invalidate author's post list
      if (operation === 'update' && doc.author !== previousDoc.author) {
        await redis.del(`author:posts:${doc.author}`)
      }
      
      return doc
    },
  ],
}
```

### Search Index Sync

```typescript
hooks: {
  afterChange: [
    async ({ doc, operation, req }) => {
      if (operation === 'create' || operation === 'update') {
        // Add/update document in search index
        await meilisearch.index('posts').addDocuments([
          {
            id: doc.id,
            title: doc.title,
            content: doc.content,
            slug: doc.slug,
            author: doc.author?.name,
            publishedAt: doc.publishedAt,
          },
        ])
      }
      
      if (operation === 'delete') {
        // Remove from search index
        await meilisearch.index('posts').deleteDocument(doc.id)
      }
      
      return doc
    },
  ],
}
```

### External Webhook Integration

```typescript
hooks: {
  afterChange: [
    async ({ doc, operation, req }) => {
      const webhookUrl = process.env.WEBHOOK_URL
      
      if (!webhookUrl) return doc
      
      await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.WEBHOOK_SECRET}`,
        },
        body: JSON.stringify({
          event: `post.${operation}`,
          payload: {
            id: doc.id,
            title: doc.title,
            slug: doc.slug,
            operation,
            timestamp: new Date().toISOString(),
          },
        }),
      })
      
      return doc
    },
  ],
}
```

### Image Processing on Upload

```typescript
export const Media: CollectionConfig = {
  slug: 'media',
  hooks: {
    afterChange: [
      async ({ doc, operation, req }) => {
        if (operation === 'create' && doc.filename) {
          // Generate thumbnails
          const thumbnails = await generateThumbnails(doc.path, [
            { width: 200, height: 200, name: 'thumbnail' },
            { width: 800, height: 600, name: 'medium' },
            { width: 1920, height: 1080, name: 'large' },
          ])
          
          // Update document with thumbnail URLs
          await req.payload.update({
            collection: 'media',
            id: doc.id,
            data: { thumbnails },
            context: { skipHooks: true }, // Prevent infinite loop
            req,
          })
        }
        
        return doc
      },
    ],
  },
}
```

## Plugin Development

### What Are Plugins?

Plugins modify Payload configuration programmatically. Use plugins to:
- Add reusable collections or globals
- Inject fields into multiple collections
- Add custom endpoints
- Modify admin panel behavior

### Basic Plugin Structure

```typescript
import type { Config, Plugin } from 'payload'

interface MyPluginOptions {
  collections?: string[]
  enabled?: boolean
}

export const myPlugin: Plugin =
  (options: MyPluginOptions) =>
  (config: Config): Config => {
    if (!options.enabled) return config
    
    return {
      ...config,
      collections: [
        ...(config.collections || []),
        // Add new collection
        {
          slug: 'my-plugin-data',
          fields: [
            { name: 'data', type: 'json' },
          ],
        },
      ],
    }
  }
```

### Modifying Existing Collections

```typescript
export const seoPlugin: Plugin =
  (options) =>
  (config): Config => ({
    ...config,
    collections: config.collections?.map((collection) => {
      // Add SEO fields to specified collections
      if (options.collections?.includes(collection.slug)) {
        return {
          ...collection,
          fields: [
            ...collection.fields,
            {
              name: 'seo',
              type: 'group',
              fields: [
                { name: 'metaTitle', type: 'text' },
                { name: 'metaDescription', type: 'textarea' },
                { name: 'ogImage', type: 'upload', relationTo: 'media' },
              ],
            },
          ],
        }
      }
      return collection
    }),
  })
```

### Adding Custom Endpoints

```typescript
export const analyticsPlugin: Plugin =
  () =>
  (config): Config => ({
    ...config,
    endpoints: [
      ...(config.endpoints || []),
      {
        path: '/api/analytics/overview',
        method: 'get',
        handler: async (req) => {
          const { payload } = req
          
          const postsCount = await payload.count({ collection: 'posts' })
          const usersCount = await payload.count({ collection: 'users' })
          
          return Response.json({
            posts: postsCount.totalDocs,
            users: usersCount.totalDocs,
          })
        },
      },
    ],
  })
```

### Adding Custom Hooks

```typescript
export const auditLogPlugin: Plugin =
  () =>
  (config): Config => ({
    ...config,
    collections: config.collections?.map((collection) => ({
      ...collection,
      hooks: {
        ...collection.hooks,
        afterChange: [
          ...(collection.hooks?.afterChange || []),
          async ({ doc, operation, req }) => {
            await req.payload.create({
              collection: 'audit-log',
              data: {
                collection: collection.slug,
                documentId: doc.id,
                operation,
                userId: req.user?.id,
                changes: doc,
              },
              req,
            })
          },
        ],
      },
    })),
  })
```

### Using Plugins

```typescript
import { buildConfig } from 'payload'
import { seoPlugin } from './plugins/seo'
import { analyticsPlugin } from './plugins/analytics'

export default buildConfig({
  plugins: [
    seoPlugin({
      collections: ['posts', 'pages'],
    }),
    analyticsPlugin(),
  ],
})
```

## Plugin Best Practices

### 1. Type Safety

Define proper TypeScript types for plugin options:

```typescript
interface SEOPluginOptions {
  collections?: string[]
  enableOGImage?: boolean
}

export const seoPlugin: Plugin<SEOPluginOptions> = (options) => (config) => {
  // Typed options throughout
}
```

### 2. Configuration Merging

Always spread existing config to preserve user settings:

```typescript
// ✅ Correct: Preserve existing config
return {
  ...config,
  collections: [
    ...(config.collections || []),
    newCollection,
  ],
}

// ❌ Wrong: Overwrites existing config
return {
  collections: [newCollection],
}
```

### 3. Conditional Logic

Make plugins configurable and optional:

```typescript
export const myPlugin: Plugin =
  (options) =>
  (config): Config => {
    if (!options.enabled) return config
    
    // Only modify specified collections
    if (!options.collections?.length) return config
    
    return {
      ...config,
      // Modifications...
    }
  }
```

### 4. Error Handling

Handle errors gracefully in plugins:

```typescript
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      try {
        await externalService.sync(doc)
      } catch (error) {
        // Log error but don't fail the operation
        console.error('Failed to sync with external service:', error)
      }
      
      return doc
    },
  ],
}
```

### 5. Context Usage

Use context to prevent conflicts:

```typescript
hooks: {
  afterChange: [
    async ({ doc, req, context }) => {
      // Check if plugin should run
      if (context.skipMyPlugin) return doc
      
      // My plugin logic...
      
      return doc
    },
  ],
}
```

## Popular Plugin Patterns

### Multi-Tenant Plugin

```typescript
export const multiTenantPlugin: Plugin =
  () =>
  (config): Config => ({
    ...config,
    collections: config.collections?.map((collection) => ({
      ...collection,
      fields: [
        {
          name: 'tenant',
          type: 'relationship',
          relationTo: 'tenants',
          required: true,
          index: true,
        },
        ...collection.fields,
      ],
      access: {
        ...collection.access,
        read: async ({ req }) => {
          // Add tenant filtering
          return {
            tenant: { equals: req.user?.tenant },
          }
        },
      },
    })),
  })
```

### i18n Plugin

```typescript
export const i18nPlugin: Plugin =
  (options) =>
  (config): Config => ({
    ...config,
    collections: config.collections?.map((collection) => ({
      ...collection,
      fields: [
        {
          name: 'localized',
          type: 'tabs',
          tabs: options.locales.map((locale) => ({
            name: locale.code,
            label: locale.label,
            fields: collection.fields, // Duplicate fields for each locale
          })),
        },
      ],
    })),
  })
```

### Revision History Plugin

```typescript
export const revisionsPlugin: Plugin =
  () =>
  (config): Config => ({
    ...config,
    collections: [
      ...(config.collections || []),
      {
        slug: 'revisions',
        access: {
          read: ({ req: { user } }) => user?.roles?.includes('admin'),
        },
        fields: [
          { name: 'collection', type: 'text' },
          { name: 'docID', type: 'text' },
          { name: 'revisionData', type: 'json' },
          { name: 'changedBy', type: 'relationship', relationTo: 'users' },
          { name: 'changedAt', type: 'date' },
        ],
      },
    ],
  })
```

## Troubleshooting Hooks

### Common Issues

**Hook not running**:
- Check hook name spelling (`beforeChange` not `before_change`)
- Verify hook is in correct array (`hooks.beforeChange[]`)
- Ensure operation matches (create vs update)

**Infinite loop**:
- Use context flags to prevent recursion
- Check for updates within afterChange hooks
- Use `context.skipHooks` when updating in hooks

**Transaction failures**:
- Always pass `req` to nested operations
- Check database supports transactions (MongoDB needs replica set)
- Review hook execution order

**Performance issues**:
- Avoid expensive operations in afterRead hooks
- Cache results in `req.context`
- Use async/await properly to prevent blocking
