---
name: payloadcms-ecommerce-3-82-1
description: Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products, variants, carts, orders, Stripe payments, multi-currency support, user accounts, guest checkout, and transaction tracking. Use when building e-commerce platforms, online stores, marketplaces, or any digital commerce project requiring product catalogs, shopping carts, order management, payment processing, customer accounts, and inventory management following official Payload best practices.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
maintainer: Tangled Skills Community
license: MIT
tags:
  - payloadcms
  - nextjs
  - typescript
  - ecommerce
  - mongodb
  - stripe
  - payments
  - online-store
  - shopping-cart
category: development
required_environment_variables:
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "For local development: mongodb://127.0.0.1/your-database-name. For production, use MongoDB Atlas or your hosted MongoDB instance."
    required_for: database connectivity
  - name: PAYLOAD_SECRET
    prompt: "Enter a secret key for Payload (minimum 32 characters)"
    help: "Generate using: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\". Required for session encryption and JWT signing."
    required_for: application security
  - name: STRIPE_SECRET_KEY
    prompt: "Enter your Stripe secret key (sk_test_... for testing)"
    help: "Get from Stripe Dashboard > Developers > API Keys. Use test keys for development, live keys for production."
    required_for: payment processing
  - name: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
    prompt: "Enter your Stripe publishable key (pk_test_... for testing)"
    help: "Get from Stripe Dashboard > Developers > API Keys. Use test keys for development, live keys for production."
    required_for: payment processing frontend
  - name: STRIPE_WEBHOOKS_SIGNING_SECRET
    prompt: "Enter your Stripe webhook signing secret (whsec_...)"
    help: "Get from Stripe Dashboard > Developers > Webhooks. Create a webhook endpoint to receive this secret."
    required_for: payment webhook verification
---

# Payload CMS Ecommerce Template v3.82.1


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products, variants, carts, orders, Stripe payments, multi-currency support, user accounts, guest checkout, and transaction tracking. Use when building e-commerce platforms, online stores, marketplaces, or any digital commerce project requiring product catalogs, shopping carts, order management, payment processing, customer accounts, and inventory management following official Payload best practices.

A production-ready, enterprise-grade ecommerce template for building online stores, marketplaces, and digital commerce platforms with Payload CMS v3.82.1, Next.js 16.2.2, TypeScript, MongoDB, Stripe payments, and advanced features including product variants, shopping carts, order management, customer accounts, guest checkout, multi-currency support, and transaction tracking.

**Note:** This template is in **BETA**. Use for learning and development; review thoroughly before production deployment.

## When to Use

- Building online stores or e-commerce platforms
- Creating marketplaces with product catalogs
- Implementing shopping cart and checkout flows
- Integrating Stripe payment processing
- Managing product variants (size, color, etc.)
- Handling customer accounts and order history
- Supporting guest checkout with secure order access
- Processing multi-currency transactions
- Tracking inventory and product availability
- Building subscription or recurring billing systems

## What This Template Includes

### Pre-configured Collections

**Core Content:**
- **Users**: Authentication-enabled with admin/customer roles, order history, saved addresses
- **Pages**: Layout builder-enabled pages with draft support, live preview, SEO fields
- **Media**: Upload collection with image optimization for products and pages
- **Categories**: Product taxonomy for organizing catalog

**Ecommerce (via @payloadcms/plugin-ecommerce):**
- **Products**: Product catalog with variants, pricing per currency, inventory tracking, gallery images
- **Variants**: Product variations (size, color, material) with individual pricing and SKU
- **VariantOptions**: Variant type options (e.g., "Small", "Medium", "Large" for size)
- **Carts**: Shopping cart management for authenticated users and guests
- **Orders**: Completed order tracking with transaction history
- **Transactions**: Payment transaction lifecycle tracking
- **Addresses**: Customer shipping/billing address management

### Core Features

**Product Management:**
- Rich product catalog with images, descriptions, pricing
- Variant support (size, color, material, etc.)
- Multi-currency pricing (USD default, extensible)
- Inventory tracking per variant
- Product categories and relationships
- SEO optimization with meta fields

