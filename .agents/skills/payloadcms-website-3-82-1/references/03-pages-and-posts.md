# Pages and Posts

This reference covers creating, managing, and rendering Pages and Posts content, including layout builders, the Lexical editor, draft workflows, and version management.

## Pages Collection

### Creating a Page

**Via Admin Panel:**

1. Navigate to `/admin` → Collections → Pages
2. Click "New Page" button
3. Fill in required fields:
   - **Title**: Page title (required)
   - **Slug**: Auto-generated from title, editable
4. Configure Hero section
5. Add layout blocks for content
6. Set SEO metadata
7. Click "Save Draft" or "Publish"

**Via Local API:**

```ts
import { getPayload } from 'payload'
import configPromise from '@payload-config'

const payload = await getPayload({ config: configPromise })

const page = await payload.create({
  collection: 'pages',
  data: {
    title: 'About Us',
    slug: 'about',
    hero: {
      type: 'centered',
      richText: [{ text: 'Learn about our company' }],
      media: null,
    },
    layout: [
      {
        blockName: 'Content Block',
        blockType: 'content',
        content: 'Our story goes here...',
        columns: [
          {
            size: 'half',
            richText: [{ text: 'First column' }],
          },
          {
            size: 'half',
            richText: [{ text: 'Second column' }],
          },
        ],
      },
    ],
    _status: 'published',
  },
})
```

### Page Structure

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | text | Page title displayed in browser and admin |
| `slug` | text | URL-friendly identifier (auto-generated) |
| `hero` | block | Hero section with type, rich text, media |
| `layout` | blocks[] | Array of layout blocks for page content |

**Optional Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `meta.title` | text | SEO title (auto-generated from title) |
| `meta.description` | text | Meta description for search engines |
| `meta.image` | upload | Open Graph/image for social sharing |
| `publishedAt` | date | Publication timestamp |

### Hero Section Types

Pages support five hero section variants:

```ts
// Available hero types
type: 'home'        // Full-width hero for homepage
type: 'centered'    // Centered text with optional background image
type: 'small'       // Compact hero with minimal styling
type: 'splitLeft'   // Split layout with content on left, media on right
type: 'splitRight'  // Split layout with media on left, content on right
```

**Hero Configuration Example:**

```ts
hero: {
  type: 'centered',
  richText: [
    {
      type: 'heading',
      children: [{ text: 'Welcome to Our Website' }],
    },
    {
      type: 'paragraph',
      children: [{ text: 'We build amazing digital experiences' }],
    },
  ],
  media: 'media-doc-id-123', // Optional background image
}
```

### Layout Blocks

Pages use a flexible block-based layout system. Each block is independently configured and rendered.

#### Content Block

Multi-column text content with alignment options:

```ts
{
  blockName: 'Content Block',
  blockType: 'content',
  content: 'Simple text content', // Or richText for formatted content
  columns: [
    {
      size: 'one-third', // Options: one-third, half, two-thirds, full
      richText: [{ text: 'First column content' }],
    },
    {
      size: 'two-thirds',
      richText: [{ text: 'Second column content' }],
    },
  ],
  align: 'left', // Options: left, center, right
}
```

#### Media Block

Image or video display with caption and styling:

```ts
{
  blockName: 'Media Block',
  blockType: 'mediaBlock',
  media: 'media-doc-id-456',
  align: 'left', // Options: left, center, right
  size: 'large', // Options: small, medium, large
  caption: 'Optional caption text',
  links: [
    {
      label: 'Learn More',
      url: '/about',
      newTab: false,
    },
  ],
}
```

#### Call To Action Block

Prominent CTA section with buttons:

```ts
{
  blockName: 'CTA Block',
  blockType: 'callToAction',
  richText: [
    { text: 'Ready to get started?' },
  ],
  links: [
    {
      label: 'Get Started',
      url: '/contact',
      newTab: false,
    },
    {
      label: 'Learn More',
      url: '/features',
      newTab: true,
    },
  ],
  align: 'center', // Options: left, center, right
}
```

#### Archive Block

Display posts or categories in a grid/list layout:

```ts
{
  blockName: 'Recent Posts',
  blockType: 'archive',
  title: 'Latest Articles',
  selectCategories: ['category-id-1', 'category-id-2'], // Optional filter
  limit: 6, // Number of posts to display
}
```

#### Form Block

Embed a form from the form builder plugin:

```ts
{
  blockName: 'Contact Form',
  blockType: 'formBlock',
  form: 'form-doc-id-789', // Reference to Forms collection
}
```

### Rendering Page Blocks

**RenderBlocks Component:**

