---
name: payloadcms-website-3-82-1
description: Complete guide for Payload CMS website template v3.82.1 providing production-ready blog and multi-page website with Next.js App Router, TypeScript, MongoDB, Lexical editor, live preview, SEO optimization, internationalization, form builder, search functionality, redirects management, and scheduled publishing. Use when building content websites, blogs, marketing sites, or any web project requiring pages, posts, categories, media management, header/footer globals, and search functionality following official Payload best practices.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - payloadcms
  - nextjs
  - typescript
  - cms
  - mongodb
  - website-template
  - blog
  - seo
  - live-preview
  - forms
  - search
category: development
required_environment_variables:
  - name: DATABASE_URL
    prompt: "Enter your MongoDB connection string"
    help: "For local development: mongodb://127.0.0.1/your-database-name. For production, use MongoDB Atlas or your hosted MongoDB instance."
    required_for: database connectivity
  - name: PAYLOAD_SECRET
    prompt: "Enter a secret key for Payload (minimum 32 characters)"
    help: "Generate using: node -e \"console.log(require('crypto').randomBytes(64).toString('hex'))\". Required for session encryption and JWT signing."
    required_for: application security
  - name: CRON_SECRET
    prompt: "Enter a secret for cron job authentication"
    help: "Generate a random string for authenticating scheduled tasks and background jobs."
    required_for: scheduled publishing and background jobs
---

# Payload CMS Website Template v3.82.1

A production-ready, enterprise-grade website template for building blogs, marketing sites, portfolios, and content platforms with Payload CMS v3.82.1, Next.js 16.2.2, TypeScript, MongoDB, Lexical editor, and advanced features including live preview, SEO optimization, search functionality, form builder, redirects management, and scheduled publishing.

## When to Use

- Building production-ready websites, blogs, or portfolios
- Creating content publishing platforms with editorial workflows
- Implementing draft preview and live preview functionality
- Adding SEO optimization with automatic meta tags and sitemaps
- Building sites with search functionality and redirects management
- Integrating form builder for contact forms and lead capture
- Setting up scheduled publishing and background jobs
- Creating multi-page websites with layout builders
- Implementing nested categories/taxonomies
- Following official Payload best practices for websites

## What This Template Includes

### Pre-configured Collections

- **Pages**: Layout builder-enabled pages with draft support, live preview, SEO fields, revalidation hooks
- **Posts**: Blog posts with rich text editor, categories, authors, related posts, drafts, live preview
- **Media**: Upload collection with image optimization, focal points, manual resizing
- **Categories**: Nested taxonomy for organizing content (uses nested-docs plugin)
- **Users**: Authentication-enabled admin users with role-based access control

### Pre-configured Globals

- **Header**: Navigation links and header configuration
- **Footer**: Footer links and configuration

### Advanced Features

- **Live Preview**: Real-time preview of drafts with responsive breakpoints
- **Draft Preview**: Shareable preview links for unpublished content
- **SEO Plugin**: Automatic meta tags, Open Graph, Twitter cards, sitemap generation
- **Search Plugin**: Full-text search across posts with custom indexing
- **Redirects Plugin**: URL redirect management with automatic revalidation
- **Form Builder Plugin**: Drag-and-drop form builder with submissions
- **Nested Docs Plugin**: Hierarchical category structure
- **On-demand Revalidation**: Instant cache invalidation on content updates
- **Scheduled Publishing**: Publish content at specific dates/times
- **Internationalization Ready**: i18n configuration and utilities

### Technology Stack

- **Runtime**: Node.js 18.20.2+ or 20.9.0+
- **Framework**: Next.js 16.2.2 (App Router with SSR/SSG)
- **Database**: MongoDB via `@payloadcms/db-mongodb`
- **Editor**: Lexical rich text editor with custom blocks
- **Styling**: Tailwind CSS 4.1+ with Radix UI components
- **Package Manager**: pnpm 9+ or 10+
- **Image Optimization**: Sharp 0.34.2

## Quick Start

### Prerequisites

- Node.js 18.20.2+ or 20.9.0+ installed
- MongoDB running locally or MongoDB Atlas account
- pnpm package manager (recommended)

### Local Development Setup

