# Draft Preview and Live Preview

## Draft System Overview

The template implements a complete draft/publish workflow using Payload's versions API. Pages and Posts collections enable drafts with autosave and scheduled publishing.

### Versions Configuration

```typescript
versions: {
  drafts: {
    autosave: { interval: 100 },  // 100ms interval for optimal live preview
    schedulePublish: true,
  },
  maxPerDoc: 50,
}
```

- `autosave.interval: 100` — Saves draft changes every 100ms, enabling near-real-time live preview
- `schedulePublish: true` — Allows setting future publish/unpublish dates via the jobs queue
- `maxPerDoc: 50` — Retains up to 50 version snapshots per document

### Document Status

When drafts are enabled, Payload automatically adds a `_status` field to documents with values `draft` or `published`. The access control pattern `authenticatedOrPublished` uses this field:

```typescript
export const authenticatedOrPublished: Access = ({ req: { user } }) => {
  if (user) return true
  return { _status: { equals: 'published' } }
}
```

## Draft Preview

Draft preview allows editors to view unpublished content on the actual frontend.

### Preview URL Generation

The `generatePreviewPath` utility creates a secure preview URL:

```typescript
export const generatePreviewPath = ({ collection, slug }: Props) => {
  if (slug === undefined || slug === null) return null

  const encodedSlug = encodeURIComponent(slug)
  const encodedParams = new URLSearchParams({
    path: `${collectionPrefixMap[collection]}/${encodedSlug}`,
    previewSecret: process.env.PREVIEW_SECRET || '',
  })

  return `/next/preview?${encodedParams.toString()}`
}
```

The collection prefix map determines the URL path:
- `pages` → `/{slug}` (empty prefix, home maps to `/`)
- `posts` → `/posts/{slug}`

### Preview Endpoint

The preview route handler at `src/app/(frontend)/next/preview/route.ts` validates the secret, enables Next.js draft mode, and redirects to the target path:

```typescript
// Conceptual pattern
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const path = searchParams.get('path')
  const secret = searchParams.get('previewSecret')

  if (secret !== process.env.PREVIEW_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 })
  }

  draftMode().enable()
  return Redirect(`${path || '/'}`)
}
```

### Admin Configuration

Each collection configures both `preview` and `livePreview` in the admin settings:

```typescript
admin: {
  preview: (data, { req }) =>
    generatePreviewPath({ slug: data?.slug as string, collection: 'pages', req }),
  livePreview: {
    url: ({ data, req }) =>
      generatePreviewPath({ slug: data?.slug, collection: 'pages', req }),
  },
}
```

- `preview` — Static preview URL (used for the "Preview" button)
- `livePreview.url` — Dynamic URL function that updates as data changes (used for live preview iframe)

## Live Preview

Live preview provides real-time rendering of content as it's being edited in the admin panel.

### Breakpoints Configuration

The payload config defines responsive breakpoints for the live preview iframe:

```typescript
admin: {
  livePreview: {
    breakpoints: [
      { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
      { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
      { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
    ],
  },
}
```

### Live Preview Listener

The `LivePreviewListener` component is conditionally rendered on the frontend when draft mode is active:

```typescript
{draft && <LivePreviewListener />}
```

This component listens for changes from the admin panel's live preview iframe and updates the page content in real-time using Payload's `@payloadcms/live-preview-react` package.

## Scheduled Publishing

Scheduled publishing uses Payload's jobs queue to automatically publish or unpublish documents at specified times.

### Jobs Configuration

```typescript
jobs: {
  access: {
    run: ({ req }: { req: PayloadRequest }): boolean => {
      if (req.user) return true
      const secret = process.env.CRON_SECRET
      if (!secret) return false
      return req.headers.get('authorization') === `Bearer ${secret}`
    },
  },
  tasks: [],
}
```

The access control allows:
1. Logged-in users to trigger jobs manually
2. Automated cron jobs with the `CRON_SECRET` bearer token

### Cron Scheduling

On Vercel, cron jobs are configured in `vercel.json` or through the Vercel dashboard. Depending on the plan tier, cron may be limited to daily intervals. On self-hosted deployments, use system cron or a process manager.

## PublishedAt Hook

The `populatePublishedAt` hook automatically sets the publication timestamp:

```typescript
export const populatePublishedAt: CollectionBeforeChangeHook = ({ data, operation, req }) => {
  if (operation === 'create' || operation === 'update') {
    if (req.data && !req.data.publishedAt) {
      return { ...data, publishedAt: new Date() }
    }
  }
  return data
}
```

This runs before document changes and sets `publishedAt` to the current time when publishing, ensuring accurate publication timestamps.

## Cache Revalidation on Publish

When a document transitions to or from published status, the `afterChange` hook triggers Next.js cache revalidation:

```typescript
export const revalidatePage: CollectionAfterChangeHook<Page> = ({
  doc, previousDoc, req: { payload, context },
}) => {
  if (!context.disableRevalidate) {
    // New publication — revalidate the new path
    if (doc._status === 'published') {
      const path = doc.slug === 'home' ? '/' : `/${doc.slug}`
      revalidatePath(path)
      revalidateTag('pages-sitemap', 'max')
    }

    // Unpublishing — revalidate the old path
    if (previousDoc?._status === 'published' && doc._status !== 'published') {
      const oldPath = previousDoc.slug === 'home' ? '/' : `/${previousDoc.slug}`
      revalidatePath(oldPath)
      revalidateTag('pages-sitemap', 'max')
    }
  }
  return doc
}
```

The `context.disableRevalidate` check allows bypassing revalidation during bulk operations or seeding.
