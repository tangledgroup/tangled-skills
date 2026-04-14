# Common Patterns & Best Practices Reference

Essential patterns, best practices, and troubleshooting guide for Payload CMS v3.82.1 development.

## Security Best Practices

### 1. Always Enforce Access Control in Local API

**Most critical security pattern:**

```typescript
// ❌ VULNERABLE: Access control bypassed
const posts = await payload.find({
  collection: 'posts',
  user: currentUser, // Ignored without overrideAccess: false!
})

// ✅ SECURE: Enforces user permissions
const posts = await payload.find({
  collection: 'posts',
  user: currentUser,
  overrideAccess: false, // REQUIRED when passing user
})

// ✅ Admin operation (intentional bypass)
const allPosts = await payload.find({
  collection: 'posts',
  // No user passed, runs with admin privileges
})
```

**Rule**: When passing `user` to Local API, ALWAYS set `overrideAccess: false`

### 2. Maintain Transaction Safety

**Critical for data integrity:**

```typescript
// ❌ DATA CORRUPTION: Separate transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { action: 'post_created' },
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
        data: { action: 'post_created' },
        req, // Maintains atomicity
      })
    },
  ],
}
```

**Rule**: ALWAYS pass `req` to nested operations in hooks

### 3. Prevent Infinite Hook Loops

**Use context flags:**

```typescript
// ❌ INFINITE LOOP
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        req, // Triggers afterChange again!
      })
    },
  ],
}

// ✅ SAFE: Context flag prevents recursion
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

### 4. Use JWT Storage for Frequently Accessed Data

**Performance optimization:**

```typescript
// ✅ Store roles in JWT to avoid database lookups
{
  name: 'roles',
  type: 'select',
  hasMany: true,
  options: ['admin', 'editor', 'user'],
  saveToJWT: true, // Include in JWT token
}

// Fast access control check (no DB query)
const adminOnly = ({ req: { user } }) => {
  return user?.roles?.includes('admin') // From JWT, not database
}
```

### 5. Implement Row-Level Security

**Query constraints for data isolation:**

```typescript
// Users see only their own documents
const ownDocumentsOnly = ({ req: { user } }) => {
  if (!user) return false
  
  if (user.roles?.includes('admin')) return true // Admins see all
  
  return { owner: { equals: user.id } } // Query constraint
}

