# Project Structure

Complete directory and file organization for the Payload CMS ecommerce template v3.82.1, explaining each component's purpose and relationships.

## Root Directory

```
ecommerce-template/
├── .cursor/                  # Cursor IDE configuration
├── src/                      # Application source code
├── tests/                    # Integration and E2E tests
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── next.config.ts            # Next.js configuration
├── package.json              # Dependencies and scripts
├── playwright.config.ts      # Playwright E2E test config
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.mjs       # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── vitest.config.mts         # Vitest integration test config
└── README.md                 # Project documentation
```

## Source Directory (src/)

### Main Application Structure

```
src/
├── app/                      # Next.js App Router
│   ├── (payload)/            # Admin panel routes (route group)
│   │   ├── admin/            # Payload admin UI
│   │   └── api/              # Payload REST/GraphQL API
│   └── (app)/                # Public storefront routes (route group)
│       ├── shop/             # Product listing pages
│       ├── products/[slug]/  # Individual product pages
│       ├── cart/             # Shopping cart page
│       ├── checkout/         # Checkout flow pages
│       ├── find-order/       # Guest order lookup
│       ├── login/            # User authentication
│       ├── create-account/   # Customer registration
│       ├── forgot-password/  # Password recovery
│       ├── logout/           # Logout page
│       ├── [slug]/           # CMS pages (Pages collection)
│       ├── next/             # Next.js specific routes
│       │   ├── seed/         # Database seeding endpoint
│       │   └── preview/      # Draft preview handling
│       └── (account)/        # User account dashboard (route group)
│           ├── account/      # Account settings
│           │   └── addresses # Address management
│           └── orders/       # Order history
│               └── [id]/     # Individual order details
├── collections/              # Payload collection configurations
│   ├── Categories.ts         # Product taxonomy
│   ├── Media.ts              # Image uploads
│   ├── Pages/                # CMS pages with layout builder
│   │   └── index.ts          # Page collection config
│   ├── Products/             # Product catalog
│   │   └── index.ts          # Product collection override
│   └── Users/                # Customer accounts
│       ├── hooks/            # User collection hooks
│       │   └── ensureFirstUserIsAdmin.ts
│       └── index.ts          # User collection config
├── globals/                  # Payload global configurations
│   ├── Footer.ts             # Footer navigation links
│   └── Header.ts             # Header navigation links
├── components/               # React components
│   ├── BeforeDashboard/      # Admin dashboard welcome block
│   ├── BeforeLogin/          # Login page branding
│   ├── forms/                # Form components
│   │   ├── AddressForm/      # Shipping/billing address form
│   │   ├── LoginForm/        # User login
│   │   ├── RegisterForm/     # Customer registration
│   │   └── ResetPasswordForm/ Password reset
│   ├── layout/               # Layout components
│   │   ├── Footer/           # Site footer
│   │   ├── Header/           # Site header with nav
│   │   └── SearchBar/        # Product search
│   ├── product/              # Product display components
│   │   ├── Gallery/          # Product image gallery
│   │   ├── ProductCard/      # Product listing card
│   │   ├── ProductVariants/  # Variant selector
│   │   └── RelatedProducts/  # Related products section
│   ├── cart/                 # Shopping cart components
│   │   ├── CartItem/         # Individual cart item
│   │   └── CartSummary/      # Cart totals and checkout
│   ├── checkout/             # Checkout flow components
│   │   ├── CheckoutForm/     # Main checkout form
│   │   ├── PaymentElement/   # Stripe payment element
│   │   └── OrderSummary/     # Order review
│   ├── account/              # User account components
│   │   ├── AccountPage/      # Account dashboard
│   │   ├── AddressCard/      # Saved address display
│   │   ├── OrderCard/        # Order history item
│   │   └── OrderDetails/     # Order detail view
│   └── blocks/               # Layout builder block renders
│       ├── CallToAction/     # CTA section
│       ├── Content/          # Text and media columns
│       └── MediaBlock/       # Full-width media
├── blocks/                   # Layout builder block configurations
│   ├── CallToAction/         # CTA block config
│   │   └── config.ts         # Field definitions
│   ├── Content/              # Content block config
│   │   └── config.ts         # Field definitions
│   └── MediaBlock/           # Media block config
│       └── config.ts         # Field definitions
├── heros/                    # Hero section components
│   ├── HighImpact/           # Full-width hero
│   ├── LowImpact/            # Subtle hero
│   ├── MediumImpact/         # Medium prominence hero
│   ├── RenderHero.tsx        # Hero type dispatcher
│   └── config.ts             # Hero field configuration
├── fields/                   # Reusable field configurations
│   ├── hero.ts               # Hero section field
│   ├── link.ts               # Link field (internal/external)
│   └── linkGroup.ts          # Multiple links field
├── access/                   # Access control functions
│   ├── adminOnly.ts          # Admin-only access
│   ├── adminOnlyFieldAccess.ts # Admin field access
│   ├── adminOrCustomerOwner.ts # Owner-based access
│   ├── adminOrPublishedStatus.ts # Draft/published filter
│   ├── adminOrSelf.ts        # User own data access
│   ├── customerOnlyFieldAccess.ts # Customer field access
│   ├── isAdmin.ts            # Admin role checker
│   ├── isDocumentOwner.ts    # Document ownership check
│   └── utilities.ts          # Role checking utilities
├── hooks/                    # Collection hooks
│   └── populatePublishedAt.ts # Auto-set published timestamp
├── lib/                      # Utility libraries
│   └── constants.ts          # Sorting options, filters
├── plugins/                  # Payload plugin configuration
│   └── index.ts              # Ecommerce, SEO, Form Builder plugins
├── providers/                # React context providers
│   ├── Auth/                 # Authentication state
│   │   └── index.tsx         # Auth context provider
│   ├── Cart/                 # Shopping cart state
│   │   └── index.tsx         # Cart context provider
│   ├── HeaderTheme/          # Header theme toggle
│   │   └── index.tsx         # Theme context
│   ├── Sonner/               # Toast notifications
│   │   └── Sonner.tsx        # Sonner toast provider
│   ├── Theme/                # Dark/light mode
│   │   ├── InitTheme/        # Theme initialization
│   │   ├── ThemeSelector/    # Theme switcher component
│   │   ├── index.tsx         # Theme provider
│   │   └── shared.ts         # Theme utilities
│   └── index.tsx             # Combined providers
├── utilities/                # Helper functions
│   ├── canUseDOM.ts          # DOM availability check
│   ├── capitaliseFirstLetter.ts # String capitalization
│   ├── cn.ts                 # Class name merger (clsx + tailwind-merge)
│   ├── createUrl.ts          # URL builder with query params
│   ├── deepMerge.ts          # Deep object merge
│   ├── ensureStartsWith.ts   # Prefix validation
│   ├── formatDateTime.ts     # Date/time formatting
│   ├── generateMeta.ts       # SEO meta generation
│   ├── generatePreviewPath.ts # Draft preview URL
│   ├── getDocument.ts        # Document fetcher
│   ├── getGlobals.ts         # Global fetcher (header/footer)
│   ├── getURL.ts             # Base URL utilities
│   ├── mergeOpenGraph.ts     # Open Graph meta merger
│   ├── toKebabCase.ts        # String to kebab-case
│   └── useClickableCard.ts   # Clickable card hook
├── endpoints/                # Custom API endpoints
│   └── seed/                 # Database seeding
│       ├── home.ts           # Home page data
│       ├── contact-page.ts   # Contact page data
│       ├── product-hat.ts    # Sample product (hat)
│       ├── product-tshirt.ts # Sample product (t-shirt)
│       ├── image-*.ts        # Sample images
│       └── index.ts          # Seed endpoint handler
├── payload-types.ts          # Auto-generated TypeScript types
└── payload.config.ts         # Main Payload configuration
```

