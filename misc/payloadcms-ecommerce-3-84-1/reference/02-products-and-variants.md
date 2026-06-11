# Products and Variants

## Product Collection

Products are the core catalog entity. The template overrides the default product collection to add custom fields, layout blocks, gallery, and SEO integration.

### Default Product Fields

The ecommerce plugin provides these fields by default:

- `title` — Product name (text, required)
- `enableVariants` — Boolean to toggle variant support per product
- `variantTypes` — Relationship to variant types (shown when variants enabled)
- `priceInUSD` — Base price in cents (when no variants)
- `inventory` — Stock quantity tracking
- Prices per supported currency

### Template Product Override

```typescript
export const ProductsCollection: CollectionOverride = ({ defaultCollection }) => ({
  ...defaultCollection,
  admin: {
    defaultColumns: ['title', 'enableVariants', '_status', 'variants.variants'],
    livePreview: {
      url: ({ data, req }) => generatePreviewPath({
        slug: data?.slug,
        collection: 'products',
        req,
      }),
    },
    useAsTitle: 'title',
  },
  defaultPopulate: {
    title: true, slug: true, variantOptions: true, variants: true,
    enableVariants: true, gallery: true, priceInUSD: true, inventory: true, meta: true,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    {
      type: 'tabs',
      tabs: [
        {
          label: 'Content',
          fields: [
            { name: 'description', type: 'richText', editor: lexicalEditor({ /* ... */ }) },
            {
              name: 'gallery',
              type: 'array',
              minRows: 1,
              fields: [
                { name: 'image', type: 'upload', relationTo: 'media', required: true },
                {
                  name: 'variantOption',
                  type: 'relationship',
                  relationTo: 'variantOptions',
                  admin: { condition: (data) => data?.enableVariants === true },
                  filterOptions: ({ data }) => {
                    // Filter to only options matching selected variant types
                    const ids = data?.variantTypes?.map((item: any) =>
                      typeof item === 'object' && item?.id ? item.id : item
                    )
                    return { variantType: { in: ids || [] } }
                  },
                },
              ],
            },
            {
              name: 'layout',
              type: 'blocks',
              blocks: [CallToAction, Content, MediaBlock],
            },
          ],
        },
        {
          label: 'Product Details',
          fields: [
            ...defaultCollection.fields,
            {
              name: 'relatedProducts',
              type: 'relationship',
              relationTo: 'products',
              hasMany: true,
              filterOptions: ({ id }) => id ? { id: { not_in: [id] } } : { id: { exists: true } },
            },
          ],
        },
        {
          name: 'meta',
          label: 'SEO',
          fields: [OverviewField(), MetaTitleField(), MetaImageField(), MetaDescriptionField(), PreviewField()],
        },
      ],
    },
    { name: 'categories', type: 'relationship', relationTo: 'categories', hasMany: true,
      admin: { position: 'sidebar', sortOptions: 'title' } },
    slugField(),
  ],
})
```

## Variants System

The variants system uses three collections working together:

### Variant Types

Define the dimensions of variation:

```
Variant Types collection:
- name (text) — e.g., "Size", "Color", "Material"
```

Example types: Size, Color, Storage Capacity.

### Variant Options

Define specific values within each type:

```
Variant Options collection:
- variantType (relationship to variantTypes)
- label (text) — e.g., "Large", "Red", "128GB"
```

Options are filtered by their parent type in the admin UI.

### Variants

Combine options into sellable variants:

```
Variants collection:
- product (relationship to products)
- variantOptions (hasMany relationship to variantOptions)
- price — Per-currency pricing for this variant
- inventory — Stock level for this variant
```

Each variant links one option from each selected type. For a product with Size and Color types, variants might be: Size=Large + Color=Red, Size=Small + Color=Blue, etc.

## Gallery with Variant Mapping

The gallery field supports mapping images to specific variants:

```typescript
{
  name: 'gallery',
  type: 'array',
  fields: [
    { name: 'image', type: 'upload', relationTo: 'media', required: true },
    {
      name: 'variantOption',
      type: 'relationship',
      relationTo: 'variantOptions',
      admin: { condition: (data) => data?.enableVariants === true },
    },
  ],
}
```

This allows showing different product images based on the selected variant option (e.g., different color swatches).

## Pricing Per Currency

Products and variants support per-currency pricing. When multiple currencies are configured, each product/variant stores prices for every supported currency:

```typescript
// Prices stored as cents
{
  priceInUSD: 2999,     // $29.99
  priceInEUR: 2799,     // €27.99
  priceInGBP: 2399,     // £23.99
}
```

The plugin provides `pricesField()` for generating currency-specific price fields automatically.

## Inventory Management

When `inventory: true` (default), products and variants track stock levels:

- Products without variants: single `inventory` field
- Products with variants: each variant has its own `inventory` field
- The checkout flow validates inventory before confirming orders
- Custom validation can enforce additional rules via `products.validation`

## Product Drafts and Publishing

Products use Payload's versioning system with drafts:

- Products are created as drafts by default
- Admin users can preview drafts via the live preview URL
- Only published products appear in the storefront
- On-demand revalidation updates the Next.js cache when products are published

## Categories

Categories provide product grouping and filtering:

```typescript
{
  name: 'categories',
  type: 'relationship',
  relationTo: 'categories',
  hasMany: true,
  admin: { position: 'sidebar', sortOptions: 'title' },
}
```

Products can belong to multiple categories. The shop page uses categories for filtering the product catalog.
