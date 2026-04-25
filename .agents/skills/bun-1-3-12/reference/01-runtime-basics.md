# Bun Runtime Basics

The Bun runtime is a JavaScript/TypeScript execution environment that replaces Node.js with significantly improved performance (10-30x faster startup, 2-5x faster execution for many workloads).

## Running Scripts

### Basic Execution

Run TypeScript or JavaScript files directly without transpilation:

```bash
# Run TypeScript file
bun run index.ts

# Run JavaScript file
bun run app.js

# Run with arguments
bun run script.ts arg1 arg2

# Short form (equivalent to bun run)
bun index.ts
```

### Supported File Types

Bun natively supports these file extensions without configuration:
- `.ts`, `.tsx` - TypeScript / TypeScript JSX
- `.js`, `.jsx` - JavaScript / JSX
- `.mjs`, `.cjs` - ES modules / CommonJS
- `.mts`, `.cts` - TypeScript modules
- `.json` - JSON data (importable)
- `.css` - CSS files (for bundling)
- `.html` - HTML templates
- `.wasm` - WebAssembly modules
- `.tome`, `.toml` - TOML configuration
- `.yaml`, `.yml` - YAML files
- `.md`, `.markdown` - Markdown files

## Watch Mode

Auto-restart on file changes (similar to `nodemon`):

```bash
# Watch mode for development
bun run --watch index.ts

# Watch specific files
bun run --watch src/index.ts --ignore src/test/

# Short form
bun --watch index.ts
```

### Watch Mode Options

```bash
# Clear screen on restart
bun run --watch --clear-screen index.ts

# Ignore patterns
bun run --watch --ignore "*.test.ts" --ignore "node_modules/" index.ts

# Custom watch path
bun run --watch --dir ./src index.ts
```

## REPL (Read-Eval-Print Loop)

Interactive JavaScript/TypeScript console:

```bash
# Start REPL
bun

# Exit with Ctrl+D or .exit
```

### REPL Features

```typescript
// TypeScript works directly
const greeting = `Hello, ${new Date().getFullYear()}!`;
console.log(greeting); // Hello, 2024!

// Import modules
import { fetch } from "bun";
const response = await fetch("https://api.github.com");
response.status; // 200

// Access Node.js globals
process.env.NODE_ENV; // "development"
Buffer.from("hello"); // <Buffer 68 65 6c 6c 6f>

// Built-in Bun APIs
Bun.version; // "1.3.12"
Bun.pid; // Current process ID
```

## Debugging

### Using Chrome DevTools

```bash
# Start with debugger attached (port 9229)
bun --inspect index.ts

# Start and break at first line
bun --inspect-brk index.ts

# Specify port
bun --inspect=9230 index.ts
```

Then open `chrome://inspect` in Chrome or `edge://inspect` in Edge.

### Debug Logging

```bash
# Enable debug logs
BUN_DEBUG=1 bun run index.ts

# Enable specific debug categories
BUN_DEBUG=gc bun run index.ts  # GC debugging
BUN_DEBUG=module bun run index.ts  # Module resolution
```

## Environment Variables

### Reading Environment Variables

```typescript
// Node.js style (compatible)
process.env.NODE_ENV; // "production"

// Bun style (preferred for new code)
env.NODE_ENV; // "production"
```

### Setting Environment Variables

```bash
# Inline environment variable
NODE_ENV=production bun run index.ts

# Multiple variables
NODE_ENV=production PORT=3000 bun run server.ts

# Load from .env file (automatic in development)
bun run index.ts
```

### .env File Support

Bun automatically loads `.env` files:

```bash title=".env"
DATABASE_URL=postgres://localhost/db
API_KEY=secret123
NODE_ENV=development
```

```typescript title="index.ts"
// Automatically available
console.log(env.DATABASE_URL); // postgres://localhost/db
console.log(process.env.API_KEY); // secret123
```

Load specific env files:

```bash
# Load .env.production
bun run --env-file .env.production index.ts

# Multiple env files (later files override earlier)
bun run --env-file .env.base --env-file .env.local index.ts
```

## Module Resolution

### Importing Modules

```typescript
// ES modules (default in Bun)
import fs from "fs";
import { readFile } from "fs/promises";

// Node.js-style require still works
const path = require("path");
const { join } = require("path");

// TypeScript imports work without transpilation
import { Component } from "./Component.tsx";

// Import JSON directly
import config from "./config.json";

// Import TOML, YAML, CSS, etc.
import settings from "settings.toml";
import styles from "./styles.css";
```

### Module Resolution Order

Bun resolves modules in this order:
1. Built-in modules (`fs`, `path`, `http`, etc.)
2. Absolute paths (`/home/user/project/file.ts`)
3. Relative paths (`./file`, `../lib/file`)
4. Node_modules packages (`import lodash from "lodash"`)

