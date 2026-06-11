# Plugin Configuration

## EcommercePluginConfig

The `@payloadcms/plugin-ecommerce` accepts a configuration object that controls all ecommerce functionality. Every field except `access` and `customers` is optional.

### Required Fields

```typescript
ecommercePlugin({
  access: {
    adminOnlyFieldAccess: ({ req }) => checkRole(['admin'], req.user),
    adminOrPublishedStatus: ({ req }) => {
      if (checkRole(['admin'], req.user)) return true
      return { _status: { equals: 'published' } }
    },
    isAdmin: ({ req }) => req.user ? checkRole(['admin'], req.user) : false,
    isDocumentOwner: ({ req }) => {
      if (req.user && checkRole(['admin'], req.user)) return true
      if (req.user?.id) return { customer: { equals: req.user.id } }
      return false
    },
  },
  customers: {
    slug: 'users', // slug of the auth-enabled collection
  },
})
```

### Optional Feature Toggles

- `products` — Enable products. Defaults to `true`. Can be `boolean` or `ProductsConfig`.
- `orders` — Enable orders. Defaults to `true`. Can be `boolean` or `OrdersConfig`.
- `carts` — Enable shopping carts. Defaults to `true`. Can be `boolean` or `CartsConfig`.
- `addresses` — Enable address management. Defaults to `true`. Can be `boolean` or `AddressesConfig`.
- `transactions` — Enable transaction tracking. Defaults to `true` when payment methods are provided.
- `inventory` — Enable inventory tracking on products/variants. Defaults to `true`.

### Products Configuration

```typescript
products: {
  productsCollectionOverride: ({ defaultCollection }) => ({
    ...defaultCollection,
    fields: [
      ...defaultCollection.fields,
      { name: 'customField', type: 'text' },
    ],
  }),
  variants: true, // or VariantsConfig for fine control
  validation: async ({ product, variant, quantity, currency }) => {
    // Custom pre-transaction validation
    if (quantity > 10) throw new Error('Maximum order quantity is 10')
  },
}
```

When `variants` is enabled, the plugin creates three additional collections:

- `variants` — Specific variant records with pricing and inventory
- `variantTypes` — Dimension types (Size, Color, Material)
- `variantOptions` — Individual option values (Large, Red, Cotton)

Override each independently:

```typescript
variants: {
  variantsCollectionOverride: ({ defaultCollection }) => ({ ... }),
  variantTypesCollectionOverride: ({ defaultCollection }) => ({ ... }),
  variantOptionsCollectionOverride: ({ defaultCollection }) => ({ ... }),
}
```

### Carts Configuration

```typescript
carts: {
  allowGuestCarts: true, // default — let unauthenticated users create carts
  cartItemMatcher: ({ existingItem, newItem }) => {
    // Custom matching logic beyond product+variant ID
    return existingItem.product === newItem.product
      && existingItem.variant === newItem.variant
  },
  cartsCollectionOverride: ({ defaultCollection }) => ({ ... }),
}
```

### Orders Configuration

```typescript
orders: {
  ordersCollectionOverride: ({ defaultCollection }) => ({
    ...defaultCollection,
    fields: [
      ...defaultCollection.fields,
      { name: 'notes', type: 'textarea' },
    ],
  }),
}
```

### Addresses Configuration

```typescript
addresses: {
  supportedCountries: [
    { label: 'United States', value: 'US' },
    { label: 'Canada', value: 'CA' },
  ],
  addressFields: ({ defaultFields }) => [
    ...defaultFields,
    { name: 'company', type: 'text' },
  ],
  addressesCollectionOverride: ({ defaultCollection }) => ({ ... }),
}
```

### Currencies Configuration

```typescript
currencies: {
  defaultCurrency: 'USD',
  supportedCurrencies: [
    { code: 'USD', label: 'US Dollar', symbol: '$', decimals: 2 },
    { code: 'EUR', label: 'Euro', symbol: '€', decimals: 2 },
    { code: 'GBP', label: 'British Pound', symbol: '£', decimals: 2 },
  ],
}
```

The plugin exports preset currencies: `USD`, `EUR`, `GBP`.

### Payments Configuration

```typescript
payments: {
  paymentMethods: [
    stripeAdapter({
      secretKey: process.env.STRIPE_SECRET_KEY!,
      publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
      webhookSecret: process.env.STRIPE_WEBHOOKS_SIGNING_SECRET!,
    }),
  ],
  productsQuery: { depth: 0 },
  variantsQuery: { depth: 0 },
}
```

Each payment method registers endpoints under `/api/payments/{methodName}/`:

- `POST /api/payments/{name}/initiate` — Create payment intent
- `POST /api/payments/{name}/confirm-order` — Confirm payment and create order
- Additional endpoints from the adapter (e.g., Stripe webhooks)

### Custom Payment Adapter

Implement the `PaymentAdapter` interface:

```typescript
import type { PaymentAdapter } from '@payloadcms/plugin-ecommerce/types'

export const customAdapter: PaymentAdapter = {
  name: 'custom',
  label: 'Custom Payment',
  group: {
    name: 'custom',
    type: 'group',
    admin: { condition: (data) => data?.paymentMethod === 'custom' },
    fields: [/* payment-specific fields */],
  },
  initiatePayment: async ({ data, req, transactionsSlug }) => {
    // Create payment intent with your provider
    return { message: 'Payment initiated', /* additional data */ }
  },
  confirmOrder: async ({ data, ordersSlug, req, transactionsSlug }) => {
    // Confirm payment and create order
    return { message: 'Order confirmed', orderID: '...', transactionID: '...' }
  },
  endpoints: [/* optional additional endpoints */],
}
```

### Slug Map Override

Override default collection slugs when needed:

```typescript
slugMap: {
  products: 'catalog-items',
  carts: 'shopping-carts',
  orders: 'purchases',
}
```

### Inventory Configuration

```typescript
inventory: {
  fieldName: 'stock', // override default field name 'inventory'
}
```
