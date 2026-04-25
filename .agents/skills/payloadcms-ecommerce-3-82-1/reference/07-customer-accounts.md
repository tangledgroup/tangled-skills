# Customer Accounts

Complete guide to user authentication, role management, account features, and address management in the Payload CMS ecommerce template v3.82.1.

## User Authentication

### Authentication System Overview

The template uses Payload's built-in authentication system with custom role-based access control.

**Authentication Features:**
- Email/password authentication
- JWT token-based sessions
- Role-based permissions (admin, customer)
- Password reset via email
- Account creation with auto-role assignment

### User Collection Configuration

**Schema (src/collections/Users/index.ts):**
```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  access: {
    admin: ({ req: { user } }) => checkRole(['admin'], user),
    create: publicAccess,           // Anyone can register
    delete: adminOnly,              // Only admins can delete users
    read: adminOrSelf,              // Users can read their own data
    unlock: adminOnly,
    update: adminOrSelf,            // Users can update their own data
  },
  admin: {
    group: 'Users',
    defaultColumns: ['name', 'email', 'roles'],
    useAsTitle: 'name',
  },
  auth: {
    tokenExpiration: 1209600,  // 14 days in seconds
  },
  fields: [
    { name: 'name', type: 'text' },
    {
      name: 'roles',
      type: 'select',
      access: {
        create: adminOnlyFieldAccess,
        read: adminOnlyFieldAccess,
        update: adminOnlyFieldAccess,
      },
      defaultValue: ['customer'],
      hasMany: true,
      hooks: {
        beforeChange: [ensureFirstUserIsAdmin],
      },
      options: [
        { label: 'admin', value: 'admin' },
        { label: 'customer', value: 'customer' }
      ]
    },
    // Join fields for related data
    {
      name: 'orders',
      type: 'join',
      collection: 'orders',
      on: 'customer'
    },
    {
      name: 'cart',
      type: 'join',
      collection: 'carts',
      on: 'customer'
    },
    {
      name: 'addresses',
      type: 'join',
      collection: 'addresses',
      on: 'customer'
    }
  ]
}
```

### User Roles

**Admin Role:**
- Full access to admin panel
- Can create/edit/delete all content
- Can manage all users, orders, products
- Can view unpublished drafts
- Can access transaction records

**Customer Role:**
- Frontend access only (no admin panel)
- Can view own orders and addresses
- Can update own profile
- Can create account and login
- Cannot access admin features

### First User Auto-Admin Hook

Ensures the first user created is automatically assigned admin role.

**Hook Implementation (src/collections/Users/hooks/ensureFirstUserIsAdmin.ts):**
```typescript
export const ensureFirstUserIsAdmin = async ({
  value,
  req
}: {
  value: string[]
  req: PayloadRequest
}): Promise<string[]> => {
  // Check if this is the first user
  const { docs: users } = await req.payload.query({
    collection: 'users',
    limit: 1,
    depth: 0
  })

  // If no users exist yet and roles not set, assign admin
  if (users.length === 0 && (!value || value.length === 0)) {
    return ['admin']
  }

  return value
}
```

**Behavior:**
1. First user created gets `['admin']` role automatically
2. Subsequent users get default `['customer']` role
3. Admin can change roles via admin panel

## Registration and Login

### User Registration

**Registration Form (src/components/forms/RegisterForm.tsx):**
```typescript
const RegisterForm = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password strength
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    try {
      // Create user account
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || 'Registration failed')
      }

      setSuccess(true)
      // Redirect to login or auto-login
      router.push('/login')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Create Account</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">Account created! Please login.</div>}

      <input
        type="text"
        placeholder="Full Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
      />

      <button type="submit">Create Account</button>

      <p>
        Already have an account?{' '}
        <Link href="/login">Login here</Link>
      </p>
    </form>
  )
}
```

### User Login

**Login Form (src/components/forms/LoginForm.tsx):**
```typescript
const LoginForm = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const response = await fetch('/api/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || 'Login failed')
      }

      const data = await response.json()

      // Store user in context/auth provider
      setUser(data.user)

      // Redirect to account page or previous location
      router.push('/account')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Login</h1>

      {error && (
        <div className="error">
          Invalid email or password
        </div>
      )}

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button type="submit">Login</button>

      <div className="links">
        <Link href="/forgot-password">Forgot password?</Link>
        <Link href="/create-account">Create an account</Link>
      </div>
    </form>
  )
}
```

