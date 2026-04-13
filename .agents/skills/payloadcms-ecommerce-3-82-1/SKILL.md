---
name: payloadcms-ecommerce-3-82-1
description: Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products, variants, carts, orders, Stripe payments, multi-currency support, user accounts, guest checkout, and transaction tracking. Use when building e-commerce platforms, online stores, marketplaces, or any digital commerce project requiring product catalogs, shopping carts, order management, payment processing, customer accounts, and inventory management following official Payload best practices.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - payload-cms
  - ecommerce
  - online-store
  - nextjs
  - stripe
  - payments
  - shopping-cart
  - inventory-management
category: development
required_environment_variables:
  - name: PAYLOAD_SECRET
    prompt: "Enter your Payload secret key"
    help: "Generate with: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\""
    required_for: "application security and session management"
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "Example: mongodb://localhost:27017/payload or use MongoDB Atlas"
    required_for: "database connectivity"
  - name: STRIPE_SECRET_KEY
    prompt: "Enter your Stripe secret key"
    help: "Get from Stripe dashboard: sk_test_... for test, sk_live_... for production"
    required_for: "payment processing"
  - name: STRIPE_PUBLISHABLE_KEY
    prompt: "Enter your Stripe publishable key"
    help: "Get from Stripe dashboard: pk_test_... for test, pk_live_... for production"
    required_for: "frontend payment integration"
  - name: PAYLOAD_PUBLIC_APP_URL
    prompt: "Enter your public app URL"
    help: "Example: http://localhost:3000 or https://your-store.com"
    required_for: "order emails and payment redirects"
---

# Payload CMS Ecommerce Template 3.82.1

The ecommerce template provides a production-ready, full-featured online store with product management, shopping carts, order processing, Stripe payment integration, multi-currency support, user accounts, and guest checkout. It includes pre-configured collections for Products, Variants, Carts, Orders, Transactions, and comprehensive access control for secure commerce operations.

**Status**: This template is in **BETA** - suitable for development and testing, with production readiness improving in future releases.

## When to Use

- Building online stores or e-commerce platforms
- Needing product catalogs with variants and pricing
- Requiring shopping cart functionality
- Implementing secure checkout processes
- Integrating Stripe payment processing
- Managing customer accounts and order history
- Supporting guest checkout options
- Handling multi-currency pricing
- Tracking transactions and order fulfillment
- Following official Payload ecommerce best practices

## Quick Start

### Installation

```bash
# Create new project from ecommerce template
pnpx create-payload-app my-store -t ecommerce

# Or use npx with specific version
npx create-payload@3.82.1 --template ecommerce

# Using bun
bunx create-payload@3.82.1 --template ecommerce
```

### Project Structure

```
my-store/
├── src/
│   ├── app/
│   │   ├── (frontend)/
│   │   │   ├── products/
│   │   │   ├── cart/
│   │   │   ├── checkout/
│   │   │   ├── account/
│   │   │   └── orders/
│   │   ├── (payload)/
│   │   │   └── admin/
│   │   ├── api/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── collections/
│   │   ├── Products/
│   │   ├── Categories/
│   │   ├── Media/
│   │   ├── Users/
│   │   └── Pages/
│   ├── globals/
│   │   ├── Header/
│   │   └── Footer/
│   ├── components/          # React components
│   ├── fields/              # Custom field configurations
│   ├── plugins/             # Ecommerce plugin config
│   ├── payload.config.ts    # Main configuration
│   └── utilities/           # Helper functions
├── .env.example
├── next.config.js
├── package.json
└── tsconfig.json
```

### Environment Setup

```bash title=".env"
# Required - Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
PAYLOAD_SECRET=your-generated-secret-here

# MongoDB connection string
DATABASE_URL=mongodb://localhost:27017/payload

# Stripe API Keys (get from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key

# Public URL for emails and redirects
PAYLOAD_PUBLIC_APP_URL=http://localhost:3000

# Optional - Cron job secret for background jobs
CRON_SECRET=your-cron-secret

# Optional - Disable telemetry
TELEMETRY_ENABLED=false
```

### Run Development Server

```bash
# Install dependencies
pnpm install

# Start MongoDB (if not running)
mongod --dbpath ./data  # Or use MongoDB Atlas

# Start development server
pnpm dev

# Access:
# - Admin panel: http://localhost:3000/admin
# - Storefront: http://localhost:3000
```

## Core Ecommerce Collections

### Products Collection

Main product catalog with variants, pricing, and inventory management.

**Key Features:**
- Multi-currency pricing
- Product variants (size, color, etc.)
- Inventory tracking
- Rich text descriptions
- Category associations
- SEO optimization
- Draft/publish workflow

