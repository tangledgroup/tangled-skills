# Troubleshooting Guide

Comprehensive solutions to common errors, debugging techniques, and problem resolution for the Payload CMS ecommerce template v3.82.1.

## Payment Issues

### Stripe Webhooks Not Working

**Symptoms:**
- Payment succeeds in UI but order not created
- No transaction record appears
- Customer sees success but receives no confirmation email

**Diagnosis:**
```bash
# Check webhook endpoint accessibility
curl -I https://your-domain.com/api/payments/stripe/webhooks

# Should return 200 or 405 (method not allowed is OK for GET)
```

**Solutions:**

1. **Verify Webhook Secret:**
   ```env
   # Ensure this matches Stripe Dashboard exactly
   STRIPE_WEBHOOKS_SIGNING_SECRET=whsec_your-actual-secret
   ```

2. **Check Event Selection in Stripe:**
   - Navigate to Stripe Dashboard > Developers > Webhooks
   - Verify these events are selected:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `charge.succeeded`
     - `charge.failed`

3. **Inspect Failed Deliveries:**
   - Stripe Dashboard > Webhooks > Recent Events
   - Click failed webhooks to see error details
   - Common errors: Connection timeout, 404, signature verification failed

4. **Local Development with ngrok:**
   ```bash
   # Install ngrok
   brew install ngrok  # macOS
   sudo snap install ngrok  # Linux

   # Start tunnel
   ngrok http 3000

   # Copy forward URL and use in Stripe Dashboard
   # Example: https://abc123.ngrok.io/api/payments/stripe/webhooks
   ```

5. **Enable Webhook Logging:**
   ```typescript
   // In webhook handler
   console.log('Webhook received:', event.type)
   console.log('Event data:', JSON.stringify(event.data, null, 2))
   ```

### Payment Fails Silently

**Symptoms:**
- No error message displayed
- Payment button clicks but nothing happens
- Cart not cleared after "successful" payment

**Diagnosis:**
```javascript
// Check browser console for errors
console.log('Payment processing...')

// Check Network tab for failed requests
```

**Solutions:**

1. **Verify Publishable Key:**
   ```env
   # Must start with pk_test_ (dev) or pk_live_ (prod)
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-key-here
   ```

2. **Check Stripe Elements Initialization:**
   ```typescript
   const stripe = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

   if (!stripe) {
     console.error('Stripe failed to load - check publishable key')
   }
   ```

3. **Add Error Handling:**
   ```typescript
   const { error } = await stripe.confirmCardPayment(clientSecret, {
     payment_method: { card: cardElement }
   })

   if (error) {
     console.error('Payment error:', error)
     showToast(error.message)
   }
   ```

4. **Test with Stripe Test Card:**
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date (12/25)
   - CVC: Any 3 digits (123)
   - ZIP: Any 5 digits (12345)

### Card Declined Error

**Symptoms:**
- "Your card was declined" message
- Payment intent status is `requires_payment_method`

**Causes:**
1. Invalid card number
2. Insufficient funds
3. Card expired
4. Bank fraud protection
5. Test card used in live mode (or vice versa)

**Solutions:**

1. **Verify Test vs Live Mode:**
   ```env
   # Development - use test keys
   STRIPE_SECRET_KEY=sk_test_...
   
   # Production - use live keys
   STRIPE_SECRET_KEY=sk_live_...
   ```

2. **Handle Decline Gracefully:**
   ```typescript
   if (error.type === 'card_error') {
     showToast('Your card was declined. Please try a different payment method.')
   }
   ```

3. **Check 3D Secure Requirements:**
   - Some cards require 3D Secure authentication
   - Use test card `4000 0025 0000 3155` to test 3D Secure flow

## Cart Issues

### Cart Not Persisting

**Symptoms:**
- Cart empties on page refresh
- Items disappear when navigating between pages
- Guest cart lost after browser close

**Solutions:**

1. **Check localStorage:**
   ```typescript
   // Verify cart ID is stored
   console.log('Cart ID:', localStorage.getItem('cartId'))

   // Should contain a valid cart ID string
   ```

2. **Verify Cart Provider:**
   ```typescript
   // Ensure app is wrapped in CartProvider
   <CartProvider>
     <AuthProvider>
       <App />
     </AuthProvider>
   </CartProvider>
   ```

