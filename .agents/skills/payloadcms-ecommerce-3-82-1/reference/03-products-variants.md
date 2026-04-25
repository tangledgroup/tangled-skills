# Products and Variants

Complete guide to product catalog management, variant configuration, inventory tracking, and pricing strategies in the Payload CMS ecommerce template v3.82.1.

## Product Types

### Simple Products

Single SKU products without variations (e.g., books, electronics).

**Configuration:**
```typescript
// In admin panel: Products > Create New Product
{
  title: "Premium Notebook",
  slug: "premium-notebook",
  description: "High-quality leather notebook...",
  priceInUSD: 29.99,
  enableVariants: false,  // Disable variants for simple products
  inventory: 100,         // Single inventory count
  gallery: [
    { image: "notebook-front.jpg" },
    { image: "notebook-open.jpg" }
  ],
  categories: ["office-supplies"]
}
```

**Key Fields:**
- `enableVariants`: Set to `false`
- `inventory`: Single quantity for the product
- `priceInUSD`: Single price point
- `gallery`: Product images (no variant associations needed)

### Variable Products

Products with multiple variants based on attributes like size, color, material.

**Configuration:**
```typescript
{
  title: "Classic T-Shirt",
  slug: "classic-tshirt",
  description: "Comfortable cotton t-shirt...",
  priceInUSD: 24.99,        // Base/fallback price
  enableVariants: true,      // Enable variant support
  variantTypes: ["size", "color"],  // Selected variant types
  variants: {
    variants: [
      {
        variantOption: {
          size: "small",
          color: "red"
        },
        priceInUSD: 24.99,
        inventory: 50,
        sku: "TSHIRT-RED-S"
      },
      {
        variantOption: {
          size: "medium", 
          color: "red"
        },
        priceInUSD: 24.99,
        inventory: 100,
        sku: "TSHIRT-RED-M"
      }
    ]
  },
  gallery: [
    { 
      image: "tshirt-red.jpg",
      variantOption: { size: "any", color: "red" }  // Filter by color
    },
    {
      image: "tshirt-blue.jpg",
      variantOption: { size: "any", color: "blue" }
    }
  ]
}
```

## Variant Types and Options

### Creating Variant Types

Variant types are predefined attribute categories (Size, Color, Material).

**In Admin Panel:**
1. Navigate to **Variant Types** (added by ecommerce plugin)
2. Click **Create New Variant Type**
3. Enter type name: `Size`, `Color`, `Material`, etc.
4. Save

**Example Variant Types:**
```typescript
// Size variant type
{
  name: "size",
  label: "Size"
}

// Color variant type  
{
  name: "color",
  label: "Color"
}
```

### Creating Variant Options

Variant options are the specific values for each type (Small, Medium, Large).

**In Admin Panel:**
1. Navigate to **Variant Options** (added by ecommerce plugin)
2. Click **Create New Variant Option**
3. Select variant type (e.g., "Size")
4. Enter option value: `Small`, `Medium`, `Large`
5. Save

**Example Variant Options:**
```typescript
// Size options
[
  { label: "Small", variantType: "size" },
  { label: "Medium", variantType: "size" },
  { label: "Large", variantType: "size" },
  { label: "X-Large", variantType: "size" }
]

// Color options
[
  { label: "Red", variantType: "color" },
  { label: "Blue", variantType: "color" },
  { label: "Green", variantType: "color" }
]
```

### Configuring Product Variants

Once variant types and options exist, configure them on products.

**Step-by-Step:**

1. **Edit Product**: Navigate to Products > Edit Product
2. **Enable Variants**: Check "Enable Variants" toggle
3. **Select Variant Types**: Choose which types apply (Size, Color)
4. **Define Variant Combinations**:
   - System auto-generates all combinations
   - Example: 4 sizes × 3 colors = 12 variants
5. **Configure Each Variant**:
   - Set individual price (optional, inherits from base if not set)
   - Set inventory quantity
   - Generate or enter SKU
6. **Associate Gallery Images** (optional):
   - Link images to specific variant options
   - Example: Red t-shirt image shows when "Red" is selected

**Variant Configuration UI:**

```
Product: Classic T-Shirt
├── Enable Variants: ☑ Yes
├── Variant Types: [Size] [Color]
└── Variants (12 combinations):
    ├── Small + Red
    │   ├── Price: $24.99
    │   ├── Inventory: 50
    │   └── SKU: TSHIRT-RED-S
    ├── Small + Blue
    │   ├── Price: $24.99
    │   ├── Inventory: 45
    │   └── SKU: TSHIRT-BLUE-S
    ├── Medium + Red
    │   └── ...
    └── ...
```

