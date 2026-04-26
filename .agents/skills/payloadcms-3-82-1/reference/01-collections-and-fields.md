# Collections and Fields

## Collection Configuration

Collections are defined as TypeScript objects implementing `CollectionConfig`. They specify a slug, fields array, access control, admin options, hooks, versions, and optional auth/upload/endpoint configuration.

### Basic Structure

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  labels: { singular: 'Post', plural: 'Posts' },
  access: {
    create: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
    delete: authenticated,
  },
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'updatedAt'],
    preview: (data, { req }) => `/posts/${data.slug}`,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'content', type: 'richText' },
  ],
  versions: {
    drafts: {
      autosave: { interval: 100 },
      schedulePublish: true,
    },
    maxPerDoc: 50,
  },
  hooks: {
    afterChange: [revalidatePage],
    beforeChange: [populatePublishedAt],
    afterDelete: [revalidateDelete],
  },
}
```

### Type-Safe Collections with Generics

Pass the collection slug as a generic to get full type safety:

```typescript
export const Pages: CollectionConfig<'pages'> = {
  slug: 'pages',
  // ...fully typed fields and hooks
}
```

### Default Population

Control what fields are populated by default when referenced from other collections:

```typescript
export const Pages: CollectionConfig<'pages'> = {
  slug: 'pages',
  defaultPopulate: {
    title: true,
    slug: true,
  },
  // ...
}
```

## Field Types

### Scalar Fields

**text** — Single-line text input with optional `maxLength`, `minLength`, `validate`, and `admin.condition`.

```typescript
{ name: 'title', type: 'text', required: true, maxLength: 200 }
```

**number** — Numeric input with `min`, `max`, `step`.

```typescript
{ name: 'price', type: 'number', min: 0 }
```

**email** — Email-validated text field.

```typescript
{ name: 'contactEmail', type: 'email' }
```

**textarea** — Multi-line text with `rows` option.

```typescript
{ name: 'description', type: 'textarea', rows: 4 }
```

**code** — Code editor with syntax highlighting (Monaco).

```typescript
{ name: 'snippet', type: 'code', language: 'typescript' }
```

**date** — Date picker with `pickerAppearance` options (`date-only`, `dayAndTime`).

```typescript
{
  name: 'publishedAt',
  type: 'date',
  admin: { date: { pickerAppearance: 'dayAndTime' }, position: 'sidebar' },
}
```

**checkbox** — Boolean toggle.

```typescript
{ name: 'featured', type: 'checkbox' }
```

**radio** — Single selection from options.

```typescript
{
  name: 'status',
  type: 'radio',
  options: [
    { label: 'Draft', value: 'draft' },
    { label: 'Published', value: 'published' },
  ],
}
```

**select** — Single or multi-select dropdown.

```typescript
{
  name: 'tags',
  type: 'select',
  hasMany: true,
  options: ['news', 'tutorial', 'announcement'],
}
```

**json** — JSON editor with optional schema validation.

```typescript
{
  name: 'metadata',
  type: 'json',
  jsonSchema: { type: 'object', properties: { author: { type: 'string' } } },
}
```

**point** — Geolocation field (latitude/longitude pair).

```typescript
{ name: 'location', type: 'point' }
```

### Structural Fields

**group** — Groups related fields under a namespace.

```typescript
{
  name: 'seo',
  type: 'group',
  fields: [
    { name: 'title', type: 'text' },
    { name: 'description', type: 'textarea' },
  ],
}
```

**row** — Lays out child fields horizontally in the admin.

```typescript
{
  type: 'row',
  fields: [
    { name: 'firstName', type: 'text' },
    { name: 'lastName', type: 'text' },
  ],
}
```

**tabs** — Organizes fields into tabbed sections.

```typescript
{
  type: 'tabs',
  tabs: [
    { label: 'Content', fields: [{ name: 'body', type: 'richText' }] },
    { label: 'SEO', name: 'meta', fields: [{ name: 'title', type: 'text' }] },
  ],
}
```

**collapsible** — Collapsible field section.

```typescript
{
  type: 'collapsible',
  label: 'Advanced Settings',
  fields: [{ name: 'cacheTtl', type: 'number' }],
}
```

### Repeating Fields

**array** — Repeatable group of fields, stored as an array.

```typescript
{
  name: 'teamMembers',
  type: 'array',
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'role', type: 'text' },
  ],
}
```

**blocks** — Polymorphic content blocks, the foundation of layout builders.

```typescript
{
  name: 'layout',
  type: 'blocks',
  blocks: [
    {
      slug: 'hero',
      labels: { singular: 'Hero', plural: 'Heroes' },
      fields: [
        { name: 'heading', type: 'text', required: true },
        { name: 'subtitle', type: 'textarea' },
        { name: 'backgroundImage', type: 'upload', relationTo: 'media' },
      ],
    },
    {
      slug: 'content',
      fields: [
        { name: 'richText', type: 'richText' },
        { name: 'columns', type: 'number', min: 1, max: 4 },
      ],
    },
    {
      slug: 'mediaBlock',
      fields: [{ name: 'media', type: 'upload', relationTo: 'media' }],
    },
  ],
}
```

### Relationship Fields

**relationship** — References documents in other collections.

```typescript
{
  name: 'categories',
  type: 'relationship',
  relationTo: 'categories',
  hasMany: true,
  admin: { position: 'sidebar' },
}

