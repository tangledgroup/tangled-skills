# Testing and Debugging Reference

This document covers Node.js 24.14 testing with the built-in test runner, assertions, debugging with the inspector, REPL usage, and diagnostic reporting.

## Test Runner Module

### Basic Tests

```javascript
import { test, describe } from 'node:test';
import assert from 'node:assert';
import { ok, strict } from 'node:assert/strict';

// Simple test
test('adds numbers correctly', () => {
  const result = 2 + 2;
  ok(result === 4, '2 + 2 should equal 4');
});

// Test with async operation
test('fetches data from API', async () => {
  const response = await fetch('https://api.example.com/data');
  ok(response.ok, 'Response should be OK');
  
  const data = await response.json();
  strict.equal(data.status, 'success');
});

// Test that throws error
test('throws on invalid input', () => {
  assert.throws(() => {
    throw new Error('Expected error');
  }, Error);
});

// Test with timeout
test('completes within timeout', async () => {
  await new Promise(resolve => setTimeout(resolve, 100));
  ok(true);
}, { timeout: 5000 });
```

### Test Organization with Describe

```javascript
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

describe('Math operations', () => {
  test('addition', () => {
    assert.equal(1 + 1, 2);
  });
  
  test('subtraction', () => {
    assert.equal(5 - 3, 2);
  });
  
  test('multiplication', () => {
    assert.equal(3 * 4, 12);
  });
});

describe('User authentication', () => {
  let user;
  
  describe.before(() => {
    // Setup before all tests in this describe block
    user = { id: 1, name: 'Test User' };
  });
  
  describe.after(() => {
    // Cleanup after all tests
    user = null;
  });
  
  test('user has ID', () => {
    assert.ok(user.id);
  });
  
  test('user has name', () => {
    assert.ok(user.name);
  });
});
```

### Test Fixtures

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';

// Using fixtures for setup
test('processes user data', async (t) => {
  // Create fixture
  const userData = {
    id: 123,
    name: 'John Doe',
    email: 'john@example.com'
  };
  
  // Use t.before and t.after for per-test setup/teardown
  await t.before(async () => {
    console.log('Setting up test fixture');
  });
  
  await t.after(async () => {
    console.log('Cleaning up test fixture');
  });
  
  // Run actual test
  assert.ok(userData.id);
  assert.ok(userData.name);
});

// Using mock functions
test('calls callback on success', async (t) => {
  const mockCallback = t.mock.fn();
  
  // Function that calls callback
  function process(data, callback) {
    callback(null, data);
  }
  
  process('data', mockCallback);
  
  assert.ok(mockCallback.mock.calls.length > 0);
});
```

### Running Tests

```bash
# Run all tests in directory
node --test

# Run specific test file
node --test ./tests/math.test.js

# Run with reporter
node --test --reporter=spec

# Available reporters: spec, tap, junit, json, lcov

# Run with coverage
node --test --experimental-test-coverage

# Run tests matching pattern
node --test --test-name-pattern="authentication"

# Run in watch mode (Node.js 18+)
node --test --watch
```

### Test Reporters Output

```bash
# Spec reporter (default)
▶ Math operations
  ✔ addition (1.23ms)
  ✔ subtraction (0.45ms)
  ✔ multiplication (0.32ms)
✔ Math operations (3.12ms)

# TAP format
TAP version 13
1..3
ok 1 - addition
ok 2 - subtraction
ok 3 - multiplication

# JSON output
{
  "tests": [
    {
      "name": "addition",
      "duration_ms": 1.23,
      "type": "test",
      "state": "pass"
    }
  ]
}
```

### Coverage Reports

```bash
# Generate coverage report
node --test --experimental-test-coverage ./tests/

# Output to directory
node --test --experimental-test-coverage --test-reporter=lcov > coverage.lcov

# View in browser (with lcov tools)
genhtml coverage.lcov -o coverage/html
open coverage/html/index.html
```

## Assert Module

### Basic Assertions

```javascript
import assert from 'node:assert/strict'; // Use strict mode for === comparisons

