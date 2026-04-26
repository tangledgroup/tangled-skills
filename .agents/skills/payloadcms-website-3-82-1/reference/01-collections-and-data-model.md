# Collections and Data Model

## Pages Collection

Pages are the primary content type for website pages. They support the layout builder, draft/published workflow, SEO metadata, and slug-based routing.

### Field Structure

- `title` (text, required) — Page display title
- `hero` (group) — Hero section configuration with type selector (none, highImpact, mediumImpact, lowImpact), rich text content, link group (max 2 rows), and conditional media upload
- `layout` (blocks, required) — Layout builder accepting CallToAction, Content, MediaBlock, Archive, and FormBlock
- `meta` (group, tab "SEO") — SEO plugin fields including OverviewField, MetaTitleField with auto-generate, MetaImageField linked to media, MetaDescriptionField, and PreviewField
- `publishedAt` (date, sidebar position) — Publication timestamp, auto-populated via beforeChange hook
- `slug` (auto-generated via slugField) — URL-friendly identifier

### Configuration

```typescript
export const Pages: CollectionConfig<'pages'> = {
  slug: 'pages',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
  },
  defaultPopulate: { title: true, slug: true },
  admin: {
    defaultColumns: ['title', 'slug', 'updatedAt'],
    useAsTitle: 'title',
    preview: (data, { req }) => generatePreviewPath({ slug: data?.slug as string, collection: 'pages', req }),
    livePreview: {
      url: ({ data, req }) => generatePreviewPath({ slug: data?.slug, collection: 'pages', req }),
    },
  },
  hooks: {
    afterChange: [revalidatePage],
    beforeChange: [populatePublishedAt],
    afterDelete: [revalidateDelete],
  },
  versions: {
    drafts: {
      autosave: { interval: 100 },
      schedulePublish: true,
    },
    maxPerDoc: 50,
  },
}
```

### Revalidation Hooks

The `afterChange` hook calls Next.js `revalidatePath()` and `revalidateTag()` when a page is published or unpublished. The `afterDelete` hook revalidates the deleted page's path. Both check `context.disableRevalidate` to allow bypassing during bulk operations.

Home page slug maps to `/`, all other slugs map to `/{slug}`.

## Posts Collection

Posts are used for blog articles, news, and time-based content. They use Lexical rich text with inline blocks instead of the page-level layout builder.

### Field Structure

- `title` (text, required) — Post title
- `heroImage` (upload, relationTo: media) — Featured image for the post
- `content` (richText, required) — Main article content using Lexical editor with features: HeadingFeature (h1-h4), BlocksFeature (Banner, Code, MediaBlock), FixedToolbarFeature, InlineToolbarFeature, HorizontalRuleFeature
- `relatedPosts` (relationship, hasMany, relationTo: posts) — Sidebar-positioned links to related posts, excludes current post via filterOptions
- `categories` (relationship, hasMany, relationTo: categories) — Sidebar-positioned category assignments
- `meta` (group, tab "SEO") — Same SEO plugin fields as Pages
- `publishedAt` (date, sidebar) — Publication timestamp
- `slug` (auto-generated) — URL slug

### defaultPopulate

Posts configure deeper default population than pages:

```typescript
defaultPopulate: {
  title: true,
  slug: true,
  categories: true,
  meta: { image: true, description: true },
}
```

This reduces N+1 queries when posts are referenced from other documents.

### Revalidation

Posts revalidate at `/posts/{slug}` path and use the `posts-sitemap` tag for sitemap cache invalidation.

## Media Collection

The Media collection handles file uploads with pre-configured image processing.

```typescript
export const Media: CollectionConfig = {
  slug: 'media',
  folders: true,
  access: {
    create: authenticated,
    delete: authenticated,
    read: anyone,
    update: authenticated,
  },
  fields: [
    { name: 'alt', type: 'text' },
    {
      name: 'caption',
      type: 'richText',
      editor: lexicalEditor({
        features: ({ rootFeatures }) => [
          ...rootFeatures,
          FixedToolbarFeature(),
          InlineToolbarFeature(),
        ],
      }),
    },
  ],
  upload: {
    staticDir: path.resolve(dirname, '../../public/media'),
    adminThumbnail: 'thumbnail',
    focalPoint: true,
    imageSizes: [
      { name: 'thumbnail', width: 300 },
      { name: 'square', width: 500, height: 500 },
      { name: 'small', width: 600 },
      { name: 'medium', width: 900 },
      { name: 'large', width: 1400 },
      { name: 'xlarge', width: 1920 },
      { name: 'og', width: 1200, height: 630, crop: 'center' },
    ],
  },
}
```

