---
name: payloadcms-3-82-1
description: Complete toolkit for Payload CMS v3.82.1 headless CMS development including collections, fields, access control, authentication, custom components, and Local API operations. Use when building content management systems, creating admin interfaces, implementing role-based access control, developing custom React components, or integrating with Next.js applications using TypeScript-first patterns with proper security practices.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - cms
  - headless-cms
  - nextjs
  - typescript
  - react
  - content-management
  - admin-panel
  - access-control
category: development
required_environment_variables:
  - name: PAYLOAD_SECRET
    prompt: "Enter your Payload secret key"
    help: "Generate with: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\""
    required_for: "application security and session management"
  - name: DATABASE_URL
    prompt: "Enter your database connection string"
    help: "MongoDB: mongodb://localhost:27017/payload or PostgreSQL: postgresql://user:pass@host:5432/db"
    required_for: "database connectivity"
---

# Payload CMS 3.82.1

Payload CMS is a TypeScript-first headless CMS and application framework for building admin panels, REST/GraphQL APIs, and custom applications. It provides type-safe collections, flexible access control, built-in authentication, and seamless Next.js integration with React components.

## When to Use

- Building headless CMS with custom content types
- Creating admin interfaces with role-based access control
- Implementing authentication with JWT tokens
- Developing custom React components for the admin panel
- Integrating CMS with Next.js applications
- Managing media uploads and relationships
- Creating API-first content management solutions
- Building e-commerce platforms with Payload's ecommerce module

## Quick Start

### Installation

```bash
# Create new Payload project
npm create payload@3.82.1

# Or use npx
npx create-payload@3.82.1

# Install to existing project
bun add payload @payloadcms/db-mongodb @payloadcms/richtext-lexical
```

### Basic Configuration

See [Configuration Guide](references/04-configuration.md) for detailed setup.

```typescript title="src/payload.config.ts"
import { buildConfig } from 'payload'
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: 'users',
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET,
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URL,
  }),
})
```

### Project Structure

```
src/
├── app/
│   ├── (frontend)/          # Frontend routes
│   └── (payload)/           # Payload admin routes
├── collections/             # Collection configs
├── globals/                 # Global configs
├── components/              # Custom React components
├── hooks/                   # Hook functions
├── access/                  # Access control functions
└── payload.config.ts        # Main config
```

## Core Features

### Collections

Define content types with type-safe schemas:

```typescript title="src/collections/Posts.ts"
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

See [Collections Guide](references/05-collections.md) for advanced patterns.

### Authentication

Built-in auth with JWT tokens and role-based access control:

```typescript title="src/collections/Users.ts"
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
      saveToJWT: true, // Include in JWT for fast access checks
    },
  ],
}
```

See [Authentication Guide](references/03-authentication.md) for complete auth patterns.

### Access Control

Secure your data with granular permissions:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: ({ req: { user } }) => {
      // Public can read published posts
      if (!user) return { status: { not_in: ['draft'] } }
      
      // Editors can read all
      if (user.roles?.includes('editor')) return true
      
      // Authors can read their own posts
      return { author: { equals: user.id } }
    },
    update: ({ req: { user } }) => {
      return user?.roles?.includes('admin')
    },
  },
  fields: [/* ... */],
}
```

See [Access Control Guide](references/02-access-control.md) for security patterns.

## Local API Usage

### CRITICAL: Access Control in Local API

```typescript
// ❌ SECURITY BUG: Access control bypassed
await payload.find({
  collection: 'posts',
  user: someUser, // Ignored! Runs with ADMIN privileges
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
  // No user - overrideAccess defaults to true
})
```

**Rule**: When passing `user` to Local API, ALWAYS set `overrideAccess: false`

### Transaction Safety in Hooks

```typescript
// ❌ DATA CORRUPTION: Separate transaction
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        // Missing req - separate transaction!
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
        req, // Pass req for same transaction
      })
    },
  ],
}
```

See [Local API Guide](references/06-local-api.md) for complete patterns.

## Custom Components

Extend the admin panel with React components:

```typescript title="src/components/CustomCell.tsx"
import type { CellProps } from 'payload'

export const CustomCell: React.FC<CellProps> = ({ value }) => {
  return <div>{formatValue(value)}</div>
}
```

Then use in collection config:
```typescript
fields: [
  {
    name: 'price',
    type: 'number',
    admin: {
      components: {
        Cell: '/components/CustomCell',
      },
    },
  },
]
```

See [Custom Components Guide](references/07-custom-components.md) for examples.

## Type Generation

After schema changes, always regenerate types:

```bash
# Generate TypeScript types
bun run generate:types

# Or directly
payload generate:types
```

