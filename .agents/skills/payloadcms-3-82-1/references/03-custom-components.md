# Custom Components Reference

Complete guide to React component customization for the Payload CMS v3.82.1 admin panel, including server components, client components, and performance best practices.

## Component Overview

Payload's admin panel is fully customizable using React components. Components can be:
- **Server Components** (default): Can use Local API directly, no JavaScript sent to browser
- **Client Components**: Use React hooks and state, require `'use client'` directive

### Component Definition Methods

Components are defined using **file paths** in configuration (not direct imports):

```typescript
export default buildConfig({
  admin: {
    components: {
      // Path-based component definition
      Logo: '/components/Logo',
      Nav: '/components/CustomNav',
      
      // Named export with suffix
      Header: '/components/Header#CustomHeader',
      
      // Array of components
      header: ['/components/AnnouncementBanner', '/components/ThemeToggle'],
    },
  },
})
```

**Path Resolution Rules**:
- Paths are relative to project root or `config.admin.importMap.baseDir`
- Named exports: use `#ExportName` suffix or `exportName` property
- Default exports: no suffix needed
- File extensions can be omitted (`.tsx`, `.ts`, `.jsx`, `.js` auto-detected)

## Component Categories

### 1. Root Components

Global admin panel customization affecting all collections.

```typescript
export default buildConfig({
  admin: {
    components: {
      // Branding
      graphics: {
        Logo: '/components/Logo',
        Icon: '/components/Icon',
      },
      
      // Navigation
      Nav: '/components/CustomNav',
      beforeNavLinks: ['/components/CustomNavItem'],
      afterNavLinks: ['/components/NavFooter'],
      
      // Header (top bar)
      header: [
        '/components/AnnouncementBanner',
        '/components/UserMenu',
      ],
      actions: ['/components/ClearCache', '/components/Preview'],
      
      // Dashboard
      beforeDashboard: ['/components/WelcomeMessage'],
      afterDashboard: ['/components/AnalyticsWidget'],
      
      // Auth pages
      beforeLogin: ['/components/SSOButtons'],
      logout: { Button: '/components/LogoutButton' },
      
      // Settings menu
      settingsMenu: ['/components/SettingsMenu'],
      
      // Views
      views: {
        dashboard: { Component: '/components/CustomDashboard' },
      },
    },
  },
})
```

### 2. Collection Components

Collection-specific UI customization:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    components: {
      // Edit view components
      edit: {
        PreviewButton: '/components/PostPreviewButton',
        SaveButton: '/components/CustomSaveButton',
        SaveDraftButton: '/components/SaveDraftButton',
        PublishButton: '/components/PublishButton',
        DuplicateButton: '/components/DuplicatePostButton',
      },
      
      // List view components
      list: {
        Header: '/components/PostsListHeader',
        beforeList: ['/components/BulkActions'],
        afterList: ['/components/ListFooterStats'],
      },
    },
  },
}
```

### 3. Global Components

Customize global document views:

```typescript
export const Header: GlobalConfig = {
  slug: 'header',
  admin: {
    components: {
      edit: {
        PreviewButton: '/components/HeaderPreview',
      },
    },
  },
}
```

### 4. Field Components

Customize individual field rendering:

```typescript
{
  name: 'status',
  type: 'select',
  options: ['draft', 'published', 'archived'],
  admin: {
    components: {
      // Edit view field component
      Field: '/components/StatusField',
      
      // List view cell component
      Cell: '/components/StatusCell',
      
      // Field label component
      Label: '/components/StatusLabel',
      
      // Field description component
      Description: '/components/StatusDescription',
      
      // Error message component
      Error: '/components/StatusError',
    },
  },
}
```

**UI Field for Custom Components**:
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

## Server vs Client Components

### Server Components (Default)

All components are Server Components by default. Can use Local API directly:

```tsx
// /components/PostStats.tsx
import type { Payload } from 'payload'

async function PostStats({ payload }: { payload: Payload }) {
  // Direct Local API usage (no 'use client' needed)
  const posts = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
  })
  
  return (
    <div className="stats">
      <h3>Published Posts</h3>
      <p>{posts.totalDocs} posts</p>
    </div>
  )
}

