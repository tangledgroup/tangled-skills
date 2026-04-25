# Collections and Fields

This reference covers the collection configurations, field types, relationships, and data models used in the Payload CMS Website Template.

## Collection Overview

The template defines five collections that form the core content structure:

| Collection | Slug | Auth | Versions | Drafts | Purpose |
|------------|------|------|----------|--------|---------|
| Users | `users` | Yes | No | No | Admin authentication and access control |
| Pages | `pages` | No | Yes | Yes | Static pages with layout builder |
| Posts | `posts` | No | Yes | Yes | Blog posts with Lexical editor |
| Media | `media` | No | No | No | Image/video uploads with transformations |
| Categories | `categories` | No | No | No | Nested taxonomy for organizing posts |

## Users Collection

### Configuration

```ts
// src/collections/Users/index.ts
export const Users: CollectionConfig<'users'> = {
  slug: 'users',
  access: {
    admin: authenticated, // Only authenticated users can access admin
    create: authenticated,
    delete: authenticated,
    read: authenticated,
    update: authenticated,
  },
  auth: true, // Enables Payload authentication
  fields: [
    {
      name: 'name',
      type: 'text',
    },
    // Email and password fields auto-added by auth: true
  ],
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | text | Yes | Auto-generated document ID |
| `email` | text | Yes | Login email (auto-added by auth) |
| `password` | password | Yes | Hashed password (auto-added by auth) |
| `name` | text | No | Display name for admin panel |
| `createdAt` | date | Yes | Document creation timestamp |
| `updatedAt` | date | Yes | Last update timestamp |

### Access Control

- **Admin**: Only authenticated users can access `/admin`
- **Read**: Authenticated users can query other users
- **Create**: Authenticated users can create new users
- **Update**: Users can update their own documents
- **Delete**: Authenticated users can delete users

### Authentication Usage

```ts
// Check if user is authenticated
import { isAuthenticated } from '@/access/authenticated'

access: {
  read: isAuthenticated,
}

// Access current user in hooks
beforeChange: [
  async ({ req }) => {
    const currentUser = req.user
    console.log('Current user:', currentUser)
    return doc
  }
]
```

## Pages Collection

### Configuration

```ts
// src/collections/Pages/index.ts
export const Pages: CollectionConfig<'pages'> = {
  slug: 'pages',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished, // Public can read published pages
    update: authenticated,
  },
  defaultPopulate: {
    title: true,
    slug: true,
  },
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'updatedAt'],
    livePreview: {
      url: ({ data, req }) => generatePreviewPath({
        slug: data?.slug,
        collection: 'pages',
        req,
      }),
    },
  },
  fields: [/* ... */],
  versions: {
    drafts: {
      autosave: { interval: 100 },
      schedulePublish: true,
    },
    maxPerDoc: 50,
  },
  hooks: {
    afterChange: [revalidatePage],
    beforeChange: [populatePublishedAt],
    afterDelete: [revalidateDelete],
  },
}
```

### Fields Structure

```ts
fields: [
  {
    name: 'title',
    type: 'text',
    required: true,
  },
  {
    type: 'tabs',
    tabs: [
      {
        fields: [hero], // Hero block configuration
        label: 'Hero',
      },
      {
        fields: [
          {
            name: 'layout',
            type: 'blocks',
            blocks: [CallToAction, Content, MediaBlock, Archive, FormBlock],
            required: true,
          },
        ],
        label: 'Content',
      },
      {
        name: 'meta',
        label: 'SEO',
        fields: [/* SEO fields */],
      },
    ],
  },
  {
    name: 'publishedAt',
    type: 'date',
    admin: { position: 'sidebar' },
  },
  slugField(), // Auto-generated slug field
]
```

### Hero Field

The hero is a block-type field with multiple variants:

```ts
// src/heros/config.ts
export const hero: Block = {
  name: 'hero',
  type: 'block',
  fields: [
    {
      name: 'type',
      type: 'select',
      options: [
        { label: 'Home', value: 'home' },
        { label: 'Centered', value: 'centered' },
        { label: 'Small', value: 'small' },
        { label: 'Split Left', value: 'splitLeft' },
        { label: 'Split Right', value: 'splitRight' },
      ],
      required: true,
    },
    {
      name: 'richText',
      type: 'richText',
      editor: lexicalEditor({ /* ... */ }),
    },
    {
      name: 'media',
      type: 'upload',
      relationTo: 'media',
    },
  ],
}
```

### Layout Blocks Field

Pages use a blocks field for flexible layouts:

```ts
{
  name: 'layout',
  type: 'blocks',
  blocks: [
    CallToAction, // CTA section with buttons
    Content,      // Text content with columns
    MediaBlock,   // Image/video display
    Archive,      // Post listing block
    FormBlock,    // Embedded form
  ],
  required: true,
  admin: {
    initCollapsed: true,
  },
}
```

### SEO Fields

Integrated via `@payloadcms/plugin-seo`:

```ts
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