### Authentication Context Provider

**Auth Provider (src/providers/Auth/index.tsx):**
```typescript
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      const token = getAuthToken()

      if (token) {
        try {
          const response = await fetch('/api/users/me', {
            headers: { Authorization: `JWT ${token}` }
          })

          if (response.ok) {
            const data = await response.json()
            setUser(data.user)
          }
        } catch (error) {
          console.error('Auth check failed:', error)
        }
      }

      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
    const response = await fetch('/api/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error)
    }

    const data = await response.json()
    setUser(data.user)
    return data.user
  }

  const logout = async () => {
    await fetch('/api/users/logout', {
      method: 'POST'
    })

    setUser(null)
    router.push('/')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
        isAdmin: user?.roles?.includes('admin')
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
```

## Password Management

### Password Reset Flow

**Step 1: Request Reset**

```typescript
// src/app/(app)/forgot-password/page.tsx
const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      await fetch('/api/users/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      setStatus('email_sent')
    } catch (error) {
      setStatus('error')
    }
  }

  if (status === 'email_sent') {
    return (
      <div>
        <h1>Check Your Email</h1>
        <p>We've sent you a password reset link.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Forgot Password</h1>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <button type="submit">Reset Password</button>
    </form>
  )
}
```

**Step 2: Reset Password**

```typescript
// src/app/(app)/reset-password/[token]/page.tsx
const ResetPasswordPage = ({ params }) => {
  const { token } = params
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      alert('Passwords do not match')
      return
    }

    try {
      await fetch('/api/users/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          newPassword: password
        })
      })

      router.push('/login?reset=success')
    } catch (error) {
      alert('Password reset failed')
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Reset Password</h1>

      <input
        type="password"
        placeholder="New Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
      />

      <button type="submit">Update Password</button>
    </form>
  )
}
```

### Password Requirements

**Enforced via validation:**
- Minimum 8 characters
- At least one letter
- At least one number (recommended)
- Payload handles password hashing automatically

## Account Dashboard

### Account Overview Page

```typescript
// src/app/(app)/(account)/account/page.tsx
const AccountPage = () => {
  const { user } = useAuth()

  if (!user) {
    router.push('/login')
    return null
  }

  return (
    <div className="account-dashboard">
      <h1>My Account</h1>

      <div className="account-info">
        <h2>Profile Information</h2>
        <p><strong>Name:</strong> {user.name}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Member since:</strong> {formatDate(user.createdAt)}</p>

        <Link href="/account/edit" className="button">
          Edit Profile
        </Link>
      </div>

      <div className="account-stats">
        <h2>Account Summary</h2>
        <div className="stat">
          <span className="value">{user.orders?.length || 0}</span>
          <span className="label">Total Orders</span>
        </div>
        <div className="stat">
          <span className="value">{user.addresses?.length || 0}</span>
          <span className="label">Saved Addresses</span>
        </div>
      </div>

      <div className="account-actions">
        <h2>Quick Links</h2>
        <ul>
          <li><Link href="/orders">Order History</Link></li>
          <li><Link href="/account/addresses">Addresses</Link></li>
          <li><Link href="/account/edit">Edit Profile</Link></li>
          <li><Link href="/logout">Logout</Link></li>
        </ul>
      </div>
    </div>
  )
}
```

### Order History Page

```typescript
// src/app/(app)/(account)/orders/page.tsx
const OrderHistoryPage = () => {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])

  useEffect(() => {
    const fetchOrders = async () => {
      const response = await fetch(`/api/orders?customer=${user.id}&sort=-createdAt`)
      const data = await response.json()
      setOrders(data.docs)
    }

    fetchOrders()
  }, [user])

  return (
    <div className="order-history">
      <h1>Order History</h1>

      {orders.length === 0 ? (
        <p>You haven't placed any orders yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Date</th>
              <th>Total</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {orders.map(order => (
              <tr key={order.id}>
                <td>{order.id}</td>
                <td>{formatDate(order.createdAt)}</td>
                <td>${order.total.toFixed(2)}</td>
                <td><StatusBadge status={order.status} /></td>
                <td>
                  <Link href={`/orders/${order.id}`}>View</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
```

