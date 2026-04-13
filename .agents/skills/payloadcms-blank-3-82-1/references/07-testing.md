# Testing Setup

Complete guide to testing in Payload CMS blank template, including Vitest integration tests, Playwright E2E tests, test helpers, and best practices.

## Test Structure

```
tests/
├── e2e/                     # Playwright end-to-end tests
│   ├── admin.e2e.spec.ts    # Admin panel tests
│   └── frontend.e2e.spec.ts # Frontend page tests
├── int/                     # Vitest integration tests
│   └── api.int.spec.ts      # API and Local API tests
└── helpers/                 # Shared test utilities
    ├── login.ts             # Login helper for E2E
    └── seedUser.ts          # Test user seeding/cleanup
```

## Integration Tests (Vitest)

### Configuration

**vitest.config.mts:**

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: 'jsdom', // Browser-like DOM environment
    setupFiles: ['./vitest.setup.ts'],
    include: ['tests/int/**/*.int.spec.ts'], // Only *.int.spec.ts files
  },
})
```

### Running Integration Tests

```bash
# Run all integration tests
pnpm test:int

# Run in watch mode (development)
pnpm vitest

# Run with coverage
pnpm vitest --coverage

# Run specific test file
pnpm vitest tests/int/api.int.spec.ts
```

### Basic Test Structure

**tests/int/api.int.spec.ts:**

```typescript
import { getPayload, Payload } from 'payload'
import config from '@/payload.config'
import { describe, it, beforeAll, expect, afterAll } from 'vitest'

let payload: Payload

describe('API', () => {
  // Setup before all tests
  beforeAll(async () => {
    const payloadConfig = await config
    payload = await getPayload({ config: payloadConfig })
  }, 30000) // 30 second timeout for setup
  
  // Cleanup after all tests
  afterAll(async () => {
    // Optional: cleanup test data
  })
  
  it('fetches users', async () => {
    const users = await payload.find({
      collection: 'users',
    })
    
    expect(users).toBeDefined()
    expect(users.docs).toBeInstanceOf(Array)
  })
})
```

### Testing CRUD Operations

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest'

describe('Posts Collection', () => {
  let testPost: any
  
  // Cleanup before each test
  beforeEach(async () => {
    // Create test data
    testPost = await payload.create({
      collection: 'posts',
      data: {
        title: 'Test Post',
        content: 'Test content',
        status: 'draft',
      },
    })
  })
  
  // Cleanup after each test
  afterEach(async () => {
    if (testPost) {
      await payload.delete({
        collection: 'posts',
        id: testPost.id,
      })
    }
  })
  
  it('creates a post', async () => {
    expect(testPost.id).toBeDefined()
    expect(testPost.title).toBe('Test Post')
    expect(testPost.status).toBe('draft')
  })
  
  it('updates a post', async () => {
    const updated = await payload.update({
      collection: 'posts',
      id: testPost.id,
      data: { title: 'Updated Title' },
    })
    
    expect(updated.title).toBe('Updated Title')
  })
  
  it('finds a post by ID', async () => {
    const found = await payload.findByID({
      collection: 'posts',
      id: testPost.id,
    })
    
    expect(found).toBeDefined()
    expect(found.id).toBe(testPost.id)
  })
  
  it('deletes a post', async () => {
    await payload.delete({
      collection: 'posts',
      id: testPost.id,
    })
    
    const deleted = await payload.findByID({
      collection: 'posts',
      id: testPost.id,
    })
    
    expect(deleted).toBeNull()
  })
})
```

### Testing Access Control

```typescript
describe('Access Control', () => {
  let adminUser: any
  let regularUser: any
  
  beforeAll(async () => {
    // Create test users with different roles
    adminUser = await payload.create({
      collection: 'users',
      data: {
        email: 'admin@test.com',
        password: 'password123',
        roles: ['admin'],
      },
    })
    
    regularUser = await payload.create({
      collection: 'users',
      data: {
        email: 'user@test.com',
        password: 'password123',
        roles: ['member'],
      },
    })
  })
  
  it('allows admin to read all posts', async () => {
    const posts = await payload.find({
      collection: 'posts',
      user: adminUser,
      overrideAccess: false, // Enforce access control
    })
    
    expect(posts.docs).toBeDefined()
  })
  
  it('restricts regular user to own posts', async () => {
    // Create a post as regular user
    const userPost = await payload.create({
      collection: 'posts',
      data: {
        title: 'User Post',
        author: regularUser.id,
      },
      req: { user: regularUser } as any,
    })
    
    // Regular user should only see their own posts
    const posts = await payload.find({
      collection: 'posts',
      user: regularUser,
      overrideAccess: false,
    })
    
    expect(posts.docs).toHaveLength(1)
    expect(posts.docs[0].id).toBe(userPost.id)
  })
  
  it('denies unauthenticated access', async () => {
    const posts = await payload.find({
      collection: 'posts',
      overrideAccess: false, // No user = no access
    })
    
    expect(posts.docs).toHaveLength(0)
  })
})
```