### Version and Draft Configuration

```ts
versions: {
  drafts: {
    autosave: {
      interval: 100, // Autosave every 100ms for live preview
    },
    schedulePublish: true, // Enable scheduled publishing
  },
  maxPerDoc: 50, // Keep last 50 versions
}
```

## Posts Collection

### Configuration

```ts
// src/collections/Posts/index.ts
export const Posts: CollectionConfig<'posts'> = {
  slug: 'posts',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
  },
  defaultPopulate: {
    title: true,
    slug: true,
    categories: true,
    meta: {
      image: true,
      description: true,
    },
  },
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'updatedAt'],
    livePreview: {
      url: ({ data, req }) => generatePreviewPath({
        slug: data?.slug,
        collection: 'posts',
        req,
      }),
    },
  },
  fields: [/* ... */],
  versions: {
    drafts: {
      autosave: { interval: 100 },
      schedulePublish: true,
    },
    maxPerDoc: 50,
  },
  hooks: {
    afterChange: [revalidatePost],
    beforeChange: [populatePublishedAt, populateAuthors],
    afterDelete: [revalidateDelete],
  },
}
```

### Fields Structure

```ts
fields: [
  {
    name: 'title',
    type: 'text',
    required: true,
  },
  {
    type: 'tabs',
    tabs: [
      {
        fields: [
          {
            name: 'heroImage',
            type: 'upload',
            relationTo: 'media',
          },
          {
            name: 'content',
            type: 'richText',
            editor: lexicalEditor({
              features: ({ rootFeatures }) => [
                ...rootFeatures,
                HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
                BlocksFeature({ blocks: [Banner, Code, MediaBlock] }),
                FixedToolbarFeature(),
                InlineToolbarFeature(),
                HorizontalRuleFeature(),
              ],
            }),
            required: true,
          },
        ],
        label: 'Content',
      },
      {
        fields: [
          {
            name: 'relatedPosts',
            type: 'relationship',
            relationTo: 'posts',
            hasMany: true,
            admin: { position: 'sidebar' },
            filterOptions: ({ id }) => ({
              id: { not_in: [id] },
            }),
          },
          {
            name: 'categories',
            type: 'relationship',
            relationTo: 'categories',
            hasMany: true,
            admin: { position: 'sidebar' },
          },
        ],
        label: 'Meta',
      },
      {
        name: 'meta',
        label: 'SEO',
        fields: [/* SEO fields same as Pages */],
      },
    ],
  },
  {
    name: 'publishedAt',
    type: 'date',
    admin: { position: 'sidebar' },
  },
  slugField(),
]
```

### Lexical Editor Features

Posts use the Lexical rich-text editor with inline blocks:

| Feature | Description |
|---------|-------------|
| Headings | H1-H4 heading sizes |
| Blocks | Inline Banner, Code, and Media blocks |
| Fixed Toolbar | Always-visible toolbar option |
| Inline Toolbar | Floating toolbar on text selection |
| Horizontal Rule | Divider/separator element |

### Inline Block Types

**Banner Block:**

```ts
// src/blocks/Banner/config.ts
export const Banner: Block = {
  slug: 'banner',
  fields: [
    {
      name: 'style',
      type: 'select',
      options: [
        { label: 'Info', value: 'info' },
        { label: 'Warning', value: 'warning' },
        { label: 'Error', value: 'error' },
      ],
      required: true,
    },
    {
      name: 'content',
      type: 'richText',
    },
  ],
}
```

