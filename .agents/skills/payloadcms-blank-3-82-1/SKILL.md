---
name: payloadcms-blank-3-82-1
description: Minimal Payload CMS 3.82.1 starter template providing a clean foundation for building custom headless CMS applications with Next.js App Router, MongoDB, and Lexical editor. Use when starting new Payload projects from scratch, needing a minimal configuration without pre-built collections or content types, or requiring full control over data modeling and admin panel customization.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - cms
  - payload
  - nextjs
  - mongodb
  - headless-cms
  - react
  - typescript
category: development
required_environment_variables:
  - name: DATABASE_URL
    prompt: "What is your MongoDB connection string?"
    help: "MongoDB connection URI (e.g., mongodb://127.0.0.1/payload or Atlas connection string)"
    required_for: "database connectivity"
  - name: PAYLOAD_SECRET
    prompt: "What is your Payload secret key?"
    help: "A random secret string for signing cookies and tokens (use: openssl rand -base64 32)"
    required_for: "application security"
---

# Payload CMS Blank Template 3.82.1

The Payload Blank Template provides a minimal, production-ready foundation for building custom headless CMS applications using Payload 3.82.1 with Next.js App Router, MongoDB database adapter, and Lexical rich text editor. This template includes only essential configurations, allowing complete control over data modeling, authentication, and admin panel customization without pre-built content types or opinions about project structure.

## When to Use

- Starting a new Payload CMS project from scratch
- Needing minimal configuration without predefined collections
- Building custom headless CMS with specific data requirements
- Requiring full control over admin panel layout and components
- Creating API-first applications with custom routing
- Migrating from other CMS platforms with unique content models
- Developing microservices or modular monoliths with Payload as backend

## Core Concepts

**Payload Architecture:**
- **Collections**: Database models with automatic REST/GraphQL APIs and admin UI
- **Fields**: Declarative schema definitions for data structure and validation
- **Access Control**: Per-collection and per-field permission policies
- **Admin Panel**: Auto-generated React-based interface for content management
- **Lexical Editor**: Block-based rich text editor for WYSIWYG content editing

**Key Features:**
- TypeScript-first development with generated types
- Next.js App Router integration for server components and API routes
- MongoDB database adapter with Mongoose under the hood
- File uploads with image optimization via Sharp
- Authentication framework with customizable user models
- Custom React components for admin panel extension
- Local API for server-side data operations

## Quick Start

### Prerequisites

- Node.js 18.20.2+ or 20.9.0+
- pnpm 9.x or 10.x (preferred package manager)
- MongoDB 6.0+ (local or Atlas)

### Installation from Template

```bash
# Using Payload CLI (recommended)
pnpm create payload@latest my-project --template blank

# Or clone directly from GitHub
git clone https://github.com/payloadcms/payload.git
cd payload/templates/blank
# Copy to your project directory
cp -r . ~/my-payload-project
```

### Local Development Setup

```bash
# Navigate to project directory
cd my-project

# Copy environment variables template
cp .env.example .env

# Install dependencies
pnpm install

# Generate TypeScript types
pnpm run generate:types

# Start development server
pnpm dev
```

The admin panel will be available at `http://localhost:3000/admin`. Follow on-screen instructions to create your first admin user.

### Docker Development (Optional)

For consistent environments across teams:

```bash
# Update .env with local MongoDB connection
# DATABASE_URL=mongodb://127.0.0.1/my-database

# Start services
docker-compose up

# Or in background
docker-compose up -d
```

See [Project Structure](references/01-project-structure.md) for detailed directory layout and file purposes.

## Common Operations

### Creating Collections

Define new content types by creating collection configuration files:

```typescript
// src/collections/Posts.ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'content',
      type: 'richText',
    },
  ],
}
```

Then register in `payload.config.ts`:

```typescript
import { Posts } from './collections/Posts'

export default buildConfig({
  collections: [Users, Media, Posts],
  // ... other config
})
```

See [Collections and Fields](references/02-collections-and-fields.md) for comprehensive field types and collection options.

### Setting Up Authentication

Enable auth on any collection:

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  fields: [
    // Email and password fields added automatically
    {
      name: 'role',
      type: 'select',
      options: ['admin', 'editor', 'user'],
    },
  ],
}
```

See [Authentication Setup](references/03-authentication-setup.md) for advanced auth patterns and access control.

### Building Custom Routes

Create API endpoints in Next.js App Router:

```typescript
// src/app/my-route/route.ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
  })
  
  return Response.json({ posts })
}
```

See [API Integration](references/05-api-integration.md) for REST and GraphQL patterns.

## Reference Files

- [`references/01-project-structure.md`](references/01-project-structure.md) - Directory layout, file purposes, and configuration files
- [`references/02-collections-and-fields.md`](references/02-collections-and-fields.md) - Complete field types, collection options, and schema patterns
- [`references/03-authentication-setup.md`](references/03-authentication-setup.md) - Auth configuration, access control, and security best practices
- [`references/04-custom-components.md`](references/04-custom-components.md) - Admin panel customization with React components
- [`references/05-api-integration.md`](references/05-api-integration.md) - REST API, GraphQL, Local API, and custom routes
- [`references/06-deployment-and-config.md`](references/06-deployment-and-config.md) - Environment setup, deployment strategies, and production considerations

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/payloadcms-blank-3-82-1/`). All paths are relative to this directory.

## Troubleshooting

### Common Issues

**TypeScript errors after adding collections:**
Run `pnpm run generate:types` to regenerate type definitions from your Payload config.

**MongoDB connection failed:**
Verify `DATABASE_URL` in `.env` matches your MongoDB instance. For local MongoDB, use `mongodb://127.0.0.1/your-db-name`.

**Uploads not working:**
Ensure Sharp is installed (`pnpm install`) and check file permissions for upload directory.

**Admin panel not loading:**
Check browser console for errors. Clear `.next` cache with `pnpm devsafe` if needed.

See [Deployment and Config](references/06-deployment-and-config.md) for production troubleshooting and environment-specific issues.

## References

- **Official Documentation**: https://payloadcms.com/docs
- **GitHub Repository**: https://github.com/payloadcms/payload/tree/v3.82.1/templates/blank
- **Discord Community**: https://discord.com/invite/payload
- **Payload 3.x Migration Guide**: https://payloadcms.com/docs/getting-started/requirements
- **Lexical Editor Docs**: https://payloadcms.com/docs/richtext/lexical/overview
