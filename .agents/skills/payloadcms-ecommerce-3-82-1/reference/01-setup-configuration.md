# Setup and Configuration

Complete guide to environment configuration, Stripe setup, dependencies, and development tools for the Payload CMS ecommerce template v3.82.1.

## Environment Variables

### Required Variables

Create a `.env` file in the project root (never commit to version control):

```env
# MongoDB Connection String
DATABASE_URL=mongodb://127.0.0.1/payload-ecommerce

# Payload Secret Key (minimum 32 characters)
PAYLOAD_SECRET=your-secret-key-minimum-32-chars

# Stripe Test Keys (for development)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOKS_SIGNING_SECRET=whsec_your-webhook-signing-secret

# Payload Public URL (required for live preview, email links)
PAYLOAD_PUBLIC_URL=http://localhost:3000

# Node Environment
NODE_ENV=development

# Server Port
PORT=3000
```

### Variable Details

**DATABASE_URL**
- **Purpose**: MongoDB connection string
- **Local**: `mongodb://127.0.0.1/payload-ecommerce`
- **Docker**: `mongodb://mongo/payload-ecommerce`
- **Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/ecommerce`

**PAYLOAD_SECRET**
- **Purpose**: Session encryption, JWT signing
- **Generate**: `node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"`
- **Security**: Never commit to version control

**STRIPE_SECRET_KEY**
- **Purpose**: Server-side Stripe API operations
- **Test Mode**: Starts with `sk_test_`
- **Live Mode**: Starts with `sk_live_`
- **Get From**: Stripe Dashboard > Developers > API Keys > Secret key
- **Permissions**: Can create charges, customers, webhooks

**NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY**
- **Purpose**: Client-side Stripe Elements integration
- **Test Mode**: Starts with `pk_test_`
- **Live Mode**: Starts with `pk_live_`
- **Get From**: Stripe Dashboard > Developers > API Keys > Publishable key
- **Security**: Safe to expose in frontend code (cannot process payments alone)

**STRIPE_WEBHOOKS_SIGNING_SECRET**
- **Purpose**: Verify webhook event authenticity
- **Format**: Starts with `whsec_`
- **Get From**: Stripe Dashboard > Developers > Webhooks > Create Endpoint
- **Critical**: Never share; used to signature verification

**PAYLOAD_PUBLIC_URL**
- **Purpose**: Base URL for previews, emails, redirects
- **Development**: `http://localhost:3000`
- **Production**: `https://your-domain.com`
- **Required For**: Live preview, draft preview, email links

### Stripe Account Setup

#### 1. Create Stripe Account

1. Visit https://stripe.com/sign_up
2. Complete business information
3. Verify email address
4. Access Dashboard at https://dashboard.stripe.com

#### 2. Get API Keys

1. Navigate to **Developers > API Keys**
2. Copy **Secret key** (sk_test_...) → `STRIPE_SECRET_KEY`
3. Copy **Publishable key** (pk_test_...) → `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
4. **Keep secret key private**; never commit to Git

#### 3. Set Up Webhooks

1. Navigate to **Developers > Webhooks**
2. Click **Add endpoint**
3. Enter URL:
   - **Local development**: Use ngrok (see below)
   - **Production**: `https://your-domain.com/api/payments/stripe/webhooks`
4. Select events to receive:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.succeeded`
   - `charge.failed`
5. Click **Add endpoint**
6. Copy **Webhook signing secret** (whsec_...) → `STRIPE_WEBHOOKS_SIGNING_SECRET`

#### 4. Local Webhook Testing

**Option A: Using Stripe CLI (Recommended)**

```bash
# Install Stripe CLI
# macOS: brew install stripe/stripe-cli/stripe
# Linux: curl -s https://packages.stripe.dev/api/security/keypair/public | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/stripe.gpg
# Then: sudo add-apt-repository "deb [signed-by=/etc/apt/trusted.gpg.d/stripe.gpg] https://packages.stripe.dev/api/debian stable main"

# Login to Stripe CLI
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:3000/api/payments/stripe/webhooks
```

Stripe CLI will display the signing secret. Use this for `STRIPE_WEBHOOKS_SIGNING_SECRET`.

**Option B: Using ngrok**

```bash
# Install ngrok
# macOS: brew install ngrok
# Linux: sudo snap install ngrok

# Start tunnel
ngrok http 3000

