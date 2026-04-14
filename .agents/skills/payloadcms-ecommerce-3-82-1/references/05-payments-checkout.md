# Payments and Checkout

Complete guide to Stripe payment integration, checkout flow implementation, webhook handling, and payment security in the Payload CMS ecommerce template v3.82.1.

## Stripe Integration Overview

### Payment Flow Architecture

```
Customer → Frontend (Stripe Elements) → Stripe API → Webhook → Backend → Order Creation
     ↓                                  ↓
  Card Token                      Payment Intent
     ↓                                  ↓
  Secure Tokenization           Payment Confirmation
```

**Key Components:**
1. **Stripe Elements**: Secure card input components (frontend)
2. **Payment Intents**: Server-side payment authorization
3. **Webhooks**: Asynchronous payment confirmation
4. **Orders**: Created after successful payment

### Stripe Adapter Configuration

The template uses `@payloadcms/plugin-ecommerce/payments/stripe` adapter.

**Configuration (src/plugins/index.ts):**
```typescript
import { stripeAdapter } from '@payloadcms/plugin-ecommerce/payments/stripe'

ecommercePlugin({
  payments: {
    paymentMethods: [
      stripeAdapter({
        secretKey: process.env.STRIPE_SECRET_KEY!,
        publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
        webhookSecret: process.env.STRIPE_WEBHOOKS_SIGNING_SECRET!,
      }),
    ],
  },
})
```

**Required Environment Variables:**
- `STRIPE_SECRET_KEY`: Server-side API key (sk_test_... or sk_live_...)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Client-side key (pk_test_... or pk_live_...)
- `STRIPE_WEBHOOKS_SIGNING_SECRET`: Webhook signature verification (whsec_...)

## Checkout Flow Implementation

### Step 1: Shipping Information

Collect customer shipping address before payment.

**Checkout Form Component:**
```typescript
// src/components/checkout/CheckoutForm.tsx
const CheckoutForm = ({ cart, user }) => {
  const [shippingAddress, setShippingAddress] = useState({
    line1: '',
    line2: '',
    city: '',
    state: '',
    zip: '',
    country: 'US'
  })
  
  const [billingAddress, setBillingAddress] = useState(shippingAddress)
  const [useSameForBilling, setUserSameForBilling] = useState(true)
  
  return (
    <div className="checkout-form">
      {/* Shipping Address */}
      <section className="address-section">
        <h2>Shipping Address</h2>
        
        {user?.addresses?.length > 0 && (
          <div className="saved-addresses">
            <p>Use a saved address:</p>
            {user.addresses.map(address => (
              <button 
                key={address.id}
                onClick={() => setShippingAddress(address)}
              >
                {address.line1}, {address.city}, {address.zip}
              </button>
            ))}
          </div>
        )}
        
        <AddressForm 
          value={shippingAddress}
          onChange={setShippingAddress}
        />
      </section>
      
      {/* Billing Address */}
      <section className="billing-section">
        <label>
          <input
            type="checkbox"
            checked={useSameForBilling}
            onChange={(e) => setUserSameForBilling(e.target.checked)}
          />
          Same as shipping address
        </label>
        
        {!useSameForBilling && (
          <AddressForm 
            value={billingAddress}
            onChange={setBillingAddress}
          />
        )}
      </section>
      
      {/* Payment Method */}
      <PaymentSection cartTotal={cart.total} />
      
      {/* Order Summary */}
      <OrderSummary items={cart.items} total={cart.total} />
      
      <button 
        onClick={() => handleSubmit(shippingAddress, billingAddress)}
        disabled={!isFormValid}
      >
        Place Order
      </button>
    </div>
  )
}
```

### Step 2: Payment Method Integration

