# Project Structure

This reference documents the complete directory layout and file purposes for the Payload Blank Template 3.82.1. Understanding this structure is essential for organizing collections, custom routes, and frontend components effectively.

## Directory Tree

```
my-project/
├── .env                    # Environment variables (created from .env.example)
├── .env.example            # Template environment variables
├── .gitignore              # Git ignore patterns
├── docker-compose.yml      # Docker services for local development
├── next.config.mjs         # Next.js configuration
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── eslint.config.js        # ESLint configuration
├── prettier.config.js      # Prettier formatting rules
├── src/
│   ├── app/
│   │   ├── (frontend)/     # Frontend application routes (grouped)
│   │   │   ├── page.tsx    # Homepage
│   │   │   └── styles.css  # Global frontend styles
│   │   └── (payload)/      # Payload admin and API routes (grouped)
│   │       ├── admin/
│   │   │   └── importMap.tsx  # Auto-generated component import map
│   │       ├── api/
│   │   │   ├── [...slug]/
│   │   │   │   └── route.ts   # REST API endpoint (auto-generated)
│   │   │   ├── graphql/
│   │   │   │   └── route.ts   # GraphQL API endpoint
│   │   │   └── graphql-playground/
│   │   │       └── route.ts   # GraphQL Playground UI
│   │       ├── custom.scss     # Admin panel custom styles
│   │       └── layout.tsx      # Admin panel root layout
│   ├── collections/        # Collection definitions
│   │   ├── Users.ts        # User collection with auth
│   │   └── Media.ts        # Media upload collection
│   ├── payload.config.ts   # Main Payload configuration
│   └── payload-types.ts    # Auto-generated TypeScript types
├── my-route/               # Example custom route directory
└── tests/                  # Test files (if configured)
```

## Key Files Explained

### Environment Configuration

**`.env`** (required at runtime)
```bash
# MongoDB connection string
DATABASE_URL=mongodb://127.0.0.1/payload

# Random secret for signing cookies and JWT tokens
PAYLOAD_SECRET=your-random-secret-here
```

Generate a secure secret:
```bash
openssl rand -base64 32
```

**`.env.example`** (template for sharing)
Contains placeholder values that should be copied to `.env` before running the application. Never commit actual `.env` files with real secrets.

### Configuration Files

**`src/payload.config.ts`** (main configuration)
```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { buildConfig } from 'payload'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

import { Users } from './collections/Users'
import { Media } from './collections/Media'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  // Admin panel configuration
  admin: {
    user: Users.slug,  // Collection used for authentication
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  
  // Registered collections
  collections: [Users, Media],
  
  // Rich text editor configuration
  editor: lexicalEditor(),
  
  // Security secret from environment
  secret: process.env.PAYLOAD_SECRET || '',
  
  // TypeScript type generation
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  
  // Database adapter configuration
  db: mongooseAdapter({
    url: process.env.DATABASE_URL || '',
  }),
  
  // Image processing library
  sharp,
  
  // Additional plugins
  plugins: [],
})
```

**`tsconfig.json`** (TypeScript configuration)
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"],
      "@payload-config": ["./src/payload.config.ts"]
    },
    "target": "ES2022"
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

Key path aliases:
- `@/*` → Resolves to `./src/*`
- `@payload-config` → Resolves to `./src/payload.config.ts`

**`package.json`** (scripts and dependencies)

Essential scripts:
```json
{
  "scripts": {
    "build": "next build",
    "dev": "next dev",
    "devsafe": "rm -rf .next && next dev",
    "generate:importmap": "payload generate:importmap",
    "generate:types": "payload generate:types",
    "lint": "eslint .",
    "payload": "payload",
    "start": "next start"
  }
}
```

Key dependencies:
- `payload` - Core Payload CMS framework
- `@payloadcms/next` - Next.js integration
- `@payloadcms/db-mongodb` - MongoDB database adapter
- `@payloadcms/richtext-lexical` - Lexical rich text editor
- `@payloadcms/ui` - Admin panel UI components
- `next` - Next.js 16.2.2
- `react` - React 19.2.4
- `sharp` - Image processing library

### Source Directory Structure

**`src/collections/`** (data models)

Each collection is a separate TypeScript file exporting a `CollectionConfig`:

```typescript
// src/collections/Users.ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',
  },
  auth: true,  // Enables authentication for this collection
  fields: [
    // Email and password added automatically when auth: true
  ],
}
```

```typescript
// src/collections/Media.ts
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,  // Public read access
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
    },
  ],
  upload: true,  // Enables file uploads
}
```

**Naming conventions:**
- File names use PascalCase: `Users.ts`, `Media.ts`, `Posts.ts`
- Exported constant matches file name: `export const Users`
- Slug is lowercase: `slug: 'users'`

**`src/app/`** (Next.js App Router)

Route groups using parentheses don't affect URL paths:

**(frontend) group** - Public-facing application:
```
src/app/(frontend)/
├── page.tsx      # Homepage at /
└── styles.css    # Global CSS
```

