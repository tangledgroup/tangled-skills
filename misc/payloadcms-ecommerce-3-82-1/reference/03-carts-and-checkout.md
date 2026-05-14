# Carts and Checkout

## Cart Collection

The carts collection tracks shopping cart state for both authenticated users and guests.

### Default Cart Structure

```typescript
type Cart = {
  id: string
  customer?: Relationship to users    // null for guest carts
  currency?: string                   // ISO 4217 code
  items: CartItem[]
  subtotal?: number                   // Calculated total in cents
  secret?: string                     // For guest cart access
}

type CartItem = {
  id: string                          // Array item ID (always string)
  product: Relationship to products
  quantity: number
  variant?: Relationship to variants   // Optional, when variants enabled
}
```

### Guest Carts

When `allowGuestCarts: true` (default), unauthenticated users can create and manage carts. Guest carts are identified by a `secret` field stored in localStorage or cookies.

Access control for carts:

- Authenticated customers access their own cart via the `customer` relationship
- Guests access any unclaimed cart by ID + secret
- Admins have full access to all carts

### Cart Item Matching

When adding items to the cart, the system determines if an item already exists. The default matcher compares product and variant IDs:

```typescript
// Default — match by product and variant only
const defaultCartItemMatcher = ({ existingItem, newItem }) => {
  return existingItem.product === newItem.product
    && (!existingItem.variant || !newItem.variant
      || existingItem.variant === newItem.variant)
}
```

Customize matching logic via `carts.cartItemMatcher`:

```typescript
cartItemMatcher: ({ existingItem, newItem }) => {
  const productMatch = existingItem.product === newItem.product
  const variantMatch = !existingItem.variant || !newItem.variant
    || existingItem.variant === newItem.variant
  // Add custom criteria — e.g., delivery option
  const deliveryMatch = existingItem.deliveryOption === newItem.deliveryOption
  return productMatch && variantMatch && deliveryMatch
}
```

When items match, quantities are combined instead of creating separate entries.

## Cart Operations (Client-Side)

The ecommerce context provides these cart operations via React hooks:

### Adding Items

```typescript
const { addItem } = useEcommerce()
await addItem({ product: productId }, quantity)
// With variant
await addItem({ product: productId, variant: variantId }, quantity)
```

### Managing Quantities

```typescript
const { incrementItem, decrementItem, removeItem } = useEcommerce()

// Increment by 1 (uses cart item's array ID, always a string)
await incrementItem('abc123')

// Decrement by 1 (removes item if quantity reaches 0)
await decrementItem('abc123')

// Remove entirely
await removeItem('abc123')
```

### Clear and Refresh

```typescript
const { clearCart, refreshCart } = useEcommerce()
await clearCart()
await refreshCart()
```

### Merging Carts (Login Flow)

When a guest user logs in, their guest cart is merged with their authenticated cart:

```typescript
const { onLogin, mergeCart } = useEcommerce()

// Called automatically after login
await onLogin()

// Or manually merge
await mergeCart(targetCartID, sourceCartID, sourceSecret)
```

### Session Management

```typescript
const { clearSession, onLogout } = useEcommerce()
clearSession()   // Clears all ecommerce session data
onLogout()       // Alias for clearSession, semantic clarity
```

## Checkout Flow

The checkout process follows this sequence:

### 1. Cart Review (`/checkout`)

User reviews cart items, selects shipping/billing addresses, and chooses payment method. The cart must have valid items before proceeding.

### 2. Payment Initiation

```typescript
const { initiatePayment } = useEcommerce()
await initiatePayment('stripe', {
  additionalData: { /* payment-specific data */ },
})
```

This calls `POST /api/payments/stripe/initiate` which:

- Validates cart items and inventory
- Creates a Stripe PaymentIntent
- Creates a transaction record in the `transactions` collection
- Returns client secret for Stripe Elements

### 3. Payment Confirmation

After the user completes payment in Stripe Elements, confirm the order:

```typescript
const { confirmOrder } = useEcommerce()
await confirmOrder('stripe', {
  additionalData: { /* payment intent ID etc */ },
})
```

This calls `POST /api/payments/stripe/confirm-order` which:

- Verifies the payment with Stripe
- Creates an Order record from the cart
- Updates the transaction record
- Clears the cart
- Returns order and transaction IDs

### 4. Order Confirmation (`/checkout/confirm-order`)

Shows order confirmation with details and next steps. For guests, provides the order ID for later lookup.

## Ecommerce Context Provider

The `EcommerceProvider` wraps the frontend app and provides state via `useEcommerce()`:

```typescript
<EcommerceProvider
  customersSlug="users"
  cartsSlug="carts"
  addressesSlug="addresses"
  enableVariants={true}
  syncLocalStorage={true}
  currenciesConfig={{ defaultCurrency: 'USD', supportedCurrencies: [USD, EUR] }}
  paymentMethods={[stripeClientAdapter]}
  api={{ apiRoute: '/api' }}
  debug={false}
>
  <App />
</EcommerceProvider>
```

Key context values:

- `cart` — Current cart data
- `cartID` — Current cart identifier
- `currency` — Currently selected currency
- `addresses` — User's saved addresses
- `isLoading` — Whether a cart operation is in progress
- `user` — Current authenticated user
- `selectedPaymentMethod` — Chosen payment method name

## Currency Handling

```typescript
const { currency, setCurrency } = useEcommerce()

// Change cart currency
setCurrency('EUR')

// Format prices using current currency
const formatted = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: currency.code,
}).format(cart.subtotal / Math.pow(10, currency.decimals))
```

The plugin exports `EUR`, `GBP`, `USD` as ready-made currency objects.