**Stripe Elements Setup:**
```typescript
// src/components/checkout/PaymentElement.tsx
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

const PaymentSection = ({ cartTotal }) => {
  const [clientSecret, setClientSecret] = useState('')
  
  // Create payment intent on mount
  useEffect(() => {
    const createPaymentIntent = async () => {
      const response = await fetch('/api/payments/create-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: cartTotal * 100,  // Convert to cents
          currency: 'usd'
        })
      })
      
      const data = await response.json()
      setClientSecret(data.clientSecret)
    }
    
    createPaymentIntent()
  }, [cartTotal])
  
  if (!clientSecret) return <div>Loading payment...</div>
  
  const options = {
    clientSecret,
    appearance: {
      theme: 'stripe',
      variables: {
        colorPrimary: '#000000',
        fontFamily: 'Inter, sans-serif',
      }
    }
  }
  
  return (
    <Elements options={options} stripe={stripePromise}>
      <StripeForm />
    </Elements>
  )
}

const StripeForm = () => {
  const stripe = useStripe()
  const elements = useElements()
  const [error, setError] = useState(null)
  
  const handleSubmit = async (event) => {
    event.preventDefault()
    
    if (!stripe || !elements) return
    
    const { error: submitError } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: elements.getElement(CardElement)!,
        billing_details: {
          name: customerName,
          email: customerEmail,
          address: {
            line1: billingAddress.line1,
            city: billingAddress.city,
            state: billingAddress.state,
            postal_code: billingAddress.zip,
            country: billingAddress.country
          }
        }
      }
    })
    
    if (submitError) {
      setError(submitError.message)
    } else {
      // Payment successful - handled by webhook
      // Show success message to user
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <CardElement options={{ style: baseStyle }} />
      
      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={!stripe?.ready}>
        Pay ${cartTotal.toFixed(2)}
      </button>
    </form>
  )
}
```

### Step 3: Create Payment Intent

**Backend API Endpoint:**
```typescript
// src/app/(app)/api/payments/create-intent/route.ts
import { stripeAdapter } from '@payloadcms/plugin-ecommerce/payments/stripe'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-04-30.basil'
})

export async function POST(request: Request) {
  const body = await request.json()
  
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: body.amount,  // In cents
      currency: body.currency,
      automatic_payment_methods: {
        enabled: true
      },
      metadata: {
        cartId: body.cartId,
        customerId: body.customerId || 'guest'
      }
    })
    
    return Response.json({
      clientSecret: paymentIntent.client_secret
    })
  } catch (error) {
    console.error('Payment intent creation failed:', error)
    return Response.json(
      { error: 'Failed to create payment intent' },
      { status: 500 }
    )
  }
}
```

### Step 4: Process Payment and Create Order

**Payment Processing:**
```typescript
// After Stripe confirms payment
const processPayment = async (paymentIntentId, cart, shippingAddress, billingAddress) => {
  // Verify payment intent status
  const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId)
  
  if (paymentIntent.status !== 'succeeded') {
    throw new Error('Payment not completed')
  }
  
  // Create transaction record
  const transaction = await payload.create({
    collection: 'transactions',
    data: {
      cart: cart.id,
      paymentMethod: 'stripe',
      amount: paymentIntent.amount,
      currency: paymentIntent.currency,
      status: 'succeeded',
      metadata: {
        paymentIntentId: paymentIntent.id,
        stripeCustomerId: paymentIntent.customer
      }
    }
  })
  
  // Create order from cart
  const order = await payload.create({
    collection: 'orders',
    data: {
      customer: cart.customer?.id || null,
      email: cart.email || null,
      items: cart.items.map(item => ({
        product: item.product.id,
        variant: item.variant?.id || null,
        quantity: item.quantity,
        price: item.price,
        total: item.total
      })),
      shippingAddress,
      billingAddress: useSameForBilling ? shippingAddress : billingAddress,
      subtotal: cart.subtotal,
      tax: cart.tax,
      shipping: cart.shipping,
      total: cart.total,
      currency: cart.currency,
      transaction: transaction.id
    }
  })
  
  // Clear cart after successful order
  await payload.update({
    collection: 'carts',
    id: cart.id,
    data: { items: [] }
  })
  
  return order
}
```

## Webhook Handling

