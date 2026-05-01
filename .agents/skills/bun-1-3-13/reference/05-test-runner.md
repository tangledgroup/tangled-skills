# Test Runner

Bun ships with a fast, built-in, Jest-compatible test runner. Tests execute with the Bun runtime and support TypeScript, JSX, lifecycle hooks, snapshots, mocking, and watch mode.

## Running Tests

```bash
bun test                     # all tests
bun test math                # filter by file/directory name
bun test ./math.test.ts      # specific file (must start with ./ or /)
bun test --watch             # watch mode
bun test --concurrent        # parallel execution
bun test -t "addition"       # filter by test name pattern
```

### Parallel and Distributed Testing (v1.3.13+)

```bash
bun test --parallel          # multi-threaded parallel execution
bun test --isolate           # isolate each test file into its own process (prevents state leakage)
bun test --shard=1/4         # run shard 1 of 4 (for distributed CI)
bun test --changed            # only tests affected by recent git changes
```

`--parallel` runs tests across multiple threads for faster execution. Combine with `--isolate` when tests share mutable global state:

```bash
bun test --parallel --isolate  # parallel + isolated processes
```

`--shard` splits the test suite into N shards, running only shard M:

```bash
# Runner 1 of 3
bun test --shard=1/3
# Runner 2 of 3
bun test --shard=2/3
# Runner 3 of 3
bun test --shard=3/3
```

`--changed` runs only tests in files modified since the last commit (or against a specific ref):

```bash
bun test --changed              # since HEAD
bun test --changed=main         # since main branch
bun test --changed=abc123       # since specific commit
```

Test file patterns:

- `*.test.{js|jsx|ts|tsx}`
- `*_test.{js|jsx|ts|tsx}`
- `*.spec.{js|jsx|ts|tsx}`
- `*_spec.{js|jsx|ts|tsx}`

## Writing Tests

Import from the built-in `bun:test` module:

```ts
import { expect, test, describe } from "bun:test";

describe("arithmetic", () => {
  test("2 + 2", () => {
    expect(2 + 2).toBe(4);
  });

  test("async operation", async () => {
    const result = await Promise.resolve(2 * 2);
    expect(result).toEqual(4);
  });

  // done callback pattern
  test("callback style", done => {
    setTimeout(() => {
      expect(true).toBe(true);
      done();
    }, 100);
  });
});
```

## Timeouts

Per-test timeout (third argument, in milliseconds):

```ts
test("slow operation", async () => {
  const data = await slowOperation();
  expect(data).toBe(42);
}, 500); // must complete in <500ms
```

Default timeout is 5000ms. Override globally with `--timeout`:

```bash
bun test --timeout 10000
```

On timeout, Bun throws an uncatchable exception and kills spawned child processes to prevent zombies.

## Retries and Repeats

```ts
// Retry flaky tests up to 3 times
test("flaky network request", async () => {
  const response = await fetch("https://example.com/api");
  expect(response.ok).toBe(true);
}, { retry: 3 });

// Run test 21 times (1 initial + 20 repeats) for stress testing
test("ensure stability", () => {
  expect(Math.random()).toBeLessThan(1);
}, { repeats: 20 });
```

Cannot use both `retry` and `repeats` on the same test.

## Test Modifiers

```ts
test.skip("not ready", () => {
  // skipped
});

test.todo("implement later", () => {
  // not run
});

test.failing("expected to fail", () => {
  // passes if it fails
});
```

Run todo tests to find any that are passing:

```bash
bun test --todo
```

## Concurrent Execution

```bash
bun test --concurrent                    # all tests run in parallel
bun test --concurrent --max-concurrency 4  # limit parallelism
```

Per-test control:

```ts
test.concurrent("parallel 1", async () => { /* ... */ });
test.concurrent("parallel 2", async () => { /* ... */ });
test.serial("sequential", () => { /* runs in order */ });
```

## Lifecycle Hooks

```ts
import { describe, test, expect, beforeAll, afterAll, beforeEach, afterEach } from "bun:test";

describe("my suite", () => {
  beforeAll(() => {
    // runs once before all tests in this suite
  });

  afterAll(() => {
    // runs once after all tests in this suite
  });

  beforeEach(() => {
    // runs before each test
  });

  afterEach(() => {
    // runs after each test
  });

  test("example", () => {
    expect(true).toBe(true);
  });
});
```

## Snapshot Testing

```ts
import { expect, test } from "bun:test";

test("snapshot", () => {
  expect({ name: "Bun", version: "1.3.12" }).toMatchInlineSnapshot(`
    {
      "name": "Bun",
      "version": "1.3.12",
    }
  `);
});
```

Update snapshots:

```bash
bun test --update-snapshots
```

## Mocking

```ts
import { mock, test, expect } from "bun:test";

// Mock a function
const fn = mock(() => "original");
fn.mockReturnValue("mocked");
expect(fn()).toBe("mocked");

// Mock a module
import * as math from "./math";
mock.module("./math", () => ({
  add: (a, b) => a + b + 1,
}));

// Spy on an object method
const obj = { method: () => "original" };
const spy = mock.method(obj, "method", () => "spied");
```

## Mock Clock

```ts
import { test, expect } from "bun:test";

test("mock time", () => {
  const clock = new TestClock(0);
  // ... tests with controlled time
  clock.restore();
});
```

## Coverage

```bash
bun test --coverage
```

Configure thresholds in `bunfig.toml`:

```toml
[test]
coverageThreshold = 0.8
```

## CI/CD Integration

### GitHub Actions

`bun test` auto-detects GitHub Actions and emits annotations:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun test
```

### JUnit XML Reports

```bash
bun test --reporter=junit --reporter-outfile=./test-results.xml
```

## DOM Testing

Bun supports DOM testing with happy-dom or jsdom. Install and configure:

```bash
bun add -d happy-dom
```

In `bunfig.toml`:

```toml
[test]
preload = ["./setup-dom.ts"]
```

Where `setup-dom.ts` initializes the DOM environment.