```tsx
// src/blocks/RenderBlocks.tsx
import { CallToAction } from '@/blocks/CallToAction/Client'
import { Content } from '@/blocks/Content/Client'
import { MediaBlock } from '@/blocks/MediaBlock/Client'
import { Archive } from '@/blocks/Archive/Client'
import { FormBlock } from '@/blocks/Form/Client'

export const RenderBlocks = ({ blocks }: { blocks: Page['layout'] }) => {
  return (
    <>
      {blocks?.map((block, i) => {
        const key = `${block.blockType}-${i}`
        switch (block.blockType) {
          case 'callToAction':
            return <CallToAction {...block} key={key} />
          case 'content':
            return <Content {...block} key={key} />
          case 'mediaBlock':
            return <MediaBlock {...block} key={key} />
          case 'archive':
            return <Archive {...block} key={key} />
          case 'formBlock':
            return <FormBlock {...block} key={key} />
          default:
            return null
        }
      })}
    </>
  )
}
```

## Posts Collection

### Creating a Post

**Via Admin Panel:**

1. Navigate to `/admin` → Collections → Posts
2. Click "New Post" button
3. Fill in required fields:
   - **Title**: Post title (required)
   - **Slug**: Auto-generated from title
4. Upload hero image (optional)
5. Write content using Lexical editor
6. Add inline blocks (banners, code, media)
7. Assign categories and related posts
8. Configure SEO metadata
9. Click "Save Draft" or "Publish"

**Via Local API:**

```ts
const post = await payload.create({
  collection: 'posts',
  data: {
    title: 'Getting Started with Payload CMS',
    slug: 'getting-started-with-payload',
    heroImage: 'media-doc-id-hero',
    content: [
      {
        type: 'heading',
        children: [{ text: 'Introduction' }],
      },
      {
        type: 'paragraph',
        children: [{ text: 'Payload CMS is a headless CMS...' }],
      },
    ],
    categories: ['category-id-tech'],
    _status: 'published',
  },
})
```

### Post Structure

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | text | Post title (required) |
| `slug` | text | URL-friendly identifier |
| `content` | richText | Main post content with Lexical editor |

**Optional Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `heroImage` | upload | Featured image for post |
| `categories` | relationship[] | Taxonomy categories (many) |
| `relatedPosts` | relationship[] | Related posts (many) |
| `meta.*` | various | SEO metadata fields |
| `publishedAt` | date | Publication timestamp |

### Lexical Editor Features

The template uses Payload's Lexical integration with custom features:

**Available Features:**

| Feature | Description | Usage |
|---------|-------------|-------|
| Headings | H1-H4 heading levels | Click heading button or use keyboard shortcut |
| Bold/Italic | Text formatting | Select text and click format buttons |
| Links | Internal/external links | Select text and add URL |
| Lists | Ordered and unordered lists | Click list button |
| Blocks | Inline content blocks | Type `/` to open block menu |
| Code | Syntax-highlighted code blocks | Type `/code` or use code button |
| Media | Inline images/videos | Type `/media` or drag-and-drop |
| Banner | Callout/alert blocks | Type `/banner` for styled callouts |

**Using Inline Blocks:**

Type `/` in the editor to open the block menu:

```
/ → Opens block picker
  → Select "Banner" for callout
  → Select "Code" for code block
  → Select "Media" for inline image
```

**Banner Block in Content:**

```ts
{
  type: 'block',
  children: [
    {
      type: 'paragraph',
      children: [{ text: 'Important note about this topic' }],
    },
  ],
  tagName: 'lexical-block',
  fields: {
    style: 'info', // Options: info, warning, error
  },
}
```

**Code Block in Content:**

```ts
{
  type: 'block',
  children: [],
  tagName: 'lexical-block',
  fields: {
    code: 'console.log("Hello, world!");',
    caption: 'JavaScript example',
  },
}
```

### Categories and Taxonomy

Posts can be assigned to multiple categories with nested hierarchy:

```ts
categories: [
  {
    relationTo: 'categories',
    value: 'tech-category-id', // Technology (parent)
  },
  {
    relationTo: 'categories',
    value: 'cms-category-id',  // CMS (child of Technology)
  },
]
```

**Querying Posts by Category:**

```ts
const posts = await payload.find({
  collection: 'posts',
  where: {
    categories: {
      equals: 'category-id-123',
    },
  },
  sort: '-publishedAt',
})
```

### Related Posts

Manually curate related posts or auto-generate based on categories:

**Manual Selection:**

```ts
relatedPosts: [
  { relationTo: 'posts', value: 'post-id-1' },
  { relationTo: 'posts', value: 'post-id-2' },
]
```

**Auto-generate by Category:**