1. **Clone and install dependencies:**
   ```bash
   cd your-project
   pnpm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```env
   DATABASE_URL=mongodb://127.0.0.1/your-database-name
   PAYLOAD_SECRET=your-secret-key-minimum-32-chars
   CRON_SECRET=your-cron-job-secret
   ```

3. **Start MongoDB (if not running):**
   ```bash
   docker run -d -p 27017:27017 --name mongo mongo:latest
   ```

4. **Start development server:**
   ```bash
   pnpm dev
   ```

5. **Open browser:**
   - Frontend: http://localhost:3000
   - Admin Panel: http://localhost:3000/admin

6. **Seed demo content (optional):**
   - Visit: http://localhost:3000/next/seed
   - Creates sample pages, posts, categories for testing

See [Setup and Configuration](references/01-setup-configuration.md) for detailed setup instructions and environment variables.

## Project Structure

```
src/
├── app/                          # Next.js App Router
│   ├── (payload)/                # Admin panel routes
│   └── (frontend)/               # Public website routes
│       ├── [slug]/page.tsx       # Dynamic page routes
│       ├── posts/                # Blog post routes
│       ├── search/page.tsx       # Search results page
│       └── (sitemaps)/           # XML sitemap routes
├── collections/                   # Collection configurations
│   ├── Pages/                    # Page collection with layout builder
│   ├── Posts/                    # Post collection with rich text
│   ├── Media/                    # Upload-enabled media
│   ├── Categories/               # Nested taxonomy
│   └── Users/                    # Auth-enabled users
├── globals/                       # Global configurations
│   ├── Header/                   # Navigation configuration
│   └── Footer/                   # Footer links
├── blocks/                        # Layout builder blocks
│   ├── ArchiveBlock/             # Post archive display
│   ├── CallToAction/             # CTA sections
│   ├── Content/                  # Text and media columns
│   ├── Form/                     # Form builder integration
│   ├── MediaBlock/               # Full-width media
│   ├── Banner/                   # Inline rich text banners
│   └── Code/                     # Code blocks with syntax highlighting
├── components/                    # React components
│   ├── ui/                       # Reusable UI components (Radix)
│   ├── RichText/                 # Lexical renderer
│   ├── Media/                    # Image and video components
│   ├── Link/                     # Link component
│   └── Pagination/               # Pagination component
├── heros/                         # Hero section variants
│   ├── HighImpact/               # Full-screen hero
│   ├── MediumImpact/             # Large hero
│   ├── LowImpact/                # Subtle hero
│   └── PostHero/                 # Post-specific hero
├── fields/                        # Reusable field configurations
├── hooks/                         # Collection hooks
├── plugins/                       # Payload plugin configuration
├── providers/                     # React context providers
│   └── Theme/                    # Dark/light theme provider
├── search/                        # Search plugin configuration
└── utilities/                     # Helper functions
```

See [Project Structure](references/02-project-structure.md) for detailed explanation of each directory and file purpose.

## Core Features

### Layout Builder

Both Pages and Posts use a powerful layout builder with reusable blocks:

- **Call to Action**: Prominent CTA sections with buttons
- **Content**: Flexible text and media column layouts
- **Media Block**: Full-width images and videos
- **Archive**: Display collections of posts
- **Form**: Embed forms from Form Builder plugin

See [Layout Builder](references/03-layout-builder.md) for block configuration and usage patterns.

### SEO Optimization

Comprehensive SEO features powered by `@payloadcms/plugin-seo`:

- Automatic meta tags (title, description, Open Graph, Twitter)
- SEO preview in admin panel
- Automatic sitemap generation (pages, posts)
- Canonical URLs
- Structured data support

See [SEO and Metadata](references/04-seo-metadata.md) for SEO configuration and best practices.

### Search Functionality

Full-text search across posts using `@payloadcms/plugin-search`:

- Automatic search indexing on content updates
- Custom search results page with filtering
- Real-time search suggestions
- Highlighted search terms

See [Search Implementation](references/05-search.md) for search configuration and customization.

### Form Builder

Drag-and-drop form builder with `@payloadcms/plugin-form-builder`:

- Create forms visually in admin panel
- Multiple field types (text, email, textarea, select, etc.)
- Email notifications on submission
- Custom confirmation messages
- Embed forms on any page using Form block

See [Form Builder](references/06-form-builder.md) for form creation and integration.

### Redirects Management

URL redirect management with `@payloadcms/plugin-redirects`:

- 301 and 302 redirects
- Automatic redirect suggestions on slug changes
- Support for internal and external URLs
- On-demand revalidation

See [Redirects](references/07-redirects.md) for redirect configuration.

### Live Preview and Drafts

Real-time preview of unpublished content:

- **Live Preview**: Real-time editing with responsive breakpoints
- **Draft Preview**: Shareable preview links for stakeholders
- **Scheduled Publishing**: Auto-publish at specified dates
- **Autosave**: Automatic draft saving every 100ms

See [Preview and Drafts](references/08-preview-drafts.md) for preview configuration.

## Common Operations

### Create a New Page

1. Navigate to Admin Panel → Pages → Create New Page
2. Add title and hero section
3. Build layout using blocks (Content, Media, CTA, etc.)
4. Configure SEO metadata
5. Click "Publish" or schedule for later

See [Pages Collection](references/03-layout-builder.md#pages-collection) for page-specific features.

### Create a Blog Post

1. Navigate to Posts → Create New Post
2. Add title, hero image, and rich text content
3. Assign categories and related posts
4. Configure SEO metadata
5. Use live preview to see changes in real-time
6. Publish or schedule

See [Posts Collection](references/09-posts-collection.md) for post-specific features.

### Customize Theme

The template uses Tailwind CSS with dark/light theme support:

```typescript
// src/providers/Theme/index.tsx
import { ThemeProvider } from '@/providers/Theme'

