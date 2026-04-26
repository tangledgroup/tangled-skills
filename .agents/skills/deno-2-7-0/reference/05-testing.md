# Testing and Benchmarking

## Built-in Test Runner

Deno includes a built-in test runner. Define tests with `Deno.test()`:

```typescript
import { assertEquals } from "jsr:@std/assert";

Deno.test("simple test", () => {
  const x = 1 + 2;
  assertEquals(x, 3);
});

Deno.test("async test", async () => {
  const x = 1 + 2;
  await new Promise((r) => setTimeout(r, 100));
  assertEquals(x, 3);
});

Deno.test({
  name: "read file test",
  fn: () => {
    const data = Deno.readTextFileSync("./somefile.txt");
    assertEquals(data, "expected content");
  },
});
```

### Jest-style Assertions

Use `@std/expect` for Jest-compatible assertions:

```typescript
import { expect } from "jsr:@std/expect";
import { add } from "./add.js";

Deno.test("add function", () => {
  expect(add(2, 3)).toBe(5);
});
```

## Running Tests

```bash
# Run all tests in current directory (recursively)
deno test

# Run tests in a specific directory
deno test util/

# Run a specific test file
deno test my_test.ts

# Run tests in parallel
deno test --parallel

# Pass arguments to test files
deno test my_test.ts -- -e --foo

# Grant permissions for tests
deno test --allow-read=. my_test.ts
```

Test files matching `{*,*.,}test.{ts,tsx,mts,js,mjs,jsx}` are auto-discovered.

## Test Steps

Break tests into smaller parts with `t.step()`:

```typescript
Deno.test("database operations", async (t) => {
  using db = await openDatabase();

  await t.step("insert user", async () => {
    // Insert user logic
  });

  await t.step("insert book", async () => {
    // Insert book logic
  });
});
```

## Test Hooks

Setup and teardown with hooks:

```typescript
// Runs once before all tests in scope
Deno.test.beforeAll(() => {
  console.log("Setup database");
});

// Runs before each test
Deno.test.beforeEach(() => {
  console.log("Clear test data");
});

// Runs after each test
Deno.test.afterEach(() => {
  console.log("Cleanup");
});

// Runs once after all tests in scope
Deno.test.afterAll(() => {
  console.log("Close database");
});
```

**Execution order:**
- `beforeAll`/`beforeEach`: FIFO (first in, first out)
- `afterEach`/`afterAll`: LIFO (last in, first out)

If an exception is raised in any hook, remaining hooks of the same type are skipped and the test fails.

## Filtering Tests

```bash
# Filter by string match
deno test --filter="database"

# Filter by regex pattern
deno test --filter="/insert.*user/"
```

## Skipping and Only

```typescript
Deno.test({
  name: "skipped test",
  ignore: true,  // Always skip
  fn: () => { /* ... */ },
});

Deno.test({
  name: "only this test",
  only: true,    // Run only this test
  fn: () => { /* ... */ },
});
```

## Failing Fast

Stop on first failure:

```bash
deno test --fail-fast
```

## Coverage

Generate coverage reports:

```bash
# Run tests with coverage
deno test --coverage=cov/

# Generate coverage report
deno coverage cov/               # Text output
deno coverage cov/ --lcov        # LCOV format
deno coverage cov/ --html         # HTML report
```

## Snapshot Testing

Use `@std/testing/snapshot` for snapshot testing:

```typescript
import { assertSnapshot } from "jsr:@std/testing/snapshot";

Deno.test("snapshot test", async (t) => {
  await assertSnapshot(t, {
    hello: "world",
    count: 42,
  });
});
```

Update snapshots with `--update` flag:

```bash
deno test --update
```

## Behavior-Driven Development (BDD)

Use `@std/testing/bdd` for BDD-style tests:

```typescript
import { describe, it } from "jsr:@std/testing/bdd";
import { expect } from "jsr:@std/expect";

describe("my module", () => {
  it("does something", () => {
    expect(true).toBe(true);
  });
});
```

## Documentation Tests

Deno can test code snippets in documentation:

```bash
# Test code blocks in JSDoc comments
deno test --doc module.ts

# Test code blocks in markdown files
deno test --doc-only README.md
```

## Sanitizers

Deno's test runner includes sanitizers that check for resource leaks:

- **Resource sanitizer** — Ensures all open resources are closed
- **Async operation sanitizer** — Ensures all async operations complete
- **Exit sanitizer** — Prevents tests from calling `Deno.exit()`

Disable sanitizers with flags:

```bash
deno test --no-clean-env     # Skip environment variable cleanup
deno test --unsafely-ignore-missing-imports
```

## Benchmarking

Deno includes a built-in benchmark runner:

```typescript
import { bench } from "jsr:@std/bench";

bench("simple addition", () => {
  const x = 1 + 2;
});

bench({
  name: "with options",
  fn: () => {
    // Benchmark code
  },
});
```

Run benchmarks:

```bash
deno bench          # All benchmarks
deno bench src/     # Benchmarks in directory
deno bench --filter="regex"  # Filter by name
```