**Shopping Experience:**
- Persistent carts for logged-in users
- Guest cart support with email recovery
- Real-time inventory checks
- Product search and filtering
- Related products recommendations
- Live preview for product edits

**Checkout & Payments:**
- Stripe payment integration (test/live modes)
- Secure checkout flow with address management
- Guest checkout without account creation
- Order confirmation emails
- Tax and shipping calculation hooks
- Webhook handling for payment events

**Order Management:**
- Complete order history for customers
- Admin order management dashboard
- Guest order access via secure token
- Order status tracking
- Transaction lifecycle monitoring

**Customer Accounts:**
- User authentication with role-based access
- Order history viewing
- Saved address management
- Account settings and preferences

### Technology Stack

- **Runtime**: Node.js 18.20.2+ or 20.9.0+
- **Framework**: Next.js 16.2.2 (App Router with SSR/SSG)
- **Database**: MongoDB via `@payloadcms/db-mongodb`
- **Payments**: Stripe via `@payloadcms/plugin-ecommerce/payments/stripe`
- **Editor**: Lexical rich text editor
- **Styling**: Tailwind CSS 4.1+ with Radix UI components
- **Package Manager**: pnpm 9+ or 10+

## Quick Start

### Prerequisites

- Node.js 18.20.2+ or 20.9.0+ installed
- MongoDB running locally or MongoDB Atlas account
- Stripe account (test mode for development)
- pnpm package manager (recommended)

### Local Development Setup