```typescript title="src/collections/Products/index.ts"
export const Products: CollectionConfig = {
  slug: 'products',
  admin: {
    useAsTitle: 'name',
    defaultColumns: ['name', 'status', 'price'],
  },
  access: {
    read: ({ req }) => {
      if (req.user) return true
      return { status: { equals: 'published' } }
    },
  },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true },
    
    // Rich text description
    {
      name: 'description',
      type: 'richText',
    },
    
    // Featured image
    {
      name: 'featuredImage',
      type: 'upload',
      relationTo: 'media',
    },
    
    // Categories (many-to-many)
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
    },
    
    // Variants (size, color, etc.)
    {
      name: 'variants',
      type: 'array',
      fields: [
        { name: 'name', type: 'text' },
        { name: 'sku', type: 'text', unique: true },
        {
          name: 'prices',
          type: 'array',
          fields: [
            { name: 'currency', type: 'select', options: ['USD', 'EUR', 'GBP'] },
            { name: 'amount', type: 'number', admin: { step: 0.01 } },
          ],
        },
        { name: 'inventory', type: 'number' },
      ],
    },
    
    // SEO fields
    seoFields(),
    
    // Status for drafts
    {
      name: 'status',
      type: 'select',
      options: ['draft', 'published'],
      defaultValue: 'draft',
    },
  ],
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
}
```

### Carts Collection

Shopping cart management for both authenticated users and guests.

**Key Features:**
- User-associated carts
- Guest cart support
- Automatic cart merging on login
- Inventory validation
- Price calculation
- Expiration handling

```typescript title="src/collections/Carts.ts"
export const Carts: CollectionConfig = {
  slug: 'carts',
  access: {
    read: ({ req, doc }) => {
      if (req.user?.id === doc?.userId) return true
      if (!doc?.userId) return true // Guest carts are public by ID
      return false
    },
    update: ({ req, doc }) => {
      return req.user?.id === doc?.userId || !doc?.userId
    },
  },
  fields: [
    {
      name: 'userId',
      type: 'relationship',
      relationTo: 'users',
      required: false,
    },
    {
      name: 'items',
      type: 'array',
      fields: [
        {
          name: 'product',
          type: 'relationship',
          relationTo: 'products',
          required: true,
        },
        {
          name: 'variant',
          type: 'relationship',
          relationTo: 'productVariants',
        },
        { name: 'quantity', type: 'number', min: 1, defaultValue: 1 },
        { name: 'price', type: 'number', admin: { step: 0.01 } },
      ],
    },
    { name: 'subtotal', type: 'number', admin: { step: 0.01 } },
    { name: 'tax', type: 'number', admin: { step: 0.01 } },
    { name: 'total', type: 'number', admin: { step: 0.01 } },
  ],
}
```

### Orders Collection

Order tracking and management with secure access control.

**Key Features:**
- Order status tracking
- Customer association
- Guest order access via token
- Payment status tracking
- Fulfillment tracking
- Order history

```typescript title="src/collections/Orders.ts"
export const Orders: CollectionConfig = {
  slug: 'orders',
  access: {
    read: ({ req, doc }) => {
      if (req.user?.roles?.includes('admin')) return true
      if (req.user?.id === doc?.userId) return true
      
      // Guest access via email + token
      if (req.data?.email && req.data?.accessToken) {
        return doc?.email === req.data.email && 
               doc?.accessToken === req.data.accessToken
      }
      return false
    },
  },
  fields: [
    {
      name: 'userId',
      type: 'relationship',
      relationTo: 'users',
      required: false,
    },
    { name: 'email', type: 'text', required: true },
    
    // Secure access token for guest orders
    {
      name: 'accessToken',
      type: 'text',
      admin: { hidden: true },
    },
    
    // Order items
    {
      name: 'items',
      type: 'array',
      fields: [
        { name: 'product', type: 'relationship', relationTo: 'products' },
        { name: 'variant', type: 'relationship', relationTo: 'productVariants' },
        { name: 'quantity', type: 'number' },
        { name: 'price', type: 'number' },
      ],
    },
    
    // Pricing
    { name: 'subtotal', type: 'number' },
    { name: 'tax', type: 'number' },
    { name: 'total', type: 'number' },
    { name: 'currency', type: 'select', options: ['USD', 'EUR', 'GBP'] },
    
    // Shipping address
    {
      name: 'shippingAddress',
      type: 'group',
      fields: [
        { name: 'address', type: 'text' },
        { name: 'city', type: 'text' },
        { name: 'country', type: 'text' },
        { name: 'postalCode', type: 'text' },
      ],
    },
    
    // Status tracking
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Pending', value: 'pending' },
        { label: 'Processing', value: 'processing' },
        { label: 'Completed', value: 'completed' },
        { label: 'Cancelled', value: 'cancelled' },
      ],
      defaultValue: 'pending',
    },
    
    // Payment tracking
    {
      name: 'paymentStatus',
      type: 'select',
      options: ['pending', 'paid', 'failed', 'refunded'],
      defaultValue: 'pending',
    },
  ],
}
```