## Route Groups and Pages

### Admin Routes: `(payload)`

**Purpose**: Payload admin panel and API endpoints, not visible to customers.

**Structure:**
```
src/app/(payload)/
├── admin/[[...segments]]/page.tsx     # Admin UI (catch-all routes)
└── api/
    ├── [...slug]/route.ts             # REST API
    ├── graphql/route.ts               # GraphQL API (POST)
    └── graphql-playground/route.ts    # GraphQL Playground (GET)
```

**Key Files:**
- `admin/[[...segments]]/page.tsx`: Renders Payload admin for all `/admin/*` paths
- `api/[...slug]/route.ts`: REST API handler for all collections
- `api/graphql/route.ts`: GraphQL endpoint for custom queries
- `api/graphql-playground/route.ts`: Interactive GraphQL testing interface

### Storefront Routes: `(app)`

**Purpose**: Public-facing ecommerce website, accessible to all visitors.

#### Shop Pages

```
src/app/(app)/shop/
├── page.tsx              # Product listing (home shop)
└── [slug]/page.tsx       # Category filter page
```

**Features:**
- Paginated product grid
- Category filtering
- Sort options (price, date, alphabetical)
- Search functionality
- Responsive layout

#### Product Pages

```
src/app/(app)/products/[slug]/page.tsx
```

