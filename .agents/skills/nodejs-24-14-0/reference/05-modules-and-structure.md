# Modules and Project Structure

## CommonJS Modules

The default module system in Node.js. Uses `require()` and `module.exports`.

```javascript
// math.js — exporting
const add = (a, b) => a + b;
const subtract = (a, b) => a - b;

module.exports = { add, subtract };
// Or: exports.add = add; exports.subtract = subtract;

// app.js — importing
const { add, subtract } = require('./math');
console.log(add(2, 3)); // 5
```

### Module Wrapper

Node.js wraps each CommonJS file in a function:

```javascript
(function(exports, require, module, __filename, __dirname) {
  // Your code here
});
```

This provides five special variables:
- `exports` — shorthand for `module.exports`
- `require()` — function to load modules
- `module` — reference to current module
- `__filename` — absolute path of current file
- `__dirname` — absolute path of current directory

### Module Caching

Modules are cached after first load:

```javascript
// First require loads and caches the module
const mod1 = require('./myModule');
// Second require returns cached instance
const mod2 = require('./myModule');
console.log(mod1 === mod2); // true

// Clear cache (development only)
delete require.cache[require.resolve('./myModule')];
```

### Cycles

Circular dependencies are handled but exports may be partially initialized:

```javascript
// a.js
const b = require('./b');
module.exports = { greeting: 'Hello from A' };

// b.js
const a = require('./a');
console.log(a.greeting); // undefined — a.js hasn't finished loading!
module.exports = { farewell: 'Goodbye from B' };
```

## ECMAScript Modules (ESM)

Enable with `"type": "module"` in package.json or use `.mjs` extension.

```javascript
// math.mjs — exporting
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;

// Named default export
export default class Calculator {
  add(a, b) { return a + b; }
}

// app.mjs — importing
import { add, subtract } from './math.mjs';
import Calculator from './math.mjs';

// Import all as namespace
import * as math from './math.mjs';

// Import with renaming
import { add as sum } from './math.mjs';
```

### ESM Features

**Top-level await:**
```javascript
// No async wrapper needed
const config = await fs.readFile('config.json', 'utf-8');
const parsed = JSON.parse(config);
```

**import.meta:**
```javascript
import { fileURLToPath } from 'node:url';

const currentFile = import.meta.url;
// 'file:///path/to/file.js'

const currentDir = fileURLToPath(new URL('.', import.meta.url));
// '/path/to/'
```

**Dynamic imports:**
```javascript
const module = await import('./dynamic-module.mjs');
const { default: MyClass } = await import('some-package');
```

### ESM vs CommonJS Differences

| Feature | CommonJS | ESM |
|---------|----------|-----|
| Import syntax | `require()` | `import` |
| Export syntax | `module.exports` | `export` |
| Live bindings | No (copy at require time) | Yes (live references) |
| Top-level await | No | Yes |
| File extensions | `.js`, `.cjs` | `.mjs`, `.js` (with type: module) |
| __dirname/__filename | Available | Not available (use import.meta.url) |
| Caching | By resolved path | By URL |

## Package.json

```json
{
  "name": "my-package",
  "version": "1.0.0",
  "type": "module",
  "main": "index.js",
  "exports": {
    ".": "./index.js",
    "./utils": "./utils.js"
  },
  "imports": {
    "#internal/*": "./lib/*"
  },
  "scripts": {
    "start": "node index.js",
    "test": "node --test",
    "dev": "node --watch index.js"
  },
  "engines": {
    "node": ">=24.0.0"
  }
}
```

### Exports Field

Controls which files are accessible from outside the package:

```json
{
  "exports": {
    ".": {
      "import": "./esm/index.js",
      "require": "./cjs/index.js",
      "default": "./default/index.js"
    },
    "./plugin": "./plugin.js",
    "./internal/*": null  // block access
  }
}
```

### Imports Field (Subpath Imports)

Map subpath aliases to actual files:

```json
{
  "imports": {
    "#utils/*": "./lib/utils/*",
    "#config": "./config.js"
  }
}
```

```javascript
import { helper } from '#utils/helper.js';
import config from '#config';
```

## node_modules Resolution

Node.js resolves modules in this order:

1. **Built-in modules** — `node:` prefix or bare name matching core module
2. **File** — exact path with extension (`.js`, `.json`, `.node`)
3. **Directory** — looks for `package.json` `main` field or `index.js`
4. **node_modules** — walks up directory tree looking for `node_modules/<name>`

```
project/
├── app.js
├── lib/
│   └── helper.js
└── node_modules/
    └── lodash/
        └── package.json
```

```javascript
require('lodash');           // from node_modules
require('./lib/helper');     // relative file
require('../config');        // parent directory
```

## Built-in Modules (node: prefix)

Use `node:` prefix to explicitly reference built-in modules and avoid shadowing:

```javascript
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import url from 'node:url';
import util from 'node:util';
import stream from 'node:stream';
import events from 'node:events';
import net from 'node:net';
import tls from 'node:tls';
import dns from 'node:dns';
import zlib from 'node:zlib';
import child_process from 'node:child_process';
import worker_threads from 'node:worker_threads';
import cluster from 'node:cluster';
import readline from 'node:readline';
import console from 'node:console';
import timers from 'node:timers';
import assert from 'node:assert';
import v8 from 'node:v8';
import perf_hooks from 'node:perf_hooks';
import test from 'node:test';
import sqlite from 'node:sqlite';
import tty from 'node:tty';
import dgram from 'node:dgram';
import http2 from 'node:http2';
import https from 'node:https';
import buffer from 'node:buffer';
import async_hooks from 'node:async_hooks';
import diagnostics_channel from 'node:diagnostics_channel';
import inspector from 'node:inspector';
import intl from 'node:intl';
import module from 'node:module';
import repl from 'node:repl';
import report from 'node:report';
import wasi from 'node:wasi';
import vm from 'node:vm';
import webcrypto from 'node:webcrypto';
```

## TypeScript Support

Node.js 24 supports native TypeScript with `--experimental-strip-types`:

```bash
node --experimental-strip-types app.ts
```

```typescript
// app.ts
import fs from 'node:fs/promises';

interface Config {
  port: number;
  host: string;
}

async function start(config: Config): Promise<void> {
  const data = await fs.readFile('data.json', 'utf-8');
  console.log(`Running on ${config.host}:${config.port}`);
}

start({ port: 3000, host: 'localhost' });
```

## JSON Modules

Import JSON directly as ESM:

```javascript
import config from './config.json' with { type: 'json' };
console.log(config.database.url);
```

## Wasm Modules

Import WebAssembly modules:

```javascript
import init, { add } from './math.wasm' with { type: 'module' };
await init();
const result = add(2, 3);
```

## Loaders

Custom module loaders for transformation (experimental):

```bash
node --experimental-loader my-loader.js app.js
```

```javascript
// my-loader.js
export async function resolve(specifier, context, nextResolve) {
  return nextResolve(specifier, context);
}

export async function load(url, context, nextLoad) {
  const result = await nextLoad(url, context);
  // Transform source code
  return {
    ...result,
    source: transform(result.source),
  };
}
```
