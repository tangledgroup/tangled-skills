# Collections & Fields Reference

Complete guide to data modeling in Payload CMS v3.82.1 covering collections, all field types, and common patterns.

## Collections Overview

Collections are the primary way to define data models in Payload. Each collection represents a database collection/table with:
- **Slug**: URL-friendly identifier (lowercase, hyphens)
- **Fields**: Schema definition for documents
- **Access Control**: Read/write permissions
- **Hooks**: Lifecycle event handlers
- **Admin Config**: UI customization

### Basic Collection Structure

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  // Unique identifier for this collection
  slug: 'posts',
  
  // Fields define the document schema
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
  ],
  
  // Auto-add createdAt and updatedAt timestamps
  timestamps: true,
  
  // Admin panel configuration
  admin: {
    useAsTitle: 'title', // Use title field for document labels
    defaultColumns: ['title', 'author', 'status', 'createdAt'],
    description: 'Blog posts and articles',
  },
  
  // Access control (who can read/write)
  access: {
    read: () => true, // Public read access
    create: ({ req: { user } }) => Boolean(user), // Auth required
  },
  
  // Versioning and drafts
  versions: {
    drafts: {
      autosave: true,
      schedulePublish: true,
    },
    maxPerDoc: 100,
  },
}
```

### Collection Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `slug` | string | URL identifier (required) |
| `fields` | Field[] | Schema definition (required) |
| `labels` | object | Singular/plural labels for UI |
| `access` | Access | Read/write permissions |
| `auth` | boolean \| AuthOptions | Enable authentication |
| `hooks` | Hooks | Lifecycle event handlers |
| `timestamps` | boolean \| TimestampsConfig | Auto-add createdAt/updatedAt |
| `versions` | VersionsConfig | Enable versioning/drafts |
| `admin` | AdminConfig | UI customization |
| `graphql` | GraphQLConfig | GraphQL API configuration |
| `indexes` | Index[] | Database indexes for performance |

## Field Types

Payload provides 25+ field types categorized into:
- **Data Fields**: Store values in database (require `name`)
- **Presentational Fields**: Organize UI only (no data storage)
- **Virtual Fields**: Computed values not stored in database

### Text Field

Simple text input for strings.

```typescript
{
  name: 'title',
  type: 'text',
  required: true,
  maxLength: 200,
  admin: {
    placeholder: 'Enter post title',
    description: 'The main title of the post',
  },
}
```

**Options**: `required`, `maxLength`, `minLength`, `defaultValue`, `unique`, `index`

### Textarea Field

Multi-line text input.

```typescript
{
  name: 'description',
  type: 'textarea',
  rows: 4,
  maxLength: 1000,
  admin: {
    placeholder: 'Enter a brief description',
  },
}
```

**Options**: `rows`, `required`, `maxLength`, `minLength`, `defaultValue`

### Number Field

Numeric values with validation.

```typescript
{
  name: 'price',
  type: 'number',
  min: 0,
  max: 999999,
  admin: {
    step: 0.01, // Allow cents
    placeholder: '0.00',
  },
}
```

**Options**: `min`, `max`, `step`, `required`, `defaultValue`

### Email Field

Validated email address input.

```typescript
{
  name: 'email',
  type: 'email',
  required: true,
  unique: true, // Enforce uniqueness in database
}
```

### Date Field

Date/time picker with timestamp storage.

```typescript
{
  name: 'publishedAt',
  type: 'date',
  admin: {
    date: {
      displayFormat: 'MMMM D, YYYY', // "January 1, 2024"
    },
    time: {
      displayFormat: 'h:mm A', // "2:30 PM"
    },
  },
}
```

**Options**: `date`, `time`, `required`, `defaultValue`

### Checkbox Field

Boolean true/false value.

```typescript
{
  name: 'featured',
  type: 'checkbox',
  defaultValue: false,
  admin: {
    description: 'Mark as featured post',
  },
}
```

**Options**: `defaultValue`, `required` (use sparingly)

### Select Field

Dropdown/picklist with predefined options.

```typescript
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
}
```

**WithOptions array**:
```typescript
{
  name: 'priority',
  type: 'select',
  options: ['low', 'medium', 'high'], // Auto-generate labels
  hasMany: true, // Allow multiple selections
}
```

**Options**: `options`, `hasMany`, `required`, `defaultValue`

### Radio Field

Radio button group (single selection).

```typescript
{
  name: 'layout',
  type: 'radio',
  options: ['default', 'wide', 'full'],
  defaultValue: 'default',
  admin: {
    layout: 'horizontal', // 'horizontal' | 'vertical'
  },
}
```

### Rich Text Field

Lexical-based rich text editor with blocks, inline fields, and custom nodes.

```typescript
{
  name: 'content',
  type: 'richText',
  required: true,
  admin: {
    elements: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'bold', 'italic', 'link', 'bulletList', 'numberedList',
      'quote', 'codeBlock',
    ],
  },
}
```

**With Custom Blocks**:
```typescript
{
  name: 'content',
  type: 'richText',
  lexical: {
    features: () => [
      lexicalFeatureHeadings(),
      lexicalFeatureLists(),
      lexicalFeatureLink({
        fields: ({ defaultFields }) => [
          ...defaultFields,
          {
            name: 'linkType',
            type: 'select',
            options: ['internal', 'external'],
          },
        ],
      }),
    ],
  },
}
```

### Relationship Field

Link to documents in other collections.

```typescript
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users', // Single collection
  required: true,
  admin: {
    description: 'Select the post author',
  },
}
```

**Multiple Collections**:
```typescript
{
  name: 'relatedPosts',
  type: 'relationship',
  relationTo: ['posts', 'pages'], // Multiple collections
  hasMany: true, // Allow multiple selections
  filterOptions: ({ user }) => {
    // Filter to only show published content for non-admins
    if (user?.roles?.includes('admin')) return {}
    return { _status: { equals: 'published' } }
  },
}
```

**Options**: `relationTo`, `hasMany`, `required`, `filterOptions`, `maxDepth`

### Upload Field

File/image upload with storage adapter integration.

```typescript
{
  name: 'coverImage',
  type: 'upload',
  relationTo: 'media', // Collection with upload configuration
  required: false,
  admin: {
    description: 'Upload a cover image for this post',
  },
}
```

**Media Collection Setup**:
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
    {
      name: 'caption',
      type: 'textarea',
    },
  ],
  upload: {
    staticDir: './media', // Local storage path
    mimeTypes: ['image/*'], // Restrict to images
  },
}
```

