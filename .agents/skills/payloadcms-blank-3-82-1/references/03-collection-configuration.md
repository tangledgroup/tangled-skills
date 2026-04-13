# Collection Configuration

Complete guide to configuring collections in Payload CMS blank template, including the pre-configured Users and Media collections, custom collection patterns, and field types.

## Pre-configured Collections

### Users Collection (Authentication)

**Location:** `src/collections/Users.ts`

```typescript
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',
  },
  auth: true,
  fields: [
    // Email added by default
    // Add more fields as needed
  ],
}
```

**Configuration Details:**

**slug: 'users'**
- Unique identifier for the collection
- Used in URLs: `/admin/collections/users`
- Used in API: `/api/users`
- Must be lowercase, URL-friendly

**admin.useAsTitle: 'email'**
- Field used to display document titles in lists
- Appears in relationship selects, list views
- Email is default for auth collections

**auth: true**
- Enables authentication for this collection
- Automatically adds:
  - Email field (required)
  - Password field (required)
  - Login/logout functionality
  - Reset password flow
  - Account creation page
- Creates admin panel routes:
  - `/admin/login`
  - `/admin/forgot-password`
  - `/admin/reset-password`

**Auto-generated Fields (when auth: true):**

```typescript
// Added automatically by Payload
{
  name: 'email',
  type: 'email',
  required: true,
  unique: true,
  admin: {
    readOnly: true, // Can't be changed after creation
  },
}

{
  name: 'password',
  type: 'text',
  required: true,
  admin: {
    readOnly: true,
    hidden: true, // Hidden in UI
  },
}

// Additional auth fields (internal)
{
  name: 'resetPasswordToken',
  type: 'text',
}

{
  name: 'resetPasswordExpiration',
  type: 'date',
}

{
  name: 'salt',
  type: 'text',
}

{
  name: 'hash',
  type: 'text',
}

{
  name: 'refreshToken',
  type: 'text',
}
```

**Timestamps:**
Payload automatically adds `createdAt` and `updatedAt` fields to all collections.

### Adding Custom Fields to Users

```typescript
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: {
    useAsTitle: 'email',
    defaultColumns: ['email', 'roles', 'createdAt'],
  },
  fields: [
    // User roles for RBAC
    {
      name: 'roles',
      type: 'select',
      hasMany: true, // Multiple roles per user
      options: [
        { label: 'Admin', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'User', value: 'user' },
      ],
      defaultValue: ['user'],
      required: true,
      saveToJWT: true, // Include in JWT for fast access checks
    },

    // Profile information
    {
      name: 'name',
      type: 'group',
      fields: [
        {
          name: 'firstName',
          type: 'text',
        },
        {
          name: 'lastName',
          type: 'text',
        },
      ],
    },

    // Avatar image
    {
      name: 'avatar',
      type: 'upload',
      relationTo: 'media',
    },

    // Bio text
    {
      name: 'bio',
      type: 'richText',
    },
  ],
}
```

### Media Collection (Uploads)

**Location:** `src/collections/Media.ts`

```typescript
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true, // Public read access
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true, // Alt text required for accessibility
    },
  ],
  upload: true,
}
```

**Configuration Details:**

**slug: 'media'**
- Collection identifier for media files
- API endpoint: `/api/media`

**access.read: () => true**
- Allows unauthenticated users to read media documents
- Required for public image serving
- Without this, uploaded images would be private

**upload: true**
- Enables file upload functionality
- Automatically adds:
  - File storage and retrieval
  - Image optimization (via Sharp)
  - URL generation
  - Thumbnail generation
  - File metadata extraction

**Auto-generated Fields (when upload: true):**

```typescript
// Added automatically by Payload
{
  name: 'url',
  type: 'text',
}

{
  name: 'filename',
  type: 'text',
}

{
  name: 'mimeType',
  type: 'text',
}

{
  name: 'filesize',
  type: 'number',
}

// Image-specific (if image uploaded)
{
  name: 'width',
  type: 'number',
}

{
  name: 'height',
  type: 'number',
}

{
  name: 'focalX',
  type: 'number',
}

{
  name: 'focalY',
  type: 'number',
}
```

