# Next.js Integration

This reference covers integrating Payload CMS with Next.js App Router, including data fetching, server components, routing, caching strategies, and deployment considerations.

## Project Structure

### Template Directory Layout

```
src/
├── app/                          # Next.js App Router
│   ├── (frontend)/               # Frontend route group
│   │   ├── [slug]/              # Dynamic page routes
│   │   ├── posts/               # Blog listing and post routes
│   │   ├── search/              # Search results page
│   │   ├── layout.tsx           # Frontend layout
│   │   └── page.tsx             # Homepage
│   ├── (payload)/               # Payload admin route group
│   │   └── admin/               # Admin panel mount point
│   ├── api/                     # API routes
│   │   └── revalidate/          # On-demand revalidation endpoint
│   └── layout.tsx               # Root layout
├── blocks/                       # Layout block components
│   ├── ArchiveBlock/
│   ├── CallToAction/
│   ├── Content/
│   ├── Form/
│   ├── MediaBlock/
│   └── RenderBlocks.tsx         # Block router component
├── collections/                  # Payload collection configs
├── components/                   # Shared React components
├── Footer/                       # Footer global component
├── Header/                       # Header global component
├── heros/                        # Hero section components
│   ├── RenderHero.tsx           # Hero router component
│   └── types.ts                 # Hero type definitions
├── hooks/                        # Payload hooks
├── payload.config.ts            # Main Payload configuration
├── plugins.ts                    # Plugin configurations
└── utilities/                    # Helper functions
```

## App Router Configuration

### Route Groups

The template uses route groups to organize routes without affecting URL structure:

**`(frontend)` Group:**

- All public-facing website pages
- Shared layout with Header, Footer, and global styles
- Dynamic routing for pages and posts

**`(payload)` Group:**

- Payload admin panel at `/admin`
- GraphQL API at `/api/graphql`
- REST API at `/api/:collection`

### Layout Components

**Root Layout:**

```tsx
// src/app/layout.tsx
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'

export const metadata: Metadata = {
  title: 'Payload Website Template',
  description: 'Built with Payload and Next.js',
}

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        {children}
      </body>
    </html>
  )
}
```

**Frontend Layout:**

```tsx
// src/app/(frontend)/layout.tsx
import { Header } from '@/Header/Client'
import { Footer } from '@/Footer/Client'

export default function FrontendLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <Header />
      <main>{children}</main>
      <Footer />
    </>
  )
}
```

## Data Fetching Patterns

### Server-Side Data Fetching

**Using Payload Local API in Server Components:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import { getPayload } from 'payload'
import configPromise from '@payload-config'
import { draftMode } from 'next/headers'
import { cache } from 'react'

// Initialize Payload (cached across requests)
const getPayloadInstance = cache(async () => {
  return await getPayload({ config: configPromise })
})

// Query function (also cached)
const queryPageBySlug = cache(async ({ slug }: { slug: string }) => {
  const payload = await getPayloadInstance()
  const { isEnabled: draft } = await draftMode()

  const result = await payload.find({
    collection: 'pages',
    where: { slug: { equals: slug } },
    draft: draft, // Respect draft mode
    overrideAccess: false, // Enforce access control
  })

  return result.docs[0] || null
})

export default async function Page({ params }) {
  const { slug = 'home' } = await params
  const decodedSlug = decodeURIComponent(slug)

  const page = await queryPageBySlug({ slug: decodedSlug })

  if (!page) {
    return <PayloadRedirects url={`/${decodedSlug}`} />
  }

  return (
    <article>
      <RenderHero {...page.hero} />
      <RenderBlocks blocks={page.layout} />
    </article>
  )
}
```

### Fetching with Select and Populate

**Optimize Queries with Field Selection:**

```ts
const page = await payload.find({
  collection: 'pages',
  where: { slug: { equals: 'about' } },
  select: {
    title: true,
    slug: true,
    hero: true,
    layout: true,
    meta: {
      title: true,
      description: true,
      image: true,
    },
  },
})
```

**Populate Relationships:**

```ts
const post = await payload.findByID({
  collection: 'posts',
  id: 'post-id-123',
  populate: {
    categories: true,
    heroImage: true,
    relatedPosts: {
      select: {
        title: true,
        slug: true,
        meta: { image: true, description: true },
      },
    },
  },
})
```

### Global Data Fetching

**Fetching Header Navigation:**

```tsx
// src/Header/Client.tsx
import { getPayload } from 'payload'
import configPromise from '@payload-config'
import { cache } from 'react'

const fetchHeader = cache(async () => {
  const payload = await getPayload({ config: configPromise })
  const header = await payload.findGlobal({
    slug: 'header',
    overrideAccess: false,
  })
  return header
})

export async function Header() {
  const header = await fetchHeader()

  return (
    <header>
      <nav>
        {header?.navItems?.map((item) => (
          <a key={item.id} href={item.url}>
            {item.label}
          </a>
        ))}
      </nav>
    </header>
  )
}
```

**Fetching Footer Content:**

```tsx
// src/Footer/Client.tsx
const fetchFooter = cache(async () => {
  const payload = await getPayload({ config: configPromise })
  const footer = await payload.findGlobal({
    slug: 'footer',
  })
  return footer
})

