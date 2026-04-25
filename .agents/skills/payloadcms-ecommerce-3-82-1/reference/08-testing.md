# Testing

Complete guide to testing strategies, integration tests, E2E tests, and test patterns for the Payload CMS ecommerce template v3.82.1.

## Test Overview

The template includes two types of automated tests:

### Integration Tests (Vitest)

- **Location**: `tests/int/`
- **Runner**: Vitest
- **Purpose**: Test API endpoints, access control, business logic
- **Speed**: Fast (runs in memory, no browser)
- **Use Case**: Unit testing collections, hooks, utilities

### End-to-End Tests (Playwright)

- **Location**: `tests/e2e/`
- **Runner**: Playwright
- **Purpose**: Test complete user flows in real browser
- **Speed**: Slower (real browser automation)
- **Use Case**: Checkout flow, cart operations, admin workflows

## Running Tests

### Run All Tests

```bash
pnpm test
```

Runs both integration and E2E tests sequentially.

### Run Integration Tests Only

```bash
pnpm test:int
```

Runs Vitest integration tests.

### Run E2E Tests Only

```bash
pnpm test:e2e
```

Runs Playwright E2E tests.

### Run Tests in Watch Mode

```bash
# Integration tests with watch mode
pnpm test:int --watch

# E2E tests with UI
pnpm test:e2e --ui
```

## Integration Tests

### Test Configuration

**Vitest Config (vitest.config.mts):**
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./vitest.setup.ts'],
    include: ['tests/int/**/*.spec.ts']
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@payload-config': path.resolve(__dirname, './src/payload.config.ts')
    }
  }
})
```

### Test Setup

**Setup File (vitest.setup.ts):**
```typescript
import { afterAll } from 'vitest'

// Cleanup after all tests
afterAll(async () => {
  // Close database connections
  // Clear test data
})
```

### API Integration Test Example

**Test File (tests/int/api.int.spec.ts):**
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import payload from 'payload'
import type { Product, User } from '@/payload-types'

describe('API Integration Tests', () => {
  let adminUser: User

  beforeEach(async () => {
    // Create admin user for authenticated tests
    adminUser = await payload.create({
      collection: 'users',
      data: {
        email: 'admin@test.com',
        password: 'password123',
        roles: ['admin']
      }
    })
  })

  describe('Products Collection', () => {
    it('should create a product', async () => {
      const product = await payload.create({
        collection: 'products',
        data: {
          title: 'Test Product',
          slug: 'test-product',
          priceInUSD: 29.99,
          enableVariants: false,
          inventory: 100,
          _status: 'published'
        }
      })

      expect(product.title).toBe('Test Product')
      expect(product.priceInUSD).toBe(29.99)
      expect(product._status).toBe('published')
    })

    it('should publish product before storefront visibility', async () => {
      // Create draft product
      const draftProduct = await payload.create({
        collection: 'products',
        data: {
          title: 'Draft Product',
          slug: 'draft-product',
          priceInUSD: 19.99,
          _status: 'draft'
        }
      })

      // Query as anonymous user (should not see draft)
      const anonymousQuery = await payload.query({
        collection: 'products',
        req: { user: null }
      })

      expect(anonymousQuery.docs).not.toIncludeEqual(
        expect.objectContaining({ id: draftProduct.id })
      )

      // Publish product
      const publishedProduct = await payload.update({
        collection: 'products',
        id: draftProduct.id,
        data: { _status: 'published' }
      })

      // Now should be visible
      const publishedQuery = await payload.query({
        collection: 'products',
        req: { user: null }
      })

      expect(publishedQuery.docs).toIncludeEqual(
        expect.objectContaining({ id: publishedProduct.id })
      )
    })

    it('should create product with variants', async () => {
      // Create variant types and options first
      const sizeType = await payload.create({
        collection: 'variantTypes',
        data: { name: 'size' }
      })

      const smallOption = await payload.create({
        collection: 'variantOptions',
        data: {
          label: 'Small',
          variantType: sizeType.id
        }
      })

      const mediumOption = await payload.create({
        collection: 'variantOptions',
        data: {
          label: 'Medium',
          variantType: sizeType.id
        }
      })

      // Create product with variants
      const product = await payload.create({
        collection: 'products',
        data: {
          title: 'Variable Product',
          slug: 'variable-product',
          priceInUSD: 39.99,
          enableVariants: true,
          variantTypes: [sizeType.id],
          variants: {
            variants: [
              {
                variantOption: { size: smallOption.id },
                priceInUSD: 39.99,
                inventory: 50
              },
              {
                variantOption: { size: mediumOption.id },
                priceInUSD: 42.99,
                inventory: 30
              }
            ]
          },
          _status: 'published'
        }
      })

      expect(product.enableVariants).toBe(true)
      expect(product.variants.variants).toHaveLength(2)
    })
  })

  describe('Access Control', () => {
    it('should restrict draft access to admins', async () => {
      const draftProduct = await payload.create({
        collection: 'products',
        data: {
          title: 'Secret Product',
          slug: 'secret-product',
          _status: 'draft'
        },
        req: { user: adminUser }
      })

      // Admin can access draft
      const adminAccess = await payload.findByID({
        collection: 'products',
        id: draftProduct.id,
        req: { user: adminUser }
      })

      expect(adminAccess).toBeDefined()

      // Customer cannot access draft
      const customerUser = await payload.create({
        collection: 'users',
        data: {
          email: 'customer@test.com',
          password: 'password',
          roles: ['customer']
        }
      })

      const customerAccess = payload.findByID({
        collection: 'products',
        id: draftProduct.id,
        req: { user: customerUser }
      })

      await expect(customerAccess).rejects.toThrow()
    })
  })

  describe('Cart Operations', () => {
    it('should create cart and add items', async () => {
      const user = await payload.create({
        collection: 'users',
        data: {
          email: 'shopper@test.com',
          password: 'password',
          roles: ['customer']
        }
      })

      const product = await payload.create({
        collection: 'products',
        data: {
          title: 'Shop Item',
          slug: 'shop-item',
          priceInUSD: 24.99,
          _status: 'published'
        }
      })

      // Create cart
      const cart = await payload.create({
        collection: 'carts',
        data: {
          customer: user.id,
          currency: 'USD',
          items: []
        }
      })

      // Add item to cart
      const updatedCart = await payload.update({
        collection: 'carts',
        id: cart.id,
        data: {
          items: [
            {
              product: product.id,
              quantity: 2,
              price: 24.99,
              total: 49.98
            }
          ],
          subtotal: 49.98,
          total: 49.98
        }
      })

      expect(updatedCart.items).toHaveLength(1)
      expect(updatedCart.items[0].quantity).toBe(2)
      expect(updatedCart.subtotal).toBe(49.98)
    })
  })
})
```

