# Async Programming Reference

This document covers Node.js 24.14 async programming patterns including Events, Timers, Async Hooks, Diagnostics Channel, and Performance Hooks.

## EventEmitter Module

### Basic Usage

```javascript
import { EventEmitter } from 'node:events';

class MyEmitter extends EventEmitter {}

const emitter = new MyEmitter();

// Emit an event
emitter.emit('greet', { name: 'World' });

// Listen for event
emitter.on('greet', (data) => {
  console.log(`Hello, ${data.name}!`);
});

// One-time listener
emitter.once('greet', (data) => {
  console.log('This runs only once:', data.name);
});

// Remove listener
function goodbye(data) {
  console.log('Goodbye,', data.name);
}

emitter.on('greet', goodbye);
emitter.off('greet', goodbye); // Remove specific listener

// Remove all listeners for event
emitter.removeAllListeners('greet');

// Remove all listeners
emitter.removeAllListeners();
```

### Event Listener Patterns

```javascript
import { EventEmitter } from 'node:events';

const emitter = new EventEmitter();

// Set max listeners limit
emitter.setMaxListeners(20);

// Get current max limit
console.log(emitter.getMaxListeners()); // 20

// Get listener count
console.log(emitter.listenerCount('greet'));

// Get all listeners for event
const listeners = emitter.listeners('greet');
console.log('Listeners:', listeners.length);

// Check if has listeners
if (emitter.hasListeners('greet')) {
  console.log('Has greet listeners');
}

// Emit with multiple arguments
emitter.emit('data', 'arg1', 'arg2', 'arg3');

emitter.on('data', (a, b, c) => {
  console.log(a, b, c); // arg1 arg2 arg3
});
```

### Async Event Handlers

```javascript
import { EventEmitter } from 'node:events';

class AsyncEmitter extends EventEmitter {
  async process(data) {
    try {
      await this.doWork(data);
      this.emit('complete', data);
    } catch (err) {
      this.emit('error', err);
    }
  }
  
  async doWork(data) {
    // Simulate async work
    await new Promise(resolve => setTimeout(resolve, 100));
    return data.toUpperCase();
  }
}

const emitter = new AsyncEmitter();

emitter.on('complete', (data) => {
  console.log('Completed:', data);
});

emitter.on('error', (err) => {
  console.error('Error:', err);
});

// Handle uncaught errors
emitter.on('error', (err) => {
  console.error('Unhandled error:', err);
});

await emitter.process('hello');
```

### Error Handling with Events

```javascript
import { EventEmitter } from 'node:events';

class SafeEmitter extends EventEmitter {
  constructor() {
    super();
    
    // Handle uncaught errors
    this.on('error', (err) => {
      console.error('Uncaught error:', err);
      // Don't crash, just log
    });
  }
  
  unsafeOperation() {
    try {
      throw new Error('Something went wrong');
    } catch (err) {
      // Emit error event instead of crashing
      this.emit('error', err);
    }
  }
}

const emitter = new SafeEmitter();
emitter.unsafeOperation(); // Won't crash
```

### Event-Driven API Pattern

```javascript
import { EventEmitter } from 'node:events';

class DataProcessor extends EventEmitter {
  constructor() {
    super();
    this.buffer = [];
  }
  
  write(data) {
    this.buffer.push(data);
    this.emit('data', data);
    
    // Emit chunk when buffer reaches size
    if (this.buffer.length >= 10) {
      this.emit('chunk', this.buffer.slice());
      this.buffer = [];
    }
  }
  
  end() {
    if (this.buffer.length > 0) {
      this.emit('chunk', this.buffer);
    }
    this.emit('end');
  }
}

const processor = new DataProcessor();

processor.on('data', (data) => {
  console.log('Data:', data);
});

processor.on('chunk', (chunk) => {
  console.log('Processing chunk of', chunk.length, 'items');
});

processor.on('end', () => {
  console.log('All data processed');
});

for (let i = 0; i < 25; i++) {
  processor.write(i);
}
processor.end();
```

## Timers Module

### Basic Timers

```javascript
import timers from 'node:timers';

// setTimeout - one-time execution
const timeoutId = setTimeout(() => {
  console.log('Executed after 1 second');
}, 1000);

// Clear timeout before it executes
clearTimeout(timeoutId);

// setInterval - repeated execution
const intervalId = setInterval(() => {
  console.log('Executed every 500ms');
}, 500);

// Clear interval after some time
setTimeout(() => {
  clearInterval(intervalId);
  console.log('Interval cleared');
}, 2000);

// setImmediate - next iteration of event loop
setImmediate(() => {
  console.log('Runs in next event loop iteration');
});

console.log('This runs first');
```

