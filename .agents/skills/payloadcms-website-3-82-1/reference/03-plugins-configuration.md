# Plugins Configuration

## Plugin Setup Overview

All plugins are configured in `src/plugins/index.ts` and registered in the Payload config via the `plugins` array. The template uses five official Payload plugins.

```typescript
import { formBuilderPlugin } from '@payloadcms/plugin-form-builder'
import { nestedDocsPlugin } from '@payloadcms/plugin-nested-docs'
import { redirectsPlugin } from '@payloadcms/plugin-redirects'
import { seoPlugin } from '@payloadcms/plugin-seo'
import { searchPlugin } from '@payloadcms/plugin-search'
import type { Plugin } from 'payload'

export const plugins: Plugin[] = [
  redirectsPlugin({ ... }),
  nestedDocsPlugin({ ... }),
  seoPlugin({ ... }),
  formBuilderPlugin({ ... }),
  searchPlugin({ ... }),
]
```

## SEO Plugin

The SEO plugin provides admin-managed meta tags for pages and posts.

### Configuration

```typescript
seoPlugin({
  generateTitle,
  generateURL,
})
```

### Generate Functions

The plugin uses generate functions to auto-populate SEO fields from document data:

```typescript
const generateTitle: GenerateTitle<Post | Page> = ({ doc }) => {
  return doc?.title ? `${doc.title} | Payload Website Template` : 'Payload Website Template'
}

const generateURL: GenerateURL<Post | Page> = ({ doc }) => {
  const url = getServerSideURL()
  return doc?.slug ? `${url}/${doc.slug}` : url
}
```

### SEO Fields in Collections

The SEO plugin exposes field components that are placed in a dedicated "SEO" tab:

```typescript
{
  name: 'meta',
  label: 'SEO',
  fields: [
    OverviewField({
      titlePath: 'meta.title',
      descriptionPath: 'meta.description',
      imagePath: 'meta.image',
    }),
    MetaTitleField({ hasGenerateFn: true }),
    MetaImageField({ relationTo: 'media' }),
    MetaDescriptionField({}),
    PreviewField({
      hasGenerateFn: true,
      titlePath: 'meta.title',
      descriptionPath: 'meta.description',
    }),
  ],
}
```

- `OverviewField` — Summary card showing title, description, and image preview
- `MetaTitleField` — SEO title with auto-generate button (when `hasGenerateFn: true`)
- `MetaImageField` — Open Graph image selection from Media collection
- `MetaDescriptionField` — Meta description text area
- `PreviewField` — Live OG preview with auto-generate URL

### Frontend Meta Generation

The template uses a `generateMeta` utility to build Next.js Metadata from Payload documents:

```typescript
// Conceptual pattern from src/utilities/generateMeta.ts
export function generateMeta({ doc }: { doc: Page | Post }): Metadata {
  // Extracts meta.title, meta.description, meta.image from document
  // Builds proper Open Graph and Twitter card metadata
}
```

## Search Plugin

The search plugin indexes specified collections for full-text search.

### Configuration

```typescript
searchPlugin({
  collections: ['posts'],
  beforeSync: beforeSyncWithSearch,
  searchOverrides: {
    fields: ({ defaultFields }) => [
      ...defaultFields,
      ...searchFields,
    ],
  },
})
```

### Before Sync Hook

The `beforeSync` hook transforms the original document into the search index format:

```typescript
export const beforeSyncWithSearch: BeforeSync = async ({ req, originalDoc, searchDoc }) => {
  const { slug, id, categories, title, meta } = originalDoc

  const modifiedDoc: DocToSync = {
    ...searchDoc,
    slug,
    meta: {
      ...meta,
      title: meta?.title || title,
      image: meta?.image?.id || meta?.image,
      description: meta?.description,
    },
    categories: [],
  }

  // Populate categories with title data
  if (categories && Array.isArray(categories) && categories.length > 0) {
    for (const category of categories) {
      const doc = await req.payload.findByID({
        collection: 'categories',
        id: typeof category === 'object' ? category.id : category,
        disableErrors: true,
        depth: 0,
        select: { title: true },
      })
      if (doc) {
        modifiedDoc.categories.push({
          relationTo: 'categories',
          categoryID: String(doc.id),
          title: doc.title,
        })
      }
    }
  }

  return modifiedDoc
}
```

