# Shopping Cart

Complete guide to shopping cart functionality, guest cart management, cart persistence, and cart operations in the Payload CMS ecommerce template v3.82.1.

## Cart Architecture

### Cart Collection

The ecommerce plugin adds a `carts` collection to manage shopping carts.

**Collection Schema:**
```typescript
interface Cart {
  id: string
  customer?: User           // Null for guest carts
  email?: string            // For guest cart recovery
  items: CartItem[]
  currency: string          // 'USD', 'EUR', etc.
  total: number             // Calculated total in selected currency
  subtotal: number          // Items total before tax/shipping
  tax: number               // Calculated tax (if configured)
  shipping: number          // Shipping cost (if configured)
  createdAt: string
  updatedAt: string
}

interface CartItem {
  product: Product
  variant?: Variant
  quantity: number
  price: number             // Price at time of adding to cart
  total: number             // price × quantity
}
```

### Cart Types

**Authenticated User Cart:**
- Linked to user account via `customer` field
- Persists across sessions
- Accessible from any device when logged in
- One active cart per user

**Guest Cart:**
- No `customer` association
- Identified by cart ID in session/localStorage
- Optional email for recovery
- Can be merged into user cart on login

## Cart Operations

### Adding Items to Cart

**API Endpoint:**
```typescript
POST /api/carts/:id/items
{
  "product": "product-slug-or-id",
  "variant": "variant-id",        // Optional for simple products
  "quantity": 1
}
```

**Frontend Implementation:**
```typescript
// Using React context
const { addToCart } = useCart()

const handleAddToCart = async (productId, variantId?, quantity) => {
  await addToCart({
    product: productId,
    variant: variantId,
    quantity
  })
}
```

**With Variants:**
```typescript
// Simple product (no variants)
await addToCart({
  product: "classic-notebook",
  quantity: 2
})

// Variable product (with variant selection)
await addToCart({
  product: "tshirt",
  variant: { size: "medium", color: "blue" },
  quantity: 1
})
```

### Updating Cart Items

**Update Quantity:**
```typescript
PATCH /api/carts/:id/items/:itemId
{
  "quantity": 3
}
```

**Frontend:**
```typescript
const { updateCartItem } = useCart()

const handleQuantityChange = async (itemId, newQuantity) => {
  await updateCartItem({
    itemId,
    quantity: newQuantity
  })
}
```

**Quantity Rules:**
- Minimum: 1 (or removes item if set to 0)
- Maximum: Limited by available inventory
- Negative values: Rejected

### Removing Items from Cart

**Remove Single Item:**
```typescript
DELETE /api/carts/:id/items/:itemId
```

**Frontend:**
```typescript
const { removeCartItem } = useCart()

const handleRemoveItem = async (itemId) => {
  await removeCartItem(itemId)
}
```

**Clear Entire Cart:**
```typescript
// Remove all items
const { clearCart } = useCart()

await clearCart()
```

### Cart Calculation

**Automatic Calculations:**

The cart automatically calculates:

1. **Item Total**: `price × quantity` for each item
2. **Subtotal**: Sum of all item totals
3. **Tax**: Applied via hooks (if configured)
4. **Shipping**: Applied via hooks (if configured)
5. **Total**: `subtotal + tax + shipping`

**Example Cart Totals:**
```typescript
{
  items: [
    {
      product: "T-Shirt",
      quantity: 2,
      price: 24.99,
      total: 49.98
    },
    {
      product: "Sneakers",
      quantity: 1,
      price: 89.99,
      total: 89.99
    }
  ],
  subtotal: 139.97,
  tax: 11.20,           // 8% tax
  shipping: 5.99,
  total: 157.16
}
```

**Tax Configuration:**

Basic tax hook example:
```typescript
// In cart collection hooks
hooks: {
  beforeChange: [
    async ({ data, operation }) => {
      if (operation === 'update' || operation === 'create') {
        // Calculate tax based on shipping address or user location
        const taxRate = 0.08  // 8%
        data.tax = data.subtotal * taxRate
        data.total = data.subtotal + data.tax + (data.shipping || 0)
      }
    }
  ]
}
```

**Shipping Configuration:**

Basic shipping hook example:
```typescript
hooks: {
  beforeChange: [
    async ({ data }) => {
      // Free shipping over $50
      if (data.subtotal >= 50) {
        data.shipping = 0
      } else {
        data.shipping = 5.99
      }
      data.total = data.subtotal + (data.tax || 0) + data.shipping
    }
  ]
}
```

## Guest Cart Management

### Guest Cart Creation

Guest carts are created automatically when a guest adds items.

