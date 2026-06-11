# Frontend Architecture

## Next.js App Router Structure

The frontend uses Next.js 16 App Router with route groups for logical separation:

```
src/app/
├── (app)/                    # Frontend routes (no URL segment)
│   ├── (account)/            # Authenticated account area
│   │   ├── account/          # Account dashboard
│   │   │   └── addresses/    # Address management
│   │   └── orders/           # Order history
│   │       └── [id]/         # Individual order view
│   ├── [slug]/               # Dynamic page routes (layout builder pages)
│   ├── checkout/             # Checkout flow
│   │   └── confirm-order/    # Post-payment confirmation
│   ├── create-account/       # User registration
│   ├── find-order/           # Guest order lookup
│   ├── forgot-password/      # Password recovery
│   ├── login/                # User login
│   ├── logout/               # User logout
│   ├── next/                 # Next.js internal routes
│   │   ├── exit-preview/     # Exit draft preview mode
│   │   ├── preview/          # Enter draft preview mode
│   │   └── seed/             # Database seeding
│   ├── products/
│   │   └── [slug]/           # Product detail pages
│   └── shop/                 # Product catalog / storefront
├── (payload)/                # Payload routes (no URL segment)
│   ├── admin/                # Admin panel
│   │   └── [[...segments]]/  # Catch-all admin routing
│   └── api/                  # API routes
│       ├── [...slug]/        # Payload REST/GraphQL API
│       ├── graphql/          # GraphQL endpoint
│       └── graphql-playground/ # GraphQL Playground
```

## Layout Builder Blocks

Pages use a blocks-based layout system. Available blocks:

- **Hero** — Full-width hero section (configured via `hero` field)
- **Content** — Rich text content with configurable column layouts
- **MediaBlock** — Image/video media display
- **CallToAction** — CTA banner with links
- **Archive** — Dynamic listing of related documents
- **Carousel** — Image/content carousel (Embla Carousel)
- **ThreeItemGrid** — Three-column feature grid
- **Banner** — Alert/information banner
- **Form** — Form builder integration

Each block has a config in `src/blocks/<BlockName>/config.ts` and a React component in `src/blocks/<BlockName>/`.

## Ecommerce Context

The `EcommerceProvider` wraps the app layout and provides commerce state:

```typescript
// src/app/(app)/layout.tsx
<EcommerceProvider
  customersSlug="users"
  cartsSlug="carts"
  addressesSlug="addresses"
  enableVariants={true}
  syncLocalStorage={true}
  currenciesConfig={{ defaultCurrency: 'USD', supportedCurrencies }}
  paymentMethods={paymentMethodClients}
>
  {children}
</EcommerceProvider>
```

Consume with `useEcommerce()` hook in any component:

```typescript
const { cart, addItem, removeItem, currency, setCurrency, user } = useEcommerce()
```

## Stripe Integration

Stripe Elements are used for secure payment input:

```typescript
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

<Elements stripe={stripePromise} options={{ clientSecret }}>
  <CheckoutForm />
</Elements>
```

The checkout page handles:

1. Cart review and address selection
2. Stripe Elements card input
3. Payment submission via `initiatePayment`
4. Order confirmation via `confirmOrder`
5. Redirect to confirmation page

## Styling

The template uses:

- **Tailwind CSS 4** — Utility-first styling with CSS-based configuration
- **shadcn/ui** — Accessible component library built on Radix UI primitives
- **clsx + tailwind-merge** — Conditional class name merging
- **sonner** — Toast notifications
- **lucide-react** — Icon library
- **next-themes** — Dark/light mode toggle
- **Geist** — Font family

Components are defined in `components.json` for shadcn/ui codegen.

## Draft Preview

Draft preview uses Next.js preview mode:

```typescript
// src/app/(app)/next/preview/route.ts
export async function GET(request: Request) {
  const { slug, secret, collection } = new URL(request.url).searchParams

  if (secret !== process.env.PREVIEW_SECRET) {
    return Response.json({ error: 'Invalid token' }, { status: 401 })
  }

  res.setPreviewData({})
  return Redirect(`${origin}/${slug}`)
}
```

The admin panel generates preview URLs via the `preview` and `livePreview` config on collections.

## On-Demand Revalidation

When content is published, the frontend revalidates automatically:

```typescript
// Hook on pages collection
hooks: {
  afterChange: [revalidatePage],
  afterDelete: [revalidateDelete],
}
```

This calls Next.js `revalidateTag` or fetches the revalidation endpoint to update the static cache.

## Search

The shop page implements SSR search with Payload's query API:

```typescript
const { docs: products, totalDocs } = await payload.find({
  collection: 'products',
  where: {
    and: [
      { _status: { equals: 'published' } },
      // Optional category filter
      ...(category ? [{ categories: { contains: category } }] : []),
      // Optional text search
      ...(search ? [{ title: { like: search } }] : []),
    ],
  },
  sort: '-createdAt',
  depth: 1,
  limit: pageSize,
  page: currentPage,
})
```
