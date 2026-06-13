# Workspaces and Monorepos

## Overview

Deno supports workspaces (monorepos) for managing multiple related and interdependent packages simultaneously. A workspace is defined in the root `deno.json`:

```jsonc
{
  "workspace": ["./packages/*"]
}
```

Each workspace member directory can contain:
- Only a `deno.json` (Deno-first package)
- Both `deno.json` and `package.json` (hybrid package)
- Only `package.json` (Node-first package that still participates in the Deno workspace)

## Example Workspace Structure

```
project/
├── deno.json          # Root workspace config
├── main.ts
├── packages/
│   ├── add/
│   │   ├── deno.json
│   │   └── mod.ts
│   └── subtract/
│       ├── deno.json
│       └── mod.ts
```

### Root Configuration

```jsonc
// deno.json
{
  "workspace": ["./packages/add", "./packages/subtract"],
  "imports": {
    "chalk": "npm:chalk@5"
  }
}
```

### Member Package Configuration

```jsonc
// packages/add/deno.json
{
  "name": "@scope/add",
  "version": "0.1.0",
  "exports": "./mod.ts"
}
```

```typescript
// packages/add/mod.ts
export function add(a: number, b: number): number {
  return a + b;
}
```

### Using Workspace Members

Import workspace members by their `name`:

```typescript
// main.ts
import chalk from "chalk";
import { add } from "@scope/add";
import { subtract } from "@scope/subtract";

console.log("1 + 2 =", chalk.green(add(1, 2)));
```

## Path Patterns

Workspace supports glob patterns:

```jsonc
{
  "workspace": [
    "./packages/*",
    "./libs/**"
  ]
}
```

## Publishing Workspace Packages

Publish individual workspace packages to JSR:

```bash
deno publish packages/add/
deno publish packages/subtract/
```

Or publish all workspace members:

```bash
deno publish --include-workspace
```

## Running Commands Across Workspaces

Deno commands run across all workspace members:

```bash
# Type check all members
deno check

# Run tests in all members
deno test

# Format all members
deno fmt

# Lint all members
deno lint
```

## Sharing Dependencies

Root-level `imports` are available to all workspace members:

```jsonc
// Root deno.json
{
  "workspace": ["./packages/*"],
  "imports": {
    "@std/assert": "jsr:@std/assert@^1.0.0"
  }
}
```

Each member can also define its own imports that override or extend the root.

## Interdependent Packages

Workspace members can depend on each other using the workspace protocol:

```jsonc
// packages/api/deno.json
{
  "name": "@scope/api",
  "version": "1.0.0",
  "imports": {
    "@scope/core": "workspace:@scope/core"
  }
}
```

## Migrating from npm Workspaces

Key differences from npm workspaces:

- Deno uses `"workspace"` (singular) instead of `"workspaces"` (plural)
- Each member needs a `"name"` field for cross-package imports
- `deno install` resolves all workspace dependencies
- `package.json`-only members are supported without requiring `deno.json`

## Workspace Protocol in package.json

For Node-first packages, use workspace protocol:

```jsonc
{
  "name": "@scope/api",
  "dependencies": {
    "@scope/core": "workspace:*"
  }
}
```
