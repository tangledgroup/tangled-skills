---
name: payloadcms-blank-3-82-1
description: Complete guide for Payload CMS blank template v3.82.1 providing minimal starter project structure with Next.js App Router, TypeScript, MongoDB adapter, and Lexical editor. Use when starting new Payload projects from scratch, setting up minimal CMS configurations, implementing basic user authentication and media uploads, or creating custom collections following official best practices and security patterns.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - payload-cms
  - nextjs
  - typescript
  - blank-template
  - cms-starter
  - mongodb
  - lexical-editor
category: development
required_environment_variables:
  - name: PAYLOAD_SECRET
    prompt: "Enter your Payload secret key"
    help: "Generate with: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\""
    required_for: "application security and session management"
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "Example: mongodb://localhost:27017/payload or use MongoDB Atlas"
    required_for: "database connectivity"
---

# Payload CMS Blank Template 3.82.1

The blank template provides a minimal, production-ready starter project for Payload CMS with Next.js App Router, TypeScript, MongoDB, and Lexical rich text editor. It includes essential collections (Users, Media) and follows official best practices for security, type safety, and project structure.

## When to Use

- Starting a new Payload CMS project from scratch
- Needing minimal configuration without pre-built features
- Building custom CMS with specific requirements
- Learning Payload fundamentals with clean baseline
- Implementing basic authentication and media uploads
- Following official Payload best practices and patterns

## Quick Start

### Installation

```bash
# Create new project from blank template
npm create payload@3.82.1 -- --template blank

# Or use npx with specific version
npx create-payload@3.82.1 --template blank

# Using bun
bunx create-payload@3.82.1 --template blank
```

### Project Structure

```
my-payload-app/
├── src/
│   ├── app/
│   │   ├── (payload)/
│   │   │   └── admin/
│   │   │       └── route.ts          # Admin panel route
│   │   ├── layout.tsx
│   │   └── page.tsx                  # Frontend homepage
│   ├── collections/
│   │   ├── Users.ts                  # User collection with auth
│   │   └── Media.ts                  # Media upload collection
│   ├── payload.config.ts             # Main Payload configuration
│   └── payload-types.ts              # Auto-generated types
├── .env                              # Environment variables
├── .env.example                      # Example environment file
├── next.config.js                    # Next.js configuration
├── package.json
└── tsconfig.json
```

### Environment Setup

Copy example env file and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash title=".env"
# Required - Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
PAYLOAD_SECRET=your-generated-secret-here

# MongoDB connection string
DATABASE_URL=mongodb://localhost:27017/payload

# Optional - Public URL for previews and emails
PAYLOAD_PUBLIC_APP_URL=http://localhost:3000

# Optional - Disable telemetry
TELEMETRY_ENABLED=false
```

### Run Development Server

```bash
# Install dependencies
bun install

# Start development server
bun run dev

# Access admin panel at http://localhost:3000/admin
```

## Core Configuration

### Payload Config (payload.config.ts)

```typescript title="src/payload.config.ts"
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
  admin: {
    user: Users.slug,  // Collection used for authentication
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Media],
  editor: lexicalEditor(),  // Rich text editor
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URL || '',
  }),
  sharp,  // Image processing library
  plugins: [],
})
```

### Key Configuration Options

**Admin Settings:**
- `user`: Specifies which collection handles authentication
- `importMap`: Base directory for custom component imports
- `locale`: Default locale (defaults to 'en')
- `date`: Date format configuration

**TypeScript Settings:**
- `outputFile`: Path for auto-generated types
- Always run `bun run generate:types` after schema changes

**Database Adapter:**
- Uses MongoDB by default (`@payloadcms/db-mongodb`)
- Can switch to PostgreSQL (`@payloadcms/db-postgres`)
- Connection URL from environment variable

## Default Collections

### Users Collection (Authentication)

```typescript title="src/collections/Users.ts"
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',  // Field used as document title in UI
  },
  auth: true,  // Enables authentication for this collection
  fields: [
    // Email and password fields added automatically by Payload
    // Add custom fields here as needed
  ],
}
```

**Auto-generated Fields:**
- `email` (text, required, unique)
- `password` (text, required, hidden)
- `resetPasswordToken` (text, hidden)
- `resetPasswordExpiration` (date, hidden)

**Authentication Features:**
- JWT token-based authentication
- Password reset via email
- Login/logout endpoints
- User session management

### Media Collection (Uploads)

```typescript title="src/collections/Media.ts"
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
      required: true,  // Alt text for accessibility
    },
  ],
  upload: true,  // Enables file upload functionality
}
```

**Auto-generated Fields:**
- `url` (text) - File URL
- `filename` (text) - Original filename
- `mimeType` (text) - MIME type
- `filesize` (number) - File size in bytes
- `width` (number) - Image width (if image)
- `height` (number) - Image height (if image)

**Upload Features:**
- Image resizing with Sharp
- Multiple file uploads
- File validation
- CDN integration support

## Adding Custom Collections

### Example: Posts Collection

```typescript title="src/collections/Posts.ts"
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
  },
  access: {
    read: () => true,  // Public can read all posts
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'slug',
      type: 'text',
      unique: true,
      index: true,
    },
    {
      name: 'content',
      type: 'richText',  // Uses Lexical editor
      required: true,
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
    },
    {
      name: 'coverImage',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
      ],
      defaultValue: 'draft',
      required: true,
    },
  ],
  versions: {
    drafts: true,  // Enable draft functionality
    maxPerDoc: 10,
  },
  timestamps: true,  // Add createdAt and updatedAt
}
```

Then add to config:

```typescript title="src/payload.config.ts"
import { Posts } from './collections/Posts'

