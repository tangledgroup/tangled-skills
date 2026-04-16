---
name: payloadcms-website-3-82-1
description: Complete guide for Payload CMS website template v3.82.1 providing production-ready starter for content-driven websites, blogs, and portfolios with Next.js App Router, MongoDB, Lexical editor, SEO optimization, draft/live preview, form builder, search, redirects, scheduled publishing, and on-demand cache revalidation. Use when building personal or enterprise-grade websites requiring publication workflows, layout builders, multi-page sites, or integrating Payload CMS with modern frontend technologies.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
maintainer: Tangled Skills Community
license: MIT
tags:
  - payloadcms
  - nextjs
  - typescript
  - website
  - blog
  - mongodb
  - lexical
  - seo
  - forms
  - content-management
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
external_references:
  - https://github.com/payloadcms/payload/tree/main/templates/website
  - https://payloadcms.com/docs
---

# Payload CMS Website Template 3.82.1

## Overview

The official Payload CMS Website Template is a production-ready starter for building personal or enterprise-grade websites, blogs, and portfolios. It includes a fully-configured backend with MongoDB, an enterprise-grade admin panel with Lexical rich-text editor, and a beautifully designed Next.js App Router frontend with TypeScript, TailwindCSS, and shadcn/ui components.

This template provides out-of-the-box functionality for content publishing workflows, including draft previews, live preview, SEO optimization, search, redirects, form builder, scheduled publishing, and on-demand cache revalidation.

## When to Use

Use this skill when:
- Building a content-driven website, blog, or portfolio with Payload CMS
- Implementing a publication workflow with draft/publish states
- Creating a multi-page site with layout builders and reusable blocks
- Setting up SEO, search, and redirect management from the admin panel
- Integrating Next.js App Router with Payload's Local API
- Implementing live preview and draft preview functionality
- Building forms with email handlers or webhook integrations
- Managing media assets with focal point cropping and responsive images
- Configuring scheduled publishing with cron jobs
- Deploying to Vercel, Payload Cloud, or self-hosted environments

## Core Concepts

### Collections and Content Types

The template defines five core collections:

| Collection | Purpose | Features |
|------------|---------|----------|
| **Users** | Admin authentication | Auth-enabled, access control for unpublished content |
| **Pages** | Static pages (home, about, etc.) | Layout builder, draft preview, SEO fields, slugs |
| **Posts** | Blog posts and articles | Lexical editor, categories, authors, related posts, drafts |
| **Media** | Image/video uploads | Focal point, manual resize, pre-configured sizes |
| **Categories** | Post taxonomy | Nested hierarchy (e.g., "News > Technology") |

### Globals

Two global configurations manage site-wide content:

- **Header**: Navigation links and header configuration
- **Footer**: Footer links and footer configuration

### Layout Builder

Pages use a flexible layout builder with pre-built blocks:

| Block | Description |
|-------|-------------|
| Hero | Full-width hero section with multiple style variants |
| Content | Text content with columns and alignment options |
| Media | Image/video display with caption and styling options |
| Call To Action | CTA section with buttons and links |
| Archive | Post/category listing with filtering options |
| Form | Embedded forms from the form builder plugin |

Posts use the Lexical rich-text editor with inline blocks:
- Banner (callouts, alerts)
- Code (syntax-highlighted code blocks)
- Media (inline images/videos)

### Draft and Live Preview

All pages and posts support version-based drafts with:
- **Draft Mode**: Unpublished content accessible via secure preview URLs
- **Live Preview**: Real-time SSR rendering as content is edited in admin
- **Scheduled Publishing**: Auto-publish/unpublish at specified times via jobs queue
- **On-Demand Revalidation**: Next.js cache invalidation on publish

### SEO and Internationalization

Pre-configured with the Payload SEO plugin:
- Meta titles, descriptions, and Open Graph images per page/post
- Automatic sitemap generation via `next-sitemap`
- Preview component showing social share cards in admin
- Support for internationalization (i18n) setup

### Search and Redirects

- **Search Plugin**: Full-text search indexed from posts with SSR results
- **Redirects Plugin**: URL redirect management for migrations or restructures
- Both plugins integrate with Next.js middleware for runtime handling

## Quick Start

### Installation

```bash
# Clone the template using create-payload-app
pnpx create-payload-app my-project -t website

# Or manually clone from GitHub
git clone https://github.com/payloadcms/payload.git
cd payload/templates/website
```

### Environment Setup

```bash
# Copy example environment variables
cp .env.example .env

# Edit .env with your configuration
# Required: PAYLOAD_SECRET, DATABASE_URL
```

### Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Open http://localhost:3000
# Follow prompts to create first admin user
```

### Seed Demo Content

Click "Seed Database" in the admin panel to populate demo pages, posts, and categories. Creates a demo author account:
- Email: `demo-author@payloadcms.com`
- Password: `password`

> **Warning**: Seeding drops existing data. Only use on fresh databases.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Payload CMS 3.82.1 |
| Database | MongoDB (default), PostgreSQL adapters available |
| Frontend | Next.js 16.2.3 (App Router) |
| Language | TypeScript 5.7.3 |
| Styling | TailwindCSS 4.1.18, shadcn/ui components |
| Rich Text | Lexical Editor (@payloadcms/richtext-lexical) |
| Forms | React Hook Form, @payloadcms/plugin-form-builder |
| Auth | Payload authentication with access control |
| Image Processing | Sharp 0.34.2 |

## Key Features

### Publication Workflow

1. Create content as draft (not visible publicly)
2. Preview via secure draft URL or live preview panel
3. Schedule publish time or publish immediately
4. On publish, Next.js pages revalidate automatically

### Access Control

- **Users**: Full admin access to create/edit/delete content
- **Posts/Pages**: Public can read published; authenticated users manage all
- **Media**: Authenticated users upload/manage; public reads allowed
- **Categories**: Authenticated users manage; public reads allowed

### On-Demand Revalidation

When documents are published or globals updated:
1. `afterChange` hooks trigger revalidation
2. Next.js `revalidatePath()` invalidates cached pages
3. Static pages regenerate on next request
4. Image cache requires republish if focal point changes

### Scheduled Publishing

Jobs queue processes scheduled publish/unpublish tasks:
- Runs on cron schedule (configurable)
- Can run as separate instance for production
- Vercel deployment limited to daily cron on some tiers
- Requires `CRON_SECRET` for authorization

## Deployment Options

### Vercel

```bash
# Install Vercel Postgres adapter
pnpm add @payloadcms/db-vercel-postgres