3. **Check Auth State:**
   ```typescript
   // For authenticated users, cart should link to user
   if (user.isAuthenticated) {
     const userCart = await fetch(`/api/carts?customer=${user.id}`)
   }
   ```

4. **Debug Cart Sync:**
   ```typescript
   const addToCart = async (item) => {
     console.log('Adding to cart:', item)
     
     const response = await fetch(`/api/carts/${cartId}/items`, {
       method: 'POST',
       body: JSON.stringify(item)
     })

     console.log('Response:', response.status)
     
     if (!response.ok) {
       const error = await response.json()
       console.error('Cart update failed:', error)
     }
   }
   ```

### Inventory Validation Fails

**Symptoms:**
- "Out of stock" error when adding to cart
- Cannot increase quantity beyond available inventory

**Diagnosis:**
```typescript
// Check product inventory
const product = await getProduct(productId)

console.log('Available inventory:', product.inventory)
console.log('Variant inventory:', product.variants?.variants.find(v => v.id === variantId)?.inventory)
```

**Solutions:**

1. **Verify Inventory Count:**
   - Admin Panel > Products > Edit Product
   - Check "Inventory" field is set correctly
   - For variants, check each variant's inventory

2. **Check Cart Item Total:**
   ```typescript
   // Sum all quantities in cart for this product
   const totalInCart = cart.items
     .filter(item => item.product.id === productId)
     .reduce((sum, item) => sum + item.quantity, 0)

   if (totalInCart + newQuantity > availableInventory) {
     showError(`Only ${availableInventory - totalInCart} more available`)
   }
   ```

3. **Restock Product:**
   ```typescript
   // In admin panel or via API
   await payload.update({
     collection: 'products',
     id: productId,
     data: { inventory: 100 }  // Set new quantity
   })
   ```

## Authentication Issues

### Login Fails

**Symptoms:**
- "Invalid email or password" error
- Login form submits but no response
- User created but cannot login

**Solutions:**

1. **Verify User Exists:**
   ```typescript
   // Check in admin panel
   // Admin > Users > Verify user exists with correct email
   ```

2. **Check Password Hashing:**
   ```typescript
   // Payload handles this automatically
   // If you manually created user, ensure password is hashed
   ```

3. **Debug Login Request:**
   ```typescript
   const response = await fetch('/api/users/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email, password })
   })

   console.log('Login response:', response.status)
   
   if (!response.ok) {
     const data = await response.json()
     console.error('Login error:', data.error)
   }
   ```

4. **Reset Password:**
   - Use "Forgot Password" flow
   - Verify email sent to correct address
   - Click reset link within expiration time

### User Session Expires

**Symptoms:**
- Automatically logged out after X minutes
- Need to re-login frequently
- Cart lost after session timeout

**Solutions:**

1. **Check Token Expiration:**
   ```typescript
   // In Users collection config
   auth: {
     tokenExpiration: 1209600  // 14 days in seconds
   }
   ```

2. **Implement Remember Me:**
   ```typescript
   // Store token in persistent cookie or localStorage
   document.cookie = `payload-token=${token}; max-age=31536000; path=/; Secure; SameSite=Lax`
   ```

3. **Auto-Refresh Token:**
   ```typescript
   // Before token expires, refresh it
   const refreshToken = async () => {
     const response = await fetch('/api/users/refresh')
     const data = await response.json()
     setToken(data.token)
   }

   // Call every hour if user is active
   setInterval(refreshToken, 3600000)
   ```

### Role Access Denied

**Symptoms:**
- Cannot access admin panel
- "Unauthorized" error on protected pages
- Customer trying to access admin-only features

**Solutions:**

1. **Verify User Role:**
   ```typescript
   // Admin Panel > Users > Edit User
   // Check "Roles" field includes 'admin' for admin access
   ```

2. **Check Access Control:**
   ```typescript
   // In collection config
   access: {
     admin: ({ req: { user } }) => {
       console.log('Admin check:', user?.roles)
       return checkRole(['admin'], user)
     }
   }
   ```

3. **First User Auto-Admin:**
   ```typescript
   // Hook should assign admin role to first user
   // If not working, manually set role in admin panel
   ```

## Database Issues

### MongoDB Connection Failed

**Symptoms:**
- Application won't start
- "MongoServerError: connect ECONNREFUSED"
- Timeout errors on database operations

**Solutions:**

