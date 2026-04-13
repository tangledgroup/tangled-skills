# Migration Guides

Detailed guides for migrating from npm/yarn/pnpm, Webpack/esbuild, Jest, and other tools to Bun's integrated toolkit.

## Migrating from npm

### Command Mapping

| npm | Bun | Notes |
|-----|-----|-------|
| `npm init` | `bun init` | Creates package.json |
| `npm install` | `bun install` | Install dependencies |
| `npm install <pkg>` | `bun add <pkg>` | Add dependency |
| `npm install -D <pkg>` | `bun add -D <pkg>` | Add dev dependency |
| `npm uninstall <pkg>` | `bun remove <pkg>` | Remove dependency |
| `npm update` | `bun update` | Update dependencies |
| `npm outdated` | `bun outdated` | Check outdated packages |
| `npm run <script>` | `bun run <script>` | Run script |
| `npx <pkg>` | `bunx <pkg>` | Execute package |
| `npm publish` | `bun publish` | Publish package |
| `npm audit` | `bun audit` | Security audit |

### Migration Steps

1. **Install Bun**
   ```bash
   curl -fsSL https://bun.com/install | bash
   ```

2. **Backup and Replace Lockfile**
   ```bash
   cp package-lock.json package-lock.json.backup
   rm -rf node_modules package-lock.json
   bun install
   ```

3. **Update Scripts**
   ```json title="package.json"
   {
     "scripts": {
       "start": "bun run index.js",  # was: "node index.js"
       "dev": "bun run --watch index.js",  # was: "nodemon index.js"
       "test": "bun test"  # was: "jest" or "mocha"
     }
   }
   ```

4. **Verify Installation**
   ```bash
   bun install  # Should complete much faster
   bun run test  # Run your tests
   ```

### Workspaces

npm workspaces → Bun workspaces (identical):

```json title="package.json"
{
  "name": "monorepo",
  "private": true,
  "workspaces": [
    "packages/*"
  ]
}
```

No changes needed - Bun uses the same format.

## Migrating from yarn

### Command Mapping

| yarn | Bun | Notes |
|------|-----|-------|
| `yarn` | `bun install` | Install dependencies |
| `yarn add <pkg>` | `bun add <pkg>` | Add dependency |
| `yarn add -D <pkg>` | `bun add -D <pkg>` | Add dev dependency |
| `yarn remove <pkg>` | `bun remove <pkg>` | Remove dependency |
| `yarn upgrade` | `bun update` | Update dependencies |
| `yarn upgrade <pkg>` | `bun update <pkg>` | Update specific package |
| `yarn run <script>` | `bun run <script>` | Run script |
| `yarn <script>` | `bun <script>` | Run script (shorthand) |
| `yarn global add <pkg>` | `bun add -g <pkg>` | Global install |
| `yarn exec <pkg>` | `bunx <pkg>` | Execute package |
| `yarn publish` | `bun publish` | Publish package |

### Yarn Specific Features

**Yarn Resolutions**:
```json title="package.json"
{
  "resolutions": {
    "lodash": "4.17.21"
  }
}
```

→ Bun supports the same format automatically.

**Yarn Workspaces**:
```bash
# Yarn
yarn workspace app-a add lodash

# Bun
bun add -w app-a lodash
```

**Yarn Zero Config**:
Bun works similarly - no config file needed for basic operations.

### Migration Steps

1. **Remove yarn.lock**
   ```bash
   rm -rf node_modules yarn.lock
   ```

2. **Install with Bun**
   ```bash
   bun install
   ```

3. **Update package.json scripts**
   ```json
   {
     "scripts": {
       "dev": "bun run --watch src/index.tsx",  # was: "react-scripts start"
       "build": "bun build ./src --outdir ./dist"  # was: "react-scripts build"
     }
   }
   ```

## Migrating from pnpm

### Command Mapping

| pnpm | Bun | Notes |
|------|-----|-------|
| `pnpm install` | `bun install` | Install dependencies |
| `pnpm add <pkg>` | `bun add <pkg>` | Add dependency |
| `pnpm add -D <pkg>` | `bun add -D <pkg>` | Add dev dependency |
| `pnpm remove <pkg>` | `bun remove <pkg>` | Remove dependency |
| `pnpm update` | `bun update` | Update dependencies |
| `pnpm exec <script>` | `bun run <script>` | Run script |
| `pnpx <pkg>` | `bunx <pkg>` | Execute package |
| `pnpm publish` | `bun publish` | Publish package |

