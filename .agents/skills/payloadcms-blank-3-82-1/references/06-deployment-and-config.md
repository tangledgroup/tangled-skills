# Deployment and Configuration

This reference documents environment setup, deployment strategies, production configurations, and troubleshooting for Payload CMS 3.82.1 blank template. Covers local development through production deployment across various platforms.

## Environment Variables

### Required Variables

**`.env`** (local development):
```bash
# MongoDB connection string
DATABASE_URL=mongodb://127.0.0.1/payload

# Random secret for signing cookies and JWT tokens
PAYLOAD_SECRET=your-random-secret-here
```

Generate a secure secret:
```bash
# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Using Payload CLI
npx payload generate:secret
```

### Production Variables

**`.env.production`**:
```bash
# Production MongoDB (Atlas or managed instance)
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/payload?retryWrites=true&w=majority

# Never commit this value!
PAYLOAD_SECRET=your-production-secret-here

# Next.js settings
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://your-domain.com

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379

# Optional: S3 for file uploads
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
```

### Development vs Production

Use environment-specific values:

```typescript
// payload.config.ts
export default buildConfig({
  secret: process.env.PAYLOAD_SECRET,
  
  db: mongooseAdapter({
    url: process.env.DATABASE_URL || 'mongodb://127.0.0.1/payload',
  }),
  
  serverURL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  
  // Development-specific settings
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
})
```

## Local Development

### Standard Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/your-project.git
cd your-project

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with local values
# DATABASE_URL=mongodb://127.0.0.1/payload
# PAYLOAD_SECRET=$(openssl rand -base64 32)

# 4. Install dependencies
pnpm install

# 5. Generate types
pnpm run generate:types

# 6. Start MongoDB (if not running)
mongod --dbpath /data/db

# 7. Start development server
pnpm dev
```

### Docker Development

For consistent environments across teams:

**`docker-compose.yml`** (from template):
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

Usage:
```bash
# Start all services
docker-compose up

# Background mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f payload

# Execute commands in container
docker-compose exec payload pnpm generate:types
```

### Development Best Practices

1. **Use `.env.local`** for personal secrets (gitignored)
2. **Generate types after schema changes**: `pnpm run generate:types`
3. **Clear cache on issues**: `pnpm devsafe` (removes `.next`)
4. **Run linting**: `pnpm run lint`
5. **Format code**: `npx prettier --write .`

## Production Build

### Building for Production

```bash
# Install dependencies (production only)
pnpm install --frozen-lockfile

# Generate types
pnpm run generate:types

# Build Next.js application
pnpm run build

# Start production server
pnpm start
```

### Production Server Requirements

- Node.js 18.20.2+ or 20.9.0+
- MongoDB 6.0+ (managed instance recommended)
- At least 2GB RAM
- Persistent storage for uploads

### PM2 Process Manager

For production deployment with PM2:

**`ecosystem.config.js`**:
```javascript
module.exports = {
  apps: [
    {
      name: 'payload-cms',
      script: 'npm',
      args: 'start',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
      },
    },
  ],
}
```

Usage:
```bash
# Install PM2 globally
npm install -g pm2

# Start application
pm2 start ecosystem.config.js

# Monitor
pm2 monit

# Logs
pm2 logs payload-cms

# Restart
pm2 restart payload-cms