export async function Footer() {
  const footer = await fetchFooter()

  return (
    <footer>
      <div className="nav-links">
        {footer?.navItems?.map((item) => (
          <a key={item.id} href={item.url}>
            {item.label}
          </a>
        ))}
      </div>
      <div className="social-links">
        {footer?.socialLinks?.map((link) => (
          <a key={link.id} href={link.url}>
            {link.platform}
          </a>
        ))}
      </div>
    </footer>
  )
}
```

## Dynamic Routing

### Generating Static Params

**Pre-render Pages at Build Time:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export async function generateStaticParams() {
  const payload = await getPayload({ config: configPromise })
  const pages = await payload.find({
    collection: 'pages',
    draft: false,
    overrideAccess: false,
    pagination: false,
    select: { slug: true },
  })

  return pages.docs
    .filter((doc) => doc.slug !== 'home') // Home is handled separately
    .map(({ slug }) => ({ slug }))
}
```

**Pre-render Post Pages:**

```tsx
// src/app/(frontend)/posts/[slug]/page.tsx
export async function generateStaticParams() {
  const payload = await getPayload({ config: configPromise })
  const posts = await payload.find({
    collection: 'posts',
    draft: false,
    overrideAccess: false,
    pagination: false,
    select: { slug: true },
  })

  return posts.docs.map(({ slug }) => ({ slug }))
}
```

### Catch-All Routes for Redirects

**Handle Unknown Routes:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import { PayloadRedirects } from '@/components/PayloadRedirects'

export default async function Page({ params }) {
  const { slug = 'home' } = await params
  const decodedSlug = decodeURIComponent(slug)

  const page = await queryPageBySlug({ slug: decodedSlug })

  if (!page) {
    // Check for redirects or return 404
    return <PayloadRedirects url={`/${decodedSlug}`} />
  }

  return <PageContent page={page} />
}
```

## Metadata and SEO

### Per-Page Metadata

**Generate Metadata Dynamically:**

```tsx
// src/app/(frontend)/[slug]/page.tsx
import type { Metadata } from 'next'
import { generateMeta } from '@/utilities/generateMeta'

