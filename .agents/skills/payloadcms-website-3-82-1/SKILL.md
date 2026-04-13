---
name: payloadcms-website-3-82-1
description: Complete guide for Payload CMS website template v3.82.1 providing production-ready blog and multi-page website with Next.js App Router, TypeScript, MongoDB, Lexical editor, live preview, SEO optimization, and internationalization. Use when building content websites, blogs, marketing sites, or any web project requiring pages, posts, categories, media management, header/footer globals, and search functionality following official Payload best practices.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - payload-cms
  - nextjs
  - website-template
  - blog
  - content-website
  - mongodb
  - lexical-editor
  - seo
  - i18n
category: development
required_environment_variables:
  - name: PAYLOAD_SECRET
    prompt: "Enter your Payload secret key"
    help: "Generate with: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\""
    required_for: "application security and session management"
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "Example: mongodb://localhost:27017/payload or use MongoDB Atlas"
    required_for: "database connectivity"
  - name: PAYLOAD_PUBLIC_APP_URL
    prompt: "Enter your public app URL"
    help: "Example: http://localhost:3000 or https://your-domain.com"
    required_for: "live preview and email links"
---

# Payload CMS Website Template 3.82.1

The website template provides a production-ready, full-featured website starter with blog functionality, multi-page support, live preview, SEO optimization, and internationalization (i18n). It includes pre-configured collections for Pages, Posts, Categories, Media, and Users, plus Header/Footer globals, custom blocks, and search functionality.

## When to Use

- Building content websites or blogs from scratch
- Needing multi-page website with navigation
- Requiring live preview for content editors
- Wanting SEO-optimized pages out of the box
- Building marketing sites with custom layouts
- Needing category-based content organization
- Requiring search functionality across content
- Following official Payload best practices

## Quick Start

### Installation

```bash
# Create new project from website template
npm create payload@3.82.1 -- --template website

# Or use npx with specific version
npx create-payload@3.82.1 --template website

# Using bun
bunx create-payload@3.82.1 --template website
```

### Project Structure

```
my-website/
├── src/
│   ├── app/
│   │   ├── (frontend)/
│   │   │   ├── pages/
│   │   │   ├── posts/
│   │   │   └── search/
│   │   ├── (payload)/
│   │   │   └── admin/
│   │   ├── api/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── collections/
│   │   ├── Categories/
│   │   ├── Media/
│   │   ├── Pages/
│   │   ├── Posts/
│   │   └── Users/
│   ├── Footer/              # Footer global
│   ├── Header/              # Header global
│   ├── blocks/              # Reusable content blocks
│   ├── components/          # React components
│   ├── fields/              # Custom field configurations
│   ├── heros/               # Hero section variants
│   ├── hooks/               # Collection hooks
│   ├── plugins/             # Custom plugins
│   ├── search/              # Search functionality
│   ├── payload.config.ts    # Main configuration
│   └── utilities/           # Helper functions
├── .env.example
├── next.config.js
├── package.json
└── tsconfig.json
```

### Environment Setup

```bash title=".env"
# Required - Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
PAYLOAD_SECRET=your-generated-secret-here

# MongoDB connection string
DATABASE_URL=mongodb://localhost:27017/payload

# Public URL for live preview and emails
PAYLOAD_PUBLIC_APP_URL=http://localhost:3000

# Optional - Cron job secret for background jobs
CRON_SECRET=your-cron-secret

# Optional - Disable telemetry
TELEMETRY_ENABLED=false
```

### Run Development Server

```bash
# Install dependencies
bun install

# Start MongoDB (if not running)
mongod --dbpath ./data  # Or use MongoDB Atlas

# Start development server
bun run dev

# Access:
# - Admin panel: http://localhost:3000/admin
# - Website: http://localhost:3000
```

## Core Collections

### Pages Collection

Multi-page website support with hierarchical structure, live preview, and SEO fields.

**Key Features:**
- Hierarchical page structure (parent/child relationships)
- Layout builder with reusable blocks
- Live preview for all devices
- SEO optimization fields
- Draft/publish workflow
- Version history

```typescript title="src/collections/Pages/index.ts"
export const Pages: CollectionConfig = {
  slug: 'pages',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'updatedAt'],
  },
  access: {
    read: () => true,  // Public can read published pages
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true },
    
    // Layout builder with blocks
    {
      name: 'layout',
      type: 'blocks',
      blocks: [
        'hero',
        'content',
        'media',
        'call-to-action',
        'team',
        'faq',
      ],
    },
    
    // SEO fields
    seoFields(),
    
    // Status for drafts
    {
      name: 'status',
      type: 'select',
      options: ['draft', 'published'],
      defaultValue: 'draft',
    },
  ],
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
}
```

### Posts Collection (Blog)

Full-featured blog with categories, authors, featured images, and SEO optimization.

**Key Features:**
- Rich text content with Lexical editor
- Category-based organization
- Author relationships
- Featured image uploads
- Publish date scheduling
- Reading time calculation
- Related posts
- SEO meta fields