## E2E Tests

### Test Configuration

**Playwright Config (playwright.config.ts):**
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    }
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
})
```

### Admin Panel E2E Test

**Test File (tests/e2e/admin.e2e.spec.ts):**
```typescript
import { test, expect } from '@playwright/test'

test.describe('Admin Panel', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/admin/login')
    await page.fill('input[type="email"]', 'admin@example.com')
    await page.fill('input[type="password"]', 'password')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/admin')
  })

  test('should create a new product', async ({ page }) => {
    // Navigate to products
    await page.goto('/admin/collections/products')

    // Click create new
    await page.click('text=Create New Product')
    await expect(page).toHaveURL('/admin/collections/products/new')

    // Fill product form
    await page.fill('input[name="title"]', 'E2E Test Product')
    await page.fill('input[name="slug"]', 'e2e-test-product')

    // Set price
    await page.fill('input[name="priceInUSD"]', '49.99')

    // Enable variants toggle
    await page.click('input[type="checkbox"][name="enableVariants"]')

    // Publish
    await page.click('text=Publish')

    // Wait for confirmation
    await expect(page.locator('text=Product created')).toBeVisible()
  })

  test('should view order details', async ({ page }) => {
    // Navigate to orders
    await page.goto('/admin/collections/orders')

    // Click on first order
    const firstOrder = page.locator('tr').first()
    await firstOrder.click()

    // Verify order details visible
    await expect(page.locator('text=Order Details')).toBeVisible()
  })
})
```

### Frontend E2E Test

**Test File (tests/e2e/frontend.e2e.spec.ts):**
```typescript
import { test, expect } from '@playwright/test'

