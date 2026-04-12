# SolidStart Deployment Guide

## Overview

SolidStart uses deployment adapters (presets) to configure your application for different platforms. The preset is configured in `app.config.ts`:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "vercel" }, // Change based on target platform
});
```

## Build Process

### Local Build

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build locally
npm run preview
```

The build process creates:
- Optimized bundles with code splitting
- Prerendered static pages (if configured)
- Platform-specific output structure

## Vercel Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "vercel" },
});
```

### Deployment Methods

#### Via Vercel CLI

```bash
npm i -g vercel

# Login once
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### Via Git Integration

1. Push code to GitHub/GitLab/Bitbucket
2. Import project in Vercel dashboard
3. Vercel auto-detects SolidStart framework
4. Deploy automatically on push

### Environment Variables

Add environment variables in Vercel dashboard or `.vercel/env`:

```bash
# Vercel dashboard > Settings > Environment Variables
VITE_API_URL=https://api.example.com
DATABASE_URL=postgresql://...
```

### Routing Configuration (Optional)

For custom rewrites or redirects:

```json
// vercel.json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/$1" }
  ],
  "redirects": [
    { "source": "/old-path", "destination": "/new-path", "permanent": true }
  ]
}
```

## Netlify Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "netlify" },
});
```

### Deployment Methods

#### Via Netlify CLI

```bash
npm i -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy

# Deploy to production
netlify deploy --prod
```

#### Via Git Integration

1. Connect repository in Netlify dashboard
2. Build command: `npm run build`
3. Publish directory: `.vercel/output` or `dist/`
4. Enable "Serverless Functions" for SSR

### Environment Variables

```bash
# netlify.toml
[build.environment]
  VITE_API_URL = "https://api.example.com"
```

Or add in Netlify dashboard > Site settings > Environment variables.

### Netlify Configuration

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/app/:splat"
  status = 200
```

## Cloudflare Pages Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "cloudflare" },
});
```

### Prerequisites

- Cloudflare account
- Wrangler CLI installed: `npm i -g wrangler`

### Deployment

#### Via Wrangler

```bash
# Login
wrangler login

# Deploy
wrangler pages deploy dist

# Deploy with branch
wrangler pages deploy dist --branch main
```

#### Via Git Integration

1. Connect repository in Cloudflare Pages dashboard
2. Build command: `npm run build`
3. Dist directory: `dist`
4. Enable compatibility flags if needed

### Environment Variables

Add in Cloudflare Pages dashboard > Settings > Variables:

```bash
VITE_API_URL=https://api.example.com
DATABASE_URL=...
```

### Cloudflare-Specific Config

```js
// wrangler.toml
name = "solidstart-app"
compatibility_date = "2024-01-01"

[vars]
  VITE_API_URL = "https://api.example.com"
```

## Node.js Server Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "node-server" },
});
```

### Running the Server

```bash
# After build
npm run build

# Start server
node dist/server/index.js

# Or use PM2 for production
pm2 start dist/server/index.js --name solidstart-app
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production image
FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

EXPOSE 3000
CMD ["node", "dist/server/index.js"]
```

Build and run:

```bash
docker build -t solidstart-app .
docker run -p 3000:3000 solidstart-app
```

### PM2 Configuration

```json
// ecosystem.config.js
module.exports = {
  apps: [{
    name: "solidstart-app",
    script: "dist/server/index.js",
    instances: "max",
    exec_mode: "cluster",
    env: {
      NODE_ENV: "production",
      PORT: 3000,
    },
  }],
};
```

Run with PM2:

```bash
npm i -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Bun Runtime Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "bun-server" },
});
```

### Running with Bun

```bash
# Install Bun if not already installed
curl -fsSL https://bun.sh/install | bash

# Build and run
bun run build
bun dist/server/index.js
```

### Docker with Bun