## Address Management

### Addresses Collection

The ecommerce plugin adds an `addresses` collection for storing customer addresses.

**Schema:**
```typescript
interface Address {
  id: string
  customer: User           // Owner of the address
  
  line1: string
  line2?: string
  city: string
  state: string
  zip: string
  country: string
  
  label?: string           // e.g., "Home", "Work"
  isDefault?: boolean      // Default shipping address
  
  createdAt: string
  updatedAt: string
}
```

### Adding Addresses

**Address Form Component:**
```typescript
// src/components/forms/AddressForm.tsx
const AddressForm = ({ address, onSave }) => {
  const [formData, setFormData] = useState(address || {
    line1: '',
    line2: '',
    city: '',
    state: '',
    zip: '',
    country: 'US',
    label: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const response = await fetch('/api/addresses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          customer: user.id
        })
      })

      if (response.ok) {
        onSave()
      }
    } catch (error) {
      console.error('Failed to save address:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <input
          type="text"
          placeholder="Label (e.g., Home, Work)"
          value={formData.label}
          onChange={(e) => setFormData({ ...formData, label: e.target.value })}
        />
      </div>

      <div className="form-row">
        <input
          type="text"
          placeholder="Address Line 1"
          value={formData.line1}
          onChange={(e) => setFormData({ ...formData, line1: e.target.value })}
          required
        />
      </div>

      <div className="form-row">
        <input
          type="text"
          placeholder="Address Line 2 (optional)"
          value={formData.line2}
          onChange={(e) => setFormData({ ...formData, line2: e.target.value })}
        />
      </div>

      <div className="form-row">
        <input
          type="text"
          placeholder="City"
          value={formData.city}
          onChange={(e) => setFormData({ ...formData, city: e.target.value })}
          required
        />
      </div>

      <div className="form-row">
        <select
          value={formData.state}
          onChange={(e) => setFormData({ ...formData, state: e.target.value })}
          required
        >
          <option value="">Select State</option>
          {US_STATES.map(state => (
            <option key={state.code} value={state.code}>
              {state.name}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="ZIP Code"
          value={formData.zip}
          onChange={(e) => setFormData({ ...formData, zip: e.target.value })}
          required
        />
      </div>

      <div className="form-row">
        <select
          value={formData.country}
          onChange={(e) => setFormData({ ...formData, country: e.target.value })}
          required
        >
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="GB">United Kingdom</option>
          {/* Add more countries */}
        </select>
      </div>

      <button type="submit">
        {address ? 'Update Address' : 'Add Address'}
      </button>
    </form>
  )
}
```

### Address Management Page

