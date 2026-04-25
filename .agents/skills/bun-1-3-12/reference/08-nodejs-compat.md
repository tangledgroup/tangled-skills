# Node.js Compatibility & Migration

Bun aims for complete Node.js compatibility while providing significant performance improvements. Most Node.js applications work with Bun without modification, but there are some differences and known issues to be aware of.

## Compatibility Overview

### Fully Compatible

These Node.js features work identically in Bun:

- **Core modules**: `fs`, `path`, `os`, `crypto`, `stream`, `buffer`, `events`, `util`
- **HTTP/HTTPS**: `http`, `https` (also supports native Web API)
- **Networking**: `net`, `dns`, `tls`
- **Child processes**: `child_process`
- **Zlib**: Compression/decompression
- **Query strings**: `querystring`
- **Assert**: `assert` module
- **Timers**: `setTimeout`, `setInterval`, `setImmediate`
- **Globals**: `process`, `require`, `module`, `__dirname`, `__filename`

### Mostly Compatible (Minor Differences)

These work but may have subtle differences:

- **Console**: `console` works, plus additional Bun-specific methods
- **Module resolution**: Same algorithm, plus Bun's extensions (.ts, .jsx, etc.)
- **Environment variables**: `process.env` works identically
- **Worker threads**: Supported with some API differences

### Limited Support

These have partial or no support:

- **Native addons**: Some C/C++ modules may not work
- **Node.js addons requiring rebuild**: May need recompilation
- **Some deprecated Node.js APIs**: Not implemented if deprecated in Node.js

## Running Node.js Code with Bun

### Direct Replacement

Most Node.js scripts run directly:

```bash
# Instead of
node app.js

# Use
bun run app.js
```

### Package.json Scripts

Update scripts in `package.json`:

```json title="package.json"
{
  "scripts": {
    // Before (Node.js)
    "start": "node index.js",
    "dev": "nodemon index.js",
    "build": "node build.js",
    "test": "jest"
    
    // After (Bun)
    "start": "bun run index.ts",
    "dev": "bun run --watch index.ts",
    "build": "bun run build.ts",
    "test": "bun test"
  }
}
```

### TypeScript Support

Node.js requires transpilation, Bun doesn't:

```bash
# Node.js workflow
tsc --build && node dist/index.js

# Bun workflow (no compilation needed)
bun run index.ts
```

## Module Import Differences

### ES Modules vs CommonJS

Both work in Bun:

```typescript
// ES modules (preferred)
import fs from "fs";
import { readFile } from "fs/promises";

// CommonJS (still supported)
const fs = require("fs");
const { readFile } = require("fs/promises");
```

### TypeScript File Extensions

Bun can import .ts files directly:

```typescript
// Works in Bun without transpilation
import { myFunction } from "./module.ts";
import Component from "./Component.tsx";

// Node.js would require compilation first
```

### Additional File Types

Bun supports more file types natively:

```typescript
// Import JSON (works in Node.js 18+)
import config from "./config.json";

// Import TOML (Bun-specific)
import settings from "settings.toml";

// Import YAML (Bun-specific)
import data from "./data.yaml";

// Import CSS (for bundling)
import styles from "./styles.css";

// Import binary files
import wasm from "./module.wasm";
```

## API Differences

### File System

Node.js:
```javascript
const fs = require("fs");
const content = fs.readFileSync("file.txt", "utf-8");
```

Bun (same API works):
```typescript
const fs = require("fs");
const content = fs.readFileSync("file.txt", "utf-8");

// Or use Bun's native API (faster)
const content2 = Bun.read("file.txt", "utf-8");
```

### HTTP Server

Node.js:
```javascript
const http = require("http");

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Hello, World!\n");
});

server.listen(3000);
```

Bun (Node.js API works):
```typescript
const http = require("http");

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Hello, World!\n");
});

server.listen(3000);
```

Bun (native Web API - faster):
```typescript
Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello, World!");
  },
});
```

### Environment Variables

Identical in both:

```typescript
// Works the same
const env = process.env.NODE_ENV;

// Bun also provides direct access
const env2 = env.NODE_ENV;
```

## Migration Steps

### 1. Install Bun

```bash
curl -fsSL https://bun.com/install | bash
```

### 2. Test Compatibility

Run existing tests with Bun:

```bash
# Backup current setup
cp package-lock.json package-lock.json.backup

# Remove node_modules and lockfiles
rm -rf node_modules package-lock.json yarn.lock pnpm-lock.yaml

# Install with Bun
bun install

# Run tests
bun test
```

### 3. Update Scripts

Modify `package.json` scripts:

```json
{
  "scripts": {
    "start": "bun run index.ts",
    "dev": "bun run --watch index.ts",
    "build": "bun build ./src/index.tsx --outdir ./dist",
    "test": "bun test"
  }
}
```

### 4. Replace Dependencies (Optional)

Some npm packages can be replaced with Bun's built-in APIs:

| npm Package | Bun Built-in | Notes |
|------------|--------------|-------|
| `better-sqlite3` | `Bun.SQLError` | Native SQLite |
| `ioredis` / `redis` | `Bun.Redis` | Native Redis client |
| `@aws-sdk/s3` | `Bun.S3Client` | Native S3 client |
| `nodemon` | `bun run --watch` | Built-in watch mode |
| `jest` | `bun test` | Built-in test runner |
| `esbuild` / `webpack` | `bun build` | Built-in bundler |
| `node-fetch` | `fetch` | Native fetch API |
| `yaml` | Native YAML import | `import data from "file.yaml"` |
| `toml` | Native TOML import | `import config from "config.toml"` |

### 5. Handle Incompatible Packages

If a package doesn't work:

