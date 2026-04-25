# Deployment and Production

## Building for Production

### Local Build

```bash
npm run build
```

This creates an optimized production build in `.next/` directory.

### Start Production Server

```bash
npm start
```

Runs `next start` which serves the production build at `http://localhost:3000`.

## Deploying to Vercel (Recommended)

### Prerequisites

1. Push code to Git repository (GitHub, GitLab, Bitbucket)
2. Install Vercel CLI: `npm i -g vercel`

### Deploy via CLI

```bash
# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Deploy via Dashboard

1. Go to https://vercel.com/new
2. Import Git repository
3. Configure settings (most auto-detected)
4. Click "Deploy"

### Vercel Features

- Automatic HTTPS
- Global CDN
- Edge Network
- Preview deployments for PRs
- Analytics
- Serverless functions

## Self-Hosting

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN yarn install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**Build and run:**
```bash
docker build -t my-next-app .
docker run -p 3000:3000 my-next-app
```

### PM2 Deployment

```bash
npm install -g pm2

# Build
npm run build

# Start with PM2
pm2 start npm --name "my-app" -- start

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

### Systemd Deployment

**/etc/systemd/system/nextapp.service:**
```ini
[Unit]
Description=Next.js Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/next-app
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nextapp
sudo systemctl start nextapp
```

## Environment Variables

### Local Development

Create `.env.local`:
```env
DATABASE_URL=postgresql://localhost/myapp
API_SECRET=dev-secret
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

### Production (Vercel)

1. Go to Project Settings → Environment Variables
2. Add each variable
3. Redeploy

### Protected Variables

- Prefix with `NEXT_PUBLIC_` for client access
- Server-only variables never exposed to client

## Configuration

### next.config.js

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for Docker
  output: 'standalone',
  
  // Image domains
  images: {
    domains: ['images.example.com'],
  },
  
  // Rewrites for SPA fallback
  rewrites: async () => {
    return [
      {
        source: '/(.*)',
        destination: '/',
      },
    ]
  },
  
  // Headers
  headers: async () => {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

### Performance Optimization

**Enable in next.config.js:**
```js
const nextConfig = {
  // Analyze bundle
  experimental: {
    bundlePagesUtils: true,
  },
  
  // Optimize fonts
  swcMinify: true,
  
  // Generate source maps (development only)
  productionBrowserSourceMaps: false,
}
```

## Monitoring and Logging

### Vercel Logs

```bash
# View logs
vercel logs

# View specific deployment
vercel logs [deployment-url]
```

### Application Logging

```tsx
// lib/logger.ts
export const logger = {
  info: (msg: string) => console.info(`[INFO] ${msg}`),
  error: (msg: string, err?: Error) => console.error(`[ERROR] ${msg}`, err),
  warn: (msg: string) => console.warn(`[WARN] ${msg}`),
}
```

## Troubleshooting

### Build Errors

1. Clear cache: `rm -rf .next node_modules/.cache`
2. Check Node version: `node --version` (need 20.9+)
3. Verify dependencies: `npm install`

### Runtime Errors

1. Check environment variables are set
2. Verify database connectivity
3. Review error logs

### Performance Issues

1. Enable caching for data fetching
2. Optimize images with `next/image`
3. Use `dynamic()` for heavy components
4. Implement code splitting

## CI/CD Pipeline Example

**.github/workflows/deploy.yml:**
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```