test.describe('Storefront', () => {
  test.describe('Product Browsing', () => {
    test('should display product listing', async ({ page }) => {
      await page.goto('/shop')

      // Verify products are displayed
      const products = page.locator('.product-card')
      await expect(products).toHaveCount({ min: 1 })

      // Verify first product has image and title
      const firstProduct = products.first()
      await expect(firstProduct.locator('img')).toBeVisible()
      await expect(firstProduct.locator('h3')).toBeVisible()
    })

    test('should filter products by category', async ({ page }) => {
      await page.goto('/shop')

      // Click on category filter
      await page.click('text=Clothing')

      // Verify URL updated
      await expect(page).toHaveURL('/shop/clothing')

      // Verify filtered products
      const products = page.locator('.product-card')
      await expect(products).toHaveCount({ min: 1 })
    })

    test('should sort products by price', async ({ page }) => {
      await page.goto('/shop')

      // Select price sort
      await page.selectOption('select[name="sort"]', 'Price: Low to high')

      // Verify products sorted
      const products = page.locator('.product-card')
      const prices = await products.allTextContents()

      // Parse and verify ascending order
      // (implementation depends on price display format)
    })
  })

  test.describe('Product Details', () => {
    test('should navigate to product page', async ({ page }) => {
      await page.goto('/shop')

      // Click on first product
      await page.click('.product-card:first-of-type')

      // Verify navigated to product page
      await expect(page).toHaveURL('/products/*')

      // Verify product details visible
      await expect(page.locator('h1.product-title')).toBeVisible()
      await expect(page.locator('.product-price')).toBeVisible()
    })

    test('should select variant and add to cart', async ({ page }) => {
      await page.goto('/products/tshirt')

      // Select size
      await page.click('input[value="medium"]')

      // Select color
      await page.click('input[value="blue"]')

      // Verify variant selected
      await expect(page.locator('.selected-variant')).toContainText('Medium, Blue')

      // Add to cart
      await page.click('button:has-text("Add to Cart")')

      // Verify cart updated
      await expect(page.locator('.cart-count')).toContainText('1')
    })
  })

  test.describe('Shopping Cart', () => {
    test('should view cart contents', async ({ page }) => {
      // Add item to cart first
      await page.goto('/products/tshirt')
      await page.click('button:has-text("Add to Cart")')

      // Navigate to cart
      await page.goto('/cart')

      // Verify cart items
      await expect(page.locator('.cart-item')).toHaveCount({ min: 1 })
      await expect(page.locator('.cart-total')).toBeVisible()
    })

    test('should update item quantity', async ({ page }) => {
      await page.goto('/cart')

      // Increase quantity
      await page.click('.quantity-selector button:has-text("+")')

      // Verify total updated
      await expect(page.locator('.cart-total')).toContainText('$')
    })

    test('should remove item from cart', async ({ page }) => {
      await page.goto('/cart')

      const initialCount = await page.locator('.cart-item').count()

      // Remove first item
      await page.click('.cart-item:first-of-type button:has-text("Remove")')

      // Verify item removed
      await expect(page.locator('.cart-item')).toHaveCount(initialCount - 1)
    })
  })

  test.describe('Checkout Flow', () => {
    test('should complete checkout with Stripe test card', async ({ page }) => {
      // Setup: Add item to cart
      await page.goto('/products/tshirt')
      await page.click('button:has-text("Add to Cart")')

      // Navigate to checkout
      await page.goto('/checkout')

      // Fill shipping address
      await page.fill('input[name="line1"]', '123 Test Street')
      await page.fill('input[name="city"]', 'San Francisco')
      await page.fill('input[name="state"]', 'CA')
      await page.fill('input[name="zip"]', '94102')
      await page.fill('input[name="country"]', 'US')

      // Check "Same for billing"
      await page.click('input[type="checkbox"][name="sameAsBilling"]')

      // Fill Stripe test card
      await page.fill('#card-number', '4242424242424242')
      await page.fill('#card-expiry', '1225')
      await page.fill('#card-cvc', '123')

      // Submit order
      await page.click('button:has-text("Place Order")')

      // Wait for confirmation page
      await expect(page).toHaveURL('/checkout/confirm-order*')
      await expect(page.locator('text=Order Confirmed')).toBeVisible()
    })

    test('should handle payment failure', async ({ page }) => {
      await page.goto('/checkout')

      // Fill address...

      // Use decline card
      await page.fill('#card-number', '4000000000000002')
      await page.fill('#card-expiry', '1225')
      await page.fill('#card-cvc', '123')

      // Submit
      await page.click('button:has-text("Place Order")')

      // Verify error displayed
      await expect(page.locator('.payment-error')).toBeVisible()
    })
  })

  test.describe('User Authentication', () => {
    test('should register new account', async ({ page }) => {
      await page.goto('/create-account')

      await page.fill('input[name="name"]', 'Test User')
      await page.fill('input[name="email"]', 'testuser@example.com')
      await page.fill('input[name="password"]', 'password123')
      await page.fill('input[name="confirmPassword"]', 'password123')

      await page.click('button:has-text("Create Account")')

      // Verify redirect to login or success message
      await expect(page).toHaveURL('/login')
    })

    test('should login and access account dashboard', async ({ page }) => {
      await page.goto('/login')

      await page.fill('input[name="email"]', 'customer@example.com')
      await page.fill('input[name="password"]', 'password')

      await page.click('button:has-text("Login")')

      // Verify redirect to account page
      await expect(page).toHaveURL('/account')

      // Verify account info visible
      await expect(page.locator('text=My Account')).toBeVisible()
    })

    test('should view order history', async ({ page }) => {
      // Login first
      await page.goto('/login')
      await page.fill('input[name="email"]', 'customer@example.com')
      await page.fill('input[name="password"]', 'password')
      await page.click('button:has-text("Login")')

      // Navigate to orders
      await page.goto('/orders')

      // Verify order history displayed
      await expect(page.locator('text=Order History')).toBeVisible()
    })

    test('should logout', async ({ page }) => {
      // Login first
      await page.goto('/login')
      await page.fill('input[name="email"]', 'customer@example.com')
      await page.fill('input[name="password"]', 'password')
      await page.click('button:has-text("Login")')

      // Logout
      await page.click('a:has-text("Logout")')

      // Verify redirect to homepage
      await expect(page).toHaveURL('/')
    })
  })
})
```

## Test Helpers

### Test Configuration

**Helper File (tests/helpers/config.ts):**
```typescript
export const testUser = {
  email: 'customer@example.com',
  password: 'password'
}