**Flow:**
1. Guest visits product page
2. Clicks "Add to Cart"
3. System creates cart (no authentication required)
4. Cart ID stored in browser localStorage/sessionStorage
5. Cart persists across page navigations

**Implementation:**
```typescript
const { getOrCreateGuestCart } = useCart()

const cart = await getOrCreateGuestCart()
// Returns existing cart or creates new one
```

### Guest Cart Storage

**Client-Side Storage:**
```typescript
// Store cart ID in localStorage
localStorage.setItem('cartId', cart.id)

// Retrieve on page load
const storedCartId = localStorage.getItem('cartId')
```

**Server-Side Session (Alternative):**
```typescript
// Store in session cookie
req.session.cartId = cart.id
```

### Guest Cart Recovery

Allow guests to recover carts by providing email.

**Email Collection:**
```typescript
// At checkout, collect email before payment
const { updateGuestCartEmail } = useCart()

await updateGuestCartEmail({
  cartId: cart.id,
  email: 'customer@example.com'
})
```

**Recovery Flow:**
1. Guest abandons cart with items
2. Later, visits site and enters email at checkout
3. System finds cart with matching email
4. Restores cart items
5. Guest completes checkout

**Implementation:**
```typescript
// Find guest cart by email
const existingCart = await payload.query({
  collection: 'carts',
  where: {
    and: [
      { customer: { exists: false } },  // No customer (guest cart)
      { email: { equals: 'customer@example.com' } }
    ]
  }
})
```

### Guest to Authenticated Cart Merge

When a guest with a cart logs in, merge the carts.

**Merge Logic:**
```typescript
const mergeGuestCartToUser = async (guestCartId, userId) => {
  // Get guest cart
  const guestCart = await payload.findByID({
    collection: 'carts',
    id: guestCartId
  })
  
  // Get or create user cart
  let userCart = await payload.query({
    collection: 'carts',
    where: {
      and: [
        { customer: { equals: userId } },
        { 'items.id': { exists: true } }  // Has items
      ]
    }
  })
  
  if (!userCart) {
    // Create new user cart
    userCart = await payload.create({
      collection: 'carts',
      data: {
        customer: userId,
        items: [],
        currency: 'USD'
      }
    })
  }
  
  // Merge items (combine quantities if same product)
  for (const guestItem of guestCart.items) {
    const existingItem = userCart.items.find(
      item => item.product.id === guestItem.product.id &&
              item.variant?.id === guestItem.variant?.id
    )
    
    if (existingItem) {
      // Add to existing quantity
      existingItem.quantity += guestItem.quantity
    } else {
      // Add new item
      userCart.items.push(guestItem)
    }
  }
  
  // Update user cart
  await payload.update({
    collection: 'carts',
    id: userCart.id,
    data: { items: userCart.items }
  })
  
  // Clear guest cart
  await payload.delete({
    collection: 'carts',
    id: guestCartId
  })
  
  return userCart
}
```

**Frontend Integration:**
```typescript
// In Auth provider on login success
const { mergeGuestCart } = useCart()

const handleLogin = async (credentials) => {
  const user = await login(credentials)
  
  // Merge guest cart if exists
  const guestCartId = localStorage.getItem('cartId')
  if (guestCartId) {
    await mergeGuestCart(guestCartId, user.id)
    localStorage.removeItem('cartId')  // Clear guest cart ID
  }
  
  return user
}
```

## Cart Persistence

### Authenticated User Persistence

User carts are automatically persisted to database.

**Auto-Save Behavior:**
- Cart saved on every add/update/remove operation
- Retrieved on page load if user authenticated
- Syncs across devices (same user account)

**Implementation:**
```typescript
// Cart provider automatically manages persistence
const { cart } = useCart()

if (user.isAuthenticated) {
  // Fetch user's active cart
  const userCart = await payload.query({
    collection: 'carts',
    where: {
      and: [
        { customer: { equals: user.id } },
        { 'items.id': { exists: true } }  // Has items
      ]
    }
  })
  
  setCart(userCart)
}
```

### Guest Cart Persistence

Guest carts persist via client-side storage.

**Storage Options:**

**localStorage (Recommended):**
```typescript
// Survives browser close and reopen
localStorage.setItem('cartId', cart.id)
localStorage.setItem('cartItems', JSON.stringify(cart.items))
```

**sessionStorage:**
```typescript
// Cleared when browser closes
sessionStorage.setItem('cartId', cart.id)
```