export default PostStats
```

**Benefits of Server Components**:
- Direct Local API access
- No JavaScript sent to browser
- Automatic data fetching
- Better performance for read-only content

### Client Components

Use `'use client'` directive for interactivity:

```tsx
// /components/LivePreview.tsx
'use client'

import { useState, useEffect } from 'react'
import { useField, useForm } from '@payloadcms/ui'

export function LivePreview() {
  const [previewData, setPreviewData] = useState(null)
  
  // Access field value
  const title = useField('title')
  const { fields } = useForm()
  
  // Poll for preview updates
  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/api/preview')
      const data = await response.json()
      setPreviewData(data)
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])
  
  return (
    <div>
      <button onClick={() => window.open(previewData?.url)}>
        Open Preview
      </button>
    </div>
  )
}
```

**When to use Client Components**:
- Need state (`useState`, `useReducer`)
- Need effects (`useEffect`, `useLayoutEffect`)
- Need event handlers (`onClick`, `onChange`, etc.)
- Need browser APIs (`localStorage`, `window`, `navigator`)

## Payload UI Hooks

Available hooks for Client Components (from `@payloadcms/ui`):

```tsx
'use client'

import {
  useAuth,         // Current user and auth state
  useConfig,       // Payload config (client-safe)
  useDocumentInfo, // Document info (id, collection, etc.)
  useField,        // Single field value and setter
  useForm,         // Full form state and methods
  useFormFields,   // Multiple field values (optimized)
  useLocale,       // Current locale (i18n)
  useTranslation,  // i18n translations
  usePayload,      // Local API methods (client-side)
} from '@payloadcms/ui'

export function MyComponent() {
  const { user, login, logout } = useAuth()
  const { config } = useConfig()
  const { id, collection, slug } = useDocumentInfo()
  const locale = useLocale()
  const { t } = useTranslation()
  
  // Single field access
  const [title, setTitle] = useField('title')
  
  // Multiple fields (optimized - only re-renders when specific fields change)
  const [fields] = useFormFields(f => [
    f['title'],
    f['status'],
    f['author'],
  ])
  
  // Full form access
  const { fields: allFields, submitForm } = useForm()
  
  // Client-side Local API
  const payload = usePayload()
  
  return (
    <div>
      <p>Hello, {user?.email}</p>
      <p>Editing: {collection} - {id}</p>
    </div>
  )
}
```

## Component Examples

### Custom Logo Component

```tsx
// /components/Logo.tsx
import type { GraphicsServerComponent } from 'payload'

const Logo: GraphicsServerComponent = () => (
  <svg width="120" height="40" viewBox="0 0 120 40">
    <text x="0" y="30" fontSize="24" fill="var(--theme-text)">
      My CMS
    </text>
  </svg>
)

export default Logo
```

### Custom Navigation Component

```tsx
// /components/CustomNav.tsx
'use client'

import { useConfig } from '@payloadcms/ui'

export function CustomNav() {
  const { config } = useConfig()
  
  return (
    <nav className="custom-nav">
      {config.collections.map(collection => (
        <a
          key={collection.slug}
          href={`/admin/${collection.slug}`}
        >
          {collection.labels.plural}
        </a>
      ))}
    </nav>
  )
}
```

### Preview Button Component

```tsx
// /components/PostPreviewButton.tsx
'use client'

import { useFormFields } from '@payloadcms/ui'

export function PostPreviewButton() {
  const [slug] = useFormFields(f => f['slug'])
  
  const handlePreview = () => {
    const previewUrl = `/preview?slug=${encodeURIComponent(slug)}`
    window.open(previewUrl, '_blank')
  }
  
  return (
    <button onClick={handlePreview} type="button">
      Preview Post
    </button>
  )
}
```

### Status Field Cell Component

```tsx
// /components/StatusCell.tsx
import type { SelectFieldCellComponent } from 'payload'

