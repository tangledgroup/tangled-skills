# Production Deployment

Complete guide to building, deploying, and monitoring the Payload CMS ecommerce template v3.82.1 in production environments including Vercel, self-hosting, and cloud platforms.

## Build Process

### Generate TypeScript Types

Before building, always generate types from Payload schema:

```bash
pnpm generate:types
```

This creates `src/payload-types.ts` with auto-generated TypeScript types from your collections and globals.

### Production Build

```bash
pnpm build
```

**What this does:**
1. Compiles Next.js application to `.next/` directory
2. Optimizes and minifies JavaScript bundles
3. Generates static pages (where applicable)
4. Creates production-ready admin panel
5. Validates all configurations

**Build Output:**
```
.next/
├── build-id              # Unique build identifier
├── cache/                # Build cache
├── server/               # Server-side code
│   ├── api/             # API routes
│   └── pages/           # Rendered pages
├── static/               # Static assets
│   ├── css/            # Compiled CSS
│   └── js/             # Client JavaScript
└── types/                # Type definitions
```

### Start Production Server

```bash
pnpm start
```

**Server Configuration:**
- Listens on `PORT` environment variable (default: 3000)
- Serves static files from `.next/`
- Runs API routes in production mode
- Enables caching optimizations

## Environment Configuration

### Required Production Variables

**Minimum required:**
```env
# Database
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/ecommerce-production

# Payload
PAYLOAD_SECRET=your-production-secret-minimum-32-chars

# Stripe (LIVE KEYS)
STRIPE_SECRET_KEY=sk_live_your-live-secret-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your-live-publishable-key
STRIPE_WEBHOOKS_SIGNING_SECRET=whsec_your-live-webhook-secret

# Public URL
PAYLOAD_PUBLIC_URL=https://your-domain.com
NEXT_PUBLIC_PAYLOAD_URL=https://your-domain.com

# Node Environment
NODE_ENV=production
PORT=3000
```

**Recommended additional:**
```env
# Email (for order confirmations, password resets)
RESEND_API_KEY=re_your-resend-api-key
# Or for Nodemailer:
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
POSTHOG_API_KEY=phc_your-posthog-key

# Security
NEXTAUTH_SECRET=your-nextauth-secret
```

### Stripe Live Mode Setup

**Critical: Switch from test to live keys**

1. **Get Live API Keys:**
   - Navigate to Stripe Dashboard > Developers > API Keys
   - Copy **Live mode** secret key (starts with `sk_live_`)
   - Copy **Live mode** publishable key (starts with `pk_live_`)

2. **Create Live Webhook Endpoint:**
   - Navigate to Stripe Dashboard > Developers > Webhooks
   - Add endpoint: `https://your-domain.com/api/payments/stripe/webhooks`
   - Select events:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `charge.succeeded`
     - `charge.failed`
   - Copy webhook signing secret (starts with `whsec_`)

3. **Update Environment Variables:**
   ```env
   # Replace test keys with live keys
   STRIPE_SECRET_KEY=sk_live_...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOKS_SIGNING_SECRET=whsec_...
   ```

4. **Test with Real Payment:**
   - Process a small real transaction ($1.00)
   - Verify webhook received in Stripe Dashboard
   - Confirm order created in admin panel
   - Refund test transaction if needed

**⚠️ Warning: Live keys process real money. Test thoroughly before enabling.**

## Deployment Platforms

### Vercel Deployment

Vercel is the recommended platform for Next.js deployments with built-in PostgreSQL support.

#### Prerequisites

1. **Vercel Account**: Free tier available
2. **Git Repository**: Push code to GitHub/GitLab/Bitbucket
3. **Vercel Postgres**: Enable in Vercel Dashboard (on paid plans)

#### Installation

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

#### Configuration

**vercel.json:**
```json
{
  "buildCommand": "pnpm build",
  "outputDirectory": ".next",
  "installCommand": "pnpm install",
  "devCommand": "pnpm dev",
  "framework": "nextjs"
}
```

**Environment Variables (Vercel Dashboard):**
1. Navigate to Project Settings > Environment Variables
2. Add all required variables from above
3. Deploy to apply changes

#### Database Setup

**Option A: Vercel Postgres (Recommended)**

```bash
# Install Vercel Postgres adapter
pnpm add @payloadcms/db-vercel-postgres
```

**Update payload.config.ts:**
```typescript
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'

export default buildConfig({
  db: vercelPostgresAdapter({
    pool: {
      connectionString: process.env.POSTGRES_URL || '',
    },
  }),
  // ... rest of config
})
```