**Code Block:**

```ts
// src/blocks/Code/config.ts
export const Code: Block = {
  slug: 'code',
  fields: [
    {
      name: 'code',
      type: 'code',
      required: true,
    },
    {
      name: 'caption',
      type: 'text',
    },
  ],
}
```

## Media Collection

### Configuration

```ts
// src/collections/Media/index.ts
export const Media: CollectionConfig<'media'> = {
  slug: 'media',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished, // Public can view media
    update: authenticated,
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
    },
    {
      name: 'caption',
      type: 'text',
    },
    // Upload field auto-configured
  ],
  upload: {
    staticDir: 'media',
    mimeTypes: ['image/*', 'video/*'],
    imageSizes: [
      {
        name: 'thumbnail',
        width: 400,
        height: 300,
        fit: 'cover',
      },
      {
        name: 'small',
        width: 800,
        height: 600,
        fit: 'cover',
      },
      {
        name: 'medium',
        width: 1200,
        height: 800,
        fit: 'cover',
      },
      {
        name: 'large',
        width: 1920,
        height: 1080,
        fit: 'cover',
      },
    ],
    focalPoint: true, // Enable focal point cropping
  },
}
```

### Upload Configuration

**Supported MIME Types:**
- Images: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml`
- Videos: `video/mp4`, `video/webm`, `video/ogg`

**Pre-configured Image Sizes:**

| Size | Width | Height | Fit | Use Case |
|------|-------|--------|-----|----------|
| thumbnail | 400 | 300 | cover | Thumbnails, avatars |
| small | 800 | 600 | cover | Sidebar images, cards |
| medium | 1200 | 800 | cover | Blog post images |
| large | 1920 | 1080 | cover | Hero sections, full-width |

**Focal Point Cropping:**

```ts
// Media documents include focal point data
{
  id: 'media-doc-id',
  url: '/media/image.jpg',
  filename: 'image.jpg',
  mimeType: 'image/jpeg',
  filesize: 123456,
  width: 1920,
  height: 1080,
  alt: 'Alt text',
  caption: 'Optional caption',
  focalPoint: {
    x: 0.5, // Horizontal position (0-1)
    y: 0.3, // Vertical position (0-1)
  },
}
```

### Using Media in Frontend

```tsx
// With automatic size selection
import Image from 'next/image'

<MediaBlock media={page.hero.media}>
  <Image
    src={media.url}
    alt={media.alt}
    width={1200}
    height={600}
  />
</MediaBlock>

// With pre-configured sizes
<Image
  src={media.url}
  alt={media.alt}
  width={800}
  height={600}
  size="small" // Uses pre-generated size
