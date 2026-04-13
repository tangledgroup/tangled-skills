# Project Structure and File Conventions

## App Router Directory Structure

```
my-app/
├── app/                      # App Router directory (required)
│   ├── layout.tsx            # Root layout (wraps all pages)
│   ├── page.tsx              # Home page route (/)
│   ├── globals.css           # Global styles
│   ├── loading.tsx           # Default loading UI
│   ├── error.tsx             # Default error boundary
│   ├── not-found.tsx         # Custom 404 page
│   ├── favicon.ico           # Favicon
│   ├── sitemap.ts            # Sitemap generator
│   ├── robots.ts             # Robots.txt generator
│   ├── default.ts            # Default route matcher
│   │
│   ├── (group)/              # Route group (doesn't create URL segment)
│   │   └── page.tsx          # Still accessible at /
│   │
│   ├── (@modal)/             # Parallel route
│   │   └── page.tsx
│   │
│   ├── blog/                 # Blog section (/blog)
│   │   ├── layout.tsx        # Layout for blog section
│   │   ├── page.tsx          # /blog
│   │   ├── loading.tsx       # Loading UI for blog
│   │   │
│   │   ├── [slug]/           # Dynamic route (/blog/[slug])
│   │   │   ├── page.tsx      # Blog post page
│   │   │   └── edit/         # Nested route (/blog/[slug]/edit)
│   │   │       └── page.tsx
│   │   │
│   │   └── tags/
│   │       └── [tag]/
│   │           └── page.tsx  # /blog/tags/[tag]
│   │
│   ├── api/                  # API routes
│   │   └── users/
│   │       ├── route.ts      # GET, POST /api/users
│   │       └── [id]/
│   │           └── route.ts  # GET, PUT, DELETE /api/users/[id]
│   │
│   └── products/
│       ├── layout.tsx
│       ├── page.tsx          # /products
│       └── [id]/
│           └── page.tsx      # /products/[id]
│
├── public/                   # Static files (copied as-is)
│   ├── images/
│   ├── fonts/
│   └── robots.txt
│
├── src/                      # Optional source directory
│   └── app/                  # Can move app here
│
├── components/               # Reusable components
│   ├── Button.tsx
│   └── Header.tsx
│
├── lib/                      # Utility functions
│   ├── db.ts
│   └── utils.ts
│
├── types/                    # TypeScript definitions
│   └── index.ts
│
├── next.config.js            # Next.js configuration
├── tsconfig.json             # TypeScript configuration
├── package.json              # Dependencies and scripts
└── .env                      # Environment variables
```

## Core File Conventions

### page.tsx (Route Page)

Defines the UI for a specific route. Must export a default component.

```tsx
// app/page.tsx - Home page (/)
export default function HomePage() {
  return <h1>Home</h1>
}

// app/about/page.tsx - About page (/about)
export default function AboutPage() {
  return <h1>About Us</h1>
}
```

### layout.tsx (Layout Wrapper)

Wraps all child routes. Preserves state during navigation.

```tsx
// app/layout.tsx - Root layout
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  )
}

// app/blog/layout.tsx - Blog section layout
export default function BlogLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="blog-layout">
      <BlogSidebar />
      {children}
    </div>
  )
}
```

**Important:** Layouts must include `children` prop to render nested routes.

### loading.tsx (Loading UI)

Displays while the route is loading data.

```tsx
// app/loading.tsx - Default loading for all routes
export default function Loading() {
  return <div className="loading-spinner">Loading...</div>
}

// app/products/loading.tsx - Loading for products section only
export default function ProductsLoading() {
  return (
    <div className="product-skeleton">
      {[1, 2, 3].map(i => (
        <div key={i} className="skeleton-card" />
      ))}
    </div>
  )
}
```

### error.tsx (Error Boundary)

Catches errors in child components. Must be a Client Component.

```tsx
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <pre>{error.message}</pre>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### not-found.tsx (404 Page)

Custom 404 page for unmatched routes.

```tsx
// app/not-found.tsx
export default function NotFound() {
  return (
    <div className="not-found">
      <h1>404 - Page Not Found</h1>
      <Link href="/">Go Home</Link>
    </div>
  )
}
```

### route.ts (API Route Handler)

Defines HTTP methods for API endpoints.

```tsx
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const users = await getUsersFromDatabase()
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  const user = await createUser(body)
  return NextResponse.json(user, { status: 201 })
}