// Polymorphic relationship (references multiple collections)
{
  name: 'link',
  type: 'relationship',
  relationTo: ['pages', 'posts'],
}
```

Filter relationship options dynamically:

```typescript
{
  name: 'relatedPosts',
  type: 'relationship',
  relationTo: 'posts',
  hasMany: true,
  filterOptions: ({ id }) => ({ id: { not_in: [id] } }),
}
```

**join** — Reverse relationship that automatically queries back-references.

```typescript
{
  name: 'postsByAuthor',
  type: 'join',
  collection: 'posts',
  onField: 'author',
  // Automatically finds all posts where posts.author === this document
}
```

**upload** — File upload field referencing a media collection.

```typescript
{
  name: 'heroImage',
  type: 'upload',
  relationTo: 'media',
}
```

### Rich Text

Rich text uses the Lexical editor with configurable features:

```typescript
import {
  BlocksFeature,
  FixedToolbarFeature,
  HeadingFeature,
  HorizontalRuleFeature,
  InlineToolbarFeature,
  lexicalEditor,
} from '@payloadcms/richtext-lexical'

{
  name: 'content',
  type: 'richText',
  editor: lexicalEditor({
    features: ({ rootFeatures }) => [
      ...rootFeatures,
      HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
      BlocksFeature({ blocks: [Banner, Code, MediaBlock] }),
      FixedToolbarFeature(),
      InlineToolbarFeature(),
      HorizontalRuleFeature(),
    ],
  }),
}
```

### Hidden Fields

Store data not visible in the admin UI:

```typescript
{ name: 'searchIndex', type: 'text', hidden: true }
```

## Field Options

All data-affecting fields support:

- `required: boolean` — enforce non-null values
- `unique: boolean` — enforce uniqueness at the database level
- `indexed: boolean` — add a database index for faster queries
- `localized: boolean` — enable per-locale storage
- `defaultValue` — static value or function returning default
- `validate` — custom validation function
- `hooks` — field-level lifecycle hooks
- `access` — field-level read/write permissions
- `admin` — admin UI options (position, disabled, readOnly, condition, width, description)

### Conditional Visibility

Show/hide fields based on other field values:

```typescript
{
  name: 'endDate',
  type: 'date',
  admin: {
    condition: (data) => data.allDay === false,
  },
}
```

### Field Validation

```typescript
{
  name: 'slug',
  type: 'text',
  validate: (value: string, { siblingData }) => {
    if (!value) return 'Slug is required'
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(value))
      return 'Slug must be lowercase alphanumeric with hyphens'
    return true
  },
}
```

## Globals Configuration

Globals are singleton documents — useful for site-wide settings:

```typescript
import type { GlobalConfig } from 'payload'

export const Header: GlobalConfig = {
  slug: 'header',
  access: {
    read: () => true,  // public
  },
  fields: [
    { name: 'navItems', type: 'array', fields: [
      { name: 'label', type: 'text', required: true },
      { name: 'url', type: 'text', required: true },
    ]},
  ],
}
```

Use globals in the Payload config:

```typescript
export default buildConfig({
  // ...
  globals: [Header, Footer],
})
```

## Upload Collections

Enable `upload: true` on a collection to handle file uploads:

```typescript
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: { read: () => true },
  upload: {
    staticDir: path.resolve(dirname, '../uploads'),
    mimeTypes: ['image/*', 'application/pdf'],
    adminThumbnail: 'details.thumbnail',
    formatOptions: {
      type: 'jpg',
      quality: 80,
    },
    imageSizes: [
      { name: 'thumbnail', width: 300, height: 300, position: 'centre' },
      { name: 'card', width: 720, height: 405, position: 'centre' },
      { name: 'tablet', width: 1024, height: undefined, position: 'centre' },
    ],
  },
  fields: [
    { name: 'alt', type: 'text', required: true },
  ],
}
```

Requires `sharp` to be passed in the config for image processing.

## Custom Endpoints

Add REST endpoints to collections or globally:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  // ...
  endpoints: [
    {
      path: '/by-category/:categoryId',
      method: 'get',
      handler: async (req) => {
        const { categoryId } = req.routeParams as { categoryId: string }
        const posts = await req.payload.find({
          collection: 'posts',
          where: { categories: { equals: categoryId } },
        })
        return Response.json(posts)
      },
    },
  ],
}
```