### Testing Hooks

```typescript
describe('Hooks', () => {
  it('auto-generates slug in beforeValidate hook', async () => {
    const post = await payload.create({
      collection: 'posts',
      data: {
        title: 'My Test Post',
      },
    })
    
    // Hook should have generated slug
    expect(post.slug).toBe('my-test-post')
  })
  
  it('sets publishedAt in beforeChange hook', async () => {
    const draft = await payload.create({
      collection: 'posts',
      data: {
        title: 'Draft Post',
        status: 'draft',
      },
    })
    
    expect(draft.publishedAt).toBeUndefined()
    
    // Publish the post
    const published = await payload.update({
      collection: 'posts',
      id: draft.id,
      data: { status: 'published' },
    })
    
    // Hook should have set publishedAt
    expect(published.publishedAt).toBeDefined()
  })
})
```

### Testing Custom Endpoints

```typescript
import request from 'supertest'
import next from 'next'

describe('Custom API Routes', () => {
  let server: any
  
  beforeAll(() => {
    // Start Next.js server for testing
    server = next({ dev: true })
    return server.prepare()
  })
  
  it('calls custom endpoint', async () => {
    const handler = server.getRequestHandler()
    
    const res = await request(handler)
      .get('/api/custom-route')
      .expect(200)
    
    expect(res.body).toHaveProperty('message')
  })
})
```

## E2E Tests (Playwright)

### Configuration

**playwright.config.ts:**

```typescript
import { defineConfig, devices } from '@playwright/test'
import 'dotenv/config'

export default defineConfig({
  testDir: './tests/e2e',
  
  // Fail CI if test.only is left in code
  forbidOnly: !!process.env.CI,
  
  // Retry failed tests in CI
  retries: process.env.CI ? 2 : 0,
  
  // Single worker in CI for stability
  workers: process.env.CI ? 1 : undefined,
  
  // HTML report for easy viewing
  reporter: 'html',
  
  use: {
    // Record trace on retry for debugging
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
  },
  
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], channel: 'chromium' },
    },
    // Add more browsers for cross-browser testing
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  
  // Auto-start dev server before tests
  webServer: {
    command: 'pnpm dev',
    reuseExistingServer: true, // Don't restart if already running
    url: 'http://localhost:3000',
    timeout: 120000, // 2 minute timeout for server startup
  },
})
```

### Running E2E Tests

```bash
# Run all E2E tests
pnpm test:e2e

# Run in UI mode (interactive)
pnpm playwright test --ui

# Run specific test file
pnpm playwright test tests/e2e/admin.e2e.spec.ts

# Run with specific browser
pnpm playwright test --project=chromium

# Run with video recording
pnpm playwright test --video=on

# View HTML report
pnpm playwright show-report
```

### Test Helpers

**tests/helpers/login.ts:**

```typescript
import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'

export interface LoginOptions {
  page: Page
  serverURL?: string
  user: {
    email: string
    password: string
  }
}

/**
 * Logs the user into the admin panel via the login page.
 */
export async function login({
  page,
  serverURL = 'http://localhost:3000',
  user,
}: LoginOptions): Promise<void> {
  // Navigate to login page
  await page.goto(`${serverURL}/admin/login`)
  
  // Fill in credentials
  await page.fill('#field-email', user.email)
  await page.fill('#field-password', user.password)
  
  // Submit form
  await page.click('button[type="submit"]')
  
  // Wait for redirect to admin dashboard
  await page.waitForURL(`${serverURL}/admin`)
  
  // Verify successful login
  const dashboardArtifact = page.locator('span[title="Dashboard"]')
  await expect(dashboardArtifact).toBeVisible()
}

/**
 * Logs out the current user.
 */
export async function logout(page: Page, serverURL = 'http://localhost:3000'): Promise<void> {
  // Open user menu and click logout
  await page.goto(`${serverURL}/admin`)
  await page.click('[data-testid="user-menu"]')
  await page.click('text=Logout')
  
  // Verify redirect to login page
  await page.waitForURL(`${serverURL}/admin/login`)
}
```

**tests/helpers/seedUser.ts:**

