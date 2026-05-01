# Orders and Transactions

## Transaction Lifecycle

Transactions track the complete payment lifecycle from initiation to completion. Only admins can access transactions in the admin panel.

### Transaction States

1. **Initiated** — Payment intent created with Stripe, transaction record saved
2. **Completed** — Payment confirmed by Stripe webhook or confirm-order endpoint
3. **Failed** — Payment declined or expired

### Transaction Fields

```typescript
type Transaction = {
  id: string
  customer?: Relationship to users
  customerEmail?: string              // For guest transactions
  cart?: Relationship to carts
  order?: Relationship to orders      // Set after successful completion
  paymentMethod: string               // e.g., 'stripe'
  currency?: string
  subtotal?: number
  billingAddress?: Group (address fields)
  shippingAddress?: Group (address fields)
  items: Array of line items
  status: 'initiated' | 'completed' | 'failed'
  // Payment-method-specific group fields (e.g., stripePaymentIntentID)
}
```

### Stripe Integration

The Stripe adapter provides:

- `initiatePayment` — Creates a Stripe PaymentIntent and saves transaction
- `confirmOrder` — Verifies payment, creates order, updates transaction
- Webhook endpoint at `/api/payments/stripe/webhooks` for async events

Local development webhook forwarding:

```bash
pnpm stripe-webhooks
# Runs: stripe listen --forward-to localhost:3000/api/payments/stripe/webhooks
```

## Order Collection

Orders are created only after a transaction completes successfully. They serve as the customer-facing purchase record.

### Order Fields

```typescript
type Order = {
  id: string
  customer?: Relationship to users
  customerEmail?: string              // For guest orders
  items: Array of line items          // Product, variant, quantity, price
  currency?: string
  subtotal?: number
  billingAddress?: Group (address fields)
  shippingAddress?: Group (address fields)
  createdAt: Date
}
```

### Template Extension — accessToken

The template adds a unique `accessToken` field to orders for secure guest access:

```typescript
{
  name: 'accessToken',
  type: 'text',
  unique: true,
  index: true,
  admin: { position: 'sidebar', readOnly: true },
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
}
```

This UUID is generated automatically on order creation and never exposed in the frontend.

## Guest Order Access

Guest users who check out without accounts can securely view their orders:

### Find Order Flow (`/find-order`)

1. Guest enters email address and order ID
2. System verifies the order exists and matches the email
3. If verified, an email is sent containing a secure link with the `accessToken`
4. The link grants temporary access to view that specific order

This two-step verification prevents order enumeration attacks where attackers iterate through sequential order IDs.

### Security Model

- Order confirmation emails include the order ID
- The `accessToken` is only sent via the verification email
- Guest access requires both email match AND valid accessToken
- Orders collection access control enforces: admins see all, customers see their own, guests need accessToken + email match

## Order Access Control

```typescript
// Orders collection access
access: {
  read: ({ req }) => {
    // Admins see all orders
    if (req.user && checkRole(['admin'], req.user)) return true
    // Authenticated users see their own orders
    if (req.user?.id) return { customer: { equals: req.user.id } }
    // Guests need accessToken + email verification
    return false  // Handled via custom endpoint with token validation
  },
}
```

## User Account Integration

The Users collection includes join fields for easy access to related commerce data:

```typescript
{
  name: 'orders',
  type: 'join',
  collection: 'orders',
  on: 'customer',
  admin: { allowCreate: false, defaultColumns: ['id', 'createdAt', 'total', 'currency', 'items'] },
},
{
  name: 'cart',
  type: 'join',
  collection: 'carts',
  on: 'customer',
  admin: { allowCreate: false, defaultColumns: ['id', 'createdAt', 'total', 'currency', 'items'] },
},
{
  name: 'addresses',
  type: 'join',
  collection: 'addresses',
  on: 'customer',
  admin: { allowCreate: false, defaultColumns: ['id'] },
},
```

These join fields appear in the admin panel sidebar, providing quick navigation from a user to their orders, cart, and addresses.