## Pricing Configuration

### Base Price vs Variant Pricing

**Base Price (`priceInUSD`):**
- Fallback price if variant doesn't have individual price
- Displayed for simple products
- Used as default when creating variants

**Variant Price:**
- Overrides base price for specific variant
- Useful for size-based pricing (larger sizes cost more)
- Optional - inherits from base if not set

**Example: Size-Based Pricing**
```typescript
{
  title: "Premium Hoodie",
  priceInUSD: 59.99,  // Base price
  variants: {
    variants: [
      { 
        variantOption: { size: "small" },
        priceInUSD: 59.99  // Same as base
      },
      { 
        variantOption: { size: "large" },
        priceInUSD: 64.99  // Premium for larger size
      },
      { 
        variantOption: { size: "x-large" },
        priceInUSD: 69.99  // Extra premium
      }
    ]
  }
}
```

### Multi-Currency Pricing

The ecommerce plugin supports multiple currencies. Default is USD, but you can add more.

**Configuration (src/plugins/index.ts):**
```typescript
ecommercePlugin({
  currencies: ['USD', 'EUR', 'GBP'],  // Add supported currencies
  // ... other config
})
```

**Product Pricing per Currency:**
```typescript
{
  title: "International Product",
  priceInUSD: 29.99,
  priceInEUR: 27.99,
  priceInGBP: 24.99,
  // Variant pricing also supports per-currency
  variants: {
    variants: [
      {
        variantOption: { size: "large" },
        priceInUSD: 34.99,
        priceInEUR: 32.99,
        priceInGBP: 29.99
      }
    ]
  }
}
```

**Currency Display:**
- Frontend automatically uses user's locale or selected currency
- Cart and checkout show prices in current currency
- Orders store currency used at time of purchase

## Inventory Management

### Simple Product Inventory

Single inventory count for the entire product.

```typescript
{
  title: "Book Title",
  inventory: 250,  // Total available units
  enableVariants: false
}
```

**Inventory Flow:**
1. Customer adds item to cart (no immediate deduction)
2. Customer completes checkout
3. Order created, inventory decremented by order quantity
4. Low stock warnings configurable

### Variant Inventory

Each variant combination has independent inventory tracking.

```typescript
{
  title: "Sneakers",
  enableVariants: true,
  variants: {
    variants: [
      { 
        variantOption: { size: "9", color: "black" },
        inventory: 30  // Only 30 pairs in size 9 black
      },
      { 
        variantOption: { size: "10", color: "black" },
        inventory: 50  // 50 pairs in size 10 black
      },
      { 
        variantOption: { size: "9", color: "white" },
        inventory: 0   // Out of stock - should hide/disable on frontend
      }
    ]
  }
}
```

**Inventory Rules:**
- Each variant tracked independently
- Zero inventory = out of stock (frontend should disable selection)
- Negative inventory prevented by hooks
- Can manually adjust or integrate with external inventory systems

### Inventory Hooks

The ecommerce plugin includes hooks to manage inventory:

**After Order Creation:**
```typescript
// Automatically decrements inventory when order completes
hooks: {
  afterChange: [
    async ({ doc, req, operation }) => {
      if (operation === 'create' && doc._status === 'completed') {
        // Decrement inventory for each item in order
        for (const item of doc.items) {
          await decrementInventory({
            productId: item.product.id,
            variantId: item.variant?.id,
            quantity: item.quantity
          })
        }
      }
    }
  ]
}
```

**Low Stock Notifications:**
Configure threshold for low stock warnings in admin panel or via custom hooks.

## Product Gallery

### Simple Product Images

Upload multiple images to showcase the product.

```typescript
{
  title: "Camera",
  gallery: [
    { image: "camera-front.jpg" },
    { image: "camera-back.jpg" },
    { image: "camera-side.jpg" },
    { image: "camera-lifestyle.jpg" }
  ]
}
```

**Frontend Display:**
- Main image with thumbnail gallery
- Click to enlarge/lightbox
- Lazy loading for performance

### Variant-Specific Images

Associate images with specific variant options for accurate representation.