**Hybrid Approach:**
```typescript
// Store cart ID in localStorage, items in memory
// Fetch full cart from server on page load
const storedCartId = localStorage.getItem('cartId')
if (storedCartId) {
  const cart = await fetch(`/api/carts/${storedCartId}`)
  setCart(cart)
}
```

### Cart Expiration

Clean up abandoned carts periodically.

**Cleanup Job:**
```typescript
// Run daily via cron job or Payload jobs queue
const cleanupAbandonedCarts = async () => {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  
  const abandonedCarts = await payload.query({
    collection: 'carts',
    where: {
      and: [
        { customer: { exists: false } },  // Guest carts only
        { createdAt: { less_than: thirtyDaysAgo.toISOString() } }
      ]
    }
  })
  
  // Delete old guest carts
  for (const cart of abandonedCarts.docs) {
    await payload.delete({
      collection: 'carts',
      id: cart.id
    })
  }
}
```

## Cart Access Control

### Read Access

**Authenticated Users:**
```typescript
// Can only read their own cart
access: {
  read: ({ req: { user } }) => {
    if (user) {
      return { customer: { equals: user.id } }
    }
    // Guests can read any cart by ID (for checkout flow)
    return true
  }
}
```

**Guests:**
- Can read cart by ID (from localStorage)
- Cannot enumerate other carts
- Cart ID must be known

### Update Access

**Authenticated Users:**
```typescript
access: {
  update: ({ req: { user } }) => {
    if (user) {
      return { customer: { equals: user.id } }
    }
    // Guests can update any cart by ID
    return true
  }
}
```

**Guests:**
- Can update cart by ID
- Cannot modify other guest carts without knowing ID

### Delete Access

**Authenticated Users:**
```typescript
access: {
  delete: ({ req: { user } }) => {
    if (user) {
      return { customer: { equals: user.id } }
    }
    return false  // Guests cannot delete carts
  }
}
```

## Cart UI Components

### Cart Item Display

**Component Structure:**
```typescript
// src/components/cart/CartItem.tsx
const CartItem = ({ item }) => {
  return (
    <div className="cart-item">
      <Image 
        src={item.product.gallery[0].image} 
        alt={item.product.title}
        width={80}
        height={80}
      />
      
      <div className="item-details">
        <h3>{item.product.title}</h3>
        {item.variant && (
          <p className="variant">
            {Object.values(item.variant.variantOption).join(', ')}
          </p>
        )}
        
        <div className="item-price">
          ${item.price.toFixed(2)} × {item.quantity} = ${item.total.toFixed(2)}
        </div>
      </div>
      
      <div className="item-actions">
        <QuantitySelector 
          value={item.quantity}
          onChange={(newQty) => updateCartItem(item.id, newQty)}
          max={item.product.inventory}
        />
        
        <button onClick={() => removeCartItem(item.id)}>
          Remove
        </button>
      </div>
    </div>
  )
}
```

### Cart Summary

**Component Structure:**
```typescript
// src/components/cart/CartSummary.tsx
const CartSummary = ({ cart }) => {
  return (
    <div className="cart-summary">
      <div className="summary-row">
        <span>Subtotal</span>
        <span>${cart.subtotal.toFixed(2)}</span>
      </div>
      
      {cart.tax > 0 && (
        <div className="summary-row">
          <span>Tax</span>
          <span>${cart.tax.toFixed(2)}</span>
        </div>
      )}
      
      {cart.shipping > 0 && (
        <div className="summary-row">
          <span>Shipping</span>
          <span>${cart.shipping.toFixed(2)}</span>
        </div>
      )}
      
      <div className="summary-row total">
        <span>Total</span>
        <span>${cart.total.toFixed(2)}</span>
      </div>
      
      <button 
        className="checkout-button"
        onClick={() => router.push('/checkout')}
      >
        Proceed to Checkout
      </button>
    </div>
  )
}
```

### Cart Icon with Count

**Component Structure:**
```typescript
// src/components/layout/Header.tsx
const CartIcon = () => {
  const { cart } = useCart()
  
  const itemCount = cart?.items?.reduce(
    (sum, item) => sum + item.quantity, 
    0
  ) || 0
  
  return (
    <button onClick={() => router.push('/cart')}>
      <ShoppingBagIcon />
      {itemCount > 0 && (
        <span className="cart-count">{itemCount}</span>
      )}
    </button>
  )
}
```

## Cart Validation

### Inventory Validation

Ensure cart items don't exceed available inventory.

