# Orders and Transactions

Complete guide to order management, transaction tracking, guest order access, and order lifecycle in the Payload CMS ecommerce template v3.82.1.

## Order Architecture

### Order Collection Schema

The ecommerce plugin adds an `orders` collection with custom fields.

**Order Structure:**
```typescript
interface Order {
  id: string
  customer?: User           // Null for guest orders
  email: string             // Customer email (required)
  accessToken: string       // Unique token for guest access (UUID)
  
  // Items
  items: OrderItem[]
  
  // Addresses
  shippingAddress: Address
  billingAddress: Address
  
  // Financials
  subtotal: number
  tax: number
  shipping: number
  total: number
  currency: string
  
  // Status
  status: OrderStatus
  _status: 'draft' | 'published'
  
  // Relationships
  transaction?: Transaction
  
  // Timestamps
  createdAt: string
  updatedAt: string
}

interface OrderItem {
  product: Product
  variant?: Variant
  quantity: number
  price: number             // Price at time of purchase
  total: number             // price × quantity
}

interface Address {
  line1: string
  line2?: string
  city: string
  state: string
  zip: string
  country: string
}

type OrderStatus = 
  | 'pending'               // Payment processing
  | 'completed'             // Payment successful
  | 'shipped'               // Order shipped
  | 'delivered'             // Order delivered
  | 'cancelled'             // Order cancelled
  | 'refunded'              // Refund processed
  | 'disputed'              // Payment disputed
```

### Transaction Collection Schema

Transactions track payment lifecycle before order creation.

**Transaction Structure:**
```typescript
interface Transaction {
  id: string
  
  // Relationships
  cart?: Cart
  order?: Order             // Null until payment succeeds
  
  // Payment Details
  paymentMethod: 'stripe' | 'paypal' | string
  amount: number
  currency: string
  
  // Status
  status: TransactionStatus
  
  // Metadata
  metadata: {
    paymentIntentId?: string   // Stripe Payment Intent ID
    stripeCustomerId?: string
    refundId?: string
    failureReason?: string
    [key: string]: unknown
  }
  
  // Timestamps
  createdAt: string
  updatedAt: string
}

type TransactionStatus = 
  | 'pending'               // Payment initiated
  | 'processing'            // Payment being processed
  | 'succeeded'             // Payment successful
  | 'failed'                // Payment failed
  | 'refunded'              // Refund processed
```

## Order Lifecycle

### Stage 1: Cart to Pending Order

**When payment is initiated:**

```typescript
const initiateOrder = async (cartId, paymentIntentId) => {
  // Get cart
  const cart = await payload.findByID({
    collection: 'carts',
    id: cartId
  })
  
  // Create transaction record
  const transaction = await payload.create({
    collection: 'transactions',
    data: {
      cart: cartId,
      paymentMethod: 'stripe',
      amount: cart.total,
      currency: cart.currency,
      status: 'pending',
      metadata: {
        paymentIntentId
      }
    }
  })
  
  // Update transaction to processing
  await payload.update({
    collection: 'transactions',
    id: transaction.id,
    data: { status: 'processing' }
  })
  
  return transaction
}
```

### Stage 2: Payment Processing

**Stripe payment intent created:**

```typescript
// Frontend initiates payment
const clientSecret = await createPaymentIntent(cart.total)

// Customer enters card details
const { error } = await stripe.confirmCardPayment(clientSecret, {
  payment_method: { card: cardElement }
})

if (error) {
  // Payment failed - webhook will update transaction status
  showError(error.message)
} else {
  // Payment processing - wait for webhook confirmation
  showProcessingMessage()
}
```

### Stage 3: Payment Success via Webhook

**Webhook confirms payment:**

```typescript
// In webhook handler
case 'payment_intent.succeeded':
  const paymentIntent = event.data.object
  
  // Update transaction status
  const transaction = await payload.update({
    collection: 'transactions',
    id: transactionId,
    data: {
      status: 'succeeded',
      metadata: {
        ...transaction.metadata,
        stripeCustomerId: paymentIntent.customer
      }
    }
  })
  
  // Create order from cart
  const order = await createOrderFromCart({
    transactionId: transaction.id,
    paymentIntent
  })
  
  // Send confirmation email
  await sendOrderConfirmationEmail(order)
  
  break
```

