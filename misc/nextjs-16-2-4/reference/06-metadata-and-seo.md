# Metadata and SEO

## Static Metadata

Export a `Metadata` object from a static `layout.js` or `page.js` file:

```tsx
// app/blog/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My Blog',
  description: 'A blog about web development',
}

export default function Layout({ children }) {
  return <section>{children}</section>
}
```

Next.js automatically generates the relevant `<head>` tags. Default meta tags always added:

```html
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

## Dynamic Metadata

Use `generateMetadata` for metadata that depends on data:

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata, ResolvingMetadata } from 'next'

type Props = {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export async function generateMetadata(
  { params, searchParams }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const slug = (await params).slug

  const post = await fetch(`https://api.vercel.app/blog/${slug}`).then((res) =>
    res.json()
  )

  return {
    title: post.title,
    description: post.description,
  }
}

export default function Page({ params, searchParams }: Props) {
  // ...
}
```

## Metadata Object Fields

Key fields in the `Metadata` object:

- `title` — Page title (string or `{ absolute, template, default }`)
- `description` — Meta description
- `themeColor` — Theme color for mobile browsers
- `colorScheme` — Light/dark color scheme
- `icons` — Favicon and icon links
- `openGraph` — Open Graph social sharing metadata
- `twitter` — Twitter card metadata
- `robots` — Robots indexing instructions
- `alternates` — Alternate language/region versions
- `keywords` — Meta keywords

Example with structured title:

```tsx
export const metadata: Metadata = {
  title: {
    template: '%s | My Site',
    default: 'Home Page',
  },
  description: 'My website description',
  openGraph: {
    title: 'My Page',
    description: 'My page description',
    images: ['/og-image.png'],
  },
}
```

## Open Graph Images

### Static OG images

Place an `opengraph-image.png` (or `.jpg`, `.webp`) file next to your layout or page:

```
app/
  blog/
    page.tsx
    opengraph-image.png   → /blog/opengraph-image.png
```

### Dynamic OG images

Create an `opengraph-image.ts` file that exports a function matching the `ImageResponse` type:

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const slug = (await params).slug

  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 60,
          background: 'white',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {slug}
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

## Sitemap

### Static sitemap

Create a `sitemap.ts` file in the `app` directory:

```ts
// app/sitemap.ts
import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
    },
    {
      url: 'https://example.com/blog',
      lastModified: new Date(),
    },
  ]
}
```

### Dynamic sitemap

Use `generateSitemaps` for large sites:

```ts
import type { MetadataRoute } from 'next'

export function generateSitemaps() {
  return Array.from({ length: 10 }, (_, i) => ({
    id: i,
  }))
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await fetch('https://api.example.com/posts').then((res) =>
    res.json()
  )

  return posts.map((post) => ({
    url: `https://example.com/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
  }))
}
```

## Robots

### Static robots

Create a `robots.ts` file in the `app` directory:

```ts
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: '/private/',
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

### Dynamic robots

Export `robots` as an async function:

```ts
import type { MetadataRoute } from 'next'

export default async function robots(): Promise<MetadataRoute.Robots> {
  const isProduction = process.env.NODE_ENV === 'production'

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: isProduction ? [] : ['/'],
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

## Viewport Configuration

Export `generateViewport` from a layout to configure viewport settings:

```tsx
export const viewport = {
  themeColor: '#fff',
  colorScheme: 'light dark',
  width: 'device-width',
  initialScale: 1,
}
```

Or dynamically:

```tsx
export async function generateViewport() {
  return {
    themeColor: (await getTheme()).color,
  }
}
```

## Favicons

### Static favicons

Place icon files in the `app` directory:

```
app/
  icon.png        → Default favicon
  icon.svg        → SVG favicon
  apple-icon.png  → Apple touch icon
```

### Dynamic favicons

Create an `icon.ts` file:

```tsx
// app/icon.ts
import { ImageResponse } from 'next/og'

export const size = { width: 32, height: 32 }
export const contentType = 'image/png'

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 24,
          background: '#000',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
        }}
      >
        N
      </div>
    ),
    { ...size }
  )
}
```