```dockerfile
FROM oven/bun:1 AS builder

WORKDIR /app
COPY package*.json ./
RUN bun install
COPY . .
RUN bun run build

FROM oven/bun:1

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000
CMD ["bun", "dist/server/index.js"]
```

## Deno Runtime Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "deno-server" },
});
```

### Running with Deno

```bash
# Build first
npm run build

# Run with Deno
deno run --allow-net --allow-env --allow-read dist/server/index.js
```

## Railway Deployment

### Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: { preset: "node-server" },
});
```

### Setup

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

### Railway.toml

```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "node dist/server/index.js"
```

## Render Deployment

### Web Service Configuration

1. Create web service in Render dashboard
2. Build command: `npm run build`
3. Start command: `node dist/server/index.js`
4. Add environment variables

### render.yaml

```yaml
services:
  - type: web
    name: solidstart-app
    env: node
    buildCommand: npm install && npm run build
    startCommand: node dist/server/index.js
    envVars:
      - key: NODE_ENV
        value: production
```

## Static Export (SSG Only)

For static sites without SSR:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: false, // Disable SSR for static export
  server: {
    preset: "static",
    prerender: {
      crawl: true, // Crawl all links
      routes: ["/", "/about", "/contact"], // Or specify routes
    },
  },
});
```

Deploy the `dist` folder to any static host:
- GitHub Pages
- Netlify (static mode)
- Cloudflare Pages
- S3 + CloudFront

## Prerendering Configuration

Combine SSR with prerendered pages:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: true,
  server: {
    preset: "vercel",
    prerender: {
      // Auto-crawl starting from these routes
      entries: ["/"],
      
      // Specific routes to always prerender
      routes: ["/", "/about", "/pricing"],
      
      // Exclude dynamic routes
      exclude: ["/users/*", "/api/*"],
    },
  },
});
```

## Environment Variables by Platform

### Vercel

```bash
# In .env or Vercel dashboard
VITE_PUBLIC_API_URL=https://api.example.com  # Client (must start with VITE_)
DATABASE_URL=postgresql://...                # Server-only
SECRET_KEY=...                               # Server-only
```

### Netlify

```bash
# In netlify.toml or dashboard
[build.environment]
  VITE_PUBLIC_API_URL = "https://api.example.com"
  DATABASE_URL = "postgresql://..."
```

### Cloudflare

```bash
# In wrangler.toml or dashboard
[vars]
  VITE_PUBLIC_API_URL = "https://api.example.com"
  DATABASE_URL = "postgresql://..."
```

## Custom Domain Setup

### Vercel

1. Deploy project
2. Settings > Domains > Add custom domain
3. Update DNS records as instructed

### Netlify

1. Site settings > Domain management
2. Add custom domain
3. Configure DNS (Netlify DNS recommended)

### Cloudflare Pages

1. Custom pages > Custom domains
2. Add domain (auto-configured with Cloudflare DNS)

## CI/CD Examples

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
          
      - name: Deploy to Vercel
        uses: vercel/actions@v2
        with:
          token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  image: vercel/vercel:latest
  script:
    - vercel --prod
  only:
    - main
```

## Monitoring and Logging

### Vercel Logs

```bash
# View deployment logs
vercel logs

# Real-time logs
vercel logs --follow
```

### Netlify Logs

View in Netlify dashboard > Deploy > Click deployment > Logs

### Custom Logging

```tsx
// src/middleware/logging.ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: async (event) => {
    console.log(
      `${event.request.method} ${event.request.url} - ${new Date().toISOString()}`
    );
  },
});
```

## Troubleshooting

### Build Failures

- Check Node.js version matches `.nvmrc` or `package.json`
- Clear cache: `rm -rf node_modules .vercel dist`
- Reinstall: `npm ci`

### Runtime Errors

- Verify environment variables are set
- Check server logs for stack traces
- Ensure database connections are established

### Hydration Mismatches

- Use `onMount` for client-only operations
- Avoid `window`/`document` in server-rendered code
- Match server and client output exactly