### Array Field

Repeating group of nested fields.

```typescript
{
  name: 'teamMembers',
  type: 'array',
  minRows: 1,
  maxRows: 10,
  labels: {
    singular: 'Team Member',
    plural: 'Team Members',
  },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'role', type: 'text' },
    { name: 'photo', type: 'upload', relationTo: 'media' },
  ],
}
```

**Stored Data Structure**:
```json
{
  "teamMembers": [
    { "name": "John Doe", "role": "CEO", "photo": "64f12345..." },
    { "name": "Jane Smith", "role": "CTO", "photo": "64f67890..." }
  ]
}
```

### Blocks Field

Content blocks for flexible page building.

```typescript
{
  name: 'layout',
  type: 'blocks',
  blocks: [
    {
      slug: 'headline',
      labels: {
        singular: 'Headline',
        plural: 'Headlines',
      },
      fields: [
        { name: 'content', type: 'text', required: true },
        { name: 'size', type: 'select', options: ['small', 'medium', 'large'] },
      ],
    },
    {
      slug: 'richText',
      labels: {
        singular: 'Rich Text',
        plural: 'Rich Text Blocks',
      },
      fields: [
        { name: 'content', type: 'richText', required: true },
      ],
    },
    {
      slug: 'media',
      labels: {
        singular: 'Media',
        plural: 'Media',
      },
      fields: [
        { name: 'media', type: 'upload', relationTo: 'media', required: true },
        { name: 'alignment', type: 'select', options: ['left', 'center', 'right'] },
      ],
    },
  ],
}
```

**Stored Data Structure**:
```json
{
  "layout": [
    {
      "blockType": "headline",
      "content": "Welcome to Our Site",
      "size": "large"
    },
    {
      "blockType": "media",
      "media": "64f12345...",
      "alignment": "center"
    }
  ]
}
```

### Group Field

Nest fields within a keyed object.

```typescript
{
  name: 'author',
  type: 'group',
  fields: [
    { name: 'firstName', type: 'text', required: true },
    { name: 'lastName', type: 'text', required: true },
    { name: 'email', type: 'email' },
  ],
}
```

**Stored Data Structure**:
```json
{
  "author": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  }
}
```

### Tabs Field

Organize fields into tabbed interface.

**Named Tabs** (create nested objects):
```typescript
{
  type: 'tabs',
  tabs: [
    {
      name: 'content',
      label: 'Content',
      fields: [
        { name: 'title', type: 'text' },
        { name: 'body', type: 'richText' },
      ],
    },
    {
      name: 'seo',
      label: 'SEO',
      fields: [
        { name: 'metaTitle', type: 'text' },
        { name: 'metaDescription', type: 'textarea' },
      ],
    },
  ],
}
```

**Unnamed Tabs** (presentational only):
```typescript
{
  type: 'tabs',
  tabs: [
    {
      label: 'General',
      fields: [
        { name: 'title', type: 'text' },
      ],
    },
    {
      label: 'Settings',
      fields: [
        { name: 'status', type: 'select' },
      ],
    },
  ],
}
```

### JSON Field

JSON editor with syntax highlighting.

```typescript
{
  name: 'metadata',
  type: 'json',
  admin: {
    description: 'Custom metadata in JSON format',
  },
}
```

**Stored Data Structure**:
```json
{
  "metadata": {
    "keywords": ["tech", "programming"],
    "readingTime": 5
  }
}
```

### Code Field

Code editor with syntax highlighting.

```typescript
{
  name: 'snippet',
  type: 'code',
  admin: {
    language: 'javascript', // 'javascript', 'typescript', 'css', 'html', etc.
    lines: 10,
  },
}
```