**Environment Variables:**
```env
POSTGRES_URL=vercel://username:password@host:5432/dbname
POSTGRES_URL_NON_POOLING=vercel://username:password@host:5432/dbname
```

**Run Migrations:**
```bash
# Create migration
pnpm payload migrate:create

# Run on deploy (add to vercel.json)
{
  "buildCommand": "pnpm build && pnpm payload migrate"
}
```

**Option B: External MongoDB**

Use existing MongoDB Atlas or managed MongoDB instance. No code changes needed, just update `DATABASE_URL`.

#### Storage Setup

**Vercel Blob Storage (for media uploads):**

```bash
pnpm add @payloadcms/storage-vercel-blob
```

**Update payload.config.ts:**
```typescript
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

export default buildConfig({
  plugins: [
    vercelBlobStorage({
      collections: {
        media: true
      },
      token: process.env.BLOB_READ_WRITE_TOKEN || ''
    })
    // ... other plugins
  ]
})
```

**Environment Variable:**
```env
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

#### Deploy Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Deploy specific branch
vercel --prod --branch main
```

### Self-Hosting (VPS/Dedicated Server)

#### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Node.js 18.20.2+ or 20.9.0+
- PM2 or systemd for process management
- Nginx or Apache as reverse proxy
- MongoDB instance (local or remote)

#### Installation Steps

**1. Setup Server:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Install PM2 globally
npm install -g pm2

# Install Git
sudo apt install git -y
```

**2. Clone and Install:**

```bash
# Clone repository
git clone https://github.com/your-org/ecommerce.git
cd ecommerce

# Install dependencies
pnpm install

# Create environment file
cp .env.example .env
nano .env  # Edit with production values
```

**3. Build Application:**

```bash
# Generate types
pnpm generate:types

# Build for production
pnpm build
```

**4. Configure PM2:**

**ecosystem.config.js:**
```javascript
module.exports = {
  apps: [
    {
      name: 'ecommerce',
      script: 'pnpm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      instances: 'max',
      max_memory_restart: '500M'
    }
  ]
}
```

**Start with PM2:**
```bash
# Start application
pm2 start ecosystem.config.js

# Save PM2 configuration (auto-start on reboot)
pm2 save

# Setup PM2 to start on system boot
pm2 startup
```

**5. Configure Nginx:**

**/etc/nginx/sites-available/ecommerce:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase upload size for media
    client_max_body_size 50M;
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL with Let's Encrypt:**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (already configured by Certbot)
sudo certbot renew --dry-run  # Test renewal
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# Builder image
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
RUN pnpm generate:types && pnpm build

# Production image
FROM base AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV NODE_ENV=production

CMD ["node", "server.js"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=mongodb://mongo:27017/ecommerce
      - PAYLOAD_SECRET=${PAYLOAD_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY}
      - STRIPE_WEBHOOKS_SIGNING_SECRET=${STRIPE_WEBHOOKS_SIGNING_SECRET}
      - PAYLOAD_PUBLIC_URL=https://your-domain.com
    depends_on:
      - mongo
    restart: unless-stopped

  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped

volumes:
  mongo-data:
```

**Deploy:**
```bash
docker-compose up -d --build
```

## Monitoring and Observability

### Error Tracking (Sentry)

**Installation:**
```bash
pnpm add @sentry/nextjs
```

**Configuration (sentry.config.ts):**
```typescript
import { SentryOptions } from '@sentry/nextjs'

const options: SentryOptions = {
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,  // 10% sampling
  environment: process.env.NODE_ENV,
  release: process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA
}

export default options
```

**Error Capture:**
```typescript
import * as Sentry from '@sentry/nextjs'

try {
  await processPayment(order)
} catch (error) {
  Sentry.captureException(error)
  throw error
}
```

### Analytics (PostHog)

**Installation:**
```bash
pnpm add posthog-js
```

**Track Events:**
```typescript
import posthog from 'posthog-js'

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY)

// Track order placement
posthog.capture('order_placed', {
  orderId: order.id,
  total: order.total,
  items: order.items.length
})

// Track add to cart
posthog.capture('add_to_cart', {
  productId: product.id,
  variantId: variant?.id,
  quantity: quantity
})
```

### Performance Monitoring