export async function generateMetadata({
  params,
}): Promise<Metadata> {
  const { slug = 'home' } = await params
  const decodedSlug = decodeURIComponent(slug)

  const page = await queryPageBySlug({ slug: decodedSlug })

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
    title: doc.meta?.title || doc.title,
    description: doc.meta?.description,
    openGraph: {
      title: doc.meta?.title || doc.title,
      description: doc.meta?.description,
      type: doc.slug === 'home' ? 'website' : 'article',
      url,
      images: doc.meta?.image
        ? [`${baseUrl}${doc.meta.image.url}`]
        : undefined,
    },
    twitter: {
      card: 'summary_large_image',
      title: doc.meta?.title || doc.title,
      description: doc.meta?.description,
    },
    alternates: {
      canonical: url,
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

  return generateMeta({ doc: post })
}
```

## Caching Strategies

### Default: No Store (Payload Cloud)

When deployed on Payload Cloud, caching is handled by Cloudflare:

```tsx
// src/app/(frontend)/[slug]/page.tsx
export const dynamic = 'force-dynamic' // Disable static generation

// In API fetch requests
const res = await fetch(payloadURL, {
  cache: 'no-store', // Always fetch fresh data
})
```

### Self-Hosted: Static Generation with Revalidation

For self-hosted deployments, enable Next.js caching:

**Remove Dynamic Export:**

```tsx
// Remove this line for static generation
// export const dynamic = 'force-dynamic'
```

**Add Revalidation:**

```tsx
// Revalidate cached page every hour
export const revalidate = 3600

// Or use on-demand revalidation
export const dynamic = 'force-static'
```

### On-Demand Revalidation

**Revalidate Endpoint:**

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
  const type = searchParams.get('type') // 'page' or 'post'

  if (slug) {
    const path = type === 'post' ? `/posts/${slug}` : `/${slug}`
    revalidatePath(path, 'page')
    return NextResponse.json({ revalidated: true, path })
  }

  return NextResponse.json({ error: 'Missing slug' }, { status: 400 })
}
```

**Trigger from Payload Hooks:**

```ts
// src/collections/Pages/hooks/revalidatePage.ts
export const revalidatePage = async ({ doc, previousDoc }) => {
  if (doc._status === 'published' || previousDoc?._status === 'published') {
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_SERVER_URL}/api/revalidate?slug=${doc.slug}&type=page`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${process.env.PAYLOAD_SECRET}`,
          },
        }
      )
    } catch (error) {
      console.error('Failed to revalidate page:', error)
    }
  }
}
```

## Client Components

### When to Use Client Components

Client components are needed for:
- Interactive state (forms, modals, dropdowns)
- Browser APIs (window, localStorage)
- Event handlers (onClick, onChange)
- Third-party libraries requiring DOM access

### Marking Client Components

```tsx
// src/components/InteractiveComponent.tsx
'use client'

import { useState } from 'react'

export function InteractiveComponent() {
  const [count, setCount] = useState(0)

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  )
}
```

### Client Component Patterns

**Form Components:**

```tsx
// src/blocks/Form/Client.tsx
'use client'

import { useForm } from 'react-hook-form'

export function FormClient({ form }) {
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    // Handle form submission
    console.log('Form data:', data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>Required</span>}
      
      <input {...register('email')} type="email" />
      
      <button type="submit">Submit</button>
    </form>
  )
}
```

**Live Preview Listener:**

```tsx
// src/components/LivePreviewListener.tsx
'use client'

import { useLivePreview } from '@payloadcms/live-preview-react'

export const LivePreviewListener = () => {
  useLivePreview()
  return null // Invisible component
}
```

## API Routes

### Custom API Endpoints

**Creating API Routes:**

```ts
// src/app/api/custom-endpoint/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export async function GET(req: NextRequest) {
  const payload = await getPayload({ config: configPromise })
  
  const { searchParams } = new URL(req.url)
  const id = searchParams.get('id')

  if (!id) {
    return NextResponse.json({ error: 'Missing ID' }, { status: 400 })
  }

  const doc = await payload.findByID({
    collection: 'pages',
    id,
  })

  return NextResponse.json(doc)
}
```

### Webhook Handlers

**Handling Form Submissions:**

```ts
// src/app/api/webhooks/form/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const data = await req.json()

  // Process form submission
  console.log('Form submission:', data)

  // Send email, store in database, etc.

  return NextResponse.json({ success: true })
}
```

## Error Handling

### Not Found Page

```tsx
// src/app/(frontend)/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="mb-8">Page not found</p>
        <Link href="/" className="text-blue-500 hover:underline">
          Return home
        </Link>
      </div>
    </div>
  )
}
```

### Error Boundary

```tsx
// src/app/(frontend)/error.tsx
'use client'

export default function Error({ error, reset }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Error</h1>
        <p className="mb-8">{error.message}</p>
        <button
          onClick={reset}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
```

## Performance Optimization

### Image Optimization

**Using Next.js Image Component:**

```tsx
import Image from 'next/image'

export function MediaDisplay({ media }) {
  return (
    <Image
      src={media.url}
      alt={media.alt}
      width={1200}
      height={600}
      priority={false} // Set true for above-the-fold images
      sizes="(max-width: 768px) 100vw, 50vw"
    />
  )
}
```

### Lazy Loading Blocks

```tsx
import dynamic from 'next/dynamic'

// Lazy load heavy components
const ArchiveBlock = dynamic(
  () => import('@/blocks/Archive/Client'),
  { loading: () => <div>Loading...</div> }
)

export function RenderBlocks({ blocks }) {
  return blocks.map((block) => {
    if (block.blockType === 'archive') {
      return <ArchiveBlock key={block.id} {...block} />
    }
    // Other blocks...
  })
}
```

### Font Optimization

```tsx
// src/app/layout.tsx
import { Geist, Geist_Mono } from 'next/font/google'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
  preload: true,
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
  preload: true,
})
```

## Deployment Considerations

### Environment Variables

**Required for Production:**

```env
PAYLOAD_SECRET=your-production-secret
DATABASE_URL=production-database-url
PAYLOAD_PUBLIC_SERVER_URL=https://your-domain.com
```

**Optional for Features:**

```env
# Vercel deployment
POSTGRES_URL=postgresql://...
BLOB_READ_WRITE_TOKEN=vercel-blob-token

# Cron jobs (scheduled publishing)
CRON_SECRET=your-cron-secret

# Admin bar (Payload Cloud)
NEXT_PUBLIC_PAYLOAD_ADMIN_BAR_ID=admin-bar-id
```

### Build and Start Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "postbuild": "next-sitemap --config next-sitemap.config.cjs",
    "start": "next start"
  }
}
```

### Vercel Configuration

**vercel.json:**

```json
{
  "framework": "nextjs",
  "crons": [
    {
      "path": "/api/cron/scheduled-publish",
      "schedule": "0 * * * *"
    }
  ]
}
```

## Debugging and Development

### Development Tools

**Enable Next.js DevTools:**

```bash
NDEBUG=false pnpm dev
```

**Payload Debug Mode:**

```ts
// In payload.config.ts
export default buildConfig({
  // ...
  telemetry: {
    enabled: true, // Send anonymous usage data
  },
})
```

### Logging

```ts
// Custom logger for API requests
const logger = async (req: PayloadRequest) => {
  console.log(`${req.method} ${req.url}`)
}

export default buildConfig({
  // ...
  expressMiddleware: [logger],
})
```

## Next Steps

After mastering Next.js integration, explore:
- [SEO and i18n](05-seo-and-i18n.md) - Search engine optimization and internationalization
- [Form Builder](06-form-builder.md) - Creating forms with email handlers
- [Search and Media](07-search-and-media.md) - Full-text search and media management
- [Customizations](08-customizations.md) - Extending the template