```typescript
// src/app/(app)/(account)/account/addresses/page.tsx
const AddressesPage = () => {
  const { user } = useAuth()
  const [addresses, setAddresses] = useState([])
  const [showAddForm, setShowAddForm] = useState(false)

  useEffect(() => {
    const fetchAddresses = async () => {
      const response = await fetch(`/api/addresses?customer=${user.id}`)
      const data = await response.json()
      setAddresses(data.docs)
    }

    fetchAddresses()
  }, [user])

  const handleDelete = async (addressId) => {
    if (!confirm('Are you sure you want to delete this address?')) {
      return
    }

    await fetch(`/api/addresses/${addressId}`, {
      method: 'DELETE'
    })

    setAddresses(addresses.filter(a => a.id !== addressId))
  }

  const handleSetDefault = async (addressId) => {
    // Set this address as default, unset others
    for (const address of addresses) {
      await fetch(`/api/addresses/${address.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          isDefault: address.id === addressId
        })
      })
    }

    setAddresses(addresses.map(a => ({
      ...a,
      isDefault: a.id === addressId
    })))
  }

  return (
    <div className="addresses-page">
      <h1>Saved Addresses</h1>

      {showAddForm && (
        <div className="add-address-form">
          <h2>Add New Address</h2>
          <AddressForm
            onSave={() => {
              setShowAddForm(false)
              // Refresh addresses
              fetchAddresses()
            }}
          />
          <button onClick={() => setShowAddForm(false)}>Cancel</button>
        </div>
      )}

      <button onClick={() => setShowAddForm(true)} className="button">
        Add New Address
      </button>

      <div className="addresses-list">
        {addresses.length === 0 ? (
          <p>You haven't saved any addresses yet.</p>
        ) : (
          addresses.map(address => (
            <div key={address.id} className="address-card">
              {address.isDefault && (
                <span className="default-badge">Default</span>
              )}

              {address.label && (
                <h3>{address.label}</h3>
              )}

              <p>
                {address.line1}<br />
                {address.line2 && <span>{address.line2}<br /></span>}
                {address.city}, {address.state} {address.zip}<br />
                {address.country}
              </p>

              <div className="address-actions">
                {!address.isDefault && (
                  <button onClick={() => handleSetDefault(address.id)}>
                    Set as Default
                  </button>
                )}

                <button onClick={() => handleEdit(address)}>
                  Edit
                </button>

                <button onClick={() => handleDelete(address.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
```

## Access Control

### Role-Based Permissions

**Admin Access:**
```typescript
// Can access admin panel
access: {
  admin: ({ req: { user } }) => checkRole(['admin'], user)
}
```

**Customer Field Access:**
```typescript
// Customers can only see their own data
fields: [
  {
    name: 'orders',
    type: 'join',
    collection: 'orders',
    on: 'customer',
    admin: {
      allowCreate: false
    }
  }
]
```

### Protected Routes

**Route Protection Middleware:**
```typescript
// src/utilities/requireAuth.ts
export const requireAuth = async (req) => {
  const token = getAuthToken(req)

  if (!token) {
    return redirect('/login')
  }

  try {
    const response = await fetch('/api/users/me', {
      headers: { Authorization: `JWT ${token}` }
    })

    if (!response.ok) {
      return redirect('/login')
    }

    const data = await response.json()
    return data.user
  } catch (error) {
    return redirect('/login')
  }
}

// Usage in page component
const AccountPage = async () => {
  const user = await requireAuth()

  if (!user) {
    return null
  }

  return <AccountDashboard user={user} />
}
```

**Admin-Only Routes:**
```typescript
// src/utilities/requireAdmin.ts
export const requireAdmin = async (user) => {
  if (!user || !checkRole(['admin'], user)) {
    redirect('/unauthorized')
  }

  return user
}
```

## Session Management

### Token Expiration

**Default: 14 days**

```typescript
auth: {
  tokenExpiration: 1209600  // 14 days in seconds
}
```

**Custom Duration:**
```typescript
// 7 days
tokenExpiration: 604800

// 30 days
tokenExpiration: 2592000

// Never expire (not recommended)
tokenExpiration: null
```

### Token Refresh

**Auto-Refresh on API Calls:**
```typescript
// Include token in all authenticated requests
const fetchWithAuth = async (url, options = {}) => {
  const token = getAuthToken()

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `JWT ${token}`
    }
  })

  // Handle token expiration
  if (response.status === 401) {
    // Token expired or invalid
    redirect('/login')
  }

  return response
}
```

### Logout

**Logout Implementation:**
```typescript
const logout = async () => {
  // Call Payload logout endpoint
  await fetch('/api/users/logout', {
    method: 'POST'
  })

  // Clear local state
  setUser(null)
  clearAuthToken()

  // Redirect to homepage
  router.push('/')
}
```

## Best Practices

### Security

1. **Always validate on server**: Never trust client-side auth checks
2. **Use HTTPS**: Ensure all authentication traffic is encrypted
3. **Secure cookies**: Set HttpOnly and Secure flags on auth cookies
4. **Rate limiting**: Prevent brute force attacks on login endpoint
5. **Password hashing**: Payload handles this automatically - don't store plain passwords

### User Experience

1. **Clear error messages**: Tell users what went wrong without exposing sensitive info
2. **Remember me option**: Extend session duration for returning users
3. **Social login**: Consider adding OAuth providers (Google, Facebook)
4. **Email verification**: Require email confirmation on registration
5. **Account recovery**: Make password reset simple and accessible

### Performance

1. **Cache user data**: Store user info in React context to avoid repeated fetches
2. **Optimistic updates**: Update UI before server confirms for faster feel
3. **Lazy load**: Load order history and addresses on demand

See [Troubleshooting Guide](10-troubleshooting.md) for common authentication issues.
