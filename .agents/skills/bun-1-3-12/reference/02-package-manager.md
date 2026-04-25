# Bun Package Manager

Bun's package manager replaces npm, yarn, and pnpm with a significantly faster alternative (30x faster than npm, 10x faster than yarn) while maintaining compatibility with existing workflows.

## Basic Commands

### Installation

```bash
# Install dependencies from package.json
bun install

# Install a specific package
bun add lodash

# Install multiple packages
bun add lodash express react

# Install dev dependency
bun add -D typescript @types/node

# Install peer dependency
bun add -P @types/react

# Install optional dependency
bun add -O @optional/package

# Install with specific version
bun add lodash@4.17.21

# Install latest version
bun add --latest lodash

# Install from git repository
bun add git+https://github.com/user/repo.git

# Install from GitHub shorthand
bun add user/repo

# Install local package
bun add ./local-package
```

### Uninstallation

```bash
# Remove package
bun remove lodash

# Remove multiple packages
bun remove lodash moment underscore
```

### Updates

```bash
# Update all packages
bun update

# Update specific package
bun update lodash

# Update to latest (ignore lockfile)
bun update --latest

# Check for outdated packages
bun outdated

# Show why a package is installed
bun why lodash

# Audit for security vulnerabilities
bun audit

# Fix security issues automatically
bun audit --fix
```

## Package.json Commands

Run scripts defined in `package.json`:

```bash
# Run script from package.json
bun run build
bun run dev
bun run test

# Short form (equivalent to bun run)
bun x build

# Run with arguments
bun run build --production

# Run without package.json scripts
bun run index.ts
```

## Global Package Management

### bunx - Package Runner

Execute packages globally without installing:

```bash
# Run package without global install
bunx typescript --version
bunx jest
bunx prettier --write src/*.ts

# Install and run locally
bunx -b tsc  # -b adds to PATH for current session
```

### Global Installation

```bash
# Install package globally
bun add -g typescript
bun add -g jest
bun add -g nodemon

# Remove global package
bun remove -g typescript

# List globally installed packages
bun list -g

# Update global packages
bun update -g
```

## Workspaces (Monorepos)

### Setup

Create `package.json` with workspaces configuration:

```json title="package.json"
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "packages/*"
  ]
}
```

Directory structure:
```
my-monorepo/
├── package.json          # Root with workspaces config
├── bun.lockb            # Lockfile (binary format)
└── packages/
    ├── app-a/
    │   ├── package.json
    │   └── src/
    ├── app-b/
    │   ├── package.json
    │   └── src/
    └── shared-lib/
        ├── package.json
        └── src/
```

### Workspace Commands

```bash
# Install all workspace dependencies
bun install

# Run script in specific workspace
bun run --filter app-a build
bun run --filter "app-*" test

# Run script in all workspaces
bun run --workspace-build build

# Install package in specific workspace
cd packages/app-a
bun add lodash

# Or from root with filter
bun add -w app-a lodash

# List workspace packages
bun workspaces
```

### Workspace Package References

Reference other workspace packages:

```json title="packages/app-a/package.json"
{
  "name": "app-a",
  "dependencies": {
    "@myorg/shared-lib": "workspace:*"
  }
}
```

Supported workspace protocols:
- `workspace:*` - Use exact version from workspace
- `workspace:^` - Compatible version (caret range)
- `workspace:~` - Approximately equivalent (tilde range)
- `workspace:1.0.0` - Specific version

## Catalogs (Dependency Deduplication)

Catalogs allow defining centralized dependency versions across workspaces:

```json title="package.json"
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["packages/*"],
  "catalog": {
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.2",
    "@types/node": "20.10.0"
  },
  "catalogs": {
    "app": {
      "react": "18.2.0",
      "next": "14.0.0"
    },
    "lib": {
      "typescript": "5.3.2",
      "eslint": "8.56.0"
    }
  }
}
```

Use catalog versions:

```json title="packages/app/package.json"
{
  "name": "my-app",
  "dependencies": {
    "react": "catalog:",
    "next": "catalog:app"
  }
}
```

Benefits:
- Single source of truth for versions
- Automatic deduplication
- Easier version updates
- Consistent dependencies across workspaces

## Lockfile Management

Bun uses a binary lockfile (`bun.lockb`) for faster parsing:

```bash
# Install with exact lockfile versions (CI/CD)
bun install --frozen

# Install ignoring lockfile (rebuild from scratch)
bun install --no-lockfile

# Force lockfile regeneration
bun install --force

# Check if lockfile is out of sync
bun install --check
```

### Lockfile Compatibility

Bun's lockfile is Bun-specific but can import from npm/yarn:

```bash
# Convert package-lock.json to bun.lockb
bun install  # Automatically converts

# Convert yarn.lock to bun.lockb
bun install  # Automatically converts

# Export to package-lock.json (for npm compatibility)
bun install --save-lockfile package-lock.json
```

## Caching

Bun has an intelligent cache system:

```bash
# Clear package cache
bun clean

# Install without using cache
bun install --no-cache

# Show cache location
echo $BUN_CACHE  # Typically ~/.bun/cache

# Configure cache size
export BUN_CACHE_CAPACITY=1073741824  # 1GB
```

Cache benefits:
- Faster installs on subsequent runs
- Offline installation capability
- Reduced network usage
- Automatic cache invalidation

## Publishing Packages

### Publish to npm Registry