**(payload) group** - Admin panel and APIs:
```
src/app/(payload)/
├── admin/                    # Admin panel at /admin
│   └── importMap.tsx         # Auto-generated component imports
├── api/
│   ├── [...slug]/route.ts    # REST API at /api/*
│   ├── graphql/route.ts      # GraphQL at /api/graphql
│   └── graphql-playground/   # GraphQL UI at /graphql
├── custom.scss               # Admin panel customization
└── layout.tsx                # Root layout for admin/API routes
```

**`src/payload-types.ts`** (auto-generated types)

Generated by `pnpm run generate:types`. Contains TypeScript types for all collections, documents, and APIs. Never edit manually - always regenerate after schema changes.

### App Router Files

**`src/app/(payload)/layout.tsx`** (admin layout)
```typescript
import config from '@payload-config'
import '@payloadcms/next/css'
import type { ServerFunctionClient } from 'payload'
import { handleServerFunctions, RootLayout } from '@payloadcms/next/layouts'
import React from 'react'

import { importMap } from './admin/importMap.js'
import './custom.scss'

type Args = {
  children: React.ReactNode
}

const serverFunction: ServerFunctionClient = async function (args) {
  'use server'
  return handleServerFunctions({
    ...args,
    config,
    importMap,
  })
}

const Layout = ({ children }: Args) => (
  <RootLayout config={config} importMap={importMap} serverFunction={serverFunction}>
    {children}
  </RootLayout>
)

export default Layout
```

**`src/app/(payload)/api/[...slug]/route.ts`** (REST API)
```typescript
/* AUTO-GENERATED - DO NOT MODIFY */
import config from '@payload-config'
import '@payloadcms/next/css'
import {
  REST_DELETE,
  REST_GET,
  REST_OPTIONS,
  REST_PATCH,
  REST_POST,
  REST_PUT,
} from '@payloadcms/next/routes'

export const GET = REST_GET(config)
export const POST = REST_POST(config)
export const DELETE = REST_DELETE(config)
export const PATCH = REST_PATCH(config)
export const PUT = REST_PUT(config)
export const OPTIONS = REST_OPTIONS(config)
```

### Custom Routes

Create custom API routes outside the `(payload)` group:

**`src/app/my-route/route.ts`**
```typescript
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export const GET = async (request: Request) => {
  const payload = await getPayload({
    config: configPromise,
  })

  // Access collections via Local API
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
  })

  return Response.json({ posts })
}

export const POST = async (request: Request) => {
  const payload = await getPayload({ config: configPromise })
  const body = await request.json()
  
  const doc = await payload.create({
    collection: 'posts',
    data: body,
  })
  
  return Response.json(doc)
}
```

### Docker Configuration

**`docker-compose.yml`** (development services)
```yaml
version: '3'

services:
  payload:
    image: node:20-alpine
    ports:
      - '3000:3000'
    volumes:
      - .:/home/node/app
      - node_modules:/home/node/app/node_modules
    working_dir: /home/node/app/
    command: sh -c "corepack enable && corepack prepare pnpm@latest --activate && pnpm install && pnpm dev"
    depends_on:
      - mongo
    env_file:
      - .env

  mongo:
    image: mongo:latest
    ports:
      - '27017:27017'
    command:
      - --storageEngine=wiredTiger
    volumes:
      - data:/data/db
    logging:
      driver: none

volumes:
  data:
  node_modules:
```

## Best Practices

### File Organization

1. **Collections**: One file per collection in `src/collections/`
2. **Shared utilities**: Create `src/lib/` for helper functions
3. **Custom hooks**: Create `src/hooks/` for beforeChange, afterRead, etc.
4. **Custom components**: Create `src/components/` for React components
5. **Tests**: Create `tests/integration/` and `tests/e2e/` directories

### Naming Conventions

- Collections: PascalCase files (`Posts.ts`), lowercase slugs (`'posts'`)
- Routes: kebab-case directories (`my-custom-route/`)
- Environment variables: SCREAMING_SNAKE_CASE (`PAYLOAD_SECRET`)
- TypeScript types: PascalCase (`PostDoc`, `UserData`)

### Type Safety

Always regenerate types after schema changes:
```bash
pnpm run generate:types
```

Import generated types:
```typescript
import type { Post, User } from '@/payload-types'
```

## Common Modifications

### Adding a New Collection

1. Create `src/collections/Posts.ts`
2. Import and add to `collections` array in `payload.config.ts`
3. Run `pnpm run generate:types`
4. Restart development server

### Adding Custom API Routes

Create route files in `src/app/` following Next.js App Router conventions:
- `src/app/api/custom/route.ts` → `GET /api/custom`
- `src/app/api/items/[id]/route.ts` → `GET /api/items/:id`

### Customizing Admin Panel

1. Edit `src/app/(payload)/custom.scss` for styling
2. Create custom components in `src/components/`
3. Reference components in collection config via `admin.components`

See [Custom Components](04-custom-components.md) for detailed customization patterns.
