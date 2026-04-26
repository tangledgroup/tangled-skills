# Async Programming Patterns

## Event Emitter

The `events` module provides the `EventEmitter` class, the foundation of Node.js async architecture.

```javascript
import { EventEmitter } from 'node:events';

class MyEmitter extends EventEmitter {}
const emitter = new MyEmitter();

// Register listeners
emitter.on('data', (chunk) => {
  console.log('Received:', chunk);
});

// One-time listener
emitter.once('connection', () => {
  console.log('First connection only');
});

// Emit events
emitter.emit('data', 'hello world');

// Error handling — uncaught errors crash the process
emitter.on('error', (err) => {
  console.error('Error:', err.message);
});

// Remove listeners
const listener = (data) => console.log(data);
emitter.on('data', listener);
emitter.removeListener('data', listener);
emitter.removeAllListeners('data'); // remove all for event
emitter.removeAllListeners();        // remove all events

// Listener count
emitter.listenerCount('data');       // number of listeners
```

### EventEmitter Static Methods

```javascript
import { setMaxListeners, getEventListeners } from 'node:events';

setMaxListeners(20, emitter); // change max for specific emitter
getEventListeners(emitter, 'data'); // get all listeners for event
```

### events.once — Promise Wrapper

```javascript
import { once } from 'node:events';

// Wait for next event as a promise
const [connection] = await once(server, 'connection');
console.log('New connection:', connection.remoteAddress);

// With abort signal
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000);
const [data] = await once(emitter, 'data', { signal: controller.signal });
```

### events.on — Async Iterator

```javascript
import { on } from 'node:events';

// Iterate over events as an async generator
for await (const [chunk] of on(stream, 'data')) {
  console.log('Chunk:', chunk);
}
```

## Callbacks (Error-First Pattern)

The original Node.js async pattern. Callback receives `(error, result)`.

```javascript
import fs from 'node:fs';

// Error-first callback
fs.readFile('file.txt', 'utf-8', (err, data) => {
  if (err) {
    console.error('Failed to read file:', err);
    return;
  }
  console.log(data);
});

// Nested callbacks (callback hell)
fs.readFile('config.json', 'utf-8', (err, config) => {
  if (err) return handleErr(err);
  fs.readFile(config.templatePath, 'utf-8', (err, template) => {
    if (err) return handleErr(err);
    // ... more nesting ...
  });
});
```

## Promises

```javascript
import { promises as fs } from 'node:fs';

// Promise chain
fs.readFile('file.txt', 'utf-8')
  .then((data) => data.toUpperCase())
  .then((upper) => fs.writeFile('output.txt', upper))
  .catch((err) => console.error(err));

// Parallel execution
const [file1, file2, file3] = await Promise.all([
  fs.readFile('a.txt', 'utf-8'),
  fs.readFile('b.txt', 'utf-8'),
  fs.readFile('c.txt', 'utf-8'),
]);

// Race — first to settle wins
const result = await Promise.race([
  fetchData(),
  new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000)),
]);

// Any — first to fulfill wins (rejects only if all fail)
const winner = await Promise.any([fastSource(), backupSource()]);

// AllSettled — wait for all, regardless of success/failure
const results = await Promise.allSettled([task1(), task2(), task3()]);
for (const r of results) {
  if (r.status === 'fulfilled') console.log(r.value);
  else console.error(r.reason);
}
```

## Async/Await (Preferred Style)

```javascript
import fs from 'node:fs/promises';

async function main() {
  try {
    const data = await fs.readFile('config.json', 'utf-8');
    const config = JSON.parse(data);

    // Sequential — each waits for previous
    const step1 = await processStep1(config);
    const step2 = await processStep2(step1);

    // Parallel — all start simultaneously
    const [users, posts, comments] = await Promise.all([
      fetch('/api/users'),
      fetch('/api/posts'),
      fetch('/api/comments'),
    ]);

  } catch (err) {
    console.error('Operation failed:', err.message);
  }
}

main();
```