/>
```

## Categories Collection

### Configuration

```ts
// src/collections/Categories/index.ts
export const Categories: CollectionConfig<'categories'> = {
  slug: 'categories',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
    },
    slugField(),
  ],
}
```

### Nested Categories

Uses `@payloadcms/plugin-nested-docs` for hierarchical categories:

```ts
// src/plugins/index.ts
nestedDocsPlugin({
  collections: ['categories'],
  generateURL: (docs) => docs.reduce((url, doc) => `${url}/${doc.slug}`, ''),
})
```

**Category Hierarchy Example:**

```
News
├── Technology
│   ├── Artificial Intelligence
│   └── Software Development
├── Business
└── Politics
```

**URL Generation:**

- `Technology` → `/categories/technology`
- `Artificial Intelligence` (child of Technology) → `/categories/technology/artificial-intelligence`

### Using Categories in Posts

```ts
// Post document with categories
{
  title: 'Introduction to AI',
  slug: 'introduction-to-ai',
  categories: [
    {
      relationTo: 'categories',
      value: 'tech-category-id', // Technology
    },
    {
      relationTo: 'categories',
      value: 'ai-category-id',   // Artificial Intelligence
    },
  ],
}
```

## Globals

### Header Global

```ts
// src/Header/config.ts
export const Header: GlobalConfig = {
  slug: 'header',
  fields: [
    {
      name: 'navItems',
      type: 'array',
      fields: [
        {
          name: 'label',
          type: 'text',
          required: true,
        },
        {
          name: 'url',
          type: 'text',
          required: true,
        },
      ],
      required: true,
    },
  ],
}
```

### Footer Global

```ts
// src/Footer/config.ts
export const Footer: GlobalConfig = {
  slug: 'footer',
  fields: [
    {
      name: 'navItems',
      type: 'array',
      fields: [
        {
          name: 'label',
          type: 'text',
          required: true,
        },
        {
          name: 'url',
          type: 'text',
          required: true,
        },
      ],
    },
    {
      name: 'socialLinks',
      type: 'array',
      fields: [
        {
          name: 'platform',
          type: 'select',
          options: [
            { label: 'Twitter', value: 'twitter' },
            { label: 'GitHub', value: 'github' },
            { label: 'LinkedIn', value: 'linkedin' },
          ],
        },
        {
          name: 'url',
          type: 'text',
        },
      ],
    },
  ],
}
```

## Field Types Reference

### Common Field Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Single-line text input | Title, name, slug |
| `richText` | Lexical editor content | Post body, page content |
| `number` | Numeric input | Counters, prices |
| `date` | Date/time picker | Published at, events |
| `select` | Dropdown selection | Status, categories |
| `radio` | Radio button group | Single choice options |
| `checkbox` | Boolean toggle | Featured flag, enabled |
| `array` | Repeating field group | Nav items, team members |
| `blocks` | Multiple block types | Page layouts, rich content |
| `relationship` | Reference to docs | Categories, related posts |
| `upload` | File/media upload | Images, videos, documents |

### Special Field Configurations

**Slug Field:**

```ts
import { slugField } from 'payload'

slugField({
  relationTo: 'pages', // Auto-generate from title
})
```

**Relationship with Filter Options:**

```ts
{
  name: 'relatedPosts',
  type: 'relationship',
  relationTo: 'posts',
  hasMany: true,
  filterOptions: ({ id }) => ({
    id: { not_in: [id] }, // Exclude self
  }),
}
```

**Upload with Image Sizes:**

```ts
{
  name: 'heroImage',
  type: 'upload',
  relationTo: 'media',
  admin: {
    thumbnailURL: true, // Show thumbnail in list view
  },
}
```

## Access Control Functions

### Authenticated Access

```ts
// src/access/authenticated.ts
export const authenticated = ({ req }: { req: PayloadRequest }): boolean => {
  return !!req.user
}
```

### Authenticated or Published

```ts
// src/access/authenticatedOrPublished.ts
export const authenticatedOrPublished = async ({
  req,
  doc,
}: {
  req: PayloadRequest
  doc?: Page
}): Promise<boolean> => {
  // Allow authenticated users to read any document
  if (req.user) return true

  // Allow public to read published documents
  if (doc && doc._status === 'published') return true

  return false
}
```

### Custom Access Control

```ts
// Example: Only allow user to edit their own posts
access: {
  update: ({ req, doc }) => {
    if (!req.user) return false
    // Allow admins full access
    if (req.user.role === 'admin') return true
    // Users can only edit their own posts
    return doc?.author.id === req.user.id
  },
}
```

## Hooks Reference

### Before Change Hook

```ts
beforeChange: [
  async ({ doc, operation }) => {
    // Modify document before saving
    if (operation === 'create') {
      doc.createdAt = new Date()
    }
    return doc
  },
]
```

### After Change Hook

```ts
afterChange: [
  async ({ doc, previousDoc, operation }) => {
    // Trigger after document is saved
    if (doc._status === 'published' && previousDoc?._status !== 'published') {
      await revalidatePath(`/${doc.slug}`, 'page')
    }
  },
]
```

### After Delete Hook

```ts
afterDelete: [
  async ({ doc }) => {
    // Clean up after document deletion
    await revalidatePath(`/${doc.slug}`, 'page')
  },
]
```

## Next Steps

After understanding collections and fields, explore:
- [Pages and Posts](03-pages-and-posts.md) - Creating and managing content
- [Next.js Integration](04-nextjs-integration.md) - Building the frontend
- [Customizations](08-customizations.md) - Extending with custom fields and blocks