### pnpm Workspaces

```bash
# pnpm
pnpm -F app-a add lodash

# Bun
bun add -w app-a lodash
```

### Migration Steps

1. **Remove pnpm-lock.yaml**
   ```bash
   rm -rf node_modules pnpm-lock.yaml
   ```

2. **Install with Bun**
   ```bash
   bun install
   ```

3. **Update scripts**
   ```json
   {
     "scripts": {
       "dev": "bun run --watch index.ts",
       "build": "bun build ./index.ts --outdir ./dist"
     }
   }
   ```

## Migrating from Jest

### API Compatibility

Most Jest code works without modification:

```typescript
// Jest and Bun test runner share the same API
import { 
  test, it, describe, expect,
  beforeEach, afterEach,
  beforeAll, afterAll,
} from "bun:test";  // was: (no import needed in Jest)

// Test structure is identical
describe("User authentication", () => {
  beforeEach(() => {
    // Setup
  });
  
  test("should authenticate with valid credentials", async () => {
    const user = await login("user", "password");
    expect(user.id).toBe(123);
  });
});
```

### Command Mapping

| Jest | Bun Test Runner |
|------|-----------------|
| `jest` | `bun test` |
| `jest --watch` | `bun test --watch` |
| `jest --coverage` | `bun test --coverage` |
| `jest --updateSnapshot` | `bun test -u` |
| `jest testNamePattern` | `bun test testNamePattern` |
| `jest --testPathPattern=foo` | `bun test foo` |
| `jest --verbose` | `bun test --verbose` |
| `jest --bail` | `bun test --bail` |

### Configuration Migration

**jest.config.js**:
```javascript
module.exports = {
  testEnvironment: "jsdom",
  testMatch: ["**/__tests__/**/*.[jt]s?(x)", "**/?(*.)+(spec|test).[jt]s?(x)"],
  collectCoverageFrom: ["src/**/*.{ts,js}"],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

**bunfig.toml**:
```toml
[test]
# Test discovery (same patterns by default)
include = ["**/*.{test,spec}.{ts,tsx,js,jsx}"]

# Coverage
coverage = true
coverageExclude = ["tests/**", "**/*.test.ts"]
thresholds = { lines = 80, branches = 80, functions = 80, statements = 80 }

# Timeout
timeout = 5000
```

### Mocking Migration

**Jest**:
```javascript
jest.mock('./my-module', () => ({
  myFunction: jest.fn(() => 'mocked'),
}));

const spy = jest.spyOn(obj, 'method');
```

**Bun**:
```typescript
import { mock } from "bun:test";

const myModule = await mock("./my-module", {
  myFunction: mock(() => 'mocked'),
});

const spy = mock(obj.method.bind(obj));
```

### Snapshot Testing

Identical API:

```typescript
test("renders correctly", () => {
  const component = render(<MyComponent />);
  expect(component).toMatchSnapshot();  // Works the same
});
```

### Migration Steps

1. **Remove jest config** (optional - can keep for reference)
2. **Update imports** in test files:
   ```typescript
   // Remove: import { test, expect } from '@jest/globals';
   // Add:    import { test, expect } from 'bun:test';
   ```
3. **Run tests**:
   ```bash
   bun test
   ```
4. **Update snapshots if needed**:
   ```bash
   bun test -u
   ```

## Migrating from esbuild

### Command Mapping

| esbuild | Bun Bundler |
|---------|-------------|
| `esbuild entry.js --bundle --outdir=dist` | `bun build entry.js --outdir ./dist` |
| `esbuild --minify` | `bun build --minify` |
| `esbuild --sourcemap` | `bun build --sourcemap` |
| `esbuild --watch` | `bun build --watch` |
| `esbuild --target=browser` | `bun build --target browser` |
| `esbuild --format=esm` | `bun build --format esm` |

### Configuration Migration

**esbuild.config.js**:
```javascript
module.exports = {
  entryPoints: ["src/index.tsx", "src/admin.tsx"],
  outdir: "dist",
  bundle: true,
  minify: true,
  sourcemap: "external",
  target: "browser",
  loader: {
    ".png": "file",
    ".jpg": "file",
  },
  define: {
    "process.env.NODE_ENV": '"production"',
  },
};
```

**bunfig.toml**:
```toml
[build]
entrypoints = ["./src/index.tsx", "./src/admin.tsx"]
outdir = "./dist"
minify = true
sourcemap = "external"
target = "browser"

loader = { ".png" = "file", ".jpg" = "file" }

