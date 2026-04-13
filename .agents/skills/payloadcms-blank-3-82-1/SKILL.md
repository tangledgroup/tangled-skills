---
name: payloadcms-blank-3-82-1
description: Complete guide for Payload CMS blank template v3.82.1 providing minimal starter project structure with Next.js App Router, TypeScript, MongoDB adapter, and Lexical editor. Use when starting new Payload projects from scratch, setting up minimal CMS configurations, implementing basic user authentication and media uploads, or creating custom collections following official best practices and security patterns.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - payloadcms
  - nextjs
  - typescript
  - cms
  - mongodb
  - headless-cms
  - blank-template
category: development
required_environment_variables:
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "For local development: mongodb://127.0.0.1/your-database-name. For production, use MongoDB Atlas or your hosted MongoDB instance."
    required_for: database connectivity
  - name: PAYLOAD_SECRET
    prompt: "Enter a secret key for Payload (minimum 32 characters)"
    help: "Generate using: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"". Required for session encryption and JWT signing.
    required_for: application security
---

# Payload CMS Blank Template v3.82.1

A minimal, production-ready starter template for building headless CMS applications with Payload CMS v3.82.1, Next.js 16.2.2, TypeScript, MongoDB, and the Lexical rich text editor. This template provides the bare minimum configuration needed to get started while following all official best practices and security patterns.

## When to Use

- Starting a new Payload CMS project from scratch with minimal boilerplate
- Building custom CMS solutions without pre-built content types
- Learning Payload fundamentals without template-specific complexity
- Setting up basic user authentication and media upload functionality
- Creating a foundation for custom collections and globals
- Implementing Next.js App Router with Payload's admin panel
- Following official Payload security patterns from the start

## What This Template Includes

### Pre-configured Components

- **Users Collection**: Authentication-enabled collection for admin users with email/password
- **Media Collection**: Upload-enabled collection for images/files with public read access
- **Lexical Editor**: Rich text editor configured for all richText fields
- **Next.js App Router**: Modern routing with `(payload)` and `(frontend)` route groups
- **TypeScript Configuration**: Path aliases, type generation, strict mode enabled
- **Docker Support**: docker-compose.yml with MongoDB for local development
- **Testing Setup**: Vitest for integration tests, Playwright for E2E tests

### Technology Stack

- **Runtime**: Node.js 18.20.2+ or 20.9.0+
- **Framework**: Next.js 16.2.2 (App Router)
- **Database**: MongoDB via `@payloadcms/db-mongodb`
- **Editor**: Lexical via `@payloadcms/richtext-lexical`
- **Package Manager**: pnpm 9+ or 10+
- **Image Optimization**: Sharp 0.34.2

## Quick Start

### Prerequisites

- Node.js 18.20.2+ or 20.9.0+ installed
- MongoDB running locally or MongoDB Atlas account
- pnpm package manager (recommended) or npm/yarn

### Local Development Setup

1. **Clone and install dependencies:**
   ```bash
   cd your-project
   pnpm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```env
   DATABASE_URL=mongodb://127.0.0.1/your-database-name
   PAYLOAD_SECRET=your-secret-key-minimum-32-chars
   ```

3. **Start MongoDB (if not running):**
   ```bash
   # Docker (recommended)
   docker run -d -p 27017:27017 --name mongo mongo:latest
   
   # Or use your local MongoDB installation
   mongod
   ```

4. **Start development server:**
   ```bash
   pnpm dev
   ```

5. **Open browser:**
   - Frontend: http://localhost:3000
   - Admin Panel: http://localhost:3000/admin

6. **Create first admin user:**
   - Navigate to /admin/login
   - Click "Create Account"
   - Enter email and password
   - You're ready to build!

See [Setup and Configuration](references/01-setup-configuration.md) for detailed setup instructions, environment variables, and alternative configurations.

### Docker Development (Alternative)

For a standardized development environment without local MongoDB installation:

```bash
# Start with Docker Compose
docker-compose up

