# Database Adapters and Plugins

## Database Adapters

Payload supports multiple database backends through adapters. Each adapter is a separate package installed alongside the core.

### MongoDB (Mongoose)

```bash
# Install separately
@payloadcms/db-mongodb
```

```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'

export default buildConfig({
  db: mongooseAdapter({
    url: process.env.MONGODB_URI || 'mongodb://localhost:27017/payload',
  }),
})
```

Default ID type: `text` (ObjectId strings).

### PostgreSQL (Drizzle)

```bash
# Install separately
@payloadcms/db-postgres
```

```typescript
import { postgresAdapter } from '@payloadcms/db-postgres'

export default buildConfig({
  db: postgresAdapter({
    pool: {
      connectionString: process.env.POSTGRES_URL || 'postgresql://localhost:5432/payload',
    },
    schema: {
      // Optional: custom table name prefixes
      collectionsTablePrefix: 'col_',
    },
  }),
})
```

Default ID type: `number` (auto-incrementing integers).

### SQLite (Drizzle)

```typescript
import { sqliteAdapter } from '@payloadcms/db-sqlite'

export default buildConfig({
  db: sqliteAdapter({
    client: {
      url: process.env.SQLITE_URL || 'file:./payload.db',
    },
  }),
})
```

Default ID type: `number`.

### Cloudflare D1 (SQLite)

```typescript
import { d1SQLiteAdapter } from '@payloadcms/db-d1-sqlite'

export default buildConfig({
  db: d1SQLiteAdapter({
    // D1 binding from Cloudflare Workers environment
  }),
})
```

### Vercel Postgres (Neon)

```typescript
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'

export default buildConfig({
  db: vercelPostgresAdapter({
    connectionString: process.env.POSTGRES_URL,
  }),
})
```

## Migrations

Payload generates and manages database migrations. Run via CLI:

```bash
# Create a new migration
npx payload migrate:create

# Run pending migrations
npx payload migrate

# Rollback last migration
npx payload migrate:down

# Show migration status
npx payload migrate:status

# Reset all migrations (drop and recreate)
npx payload migrate:fresh
```

## Storage Adapters

Replace the default filesystem upload storage:

### S3

```typescript
import { s3Storage } from '@payloadcms/storage-s3'

plugins: [
  s3Storage({
    collections: ['media'],
    bucket: process.env.S3_BUCKET,
    config: {
      region: process.env.S3_REGION,
      credentials: {
        accessKeyId: process.env.S3_ACCESS_KEY_ID,
        secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
      },
    },
  }),
]
```

### Cloudflare R2

```typescript
import { r2Storage } from '@payloadcms/storage-r2'

plugins: [
  r2Storage({
    collections: ['media'],
    bucket: process.env.R2_BUCKET,
    config: {
      accountID: process.env.R2_ACCOUNT_ID,
      credentials: {
        accessKeyId: process.env.R2_ACCESS_KEY_ID,
        secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
      },
      endpoint: `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
      region: 'auto',
    },
  }),
]
```

### Google Cloud Storage

```typescript
import { gcsStorage } from '@payloadcms/storage-gcs'

plugins: [
  gcsStorage({
    collections: ['media'],
    bucket: process.env.GCS_BUCKET,
  }),
]
```

### Azure Blob Storage

```typescript
import { azureStorage } from '@payloadcms/storage-azure'

plugins: [
  azureStorage({
    collections: ['media'],
    container: process.env.AZURE_CONTAINER,
  }),
]
```

### Vercel Blob

```typescript
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

plugins: [
  vercelBlobStorage({
    collections: ['media'],
  }),
]
```

## Official Plugins

### SEO Plugin

Add SEO fields to collections:

```typescript
import { seoPlugin } from '@payloadcms/plugin-seo'

plugins: [
  seoPlugin({
    collections: ['pages', 'posts'],
  }),
]
```

Use SEO field components in your collection:

```typescript
import {
  OverviewField,
  MetaTitleField,
  MetaImageField,
  MetaDescriptionField,
  PreviewField,
} from '@payloadcms/plugin-seo/fields'

// In your collection fields
{
  name: 'meta',
  label: 'SEO',
  fields: [
    OverviewField({ titlePath: 'meta.title', descriptionPath: 'meta.description', imagePath: 'meta.image' }),
    MetaTitleField({ hasGenerateFn: true }),
    MetaImageField({ relationTo: 'media' }),
    MetaDescriptionField({}),
    PreviewField({ hasGenerateFn: true, titlePath: 'meta.title', descriptionPath: 'meta.description' }),
  ],
}
```

### Search Plugin

Add full-text search to collections:

```typescript
import { searchPlugin } from '@payloadcms/plugin-search'

