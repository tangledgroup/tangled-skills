# Advanced Features Reference

This document covers Node.js 24.14 advanced features including VM module, native addons, SQLite integration, WASI support, and single executable applications.

## VM Module (Code Execution)

### Creating Isolated Contexts

```javascript
import vm from 'node:vm';

// Create new context (isolated from global)
const context = vm.createContext({
  console: console,
  setTimeout: setTimeout
});

// Compile and run code in context
const code = `
  const message = 'Hello from VM';
  console.log(message);
`;

vm.runInContext(code, context);

// Code cannot access Node.js built-ins unless provided
const unsafeCode = `
  require('fs').readFileSync('/etc/passwd') // Will fail - no 'require'
`;

try {
  vm.runInContext(unsafeCode, context);
} catch (err) {
  console.log('Blocked:', err.message);
}
```

### Script Compilation

```javascript
import vm from 'node:vm';

// Compile script once, run multiple times
const script = new vm.Script('x + y', {
  filename: 'math.js',
  lineOffset: -1,
  columnOffset: 0,
  displayErrors: true
});

// Run with different contexts
const context1 = { x: 5, y: 10 };
console.log(script.runInContext(context1)); // 15

const context2 = { x: 100, y: 200 };
console.log(script.runInContext(context2)); // 300

// Get compiled function
const fn = script.runInThisContext();
console.log(fn({ x: 1, y: 2 })); // 3
```

### Sandboxing with Object Wrapping

```javascript
import vm from 'node:vm';

// Create sandbox with limited globals
const sandbox = {
  Math: Math,
  console: {
    log: (...args) => console.log('[Sandbox]', ...args),
    error: (...args) => console.error('[Sandbox Error]', ...args)
  },
  setTimeout: undefined, // Explicitly block
  setInterval: undefined
};

vm.createContext(sandbox);

const code = `
  const result = Math.sqrt(16);
  console.log('Square root:', result);
  
  // These will fail
  // setTimeout(() => {}, 1000); // ReferenceError
  // require('fs'); // ReferenceError
`;

vm.runInContext(code, sandbox);
```

### Module Loading in VM

```javascript
import vm from 'node:vm';
import fs from 'node:fs/promises';
import path from 'node:path';

// Create module-like environment
async function runModule(filepath) {
  const context = vm.createContext({
    console,
    setTimeout,
    Promise
  });
  
  // Mock module exports
  const exports = {};
  const module = { exports };
  
  context.exports = exports;
  context.module = module;
  
  // Read and compile code
  const code = await fs.readFile(filepath, 'utf8');
  const script = new vm.Script(code, { filename: filepath });
  
  script.runInContext(context);
  
  return module.exports;
}

// Usage
const myModule = await runModule('./my-module.js');
console.log(myModule);
```

### Timer Sandboxing

```javascript
import vm from 'node:vm';

// Safe timer implementation for sandbox
function createSafeTimers(sandbox) {
  const timers = new Map();
  let timerId = 0;
  
  sandbox.setTimeout = function(fn, delay, ...args) {
    const id = ++timerId;
    
    const realFn = () => {
      try {
        // Run in sandbox context
        vm.runInContext(fn.toString().replace('function()','function(){}'), sandbox);
      } catch (err) {
        console.error('Timer error:', err);
      }
      timers.delete(id);
    };
    
    const realId = setTimeout(realFn, delay);
    timers.set(id, realId);
    
    return id;
  };
  
  sandbox.clearTimeout = function(id) {
    const realId = timers.get(id);
    if (realId) {
      clearTimeout(realId);
      timers.delete(id);
    }
  };
  
  return sandbox;
}

const context = vm.createContext({});
createSafeTimers(context);

vm.runInContext(`
  const id = setTimeout(() => console.log('Delayed'), 100);
  // clearTimeout(id);
`, context);
```

## Native Addons (Node-API)

### C++ Addon with Node-API

