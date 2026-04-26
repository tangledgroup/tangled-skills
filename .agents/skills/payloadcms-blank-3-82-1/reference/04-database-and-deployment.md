# Database and Deployment

## MongoDB Adapter

The blank template uses `@payloadcms/db-mongodb` with the Mongoose driver. Configuration in `payload.config.ts`:

```ts
import { mongooseAdapter } from '@payloadcms/db-mongodb'

db: mongooseAdapter({
  url: process.env.DATABASE_URL || '',
}),
```

### Local MongoDB

Install MongoDB locally and set `DATABASE_URL` to point to it:

```
DATABASE_URL=mongodb://127.0.0.1/your-database-name
```

Or use MongoDB Atlas for a cloud-hosted database:

```
DATABASE_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/your-database-name
```

### Switching to PostgreSQL

To use PostgreSQL instead of MongoDB, replace the adapter:

```ts
import { postgresAdapter } from '@payloadcms/db-postgres'

db: postgresAdapter({
  pool: {
    connectionString: process.env.DATABASE_URL || '',
  },
}),
```

Then update `DATABASE_URL` to a PostgreSQL connection string:

```
DATABASE_URL=postgresql://user:password@localhost:5432/your-database-name
```

## Docker Development

The `docker-compose.yml` provides a two-service setup for local development:

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

Key details:

- The Payload service uses Node 20 Alpine with hot-reload via volume mounts
- `corepack enable` activates pnpm without pre-installing it
- MongoDB runs with WiredTiger storage engine (recommended for performance)
- MongoDB logs are suppressed (`driver: none`) to reduce noise
- Named volumes persist data across container restarts
- PostgreSQL is available as a commented-out service — uncomment and update `DATABASE_URL` to use it

To start:

```bash
docker-compose up
# or in background:
docker-compose up -d
```

## Production Docker Build

The `Dockerfile` uses a multi-stage build optimized for Next.js standalone output:

```dockerfile
FROM node:22.17.0-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm run build

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

Build stages:

1. **deps** — installs dependencies only (cached layer for faster rebuilds)
2. **builder** — copies source and runs `pnpm run build`
3. **runner** — production image with only the `.next/standalone` output, running as non-root user

The Dockerfile requires `output: 'standalone'` in Next.js config. The blank template achieves this through `withPayload()` which includes standalone output support by default. For explicit configuration:

```ts
const nextConfig: NextConfig = {
  output: 'standalone',
  // ... other config
}
```

Build and run the production image:

```bash
docker build -t my-payload-app .
docker run -p 3000:3000 --env-file .env my-payload-app
```

## Production Considerations

- **PAYLOAD_SECRET** must be a strong random string — never use the example value
- **DATABASE_URL** should point to a production database with proper authentication
- Set `NODE_ENV=production` in the runtime environment
- Use a reverse proxy (nginx, caddy) for TLS termination if not deploying behind a managed platform
- For media uploads, consider using a storage plugin (S3, Cloudflare R2) instead of local filesystem
- Enable CORS if the admin panel and frontend are served from different domains

## Testing

The template includes both integration and e2e test configurations:

- **Vitest** (`vitest.config.mts`) — unit and integration tests
- **Playwright** (`playwright.config.ts`) — end-to-end browser tests
- **jsdom** — DOM simulation for component testing

Run tests with:

```bash
pnpm test          # runs both integration and e2e
pnpm test:int      # integration tests only
pnpm test:e2e      # e2e tests only
```