```typescript
import { getPayload } from 'payload'
import config from '../../src/payload.config.js'

export const testUser = {
  email: 'dev@payloadcms.com',
  password: 'test',
}

/**
 * Seeds a test user for e2e admin tests.
 */
export async function seedTestUser(): Promise<void> {
  const payload = await getPayload({ config })
  
  // Delete existing test user if any
  await payload.delete({
    collection: 'users',
    where: {
      email: {
        equals: testUser.email,
      },
    },
  }).catch(() => {}) // Ignore if doesn't exist
  
  // Create fresh test user
  await payload.create({
    collection: 'users',
    data: testUser,
  })
}

/**
 * Cleans up test user after tests.
 */
export async function cleanupTestUser(): Promise<void> {
  const payload = await getPayload({ config })
  
  await payload.delete({
    collection: 'users',
    where: {
        email: {
          equals: testUser.email,
        },
    },
  }).catch(() => {})
}
```

### Admin Panel E2E Tests

**tests/e2e/admin.e2e.spec.ts:**

```typescript
import { test, expect, Page } from '@playwright/test'
import { login } from '../helpers/login'
import { seedTestUser, cleanupTestUser, testUser } from '../helpers/seedUser'

test.describe('Admin Panel', () => {
  let page: Page
  
  // Setup: seed user and login before all tests
  test.beforeAll(async ({ browser }) => {
    await seedTestUser()
    
    const context = await browser.newContext()
    page = await context.newPage()
    
    await login({ page, user: testUser })
  })
  
  // Cleanup after all tests
  test.afterAll(async () => {
    await cleanupTestUser()
  })
  
  test('can navigate to dashboard', async () => {
    await page.goto('http://localhost:3000/admin')
    
    // Verify URL
    await expect(page).toHaveURL('http://localhost:3000/admin')
    
    // Verify dashboard is visible
    const dashboardArtifact = page.locator('span[title="Dashboard"]').first()
    await expect(dashboardArtifact).toBeVisible()
  })
  
  test('can navigate to list view', async () => {
    await page.goto('http://localhost:3000/admin/collections/users')
    
    // Verify URL
    await expect(page).toHaveURL('http://localhost:3000/admin/collections/users')
    
    // Verify list view header
    const listViewArtifact = page.locator('h1', { hasText: 'Users' }).first()
    await expect(listViewArtifact).toBeVisible()
  })
  
  test('can create a new user', async () => {
    await page.goto('http://localhost:3000/admin/collections/users/create')
    
    // Fill in form
    await page.fill('#field-email', `test-${Date.now()}@example.com`)
    await page.fill('#field-password', 'password123')
    
    // Submit
    await page.click('button[type="submit"]')
    
    // Wait for redirect to edit view
    await page.waitForURL(/\/admin\/collections\/users\/[a-zA-Z0-9-_]+/)
    
    // Verify success message or page title
    const title = page.locator('h1')
    await expect(title).toBeVisible()
  })
  
  test('can edit existing user', async () => {
    // Navigate to first user in list
    await page.goto('http://localhost:3000/admin/collections/users')
    
    // Click on first row
    await page.click('[data-testid="row-cell"]:first-child')
    
    // Verify we're on edit page
    await expect(page).toHaveURL(/\/admin\/collections\/users\/[a-zA-Z0-9-_]+/)
    
    // Make changes and save
    const nameField = page.locator('#field-name')
    if (nameField) {
      await nameField.fill('Updated Name')
      await page.click('button[type="submit"]')
      
      // Wait for save to complete
      await page.waitForLoadState('networkidle')
    }
  })
})
```

### Frontend E2E Tests

**tests/e2e/frontend.e2e.spec.ts:**

```typescript
import { test, expect } from '@playwright/test'

test.describe('Frontend', () => {
  test('loads home page', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Verify page title
    await expect(page).toHaveTitle(/Payload/)
    
    // Verify welcome message
    const welcome = page.locator('h1')
    await expect(welcome).toBeVisible()
  })
  
  test('can navigate to admin panel', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Click admin link
    await page.click('a[href*="/admin"]')
    
    // Verify redirect to login (if not authenticated)
    await expect(page).toHaveURL(/\/admin\/login/)
  })
  
  test('displays correct meta tags', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Check meta description
    const metaDescription = page.locator('meta[name="description"]')
    await expect(metaDescription).toHaveAttribute('content', /Payload/i)
  })
})
```

### Testing Authentication Flow

