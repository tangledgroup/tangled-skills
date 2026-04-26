# Deployment and Production

## Build Process

To run Payload in production, build and start the application:

```bash
pnpm build    # Runs `next build`, creates .next directory with production bundle
pnpm start    # Runs `next start`, serves from .build directory
```

The build process compiles the Next.js application including the Payload admin panel and API routes into a single production-ready bundle.

## Vercel Deployment

### Vercel Postgres Adapter

For Vercel hosting, replace MongoDB with Vercel's Postgres:

```typescript
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'

export default buildConfig({
  db: vercelPostgresAdapter({
    pool: {
      connectionString: process.env.POSTGRES_URL || '',
    },
  }),
})
```

### Vercel Blob Storage

For media file storage on Vercel:

```typescript
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

export default buildConfig({
  plugins: [
    vercelBlobStorage({
      collections: {
        [Media.slug]: true,
      },
      token: process.env.BLOB_READ_WRITE_TOKEN || '',
    }),
  ],
})
```

### Environment Variables on Vercel

Configure these in the Vercel project settings:

- `PAYLOAD_SECRET` — Application secret
- `POSTGRES_URL` — Vercel Postgres connection string
- `BLOB_READ_WRITE_TOKEN` — Vercel Blob storage token
- `PREVIEW_SECRET` — Draft preview authentication
- `CRON_SECRET` — Scheduled jobs authorization
- `VERCEL_PROJECT_PRODUCTION_URL` — Auto-set by Vercel, used for URL generation

### Cron Configuration

For scheduled publishing on Vercel, configure cron in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/tasks/cron",
      "schedule": "0 * * * *"
    }
  ]
}
```

Note: Vercel Hobby plan limits cron to daily intervals. Pro and Team plans support hourly scheduling.

## Docker Deployment

### Multi-Stage Dockerfile

The template includes a production-ready multi-stage Dockerfile:

```dockerfile
FROM node:22.17.0-alpine AS base

# Dependencies stage
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

# Build stage
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm run build

# Production stage
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
RUN mkdir .next && chown nextjs:nodejs .next
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD HOSTNAME="0.0.0.0" node server.js
```

The Dockerfile uses Next.js standalone output mode, which produces a minimal production bundle in `.next/standalone` containing only the files needed to run the server. This significantly reduces image size.

### Docker Compose (Development)

For local development with Docker:

```yaml
version: '3'
services:
  payload:
    image: node:18-alpine
    ports:
      - '3000:3000'
    volumes:
      - .:/home/node/app
      - node_modules:/home/node/app/node_modules
    working_dir: /home/node/app/
    command: sh -c "yarn install && yarn dev"
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
volumes:
  data:
  node_modules:
```

## Self-Hosting

For VPS, DigitalOcean Apps Platform, Coolify, or similar:

1. Ensure the application builds: `pnpm build`
2. Start the server: `pnpm start`
3. Configure a reverse proxy (nginx, caddy) if needed
4. Set up SSL/TLS termination
5. Configure environment variables
6. Set up database (MongoDB or PostgreSQL)
7. Configure cron for scheduled publishing

## Database Migrations

### MongoDB

MongoDB adapter is schemaless — no migrations needed. Schema changes are applied immediately.

### PostgreSQL

PostgreSQL requires explicit migration management:

```bash
# Create a migration file locally
pnpm payload migrate:create

# Apply pending migrations on the server
pnpm payload migrate
```

Key rules:
- Set `push: true` for local development (auto-applies schema changes)
- Set `push: false` for production databases
- Always create and test migrations before deploying
- Migration files should be committed to version control

## Cache Management

### Payload Cloud (Default)

On Payload Cloud, all requests are proxied through Cloudflare. Next.js caching is disabled by default:
- Fetch requests include `no-store` directive
- Page files include `export const dynamic = 'force-dynamic'`
- On-demand revalidation uses `revalidatePath()` and `revalidateTag()` in hooks

### Self-Hosted Caching

To re-enable Next.js caching for self-hosted deployments:

1. Remove `no-store` from fetch requests in `src/app/_api`
2. Remove `export const dynamic = 'force-dynamic'` from page files
3. Configure appropriate `revalidate` values in `fetch` options or use `generateStaticParams` with ISR

### Sitemap Generation

The template uses `next-sitemap` configured in `next-sitemap.config.cjs`. The postbuild script generates sitemaps after each build:

```json
"postbuild": "next-sitemap --config next-sitemap.config.cjs"
```

Sitemaps are also dynamically generated via the `(sitemaps)` route group with tag-based cache invalidation through `revalidateTag('pages-sitemap')` and `revalidateTag('posts-sitemap')`.

## Production Checklist

- [ ] Set strong `PAYLOAD_SECRET` (use `openssl rand -base64 32`)
- [ ] Configure production database connection
- [ ] Set `PREVIEW_SECRET` for draft preview
- [ ] Set `CRON_SECRET` for scheduled jobs
- [ ] Run database migrations (`pnpm payload migrate`)
- [ ] Build and test production build locally (`pnpm build && pnpm start`)
- [ ] Configure reverse proxy and SSL
- [ ] Set up cron for scheduled publishing
- [ ] Verify media upload storage is configured
- [ ] Test draft preview and live preview
- [ ] Verify SEO metadata renders correctly
- [ ] Test search functionality
- [ ] Verify redirects work as expected