// Value assertions
assert.ok(true, 'Value should be truthy');
assert.equal(1, 1, 'Values are equal (==)');
assert.strictEqual(1, 1, 'Values are strictly equal (===)');
assert.notEqual(1, 2, 'Values are not equal');
assert.notStrictEqual(1, '1', 'Values are not strictly equal');

// Deep equality
assert.deepEqual({ a: 1 }, { a: 1 });
assert.deepStrictEqual({ a: 1 }, { a: 1 });
assert.notDeepEqual({ a: 1 }, { a: 2 });

// Type assertions
assert.strictEqual(typeof value, 'string');
assert.ok(Array.isArray([]));
assert.ok(value instanceof MyClass);

// Value constraints
assert.ifError(null); // Passes if falsy
assert.doesNotThrow(() => { /* no error */ });
```

### Error Assertions

```javascript
import assert from 'node:assert/strict';

// Assert that function throws
assert.throws(
  () => { throw new Error('Expected'); },
  Error,
  'Should throw Error'
);

// Assert with specific message
assert.throws(
  () => { throw new Error('Not found'); },
  { name: 'Error', message: /not found/i }
);

// Assert that function does NOT throw
assert.doesNotThrow(() => {
  console.log('No error here');
});

// Custom error class
class NotFoundError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NotFoundError';
  }
}

assert.throws(
  () => { throw new NotFoundError('User not found'); },
  NotFoundError
);
```

### Deep Equality Options

```javascript
import assert from 'node:assert/strict';

// Custom deep equality comparator
const options = {
  strictCheck: false,
  cmp(a, b) {
    // Custom comparison logic
    if (a instanceof Date && b instanceof Date) {
      return a.getTime() === b.getTime();
    }
    return undefined; // Fall back to default
  }
};

assert.deepEqual(
  new Date('2024-01-01'),
  new Date('2024-01-01'),
  options
);

// Ignore specific properties
const obj1 = { a: 1, b: 2, timestamp: Date.now() };
const obj2 = { a: 1, b: 2, timestamp: Date.now() + 1 };

assert.deepEqual(obj1, obj2, {
  cmp(a, b) {
    if (a.key === 'timestamp' || b.key === 'timestamp') {
      return true; // Ignore timestamp differences
    }
    return undefined;
  }
});
```

### Assertion Messages

```javascript
import assert from 'node:assert/strict';

// Custom error messages
try {
  assert.strictEqual(1, 2, 'One should equal two');
} catch (err) {
  console.error(err.message); // "One should equal two"
}

// Template literal messages
const expected = 4;
const actual = 5;

assert.strictEqual(
  actual,
  expected,
  `Expected ${expected} but got ${actual}`
);

// Dynamic messages
function validateUser(user) {
  assert.ok(user.id, 'User must have an ID');
  assert.ok(user.name, `User must have a name (got: ${user.name})`);
  assert.match(
    user.email,
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    'Email must be valid'
  );
}
```

## Inspector and Debugging

### Starting the Inspector

```bash
# Start with inspector on default port
node --inspect app.js
# Listening on ws://127.0.0.1:9229

# Specify host and port
node --inspect=0.0.0.0:9229 app.js
# Accessible from other machines

# Pause execution at start
node --inspect-brk app.js
# Breaks on first line of user code

# Inspector with web UI URL
node --inspect-publish-uid app.js
# Prints URL for Chrome DevTools
```

### Connecting with Chrome DevTools

1. Start Node.js with `--inspect` flag
2. Open Chrome browser
3. Navigate to `chrome://inspect`
4. Click "Open dedicated DevTools" under target
5. Use full DevTools interface

### Debugger API Commands

```javascript
// In the Debug console in Chrome DevTools or via REPL

// Set breakpoint at line
DB.setBreakpoint('app.js', 42);

// Set conditional breakpoint
DB.setBreakpoint('app.js', 42, 'userId === 123');

// Continue execution
DB.continue();

// Step over (next line)
DB.stepOver();

// Step into (function call)
DB.stepInto();

// Step out (return from function)
DB.stepOut();

// Evaluate expression
DB.evaluate('user.name');

// Get stack trace
DB.getStackTrace();

// List functions in scope
DB.listFunctions();

// Restart with arguments
DB.restart('arg1', 'arg2');
```