```bash
# Publish current package
bun publish

# Publish with access control (for scoped packages)
bun publish --access public

# Publish with tag
bun publish --tag next
bun publish --tag latest

# Dry run (test without publishing)
bun publish --dry-run

# Publish from specific directory
bun publish ./packages/my-package
```

### Registry Configuration

```bash
# Publish to custom registry
bun publish --registry https://registry.example.com

# Configure default registry in .npmrc
echo "@myorg:registry=https://npm.mycompany.com" >> .npmrc

# Authenticate with registry
bun add -g npm
npm login --registry=https://registry.example.com
```

### Package Metadata

Ensure `package.json` is properly configured:

```json title="package.json"
{
  "name": "@myorg/my-package",
  "version": "1.0.0",
  "description": "A great package",
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "bun build src/index.ts --outdir dist",
    "prepublishOnly": "bun run build"
  },
  "keywords": ["typescript", "utility"],
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/myorg/my-package"
  },
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  }
}
```

## Dependency Analysis

### Inspect Package Information

```bash
# Show package details
bun info lodash

# Show package version history
bun view lodash versions

# Show package dependencies
bun view lodash dependencies

# Show who depends on a package
bun view lodash dependents
```

### Dependency Tree

```bash
# Show dependency tree
bun list

# Show only direct dependencies
bun list --depth=0

# Show specific package and its dependencies
bun list lodash

# Show production dependencies only
bun list --production

# Show dev dependencies only
bun list --dev
```

## Patching Packages

Apply local modifications to dependencies:

```bash
# Create patch for package
bun add -p lodash

# Edit node_modules/lodash temporarily
# Then commit the patch

# Patches are stored in .patches/ directory
```

Patch file example:

```json title=".patches/lodash+4.17.21.patch"
{
  "dependencies": {
    "lodash": "patch:lodash@npm%3A4.17.21#./.patches/lodash+4.17.21.patch"
  }
}
```

## Advanced Configuration

### .npmrc Configuration

Create `.npmrc` in project root:

```bash title=".npmrc"
# Registry settings
registry=https://registry.npmjs.org/

# Scope-specific registry
@myorg:registry=https://npm.mycompany.com

# Install options
engine-strict=true
save-exact=true

# Proxy settings
http-proxy=http://proxy.example.com:8080
https-proxy=http://proxy.example.com:8080

# SSL settings
strict-ssl=true
```

### bunfig.toml Package Options

```toml title="bunfig.toml"
[install]
# Use specific Node version for compatibility
node-resolver = 18

# Fallback resolution order
resolution = ["node", "bun"]

# Disable cache
cache = false

# Force reinstall
force = false

# Frozen mode (fail if lockfile out of sync)
frozen = false
```

## Migration from npm/yarn/pnpm

### Command Equivalents

| npm | yarn | pnpm | bun |
|-----|------|------|-----|
| `npm install` | `yarn install` | `pnpm install` | `bun install` |
| `npm install lodash` | `yarn add lodash` | `pnpm add lodash` | `bun add lodash` |
| `npm install -D lodash` | `yarn add -D lodash` | `pnpm add -D lodash` | `bun add -D lodash` |
| `npm uninstall lodash` | `yarn remove lodash` | `pnpm remove lodash` | `bun remove lodash` |
| `npm update` | `yarn upgrade` | `pnpm update` | `bun update` |
| `npm run build` | `yarn build` | `pnpm run build` | `bun run build` |
| `npx typescript` | `yarn typescript` | `pnpm exec typescript` | `bunx typescript` |
| `npm publish` | `yarn publish` | `pnpm publish` | `bun publish` |

### Migration Steps

1. **Backup existing lockfiles**
   ```bash
   cp package-lock.json package-lock.json.backup
   cp yarn.lock yarn.lock.backup
   ```

2. **Remove node_modules and old lockfiles**
   ```bash
   rm -rf node_modules package-lock.json yarn.lock pnpm-lock.yaml
   ```

3. **Install with Bun**
   ```bash
   bun install
   ```

4. **Test the application**
   ```bash
   bun run build
   bun run test
   ```

5. **Update scripts in package.json** (optional)
   ```json
   {
     "scripts": {
       "start": "bun run index.ts",  # was: "node index.js"
       "dev": "bun run --watch index.ts"  # was: "nodemon index.js"
     }
   }
   ```

## Performance Tips

1. **Use workspaces** for monorepos to deduplicate dependencies
2. **Enable caching** for faster subsequent installs
3. **Use catalogs** to centralize version management
4. **Run `bun install --frozen` in CI/CD** for deterministic builds
5. **Avoid unnecessary devDependencies** in production builds

## Troubleshooting

### Common Issues

**Peer dependency warnings**: Install missing peer dependencies:
```bash
bun add -P @types/react
```

**Resolution conflicts**: Use patches or force specific versions:
```bash
bun add lodash@4.17.21 --force
```

**Cache issues**: Clear cache and reinstall:
```bash
bun clean
bun install --no-cache
```

**Registry authentication**: Ensure proper .npmrc configuration:
```bash
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
```

**Binary packages**: Some native modules may need rebuilding:
```bash
bun install --force
```

## Environment Variables

```bash
# Custom cache directory
export BUN_CACHE=/path/to/cache

# Disable color output
export NO_COLOR=1

# Force HTTPS
export NPM_CONFIG_REGISTRY=https://registry.npmjs.org/

# Proxy settings
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Engine strictness
export BUN_ENGINE_STRICT=1
```
