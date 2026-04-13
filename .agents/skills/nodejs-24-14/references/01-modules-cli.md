# Module Systems and CLI Reference

This document covers Node.js 24.14 module systems, package.json configuration, CLI options, and TypeScript integration.

## ECMAScript Modules (ESM)

### Introduction

ECMAScript modules are the official standard format to package JavaScript code for reuse. Node.js fully supports ES modules with interoperability between them and CommonJS.

### Enabling ES Modules

Node.js has two module systems: CommonJS and ECMAScript modules.

Authors can tell Node.js to interpret JavaScript as an ES module via:
- The `.mjs` file extension
- The `package.json` `"type"` field with value `"module"`
- The `--input-type=module` flag

Inversely, explicitly use CommonJS via:
- The `.cjs` file extension
- The `package.json` `"type"` field with value `"commonjs"`
- The `--input-type=commonjs` flag

When code lacks explicit markers, Node.js inspects source code for ES module syntax.

### Import Specifiers

There are three types of specifiers:

1. **Relative specifiers**: `'./startup.js'` or `'../config.mjs'`. File extension is always necessary.
2. **Bare specifiers**: `'some-package'` or `'some-package/shuffle'`. Resolved via package.json exports.
3. **Absolute specifiers**: `'file:///opt/nodejs/config.js'`. Full path references.

### ES Module Syntax

```javascript
// Named exports
export const name = 'value';
export function greet() { return 'Hello'; }

// Default export
export default class MyClass {}

// Re-export
export { named } from './module.js';
export * from './module.js';

// Import statements
import { named } from './module.js';
import defaultExport from './module.js';
import * as namespace from './module.js';
import defaultExport, { named } from './module.js';

// Dynamic import
const module = await import('./module.js');
```

### Top-Level Await

Top-level await is supported in ES modules:

```javascript
// app.mjs
import fs from 'node:fs/promises';

const config = await fs.readFile('config.json', 'utf8');
const data = JSON.parse(config);

console.log('Configuration loaded:', data);
```

### Import Attributes

Import attributes (formerly assertions) specify how module content should be parsed:

```javascript
// Import JSON with attribute
import packageData from './package.json' with { type: 'json' };

// Import text file
import text from './data.txt' with { type: 'text' };
```

### Cycle Handling

Circular dependencies are handled differently in ES modules vs CommonJS:

- ES modules: Live bindings, may get `undefined` if accessed before export initialization
- CommonJS: Copy of exports object at require() time

## CommonJS Modules

### Syntax

```javascript
// Require modules
const fs = require('node:fs');
const path = require('node:path');

// Export from module
module.exports = { name: 'value' };
exports.another = 'export';

// Short form
module.exports = function() {};
```

### Module Resolution

CommonJS resolution algorithm:
1. Core modules (e.g., `fs`, `http`) - built-in
2. Relative paths (`./file`, `../dir/file`) - resolved from current file
3. Node modules (`package-name`) - searched in node_modules directories upward

### Interoperability

**Importing CommonJS from ES Module:**

```javascript
// Default export is the CommonJS module.exports object
import cjsModule from './commonjs-module.js';
const { namedExport } = cjsModule; // Destructure named exports

// Named exports auto-detected for some packages
import { namedExport } from './commonjs-module.js';
```

**Importing ES Module from CommonJS:**

```javascript
// Default export becomes .default property
const esmModule = require('./esm-module.js');
const defaultExport = esmModule.default;
```

## Package.json Configuration

### Type Field

Controls module system for `.js` files:

```json
{
  "type": "module"
}
```

Or `"type": "commonjs"` for CommonJS default.

### Exports Field

Defines package entry points and subpath exports:

```json
{
  "name": "my-package",
  "main": "./index.js",
  "exports": {
    ".": "./index.js",
    "./utils": "./utils.js",
    "./package.json": "./package.json",
    "./public/*": "./public/*.js"
  }
}
```

Conditional exports:

