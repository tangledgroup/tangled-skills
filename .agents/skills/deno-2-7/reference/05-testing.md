# Testing Guide

Deno has a built-in test runner with support for synchronous and asynchronous tests, fixtures, mocking, and coverage. This guide covers test patterns, assertions, and best practices.

## Basic Usage

### Running Tests

```bash
# Run all tests in current directory
deno test

# Run with required permissions
deno test --allow-read --allow-net --allow-env

# Run specific test file
deno test database.test.ts

# Run tests matching pattern
deno test **/user*.test.ts

# Run with type checking
deno test --check

# Skip type checking (faster)
deno test --no-check
```

### Test File Convention

Deno automatically discovers files matching:
- `*.test.ts`
- `*.test.js`
- `*_test.ts`
- `*_test.js`

## Writing Tests

### Basic Test Structure

```typescript
// math.test.ts
import { assertEquals } from "@std/assert";

Deno.test("addition works", () => {
  const result = 1 + 1;
  assertEquals(result, 2);
});

Deno.test("subtraction works", () => {
  const result = 5 - 3;
  assertEquals(result, 2);
});
```

### Asynchronous Tests

```typescript
Deno.test("fetches data", async () => {
  const response = await fetch("https://api.example.com/data");
  const data = await response.json();
  
  assertEquals(response.status, 200);
  assertEquals(Array.isArray(data), true);
});
```

### Test Timeout

Set timeout for long-running tests:

```typescript
Deno.test(
  "slow operation",
  { timeout: 30_000 }, // 30 seconds
  async () => {
    await delay(25_000);
    assertEquals(true, true);
  }
);
```

### Ignoring Tests

Skip tests conditionally:

```typescript
// Always skip
Deno.test("incomplete feature", { ignore: true }, () => {
  // Test will be skipped
});

// Skip on specific conditions
Deno.test(
  "Linux-only test",
  { ignore: Deno.build.os === "windows" },
  () => {
    // Skipped on Windows
  }
);
```

### Sanitize Options

Control test isolation:

```typescript
Deno.test(
  "test with ops",
  { sanitizeOps: false, sanitizeResources: false },
  async () => {
    // Can perform operations that affect global state
  }
);
```

## Assertions

Deno's standard library provides comprehensive assertions in `@std/assert`:

### Equality Assertions

```typescript
import { assertEquals, assertNotEquals } from "@std/assert";

// Values are strictly equal
assertEquals(1, 1);
assertEquals("hello", "hello");
assertEquals({ a: 1 }, { a: 1 });

// Values are not equal
assertNotEquals(1, 2);
```

### Truthiness Assertions

```typescript
import { assert, assertFalse, assertTrue } from "@std/assert";

// Value is truthy
assert("non-empty string");
assert(1);
assert({});

// Explicit boolean checks
assertTrue(true);
assertFalse(false);
```

### Type Assertions

```typescript
import { assertInstanceOf, assertIsInstance, assertType } from "@std/assert";

// Instance of class
assertInstanceOf(new Date(), Date);

// Type checking (compile-time)
assertType<string>("hello");
```

### Array Assertions

```typescript
import { assertArrayIncludes, assertNotIncludes } from "@std/assert";

// Array includes values
assertArrayIncludes([1, 2, 3], [1, 2]);

// Value not in array
assertNotIncludes([1, 2, 3], 4);
```

### String Assertions

```typescript
import { assertStringIncludes, assertMatch } from "@std/assert";

// String contains substring
assertStringIncludes("hello world", "world");

// String matches regex
assertMatch("hello 123", /\d+/);
```

### Error Assertions

```typescript
import { assertThrows, assertRejects } from "@std/assert";

// Synchronous function throws
assertThrows(
  () => { throw new Error("test"); },
  Error,
  "test"
);

// Async function rejects
await assertRejects(
  async () => { throw new Error("test"); },
  Error,
  "test"
);

// With specific error class
assertThrows(
  () => { throw new TypeError("wrong type"); },
  TypeError
);
```

### Near Equality (for floats)

```typescript
import { assertAlmostEquals } from "@std/assert";

// Float comparison with tolerance
assertAlmostEquals(1.0000001, 1.0);
assertAlmostEquals(1.0001, 1.0, 1e-3); // Custom tolerance
```

### Object Assertions

```typescript
import { assertObjectMatch } from "@std/assert";

// Object contains at least these properties
assertObjectMatch(
  { a: 1, b: 2, c: 3 },
  { a: 1, c: 3 }
);

// Nested objects
assertObjectMatch(
  { user: { name: "Alice", age: 30 } },
  { user: { name: "Alice" } }
);
```

## Test Organization

### Test Suites with `describe`

Group related tests:

