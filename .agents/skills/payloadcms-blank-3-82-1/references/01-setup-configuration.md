# Setup and Configuration

Complete guide to environment configuration, dependencies, Docker setup, and development tools for the Payload CMS blank template v3.82.1.

## Environment Variables

### Required Variables

Create a `.env` file in the project root (never commit to version control):

```env
# MongoDB Connection String
# Local: mongodb://127.0.0.1/your-database-name
# Docker: mongodb://mongo/your-database-name (when using docker-compose)
# Atlas: mongodb+srv://username:password@cluster.mongodb.net/database-name
DATABASE_URL=mongodb://127.0.0.1/payload

# Payload Secret Key (minimum 32 characters)
# Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
PAYLOAD_SECRET=your-secret-key-minimum-32-chars
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

### Optional Variables

```env
# Node.js environment (default: development)
NODE_ENV=development

# Next.js port (default: 3000)
PORT=3000

# MongoDB replica set (required for transactions)
# MONGODB_REPLICA_SET=rs0

# Payload public URL (for email links, previews)
PAYLOAD_PUBLIC_URL=http://localhost:3000

# Logging level (debug, info, warn, error)
LOG_LEVEL=info
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

**pnpm configuration:**
```json
{
  "pnpm": {
    "onlyBuiltDependencies": [
      "sharp",
      "esbuild",
      "unrs-resolver"
    ]
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

Note: Lockfile must match package manager (pnpm-lock.yaml for pnpm, package-lock.json for npm, yarn.lock for yarn).

## Dependencies

### Production Dependencies

```json
{
  "@payloadcms/db-mongodb": "workspace:*",
  "@payloadcms/next": "workspace:*",
  "@payloadcms/richtext-lexical": "workspace:*",
  "@payloadcms/ui": "workspace:*",
  "cross-env": "^7.0.3",
  "dotenv": "16.4.7",
  "graphql": "^16.8.1",
  "next": "16.2.2",
  "payload": "workspace:*",
  "react": "19.2.4",
  "react-dom": "19.2.4",
  "sharp": "0.34.2"
}
```

**Key Packages:**

- **@payloadcms/db-mongodb**: MongoDB database adapter for Payload
- **@payloadcms/next**: Next.js integration bundle (routes, views, config)
- **@payloadcms/richtext-lexical**: Lexical rich text editor integration
- **@payloadcms/ui**: Admin panel UI components and hooks
- **next**: React framework for web applications (App Router)
- **sharp**: Image processing and optimization library
- **dotenv**: Environment variable loading from .env file

### Development Dependencies

```json
{
  "@playwright/test": "1.58.2",
  "@testing-library/react": "16.3.0",
  "@types/node": "22.19.9",
  "@types/react": "19.2.14",
  "@types/react-dom": "19.2.3",
  "@vitejs/plugin-react": "4.5.2",
  "eslint": "^9.16.0",
  "eslint-config-next": "16.2.2",
  "jsdom": "28.0.0",
  "prettier": "^3.4.2",
  "tsx": "4.21.0",
  "typescript": "5.7.3",
  "vite-tsconfig-paths": "6.0.5",
  "vitest": "4.0.18"
}
```

**Key Packages:**

- **@playwright/test**: E2E testing framework for browser automation
- **vitest**: Unit and integration testing with Vite
- **jsdom**: JavaScript DOM implementation for testing
- **typescript**: Type safety and compilation
- **eslint + eslint-config-next**: Code linting with Next.js rules
- **tsx**: TypeScript execution for Node.js scripts

## npm Scripts

Available commands in `package.json`:

```json
{
  "scripts": {
    // Development
    "dev": "cross-env NODE_OPTIONS=--no-deprecation next dev",
    "devsafe": "rm -rf .next && cross-env NODE_OPTIONS=--no-deprecation next dev",
    
    // Production
    "build": "cross-env NODE_OPTIONS=\"--no-deprecation --max-old-space-size=8000\" next build",
    "start": "cross-env NODE_OPTIONS=--no-deprecation next start",
    
    // Payload CLI
    "payload": "cross-env NODE_OPTIONS=--no-deprecation payload",
    "generate:types": "cross-env NODE_OPTIONS=--no-deprecation payload generate:types",
    "generate:importmap": "cross-env NODE_OPTIONS=--no-deprecation payload generate:importmap",
    
    // Quality
    "lint": "cross-env NODE_OPTIONS=--no-deprecation eslint .",
    
    // Testing
    "test": "pnpm run test:int && pnpm run test:e2e",
    "test:int": "cross-env NODE_OPTIONS=--no-deprecation vitest run --config ./vitest.config.mts",
    "test:e2e": "cross-env NODE_OPTIONS=\"--no-deprecation --import=tsx/esm\" playwright test --config=playwright.config.ts"
  }
}
```

### Script Usage

**Development:**
```bash
# Start development server (port 3000)
pnpm dev

# Clean start (removes .next cache)
pnpm devsafe
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
# Build for production
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
```

## Docker Development Setup

### docker-compose.yml Configuration

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

### Docker Service Details

**Payload Service:**
- Uses Node.js 20 Alpine image for small footprint
- Mounts project directory to `/home/node/app`
- Separate volume for `node_modules` (performance optimization)
- Enables corepack and pnpm automatically
- Depends on MongoDB service being ready first
- Uses `.env` file for environment variables

**MongoDB Service:**
- Official MongoDB latest image
- WiredTiger storage engine (default, recommended)
- Persistent volume for data (`data:`)
- Port 27017 exposed for direct access
- Logging disabled to reduce noise

### Docker Usage

**Start Development Environment:**
```bash
# Start all services in foreground
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

**Environment Configuration for Docker:**