# Install Vercel Blob storage (optional)
pnpm add @payloadcms/storage-vercel-blob
```

Configure in `payload.config.ts`:
```ts
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

export default buildConfig({
  db: vercelPostgresAdapter({
    pool: { connectionString: process.env.POSTGRES_URL },
  }),
  plugins: [
    vercelBlobStorage({
      collections: { media: true },
      token: process.env.BLOB_READ_WRITE_TOKEN,
    }),
  ],
})
```

### Self-Hosting

1. Build production bundle: `pnpm build`
2. Run migrations (Postgres): `pnpm payload migrate`
3. Start server: `pnpm start`
4. Deploy as any Node.js/Next.js application

### Docker

```bash
# Start with docker-compose
docker-compose up

# Uses .env file automatically
# Includes MongoDB and Payload app
```

## Reference Documentation

For detailed implementation guides, see the following reference files:

| Topic | File |
|-------|------|
| **Setup & Configuration** | [references/01-overview-and-setup.md](references/01-overview-and-setup.md) |
| **Collections & Fields** | [references/02-collections-and-fields.md](references/02-collections-and-fields.md) |
| **Pages & Posts** | [references/03-pages-and-posts.md](references/03-pages-and-posts.md) |
| **Next.js Integration** | [references/04-nextjs-integration.md](references/04-nextjs-integration.md) |
| **SEO & i18n** | [references/05-seo-and-i18n.md](references/05-seo-and-i18n.md) |
| **Form Builder** | [references/06-form-builder.md](references/06-form-builder.md) |
| **Search & Media** | [references/07-search-and-media.md](references/07-search-and-media.md) |
| **Customizations** | [references/08-customizations.md](references/08-customizations.md) |

## Common Workflows

### Create a New Page

1. Admin panel → Pages → "New Page"
2. Set title and slug (auto-generated)
3. Configure hero section (style, content, media)
4. Add layout blocks (Content, Media, CTA, Archive)
5. Configure SEO meta fields
6. Save as draft or publish immediately

### Create a Blog Post

1. Admin panel → Posts → "New Post"
2. Set title and slug
3. Upload hero image (optional)
4. Write content in Lexical editor
5. Add inline blocks (banners, code, media)
6. Assign categories and related posts
7. Configure SEO fields
8. Preview and publish

### Add a New Layout Block

1. Define block config in `src/blocks/YourBlock/config.ts`
2. Add to Pages collection `layout` field blocks array
3. Create React component in `src/blocks/YourBlock/Client.tsx`
4. Add render case to `src/blocks/RenderBlocks.tsx`
5. Style with TailwindCSS classes

### Configure Custom SEO Settings

1. SEO plugin already configured in `src/plugins/index.ts`
2. Each page/post has meta tab with:
   - Meta title (auto-generated from title)
   - Meta description
   - Meta image (from media library)
   - Preview component shows social card
3. Override `generateTitle` and `generateURL` in plugin config

### Set Up Form Notifications

1. Admin panel → Forms → "New Form"
2. Design form with drag-and-drop fields
3. Configure submission handlers:
   - Email (requires email service config)
   - Webhook (POST to external URL)
4. Embed form on page using Form block
5. Submissions stored in Form Submissions collection

## Troubleshooting

### Pages Not Revalidating

- Check `afterChange` hooks are configured
- Verify `PAYLOAD_SECRET` is set
- Ensure Next.js fetch requests include `no-store` or revalidation triggers

### Draft Preview Not Working

- Verify `versions.drafts` enabled on collection
- Check `generatePreviewPath` utility returns valid URL
- Ensure draft mode middleware is configured
- Test with authenticated admin user

### Live Preview Connection Issues

- Check `@payloadcms/live-preview-react` installed
- Verify `LivePreviewProvider` wraps app layout
- Ensure websocket connection to Payload backend
- Review browser console for connection errors

### Search Not Indexing Content

- Verify `searchPlugin` configured with correct collections
- Check `beforeSync` hook transforms data correctly
- Ensure search index collection has proper access control
- Test search API endpoint directly

## References

- **Official Template Repository**: https://github.com/payloadcms/payload/tree/main/templates/website
- **Payload CMS Documentation**: https://payloadcms.com/docs
- **Next.js Documentation**: https://nextjs.org/docs
- **Lexical Editor Docs**: https://payloadcms.com/docs/rich-text/overview
- **Plugin Documentation**:
  - SEO Plugin: https://payloadcms.com/docs/plugins/seo
  - Search Plugin: https://payloadcms.com/docs/plugins/search
  - Redirects Plugin: https://payloadcms.com/docs/plugins/redirects
  - Form Builder: https://payloadcms.com/docs/plugins/form-builder
  - Nested Docs: https://payloadcms.com/docs/plugins/nested-docs
- **Deployment Guide**: https://payloadcms.com/docs/production/deployment
- **Discord Community**: https://discord.com/invite/payload
