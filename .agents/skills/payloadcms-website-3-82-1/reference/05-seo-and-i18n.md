# SEO and Internationalization

This reference covers search engine optimization features, metadata management, sitemaps, redirects, and internationalization (i18n) setup for the Payload CMS Website Template.

## SEO Plugin Configuration

### Overview

The template uses `@payloadcms/plugin-seo` to provide comprehensive SEO controls directly in the admin panel. The plugin adds meta fields to collections and provides utilities for generating SEO data.

### Plugin Setup

```ts
// src/plugins/index.ts
import { seoPlugin } from '@payloadcms/plugin-seo'
import { GenerateTitle, GenerateURL } from '@payloadcms/plugin-seo/types'
import { Page, Post } from '@/payload-types'
import { getServerSideURL } from '@/utilities/getURL'

const generateTitle: GenerateTitle<Post | Page> = ({ doc }) => {
  return doc?.title 
    ? `${doc.title} | Payload Website Template` 
    : 'Payload Website Template'
}

const generateURL: GenerateURL<Post | Page> = ({ doc }) => {
  const url = getServerSideURL()
  return doc?.slug ? `${url}/${doc.slug}` : url
}

export const plugins: Plugin[] = [
  seoPlugin({
    collections: ['pages', 'posts'], // Collections to add SEO fields to
    generateTitle,
    generateURL,
  }),
]
```

### SEO Fields Added

The plugin automatically adds these fields to configured collections:

**Meta Tab Fields:**

| Field | Type | Description | Auto-Generate |
|-------|------|-------------|---------------|
| `meta.title` | text | Page title for search results | Yes (from doc title) |
| `meta.description` | text | Meta description snippet | No |
| `meta.image` | upload | Open Graph/social sharing image | No |

**Overview Field:**

Shows a summary of all SEO fields in one place:

```ts
OverviewField({
  titlePath: 'meta.title',
  descriptionPath: 'meta.description',
  imagePath: 'meta.image',
})
```

**Preview Field:**

Displays a live preview of how the page will appear in search results and social shares:

```ts
PreviewField({
  hasGenerateFn: true, // URL is auto-generated
  titlePath: 'meta.title',
  descriptionPath: 'meta.description',
})
```

### Using SEO Fields in Collections

**Pages Collection:**

```ts
// src/collections/Pages/index.ts
import {
  MetaDescriptionField,
  MetaImageField,
  MetaTitleField,
  OverviewField,
  PreviewField,
} from '@payloadcms/plugin-seo/fields'

export const Pages: CollectionConfig<'pages'> = {
  // ...
  fields: [
    // ... other fields
    {
      type: 'tabs',
      tabs: [
        // ... other tabs
        {
          name: 'meta',
          label: 'SEO',
          fields: [
            OverviewField({
              titlePath: 'meta.title',
              descriptionPath: 'meta.description',
              imagePath: 'meta.image',
            }),
            MetaTitleField({
              hasGenerateFn: true, // Auto-generate from title
            }),
            MetaImageField({
              relationTo: 'media', // Upload field relation
            }),
            MetaDescriptionField({}),
            PreviewField({
              hasGenerateFn: true,
              titlePath: 'meta.title',
              descriptionPath: 'meta.description',
            }),
          ],
        },
      ],
    },
  ],
}
```

## Metadata Generation

### Next.js Metadata API

The template uses Next.js 13+ Metadata API for SEO:

**Page-Level Metadata:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import type { Metadata } from 'next'
import { generateMeta } from '@/utilities/generateMeta'

export async function generateMetadata({
  params,
}): Promise<Metadata> {
  const { slug = 'home' } = await params
  const page = await queryPageBySlug({ slug })

  return generateMeta({ doc: page })
}
```

**Metadata Generation Utility:**

```ts
// src/utilities/generateMeta.ts
import type { Metadata } from 'next'
import type { Page, Post } from '@/payload-types'