### Webhook Endpoint Setup

**Webhook Route:**
```typescript
// src/app/(app)/api/payments/stripe/webhooks/route.ts
import Stripe from 'stripe'
import { headers } from 'next/headers'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-04-30.basil'
})

export async function POST(request: Request) {
  const body = await request.text()
  const signature = (await headers()).get('stripe-signature')!
  
  let event: Stripe.Event
  
  try {
    // Verify webhook signature
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOKS_SIGNING_SECRET!
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err)
    return Response.json(
      { error: 'Invalid signature' },
      { status: 400 }
    )
  }
  
  // Handle event
  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSucceeded(event.data.object)
      break
      
    case 'payment_intent.payment_failed':
      await handlePaymentFailed(event.data.object)
      break
      
    case 'charge.succeeded':
      await handleChargeSucceeded(event.data.object)
      break
      
    case 'charge.failed':
      await handleChargeFailed(event.data.object)
      break
      
    default:
      console.log(`Unhandled event type: ${event.type}`)
  }
  
  return Response.json({ received: true })
}
```

### Webhook Event Handlers

**Payment Succeeded:**
```typescript
const handlePaymentSucceeded = async (paymentIntent: Stripe.PaymentIntent) => {
  console.log('Payment succeeded:', paymentIntent.id)
  
  // Get cart and customer from metadata
  const cartId = paymentIntent.metadata?.cartId
  const customerId = paymentIntent.metadata?.customerId
  
  if (!cartId) {
    console.error('No cart ID in payment metadata')
    return
  }
  
  // Get cart
  const cart = await payload.findByID({
    collection: 'carts',
    id: cartId
  })
  
  if (!cart) {
    console.error('Cart not found:', cartId)
    return
  }
  
  // Create transaction
  const transaction = await payload.create({
    collection: 'transactions',
    data: {
      cart: cartId,
      paymentMethod: 'stripe',
      amount: paymentIntent.amount / 100,  // Convert from cents
      currency: paymentIntent.currency.toUpperCase(),
      status: 'succeeded',
      metadata: {
        paymentIntentId: paymentIntent.id,
        stripeCustomerId: paymentIntent.customer as string
      }
    }
  })
  
  // Create order
  const order = await createOrderFromCart(cart, transaction)
  
  // Send confirmation email
  await sendOrderConfirmationEmail(order)
  
  console.log('Order created:', order.id)
}
```

**Payment Failed:**
```typescript
const handlePaymentFailed = async (paymentIntent: Stripe.PaymentIntent) => {
  console.log('Payment failed:', paymentIntent.id)
  
  const cartId = paymentIntent.metadata?.cartId
  
  if (cartId) {
    // Update transaction status
    const transaction = await payload.query({
      collection: 'transactions',
      where: {
        'metadata.paymentIntentId': { equals: paymentIntent.id }
      }
    })
    
    if (transaction.docs[0]) {
      await payload.update({
        collection: 'transactions',
        id: transaction.docs[0].id,
        data: {
          status: 'failed',
          metadata: {
            ...transaction.docs[0].metadata,
            failureReason: paymentIntent.last_payment_error?.message
          }
        }
      })
    }
  }
  
  // Optionally notify customer
  // await sendPaymentFailedEmail(...)
}
```

### Webhook Security

**Signature Verification:**
```typescript
// Always verify webhook signatures
const verifyWebhookSignature = (body, signature, secret) => {
  try {
    return stripe.webhooks.constructEvent(
      body,
      signature,
      secret
    )
  } catch (error) {
    throw new Error('Invalid webhook signature')
  }
}
```

**Important Security Notes:**
1. **Never skip signature verification**: Always verify `stripe-signature` header
2. **Use webhook secret**: Different from API secret key
3. **Idempotency**: Handle duplicate webhooks gracefully
4. **Retry logic**: Stripe retries failed webhooks automatically

## Stripe Test Mode

### Test Cards

Use these test card numbers in development:

