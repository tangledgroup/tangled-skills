# Setup and Configuration

Complete guide to environment configuration, dependencies, plugins, and development tools for the Payload CMS website template v3.82.1.

## Environment Variables

### Required Variables

Create a `.env` file in the project root (never commit to version control):

```env
# MongoDB Connection String
# Local: mongodb://127.0.0.1/your-database-name
# Docker: mongodb://mongo/your-database-name
# Atlas: mongodb+srv://username:password@cluster.mongodb.net/database-name
DATABASE_URL=mongodb://127.0.0.1/payload-website

# Payload Secret Key (minimum 32 characters)
# Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
PAYLOAD_SECRET=your-secret-key-minimum-32-chars

# Cron Secret for scheduled tasks and background jobs
# Generate a random string for authenticating cron endpoints
CRON_SECRET=your-cron-job-secret-random-string

# Payload Public URL (required for live preview, draft preview, email links)
PAYLOAD_PUBLIC_URL=http://localhost:3000
```

### Variable Details

**DATABASE_URL**
- **Purpose**: MongoDB connection string for database connectivity
- **Format**: Standard MongoDB URI format
- **Local Development**: `mongodb://127.0.0.1/your-database-name`
- **Docker Compose**: `mongodb://mongo/your-database-name` (service name as hostname)
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/database-name`
- **Required for**: All database operations, application startup

**PAYLOAD_SECRET**
- **Purpose**: Session encryption, JWT signing, cookie encryption
- **Minimum Length**: 32 characters (64+ recommended)
- **Generation Methods**:
  ```bash
  # Node.js
  node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
  
  # OpenSSL
  openssl rand -hex 64
  
  # Python
  python3 -c "import secrets; print(secrets.token_hex(64))"
  ```
- **Security**: Never commit to version control, rotate periodically in production
- **Required for**: Application security, authentication

**CRON_SECRET**
- **Purpose**: Authentication for scheduled tasks and background jobs
- **Usage**: Passed as Bearer token in Authorization header for cron endpoints
- **Example**: `curl -H "Authorization: Bearer $CRON_SECRET" https://your-site.com/api/jobs/process`
- **Required for**: Scheduled publishing, background job execution

**PAYLOAD_PUBLIC_URL**
- **Purpose**: Base URL for live preview, draft preview links, email notifications
- **Development**: `http://localhost:3000`
- **Production**: `https://your-domain.com`
- **Required for**: Live preview functionality, draft preview sharing, form notifications

### Optional Variables

```env
# Node.js environment (default: development)
NODE_ENV=development

# Next.js port (default: 3000)
PORT=3000

# Payload public URL for production
PAYLOAD_PUBLIC_URL=https://your-domain.com

# Logging level (debug, info, warn, error)
LOG_LEVEL=info

# Email service configuration (for form submissions)
# See Form Builder documentation for email setup
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=your-sendgrid-api-key
```

## Package Manager Configuration

### pnpm (Recommended)

The template uses pnpm 9+ or 10+. Enable with corepack:

```bash
# Enable corepack (Node.js 16.10+)
corepack enable

# Prepare pnpm latest
corepack prepare pnpm@latest --activate

# Install dependencies
pnpm install
```

**package.json engines field:**
```json
{
  "engines": {
    "node": "^18.20.2 || >=20.9.0",
    "pnpm": "^9 || ^10"
  }
}
```

### Alternative Package Managers

While pnpm is recommended, the template works with npm or yarn:

```bash
# npm
npm install
npm run dev

# yarn
yarn install
yarn dev
```

## Dependencies

### Production Dependencies

```json
{
  "@payloadcms/admin-bar": "workspace:*",
  "@payloadcms/db-mongodb": "workspace:*",
  "@payloadcms/live-preview-react": "workspace:*",
  "@payloadcms/next": "workspace:*",
  "@payloadcms/plugin-form-builder": "workspace:*",
  "@payloadcms/plugin-nested-docs": "workspace:*",
  "@payloadcms/plugin-redirects": "workspace:*",
  "@payloadcms/plugin-search": "workspace:*",
  "@payloadcms/plugin-seo": "workspace:*",
  "@payloadcms/richtext-lexical": "workspace:*",
  "@payloadcms/ui": "workspace:*",
  "@radix-ui/react-checkbox": "^1.0.4",
  "@radix-ui/react-label": "^2.0.2",
  "@radix-ui/react-select": "^2.0.0",
  "@radix-ui/react-slot": "^1.0.2",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.1.1",
  "cross-env": "^7.0.3",
  "dotenv": "16.4.7",
  "geist": "^1.3.0",
  "graphql": "^16.8.2",
  "lucide-react": "0.563.0",
  "next": "16.2.2",
  "next-sitemap": "^4.2.3",
  "payload": "workspace:*",
  "prism-react-renderer": "^2.3.1",
  "react": "19.2.4",
  "react-dom": "19.2.4",
  "react-hook-form": "7.71.1",
  "sharp": "0.34.2",
  "tailwind-merge": "^3.4.0"
}
```

