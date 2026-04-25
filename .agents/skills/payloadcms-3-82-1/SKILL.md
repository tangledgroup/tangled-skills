---
name: payloadcms-3-82-1
description: Complete toolkit for Payload CMS v3.82.1 headless CMS development including collections, fields, access control, authentication, custom components, and Local API operations. Use when building content management systems, creating admin interfaces, implementing role-based access control, developing custom React components, or integrating with Next.js applications using TypeScript-first patterns with proper security practices.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - cms
  - headless-cms
  - content-management
  - nextjs
  - typescript
  - react
  - database
  - admin-panel
category: development
required_environment_variables:
  - name: PAYLOAD_SECRET
    prompt: "Enter your Payload secret key"
    help: "Generate a random string (e.g., openssl rand -base64 32)"
    required_for: "full functionality"
  - name: DATABASE_URL
    prompt: "Enter your database connection string"
    help: "MongoDB: mongodb://localhost:27017/payload, PostgreSQL: postgresql://user:pass@host/db"
    required_for: "full functionality"
---

# Payload CMS v3.82.1

Complete toolkit for Payload CMS v3.82.1 headless CMS development including collections, fields, access control, authentication, custom components, and Local API operations. Use when building content management systems, creating admin interfaces, implementing role-based access control, developing custom React components, or integrating with Next.js applications using TypeScript-first patterns with proper security practices.


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

Payload CMS is a TypeScript-first headless CMS providing:
- **Admin Panel**: Auto-generated React admin interface
- **APIs**: REST and GraphQL out of the box
- **Database Adapters**: MongoDB, PostgreSQL, SQLite support
- **Authentication**: Built-in auth with JWT tokens
- **Customization**: Extensible via plugins and custom components
- **Type Safety**: Full TypeScript support with generated types

## When to Use

- Building content management systems with custom data models
- Creating admin interfaces for content editors
- Implementing role-based access control (RBAC)
- Developing headless CMS for Next.js applications
- Needing type-safe database operations in TypeScript
- Building multi-tenant or multi-language applications
- Requiring custom React components in admin panel
- Integrating with external services via hooks

## Setup

### Prerequisites

- Node.js 18.17 or higher
- TypeScript knowledge
- React fundamentals
- Database (MongoDB, PostgreSQL, or SQLite)

### Installation

```bash
# Create new Payload project
npx create-payload-app@latest my-payload-app

# Or add to existing Next.js project
npm install payload @payloadcms/db-mongodb @payloadcms/richtext-lexical
```

### Minimal Configuration

See [Configuration Options](references/06-configuration-options.md) for complete setup patterns.

## Quick Start

### Creating Collections

Define data models with collections:

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'content', type: 'richText' },
    { name: 'author', type: 'relationship', relationTo: 'users' },
  ],
  timestamps: true,
}
```

See [Collections & Fields](references/01-collections-fields.md) for detailed patterns.

### Implementing Access Control

Secure your data with role-based permissions:

```typescript
import type { Access } from 'payload'

// Row-level security: users see only their own posts
const ownPostsOnly: Access = ({ req: { user } }) => {
  if (!user) return false
  if (user?.roles?.includes('admin')) return true
  
  return { author: { equals: user.id } }
}

export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: ownPostsOnly,
    update: ownPostsOnly,
    delete: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
  fields: [/* ... */],
}
```

See [Access Control & Authentication](references/02-access-control-auth.md) for security patterns.

### Custom Components

Extend the admin panel with React components:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    components: {
      edit: {
        PreviewButton: '/components/PostPreview',
      },
      list: {
        Header: '/components/ListHeader',
      },
    },
  },
}
```

See [Custom Components](references/03-custom-components.md) for component patterns.

### Local API Operations

Perform database operations programmatically:

```typescript
import { getPayload } from 'payload'
import config from '@payload-config'

const payload = await getPayload({ config })

// Find documents
const posts = await payload.find({
  collection: 'posts',
  where: { status: { equals: 'published' } },
  depth: 2, // Populate relationships
})

// Create document
const newPost = await payload.create({
  collection: 'posts',
  data: { title: 'New Post', status: 'draft' },
})

// ⚠️ CRITICAL: Always set overrideAccess: false when passing user
await payload.find({
  collection: 'posts',
  user, // User context
  overrideAccess: false, // REQUIRED for security
})
```

See [Local API Operations](references/04-local-api-operations.md) for operation patterns.

## Reference Files

- [`references/01-collections-fields.md`](references/01-collections-fields.md) - Data modeling with collections and all field types
- [`references/02-access-control-auth.md`](references/02-access-control-auth.md) - Security patterns, RBAC, authentication
- [`references/03-custom-components.md`](references/03-custom-components.md) - React component customization for admin panel
- [`references/04-local-api-operations.md`](references/04-local-api-operations.md) - Programmatic database operations with security
- [`references/05-hooks-extensions.md`](references/05-hooks-extensions.md) - Lifecycle hooks and plugin development
- [`references/06-configuration-options.md`](references/06-configuration-options.md) - Complete Payload configuration reference
- [`references/07-common-patterns.md`](references/07-common-patterns.md) - Best practices and common gotchas

## Troubleshooting

### Common Issues

**Types not updating after schema changes:**
```bash
npm run generate:types
```

**Access control bypassed in Local API:**
Always set `overrideAccess: false` when passing `user` parameter.

**Infinite hook loops:**
Use context flags to prevent recursive operations in hooks.

**Transaction failures in MongoDB:**
Ensure replica set is configured for multi-operation transactions.

See [Common Patterns](references/07-common-patterns.md) for detailed troubleshooting.

## Resources

- **Official Docs**: https://payloadcms.com/docs
- **GitHub Repository**: https://github.com/payloadcms/payload
- **Examples**: https://github.com/payloadcms/payload/tree/v3.82.1/examples
- **Templates**: https://github.com/payloadcms/payload/tree/v3.82.1/templates
- **Plugins**: https://payloadcms.com/docs/plugins/overview

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