```cpp
// addon.cpp
#include <node_api.h>

static napi_value Add(napi_env env, napi_callback_info info) {
  size_t argc = 2;
  napi_value args[2];
  double args_values[2];
  
  napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
  
  for (int i = 0; i < 2; i++) {
    napi_get_value_double(env, args[i], &args_values[i]);
  }
  
  double result = args_values[0] + args_values[1];
  napi_value return_value;
  napi_create_double(env, result, &return_value);
  
  return return_value;
}

static napi_value Init(napi_env env, napi_value exports) {
  napi_value fn;
  napi_create_function(env, nullptr, 0, Add, nullptr, &fn);
  napi_set_named_property(env, exports, "add", fn);
  return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

### binding.gyp Configuration

```json
// binding.gyp
{
  "targets": [
    {
      "target_name": "addon",
      "sources": ["addon.cpp"],
      "cflags!": ["-fno-exceptions"],
      "cflags_cc!": ["-fno-exceptions"],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      "dependencies": [
        "<!(node -p \"require('node-addon-api').gyp\")"
      ],
      "defines": ["NAPI_DISABLE_CPP_EXCEPTIONS"]
    }
  ]
}
```

### Using Native Addon

```javascript
// Load compiled addon
const addon = require('./build/Release/addon.node');

console.log(addon.add(2, 3)); // 5

// Or with ES modules (Node.js 16+)
import addon from './build/Release/addon.node' assert { type: 'commonjs' };
```

### Rust Addon with Neon

```rust
// src/lib.rs
use neon::prelude::*;

fn add(mut cx: FunctionContext) -> JsResult<JsNumber> {
    let a = cx.number_arg(0)?;
    let b = cx.number_arg(1)?;
    Ok(cx.number(a + b))
}

fn register_js(m: &mut JsModule) {
    m.export_function("add", add)?;
}

neon::main! {
    fn main(mut m: Mut<JsModule>) -> NeonResult<()> {
        register_js(&mut m)?;
        Ok(())
    }
}
```

### N-API Version Management

```javascript
import { addons } from 'node:process';

// Check N-API version
console.log('N-API version:', process.versions.napi);

// Check if addon is compatible
function isAddonCompatible(requiredNapiVersion) {
  const current = parseInt(process.versions.napi, 10);
  return current >= requiredNapiVersion;
}

if (isAddonCompatible(6)) {
  const addon = require('./addon.node');
  console.log(addon.add(1, 2));
} else {
  console.error('Addon requires N-API version 6 or higher');
}
```

## SQLite Module (New in Node.js 24)

### Basic Usage

```javascript
import sqlite from 'node:sqlite';

// Create database connection
const db = new sqlite.Database('example.db');

// Create table
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Insert data
const insertUser = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
insertUser.run('John Doe', 'john@example.com');
insertUser.run('Jane Smith', 'jane@example.com');

// Query data
const getUser = db.prepare('SELECT * FROM users WHERE id = ?');
const user = getUser.get(1);
console.log(user); // { id: 1, name: 'John Doe', email: 'john@example.com', ... }

// Get all users
const getAllUsers = db.prepare('SELECT * FROM users');
const users = getAllUsers.all();
console.log(users);

// Update data
const updateUser = db.prepare('UPDATE users SET email = ? WHERE id = ?');
updateUser.run('newemail@example.com', 1);

// Delete data
const deleteUser = db.prepare('DELETE FROM users WHERE id = ?');
deleteUser.run(1);

// Close connection
db.close();
```

### Transactions

```javascript
import sqlite from 'node:sqlite';

const db = new sqlite.Database('example.db');

// Manual transaction
const transaction = db.transaction((userId, amount) => {
  // Get current balance
  const account = db.prepare('SELECT balance FROM accounts WHERE id = ?').get(userId);
  
  if (account.balance < amount) {
    throw new Error('Insufficient funds');
  }
  
  // Deduct amount
  db.prepare('UPDATE accounts SET balance = balance - ? WHERE id = ?')
    .run(amount, userId);
  
  // Record transaction
  db.prepare('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, ?)')
    .run(userId, amount, 'withdrawal');
});

try {
  transaction(1, 100);
  console.log('Transaction successful');
} catch (err) {
  console.error('Transaction failed:', err.message);
  // Automatically rolled back
}

// Deferred transaction (commits if no errors)
const deferredTx = db.transaction((data) => {
  db.prepare('INSERT INTO logs (?)').run(data);
}, 'DEFERRED');

// Immediate transaction
const immediateTx = db.transaction((data) => {
  db.prepare('INSERT INTO data (?)').run(data);
}, 'IMMEDIATE');

// Exclusive transaction
const exclusiveTx = db.transaction((data) => {
  db.prepare('INSERT INTO critical (?)').run(data);
}, 'EXCLUSIVE');
```

### Prepared Statements with Parameters

```javascript
import sqlite from 'node:sqlite';

