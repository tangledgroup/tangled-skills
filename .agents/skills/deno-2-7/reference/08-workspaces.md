# Workspaces Guide

Deno workspaces allow you to manage multiple related packages in a single repository. This guide covers workspace setup, shared dependencies, and monorepo patterns.

## Basic Workspace Setup

### Creating a Workspace

Create a root `deno.json` with workspace configuration:

```json
{
  "name": "@myorg/monorepo",
  "version": "1.0.0",
  "workspace": ["packages/*"]
}
```

Directory structure:

```
my-monorepo/
├── deno.json              # Root workspace config
├── packages/
│   ├── cli/
│   │   └── deno.json      # CLI package
│   ├── core/
│   │   └── deno.json      # Core library
│   └── utils/
│       └── deno.json      # Shared utilities
```

### Package Configuration

Each package has its own `deno.json`:

**packages/core/deno.json:**
```json
{
  "name": "@myorg/core",
  "version": "1.0.0",
  "exports": "./mod.ts",
  "tasks": {
    "test": "deno test -A"
  }
}
```

**packages/cli/deno.json:**
```json
{
  "name": "@myorg/cli",
  "version": "1.0.0",
  "imports": {
    "@myorg/core": "../core/mod.ts"
  },
  "tasks": {
    "start": "deno run -A main.ts"
  }
}
```

## Importing Between Packages

### Using Workspace Imports

Reference local packages in imports:

```json
{
  "imports": {
    "@myorg/core": "../core/mod.ts",
    "@myorg/utils": "../utils/mod.ts"
  }
}
```

Usage in code:

```typescript
import { CoreFunction } from "@myorg/core";
import { helper } from "@myorg/utils";

const result = CoreFunction(helper("data"));
```

### Absolute Paths from Root

For simpler paths, use root-relative imports:

```json
{
  "imports": {
    "@/core/": "../../packages/core/",
    "@/utils/": "../../packages/utils/"
  }
}
```

Usage:

```typescript
import { CoreFunction } from "@/core/mod.ts";
import { helper } from "@/utils/helpers.ts";
```

## Shared Dependencies

### Managing Common Imports

Define shared dependencies in root `deno.json`:

```json
{
  "workspace": ["packages/*"],
  "imports": {
    "@std/path": "jsr:@std/path@1",
    "@std/assert": "jsr:@std/assert@1",
    "lodash": "npm:lodash@4.17.21"
  }
}
```

Packages inherit these imports automatically.

### Version Alignment

Keep dependency versions consistent across packages:

```json
// Root deno.json
{
  "imports": {
    "react": "npm:react@18.2.0",
    "react-dom": "npm:react-dom@18.2.0"
  }
}
```

All packages use the same React version automatically.

## Running Tasks Across Packages

### Workspace Task Commands

Run tasks in all workspace packages:

```bash
# Run test task in all packages
deno task test

# Run specific package task
deno task --filter=@myorg/cli test

# List all workspace tasks
deno task
```

### Package-Specific Tasks

Define tasks in each package:

**packages/core/deno.json:**
```json
{
  "tasks": {
    "test": "deno test -A",
    "lint": "deno lint",
    "build": "deno bundle mod.ts dist/core.js"
  }
}
```

**packages/cli/deno.json:**
```json
{
  "tasks": {
    "test": "deno test -A",
    "start": "deno run -A main.ts",
    "build": "deno compile -A -o cli main.ts"
  }
}
```

Run from root:
```bash
cd packages/core && deno task test
cd packages/cli && deno task start
```

### Cross-Package Task Dependencies

Set up dependencies between packages:

**Root deno.json:**
```json
{
  "tasks": {
    "test:core": "deno task --cwd=packages/core test",
    "test:cli": "deno task --cwd=packages/cli test",
    "test:all": {
      "dependencies": ["test:core", "test:cli"]
    },
    "build:core": "deno task --cwd=packages/core build",
    "build:cli": "deno task --cwd=packages/cli build",
    "build:all": {
      "command": "echo 'All packages built!'",
      "dependencies": ["build:core", "build:cli"]
    }
  }
}
```