1. **Verify MongoDB is Running:**
   ```bash
   # Check local MongoDB
   ps aux | grep mongod

   # Or check Docker container
   docker ps | grep mongo
   ```

2. **Check Connection String:**
   ```env
   # Local development
   DATABASE_URL=mongodb://127.0.0.1:27017/ecommerce

   # MongoDB Atlas
   DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/ecommerce?retryWrites=true&w=majority

   # Docker
   DATABASE_URL=mongodb://mongo:27017/ecommerce
   ```

3. **Test Connection:**
   ```bash
   # Using mongosh
   mongosh "mongodb://127.0.0.1:27017/ecommerce"

   # Should connect without errors
   ```

4. **Firewall/Network:**
   - Ensure port 27017 is accessible
   - Check MongoDB Atlas IP whitelist
   - Verify VPC peering if using AWS/GCP

### Migration Errors

**Symptoms:**
- "Collection already exists" error
- Schema mismatch errors
- Migration fails partway through

**Solutions:**

1. **Reset Database (Development Only):**
   ```bash
   # Drop and recreate database
   mongosh
   > use ecommerce
   > db.dropDatabase()
   > exit

   # Restart application - will recreate schema
   pnpm dev
   ```

2. **Manual Migration:**
   ```bash
   # Create migration file
   pnpm payload migrate:create

   # Review generated SQL/operations
   # Run migration
   pnpm payload migrate
   ```

3. **Check Migration Lock:**
   ```typescript
   // If migration is stuck, check payload_migrations collection
   // May need to manually clear lock
   ```

## Build and Deployment Issues

### TypeScript Errors on Build

**Symptoms:**
- `pnpm build` fails with type errors
- Missing type definitions
- Payload types not generated

**Solutions:**

1. **Generate Types First:**
   ```bash
   pnpm generate:types
   pnpm build
   ```

2. **Check payload-types.ts:**
   ```typescript
   // Ensure file exists and is up to date
   // Regenerate if collections changed
   pnpm generate:types
   ```

3. **Common Type Errors:**
   ```typescript
   // Error: Property does not exist on type
   // Solution: Check field names match collection schema

   // Error: Type is not assignable
   // Solution: Verify data types match field definitions
   ```

### Environment Variables Not Loading

**Symptoms:**
- "Missing environment variable" errors
- Undefined values in production
- Different behavior between dev and prod

**Solutions:**

1. **Verify .env File:**
   ```bash
   # Check file exists
   ls -la .env

   # Check syntax (no quotes around values unless needed)
   cat .env
   ```

2. **Next.js Public Variables:**
   ```env
   # Must start with NEXT_PUBLIC_ for client access
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
   
   # Server-only variables (don't need prefix)
   STRIPE_SECRET_KEY=sk_test_...
   ```

3. **Vercel Environment Variables:**
   - Settings > Environment Variables
   - Add each variable
   - Deploy to apply changes

4. **Docker Environment:**
   ```yaml
   # In docker-compose.yml
   environment:
     - DATABASE_URL=${DATABASE_URL}
     - PAYLOAD_SECRET=${PAYLOAD_SECRET}
   ```

### Image Upload Fails

**Symptoms:**
- 500 error when uploading images
- Images not appearing after upload
- "ENOENT: no such file or directory"

**Solutions:**

1. **Create Upload Directory:**
   ```bash
   mkdir -p ./uploads/media
   chmod 755 ./uploads/media
   ```

2. **Check Sharp Installation:**
   ```bash
   # Install sharp for image processing
   pnpm add sharp

   # Add to payload.config.ts
   import sharp from 'sharp'
   
   export default buildConfig({
     sharp,
     // ... rest of config
   })
   ```

3. **Verify Storage Configuration:**
   ```typescript
   // For local storage
   {
     name: 'media',
     upload: {
       staticDir: 'uploads',
       mimeTypes: ['image/*']
     }
   }

   // For cloud storage (Vercel Blob, S3)
   // Configure storage adapter in plugins
   ```

## Performance Issues

### Slow Page Loads

**Diagnosis:**
```bash
# Check bundle size
pnpm build
ls -lh .next/static/js/

# Profile with Next.js analytics
npm i @vercel/analytics
```

**Solutions:**

1. **Enable Image Lazy Loading:**
   ```typescript
   <Image
     src={imageUrl}
     alt={alt}
     loading="lazy"  // Default in Next.js 13+
   />
   ```

