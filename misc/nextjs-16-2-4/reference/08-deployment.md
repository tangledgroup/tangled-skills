# Deployment

## Node.js Server

Build and run as a Node.js server — supports all Next.js features:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

```bash
npm run build   # Build the application
npm start       # Start the production server
```

Deploy to any Node.js provider: Railway, Render, DigitalOcean, Fly.io, Google Cloud Run, and more.

## Docker

### Standalone Output

Generate a minimal production-ready image with only required runtime files:

```ts
// next.config.ts
const nextConfig = {
  output: 'standalone',
}
```

```dockerfile
FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat
WORKDIR /app

FROM base AS build
COPY . .
RUN npm ci && npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

### Static Export

For fully static sites:

```ts
// next.config.ts
const nextConfig = {
  output: 'export',
}
```

This generates HTML files that can be served from any static hosting (S3, GitHub Pages, Nginx). Note: static export does not support server-side features like Route Handlers, Server Components with dynamic data, or middleware.

## Vercel

The easiest deployment — push to Git and Vercel auto-detects Next.js:

```bash
npx vercel
```

Vercel supports all Next.js features including Image Optimization, Middleware/Proxy, and Edge Functions.

## Adapters

Next.js supports deployment adapters for custom platforms via the `adapterPath` config:

```ts
// next.config.ts
const nextConfig = {
  adapterPath: '@your-platform/nextjs-adapter',
}
```

### Verified Adapters

Verified adapters run the full Next.js compatibility test suite:

- Vercel
- Bun

Cloudflare and Netlify are working on verified adapters. Other platforms (Appwrite, AWS Amplify, Deno Deploy, Firebase, etc.) offer their own integrations.

## Build Configuration

### Environment Variables

Production environment variables should be configured on your hosting platform or in `.env.production`:

```bash
# .env.production
DATABASE_URL=postgresql://prod-user:password@prod-host/db
NEXT_PUBLIC_API_URL=https://api.production.example.com
```

### TypeScript and ESLint

Next.js reports TypeScript errors and ESLint warnings during builds by default. Configure in `next.config.ts`:

```ts
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,  // Opt out of TypeScript error checking during build
  },
  eslint: {
    ignoreDuringBuilds: true,  // Opt out of ESLint during build
  },
}
```

### Turbopack

Turbopack is a Rust-based incremental bundler built into Next.js. Enable for development:

```bash
next dev --turbopack
```

Or configure in `next.config.ts`:

```ts
const nextConfig = {
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
}
```

## Self-Hosting

For self-hosted deployments, consider:

- Using a reverse proxy (Nginx, Caddy) in front of the Next.js server
- Configuring proper SSL/TLS termination
- Setting up health checks and process management (PM2, systemd)
- Monitoring memory usage and setting appropriate limits
- Using Docker for consistent environments across deployments

## Continuous Deployment

Recommended CI/CD workflow:

1. Push code to Git repository
2. CI pipeline runs `npm run build` to verify the build succeeds
3. Run tests (`npm test`)
4. Deploy to staging environment
5. Run integration tests against staging
6. Deploy to production on approval

## next.config.ts Reference

Key configuration options:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Build output
  output: 'standalone',       // 'standalone' | 'export' | undefined (default)

  // Caching
  cacheComponents: true,      // Enable Cache Components model

  // Images
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'example.com' },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Rewrites and redirects
  async rewrites() {
    return [
      { source: '/old-path', destination: '/new-path' },
    ]
  },
  async redirects() {
    return [
      { source: '/legacy', destination: '/', permanent: true },
    ]
  },

  // Headers
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
        ],
      },
    ]
  },

  // Internationalization
  i18n: {
    locales: ['en', 'fr', 'de'],
    defaultLocale: 'en',
  },

  // Webpack customization
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = { fs: false }
    }
    return config
  },

  // Transpile packages
  transpilePackages: ['@my-org/shared-package'],

  // Trailing slash
  trailingSlash: false,

  // Base path for subdirectory deployment
  basePath: '/app',

  // Asset prefix for CDN
  assetPrefix: 'https://cdn.example.com',
}

export default nextConfig
```
