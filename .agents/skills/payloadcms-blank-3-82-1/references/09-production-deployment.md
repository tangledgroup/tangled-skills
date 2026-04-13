# Production Deployment

Complete guide to deploying Payload CMS blank template to production, including build process, Docker deployment, environment configuration, and monitoring.

## Build Process

### Pre-Deployment Checklist

Before deploying to production:

1. **Generate TypeScript types:**
   ```bash
   pnpm generate:types
   ```

2. **Run tests:**
   ```bash
   pnpm test
   ```

3. **Lint code:**
   ```bash
   pnpm lint
   ```

4. **Check for security issues:**
   ```bash
   pnpm audit
   ```

5. **Verify environment variables:**
   - `DATABASE_URL` points to production database
   - `PAYLOAD_SECRET` is unique and secure (different from development)
   - All required API keys and secrets are set

### Build for Production

```bash
# Install dependencies (production mode)
pnpm install --frozen-lockfile

# Generate types
pnpm generate:types

# Build Next.js application
pnpm build

# Start production server
pnpm start
```

**Build output:**
- `.next/` directory contains optimized production build
- Minified JavaScript bundles
- Compiled TypeScript
- Optimized images and assets

### Production Server Requirements

**Node.js version:** Must match development (18.20.2+ or 20.9.0+)

**Environment variables:**
```env
NODE_ENV=production
PORT=3000
DATABASE_URL=mongodb+srv://production-connection-string
PAYLOAD_SECRET=production-secret-different-from-dev
```

**System requirements:**
- Minimum 2GB RAM
- 2+ CPU cores recommended
- SSD storage for database
- Reverse proxy (nginx, Cloudflare) for SSL termination

## Docker Production Deployment

### Multi-Stage Dockerfile

The template includes a production-ready `Dockerfile`:

```dockerfile
# Build stage
FROM node:22.17.0-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Production stage
FROM node:22.17.0-alpine AS runner
WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=deps /app/.next/standalone ./
COPY --from=deps /app/.next/static ./.next/static
COPY --from=deps /app/public ./public

# Set ownership
RUN chown -R nextjs:nodejs /app

# Run as non-root user
USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD HOSTNAME="0.0.0.0" node server.js
```

### Required Configuration for Docker

**next.config.ts:** Add standalone output:

```typescript
const nextConfig: NextConfig = {
  output: 'standalone', // Required for Docker multi-stage build
  
  images: {
    localPatterns: [
      { pathname: '/api/media/file/**' },
    ],
  },
  
  webpack: (webpackConfig) => {
    webpackConfig.resolve.extensionAlias = {
      '.cjs': ['.cts', '.cjs'],
      '.js': ['.ts', '.tsx', '.js', '.jsx'],
      '.mjs': ['.mts', '.mjs'],
    }
    return webpackConfig
  },
}

export default withPayload(nextConfig, { devBundleServerPackages: false })
```

### Building Docker Image

```bash
# Build image
docker build -t payload-production:latest .

# Run container
docker run -d \
  --name payload-prod \
  -p 3000:3000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e PAYLOAD_SECRET=$PAYLOAD_SECRET \
  payload-production:latest
```

### Docker Compose for Production

**docker-compose.prod.yml:**

```yaml
version: '3'

services:
  payload:
    build:
      context: .
      dockerfile: Dockerfile
    image: payload-production:latest
    ports:
      - '3000:3000'
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - PAYLOAD_SECRET=${PAYLOAD_SECRET}
    restart: unless-stopped
    depends_on:
      mongo:
        condition: service_healthy
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db
    command:
      - --storageEngine=wiredTiger
      - --bind_ip_all
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    logging:
      driver: none

volumes:
  mongo-data:
```

**Run production stack:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Configuration

### Required Production Variables

```env
# Database (MongoDB Atlas recommended for production)
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/production-db?retryWrites=true&w=majority

# Payload Secret (MUST be different from development!)
PAYLOAD_SECRET=generate-new-64-char-hex-secret-for-production

# Node Environment
NODE_ENV=production

# Server Configuration
PORT=3000
HOSTNAME=0.0.0.0

# Payload Public URL (for email links, previews, webhooks)
PAYLOAD_PUBLIC_URL=https://your-domain.com

# Optional: Redis for caching and sessions
REDIS_URL=redis://redis:6379

# Optional: Email service (for password resets, notifications)
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@your-domain.com

# Optional: Logging
LOG_LEVEL=info
LOG_FORMAT=json

# Optional: Security headers
HSTS_MAX_AGE=31536000
```

### Secret Management

**Never commit secrets to version control:**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore
```

**Use environment-specific files:**
- `.env` - Local development (gitignored)
- `.env.example` - Template with placeholder values (committed)
- `.env.production` - Production secrets (gitignored, on server only)

**Generate secure secrets:**

```bash
# Payload secret (64 hex characters)
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# JWT secret
openssl rand -hex 64