export const generateMeta = ({
  doc,
}: {
  doc: Page | Post | null
}): Metadata => {
  if (!doc) {
    return {
      title: 'Page Not Found',
      description: 'The page you requested could not be found.',
      robots: 'noindex, nofollow',
    }
  }

  const baseUrl = process.env.PAYLOAD_PUBLIC_SERVER_URL || 'http://localhost:3000'
  const url = `${baseUrl}/${doc.slug}`

  return {
    // Basic metadata
    title: doc.meta?.title || doc.title,
    description: doc.meta?.description,
    
    // Open Graph data
    openGraph: {
      title: doc.meta?.title || doc.title,
      description: doc.meta?.description,
      type: doc.slug === 'home' ? 'website' : 'article',
      url,
      locale: 'en_US',
      siteName: 'Payload Website Template',
      images: doc.meta?.image
        ? [
            {
              url: `${baseUrl}${doc.meta.image.url}`,
              width: 1200,
              height: 630,
              alt: doc.meta?.title || doc.title,
            },
          ]
        : undefined,
    },

    // Twitter Card data
    twitter: {
      card: 'summary_large_image',
      title: doc.meta?.title || doc.title,
      description: doc.meta?.description,
      images: doc.meta?.image ? [`${baseUrl}${doc.meta.image.url}`] : undefined,
    },

    // Canonical URL
    alternates: {
      canonical: url,
    },

    // Robots directives
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
  }
}
```

### Post-Specific Metadata

```tsx
// src/app/(frontend)/posts/[slug]/page.tsx
export async function generateMetadata({
  params,
}): Promise<Metadata> {
  const { slug } = await params
  const post = await queryPostBySlug({ slug })

  if (!post) {
    return {
      title: 'Post Not Found',
      description: 'The post you requested could not be found.',
      robots: 'noindex, nofollow',
    }
  }

  const baseUrl = process.env.PAYLOAD_PUBLIC_SERVER_URL
  const url = `${baseUrl}/posts/${post.slug}`

  return {
    title: post.meta?.title || post.title,
    description: post.meta?.description,
    openGraph: {
      title: post.meta?.title || post.title,
      description: post.meta?.description,
      type: 'article',
      url,
      publishedTime: post.publishedAt,
      authors: post.authors?.map((author) => author.name),
      images: post.meta?.image
        ? [`${baseUrl}${post.meta.image.url}`]
        : post.heroImage
        ? [`${baseUrl}${post.heroImage.url}`]
        : undefined,
    },
    alternates: {
      canonical: url,
    },
  }
}
```

## Sitemap Generation

### Configuration

The template uses `next-sitemap` for automatic sitemap generation:

**next-sitemap.config.cjs:**

```js
/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: process.env.PAYLOAD_PUBLIC_SERVER_URL || 'http://localhost:3000',
  generateRobotsTxt: true,
  exclude: ['/admin/*', '/api/*'],
  robotsTxtOptions: {
    policies: [
      {
        userAgent: '*',
        allow: '/',
      },
    ],
  },
}
```

### Post-Build Sitemap Generation

```json
{
  "scripts": {
    "build": "next build",
    "postbuild": "next-sitemap --config next-sitemap.config.cjs"
  }
}
```

This generates:
- `sitemap.xml` - Main sitemap with all pages
- `robots.txt` - Robot exclusion rules

### Dynamic Sitemap Route (Alternative)

For large sites with frequent updates, use dynamic sitemap generation:

```tsx
// src/app/sitemap.ts
import { MetadataRoute } from 'next'
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const payload = await getPayload({ config: configPromise })
  const baseUrl = process.env.PAYLOAD_PUBLIC_SERVER_URL || 'http://localhost:3000'

  // Fetch all published pages
  const pages = await payload.find({
    collection: 'pages',
    where: { _status: { equals: 'published' } },
    overrideAccess: false,
    select: { slug: true, updatedAt: true },
  })

  // Fetch all published posts
  const posts = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    overrideAccess: false,
    select: { slug: true, updatedAt: true },
  })

  const pageEntries = pages.docs.map((page) => ({
    url: `${baseUrl}/${page.slug}`,
    lastModified: page.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: page.slug === 'home' ? 1 : 0.8,
  }))

  const postEntries = posts.docs.map((post) => ({
    url: `${baseUrl}/posts/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }))

  return [...pageEntries, ...postEntries]
}
```

## Redirects Plugin

### Configuration

The template uses `@payloadcms/plugin-redirects` for managing URL redirects:

```ts
// src/plugins/index.ts
import { redirectsPlugin } from '@payloadcms/plugin-redirects'
import { revalidateRedirects } from '@/hooks/revalidateRedirects'

export const plugins: Plugin[] = [
  redirectsPlugin({
    collections: ['pages', 'posts'], // Collections to generate redirects for
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
  }),
]
```

### Creating Redirects

**Via Admin Panel:**

1. Navigate to `/admin` → Collections → Redirects
2. Click "New Redirect"
3. Fill in fields:
   - **From**: Old URL path (e.g., `/old-page`)
   - **To**: New URL path or external URL
   - **Type**: 301 (permanent) or 302 (temporary)

**Via Local API:**

```ts
const redirect = await payload.create({
  collection: 'redirects',
  data: {
    from: '/old-page-slug',
    to: '/new-page-slug',
    type: 301, // Permanent redirect
  },
})
```

### Redirect Types

| Type | Status Code | Use Case |
|------|-------------|----------|
| 301 | Moved Permanently | SEO-friendly, permanent URL changes |
| 302 | Found (Temporary) | Temporary redirects, A/B testing |

### Using Redirects in Frontend

**PayloadRedirects Component:**

```tsx
// src/components/PayloadRedirects.tsx
import { getPayload } from 'payload'
import configPromise from '@payload-config'
import { redirect } from 'next/navigation'
import { notFound } from 'next/navigation'

export async function PayloadRedirects({
  url,
  disableNotFound = false,
}: {
  url: string
  disableNotFound?: boolean
}) {
  const payload = await getPayload({ config: configPromise })
  
  const redirects = await payload.find({
    collection: 'redirects',
    where: {
      from: { equals: url },
    },
  })

  if (redirects.docs.length > 0) {
    const redirectDoc = redirects.docs[0]
    const isExternal = redirectDoc.to.startsWith('http')
    
    if (isExternal) {
      return redirect(redirectDoc.to)
    }
    
    return redirect(`${redirectDoc.to}`)
  }

  if (!disableNotFound) {
    notFound()
  }

  return null
}
```

**Usage in Pages:**

```tsx
export default async function Page({ params }) {
  const { slug } = await params
  const page = await queryPageBySlug({ slug })

  if (!page) {
    // Check for redirects or show 404
    return <PayloadRedirects url={`/${slug}`} />
  }

  return <PageContent page={page} />
}
```

## Internationalization (i18n)

### Setup Overview

While the template doesn't include i18n by default, it can be added using Next.js internationalization features.

### Installing i18n Dependencies

```bash
pnpm add next-intl
```

### Configuration

**next.config.js:**

```js
import {i18n} from './src/i18n-config'

/** @type {import('next').NextConfig} */
const nextConfig = {
  i18n,
}

export default nextConfig
```

**i18n-config.ts:**

```ts
export const i18n = {
  locales: ['en', 'de', 'fr'],
  defaultLocale: 'en',
}
```

### Locale-Specific Content

**Option 1: Duplicate Collections**

Create locale-specific versions of collections:

```ts
collections: [
  {
    slug: 'pages-en',
    fields: [/* English fields */],
  },
  {
    slug: 'pages-de',
    fields: [/* German fields */],
  },
]
```

**Option 2: Localization Fields**

Add localized fields to existing collections:

```ts
{
  name: 'title',
  type: 'text',
  required: true,
}
{
  name: 'title_de',
  type: 'text',
}
{
  name: 'title_fr',
  type: 'text',
}
```

**Option 3: Relationship-Based Localization**

Create a separate localization collection:

```ts
{
  slug: 'localizations',
  fields: [
    {
      name: 'locale',
      type: 'select',
      options: ['en', 'de', 'fr'],
    },
    {
      name: 'document',
      type: 'relationship',
      relationTo: ['pages', 'posts'],
    },
    {
      name: 'title',
      type: 'text',
    },
    {
      name: 'content',
      type: 'richText',
    },
  ],
}
```

### Using next-intl

**App Router with i18n:**

```tsx
// src/app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'

export default async function LocaleLayout({
  children,
  params: { locale },
}) {
  const messages = await getMessages()

  return (
    <NextIntlClientProvider messages={messages}>
      {children}
    </NextIntlClientProvider>
  )
}
```

**Locale-Specific Messages:**

```ts
// src/messages/en.json
{
  "Navigation": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  }
}

// src/messages/de.json
{
  "Navigation": {
    "home": "Startseite",
    "about": "Über uns",
    "contact": "Kontakt"
  }
}
```

### SEO with i18n

**Hreflang Tags:**

```tsx
export async function generateMetadata({
  params: { locale },
}): Promise<Metadata> {
  const page = await queryPageBySlug({ slug: params.slug, locale })

  return {
    // ... other metadata
    alternates: {
      canonical: `${baseUrl}/${locale}/${page.slug}`,
      languages: {
        'en': `${baseUrl}/en/${page.slug}`,
        'de': `${baseUrl}/de/${page.slug}`,
        'fr': `${baseUrl}/fr/${page.slug}`,
      },
    },
  }
}
```

## Robots and Indexing

### Robots.txt

Generated automatically by `next-sitemap`:

```
User-agent: *
Allow: /

Sitemap: https://your-domain.com/sitemap.xml
```

**Custom Rules:**

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /search/

Sitemap: https://your-domain.com/sitemap.xml
```

### Meta Robots

Control indexing per page:

```tsx
export async function generateMetadata(): Promise<Metadata> {
  return {
    robots: {
      index: true,      // Allow search engines to index
      follow: true,     // Follow links on the page
      noarchive: false, // Allow caching of page copies
      googleBot: {
        index: true,
        follow: true,
      },
    },
  }
}
```

**Draft Pages - No Index:**

```tsx
const { isEnabled: draft } = await draftMode()

export async function generateMetadata(): Promise<Metadata> {
  return {
    robots: draft ? { index: false, follow: false } : { index: true, follow: true },
  }
}
```

## Open Graph and Social Sharing

### Image Best Practices

**Recommended Specifications:**

| Platform | Recommended Size | Format | Max File Size |
|----------|-----------------|--------|---------------|
| Facebook | 1200 x 630 px | JPG/PNG | 8 MB |
| Twitter | 1200 x 600 px | JPG/PNG/GIF | 5 MB |
| LinkedIn | 1200 x 627 px | JPG/PNG | 5 MB |
| Slack | 1200 x 640 px | JPG/PNG | 100 KB |

**Using Media Collection:**

```ts
// Configure image size for social sharing
imageSizes: [
  {
    name: 'social',
    width: 1200,
    height: 630,
    fit: 'cover',
  },
]
```

### Rich Snippets

**Article Schema:**

```tsx
export async function generateMetadata(): Promise<Metadata> {
  return {
    metadataBase: new URL(baseUrl),
    openGraph: {
      type: 'article',
      publishedTime: post.publishedAt,
      modifiedTime: post.updatedAt,
      authors: post.authors?.map((a) => a.name),
      section: post.categories?.map((c) => c.name),
    },
  }
}
```

**JSON-LD Structured Data:**

```tsx
// src/components/StructuredData.tsx
export function StructuredData({ post }) {
  const jsonData = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    'headline': post.title,
    'datePublished': post.publishedAt,
    'dateModified': post.updatedAt,
    'author': post.authors?.map((a) => ({
      '@type': 'Person',
      'name': a.name,
    })),
    'image': post.meta?.image?.url,
    'description': post.meta?.description,
    'publisher': {
      '@type': 'Organization',
      'name': 'Payload Website Template',
      'logo': {
        '@type': 'ImageObject',
        'url': `${baseUrl}/logo.png`,
      },
    },
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonData) }}
    />
  )
}
```

## Performance and SEO

### Core Web Vitals

**Metrics to Optimize:**

| Metric | Target | How to Improve |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | Optimize hero images, use CDN |
| FID (First Input Delay) | < 100ms | Minimize JavaScript, code splitting |
| CLS (Cumulative Layout Shift) | < 0.1 | Set image dimensions, reserve space |

**Image Optimization:**

```tsx
import Image from 'next/image'