# Copy the forward URL (e.g., https://abc123.ngrok.io)
# Use this as webhook endpoint in Stripe Dashboard
```

### Development vs Production Keys

**Test Mode (Development):**
- Safe to use freely
- No real money charged
- Test cards available (4242 4242 4242 4242)
- Keys start with `sk_test_` / `pk_test_`

**Live Mode (Production):**
- Real money processed
- Requires Stripe account verification
- Keys start with `sk_live_` / `pk_live_`
- **Never use live keys in development**

**Switching Modes:**
1. Update environment variables with live keys
2. Create new webhook endpoint in Stripe Dashboard
3. Redeploy application
4. Test with small real transaction

## Package Manager Configuration

### pnpm (Recommended)

```bash
# Enable corepack
corepack enable

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

**package.json engines:**
```json
{
  "engines": {
    "node": "^18.20.2 || >=20.9.0"
  }
}
```

## Dependencies

### Ecommerce-Specific Dependencies

```json
{
  "@payloadcms/plugin-ecommerce": "workspace:*",
  "@stripe/react-stripe-js": "^3",
  "@stripe/stripe-js": "^4.0.0",
  "stripe": "18.5.0",
  "date-fns": "^4.1.0",
  "jsonwebtoken": "9.0.1",
  "qs-esm": "8.0.1",
  "sonner": "^1.7.2"
}
```

**Key Packages:**

- **@payloadcms/plugin-ecommerce**: Core ecommerce functionality (products, carts, orders)
- **@stripe/react-stripe-js**: React components for Stripe Elements
- **@stripe/stripe-js**: Stripe JavaScript API
- **stripe**: Server-side Stripe Node.js library
- **date-fns**: Date formatting for orders and transactions
- **jsonwebtoken**: Access token generation for guest order access
- **sonner**: Toast notifications for user feedback

### All Production Dependencies