The `staticDir` points to `public/media` in the Next.js project, making files accessible outside Payload's API. The `og` size (1200x630) is optimized for Open Graph social sharing images.

## Categories Collection

Categories provide a taxonomy for organizing posts. The nested-docs plugin enables hierarchical structures like "News > Technology".

```typescript
export const Categories: CollectionConfig = {
  slug: 'categories',
  access: {
    create: authenticated,
    delete: authenticated,
    read: anyone,
    update: authenticated,
  },
  admin: { useAsTitle: 'title' },
  fields: [
    { name: 'title', type: 'text', required: true },
    slugField({ position: undefined }),
  ],
}
```

## Users Collection

Users control admin panel access with built-in Payload authentication.

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  access: {
    admin: authenticated,
    create: authenticated,
    delete: authenticated,
    read: authenticated,
    update: authenticated,
  },
  admin: { defaultColumns: ['name', 'email'], useAsTitle: 'name' },
  auth: true,
  fields: [{ name: 'name', type: 'text' }],
  timestamps: true,
}
```

The `auth: true` flag automatically adds email and password fields. All access operations require authentication — users are not publicly readable.

## Access Control Functions

### anyone

```typescript
export const anyone: Access = () => true
```

Unrestricted public access. Used for Media and Categories read operations.

### authenticated

```typescript
export const authenticated: isAuthenticated = ({ req: { user } }) => {
  return Boolean(user)
}
```

Requires logged-in user. Used for create, update, delete operations on all collections.

### authenticatedOrPublished

```typescript
export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  if (user) return true
  return { _status: { equals: 'published' } }
}
```

Returns `true` for authenticated users (full access). For anonymous requests, returns a Where clause that filters to only published documents. This is the key pattern enabling draft privacy while allowing public content consumption.

## Globals

### Header

```typescript
export const Header: GlobalConfig = {
  slug: 'header',
  access: { read: () => true },
  fields: [{
    name: 'navItems',
    type: 'array',
    fields: [link({ appearances: false })],
    maxRows: 6,
    admin: {
      initCollapsed: true,
      components: { RowLabel: '@/Header/RowLabel#RowLabel' },
    },
  }],
  hooks: { afterChange: [revalidateHeader] },
}
```

### Footer

Same structure as Header with `slug: 'footer'` and its own revalidation hook.

Both globals use the reusable `link` field definition (supporting internal references to pages/posts or custom URLs) without appearance styling options.

## Lexical Editor Configuration

The template defines a default Lexical editor in `src/fields/defaultLexical.ts`:

```typescript
export const defaultLexical = lexicalEditor({
  features: [
    ParagraphFeature(),
    UnderlineFeature(),
    BoldFeature(),
    ItalicFeature(),
    LinkFeature({
      enabledCollections: ['pages', 'posts'],
      fields: ({ defaultFields }) => {
        const defaultFieldsWithoutUrl = defaultFields.filter(
          (field) => !('name' in field && field.name === 'url')
        )
        return [
          ...defaultFieldsWithoutUrl,
          {
            name: 'url',
            type: 'text',
            admin: { condition: (_data, siblingData) => siblingData?.linkType !== 'internal' },
            label: ({ t }) => t('fields:enterURL'),
            required: true,
            validate: ((value, options) => {
              if ((options?.siblingData as LinkFields)?.linkType === 'internal') return true
              return value ? true : 'URL is required'
            }) as TextFieldSingleValidation,
          },
        ]
      },
    }),
  ],
})
```

This configuration is set as the global editor in `payload.config.ts` via `editor: defaultLexical`, so all richText fields inherit these features unless they override with their own `lexicalEditor()` call.