define = { "process.env.NODE_ENV" = '"production"' }
```

### JavaScript API

**esbuild**:
```javascript
const esbuild = require("esbuild");

await esbuild.build({
  entryPoints: ["src/index.tsx"],
  bundle: true,
  outdir: "dist",
});
```

**Bun**:
```typescript
await Bun.build({
  entrypoints: ["./src/index.tsx"],
  outdir: "./dist",
});
```

### Migration Steps

1. **Replace build commands** in package.json:
   ```json
   {
     "scripts": {
       "build": "bun build ./src/index.tsx --outdir ./dist --minify"
     }
   }
   ```

2. **Remove esbuild dependency**:
   ```bash
   bun remove esbuild
   ```

3. **Update build scripts** if using programmatic API

## Migrating from Webpack

### Basic Migration

**webpack.config.js**:
```javascript
const path = require("path");

module.exports = {
  mode: "production",
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
};
```

**bunfig.toml**:
```toml
[build]
entrypoints = ["./src/index.tsx"]
outdir = "./dist"
minify = true
target = "browser"
```

### Key Differences

1. **No loaders needed**: Bun handles TypeScript, JSX, CSS natively
2. **Simpler configuration**: Most webpack plugins not needed
3. **Faster builds**: 10-100x faster than webpack

### Migration Steps

1. **Remove webpack dependencies**:
   ```bash
   bun remove webpack webpack-cli ts-loader css-loader style-loader
   ```

2. **Update build script**:
   ```json
   {
     "scripts": {
       "build": "bun build ./src/index.tsx --outdir ./dist"
     }
   }
   ```

3. **Test the build**:
   ```bash
   bun build ./src/index.tsx --outdir ./dist
   ```

### Advanced Webpack Features

**Code splitting** → Dynamic imports (same syntax):
```typescript
const Module = await import("./heavy-module");
```

**Environment variables** → Define in bunfig.toml:
```toml
[build]
define = { "process.env.API_URL" = '"https://api.example.com"' }
```

## Migrating from Vite

Vite and Bun have similar philosophies. Main differences:

### Command Mapping

| Vite | Bun |
|------|-----|
| `vite` | `bun build --watch` |
| `vite build` | `bun build --minify` |
| `vite preview` | `bun run server.ts` |

### Configuration

**vite.config.ts**:
```typescript
export default {
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    port: 3000,
  },
};
```

**bunfig.toml**:
```toml
[build]
# Aliases handled via tsconfig.json paths
# Server configured in code, not config
```

### Migration Steps

1. **Keep tsconfig.json** for path aliases (Bun respects it)
2. **Replace dev server** with Bun's watch mode or built-in HTTP server
3. **Update build commands**

## Common Issues & Solutions

### TypeScript Errors

**Issue**: Type errors after migration

**Solution**: Ensure `tsconfig.json` is compatible:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true
  }
}
```

### Module Resolution Errors

**Issue**: Cannot find module errors

**Solution**: Use `--bun` flag or configure resolution:
```toml title="bunfig.toml"
[install]
resolution = ["node", "bun"]
```

### Native Module Issues

**Issue**: C/C++ addons don't work

**Solution**: 
1. Try `bun install --force` to rebuild
2. Use `--node-resolver` flag
3. Find pure JavaScript alternative

### Test Failures

**Issue**: Tests pass with Jest, fail with Bun

**Solution**: Check for Jest-specific APIs:
- Replace `jest.fn()` with `mock()`
- Replace `jest.mock()` with Bun's mock system
- Update test file imports to `from "bun:test"`

## Performance Improvements After Migration

Expected improvements:

- **Package installation**: 30x faster
- **Test execution**: 5-10x faster
- **Bundling**: 10-100x faster
- **Runtime startup**: 10-30x faster
- **Development iterations**: Near-instant with watch mode

## Rollback Plan

If migration issues persist:

1. **Keep backup lockfiles** for easy rollback
2. **Use Bun selectively**: Run specific commands with Bun while keeping npm/yarn
3. **Gradual migration**: Migrate one package at a time in monorepos

```bash
# Quick rollback
rm bun.lockb
cp package-lock.json.backup package-lock.json
npm install
```

## Related Documentation

- [Package Manager](references/02-package-manager.md) - Complete Bun PM guide
- [Bundler](references/03-bundler.md) - Bundling details
- [Test Runner](references/04-test-runner.md) - Testing documentation
- [Node.js Compatibility](references/08-nodejs-compat.md) - Compatibility details
