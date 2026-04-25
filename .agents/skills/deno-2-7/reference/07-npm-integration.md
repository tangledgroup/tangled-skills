# NPM Integration

Deno can use npm packages directly without a build step or package.json. This guide covers importing npm packages, version management, and migration patterns.

## Basic Usage

### Importing npm Packages

Use the `npm:` prefix to import from the npm registry:

```typescript
// Import with specific version
import express from "npm:express@4.18.2";

// Import without version (uses latest)
import lodash from "npm:lodash";

// Subpath imports
import { Router } from "npm:express@4.18.2";
import { join } from "npm:path@0.12.7";
```

### Using npm Packages

```typescript
import _ from "npm:lodash";

const data = _.groupBy([6.1, 4.2, 6.3], Math.floor);
console.log(data);  // { '4': [4.2], '6': [6.1, 6.3] }

import axios from "npm:axios";

const response = await axios.get("https://api.example.com/data");
console.log(response.data);
```

## Version Management

### Pinning Versions

Always pin versions for reproducibility:

```typescript
// ✅ Recommended: Pin exact version
import react from "npm:react@18.2.0";

// ❌ Avoid: Unpinned (uses latest)
import react from "npm:react";
```

### Semver Ranges

Deno supports semver ranges:

```typescript
// Caret range (compatible with 4.18.2)
import express from "npm:express@^4.18.2";

// Tilde range (patch updates only)
import lodash from "npm:lodash@~4.17.21";

// Exact version
import axios from "npm:axios@1.6.0";
```

### Updating Packages

Check for outdated packages:

```bash
# Check which packages can be updated
deno outdated

# Update specific package
deno update npm:express

# Update all packages
deno update --all
```

## TypeScript Support

### Built-in Types

Many npm packages include TypeScript types:

```typescript
import express, { Request, Response } from "npm:express@4.18.2";

const app = express();

app.get("/", (req: Request, res: Response) => {
  res.send("Hello!");
});
```

### Adding Types for Untyped Packages

Use `@ts-types` directive:

```typescript
// @ts-types="npm:@types/lodash"
import _ from "npm:lodash";

_.map([1, 2, 3], String);  // Type-checked
```

For packages without `@types`:

```typescript
// Create declaration file
// lodash.d.ts
declare module "npm:lodash" {
  export function map<T, U>(array: T[], iteratee: (value: T) => U): U[];
}

// Use in code
// @ts-types="./lodash.d.ts"
import _ from "npm:lodash";
```

### Type Overrides

Override types for specific packages:

```json
{
  "compilerOptions": {
    "types": ["npm:@types/node"]
  }
}
```

## Import Maps

Use import maps to simplify npm imports:

```json
{
  "imports": {
    "express": "npm:express@4.18.2",
    "lodash": "npm:lodash@4.17.21",
    "axios": "npm:axios@1.6.0"
  }
}
```

Then import without `npm:` prefix:

```typescript
import express from "express";
import _ from "lodash";
import axios from "axios";
```

## Common npm Packages

### Web Frameworks

```typescript
// Express
import express from "npm:express@4.18.2";

const app = express();
app.get("/", (req, res) => res.send("Hello"));
app.listen(3000);

// Koa
import Koa from "npm:koa@2.14.2";

const app = new Koa();
app.use((ctx) => {
  ctx.body = "Hello";
});
app.listen(3000);

// Fastify
import fastify from "npm:fastify@4.24.0";

const app = fastify();
app.get("/", () => "Hello");
await app.listen({ port: 3000 });
```

### Utility Libraries

```typescript
// Lodash
import _ from "npm:lodash@4.17.21";

const result = _.chunk([1, 2, 3, 4], 2);
// [[1, 2], [3, 4]]

// Moment.js (or date-fns)
import moment from "npm:moment@2.29.4";

const now = moment().format("YYYY-MM-DD");

// Better: use date-fns
import { format } from "npm:date-fns@3.0.0";

const formatted = format(new Date(), "yyyy-MM-dd");

// Day.js
import dayjs from "npm:dayjs@1.11.10";

const today = dayjs().format("YYYY-MM-DD");
```

### Testing Libraries

```typescript
// Jest (can use with Deno test)
import { describe, it, expect } from "npm:@jest/globals@29.7.0";

describe("math", () => {
  it("adds numbers", () => {
    expect(1 + 1).toBe(2);
  });
});

// Mocha
import mocha from "npm:mocha@10.2.0";

mocha.describe("math", () => {
  mocha.it("adds numbers", () => {
    // ...
  });
});
```

### Database Clients

```typescript
// PostgreSQL (pg)
import postgres from "npm:postgres@3.4.3";

const sql = postgres({
  host: "localhost",
  port: 5432,
  database: "mydb",
  user: "postgres"
});

const rows = await sql`SELECT * FROM users`;

// MongoDB (mongodb)
import { MongoClient } from "npm:mongodb@6.3.0";

const client = new MongoClient("mongodb://localhost:27017");
await client.connect();
const db = client.db("mydb");
const users = await db.collection("users").find({}).toArray();

// SQLite (better-sqlite3)
import Database from "npm:better-sqlite3@9.2.2";

const db = new Database("database.sqlite");
const rows = db.prepare("SELECT * FROM users").all();
```

### Build Tools

```typescript
// ESLint
import { ESLint } from "npm:eslint@8.56.0";

const eslint = new ESLint();
const results = await eslint.lintFiles(["src/**/*.ts"]);

// Prettier
import prettier from "npm:prettier@3.1.1";

const formatted = await prettier.format("const x=1;", {
  parser: "typescript"
});

// TypeScript compiler API
import ts from "npm:typescript@5.3.3";

const sourceFile = ts.createSourceFile(
  "example.ts",
  code,
  ts.ScriptTarget.Latest,
  true
);
```