**Validation Hook:**
```typescript
hooks: {
  beforeValidate: [
    async ({ data, operation }) => {
      if (operation === 'create' || operation === 'update') {
        for (const item of data.items) {
          const product = await payload.findByID({
            collection: 'products',
            id: item.product.id
          })
          
          let availableInventory = 0
          
          if (product.enableVariants && item.variant) {
            // Check variant inventory
            const variant = product.variants.variants.find(
              v => v.id === item.variant.id
            )
            availableInventory = variant?.inventory || 0
          } else {
            // Check product inventory
            availableInventory = product.inventory || 0
          }
          
          if (item.quantity > availableInventory) {
            throw new Error(
              `Only ${availableInventory} units of "${product.title}" available`
            )
          }
        }
      }
    }
  ]
}
```

### Price Validation

Lock in prices at time of adding to cart.

**Why Lock Prices:**
- Product price may change after item added to cart
- Customer should pay price shown when they added item
- Prevent disputes over price changes

**Implementation:**
```typescript
// When adding to cart, store price in cart item
const addToCart = async (productId, variantId, quantity) => {
  const product = await getProduct(productId)
  
  const itemPrice = variantId 
    ? getVariantPrice(product, variantId)
    : product.priceInUSD
  
  // Store price in cart item
  await payload.update({
    collection: 'carts',
    id: cart.id,
    data: {
      items: [
        ...cart.items,
        {
          product: productId,
          variant: variantId,
          quantity,
          price: itemPrice,  // Locked price
          total: itemPrice * quantity
        }
      ]
    }
  })
}
```

## Cart Edge Cases

### Empty Cart Handling

**Cart Page:**
```typescript
const CartPage = () => {
  const { cart } = useCart()
  
  if (!cart || cart.items.length === 0) {
    return (
      <div className="empty-cart">
        <h1>Your cart is empty</h1>
        <p>Start shopping to add items to your cart.</p>
        <button onClick={() => router.push('/shop')}>
          Browse Products
        </button>
      </div>
    )
  }
  
  return <CartWithItems cart={cart} />
}
```

### Product Goes Out of Stock

**Scenario**: Product in cart goes out of stock before checkout.

**Handling:**
```typescript
const checkCartInventory = async (cart) => {
  const outOfStockItems = []
  
  for (const item of cart.items) {
    const product = await getProduct(item.product.id)
    const available = getAvailableInventory(product, item.variant?.id)
    
    if (available < item.quantity) {
      outOfStockItems.push({
        item,
        available
      })
    }
  }
  
  if (outOfStockItems.length > 0) {
    // Show warning to user
    showOutOfStockWarning(outOfStockItems)
    
    // Optionally auto-remove or reduce quantities
    // await updateCartItems(...)
  }
  
  return outOfStockItems
}
```

### Product Deleted

**Scenario**: Product in cart is deleted by admin.

**Handling:**
```typescript
// When rendering cart, filter out deleted products
const validItems = cart.items.filter(item => {
  return item.product.exists  // Check if product still exists
})

if (validItems.length < cart.items.length) {
  // Remove invalid items
  await updateCart({ items: validItems })
  
  // Notify user
  showToast('Some items were removed as they are no longer available')
}
```

### Price Changed

**Scenario**: Product price changed after adding to cart.

**Display:**
```typescript
const CartItem = ({ item }) => {
  const currentProduct = useProduct(item.product.id)
  const currentPrice = currentProduct?.priceInUSD || 0
  const cartPrice = item.price  // Price when added to cart
  
  return (
    <div className="cart-item">
      <h3>{currentProduct.title}</h3>
      
      <div className="price">
        ${cartPrice.toFixed(2)}
        {cartPrice !== currentPrice && (
          <span className="price-note">
            (Current price: ${currentPrice.toFixed(2)})
          </span>
        )}
      </div>
    </div>
  )
}
```

## Cart Best Practices

### Performance

1. **Minimize API Calls**: Batch cart updates when possible
2. **Optimistic UI Updates**: Update UI before server confirms
3. **Cache Cart Data**: Store in React context to avoid re-fetching
4. **Debounced Saves**: Wait for user to stop modifying before saving

### User Experience

1. **Show Cart Updates**: Toast notification when item added
2. **Quick View**: Mini-cart sidebar instead of full page navigation
3. **Persistent Cart Icon**: Always visible with item count
4. **Save for Later**: Move items to wishlist instead of removing
5. **Restock Notifications**: Alert when out-of-stock items available

### Security

1. **Validate on Server**: Never trust client-side cart totals
2. **Re-calculate Totals**: Always recalculate on server before checkout
3. **Price Bounds Check**: Flag unusually low prices (possible exploit)
4. **Rate Limiting**: Prevent cart manipulation attacks

See [Payments and Checkout](05-payments-checkout.md) for converting carts to orders.