```typescript
{
  title: "Dress",
  enableVariants: true,
  variantTypes: ["color"],
  gallery: [
    { 
      image: "dress-red-front.jpg",
      variantOption: { color: "red" }  // Shows when red selected
    },
    { 
      image: "dress-red-back.jpg",
      variantOption: { color: "red" }
    },
    { 
      image: "dress-blue-front.jpg",
      variantOption: { color: "blue" }  // Shows when blue selected
    },
    { 
      image: "dress-blue-back.jpg",
      variantOption: { color: "blue" }
    }
  ]
}
```

**Filter Logic:**
- When customer selects "Red" variant, only red images display
- If no variant-specific image exists, fallback to unassociated images
- Admin can filter variant options when assigning images

### Image Optimization

Media collection includes automatic image optimization:

**Features:**
- Automatic resizing on upload
- Focal point selection for smart cropping
- Pre-defined sizes (thumbnail, medium, large)
- WebP format conversion
- Lazy loading support

**Configuration (src/collections/Media.ts):**
```typescript
{
  name: 'media',
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true
    },
    {
      name: 'focalPoint',
      type: 'point'
    },
    // Automatic image sizes configured here
  ]
}
```

## Product Categories

### Creating Categories

Organize products into taxonomy for filtering and navigation.

**In Admin Panel:**
1. Navigate to **Categories** > Create New Category
2. Enter category name: `Summer Collection`
3. Set slug: `summer-collection` (auto-generated from name)
4. Add description (optional)
5. Set parent category if hierarchical (optional)

**Category Structure:**
```typescript
// Flat structure
[
  { name: "Men", slug: "men" },
  { name: "Women", slug: "women" },
  { name: "Accessories", slug: "accessories" }
]

// Hierarchical structure
[
  { 
    name: "Clothing", 
    slug: "clothing",
    children: [
      { name: "Shirts", slug: "shirts" },
      { name: "Pants", slug: "pants" }
    ]
  }
]
```

### Assigning Products to Categories

**In Product Edit:**
1. Open product edit page
2. Find "Categories" field (sidebar)
3. Search and select categories
4. Save product

**Multiple Categories:**
```typescript
{
  title: "Leather Wallet",
  categories: ["accessories", "leather-goods", "mens", "gifts"]
}
```

**Frontend Usage:**
- Category filter in shop page
- Category archive pages (`/shop/clothing`)
- Breadcrumb navigation
- Related products by category

## Product Relationships

### Related Products

Manually curate related product recommendations.

**Configuration:**
```typescript
{
  title: "Running Shoes",
  relatedProducts: [
    "running-socks",      // By slug or ID
    "sports-water-bottle",
    "gym-backpack"
  ]
}
```

**Admin UI:**
- Relationship field with search
- Filter excludes current product
- Multi-select interface
- Displays related product titles and images

**Frontend Display:**
- "You May Also Like" section on product page
- Grid of 4-6 related products
- Clickable cards linking to product pages

### Category-Based Recommendations

Automatically suggest products from same categories.

**Implementation (frontend):**
```typescript
// Fetch products in same categories
const relatedProducts = await query('products', {
  where: {
    categories: { in: currentProduct.categories },
    id: { not_in: [currentProduct.id] }
  },
  limit: 4
})
```

## Product SEO

### Meta Fields

Each product includes SEO configuration tab.

**Fields:**
```typescript
meta: {
  title: "Classic T-Shirt | Store Name",      // Page title (60 chars max)
  description: "Comfortable cotton t-shirt...", // Meta description (160 chars max)
  image: "product-seo-image.jpg"              // Social share image
}
```

**Auto-Generation:**
- Meta title generated from product title if not set
- Meta description generated from product description
- Can manually override any field

### SEO Plugin Integration

The template includes @payloadcms/plugin-seo for enhanced SEO:

**Features:**
- Overview field shows search result preview
- Character count for title/description
- Social media preview (Open Graph)
- Schema.org structured data
- Canonical URL generation

**Configuration (src/collections/Products/index.ts):**
```typescript
{
  name: 'meta',
  label: 'SEO',
  fields: [
    OverviewField({
      titlePath: 'meta.title',
      descriptionPath: 'meta.description',
      imagePath: 'meta.image'
    }),
    MetaTitleField({ hasGenerateFn: true }),
    MetaImageField({ relationTo: 'media' }),
    MetaDescriptionField({}),
    PreviewField({
      hasGenerateFn: true,
      titlePath: 'meta.title',
      descriptionPath: 'meta.description'
    })
  ]
}
```

## Product Status and Publishing