### Timer Promises (Node.js 16+)

```javascript
import timers from 'node:timers/promises';

// Delay with promise
await timers.setTimeout(1000);
console.log('Waited 1 second');

// Timeout with abort signal
const controller = new AbortController();

try {
  await timers.setTimeout(5000, { signal: controller.signal });
} catch (err) {
  if (err.name === 'AbortError') {
    console.log('Timeout was aborted');
  }
}

// Abort after 1 second
setTimeout(() => controller.abort(), 1000);

// Interval as async iterator
async function countDown(seconds) {
  const interval = 1000;
  
  for await (const _ of timers.interval(interval)) {
    console.log(seconds--);
    
    if (seconds < 0) {
      break;
    }
  }
}

await countDown(5);
```

### Timer Management

```javascript
import timers from 'node:timers';

// Track active timers
const activeTimers = new Set();

function createTrackedTimer(fn, delay) {
  const id = setTimeout(fn, delay);
  activeTimers.add(id);
  
  return () => {
    clearTimeout(id);
    activeTimers.delete(id);
  };
}

// Cancel all tracked timers
function cancelAllTimers() {
  for (const id of activeTimers) {
    clearTimeout(id);
  }
  activeTimers.clear();
}

// Usage
const stop1 = createTrackedTimer(() => console.log('Timer 1'), 5000);
const stop2 = createTrackedTimer(() => console.log('Timer 2'), 10000);

// Cancel timer 1 early
stop1();

// Or cancel all
// cancelAllTimers();
```

### Debounce and Throttle

```javascript
import timers from 'node:timers';

// Debounce - delay execution until after pause
function debounce(fn, delay) {
  let timeoutId;
  
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Throttle - limit execution frequency
function throttle(fn, limit) {
  let inThrottle;
  
  return function(...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Usage
const debouncedLog = debounce((msg) => console.log(msg), 300);
debouncedLog('typing...'); // Won't log immediately
debouncedLog('more typing...'); // Won't log yet
// After 300ms of no calls: logs "more typing..."

const throttledClick = throttle(() => console.log('clicked!'), 1000);
throttledClick(); // Logs immediately
throttledClick(); // Ignored
throttledClick(); // Ignored
// After 1 second: can log again
```

### NextTick vs SetImmediate

```javascript
import { nextTick } from 'node:timers';

console.log('1. Start');

setTimeout(() => {
  console.log('2. setTimeout');
}, 0);

setImmediate(() => {
  console.log('3. setImmediate');
});

nextTick(() => {
  console.log('4. nextTick');
});

Promise.resolve().then(() => {
  console.log('5. Promise');
});

console.log('6. End');

// Output order:
// 1. Start
// 6. End
// 4. nextTick (runs before I/O)
// 5. Promise (microtask queue)
// 2. setTimeout (macrotask)
// 3. setImmediate (next event loop iteration)
```

## Async Hooks Module

### Tracking Async Operations

```javascript
import async_hooks from 'node:async_hooks';
import fs from 'node:fs/promises';

const executionStack = [];

const hook = async_hooks.createHook({
  init(asyncId, type, trigger) {
    console.log(`init: ${asyncId} (${type}) triggered by ${trigger?.constructor.name}`);
    executionStack.push(asyncId);
  },
  
  destroy(asyncId) {
    console.log(`destroy: ${asyncId}`);
    executionStack.pop();
  },
  
  before(asyncId) {
    console.log(`before: ${asyncId}`);
  },
  
  after(asyncId) {
    console.log(`after: ${asyncId}`);
  },
  
  promiseResolve(asyncId) {
    console.log(`promiseResolve: ${asyncId}`);
  }
});

hook.enable();

// Test with async operation
fs.readFile('package.json', 'utf8')
  .then(data => console.log('File loaded'))
  .finally(() => hook.disable());
```

### Context Tracking

```javascript
import async_hooks from 'node:async_hooks';

const AsyncLocalStorage = async_hooks.AsyncLocalStorage;

const store = new AsyncLocalStorage();

function logWithContext() {
  const context = store.getStore();
  console.log('Current context:', context);
}

// Without context
logWithContext(); // Current context: undefined

// With context
store.run({ requestId: '123', userId: '456' }, () => {
  logWithContext(); // Current context: { requestId: '123', userId: '456' }
  
  // Nested async operations maintain context
  setTimeout(() => {
    logWithContext(); // Still has context
  }, 100);
  
  Promise.resolve().then(() => {
    logWithContext(); // Still has context
  });
});

// After store.run(), context is gone
setTimeout(() => {
  logWithContext(); // Current context: undefined
}, 200);
```

### Request ID Propagation

