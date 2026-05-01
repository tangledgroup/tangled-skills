# Versions, Drafts, and Localization

## Document Versioning

Enable versioning on a collection to track document history:

```typescript
export const Pages: CollectionConfig = {
  slug: 'pages',
  versions: {
    maxPerDoc: 50,        // Keep last 50 versions
    drafts: {
      autosave: {
        interval: 100,    // Autosave every 100ms (for live preview)
      },
      schedulePublish: true, // Enable scheduled publishing
    },
  },
}
```

### How Drafts Work

When `drafts: true` is enabled, Payload automatically adds a `_status` field with values `draft` or `published`. Documents are stored in the versions collection until published.

The `_status` field is managed by Payload — you typically don't need to set it manually. The admin panel provides Publish/Unpublish buttons.

### Autosave

Autosave continuously saves draft changes at a configurable interval:

```typescript
versions: {
  drafts: {
    autosave: {
      interval: 100,  // milliseconds between autosaves
    },
  },
}
```

Lower intervals (50-100ms) are ideal for live preview. Higher intervals (2000ms+) reduce database load.

### Scheduled Publishing

Enable `schedulePublish: true` to allow setting a future publish date:

```typescript
versions: {
  drafts: {
    schedulePublish: true,
  },
}
```

Combined with a `publishedAt` date field and the Jobs system, Payload can auto-publish documents at the scheduled time.

### Draft API

Query draft content via the REST API by adding `?draft=true` to requests, or via the Local API:

```typescript
const drafts = await payload.find({
  collection: 'pages',
  draft: true,
})
```

For the REST API, use the draft endpoint: `/api/pages?draft=true`.

## Version Operations

### List Versions

```typescript
const versions = await payload.findVersions({
  collection: 'posts',
  where: { 'version.title': { contains: 'hello' } },
  limit: 20,
  sort: '-version.updatedAt',
})
```

### Find Specific Version

```typescript
const version = await payload.findVersionByID({
  collection: 'posts',
  id: versionId,
})
```

### Restore Version

```typescript
const restored = await payload.restoreVersion({
  collection: 'posts',
  id: versionId,  // The version ID to restore
})
```

### Count Versions

```typescript
const count = await payload.countVersions({
  collection: 'posts',
  where: { 'version._status': { equals: 'draft' } },
})
```

## Globals with Versions

Globals also support versioning:

```typescript
export const Settings: GlobalConfig = {
  slug: 'settings',
  versions: {
    maxPerDoc: 20,
    drafts: true,
  },
  fields: [/* ... */],
}
```

Global version operations use `findGlobalVersions`, `findGlobalVersionByID`, and `restoreGlobalVersion`.

## Localization

Enable multi-language content in the Payload config:

```typescript
export default buildConfig({
  localization: {
    locales: [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Spanish' },
      { code: 'fr', label: 'French' },
    ],
    defaultLocale: 'en',
    // Fallback to default locale when translation is missing
    fallback: true,
  },
  // ...
})
```

### Localizing Fields

Mark individual fields as localized:

```typescript
{
  name: 'title',
  type: 'text',
  localized: true,  // Separate value per locale
}

{
  name: 'slug',
  type: 'text',
  // Not localized — shared across all locales
}
```

### RTL Support

For right-to-left languages:

```typescript
localization: {
  locales: [
    { code: 'en', label: 'English' },
    { code: 'ar', label: 'Arabic', rtl: true },
    { code: 'he', label: 'Hebrew', rtl: true },
  ],
}
```

### Querying by Locale

```typescript
// Find documents in Spanish
const posts = await payload.find({
  collection: 'posts',
  locale: 'es',
})

// Get all locales for a document
const post = await payload.findByID({
  collection: 'posts',
  id: postId,
  locale: 'all',
})
```

### Fallback Locale

When `fallback: true` (default), missing translations fall back to the `defaultLocale`. You can also set per-request fallback:

```typescript
const post = await payload.findByID({
  collection: 'posts',
  id: postId,
  locale: 'es',
  fallbackLocale: 'en',
})
```

### Filtering Available Locales

Dynamically control which locales a user can access:

```typescript
localization: {
  filterAvailableLocales: ({ locales, req }) => {
    if (req.user?.role === 'admin') return locales
    // Editors only see English and Spanish
    return locales.filter(l => ['en', 'es'].includes(l.code))
  },
}
```

## Combining Drafts and Localization

Drafts and localization work together. Each locale can have its own draft/published state:

```typescript
versions: {
  drafts: true,
}

// In access control:
access: {
  read: ({ req: { user, locale } }) => {
    if (user) return true
    return { _status: { equals: 'published' } }
  },
}
```

When publishing with localization, use `defaultLocalePublishOption` to control behavior:

```typescript
localization: {
  defaultLocale: 'en',
  // Publish all locales together, or only the active locale
  defaultLocalePublishOption: 'active', // or 'all' (default)
}
```

## Migration Considerations

When enabling versions on an existing collection, Payload creates a new versions collection/table (e.g., `post-versions` for MongoDB, `post_versions` for Postgres). Existing documents are not automatically versioned — only new changes create versions.

When enabling localization on existing fields, existing data remains in the default locale. New locales start empty and should be populated through the admin or API.