export const testAdmin = {
  email: 'admin@example.com',
  password: 'password'
}

export const testProduct = {
  title: 'Test Product',
  slug: 'test-product',
  priceInUSD: 29.99,
  enableVariants: false,
  inventory: 100,
  _status: 'published'
}

export const stripeTestCard = {
  number: '4242424242424242',
  expiry: '1225',
  cvc: '123'
}

export const stripeDeclineCard = {
  number: '4000000000000002',
  expiry: '1225',
  cvc: '123'
}
```

### Payload Test Initialization

**Helper File (tests/helpers/initPayload.ts):**
```typescript
import { initPayloadTest } from '@payloadcms/local-api/tests'
import config from '@payload-config'

export const initTests = async () => {
  return await initPayloadTest({
    init: {
      cwd: import.meta.dirname,
      config,
      localAPI: true
    }
  })
}
```

## Test Best Practices

### Integration Tests

1. **Isolate tests**: Each test should be independent
2. **Clean up**: Delete test data after each test
3. **Use fixtures**: Reuse test data with factories
4. **Test edge cases**: Invalid input, permission errors
5. **Mock external services**: Don't call real Stripe API

### E2E Tests

1. **Stable selectors**: Use data-testid attributes
2. **Wait for elements**: Use Playwright auto-waiting
3. **Screenshot on failure**: Capture visual state
4. **Run in CI**: Catch regressions early
5. **Keep fast**: Minimize test duration

### Test Data Management

**Seeding Test Data:**
```typescript
beforeEach(async () => {
  // Create test product
  await payload.create({
    collection: 'products',
    data: testProduct
  })
})

afterEach(async () => {
  // Clean up test data
  const products = await payload.query({
    collection: 'products',
    where: { slug: { equals: 'test-product' } }
  })

  for (const product of products.docs) {
    await payload.delete({
      collection: 'products',
      id: product.id
    })
  }
})
```

## Debugging Tests

### Integration Test Debugging

```typescript
// Add debug logging
console.log('Test data:', JSON.stringify(product, null, 2))

// Use debugger in watch mode
debugger

// Fail fast with detailed errors
expect(product.title).toBe('Expected Title') || 
  console.error('Product title mismatch:', product.title)
```

### E2E Test Debugging

```typescript
// Slow down test execution
await page.waitForTimeout(2000)

// Take manual screenshot
await page.screenshot({ path: 'debug.png' })

// Run single test in UI mode
pnpm test:e2e --ui

// Console logging
console.log('Current URL:', page.url())
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
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: pnpm install

      - name: Run integration tests
        run: pnpm test:int
        env:
          DATABASE_URL: mongodb://127.0.0.1/test-db
          PAYLOAD_SECRET: test-secret
          STRIPE_SECRET_KEY: sk_test_fake
          NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: pk_test_fake
          STRIPE_WEBHOOKS_SIGNING_SECRET: whsec_fake

      - name: Run E2E tests
        run: pnpm test:e2e
        env:
          DATABASE_URL: mongodb://127.0.0.1/test-db
          PAYLOAD_SECRET: test-secret
          STRIPE_SECRET_KEY: sk_test_fake
          NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: pk_test_fake
          STRIPE_WEBHOOKS_SIGNING_SECRET: whsec_fake

      - name: Upload test report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-report
          path: playwright-report/
```

## Common Test Issues

### Database Connection Errors

**Issue**: Tests fail with "MongoDB connection failed"

**Solution**:
```bash
# Ensure MongoDB is running
docker run -d -p 27017:27017 mongo:latest

# Use correct DATABASE_URL
DATABASE_URL=mongodb://127.0.0.1/test-db
```

### Stripe Webhook Tests

**Issue**: Payment tests fail without real webhook

**Solution**: Mock webhook handling in tests:
```typescript
// Mock Stripe webhook
const mockWebhook = jest.fn().mockImplementation(() => {
  // Simulate payment success
})
```

See [Troubleshooting Guide](10-troubleshooting.md) for more solutions.