## Node.js Compatibility

### Node.js Built-in Modules

Deno can use Node.js built-in modules via npm:

```typescript
// fs module
import * as fs from "npm:fs@0.0.1-security";

const data = fs.readFileSync("file.txt", "utf-8");

// path module
import * as path from "npm:path@0.12.7";

const joined = path.join("/foo", "bar", "baz");

// crypto module
import * as crypto from "npm:crypto@0.0.1-security";

const hash = crypto.createHash("sha256").update("data").digest("hex");

// os module
import * as os from "npm:os@0.1.2";

console.log(os.hostname());
console.log(os.totalmem());
```

Note: These are stubs that map to Deno's native APIs when using Node.js compatibility mode.

### Using Node.js-Specific Packages

Some packages require Node.js APIs:

```typescript
// Enable Node.js compatibility
Deno.serve({ port: 8000 }, async (req) => {
  // Works with Node.js packages
  const express = await import("npm:express@4.18.2");
  
  // ...
});
```

For full Node.js compatibility, use `--node-modules-dir`:

```bash
deno run --node-modules-dir script.ts
```

## Caching and Performance

### Module Cache

Deno caches npm packages automatically:

```bash
# First run downloads and caches package
deno run script.ts

# Subsequent runs use cache (faster)
deno run script.ts

# Clear cache
deno cache --reload script.ts

# Remove cached packages
rm -rf ~/.cache/deno/npm/
```

### Pre-caching Dependencies

Cache dependencies before running:

```bash
deno cache script.ts
```

This resolves and caches all imports without executing the code.

## Migration from Node.js

### Package.json to deno.json

Convert package.json dependencies to import maps:

**package.json:**
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21"
  }
}
```

**deno.json:**
```json
{
  "imports": {
    "express": "npm:express@4.18.2",
    "lodash": "npm:lodash@4.17.21"
  }
}
```

### CommonJS to ES Modules

Convert `require()` to imports:

**Before (CommonJS):**
```javascript
const express = require("express");
const _ = require("lodash");

module.exports = { handler };
```

**After (ES Module):**
```typescript
import express from "npm:express@4.18.2";
import _ from "npm:lodash@4.17.21";

export { handler };
```

### Node.js Globals to Deno APIs

Replace Node.js globals with Deno equivalents:

| Node.js | Deno |
|---------|------|
| `process.env` | `Deno.env` |
| `__dirname` | `import.meta.dirname` |
| `__filename` | `import.meta.filename` |
| `require()` | `import` or `await import()` |
| `console.*` | `console.*` (same) |
| `global` | `globalThis` |

Example:

```typescript
// Node.js
const env = process.env.NODE_ENV;
const dir = __dirname;

// Deno
const env = Deno.env.get("NODE_ENV");
const dir = import.meta.dirname;
```

## Best Practices

### Pin Exact Versions

```typescript
// ✅ Good: Exact version
import express from "npm:express@4.18.2";

// ❌ Bad: Unpinned
import express from "npm:express";
```

### Use Import Maps for Repeated Imports

```json
{
  "imports": {
    "@app/express": "npm:express@4.18.2",
    "@app/lodash": "npm:lodash@4.17.21",
    "@app/react": "npm:react@18.2.0"
  }
}
```

### Prefer Deno Standard Library When Possible

| npm Package | Deno @std Alternative |
|-------------|----------------------|
| `express` | `@std/http` (for simple servers) |
| `lodash` | `@std/collections`, `@std/async` |
| `path` | `@std/path` |
| `fs` | `Deno.*File*` APIs |
| `chalk` | `@std/fmt/colors` |
| `yaml` | `@std/yaml` |
| `uuid` | `crypto.randomUUID()` (built-in) |

Example:

```typescript
// Instead of npm packages
import { join } from "@std/path";
import { colors } from "@std/fmt/colors";
import { parse } from "@std/yaml";

// Use Deno APIs
const uuid = crypto.randomUUID();
```

### Check Package Compatibility

Before using an npm package:

1. Check if it relies heavily on Node.js-specific APIs
2. Look for TypeScript type definitions
3. Test in a small example first
4. Consider Deno alternatives (@std)

## Troubleshooting

### "Cannot find module" Errors

Ensure the package name is correct:

```typescript
// ❌ Wrong: Using scoped package incorrectly
import pkg from "npm:@scope/package";

// ✅ Correct
import pkg from "npm:@scope/package@1.0.0";
```

### Type Errors with npm Packages

Add types explicitly:

```typescript
// @ts-types="npm:@types/lodash"
import _ from "npm:lodash";
```

Or install `@types` package:

```typescript
import _ from "npm:lodash";
import type { Chunk } from "npm:@types/lodash";
```

### Native Module Failures

Some npm packages have native bindings that don't work in Deno:

```typescript
// ❌ May not work: Packages with native C++ bindings
import nodeSqlite3 from "npm:sqlite3";

// ✅ Use pure JS alternative or Deno API
import { Client } from "@std/sql";
```

### Circular Dependencies

Use dynamic imports for circular dependencies:

```typescript
// Instead of static import that causes cycle
const module = await import("npm:some-package@1.0.0");
const { func } = module;
```

## Related Topics

- [TypeScript Configuration](03-typescript.md) - Type checking npm packages
- [API Reference](06-api-reference.md) - Deno native alternatives to npm
- [Task Runner Guide](04-task-runner.md) - Using npm packages in tasks