<MediaBlock media={media}>
  <Image
    src={media.url}
    alt={media.alt}
    width={1200}
    height={630}
    priority={true} // For above-the-fold images
    sizes="(max-width: 768px) 100vw, 1200px"
  />
</MediaBlock>
```

### Preloading Critical Resources

```tsx
export default function Layout() {
  return (
    <html>
      <head>
        <link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

## Testing SEO

### Validation Tools

**Google Search Console:**
- Submit sitemap.xml
- Monitor indexing status
- Check for crawl errors
- View search performance

**Rich Results Test:**
- Validate structured data
- Test rich snippet appearance
- https://search.google.com/test/rich-results

**Facebook Debugger:**
- Debug Open Graph tags
- Scrape and preview
- https://developers.facebook.com/tools/debug/

**Twitter Card Validator:**
- Verify Twitter card data
- https://cards-dev.twitter.com/validator

### Manual Testing

**Check Meta Tags:**

```bash
# View page source and grep for meta tags
curl -s https://your-domain.com/about | grep -i '<meta'

# Check viewport, charset, title, description, OG tags
```

**Test Redirects:**

```bash
# Check redirect chain and status code
curl -I https://your-domain.com/old-page
# Should return 301 or 302 with Location header
```

## Next Steps

After implementing SEO and i18n, explore:
- [Form Builder](06-form-builder.md) - Creating forms with email handlers
- [Search and Media](07-search-and-media.md) - Full-text search capabilities
- [Customizations](08-customizations.md) - Extending template functionality