```typescript title="src/collections/Posts/index.ts"
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'publishDate'],
  },
  access: {
    read: ({ req }) => {
      if (req.user) return true
      return { status: { equals: 'published' } }
    },
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true },
    
    // Rich text content
    {
      name: 'content',
      type: 'richText',
      required: true,
    },
    
    // Featured image
    {
      name: 'featuredImage',
      type: 'upload',
      relationTo: 'media',
    },
    
    // Categories (many-to-many)
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
    },
    
    // Author
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
    },
    
    // Publish date
    {
      name: 'publishDate',
      type: 'date',
    },
    
    // SEO fields
    seoFields(),
    
    // Status
    {
      name: 'status',
      type: 'select',
      options: ['draft', 'published'],
      defaultValue: 'draft',
    },
  ],
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
}
```

### Categories Collection

Organize posts into categories with descriptions and icons.

```typescript title="src/collections/Categories.ts"
export const Categories: CollectionConfig = {
  slug: 'categories',
  admin: {
    useAsTitle: 'title',
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true },
    { name: 'description', type: 'text' },
  ],
}
```

### Media Collection

Upload and manage images, videos, and documents with metadata.

```typescript title="src/collections/Media.ts"
export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,  // Public access
  },
  fields: [
    { name: 'alt', type: 'text', required: true },
    { name: 'caption', type: 'text' },
    { name: 'credits', type: 'text' },
  ],
  upload: true,
}
```

### Users Collection

Authentication with role-based access control.

```typescript title="src/collections/Users.ts"
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: {
    useAsTitle: 'email',
  },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      options: ['admin', 'editor', 'author'],
      defaultValue: ['author'],
      saveToJWT: true,
    },
    { name: 'displayName', type: 'text' },
  ],
}
```

## Globals

### Header Global

Manage global website header/navigation.

```typescript title="src/Header/config.ts"
export const Header: GlobalConfig = {
  slug: 'header',
  fields: [
    {
      name: 'navItems',
      type: 'array',
      fields: [
        { name: 'label', type: 'text' },
        { name: 'url', type: 'text' },
      ],
    },
  ],
}
```

### Footer Global

Manage global website footer content.

```typescript title="src/Footer/config.ts"
export const Footer: GlobalConfig = {
  slug: 'footer',
  fields: [
    { name: 'copyright', type: 'text' },
    { name: 'socialLinks', type: 'array' },
  ],
}
```

## Custom Blocks

Reusable content blocks for page builders.

### Available Blocks

1. **Hero Block**: Full-width hero sections with various layouts
2. **Content Block**: Text and media combinations
3. **Media Block**: Image galleries and video embeds
4. **Call-to-Action Block**: Prominent CTAs with buttons
5. **Team Block**: Team member grids
6. **FAQ Block**: Accordion-style FAQs

### Example: Hero Block

```typescript title="src/blocks/Hero/index.ts"
export const HeroBlock: Block = {
  slug: 'hero',
  labels: {
    singular: 'Hero',
    plural: 'Heroes',
  },
  fields: [
    {
      name: 'type',
      type: 'select',
      options: ['default', 'large', 'small'],
      defaultValue: 'default',
    },
    { name: 'title', type: 'text' },
    { name: 'subtitle', type: 'richText' },
    {
      name: 'media',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'buttons',
      type: 'array',
      fields: [
        { name: 'link', type: 'text' },
        { name: 'label', type: 'text' },
      ],
    },
  ],
}
```

## Live Preview

Real-time preview of content changes across devices.

### Configuration

```typescript title="src/payload.config.ts"
admin: {
  livePreview: {
    breakpoints: [
      { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
      { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
      { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
    ],
  },
}
```

### Usage in Pages

```typescript title="src/app/(frontend)/pages/[slug]/page.tsx"
export default async function Page({ params, searchParams }) {
  const isPreview = searchParams?.preview === 'true'
  
  const query = {
    where: { slug: { equals: params.slug } },
    ...(isPreview ? { draft: true } : {}),
  }
  
  const page = await payload.findBySlug({
    collection: 'pages',
    ...query,
  })
  
  return <PageTemplate data={page} isPreview={isPreview} />
}
```

## SEO Features

### SEO Fields

Reusable SEO field group for all collections.

```typescript title="src/fields/seoFields.ts"
export function seoFields() {
  return {
    name: 'seo',
    type: 'group',
    fields: [
      { name: 'title', type: 'text' },
      { name: 'description', type: 'textarea' },
      { name: 'image', type: 'upload', relationTo: 'media' },
    ],
  }
}
```

### Meta Tags in Next.js

```typescript title="src/app/(frontend)/pages/[slug]/page.tsx"
export async function generateMetadata({ params }) {
  const page = await payload.findBySlug({
    collection: 'pages',
    slug: params.slug,
  })
  
  return {
    title: page.seo?.title || page.title,
    description: page.seo?.description,
    openGraph: {
      images: [page.seo?.image.url],
    },
  }
}
```

