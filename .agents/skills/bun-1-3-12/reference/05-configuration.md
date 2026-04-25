# Bun Configuration

Bun uses `bunfig.toml` for configuration. Most features work without configuration, but `bunfig.toml` allows fine-grained control over installation, testing, and building.

## File Location

Place `bunfig.toml` in your project root:
```
my-project/
├── bunfig.toml
├── package.json
└── src/
```

## Basic Structure

```toml title="bunfig.toml"
# Package manager configuration
[install]

# Test runner configuration
[test]

# Bundler configuration
[build]

# Environment variables
[env]
```

## Install Configuration

### Dependency Resolution

```toml
[install]
# Force specific Node.js version for compatibility
node-resolver = 18

# Module resolution order
resolution = ["node", "bun"]

# Disable caching (useful for debugging)
cache = true

# Force reinstall ignoring lockfile
force = false

# Frozen mode: fail if lockfile out of sync (CI/CD)
frozen = false

# Use workspaces
workspaces = ["packages/*"]
```

### Registry Settings

```toml
[install]
# Custom npm registry
registry = "https://registry.npmjs.org/"

# Scope-specific registries
registries = { "@myorg" = "https://npm.mycompany.com" }
```

## Test Configuration

### Basic Test Settings

```toml
[test]
# Test timeout in milliseconds (default: 5000)
timeout = 10000

# Run tests in random order
shuffle = false

# Run tests concurrently
concurrent = false

# Maximum concurrent tests
maxConcurrency = 20

# Stop on first failure
bail = false

# Update snapshots automatically
updateSnapshot = false

# Verbose output
verbose = false
```

### Coverage Configuration

```toml
[test]
# Enable coverage reporting
coverage = true

# Output directory for coverage reports
coverageDir = "./coverage"

# Files to exclude from coverage
coverageExclude = [
  "tests/**",
  "**/*.test.ts",
  "**/*.spec.ts",
  "**/node_modules/**",
  "**/dist/**",
]

# Coverage thresholds (fail if below)
thresholds = {
  lines = 80,
  branches = 70,
  functions = 80,
  statements = 80,
}
```

### Test Discovery

```toml
[test]
# Files to include in test discovery
include = [
  "**/*.{test,spec}.{ts,tsx,js,jsx}",
  "**/*_test.{ts,tsx,js,jsx}",
]

# Files to exclude
exclude = [
  "node_modules",
  "dist",
  "build",
  ".git",
]

# Preload scripts before tests
preload = ["./tests/setup.ts"]
```

### Reporter Configuration

```toml
[test]
# Output format
reporter = "auto"  # "auto" | "junit" | "json" | "compact"

# Output file for reporters
reporterOutfile = "./test-results.xml"
```

## Build Configuration

### Output Settings

```toml
[build]
# Output directory
outdir = "./dist"

# Minify output
minify = false

# Generate sourcemaps
sourcemap = false  # false | true | "inline" | "external"

# Target environment
target = "browser"  # "browser" | "bun" | "node"

# Output format
format = "esm"  # "esm" | "cjs" | "iife"
```

### Advanced Build Options

```toml
[build]
# File type loaders
loader = {
  ".png" = "file",
  ".jpg" = "file",
  ".gif" = "file",
  ".svg" = "file",
  ".woff" = "file",
  ".woff2" = "file",
  ".ttf" = "file",
  ".eot" = "file",
}

# Compile to bytecode
bytecode = false

# Tree shaking
treeShaking = true

# External dependencies (don't bundle)
external = ["lodash", "axios"]

# Define replacements at build time
define = {
  "process.env.API_URL" = '"https://api.example.com"',
  "__VERSION__" = '"1.0.0"',
  "__DEV__" = 'true',
}

# Public directory for static assets
publicDir = "./public"

# Entry points
entrypoints = ["./src/index.tsx", "./src/admin.tsx"]
```

### Watch Mode Settings

```toml
[build]
# Enable watch mode
watch = false

# Hot module replacement
hot = false

# HMR port
hmrPort = 1234

# Files to watch
watchDir = "./src"

# Files to ignore
ignore = ["**/*.test.ts", "**/node_modules/**"]
```

## Environment Configuration

### Environment Variables

```toml
[env]
# Set environment variables
NODE_ENV = "development"
API_URL = "https://api.example.com"
DEBUG = "true"

# Load from .env files (in order, later overrides earlier)
envFiles = [".env", ".env.local"]
```

### Conditional Environments

```toml
[env.development]
NODE_ENV = "development"
DEBUG = "true"

[env.production]
NODE_ENV = "production"
DEBUG = "false"

# Use with: bun run --env production
```

## Runtime Configuration

### Script Execution

```toml
[run]
# Default script to run
script = "./src/index.ts"

# Watch mode for script execution
watch = false

# Environment file for runtime
envFile = ".env"
```

## Project-Specific Examples

### Full-Stack Application