### Enhancing Media Collection

```typescript
export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,
  },
  admin: {
    defaultColumns: ['thumbnail', 'alt', 'filesize', 'createdAt'],
    listRelation: (doc) => `${doc.url}?w=50&h=50`, // Thumbnail in lists
  },
  fields: [
    {
      name: 'alt',
      type: 'text',
      required: true,
      label: 'Alt Text',
    },
    
    // Copyright information
    {
      name: 'copyright',
      type: 'text',
      label: 'Copyright / Attribution',
    },
    
    // License type
    {
      name: 'license',
      type: 'select',
      options: [
        { label: 'All Rights Reserved', value: 'all-rights' },
        { label: 'Creative Commons', value: 'cc' },
        { label: 'Public Domain', value: 'public-domain' },
      ],
      defaultValue: 'all-rights',
    },
  ],
  upload: {
    // File configuration
    staticDir: './media', // Store files in ./media directory
    mimeTypes: [
      'image/*', // Images only
      // 'application/pdf', // Or include PDFs
      // 'video/*', // Or include videos
    ],
  },
}
```

### Upload Configuration Options

```typescript
upload: {
  // File storage location (relative to project root)
  staticDir: './media',
  
  // Allowed MIME types
  mimeTypes: ['image/*', 'application/pdf'],
  
  // Image resizing (for images only)
  imageSizes: [
    {
      name: 'thumbnail',
      width: 200,
      height: 200,
      fit: 'cover', // crop, fill, contain, cover
      position: 'center',
    },
    {
      name: 'medium',
      width: 800,
      height: 600,
      fit: 'contain',
    },
    {
      name: 'large',
      width: 1920,
      height: 1080,
      fit: 'cover',
    },
  ],
  
  // Auto-convert images to WebP format
  // (requires sharp library)
  format: 'webp',
}
```

## Creating Custom Collections

### Basic Collection Pattern

```typescript
// src/collections/Posts.ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  
  // Admin panel configuration
  admin: {
    useAsTitle: 'title', // Field to display in lists
    
    // Default columns shown in list view
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
    
    // Pre-fill field values for new documents
    defaults: {
      status: 'draft',
    },
    
    // Group fields into tabs
    groupFieldsByDefault: true,
  },
  
  // Fields definition
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
      unique: true, // Enforce uniqueness in database
    },
    
    {
      name: 'slug',
      type: 'text',
      admin: {
        position: 'sidebar', // Move to sidebar
      },
    },
    
    {
      name: 'content',
      type: 'richText', // Uses Lexical editor
      required: true,
    },
    
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users', // Reference to Users collection
      required: true,
    },
    
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
        { label: 'Archived', value: 'archived' },
      ],
      defaultValue: 'draft',
      required: true,
    },
  ],
  
  // Timestamps (auto-added if omitted)
  timestamps: true,
}
```

### Registering Custom Collections

**payload.config.ts:**

```typescript
import { Users } from './collections/Users'
import { Media } from './collections/Media'
import { Posts } from './collections/Posts' // Import new collection

export default buildConfig({
  collections: [Users, Media, Posts], // Add to array
  // ...
})
```

**Generate types:**
```bash
pnpm generate:types
```

### Collection with Access Control

```typescript
import type { CollectionConfig } from 'payload'
import { adminOnly } from '@/access/adminOnly'
import { authenticatedOrPublished } from '@/access/authenticatedOrPublished'

export const Posts: CollectionConfig = {
  slug: 'posts',
  
  // Who can read/create/update/delete
  access: {
    // Public can read published posts, authenticated users see all
    read: authenticatedOrPublished,
    
    // Only authenticated users can create
    create: ({ req: { user } }) => Boolean(user),
    
    // Only admins or document owner can update
    update: ({ req: { user }, doc }) => {
      if (!user) return false
      if (user.roles?.includes('admin')) return true
      return user.id === doc.author
    },
    
    // Only admins can delete
    delete: adminOnly,
  },
  
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
    { 
      name: 'author', 
      type: 'relationship', 
      relationTo: 'users',
      // Auto-set to current user on create
      hooks: {
        beforeChange: [
          ({ value, operation, req }) => {
            if (operation === 'create' && !value) {
              return req.user?.id
            }
            return value
          },
        ],
      },
    },
  ],
}
```