## Search Functionality

Full-text search across all content.

### Search Collection

```typescript title="src/collections/Search.ts"
export const Search: CollectionConfig = {
  slug: 'search',
  access: {
    read: () => true,
  },
  fields: [
    { name: 'title', type: 'text' },
    { name: 'url', type: 'text' },
    { name: 'excerpt', type: 'text' },
    { name: 'document', type: 'relationship', relationTo: ['pages', 'posts'] },
  ],
}
```

### Search Hook

Automatically index content on create/update.

```typescript title="src/hooks/populateSearch.ts"
export const populateSearch = async ({ doc, req }: { doc: any; req: any }) => {
  await req.payload.update({
    collection: 'search',
    id: doc.id,
    data: {
      title: doc.title,
      url: `/${doc.slug}`,
      excerpt: doc.content?.substring(0, 200),
    },
  })
}
```

## Internationalization (i18n)

Multi-language support with localized content.

### Configuration

```typescript title="src/payload.config.ts"
localization: {
  locales: [
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Spanish' },
    { code: 'fr', label: 'French' },
  ],
  defaultLocale: 'en',
  fallback: true,
}
```

### Localized Fields

```typescript
fields: [
  { name: 'title', type: 'text', localized: true },
  { name: 'content', type: 'richText', localized: true },
]
```

### Next.js i18n Routing

```typescript title="src/app/[[locale]]/layout.tsx"
export default function LocaleLayout({ children, params }) {
  const locale = params.locale || 'en'
  
  return (
    <html lang={locale}>
      <body>{children}</body>
    </html>
  )
}
```

## Security Best Practices

### Access Control

Always implement proper access control:

```typescript
access: {
  read: ({ req }) => {
    if (req.user) return true
    return { status: { equals: 'published' } }
  },
  update: ({ req }) => {
    return req.user?.roles?.includes('admin')
  },
}
```

### Local API Security

**CRITICAL**: When using Local API with user context:

```typescript
// ✅ CORRECT - Enforces permissions
await payload.find({
  collection: 'pages',
  user: req.user,
  overrideAccess: false,  // REQUIRED!
})
```

See [Payload CMS Skill](../payloadcms-3-82-1/SKILL.md) for complete security patterns.

## Customization

### Add New Block

1. Create block configuration in `src/blocks/`
2. Add to page layout blocks array
3. Create React component in `src/components/`
4. Update type generation: `bun run generate:types`

### Add New Collection

1. Create collection in `src/collections/`
2. Import and add to `payload.config.ts`
3. Create frontend pages in `src/app/`
4. Regenerate types

### Customize Theme

```typescript title="src/cssVariables.js"
export const cssVariables = {
  colors: {
    primary: '#0070f3',
    secondary: '#fa823e',
  },
}
```

## Scripts

```json title="package.json"
{
  "scripts": {
    "build": "next build",
    "dev": "next dev",
    "generate:types": "payload generate:types",
    "lint": "next lint",
    "start": "next start",
    "typecheck": "tsc --noEmit"
  }
}
```

## Deployment

### Production Build

```bash
# Install dependencies
bun install --frozen

# Generate types
bun run generate:types

# Build Next.js app
bun run build

# Start production server
bun run start
```

### Docker Deployment

```dockerfile title="Dockerfile"
FROM oven/bun:1.3.12

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen

COPY . .
RUN bun run generate:types
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
```

## Troubleshooting

### Live Preview Not Working

- Verify `PAYLOAD_PUBLIC_APP_URL` is set correctly
- Check CORS configuration in `payload.config.ts`
- Ensure preview endpoint is accessible

### Search Not Indexing

- Verify search hook is added to collections
- Check search collection has proper access control
- Run manual indexing if needed

### Types Not Generating

```bash
# Clean and regenerate
rm src/payload-types.ts
bun run generate:types
```

## Package Dependencies

Key packages included:
- `@payloadcms/db-mongodb` - MongoDB adapter
- `@payloadcms/richtext-lexical` - Lexical editor
- `next` - Next.js framework
- `payload` - Payload CMS core
- `react` & `react-dom` - UI library

## Next Steps

1. **Customize Content**: Add your pages and posts
2. **Extend Blocks**: Create custom layout blocks
3. **Add Collections**: Implement custom content types
4. **Configure Email**: Set up email provider for notifications
5. **Deploy**: Push to production hosting

## Resources

- [Payload Website Template](https://github.com/payloadcms/payload/tree/v3.82.1/templates/website)
- [Payload Documentation](https://payloadcms.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)

## Related Skills

- `payloadcms-3-82-1` - Complete Payload CMS development guide
- `payloadcms-blank-3-82-1` - Minimal starter template
- `nextjs-14-2` - Next.js App Router patterns
- `mongodb-8-0` - MongoDB database operations