### Stage 4: Order Creation

**Create order after successful payment:**

```typescript
const createOrderFromCart = async ({ transactionId, paymentIntent }) => {
  const transaction = await payload.findByID({
    collection: 'transactions',
    id: transactionId
  })
  
  const cart = await payload.findByID({
    collection: 'carts',
    id: transaction.cart.id
  })
  
  // Generate access token for guest order access
  const accessToken = crypto.randomUUID()
  
  // Create order
  const order = await payload.create({
    collection: 'orders',
    data: {
      customer: cart.customer?.id || null,
      email: cart.email || null,
      accessToken,
      
      items: cart.items.map(item => ({
        product: item.product.id,
        variant: item.variant?.id || null,
        quantity: item.quantity,
        price: item.price,
        total: item.total
      })),
      
      shippingAddress: cart.shippingAddress,
      billingAddress: cart.billingAddress,
      
      subtotal: cart.subtotal,
      tax: cart.tax,
      shipping: cart.shipping,
      total: cart.total,
      currency: cart.currency,
      
      transaction: transactionId,
      status: 'completed'
    }
  })
  
  // Link order to transaction
  await payload.update({
    collection: 'transactions',
    id: transactionId,
    data: { order: order.id }
  })
  
  // Decrement inventory
  await decrementInventoryForOrder(order)
  
  // Clear cart
  await payload.update({
    collection: 'carts',
    id: cart.id,
    data: { items: [] }
  })
  
  return order
}
```

### Stage 5: Order Fulfillment

**Update order status as it progresses:**

```typescript
// Mark order as shipped
const markOrderShipped = async (orderId, trackingNumber?) => {
  await payload.update({
    collection: 'orders',
    id: orderId,
    data: {
      status: 'shipped',
      metadata: {
        trackingNumber,
        shippedAt: new Date().toISOString()
      }
    }
  })
  
  // Send shipping notification email
  const order = await payload.findByID({
    collection: 'orders',
    id: orderId
  })
  
  await sendShippingNotificationEmail(order)
}

// Mark order as delivered
const markOrderDelivered = async (orderId) => {
  await payload.update({
    collection: 'orders',
    id: orderId,
    data: {
      status: 'delivered',
      metadata: {
        deliveredAt: new Date().toISOString()
      }
    }
  })
}
```

## Guest Order Access

### Access Token Generation

Each order receives a unique access token for secure guest access.

**Auto-Generation (src/plugins/index.ts):**
```typescript
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
                return crypto.randomUUID()  // Generate UUID v4
              }
              return value
            },
          ],
        },
      },
    ],
  }),
}
```

