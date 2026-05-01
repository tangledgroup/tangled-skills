---
name: payloadcms-blank-3-84-1
description: Minimal Payload CMS 3.84.1 starter template providing a clean foundation for building custom headless CMS applications with Next.js App Router, MongoDB, and Lexical editor. Use when starting new Payload projects from scratch, needing a minimal configuration without pre-built collections or content types, or requiring full control over data modeling and admin panel customization.
version: "3.84.1"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - cms
  - payload
  - nextjs
  - mongodb
  - headless-cms
  - react
  - typescript
category: development
external_references:
  - https://payloadcms.com/docs/richtext/lexical/overview
  - https://payloadcms.com/docs/getting-started/requirements
  - https://payloadcms.com/docs
  - https://github.com/payloadcms/payload/tree/v3.84.1/templates/blank
  - https://discord.com/invite/payload
---

# Payload CMS Blank Template v3.84.1

## Overview

The blank template is the minimal starting point for Payload CMS 3.84.1 projects. It provides a clean, opinionated foundation built on Next.js 16 with App Router, MongoDB as the database adapter, Lexical as the rich-text editor, and React 19 for the admin UI. Unlike other Payload templates that include pre-built collections and content types, the blank template ships with only the essential Users and Media collections — giving you full control over data modeling from day one.

The template is designed to be extended. You add collections, fields, access control rules, custom React components, and API routes as your project requires. It supports both local development and Docker-based workflows, with production-ready build and deployment configurations included out of the box.

Key dependencies in the blank template:

- `payload` — core CMS framework
- `@payloadcms/next` — Next.js integration with server functions and layouts
- `@payloadcms/db-mongodb` — MongoDB database adapter
- `@payloadcms/richtext-lexical` — Lexical-based rich-text editor
- `@payloadcms/ui` — admin panel UI components
- `next` 16.2.2 — React framework with App Router
- `react` 19.2.4 / `react-dom` 19.2.4 — frontend library
- `sharp` 0.34.2 — image processing for media uploads
- `graphql` — built-in GraphQL API support

New in 3.83/3.84:

- `create-payload-app` supports `--agent` flag for coding agent skill installation
- `definePlugin` helper for type-safe plugin development with execution ordering
- Drizzle adapter supports uuidv7 IDs
- Lexical view override system for custom node rendering
- Client components can be used as custom collection views

## When to Use

Use this skill when:

- Starting a new Payload CMS project from scratch with no pre-built content
- Needing a minimal configuration that you fully control
- Building a custom headless CMS where data modeling is project-specific
- Setting up a Payload development environment locally or in Docker
- Understanding the blank template file structure and conventions
- Extending the default Users and Media collections
- Configuring the Payload config, Next.js config, or TypeScript paths
- Deploying a Payload app to production with Docker

## Core Concepts

**Payload CMS** is a type-safe, API-first headless CMS and application framework. It generates REST and GraphQL APIs automatically from your TypeScript configuration. The admin panel is a React-based UI that runs inside the same Next.js application.

**The blank template philosophy** is minimalism. It ships with only what is required for Payload to function — a Users collection for authentication and a Media collection for file uploads. Everything else is added by you. This contrasts with the website or ecommerce templates, which include pre-built pages, posts, products, and carts.

**Collections** are the primary data model in Payload. Each collection defines a set of fields, access control rules, and hooks. Collections map to database collections (MongoDB) or tables (PostgreSQL). The blank template includes:

- `users` — authentication-enabled collection for admin panel access
- `media` — upload-enabled collection for images and files

**Lexical Editor** is the default rich-text editor in Payload 3.x. It replaces Slate from earlier versions and provides a modern, extensible editing experience with plugins for headings, lists, links, images, and custom content types. New in 3.83: view override system for custom node rendering.

**Next.js App Router** is used for both the admin panel and any frontend pages. Route groups like `(payload)` and `(frontend)` organize routes without affecting URL paths. Server components can access Payload's Local API directly using `getPayload()`.

**TypeScript-first development** means all configuration, collections, and hooks are written in TypeScript. Payload generates types automatically via `payload generate:types`, producing a `payload-types.ts` file that keeps your entire stack type-safe.

## Installation / Setup

### System Requirements

- Node.js 18.20.2+ or 20.9.0+
- pnpm 9+ or 10+ (preferred package manager)
- MongoDB instance (local, Docker, or cloud)

### Quick Start

Create a new project from the blank template:

```bash
# Initialize with create-payload
npx create-payload-app@latest my-project --template blank

# New in 3.83: install coding agent skills alongside the project
npx create-payload-app@latest my-project --template blank --agent
```

Or clone the template directly:

```bash
git clone https://github.com/payloadcms/payload.git my-project
cd my-project
# Checkout the specific version tag and copy templates/blank contents
```

### Local Development

1. Copy environment variables:

```bash
cp .env.example .env
```

The `.env` file requires two variables:

```
DATABASE_URL=mongodb://127.0.0.1/your-database-name
PAYLOAD_SECRET=YOUR_SECRET_HERE
```

2. Install dependencies and start the dev server:

```bash
pnpm install
pnpm dev
```

3. Open `http://localhost:3000` in your browser. Follow on-screen instructions to create your first admin user.

### Docker Development

The template includes a `docker-compose.yml` that runs both Payload and MongoDB:

```bash
# Ensure DATABASE_URL in .env points to the mongo service
DATABASE_URL=mongodb://mongo/your-database-name

# Start both services
docker-compose up
```

The compose file runs Payload in a Node 20 Alpine container with hot-reload volumes, and MongoDB with WiredTiger storage engine on port 27017.

### Available Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start Next.js development server |
| `pnpm build` | Production build with increased memory limit |
| `pnpm start` | Run production server |
| `pnpm generate:types` | Regenerate TypeScript types from config |
| `pnpm generate:importmap` | Generate admin import map |
| `pnpm lint` | Run ESLint |
| `pnpm test` | Run integration and e2e tests |

## Advanced Topics

**Project Structure**: File tree, route groups, and directory conventions → [Project Structure](reference/01-project-structure.md)

**Collections and Fields**: Users and Media collections, field types, access control, and upload configuration → [Collections and Fields](reference/02-collections-and-fields.md)

**Configuration Files**: payload.config.ts, next.config.ts, tsconfig.json, and environment setup → [Configuration Files](reference/03-configuration-files.md)

**Database and Deployment**: MongoDB adapter, Docker production builds, docker-compose patterns, and deployment considerations → [Database and Deployment](reference/04-database-and-deployment.md)