```javascript
import async_hooks from 'node:async_hooks';
import http from 'node:http';

const AsyncLocalStorage = async_hooks.AsyncLocalStorage;
const requestStore = new AsyncLocalStorage();

// Middleware to set request context
function requestIdMiddleware(req, res, next) {
  const requestId = Math.random().toString(36).slice(2);
  
  requestStore.run({ requestId }, () => {
    console.log(`Request ${requestId} started`);
    
    // All async operations within this callback have the context
    next();
  });
}

// Logging that includes request ID
function log(message) {
  const context = requestStore.getStore();
  const prefix = context ? `[${context.requestId}]` : '';
  console.log(`${prefix} ${message}`);
}

// Usage in server
const server = http.createServer((req, res) => {
  const context = requestStore.getStore();
  log(`Received request to ${req.url}`);
  
  // Simulate async operation
  setTimeout(() => {
    log('Async operation completed');
    res.end('Done');
  }, 100);
});

server.listen(3000);
```

## Diagnostics Channel Module

### Publishing Events

```javascript
import { channel } from 'node:diagnostics_channel';

const myChannel = channel('my-app:event');

// Subscribe to events
myChannel.subscribe((message, type) => {
  console.log('Event received:', type, message);
});

// Publish events
myChannel.publish({ data: 'hello' }, 'greeting');
myChannel.publish({ userId: 123 }, 'user-action');

// Unsubscribe when done
// myChannel.unsubscribe(listener);
```

### Tracing Function Calls

```javascript
import { channel } from 'node:diagnostics_channel';

const traceChannel = channel('app:trace');

function traceFunction(fn, name) {
  return function(...args) {
    const start = Date.now();
    
    traceChannel.publish({
      event: 'start',
      function: name,
      args
    }, 'trace');
    
    try {
      const result = fn.apply(this, args);
      
      traceChannel.publish({
        event: 'end',
        function: name,
        duration: Date.now() - start,
        result
      }, 'trace');
      
      return result;
    } catch (err) {
      traceChannel.publish({
        event: 'error',
        function: name,
        error: err.message
      }, 'trace');
      
      throw err;
    }
  };
}

// Usage
const slowFunction = traceFunction(
  (x) => {
    // Simulate work
    for (let i = 0; i < 1e6; i++) Math.sqrt(i);
    return x * 2;
  },
  'slowFunction'
);

// Subscribe to trace events
traceChannel.subscribe((message) => {
  console.log('Trace:', message);
});

slowFunction(5);
```

### Database Query Tracking

```javascript
import { channel } from 'node:diagnostics_channel';

const dbChannel = channel('db:query');

// Subscribe once in your app
dbChannel.subscribe((message) => {
  if (message.event === 'error') {
    console.error('Database error:', message.error);
  } else if (message.event === 'slow') {
    console.warn(`Slow query: ${message.duration}ms - ${message.query}`);
  }
});

// Wrap database operations
function trackQuery(query, params) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    
    dbChannel.publish({
      event: 'start',
      query,
      params
    }, 'query');
    
    // Simulate query execution
    setTimeout(() => {
      const duration = Date.now() - start;
      
      if (duration > 1000) {
        dbChannel.publish({
          event: 'slow',
          query,
          duration
        }, 'query');
      }
      
      resolve({ rows: [], duration });
    }, Math.random() * 2000);
  });
}

// Usage
await trackQuery('SELECT * FROM users WHERE id = ?', [123]);
```

## Performance Hooks Module

### Measuring Execution Time

```javascript
import { performance } from 'node:perf_hooks';

// High-resolution time
const start = performance.now();

// Do some work
for (let i = 0; i < 1e6; i++) {
  Math.sqrt(i);
}

const end = performance.now();
console.log(`Operation took ${end - start} milliseconds`);

// Timeline with named events
performance.mark('start-operation');

// ... operation ...

performance.mark('end-operation');

performance.measure('operation-duration', 'start-operation', 'end-operation');

// Get measurement
const measures = performance.getEntries();
console.log(measures);

// Clear entries
performance.clearMarks();
performance.clearMeasures();
```

### HTTP Request Timing

```javascript
import { performance } from 'node:perf_hooks';
import http from 'node:http';

function timeRequest(url) {
  return new Promise((resolve, reject) => {
    performance.mark('request-start');
    
    const req = http.get(url, (res) => {
      performance.mark('response-start');
      
      let data = '';
      res.on('data', chunk => data += chunk);
      
      res.on('end', () => {
        performance.mark('response-end');
        
        performance.measure('dns-and-connect', 'request-start', 'response-start');
        performance.measure('download-time', 'response-start', 'response-end');
        performance.measure('total-request-time', 'request-start', 'response-end');
        
        const measures = performance.getEntriesByName('total-request-time');
        resolve({
          data,
          totalTime: measures[0].duration
        });
      });
    });
    
    req.on('error', reject);
  });
}

// Usage
const result = await timeRequest('http://example.com');
console.log(`Total time: ${result.totalTime.toFixed(2)}ms`);
```