2. **Code Split Large Components:**
   ```typescript
   const HeavyComponent = dynamic(
     () => import('@/components/HeavyComponent'),
     { ssr: false }
   )
   ```

3. **Optimize Database Queries:**
   ```typescript
   // Use depth parameter to limit nested queries
   const products = await payload.query({
     collection: 'products',
     depth: 1,  // Only fetch 1 level of relationships
     limit: 20
   })
   ```

4. **Enable Caching:**
   ```typescript
   // Cache product listings
   export const revalidate = 3600  // Revalidate every hour
   ```

### High Memory Usage

**Symptoms:**
- Application crashes with "OutOfMemory" error
- Server becomes unresponsive
- Slow response times under load

**Solutions:**

1. **Increase Node Memory:**
   ```bash
   # In package.json scripts
   "dev": "NODE_OPTIONS='--max-old-space-size=4096' next dev",
   "build": "NODE_OPTIONS='--max-old-space-size=8000' next build"
   ```

2. **Optimize Payload Queries:**
   ```typescript
   // Don't fetch unnecessary fields
   const products = await payload.query({
     collection: 'products',
     overrideAccess: false,
     depth: 0,  // Minimize nested queries
     select: ['title', 'slug', 'priceInUSD', 'gallery']  // Only needed fields
   })
   ```

3. **Use PM2 Memory Limits:**
   ```javascript
   // ecosystem.config.js
   {
     max_memory_restart: '500M'  // Restart if exceeds 500MB
   }
   ```

## Debugging Techniques

### Enable Verbose Logging

**Payload Logging:**
```typescript
// In payload.config.ts
export default buildConfig({
  logger: {
    level: 'info'  // or 'debug' for more detail
  }
})
```

**Next.js Logging:**
```typescript
// In API routes
export async function GET(request: Request) {
  console.log('API request received:', request.url)
  console.log('Headers:', Object.keys((await request.headers()).getAll()))
  
  try {
    // ... handler code
  } catch (error) {
    console.error('API error:', error)
    throw error
  }
}
```

### Browser DevTools

**Network Tab:**
- Inspect failed API requests
- Check response status and body
- Verify request headers (Authorization, Content-Type)

**Application Tab:**
- Check localStorage for cart ID and auth tokens
- Inspect cookies for session data
- Clear storage to test fresh state

**Console Tab:**
- Look for JavaScript errors
- Check Stripe SDK initialization
- Monitor custom console.log statements

### Remote Debugging

**Vercel Logs:**
```bash
# Stream logs in real-time
vercel logs

# View specific deployment
vercel logs --deployment=your-deployment-url
```

**PM2 Logs:**
```bash
# View live logs
pm2 logs

# View last 100 lines
pm2 logs --lines 100

# Monitor specific app
pm2 monit
```

## Common Error Messages

### "Payload is not defined"

**Cause**: Import error or configuration issue

**Solution:**
```typescript
// Correct import
import { buildConfig } from 'payload'
import payload from 'payload'
```

### "Collection not found"

**Cause**: Collection slug mismatch or plugin not loaded

**Solution:**
- Verify collection exists in `payload.config.ts`
- Check ecommerce plugin is included in plugins array
- Ensure collection slug matches exactly (case-sensitive)

### "Cannot read property of undefined"

**Cause**: Accessing nested property on undefined value

**Solution:**
```typescript
// Use optional chaining
const price = product?.variants?.variants[0]?.priceInUSD || 0

// Or check before accessing
if (product && product.variants && product.variants.variants.length > 0) {
  const price = product.variants.variants[0].priceInUSD
}
```

## Getting Help

### Official Resources

1. **Payload Documentation**: https://payloadcms.com/docs
2. **Ecommerce Plugin Docs**: https://payloadcms.com/docs/ecommerce/plugin
3. **Stripe Documentation**: https://stripe.com/docs
4. **Next.js Documentation**: https://nextjs.org/docs

### Community Support

1. **Payload Discord**: https://discord.com/invite/payload
2. **GitHub Discussions**: https://github.com/payloadcms/payload/discussions
3. **Stack Overflow**: Tag with `payload-cms`

### Before Asking for Help

1. Check this troubleshooting guide
2. Search existing issues on GitHub
3. Review official documentation
4. Prepare minimal reproduction case
5. Include error messages and relevant code snippets
