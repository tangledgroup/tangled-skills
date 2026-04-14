# Collections and Fields

This reference documents all available field types, collection configuration options, and schema patterns for Payload CMS 3.82.1. Use this guide to define data models with proper validation, relationships, and access control.

## Collection Configuration

### Basic Structure

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',           // Required: lowercase, URL-friendly identifier
  label: 'Posts',          // Optional: display name in admin (plural)
  labels: {                // Optional: custom labels for singular/plural
    singular: 'Post',
    plural: 'Posts',
  },
  admin: {                 // Optional: admin panel configuration
    useAsTitle: 'title',   // Field to use as document title
    defaultColumns: ['title', 'updatedAt'],
    hidden: false,         // Hide from admin panel
    description: 'Blog posts and articles',
  },
  auth: false,             // Optional: enable authentication
  fields: [],              // Required: field definitions
  access: {},              // Optional: access control policies
  hooks: {},               // Optional: lifecycle hooks
  versions: {},            // Optional: versioning/revision control
  cache: {},               // Optional: caching configuration
}
```

### Collection Options

**`slug`** (required)
- Lowercase, URL-friendly identifier
- Used in API endpoints: `/api/posts`
- Must be unique across all collections

**`admin`** configuration:
```typescript
admin: {
  useAsTitle: 'title',           // Field for document titles
  defaultColumns: ['title', 'author', 'updatedAt'],
  listRelations: {               // Fields shown in list view
    title: ['id', 'title'],
  },
  defaultSort: 'createdAt',      // Default sort field
  defaultLimit: 10,              // Default items per page
  isSortable: true,              // Enable drag-and-drop sorting
  description: 'Help text for this collection',
  hidden: false,                 // Hide from admin navigation
  position: 'sidebar',           // 'sidebar' | 'menu'
  group: 'Content',              // Group collections in sidebar
}
```

**`access`** control:
```typescript
access: {
  read: ({ req }) => {
    // Return true/false or Promise<boolean>
    return req.user.role === 'admin'
  },
  create: ({ req }) => req.user.role === 'editor',
  update: ({ req, data }) => {
    // Check if user owns this document
    return req.user.id === data.id
  },
  delete: ({ req }) => req.user.role === 'admin',
}
```

**`hooks`** lifecycle:
```typescript
hooks: {
  beforeValidate: [
    async ({ data, req }) => {
      // Modify data before validation
      return { ...data, slug: data.slug.toLowerCase() }
    },
  ],
  beforeChange: [
    async ({ data, req }) => {
      // Transform data before saving
      return { ...data, normalizedField: data.field.toUpperCase() }
    },
  ],
  afterChange: [
    async ({ doc, req }) => {
      // Side effects after save (webhooks, notifications)
      await sendNotification({ postId: doc.id })
    },
  ],
  afterRead: [
    async ({ doc, req }) => {
      // Modify document before returning
      // Useful for filtering sensitive data
      delete doc.password
      return doc
    },
  ],
}
```

## Field Types

### Text Fields

**`text`** - Single-line text input
```typescript
{
  name: 'title',
  type: 'text',
  required: true,
  unique: true,              // Enforce uniqueness in database
  minLength: 3,
  maxLength: 100,
  placeholder: 'Enter title',
  admin: {
    width: '50%',            // '50%' | '33%' | '25%'
    description: 'Article title',
  },
}
```

**`email`** - Email address with validation
```typescript
{
  name: 'email',
  type: 'email',
  required: true,
  unique: true,
}
```

### Rich Text Fields

**`richText`** - Lexical block editor
```typescript
{
  name: 'content',
  type: 'richText',
  required: true,
  admin: {
    elements: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'link'],
    leafNodes: ['bold', 'italic', 'underline', 'strikethrough'],
  },
}
```

With custom blocks:
```typescript
{
  name: 'content',
  type: 'richText',
  lexical: {
    features: () => [
      headings(),
      lists(),
      link({ enableAutoLink: true }),
      horizontalRule(),
      indent(),
      inlineCode(),
      paragraph(),
      // Custom blocks
      customBlock({ slug: 'callout' }),
    ],
  },
}
```

### Number Fields

**`number`** - Numeric input with validation
```typescript
{
  name: 'age',
  type: 'number',
  min: 0,
  max: 150,
  step: 1,                   // Increment step
  admin: {
    placeholder: 'Enter age',
    step: 1,
  },
}
```

### Select Fields

**`select`** - Dropdown with predefined options
```typescript
{
  name: 'status',
  type: 'select',
  options: [
    { label: 'Draft', value: 'draft' },
    { label: 'Published', value: 'published' },
    { label: 'Archived', value: 'archived' },
  ],
  hasMany: false,            // Set true for multiple selections
  required: true,
  admin: {
    isClearable: true,       // Show clear button
  },
}
```

Dynamic options from function:
```typescript
{
  name: 'category',
  type: 'select',
  options: async ({ req }) => {
    const categories = await req.payload.find({
      collection: 'categories',
      depth: 0,
    })
    return categories.docs.map(cat => ({
      label: cat.name,
      value: cat.id,
    }))
  },
}
```

### Checkbox Fields

**`checkbox`** - Boolean toggle
```typescript
{
  name: 'published',
  type: 'checkbox',
  defaultValue: false,
  admin: {
    description: 'Mark as published',
  },
}
```

### Date/Time Fields

**`date`** - DateTime picker
```typescript
{
  name: 'publishedAt',
  type: 'date',
  admin: {
    date: {
      pickerStyle: 'modern',  // 'classic' | 'modern'
    },
    time: {
      pickerStyle: 'modern',
      format: '12hr',         // '12hr' | '24hr'
    },
  },
}
```

### Relationship Fields

**`relationship`** - Reference to another document
```typescript
{
  name: 'author',
  type: 'relationship',
  relationTo: 'users',       // Collection slug
  required: true,
  hasMany: false,            // Multiple authors if true
  filterOptions: ({ req }) => ({
    id: { equals: req.user.id },
  }),
  admin: {
    placeholder: 'Select author',
  },
}
```

Multiple relation types:
```typescript
{
  name: 'relatedMedia',
  type: 'relationship',
  relationTo: ['posts', 'pages', 'media'],
  hasMany: true,
}
```

### Group Fields

**`group`** - Organize fields into collapsible sections
```typescript
{
  name: 'seo',
  type: 'group',
  fields: [
    {
      name: 'metaTitle',
      type: 'text',
      maxLength: 60,
    },
    {
      name: 'metaDescription',
      type: 'textarea',
      maxLength: 160,
    },
    {
      name: 'keywords',
      type: 'text',
      hasMany: true,
    },
  ],
  admin: {
    description: 'Search engine optimization settings',
  },
}
```

### Tabs

**`tabs`** - Organize fields into tabbed interface
```typescript
{
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
    {
      label: 'Advanced',
      fields: [
        { name: 'canonicalURL', type: 'text' },
      ],
    },
  ],
}
```

### Array Fields

**`array`** - Repeating field groups
```typescript
{
  name: 'teamMembers',
  type: 'array',
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
    },
    {
      name: 'role',
      type: 'select',
      options: ['Developer', 'Designer', 'Manager'],
    },
    {
      name: 'photo',
      type: 'relationship',
      relationTo: 'media',
    },
  ],
  admin: {
    initCollapsed: true,      // Collapse by default
    description: 'List team members',
  },
}
```

### Blocks

**`blocks`** - Content blocks with different types
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
        {
          name: 'content',
          type: 'text',
          required: true,
        },
        {
          name: 'size',
          type: 'select',
          options: ['small', 'medium', 'large'],
        },
      ],
    },
    {
      slug: 'richText',
      labels: {
        singular: 'Rich Text',
        plural: 'Rich Text Blocks',
      },
      fields: [
        {
          name: 'content',
          type: 'richText',
        },
      ],
    },
    {
      slug: 'media',
      labels: {
        singular: 'Media',
        plural: 'Media Blocks',
      },
      fields: [
        {
          name: 'image',
          type: 'relationship',
          relationTo: 'media',
          required: true,
        },
        {
          name: 'alt',
          type: 'text',
        },
      ],
    },
  ],
}
```

