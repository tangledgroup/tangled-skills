# Testing and Debugging

## Built-in Test Runner (node:test)

Run tests with `node --test` — no external dependencies needed.

```bash
node --test                     # run all test files
node --test test/**/*.test.js   # specific pattern
node --test --watch             # watch mode
node --test --test-name-pattern="login"  # filter by name
node --test --concurrency=4     # parallel execution
node --test --experimental-test-coverage  # coverage report
```

### Basic Test Structure

```javascript
import { describe, it, before, after, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';

describe('Math operations', () => {
  let calculator;

  before(() => {
    calculator = new Calculator();
  });

  beforeEach(() => {
    calculator.reset();
  });

  it('adds two numbers', () => {
    assert.strictEqual(calculator.add(2, 3), 5);
  });

  it('subtracts two numbers', () => {
    assert.strictEqual(calculator.subtract(5, 3), 2);
  });

  it('handles async operations', async () => {
    const result = await calculator.computeAsync();
    assert.ok(result > 0);
  });

  it('times out after 1 second', { timeout: 1000 }, async () => {
    await slowOperation();
  });

  afterEach(() => {
    // cleanup
  });

  after(() => {
    calculator.destroy();
  });
});
```

### Test Modifiers

```javascript
import { test, describe } from 'node:test';

// Run only this test
test.only('important test', () => { /* ... */ });

// Skip this test
test.skip('flaky test', () => { /* ... */ });

// Mark as TODO (skipped with special output)
test.todo('implement later', () => { /* ... */ });

// Expect failure
test.fails('known bug', () => {
  assert.fail('This should fail');
});
```

### Subtests

```javascript
import { test } from 'node:test';

test('parent test', async (t) => {
  await t.test('child test 1', () => {
    // ...
  });

  await t.test('child test 2', async () => {
    // ...
  });
});
```

### Mocking

```javascript
import { mock } from 'node:test';
import assert from 'node:assert/strict';

// Mock a function
const original = Math.random;
const mockRandom = mock.method(Math, 'random', () => 0.5);
assert.strictEqual(Math.random(), 0.5);
mockRandom.restore();

// Mock with return values
const fn = mock.fn((x) => x * 2);
fn(5);
fn(10);

assert.strictEqual(fn.mock.calls.length, 2);
assert.deepStrictEqual(fn.mock.calls[0].arguments, [5]);
assert.deepStrictEqual(fn.mock.calls[1].arguments, [10]);

// Mock with specific returns
const mockFn = mock.fn()
  .mockImplementationOnce(() => 'first')
  .mockImplementationOnce(() => 'second');
assert.strictEqual(mockFn(), 'first');
assert.strictEqual(mockFn(), 'second');

// Mock timers
const timer = mock.timer();
timer.setTimeout(() => console.log('fired'), 1000);
timer.tick(1000); // advance time
```

### Snapshot Testing

```javascript
import { test, snapshot } from 'node:test';

test('renders output', async (t) => {
  const result = generateReport({ users: 42, errors: 0 });
  await t.snapshot(result, { diffAlgorithm: 'natural' });
});

// Update snapshots
node --test --update-snapshots
```

### Test Reporters

```bash
node --test --reporter=spec          # detailed output (default)
node --test --reporter=tap           # TAP format
node --test --reporter=json          # JSON output
node --test --reporter=junit         # JUnit XML
node --test --reporter=dot           # minimal dots
node --test --reporter=lcov          # coverage in LCOV format
node --test --reporter=html          # HTML report
```

Multiple reporters:
```bash
node --test --reporter=spep --reporter=json --reporter-directory=./reports
```

### Code Coverage

```bash
# Basic coverage
node --test --experimental-test-coverage test/

# With threshold
node --test --experimental-test-coverage \
  --test-coverage-branches=80 \
  --test-coverage-functions=90 \
  --test-coverage-lines=95 \
  test/

# Exclude patterns
node --test --experimental-test-coverage \
  --test-coverage-exclude="**/*.test.js,**/node_modules/**" \
  test/

# Output formats
node --test --experimental-test-coverage --reporter=lcov --coverage-directory=./coverage
```

## assert Module

```javascript
import assert from 'node:assert/strict'; // prefer strict over default

// Basic assertions
assert.ok(value);                      // truthy check
assert.strictEqual(a, b);              // === comparison
assert.notStrictEqual(a, b);           // !== comparison
assert.deepEqual(a, b);                // loose deep equality
assert.deepStrictEqual(a, b);          // strict deep equality (preferred)
assert.partialDeepStrictEqual(obj, { a: 1 }); // partial object match

// Type checking
assert.instanceof(obj, MyClass);
assert.match(string, /pattern/);
assert.doesNotMatch(string, /pattern/);

// Function behavior
assert.throws(fn, Error);
assert.throws(fn, /error message/);
assert.doesNotThrow(fn);

// Async assertions
await assert.rejects(asyncFn, TypeError);
await assert.rejects(asyncFn, /failed/);
await assert.doesNotReject(asyncFn);

// ifError — fail if argument is truthy (for error-first callbacks)
fs.readFile('file.txt', (err, data) => {
  assert.ifError(err);
});
```

