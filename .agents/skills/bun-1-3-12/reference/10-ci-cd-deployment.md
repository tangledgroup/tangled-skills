# CI/CD & Deployment

Complete guide for integrating Bun into CI/CD pipelines and deploying applications to various platforms including GitHub Actions, Docker, Vercel, Railway, Render, and more.

## GitHub Actions

### Basic Workflow

```yaml title=".github/workflows/test.yml"
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      - name: Install dependencies
        run: bun install --frozen
      
      - name: Run tests
        run: bun test
      
      - name: Build application
        run: bun build ./src/index.ts --outdir ./dist --minify
```

### With Coverage

```yaml
name: Test with Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      - run: bun install --frozen
      
      - name: Run tests with coverage
        run: bun test --coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### With Caching

```yaml
name: Test with Cache

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      - name: Cache Bun dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.bun/install/cache
            node_modules
          key: ${{ runner.os }}-bun-${{ hashFiles('**/bun.lockb') }}
          restore-keys: |
            ${{ runner.os }}-bun-
      
      - run: bun install --frozen
      
      - run: bun test
```

### Multi-OS Testing

```yaml
name: Test on Multiple OS

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      - run: bun install --frozen
      
      - run: bun test
```

## Docker Deployment

### Basic Dockerfile

```dockerfile title="Dockerfile"
# Use official Bun image
FROM oven/bun:1.3.12

# Set working directory
WORKDIR /app

# Copy package files first (for better caching)
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install --frozen

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Run application
CMD ["bun", "run", "server.ts"]
```

### Multi-Stage Build (Optimized)

```dockerfile
# Build stage
FROM oven/bun:1.3.12 AS builder

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install

COPY . .

# Build production bundle
RUN bun build ./src/index.ts --outdir ./dist --minify

# Production stage (smaller image)
FROM oven/bun:1.3.12-alpine

WORKDIR /app

# Copy only production dependencies
COPY package.json ./
RUN bun install --production --frozen

# Copy built application
COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["bun", "run", "dist/index.js"]
```

### Single Binary (Smallest Image)

```dockerfile
# Build stage - compile to binary
FROM oven/bun:1.3.12 AS builder

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install

COPY . .

# Compile TypeScript to native binary
RUN bun build ./server.ts --compile --outfile ./server-binary

# Runtime stage - ultra small
FROM scratch

# Copy the binary
COPY --from=builder /app/server-binary /server-binary

EXPOSE 3000

ENTRYPOINT ["/server-binary"]
```

### Docker Compose

```yaml title="docker-compose.yml"
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://db:5432/app
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Docker Best Practices

1. **Use multi-stage builds** to reduce image size
2. **Pin Bun version** for reproducibility
3. **Use --frozen flag** in CI for deterministic installs
4. **Layer caching**: Copy package.json first, then source
5. **Use alpine variant** for smaller production images

## Vercel Deployment

### vercel.json Configuration

```json title="vercel.json"
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "bun build ./src/index.tsx --outdir ./dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

### Serverless Functions

```json title="vercel.json"
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.ts",
      "use": "@vercel/bun"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    }
  ]
}
```

### Deployment Commands

```bash
# Install Vercel CLI
bun add -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Railway Deployment

### railway.toml Configuration

```toml title="railway.toml"
[build]
type = "bun"

[deploy]
startCommand = "bun run server.ts"
dockerfile = "Dockerfile"

[env]
NODE_ENV = "production"
```

### Deployment

```bash
# Install Railway CLI
bun add -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

## Render Deployment

### render.yaml

```yaml title="render.yaml"
services:
  - type: web
    name: my-app
    env: bun
    buildCommand: bun install && bun build ./src/index.ts --outdir ./dist
    startCommand: bun run dist/index.js
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
```

### Deployment

Push to GitHub and connect repository on Render dashboard.

## Netlify Deployment

### netlify.toml

```toml title="netlify.toml"
[build]
  command = "bun install && bun build ./src/index.tsx --outdir ./dist"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NETLIFY_USE_BUN = "true"
```

## Fly.io Deployment

### fly.toml

```toml title="fly.toml"
app = "my-app"
primary_region = "nyc"

[build]
  image = "oven/bun:1.3.12"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Deployment

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly login

# Launch
fly launch

# Deploy
fly deploy
```

## Cloud Run (Google Cloud)

### Dockerfile for Cloud Run

```dockerfile
FROM oven/bun:1.3.12

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --production --frozen

COPY . .

# Cloud Run requires listening on $PORT env var
EXPOSE $PORT

CMD ["sh", "-c", "bun run server.ts"]
```

### Deployment

```bash
# Build and deploy
gcloud run deploy my-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## AWS Deployment

### Lambda with Bun

```typescript title="index.ts"
export const handler = async (event: APIGatewayProxyEvent) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Hello from Bun!" }),
  };
};
```

### Deployment Package

```bash
# Install AWS Lambda Layer for Bun or use container image
bun build ./index.ts --compile --outfile ./bootstrap

# Package for deployment
zip function.zip bootstrap
aws lambda create-function \
  --function-name my-function \
  --runtime provided.al2 \
  --handler bootstrap \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --zip-file fileb://function.zip
```

