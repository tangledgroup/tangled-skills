# Bun Test Runner

Bun's test runner is a fast, Jest-compatible testing framework with native TypeScript support, lifecycle hooks, mocking, snapshots, and watch mode. It runs 5-10x faster than Jest while maintaining API compatibility.

## Getting Started

### Running Tests

```bash
# Run all tests
bun test

# Run specific test file
bun test ./tests/math.test.ts

# Run tests matching pattern
bun test math

# Run with watch mode
bun test --watch

# Run with coverage
bun test --coverage

# Run in CI mode (no colors, fail fast)
bun test --ci
```

### Test File Patterns

Bun automatically discovers test files matching:
- `*.test.{js,jsx,ts,tsx}`
- `*_test.{js,jsx,ts,tsx}`
- `*.spec.{js,jsx,ts,tsx}`
- `*_spec.{js,jsx,ts,tsx}`

Example filenames:
```
math.test.ts
user_service_test.ts
api.spec.tsx
component_spec.jsx
```

## Writing Tests

### Basic Test Structure

```typescript title="math.test.ts"
import { expect, test, describe } from "bun:test";

describe("Math operations", () => {
  test("addition", () => {
    expect(2 + 2).toBe(4);
  });

  test("subtraction", () => {
    expect(10 - 3).toBe(7);
  });

  test("multiplication", () => {
    expect(3 * 4).toBe(12);
  });
});

// Top-level tests work too
test("standalone test", () => {
  expect(true).toBeTruthy();
});
```

### Test Functions

```typescript
import { test, it, describe } from "bun:test";

// All are equivalent
test("description", () => { /* ... */ });
it("description", () => { /* ... */ });

// Group related tests
describe("User authentication", () => {
  test("should login with valid credentials", () => { /* ... */ });
  test("should reject invalid credentials", () => { /* ... */ });
});

// Nested describe blocks
describe("API", () => {
  describe("GET /users", () => {
    test("returns user list", () => { /* ... */ });
    test("handles pagination", () => { /* ... */ });
  });
  
  describe("POST /users", () => {
    test("creates new user", () => { /* ... */ });
  });
});
```

## Matchers

### Basic Matchers

```typescript
import { expect } from "bun:test";

// Equality
expect(value).toBe(42);           // Strict equality (===)
expect(value).toEqual({ a: 1 });  // Deep equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeDefined();
expect(value).toBeUndefined();
expect(value).toBeNull();
expect(value).not.toBeNull();

// Types
expect(value).toBeNaN();
expect(value).toBeGreaterThan(10);
expect(value).toBeLessThan(20);
expect(value).toBeCloseTo(3.14, 2);  // 2 decimal places
```

### Array and Object Matchers

```typescript
// Arrays
expect([1, 2, 3]).toContain(2);
expect([1, 2, 3]).toContainEqual({ id: 2 });
expect([1, 2, 3]).toHaveLength(3);

// Objects
expect({ a: 1, b: 2 }).toHaveProperty("a");
expect({ a: 1, b: 2 }).toHaveProperty("a", 1);
expect({ a: 1, b: 2 }).toMatchObject({ a: 1 });

// Strings
expect("hello world").toContain("world");
expect("hello").toMatch(/ell/);
expect("Hello World").toMatchInlineSnapshot(`"Hello World"`);
```

### Function Matchers

```typescript
// Function calls
test("function returns correct value", () => {
  const add = (a: number, b: number) => a + b;
  expect(add(2, 3)).toBe(5);
});

// Async functions
test("async function resolves correctly", async () => {
  const fetchData = async () => "data";
  await expect(fetchData()).resolves.toBe("data");
});

// Rejection
test("function rejects on error", async () => {
  const fail = async () => { throw new Error("fail"); };
  await expect(fail()).rejects.toThrow("fail");
});
```

### Exception Matchers

```typescript
// Throw errors
expect(() => { throw new Error("boom"); }).toThrow();
expect(() => { throw new Error("boom"); }).toThrow("boom");
expect(() => { throw new Error("boom"); }).toThrow(/boom/);
expect(() => { throw new CustomError(); }).toThrow(CustomError);

// Async errors
await expect(asyncFn()).rejects.toThrow("error message");
```

## Lifecycle Hooks

### Test File Level

```typescript
import { beforeEach, afterEach, beforeAll, afterAll } from "bun:test";

let setupData: any;

beforeAll(async () => {
  console.log("Runs once before all tests");
  setupData = await initialize();
});

afterAll(async () => {
  console.log("Runs once after all tests");
  await cleanup();
});

beforeEach(async () => {
  console.log("Runs before each test");
  // Reset state
});

afterEach(async () => {
  console.log("Runs after each test");
  // Cleanup
});

describe("Tests", () => {
  test("first test", () => {
    expect(setupData).toBeDefined();
  });
  
  test("second test", () => {
    expect(setupData).toBeDefined();
  });
});
```

### Hook Execution Order

```
beforeAll
  beforeEach
    test 1
  afterEach
  
  beforeEach
    test 2
  afterEach
afterAll
```