```typescript
import { describe, it } from "@std/testing/bdd";

describe("User service", () => {
  it("creates a new user", () => {
    const user = createUser("Alice");
    assertEquals(user.name, "Alice");
  });

  it("validates user email", () => {
    assertThrows(
      () => createUser("Bob", "invalid-email"),
      ValidationError
    );
  });

  describe("with authentication", () => {
    it("requires valid token", async () => {
      const response = await fetch("/api/user", {
        headers: { Authorization: "Bearer invalid" }
      });
      assertEquals(response.status, 401);
    });
  });
});
```

### Test Files Structure

Organize tests alongside source files:

```
src/
  user/
    service.ts
    service.test.ts
  auth/
    middleware.ts
    middleware.test.ts
tests/
  integration/
    api.test.ts
  fixtures/
    user.json
```

## Fixtures and Setup

### Before Each Test

```typescript
import { beforeAll, beforeEach } from "@std/testing/mock";

let db: Database;
let user: User;

beforeAll(async () => {
  // Run once before all tests
  db = await connectDb();
});

beforeEach(async () => {
  // Run before each test
  user = await createUser("Test User");
});

Deno.test("can fetch user", async () => {
  const fetched = await db.getUser(user.id);
  assertEquals(fetched.name, "Test User");
});

Deno.test("can update user", async () => {
  await db.updateUser(user.id, { name: "Updated" });
  const fetched = await db.getUser(user.id);
  assertEquals(fetched.name, "Updated");
});
```

### Cleanup with `afterEach`

```typescript
import { afterEach } from "@std/testing/mock";

afterEach(async () => {
  // Cleanup after each test
  await db.deleteUser(user.id);
});
```

### Test Fixtures Directory

Use fixtures for test data:

```typescript
// tests/fixtures/user.json
{
  "id": 1,
  "name": "Test User",
  "email": "test@example.com"
}

// In test file
const fixture = JSON.parse(
  await Deno.readTextFile("./fixtures/user.json")
);
```

## Mocking

### Function Mocks

```typescript
import { mock } from "@std/testing/mock";

// Mock a function
const originalFetch = globalThis.fetch;
let mockCalled = false;

globalThis.fetch = mock(async (url: string) => {
  mockCalled = true;
  return new Response(JSON.stringify({ data: "mocked" }));
}) as typeof fetch;

Deno.test("uses mocked fetch", async () => {
  const response = await fetch("https://api.example.com");
  const json = await response.json();
  
  assertEquals(mockCalled, true);
  assertEquals(json.data, "mocked");
});

// Restore original
globalThis.fetch = originalFetch;
```

### Partial Mocks

Call original function with modified behavior:

```typescript
import { partialMock } from "@std/testing/mock";

const api = {
  getUser(id: number) {
    return fetch(`/api/users/${id}`);
  }
};

const mockApi = partialMock(api, {
  getUser: mock(async (id: number) => {
    if (id === 999) {
      return new Response(null, { status: 404 });
    }
    // Call original for other IDs
    return api.getUser(id);
  })
});
```

### Time Mocking

```typescript
import { mockTime } from "@std/testing/time";

Deno.test("respects timeout", async () => {
  const start = Date.now();
  
  // Freeze time
  const time = mockTime(1000000);
  
  await someOperation();
  
  // Time hasn't passed
  assertEquals(Date.now(), 1000000);
  
  // Advance time by 5 seconds
  time.tick(5000);
  assertEquals(Date.now(), 1000005);
  
  // Restore real time
  time.restore();
});
```

## Testing HTTP Servers

### In-Memory Server Testing

```typescript
import { serve } from "@std/http";
import { assert, assertEquals } from "@std/assert";

Deno.test("HTTP server returns correct response", async (t) => {
  // Start test server
  const controller = new AbortController();
  
  Deno.serve({ 
    port: 0, // Random available port
    signal: controller.signal 
  }, (req) => {
    return new Response("Hello");
  });
  
  // Cleanup after test
  addCleanup(() => controller.abort());
  
  // Make request
  const response = await fetch("http://localhost:PORT");
  assertEquals(await response.text(), "Hello");
});
```

### Using Test Server Utility

```typescript
import { assert, assertEquals } from "@std/assert";

Deno.test("API endpoint", async () => {
  // Create test server
  const { address, fetch: serverFetch } = await createTestServer((req) => {
    const url = new URL(req.url);
    
    if (url.pathname === "/users") {
      return Response.json([{ id: 1, name: "Alice" }]);
    }
    
    return new Response("Not found", { status: 404 });
  });
  
  // Make requests to test server
  const response = await serverFetch("/users");
  const users = await response.json();
  
  assertEquals(users.length, 1);
  assertEquals(users[0].name, "Alice");
});
```

## Coverage

### Generating Coverage

