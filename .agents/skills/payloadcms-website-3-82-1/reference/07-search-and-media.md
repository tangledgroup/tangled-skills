# Search and Media Management

This reference covers the Payload Search plugin for full-text search, media collection management, image optimization with Sharp, focal point cropping, and responsive images in Next.js.

## Search Plugin

### Overview

The template uses `@payloadcms/plugin-search` to provide full-text search functionality. The plugin automatically indexes content from specified collections and provides a search interface.

### Plugin Configuration

```ts
// src/plugins/index.ts
import { searchPlugin } from '@payloadcms/plugin-search'
import { beforeSyncWithSearch } from '@/search/beforeSync'
import { searchFields } from '@/search/fieldOverrides'

export const plugins: Plugin[] = [
  searchPlugin({
    collections: ['posts'], // Collections to index
    beforeSync: beforeSyncWithSearch, // Transform data before indexing
    searchOverrides: {
      fields: ({ defaultFields }) => {
        return [...defaultFields, ...searchFields] // Add custom fields
      },
    },
  }),
]
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `collections` | string[] | Collections to index for search |
| `beforeSync` | function | Transform document before syncing to search |
| `searchOverrides` | object | Override search collection configuration |

### Search Index Structure

The plugin creates a `search` collection with indexed content:

```ts
{
  id: 'search-doc-id',
  title: 'Post Title',
  slug: 'post-slug',
  url: '/posts/post-slug',
  excerpt: 'Post excerpt or first paragraph...',
  categories: ['Category 1', 'Category 2'],
  parent: {
    relationTo: 'posts',
    value: 'original-post-id',
  },
  _status: 'published',
}
```

### Before Sync Hook

Transform documents before indexing:

```ts
// src/search/beforeSync.ts
import type { BeforeSync } from '@payloadcms/plugin-search/types'
import type { Post } from '@/payload-types'

export const beforeSyncWithSearch: BeforeSync<Post> = ({ doc, collection }) => {
  // Filter out unpublished posts
  if (doc._status !== 'published') {
    return false
  }

  // Transform the document for search
  return {
    ...doc,
    title: doc.title,
    slug: doc.slug,
    url: `/posts/${doc.slug}`,
    // Extract excerpt from content
    excerpt: extractExcerpt(doc.content),
    // Format categories as labels
    categories: doc.categories?.map((cat) => cat.name),
  }
}

// Helper to extract excerpt from Lexical content
function extractExcerpt(content: any): string {
  if (!content || !content.root?.children) return ''
  
  const textNodes = content.root.children
    .filter((node: any) => node.type === 'paragraph')
    .map((node: any) => node.children?.map((child: any) => child.text).join(''))
    .join(' ')
    .slice(0, 160)
  
  return textNodes || ''
}
```

### Custom Search Fields

Add additional fields to the search index:

```ts
// src/search/fieldOverrides.ts
import type { Field } from 'payload'

export const searchFields: Field[] = [
  {
    name: 'author',
    type: 'text',
    admin: {
      readOnly: true,
      position: 'sidebar',
    },
  },
  {
    name: 'publishedAt',
    type: 'date',
    admin: {
      readOnly: true,
      position: 'sidebar',
    },
  },
]
```

### Search Query Function

Query the search index:

```ts
// src/utilities/search.ts
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export async function searchPosts(query: string, limit = 10) {
  const payload = await getPayload({ config: configPromise })

  const results = await payload.find({
    collection: 'search',
    where: {
      or: [
        { title: { like: query } },
        { excerpt: { like: query } },
        { categories: { like: query } },
      ],
    },
    limit,
    sort: 'title',
  })

  return results.docs
}
```

### Search Page Implementation

**Search Route:**

```tsx
// src/app/(frontend)/search/page.tsx
import { searchPosts } from '@/utilities/search'
import SearchResults from './SearchResults'