const db = new sqlite.Database('example.db');

// Single parameter
const stmt1 = db.prepare('SELECT * FROM users WHERE id = ?');
const user1 = stmt1.get(42);

// Multiple parameters
const stmt2 = db.prepare('SELECT * FROM users WHERE id > ? AND id < ?');
const users = stmt2.all(1, 100);

// Named parameters (using :name)
const stmt3 = db.prepare('SELECT * FROM users WHERE email = :email');
const user3 = stmt3.get({ email: 'john@example.com' });

// Array of values for IN clause
const stmt4 = db.prepare('SELECT * FROM users WHERE id IN (?, ?, ?)');
const users4 = stmt4.all([1, 2, 3]);

// Binding different types
const stmt5 = db.prepare(`
  INSERT INTO data (text, number, boolean, null_value, blob) 
  VALUES (?, ?, ?, ?, ?)
`);
stmt5.run('hello', 42, true, null, Buffer.from('binary'));
```

### Async Iterator Support

```javascript
import sqlite from 'node:sqlite';

const db = new sqlite.Database('example.db');

// Iterate over results
const stmt = db.prepare('SELECT * FROM large_table');

for await (const row of stmt.iterate({ batchSize: 100 })) {
  console.log(row);
  // Process each row without loading all into memory
}

// With parameters
for await (const row of stmt.iterate({ 
  batchSize: 50,
  params: [1, 1000] 
})) {
  console.log(row);
}
```

### Database Schema Management

```javascript
import sqlite from 'node:sqlite';
import fs from 'node:fs/promises';

const db = new sqlite.Database('example.db');

// Get table list
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
console.log('Tables:', tables);

// Get table schema
const schema = db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").get();
console.log('Schema:', schema.sql);

// Backup database
async function backupDatabase(sourceDb, destPath) {
  const source = new sqlite.Database(sourceDb);
  const destination = new sqlite.Database(destPath);
  
  source.backup(destination);
  
  source.close();
  destination.close();
}

await backupDatabase('production.db', 'backup.db');

// Vacuum database (reclaim space)
db.exec('VACUUM');

// Analyze for query optimization
db.exec('ANALYZE');
```

## WASI (WebAssembly System Interface)

### Running WASM Modules

```javascript
import { compile, instantiate } from 'node:wasi';
import fs from 'node:fs/promises';

// Load WASM binary
const wasmBuffer = await fs.readFile('module.wasm');

// Compile WASM module
const module = compile(wasmBuffer);

// Configure WASI environment
const wasiOptions = {
  args: ['program', 'arg1', 'arg2'],
  env: {
    HOME: '/home/user',
    PATH: '/usr/bin:/bin'
  },
  preopens: {
    '/': '/host/path',
    '/data': '/host/data'
  }
};

// Instantiate and run
const instance = instantiate(module, wasiOptions);

// Call exported functions
const result = instance.exports.main();
console.log('Result:', result);
```

### WASI File System Access

```javascript
import { instantiate } from 'node:wasi';
import fs from 'node:fs/promises';

const wasmBuffer = await fs.readFile('file-processor.wasm');

// Map host directories to WASI paths
const instance = instantiate(wasmBuffer, {
  args: ['process', '/data/input.txt'],
  preopens: {
    '/data': '/home/user/project/data'
  }
});

// WASM module can now read/write files in /data
instance.exports.process_file();
```

### WASI Clocks and Random

```javascript
import { instantiate } from 'node:wasi';

const instance = instantiate(wasmBuffer, {
  // Use real clocks (default)
  clocks: {
    realtime: true,
    monotonic: true
  },
  
  // Seed for random number generator
  random_seed: Date.now()
});

// WASI module can use time and random functions
const timestamp = instance.exports.get_time();
const randomValue = instance.exports.get_random();
```

## Single Executable Applications (SEA)

### Creating a SEA

```javascript
// sea-config.json
{
  "main": "app.js",
  "files": [
    "public/**",
    "config.json",
    "*.js"
  ],
  "output": "my-app",
  "icon": "icon.png",
  "metadata": {
    "name": "My Application",
    "version": "1.0.0",
    "description": "A single executable Node.js app"
  }
}