### Search Field Overrides

Custom fields added to the search collection:

```typescript
export const searchFields: Field[] = [
  { name: 'slug', type: 'text', index: true, admin: { readOnly: true } },
  {
    name: 'meta',
    label: 'Meta',
    type: 'group',
    index: true,
    admin: { readOnly: true },
    fields: [
      { name: 'title', type: 'text', label: 'Title' },
      { name: 'description', type: 'text', label: 'Description' },
      { name: 'image', type: 'upload', relationTo: 'media', label: 'Image' },
    ],
  },
  {
    name: 'categories',
    label: 'Categories',
    type: 'array',
    admin: { readOnly: true },
    fields: [
      { name: 'relationTo', type: 'text' },
      { name: 'categoryID', type: 'text' },
      { name: 'title', type: 'text' },
    ],
  },
]
```

## Redirects Plugin

The redirects plugin manages URL redirects from the admin panel.

### Configuration

```typescript
redirectsPlugin({
  collections: ['pages', 'posts'],
  overrides: {
    fields: ({ defaultFields }) => {
      return defaultFields.map((field) => {
        if ('name' in field && field.name === 'from') {
          return {
            ...field,
            admin: {
              description: 'You will need to rebuild the website when changing this field.',
            },
          }
        }
        return field
      })
    },
    hooks: {
      afterChange: [revalidateRedirects],
    },
  },
})
```

### Revalidation Hook

```typescript
export const revalidateRedirects: CollectionAfterChangeHook = ({ doc, req: { payload } }) => {
  payload.logger.info('Revalidating redirects')
  revalidateTag('redirects', 'max')
  return doc
}
```

### Frontend Redirect Component

The `PayloadRedirects` component handles redirect resolution on the frontend, checking the redirects collection and performing proper HTTP redirects with correct status codes.

### Next.js-Level Redirects

Additional redirects are defined in `redirects.ts` and loaded into `next.config.ts`:

```typescript
// redirects.ts
export const redirects: NextConfig['redirects'] = async () => {
  return [
    {
      source: '/:path((?!ie-incompatible.html$).*)',
      destination: '/ie-incompatible.html',
      permanent: false,
      has: [{ type: 'header', key: 'user-agent', value: '(.*Trident.*)' }],
    },
  ]
}
```

This redirects Internet Explorer users to an incompatibility page.

## Form Builder Plugin

The form builder plugin enables creating and managing forms from the admin panel.

### Configuration

```typescript
formBuilderPlugin({
  fields: {
    payment: false,
  },
  formOverrides: {
    fields: ({ defaultFields }) => {
      return defaultFields.map((field) => {
        if ('name' in field && field.name === 'confirmationMessage') {
          return {
            ...field,
            editor: lexicalEditor({
              features: ({ rootFeatures }) => [
                ...rootFeatures,
                FixedToolbarFeature(),
                HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
              ],
            }),
          }
        }
        return field
      })
    },
  },
})
```

Payment fields are disabled. The confirmation message field uses the Lexical editor instead of a plain textarea for richer formatting.

Forms can be embedded on pages using the Form block in the layout builder.

## Nested Docs Plugin

The nested docs plugin enables hierarchical document structures.

### Configuration

```typescript
nestedDocsPlugin({
  collections: ['categories'],
  generateURL: (docs) => docs.reduce((url, doc) => `${url}/${doc.slug}`, ''),
})
```

This allows categories to be nested inside each other, generating URLs like `/technology/web-development` from a chain of parent → child category slugs. The `generateURL` function concatenates slug segments with forward slashes.

## Plugin Dependencies

All five plugins are listed as workspace dependencies in the template's `package.json`:

- `@payloadcms/plugin-form-builder`
- `@payloadcms/plugin-nested-docs`
- `@payloadcms/plugin-redirects`
- `@payloadcms/plugin-search`
- `@payloadcms/plugin-seo`
