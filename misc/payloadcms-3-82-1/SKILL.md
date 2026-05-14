---
name: payloadcms-3-82-1
description: Payload CMS headless CMS toolkit including collections, fields, access control, authentication, custom components, and Local API operations. Use when building content management systems, creating admin interfaces, implementing role-based access control, developing custom React components, or integrating with Next.js applications.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - cms
  - headless-cms
  - content-management
  - nextjs
  - typescript
  - react
  - database
  - admin-panel
category: development
external_references:
  - https://payloadcms.com/docs
  - https://github.com/payloadcms/payload
---

# Payload CMS 3.82.1

## Overview

Payload is the open-source, fullstack Next.js framework that gives you instant backend superpowers. It installs directly into your existing `/app` folder, providing a full TypeScript backend and admin panel. Use it as a headless CMS or for building powerful applications. Payload 3.x replatformed the Admin Panel from a React Router SPA onto the Next.js App Router with full React Server Components support, completely separating core logic from HTTP and rendering layers.

Key capabilities:

- **Next.js native** — runs inside your `/app` folder, no separate server
- **TypeScript-first** — automatic type generation for all data models
- **Local API** — query the database directly in server components without REST/GraphQL
- **Built-in auth** — user management with JWT, API keys, and custom strategies
- **Versions and drafts** — document versioning with autosave and scheduled publishing
- **Localization** — multi-language content with fallback support
- **Block-based layout builder** — composable content blocks for flexible page design
- **Lexical rich text editor** — extensible WYSIWYG editor with custom features
- **Granular access control** — collection, field, and document-level permissions
- **Extensive hooks system** — document and field-level hooks for every operation
- **HTTP-only cookies, CSRF protection** — enterprise-grade security by default

## When to Use

- Building a headless CMS with a customizable React admin panel
- Creating content-driven websites with Next.js App Router
- Implementing role-based access control with fine-grained permissions
- Building applications that need built-in authentication and user management
- Creating block-based page builders or content management interfaces
- Integrating versioning, drafts, and scheduled publishing workflows
- Working with multi-language content requiring localization
- Extending the admin UI with custom React Server Components
- Building REST APIs or GraphQL endpoints on top of typed data models

## Core Concepts

**Collections** are the primary data model — similar to database tables. Each collection defines a slug, fields, access control, hooks, and admin UI configuration. Collections can enable authentication (`auth: true`), file uploads (`upload: true`), or versioning (`versions: { drafts: true }`).

**Globals** are singleton documents for site-wide content like headers, footers, and settings. Unlike collections, globals have no list view — only a single editable document.

**Fields** define the data shape within collections and globals. Payload supports text, number, email, textarea, code, date, point, radio, checkbox, select, richText, upload, relationship, join, group, row, tabs, collapsible, array, blocks, hidden, and json field types. Fields support validation, hooks, access control, localization, and conditional visibility.

**Access Control** operates at three levels: collection-level (create/read/update/delete), field-level (read/write per field), and document-level (returning a Where query to filter visible documents). Access functions receive the request context including the authenticated user.

**Hooks** run at every stage of the document lifecycle: `beforeValidate`, `beforeChange`, `afterChange`, `beforeRead`, `afterRead`, `beforeDelete`, `afterDelete`, and field-level hooks (`beforeValidate`, `beforeChange`, `afterChange`, `afterRead`, `beforeDuplicate`). Hooks can transform data, enforce business rules, trigger side effects, and integrate with external services.

**The Payload Config** (`payload.config.ts`) is the central configuration file defining collections, globals, database adapter, admin panel settings, plugins, custom endpoints, email adapter, localization, and more. It uses `buildConfig()` from the `payload` package.

## Project Structure

A typical Payload project:

```
my-project/
├── src/
│   ├── app/
│   │   └── (payload)/
│   │       ├── admin/    # Admin panel routes (auto-generated)
│   │       └── api/      # API routes (auto-generated)
│   ├── collections/
│   │   ├── Users.ts
│   │   ├── Media.ts
│   │   └── Pages.ts
│   ├── globals/
│   │   ├── Header.ts
│   │   └── Footer.ts
│   ├── blocks/
│   │   ├── Content/
│   │   └── MediaBlock/
│   ├── access/
│   │   ├── authenticated.ts
│   │   └── authenticatedOrPublished.ts
│   ├── hooks/
│   │   └── populatePublishedAt.ts
│   ├── payload.config.ts
│   └── payload-types.ts  # auto-generated types
├── package.json
└── tsconfig.json
```

## Quick Start

Create a new project with the blank template:

```bash
npx create-payload-app@latest my-project
cd my-project
pnpm dev
```

Or use the website template for a full-featured starter:

```bash
npx create-payload-app@latest -t website
```

## Usage Examples

### Minimal Payload Config

```typescript
// payload.config.ts
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { buildConfig } from 'payload'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

import { Users } from './collections/Users'
import { Media } from './collections/Media'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: Users.slug,
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Media],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URL || '',
  }),
  sharp,
  plugins: [],
})
```

### Collection with Auth

```typescript
// collections/Users.ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',
  },
  auth: true,
  fields: [
    // Email and password fields added automatically
  ],
}
```

### Collection with Uploads

```typescript
// collections/Media.ts
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,  // public access
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
    },
  ],
  upload: true,
}
```

### Access Control Functions

```typescript
// access/authenticated.ts
import type { AccessArgs } from 'payload'
import type { User } from '@/payload-types'

export const authenticated = ({ req: { user } }: AccessArgs<User>) => {
  return Boolean(user)
}

// access/authenticatedOrPublished.ts
import type { Access } from 'payload'

export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  if (user) return true
  return { _status: { equals: 'published' } }
}
```

### Using the Local API in Server Components

```typescript
import { getPayload } from 'payload'
import configPromise from '@/payload.config'

export async function getPosts() {
  const payload = await getPayload({ config: configPromise })
  const posts = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    sort: '-publishedAt',
  })
  return posts.docs
}
```

## Advanced Topics

**Collections and Fields**: Deep dive into all field types, validation, relationships, joins, blocks, arrays, and rich text configuration → [Collections and Fields](reference/01-collections-and-fields.md)

**Access Control and Authentication**: Role-based permissions, custom auth strategies, API keys, JWT configuration, and field-level access → [Access Control and Authentication](reference/02-access-control-and-auth.md)

**Hooks and Lifecycle**: Document hooks, field hooks, before/after operation patterns, and integration with external services → [Hooks and Lifecycle](reference/03-hooks-and-lifecycle.md)

**Local API and Queries**: The `Where` query system, depth/population, select/projection, pagination, sorting, joins, and transactions → [Local API and Queries](reference/04-local-api-and-queries.md)

**Versions, Drafts, and Localization**: Document versioning, autosave drafts, scheduled publishing, multi-language content, and fallback locales → [Versions Drafts and Localization](reference/05-versions-drafts-and-localization.md)

**Admin Panel Customization**: Custom React components, views, tabs, live preview, dashboard widgets, and theme configuration → [Admin Panel Customization](reference/06-admin-panel-customization.md)

**Database Adapters and Plugins**: MongoDB, Postgres, SQLite, Drizzle ORM adapter patterns, storage adapters, and official plugins → [Database Adapters and Plugins](reference/07-database-adapters-and-plugins.md)
