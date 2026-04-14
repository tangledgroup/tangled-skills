# Overview and Setup

This reference covers installation, environment configuration, database setup, and development workflows for the Payload CMS Website Template.

## Installation Methods

### Method 1: create-payload-app (Recommended)

```bash
pnpx create-payload-app my-project -t website
```

This command:
- Clones the website template to `my-project` directory
- Sets up pnpm workspace configuration
- Includes all dependencies and dev tools
- Copies `.env.example` for environment setup

### Method 2: Manual Clone

```bash
# Clone the Payload monorepo
git clone https://github.com/payloadcms/payload.git
cd payload/templates/website

# Or clone specific template (if available as separate repo)
git clone https://github.com/payloadcms/payload-website-template.git
```

### Method 3: Degit

```bash
npx degit payloadcms/payload/templates/website my-project
cd my-project
```

## Environment Configuration

### Required Environment Variables

Create `.env` from the example template:

```bash
cp .env.example .env
```

**Required variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `PAYLOAD_SECRET` | Encryption key for sessions and cookies | Generate with `openssl rand -base64 32` |
| `DATABASE_URL` | MongoDB connection string | `mongodb://localhost:27017/payload` |
| `PAYLOAD_PUBLIC_SERVER_URL` | Public URL for preview and redirects | `http://localhost:3000` |

**Optional variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_PAYLOAD_ADMIN_BAR_ID` | Admin bar integration ID | From Payload Cloud dashboard |
| `CRON_SECRET` | Secret for scheduled job authorization | Any random string |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob storage token | From Vercel dashboard |
| `POSTGRES_URL` | PostgreSQL connection (alternative to MongoDB) | `postgresql://user:pass@host:5432/db` |

### Complete .env Example

```env
# Required
PAYLOAD_SECRET=your-generated-secret-here
DATABASE_URL=mongodb://localhost:27017/payload
PAYLOAD_PUBLIC_SERVER_URL=http://localhost:3000

# Optional - Scheduled Publishing
CRON_SECRET=your-cron-secret-here

# Optional - Vercel Deployment
POSTGRES_URL=postgresql://user:pass@host:5432/db
BLOB_READ_WRITE_TOKEN=vercel-blob-token

# Optional - Admin Bar (Payload Cloud)
NEXT_PUBLIC_PAYLOAD_ADMIN_BAR_ID=admin-bar-id-from-dashboard
```

## Database Setup

### MongoDB (Default)

**Local Development:**

```bash
# Install MongoDB locally or use Docker
docker run -d --name mongodb -p 27017:27017 mongo

# Connection string in .env
DATABASE_URL=mongodb://localhost:27017/payload
```

**MongoDB Atlas (Cloud):**

```bash
# Create cluster at https://atlas.mongodb.com
# Get connection string and update .env
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/payload?retryWrites=true&w=majority
```

### PostgreSQL (Alternative)

**Install Postgres Adapter:**

```bash
pnpm add @payloadcms/db-postgres
```

**Update payload.config.ts:**

```ts
import { postgresAdapter } from '@payloadcms/db-postgres'

export default buildConfig({
  db: postgresAdapter({
    pool: {
      connectionString: process.env.POSTGRES_URL || '',
    },
  }),
  // ... rest of config
})
```

**Local Development with Docker:**

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=payload \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=payload \
  -p 5432:5432 postgres

DATABASE_URL=postgresql://payload:password@localhost:5432/payload
```

### Migrations (PostgreSQL Only)

MongoDB uses auto-schema with `push: true` in development. PostgreSQL requires explicit migrations:

**Create Migration:**

```bash
pnpm payload migrate:create
```

**Run Migrations:**

```bash
pnpm payload migrate
```

**Production Deployment:**

```bash
# After build, before start
pnpm build
pnpm payload migrate
pnpm start
```

## Development Workflow

### Start Development Server

```bash
# Install dependencies
pnpm install

# Start dev server with hot reload
pnpm dev
```

Server starts on `http://localhost:3000`:
- Admin panel: `/admin`
- Frontend: `/`
- GraphQL playground: `/api/graphql`
- REST API: `/api/:collection`

### First-Time Setup

1. Open `http://localhost:3000/admin`
2. Click "Create First User"
3. Enter email and password
4. Login with created credentials

### Seed Demo Content

**From Admin Panel:**
1. Login to admin panel
2. Look for "Seed Database" link (typically in footer or dashboard)
3. Click to populate demo pages, posts, categories
4. Creates demo author: `demo-author@payloadcms.com` / `password`

**Via Command Line:**

```bash
pnpm payload migrate # If migrations needed
# Then manually trigger seed endpoint if exposed
```

> **Warning**: Seeding drops all existing data. Only use on fresh databases or development environments.

### Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| Develop | `pnpm dev` | Start dev server with hot reload |
| Build | `pnpm build` | Build production bundle |
| Start | `pnpm start` | Start production server |
| Dev (Prod) | `pnpm dev:prod` | Build and start for testing production |
| Generate Types | `pnpm generate:types` | Generate TypeScript types from config |
| Generate Import Map | `pnpm generate:importmap` | Generate admin import map |
| Lint | `pnpm lint` | Run ESLint |
| Lint Fix | `pnpm lint:fix` | Auto-fix linting issues |
| Test | `pnpm test` | Run all tests (integration + e2e) |
| Test Integration | `pnpm test:int` | Run Vitest integration tests |
| Test E2E | `pnpm test:e2e` | Run Playwright e2e tests |