### Transactions Collection

Payment transaction tracking for Stripe integration.

**Key Features:**
- Stripe payment intent tracking
- Transaction status monitoring
- Webhook event logging
- Refund tracking
- Admin-only access

```typescript title="src/collections/Transactions.ts"
export const Transactions: CollectionConfig = {
  slug: 'transactions',
  access: {
    read: ({ req }) => req.user?.roles?.includes('admin'),
    create: ({ req }) => req.user?.roles?.includes('admin'),
    update: ({ req }) => req.user?.roles?.includes('admin'),
    delete: ({ req }) => req.user?.roles?.includes('admin'),
  },
  fields: [
    {
      name: 'order',
      type: 'relationship',
      relationTo: 'orders',
      required: true,
    },
    { name: 'stripePaymentIntent', type: 'text' },
    { name: 'amount', type: 'number' },
    { name: 'currency', type: 'text' },
    
    // Status tracking
    {
      name: 'status',
      type: 'select',
      options: ['pending', 'succeeded', 'failed', 'refunded'],
      defaultValue: 'pending',
    },
    
    // Webhook events
    {
      name: 'events',
      type: 'array',
      fields: [
        { name: 'type', type: 'text' },
        { name: 'timestamp', type: 'date' },
        { name: 'data', type: 'json' },
      ],
    },
  ],
}
```

### Users Collection (Enhanced)

Customer accounts with order history and saved addresses.

```typescript title="src/collections/Users.ts"
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: {
    useAsTitle: 'email',
  },
  fields: [
    // Auth fields (auto-generated)
    
    // Custom fields
    { name: 'displayName', type: 'text' },
    
    // Role-based access
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      options: ['admin', 'customer'],
      defaultValue: ['customer'],
      saveToJWT: true,
    },
    
    // Saved addresses for faster checkout
    {
      name: 'addresses',
      type: 'array',
      fields: [
        { name: 'label', type: 'text' },
        { name: 'address', type: 'text' },
        { name: 'city', type: 'text' },
        { name: 'country', type: 'text' },
        { name: 'postalCode', type: 'text' },
      ],
    },
  ],
}
```

## Ecommerce Plugin Features

The template includes the official Payload ecommerce plugin which adds:

### Products & Variants
- Multi-currency pricing support
- SKU management
- Inventory tracking per variant
- Product categorization

### Carts
- Persistent carts for logged-in users
- Guest cart support with automatic merge on login
- Real-time inventory validation
- Automatic price calculations

### Orders
- Secure order creation
- Guest order access via email + token
- Order status workflow
- Email notifications

### Transactions
- Stripe payment integration
- Webhook event handling
- Payment status tracking
- Refund support

### Addresses
- Customer address management
- Shipping address validation
- Address auto-complete

## Stripe Integration

### Configuration

```typescript title="src/plugins/stripe.ts"
import { stripePlugin } from '@payloadcms/plugin-stripe'

export const stripeConfig = stripePlugin({
  secretKey: process.env.STRIPE_SECRET_KEY,
  publishableKey: process.env.STRIPE_PUBLISHABLE_KEY,
  productsCollection: 'products',
  ordersCollection: 'orders',
  transactionsCollection: 'transactions',
})
```

### Payment Flow

1. **Cart to Checkout**: Customer clicks checkout, system validates inventory
2. **Stripe Intent**: Create Stripe PaymentIntent with cart total
3. **Payment**: Customer enters card details in Stripe Elements
4. **Confirmation**: Stripe confirms payment, webhook updates order status
5. **Fulfillment**: Order marked as paid, confirmation email sent

### Webhook Handling

```typescript title="src/endpoints/stripe-webhook.ts"
export const stripeWebhook = async (req: Request) => {
  const body = await req.text()
  const sig = req.headers.get('stripe-signature')
  
  const event = stripe.webhooks.constructEvent(
    body,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  )
  
  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSuccess(event.data.object)
      break
    case 'payment_intent.payment_failed':
      await handlePaymentFailure(event.data.object)
      break
  }
  
  return new Response('OK', { status: 200 })
}
```