// Build command
node --experimental-sea-config=sea-config.json
```

### SEA Configuration Example

```json
{
  "main": "./src/index.js",
  "files": [
    "./views/**",
    "./public/**",
    "./config/*.json"
  ],
  "output": "./build/my-app",
  "metadata": {
    "name": "MyApp",
    "version": "1.0.0",
    "description": "Single Executable Application"
  },
  "windows": {
    "icon": "./assets/icon.ico",
    "requestedExecutionLevel": "asInvoker"
  },
  "macOS": {
    "icon": "./assets/icon.icns",
    "signingIdentity": "-"
  },
  "linux": {
    "icon": "./assets/icon.png"
  }
}
```

### Accessing SEA Resources

```javascript
// In your application code
import process from 'node:process';
import path from 'node:path';

// Check if running as SEA
if (process.sea) {
  console.log('Running as Single Executable Application');
  
  // Get path to SEA executable
  const seaPath = process.sea.execPath;
  console.log('SEA path:', seaPath);
}

// Access embedded files
import fs from 'node:fs/promises';

async function getEmbeddedFile(filepath) {
  if (process.sea) {
    // Read from embedded resources
    const data = await fs.readFile(process.resourcePath + '/' + filepath);
    return data;
  } else {
    // Development mode
    return await fs.readFile(filepath);
  }
}

const config = JSON.parse(await getEmbeddedFile('config.json'));
```

### SEA Development Workflow

```javascript
// index.js - Entry point for SEA
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine resource path
const resourcePath = process.resourcePath || __dirname;

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end('<h1>Hello from SEA!</h1>');
});

server.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
  console.log('Resource path:', resourcePath);
});
```

## Other Advanced Topics

### Worker Threads for CPU-intensive Tasks

```javascript
import { Worker } from 'node:worker_threads';
import { fileURLToPath } from 'node:url';

// Main thread
const worker = new Worker(fileURLToPath(new URL('./worker.js', import.meta.url)), {
  workerData: { initialValue: 1000000 }
});

worker.on('message', (result) => {
  console.log('Result from worker:', result);
});

worker.on('error', (err) => {
  console.error('Worker error:', err);
});

worker.on('exit', (code) => {
  console.log(`Worker exited with code: ${code}`);
});

// Worker thread (worker.js)
import { parentPort, workerData } from 'node:worker_threads';

function cpuIntensive(value) {
  let sum = 0;
  for (let i = 0; i < value * 1e6; i++) {
    sum += Math.sqrt(i) * Math.sin(i);
  }
  return sum;
}

const result = cpuIntensive(workerData.initialValue);
parentPort.postMessage(result);
```

### MessageChannel for Thread Communication

```javascript
import { MessageChannel } from 'node:worker_threads';

const { port1, port2 } = new MessageChannel();

port1.on('message', (msg) => {
  console.log('Received in main:', msg);
  port1.postMessage({ reply: 'Got it!' });
});

// In worker thread
port2.postMessage({ data: 'Hello from worker' });

port2.on('message', (msg) => {
  console.log('Received in worker:', msg.reply);
});
```

### SharedArrayBuffer for Zero-Copy

```javascript
import { Worker } from 'node:worker_threads';
import { fileURLToPath } from 'node:url';
import { isSharedArrayBuffer } from 'node:util/types';

// Create shared buffer
const sharedBuffer = new SharedArrayBuffer(1024 * 1024); // 1MB
const array = new Float64Array(sharedBuffer);

// Verify it's shared
console.log('Is shared:', isSharedArrayBuffer(sharedBuffer));

// Pass to worker
const worker = new Worker(fileURLToPath('./worker.js'), {
  workerData: { buffer: sharedBuffer }
});

// Both main and worker can read/write same memory
for (let i = 0; i < array.length; i++) {
  array[i] = i * Math.PI;
}
```

### Performance Optimization Tips

1. **Use streams for large data**: Avoid loading entire files into memory
2. **Enable HTTP keep-alive**: Reduce connection overhead
3. **Use clustering**: Utilize all CPU cores
4. **Profile before optimizing**: Use `--prof` and Chrome DevTools
5. **Cache expensive operations**: Use LRU caches for repeated computations
6. **Use worker threads**: Offload CPU-intensive tasks
7. **Enable compression**: Use gzip for large responses
8. **Monitor event loop lag**: Keep it under 5ms average
