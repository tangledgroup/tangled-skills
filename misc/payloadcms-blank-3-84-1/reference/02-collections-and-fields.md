# Collections and Fields

## Users Collection

The Users collection is the authentication-enabled collection that controls admin panel access. It is referenced in the admin config as the user collection slug.

```ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: {
    useAsTitle: 'email',
  },
  auth: true,
  fields: [
    // Email and password fields are added automatically by auth: true
    // Add custom fields here as needed
  ],
}
```

Key properties:

- `slug: 'users'` — URL-safe identifier used in API endpoints (`/api/users`) and database collection names
- `auth: true` — enables authentication, automatically adding email, password, and verification fields
- `admin.useAsTitle` — determines which field displays as the document title in the admin UI
- When `auth: true` is set, Payload automatically generates login, logout, registration, and password reset endpoints

To extend the Users collection with custom fields:

```ts
fields: [
  {
    name: 'role',
    type: 'select',
    options: ['admin', 'editor', 'viewer'],
    defaultValue: 'viewer',
  },
  {
    name: 'displayName',
    type: 'text',
  },
]
```

## Media Collection

The Media collection handles file uploads including images, documents, and other assets. It is upload-enabled with public read access.

```ts
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: {
    read: () => true,
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

Key properties:

- `upload: true` — enables file upload functionality, automatically adding `url`, `filename`, `mimeType`, `filesize`, and `width`/`height` (for images) fields
- `access.read: () => true` — allows unauthenticated reads so media files are publicly accessible
- `alt` field — required text field for accessibility descriptions

To configure image sizes and focal point for the Media collection:

```ts
upload: {
  staticDir: 'media',
  mimeTypes: ['image/*', 'application/pdf'],
  adminThumbnail: 'thumbnail',
  imageSizes: [
    {
      name: 'thumbnail',
      width: 300,
      height: 300,
      position: 'centre',
    },
    {
      name: 'medium',
      width: 720,
      height: 720,
      position: 'centre',
    },
  ],
  focalPoint: true,
},
```

## Field Types

Payload supports a comprehensive set of field types. The most commonly used include:

- **`text`** — single-line text input
- **`textarea`** — multi-line text input
- **`number`** — numeric input with optional min/max
- **`date`** — date picker
- **`select`** — dropdown with predefined options
- **`checkbox`** — boolean toggle
- **`richText`** — rich-text editor (Lexical when configured)
- **`relationship`** — reference to documents in other collections
- **`upload`** — file picker referencing the Media collection
- **`group`** — groups fields under a nested object
- **`row`** — lays out child fields horizontally in the admin UI
- **`tabs`** — organizes fields into tabbed sections
- **`array`** — repeatable group of fields
- **`blocks`** — repeatable content blocks with different types

Example of a rich-text field using Lexical:

```ts
{
  name: 'content',
  type: 'richText',
}
```

When the editor is configured as `lexicalEditor()` in `payload.config.ts`, all `richText` fields use the Lexical editor automatically.

## Access Control

Access control functions determine who can read, create, update, or delete documents. The blank template sets public read access on Media:

```ts
access: {
  read: () => true,  // anyone can read
}
```

For authenticated-only access:

```ts
access: {
  read: ({ req: { user } }) => Boolean(user),
  create: ({ req: { user } }) => Boolean(user),
  update: ({ req: { user } }) => Boolean(user),
  delete: ({ req: { user } }) => Boolean(user),
},
```

Field-level access control is also supported:

```ts
{
  name: 'internalNotes',
  type: 'textarea',
  access: {
    read: ({ req: { user } }) => user?.role === 'admin',
  },
}
```

## Creating New Collections

To add a new collection, create a file in `src/collections/` and register it in `payload.config.ts`:

```ts
// src/collections/Posts.ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'content',
      type: 'richText',
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
    },
  ],
}
```

Then import and add it to the collections array in `payload.config.ts`:

```ts
import { Posts } from './collections/Posts'

export default buildConfig({
  collections: [Users, Media, Posts],
  // ...
})
```

After adding collections, regenerate types:

```bash
pnpm generate:types
```