```ts
const related = await payload.find({
  collection: 'posts',
  where: {
    and: [
      {
        categories: {
          in: post.categories.map((c) => c.value),
        },
      },
      {
        id: { not_in: [post.id] }, // Exclude current post
      },
    ],
  },
  limit: 3,
  sort: '-publishedAt',
})
```

## Draft and Version Management

### Draft Workflow

Both Pages and Posts support draft mode with version tracking:

**Draft States:**

| Status | Visibility | Description |
|--------|------------|-------------|
| `draft` | Admin only | Unpublished, editable |
| `published` | Public | Live on website |
| `scheduled` | Scheduled time | Auto-publish at specified time |

### Creating a Draft

```ts
const draft = await payload.create({
  collection: 'pages',
  data: {
    title: 'Upcoming Feature',
    slug: 'upcoming-feature',
    hero: { type: 'small', richText: [], media: null },
    layout: [],
    _status: 'draft', // Explicitly set as draft
  },
})
```

### Previewing Drafts

**Draft Mode URL:**

```ts
// Generate preview URL
const previewURL = `/preview/${collection}/${slug}?secret=${previewSecret}`

// Example: /preview/pages/my-page?secret=abc123
```

**Using Next.js Draft Mode:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import { draftMode } from 'next/headers'

export default async function Page({ params }) {
  const { isEnabled: draft } = await draftMode()
  
  const page = await payload.find({
    collection: 'pages',
    where: { slug: { equals: params.slug } },
    draft: draft, // Fetch draft if draft mode enabled
  })
}
```

### Live Preview

Live preview provides real-time SSR rendering as content is edited:

**Configuration:**

```ts
// In collection config
admin: {
  livePreview: {
    url: ({ data, req }) => generatePreviewPath({
      slug: data?.slug,
      collection: 'pages',
      req,
    }),
  },
}
```

**Live Preview Listener:**

```tsx
// src/components/LivePreviewListener.tsx
'use client'

import { useLivePreview } from '@payloadcms/live-preview-react'

export const LivePreviewListener = () => {
  useLivePreview()
  return null
}
```

Add to page components:

```tsx
export default async function Page() {
  const { isEnabled: draft } = await draftMode()
  
  return (
    <article>
      {draft && <LivePreviewListener />}
      {/* Page content */}
    </article>
  )
}
```

### Publishing Content

**Manual Publish:**

```ts
const published = await payload.update({
  collection: 'pages',
  id: 'page-id-123',
  data: {
    _status: 'published',
  },
})
```

**Scheduled Publish:**

```ts
const scheduled = await payload.update({
  collection: 'pages',
  id: 'page-id-123',
  data: {
    _status: 'scheduled',
    publishedAt: '2024-12-31T23:59:59.000Z', // ISO timestamp
  },
})
```

Jobs queue processes scheduled documents:

```ts
// In payload.config.ts
jobs: {
  tasks: [
    {
      name: 'scheduled-publish',
      interval: 60, // Run every 60 seconds
      func: async ({ jobsQueue }) => {
        const now = new Date()
        const docs = await jobsQueue.findScheduledDocs({
          dueAt: now,
        })
        
        for (const doc of docs) {
          await payload.update({
            collection: doc.collection,
            id: doc.id,
            data: { _status: 'published' },
          })
        }
      },
    },
  ],
}
```

### Version History

Payload tracks document versions for rollback and audit:

**Query Versions:**

```ts
const versions = await payload.findVersions({
  collection: 'pages',
  where: {
    parent: { equals: 'page-id-123' },
  },
  limit: 10, // Last 10 versions
})
```

**Restore Version:**

```ts
const restored = await payload.restoreVersion({
  collection: 'pages',
  id: 'version-id-456',
})
```

## Querying Pages and Posts

### Basic Queries

**Find All Published Pages:**

```ts
const pages = await payload.find({
  collection: 'pages',
  where: {
    _status: { equals: 'published' },
  },
  sort: '-publishedAt',
})
```

**Find Page by Slug:**

```ts
const page = await payload.find({
  collection: 'pages',
  where: {
    slug: { equals: 'about' },
    _status: { equals: 'published' },
  },
  limit: 1,
})
```

**Find Posts with Pagination:**

```ts
const posts = await payload.find({
  collection: 'posts',
  where: {
    _status: { equals: 'published' },
  },
  page: 2, // Page number
  limit: 10, // Posts per page
  sort: '-publishedAt',
})