```typescript
test.describe('Authentication Flow', () => {
  test('can log in and out', async ({ page }) => {
    // Start at login page
    await page.goto('http://localhost:3000/admin/login')
    
    // Log in
    await page.fill('#field-email', testUser.email)
    await page.fill('#field-password', testUser.password)
    await page.click('button[type="submit"]')
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('http://localhost:3000/admin')
    
    // Log out
    await page.click('[data-testid="user-menu"]')
    await page.click('text=Logout')
    
    // Verify redirect to login
    await expect(page).toHaveURL('http://localhost:3000/admin/login')
  })
  
  test('shows error on invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/login')
    
    // Submit with wrong password
    await page.fill('#field-email', 'wrong@example.com')
    await page.fill('#field-password', 'wrongpassword')
    await page.click('button[type="submit"]')
    
    // Wait for error message
    const errorMessage = page.locator('[role="alert"]')
    await expect(errorMessage).toBeVisible()
  })
})
```

## Test Best Practices

### 1. Use Descriptive Test Names

```typescript
// Bad
it('creates post', async () => { /* ... */ })

// Good
it('creates a post with title and content in draft status', async () => { /* ... */ })

// Better
it('POST /api/posts - creates new post with required fields', async () => { /* ... */ })
```

### 2. Isolate Test Data

```typescript
// Use unique identifiers for test data
const uniqueId = `test-${Date.now()}`

const post = await payload.create({
  collection: 'posts',
  data: {
    title: `${uniqueId} - Test Post`,
    slug: `${uniqueId}-test-post`,
  },
})
```

### 3. Clean Up After Tests

```typescript
afterEach(async () => {
  // Cleanup test data
  await payload.delete({
    collection: 'posts',
    where: { title: { contains: 'test-' } },
  })
})
```

### 4. Use Test Doubles for External Services

```typescript
// Mock external API calls
vi.mock('@/services/emailService', () => ({
  sendWelcomeEmail: vi.fn().mockResolvedValue(true),
}))
```

### 5. Test Error Cases

```typescript
it('returns 404 when document not found', async () => {
  const post = await payload.findByID({
    collection: 'posts',
    id: 'non-existent-id',
  })
  
  expect(post).toBeNull()
})

it('throws validation error for missing required fields', async () => {
  try {
    await payload.create({
      collection: 'posts',
      data: {}, // Missing required title field
    })
    
    // Should not reach here
    expect(true).toBe(false)
  } catch (error: any) {
    expect(error.name).toBe('ValidationError')
  }
})
```

### 6. Parallel Test Execution

Vitest runs tests in parallel by default. Ensure tests don't share state:

```typescript
// Each test should be independent
it('test 1', async () => {
  const data = await createTestData()
  // ... test logic
  await cleanupTestData(data)
})

it('test 2', async () => {
  const data = await createTestData() // Create fresh data
  // ... test logic
  await cleanupTestData(data)
})
```

### 7. Slow Test Detection

```typescript
// Add timeout for slow tests
it('performs expensive operation', async () => {
  // Test logic
}, 30000) // 30 second timeout
```

## Debugging Tests

### Vitest Debugging

```bash
# Run with verbose output
pnpm vitest --reporter=verbose

# Run single test file in watch mode
pnpm vitest tests/int/api.int.spec.ts --watch

# Open Vitest UI
pnpm vitest --ui
```

### Playwright Debugging

```bash
# Launch Playwright Test UI
pnpm playwright test --ui

# Debug specific test (break on first line)
pnpm playwright test --debug

# Run with video recording
pnpm playwright test --video=on

# Show trace viewer after failure
pnpm playwright show-trace trace.zip
```

### Adding Debug Statements

**Vitest:**

```typescript
it('debugging test', async () => {
  const data = await payload.find({ collection: 'posts' })
  
  console.log('Found posts:', data.docs.length)
  console.log('First post:', data.docs[0])
  
  debug() // Breakpoint for VS Code debugging
  
  expect(data.docs).toBeDefined()
})
```

**Playwright:**

```typescript
test('debugging test', async ({ page }) => {
  await page.goto('http://localhost:3000')
  
  // Slow down for manual inspection
  await page.waitForTimeout(5000)
  
  // Take screenshot
  await page.screenshot({ path: 'debug-screenshot.png' })
  
  expect(page).toHaveTitle(/Payload/)
})
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongo:
        image: mongo:latest
        ports:
          - 27017:27017
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Setup environment
        run: cp .env.example .env && echo "DATABASE_URL=mongodb://127.0.0.1/test" >> .env
      
      - name: Run integration tests
        run: pnpm test:int
      
      - name: Run E2E tests
        run: pnpm test:e2e
      
      - name: Upload test report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playright-report
          path: playwright-report/
```

## Coverage Reporting

### Vitest Coverage Configuration

Add to `vitest.config.mts`:

```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/payload-types.ts',
        'src/**/*.test.ts',
        'src/**/*.spec.ts',
      ],
    },
  },
})
```

Run with coverage:

```bash
pnpm vitest run --coverage
```

View HTML report in `coverage/index.html`.