### Monitoring Event Loop Delay

```javascript
import { performance } from 'node:perf_hooks';

function monitorEventLoopDelay() {
  const delays = [];
  const maxSamples = 100;
  
  function measure() {
    const start = performance.now();
    
    setImmediate(() => {
      const delay = performance.now() - start;
      delays.push(delay);
      
      if (delays.length >= maxSamples) {
        const avg = delays.reduce((a, b) => a + b, 0) / delays.length;
        const p95 = delays.toSorted()[Math.floor(maxSamples * 0.95)];
        
        console.log(`Event loop delay - Avg: ${avg.toFixed(2)}ms, P95: ${p95.toFixed(2)}ms`);
        
        if (avg > 5) {
          console.warn('High event loop delay detected!');
        }
      } else {
        measure();
      }
    });
  }
  
  measure();
}

monitorEventLoopDelay();
```

### Performance Observer

```javascript
import { performance, PerformanceObserver } from 'node:perf_hooks';

// Observe marks as they're created
const markObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`Mark: ${entry.name} at ${entry.startTime.toFixed(2)}ms`);
  }
});

markObserver.observe({ entryTypes: ['mark'] });

performance.mark('step-1');
performance.mark('step-2');
performance.mark('step-3');

// Observe measures
const measureObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`Measure: ${entry.name} = ${entry.duration.toFixed(2)}ms`);
  }
});

measureObserver.observe({ entryTypes: ['measure'] });

performance.measure('step-1-to-2', 'step-1', 'step-2');
performance.measure('step-2-to-3', 'step-2', 'step-3');

// Cleanup
markObserver.disconnect();
measureObserver.disconnect();
```

### Resource Timing

```javascript
import { performance } from 'node:perf_hooks';

// Get resource timing for loaded modules
function getModuleLoadTimes() {
  const resources = performance.getEntriesByType('resource');
  
  for (const resource of resources) {
    console.log(`${resource.name}:`);
    console.log(`  Duration: ${resource.duration.toFixed(2)}ms`);
    console.log(`  Fetch start: ${resource.fetchStart.toFixed(2)}ms`);
    console.log(`  Download end: ${resource.responseEnd.toFixed(2)}ms`);
  }
}

getModuleLoadTimes();
```

## Best Practices

### Error Handling in Async Code

```javascript
// Pattern 1: Try-catch with async/await
async function safeOperation() {
  try {
    const result = await riskyOperation();
    return result;
  } catch (err) {
    console.error('Operation failed:', err.message);
    throw err; // Re-throw or handle
  }
}

// Pattern 2: Promise with .catch()
riskyOperation()
  .then(result => console.log(result))
  .catch(err => console.error(err));

// Pattern 3: Event-based error handling
emitter.on('error', (err) => {
  // Handle error without crashing
  logger.error(err);
});
```

### Timeout for Async Operations

```javascript
import { setTimeout } from 'node:timers/promises';

async function operationWithTimeout(operation, timeoutMs) {
  const timeout = setTimeout(timeoutMs);
  
  try {
    return await Promise.race([operation, timeout]);
  } catch (err) {
    if (err.code === 'ETIMEOUT') {
      throw new Error('Operation timed out');
    }
    throw err;
  } finally {
    // Clear timeout if operation completed
    clearTimeout(timeout);
  }
}

// Usage
try {
  const result = await operationWithTimeout(slowOperation(), 5000);
  console.log(result);
} catch (err) {
  console.error(err.message);
}
```

### Context Preservation Across Async Boundaries

```javascript
import async_hooks from 'node:async_hooks';

const AsyncLocalStorage = async_hooks.AsyncLocalStorage;
const contextStore = new AsyncLocalStorage();

// Middleware pattern
function withContext(context, fn) {
  return function(...args) {
    return contextStore.run(context, () => fn.apply(this, args));
  };
}

// Usage in HTTP server
app.use((req, res, next) => {
  const ctx = {
    requestId: generateId(),
    userId: req.headers['x-user-id'],
    startTime: Date.now()
  };
  
  withContext(ctx, next)(req, res);
});

// Access context anywhere in the call chain
function log(message) {
  const ctx = contextStore.getStore();
  if (ctx) {
    console.log(`[${ctx.requestId}] ${message}`);
  } else {
    console.log(message);
  }
}
```