// posts.totalDocs - Total number of matching docs
// posts.page - Current page number
// posts.docs - Array of post documents
```

### Advanced Queries

**Posts by Multiple Categories:**

```ts
const posts = await payload.find({
  collection: 'posts',
  where: {
    or: [
      { categories: { equals: 'cat-id-1' } },
      { categories: { equals: 'cat-id-2' } },
    ],
  },
})
```

**Posts with Specific Author:**

```ts
const posts = await payload.find({
  collection: 'posts',
  where: {
    author: { equals: 'user-id-123' },
  },
  populate: ['author'], // Include author data
})
```

**Search by Title or Content:**

```ts
const posts = await payload.find({
  collection: 'posts',
  where: {
    or: [
      { title: { like: 'search term' } },
      { 'meta.description': { like: 'search term' } },
    ],
  },
})
```

### Population and Select

**Populate Relationships:**

```ts
const post = await payload.findByID({
  collection: 'posts',
  id: 'post-id-123',
  populate: ['categories', 'relatedPosts', 'heroImage'],
})
```

**Select Specific Fields:**

```ts
const pages = await payload.find({
  collection: 'pages',
  select: {
    title: true,
    slug: true,
    meta: {
      image: true,
      description: true,
    },
  },
})
```

## SEO and Metadata

### Meta Field Configuration

Both Pages and Posts include SEO fields via the plugin:

```ts
meta: {
  title: 'Custom SEO Title', // Overrides auto-generated title
  description: 'Meta description for search engines (160 chars max)',
  image: 'media-doc-id-for-social-sharing',
}
```

### Auto-Generated Meta

If not manually set, meta fields are auto-generated:

```ts
// In plugins/index.ts
const generateTitle: GenerateTitle<Post | Page> = ({ doc }) => {
  return doc?.title 
    ? `${doc.title} | Payload Website Template` 
    : 'Payload Website Template'
}

const generateURL: GenerateURL<Post | Page> = ({ doc }) => {
  const url = getServerSideURL()
  return doc?.slug ? `${url}/${doc.slug}` : url
}
```

### Using Meta in Frontend

```tsx
// src/utilities/generateMeta.ts
import type { Metadata } from 'next'

export const generateMeta = async ({
  doc,
}: {
  doc: Page | Post | null
}): Promise<Metadata> => {
  if (!doc) {
    return {
      title: 'Page Not Found',
      description: 'The page you requested could not be found.',
    }
  }

  return {
    title: doc.meta?.title || doc.title,
    description: doc.meta?.description,
    openGraph: doc.meta?.image
      ? {
          images: [doc.meta.image.url],
        }
      : {},
  }
}
```

## On-Demand Revalidation

### Page Revalidation Hook

```ts
// src/collections/Pages/hooks/revalidatePage.ts
export const revalidatePage = async ({
  doc,
  previousDoc,
}: {
  doc: Page
  previousDoc?: Page
}) => {
  if (doc._status === 'published' || previousDoc?._status === 'published') {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_SERVER_URL}/api/revalidate`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${process.env.PAYLOAD_SECRET}`,
          },
          body: JSON.stringify({
            slug: doc.slug,
            collection: 'pages',
          }),
        }
      )
    } catch (error) {
      console.error('Revalidation failed:', error)
    }
  }
}
```

### Revalidate Endpoint

```ts
// src/app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const authHeader = req.headers.get('authorization')
  
  if (authHeader !== `Bearer ${process.env.PAYLOAD_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(req.url)
  const slug = searchParams.get('slug')
  const collection = searchParams.get('collection')

  if (slug) {
    revalidatePath(`/${slug}`, 'page')
    return NextResponse.json({ revalidated: true })
  }

  return NextResponse.json({ error: 'Missing slug' }, { status: 400 })
}
```

## Best Practices

### Page Creation

1. **Use descriptive slugs**: `about-us` not `page-1`
2. **Configure SEO fields**: Always set meta title and description
3. **Optimize hero images**: Use appropriate sizes and focal points
4. **Limit layout blocks**: 5-7 blocks per page for readability
5. **Test responsive design**: Preview on mobile and tablet breakpoints

### Post Creation

1. **Write compelling titles**: Clear, descriptive, under 60 characters
2. **Use hero images**: Consistent sizing across all posts
3. **Leverage categories**: Assign 1-3 relevant categories per post
4. **Add related posts**: Help users discover related content
5. **Proofread content**: Use Lexical's formatting tools consistently

### Draft Workflow

1. **Save frequently**: Autosave runs every 100ms in live preview
2. **Preview before publishing**: Check draft mode rendering
3. **Schedule strategic publishes**: Queue posts for optimal timing
4. **Review version history**: Track changes over time
5. **Test on staging**: Preview on staging environment before production

## Next Steps

After mastering pages and posts, explore:
- [Next.js Integration](04-nextjs-integration.md) - Building the frontend application
- [SEO and i18n](05-seo-and-i18n.md) - Search optimization and internationalization
- [Search and Media](07-search-and-media.md) - Full-text search and media management
- [Customizations](08-customizations.md) - Extending with custom blocks and components