# Session secret
python3 -c "import secrets; print(secrets.token_hex(64))"
```

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. **Create cluster:**
   - Go to https://cloud.mongodb.com/
   - Create free cluster (M0) or paid (M10+)
   - Choose production region closest to users

2. **Configure database user:**
   - Database Access > Add New User
   - Username: `payload-app`
   - Password: Auto-generate secure password
   - Role: Read and write to any database

3. **Configure network access:**
   - Network Access > Add IP Address
   - For VPS/Dedicated: Add server IP
   - For PaaS (Vercel, Railway): Allow access from anywhere (0.0.0.0/0)

4. **Get connection string:**
   - Clusters > Connect > Drivers
   - Copy connection string
   - Replace `<password>` with actual password
   - Replace `<database>` with your database name

5. **Update .env:**
   ```env
   DATABASE_URL=mongodb+srv://payload-app:your-password@cluster.mongodb.net/production-db?retryWrites=true&w=majority
   ```

### MongoDB Replica Set (For Transactions)

**Required for:** Multi-document transactions, atomic operations

**Setup on Atlas:** Automatically configured

**Self-hosted setup:**
```bash
# Start with replica set flag
docker run -d \
  --name mongo \
  -p 27017:27017 \
  mongo:latest \
  --replSet rs0

# Initialize replica set
docker exec -it mongo mongosh --eval "rs.initiate()"

# Connection string
mongodb://localhost:27017/?replicaSet=rs0
```

### Database Backups

**MongoDB Atlas:** Automatic snapshots (paid plans)

**Self-hosted backup:**
```bash
# Backup entire database
mongodump --uri="mongodb+srv://connection-string" --out=/backups/$(date +%Y%m%d)

# Backup specific database
mongodump --uri="mongodb+srv://connection-string" --db=production-db --out=/backups/

# Restore from backup
mongorestore --uri="mongodb+srv://connection-string" /backups/20240101/
```

**Automated backups (cron):**
```bash
# Add to crontab
0 2 * * * mongodump --uri="$DATABASE_URL" --out=/backups/$(date +\%Y\%m\%d) && find /backups -type d -mtime +7 -exec rm -rf {} \;
```

## Platform-Specific Deployments

### Vercel Deployment

**vercel.json:**
```json
{
  "buildCommand": "pnpm install --frozen-lockfile && pnpm generate:types && pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install --frozen-lockfile",
  "framework": "nextjs"
}
```

**Environment variables in Vercel:**
- Go to Project Settings > Environment Variables
- Add `DATABASE_URL`, `PAYLOAD_SECRET`, etc.
- Deploy: `vercel deploy --prod`

**Note:** Vercel functions have timeout limits (10s on Hobby, 60s on Pro). Long-running operations should use background jobs.

### Railway Deployment

**railway.toml:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "pnpm start"
```

**Add services:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link project
railway login
railway link

# Add MongoDB
railway up mongodb

# Deploy
railway up
```

### Render Deployment

**Create web service:**
1. New Web Service from GitHub repo
2. Build Command: `pnpm install --frozen-lockfile && pnpm generate:types && pnpm build`
3. Start Command: `pnpm start`
4. Add environment variables
5. Attach PostgreSQL or MongoDB addon

### AWS ECS (Container Registry)

**Docker Hub push:**
```bash
# Login to Docker Hub
docker login

# Tag image
docker tag payload-production:latest username/payload-prod:v1.0.0