# Stop
pm2 stop payload-cms
```

## Deployment Platforms

### Vercel

**`vercel.json`**:
```json
{
  "buildCommand": "pnpm run build",
  "devCommand": "pnpm run dev",
  "installCommand": "pnpm install",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

Environment variables in Vercel dashboard:
- `DATABASE_URL` - MongoDB Atlas connection string
- `PAYLOAD_SECRET` - Production secret

Deploy commands:
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Preview deployment
vercel
```

### Netlify

**`netlify.toml`**:
```toml
[build]
  command = "pnpm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[functions]
  directory = ".next/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

Deploy:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

### Docker Production

**`Dockerfile`**:
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile

# Copy source
COPY . .

# Generate types and build
RUN pnpm run generate:types
RUN pnpm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/.next .next
COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/package.json package.json
COPY --from=builder /app/public public

# Set permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]
```

**Build and run**:
```bash
# Build image
docker build -t payload-cms:production .

# Run container
docker run -d \
  --name payload-prod \
  -p 3000:3000 \
  -e DATABASE_URL=mongodb+srv://... \
  -e PAYLOAD_SECRET=... \
  payload-cms:production
```

### Kubernetes Deployment

**`kubernetes/deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payload-cms
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payload-cms
  template:
    metadata:
      labels:
        app: payload-cms
    spec:
      containers:
        - name: payload
          image: payload-cms:production
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: payload-secrets
                  key: database-url
            - name: PAYLOAD_SECRET
              valueFrom:
                secretKeyRef:
                  name: payload-secrets
                  key: payload-secret
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: payload-cms
spec:
  selector:
    app: payload-cms
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

### Railway

**`railway.toml`**:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "pnpm start"
numReplicas = 1
```

Deploy:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Render

Create `render.yaml`:
```yaml
services:
  - type: web
    name: payload-cms
    env: node
    buildCommand: pnpm install && pnpm run build
    startCommand: pnpm start
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: PAYLOAD_SECRET
        generateValue: true
      - key: NODE_ENV
        value: production
```

## Database Configuration

### MongoDB Atlas Setup

1. Create MongoDB Atlas account
2. Create new cluster (free tier M0 available)
3. Create database user with read/write permissions
4. Whitelist IP addresses (0.0.0.0/0 for public access)
5. Get connection string from Atlas dashboard
6. Replace `<password>` with actual password

Example connection string:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/payload?retryWrites=true&w=majority
```

### Local MongoDB Installation

**Ubuntu/Debian**:
```bash
# Install MongoDB
wget https://www.mongodb.org/static/pgp/server-7.0.asc
sudo apt-key add mongo-server-7.0.asc
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**macOS (Homebrew)**:
```bash
brew install mongodb-community
brew services start mongodb-community
```

### Database Migration

Payload handles schema migrations automatically through Mongoose. For manual migrations:

```typescript
// src/scripts/migrate-users.ts
import config from '@/payload.config'
import { getPayload } from 'payload'

const migrateUsers = async () => {
  const payload = await getPayload({ config })
  
  // Get all users
  const { docs: users } = await payload.find({
    collection: 'users',
    limit: 1000,
  })
  
  // Update each user
  for (const user of users) {
    await payload.update({
      collection: 'users',
      id: user.id,
      data: {
        // Add new field or migrate data
        role: user.role || 'user',
      },
    })
  }
  
  console.log('Migration complete')
  process.exit(0)
}

migrateUsers()
```

Run migration:
```bash
npx tsx src/scripts/migrate-users.ts
```

## File Upload Configuration

### Local Storage (Development)

Default configuration stores uploads in `./uploads`:

```typescript
// payload.config.ts
export default buildConfig({
  collections: [
    {
      slug: 'media',
      upload: {
        staticDir: './uploads',
      },
      fields: [/* ... */],
    },
  ],
})
```

Ensure uploads directory exists and has write permissions.

### AWS S3 (Production)

Use `@payloadcms/storage-s3` plugin:

```bash
pnpm add @payloadcms/storage-s3
```

```typescript
// payload.config.ts
import { s3Storage } from '@payloadcms/storage-s3'

export default buildConfig({
  plugins: [
    s3Storage({
      collection: 'media',
      bucket: process.env.S3_BUCKET,
      config: {
        region: process.env.AWS_REGION,
        credentials: {
          accessKeyId: process.env.AWS_ACCESS_KEY_ID,
          secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        },
      },
    }),
  ],
  collections: [/* ... */],
})
```

### Cloudinary

Use `@payloadcms/storage-cloudinary` plugin:

```bash
pnpm add @payloadcms/storage-cloudinary
```

```typescript
import { cloudinaryStorage } from '@payloadcms/storage-cloudinary'

export default buildConfig({
  plugins: [
    cloudinaryStorage({
      collection: 'media',
      cloudName: process.env.CLOUDINARY_CLOUD_NAME,
      apiKey: process.env.CLOUDINARY_API_KEY,
      apiSecret: process.env.CLOUDINARY_API_SECRET,
    }),
  ],
})
```

## Caching Strategy

### Response Caching

Implement caching for read operations:

```typescript
// Custom route with caching
export const GET = async (request: Request) => {
  const cacheKey = 'posts-list'
  
  // Check cache first (requires Redis or similar)
  const cached = await redis.get(cacheKey)
  if (cached) {
    return Response.json(JSON.parse(cached))
  }
  
  // Fetch from database
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
  })
  
  // Cache for 5 minutes
  await redis.setex(cacheKey, 300, JSON.stringify(posts.docs))
  
  return Response.json(posts.docs)
}
```

### Next.js Caching

Use Next.js built-in caching for server components:

```typescript
// src/app/page.tsx
import { getPayload } from 'payload'
import config from '@/payload.config'