### ECS/Fargate

Use the Docker deployment guide above with AWS ECS task definition.

## Azure Deployment

### azure.yaml (Azure Developer CLI)

```yaml title="azure.yaml"
name: bun-app
services:
  web:
    project: .
    language: ts
    host: containerapp
    docker:
      dockerfile: Dockerfile
    env:
      NODE_ENV: production
```

### Deployment

```bash
# Install Azure Developer CLI
npm install -g @azure/developer-cli

# Login
azd auth login

# Provision and deploy
azd up
```

## Database Migration

### PostgreSQL with Bun

```typescript title="migrate.ts"
import { Pool } from "pg";  // Or use native Bun SQLite for smaller apps

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function runMigration() {
  const client = await pool.connect();
  
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    console.log("Migration completed");
  } finally {
    client.release();
  }
}

runMigration();
```

### Using Bun's Built-in SQLite

```typescript title="migrate.ts"
const db = new Bun.SQLiteDatabase("./app.sqlite");

db.query(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`).run();

console.log("Migration completed");

db.close();
```

## Environment Variables

### Local Development (.env)

```bash title=".env"
NODE_ENV=development
DATABASE_URL=postgres://localhost:5432/dev
REDIS_URL=redis://localhost:6379
API_KEY=dev-key-123
```

### Production (CI/CD Secrets)

**GitHub Actions**:
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

**Docker**:
```bash
docker run -e DATABASE_URL=$DATABASE_URL -e API_KEY=$API_KEY my-app
```

## Monitoring & Logging

### Structured Logging

```typescript title="logger.ts"
function log(level: string, message: string, data?: Record<string, unknown>) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    ...data,
  }));
}

export const logger = {
  info: (msg: string, data?: Record<string, unknown>) => log("info", msg, data),
  error: (msg: string, data?: Record<string, unknown>) => log("error", msg, data),
  warn: (msg: string, data?: Record<string, unknown>) => log("warn", msg, data),
};
```

### Health Check Endpoint

```typescript title="server.ts"
Bun.serve({
  port: 3000,
  
  fetch(req) {
    const url = new URL(req.url);
    
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "healthy",
        uptime: process.uptime(),
        version: Bun.version,
      }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    
    // ... rest of your app
  },
});
```

### Metrics Endpoint (Prometheus)

```typescript title="metrics.ts"
let requestCount = 0;
let errorCount = 0;

function getMetrics() {
  return `
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total ${requestCount}

# HELP http_errors_total Total HTTP errors
# TYPE http_errors_total counter
http_errors_total ${errorCount}

# HELP process_uptime_seconds Process uptime in seconds
# TYPE process_uptime_seconds gauge
process_uptime_seconds ${process.uptime()}
  `;
}

export { getMetrics };
```

## Blue-Green Deployment

### Setup

```yaml title="docker-compose.yml"
version: '3.8'

services:
  app-blue:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DEPLOYMENT=blue

  app-green:
    build: .
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=production
      - DEPLOYMENT=green

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - app-blue
      - app-green
```

### Switch Deployment

Update nginx config to point to different backend:

```nginx title="nginx.conf"
upstream backend {
    server 127.0.0.1:3000;  # Blue
    # server 127.0.0.1:3001;  # Green (uncomment to switch)
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
    }
}
```

## Rollback Strategy

### Git-based Rollback

```yaml name=".github/workflows/rollback.yml"
on:
  workflow_dispatch:
    inputs:
      commit:
        description: 'Commit to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.commit }}
      
      - uses: oven-sh/setup-bun@v2
      
      - run: bun install --frozen
      
      - run: bun build ./src/index.ts --outdir ./dist
      
      # Deploy rollback version
      - name: Deploy
        run: |
          # Your deployment command here
          vercel --prod --confirm
```

## Best Practices

1. **Use `--frozen` flag** in CI for deterministic builds
2. **Cache dependencies** to speed up CI pipelines
3. **Pin Bun version** for reproducibility
4. **Run tests on multiple platforms** (Ubuntu, macOS, Windows)
5. **Use multi-stage Docker builds** for smaller images
6. **Implement health checks** for all deployments
7. **Set up monitoring and alerting**
8. **Keep .env files out of version control**
9. **Use secrets management** for sensitive data
10. **Test deployment process** regularly

## Troubleshooting

### CI Build Failures

**Issue**: `bun: command not found`

**Solution**: Ensure setup-bun action is included:
```yaml
- uses: oven-sh/setup-bun@v2
```

**Issue**: Dependency installation fails

**Solution**: Use `--frozen` flag and check lockfile:
```bash
bun install --frozen
```

### Docker Build Issues

**Issue**: Large image size

**Solution**: Use multi-stage build or compile to binary:
```bash
bun build ./server.ts --compile --outfile ./server-binary
```

**Issue**: Port binding errors

**Solution**: Use environment variable for port:
```typescript
const port = parseInt(process.env.PORT || "3000");
```

## Related Documentation

- [HTTP Server](references/06-http-server.md) - Server configuration
- [Data Storage](references/07-data-storage.md) - Database setup
- [Migration Guides](references/09-migration-guides.md) - Moving from other platforms