export default buildConfig({
  collections: [Users, Media, Posts],  // Add Posts
  // ... rest of config
})
```

## Type Generation

**CRITICAL**: Always regenerate types after schema changes:

```bash
# Generate TypeScript types
bun run generate:types

# Or directly
payload generate:types
```

This creates/updates `src/payload-types.ts` with full type safety for:
- Collection types
- Field types
- Hook contexts
- API responses

### Using Generated Types

```typescript
import type { Post, User, Media } from './payload-types'

async function getPost(id: string): Promise<Post> {
  // Fully typed Post object
}

async function getUser(email: string): Promise<User> {
  // Fully typed User object with auth fields
}
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

## Development Workflow

### 1. Add New Collection

```bash
# Create collection file
touch src/collections/Products.ts

# Define collection schema
# (add fields, access control, etc.)

# Import in payload.config.ts
# Add to collections array
```

### 2. Update Schema

```bash
# Modify collection config
# Add/remove fields, change types

# Regenerate types
bun run generate:types

# Validate TypeScript
bun run typecheck
```

### 3. Test Changes

```bash
# Start dev server
bun run dev

# Access admin panel
# http://localhost:3000/admin

# Test CRUD operations
# Verify access control works
```

## Security Best Practices

### 1. Environment Variables

**Never commit `.env` file:**

```bash title=".gitignore"
.env
.env.local
.env.production
```

Use `.env.example` for documentation:

```bash title=".env.example"
PAYLOAD_SECRET=generate-your-own
DATABASE_URL=mongodb://localhost:27017/payload
```

### 2. Access Control

Always define access control for collections:

```typescript
access: {
  read: ({ req: { user } }) => {
    if (user) return true  // Authenticated users can read
    return { status: { equals: 'published' } }  // Public sees published only
  },
  create: ({ req: { user } }) => {
    return user?.roles?.includes('admin')
  },
  update: ({ req: { user } }) => {
    return user?.roles?.includes('admin')
  },
  delete: ({ req: { user } }) => {
    return user?.roles?.includes('admin')
  },
}
```

### 3. Local API Security

**CRITICAL**: When using Local API with user context:

```typescript
// ❌ WRONG - Access control bypassed
await payload.find({
  collection: 'posts',
  user: someUser,
})

// ✅ CORRECT - Enforces permissions
await payload.find({
  collection: 'posts',
  user: someUser,
  overrideAccess: false,  // REQUIRED!
})
```

See [Payload CMS Skill](../payloadcms-3-82-1/SKILL.md) for complete security patterns.

## Common Customizations