const StatusCell: SelectFieldCellComponent = ({ value }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'var(--theme-success)'
      case 'draft': return 'var(--theme-text-500)'
      case 'archived': return 'var(--theme-text-300)'
      default: return 'var(--theme-text)'
    }
  }
  
  return (
    <span style={{ 
      color: getStatusColor(value || ''),
      fontWeight: 'bold',
      textTransform: 'capitalize',
    }}>
      {value}
    </span>
  )
}

export default StatusCell
```

### Announcement Banner Component

```tsx
// /components/AnnouncementBanner.tsx
import type { HeaderServerComponent } from 'payload'

const AnnouncementBanner: HeaderServerComponent = () => (
  <div className="announcement-banner" style={{
    backgroundColor: 'var(--theme-warning)',
    color: 'var(--theme-text-on-color)',
    padding: 'var(--base)',
    textAlign: 'center',
    fontWeight: 'bold',
  }}>
    🎉 New features available! Check out the changelog.
  </div>
)

export default AnnouncementBanner
```

### Custom Save Button with Analytics

```tsx
// /components/CustomSaveButton.tsx
'use client'

import { useCallback } from 'react'
import { useForm } from '@payloadcms/ui'

export function CustomSaveButton() {
  const { submitForm, saving } = useForm()
  
  const handleSave = useCallback(async () => {
    // Track analytics event
    if (window.gtag) {
      window.gtag('event', 'save_document', {
        event_category: 'Content',
        event_label: 'Save Button Click',
      })
    }
    
    // Submit form
    await submitForm()
  }, [submitForm])
  
  return (
    <button
      onClick={handleSave}
      disabled={saving}
      type="button"
    >
      {saving ? 'Saving...' : 'Save'}
    </button>
  )
}
```

## Styling Components

### CSS Variables

Use Payload's theme variables for consistent styling:

```tsx
<div style={{
  backgroundColor: 'var(--theme-elevation-500)',
  color: 'var(--theme-text)',
  padding: 'var(--base)',
  borderRadius: 'var(--border-radius-m)',
  border: '1px solid var(--theme-border)',
}}>
  Content
</div>
```

**Common Theme Variables**:
- `--theme-text`, `--theme-text-500`, `--theme-text-300`
- `--theme-elevation-500`, `--theme-elevation-400`, etc.
- `--theme-success`, `--theme-error`, `--theme-warning`
- `--theme-border`, `--theme-border-focus`
- `--base` (spacing unit, typically 8px)
- `--border-radius-m`, `--border-radius-l`

### SCSS Imports

Use Payload's SCSS library with mixins:

```scss
// /components/CustomNav.scss
@import '~@payloadcms/ui/scss';

.custom-nav {
  background-color: var(--theme-elevation-500);
  padding: var(--base);
  border-radius: var(--border-radius-m);
  
  a {
    color: var(--theme-text);
    text-decoration: none;
    margin-right: var(--base);
    
    &:hover {
      color: var(--theme-link);
    }
  }
  
  // Responsive breakpoint mixin
  @include mid-break {
    background-color: var(--theme-elevation-900);
  }
}
```

### CSS Modules

Use CSS modules for scoped styling:

```tsx
// /components/StatusCell.tsx
import styles from './StatusCell.module.scss'

const StatusCell = ({ value }) => (
  <span className={styles.cell} data-status={value}>
    {value}
  </span>
)
```

```scss
// /components/StatusCell.module.scss
.cell {
  font-weight: bold;
  text-transform: capitalize;
  
  &[data-status='published'] {
    color: var(--theme-success);
  }
  
  &[data-status='draft'] {
    color: var(--theme-text-500);
  }
}
```

## Performance Best Practices

### 1. Import Components Correctly

**Admin Panel** (components loaded in admin bundle):
```tsx
import { Button, Stack } from '@payloadcms/ui'
```

**Frontend** (avoid loading admin-specific code):
```tsx
import { Button } from '@payloadcms/ui/elements/Button'
import { Stack } from '@payloadcms/ui/elements/Stack'
```

### 2. Optimize Re-renders with useFormFields

**❌ BAD**: Re-renders on every form change:
```tsx
const { fields } = useForm()
const title = fields['title']
const status = fields['status']
```

**✅ GOOD**: Only re-renders when specific fields change:
```tsx
const [title] = useFormFields(f => [f['title']])
const [status] = useFormFields(f => [f['status']])
```

### 3. Prefer Server Components

Only use Client Components when you need:
- React state (`useState`, `useReducer`)
- Effects (`useEffect`)
- Event handlers (`onClick`, `onChange`)
- Browser APIs (`localStorage`, `window`)

**Server Component** (better performance):
```tsx
// No 'use client' - Server Component by default
async function DocumentStats({ payload }) {
  const docs = await payload.find({ collection: 'posts' })
  return <p>{docs.totalDocs} documents</p>
}
```

**Client Component** (when interactivity needed):
```tsx
'use client' // Required for hooks/state