**Token Characteristics:**
- **Format**: UUID v4 (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Uniqueness**: Guaranteed unique per order
- **Indexing**: Fast database lookups
- **Read-only**: Cannot be modified after creation

### Guest Order Lookup Flow

**Step 1: Customer Requests Access**

```typescript
// src/app/(app)/find-order/page.tsx
const FindOrderPage = () => {
  const [email, setEmail] = useState('')
  const [orderId, setOrderId] = useState('')
  const [status, setStatus] = useState(null)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      // Verify order exists for this email
      const order = await payload.query({
        collection: 'orders',
        where: {
          and: [
            { id: { equals: orderId } },
            { email: { equals: email } }
          ]
        }
      })
      
      if (order.docs.length === 0) {
        setStatus('not_found')
        return
      }
      
      // Send access link via email
      await sendOrderAccessEmail({
        email,
        orderId,
        accessToken: order.docs[0].accessToken
      })
      
      setStatus('email_sent')
    } catch (error) {
      setStatus('error')
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <h1>Find Your Order</h1>
      
      <input
        type="email"
        placeholder="Email address"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      
      <input
        type="text"
        placeholder="Order ID"
        value={orderId}
        onChange={(e) => setOrderId(e.target.value)}
        required
      />
      
      <button type="submit">Get Order Link</button>
      
      {status === 'email_sent' && (
        <div className="success">
          We've sent an email with a secure link to view your order.
        </div>
      )}
      
      {status === 'not_found' && (
        <div className="error">
          No order found with that ID and email combination.
        </div>
      )}
    </form>
  )
}
```

**Step 2: Send Access Email**

```typescript
const sendOrderAccessEmail = async ({ email, orderId, accessToken }) => {
  const resend = new Resend(process.env.RESEND_API_KEY)
  
  // Create secure access URL
  const accessUrl = `${process.env.PAYLOAD_PUBLIC_URL}/order/${orderId}?token=${accessToken}`
  
  await resend.emails.send({
    from: 'Store <orders@yourstore.com>',
    to: email,
    subject: `Access Link for Order #${orderId}`,
    html: `
      <h1>View Your Order</h1>
      
      <p>You requested access to view order #${orderId}.</p>
      
      <p>
        Click the link below to view your order details:
      </p>
      
      <a href="${accessUrl}" class="button">
        View Order Details
      </a>
      
      <p>This link is secure and can only be used to view this specific order.</p>
      
      <p>The link will expire in 7 days for security reasons.</p>
    `
  })
}
```

**Step 3: Verify Access Token**

```typescript
// src/app/(app)/order/[id]/page.tsx
const OrderDetailPage = ({ params, searchParams }) => {
  const { id: orderId } = params
  const { token: accessToken } = searchParams
  
  const [order, setOrder] = useState(null)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchOrder = async () => {
      try {
        // Verify access token matches order
        const order = await payload.query({
          collection: 'orders',
          where: {
            and: [
              { id: { equals: orderId } },
              { accessToken: { equals: accessToken } }
            ]
          }
        })
        
        if (order.docs.length === 0) {
          setError('Invalid access token')
          return
        }
        
        setOrder(order.docs[0])
      } catch (error) {
        setError('Failed to load order')
      }
    }
    
    fetchOrder()
  }, [orderId, accessToken])
  
  if (error) return <div>Error: {error}</div>
  if (!order) return <div>Loading...</div>
  
  return <OrderDetails order={order} />
}
```

### Security Considerations

**Why Email Verification is Required:**

1. **Prevents Enumeration Attacks**: Cannot iterate through order IDs to access orders
2. **Email Confirmation**: Ensures requester has access to order email
3. **Secure Token**: UUID tokens are unpredictable and unique
4. **No Password Required**: Simple UX while maintaining security

**Access Control Rules:**

```typescript
// src/access/orderAccess.ts
export const orderAccess: Access = ({ req }) => {
  // Admins see all orders
  if (req.user && checkRole(['admin'], req.user)) {
    return true
  }
  
  // Customers see their own orders
  if (req.user?.id) {
    return {
      customer: { equals: req.user.id }
    }
  }
  
  // Guests need valid accessToken + email match
  if (req.query?.accessToken && req.query?.email) {
    return {
      and: [
        { accessToken: { equals: req.query.accessToken } },
        { email: { equals: req.query.email } }
      ]
    }
  }
  
  // No access
  return false
}
```

## Order Management

### Viewing Orders (Admin)

**Admin Panel Features:**

1. **Order List**: All orders with filtering and sorting
2. **Order Details**: Complete order information
3. **Status Updates**: Change order status
4. **Transaction History**: View payment records

**Custom Admin View:**
```typescript
// In Orders collection config
admin: {
  defaultColumns: ['id', 'customer', 'total', 'status', 'createdAt'],
  listViews: [
    {
      title: 'All Orders',
      query: {}
    },
    {
      title: 'Pending Orders',
      query: { status: { equals: 'pending' } }
    },
    {
      title: 'Completed Orders',
      query: { status: { equals: 'completed' } }
    }
  ]
}
```

### Viewing Orders (Customer)

**Account Dashboard:**

```typescript
// src/app/(app)/(account)/orders/page.tsx
const OrderHistoryPage = () => {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  
  useEffect(() => {
    const fetchOrders = async () => {
      const orders = await payload.query({
        collection: 'orders',
        where: {
          customer: { equals: user.id }
        },
        sort: '-createdAt'
      })
      
      setOrders(orders.docs)
    }
    
    fetchOrders()
  }, [user])
  
  return (
    <div className="order-history">
      <h1>Order History</h1>
      
      {orders.length === 0 ? (
        <p>You haven't placed any orders yet.</p>
      ) : (
        <ul>
          {orders.map(order => (
            <li key={order.id}>
              <Link href={`/orders/${order.id}`}>
                <OrderCard order={order} />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

### Order Status Updates

**Available Statuses:**

```typescript
const orderStatuses = [
  { value: 'pending', label: 'Pending Payment' },
  { value: 'completed', label: 'Payment Completed' },
  { value: 'processing', label: 'Processing' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'delivered', label: 'Delivered' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'refunded', label: 'Refunded' },
  { value: 'disputed', label: 'Disputed' }
]
```

**Update Status (Admin):**
```typescript
const updateOrderStatus = async (orderId, newStatus, metadata?) => {
  await payload.update({
    collection: 'orders',
    id: orderId,
    data: {
      status: newStatus,
      metadata: {
        ...metadata,
        statusUpdatedAt: new Date().toISOString()
      }
    }
  })
  
  // Send notification email based on status
  if (newStatus === 'shipped') {
    await sendShippingNotification(orderId)
  } else if (newStatus === 'delivered') {
    await sendDeliveryConfirmation(orderId)
  }
}
```

## Inventory Management

### Decrementing Inventory

**After Order Creation:**

```typescript
const decrementInventoryForOrder = async (order) => {
  for (const item of order.items) {
    const product = await payload.findByID({
      collection: 'products',
      id: item.product.id
    })
    
    if (product.enableVariants && item.variant) {
      // Decrement variant inventory
      const variant = product.variants.variants.find(
        v => v.id === item.variant.id
      )
      
      if (variant) {
        variant.inventory -= item.quantity
        
        await payload.update({
          collection: 'products',
          id: product.id,
          data: { variants: product.variants }
        })
      }
    } else {
      // Decrement product inventory
      product.inventory -= item.quantity
      
      await payload.update({
        collection: 'products',
        id: product.id,
        data: { inventory: product.inventory }
      })
    }
  }
}
```

### Restocking Inventory

**Manual Restock (Admin):**

```typescript
const restockProduct = async (productId, quantity, variantId?) => {
  const product = await payload.findByID({
    collection: 'products',
    id: productId
  })
  
  if (variantId) {
    // Restock specific variant
    const variant = product.variants.variants.find(v => v.id === variantId)
    variant.inventory += quantity
    
    await payload.update({
      collection: 'products',
      id: productId,
      data: { variants: product.variants }
    })
  } else {
    // Restock simple product
    product.inventory += quantity
    
    await payload.update({
      collection: 'products',
      id: productId,
      data: { inventory: product.inventory }
    })
  }
}
```

**Automated Restock (Integration):**

```typescript
// Webhook from inventory management system
const handleInventoryUpdate = async (inventoryData) => {
  for (const item of inventoryData) {
    await restockProduct(item.productId, item.quantity, item.variantId)
  }
}
```

## Order Analytics

### Sales Reports

**Daily Sales:**
```typescript
const getDailySales = async (date) => {
  const startOfDay = new Date(date)
  startOfDay.setHours(0, 0, 0, 0)
  
  const endOfDay = new Date(date)
  endOfDay.setHours(23, 59, 59, 999)
  
  const orders = await payload.query({
    collection: 'orders',
    where: {
      and: [
        { createdAt: { gte: startOfDay.toISOString() } },
        { createdAt: { lte: endOfDay.toISOString() } },
        { status: { equals: 'completed' } }
      ]
    }
  })
  
  const totalRevenue = orders.docs.reduce((sum, order) => 
    sum + order.total, 0
  )
  
  const totalOrders = orders.docs.length
  
  return {
    date: date.toISOString(),
    orders: totalOrders,
    revenue: totalRevenue,
    averageOrderValue: totalRevenue / totalOrders
  }
}
```

**Top Products:**
```typescript
const getTopProducts = async (limit = 10) => {
  // Aggregate sales by product
  const orders = await payload.query({
    collection: 'orders',
    where: { status: { equals: 'completed' } },
    limit: 1000  // Adjust for production
  })
  
  const productSales = {}
  
  for (const order of orders.docs) {
    for (const item of order.items) {
      if (!productSales[item.product.id]) {
        productSales[item.product.id] = {
          productId: item.product.id,
          quantity: 0,
          revenue: 0
        }
      }
      
      productSales[item.product.id].quantity += item.quantity
      productSales[item.product.id].revenue += item.total
    }
  }
  
  // Sort by revenue
  return Object.values(productSales)
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, limit)
}
```

## Transaction Management

### Viewing Transactions

**Admin Access Only:**

```typescript
// Transactions collection access control
access: {
  read: adminOnly,
  create: adminOnly,
  update: adminOnly,
  delete: adminOnly
}
```

**Transaction History:**

```typescript
const getTransactionHistory = async (orderId) => {
  const order = await payload.findByID({
    collection: 'orders',
    id: orderId
  })
  
  const transaction = await payload.findByID({
    collection: 'transactions',
    id: order.transaction.id
  })
  
  return {
    ...transaction,
    metadata: {
      statusHistory: transaction.metadata?.statusHistory || []
    }
  }
}
```

### Failed Transactions

**Handling Payment Failures:**

```typescript
const handleFailedTransaction = async (transactionId, failureReason) => {
  // Update transaction status
  await payload.update({
    collection: 'transactions',
    id: transactionId,
    data: {
      status: 'failed',
      metadata: {
        failureReason,
        failedAt: new Date().toISOString()
      }
    }
  })
  
  // Optionally notify customer
  const transaction = await payload.findByID({
    collection: 'transactions',
    id: transactionId
  })
  
  const cart = await payload.findByID({
    collection: 'carts',
    id: transaction.cart.id
  })
  
  await sendPaymentFailedEmail({
    email: cart.email,
    amount: transaction.amount,
    reason: failureReason
  })
}
```

## Order Emails

### Confirmation Email

See [Payments and Checkout](05-payments-checkout.md) for order confirmation email template.

### Shipping Notification

```typescript
const sendShippingNotificationEmail = async (order) => {
  const resend = new Resend(process.env.RESEND_API_KEY)
  
  await resend.emails.send({
    from: 'Store <orders@yourstore.com>',
    to: order.email,
    subject: `Your Order #${order.id} Has Shipped!`,
    html: `
      <h1>Your Order is on the Way!</h1>
      
      <p>Great news - your order has been shipped!</p>
      
      <h2>Shipping Details</h2>
      <p><strong>Tracking Number:</strong> ${order.metadata?.trackingNumber}</p>
      <p><strong>Carrier:</strong> ${order.metadata?.carrier}</p>
      
      <h3>Shipping Address</h3>
      <p>
        ${order.shippingAddress.line1}<br>
        ${order.shippingAddress.city}, ${order.shippingAddress.state} ${order.shippingAddress.zip}<br>
        ${order.shippingAddress.country}
      </p>
      
      <a href="${process.env.PAYLOAD_PUBLIC_URL}/orders/${order.id}?token=${order.accessToken}">
        Track Your Order
      </a>
    `
  })
}
```

## Best Practices

### Order Security

1. **Never expose accessToken in URLs**: Use POST requests or hidden form fields
2. **Validate tokens server-side**: Always verify on backend, not just frontend
3. **Token expiration**: Implement token expiry for added security
4. **Rate limiting**: Prevent brute force attacks on order lookup

### Inventory Accuracy

1. **Real-time updates**: Decrement inventory immediately on payment success
2. **Reservation system**: Reserve inventory when cart abandoned (optional)
3. **Buffer stock**: Maintain safety stock to prevent overselling
4. **Regular audits**: Reconcile physical and digital inventory

### Order Fulfillment

1. **Clear status workflow**: Define order status progression
2. **Automated notifications**: Email customers at each stage
3. **Tracking integration**: Auto-update tracking numbers
4. **Return handling**: Clear process for returns and refunds

See [Troubleshooting Guide](10-troubleshooting.md) for common order issues.