1. **Check compatibility**: See if there's a Bun-compatible alternative
2. **Use Node.js resolver**: Run with `bun --node-resolver` flag
3. **File an issue**: Report on [Bun GitHub](https://github.com/oven-sh/bun/issues)
4. **Keep using npm package**: Most still work, just slower

## Known Issues & Workarounds

### Native Addons

Some native modules require rebuilding:

```bash
# Force rebuild with Bun's node-gyp equivalent
bun install --force
```

If a native module doesn't work:
- Check if there's a pure JavaScript alternative
- Use `--node-resolver` flag for better compatibility
- Report the issue to Bun maintainers

### Module Resolution Issues

```bash
# Use Node.js-style resolution
bun run --node-resolver index.ts

# Or configure in bunfig.toml
```

```toml title="bunfig.toml"
[install]
resolution = ["node", "bun"]
```

### TypeScript Path Aliases

Node.js requires `tsconfig-paths` for path aliases:

```json title="tsconfig.json"
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

In Node.js, you need additional setup. In Bun, it works automatically with `--bun` flag:

```bash
bun run --bun index.ts
```

### Stream Compatibility

Most streams work identically, but some edge cases may differ:

```typescript
// Prefer Web Streams API in Bun
const stream = req.body;  // ReadableStream

// Node.js streams still work
const fs = require("fs");
const readStream = fs.createReadStream("file.txt");
```

## Performance Comparisons

### Startup Time

| Application | Node.js | Bun | Improvement |
|------------|---------|-----|-------------|
| Simple script | 80ms | 2ms | 40x faster |
| Express server | 350ms | 15ms | 23x faster |
| Next.js app | 2s | 150ms | 13x faster |

### Package Installation

| Operation | npm | yarn | Bun | Fastest |
|-----------|-----|------|-----|---------|
| Fresh install | 45s | 38s | 1.5s | Bun (30x) |
| Incremental | 12s | 8s | 0.5s | Bun (24x) |

### Test Execution

| Tests | Jest | Bun test | Improvement |
|-------|------|----------|-------------|
| 100 tests | 8s | 0.8s | 10x faster |
| 1000 tests | 75s | 7s | 10x faster |

## CI/CD Integration

### GitHub Actions

```yaml title=".github/workflows/test.yml"
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      # Setup Bun
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      
      # Install dependencies
      - run: bun install
      
      # Run tests
      - run: bun test
      
      # Build application
      - run: bun build ./src/index.ts --outdir ./dist
```

### Docker

```dockerfile title="Dockerfile"
# Use official Bun image
FROM oven/bun:1.3.12

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install --frozen

# Copy source code
COPY . .

# Build application (optional)
RUN bun build ./src/index.ts --outdir ./dist --minify

# Expose port
EXPOSE 3000

# Run application
CMD ["bun", "run", "server.ts"]
```

### Alternative: Multi-stage Build

```dockerfile
FROM oven/bun:1.3.12 AS builder

WORKDIR /app
COPY package.json bun.lockb* ./
RUN bun install
COPY . .
RUN bun build ./src/index.ts --compile --outfile ./app

# Smaller runtime image
FROM oven/bun:1.3.12-alpine

WORKDIR /app
COPY --from=builder /app/app .

CMD ["./app"]
```

## Debugging Compatibility Issues

### Enable Debug Mode

```bash
# Verbose module resolution
BUN_DEBUG=module bun run index.ts

# All debug logs
BUN_DEBUG=1 bun run index.ts

# Print stack traces
BUN_PRINT_STACK_TRACES=1 bun run index.ts
```

### Compare Behavior

Run same code with both Node.js and Bun:

```bash
# Node.js
node --version
node index.js

# Bun
bun --version
bun run index.js

# Compare outputs
```

### Check Compatibility Status

Visit [Bun compatibility docs](https://bun.sh/docs/runtime/nodejs-compat) for the latest status.

## When to Stick with Node.js

Consider staying with Node.js if:

1. **Heavy native addon usage**: Your app relies on many C/C++ modules
2. **Enterprise support requirements**: Need long-term support contracts
3. **Specific Node.js features**: Using cutting-edge Node.js features not yet in Bun
4. **Team familiarity**: Team is deeply invested in Node.js tooling

## When to Migrate to Bun

Strong candidates for migration:

1. **TypeScript projects**: No compilation step needed
2. **Full-stack applications**: Built-in bundler + runtime
3. **Microservices**: Faster startup = better cold start performance
4. **CLI tools**: Smaller binaries, faster execution
5. **Testing-heavy projects**: 10x faster test execution

## Migration Checklist

- [ ] Install Bun and verify with `bun --version`
- [ ] Backup current lockfiles
- [ ] Run `bun install` to generate bun.lockb
- [ ] Update package.json scripts
- [ ] Run test suite: `bun test`
- [ ] Test application in development: `bun run --watch`
- [ ] Build production version: `bun build`
- [ ] Update CI/CD pipelines
- [ ] Monitor for any runtime issues
- [ ] Document any workarounds needed

## Getting Help

- [Bun Discord](https://bun.com/discord) - Active community support
- [GitHub Issues](https://github.com/oven-sh/bun/issues) - Bug reports
- [Compatibility Docs](https://bun.sh/docs/runtime/nodejs-compat) - Official compatibility guide
- [Migration Guide](references/09-migration-guides.md) - Detailed migration steps

## Related Documentation

- [Runtime Basics](references/01-runtime-basics.md) - Core runtime features
- [Package Manager](references/02-package-manager.md) - Migration from npm/yarn/pnpm
- [Bundler](references/03-bundler.md) - Migration from esbuild/Webpack
- [Test Runner](references/04-test-runner.md) - Migration from Jest
