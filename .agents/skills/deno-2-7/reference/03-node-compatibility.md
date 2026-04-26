# Node.js and npm Compatibility

## Overview

Deno 2.x is fully compatible with Node.js. Most Node projects run in Deno with little or no change. Key compatibility features include npm package imports, CommonJS support, Node built-in modules, and `package.json` support.

## Importing npm Packages

Use the `npm:` specifier to import any npm package:

```typescript
import chalk from "npm:chalk@5";
console.log(chalk.green("Hello from npm in Deno"));

import * as emoji from "npm:node-emoji";
console.log(emoji.emojify(":sauropod: :heart: npm"));
```

Version specifiers follow npm conventions (`^5`, `~5.1`, `5.1.0`).

## Using Node Built-in Modules

Add the `node:` prefix to import Node built-ins:

```typescript
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { createServer } from "node:http";

console.log(path.join("./foo", "../bar"));
console.log(os.cpus());
```

Deno provides helpful hints when you forget the `node:` prefix:

```
error: Relative import path "fs" not prefixed with / or ./ or ../
  hint: If you want to use a built-in Node module, add a "node:" prefix (ex. "node:fs").
```

## CommonJS Support

Deno supports CommonJS modules through the `.cjs` extension:

```javascript
// main.cjs
const chalk = require("chalk");
console.log(chalk.green("Hello from npm in Deno"));
```

Run with: `deno run main.cjs`

### package.json type option

Set `"type": "commonjs"` in `package.json` to treat `.js` files as CommonJS:

```json
{
  "type": "commonjs"
}
```

## package.json Support

Deno natively supports `package.json`. Dependencies from `package.json` can be resolved:

```jsonc
// package.json
{
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

```typescript
// After running `deno install`
import express from "express";
const app = express();
```

Run `deno install` to resolve and cache dependencies from `package.json`.

If both `deno.json` and `package.json` exist in the same directory, Deno merges dependencies from both and uses `deno.json` for Deno-specific configuration.

## node_modules Directory

Deno supports three modes for `node_modules`:

**Default (Deno-managed):** Deno creates and manages `node_modules/.deno/` automatically. This is the recommended approach — no manual `npm install` needed.

**Manual mode:** Use traditional `node_modules` created by npm/pnpm/yarn:

```jsonc
// deno.json
{
  "nodeModulesDir": "manual"
}
```

```bash
npm install    # or pnpm install, yarn install
deno run main.ts
```

**Disabled:** No `node_modules` at all — all npm packages resolved through Deno's cache:

```jsonc
// deno.json
{
  "nodeModulesDir": false
}
```

## Node.js Global Objects

Deno provides Node.js global objects for compatibility:

- `process` — Access environment variables, exit codes, stdio
- `global` / `globalThis` — Global object access
- `__dirname` and `__filename` — Available in CommonJS modules
- `require()` — Available in CommonJS context

## Conditional Exports

Deno respects conditional exports in `package.json`:

```json
{
  "exports": {
    "types": "./dist/index.d.ts",
    "import": "./dist/index.mjs",
    "require": "./dist/index.js"
  }
}
```

## Migrating from Node to Deno

Key differences to be aware of:

- Use `node:` prefix for built-in imports
- Permissions must be explicitly granted (or use `-A` for full access)
- `package.json` scripts work via `deno task` or the `scripts` field
- No need for TypeScript compiler — Deno handles TS natively
- Use `Deno.serve()` instead of `http.createServer()` for native HTTP servers

## Node-API (N-API) Addons

Deno supports Node-API addons through the `--allow-ffi` permission. Native addons that use the N-API can be loaded and used in Deno.