## Guest Checkout

Secure guest checkout without account creation:

### Flow
1. Guest adds items to cart
2. Enters email and shipping info at checkout
3. Completes payment via Stripe
4. Receives order confirmation email
5. Can view order via secure link with access token

### Security
- Unique `accessToken` generated per order
- Token required along with email to view order
- Prevents order enumeration attacks
- Tokens expire after 90 days

### Order Lookup

```typescript title="src/app/api/orders/lookup/route.ts"
export async function POST(request: Request) {
  const { email, orderId } = await request.json()
  
  const order = await payload.findOne({
    collection: 'orders',
    where: {
      and: [
        { email: { equals: email } },
        { id: { equals: orderId } },
      ],
    },
  })
  
  if (order) {
    // Send email with secure access link
    await sendOrderAccessEmail(email, order.accessToken)
  }
  
  return Response.json({ success: true })
}
```

## Multi-Currency Support

### Configuration

Support multiple currencies with automatic conversion:

```typescript
// Product variant pricing
{
  name: 'prices',
  type: 'array',
  fields: [
    { 
      name: 'currency', 
      type: 'select', 
      options: [
        { label: 'USD ($)', value: 'USD' },
        { label: 'EUR (€)', value: 'EUR' },
        { label: 'GBP (£)', value: 'GBP' },
      ],
    },
    { name: 'amount', type: 'number', admin: { step: 0.01 } },
  ],
}
```

### Currency Detection

```typescript
// Detect user currency from IP or preference
const detectCurrency = async (req: Request) => {
  const locale = req.headers.get('accept-language')?.split(',')[0]
  
  const currencyMap: Record<string, string> = {
    'en-US': 'USD',
    'de-DE': 'EUR',
    'en-GB': 'GBP',
  }
  
  return currencyMap[locale] || 'USD'
}
```

## Access Control

Comprehensive security for ecommerce operations:

### Role-Based Permissions

**Admin Role:**
- Full access to all collections
- Manage products, orders, transactions
- View analytics and reports
- Process refunds

**Customer Role:**
- View own orders and profile
- Manage saved addresses
- Update own cart
- View published products

**Guest Access:**
- Browse published products
- Create guest carts
- Complete checkout with email
- View own orders via token

### Collection Access Matrix

| Collection | Admin | Customer | Guest |
|------------|-------|----------|-------|
| Products (all) | ✅ | ✅ (published only) | ✅ (published only) |
| Carts | ✅ | ✅ (own only) | ✅ (by ID) |
| Orders | ✅ | ✅ (own only) | ✅ (via token) |
| Transactions | ✅ | ❌ | ❌ |
| Users | ✅ | ✅ (own only) | ❌ |

## SEO Features

### Product SEO

```typescript
fields: [
  {
    name: 'seo',
    type: 'group',
    fields: [
      { name: 'title', type: 'text' },
      { name: 'description', type: 'textarea' },
      { name: 'keywords', type: 'array', fields: [{ name: 'keyword', type: 'text' }] },
      { name: 'ogImage', type: 'upload', relationTo: 'media' },
    ],
  },
]
```

### Dynamic Metadata

```typescript title="src/app/products/[slug]/page.tsx"
export async function generateMetadata({ params }) {
  const product = await payload.findBySlug({
    collection: 'products',
    slug: params.slug,
  })
  
  return {
    title: product.seo?.title || product.name,
    description: product.seo?.description,
    openGraph: {
      images: [product.seo?.ogImage?.url || product.featuredImage.url],
    },
    structuredData: {
      '@type': 'Product',
      name: product.name,
      offers: {
        '@type': 'Offer',
        price: product.variants[0].prices[0].amount,
        priceCurrency: product.variants[0].prices[0].currency,
      },
    },
  }
}
```

## Scripts

```json title="package.json"
{
  "scripts": {
    "build": "next build",
    "dev": "next dev",
    "generate:types": "payload generate:types",
    "lint": "next lint",
    "start": "next start",
    "stripe:listen": "stripe listen --forward-to localhost:3000/api/stripe/webhook"
  }
}
```

## Development Workflow

### 1. Add New Product Type

```typescript
// Extend product variants
{
  name: 'variants',
  type: 'array',
  fields: [
    // ... existing fields
    {
      name: 'type',
      type: 'select',
      options: ['physical', 'digital', 'service'],
    },
  ],
}
```

### 2. Customize Checkout Flow

```typescript
// Add custom checkout steps
const checkoutSteps = [
  'cart-review',
  'shipping-info',
  'payment-method',
  'order-confirmation',
]
```