1. **Clone and install dependencies:**
   ```bash
   cd your-project
   pnpm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```env
   # Database
   DATABASE_URL=mongodb://127.0.0.1/payload-ecommerce
   
   # Payload
   PAYLOAD_SECRET=your-secret-key-minimum-32-chars
   
   # Stripe (Test Mode)
   STRIPE_SECRET_KEY sk_test_your-stripe-secret-key
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
   STRIPE_WEBHOOKS_SIGNING_SECRET=whsec_your-webhook-secret
   
   # Payload Public URL (required for previews)
   PAYLOAD_PUBLIC_URL=http://localhost:3000
   ```

3. **Set up Stripe webhooks (for development):**
   ```bash
   # In a separate terminal
   pnpm stripe-webhooks
   ```
   
   This will forward webhooks from Stripe to your local server and display the signing secret.

4. **Start MongoDB (if not running):**
   ```bash
   docker run -d -p 27017:27017 --name mongo mongo:latest
   ```

5. **Start development server:**
   ```bash
   pnpm dev
   ```

6. **Open browser:**
   - Storefront: http://localhost:3000
   - Admin Panel: http://localhost:3000/admin

7. **Create first admin user:**
   - Navigate to /admin/login
   - Click "Create Account"
   - Use role: `admin` for full access

8. **Seed demo data (optional):**
   - Visit: http://localhost:3000/next/seed
   - Creates sample products, categories, and pages

See [Setup and Configuration](references/01-setup-configuration.md) for detailed setup instructions and Stripe configuration.

## Project Structure

```
src/
├── app/                          # Next.js App Router
│   ├── (payload)/                # Admin panel routes
│   └── (frontend)/               # Public storefront
│       ├── shop/                 # Product listing pages
│       ├── product/[slug]/       # Individual product pages
│       ├── cart/                 # Shopping cart page
│       ├── checkout/             # Checkout flow
│       ├── account/              # User account dashboard
│       └── find-order/           # Guest order lookup
├── collections/                   # Collection configurations
│   ├── Products/                 # Product catalog with variants
│   ├── Pages/                    # CMS pages with layout builder
│   ├── Users/                    # Customer accounts with roles
│   ├── Categories/               # Product taxonomy
│   └── Media/                    # Image uploads
├── globals/                       # Global configurations
│   ├── Header/                   # Navigation configuration
│   └── Footer/                   # Footer links
├── components/                    # React components
│   ├── product/                  # Product cards, galleries, variants
│   ├── cart/                     # Cart items, summary
│   ├── checkout/                 # Checkout forms, payment
│   ├── account/                  # User dashboard components
│   ├── forms/                    # Login, registration, addresses
│   └── layout/                   # Header, footer, search
├── blocks/                        # Layout builder blocks
│   ├── CallToAction/             # CTA sections
│   ├── Content/                  # Text and media columns
│   └── MediaBlock/               # Full-width media
├── hooks/                         # Collection hooks
├── access/                        # Access control functions
├── lib/                           # Utility libraries
│   └── stripe/                   # Stripe integration helpers
├── plugins/                       # Payload plugin configuration
├── providers/                     # React context providers
│   ├── Auth/                     # Authentication state
│   ├── Cart/                     # Shopping cart state
│   └── Theme/                    # Dark/light theme
└── utilities/                     # Helper functions
```

See [Project Structure](references/02-project-structure.md) for detailed explanation of each directory and file purpose.

## Core Ecommerce Features

### Products and Variants

**Simple Products:** Single SKU, no variants (e.g., a book)

**Variable Products:** Multiple variants with different attributes:
- **Variant Types**: Size, Color, Material
- **Variant Options**: Small/Medium/Large, Red/Blue/Green
- **Variant Combinations**: Each unique combination can have:
  - Individual pricing
  - Separate SKU
  - Independent inventory
  - Specific images

See [Products and Variants](references/03-products-variants.md) for complete configuration.

### Shopping Cart

**Features:**
- Persistent carts for logged-in users
- Guest carts stored by session
- Real-time inventory validation
- Automatic tax calculations (configurable)
- Shipping cost hooks
- Cart recovery via email

**Cart Flow:**
1. Add products to cart (with variant selection)
2. Review cart items and quantities
3. Proceed to checkout
4. Enter shipping/billing info
5. Complete payment

See [Shopping Cart](references/04-shopping-cart.md) for cart management patterns.

### Checkout and Payments

**Stripe Integration:**
- Test mode with test cards (4242 4242 4242 4242)
- Live mode for production
- Webhook handling for payment events
- Secure token-based card processing
- Support for all Stripe payment methods

**Checkout Flow:**
1. **Shipping Information**: Address entry or selection
2. **Payment Method**: Stripe Elements integration
3. **Order Review**: Final cart summary
4. **Payment Processing**: Secure Stripe checkout
5. **Order Confirmation**: Email with order details

See [Payments and Checkout](references/05-payments-checkout.md) for Stripe setup and webhook configuration.

### Orders and Transactions

**Order Lifecycle:**
1. Cart converted to pending order
2. Payment initiated (Transaction created)
3. Payment confirmed via webhook
4. Order marked as completed
5. Confirmation email sent

**Order Access:**
- **Admins**: Full access to all orders
- **Customers**: Access to their own orders via account dashboard
- **Guests**: Secure access via email + accessToken (sent in confirmation email)

See [Orders and Transactions](references/06-orders-transactions.md) for order management.

### Customer Accounts

**User Roles:**
- **Admin**: Full admin panel access, can manage all content
- **Customer**: Frontend access only, can view own orders/addresses

**Account Features:**
- Order history with status tracking
- Saved shipping/billing addresses
- Account settings and preferences
- Password management

See [Customer Accounts](references/07-customer-accounts.md) for user management.

## Common Operations

### Add a New Product

1. Navigate to Admin Panel → Products → Create New Product
2. Enter product details:
   - Title, description, gallery images
   - Base price in USD
   - Categories
3. Enable variants if needed:
   - Select variant types (Size, Color)
   - Define options for each type
   - Set prices and inventory per variant
4. Configure SEO metadata
5. Publish product

See [Products and Variants](references/03-products-variants.md) for detailed guide.

### Process a Payment

1. Customer adds items to cart
2. Proceeds to checkout
3. Enters shipping information
4. Enters payment details (Stripe Elements)
5. Submits order
6. Payment processed via Stripe
7. Webhook confirms payment
8. Order marked complete
9. Confirmation email sent

See [Payments and Checkout](references/05-payments-checkout.md) for payment flow details.

### View Guest Order

1. Guest receives order confirmation email
2. Clicks secure link in email (contains accessToken)
3. Redirected to order details page
4. Can view order status and items

Alternative: Visit `/find-order`, enter email + order ID, receive email with secure link.

See [Orders and Transactions](references/06-orders-transactions.md) for guest access patterns.

### Manage Inventory

**Simple Products:**
- Set inventory quantity on product
- Automatically decrements on order

**Variable Products:**
- Set inventory per variant combination
- Each variant tracked independently
- Low stock warnings configurable

See [Products and Variants](references/03-products-variants.md#inventory-management) for inventory patterns.

## Testing

### Run Integration Tests

```bash
pnpm test:int
```

Tests API endpoints, access control, payment flows using Vitest.

### Run E2E Tests

```bash
pnpm test:e2e
```

Tests complete checkout flow, cart operations, user accounts using Playwright.

### Stripe Test Mode

Use Stripe test cards:
- **Success**: 4242 4242 4242 4242 (any future expiry, any CVC)
- **Decline**: 4000 0000 0000 0002
- **3D Secure**: 4000 0025 0000 3155

See [Testing](references/08-testing.md) for test patterns.

## Production Deployment

### Build for Production

```bash
# Generate types
pnpm generate:types