# Push
docker push username/payload-prod:v1.0.0
```

**ECS task definition:** Configure in AWS Console with environment variables and volume mounts for media files.

## CDN and Caching

### Media CDN Setup

**Using Cloudflare:**
1. Point domain to Cloudflare nameservers
2. Enable caching for `/media/*` and `/api/media/*`
3. Set cache TTL: 1 year for static assets
4. Enable image optimization (Polish, Mirage)

**Using AWS CloudFront:**
1. Create CloudFront distribution
2. Origin: Your Payload server or S3 bucket
3. Cache policy: Default caching for media files
4. Invalidations when media updates

### Next.js Image Optimization

```typescript
// next.config.ts
const nextConfig = {
  images: {
    // External image domains
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.your-domain.com',
      },
      {
        protocol: 'https',
        hostname: '*.cloudfront.net',
      },
    ],
    // Local media files
    localPatterns: [
      {
        pathname: '/api/media/file/**',
      },
    ],
    // Cache configuration
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
}
```

### HTTP Caching Headers

**nginx configuration:**
```nginx
# Cache media files for 1 year
location ~* \.(jpg|jpeg|png|gif|webp|svg|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Cache admin assets for 1 month
location /_next/ {
    expires 1M;
    add_header Cache-Control "public, must-revalidate";
}

# No cache for API responses
location /api/ {
    add_header Cache-Control "no-store, no-cache, must-revalidate";
    add_header Pragma "no-cache";
}
```

## Security Hardening

### SSL/TLS Configuration

**Use Let's Encrypt (Certbot):**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (automatic via systemd timer)
sudo certbot renew --dry-run
```

**Security headers:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Rate Limiting

**Using nginx:**
```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://localhost:3000;
        }
    }
}
```

**Using Redis (for distributed rate limiting):**
```typescript
import { RateLimiterRedis } from 'rate-limiter-flexible'

const rateLimiter = new RateLimiterRedis({
  storeClient: redisClient,
  keyPrefix: 'api_rate_limit',
  points: 100, // Number of requests
  duration: 60, // Per second
})

// In route handler
await rateLimiter.consume(req.ip)
```

### Firewall Configuration

**UFW (Ubuntu):**
```bash
sudo ufw enable
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH (consider restricting to your IP)
sudo ufw status
```

## Monitoring and Logging

### Application Logs

**Structured logging:**
```typescript
import winston from 'winston'

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})

// Usage
logger.info('User logged in', { userId: user.id, email: user.email })
logger.error('Database connection failed', { error: err.message })
```

### Error Tracking

**Sentry integration:**
```bash
pnpm add @sentry/nextjs
```

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: 'your-sentry-dsn',
  environment: process.env.NODE_ENV,
})
```

### Performance Monitoring

**APM with New Relic/Datadog:**
```bash
pnpm add newrelic
```

Configure in `newrelic.js` or via environment variables.

### Health Checks

**Add health check endpoint:**
```typescript
// src/app/api/health/route.ts
export const GET = async () => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  }
  
  return Response.json(health)
}
```

**Docker health check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1
```

## Scaling Considerations

### Horizontal Scaling

**Stateless application:** Payload is stateless and can be horizontally scaled.

**Load balancer configuration:**
- Use sticky sessions for file uploads
- Health checks on `/api/health`
- Connection pooling to database

**Multiple instances:**
```yaml
# docker-compose.yml
services:
  payload-1:
    image: payload-production:latest
    # ... config
    
  payload-2:
    image: payload-production:latest
    # ... same config
```

### Database Connection Pooling

**MongoDB connection limits:**
- Free tier Atlas: 100 connections
- Paid tiers: Higher limits

**Configure pool size:**
```typescript
db: mongooseAdapter({
  url: process.env.DATABASE_URL,
  mongoOptions: {
    maxPoolSize: 50, // Adjust based on tier and instances
    minPoolSize: 10,
  },
})
```

### File Storage

**For multiple instances, use shared storage:**

**AWS S3:**
```typescript
import { s3Storage } from '@payloadcms/storage-s3'

export default buildConfig({
  plugins: [
    s3Storage({
      collection: 'media',
      bucket: 'your-bucket-name',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION || 'us-east-1',
    }),
  ],
})
```

**Alternative: Cloudinary, Azure Blob, Google Cloud Storage**

### Background Jobs

**For long-running tasks, use job queue:**

**BullMQ with Redis:**
```bash
pnpm add bullmq ioredis
```

```typescript
import { Queue } from 'bullmq'

const imageProcessingQueue = new Queue('image-processing', {
  connection: redisConnection,
})

// In hook
hooks: {
  afterChange: [
    async ({ doc }) => {
      await imageProcessingQueue.add('process-image', { docId: doc.id })
    },
  ],
}
```

Run worker separately:
```typescript
import { Worker } from 'bullmq'

const worker = new Worker('image-processing', async (job) => {
  await processImage(job.data.docId)
}, { connection: redisConnection })
```

## Rollback Strategy

### Versioned Deployments

**Keep previous version:**
```bash
# Tag Docker images with version
docker tag payload-production username/payload:v1.2.3
docker push username/payload:v1.2.3

# In production, quick rollback:
docker stop payload && docker rm payload
docker run -d --name payload username/payload:v1.2.2
```

### Database Migrations

**Before schema changes:**
1. Backup database
2. Test migration in staging
3. Deploy during low-traffic period
4. Monitor for errors
5. Have rollback plan ready

**Rollback steps:**
```bash
# Stop application
docker stop payload

# Restore database
mongorestore --uri="$DATABASE_URL" --drop backup/pre-migration/

# Deploy previous version
docker run -d --name payload username/payload:v1.2.2
```

## Monitoring Checklist

**Set up monitoring for:**

- [ ] Application uptime (Pingdom, UptimeRobot)
- [ ] Error rate (Sentry, LogRocket)
- [ ] Response times (New Relic, Datadog)
- [ ] Database connections (MongoDB Atlas metrics)
- [ ] Disk space usage
- [ ] Memory usage
- [ ] CPU usage
- [ ] Failed logins/security events
- [ ] Email delivery rates
- [ ] CDN cache hit ratio

**Alert thresholds:**
- Uptime < 99.9%
- Error rate > 1%
- Response time > 2s (p95)
- Database connections > 80% of limit
- Disk usage > 80%

## Post-Deployment Testing

**After deploying, verify:**

1. **Basic functionality:**
   - Homepage loads
   - Admin panel accessible
   - Login works
   - Can create/edit documents

2. **API endpoints:**
   - REST API responds correctly
   - GraphQL endpoint functional
   - Custom routes work

3. **Media handling:**
   - Image upload works
   - Images serve correctly
   - Optimization applied

4. **Email functionality:**
   - Password reset emails sent
   - Email links work

5. **Performance:**
   - Page load times acceptable
   - API response times within SLA

6. **Security:**
   - HTTPS enforced
   - Security headers present
   - No exposed sensitive data