# Or in background
docker-compose up -d
```

This starts both the Payload app and MongoDB container automatically. Update `DATABASE_URL` to `mongodb://mongo/your-database-name` in `.env`.

See [Docker Configuration](references/01-setup-configuration.md#docker-development) for complete Docker setup details.

## Project Structure

```
src/
├── app/                          # Next.js App Router
│   ├── (payload)/                # Payload admin panel routes
│   │   ├── admin/
│   │   │   └── [[...segments]]/  # Admin panel catch-all route
│   │   │       ├── page.tsx      # Root admin page (auto-generated)
│   │   │       └── not-found.tsx # 404 handler
│   │   ├── api/
│   │   │   ├── [...slug]/route.ts    # REST API endpoint
│   │   │   └── graphql/route.ts      # GraphQL endpoint
│   │   └── layout.tsx          # Admin layout
│   └── (frontend)/              # Public frontend routes
│       ├── page.tsx            # Home page
│       ├── layout.tsx          # Frontend layout
│       └── styles.css          # Global styles
├── collections/                  # Collection configurations
│   ├── Users.ts                # Auth-enabled user collection
│   └── Media.ts                # Upload-enabled media collection
├── payload.config.ts            # Main Payload configuration
└── payload-types.ts             # Auto-generated TypeScript types

tests/
├── e2e/                         # Playwright E2E tests
│   ├── admin.e2e.spec.ts       # Admin panel tests
│   └── frontend.e2e.spec.ts    # Frontend tests
└── helpers/                     # Test utilities
    ├── login.ts                # Login helper
    └── seedUser.ts             # Test user seeding

tests/int/                       # Vitest integration tests
└── api.int.spec.ts             # API integration tests

root/
├── package.json                 # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── next.config.ts              # Next.js configuration with Payload
├── docker-compose.yml          # Docker development setup
├── Dockerfile                  # Production Docker image
├── .env.example                # Environment variable template
└── README.md                   # Project documentation
```

See [Project Structure](references/02-project-structure.md) for detailed explanation of each directory and file purpose.

## Common Operations

### Generate TypeScript Types

After modifying collections, globals, or configuration:

```bash
pnpm generate:types
```

This creates `src/payload-types.ts` with types for all collections, globals, and fields. **Always run this after schema changes** to maintain type safety.

See [Type Generation](references/02-project-structure.md#type-generation) for details on generated types and how to use them.

### Create Custom Collections

1. Create file in `src/collections/`:
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

2. Import in `payload.config.ts`:
   ```typescript
   import { Posts } from './collections/Posts'

   export default buildConfig({
     collections: [Users, Media, Posts],
     // ...
   })
   ```

3. Generate types:
   ```bash
   pnpm generate:types
   ```

See [Collection Configuration](references/03-collection-configuration.md) for complete collection patterns, field types, and best practices.

### Implement Access Control

**CRITICAL SECURITY PATTERN**: When using Local API with user context:

```typescript
// ❌ WRONG: Access control bypassed (runs as admin)
await payload.find({
  collection: 'posts',
  user: someUser, // Ignored!
})

// ✅ CORRECT: Enforces user permissions
await payload.find({
  collection: 'posts',
  user: someUser,
  overrideAccess: false, // REQUIRED
})
```

See [Security Patterns](references/04-security-patterns.md) for critical security patterns and access control implementation.

### Build Custom API Routes

Create Next.js route handlers in `src/app/`:

```typescript
// src/app/api/custom/route.ts
import { getPayload } from 'payload'
import config from '@payload-config'

export const GET = async () => {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    overrideAccess: false, // Enforce access control
  })
  
  return Response.json(posts)
}
```

See [Custom Routes and Endpoints](references/05-custom-routes-endpoints.md) for API route patterns and Local API usage.

### Query Data in Server Components

```typescript
// src/app/(frontend)/posts/page.tsx
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function PostsPage() {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    where: {
      _status: { equals: 'published' },
    },
    depth: 2, // Populate relationships
  })
  
  return (
    <div>
      {posts.docs.map(post => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  )
}
```

See [Local API Usage](references/06-local-api-usage.md) for comprehensive query patterns and operators.

## Testing

### Run Integration Tests

```bash
pnpm test:int
```

Uses Vitest with jsdom environment to test API functionality.

### Run E2E Tests

```bash
pnpm test:e2e
```

Uses Playwright to test admin panel and frontend in real browser.

See [Testing Setup](references/07-testing.md) for test patterns, helpers, and best practices.

## Production Deployment

### Build for Production

```bash
# Generate types first
pnpm generate:types

# Build Next.js application
pnpm build

# Start production server
pnpm start
```

### Docker Production Build

See [Docker Configuration](references/01-setup-configuration.md#docker-production) for multi-stage Docker builds and deployment strategies.

## Troubleshooting

### Common Issues

**"Cannot find module '@payload-config'"**: Run `pnpm generate:types` to regenerate type definitions.

**MongoDB connection errors**: Verify `DATABASE_URL` is correct and MongoDB is running. For Docker, use `mongodb://mongo/your-db`.

**TypeScript errors in payload-types.ts**: Delete `.next` folder and run `pnpm generate:types` again.

**Import map errors**: Run `pnpm generate:importmap` to regenerate component import map.

See [Troubleshooting Guide](references/08-troubleshooting.md) for comprehensive error solutions and debugging tips.

## Reference Files

This skill includes detailed reference documentation organized by topic:

### Core Setup and Configuration

- [`references/01-setup-configuration.md`](references/01-setup-configuration.md) - Environment variables, Docker setup, Next.js config, TypeScript configuration
- [`references/02-project-structure.md`](references/02-project-structure.md) - Directory organization, file purposes, type generation, path aliases

### Collections and Data Modeling

- [`references/03-collection-configuration.md`](references/03-collection-configuration.md) - Users collection (auth), Media collection (uploads), custom collections, field types
- [`references/04-security-patterns.md`](references/04-security-patterns.md) - **CRITICAL**: Local API access control, transaction safety, hook patterns, RBAC implementation

### API and Routes

- [`references/05-custom-routes-endpoints.md`](references/05-custom-routes-endpoints.md) - Next.js route handlers, custom endpoints, REST/GraphQL APIs
- [`references/06-local-api-usage.md`](references/06-local-api-usage.md) - Query patterns, operators, CRUD operations, relationship population

### Testing and Quality

- [`references/07-testing.md`](references/07-testing.md) - Vitest integration tests, Playwright E2E tests, test helpers, seeding data

### Operations and Deployment

- [`references/08-troubleshooting.md`](references/08-troubleshooting.md) - Common errors, debugging techniques, performance issues
- [`references/09-production-deployment.md`](references/09-production-deployment.md) - Build process, Docker deployment, environment configuration, monitoring

## Important Notes

1. **Type Generation**: Always run `pnpm generate:types` after modifying collections or globals
2. **Security First**: Read [Security Patterns](references/04-security-patterns.md) before implementing access control
3. **Environment Variables**: Never commit `.env` files; use `.env.example` as template
4. **Database Backups**: Regular backups for production MongoDB instances
5. **Secret Management**: Use secure secret generation and rotate periodically
6. **Docker Development**: Preferred for consistent environments across teams
7. **Testing**: Run tests before deploying to catch breaking changes

## Resources

- **Payload Docs**: https://payloadcms.com/docs
- **Blank Template GitHub**: https://github.com/payloadcms/payload/tree/v3.82.1/templates/blank
- **Next.js Docs**: https://nextjs.org/docs
- **MongoDB Docs**: https://www.mongodb.com/docs
- **Lexical Editor**: https://lexical.dev

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/payloadcms-blank-3-82-1/`). All paths in this skill are relative to this directory.