See [Security Patterns](04-security-patterns.md) for detailed access control patterns.

### Collection with Drafts and Versions

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  
  // Enable drafts and versioning
  versions: {
    drafts: {
      autosave: true, // Auto-save draft every 10 seconds
      schedulePublish: true, // Allow scheduled publishing
      validate: false, // Don't validate required fields in drafts
    },
    maxPerDoc: 100, // Keep last 100 versions
  },
  
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
    
    // Status field (auto-injected when drafts enabled)
    // _status: 'draft' | 'published'
  ],
  
  access: {
    read: ({ req: { user } }) => {
      if (user) return true // Authenticated sees drafts
      return { _status: { equals: 'published' } } // Public sees published only
    },
  },
}
```

**Using Drafts:**

```typescript
// Create draft (skips required field validation)
await payload.create({
  collection: 'posts',
  data: { title: 'Draft Post' },
  draft: true,
})

// Read with drafts enabled
const post = await payload.findByID({
  collection: 'posts',
  id: '123',
  draft: true, // Returns draft version if available
})

// Publish a draft
await payload.update({
  collection: 'posts',
  id: '123',
  data: { _status: 'published' },
})
```

### Collection with Hooks

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  
  hooks: {
    // Before validation - format/sanitize data
    beforeValidate: [
      async ({ data, operation }) => {
        if (operation === 'create' && data.title) {
          data.slug = data.title.toLowerCase().replace(/\s+/g, '-')
        }
        return data
      },
    ],
    
    // Before save - business logic
    beforeChange: [
      async ({ data, operation }) => {
        if (operation === 'update' && data.status === 'published') {
          data.publishedAt = new Date()
        }
        return data
      },
    ],
    
    // After save - side effects (notifications, etc.)
    afterChange: [
      async ({ doc, req, operation }) => {
        if (operation === 'create') {
          // Send notification, update analytics, etc.
          console.log(`New post created: ${doc.title}`)
        }
        return doc
      },
    ],
    
    // After read - computed fields, enrichment
    afterRead: [
      async ({ doc }) => {
        // Add computed field
        const wordCount = doc.content?.split(' ').length || 0
        ;(doc as any).readTime = Math.ceil(wordCount / 200)
        return doc
      },
    ],
  },
  
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text' },
    { name: 'content', type: 'richText' },
    { name: 'status', type: 'select', options: ['draft', 'published'] },
    { name: 'publishedAt', type: 'date' },
  ],
}
```

See [Security Patterns](04-security-patterns.md) for hook best practices and transaction safety.

## Common Field Types

### Basic Fields

```typescript
// Text field
{
  name: 'title',
  type: 'text',
  required: true,
  maxLength: 100,
}

// Number field
{
  name: 'price',
  type: 'number',
  min: 0,
  max: 999999,
  admin: {
    step: 0.01, // Decimal precision
  },
}

// Email field
{
  name: 'email',
  type: 'email',
  required: true,
  unique: true,
}

// Date field
{
  name: 'publishedAt',
  type: 'date',
  admin: {
    date: {
      pickerAppearance: 'dayAndTime', // dayAndTime, timeOnly, dayOnly
    },
  },
}

// Checkbox field
{
  name: 'featured',
  type: 'checkbox',
  defaultValue: false,
}

// Select (dropdown) field
{
  name: 'status',
  type: 'select',
  options: [
    { label: 'Draft', value: 'draft' },
    { label: 'Published', value: 'published' },
  ],
  defaultValue: 'draft',
}

// Radio field
{
  name: 'size',
  type: 'radio',
  options: [
    { label: 'Small', value: 'S' },
    { label: 'Medium', value: 'M' },
    { label: 'Large', value: 'L' },
  ],
}
```

### Rich Text Field (Lexical Editor)