## Testing in Workspaces

### Running All Tests

From workspace root:

```bash
# Test all packages
deno test -A packages/*/

# Test specific package
deno test -A packages/core/

# Test with pattern
deno test -A packages/**/*core*.test.ts
```

### Shared Test Utilities

Create shared test utilities:

**packages/test-utils/deno.json:**
```json
{
  "name": "@myorg/test-utils",
  "version": "1.0.0",
  "exports": "./mod.ts"
}
```

**packages/test-utils/mod.ts:**
```typescript
import { assertEquals } from "@std/assert";

export function assertEqual(a: unknown, b: unknown) {
  assertEquals(a, b);
}

export async function createTestDb() {
  // Shared test database setup
}
```

Use in package tests:

**packages/core/test/example.test.ts:**
```typescript
import { assertEqual } from "@myorg/test-utils";

Deno.test("example", () => {
  assertEqual(1 + 1, 2);
});
```

## Publishing Packages

### Preparing for Publication

Configure package for JSR publication:

**packages/core/deno.json:**
```json
{
  "name": "@myorg/core",
  "version": "1.0.0",
  "exports": "./mod.ts",
  "publish": {
    "exclude": ["tests/**", "*.test.ts"]
  }
}
```

### Publishing to JSR

```bash
# Login to JSR
deno jsr whoami

# Publish package
cd packages/core
deno publish

# Publish with confirmation bypass
deno publish --dry-run  # Test first
deno publish
```

### Version Management

Use consistent versioning across workspace:

**Option 1: Independent versions**
- Each package has its own version
- Update independently

**Option 2: Lockstep versions**
- All packages share same version
- Update all together

For lockstep, update root `deno.json` and sync package versions.

## Monorepo Patterns

### Library + CLI Pattern

```
my-project/
├── deno.json
├── packages/
│   ├── core/           # Core library
│   │   ├── mod.ts
│   │   └── deno.json
│   ├── api/            # API client
│   │   ├── mod.ts
│   │   └── deno.json
│   └── cli/            # CLI tool
│       ├── main.ts
│       └── deno.json
```

**packages/cli/deno.json:**
```json
{
  "name": "@myorg/cli",
  "imports": {
    "@myorg/core": "../core/mod.ts",
    "@myorg/api": "../api/mod.ts"
  }
}
```

### Frontend + Backend Pattern

```
my-app/
├── deno.json
├── packages/
│   ├── shared/         # Shared types/utilities
│   ├── backend/        # Deno server
│   └── frontend/       # Fresh/Oak app
```

**packages/shared/deno.json:**
```json
{
  "name": "@myapp/shared",
  "exports": {
    "./types": "./types.ts",
    "./utils": "./utils.ts"
  }
}
```

**packages/backend/deno.json:**
```json
{
  "imports": {
    "@myapp/shared": "../shared/mod.ts"
  }
}
```

### Plugin Architecture

```
plugin-system/
├── deno.json
├── packages/
│   ├── core/           # Core plugin system
│   └── plugins/
│       ├── plugin-a/   # Plugin A
│       └── plugin-b/   # Plugin B
```

**packages/core/mod.ts:**
```typescript
export interface Plugin {
  name: string;
  initialize(): void;
}

export class PluginManager {
  plugins: Plugin[] = [];
  
  register(plugin: Plugin) {
    this.plugins.push(plugin);
    plugin.initialize();
  }
}
```

**packages/plugins/plugin-a/mod.ts:**
```typescript
import type { Plugin } from "@myorg/core";

export const PluginA: Plugin = {
  name: "plugin-a",
  initialize() {
    console.log("Plugin A initialized");
  }
};
```

## Configuration Inheritance

### Extending Root Config

Packages inherit settings from root:

**Root deno.json:**
```json
{
  "workspace": ["packages/*"],
  "lint": {
    "rules": { "tags": ["recommended"] }
  },
  "fmt": {
    "lineLength": 100
  },
  "compilerOptions": {
    "strict": true
  }
}
```