**Features:**
- Product details display
- Image gallery with thumbnails
- Variant selection (size, color, etc.)
- Add to cart functionality
- Related products section
- SEO meta tags from product meta fields

#### Cart Pages

```
src/app/(app)/cart/
└── page.tsx              # Shopping cart view
```

**Features:**
- Cart items list with quantities
- Item total calculations
- Tax estimation (if configured)
- Shipping cost hooks
- Proceed to checkout button
- Continue shopping link

#### Checkout Flow

```
src/app/(app)/checkout/
├── page.tsx              # Main checkout form
└── confirm-order/
    └── page.tsx          # Order confirmation page
```

**Checkout Steps:**
1. **Shipping Information**: Address entry or selection from saved addresses
2. **Billing Information**: Same as shipping or separate address
3. **Payment Method**: Stripe Elements integration
4. **Order Review**: Final cart summary before submission
5. **Processing**: Payment processed via Stripe
6. **Confirmation**: Success page with order details

#### User Authentication

```
src/app/(app)/login/page.tsx              # Login form
src/app/(app)/create-account/page.tsx     # Registration form
src/app/(app)/forgot-password/page.tsx    # Password reset request
src/app/(app)/logout/LogoutPage/page.tsx  # Logout confirmation
```

**Features:**
- Email/password authentication via Payload
- Social login (if configured)
- Password reset via email
- Account creation with role assignment

#### Guest Order Access

```
src/app/(app)/find-order/page.tsx
```

**Purpose**: Allow guests to lookup orders without account.

**Flow:**
1. Enter email address and order ID
2. System verifies order exists for that email
3. Sends email with secure access link (contains accessToken)
4. Guest clicks link to view order details

**Security**: Prevents order enumeration attacks by requiring email verification.

#### User Account Dashboard

```
src/app/(app)/(account)/
├── account/
│   ├── page.tsx              # Account overview
│   └── addresses/
│       └── page.tsx          # Address management
└── orders/
    ├── page.tsx              # Order history list
    └── [id]/
        └── page.tsx          # Individual order details
```

**Features:**
- Protected routes (require authentication)
- Order history with status tracking
- Saved address management
- Account settings and preferences

#### CMS Pages

```
src/app/(app)/[slug]/page.tsx
```

**Purpose**: Render Pages collection content (About, Contact, etc.).

**Features:**
- Layout builder blocks rendering
- Hero section display
- SEO meta tags
- Draft preview support
- Live preview during editing

### Next.js System Routes

```
src/app/(app)/next/
├── seed/route.ts             # Database seeding endpoint
├── preview/route.ts          # Draft preview token validation
└── exit-preview/route.ts     # Exit draft preview mode
```