### Upload Fields

**`upload`** - File upload at field level (use `upload: true` on collection for full upload)
```typescript
{
  name: 'thumbnail',
  type: 'upload',
  relationTo: 'media',
  required: true,
}
```

### JSON Fields

**`json`** - Code editor for JSON data
```typescript
{
  name: 'metadata',
  type: 'json',
  admin: {
    description: 'Custom metadata in JSON format',
  },
}
```

### Row Fields

**`row`** - Horizontal field layout
```typescript
{
  type: 'row',
  fields: [
    {
      name: 'firstName',
      type: 'text',
      admin: { width: '50%' },
    },
    {
      name: 'lastName',
      type: 'text',
      admin: { width: '50%' },
    },
  ],
}
```

### Collapsible Fields

**`collapsible`** - Collapsible field groups
```typescript
{
  type: 'collapsible',
  label: 'Advanced Settings',
  fields: [
    { name: 'customField1', type: 'text' },
    { name: 'customField2', type: 'number' },
  ],
}
```

### Code Fields

**`code`** - Syntax-highlighted code editor
```typescript
{
  name: 'script',
  type: 'code',
  admin: {
    language: 'javascript',  // 'javascript' | 'typescript' | 'css' | 'html' | etc.
  },
}
```

### Radio Fields

**`radio`** - Radio button group
```typescript
{
  name: 'priority',
  type: 'radio',
  options: [
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' },
  ],
  admin: {
    layout: 'horizontal',     // 'horizontal' | 'vertical'
  },
}
```