```typescript
{
  name: 'content',
  type: 'richText',
  
  // Lexical editor configuration
  lexical: {
    // Enable/disable features
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      // addLinkFeature(),
      // addHeadingFeature(),
      // addListFeature(),
    ],
    
    // Upload node for image insertion
    nodes: ({ defaultNodes }) => [
      ...defaultNodes,
      UploadNode.build({
        uploadCollection: 'media',
      }),
    ],
  },
}
```

### Relationship Field

```typescript
// Single relationship
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users', // Collection slug
  required: true,
  
  // Filter available options
  filterOptions: {
    active: { equals: true },
  },
}

// Multiple relationships (many-to-many)
{
  name: 'categories',
  type: 'relationship',
  relationTo: 'categories',
  hasMany: true,
}

// Relationship to multiple collections
{
  name: 'relatedContent',
  type: 'relationship',
  relationTo: ['posts', 'pages'], // Polymorphic relationship
  hasMany: true,
}
```

### Upload Field

```typescript
{
  name: 'coverImage',
  type: 'upload',
  relationTo: 'media', // Must reference upload-enabled collection
  
  // Admin options
  admin: {
    position: 'sidebar',
  },
}
```

### Group and Tab Fields

```typescript
// Group (nested fields)
{
  name: 'address',
  type: 'group',
  fields: [
    { name: 'street', type: 'text' },
    { name: 'city', type: 'text' },
    { name: 'zipCode', type: 'text' },
    { name: 'country', type: 'text' },
  ],
}

// Tabs (field organization in admin)
{
  name: 'details',
  type: 'tabs',
  tabs: [
    {
      label: 'Content',
      fields: [
        { name: 'title', type: 'text' },
        { name: 'content', type: 'richText' },
      ],
    },
    {
      label: 'SEO',
      fields: [
        { name: 'metaTitle', type: 'text' },
        { name: 'metaDescription', type: 'textarea' },
      ],
    },
  ],
}
```

### Array and Block Fields

```typescript
// Array (repeating group)
{
  name: 'teamMembers',
  type: 'array',
  fields: [
    { name: 'name', type: 'text' },
    { name: 'role', type: 'text' },
    { name: 'photo', type: 'upload', relationTo: 'media' },
  ],
  minRows: 1,
  maxRows: 10,
}

// Blocks (content builder)
{
  name: 'layout',
  type: 'blocks',
  blocks: [
    {
      slug: 'hero',
      label: 'Hero Section',
      fields: [
        { name: 'title', type: 'text' },
        { name: 'subtitle', type: 'text' },
        { name: 'backgroundImage', type: 'upload', relationTo: 'media' },
      ],
    },
    {
      slug: 'content',
      label: 'Content Section',
      fields: [
        { name: 'content', type: 'richText' },
        { name: 'align', type: 'select', options: ['left', 'center', 'right'] },
      ],
    },
    {
      slug: 'gallery',
      label: 'Image Gallery',
      fields: [
        {
          name: 'images',
          type: 'array',
          fields: [{ name: 'image', type: 'upload', relationTo: 'media' }],
        },
      ],
    },
  ],
}
```

See [Field Types Reference](https://payloadcms.com/docs/fields/overview) for complete field type documentation.

## Collection Best Practices

### Naming Conventions

- **Slugs**: Lowercase, plural nouns (e.g., `posts`, `users`, `categories`)
- **File names**: PascalCase matching collection concept (e.g., `Posts.ts`, `Users.ts`)
- **Field names**: camelCase (e.g., `coverImage`, `publishedAt`)
- **Labels**: Title Case for UI display (e.g., "Cover Image")

### Organization

1. **One file per collection** - Keep configs isolated and testable
2. **Extract complex logic** - Move hooks, access control to separate files
3. **Use constants** - Define options, slugs as constants for reuse
4. **Document fields** - Add comments explaining field purpose

### Performance

1. **Index frequently queried fields**:
   ```typescript
   {
     name: 'slug',
     type: 'text',
     index: true, // Database index for faster queries
   }
   ```

2. **Use defaultColumns** - Optimize list view performance
3. **Limit depth** - Set `maxDepth` on relationships to prevent over-fetching
4. **Select fields** - Use `select` option in queries to limit returned fields

See [Local API Usage](06-local-api-usage.md) for query optimization patterns.
