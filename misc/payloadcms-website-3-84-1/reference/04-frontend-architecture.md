# Frontend Architecture

## Next.js App Router Structure

The frontend is organized under `src/app/(frontend)/` using Next.js App Router with React Server Components. The `(frontend)` directory is a route group — it does not affect the URL path.

```
src/app/(frontend)/
├── layout.tsx           # Root layout: fonts, providers, Header, Footer, AdminBar
├── page.tsx             # Home page (delegates to [slug]/page)
├── [slug]/              # Dynamic page routes
│   ├── page.tsx         # Page template with draft mode and Local API
│   └── page.client.tsx  # Client-side interactivity for pages
├── posts/
│   └── [slug]/          # Dynamic post routes
│       ├── page.tsx     # Post template
│       └── page.client.tsx
├── search/              # Search results page
├── next/preview/        # Draft preview endpoint (route handler)
├── (sitemaps)/          # XML sitemap generation
├── globals.css          # Global styles with CSS variables
└── not-found.tsx        # Custom 404 page
```

## Root Layout

The frontend root layout provides the shared shell:

```typescript
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const { isEnabled } = await draftMode()

  return (
    <html className={cn(GeistSans.variable, GeistMono.variable)} lang="en" suppressHydrationWarning>
      <head>
        <InitTheme />
        <link href="/favicon.ico" rel="icon" sizes="32x32" />
        <link href="/favicon.svg" rel="icon" type="image/svg+xml" />
      </head>
      <body>
        <Providers>
          <AdminBar adminBarProps={{ preview: isEnabled }} />
          <Header />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
```

Key components:

- **AdminBar** — Payload's admin bar component, shows preview indicator when draft mode is active
- **Header** — Renders navigation from the Header global
- **Footer** — Renders footer links from the Footer global
- **Providers** — React context providers (theme, etc.)
- **InitTheme** — Initializes dark/light theme before hydration

## Page Template Pattern

The page template demonstrates the core pattern for all frontend pages:

```typescript
export default async function Page({ params: paramsPromise }: Args) {
  const { isEnabled: draft } = await draftMode()
  const { slug = 'home' } = await paramsPromise
  const decodedSlug = decodeURIComponent(slug)

  const page = await queryPageBySlug({ slug: decodedSlug })

  if (!page) return <PayloadRedirects url={'/' + decodedSlug} />

  return (
    <article className="pt-16 pb-24">
      <PayloadRedirects disableNotFound url={'/' + decodedSlug} />
      {draft && <LivePreviewListener />}
      <RenderHero {...page.hero} />
      <RenderBlocks blocks={page.layout} />
    </article>
  )
}
```

Key patterns:

1. **Async params** — Next.js 15+ passes params as a Promise that must be awaited
2. **Draft mode check** — `draftMode()` from `next/headers` determines if viewing a draft
3. **Slug decoding** — `decodeURIComponent` handles special characters in URLs
4. **Redirect fallback** — `PayloadRedirects` component checks for redirects before showing 404
5. **Live preview listener** — Only rendered when in draft mode, enables real-time preview updates

## Cached Data Queries

The template uses React's `cache` function to memoize database queries within a single request:

```typescript
const queryPageBySlug = cache(async ({ slug }: { slug: string }) => {
  const { isEnabled: draft } = await draftMode()
  const payload = await getPayload({ config: configPromise })

  const result = await payload.find({
    collection: 'pages',
    draft,
    limit: 1,
    pagination: false,
    overrideAccess: draft,
    where: { slug: { equals: slug } },
  })

  return result.docs?.[0] || null
})
```

The `cache` wrapper ensures that if the same slug is queried multiple times during a single request (e.g., in parallel components), the database is only hit once. The query respects draft mode — when draft is enabled, it accesses unpublished content and overrides access control.

## Static Params Generation

For static site generation (SSG) / incremental static regeneration (ISR), the template generates static params at build time:

```typescript
export async function generateStaticParams() {
  const payload = await getPayload({ config: configPromise })
  const pages = await payload.find({
    collection: 'pages',
    draft: false,
    limit: 1000,
    overrideAccess: false,
    pagination: false,
    select: { slug: true },
  })

  return pages.docs
    ?.filter((doc) => doc.slug !== 'home')
    .map(({ slug }) => ({ slug }))
}
```

This pre-renders all published pages at build time. The home page is excluded because it has its own `page.tsx` at the root.

## Metadata API

Each page template implements Next.js's `generateMetadata` for SEO:

```typescript
export async function generateMetadata({ params: paramsPromise }: Args): Promise<Metadata> {
  const { slug = 'home' } = await paramsPromise
  const decodedSlug = decodeURIComponent(slug)
  const page = await queryPageBySlug({ slug: decodedSlug })
  return generateMeta({ doc: page })
}
```

The `generateMeta` utility extracts SEO data from the document's `meta` field and builds proper Next.js Metadata including title, description, Open Graph tags, and Twitter cards.

## Home Page

The home page (`src/app/(frontend)/page.tsx`) delegates to the `[slug]/page.tsx` template:

```typescript
import PageTemplate, { generateMetadata } from './[slug]/page'
export default PageTemplate
export { generateMetadata }
```

When `queryPageBySlug` receives slug `'home'`, it queries for the page with slug `home`. If no home page exists (fresh install), a static fallback is provided:

```typescript
import { homeStatic } from '@/endpoints/seed/home-static'

// In page.tsx:
if (!page && slug === 'home') {
  page = homeStatic
}
```

## Payload Route Group

The `(payload)` route group contains auto-generated routes:

```
src/app/(payload)/
├── admin/     # Payload admin panel (auto-generated)
├── api/       # REST and GraphQL API endpoints (auto-generated)
└── layout.tsx # Minimal layout for payload routes
```

The `custom.scss` file in `(payload)/` allows customizing the admin panel's SCSS theme.

## Next.js Configuration

The `next.config.ts` wraps configuration with Payload's helper:

```typescript
import { withPayload } from '@payloadcms/next/withPayload'
import type { NextConfig } from 'next'
import { redirects } from './redirects'

const nextConfig: NextConfig = {
  images: {
    localPatterns: [{ pathname: '/api/media/file/**' }],
    qualities: [100],
    remotePatterns: [...],
  },
  webpack: (webpackConfig) => {
    webpackConfig.resolve.extensionAlias = {
      '.cjs': ['.cts', '.cjs'],
      '.js': ['.ts', '.tsx', '.js', '.jsx'],
      '.mjs': ['.mts', '.mjs'],
    }
    return webpackConfig
  },
  reactStrictMode: true,
  redirects,
  turbopack: { root: path.resolve(dirname) },
}

export default withPayload(nextConfig, { devBundleServerPackages: false })
```

Key settings:
- `images.localPatterns` — Allows Next.js Image component to serve files from Payload's media API
- `webpack.extensionAlias` — Resolves `.ts`/`.tsx` when importing `.js` (TypeScript support)
- `withPayload` — Integrates Payload with Next.js build and runtime
- `redirects` — Loads IE compatibility redirect from `redirects.ts`

## Caching Strategy

By default on Payload Cloud, all requests go through Cloudflare and Next.js caching is disabled via `no-store` directives. For self-hosted deployments, re-enable caching by:

1. Removing `no-store` from fetch requests in `src/app/_api`
2. Removing `export const dynamic = 'force-dynamic'` from page files

On-demand revalidation via `revalidatePath()` and `revalidateTag()` in collection hooks keeps content fresh without full rebuilds.

## Styling

The template uses:
- **Tailwind CSS 4.x** — Utility-first CSS framework
- **shadcn/ui** — Component library built on Radix UI primitives
- **Geist fonts** — Sans and Mono font families from Vercel
- **CSS variables** — Theme tokens defined in `src/cssVariables.js`
- **tailwind-merge** and **clsx** — Utility classes for conditional class merging
- **@tailwindcss/typography** — Prose styling plugin with custom overrides for heading sizes