### Custom Module Resolution

Configure in `bunfig.toml`:

```toml title="bunfig.toml"
[install]
# Fallback resolution order for packages
resolution = ["node", "bun"]

[test]
# Module aliases
aliases = { "@components" = "./src/components" }
```

## TypeScript Support

### No Transpilation Needed

Bun has a built-in TypeScript compiler:

```typescript title="index.ts"
// This works without tsc compilation step
interface Config {
  port: number;
  host: string;
}

const config: Config = { port: 3000, host: "localhost" };

async function start(): Promise<void> {
  console.log(`Starting on ${config.host}:${config.port}`);
}

start();
```

```bash
# Run directly - no tsc needed
bun run index.ts
```

### tsconfig.json Compatibility

Bun respects your `tsconfig.json`:

```json title="tsconfig.json"
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### TypeScript-Only Features

Some TypeScript features require `bun --bun` flag:

```bash
# Use Bun's module resolution for .ts imports
bun run --bun index.ts
```

## JSX Support

### React JSX

Works without Babel or transpilation:

```tsx title="App.tsx"
import { h } from "preact";

function App() {
  const name = "Bun";
  return <h1>Hello, {name}!</h1>;
}

export default App;
```

```bash
bun run App.tsx
```

### JSX Configuration

Configure in `bunfig.toml`:

```toml
[install]
jsxFactory = "h"
jsxFragment = "Fragment"
```

## Workers (Parallel Execution)

Run code in parallel using worker threads:

```typescript title="index.ts"
// Main thread
const worker = new Worker("./worker.ts", { type: "module" });

worker.postMessage({ task: "process-data" });

worker.onmessage = (event) => {
  console.log("Result:", event.data);
};

// worker.ts
self.onmessage = async (event) => {
  const result = await heavyComputation(event.data.task);
  self.postMessage(result);
};
```

### Worker Options

```typescript
// Shared memory for fast data transfer
const sharedArrayBuffer = new SharedArrayBuffer(1024);
const worker = new Worker("./worker.ts", {
  type: "module",
  transferList: [sharedArrayBuffer],
});

// Named workers for debugging
const worker = new Worker("./worker.ts", {
  name: "data-processor",
  type: "module",
});
```

## Performance Tips

1. **Use native Bun APIs** instead of npm packages when available
2. **Enable bytecode compilation** for faster startup: `bun build --bytecode`
3. **Use workers** for CPU-intensive tasks to avoid blocking main thread
4. **Stream large files** instead of loading into memory
5. **Use watch mode** in development for instant feedback

## Common Runtime Commands

```bash
# Run script with arguments
bun run script.ts arg1 arg2

# Run with specific Node version emulation
bun run --node-resolver index.ts

# Run in debug mode
bun run --inspect-brk index.ts

# Run with increased memory limit
bun run --max-old-space-size=4096 index.ts

# Run TypeScript with path aliases
bun run --bun index.ts

# Show startup performance
BUN_PRINT_STACK_TRACES=1 bun run index.ts
```

## Global Objects

### Available Globals

```typescript
// Web APIs (native)
fetch(url, options);
WebSocket(url);
ReadableStream();
Blob();
File();
TextEncoder/TextDecoder;
crypto.subtle;

// Node.js globals (compatible)
process;
Buffer;
__dirname;
__filename;
require();
module.exports;

// Bun-specific
Bun; // Bun runtime API
env; // Environment variables
```

### Bun Runtime API

```typescript
// Bun object provides runtime info and utilities
Bun.version;        // "1.3.12"
Bun.pid;            // Process ID
Bun.argv;           // Command line arguments
Bun.env;            // Environment variables (same as env)
Bun.cwd();          // Current working directory
Bun.execSync(cmd);  // Execute shell command
Bun.sleep(ms);      // Sleep for milliseconds (async)

// File operations
Bun.file("path.txt");           // Read file as Blob
Bun.read("path.txt");           // Read file as Uint8Array
Bun.write("path.txt", data);    // Write file
Bun.remove("path.txt");         // Delete file
Bun.mkdir("dir");               // Create directory
Bun.exists("path");             // Check if path exists

// Process management
Bun.spawn(["command", "arg1"]); // Spawn child process
Bun.exit(code);                 // Exit process
```

## Migration from Node.js

Most Node.js code works without modification:

```bash
# Replace 'node' with 'bun' in package.json scripts
{
  "scripts": {
    "start": "bun run index.ts",  # was: "node index.js"
    "dev": "bun run --watch index.ts",  # was: "nodemon index.js"
    "test": "bun test"  # was: "jest"
  }
}
```

See [references/08-nodejs-compat.md](references/08-nodejs-compat.md) for detailed compatibility information.