See package.json for complete list including:
- Payload core packages (@payloadcms/next, @payloadcms/db-mongodb)
- UI components (@radix-ui/*, lucide-react)
- Styling (tailwindcss, class-variance-authority)
- Form handling (react-hook-form)

## npm Scripts

```json
{
  "scripts": {
    // Development
    "dev": "cross-env NODE_OPTIONS=--no-deprecation next dev",
    "dev:prod": "cross-env NODE_OPTIONS=--no-deprecation rm -rf .next && pnpm build && pnpm start",
    
    // Production
    "build": "cross-env NODE_OPTIONS=\"--no-deprecation --max-old-space-size=8000\" next build",
    "start": "cross-env NODE_OPTIONS=--no-deprecation next start",
    
    // Payload CLI
    "payload": "cross-env NODE_OPTIONS=--no-deprecation payload",
    "generate:types": "cross-env NODE_OPTIONS=--no-deprecation payload generate:types",
    "generate:importmap": "cross-env NODE_OPTIONS=--no-deprecation payload generate:importmap",
    
    // Stripe
    "stripe-webhooks": "stripe listen --forward-to localhost:3000/api/payments/stripe/webhooks",
    
    // Testing
    "test": "pnpm run test:int && pnpm run test:e2e",
    "test:int": "cross-env NODE_OPTIONS=--no-deprecation vitest run --config ./vitest.config.mts",
    "test:e2e": "cross-env NODE_OPTIONS=\"--no-deprecation --import=tsx/esm\" playwright test --config=playwright.config.ts"
  }
}
```

### Stripe Webhook Script

**Development:**
```bash
# Start webhook listener (in separate terminal)
pnpm stripe-webhooks

# Follow prompts to connect to Stripe account
# Copy the displayed signing secret to .env
```

This forwards Stripe webhooks to your local server for testing payment flows.

## Payload Configuration

### Main Config (src/payload.config.ts)

```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import { buildConfig } from 'payload'

export default buildConfig({
  admin: {
    components: {
      beforeLogin: ['@/components/BeforeLogin#BeforeLogin'],
      beforeDashboard: ['@/components/BeforeDashboard#BeforeDashboard'],
    },
    user: Users.slug,
  },
  collections: [Users, Pages, Categories, Media],
  // Products collection added by ecommerce plugin
  db: mongooseAdapter({ url: process.env.DATABASE_URL }),
  editor: lexicalEditor({
    features: () => [
      UnderlineFeature(),
      BoldFeature(),
      ItalicFeature(),
      LinkFeature({
        enabledCollections: ['pages'],
        fields: ({ defaultFields }) => {
          // Custom link fields for internal/external URLs
        },
      }),
      // More features...
    ],
  }),
  globals: [Header, Footer],
  plugins, // Ecommerce plugin configured here
  secret: process.env.PAYLOAD_SECRET,
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
})
```

### Ecommerce Plugin Configuration (src/plugins/index.ts)

```typescript
import { ecommercePlugin } from '@payloadcms/plugin-ecommerce'
import { stripeAdapter } from '@payloadcms/plugin-ecommerce/payments/stripe'

export const plugins: Plugin[] = [
  // SEO and Form Builder plugins...
  
  ecommercePlugin({
    access: {
      adminOnlyFieldAccess,
      adminOrPublishedStatus,
      customerOnlyFieldAccess,
      isAdmin,
      isDocumentOwner,
    },
    customers: {
      slug: 'users', // Use existing Users collection
    },
    orders: {
      ordersCollectionOverride: ({ defaultCollection }) => ({
        ...defaultCollection,
        fields: [
          ...defaultCollection.fields,
          {
            name: 'accessToken',
            type: 'text',
            unique: true,
            index: true,
            admin: {
              position: 'sidebar',
              readOnly: true,
            },
            hooks: {
              beforeValidate: [
                ({ value, operation }) => {
                  if (operation === 'create' || !value) {
                    return crypto.randomUUID()
                  }
                  return value
                },
              ],
            },
          },
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

**Configuration Details:**

**access**: Access control functions for ecommerce collections
- `adminOnlyFieldAccess`: Admin-only field access
- `adminOrPublishedStatus`: Published content public, drafts admin-only
- `customerOnlyFieldAccess`: Customers access own data
- `isDocumentOwner`: Owner-based access control

**customers.slug**: Maps to existing Users collection

**orders.ordersCollectionOverride**: Custom order fields
- Adds `accessToken` for guest order access
- Auto-generated UUID on order creation
- Indexed for fast lookups

**payments.paymentMethods**: Payment processor adapters
- Stripe adapter with API keys from environment
- Can add multiple payment methods (PayPal, etc.)

**products.productsCollectionOverride**: Custom product configuration
- Extends default product fields
- Adds custom layout blocks, SEO fields

See [Products and Variants](03-products-variants.md) for product configuration details.

## Next.js Configuration

### next.config.ts

```typescript
import { withPayload } from '@payloadcms/next/withPayload'

const nextConfig = {
  images: {
    remotePatterns: [
      {
        hostname: 'images.unsplash.com',
        protocol: 'https',
      },
      // Add product image domains here
    ],
  },
  webpack: (webpackConfig) => {
    webpackConfig.resolve.extensionAlias = {
      '.cjs': ['.cts', '.cjs'],
      '.js': ['.ts', '.tsx', '.js', '.jsx'],
      '.mjs': ['.mts', '.mjs'],
    }
    return webpackConfig
  },
}

export default withPayload(nextConfig)
```

## TypeScript Configuration

### tsconfig.json

Path aliases for imports:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@payload-config": ["./src/payload.config.ts"]
    }
  }
}
```

## Docker Development (Optional)

### docker-compose.yml

```yaml
version: '3'

services:
  payload:
    build: .
    ports:
      - '3000:3000'
    volumes:
      - .:/home/node/app
      - node_modules:/home/node/app/node_modules
    working_dir: /home/node/app
    command: pnpm dev
    depends_on:
      - mongo
    env_file:
      - .env

  mongo:
    image: mongo:latest
    ports:
      - '27017:27017'
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
  node_modules:
```

**Start Docker development:**
```bash
docker-compose up --build
```

Update `.env` to use `DATABASE_URL=mongodb://mongo/payload-ecommerce`.

## Seed Demo Data

The template includes a seed endpoint for populating demo products and content:

**Visit**: http://localhost:3000/next/seed

**Creates:**
- Sample products with variants
- Product categories
- Demo pages
- Header/footer navigation

**Usage:**
- Development: Use to test storefront features
- Production: Optional, can create custom products from scratch

## Common Setup Issues

### Stripe Webhook Not Received

**Symptoms**: Payment succeeds but order not created

**Solutions:**
1. Verify webhook endpoint is accessible (use ngrok for local)
2. Check Stripe Dashboard > Webhooks for failed deliveries
3. Confirm `STRIPE_WEBHOOKS_SIGNING_SECRET` matches webhook endpoint
4. Ensure endpoint path is `/api/payments/stripe/webhooks`

### Payment Fails Silently

**Symptoms**: No error message, payment doesn't process

**Solutions:**
1. Check browser console for Stripe errors
2. Verify `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is correct
3. Ensure using test keys in development
4. Check network tab for failed API calls

### Cart Not Persisting

**Symptoms**: Cart empties on page refresh

**Solutions:**
1. Ensure user is authenticated (guest carts use session)
2. Check cart collection access control
3. Verify cart provider is wrapped around app
4. Check browser localStorage is enabled

See [Troubleshooting Guide](10-troubleshooting.md) for more solutions.
