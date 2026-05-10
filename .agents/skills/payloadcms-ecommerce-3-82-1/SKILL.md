---
name: payloadcms-ecommerce-3-82-1
description: Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products, variants, carts, orders, Stripe payments, multi-currency support, user accounts, guest checkout, and transaction tracking. Use when building e-commerce platforms, online stores, marketplaces, or any digital commerce project requiring product catalogs, shopping carts, order management, payment processing, customer accounts, and inventory management following official Payload best practices.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - payloadcms
  - ecommerce
  - commerce
  - stripe
  - payments
  - nextjs
  - headless-cms
category: cms-template
external_references:
  - https://payloadcms.com/docs/ecommerce/plugin
  - https://github.com/payloadcms/payload/tree/v3.82.1/templates/ecommerce
---

# Payload CMS Ecommerce Template v3.82.1

## Overview

The official Payload Ecommerce Template is a production-ready, full-stack ecommerce solution built on Payload CMS v3 with Next.js App Router. It provides a complete online store with a working backend, enterprise-grade admin panel, and a beautifully designed frontend — all in a single deployable application.

The template uses the `@payloadcms/plugin-ecommerce` package to provide collections for products, variants, carts, orders, transactions, and addresses. Stripe is the default payment adapter. The frontend is built with Next.js 16, Tailwind CSS 4, shadcn/ui components, and React Hook Form.

## When to Use

- Building a new ecommerce platform or online store from scratch
- Creating marketplaces with product catalogs and shopping carts
- Implementing payment processing with Stripe in a Payload project
- Setting up guest checkout flows with secure order access
- Building stores that need multi-currency support
- Adding ecommerce functionality to an existing Payload CMS site
- Prototyping commerce features rapidly with a production-ready foundation

## Quick Start

Create the project using the Payload CLI:

```bash
pnpx create-payload-app my-project -t ecommerce
```

Then set up locally:

```bash
cd my-project
cp .env.example .env
pnpm install && pnpm dev
```

Open `http://localhost:3000` and follow on-screen instructions to create the first admin user.

### Required Environment Variables

- `PAYLOAD_SECRET` — Application secret for signing JWTs
- `DATABASE_URL` — MongoDB connection string (default adapter)
- `STRIPE_SECRET_KEY` — Stripe secret API key
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` — Stripe publishable key
- `STRIPE_WEBHOOKS_SIGNING_SECRET` — Stripe webhook signing secret
- `PAYLOAD_PUBLIC_SERVER_URL` — Server URL for Payload
- `NEXT_PUBLIC_SERVER_URL` — Server URL for the frontend
- `PREVIEW_SECRET` — Secret for draft preview authentication

## Core Architecture

The template follows a unified monorepo structure where Payload backend and Next.js frontend share a single instance:

```
src/
├── access/              # Access control functions
├── app/
│   ├── (app)/           # Frontend routes (Next.js App Router)
│   └── (payload)/       # Payload admin & API routes
├── blocks/              # Layout builder blocks
├── collections/         # Collection configurations
├── components/          # Custom React components
├── endpoints/           # Seed data endpoint
├── fields/              # Reusable field definitions
├── fonts/               # Custom fonts
├── globals/             # Global configurations (Header, Footer)
├── hooks/               # Lifecycle hooks
├── lib/                 # Utility libraries
├── plugins/             # Plugin configuration (ecommerce, SEO, forms)
├── providers/           # React context providers
└── utilities/           # Shared utility functions
```

## Collections Overview

The template defines these core collections:

- **Users** — Auth-enabled with `admin` and `customer` roles. Join fields link to orders, carts, and addresses.
- **Pages** — Layout-builder enabled with draft/publish workflow, live preview, and SEO.
- **Media** — Upload collection for images, videos, and assets with pre-configured sizes and focal point.
- **Categories** — Taxonomy for grouping products.

The ecommerce plugin adds:

- **Products** — Product catalog with pricing per currency, variants, gallery, and layout blocks.
- **Variants** — Variant definitions (when enabled) with independent pricing and inventory.
- **Variant Types** — Variant dimension types (e.g., Size, Color).
- **Variant Options** — Specific variant values (e.g., "Large", "Red").
- **Carts** — Shopping carts for authenticated and guest users.
- **Orders** — Completed purchase records with line items, addresses, and totals.
- **Transactions** — Payment tracking from initiation to completion.
- **Addresses** — Saved shipping and billing addresses for customers.

## Plugin Configuration

The ecommerce plugin is configured in `src/plugins/index.ts`:

```typescript
import { ecommercePlugin } from '@payloadcms/plugin-ecommerce'
import { stripeAdapter } from '@payloadcms/plugin-ecommerce/payments/stripe'

export const plugins: Plugin[] = [
  ecommercePlugin({
    access: {
      adminOnlyFieldAccess,
      adminOrPublishedStatus,
      customerOnlyFieldAccess,
      isAdmin,
      isDocumentOwner,
    },
    customers: {
      slug: 'users',
    },
    orders: {
      ordersCollectionOverride: ({ defaultCollection }) => ({
        ...defaultCollection,
        fields: [
          ...defaultCollection.fields,
          { name: 'accessToken', type: 'text', unique: true, index: true, /* ... */ },
        ],
      }),
    },
    payments: {
      paymentMethods: [
        stripeAdapter({
          secretKey: process.env.STRIPE_SECRET_KEY!,
          publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
          webhookSecret: process.env.STRIPE_WEBHOOKS_SIGNING_SECRET!,
        }),
      ],
    },
    products: {
      productsCollectionOverride: ProductsCollection,
    },
  }),
]
```

## Frontend Routes

The Next.js frontend provides these key routes:

- `/` — Homepage (layout builder page)
- `/[slug]` — Dynamic page routes
- `/shop` — Product catalog with search and filters
- `/products/[slug]` — Individual product pages
- `/checkout` — Checkout flow with cart review and payment
- `/checkout/confirm-order` — Post-payment confirmation
- `/login`, `/create-account`, `/logout` — Authentication
- `/find-order` — Guest order lookup
- `/account` — Customer account dashboard
- `/account/addresses` — Address management
- `/orders` — Order history
- `/orders/[id]` — Individual order details

## Advanced Topics

**Plugin Configuration Reference**: Full ecommerce plugin config options, collection overrides, access control patterns → [Plugin Configuration](reference/01-plugin-configuration.md)

**Products and Variants**: Product catalog structure, variant types/options, pricing per currency, inventory management, gallery, related products → [Products and Variants](reference/02-products-and-variants.md)

**Carts and Checkout**: Cart operations, guest carts, item matching, checkout flow, payment initiation, order confirmation → [Carts and Checkout](reference/03-carts-and-checkout.md)

**Orders and Transactions**: Order lifecycle, transaction tracking, Stripe webhooks, guest order access with accessToken → [Orders and Transactions](reference/04-orders-and-transactions.md)

**Access Control Patterns**: Role-based access (admin/customer), document ownership, published status filtering, field-level security → [Access Control](reference/05-access-control.md)

**Frontend Architecture**: Next.js App Router structure, React context for ecommerce state, Stripe Elements integration, layout builder blocks → [Frontend Architecture](reference/06-frontend-architecture.md)

**Deployment and Production**: Build process, Vercel deployment, PostgreSQL adapter, migrations, scheduled publishing, caching strategy → [Deployment and Production](reference/07-deployment-and-production.md)