## Docker Development

### Using Docker Compose

**docker-compose.yml included in template:**

```yaml
version: '3'
services:
  mongo:
    image: mongo:latest
    ports:
      - 27017:27017
    volumes:
      - mongo-data:/data/db

  app:
    build: .
    ports:
      - 3000:3000
    environment:
      - DATABASE_URL=mongodb://mongo:27017/payload
      - PAYLOAD_SECRET=${PAYLOAD_SECRET}
    depends_on:
      - mongo

volumes:
  mongo-data:
```

**Start Services:**

```bash
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Custom Docker Image

**Dockerfile example:**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "start"]
```

## Production Build

### Build Process

```bash
# 1. Install dependencies
pnpm install

# 2. Build Next.js and Payload
pnpm build

# 3. Run migrations (PostgreSQL only)
pnpm payload migrate

# 4. Start production server
pnpm start
```

### Build Artifacts

- `.next/` - Compiled Next.js application
- `build/` - Payload admin bundle
- `payload-types.ts` - Generated TypeScript types

### Environment for Production

**Required production variables:**

```env
PAYLOAD_SECRET=strong-random-secret-min-32-chars
DATABASE_URL=production-database-connection-string
PAYLOAD_PUBLIC_SERVER_URL=https://your-production-domain.com
NODE_ENV=production
```

**Recommended security measures:**
- Use strong, unique `PAYLOAD_SECRET` (minimum 32 characters)
- Enable database connection pooling
- Use environment-specific database URLs
- Restrict admin panel access with authentication
- Enable HTTPS in production

## Caching Configuration

### Default: No Caching (Payload Cloud)

When deployed on Payload Cloud, caching is handled by Cloudflare proxy. Next.js caching is disabled:

```ts
// In src/app/_api/* fetch requests
const res = await fetch(url, { cache: 'no-store' })

// In page components
export const dynamic = 'force-dynamic'
```

### Self-Hosted: Enable Next.js Caching

Remove `no-store` directives and `force-dynamic` exports:

```ts
// Enable caching in fetch requests
const res = await fetch(url) // Default caching applied

// In page components - remove dynamic export
// Or explicitly set revalidation
export const dynamic = 'force-static'
export const revalidate = 3600 // Revalidate every hour
```

### On-Demand Revalidation

Pages automatically revalidate when content publishes:

```ts
// In collection hooks (already configured)
afterChange: [
  async ({ doc, req }: { doc: any; req: any }) => {
    if (doc._status === 'published') {
      await revalidatePath(`/${doc.slug}`, 'page')
    }
  }
]
```

## TypeScript Configuration

### Generated Types

Payload generates types from the config:

```bash
pnpm generate:types
```

**Generated file:** `src/payload-types.ts`

Includes:
- Collection doc types (`Page`, `Post`, `Media`, etc.)
- Global types (`Header`, `Footer`)
- Block types from layout builders
- Relationship and upload field types

### Using Generated Types

```ts
import type { Page, Post } from '@/payload-types'

// Type-safe page component
async function HomePage({ page }: { page: Page }) {
  return <div>{page.title}</div>
}

// Type-safe query result
const result = await payload.find({
  collection: 'pages',
  where: { slug: { equals: 'home' } },
})

// result.docs is typed as Page[]
```

### Custom TypeScript Config

**tsconfig.json includes:**
- Path aliases (`@/` → `src/`)
- React 19 JSX support
- ES modules (`"module": "esnext"`)
- Strict mode enabled

## Debugging and Development Tools

### Browser DevTools

- **React DevTools**: Inspect component tree and props
- **Payload Admin Panel**: Built-in debugging for queries
- **Network Tab**: Monitor API requests and responses

### Console Logging

```ts
// Payload hooks
beforeChange: [
  async ({ doc, req }) => {
    console.log('Document before change:', doc)
    return doc
  }
]

// Next.js pages
console.log('Page props:', props)
```

### Performance Profiling

```bash
# Profile Next.js build
pnpm build --profile

# Analyze bundle size
pnpx @next/bundle-analyzer
```

### Common Development Issues

**Issue: Module not found errors**

```bash
# Regenerate import map
pnpm generate:importmap

# Restart dev server
```

**Issue: Type errors after config changes**

```bash
# Regenerate types
pnpm generate:types

# Restart TypeScript server in editor
```

**Issue: Database connection errors**

- Verify MongoDB/Postgres is running
- Check connection string in `.env`
- Ensure firewall allows database port
- Check database user permissions

## Next Steps

After setup, explore:
- [Collections and Fields](02-collections-and-fields.md) - Understanding data models
- [Pages and Posts](03-pages-and-posts.md) - Creating content
- [Next.js Integration](04-nextjs-integration.md) - Frontend development
- [Customizations](08-customizations.md) - Extending functionality
