# TypeScript Configuration

Deno has first-class TypeScript support with no build step required. This guide covers type checking, configuration options, import maps, and advanced TypeScript features.

## Running TypeScript

### Basic Usage

Deno runs TypeScript files directly without compilation:

```bash
# Run TypeScript file
deno run app.ts

# Remote TypeScript files work too
deno run https://example.com/app.ts
```

### Type Checking

Type checking is separate from execution for performance:

```bash
# Type-check before running (fails if errors found)
deno run --check app.ts

# Type-check without running
deno check app.ts

# Type-check all modules including dependencies
deno check --all app.ts

# Skip type checking during tests
deno test --no-check

# Type-check JSDoc code snippets
deno check --doc readme.md
```

By default, `deno run` skips type checking. Use `--check` to enable it.

## Configuration File

Create `deno.json` or `deno.jsonc` in your project root:

```json
{
  "compilerOptions": {
    "lib": ["deno.ns", "dom"],
    "target": "ES2022",
    "module": "esnext",
    "strict": true,
    "checkJs": false,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": false,
    "esModuleInterop": false,
    "emitDecoratorMetadata": false,
    "experimentalDecorators": false,
    "importsNotUsedAsValues": "remove",
    "isolatedModules": true,
    "resolveJsonModule": true,
    "skipLibCheck": false,
    "types": [],
    "jsx": "react",
    "jsxFactory": "React.createElement",
    "jsxFragmentFactory": "React.Fragment"
  }
}
```

### Compiler Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `lib` | TypeScript library files to include | `["deno.ns"]` |
| `target` | JavaScript target version | `ES2022` |
| `module` | Module system | `esnext` |
| `strict` | Enable all strict type-checking options | `true` |
| `checkJs` | Type-check JavaScript files | `false` |
| `noImplicitAny` | Error on implicit `any` types | `true` (with strict) |
| `noImplicitReturns` | Error if not all paths return | `true` (with strict) |
| `noUnusedLocals` | Error on unused variables | `false` |
| `skipLibCheck` | Skip type checking of `.d.ts` files | `false` |
| `types` | Type declaration files to include | `[]` |
| `jsx` | JSX emit mode | `undefined` |
| `jsxFactory` | JSX factory function | `React.createElement` |

### Library Files

Specify which global types are available:

```json
{
  "compilerOptions": {
    "lib": ["deno.ns"]  // Default: Deno runtime APIs
  }
}
```

Common library combinations:

```json
// Browser environment only
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable"]
  }
}

// Deno + browser (SSR)
{
  "compilerOptions": {
    "lib": ["deno.ns", "dom", "dom.iterable"]
  }
}

// Web worker in Deno
{
  "compilerOptions": {
    "lib": ["deno.worker"]
  }
}

// Node.js compatibility mode
{
  "compilerOptions": {
    "lib": ["deno.node"]
  }
}
```

## Import Maps

Import maps allow you to remap module specifiers to different URLs:

### Basic Import Map

```json
{
  "imports": {
    // Remap bare specifiers
    "lodash": "https://cdn.skypack.dev/lodash@4.17.21",
    
    // Prefix-based remapping
    "@std/": "https://deno.land/std@0.224.0/",
    
    // Exact path remapping
    "my-app/": "./src/",
    
    // Versioned imports
    "@std/path": "jsr:@std/path@1",
    "@std/assert": "jsr:@std/assert@1"
  }
}
```

Usage in code:

```typescript
// Instead of:
import { join } from "https://deno.land/std@0.224.0/path/mod.ts";

// You can write:
import { join } from "@std/path/mod.ts";

// Or with JSR:
import { join } from "@std/path/join";
```

### Scoped Import Maps

Limit remappings to specific scopes:

```json
{
  "imports": {
    "preact": "https://esm.sh/preact@10.11.0",
    "preact/": "https://esm.sh/preact@10.11.0/"
  },
  "scopes": {
    "https://example.com/": {
      // Within this scope, remap differently
      "preact": "https://cdn.example.com/preact@9.0.0"
    }
  }
}
```

### Specifying Import Map Location