### Draft vs Published

Products support draft/published workflow.

**Statuses:**
- `draft`: Visible only to admins, not in storefront
- `published`: Visible to all customers

**Workflow:**
1. Create product as draft
2. Configure all details (variants, images, pricing)
3. Preview using "Preview" button (opens draft version)
4. Click "Publish" when ready
5. Product appears in storefront

### Live Preview

Edit product and see changes in real-time on storefront.

**How It Works:**
1. Open product in admin panel
2. Click "Live Preview" button
3. Split view shows admin panel + storefront
4. Edit product fields
5. Storefront updates instantly (SSR)
6. Click "Publish" when satisfied

**Configuration:**
```typescript
admin: {
  livePreview: {
    url: ({ data, req }) => 
      generatePreviewPath({
        slug: data?.slug,
        collection: 'products',
        req
      })
  }
}
```

## Product Schema Reference

### Complete Product Structure

```typescript
interface Product {
  // Core fields
  id: string
  title: string
  slug: string
  description: RichTextValue
  _status: 'draft' | 'published'
  createdAt: string
  updatedAt: string
  
  // Pricing
  priceInUSD: number
  priceInEUR?: number  // If multi-currency enabled
  priceInGBP?: number
  
  // Variants
  enableVariants: boolean
  variantTypes: VariantType[]  // Array of variant type IDs
  variants: {
    variants: Variant[]
  }
  
  // Inventory (for simple products)
  inventory?: number
  
  // Media
  gallery: {
    image: Media
    variantOption?: VariantOption  // Optional variant filter
  }[]
  
  // Organization
  categories: Category[]
  relatedProducts: Product[]
  
  // Content
  layout: LayoutBlock[]  // Layout builder blocks
  
  // SEO
  meta: {
    title?: string
    description?: string
    image?: Media
  }
}
```

### Variant Structure

```typescript
interface Variant {
  variantOption: {
    [variantTypeName]: string  // e.g., { size: "large", color: "red" }
  }
  priceInUSD?: number  // Optional override
  priceInEUR?: number
  inventory: number
  sku?: string
}
```

## Best Practices

### Product Creation

1. **Use Descriptive Titles**: Include key attributes (e.g., "Men's Cotton T-Shirt" not just "T-Shirt")
2. **Write Rich Descriptions**: Use Lexical editor for formatted content with images, lists, etc.
3. **Upload Multiple Images**: Show product from multiple angles, lifestyle shots
4. **Configure Variants Carefully**: Test all combinations before publishing
5. **Set Accurate Inventory**: Prevent overselling with correct stock levels
6. **Optimize SEO**: Fill meta fields for each product
7. **Assign Categories**: Make products discoverable through filtering

### Variant Management

1. **Limit Variant Types**: 2-3 types maximum (too many = combinatorial explosion)
2. **Use Meaningful Option Labels**: "Small/Medium/Large" not "S/M/L"
3. **Generate SKUs Systematically**: Use pattern like `PRODUCT-VARIANT-SIZE`
4. **Track Inventory Per Variant**: Essential for accurate stock management
5. **Price Variants Appropriately**: Larger sizes/special colors may cost more

### Image Optimization

1. **Use High-Quality Images**: Minimum 800px width for product photos
2. **Consistent Aspect Ratio**: All gallery images same ratio (e.g., 4:3 or 1:1)
3. **Set Focal Points**: Ensure important part of image stays visible when cropped
4. **Compress Before Upload**: Use tools like TinyPNG to reduce file size
5. **Add Alt Text**: Describe image content for accessibility

## Common Issues

### Variants Not Showing

**Symptoms**: Variant selector doesn't appear on product page.

**Solutions:**
1. Verify `enableVariants` is set to `true`
2. Check that variant types are selected
3. Ensure variant options exist for selected types
4. Confirm variants have been created (not just types)

### Gallery Images Not Filtering

**Symptoms**: All images show regardless of selected variant.

**Solutions:**
1. Verify `variantOption` is set on gallery items
2. Check variant option matches selected variant type
3. Ensure image is associated with correct variant option ID

### Inventory Not Updating

**Symptoms**: Stock count doesn't decrease after order.

**Solutions:**
1. Check ecommerce plugin inventory hooks are enabled
2. Verify order status is "completed" (inventory decrements on completion)
3. Check for custom hooks that might override default behavior

See [Troubleshooting Guide](10-troubleshooting.md) for more solutions.