**Successful Payments:**
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/25)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)
```

**Declined Payments:**
```
Card Number: 4000 0000 0000 0002
Result: Payment will be declined
```

**3D Secure Authentication:**
```
Card Number: 4000 0025 0000 3155
Result: Triggers 3D Secure flow
```

**Other Test Scenarios:**
```
Card Requires Action: 4000 0025 0000 3155
Instant Debit (SEPA): 4000 0000 0000 9995
```

See [Stripe Testing Documentation](https://stripe.com/docs/testing) for complete list.

### Test Mode Best Practices

1. **Always use test keys in development**: Never use live keys locally
2. **Test all scenarios**: Success, failure, 3D Secure, refunds
3. **Verify webhook delivery**: Use Stripe Dashboard to inspect webhooks
4. **Check email notifications**: Ensure confirmation emails work

## Order Confirmation

### Confirmation Email

**Email Template:**
```typescript
// src/utilities/sendOrderConfirmationEmail.ts
import { Resend } from 'resend'  // Or your email provider

const sendOrderConfirmationEmail = async (order) => {
  const resend = new Resend(process.env.RESEND_API_KEY)
  
  await resend.emails.send({
    from: 'Store <orders@yourstore.com>',
    to: order.email,
    subject: `Order Confirmation #${order.id}`,
    html: `
      <h1>Thank you for your order!</h1>
      
      <p>Your order has been confirmed and will be processed shortly.</p>
      
      <h2>Order Details</h2>
      <p><strong>Order ID:</strong> ${order.id}</p>
      <p><strong>Total:</strong> $${order.total.toFixed(2)}</p>
      
      <h3>Items</h3>
      <ul>
        ${order.items.map(item => `
          <li>
            ${item.quantity} × ${item.product.title}
            ${item.variant ? `- ${Object.values(item.variant.variantOption).join(', ')}` : ''}
            - $${item.total.toFixed(2)}
          </li>
        `).join('')}
      </ul>
      
      <h3>Shipping Address</h3>
      <p>
        ${order.shippingAddress.line1}<br>
        ${order.shippingAddress.city}, ${order.shippingAddress.state} ${order.shippingAddress.zip}<br>
        ${order.shippingAddress.country}
      </p>
      
      <p>
        Track your order: 
        <a href="${process.env.PAYLOAD_PUBLIC_URL}/find-order?email=${order.email}&orderId=${order.id}">
          View Order Details
        </a>
      </p>
    `
  })
}
```

### Confirmation Page

**Success Page Component:**
```typescript
// src/app/(app)/checkout/confirm-order/page.tsx
const OrderConfirmationPage = ({ searchParams }) => {
  const { orderId } = searchParams
  const [order, setOrder] = useState(null)
  
  useEffect(() => {
    const fetchOrder = async () => {
      const order = await fetchOrderById(orderId)
      setOrder(order)
    }
    
    fetchOrder()
  }, [orderId])
  
  if (!order) return <div>Loading...</div>
  
  return (
    <div className="order-confirmation">
      <div className="success-icon">✓</div>
      
      <h1>Order Confirmed!</h1>
      <p>Thank you for your purchase.</p>
      
      <div className="order-details">
        <p><strong>Order ID:</strong> {order.id}</p>
        <p><strong>Total:</strong> ${order.total.toFixed(2)}</p>
      </div>
      
      <p>We've sent a confirmation email to {order.email}</p>
      
      <button onClick={() => router.push('/')}>
        Continue Shopping
      </button>
    </div>
  )
}
```

## Payment Methods

### Credit/Debit Cards (Default)

Stripe Elements provides secure card input:

```typescript
import { CardElement } from '@stripe/react-stripe-js'

<CardElement options={{
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      iconColor: '#666EE8',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#9e2f2f',
      iconColor: '#9e2f2f'
    }
  }
}} />
```

### Adding Payment Methods

The ecommerce plugin supports multiple payment methods. To add PayPal or other providers:

```typescript
import { paypalAdapter } from '@payloadcms/plugin-ecommerce/payments/paypal'