Update `.env` file:
```env
# Use 'mongo' as hostname (Docker service name)
DATABASE_URL=mongodb://mongo/your-database-name
PAYLOAD_SECRET=your-secret-key
```

### Docker Benefits

1. **Consistent Environment**: Same setup across all developers
2. **No Local MongoDB**: No need to install MongoDB locally
3. **Quick Setup**: One command to start entire stack
4. **Isolated**: Doesn't conflict with local services
5. **Easy Cleanup**: `docker-compose down` removes everything

### Docker Limitations

1. **Volume Mounts**: File changes sync to container (may be slow on large projects)
2. **node_modules Volume**: Can cause permission issues on some systems
3. **Performance**: Slightly slower than native development
4. **Debugging**: More complex than local Node.js debugging

### Troubleshooting Docker

**"Permission denied" errors:**
```bash
# Fix volume permissions
docker-compose run --rm payload chown -R node:node /home/node/app
```

**MongoDB connection refused:**
- Wait for MongoDB to be ready (check logs: `docker-compose logs mongo`)
- Verify `DATABASE_URL` uses `mongo` as hostname
- Check MongoDB is running: `docker-compose ps`

**Port already in use:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## Next.js Configuration

### next.config.ts

```typescript
import { withPayload } from '@payloadcms/next/withPayload'
import type { NextConfig } from 'next'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(__filename)

const nextConfig: NextConfig = {
  images: {
    localPatterns: [
      {
        pathname: '/api/media/file/**',
      },
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
  turbopack: {
    root: path.resolve(dirname),
  },
}

export default withPayload(nextConfig, { devBundleServerPackages: false })
```

### Configuration Details

**images.localPatterns:**
- Allows Next.js Image optimization for Payload media files
- Pattern matches uploaded files served from `/api/media/file/**`
- Required for `<Image>` components to work with uploaded media

**webpack.extensionAlias:**
- Resolves TypeScript extensions correctly
- `.js` imports can resolve to `.ts` or `.tsx` files
- `.mjs` imports can resolve to `.mts` files
- Prevents import errors in development

**turbopack.root:**
- Configures Turbopack (Next.js fast bundler) root directory
- Required for ES module path resolution

**withPayload wrapper:**
- Integrates Payload with Next.js configuration
- `devBundleServerPackages: false` optimizes build size
- Adds Payload-specific webpack and Vite configurations

### Alternative: Standalone Output for Docker

For production Docker builds, add standalone output:

```typescript
const nextConfig: NextConfig = {
  output: 'standalone', // Add this for Docker production
  images: { /* ... */ },
  webpack: { /* ... */ },
}
```

This creates minimal `.next/standalone` directory for Docker COPY.

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
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

### Configuration Details

**baseUrl**: Root directory for path resolution

**lib**: TypeScript library definitions (DOM, ES2022)

**strict**: Enables all strict type-checking options

**noEmit**: Don't emit JavaScript (Next.js handles compilation)

**moduleResolution: "bundler"**: Modern resolution for ES modules

**jsx: "react-jsx"**: Automatic JSX transformation (React 17+)

**paths**: Import path aliases
- `@/*` → `./src/*` (e.g., `import { Users } from '@/collections/Users'`)
- `@payload-config` → `./src/payload.config.ts` (Payload config import)

**plugins**: Next.js TypeScript plugin for page routing

### Using Path Aliases

```typescript
// Instead of:
import { Users } from '../../collections/Users'
import config from '../../payload.config'

// Use:
import { Users } from '@/collections/Users'
import config from '@payload-config'
```

Path aliases work in both TypeScript and JavaScript files.

## ESLint Configuration

### eslint.config.mjs

```javascript
import { dirname } from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname,
})

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/ban-ts-comment': 'warn',
      '@typescript-eslint/no-empty-object-type': 'warn',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          vars: 'all',
          args: 'after-used',
          ignoreRestSiblings: false,
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          destructuredArrayIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^(_|ignore)',
        },
      ],
    },
  },
  {
    ignores: ['.next/', 'src/payload-types.ts', 'src/payload-generated-schema.ts'],
  },
]

export default eslintConfig
```

### ESLint Rules

- **ban-ts-comment**: Warn on `@ts-ignore` and `@ts-expect-error`
- **no-empty-object-type**: Warn on empty object types `{}`
- **no-explicit-any**: Warn on explicit `any` types
- **no-unused-vars**: Warn on unused variables (ignore prefixed with `_`)

### Ignored Files

- `.next/`: Build output directory
- `src/payload-types.ts`: Auto-generated types
- `src/payload-generated-schema.ts`: Auto-generated schema

## Testing Configuration

### Vitest Configuration (vitest.config.mts)

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['tests/int/**/*.int.spec.ts'],
  },
})
```

**Configuration Details:**
- **jsdom**: Browser-like environment for DOM testing
- **tsconfigPaths**: Resolves TypeScript path aliases in tests
- **react plugin**: JSX transformation for React component tests
- **include pattern**: Only runs `*.int.spec.ts` files in `tests/int/`

### Playwright Configuration (playwright.config.ts)

```typescript
import { defineConfig, devices } from '@playwright/test'
import 'dotenv/config'

export default defineConfig({
  testDir: './tests/e2e',
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], channel: 'chromium' },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    reuseExistingServer: true,
    url: 'http://localhost:3000',
  },
})
```

**Configuration Details:**
- **testDir**: E2E test location
- **forbidOnly**: Fail CI if `test.only` is left in code
- **retries**: Retry failed tests twice in CI
- **workers**: Single worker in CI for stability
- **reporter**: HTML report for easy viewing
- **trace**: Record trace on first retry for debugging
- **webServer**: Auto-starts dev server before tests

See [Testing Setup](07-testing.md) for detailed testing patterns and examples.