## process.nextTick vs setImmediate

Both schedule callbacks but at different event loop phases:

```javascript
console.log('1. start');

setTimeout(() => console.log('2. setTimeout'), 0);
setImmediate(() => console.log('3. setImmediate'));
process.nextTick(() => console.log('0. nextTick'));

console.log('4. end');

// Output order:
// 1. start
// 4. end
// 0. nextTick      — runs before ANY other async callback
// 2. setTimeout    — or setImmediate (order varies between runs)
// 3. setImmediate  — check phase, after poll

// process.nextTick fires IMMEDIATELY after current operation completes
// It does NOT yield to the event loop
// Use sparingly — can starve I/O

// queueMicrotask is the web-compatible equivalent of nextTick
queueMicrotask(() => console.log('microtask'));
```

### Event Loop Phases (in order)

1. **timers** — `setTimeout`, `setInterval` callbacks
2. **pending callbacks** — I/O callbacks deferred to next iteration
3. **idle, prepare** — internal use only
4. **poll** — retrieve new I/O events, execute I/O related callbacks
5. **check** — `setImmediate` callbacks
6. **close callbacks** — `socket.on('close', ...)`

Within each phase, `process.nextTick` and microtasks run before the next phase.

## util.promisify and callbackify

```javascript
import { promisify, callbackify } from 'node:util';
import { exec, readdir } from 'node:child_process';
import fs from 'node:fs';

// Convert callback-style to promise
const execAsync = promisify(exec);
const { stdout } = await execAsync('ls -la');

// readdir with options (promisify preserves arguments)
const readDir = promisify(fs.readdir);
const files = await readDir('/path', { withFileTypes: true });

// Convert promise-style back to callback
const callbackFn = callbackify(async (filename) => {
  return await fs.readFile(filename, 'utf-8');
});
callbackFn('file.txt', (err, data) => {
  if (err) throw err;
  console.log(data);
});
```

### Custom promisify transformation

```javascript
const customPromisify = promisify((cb) => {
  // callback signature: (err, result1, result2)
  someMultiArgCallback((err, a, b) => cb(err, { a, b }));
});
const { a, b } = await customPromisify();
```

## AbortController and Signal Integration

Modern Node.js modules support `AbortSignal` for cancellation:

```javascript
const controller = new AbortController();
const { signal } = controller;

// Abort fetch
const promise = fetch('https://api.example.com/data', { signal });
setTimeout(() => controller.abort(), 5000);

// Abort with events/on
import { on } from 'node:events';
try {
  for await (const [chunk] of on(stream, 'data', { signal })) {
    process(chunk);
  }
} catch (err) {
  if (err.name === 'AbortError') console.log('Aborted');
}

// Abort timers/promises
import { setTimeout as sleep } from 'node:timers/promises';
try {
  await sleep(10000, undefined, { signal });
} catch (err) {
  if (err.name === 'AbortError') console.log('Timer aborted');
}

// Multiple signals
const combined = AbortSignal.any([signal1, signal2]);
```

## Async Local Storage (Async Context)

Track context across async boundaries without passing it explicitly:

```javascript
import { AsyncLocalStorage } from 'node:async_hooks';

const asyncLocalStorage = new AsyncLocalStorage();

function middleware(req, res, next) {
  asyncLocalStorage.run({ requestId: req.id }, () => {
    next();
  });
}

function deepFunction() {
  const context = asyncLocalStorage.getStore();
  console.log(`Request ID: ${context.requestId}`);
}
```

## EventEmitterAsyncResource

For custom event emitters that need proper async context tracking:

```javascript
import { EventEmitterAsyncResource } from 'node:events';

class MyAsyncEmitter extends EventEmitterAsyncResource {
  constructor(options) {
    super({ ...options, name: 'MyAsyncEmitter' });
  }
}
// Listeners inherit the async context of the emitter
```