interface SearchPageProps {
  searchParams: Promise<{ q?: string }>
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q = '' } = await searchParams
  
  let results = []
  if (q.trim().length > 0) {
    results = await searchPosts(q.trim())
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold mb-8">Search {q && `&quot;${q}&quot;`}</h1>
      
      {q && (
        <p className="mb-8 text-gray-600">
          {results.length} result{results.length !== 1 ? 's' : ''} found
        </p>
      )}
      
      <SearchResults results={results} query={q} />
    </div>
  )
}
```

**Search Results Component:**

```tsx
// src/app/(frontend)/search/SearchResults.tsx
import Link from 'next/link'

export default function SearchResults({ results, query }: {
  results: any[]
  query: string
}) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No results found for &quot;{query}&quot;</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {results.map((result) => (
        <article key={result.id} className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-2">
            <Link href={result.url} className="hover:text-blue-600">
              {result.title}
            </Link>
          </h2>
          {result.excerpt && (
            <p className="text-gray-600 mb-2">{result.excerpt}</p>
          )}
          {result.categories && result.categories.length > 0 && (
            <div className="flex gap-2">
              {result.categories.map((cat: string) => (
                <span key={cat} className="text-sm bg-gray-100 px-2 py-1 rounded">
                  {cat}
                </span>
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  )
}
```

### Real-Time Search with Client Component

**Client-Side Search:**

```tsx
// src/components/SearchInput.tsx
'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'

export function SearchInput() {
  const [query, setQuery] = useState('')
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search articles..."
        className="w-full px-4 py-2 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>
    </form>
  )
}
```

## Media Management

### Media Collection Configuration

The template includes a pre-configured media collection with upload capabilities:

```ts
// src/collections/Media/index.ts
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig<'media'> = {
  slug: 'media',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
      admin: {
        description: 'Alternative text for accessibility and SEO',
      },
    },
    {
      name: 'caption',
      type: 'text',
      admin: {
        description: 'Optional caption displayed below the image',
      },
    },
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
        position: 'center',
      },
      {
        name: 'small',
        width: 800,
        height: 600,
        fit: 'cover',
        position: 'center',
      },
      {
        name: 'medium',
        width: 1200,
        height: 800,
        fit: 'cover',
        position: 'center',
      },
      {
        name: 'large',
        width: 1920,
        height: 1080,
        fit: 'cover',
        position: 'center',
      },
    ],
    focalPoint: true,
  },
}
```

### Upload Configuration Options

**Supported MIME Types:**

```ts
mimeTypes: [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',
  'video/mp4',
  'video/webm',
  'video/ogg',
]
```

**Image Size Presets:**

| Size | Dimensions | Use Case |
|------|------------|----------|
| thumbnail | 400 x 300 | Avatars, thumbnails, cards |
| small | 800 x 600 | Sidebar images, blog excerpts |
| medium | 1200 x 800 | Blog post content, features |
| large | 1920 x 1080 | Hero sections, full-width banners |

### Focal Point Cropping

**How It Works:**

Focal point allows editors to specify the important area of an image that should remain visible when cropped to different sizes.

**Media Document with Focal Point:**

```ts
{
  id: 'media-doc-id',
  url: '/media/image.jpg',
  filename: 'image.jpg',
  mimeType: 'image/jpeg',
  filesize: 123456,
  width: 1920,
  height: 1080,
  alt: 'Conference presentation',
  focalPoint: {
    x: 0.6, // Horizontal position (0 = left, 1 = right)
    y: 0.3, // Vertical position (0 = top, 1 = bottom)
  },
}
```

**Using Focal Point in Admin:**

1. Upload an image in the admin panel
2. Click and drag the focal point marker on the image
3. Save the document
4. All generated sizes will crop around the focal point

### Using Media in Frontend

**Basic Image Display:**

```tsx
import Image from 'next/image'

export function MediaDisplay({ media }) {
  return (
    <div className="relative">
      <Image
        src={media.url}
        alt={media.alt || 'Media'}
        width={1200}
        height={600}
      />
      {media.caption && (
        <p className="mt-2 text-sm text-gray-600">{media.caption}</p>
      )}
    </div>
  )
}
```

**Using Pre-generated Sizes:**

```tsx
export function ResponsiveMedia({ media, size = 'medium' }) {
  const sizeConfig = {
    thumbnail: { width: 400, height: 300 },
    small: { width: 800, height: 600 },
    medium: { width: 1200, height: 800 },
    large: { width: 1920, height: 1080 },
  }

  const { width, height } = sizeConfig[size]

  return (
    <Image
      src={media.url}
      alt={media.alt || 'Media'}
      width={width}
      height={height}
      sizes={`(max-width: ${width}px) 100vw, ${width}px`}
    />
  )
}
```

**Hero Image with Focal Point:**

```tsx
export function HeroImage({ media }) {
  return (
    <div className="relative h-[600px] w-full">
      <Image
        src={media.url}
        alt={media.alt || 'Hero'}
        fill
        style={{ objectFit: 'cover', objectPosition: `${media.focalPoint?.x || 0.5} ${media.focalPoint?.y || 0.5}` }}
        priority
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
    </div>
  )
}
```

### Video Support

**Video Display Component:**

```tsx
export function VideoDisplay({ media }) {
  if (!media.url.startsWith('video/')) {
    return null
  }

  return (
    <div className="relative">
      <video
        controls
        poster={media.thumbnail?.url}
        className="w-full rounded-lg"
      >
        <source src={media.url} type={media.mimeType} />
        Your browser does not support the video tag.
      </video>
      {media.caption && (
        <p className="mt-2 text-sm text-gray-600">{media.caption}</p>
      )}
    </div>
  )
}
```

## Image Optimization with Sharp

### Sharp Configuration

The template uses Sharp for image processing:

```ts
// payload.config.ts
import sharp from 'sharp'

export default buildConfig({
  // ...
  sharp, // Enable Sharp for image processing
})
```

### Advanced Image Processing

**Custom Image Transformations:**

```ts
// Custom resize with Sharp
import sharp from 'sharp'

async function customResize(buffer: Buffer, options: { width: number; height: number }) {
  const processed = await sharp(buffer)
    .resize(options.width, options.height, {
      fit: 'cover',
      position: 'center',
    })
    .webp({ quality: 80 })
    .toBuffer()

  return processed
}
```

**WebP Conversion:**

```ts
// Automatically convert to WebP
imageSizes: [
  {
    name: 'webp-small',
    width: 800,
    height: 600,
    fit: 'cover',
  },
]

// In frontend, use Next.js Image which auto-converts to WebP
<Image src={media.url} alt={media.alt} />
```

### Media Block Implementation

**Media Block Configuration:**

```ts
// src/blocks/MediaBlock/config.ts
import type { Block } from 'payload'

export const MediaBlock: Block = {
  slug: 'mediaBlock',
  fields: [
    {
      name: 'media',
      type: 'upload',
      relationTo: 'media',
      required: true,
    },
    {
      name: 'align',
      type: 'select',
      options: [
        { label: 'Left', value: 'left' },
        { label: 'Center', value: 'center' },
        { label: 'Right', value: 'right' },
      ],
      defaultValue: 'left',
    },
    {
      name: 'size',
      type: 'select',
      options: [
        { label: 'Small', value: 'small' },
        { label: 'Medium', value: 'medium' },
        { label: 'Large', value: 'large' },
      ],
      defaultValue: 'medium',
    },
    {
      name: 'caption',
      type: 'text',
    },
    {
      name: 'links',
      type: 'array',
      fields: [
        {
          name: 'label',
          type: 'text',
        },
        {
          name: 'url',
          type: 'text',
        },
        {
          name: 'newTab',
          type: 'checkbox',
        },
      ],
    },
  ],
}
```

**Media Block Component:**

```tsx
// src/blocks/MediaBlock/Client.tsx
import Image from 'next/image'
import Link from 'next/link'

export function MediaBlock({ media, align = 'left', size = 'medium', caption, links }) {
  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-2xl',
    large: 'max-w-4xl',
  }

  const alignClasses = {
    left: 'items-start',
    center: 'items-center',
    right: 'items-end',
  }

  return (
    <div className={`flex ${alignClasses[align]} mb-12`}>
      <div className={`${sizeClasses[size]} w-full`}>
        {media.mimeType.startsWith('video/') ? (
          <video controls className="w-full rounded-lg">
            <source src={media.url} type={media.mimeType} />
          </video>
        ) : (
          <Image
            src={media.url}
            alt={media.alt || 'Media'}
            width={1200}
            height={600}
            className="w-full rounded-lg"
          />
        )}
        
        {caption && (
          <p className="mt-3 text-sm text-gray-600 text-center">{caption}</p>
        )}
        
        {links && links.length > 0 && (
          <div className="flex gap-4 mt-4 justify-center">
            {links.map((link, index) => (
              <Link
                key={index}
                href={link.url}
                target={link.newTab ? '_blank' : '_self'}
                rel={link.newTab ? 'noopener noreferrer' : undefined}
                className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

## Storage Adapters

### Local Storage (Default)

Files are stored in the `media/` directory:

```ts
upload: {
  staticDir: 'media',
}
```

### Vercel Blob Storage

**Installation:**

```bash
pnpm add @payloadcms/storage-vercel-blob
```

**Configuration:**

```ts
// payload.config.ts
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

export default buildConfig({
  // ...
  plugins: [
    vercelBlobStorage({
      collections: {
        media: true, // Enable for media collection
      },
      token: process.env.BLOB_READ_WRITE_TOKEN || '',
    }),
  ],
})
```

### AWS S3 Storage

**Installation:**

```bash
pnpm add @payloadcms/storage-s3
```

**Configuration:**

```ts
// payload.config.ts
import { s3Storage } from '@payloadcms/storage-s3'

export default buildConfig({
  // ...
  plugins: [
    s3Storage({
      collections: {
        media: true,
      },
      bucketName: process.env.S3_BUCKET_NAME || '',
      accessKeyId: process.env.S3_ACCESS_KEY_ID || '',
      secretAccessKey: process.env.S3_SECRET_ACCESS_KEY || '',
      region: process.env.S3_REGION || 'us-east-1',
    }),
  ],
})
```

## Best Practices

### Search Optimization

1. **Index relevant content**: Only index collections that need search
2. **Transform for search**: Extract key information in `beforeSync`
3. **Filter unpublished**: Don't index drafts or unpublished content
4. **Update on change**: Ensure search index updates when content changes
5. **Provide feedback**: Show "no results" messages clearly

### Media Management

1. **Use descriptive filenames**: `conference-keynote-2024.jpg` not `IMG_1234.jpg`
2. **Always add alt text**: Required for accessibility and SEO
3. **Set focal points**: Ensure important areas stay in frame
4. **Choose appropriate sizes**: Don't use large images for thumbnails
5. **Optimize before upload**: Compress images before uploading when possible

### Image Performance

1. **Use Next.js Image component**: Auto-optimizes and serves WebP
2. **Set explicit sizes**: Help browser allocate space (prevents CLS)
3. **Lazy load below-fold**: Don't use `priority` for all images
4. **Use appropriate quality**: 75-80% quality is usually sufficient
5. **Consider CDN**: Use CDN for global image delivery

### File Size Guidelines

| Type | Max Size | Recommended |
|------|----------|-------------|
| Hero images | 500 KB | 200-300 KB |
| Blog images | 300 KB | 100-200 KB |
| Thumbnails | 50 KB | 20-30 KB |
| Icons/Logos | 50 KB | 10-20 KB |

## Troubleshooting

### Search Not Working

**Check:**
- Search plugin is configured in plugins array
- Collections are listed in `collections` option
- Documents have `_status: 'published'`
- Search index has documents (check admin panel)

### Images Not Loading

**Check:**
- Media URL is accessible
- Image dimensions are set correctly
- Next.js images domain is configured (for external images)
- File exists in storage location

### Upload Failing

**Check:**
- File size is within limits
- MIME type is allowed
- Storage adapter is configured correctly
- Write permissions on storage location

## Next Steps

After implementing search and media, explore:
- [Customizations](08-customizations.md) - Extending with custom components and functionality