## Mocking

### Function Mocks

```typescript
import { mock } from "bun:test";

// Mock implementation
const fn = mock(() => "original");
fn.mockImplementation(() => "mocked");
fn.mockReturnValue("static value");
fn.mockResolvedValue("async value");
fn.mockRejectedValue(new Error("rejected"));

test("function is mocked", () => {
  expect(fn()).toBe("mocked");
});

// Reset mock
fn.mockReset();  // Clear calls and implementation
fn.mockClear();  // Clear only call history
fn.mockRestore();  // Restore original implementation
```

### Mock Call Tracking

```typescript
const fn = mock((x: number) => x * 2);

fn(5);
fn(10);
fn(5, "extra");

test("mock tracking", () => {
  expect(fn).toHaveBeenCalledTimes(3);
  expect(fn).toHaveBeenCalledWith(5);
  expect(fn).toHaveBeenCalledWith(10);
  expect(fn).toHaveBeenCalledWith(5, "extra");
  
  // Return values
  expect(fn.mock.results[0].value).toBe(10);
  expect(fn.mock.results[1].value).toBe(20);
});
```

### Module Mocking

```typescript
// Auto-mock all modules from directory
bun test --mock ./tests/

// Manual module mock
import { mock } from "bun:test";

const myModule = await mock("./my-module");
myModule.default.mockReturnValue("mocked");

// Partial mocking
const originalModule = await import("./my-module");
const partialMock = await mock("./my-module", {
  __esModule: true,
  default: originalModule.default,
  helperFunction: mock(() => "mocked"),
});
```

### Global Mocks

```typescript
// Mock global functions
global.fetch = mock(async (url: string) => ({
  json: async () => ({ data: "mocked" }),
}));

// Mock timers
const { tick, pauseAll } = mock.timers();

setTimeout(() => console.log("later"), 1000);
await tick(1000);  // Advance time by 1000ms

pauseAll();  // Pause all timers
```

## Snapshot Testing

### Basic Snapshots

```typescript
import { expect } from "bun:test";

test("renders correct output", () => {
  const component = render(<UserProfile user={user} />);
  expect(component).toMatchSnapshot();
});

// Inline snapshots
test("inline snapshot", () => {
  expect({ a: 1, b: 2 }).toMatchInlineSnapshot(`
    {
      "a": 1,
      "b": 2,
    }
  `);
});
```

### Snapshot Management

```bash
# Update all snapshots
bun test -u

# Update specific test file snapshots
bun test ./tests/component.test.ts -u

# Delete snapshots
bun test --clearCache
```

### Snapshot Files

Snapshots are stored in `__snapshots__/` directory:
```
tests/
  component.test.ts
__snapshots__/
  component.test.ts.snap
```

## Concurrent Testing

### Running Tests in Parallel

```bash
# Enable concurrent execution
bun test --concurrent

# Limit concurrency
bun test --concurrent --max-concurrency 4

# Mark specific tests as concurrent
test.concurrent("heavy computation", () => {
  // Runs in parallel with other concurrent tests
});
```

### Serial Tests

Force sequential execution:

```typescript
// In describe block
describe.serial("Database operations", () => {
  test("creates table", () => { /* ... */ });
  test("inserts data", () => { /* ... */ });
  test("queries data", () => { /* ... */ });
});

// Individual test
test.serial("must run in order", () => { /* ... */ });
```

## Code Coverage

### Generating Coverage Reports

```bash
# Run tests with coverage
bun test --coverage

# Specify coverage directory
bun test --coverage --coverage-dir ./cov

# Set coverage thresholds
bun test --coverage --threshold-lines 80 --threshold-branches 70
```

### Coverage Configuration

```toml title="bunfig.toml"
[test]
coverage = true
coverageDir = "./coverage"
coverageExclude = [
  "tests/**",
  "**/*.test.ts",
  "**/node_modules/**",
]
thresholds = { lines = 80, branches = 70, functions = 80, statements = 80 }
```

### Coverage Output

Coverage reports are generated in:
- `coverage/lcov.info` - LCOV format for CI tools
- `coverage/index.html` - HTML report (if supported)

## Test Filters

### Filtering Tests

```bash
# Run tests by name pattern
bun test --test-name-pattern "authentication"

# Run tests in specific directory
bun test ./tests/unit/

# Run specific file
bun test ./tests/user.test.ts

# Multiple filters
bun test user authentication
```

### Skip and Only

```typescript
// Skip specific test
test.skip("not ready yet", () => {
  // This test won't run
});

// Run only specific tests (useful for debugging)
test.only("debug this one", () => {
  // Only this test runs
});

// Skip entire describe block
describe.skip("feature in progress", () => {
  // None of these tests run
});
```

## Custom Reporters

### Built-in Reporters

```bash
# Default reporter (verbose)
bun test

# JUnit XML for CI/CD
bun test --reporter=junit --reporter-outfile=./test-results.xml

# JSON output
bun test --reporter=json --reporter-outfile=./results.json

# Compact output
bun test --reporter=compact
```