**Next.js Built-in:**
```typescript
// Enable in next.config.ts
const nextConfig = {
  experimental: {
    // Enable runtime instrumentation
    serverActions: {
      bodySizeLimit: '2mb'
    }
  },
  // Custom metrics
  headers: async () => [
    {
      source: '/api/:path*',
      headers: [
        {
          key: 'X-Frame-Options',
          value: 'DENY'
        }
      ]
    }
  ]
}
```

## Caching Strategy

### Next.js Caching

**Default Behavior:**
- Static pages pre-rendered at build time
- API routes dynamic (no caching by default)
- Images cached automatically

**Disable Caching (for dynamic content):**
```typescript
// In page component
export const dynamic = 'force-dynamic'

// In API route
export const dynamic = 'force-dynamic'
```

**Revalidation:**
```typescript
// On-demand revalidation after order creation
await revalidatePath('/shop')
await revalidatePath(`/products/${productSlug}`)
```

### CDN Configuration

**Cloudflare (if using):**
```nginx
# Cache static assets
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Don't cache API responses
location /api/ {
    add_header Cache-Control "no-store, no-cache, must-revalidate";
}
```

## Backup and Recovery

### Database Backups

**MongoDB Backup:**
```bash
# Full database backup
mongodump --uri="$DATABASE_URL" --out=/backups/$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="$DATABASE_URL" /backups/20240101/
```

**Automated Backups (cron):**
```bash
# Add to crontab
0 2 * * * cd /app && mongodump --uri="$DATABASE_URL" --out=/backups/$(date +\%Y\%m\%d)
```

### Media File Backups

**Vercel Blob:**
- Automatic backups handled by Vercel
- Enable versioning for additional safety

**Self-hosted:**
```bash
# Backup uploads directory
tar -czf media-backup-$(date +%Y%m%d).tar.gz ./uploads/

# Restore
tar -xzf media-backup-20240101.tar.gz -C ./
```

## Performance Optimization

### Image Optimization

**Next.js Image Component:**
```typescript
import Image from 'next/image'

<Image
  src={productImage.url}
  alt={productImage.alt}
  width={800}
  height={600}
  priority={isVisible}  // Lazy load by default
  placeholder="blur"
  blurDataURL={blurData}
/>
```

**Remote Patterns (next.config.ts):**
```typescript
images: {
  remotePatterns: [
    {
      hostname: 'images.unsplash.com',
      protocol: 'https'
    },
    {
      hostname: 'your-cdn-domain.com',
      protocol: 'https'
    }
  ]
}
```

### Database Indexing

**Add indexes for performance:**
```typescript
// In collection config
fields: [
  {
    name: 'slug',
    type: 'text',
    unique: true,
    index: true  // Fast lookups by slug
  },
  {
    name: 'email',
    type: 'text',
    unique: true,
    index: true  // Fast user lookup
  }
]
```

### Code Splitting

Next.js automatically splits code by route. Ensure dynamic imports for large components:

```typescript
// Dynamic import for heavy component
const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  { loading: () => <LoadingSpinner /> }
)
```

## Security Hardening

### Environment Variables

**Never commit to Git:**
```gitignore
# Add to .gitignore
.env
.env.local
.env.production
.env.*.local
```

**Validate required variables:**
```typescript
// src/utilities/validateEnv.ts
export const validateEnv = () => {
  const required = [
    'DATABASE_URL',
    'PAYLOAD_SECRET',
    'STRIPE_SECRET_KEY',
    'NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY',
    'STRIPE_WEBHOOKS_SIGNING_SECRET'
  ]

  const missing = required.filter(key => !process.env[key])

  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`)
  }
}
```

### Rate Limiting

**Prevent abuse on API endpoints:**
```typescript
// Using Upstash or similar
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL,
  token: process.env.UPSTASH_REDIS_TOKEN
})

export const rateLimit = async (ip: string) => {
  const key = `rate-limit:${ip}`
  const count = await redis.incr(key)

  if (count === 1) {
    await redis.expire(key, 60)  // 1 minute window
  }

  if (count > 100) {
    throw new Error('Rate limit exceeded')
  }
}
```

### HTTPS Enforcement

**Nginx redirect:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring Checklist

- [ ] Database connection health
- [ ] API response times
- [ ] Error rates (Sentry)
- [ ] Payment success/failure rates
- [ ] Server resource usage (CPU, memory)
- [ ] Disk space for logs/backups
- [ ] SSL certificate expiration
- [ ] CDN cache hit ratios

See [Troubleshooting Guide](10-troubleshooting.md) for common deployment issues.
