# Customizations and Extensions

This reference covers extending the Payload CMS Website Template with custom components, hooks, access control, fields, blocks, and integration patterns.

## Custom Layout Blocks

### Creating a New Block

**Step 1: Define Block Configuration**

```ts
// src/blocks/Testimonial/config.ts
import type { Block } from 'payload'

export const Testimonial: Block = {
  slug: 'testimonial',
  labels: {
    singular: 'Testimonial',
    plural: 'Testimonials',
  },
  fields: [
    {
      name: 'content',
      type: 'textarea',
      required: true,
      admin: {
        rows: 4,
      },
    },
    {
      name: 'author',
      type: 'text',
      required: true,
    },
    {
      name: 'role',
      type: 'text',
    },
    {
      name: 'company',
      type: 'text',
    },
    {
      name: 'avatar',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'position',
      type: 'select',
      options: [
        { label: 'Left', value: 'left' },
        { label: 'Center', value: 'center' },
        { label: 'Right', value: 'right' },
      ],
      defaultValue: 'center',
    },
  ],
}
```

**Step 2: Add Block to Pages Collection**

```ts
// src/collections/Pages/index.ts
import { Testimonial } from '../../blocks/Testimonial/config'

export const Pages: CollectionConfig<'pages'> = {
  // ...
  fields: [
    {
      type: 'tabs',
      tabs: [
        {
          fields: [
            {
              name: 'layout',
              type: 'blocks',
              blocks: [
                CallToAction,
                Content,
                MediaBlock,
                Archive,
                FormBlock,
                Testimonial, // Add new block
              ],
            },
          ],
          label: 'Content',
        },
      ],
    },
  ],
}
```

**Step 3: Create React Component**

```tsx
// src/blocks/Testimonial/Client.tsx
import Image from 'next/image'

export function Testimonial({
  content,
  author,
  role,
  company,
  avatar,
  position = 'center',
}: {
  content: string
  author: string
  role?: string
  company?: string
  avatar?: any
  position?: 'left' | 'center' | 'right'
}) {
  const positionClasses = {
    left: 'items-start',
    center: 'items-center',
    right: 'items-end',
  }

  return (
    <div className={`flex ${positionClasses[position]} max-w-4xl mx-auto my-16 px-4`}>
      <div className="w-full bg-gray-50 rounded-xl p-8">
        <div className="flex gap-4 mb-6">
          {avatar && (
            <Image
              src={avatar.url}
              alt={author}
              width={64}
              height={64}
              className="rounded-full"
            />
          )}
          <div>
            <h3 className="font-semibold text-lg">{author}</h3>
            {(role || company) && (
              <p className="text-gray-600">
                {role}{role && company && ' at '}{company}
              </p>
            )}
          </div>
        </div>
        <blockquote className="text-xl italic text-gray-700">
          &quot;{content}&quot;
        </blockquote>
      </div>
    </div>
  )
}
```

**Step 4: Add to RenderBlocks**

```tsx
// src/blocks/RenderBlocks.tsx
import { Testimonial } from '@/blocks/Testimonial/Client'

export const RenderBlocks = ({ blocks }: { blocks: Page['layout'] }) => {
  return (
    <>
      {blocks?.map((block, i) => {
        const key = `${block.blockType}-${i}`
        switch (block.blockType) {
          case 'callToAction':
            return <CallToAction {...block} key={key} />
          case 'content':
            return <Content {...block} key={key} />
          case 'mediaBlock':
            return <MediaBlock {...block} key={key} />
          case 'archive':
            return <Archive {...block} key={key} />
          case 'formBlock':
            return <FormBlock {...block} key={key} />
          case 'testimonial': // Add new block handler
            return <Testimonial {...block} key={key} />
          default:
            return null
        }
      })}
    </>
  )
}
```

## Custom Hero Types

### Adding a New Hero Variant

**Step 1: Extend Hero Configuration**