### Add Roles to Users

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
      required: true,
      saveToJWT: true,  // Include in JWT for fast access checks
    },
  ],
}
```

### Add Custom Fields to Media

```typescript title="src/collections/Media.ts"
export const Media: CollectionConfig = {
  slug: 'media',
  upload: true,
  fields: [
    { name: 'alt', type: 'text', required: true },
    {
      name: 'caption',
      type: 'text',
    },
    {
      name: 'credits',
      type: 'text',
    },
  ],
}
```

### Enable Localization

```typescript title="src/payload.config.ts"
export default buildConfig({
  localization: {
    locales: [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Spanish' },
    ],
    defaultLocale: 'en',
    fallback: true,
  },
  // ... rest of config
})
```

Then mark fields as localized:

```typescript
fields: [
  { name: 'title', type: 'text', localized: true },
  { name: 'content', type: 'richText', localized: true },
]
```

## Next.js Integration

### Admin Panel Route

```typescript title="src/app/(payload)/admin/route.ts"
// This file enables the Payload admin panel
// Payload automatically handles routing
```

### Frontend Routes

```typescript title="src/app/page.tsx"
export default function Home() {
  return (
    <main>
      <h1>Welcome to my Payload app</h1>
      <p>Admin: /admin</p>
    </main>
  )
}
```

### API Routes

```typescript title="src/app/api/posts/route.ts"
import { getPayload } from 'payload'
import { config as payloadConfig } from '@/payload.config'

export async function GET() {
  const payload = await getPayload({ config: payloadConfig })
  
  const posts = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
  })
  
  return Response.json(posts)
}
```

## Deployment

### Production Build

```bash
# Install dependencies
bun install --frozen

# Generate types
bun run generate:types

# Build Next.js app
bun run build

# Start production server
bun run start
```

### Environment Variables (Production)

```bash title=".env.production"
PAYLOAD_SECRET=your-production-secret
DATABASE_URL=mongodb+srv://atlas-connection-string
PAYLOAD_PUBLIC_APP_URL=https://your-domain.com
NODE_ENV=production
```

### Docker Deployment

```dockerfile title="Dockerfile"
FROM oven/bun:1.3.12

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen

COPY . .
RUN bun run generate:types
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
```

## Troubleshooting

### Types Not Generating

**Problem**: `payload-types.ts` not updating

**Solution**:
```bash
# Clean and regenerate
rm src/payload-types.ts
bun run generate:types

# Check payload.config.ts is exported correctly
```

### Database Connection Errors

**Problem**: Can't connect to MongoDB

**Solution**:
```bash
# Check DATABASE_URL format
# MongoDB Local: mongodb://localhost:27017/payload
# MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/db

# Verify MongoDB is running
mongosh --version
```

### Admin Panel Not Loading

**Problem**: `/admin` returns 404 or errors

**Solution**:
- Verify `admin.user` points to valid collection slug
- Check `PAYLOAD_SECRET` is set
- Ensure collections array includes user collection
- Run `bun run build` to regenerate import map

### Access Control Issues

**Problem**: Users can't access data they should

**Solution**:
- Check access control functions return boolean or query
- Verify user is authenticated (`req.user` exists)
- For Local API, ensure `overrideAccess: false` when passing user

## Package Dependencies

```json title="package.json"
{
  "dependencies": {
    "@payloadcms/db-mongodb": "^3.82.1",
    "@payloadcms/next": "^3.82.1",
    "@payloadcms/richtext-lexical": "^3.82.1",
    "next": "^14.2.0",
    "payload": "^3.82.1",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "sharp": "^0.33.5"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^18.3.0",
    "typescript": "^5.6.0"
  }
}
```

## Migration from Other Templates

### From E-commerce Template

Remove e-commerce specific packages:
```bash
bun remove @payloadcms/plugin-stripe @payloadcms/ecommerce
```

Keep only core dependencies and custom collections.

### From Website Template

Remove blog/portfolio collections you don't need, keeping minimal Users and Media.

## Next Steps

1. **Add Custom Collections**: Define your content types
2. **Implement Access Control**: Secure your data
3. **Build Frontend**: Create pages to display content
4. **Add Custom Components**: Extend admin panel UI
5. **Set Up Email**: Configure email provider for password resets
6. **Deploy**: Push to production hosting

## Resources

- [Payload Documentation](https://payloadcms.com/docs)
- [Payload Blank Template](https://github.com/payloadcms/payload/tree/v3.82.1/templates/blank)
- [Next.js Documentation](https://nextjs.org/docs)
- [MongoDB Documentation](https://www.mongodb.com/docs)

## Related Skills

- `payloadcms-3-82-1` - Complete Payload CMS development guide
- `nextjs-14-2` - Next.js App Router patterns
- `mongodb-8-0` - MongoDB database operations
- `typescript-5-6` - TypeScript configuration and types