export const Documents: CollectionConfig = {
  slug: 'documents',
  access: {
    read: ownDocumentsOnly,
    update: ownDocumentsOnly,
    delete: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
}
```

## Performance Best Practices

### 1. Index Frequently Queried Fields

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'status', type: 'select', index: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'author', type: 'relationship', relationTo: 'users', index: true },
  ],
  indexes: [
    // Compound index for common queries
    {
      fields: ['status', 'createdAt'],
      keys: { status: 1, createdAt: -1 },
    },
  ],
}
```

### 2. Limit Relationship Depth

**Prevent over-fetching:**

```typescript
// Default depth is 2 - explicitly limit when needed
const posts = await payload.find({
  collection: 'posts',
  depth: 1, // Only direct relationships
  maxDepth: 2, // Never go deeper than 2 levels
})

// For ID-only queries, use depth 0
const postIDs = await payload.find({
  collection: 'posts',
  depth: 0, // Returns IDs only, no population
  limit: 1000,
})
```

### 3. Use Field Selection

**Fetch only needed fields:**

```typescript
const posts = await payload.find({
  collection: 'posts',
  select: {
    title: true,
    slug: true,
    createdAt: true,
    // Other fields excluded for performance
  },
})
```

### 4. Cache Expensive Operations

**Use request context for caching:**

```typescript
hooks: {
  afterRead: [
    async ({ doc, req }) => {
      // Cache expensive lookup in request context
      if (!req.context.authorStats) {
        req.context.authorStats = await calculateAuthorStats(doc.author)
      }
      
      doc.authorStats = req.context.authorStats
      return doc
    },
  ],
}
```

### 5. Batch Large Operations

**Process documents in batches:**

```typescript
const processInBatches = async (collection, where, batchSize = 100) => {
  let offset = 0
  let hasMore = true
  
  while (hasMore) {
    const { docs, totalDocs } = await payload.find({
      collection,
      where,
      limit: batchSize,
      offset,
    })
    
    for (const doc of docs) {
      await processDocument(doc)
    }
    
    hasMore = offset + docs.length < totalDocs
    offset += batchSize
  }
}
```

## Common Development Patterns

### Auto-generate Slugs

**Using built-in helper:**

```typescript
import { slugField } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'title', type: 'text', required: true },
    slugField({ fieldToUse: 'title' }), // Auto-generates slug
  ],
}
```

**Custom slug with uniqueness:**

```typescript
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

### Draft Publishing Workflow

**Complete draft workflow with status:**

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  versions: {
    drafts: {
      autosave: true,
      schedulePublish: true,
      validate: false, // Don't validate drafts
    },
    maxPerDoc: 100,
  },
  access: {
    read: ({ req: { user } }) => {
      if (user) return true // Authenticated users see drafts
      return { _status: { equals: 'published' } } // Public sees published only
    },
  },
  fields: [
    {
      name: '_status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
        { label: 'Archived', value: 'archived' },
      ],
      defaultValue: 'draft',
      required: true,
    },
    { name: 'title', type: 'text', required: true },
  ],
}

// Create draft
const draft = await payload.create({
  collection: 'posts',
  data: { title: 'Draft Post' },
  draft: true, // Skip validation
})

// Read draft version
const post = await payload.findByID({
  collection: 'posts',
  id: postId,
  draft: true, // Return draft if available
})

// Publish (update status)
await payload.update({
  collection: 'posts',
  id: postId,
  data: { _status: 'published' },
})
```

### Rich Text with Custom Components

**Lexical editor with custom blocks:**

```typescript
{
  name: 'content',
  type: 'richText',
  lexical: {
    features: () => [
      lexicalFeatureHeadings(),
      lexicalFeatureLists(),
      lexicalFeatureLink({
        fields: ({ defaultFields }) => [
          ...defaultFields,
          {
            name: 'linkType',
            type: 'select',
            options: ['internal', 'external'],
          },
          {
            name: 'newTab',
            type: 'checkbox',
            label: 'Open in new tab',
          },
        ],
      }),
    ],
  },
}
```

### Conditional Fields

**Show/hide fields based on values:**

```typescript
export const ContactForm: CollectionConfig = {
  slug: 'contact-forms',
  fields: [
    {
      name: 'contactMethod',
      type: 'select',
      options: ['email', 'phone', 'address'],
      required: true,
    },
    {
      name: 'email',
      type: 'email',
      admin: {
        condition: (data) => data.contactMethod === 'email',
      },
    },
    {
      name: 'phone',
      type: 'text',
      admin: {
        condition: (data) => data.contactMethod === 'phone',
      },
    },
    {
      name: 'address',
      type: 'group',
      admin: {
        condition: (data) => data.contactMethod === 'address',
      },
      fields: [
        { name: 'street', type: 'text' },
        { name: 'city', type: 'text' },
        { name: 'zipCode', type: 'text' },
      ],
    },
  ],
}
```

### Multi-tenant Isolation

**Complete multi-tenant pattern:**

```typescript
// Tenant collection
export const Tenants: CollectionConfig = {
  slug: 'tenants',
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'domain', type: 'text', unique: true },
    {
      name: 'members',
      type: 'relationship',
      relationTo: 'users',
      hasMany: true,
    },
  ],
}

// User collection with tenant relationship
export const Users: CollectionConfig = {
  slug: 'user',
  auth: true,
  fields: [
    {
      name: 'tenant',
      type: 'relationship',
      relationTo: 'tenants',
      required: true,
      saveToJWT: true, // Include in JWT for fast filtering
    },
  ],
}

// Tenant-isolated collection
export const Projects: CollectionConfig = {
  slug: 'projects',
  fields: [
    {
      name: 'tenant',
      type: 'relationship',
      relationTo: 'tenants',
      required: true,
      index: true,
    },
    { name: 'name', type: 'text', required: true },
  ],
  access: {
    read: ({ req: { user } }) => {
      if (!user) return false
      if (user.roles?.includes('admin')) return // Super admin sees all
      
      // Users only see their tenant's projects
      return { tenant: { equals: user.tenant } }
    },
    create: ({ req: { user } }) => {
      if (!user) return false
      // Auto-assign tenant on creation
      return Boolean(user.tenant)
    },
  },
  hooks: {
    beforeChange: [
      ({ data, req }) => {
        // Auto-assign tenant on creation
        if (!data.tenant && req.user?.tenant) {
          data.tenant = req.user.tenant
        }
        return data
      },
    ],
  },
}
```

### Audit Logging

**Complete audit trail pattern:**

```typescript
// Audit log collection
export const AuditLog: CollectionConfig = {
  slug: 'audit-log',
  access: {
    read: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
  admin: {
    hidden: true, // Hide from admin panel
  },
  fields: [
    { name: 'collection', type: 'text', required: true },
    { name: 'docID', type: 'text', required: true },
    { name: 'operation', type: 'select', options: ['create', 'update', 'delete'] },
    { name: 'userId', type: 'relationship', relationTo: 'users' },
    { name: 'changes', type: 'json' },
    { name: 'timestamp', type: 'date', defaultValue: new Date() },
  ],
}

// Add audit hook to all collections
const auditHook = (collectionSlug: string) => ({
  afterChange: [
    async ({ doc, operation, previousDoc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: {
          collection: collectionSlug,
          docID: doc.id,
          operation,
          userId: req.user?.id,
          changes: {
            current: doc,
            previous: previousDoc,
          },
        },
        req, // Maintain transaction
      })
    },
  ],
})

// Apply to collections
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: auditHook('posts'),
  fields: [/* ... */],
}
```

### Search Integration

**Meilisearch integration pattern:**

```typescript
import MeiliSearch from 'meilisearch'

const meilisearch = new MeiliSearch({
  host: process.env.MEILISEARCH_URL,
  apiKey: process.env.MEILISEARCH_API_KEY,
})

export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    afterChange: [
      async ({ doc, operation, req }) => {
        if (operation === 'create' || operation === 'update') {
          // Add/update in search index
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
  },
}

// Search endpoint
export const searchEndpoint: Endpoint = {
  path: '/api/search',
  method: 'get',
  handler: async (req) => {
    const { q } = req.query
    
    const results = await meilisearch.index('posts').search(q as string, {
      limit: 20,
      attributesToRetrieve: ['id', 'title', 'slug'],
    })
    
    return Response.json(results)
  },
}
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Types Not Updating

**Problem**: TypeScript types not reflecting schema changes.

**Solution**:
```bash
# Regenerate types
npm run generate:types

# Or manually
payload generate:types
```

**Verify**: Check `payload-types.ts` exists and has correct timestamp.

#### Access Control Not Working

**Problem**: Local API bypassing access control.

**Cause**: Missing `overrideAccess: false` when passing user.

**Solution**:
```typescript
// ❌ Wrong
await payload.find({ collection: 'posts', user })

// ✅ Correct
await payload.find({
  collection: 'posts',
  user,
  overrideAccess: false, // REQUIRED
})
```

#### Infinite Hook Loops

**Problem**: Server crashes from recursive hook execution.

**Cause**: Update operation in afterChange hook without context flag.

**Solution**:
```typescript
hooks: {
  afterChange: [
    async ({ doc, req, context }) => {
      if (context.skipHooks) return // Prevent recursion
      
      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        context: { skipHooks: true }, // Add flag
        req,
      })
    },
  ],
}
```

#### Component Not Loading

**Problem**: Custom component not appearing in admin panel.

**Solutions**:
1. Regenerate import map: `payload generate:importmap`
2. Check path is relative to `baseDir`
3. Verify export name matches (`default` vs named)
4. Check browser console for errors

#### Transaction Failures in MongoDB

**Problem**: "Transactions not supported" error.

**Cause**: MongoDB requires replica set for transactions.

**Solution**:
```bash
# Start MongoDB with replica set
mongod --replSet rs0 --port 27017