```toml title="bunfig.toml"
[install]
workspaces = ["apps/*", "packages/*"]
frozen = true  # CI/CD safety

[test]
timeout = 15000
concurrent = true
maxConcurrency = 8
coverage = true
coverageDir = "./coverage"
exclude = ["node_modules", "dist", ".next"]

[build]
outdir = "./dist"
minify = true
sourcemap = "external"
target = "node"
publicDir = "./public"

[env]
NODE_ENV = "development"
DATABASE_URL = "postgres://localhost/dev"
```

### Library Package

```toml title="bunfig.toml"
[test]
timeout = 5000
coverage = true
thresholds = { lines = 90, branches = 80 }

[build]
# Build both ESM and CJS versions
format = "esm"
target = "bun"
outdir = "./dist"
minify = false
sourcemap = true

[env]
LIB_VERSION = "1.0.0"
```

### Web Application

```toml title="bunfig.toml"
[build]
target = "browser"
format = "esm"
outdir = "./static"
minify = true
sourcemap = "external"
hot = true  # HMR in development
publicDir = "./public"

loader = {
  ".png" = "file",
  ".jpg" = "file",
  ".svg" = "file",
  ".woff2" = "file",
}

define = {
  "process.env.API_URL" = '"https://api.myapp.com"',
  "__APP_VERSION__" = '"2.0.0"',
}

[test]
include = ["**/*.test.{ts,tsx}"]
exclude = ["node_modules", ".next", "dist"]
```

### CLI Tool

```toml title="bunfig.toml"
[build]
target = "bun"
format = "esm"
compile = true  # Single executable
bytecode = true

[test]
timeout = 10000
verbose = true

[env]
CLI_VERSION = "1.0.0"
```

## Migration from Other Tools

### From Jest Config

```javascript title="jest.config.js"
module.exports = {
  testTimeout: 10000,
  collectCoverageFrom: ["src/**/*.{ts,js}"],
  coverageThreshold: {
    global: {
      lines: 80,
      branches: 70,
    },
  },
};
```

```toml title="bunfig.toml"
[test]
timeout = 10000
coverage = true
coverageExclude = ["tests/**"]
thresholds = { lines = 80, branches = 70 }
```

### From esbuild Config

```javascript title="esbuild.config.js"
module.exports = {
  entryPoints: ["src/index.tsx"],
  outdir: "dist",
  bundle: true,
  minify: true,
  sourcemap: true,
};
```

```toml title="bunfig.toml"
[build]
entrypoints = ["./src/index.tsx"]
outdir = "./dist"
minify = true
sourcemap = "external"
```

### From Webpack Config

```javascript title="webpack.config.js"
module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
};
```

```toml title="bunfig.toml"
[build]
entrypoints = ["./src/index.js"]
outdir = "./dist"
minify = true
```

## Environment Variable Precedence

Bun loads environment variables in this order (later overrides earlier):

1. Operating system environment variables
2. `[env]` section in `bunfig.toml`
3. `.env` file (if exists)
4. `.env.local` file (if exists)
5. Command-line overrides: `NODE_ENV=production bun run`

## Validation and Debugging

### Validate Configuration

```bash
# Check for syntax errors
bun run --help  # If this works, TOML is valid

# Test with verbose output
bun test --verbose
bun build --verbose
```

### Common Issues

**TOML syntax errors**: Use a TOML validator or editor with TOML support.

**Configuration not applied**: Ensure file is named exactly `bunfig.toml` in project root.

**Wrong section**: Double-check section names (`[test]`, `[build]`, `[install]`).

**Type errors**: TOML values must match expected types (strings in quotes, numbers without).

## Tips and Best Practices

1. **Keep configuration minimal**: Only add settings you need
2. **Use environment-specific configs**: Different settings for dev/production
3. **Version control bunfig.toml**: Share configuration with team
4. **Document non-obvious settings**: Add comments explaining why
5. **Test configuration changes**: Verify they work before committing

## Complete Example

```toml title="bunfig.toml"
# Package manager settings
[install]
node-resolver = 18
workspaces = ["packages/*"]
cache = true
frozen = false

# Test runner settings
[test]
timeout = 10000
concurrent = true
maxConcurrency = 8
coverage = true
coverageDir = "./coverage"
coverageExclude = [
  "tests/**",
  "**/*.test.ts",
  "**/node_modules/**",
]
thresholds = { lines = 80, branches = 70 }
reporter = "auto"

# Bundler settings
[build]
outdir = "./dist"
minify = true
sourcemap = "external"
target = "browser"
format = "esm"
publicDir = "./public"

loader = {
  ".png" = "file",
  ".jpg" = "file",
  ".svg" = "file",
}

define = {
  "process.env.API_URL" = '"https://api.example.com"',
  "__VERSION__" = '"1.0.0"',
}

external = ["react", "react-dom"]

# Environment variables
[env]
NODE_ENV = "development"
DEBUG = "true"

[env.production]
NODE_ENV = "production"
DEBUG = "false"
```

## Related Documentation

- [Runtime Basics](references/01-runtime-basics.md) - Runtime configuration
- [Package Manager](references/02-package-manager.md) - Install settings
- [Bundler](references/03-bundler.md) - Build configuration
- [Test Runner](references/04-test-runner.md) - Test settings