### Programmatic Debugging

```javascript
import { debug } from 'node:inspector';

// Enable debugger programmatically
debug port = debug.enable();

// Set breakpoint
debug.setBreakpoint({
  scriptName: 'app.js',
  lineNumber: 42,
  columnNumber: 0
});

// Continue execution
debug.continue();

// Get call stack
const stack = debug.getStackTrace();
console.log(stack);

// Disable debugger
debug.disable();
```

### Remote Debugging

```javascript
import { inspect } from 'node:util';
import http from 'node:http';

// Create debugging proxy server
const proxyServer = http.createServer((req, res) => {
  // Proxy to Node.js inspector
  const options = {
    hostname: 'localhost',
    port: 9229,
    path: req.url
  };
  
  // Implementation depends on proxy library
});

proxyServer.listen(8080);
```

### Performance Profiling with Inspector

1. Open Chrome DevTools connected to Node.js
2. Go to "Performance" tab
3. Click "Record"
4. Run your application code
5. Stop recording
6. Analyze:
   - Event log for async operations
   - Bottom-up for hot functions
   - Call tree for execution flow
   - Memory allocations

## REPL (Read-Eval-Print Loop)

### Starting REPL

```bash
# Start basic REPL
node

# Start with inspect mode (shows values)
node --inspect

# Start with specific module loaded
node -e "require('dotenv').config()"

# Load configuration file
node --eval "$(cat .replrc)"
```

### REPL Commands

```javascript
// In REPL:

// .help - Show help
.help

// .load <filename> - Load file into REPL
.load ./script.js

// .save <filename> - Save session to file
.save ./session.js

// .clear - Clear REPL buffer
.clear

// .exit or Ctrl+D - Exit REPL
.exit

// .break or Ctrl+C - Cancel current command
.break

// Multi-line input (auto-detects)
const obj = {
  name: 'value',
  items: [1, 2, 3]
}; // Press Enter twice to execute

// Access previous results with _
_ + 10

// Access specific history with _1, _2, etc.
_1 + _2
```

### REPL Modes

```javascript
// In REPL:

// List mode - shows all commands
.list

// Edit mode - opens editor for multi-line
.edit

// Debugger mode (when inspector is active)
.debugger

// Sandbox mode - isolated context
.sandbox
```

### REPL Configuration

Create `.replrc` file:

```javascript
// .replrc
const util = require('node:util');

// Pretty print results
util.inspect.defaultOptions.depth = 10;
util.inspect.defaultOptions.colors = true;

// Auto-load modules
require('dotenv').config();

// Custom prompt
setup REPL with custom settings
```

### Interactive Development

```javascript
// In REPL:

// Import and test module
const fs = require('node:fs/promises');

// Test async operations
await fs.readFile('package.json', 'utf8');
JSON.parse(_).name;

// Define and test functions
function add(a, b) { return a + b; }
add(2, 3);

// Use arrow functions
const multiply = (a, b) => a * b;
multiply(4, 5);

// Debug objects
const user = { id: 1, name: 'John' };
util.inspect(user, { depth: null, colors: true });

// Test regex patterns
/^\d{3}-\d{2}-\d{4}$/.test('123-45-6789');

// Profile code execution
const start = Date.now();
for (let i = 0; i < 1e6; i++) Math.sqrt(i);
Date.now() - start;
```

## Report Module

### Diagnostic Reports

```javascript
import { report } from 'node:report';

// Configure report options
report.addReporter({
  getReport: () => ({
    customData: 'value',
    timestamp: Date.now()
  }),
  applicationName: 'my-app'
});

// Generate report to stdout
report.report();

// Generate report to file
import fs from 'node:fs/promises';

await fs.writeFile('report.json', JSON.stringify(report.getReport(), null, 2));

// Trigger report on signal
process.on('SIGUSR2', () => {
  console.log('Generating diagnostic report...');
  report.report();
});
```

### Report Configuration