# Build Next.js application
pnpm build

# Start production server
pnpm start
```

### Stripe Live Mode

1. Replace test keys with live keys in `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_live_...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```

2. Create live webhooks in Stripe Dashboard
3. Update `STRIPE_WEBHOOKS_SIGNING_SECRET` with live secret
4. Test with real payment (small amount)

See [Production Deployment](references/09-production-deployment.md) for deployment guides.

## Troubleshooting

**Webhooks not working**: Verify webhook endpoint is accessible from internet, check Stripe Dashboard for failed deliveries.

**Payment fails silently**: Check browser console for Stripe errors, verify publishable key is correct.

**Cart not persisting**: Ensure user is authenticated, check cart collection access control.

**Variants not showing**: Verify variant types and options are properly linked.

See [Troubleshooting Guide](references/10-troubleshooting.md) for comprehensive solutions.

## Reference Files

This skill includes detailed reference documentation organized by topic:

### Core Setup

- [`references/01-setup-configuration.md`](references/01-setup-configuration.md) - Environment variables, Stripe setup, dependencies, plugins
- [`references/02-project-structure.md`](references/02-project-structure.md) - Directory organization, file purposes, TypeScript paths

### Ecommerce Features

- [`references/03-products-variants.md`](references/03-products-variants.md) - Product configuration, variants, inventory, pricing
- [`references/04-shopping-cart.md`](references/04-shopping-cart.md) - Cart management, guest carts, persistence
- [`references/05-payments-checkout.md`](references/05-payments-checkout.md) - Stripe integration, webhooks, checkout flow
- [`references/06-orders-transactions.md`](references/06-orders-transactions.md) - Order lifecycle, guest access, transaction tracking
- [`references/07-customer-accounts.md`](references/07-customer-accounts.md) - User roles, account features, address management

### Operations and Deployment

- [`references/08-testing.md`](references/08-testing.md) - Integration tests, E2E tests, Stripe test mode
- [`references/09-production-deployment.md`](references/09-production-deployment.md) - Build process, Stripe live mode, monitoring
- [`references/10-troubleshooting.md`](references/10-troubleshooting.md) - Common errors, debugging techniques, payment issues

## Important Notes

1. **Beta Status**: Template is in BETA; review all code before production use
2. **Stripe Keys**: Never commit Stripe keys to version control
3. **Webhook Security**: Always verify webhook signatures using signing secret
4. **Test Mode**: Use Stripe test mode for all development/testing
5. **Inventory**: Manually managed; integrate with external systems as needed
6. **Tax/Shipping**: Basic hooks provided; implement based on your requirements
7. **Email**: Configure email service for order confirmations and password resets
8. **Access Control**: Guest order access requires both email AND accessToken

## Resources

- **Payload Docs**: https://payloadcms.com/docs
- **Ecommerce Plugin**: https://payloadcms.com/docs/ecommerce/plugin
- **Stripe Documentation**: https://stripe.com/docs
- **Website Template**: See `payloadcms-website-3-82-1` skill for shared features

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/payloadcms-ecommerce-3-82-1/`). All paths in this skill are relative to this directory.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