ecommercePlugin({
  payments: {
    paymentMethods: [
      stripeAdapter({ /* ... */ }),
      paypalAdapter({
        clientId: process.env.PAYPAL_CLIENT_ID,
        clientSecret: process.env.PAYPAL_CLIENT_SECRET,
        environment: 'sandbox'  // or 'production'
      })
    ]
  }
})
```

## Refunds and Disputes

### Processing Refunds

**Via Stripe API:**
```typescript
const processRefund = async (paymentIntentId, amount?) => {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)
  
  const refund = await stripe.refunds.create({
    payment_intent: paymentIntentId,
    amount: amount,  // Optional - omit for full refund
    reason: 'requested_by_customer'  // or 'duplicate', 'fraudulent', etc.
  })
  
  // Update transaction record
  await payload.update({
    collection: 'transactions',
    id: transactionId,
    data: {
      status: 'refunded',
      metadata: {
        ...transaction.metadata,
        refundId: refund.id,
        refundedAt: new Date().toISOString()
      }
    }
  })
  
  return refund
}
```

**Via Stripe Dashboard:**
1. Navigate to Payments > Find Payment
2. Click "Refund" button
3. Select full or partial refund
4. Add optional reason note
5. Confirm refund

### Handling Disputes

When a customer disputes a charge with their bank:

**Webhook Event:**
```typescript
case 'charge.dispute.created':
  await handleDisputeCreated(event.data.object)
  break

const handleDisputeCreated = async (dispute: Stripe.Dispute) => {
  console.log('Dispute created:', dispute.id)
  
  // Notify admin team
  await sendAdminAlertEmail({
    subject: 'New Dispute Received',
    dispute: dispute
  })
  
  // Update order status
  await payload.update({
    collection: 'orders',
    id: dispute.metadata?.orderId,
    data: {
      status: 'disputed'
    }
  })
}
```

**Responding to Disputes:**
1. Gather evidence (proof of delivery, communication logs)
2. Submit evidence via Stripe Dashboard within 7 days
3. Stripe makes final decision

## Currency Support

### Multi-Currency Configuration

**Enable Currencies:**
```typescript
ecommercePlugin({
  currencies: ['USD', 'EUR', 'GBP', 'CAD'],
  defaultCurrency: 'USD'
})
```

**Product Pricing:**
```typescript
{
  title: "International Product",
  priceInUSD: 29.99,
  priceInEUR: 27.99,
  priceInGBP: 24.99,
  priceInCAD: 39.99
}
```

**Currency Conversion:**
- Manual: Set prices for each currency
- Automatic: Use exchange rate API (requires custom implementation)

**Frontend Currency Display:**
```typescript
const { currency } = useStore()

const price = product[`priceIn${currency}`] || product.priceInUSD
const symbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : '£'

<p>{symbol}{price.toFixed(2)}</p>
```

## Error Handling

### Payment Errors

**Common Errors:**
```typescript
const handlePaymentError = (error) => {
  switch (error.type) {
    case 'card_error':
      // Card was declined
      showToast('Your card was declined. Please try another payment method.')
      break
      
    case 'validation_error':
      // Invalid field (e.g., incomplete card number)
      showToast('Please check your payment details.')
      break
      
    case 'rate_limit_error':
      // Too many requests
      showToast('Too many attempts. Please wait a moment and try again.')
      break
      
    default:
      showToast('An error occurred. Please try again.')
  }
}
```

### Network Errors

**Retry Logic:**
```typescript
const processPaymentWithRetry = async (attempt = 0) => {
  try {
    return await processPayment()
  } catch (error) {
    if (attempt < 3 && isNetworkError(error)) {
      // Exponential backoff
      const delay = Math.pow(2, attempt) * 1000
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return processPaymentWithRetry(attempt + 1)
    }
    
    throw error
  }
}
```

See [Orders and Transactions](06-orders-transactions.md) for order creation after payment.
See [Troubleshooting Guide](10-troubleshooting.md) for common payment issues.