```javascript
import { report } from 'node:report';

// Configure what to include
report.addReporter({
  getReport: (context) => ({
    heapStatistics: context.heapStatistics,
    resourceUsage: context.resourceUsage,
    openHandles: context.openHandles
  })
});

// Set report directory
import os from 'node:os';
import path from 'node:path';

const reportDir = path.join(os.tmpdir(), 'node-reports');
report.setReportDirectory(reportDir);

// Generate numbered reports
report.report(); // reports/report-1.json
report.report(); // reports/report-2.json
```

### CLIF Report Format

```bash
# Enable CLIF (Chrome Linear IR Format) reports
export NODE_OPTIONS="--generate-report-on-crash"

# Or programmatically
import { report } from 'node:report';

report.setReportDirectory('./reports');
report.report();
```

## Troubleshooting Common Issues

### Memory Leaks

```javascript
// 1. Enable garbage collection tracking
export NODE_OPTIONS="--trace-gc --expose-gc"

// 2. Monitor heap usage
import v8 from 'node:v8';

setInterval(() => {
  const stats = v8.getHeapStatistics();
  console.log('Heap used:', (stats.used_heap_size / 1024 / 1024).toFixed(2), 'MB');
}, 5000);

// 3. Take heap snapshots
import fs from 'node:fs/promises';

process.on('SIGUSR2', async () => {
  const snapshot = v8.getHeapSnapshot();
  await fs.writeFile('heap-snapshot.json', JSON.stringify(snapshot));
  console.log('Heap snapshot saved');
});

// 4. Common leak patterns to check:
// - Unclosed streams and sockets
// - Event listeners not removed
// - Global variables accumulating data
// - Closures holding references
```

### Event Loop Blocking

```javascript
import { performance } from 'node:perf_hooks';

// Monitor event loop lag
function monitorEventLoop() {
  let lastTick = performance.now();
  
  setImmediate(function checkLag() {
    const now = performance.now();
    const lag = now - lastTick;
    
    if (lag > 5) {
      console.warn(`Event loop lag: ${lag.toFixed(2)}ms`);
    }
    
    lastTick = now;
    setImmediate(checkLag);
  });
}

// Common causes:
// - Synchronous file operations
// - Heavy CPU computations
// - Large JSON.parse/stringify
// - Blocking native modules
```

### High Memory Usage

```javascript
import v8 from 'node:v8';

function checkMemoryUsage() {
  const stats = v8.getHeapStatistics();
  
  const heapUsed = stats.used_heap_size / 1024 / 1024;
  const heapTotal = stats.heap_size / 1024 / 1024;
  const limit = stats.heap_size_limit / 1024 / 1024;
  
  console.log(`Memory: ${heapUsed.toFixed(2)}MB / ${heapTotal.toFixed(2)}MB (limit: ${limit.toFixed(2)}MB)`);
  
  if (heapUsed > limit * 0.9) {
    console.warn('High memory usage! Consider increasing heap size.');
  }
}

// Increase heap size if needed:
# node --max-old-space-size=4096 app.js
```

### Debugging Child Processes

```javascript
import { fork } from 'node:child_process';

// Fork with debug flag
const worker = fork('./worker.js', [], {
  execArgv: ['--inspect=127.0.0.1:9230']
});

console.log('Worker debugging on ws://127.0.0.1:9230');

// Or spawn with debug
import { spawn } from 'node:child_process';

const child = spawn('node', ['--inspect', 'script.js'], {
  stdio: 'inherit'
});
```

### Performance Troubleshooting Checklist

1. **Slow startup**: Check module loading, use `--prof` for profiling
2. **High CPU**: Profile with inspector, check for infinite loops
3. **Memory growth**: Take heap snapshots, check for leaks
4. **Event loop lag**: Monitor with perf_hooks, reduce sync operations
5. **Network latency**: Check DNS, enable keep-alive, use connection pooling
6. **Database slow**: Add query logging, check indexes, use connection pool

### Useful Debug Flags

```bash
# Trace garbage collection
node --trace-gc app.js

# Print heap statistics on exit
node --print-histogram app.js

# Track async operations
node --trace-async-apps app.js

# Show deprecation warnings
node --trace-deprecation app.js

# Generate stack trace on uncaught exception
node --trace-uncaught app.js

# All V8 flags
node --v8-options

# Memory tracking
node --track-heap-objects app.js
```