export async function PUT(request: Request) {
  // Handle update
}

export async function DELETE() {
  // Handle delete
}
```

## Special Files

### metadata (SEO and Metadata)

Define page metadata for SEO:

```tsx
// app/page.tsx
export const metadata = {
  title: 'Home - My App',
  description: 'Welcome to my Next.js application',
  openGraph: {
    title: 'Home - My App',
    description: 'Welcome to my Next.js application',
    images: ['/og-image.png'],
  },
}

export default function Home() {
  return <h1>Home</h1>
}
```

### Dynamic Metadata

Generate metadata dynamically:

```tsx
// app/products/[id]/page.tsx
interface Props {
  params: { id: string }
}

export async function generateMetadata({ params }: Props) {
  const product = await getProduct(params.id)
  
  return {
    title: `${product.name} - My Store`,
    description: product.description,
  }
}

export default function ProductPage({ params }: Props) {
  const product = await getProduct(params.id)
  return <div>{product.name}</div>
}
```

### generateStaticParams() (Pre-render Routes)

Generate static routes for dynamic segments:

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getPostsFromDatabase()
  
  return posts.map(post => ({
    slug: post.slug,
  }))
}

export default function BlogPost({ params }: { params: { slug: string } }) {
  return <div>Post: {params.slug}</div>
}
```

### generateViewport() (Viewport Settings)

Configure viewport for mobile devices:

```tsx
// app/layout.tsx
export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#000000',
}
```

## Route Groups

Group routes without creating URL segments using `(group-name)`:

```
app/
├── (marketing)/          # Marketing group
│   ├── page.tsx          # /
│   └── about/
│       └── page.tsx      # /about
│
├── (dashboard)/          # Dashboard group
│   ├── layout.tsx        # Dashboard layout only
│   └── settings/
│       └── page.tsx      # /settings
│
└── layout.tsx            # Root layout (wraps all)
```

**Use cases:**
- Different layouts for sections
- Organizing large applications
- Sharing layouts across unrelated routes

## Parallel Routes

Render multiple routes simultaneously using `@slot-name`:

```
app/
├── layout.tsx
├── page.tsx
└── (@modal)/            # Parallel route slot
    ├── default.tsx      # Default content for @modal
    └── modal/
        └── page.tsx     # Modal content
```

**Usage in layout:**
```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal?: React.ReactNode
}) {
  return (
    <div>
      {children}
      {modal && <div className="modal-overlay">{modal}</div>}
    </div>
  )
}
```

## Interception Routes

Intercept navigation to display content in current view:

```
app/
├── shop/
│   └── page.tsx          # /shop
└── (./shop)/
    └── [product]/
        └── page.tsx      # Intercepts /shop, shows product
```

## File Naming Conventions

| File | Purpose | URL Segment |
|------|---------|-------------|
| `page.tsx` | Route page | Creates route |
| `layout.tsx` | Layout wrapper | No URL change |
| `loading.tsx` | Loading UI | No URL change |
| `error.tsx` | Error boundary | No URL change |
| `not-found.tsx` | 404 page | No URL change |
| `route.ts` | API handler | Creates API route |
| `route-handlers/[name].ts` | Separate handler files | No URL change |
| `(group)/` | Route group | No URL segment |
| `@slot/` | Parallel route | No URL segment |
| `(./path)/` | Intercept route | Intercepts navigation |

## Best Practices

1. **Keep components close to routes** - Colocate components in route folders when used only there
2. **Use route groups for organization** - Avoid deep nesting with `(group-name)`
3. **Separate large components** - Move complex UI to `components/` directory
4. **Type your props** - Always interface route props (`params`, `searchParams`)
5. **Use meaningful folder names** - Clear structure improves maintainability

## Migration from Pages Router

```
pages/ (Old)          →   app/ (New)
├── index.tsx         →   page.tsx
├── about.tsx         →   about/page.tsx
├── blog/[slug].tsx   →   blog/[slug]/page.tsx
└── api/users.ts      →   api/users/route.ts
```