export const revalidate = 3600 // Revalidate every hour

export default async function HomePage() {
  const payload = await getPayload({ config })
  
  const posts = await payload.find({
    collection: 'posts',
    limit: 10,
  })
  
  return <>{/* render posts */}</>
}
```

## Monitoring and Logging

### Application Logs

Use a logging library like `winston`:

```bash
pnpm add winston
```

```typescript
// src/lib/logger.ts
import winston from 'winston'

export const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})
```

### Health Check Endpoint

Create a health check route:

```typescript
// src/app/api/health/route.ts
import configPromise from '@payload-config'
import { getPayload } from 'payload'

export const GET = async () => {
  try {
    const payload = await getPayload({ config: configPromise })
    
    // Check database connection
    await payload.count({ collection: 'posts' })
    
    return Response.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    })
  } catch (error) {
    return Response.json(
      { status: 'unhealthy', error: error.message },
      { status: 503 }
    )
  }
}
```

## Troubleshooting

### Common Issues

**MongoDB connection failed**:
- Verify `DATABASE_URL` is correct
- Check MongoDB is running and accessible
- Ensure IP whitelist includes your server
- Test connection: `mongosh "mongodb://127.0.0.1/payload"`

**TypeScript errors after changes**:
```bash
pnpm run generate:types
```

**Admin panel not loading**:
- Clear `.next` cache: `rm -rf .next && pnpm dev`
- Check browser console for errors
- Verify `PAYLOAD_SECRET` is set

**Uploads failing**:
- Check file permissions on uploads directory
- Verify MIME types are allowed
- Check disk space: `df -h`

**Memory issues in production**:
```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" pnpm start
```

**Port already in use**:
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port
NEXT_PORT=3001 pnpm dev
```

### Debugging Mode

Enable verbose logging:

```bash
# MongoDB debug
MONGODB_DEBUG=true pnpm dev

# Payload debug
PAYLOAD_DEBUG=true pnpm dev

# Next.js debug
NEXT_DEBUG=1 pnpm dev
```

### Performance Issues

**Slow queries**:
- Add database indexes on frequently queried fields
- Use `limit` and pagination
- Enable query caching

**Large payloads**:
- Use `fields` parameter to select only needed fields
- Implement lazy loading for relationships
- Compress responses with gzip

**Memory leaks**:
- Monitor with `node --inspect`
- Check for unclosed database connections
- Review event listener cleanup

## Security Checklist

Before deploying to production:

- [ ] Set strong `PAYLOAD_SECRET` (64+ characters)
- [ ] Use HTTPS for all endpoints
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Restrict admin panel access
- [ ] Use environment variables for secrets
- [ ] Enable database authentication
- [ ] Regular security updates
- [ ] Implement backup strategy
- [ ] Monitor for suspicious activity
- [ ] Set up error alerting

## Backup Strategy

### Database Backups

**MongoDB manual backup**:
```bash
# Backup entire database
mongodump --uri "mongodb+srv://..." --out ./backup

# Restore
mongorestore --uri "mongodb+srv://..." ./backup
```

**Automated backups (cron)**:
```bash
# Add to crontab
0 2 * * * mongodump --uri "$DATABASE_URL" --out /backups/mongodb-$(date +\%Y\%m\%d)
```

### File Uploads Backup

For S3, enable versioning and lifecycle policies. For local storage:

```bash
# Backup uploads directory
tar -czf uploads-backup-$(date +\%Y\%m\%d).tar.gz ./uploads
```

## References

- **Payload Deployment Guide**: https://payloadcms.com/docs/getting-started/deployment
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas
- **Vercel Documentation**: https://vercel.com/docs
- **Docker Documentation**: https://docs.docker.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