<ThemeProvider>
  <YourApp />
</ThemeProvider>
```

See [Theming and Styling](references/10-theming-styling.md) for customization options.

### Add Custom Blocks

Create reusable layout blocks:

1. Create block config in `src/blocks/YourBlock/config.ts`
2. Create React component in `src/blocks/YourBlock/Component.tsx`
3. Add to Pages/Posts collection fields
4. Implement in `RenderBlocks.tsx`

See [Custom Blocks](references/03-layout-builder.md#creating-custom-blocks) for detailed guide.

## Testing

### Run Integration Tests

```bash
pnpm test:int
```

Tests API endpoints, access control, and hooks using Vitest.

### Run E2E Tests

```bash
pnpm test:e2e
```

Tests admin panel and frontend functionality using Playwright.

See [Testing](references/11-testing.md) for test patterns and examples.

## Production Deployment

### Build for Production

```bash
# Generate types
pnpm generate:types

# Build Next.js application with sitemaps
pnpm build

# Start production server
pnpm start
```

### Configure Cron Jobs

For scheduled publishing, set up cron jobs:

```bash
# Example: Check every minute for posts to publish
* * * * * curl -H "Authorization: Bearer $CRON_SECRET" https://your-site.com/api/jobs/process
```

See [Production Deployment](references/12-production-deployment.md) for deployment guides and cron configuration.

## Troubleshooting

**Live preview not working**: Verify `PAYLOAD_PUBLIC_URL` is set correctly in `.env`.

**Search not indexing**: Check search collection has proper access control and revalidation hooks.

**Forms not submitting**: Verify email service configuration in form settings.

**Sitemap not updating**: Run `pnpm build` to regenerate sitemaps after content changes.

See [Troubleshooting Guide](references/13-troubleshooting.md) for comprehensive solutions.

## Reference Files

This skill includes detailed reference documentation organized by topic:

### Core Setup and Structure

- [`references/01-setup-configuration.md`](references/01-setup-configuration.md) - Environment variables, dependencies, Docker setup, Next.js config
- [`references/02-project-structure.md`](references/02-project-structure.md) - Directory organization, file purposes, TypeScript paths

### Content and Layout

- [`references/03-layout-builder.md`](references/03-layout-builder.md) - Pages collection, Posts collection, block configuration, custom blocks
- [`references/04-seo-metadata.md`](references/04-seo-metadata.md) - SEO plugin, meta tags, sitemaps, Open Graph, Twitter cards
- [`references/05-search.md`](references/05-search.md) - Search plugin, indexing, search page, customization

### Features and Plugins

- [`references/06-form-builder.md`](references/06-form-builder.md) - Form creation, field types, submissions, email notifications
- [`references/07-redirects.md`](references/07-redirects.md) - Redirect management, automatic suggestions, revalidation
- [`references/08-preview-drafts.md`](references/08-preview-drafts.md) - Live preview, draft preview, scheduled publishing, autosave

### Collections and Content Types

- [`references/09-posts-collection.md`](references/09-posts-collection.md) - Post fields, rich text editor, categories, authors, related posts
- [`references/10-theming-styling.md`](references/10-theming-styling.md) - Tailwind CSS, theme provider, dark mode, custom components

### Operations and Deployment

- [`references/11-testing.md`](references/11-testing.md) - Vitest integration tests, Playwright E2E tests, test helpers
- [`references/12-production-deployment.md`](references/12-production-deployment.md) - Build process, Docker deployment, cron jobs, monitoring
- [`references/13-troubleshooting.md`](references/13-troubleshooting.md) - Common errors, debugging techniques, performance issues

## Important Notes

1. **Type Generation**: Always run `pnpm generate:types` after modifying collections or globals
2. **Revalidation Hooks**: Template uses on-demand revalidation for instant content updates
3. **Environment Variables**: Never commit `.env` files; use `.env.example` as template
4. **Cron Secret**: Required for scheduled publishing and background jobs
5. **Live Preview**: Requires `PAYLOAD_PUBLIC_URL` to be set correctly
6. **Search Indexing**: Automatic on content updates via `beforeSync` hook
7. **Form Submissions**: Configure email service in Form Builder plugin settings
8. **Sitemap Generation**: Runs automatically post-build via `next-sitemap`

## Resources

- **Payload Docs**: https://payloadcms.com/docs
- **Website Template GitHub**: https://github.com/payloadcms/payload/tree/v3.82.1/templates/website
- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lexical Editor**: https://lexical.dev

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/payloadcms-website-3-82-1/`). All paths in this skill are relative to this directory.