**Seed Endpoint:**
- Visit `/next/seed` to populate demo data
- Creates sample products, categories, pages
- **Warning**: Destructive - drops existing data

**Preview Routes:**
- Handle draft preview token validation
- Enable live preview from admin panel
- Exit preview mode when done

## Collection Configurations

### Users Collection (`src/collections/Users/`)

```
Users/
├── hooks/
│   └── ensureFirstUserIsAdmin.ts  # Auto-set admin role for first user
└── index.ts                        # Collection configuration
```

**Fields:**
- `name`: User display name
- `email`: Authentication email
- `password`: Hashed password (auto-managed)
- `roles`: Array of roles ('admin' or 'customer')
- `orders`: Join field to Orders collection
- `cart`: Join field to Carts collection
- `addresses`: Join field to Addresses collection

**Access Control:**
- `create`: Public (registration enabled)
- `read`: Admin or self
- `update`: Admin or self
- `delete`: Admin only
- `admin panel access`: Admin role only

### Products Collection (`src/collections/Products/`)

```
Products/
└── index.ts  # Product collection override (extends ecommerce plugin default)
```

**Fields:**
- `title`: Product name
- `slug`: URL-friendly identifier
- `description`: Rich text description (Lexical editor)
- `gallery`: Array of product images with optional variant associations
- `priceInUSD`: Base price in USD
- `enableVariants`: Toggle for variant support
- `variantTypes`: Selected variant types (Size, Color, etc.)
- `variants`: Variant combinations with pricing/inventory
- `inventory`: Base inventory quantity (for simple products)
- `categories`: Related product categories
- `relatedProducts`: Related product recommendations
- `layout`: Layout builder blocks for additional content
- `_status`: Draft/published status
- `meta`: SEO fields (title, description, image)

**Access Control:**
- `read`: Published products public, drafts admin-only
- `create/update/delete`: Admin only

### Pages Collection (`src/collections/Pages/`)

```
Pages/
└── index.ts  # Page collection configuration
```

**Fields:**
- `title`: Page title
- `slug`: URL path
- `hero`: Hero section type and content
- `layout`: Layout builder blocks (Content, Media, CTA, Archive)
- `_status`: Draft/published status
- `meta`: SEO fields

**Features:**
- Layout builder for flexible page design
- Draft preview with live updates
- Version history
- Scheduled publishing

### Categories Collection (`src/collections/Categories.ts`)

**Fields:**
- `name`: Category name
- `slug`: URL identifier
- `description`: Category description
- `parent`: Hierarchical category support (self-referential)

**Purpose**: Organize products into taxonomy for filtering and navigation.

### Media Collection (`src/collections/Media.ts`)

**Fields:**
- `alt`: Alternative text for accessibility
- `caption`: Image caption
- `focalPoint`: Image focal point for cropping
- `width`, `height`: Image dimensions
- `size`: File size
- `mimeType`: File type

**Features:**
- Image upload with automatic resizing
- Focal point selection
- Pre-defined image sizes
- MIME type validation

## Globals

### Header (`src/globals/Header.ts`)

**Purpose**: Site-wide navigation configuration.

**Fields:**
- `navItems`: Array of navigation links (label, URL, target)

**Usage**: Populates header component across all pages.

### Footer (`src/globals/Footer.ts`)

**Purpose**: Site-wide footer configuration.

**Fields:**
- `footerLinks`: Multiple link groups for footer columns

**Usage**: Populates footer component across all pages.

## Access Control Patterns

### Admin Only (`src/access/adminOnly.ts`)

```typescript
export const adminOnly: Access = ({ req: { user } }) => {
  if (user) return checkRole(['admin'], user)
  return false
}
```

**Usage**: Restrict access to admin users only.

### Admin or Published (`src/access/adminOrPublishedStatus.ts`)

```typescript
export const adminOrPublishedStatus: Access = ({ req: { user } }) => {
  if (user && checkRole(['admin'], user)) {
    return true
  }
  return { _status: { equals: 'published' } }
}
```