**Key Packages:**

- **@payloadcms/admin-bar**: Admin control bar for logged-in users on frontend
- **@payloadcms/live-preview-react**: Live preview functionality for drafts
- **@payloadcms/plugin-form-builder**: Drag-and-drop form builder
- **@payloadcms/plugin-nested-docs**: Hierarchical document structure (categories)
- **@payloadcms/plugin-redirects**: URL redirect management
- **@payloadcms/plugin-search**: Full-text search functionality
- **@payloadcms/plugin-seo**: SEO metadata and sitemap generation
- **@radix-ui/**: Headless UI components for accessible primitives
- **next-sitemap**: Automatic XML sitemap generation
- **prism-react-renderer**: Syntax highlighting for code blocks
- **react-hook-form**: Form management and validation

### Development Dependencies

```json
{
  "@eslint/eslintrc": "^3.2.0",
  "@playwright/test": "1.58.2",
  "@tailwindcss/postcss": "^4.1.18",
  "@tailwindcss/typography": "^0.5.19",
  "@testing-library/react": "16.3.0",
  "@types/node": "22.19.9",
  "@types/react": "19.2.14",
  "@types/react-dom": "19.2.3",
  "@vitejs/plugin-react": "4.5.2",
  "autoprefixer": "^10.4.19",
  "eslint": "^9.16.0",
  "eslint-config-next": "16.2.2",
  "jsdom": "28.0.0",
  "postcss": "^8.4.38",
  "prettier": "^3.4.2",
  "tailwindcss": "^4.1.18",
  "tsx": "4.21.0",
  "tw-animate-css": "^1.4.0",
  "typescript": "5.7.3",
  "vite-tsconfig-paths": "6.0.5",
  "vitest": "4.0.18"
}
```

**Key Packages:**

- **@tailwindcss/postcss**: Tailwind CSS PostCSS plugin
- **@tailwindcss/typography**: Beautiful prose typography for rich text
- **@playwright/test**: E2E testing framework
- **autoprefixer**: Automatically adds vendor prefixes to CSS
- **tw-animate-css**: Animation utilities for Tailwind CSS
- **vitest**: Unit and integration testing with Vite

## npm Scripts

Available commands in `package.json`:

```json
{
  "scripts": {
    // Development
    "dev": "cross-env NODE_OPTIONS=--no-deprecation next dev",
    "dev:prod": "cross-env NODE_OPTIONS=--no-deprecation rm -rf .next && pnpm build && pnpm start",
    
    // Production
    "build": "cross-env NODE_OPTIONS=--no-deprecation next build",
    "postbuild": "next-sitemap --config next-sitemap.config.cjs",
    "start": "cross-env NODE_OPTIONS=--no-deprecation next start",
    
    // Payload CLI
    "payload": "cross-env NODE_OPTIONS=--no-deprecation payload",
    "generate:types": "cross-env NODE_OPTIONS=--no-deprecation payload generate:types",
    "generate:importmap": "cross-env NODE_OPTIONS=--no-deprecation payload generate:importmap",
    
    // Quality
    "lint": "cross-env NODE_OPTIONS=--no-deprecation eslint .",
    "lint:fix": "cross-env NODE_OPTIONS=--no-deprecation eslint . --fix",
    
    // Testing
    "test": "pnpm run test:int && pnpm run test:e2e",
    "test:int": "cross-env NODE_OPTIONS=--no-deprecation vitest run --config ./vitest.config.mts",
    "test:e2e": "cross-env NODE_OPTIONS=\"--no-deprecation --import=tsx/esm\" playwright test --config=playwright.config.ts",
    
    // Maintenance
    "ii": "cross-env NODE_OPTIONS=--no-deprecation pnpm --ignore-workspace install",
    "reinstall": "cross-env NODE_OPTIONS=--no-deprecation rm -rf node_modules && rm pnpm-lock.yaml && pnpm --ignore-workspace install"
  }
}
```

### Script Usage

**Development:**
```bash
# Start development server (port 3000)
pnpm dev

# Clean production build and start (testing production build locally)
pnpm dev:prod
```

**Type Generation:**
```bash
# Generate TypeScript types from schema
pnpm generate:types

# Regenerate component import map
pnpm generate:importmap
```

**Production:**
```bash
# Build for production (includes sitemap generation)
pnpm build

# Start production server
pnpm start
```

**Testing:**
```bash
# Run all tests
pnpm test

# Integration tests only
pnpm test:int

# E2E tests only
pnpm test:e2e
```

**Quality:**
```bash
# Lint code
pnpm lint

# Auto-fix linting issues
pnpm lint:fix
```

## Payload Configuration

### Main Config (src/payload.config.ts)

```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import sharp from 'sharp'
import { buildConfig, PayloadRequest } from 'payload'

export default buildConfig({
  admin: {
    components: {
      beforeLogin: ['@/components/BeforeLogin'],
      beforeDashboard: ['@/components/BeforeDashboard'],
    },
    importMap: {
      baseDir: path.resolve(dirname),
    },
    user: Users.slug,
    livePreview: {
      breakpoints: [
        { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
        { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
        { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
      ],
    },
  },
  editor: defaultLexical,
  db: mongooseAdapter({ url: process.env.DATABASE_URL }),
  collections: [Pages, Posts, Media, Categories, Users],
  globals: [Header, Footer],
  plugins, // SEO, Search, Redirects, Forms, Nested Docs
  secret: process.env.PAYLOAD_SECRET,
  sharp,
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  jobs: {
    access: {
      run: ({ req }: { req: PayloadRequest }): boolean => {
        if (req.user) return true
        const secret = process.env.CRON_SECRET
        if (!secret) return false
        const authHeader = req.headers.get('authorization')
        return authHeader === `Bearer ${secret}`
      },
    },
    tasks: [],
  },
})
```

**Configuration Details:**

**admin.livePreview.breakpoints**: Defines responsive breakpoints for live preview
- Mobile: 375x667 (iPhone SE)
- Tablet: 768x1024 (iPad)
- Desktop: 1440x900 (Laptop)

**jobs.access**: Authentication for background jobs and scheduled tasks
- Requires logged-in user OR valid CRON_SECRET in Authorization header
- Used for scheduled publishing and automated tasks

### Plugins Configuration (src/plugins/index.ts)

The template configures 5 major plugins:

1. **Redirects Plugin**: URL redirect management
2. **Nested Docs Plugin**: Hierarchical categories
3. **SEO Plugin**: Meta tags, sitemaps, Open Graph
4. **Form Builder Plugin**: Drag-and-drop forms
5. **Search Plugin**: Full-text search indexing

See individual plugin references for detailed configuration.

## Next.js Configuration

### next.config.ts

```typescript
import { withPayload } from '@payloadcms/next/withPayload'
import type { NextConfig } from 'next'
import redirects from './redirects'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        hostname: 'images.unsplash.com',
        protocol: 'https',
      },
    ],
  },
  redirects, // Custom redirect configuration
  webpack: (webpackConfig) => {
    webpackConfig.resolve.extensionAlias = {
      '.cjs': ['.cts', '.cjs'],
      '.js': ['.ts', '.tsx', '.js', '.jsx'],
      '.mjs': ['.mts', '.mjs'],
    }
    return webpackConfig
  },
}

export default withPayload(nextConfig)
```

**Configuration Details:**

**images.remotePatterns**: Allows Next.js Image optimization for external domains
- Currently configured for Unsplash images
- Add additional patterns for other image CDNs

**redirects**: Custom Next.js redirects (separate from Payload redirects plugin)
- Defined in `redirects.ts` file
- Applied at the Next.js level before routing

### Sitemap Configuration (next-sitemap.config.cjs)

```javascript
const path = require('path')

module.exports = {
  siteUrl: process.env.PAYLOAD_PUBLIC_URL || 'https://payloadcms.com',
  generateRobotsTxt: true,
  transform: async (config, data) => {
    if (data.path === '/') {
      data.priority = 1
      data.changefreq = 'weekly'
    }
    return data
  },
  exclude: [
    '/api/*',
    '/admin/*',
    '/app/(payload)/*',
    '/next/seed',
    '/next/preview',
    '/next/exit-preview',
  ],
}
```

**Features:**
- Automatic sitemap generation for pages and posts
- Generates `robots.txt` file
- Custom priority and changefreq for homepage
- Excludes admin and API routes from indexing

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {
      "@/*": ["./src/*"],
      "@payload-config": ["./src/payload.config.ts"]
    },
    "target": "ES2022"
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

**Path Aliases:**
- `@/*` → `./src/*` (e.g., `import { Pages } from '@/collections/Pages'`)
- `@payload-config` → `./src/payload.config.ts`

See [Project Structure](02-project-structure.md) for detailed path alias usage.

## Docker Development Setup

### docker-compose.yml

```yaml
version: '3'

services:
  payload:
    build: .
    ports:
      - '3000:3000'
    volumes:
      - .:/home/node/app
      - node_modules:/home/node/app/node_modules
    working_dir: /home/node/app/
    command: pnpm dev
    depends_on:
      - mongo
    env_file:
      - .env

  mongo:
    image: mongo:latest
    ports:
      - '27017:27017'
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
  node_modules:
```

**Start Docker development:**
```bash
docker-compose up --build
```

Update `.env` to use `DATABASE_URL=mongodb://mongo/your-database-name`.

## Seed Demo Content

The template includes a seed endpoint for populating demo content:

**Visit**: http://localhost:3000/next/seed

**Creates:**
- Sample pages (Home, About, Contact)
- Demo blog posts with various layouts
- Category hierarchy
- Sample media files
- Header and footer navigation

**Usage:**
- Development: Use to test layouts and features
- Production: Optional, can create custom content from scratch

See [Project Setup](02-project-structure.md#seed-endpoint) for seed script details.