```json
{
  "exports": {
    ".": {
      "import": "./esm.js",
      "require": "./cjs.js",
      "types": "./types.d.ts"
    }
  }
}
```

### Imports Field

Maps bare specifiers to file paths:

```json
{
  "imports": {
    "#utils/*": "./utils/*.js",
    "#config": "./config.json"
  }
}
```

Usage in ES modules:

```javascript
import { helper } from '#utils/helper.js';
import config from '#config' with { type: 'json' };
```

## Command-Line Interface

### Synopsis

```bash
node [options] [V8 options] [<program-entry-point> | -e "script" | -] [--] [arguments]
node inspect [<program-entry-point> | -e "script" | <host>:<port>] …
node --v8-options
```

Execute without arguments to start the REPL.

### Program Entry Point

The program entry point is resolved as a relative path from current working directory, then loaded as if requested by `require()` or `import()`.

Loaded as ES module when:
- Started with `--import` flag
- File has `.mjs`, `.mts`, or `.wasm` extension
- No `.cjs` extension and nearest `package.json` has `"type": "module"`

### Common CLI Options

#### Execution Control

```bash
# Execute string as script
node -e "console.log('Hello')"

# Read script from stdin
echo "console.log('Hello')" | node

# Specify input type
node --input-type=module script.js
node --input-type=commonjs script.js

# Load preload modules
node --preload ./setup.js app.js

# Import ES module for side effects
node --import ./setup.mjs app.js
```

#### Debugging and Inspection

```bash
# Start inspector on default port 9229
node --inspect app.js

# Specify host and port
node --inspect=0.0.0.0:9229 app.js

# Pause execution at start
node --inspect-brk app.js

# Inspector with web UI url
node --inspect-publish-uid app.js

# Trace garbage collection
node --trace-gc app.js

# Print V8 heap statistics
node --print-histogram app.js
```

#### Performance Profiling

```bash
# Basic profiling
node --perf-basic-prof app.js

# Profiling with precise timing
node --perf-basic-prof-live app.js

# Generate startup snapshot
node --snapshot-blob=snapshot.blob app.js

# Trace events for Chrome tracing
node --trace-events-enabled app.js
```

#### Security and Permissions

```bash
# Enable permission model
node --permission app.js

# Allow specific permissions
node --allow-fs-read=* --allow-env app.js

# Restrict to network only
node --allow-net=google.com app.js

# Disable addons loading
node --disallow-addons app.js
```

#### Environment and Configuration

```bash
# Set NODE_OPTIONS via CLI (overrides env var)
NODE_OPTIONS="--max-old-space-size=512" node app.js

# Use custom config file
node --config-store=./config app.js

# Set user data directory
node --user-data-dir=/tmp/node-data app.js
```

#### Memory and Performance Tuning

```bash
# Increase heap size (MB)
node --max-old-space-size=4096 app.js

# Set stack size (KB)
node --stack-size=10240 app.js

# Enable code caching
node --code-cache app.js

# Optimize for startup time
node --optimize-for-speed app.js
```

#### Output and Logging

```bash
# Print version
node --version

# Print all CLI options
node --help

# Print V8 options
node --v8-options

# Show deprecation warnings
node --trace-deprecation app.js

# Throw on deprecation
node --throw-deprecation app.js
```

#### Single Executable Applications

```bash
# Create SEA from archive
node --experimental-sea-config=sea-config.json

# Run existing SEA
./my-app-sea
```

### Environment Variables

#### NODE_OPTIONS

Sets default CLI options:

```bash
export NODE_OPTIONS="--max-old-space-size=2048 --trace-warnings"
node app.js  # Inherits NODE_OPTIONS
```

CLI options override `NODE_OPTIONS`.

#### NODE_ENV

Commonly used for environment detection:

```javascript
const env = process.env.NODE_ENV || 'development';
```

Common values: `development`, `test`, `production`

#### NODE_DEBUG

Enable internal debugging:

```bash
export NODE_DEBUG=http,net,tls
node app.js
```