### Row Field

Layout fields horizontally in admin panel.

```typescript
{
  type: 'row',
  fields: [
    { name: 'firstName', type: 'text' },
    { name: 'lastName', type: 'text' },
  ],
}
```

### Collapsible Field

Group fields in collapsible section.

```typescript
{
  type: 'collapsible',
  label: 'Advanced Settings',
  defaultCollapsed: true,
  fields: [
    { name: 'cacheDuration', type: 'number' },
    { name: 'enableAnalytics', type: 'checkbox' },
  ],
}
```

### UI Field

Custom React component without data storage.

```typescript
{
  name: 'refundButton',
  type: 'ui',
  admin: {
    components: {
      Field: '/components/RefundButton',
    },
  },
}
```

### Point Field

Geographic coordinates (lat/long).

```typescript
{
  name: 'location',
  type: 'point',
  admin: {
    mapboxApiKey: process.env.MAPBOX_API_KEY,
  },
}
```

**Stored Data Structure**:
```json
{
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194
  }
}
```

## Field Configuration Options

All fields support these common options:

### Validation

```typescript
{
  name: 'age',
  type: 'number',
  validate: (value, { siblingData }) => {
    if (value < 0) return 'Age cannot be negative'
    if (value > 150) return 'Age seems unrealistic'
    return true
  },
}
```

### Conditional Logic

Show/hide fields based on other field values:

```typescript
{
  name: 'featuredImage',
  type: 'upload',
  relationTo: 'media',
  admin: {
    condition: (data) => data.featured === true,
  },
}
```

### Access Control

Field-level read permissions:

```typescript
{
  name: 'salary',
  type: 'number',
  access: {
    read: ({ req: { user }, doc }) => {
      // Users can read own salary
      if (user?.id === doc?.id) return true
      // Admins can read all
      return user?.roles?.includes('admin')
    },
  },
}
```

### Hooks

Field-level lifecycle hooks:

```typescript
{
  name: 'slug',
  type: 'text',
  hooks: {
    beforeValidate: [
      ({ value, siblingData }) => {
        // Auto-generate slug from title if empty
        if (!value && siblingData.title) {
          return slugify(siblingData.title)
        }
        return value
      },
    ],
  },
}
```

### Admin Customization

```typescript
{
  name: 'title',
  type: 'text',
  admin: {
    placeholder: 'Enter title here',
    description: 'The main title of the document',
    width: '50%', // '50%' | '33%' | '100%'
    style: { color: 'red' }, // Inline styles
    className: 'custom-field', // CSS class
    hidden: false, // Hide from admin
    readOnly: false, // Make read-only
  },
}
```

## Virtual Fields

Computed fields not stored in database.

### Boolean Virtual Fields

```typescript
{
  name: 'fullName',
  type: 'text',
  virtual: true,
  hooks: {
    afterRead: [
      ({ siblingData }) => {
        return `${siblingData.firstName} ${siblingData.lastName}`
      },
    ],
  },
}
```

### Virtual Path Fields

Auto-resolve from relationships:

```typescript
// Original relationship field
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users',
},
// Virtual field to display author's name
{
  name: 'authorName',
  type: 'text',
  virtual: 'author.name', // Resolves to author relationship's name field
}
```

**Virtual Path Examples**:
- `author.name` - Gets name from author relationship
- `categories.title` - Returns array of titles for hasMany relationship
- `request.stakeholders.email` - Traverses multiple relationship levels

## Globals

Singleton documents for site-wide configuration.

```typescript
import type { GlobalConfig } from 'payload'

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

export const Footer: GlobalConfig = {
  slug: 'footer',
  fields: [
    { name: 'copyright', type: 'text' },
    { name: 'socialLinks', type: 'array' },
  ],
}
```

**Usage in Config**:
```typescript
export default buildConfig({
  globals: [Header, Footer],
  // ...
})
```

## Common Field Patterns

### Auto-generate Slugs

```typescript
import { slugField } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'title', type: 'text', required: true },
    slugField({ fieldToUse: 'title' }), // Auto-generates slug from title
  ],
}
```

### Conditional Fields

```typescript
{
  name: 'paymentMethod',
  type: 'select',
  options: ['credit_card', 'paypal', 'bank_transfer'],
},
{
  name: 'creditCardNumber',
  type: 'text',
  admin: {
    condition: (data) => data.paymentMethod === 'credit_card',
  },
},
{
  name: 'paypalEmail',
  type: 'email',
  admin: {
    condition: (data) => data.paymentMethod === 'paypal',
  },
},
```

### Computed Fields with Hooks

```typescript
{
  name: 'wordCount',
  type: 'number',
  virtual: true,
  hooks: {
    afterRead: [
      ({ siblingData }) => {
        const content = siblingData.content || ''
        return content.split(/\s+/).length
      },
    ],
  },
}
```

### Nested Relationships

```typescript
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users',
  maxDepth: 2, // Populate up to 2 levels deep
},
// Virtual field for author's company name
{
  name: 'companyName',
  type: 'text',
  virtual: 'author.company.name',
}
```
