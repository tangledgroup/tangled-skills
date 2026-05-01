# Admin Panel Customization

## Overview

The Payload admin panel is built with Next.js App Router and React Server Components. Every component in the admin UI can be extended or replaced. Custom components are referenced by string paths relative to the `importMap.baseDir`.

## Import Map

The import map resolves component paths to actual files:

```typescript
// payload.config.ts
export default buildConfig({
  admin: {
    importMap: {
      baseDir: path.resolve(dirname),
      // Auto-generate during development (default: true)
      autoGenerate: true,
    },
  },
})
```

Components are referenced as relative paths from `baseDir`:

```typescript
admin: {
  components: {
    beforeLogin: ['@/components/BeforeLogin'],
    beforeDashboard: ['@/components/BeforeDashboard'],
  },
}
```

## Custom Components in Config

### Global Admin Components

```typescript
admin: {
  components: {
    // Top right of admin panel
    actions: ['@/components/AdminActions'],
    // After navigation section
    afterNav: ['@/components/AfterNav'],
    afterNavLinks: ['@/components/NavLinks'],
    // Before navigation section
    beforeNav: ['@/components/BeforeNav'],
    beforeNavLinks: ['@/components/BeforeNavLinks'],
    // Global header
    header: ['@/components/AdminHeader'],
    // Login page customizations
    beforeLogin: ['@/components/BeforeLogin'],
    afterLogin: ['@/components/AfterLogin'],
    // Dashboard
    beforeDashboard: ['@/components/BeforeDashboard'],
    afterDashboard: ['@/components/AfterDashboard'],
    // Graphics
    graphics: {
      Icon: '@/components/AdminIcon',
      Logo: '@/components/AdminLogo',
    },
    // Settings menu (gear icon)
    settingsMenu: ['@/components/SettingsMenuItem'],
    // Context providers
    providers: ['@/components/ThemeProvider'],
  },
}
```

### Custom Views

Replace or add admin views:

```typescript
admin: {
  components: {
    views: [
      {
        Component: '@/components/DashboardView',
        path: '/custom-dashboard',
      },
      // Replace the account view
      {
        Component: '@/components/AccountView',
        path: '/account',
        key: 'account',
      },
    ],
  },
}
```

## Collection Admin Options

### Default Columns

```typescript
admin: {
  defaultColumns: ['title', 'slug', 'updatedAt'],
}
```

### Live Preview

Configure live preview for collections:

```typescript
admin: {
  livePreview: {
    url: ({ data, req }) =>
      `${getServerSideURL()}/posts/${data?.slug}?preview=true`,
  },
}
```

Root-level live preview config with breakpoints:

```typescript
admin: {
  livePreview: {
    breakpoints: [
      { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
      { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
      { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
    ],
    // Collections and globals to enable live preview for
    collections: ['pages', 'posts'],
    globals: ['header'],
  },
}
```

### Collection-Level Components

Add custom components to collection views:

```typescript
admin: {
  components: {
    // Before/after the list view table
    beforeList: ['@/components/BeforePostsList'],
    afterList: ['@/components/AfterPostsList'],
    beforeListTable: ['@/components/FilterBar'],
    afterListTable: ['@/components/PaginationInfo'],
    // Before document controls
    beforeDocumentControls: ['@/components/DocumentActions'],
  },
}
```

### Custom Document Views

Replace the edit view for a collection:

```typescript
admin: {
  components: {
    views: {
      Edit: '@/components/CustomEditView',
    },
  },
}
```

### Custom Collection Views (New in 3.84)

Client components can now be used as custom collection views, enabling interactive list views with client-side state:

```typescript
import type { CollectionConfig } from 'payload'

export const Products: CollectionConfig = {
  slug: 'products',
  admin: {
    components: {
      views: {
        // Client component for custom list view
        List: '@/components/ProductsList/client',
      },
    },
  },
  fields: [
    { name: 'name', type: 'text' },
  ],
}
```

This allows building interactive Kanban boards, calendar views, or data table views with client-side sorting and filtering directly in the admin panel.

## Field Admin Options

All fields support admin configuration:

```typescript
{
  name: 'title',
  type: 'text',
  admin: {
    position: 'sidebar',           // 'main' or 'sidebar'
    width: '50%',                  // CSS width
    disabled: false,               // Make field non-editable in UI
    readOnly: false,               // Show but don't allow edits
    hidden: false,                 // Hide from admin entirely
    description: 'Enter the post title',
    condition: (data) => data.type === 'article',
    style: { backgroundColor: '#f0f0f0' },
    className: 'my-custom-class',
  },
}
```

### Custom Field Components

Replace how fields render in the admin:

```typescript
{
  name: 'customField',
  type: 'text',
  admin: {
    components: {
      // Replace the field input
      Field: '@/components/CustomFieldInput',
      // Replace the cell in list view
      Cell: '@/components/CustomCell',
      // Replace the filter component
      Filter: '@/components/CustomFilter',
      // Replace the description
      Description: '@/components/CustomDescription',
      // Replace the diff view
      Diff: '@/components/CustomDiff',
    },
  },
}
```

## Dashboard Widgets

Configure the admin dashboard with custom widgets:

```typescript
admin: {
  dashboard: {
    widgets: [
      {
        slug: 'recent-posts',
        Component: '@/widgets/RecentPosts',
        label: 'Recent Posts',
        minWidth: 'medium',
        maxWidth: 'large',
      },
    ],
    defaultLayout: [
      { widgetSlug: 'recent-posts', width: ['large'] },
    ],
  },
}
```

## Theme and Appearance

```typescript
admin: {
  // Restrict theme (default: 'all' — user can choose)
  theme: 'dark', // 'light' | 'dark' | 'all'

  // Date format for the admin panel
  dateFormat: 'yyyy/MM/dd',

  // Timezone configuration
  timezones: {
    defaultTimezone: 'America/New_York',
  },

  // Toast notification settings
  toast: {
    duration: 4000,
    position: 'bottom-right',
    limit: 5,
    expand: false,
  },
}
```

## Meta Configuration

Customize admin panel metadata:

```typescript
admin: {
  meta: {
    titleSuffix: ' - My CMS',
    ogImage: {
      url: '/og-image.png',
      width: 1200,
      height: 630,
      alt: 'My CMS',
    },
  },
}
```

## Custom Admin Routes

The admin panel uses Next.js routing. Key routes:

- `/admin` — Dashboard
- `/admin/login` — Login page
- `/admin/account` — User account
- `/admin/collections/:slug` — Collection list view
- `/admin/collections/:slug/create` — Create document
- `/admin/collections/:slug/:id` — Edit document
- `/admin/globals/:slug` — Global edit

Routes can be customized:

```typescript
admin: {
  routes: {
    account: '/my-account',
    login: '/sign-in',
    logout: '/sign-out',
    createFirstUser: '/setup',
  },
}
```

## AutoLogin for Development

```typescript
admin: {
  autoLogin: {
    email: 'dev@example.com',
    password: 'password123',
    prefillOnly: true, // Prefill credentials but require clicking login
  },
}
```

## Custom SCSS

Customize admin styles by editing `(payload)/custom.scss` in your Next.js app. Import Tailwind or custom CSS here.