#### NODE_NO_WARNINGS

Suppress deprecation warnings:

```bash
export NODE_NO_WARNINGS=1
node app.js
```

#### NODE_PATH

Additional module search paths (CommonJS only):

```bash
export NODE_PATH=/path/to/modules:/another/path
node app.js
```

## TypeScript Integration

Node.js has built-in TypeScript support for `.ts`, `.mts`, and `.cts` files.

### File Extensions

- `.ts`: CommonJS TypeScript
- `.mts`: ES Module TypeScript
- `.cts`: Explicit CommonJS TypeScript

### Basic Usage

```bash
# Run TypeScript file directly
node app.ts

# With type checking (requires tsc)
npx tsc --noEmit && node app.js
```

### Example TypeScript Module

```typescript
// app.mts
import fs from 'node:fs/promises';

async function main() {
  const data = await fs.readFile('config.json', 'utf8');
  console.log(JSON.parse(data));
}

main();
```

## Module Loading Patterns

### Lazy Loading

```javascript
// ES Module dynamic import
async function getModule() {
  const mod = await lazyImport('./heavy-module.js');
  return mod.function();
}

// CommonJS require in function
function getModule() {
  const mod = require('./heavy-module');
  return mod.function();
}
```

### Conditional Loading

```javascript
// Load based on platform
const os = process.platform === 'win32' 
  ? await import('./windows.js')
  : await import('./unix.js');

// Load optional dependency
let optionalMod;
try {
  optionalMod = await import('optional-package');
} catch {
  console.log('Optional package not available');
}
```

### Plugin Architecture

```javascript
// loader.mjs
export async function loadPlugin(name) {
  const plugin = await import(`./plugins/${name}.js`);
  return plugin.default;
}

// Usage
const authPlugin = await loadPlugin('auth');
const dbPlugin = await loadPlugin('database');
```

## Best Practices

1. **Use ES modules for new projects**: Better tree-shaking, static analysis, and standard compliance
2. **Prefix built-in modules**: Use `node:fs` instead of `fs` to clarify built-in vs local modules
3. **Include file extensions in relative imports**: Required for ES modules
4. **Use package.json exports**: Control what's accessible from your packages
5. **Avoid circular dependencies**: Restructure code to prevent import cycles
6. **Leverage top-level await**: Simplify initialization code in entry points
7. **Use conditional exports**: Provide different implementations for ESM/CJS/TypeScript

## Common Pitfalls

**Missing file extension in relative imports:**
```javascript
// Wrong (ESM)
import { foo } from './bar';  // Error

// Correct
import { foo } from './bar.js';  // OK
```

**Mixing module systems incorrectly:**
```javascript
// Wrong - mixing export styles
export default function() {}
module.exports.named = 'value';  // Confusing

// Correct - choose one style
export default function() {}
export const named = 'value';
```

**Circular dependency issues:**
```javascript
// a.js
import { b } from './b.js';
export const a = 'a';  // b may see undefined a

// b.js  
import { a } from './a.js';
export const b = a + 'b';  // May be 'undefinedb'
```

## Migration Guide: CommonJS to ES Modules

1. Rename `.js` to `.mjs` or add `"type": "module"` to package.json
2. Replace `require()` with `import` statements
3. Replace `module.exports` with `export` statements
4. Add file extensions to relative imports
5. Use top-level await instead of async IIFE patterns
6. Update dynamic `require()` to dynamic `import()`

```javascript
// Before (CommonJS)
const fs = require('fs');
const path = require('path');

module.exports = { readFile };

async function readFile(file) {
  return new Promise((resolve, reject) => {
    fs.readFile(file, 'utf8', (err, data) => {
      if (err) reject(err);
      else resolve(data);
    });
  });
}

// After (ES Module)
import fs from 'node:fs/promises';
import path from 'node:path';

export async function readFile(file) {
  return fs.readFile(file, 'utf8');
}

export default { readFile };
```