# Initialize replica set (in mongosh)
rs.initiate()
```

**Connection string**:
```typescript
db: mongooseAdapter({
  url: 'mongodb://localhost:27017/payload?replicaSet=rs0',
})
```

#### SQLite Point Field Errors

**Problem**: Point fields not working in SQLite.

**Cause**: Point fields not supported in SQLite adapter.

**Solution**: Use MongoDB or PostgreSQL for geospatial features, or store lat/long as separate number fields.

#### Relationship Not Populating

**Problem**: Relationships returning IDs instead of full documents.

**Cause**: Depth limit reached or incorrect depth parameter.

**Solution**:
```typescript
// Increase depth
const posts = await payload.find({
  collection: 'posts',
  depth: 3, // Populate up to 3 levels deep
})

// Check relationship field has correct relationTo
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users', // Must match collection slug
}
```

#### Upload Failing

**Problem**: File uploads not working.

**Solutions**:
1. Check `staticDir` exists and is writable
2. Verify MIME type restrictions aren't too strict
3. Check file size limits in server configuration
4. For S3, verify credentials and bucket permissions

#### Email Not Sending

**Problem**: Emails not being sent from hooks.

**Solutions**:
1. Verify email adapter is configured in `payload.config.ts`
2. Check SMTP credentials are correct
3. Test email configuration separately
4. Check email is not going to spam folder

### Performance Troubleshooting

#### Slow Queries

**Diagnosis**: Enable query logging.

```typescript
db: mongooseAdapter({
  url: process.env.DATABASE_URL,
  logQueries: true, // Log all queries to console
})
```

**Solutions**:
1. Add indexes to frequently queried fields
2. Use field selection to limit returned data
3. Reduce relationship depth
4. Implement caching for expensive operations

#### Memory Issues

**Problem**: High memory usage with large datasets.

**Solutions**:
1. Process documents in batches (100-500 at a time)
2. Use cursors for large queries
3. Implement pagination with limits
4. Clear unused data from request context

### Debugging Techniques

#### Enable Debug Logging

```typescript
export default buildConfig({
  secret: process.env.PAYLOAD_SECRET,
  // Enable detailed logging
  express: (app) => {
    app.use((req, res, next) => {
      console.log(`${req.method} ${req.path}`)
      next()
    })
    return app
  },
})
```

#### Inspect Request Context

```typescript
hooks: {
  beforeChange: [
    ({ req }) => {
      console.log('User:', req.user)
      console.log('Context:', req.context)
      console.log('Operation:', operation)
    },
  ],
}
```

#### Test Access Control

```typescript
// Test as different users
const adminResults = await payload.find({
  collection: 'posts',
  user: adminUser,
  overrideAccess: false,
})