## Validation

### Field-Level Validation

```typescript
{
  name: 'username',
  type: 'text',
  validate: (value, { data }) => {
    if (!value) {
      return 'Username is required'
    }
    if (value.length < 3) {
      return 'Username must be at least 3 characters'
    }
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      return 'Username can only contain letters, numbers, and underscores'
    }
    return true
  },
}
```

### Custom Validation Functions

```typescript
const uniqueSlug = async (value: string, options: any) => {
  const { doc, req, siblingData } = options
  
  if (!value) return 'Slug is required'
  
  // Check if slug already exists
  const existing = await req.payload.find({
    collection: req.collection.slug,
    where: {
      slug: { equals: value },
    },
    limit: 1,
  })
  
  if (existing.docs.length > 0) {
    return 'This slug is already in use'
  }
  
  return true
}

{
  name: 'slug',
  type: 'text',
  validate: uniqueSlug,
}
```

## Upload Configuration

### Media Collection with Upload

```typescript
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,         // Public access
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
      type: 'text',
      label: 'Caption',
    },
  ],
  upload: {
    staticDir: './uploads',   // Local directory for uploads
    mimeTypes: [
      'image/*',
      'application/pdf',
      'application/msword',
    ],
    imageSizes: [
      {
        name: 'thumbnail',
        width: 200,
        height: 200,
        position: 'center',
      },
      {
        name: 'small',
        width: 400,
        height: 400,
        position: 'center',
      },
      {
        name: 'medium',
        width: 800,
        height: 600,
        position: 'top left',
      },
      {
        name: 'large',
        width: 1200,
        height: 800,
        position: 'center',
      },
    ],
  },
}
```

### Cloud Storage (S3 Example)

```typescript
import { s3Adapter } from '@payloadcms/db-postgres' // or appropriate adapter

upload: {
  flatten: false,
  crop: true,
  focalPoint: true,
  mimeTypes: ['image/*'],
}
```

## Best Practices

### Field Organization

1. **Use groups** to organize related fields
2. **Use tabs** for complex forms with many sections
3. **Use collapsible** for advanced/optional settings
4. **Use rows** for short fields that fit side-by-side
5. **Order fields** logically: required first, optional last

### Performance Considerations

1. **Limit depth** on relationship queries to prevent N+1
2. **Use indexing** on frequently queried fields
3. **Avoid deep nesting** - keep schema flat when possible
4. **Use hasMany sparingly** - prefer separate collections for large lists

### Type Safety

Always use TypeScript types:
```typescript
import type { CollectionConfig, Field } from 'payload'

const myFields: Field[] = [
  { name: 'title', type: 'text' },
]
```

## Common Patterns

### Blog Post Collection

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'publishedAt'],
  },
  versions: {
    drafts: true,
    maxPerDoc: 10,
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
      ],
      defaultValue: 'draft',
    },
    {
      name: 'cover',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
    },
    {
      name: 'publishedAt',
      type: 'date',
    },
    {
      name: 'content',
      type: 'richText',
      required: true,
    },
    {
      type: 'tabs',
      tabs: [
        {
          label: 'SEO',
          fields: [
            { name: 'metaTitle', type: 'text' },
            { name: 'metaDescription', type: 'textarea' },
          ],
        },
      ],
    },
  ],
}
```

See [Authentication Setup](03-authentication-setup.md) for auth-enabled collection patterns.