Packages automatically use these settings unless overridden.

### Overriding Settings

Package can override inherited settings:

**packages/legacy/deno.json:**
```json
{
  "name": "@myorg/legacy",
  "compilerOptions": {
    "strict": false  // Override root setting
  },
  "fmt": {
    "lineLength": 80  // Different line length
  }
}
```

## Tooling Integration

### Linting All Packages

```bash
# Lint all packages
deno lint packages/*/

# Lint with custom config
deno lint --config=deno.json packages/
```

### Formatting All Packages

```bash
# Format all packages
deno fmt packages/*/

# Check formatting (CI mode)
deno fmt --check packages/
```

### Type Checking All Packages

```bash
# Check all packages
deno check packages/*/mod.ts

# Check with all dependencies
deno check --all packages/*/mod.ts
```

## CI/CD Integration

### GitHub Actions for Workspaces

```yaml
name: Workspace Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Deno
        uses: denoland/setup-deno@main
        with:
          deno-version: stable
      
      - name: Lint all packages
        run: deno lint packages/*/
      
      - name: Type check all packages
        run: deno check --all packages/*/mod.ts
      
      - name: Run all tests
        run: deno test -A packages/*/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.lcov
```

### Publishing Workflow

```yaml
name: Publish Packages

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Deno
        uses: denoland/setup-deno@main
      
      - name: Publish core package
        run: cd packages/core && deno publish
        env:
          JSR_TOKEN: ${{ secrets.JSR_TOKEN }}
      
      - name: Publish CLI package
        run: cd packages/cli && deno publish
        env:
          JSR_TOKEN: ${{ secrets.JSR_TOKEN }}
```

## Best Practices

### Clear Package Boundaries

Define clear responsibilities for each package:

```
packages/
├── core/         # Core business logic (no dependencies on other packages)
├── api/          # API client (depends on core)
├── cli/          # CLI tool (depends on core, api)
└── shared/       # Shared utilities (no dependencies)
```

### Avoid Circular Dependencies

Structure imports to prevent cycles:

```typescript
// ✅ Good: Linear dependency graph
// shared -> core -> api -> cli

// ❌ Bad: Circular dependency
// core imports from cli, cli imports from core
```

### Use Barrel Exports

Create clean public APIs with barrel files:

**packages/core/mod.ts:**
```typescript
export { CoreClass } from "./core.ts";
export type { CoreOptions } from "./types.ts";
export { helperFunction } from "./utils.ts";

// Re-export commonly used types
export type { Plugin } from "./plugin.ts";
```

### Document Package Purpose

Include README in each package:

**packages/core/README.md:**
```markdown
# @myorg/core

Core library providing main functionality.

## Installation

Use via workspace import or publish to JSR.

## Usage

```typescript
import { CoreClass } from "@myorg/core";

const core = new CoreClass();
```

## API

- `CoreClass` - Main class
- `helperFunction()` - Utility function
```

### Version Dependencies Carefully

When packages depend on each other:

```json
{
  "imports": {
    // Use relative paths for workspace packages
    "@myorg/core": "../core/mod.ts",
    
    // Use versioned imports for external packages
    "@std/path": "jsr:@std/path@1"
  }
}
```

## Troubleshooting

### Import Resolution Errors

Ensure workspace is properly configured:

```json
{
  "workspace": ["packages/*"]  // Must match directory structure
}
```

Check that package paths are correct in imports.

### Task Execution Issues

Use `--cwd` to specify working directory:

```bash
# Run task in specific package
deno task --cwd=packages/core test
```

Or change directory first:

```bash
cd packages/core && deno task test
```

### Permission Errors

Each package may need different permissions:

```bash
# Grant permissions per-package
cd packages/cli && deno task start  # May need --allow-net
cd packages/core && deno task test  # May need --allow-read
```

## Related Topics

- [Task Runner Guide](04-task-runner.md) - Running workspace tasks
- [TypeScript Configuration](03-typescript.md) - Workspace TypeScript setup
- [NPM Integration](07-npm-integration.md) - Shared npm dependencies
