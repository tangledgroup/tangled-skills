# Deployment and Production

## Build Process

```bash
# Install dependencies
pnpm install

# Build for production
pnpm build

# Start production server
pnpm start
```

The build process creates a `.next` directory with the production-ready Next.js bundle and a `.build` directory for Payload.

## Running in Production

Production requires these steps:

1. Set all environment variables (especially `PAYLOAD_SECRET`, database URL, Stripe keys)
2. Run `pnpm build` to generate production bundles
3. Run `pnpm start` to serve the application
4. Ensure Node.js version matches engine requirements (`^18.20.2 || >=20.9.0`)

## Database Options

### MongoDB (Default)

The template defaults to MongoDB via `@payloadcms/db-mongodb`:

```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'

db: mongooseAdapter({
  url: process.env.DATABASE_URL || '',
})
```

MongoDB supports transactions natively with replica sets, which the ecommerce plugin uses for atomic cart and order operations.

### PostgreSQL

Switch to PostgreSQL by installing the Postgres adapter:

```bash
pnpm add @payloadcms/db-postgres
```

```typescript
import { postgresAdapter } from '@payloadcms/db-postgres'

db: postgresAdapter({
  pool: { connectionString: process.env.POSTGRES_URL },
})
```

#### Migrations

PostgreSQL requires migrations for schema changes:

```bash
# Create a migration file locally
pnpm payload migrate:create

# Run pending migrations on the server
pnpm payload migrate
```

During local development, `push: true` auto-applies schema changes. Disable this (`push: false`) when pointing to production databases.

### Vercel Postgres

For Vercel deployment, use the Vercel Postgres adapter:

```bash
pnpm add @payloadcms/db-vercel-postgres
```

```typescript
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'

db: vercelPostgresAdapter({
  pool: { connectionString: process.env.POSTGRES_URL || '' },
})
```

## Storage Adapters

### Vercel Blob Storage

For media file storage on Vercel:

```bash
pnpm add @payloadcms/storage-vercel-blob
```

```typescript
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

plugins: [
  vercelBlobStorage({
    collections: { ['media']: true },
    token: process.env.BLOB_READ_WRITE_TOKEN || '',
  }),
]
```

### Other Storage Options

Payload supports S3, Azure Blob, Google Cloud Storage, and local filesystem storage via dedicated adapter packages.

## Caching Strategy

On Payload Cloud, all files are proxied through Cloudflare using `@payloadcms/payload-cloud`. Next.js caching is disabled by default — fetch requests include `no-store` and pages use `export const dynamic = 'force-dynamic'`.

To re-enable Next.js caching for self-hosted deployments:

1. Remove `no-store` from fetch requests in `src/app/_api/`
2. Remove `export const dynamic = 'force-dynamic'` from page files

## Scheduled Publishing

The template configures scheduled publishing using Payload's jobs queue:

```typescript
versions: {
  drafts: {
    autosave: true,
    schedulePublish: true,
  },
  maxPerDoc: 50,
}
```

Tasks run on a cron schedule. On Vercel, plan tier limits may restrict cron frequency (daily on hobby plans).

## Deployment Targets

### Vercel

1. Push code to Git repository
2. Connect to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy — Vercel handles build and serving automatically
5. Use Vercel Postgres adapter and Vercel Blob storage for full integration

### Self-Hosted (VPS)

1. Provision a server (DigitalOcean, AWS EC2, etc.)
2. Install Node.js matching engine requirements
3. Clone repository and install dependencies
4. Set environment variables
5. Run build and start commands
6. Configure a reverse proxy (Nginx, Caddy) for HTTPS
7. Set up process manager (PM2, systemd) for reliability

### Docker

```bash
# Copy .env.example to .env and configure
cp .env.example .env

# Build and run with docker-compose
docker-compose up
```

The `docker-compose.yml` file manages the application and database containers.

## Testing

```bash
# Run integration tests (Vitest)
pnpm test:int

# Run end-to-end tests (Playwright)
pnpm test:e2e

# Run both
pnpm test
```

## Seed Data

The template provides a seed script accessible from the admin panel or via the `/next/seed` endpoint. The seed creates:

- Sample pages with layout blocks
- Demo products with variants
- Sample orders and transactions
- Demo customer account (`customer@example.com` / `password`)

Warning: seeding drops the entire database — use only in development.

## Monitoring and Observability

For production monitoring:

- Enable Payload's built-in error logging
- Monitor Stripe webhook delivery for payment issues
- Track database connection health
- Set up uptime monitoring for the storefront
- Review transaction logs for failed payments