Deno automatically loads `deno.json` or `import_map.json` from the current directory. To use a custom location:

```bash
# Use specific import map file
deno run --import-map=import_map.json app.ts

# Remote import map
deno run --import-map=https://example.com/import_map.json app.ts
```

## Module Resolution

### Local Modules

Import local files with relative paths:

```typescript
// Must include extension
import { foo } from "./mod.ts";
import { bar } from "./utils/index.ts";
import { baz } from "../shared/types.ts";

// JavaScript files
import { qux } from "./legacy.js";
```

### Remote Modules

Import from URLs:

```typescript
// Deno Standard Library (versioned)
import { join } from "https://deno.land/std@0.224.0/path/mod.ts";

// Third-party libraries
import React from "https://esm.sh/react@18.2.0";

// GitHub raw content
import { plugin } from "https://raw.githubusercontent.com/user/repo/main/mod.ts";
```

### NPM Packages

Import npm packages directly:

```typescript
// Import from npm registry
import express from "npm:express@4.18.2";
import lodash from "npm:lodash";

// With specific version
import axios from "npm:axios@1.6.0";

// TypeScript types for npm packages
// @ts-types="npm:@types/lodash"
import _ from "npm:lodash";
```

### JSR Packages

JSR is the JavaScript Registry for modern packages:

```typescript
// Import from JSR
import { join } from "@std/path";
import { assertEquals } from "@std/assert";
import { serve } from "@std/http";

// Versioned imports (recommended)
import { join } from "@std/path@1.0.0";
```

## JavaScript Interop

### Type Checking JavaScript

Enable type checking for JavaScript files:

```json
{
  "compilerOptions": {
    "checkJs": true
  }
}
```

Or add pragma to individual files:

```javascript
// @ts-check

function add(a, b) {
  return a + b;
}

const result = add(1, "2"); // Error: Type 'string' is not assignable
```

### Providing Types for JavaScript

#### Using `@ts-self-types`

In the JavaScript file:

```javascript
// @ts-self-types="./my-module.d.ts"

export function add(a, b) {
  return a + b;
}
```

In the declaration file (`my-module.d.ts`):

```typescript
export function add(a: number, b: number): number;
```

#### Using `@ts-types` in Importer

In the TypeScript file:

```typescript
// @ts-types="./my-module.d.ts"
import { add } from "./my-module.js";
```

#### For NPM Packages

Provide types for untyped npm packages:

```typescript
// @ts-types="npm:@types/lodash"
import _ from "npm:lodash";
```

### TSDoc Comments

Use TSDoc to provide type information in JavaScript:

```javascript
/**
 * Adds two numbers.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function add(a, b) {
  return a + b;
}

/**
 * @type {{ name: string, age: number }}
 */
const user = { name: "Alice", age: 30 };
```

## Global Type Augmentation

### Using `declare global`

Extend global types in TypeScript files:

```typescript
// global.d.ts
declare global {
  interface Window {
    customAPI: {
      getData(): Promise<unknown>;
    };
  }
  
  var CONFIG: {
    apiUrl: string;
    debug: boolean;
  };
}

export {};
```

### Using Reference Directives

Include type files with reference comments:

```typescript
/// <reference types="./global.d.ts" />

// Now Window.customAPI is available
console.log(window.customAPI);
```

Or in `deno.json`:

```json
{
  "compilerOptions": {
    "types": ["./global.d.ts"]
  }
}
```

## JSX Support

### React JSX

Configure for React:

```json
{
  "compilerOptions": {
    "jsx": "react",
    "jsxFactory": "React.createElement"
  }
}
```

Usage:

```tsx
import React from "https://esm.sh/react@18.2.0";

function App() {
  return <div>Hello, World!</div>;
}
```

### JSX Transform (Modern React)