This creates `src/payload-types.ts` with full type safety.

## Reference Files

### Core Concepts
- [`references/01-agent-rules.md`](references/01-agent-rules.md) - Official Payload development rules and patterns
- [`references/02-access-control.md`](references/02-access-control.md) - Access control for collections, fields, and globals
- [`references/03-authentication.md`](references/03-authentication.md) - Authentication, JWT, API keys, and token management
- [`references/04-configuration.md`](references/04-configuration.md) - Complete configuration options and environment setup

### Advanced Topics
- [`references/05-collections.md`](references/05-collections.md) - Collection configs, hooks, and validation
- [`references/06-local-api.md`](references/06-local-api.md) - Local API patterns, transactions, and security
- [`references/07-custom-components.md`](references/07-custom-components.md) - Custom React components for admin panel
- [`references/08-fields-guide.md`](references/08-fields-guide.md) - All field types and configurations

### Integration & Deployment
- [`references/09-nextjs-integration.md`](references/09-nextjs-integration.md) - Next.js app router integration patterns
- [`references/10-database-adapters.md`](references/10-database-adapters.md) - MongoDB, PostgreSQL, and SQLite adapters
- [`references/11-hooks-and-validation.md`](references/11-hooks-and-validation.md) - Hook lifecycle and validation patterns
- [`references/12-troubleshooting.md`](references/12-troubleshooting.md) - Common issues and debugging techniques

## Common Patterns

### Auto-generate Slugs

```typescript
import { slugField } from 'payload'

fields: [
  { name: 'title', type: 'text' },
  slugField({ fieldToUse: 'title' }),
]
```

### Relationship with Filtering

```typescript
{
  name: 'category',
  type: 'relationship',
  relationTo: 'categories',
  filterOptions: { active: { equals: true } },
}
```

### Conditional Fields

```typescript
{
  name: 'featuredImage',
  type: 'upload',
  relationTo: 'media',
  admin: {
    condition: (data) => data.featured === true,
  },
}
```

### Virtual Fields

```typescript
{
  name: 'fullName',
  type: 'text',
  virtual: true,
  hooks: {
    afterRead: [({ siblingData }) => `${siblingData.firstName} ${siblingData.lastName}`],
  },
}
```

## Environment Variables

```bash title=".env"
# Required
PAYLOAD_SECRET=your-secret-key-here
DATABASE_URL=mongodb://localhost:27017/payload

# Optional
NODE_ENV=development
PAYLOAD_PUBLIC_APP_URL=http://localhost:3000
TELEMETRY_ENABLED=false
```

## Scripts

```json title="package.json"
{
  "scripts": {
    "build": "next build",
    "dev": "next dev",
    "generate:types": "payload generate:types",
    "lint": "next lint",
    "start": "next start",
    "typecheck": "tsc --noEmit"
  }
}
```

## Troubleshooting

### Type Errors

**Issue**: TypeScript errors after schema changes

**Solution**: Regenerate types:
```bash
bun run generate:types
bun run typecheck
```

### Access Control Not Working

**Issue**: Local API bypassing access control

**Solution**: Always set `overrideAccess: false` when passing user:
```typescript
await payload.find({
  collection: 'posts',
  user: req.user,
  overrideAccess: false, // Required!
})
```

### Import Map Issues

**Issue**: Custom components not loading

**Solution**: Regenerate import map:
```bash
bun run build
# Or manually
payload build
```

## Best Practices

1. **TypeScript-First**: Always use TypeScript with proper types from Payload
2. **Security-Critical**: Follow all security patterns, especially access control
3. **Type Generation**: Run `generate:types` after schema changes
4. **Transaction Safety**: Always pass `req` to nested operations in hooks
5. **Access Control**: Understand Local API bypasses access control by default
6. **Code Validation**: Run `tsc --noEmit` to validate TypeScript correctness

## Migration from v2

Key breaking changes:
- `buildConfig` replaces `configure`
- Database adapters are separate packages
- Lexical editor replaces Slate
- App Router required for Next.js 13+

See Payload's migration guide for detailed steps.

## Getting Help

- [Payload Documentation](https://payloadcms.com/docs)
- [Payload Discord](https://discord.com/invite/payload)
- [GitHub Issues](https://github.com/payloadcms/payload/issues)
- [Payload Templates](https://github.com/payloadcms/payload/tree/main/templates)

## Related Skills

Consider also using:
- `nextjs-14-2` - For Next.js integration patterns
- `typescript-5-6` - For TypeScript configuration
- `mongodb-8-0` - For MongoDB database operations
- `react-18-3` - For custom React components