### 3. Implement Custom Pricing

```typescript
// Hook for dynamic pricing
hooks: {
  beforeChange: [
    async ({ data, operation }) => {
      if (operation === 'create') {
        // Apply discounts, taxes, etc.
        data.total = calculateTotal(data.items)
      }
      return data
    },
  ],
}
```

## Deployment

### Production Checklist

- [ ] Set production `PAYLOAD_SECRET`
- [ ] Configure production MongoDB
- [ ] Use live Stripe keys (`sk_live_...`, `pk_live_...`)
- [ ] Set up Stripe webhook endpoint
- [ ] Configure email service for order notifications
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Test checkout flow end-to-end

### Docker Deployment

```dockerfile title="Dockerfile"
FROM oven/bun:1.3.12

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen

COPY . .
RUN bun run generate:types
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
```

### Environment Variables (Production)

```bash title=".env.production"
PAYLOAD_SECRET=your-production-secret
DATABASE_URL=mongodb+srv://atlas-connection-string
STRIPE_SECRET_KEY=sk_live_production-key
STRIPE_PUBLISHABLE_KEY=pk_live_production-key
STRIPE_WEBHOOK_SECRET=whsec_production-secret
PAYLOAD_PUBLIC_APP_URL=https://your-store.com
NODE_ENV=production
```

## Troubleshooting

### Stripe Webhooks Not Working

**Problem**: Payment succeeded but order not updated

**Solution**:
```bash
# Local development
stripe listen --forward-to localhost:3000/api/stripe/webhook

# Production - verify webhook URL in Stripe dashboard
# Settings > Developers > Webhooks > Endpoints
```

### Cart Not Persisting

**Problem**: Guest cart lost on page refresh

**Solution**: Ensure cart is saved to localStorage or cookies:
```typescript
const saveCartToStorage = (cart) => {
  localStorage.setItem('guest-cart', JSON.stringify(cart))
}
```

### Currency Conversion Issues

**Problem**: Prices showing in wrong currency

**Solution**: Verify currency detection and product pricing:
```typescript
// Ensure all currencies are priced for each product
product.variants.forEach(variant => {
  ['USD', 'EUR', 'GBP'].forEach(currency => {
    if (!variant.prices.find(p => p.currency === currency)) {
      console.warn(`Missing ${currency} price for variant ${variant.name}`)
    }
  })
})
```

## Package Dependencies

Key packages included:
- `@payloadcms/db-mongodb` - MongoDB adapter
- `@payloadcms/richtext-lexical` - Lexical editor
- `@payloadcms/plugin-stripe` - Stripe integration (if using)
- `next` - Next.js framework
- `payload` - Payload CMS core
- `stripe` - Stripe API client

## Security Best Practices

### 1. Order Access Control

**CRITICAL**: Always validate order access:
```typescript
// ✅ CORRECT
const canAccess = req.user?.id === order.userId || 
                  (req.data.email === order.email && 
                   req.data.accessToken === order.accessToken)

// ❌ WRONG - Allows enumeration
const order = await payload.findOne({ collection: 'orders', id: orderId })
```

### 2. Payment Security

- Never store raw card data
- Use Stripe Elements for PCI compliance
- Validate webhook signatures
- Implement idempotency keys

### 3. Price Validation

**CRITICAL**: Always calculate prices server-side:
```typescript
// ✅ CORRECT - Server calculates total
const total = cart.items.reduce((sum, item) => {
  const product = await getProduct(item.productId)
  return sum + (product.price * item.quantity)
}, 0)

// ❌ WRONG - Trust client prices
const total = cart.items.reduce((sum, item) => sum + item.price, 0)
```

## Next Steps

1. **Configure Stripe**: Set up test keys and webhook
2. **Add Products**: Create product catalog with variants
3. **Customize Storefront**: Brand the checkout flow
4. **Set Up Email**: Configure order notifications
5. **Test Checkout**: Complete end-to-end test purchases
6. **Go Live**: Switch to production Stripe keys

## Resources

- [Payload Ecommerce Template](https://github.com/payloadcms/payload/tree/v3.82.1/templates/ecommerce)
- [Payload Ecommerce Plugin](https://payloadcms.com/docs/ecommerce/plugin)
- [Stripe Documentation](https://stripe.com/docs)
- [Payload Access Control](https://payloadcms.com/docs/access-control/overview)

## Related Skills

- `payloadcms-3-82-1` - Complete Payload CMS development guide
- `payloadcms-blank-3-82-1` - Minimal starter template
- `payloadcms-website-3-82-1` - Website and blog template
- `stripe-node` - Stripe API integration patterns