**Usage**: Allow admins to see drafts, public sees only published.

### Document Owner (`src/access/isDocumentOwner.ts`)

```typescript
export const isDocumentOwner: Access = ({ req }) => {
  if (req.user && checkRole(['admin'], req.user)) {
    return true
  }
  if (req.user?.id) {
    return { customer: { equals: req.user.id } }
  }
  return false
}
```

**Usage**: Allow admins full access, customers access own data only.

### Admin or Self (`src/access/adminOrSelf.ts`)

```typescript
export const adminOrSelf: Access = ({ req: { user } }) => {
  if (user) {
    if (checkRole(['admin'], user)) return true
    return { id: { equals: user.id } }
  }
  return false
}
```

**Usage**: Allow users to access/update their own records.

## Key Utility Functions

### URL Generation (`src/utilities/getURL.ts`)

```typescript
export const getServerSideURL = () => {
  return process.env.NEXT_PUBLIC_PAYLOAD_URL || `http://localhost:${process.env.PORT || 3000}`
}
```

**Purpose**: Get base URL for server-side rendering.

### Preview Path Generation (`src/utilities/generatePreviewPath.ts`)

```typescript
export const generatePreviewPath = ({ slug, collection, req }) => {
  const url = getServerSideURL()
  return `${url}/${collection === 'products' ? `products/${slug}` : slug}`
}
```

**Purpose**: Generate draft preview URLs for live preview.

### Document Fetching (`src/utilities/getDocument.ts`)

```typescript
export const getDocument = async <T>(args: {
  collection: string
  slug: string
  draft?: boolean
}): Promise<T> => {
  // Fetches document from Payload API with optional draft access
}
```

**Purpose**: Type-safe document fetching with draft support.

### Class Name Merger (`src/utilities/cn.ts`)

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs))
}
```

**Purpose**: Merge Tailwind classes with conditional logic.

## Testing Structure

### Integration Tests (`tests/int/`)

```
tests/int/
└── api.int.spec.ts    # API endpoint tests using Vitest
```

**Tests:**
- Collection CRUD operations
- Access control enforcement
- Payment webhook handling

### E2E Tests (`tests/e2e/`)

```
tests/e2e/
├── admin.e2e.spec.ts      # Admin panel workflow tests
└── frontend.e2e.spec.ts   # Storefront user flow tests
```

**Tests:**
- Product browsing and filtering
- Add to cart flow
- Checkout with Stripe test mode
- User authentication
- Order management

### Test Helpers (`tests/helpers/`)

```
tests/helpers/
├── config.ts              # Test configuration
├── initPayload.ts         # Payload test initialization
└── seed-test-data.ts      # Test data seeding
```

## Configuration Files

### TypeScript (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "strict": true,
    "paths": {
      "@/*": ["./src/*"],
      "@payload-config": ["./src/payload.config.ts"]
    }
  }
}
```

### Next.js (`next.config.ts`)

- `withPayload()`: Integrates Payload with Next.js
- Image domains: Configure allowed remote image domains
- Webpack aliases: TypeScript extension resolution

### Tailwind (`tailwind.config.mjs`)

- Content paths: All source files for class detection
- Theme extensions: Custom colors, fonts, spacing
- Plugins: Typography plugin for prose styling

### Playwright (`playwright.config.ts`)

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
  },
})
```

### Vitest (`vitest.config.mts`)

```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./vitest.setup.ts'],
  },
})
```

## Summary

This template follows a clear separation of concerns:

1. **Admin Panel**: `(payload)` route group for content management
2. **Storefront**: `(app)` route group for customer-facing pages
3. **Collections**: Payload schemas for data modeling
4. **Components**: Reusable React components organized by feature
5. **Access Control**: Centralized permission logic
6. **Utilities**: Shared helper functions
7. **Plugins**: Ecommerce, SEO, Form Builder integration

Understanding this structure helps navigate the codebase and extend functionality effectively.
