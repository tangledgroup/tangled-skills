# Configuration Options Reference

Complete guide to Payload CMS v3.82.1 configuration including all config options, database setup, and environment requirements.

## Configuration Overview

Payload configuration is defined in `payload.config.ts` and controls:
- Collections and globals
- Database connection
- Authentication settings
- Admin panel customization
- API endpoints
- Plugins

### Minimal Configuration

```typescript
import { buildConfig } from 'payload'
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  // Secret for JWT and session cookies
  secret: process.env.PAYLOAD_SECRET,
  
  // Admin panel configuration
  admin: {
    user: 'users', // Collection with authentication
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  
  // Rich text editor
  editor: lexicalEditor(),
  
  // Collections
  collections: [Users, Posts, Media],
  
  // Globals
  globals: [Header, Footer],
  
  // Database adapter
  db: mongooseAdapter({
    url: process.env.DATABASE_URL,
  }),
  
  // TypeScript configuration
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
})
```

## Required Configuration

### Secret

**Required**: Cryptographic secret for JWT tokens and session cookies.

```typescript
export default buildConfig({
  secret: process.env.PAYLOAD_SECRET, // Minimum 32 characters
})
```

**Generate secret**:
```bash
openssl rand -base64 32
# or
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### Database Adapter

**Required**: Database connection configuration.

#### MongoDB (Mongoose)

```typescript
import { mongooseAdapter } from '@payloadcms/db-mongodb'

export default buildConfig({
  db: mongooseAdapter({
    url: process.env.DATABASE_URL, // mongodb://localhost:27017/payload
  }),
})
```

**With replica set (for transactions)**:
```typescript
db: mongooseAdapter({
  url: 'mongodb://user:pass@host1:27017,host2:27017,host3:27017/payload?replicaSet=rs0',
})
```

#### PostgreSQL

```typescript
import { postgresAdapter } from '@payloadcms/db-postgresql'

export default buildConfig({
  db: postgresAdapter({
    pool: {
      connectionString: process.env.DATABASE_URL, // postgresql://user:pass@host/db
    },
  }),
})
```

**With Prisma**:
```typescript
import { pgAdapter } from '@payloadcms/db-postgres'
import { prisma } from './prisma'

export default buildConfig({
  db: pgAdapter({
    pool: prisma.$connection,
  }),
})
```

#### SQLite

```typescript
import { sqliteAdapter } from '@payloadcms/db-sqlite'

export default buildConfig({
  db: sqliteAdapter({
    client: new BetterSQLite3('./payload.db'),
  }),
})
```

## Admin Configuration

### Basic Admin Settings

```typescript
export default buildConfig({
  admin: {
    // Collection slug for admin authentication
    user: 'users',
    
    // Logo component
    logo: '/components/Logo.svg',
    
    // Meta title for browser tab
    meta: {
      titleSuffix: ' - My CMS',
    },
    
    // Base path for admin panel
    basePath: 'admin',
    
    // Disable local API (server-only mode)
    disableLocalAPI: false,
    
    // Auto-login for development
    autoLogin: {
      email: 'admin@example.com',
      password: 'password',
    },
  },
})
```

### Import Map Configuration

Configure component path resolution:

```typescript
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    importMap: {
      // Base directory for component paths
      baseDir: path.resolve(dirname, 'src'),
      
      // Custom import map file location
      importMapFile: path.resolve(dirname, 'app', 'custom-import-map.js'),
    },
  },
})
```

### Theme Configuration

Customize admin panel appearance:

```typescript
export default buildConfig({
  admin: {
    theme: {
      cssVariables: {
        light: {
          brand: '#3b82f6',
          'brand-background': '#eff6ff',
        },
        dark: {
          brand: '#60a5fa',
          'brand-background': '#1e3a5f',
        },
      },
    },
  },
})
```

## Collections Configuration

### Collection Schema

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  // Required: Unique identifier
  slug: 'posts',
  
  // Optional: Human-readable labels
  labels: {
    singular: 'Post',
    plural: 'Posts',
  },
  
  // Required: Field definitions
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
  ],
  
  // Optional: Access control
  access: {
    read: () => true,
    create: ({ req: { user } }) => Boolean(user),
    update: ({ req: { user } }) => Boolean(user),
    delete: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
  
  // Optional: Authentication configuration
  auth: true,
  
  // Optional: Lifecycle hooks
  hooks: {
    beforeValidate: [/* ... */],
    beforeChange: [/* ... */],
    afterChange: [/* ... */],
    afterRead: [/* ... */],
    beforeDelete: [/* ... */],
  },
  
  // Optional: Admin panel customization
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
    description: 'Blog posts and articles',
    hidden: false,
    preview: (doc) => `/preview?slug=${doc.slug}`,
  },
  
  // Optional: Versioning and drafts
  versions: {
    drafts: {
      autosave: true,
      schedulePublish: true,
      validate: false,
    },
    maxPerDoc: 100,
    retainDrafts: true,
  },
  
  // Optional: Timestamps
  timestamps: true,
  
  // Optional: GraphQL configuration
  graphql: {
    name: 'Post',
    singularName: 'post',
    version: 4,
  },
  
  // Optional: REST API configuration
  rest: true,
  
  // Optional: Database indexes
  indexes: [
    { fields: ['status', 'createdAt'], keys: { status: 1, createdAt: -1 } },
    { fields: ['author'], keys: { author: 1 } },
  ],
}
```