### GitHub Actions Integration

Bun automatically detects GitHub Actions and emits annotations:

```yaml title=".github/workflows/test.yml"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun test  # Automatically emits annotations
```

## Configuration

### Command Line Options

```bash
# Timeout per test (default: 5000ms)
bun test --timeout 10000

# Stop after first failure
bun test --bail

# Run in random order
bun test --shuffle

# Show slow tests (> threshold ms)
bun test --slow-testThreshold 1000

# List tests without running
bun test --list

# Update snapshots
bun test -u

# Verbose output
bun test --verbose
```

### bunfig.toml Configuration

```toml title="bunfig.toml"
[test]
# Basic settings
timeout = 5000
shuffle = false
concurrent = false
maxConcurrency = 20

# Coverage
coverage = false
coverageDir = "./coverage"
coverageExclude = ["tests/**", "**/*.test.ts"]

# Reporting
reporter = "auto"  # "auto" | "junit" | "json" | "compact"

# Filters
include = ["**/*.{test,spec}.{ts,tsx,js,jsx}"]
exclude = ["node_modules", "dist", "build"]

# Environment
envFile = ".env.test"
```

## DOM Testing

### Browser-like Environment

Bun provides basic DOM APIs for testing:

```typescript title="component.test.tsx"
import { expect, test } from "bun:test";

test("DOM manipulation", () => {
  // Create element
  const div = document.createElement("div");
  div.textContent = "Hello";
  
  expect(div.textContent).toBe("Hello");
});
```

### JSX Testing

```typescript title="jsx.test.tsx"
import { expect, test } from "bun:test";

test("JSX element creation", () => {
  const element = <div className="test">Hello</div>;
  
  expect(element.type).toBe("div");
  expect(element.props.className).toBe("test");
  expect(element.props.children).toBe("Hello");
});
```

## Migration from Jest

### API Compatibility

Most Jest code works without modification:

```typescript
// Jest and Bun test runner share the same API
import { 
  test, it, describe, 
  beforeEach, afterEach, 
  beforeAll, afterAll,
  expect, jest  // Note: use "mock" instead of "jest"
} from "bun:test";

// Instead of jest.mock(), use:
import { mock } from "bun:test";
```

### Command Migration

| Jest | Bun Test Runner |
|------|-----------------|
| `jest` | `bun test` |
| `jest --watch` | `bun test --watch` |
| `jest --coverage` | `bun test --coverage` |
| `jest --updateSnapshot` | `bun test -u` |
| `jest testNamePattern` | `bun test testNamePattern` |
| `jest --testPathPattern=foo` | `bun test foo` |

### Setup Files

```typescript title="setup.ts"
// Jest: jest.setup.js
// Bun: Auto-loaded if named setup.{ts,js}

// Or specify in bunfig.toml
export { mockAPI, setupDatabase } from "./test-utils";
```

```toml title="bunfig.toml"
[test]
preload = ["./setup.ts"]
```

## Best Practices

1. **Use descriptive test names**: `test("should return 4 when adding 2 + 2")` not `test("add")`
2. **Arrange-Act-Assert pattern**: Setup, execute, verify
3. **One assertion per test** (usually): Makes failures easier to debug
4. **Test edge cases**: Empty inputs, null values, boundary conditions
5. **Use fixtures for complex data**: Store test data in separate files
6. **Mock external dependencies**: Don't call real APIs in unit tests
7. **Keep tests independent**: Tests should not rely on each other's state
8. **Use concurrent testing wisely**: Only for truly independent tests

## Troubleshooting

### Common Issues

**Tests running slowly**: Enable concurrent execution:
```bash
bun test --concurrent --max-concurrency 8
```

**Snapshot mismatches**: Review changes and update if intentional:
```bash
bun test -u
```

**Module resolution errors**: Check import paths or use `--bun` flag:
```bash
bun test --bun
```

**Timeout errors**: Increase timeout for slow tests:
```typescript
test("slow operation", async () => {
  // ...
}, { timeout: 30000 });
```

**Environment variable issues**: Load env file:
```bash
bun test --env-file .env.test
```

## Advanced Patterns

### Factory Functions for Test Data

```typescript
function createUser({ 
  id = 1, 
  name = "Test User", 
  email = "test@example.com" 
} = {}) {
  return { id, name, email };
}

test("user creation", () => {
  const user = createUser({ id: 42 });
  expect(user.id).toBe(42);
});
```

### Custom Matchers

```typescript
import { expect, test } from "bun:test";

// Extend expect with custom matchers (via third-party packages)
// Bun supports Jest's custom matcher API

test("custom matcher example", () => {
  expect([1, 2, 3]).toSatisfy((arr) => arr.length > 0);
});
```

### Performance Testing

```typescript
import { test, expect } from "bun:test";

test("should complete within time limit", async () => {
  const start = Date.now();
  
  await heavyComputation();
  
  const duration = Date.now() - start;
  expect(duration).toBeLessThan(100); // Complete in < 100ms
});
```