For React 17+:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  }
}
```

This doesn't require importing React:

```tsx
function App() {
  return <div>Hello!</div>;
}
```

### Preact JSX

```json
{
  "compilerOptions": {
    "jsx": "preact",
    "jsxFactory": "h"
  }
}
```

## Strict Mode

Deno enables strict mode by default. Key strict options:

```json
{
  "compilerOptions": {
    "strict": true,
    "strictBindCallApply": true,
    "strictBuiltinIteratorReturn": false,
    "strictFunctionTypes": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "useUnknownInCatchVariables": true
  }
}
```

### Disabling Strict Mode

Not recommended, but possible:

```json
{
  "compilerOptions": {
    "strict": false,
    "noImplicitAny": false,
    "strictNullChecks": false
  }
}
```

## Path Mapping (via Import Maps)

Deno doesn't support `paths` in compilerOptions. Use import maps instead:

```json
{
  "imports": {
    "#/": "./src/",
    "#utils/": "./src/utils/",
    "#types/": "./src/types/"
  }
}
```

Usage:

```typescript
import { helper } from "#utils/helper.ts";
import { MyType } from "#types/index.ts";
```

## Declaration File Generation

Generate `.d.ts` files for distribution:

```bash
# Generate declaration file
deno cache --emit=dts app.ts

# Output is cached, extract from Deno cache
```

Or use `deno bundle` with emit options:

```bash
deno bundle app.ts bundle.js
```

## Common TypeScript Patterns

### Exporting Types

```typescript
// mod.ts
export interface User {
  id: number;
  name: string;
}

export function createUser(name: string): User {
  return { id: Date.now(), name };
}

// Import type only (erased at runtime)
import type { User } from "./mod.ts";

// Import value and type
import { createUser, type User } from "./mod.ts";
```

### Conditional Types

```typescript
type IsString<T> = T extends string ? true : false;

type StringLength<S extends string> = S extends `${infer Head}${infer Rest}` 
  ? 1 + StringLength<Rest> 
  : 0;
```

### Generic Functions

```typescript
function firstElement<T>(arr: T[]): T | undefined {
  return arr[0];
}

const numbers = [1, 2, 3];
const firstNum = firstElement(numbers); // number | undefined
```

### Type Guards

```typescript
interface Fish { swim(): void; }
interface Bird { fly(): void; }

function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined;
}

const pet = getRandomPet();
if (isFish(pet)) {
  pet.swim(); // Type-safe
}
```

## Debugging TypeScript

### Source Maps

Deno generates source maps automatically for debugging:

```bash
# Run with inspector
deno run --inspect=0.0.0.0:9229 app.ts

# Connect Chrome DevTools to http://localhost:9229
```

### Type Errors in Logs

Include type information in error messages:

```typescript
try {
  await riskyOperation();
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  console.error("Type:", typeof error);
}
```

## Migration from Node.js TypeScript

### Key Differences

| Node.js + tsc | Deno |
|---------------|------|
| `tsconfig.json` | `deno.json` |
| `tsc` compilation step | No compilation needed |
| `require()` / CommonJS | ES modules only |
| `node:` prefix for builtins | `deno:` or no prefix |
| `paths` in tsconfig | Import maps in deno.json |

### Migration Steps

1. Create `deno.json` with compiler options
2. Replace `tsconfig.json` paths with import maps
3. Convert CommonJS to ES modules
4. Update imports to use full URLs or npm: specifiers
5. Remove build step from package.json scripts

## Performance Tips

### Skip Type Checking in Development

```bash
# Faster runs without type checking
deno run app.ts

# Type-check only when needed
deno check app.ts
```

### Use `--no-check` for Tests

```bash
# Skip type checking in test runner (faster)
deno test --no-check
```

### Incremental Type Checking

Deno caches type information. Subsequent runs are faster:

```bash
# First run (slower)
deno check app.ts

# Second run (faster, uses cache)
deno check app.ts
```

### Clear Cache When Needed

```bash
# Force re-type-check everything
deno cache --reload app.ts

# Clear entire cache
rm -rf ~/.cache/deno
```

## Related Topics

- [Permissions and Security](01-permissions.md) - Running scripts with permissions
- [Task Runner Guide](04-task-runner.md) - Automating TypeScript tasks
- [Testing Guide](05-testing.md) - Type-safe testing patterns
- [NPM Integration](07-npm-integration.md) - Using npm packages with TypeScript