const userResults = await payload.find({
  collection: 'posts',
  user: regularUser,
  overrideAccess: false,
})

const publicResults = await payload.find({
  collection: 'posts',
  overrideAccess: false, // No user
})

console.log('Admin sees:', adminResults.docs.length)
console.log('User sees:', userResults.docs.length)
console.log('Public sees:', publicResults.docs.length)
```

## Migration Best Practices

### Schema Changes

1. **Backup database** before making changes
2. **Generate types**: `npm run generate:types`
3. **Test in development** before production
4. **Use migrations** for database schema changes

### Data Migration Pattern

```typescript
// scripts/migrate-data.ts
import { getPayload } from 'payload'
import config from '@payload-config'

async function migrate() {
  const payload = await getPayload({ config })
  
  // Get all documents needing migration
  const { docs } = await payload.find({
    collection: 'posts',
    where: { migrated: { exists: false } },
  })
  
  // Process each document
  for (const doc of docs) {
    await payload.update({
      collection: 'posts',
      id: doc.id,
      data: {
        // Transform data
        newField: transform(doc.oldField),
        migrated: true,
      },
    })
  }
  
  console.log('Migration complete')
}

migrate()
```

## Resources

- **Official Docs**: https://payloadcms.com/docs
- **GitHub**: https://github.com/payloadcms/payload
- **Examples**: https://github.com/payloadcms/payload/tree/v3.82.1/examples
- **Templates**: https://github.com/payloadcms/payload/tree/v3.82.1/templates
- **Discord**: https://payloadcms.com/discord
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/payload-cms