function LiveCounter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

### 4. Minimize Serialized Props

Server Components serialize props when passing to Client Components:

**❌ BAD**: Large object prop causes serialization overhead:
```tsx
<ClientComponent allData={hugeObject} />
```

**✅ GOOD**: Pass minimal data, fetch in client if needed:
```tsx
<ClientComponent docId={doc.id} collection={collection.slug} />
```

### 5. Lazy Load Heavy Components

Use dynamic imports for rarely-used components:

```tsx
const HeavyAnalytics = dynamic(
  () => import('/components/HeavyAnalytics'),
  { loading: () => <Spinner /> }
)
```

## Type Safety

### Component Type Definitions

Use Payload's built-in types for full type safety:

```tsx
import type {
  // Field components
  TextFieldServerComponent,
  TextFieldClientComponent,
  TextFieldCellComponent,
  SelectFieldServerComponent,
  NumberFieldClientComponent,
  
  // View components
  EditViewServerComponent,
  ListViewClientComponent,
  
  // Root components
  GraphicsServerComponent,
  HeaderServerComponent,
} from 'payload'

// Typed field component
export const MyTextField: TextFieldClientComponent = (props) => {
  // props is fully typed with field info, value, onChange, etc.
  const { value, onChange, field } = props
  
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={field.admin?.placeholder}
    />
  )
}

// Typed graphics component
export const Logo: GraphicsServerComponent = () => {
  return <img src="/logo.svg" alt="Logo" />
}
```

### Props Types by Component Type

**Field Components receive**:
```typescript
{
  value: string | number | boolean | object,
  onChange: (value) => void,
  field: Field,
  readOnly: boolean,
  error: string | null,
  // ... other field-specific props
}
```

**Cell Components receive**:
```typescript
{
  value: string | number | boolean | object,
  row: Document,
  field: Field,
  collection: CollectionConfig,
}
```

## Import Map Configuration

Payload auto-generates `app/(payload)/admin/importMap.js` to resolve component paths.

### Regenerate Import Map

Manually regenerate after adding/modifying components:

```bash
payload generate:importmap
```

### Custom Import Map Location

Configure custom import map path:

```typescript
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    importMap: {
      baseDir: path.resolve(dirname, 'src'), // Base directory for component paths
      importMapFile: path.resolve(dirname, 'app', 'custom-import-map.js'),
    },
  },
})
```

## Component Debugging

### Check Component Registration

Verify components are properly registered:

```bash
# Check import map
cat app/(payload)/admin/importMap.js

# Look for your component paths
grep -n "Logo\|CustomNav" app/(payload)/admin/importMap.js
```

### TypeScript Validation

Validate component types:

```bash
npm run typecheck
# or
tsc --noEmit
```

### Common Issues

**Component not appearing**:
- Check path is correct (relative to `baseDir`)
- Verify export name matches (`default` vs named export)
- Regenerate import map: `payload generate:importmap`
- Check browser console for errors

**TypeScript errors**:
- Use correct component type from `payload`
- Ensure all required props are handled
- Check field types match component expectations

**Client component hydration errors**:
- Ensure `'use client'` directive is first line
- Match server/client rendering logic
- Use `useEffect` for browser-only code