```ts
// src/heros/config.ts
import type { Block } from 'payload'

export const hero: Block = {
  name: 'hero',
  type: 'block',
  fields: [
    {
      name: 'type',
      type: 'select',
      options: [
        { label: 'Home', value: 'home' },
        { label: 'Centered', value: 'centered' },
        { label: 'Small', value: 'small' },
        { label: 'Split Left', value: 'splitLeft' },
        { label: 'Split Right', value: 'splitRight' },
        { label: 'Video Background', value: 'video' }, // New variant
      ],
      required: true,
    },
    {
      name: 'richText',
      type: 'richText',
      editor: lexicalEditor({ /* ... */ }),
    },
    {
      name: 'media',
      type: 'upload',
      relationTo: 'media',
    },
    // Additional fields for video hero
    {
      name: 'videoUrl',
      type: 'text',
      admin: {
        condition: (_, { type } = {}) => type === 'video',
      },
    },
  ],
}
```

**Step 2: Update RenderHero Component**

```tsx
// src/heros/RenderHero.tsx
import { VideoHero } from './VideoHero'

export const RenderHero = (props: Hero) => {
  const { type } = props

  switch (type) {
    case 'home':
      return <HomeHero {...props} />
    case 'centered':
      return <CenteredHero {...props} />
    case 'small':
      return <SmallHero {...props} />
    case 'splitLeft':
      return <SplitLeftHero {...props} />
    case 'splitRight':
      return <SplitRightHero {...props} />
    case 'video':
      return <VideoHero {...props} /> // New variant
    default:
      return null
  }
}
```

**Step 3: Create Hero Component**

```tsx
// src/heros/VideoHero.tsx
export function VideoHero({ richText, videoUrl }: {
  richText: any
  videoUrl?: string
}) {
  return (
    <div className="relative min-h-[600px] flex items-center justify-center">
      {videoUrl && (
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        >
          <source src={videoUrl} />
        </video>
      )}
      <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
        <ReactNodeRenderer nodes={richText} />
      </div>
    </div>
  )
}
```

## Custom Fields

### Creating Reusable Field Groups

**SEO Fields Group:**

```ts
// src/fields/customSEO.ts
import type { Field } from 'payload'

export const customSEOFields: Field[] = [
  {
    name: 'customMeta',
    label: 'Custom SEO',
    type: 'group',
    fields: [
      {
        name: 'keywords',
        type: 'relationship',
        relationTo: 'keywords',
        hasMany: true,
        admin: {
          description: 'Select keywords relevant to this content',
        },
      },
      {
        name: 'noIndex',
        type: 'checkbox',
        label: 'Exclude from search engines',
        admin: {
          description: 'Check to prevent search engines from indexing this page',
        },
      },
      {
        name: 'canonicalURL',
        type: 'text',
        label: 'Canonical URL',
        admin: {
          description: 'Override the canonical URL (leave empty for auto-generated)',
        },
      },
    ],
  },
]
```

**Usage in Collection:**

```ts
// src/collections/Pages/index.ts
import { customSEOFields } from '@/fields/customSEO'

export const Pages: CollectionConfig<'pages'> = {
  fields: [
    // ... existing fields
    ...customSEOFields,
  ],
}
```

### Custom Rich Text Editor Features

**Adding Custom Lexical Features:**

```ts
// src/fields/customLexical.ts
import {
  lexicalEditor,
  BlocksFeature,
} from '@payloadcms/richtext-lexical'
import { Quote } from '@/blocks/Quote/config'

export const customLexicalEditor = lexicalEditor({
  features: ({ rootFeatures }) => {
    return [
      ...rootFeatures,
      BlocksFeature({ blocks: [Quote] }), // Add custom block
      // Add more custom features here
    ]
  },
})
```

## Custom Hooks

### Before Change Hook

**Transform Data Before Save:**

```ts
// src/hooks/slugifyTitle.ts
export const slugifyTitle = ({ doc, operation }: {
  doc: any
  operation: 'create' | 'update'
}) => {
  if (operation === 'create' && doc.title && !doc.slug) {
    doc.slug = doc.title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
  }
  return doc
}
```

**Usage:**

```ts
export const Pages: CollectionConfig<'pages'> = {
  hooks: {
    beforeChange: [slugifyTitle],
  },
}
```

### After Change Hook

**Trigger External Actions:**