### Upload Collection Configuration

```typescript
export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true, // Public access to uploaded files
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
      label: 'Alt Text',
    },
  ],
  upload: {
    // Local file storage
    staticDir: './media',
    
    // Or use external storage adapter
    // storageAdapter: s3StorageAdapter({
    //   bucket: 'my-bucket',
    //   accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    //   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    //   region: 'us-east-1',
    // }),
    
    // File type restrictions
    mimeTypes: ['image/*'],
    
    // Auto-generate image sizes
    imageSizes: [
      {
        name: 'thumbnail',
        width: 200,
        height: 200,
        fit: 'cover',
      },
      {
        name: 'medium',
        width: 800,
        height: 600,
        position: 'center',
      },
    ],
    
    // Filename customization
    filename: ({ doc }) => `${Date.now()}-${doc.originalFilename}`,
  },
}
```

## Globals Configuration

### Global Schema

```typescript
import type { GlobalConfig } from 'payload'

export const Header: GlobalConfig = {
  // Required: Unique identifier
  slug: 'header',
  
  // Optional: Labels
  labels: {
    singular: 'Header',
    plural: 'Headers',
  },
  
  // Required: Field definitions
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
  
  // Optional: Access control
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
  
  // Optional: Admin customization
  admin: {
    description: 'Site header configuration',
  },
  
  // Optional: Versioning
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
  
  // Optional: GraphQL configuration
  graphql: {
    name: 'Header',
  },
}
```

## Editor Configuration

### Lexical Editor (Default)

```typescript
import { lexicalEditor } from '@payloadcms/richtext-lexical'

export default buildConfig({
  editor: lexicalEditor({
    features: () => [
      lexicalFeatureHeading(),
      lexicalFeatureBold(),
      lexicalFeatureItalic(),
      lexicalFeatureLink({
        enabledCollections: ['posts', 'pages'],
        fields: ({ defaultFields }) => [
          ...defaultFields,
          {
            name: 'rel',
            type: 'select',
            options: ['noopener', 'nofollow'],
            hasMany: true,
          },
        ],
      }),
    ],
  }),
})
```

## Localization (i18n) Configuration

### Multi-language Support

```typescript
export default buildConfig({
  localization: {
    locales: [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Spanish' },
      { code: 'fr', label: 'French' },
    ],
    defaultLocale: 'en',
    fallback: true, // Use default locale if translation missing
  },
})
```

### Localized Fields

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'title', type: 'text', localized: true, required: true },
    { name: 'content', type: 'richText', localized: true },
    { name: 'slug', type: 'text', localized: false, unique: true }, // Not localized
  ],
}
```

## Email Configuration

### Nodemailer Setup

```typescript
import { nodemailerAdapter } from '@payloadcms/email-nodemailer'

export default buildConfig({
  email: nodemailerAdapter({
    defaultFromAddress: 'noreply@example.com',
    defaultFromName: 'My CMS',
    transport: {
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: false,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASSWORD,
      },
    },
  }),
})
```

## Plugins Configuration

### Using Plugins

```typescript
import { seoPlugin } from '@payloadcms/plugin-seo'
import { redirectsPlugin } from '@payloadcms/plugin-redirects'
import { nestedDocsPlugin } from '@payloadcms/plugin-nested-docs'

export default buildConfig({
  plugins: [
    // SEO plugin for posts and pages
    seoPlugin({
      collections: ['posts', 'pages'],
    }),
    
    // Redirects plugin
    redirectsPlugin({
      collections: ['pages'],
      overrides: {
        slug: 'redirects',
      },
    }),
    
    // Nested docs for categories
    nestedDocsPlugin({
      collection: 'categories',
      titleField: 'name',
    }),
  ],
})
```

## TypeScript Configuration

### Type Generation

```typescript
export default buildConfig({
  typescript: {
    // Output file for generated types
    outputFile: './payload-types.ts',
    
    // Declare types globally (no imports needed)
    declare: true,
  },
})
```

**Generated types usage**:
```typescript
import type { Post, User } from './payload-types'