```bash
# Run tests with coverage
deno test --coverage=coverage

# Generate coverage report
deno coverage coverage/

# Generate LCov format (for CI)
deno coverage coverage/ --lcov > coverage.lcov

# Generate HTML report
deno coverage coverage/ --html
```

### Coverage Configuration

Configure coverage in `deno.json`:

```json
{
  "test": {
    "include": ["tests/**", "**/*.test.ts"],
    "exclude": ["tests/fixtures/**", "vendor/**"]
  }
}
```

### Ignoring Code from Coverage

```typescript
// deno-lint-ignore-file
// or
// deno-coverage-ignore-next-line
const unreachedCode = true;
```

## Parallel Testing

### Running Tests in Parallel

By default, Deno runs tests in parallel:

```bash
# Run all tests in parallel (default)
deno test

# Run tests sequentially
deno test --no-parallel
```

### Test Isolation

Each test runs in isolation:

```typescript
Deno.test("test 1 modifies global", () => {
  (globalThis as any).counter = 1;
});

Deno.test("test 2 sees clean state", () => {
  assertEquals((globalThis as any).counter, undefined);
});
```

### Controlling Parallelism

```bash
# Limit parallel jobs
deno test --jobs=4

# Run single-threaded
deno test --jobs=1
```

## Filtering Tests

### By Name Pattern

```bash
# Run tests matching "user"
deno test --filter="user"

# Exclude tests matching "slow"
deno test --filter="^((?!slow).)*$"

# Run only integration tests
deno test --filter="integration"
```

### Case-Insensitive Filtering

```bash
# Matches "User", "USER", "user"
deno test --filter="user"
```

## Test Reports

### JUnit Format

```bash
# Generate JUnit XML report
deno test --reporter=junit > test-results.xml
```

### Dot Reporter

```bash
# Compact output
deno test --reporter=dot
```

### Pretty Reporter (Default)

```bash
# Verbose, colorized output
deno test --reporter=pretty
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Deno
        uses: denoland/setup-deno@main
        with:
          deno-version: stable
      
      - name: Run tests
        run: deno test -A --coverage
        
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.lcov
```

### Test in CI with Artifacts

```yaml
- name: Run tests
  run: |
    deno test -A --coverage=coverage
    deno coverage coverage --lcov > coverage.lcov
    
- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: coverage
    path: coverage.lcov
```

## Best Practices

### Write Descriptive Test Names

```typescript
// ❌ Not descriptive
Deno.test("works", () => { ... });

// ✅ Clear and specific
Deno.test("returns 404 when user not found", () => { ... });
```

### Arrange-Act-Assert Pattern

```typescript
Deno.test("calculates total with discount", () => {
  // Arrange
  const items = [{ price: 100 }, { price: 200 }];
  const discount = 0.1;
  
  // Act
  const total = calculateTotal(items, discount);
  
  // Assert
  assertEquals(total, 270); // (100 + 200) * 0.9
});
```

### Test Edge Cases

```typescript
Deno.test("handles empty array", () => {
  assertEquals(sum([]), 0);
});

Deno.test("handles negative numbers", () => {
  assertEquals(sum([-1, -2, -3]), -6);
});

Deno.test("handles very large numbers", () => {
  assertEquals(sum([Number.MAX_SAFE_INTEGER, 1]), Infinity);
});
```

### Mock External Dependencies

```typescript
Deno.test("retries on failure", async () => {
  let callCount = 0;
  
  const mockFetch = mock(async () => {
    callCount++;
    if (callCount < 3) {
      throw new Error("Network error");
    }
    return new Response("success");
  });
  
  const result = await retryableFetch(url, { retries: 3 });
  
  assertEquals(callCount, 3);
  assertEquals(result, "success");
});
```

### Use Fixtures for Complex Data

```typescript
// Avoid inline complex data
Deno.test("parses user", () => {
  const userData = JSON.parse(
    await Deno.readTextFile("./fixtures/complex-user.json")
  );
  
  const user = parseUser(userData);
  assertEquals(user.name, "Alice Smith");
});
```

## Debugging Tests

### Inspector Breakpoints

```bash
# Start test with inspector
deno test --inspect-brk

# Connect Chrome DevTools to http://localhost:9229
```

### Debug Logging

```typescript
Deno.test("with debug output", () => {
  console.log("Debug: starting test");
  
  const result = compute();
  console.log("Debug: result =", result);
  
  assertEquals(result, expected);
});
```

### Only Run Specific Test

```bash
# Filter to single test
deno test --filter="exact test name"
```

## Related Topics

- [Task Runner Guide](04-task-runner.md) - Running tests via tasks
- [TypeScript Configuration](03-typescript.md) - Type checking in tests
- [Permissions and Security](01-permissions.md) - Permission requirements for tests