plugins: [
  searchPlugin({
    collections: ['posts'],
    searchCollection: {
      fields: {
        // Custom fields on the search index
      },
    },
  }),
]
```

### Form Builder Plugin

Create and manage forms:

```typescript
import { formBuilderPlugin } from '@payloadcms/plugin-form-builder'

plugins: [
  formBuilderPlugin({
    fields: {
      payment: false, // Disable Stripe payment fields
    },
  }),
]
```

### Redirects Plugin

Manage URL redirects:

```typescript
import { redirectsPlugin } from '@payloadcms/plugin-redirects'

plugins: [
  redirectsPlugin({
    collections: ['pages', 'posts'],
    overrides: (req) => ({
      // Custom redirect logic
    }),
  }),
]
```

### Nested Docs Plugin

Add folder-like hierarchy to collections:

```typescript
import { nestedDocsPlugin } from '@payloadcms/plugin-nested-docs'

plugins: [
  nestedDocsPlugin({
    collections: ['pages'],
    generateURL: ({ doc }) => `/pages/${doc.slug}`,
  }),
]
```

### Stripe Plugin

Integrate Stripe payments:

```typescript
import { stripePlugin } from '@payloadcms/plugin-stripe'

plugins: [
  stripePlugin({
    apiKey: process.env.STRIPE_SECRET_KEY,
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET,
    categories: true,
    products: true,
    prices: true,
  }),
]
```

### Sentry Plugin

Add error monitoring:

```typescript
import { sentryPlugin } from '@payloadcms/plugin-sentry'

plugins: [
  sentryPlugin({
    dsn: process.env.SENTRY_DSN,
  }),
]
```

### Cloud Storage Plugin

Unified cloud storage with Payload Cloud:

```typescript
import { payloadCloudPlugin } from '@payloadcms/payload-cloud'

plugins: [
  payloadCloudPlugin(),
]
```

## Email Adapters

### Nodemailer

```typescript
import { nodemailerAdapter } from '@payloadcms/email-nodemailer'

export default buildConfig({
  email: nodemailerAdapter({
    defaultFromAddress: 'noreply@example.com',
    defaultFromName: 'My Site',
    transport: {
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT),
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    },
  }),
})
```

### Resend

```typescript
import { resendAdapter } from '@payloadcms/email-resend'

export default buildConfig({
  email: resendAdapter({
    defaultFromAddress: 'noreply@example.com',
    defaultFromName: 'My Site',
    apiKey: process.env.RESEND_API_KEY,
  }),
})
```

## Plugin Architecture

Create custom plugins as functions that transform the config:

```typescript
import type { Plugin } from 'payload'

export const myPlugin: Plugin = (config) => ({
  ...config,
  collections: [
    ...(config.collections || []),
    {
      slug: 'my-plugin-docs',
      fields: [{ name: 'data', type: 'json' }],
    },
  ],
})
```

Register in config:

```typescript
export default buildConfig({
  plugins: [myPlugin],
  // ...
})
```

## Jobs System

Payload includes a built-in job system for background tasks:

```typescript
export default buildConfig({
  jobs: {
    access: {
      run: ({ req }) => {
        if (req.user) return true
        const secret = process.env.CRON_SECRET
        if (!secret) return false
        return req.headers.get('authorization') === `Bearer ${secret}`
      },
    },
    tasks: [
      {
        name: 'send-newsletter',
        handler: async ({ payload, progress }) => {
          const subscribers = await payload.find({ collection: 'subscribers' })
          for (let i = 0; i < subscribers.docs.length; i++) {
            await sendEmail(subscribers.docs[i].email)
            progress(i / subscribers.docs.length)
          }
        },
      },
    ],
    workflows: [
      {
        name: 'publish-and-notify',
        tasks: ['send-newsletter', 'update-analytics'],
      },
    ],
  },
})
```

## Deployment Considerations

- **Vercel**: Use `@payloadcms/db-vercel-postgres` with Neon, or MongoDB Atlas. Deploy as serverless.
- **Cloudflare**: Use `@payloadcms/db-d1-sqlite` with D1 database and R2 for storage.
- **Docker**: Any adapter works. Run Payload in a container with the database externally.
- **Always set** `PAYLOAD_SECRET` in production — never hardcode it.
- **Database migrations** should run during deployment before starting the server.