```ts
// src/hooks/notifySlack.ts
export const notifySlack = async ({ doc, previousDoc, operation }: {
  doc: any
  previousDoc?: any
  operation: string
}) => {
  if (operation === 'create' && doc._status === 'published') {
    const webhookURL = process.env.SLACK_WEBHOOK_URL
    
    await fetch(webhookURL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: `New ${doc.collection} published: ${doc.title}`,
        attachments: [{
          title: doc.title,
          title_link: `${process.env.PAYLOAD_PUBLIC_SERVER_URL}/${doc.slug}`,
        }],
      }),
    })
  }
}
```

### Before Delete Hook

**Prevent Deletion with Dependencies:**

```ts
// src/hooks/checkDependencies.ts
export const checkDependencies = async ({ doc, context }: {
  doc: any
  context: any
}) => {
  // Check if other documents reference this one
  const references = await payload.find({
    collection: 'pages',
    where: {
      'layout.form': { equals: doc.id },
    },
    limit: 1,
  })

  if (references.docs.length > 0) {
    throw new Error(
      'Cannot delete this form. It is being used by one or more pages.'
    )
  }
}
```

## Access Control

### Custom Access Functions

**Role-Based Access:**

```ts
// src/access/hasRole.ts
export const hasRole = (roles: string[]) => {
  return ({ req }: { req: any }) => {
    if (!req.user) return false
    return roles.includes(req.user.role)
  }
}
```

**Usage:**

```ts
export const Pages: CollectionConfig<'pages'> = {
  access: {
    create: hasRole(['admin', 'editor']),
    update: hasRole(['admin', 'editor']),
    delete: hasRole(['admin']),
    read: authenticatedOrPublished,
  },
}
```

**Document Ownership:**

```ts
// src/access/ownerOrAdmin.ts
export const ownerOrAdmin = ({ req, doc }: { req: any; doc?: any }) => {
  if (!req.user) return false
  
  // Admins can access everything
  if (req.user.role === 'admin') return true
  
  // Users can only access their own documents
  if (doc && doc.author) {
    return doc.author.id === req.user.id
  }
  
  return false
}
```

### Field-Level Access Control

**Restrict Field Editing:**

```ts
export const Posts: CollectionConfig<'posts'> = {
  fields: [
    {
      name: 'publishedAt',
      type: 'date',
      access: {
        create: ({ req }) => req.user?.role === 'admin',
        update: ({ req }) => req.user?.role === 'admin',
      },
      admin: {
        condition: ({ user }) => user?.role === 'admin',
      },
    },
  ],
}
```

## Custom Components

### Admin Panel Components

**Before Login Component:**

```tsx
// src/components/BeforeLogin.tsx
export default function BeforeLogin() {
  return (
    <div className="p-4 bg-blue-50 rounded-lg">
      <h3 className="font-semibold text-blue-800 mb-2">Welcome!</h3>
      <p className="text-sm text-blue-700">
        Login to access the admin panel and manage your content.
      </p>
    </div>
  )
}
```

**Before Dashboard Component:**

```tsx
// src/components/BeforeDashboard.tsx
export default function BeforeDashboard() {
  return (
    <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg mb-8">
      <h2 className="text-2xl font-bold mb-2">Welcome back!</h2>
      <p className="opacity-90">
        You have full access to manage pages, posts, and media.
      </p>
    </div>
  )
}
```

### Custom List Views

**Custom Table Columns:**

```ts
export const Posts: CollectionConfig<'posts'> = {
  admin: {
    defaultColumns: ['title', 'slug', 'categories', 'publishedAt', 'updatedAt'],
    listRelation: (post: Post) => `${post.slug}`,
  },
}
```

**Custom Cell Components:**

```tsx
// src/components/CategoryCell.tsx
export function CategoryCell({ value }: { value: any[] }) {
  return (
    <div className="flex gap-1">
      {value?.slice(0, 2).map((cat: any) => (
        <span key={cat.id} className="px-2 py-1 bg-gray-100 rounded text-sm">
          {cat.name}
        </span>
      ))}
      {value?.length > 2 && (
        <span className="px-2 py-1 text-gray-500 text-sm">
          +{value.length - 2}
        </span>
      )}
    </div>
  )
}
```