### CallTracker — Verify Callbacks Were Called

```javascript
import assert from 'node:assert/strict';

const tracker = new assert.CallTracker();
const fn = () => {};
const verified = tracker.capture(fn);

fn();
tracker.verify(verified); // passes — fn was called

// With call count
tracker.callCountContract(verified, 2);
fn(); fn();
tracker.verify(verified); // passes — called exactly 2 times
```

## Inspector Protocol

Node.js includes Chrome DevTools protocol support:

```bash
# Start with inspector
node --inspect app.js              # listens on :9229
node --inspect=0.0.0.0:9229 app.js # allow remote connections
node --inspect-brk app.js          # break on first line

# Programmatic control
import { inspect } from 'node:inspector';

const session = new inspect.Session();
session.connect();
session.post('Runtime.evaluate', { expression: 'process.pid' }, (err, result) => {
  console.log(result.body.result.value);
  session.disconnect();
});
```

## diagnostics_channel — Custom Diagnostics

Low-overhead channel for diagnostic information:

```javascript
import { Channel, subscribe } from 'node:diagnostics_channel';

const myChannel = new Channel('my-app-event');

// Publisher
function doWork() {
  myChannel.publish({ startTime: performance.now() });
  // ... work ...
  myChannel.publish({ endTime: performance.now() });
}

// Subscriber (only active when needed, zero overhead when not)
subscribe('my-app-event', (data) => {
  if (data.endTime) {
    console.log(`Duration: ${data.endTime - data.startTime}ms`);
  }
});
```

## trace_events — Low-Level Tracing

```bash
# Enable tracing
node --trace-event-categories=v8,node,perf.userland app.js
# Outputs: node.<pid>.events.logece

# Parse with Chrome DevTools or Node's trace-events tool
```

```javascript
import { Tracing } from 'node:trace_events';

const tracing = new Tracing();
tracing.disable(); // disabled by default
tracing.enable({
  categories: ['v8', 'node'],
});

// Custom trace events
tracing.clusterTraceSwitch((switches) => {
  switches.push('--event-buffer-size=1024');
});
```

## v8 — Heap and CPU Profiling

```javascript
import v8 from 'node:v8';

// Heap statistics
const stats = v8.getHeapStatistics();
console.log(`Used heap: ${(stats.used_heap_size / 1024 / 1024).toFixed(2)} MB`);
console.log(`Heap limit: ${(stats.heap_size_limit / 1024 / 1024).toFixed(2)} MB`);

// Write heap snapshot
v8.writeHeapSnapshot('./heap.heapsnapshot');
// Open in Chrome DevTools Memory tab

// CPU profiling
const profile = v8.startCpuProfile('my-profile', { sampleInterval: 100 });
// ... run code to profile ...
const result = v8.stopCpuProfile('my-profile');

// Query objects in heap
const stringInstances = v8.queryObjects(String, 10);
```

## perf_hooks — Performance Monitoring

```javascript
import { performance, PerformanceObserver } from 'node:perf_hooks';

// Mark and measure
performance.mark('before-work');
doExpensiveWork();
performance.mark('after-work');
performance.measure('work-duration', 'before-work', 'after-work');

const entries = performance.getEntriesByName('work-duration');
console.log(`${entries[0].duration}ms`);

// Observe function calls
const observer = new PerformanceObserver((items) => {
  for (const entry of items.getEntries()) {
    console.log(`Function: ${entry.name}, Duration: ${entry.duration}μs`);
  }
});
observer.observe({ entryTypes: ['function'] });

// Event loop utilization
import { eventLoopUtilization } from 'node:perf_hooks';
const elu1 = eventLoopUtilization();
// ... do work ...
const elu2 = eventLoopUtilization(elu1);
console.log(`Event loop was busy ${elu2.utilization * 100}% of the time`);

// Monitor event loop delay
const monitor = performance.monitorEventLoopDelay({
  resolution: 10, // sample every 10ms
});
monitor.enable();
// ... run application ...
console.log(`Mean delay: ${monitor.mean}ms, P95: ${monitor.percentile(95)}ms`);
monitor.disable();
```

## console — Debug Output

```javascript
// Basic output
console.log('message');
console.error('error');
console.warn('warning');
console.info('info');

// Formatted output
console.table([{ id: 1, name: 'Alice' }, { id: 2, name: 'Bob' }]);
console.dir(obj, { depth: null, colors: true });

// Timing
console.time('operation');
doWork();
console.timeEnd('operation');

// Grouping
console.group('Request');
console.log('URL:', req.url);
console.log('Method:', req.method);
console.groupEnd();

// Tracing
console.trace('execution path');

// Count
console.count('label'); // label: 1
console.count('label'); // label: 2
console.countReset('label');
```

## report — Crash Diagnostics

```javascript
import { report } from 'node:report';

// Manual report
report.writeReport('./crash-reports');

// Auto-report on signals
import { register } from 'node:report';
register({
  directory: './reports',
  filename: 'report-%YYYY%-%MM%-%DD%.json',
});

process.on('SIGUSR2', () => {
  report.writeReport();
});
```