function handlePost(post: Post) {
  console.log(post.title) // Fully typed
}
```

## API Configuration

### Custom Endpoints

```typescript
export default buildConfig({
  endpoints: [
    {
      path: '/api/health',
      method: 'get',
      handler: async () => {
        return Response.json({ status: 'ok' })
      },
    },
    {
      path: '/api/custom/posts',
      method: 'get',
      handler: async (req) => {
        const { payload } = req
        
        const posts = await payload.find({
          collection: 'posts',
          where: { status: { equals: 'published' } },
        })
        
        return Response.json(posts)
      },
    },
  ],
})
```

### Middleware

```typescript
export default buildConfig({
  endpoints: [
    {
      path: '/api/protected/*',
      method: 'all',
      handler: async (req) => {
        // Authentication middleware
        if (!req.user) {
          throw new APIError('Unauthorized', 401)
        }
        
        // Continue to next handler...
      },
    },
  ],
})
```

## Server Configuration

### Port and Host

```typescript
export default buildConfig({
  serverURL: process.env.PAYLOAD_PUBLIC_SERVER_URL || 'http://localhost:3000',
})
```

### Rate Limiting

```typescript
import rateLimit from 'express-rate-limit'

export default buildConfig({
  express: (app) => {
    app.use(rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // Limit each IP to 100 requests per windowMs
    }))
    
    return app
  },
})
```

## Environment Variables

### Required Environment Variables

```bash
# .env file
PAYLOAD_SECRET=your-secret-key-minimum-32-characters
DATABASE_URL=mongodb://localhost:27017/payload
PAYLOAD_PUBLIC_SERVER_URL=http://localhost:3000
```

### Optional Environment Variables

```bash
# Email configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password

# AWS S3 for file uploads
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# External services
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG....
```

### Public Environment Variables

Prefix with `PAYLOAD_PUBLIC_` for client-side access:

```bash
PAYLOAD_PUBLIC_SITE_URL=https://example.com
PAYLOAD_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

**Access in components**:
```typescript
const siteURL = process.env.PAYLOAD_PUBLIC_SITE_URL
```

## Production Configuration

### Production Checklist

```typescript
export default buildConfig({
  // Use environment variable for secret
  secret: process.env.PAYLOAD_SECRET,
  
  // Disable auto-login in production
  admin: {
    autoLogin: process.env.NODE_ENV === 'development' ? {
      email: 'admin@example.com',
      password: 'password',
    } : undefined,
  },
  
  // Enable security headers
  express: (app) => {
    app.use((req, res, next) => {
      res.setHeader('X-Content-Type-Options', 'nosniff')
      res.setHeader('X-Frame-Options', 'DENY')
      res.setHeader('X-XSS-Protection', '1; mode=block')
      next()
    })
    return app
  },
  
  // Database connection pooling for production
  db: mongooseAdapter({
    url: process.env.DATABASE_URL,
    poolSize: 10,
  }),
})
```

### Security Best Practices

```typescript
export default buildConfig({
  // Restrict admin panel access
  admin: {
    user: 'users',
    webpack: (config) => ({
      ...config,
      // Disable source maps in production
      devtool: process.env.NODE_ENV === 'development' ? 'eval-cheap-module-source-map' : false,
    }),
  },
  
  // CORS configuration
  express: (app) => {
    const cors = require('cors')
    app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true,
    }))
    return app
  },
})
```

## Common Configuration Patterns

### Multi-tenant Setup

```typescript
export default buildConfig({
  collections: [
    Tenants,
    {
      ...Posts,
      fields: [
        {
          name: 'tenant',
          type: 'relationship',
          relationTo: 'tenants',
          required: true,
          index: true,
        },
        ...Posts.fields,
      ],
      access: {
        read: ({ req: { user } }) => ({ tenant: { equals: user.tenant } }),
      },
    },
  ],
})
```

### E-commerce Setup

```typescript
export default buildConfig({
  collections: [
    Products,
    Orders,
    OrderItems,
    CartItems,
  ],
  plugins: [
    ecommercePlugin({
      currencies: ['USD', 'EUR', 'GBP'],
      taxEnabled: true,
    }),
  ],
})
```

### Multi-language Blog

```typescript
export default buildConfig({
  localization: {
    locales: [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Spanish' },
      { code: 'fr', label: 'French' },
    ],
    defaultLocale: 'en',
    fallback: true,
  },
  collections: [
    {
      ...Posts,
      fields: [
        { name: 'title', type: 'text', localized: true, required: true },
        { name: 'slug', type: 'text', localized: true, unique: true },
        { name: 'content', type: 'richText', localized: true },
      ],
    },
  ],
})
```

## Troubleshooting Configuration

### Common Issues

**Types not generated**:
- Run `npm run generate:types`
- Check `typescript.outputFile` path is correct
- Verify collections are properly exported

**Import map errors**:
- Regenerate import map: `payload generate:importmap`
- Check component paths are relative to `baseDir`
- Verify file extensions are correct

**Database connection failures**:
- Check DATABASE_URL format is correct
- Verify database is running and accessible
- For MongoDB transactions, ensure replica set is configured

**Admin panel not loading**:
- Check `admin.user` points to valid collection with auth enabled
- Verify secret is set and at least 32 characters
- Check browser console for JavaScript errors