## Custom Collections

### Adding a New Collection

**Projects Collection Example:**

```ts
// src/collections/Projects/index.ts
import type { CollectionConfig } from 'payload'

export const Projects: CollectionConfig<'projects'> = {
  slug: 'projects',
  access: {
    create: authenticated,
    delete: authenticated,
    read: authenticatedOrPublished,
    update: authenticated,
  },
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'status'],
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'description',
      type: 'textarea',
      rows: 3,
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'In Progress', value: 'in-progress' },
        { label: 'Completed', value: 'completed' },
        { label: 'On Hold', value: 'on-hold' },
      ],
      defaultValue: 'in-progress',
    },
    {
      name: 'thumbnail',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'client',
      type: 'text',
    },
    {
      name: 'startDate',
      type: 'date',
    },
    {
      name: 'completionDate',
      type: 'date',
    },
    slugField(),
  ],
}
```

**Register Collection:**

```ts
// payload.config.ts
import { Projects } from './collections/Projects'

export default buildConfig({
  collections: [Pages, Posts, Media, Categories, Users, Projects],
})
```

## Custom Globals

### Adding a New Global

**Testimonials Global:**

```ts
// src/Testimonials/config.ts
import type { GlobalConfig } from 'payload'

export const Testimonials: GlobalConfig = {
  slug: 'testimonials',
  fields: [
    {
      name: 'featuredTestimonials',
      type: 'array',
      maxRows: 4,
      labels: {
        singular: 'Testimonial',
        plural: 'Testimonials',
      },
      fields: [
        {
          name: 'content',
          type: 'textarea',
          required: true,
        },
        {
          name: 'author',
          type: 'text',
          required: true,
        },
        {
          name: 'role',
          type: 'text',
        },
        {
          name: 'avatar',
          type: 'upload',
          relationTo: 'media',
        },
      ],
    },
  ],
}
```

**Register Global:**

```ts
// payload.config.ts
import { Testimonials } from './Testimonials/config'

export default buildConfig({
  globals: [Header, Footer, Testimonials],
})
```

## Custom API Routes

### Creating REST Endpoints

```ts
// src/app/api/statistics/route.ts
import { NextResponse } from 'next/server'
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export async function GET() {
  const payload = await getPayload({ config: configPromise })

  const pagesCount = await payload.count({ collection: 'pages' })
  const postsCount = await payload.count({ collection: 'posts' })
  const mediaCount = await payload.count({ collection: 'media' })

  return NextResponse.json({
    pages: pagesCount.totalDocs,
    posts: postsCount.totalDocs,
    media: mediaCount.totalDocs,
  })
}
```

### GraphQL Queries

Custom GraphQL resolvers can be added through the Payload config:

```ts
// payload.config.ts
export default buildConfig({
  graphQL: {
    schema: async (schema) => {
      // Add custom queries or mutations
      return schema
    },
  },
})
```

## Best Practices

### Code Organization

1. **Group related files**: Keep block configs and components together
2. **Use TypeScript**: Define types for all custom components
3. **Export clearly**: Use named exports for better tree-shaking
4. **Document APIs**: Add JSDoc comments for custom functions

### Performance

1. **Lazy load components**: Use dynamic imports for heavy components
2. **Memoize queries**: Cache Payload API calls with `cache()`
3. **Optimize images**: Use appropriate sizes and formats
4. **Minimize re-renders**: Use React.memo for static components

### Security

1. **Validate input**: Sanitize all user-provided data
2. **Enforce access control**: Check permissions on every operation
3. **Use environment variables**: Never hardcode secrets
4. **Rate limit APIs**: Prevent abuse with rate limiting

## Debugging

### Enable Debug Mode

```ts
// payload.config.ts
export default buildConfig({
  // ...
  telemetry: {
    enabled: true,
  },
})
```

### Logging Hooks

```ts
beforeChange: [
  async ({ doc, operation }) => {
    console.log(`Before ${operation}:`, { docId: doc.id, changes: doc })
    return doc
  },
]
```

### Browser DevTools

- Use React DevTools to inspect component props
- Check Network tab for API requests
- Review Console for errors and warnings
