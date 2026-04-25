# Custom Components

This reference documents how to customize the Payload admin panel with React components. The blank template uses `@payloadcms/ui` components and supports full customization through component overrides, custom cells, lists, graphs, and form fields.

## Import Map System

Payload uses an import map for component lazy loading in the admin panel. After creating custom components, regenerate the import map:

```bash
pnpm run generate:importmap
```

This creates/updates `src/app/(payload)/admin/importMap.tsx`.

## Admin Component Types

### Field Components

Customize how fields render in the admin panel:

```typescript
// src/components/admin/CustomTextField.tsx
import React from 'react'
import { TextField } from '@payloadcms/ui/fields'

export const CustomTextField = (props) => {
  return (
    <TextField {...props}>
      <TextField.Label />
      <TextField.Control 
        placeholder="Enter custom text"
      />
      <TextField.Description>
        This is a custom description
      </TextField.Description>
    </TextField>
  )
}
```

Usage in collection:

```typescript
{
  name: 'customField',
  type: 'text',
  admin: {
    components: {
      Field: '@/components/admin/CustomTextField',
    },
  },
}
```

### Cell Components (List View)

Customize how documents appear in list views:

```typescript
// src/components/admin/StatusCell.tsx
import React from 'react'

export const StatusCell = ({ value }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return '#22c55e' // green
      case 'draft': return '#f59e0b'     // amber
      case 'archived': return '#64748b'  // slate
      default: return '#3b82f6'          // blue
    }
  }

  return (
    <div style={{
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '9999px',
      backgroundColor: getStatusColor(value),
      color: 'white',
      fontSize: '12px',
      fontWeight: 500,
      textTransform: 'capitalize',
    }}>
      {value}
    </div>
  )
}
```

Usage in collection:

```typescript
{
  name: 'status',
  type: 'select',
  admin: {
    components: {
      Cell: '@/components/admin/StatusCell',
    },
  },
}
```

### Before/After Input Components

Add custom UI around fields:

```typescript
// src/components/admin/BeforeTitleInput.tsx
import React from 'react'

export const BeforeTitleInput = () => {
  return (
    <div style={{ marginBottom: '8px', fontSize: '14px', color: '#64748b' }}>
      <strong>Tip:</strong> Titles should be descriptive and under 60 characters for SEO.
    </div>
  )
}
```

Usage:

```typescript
{
  name: 'title',
  type: 'text',
  admin: {
    components: {
      BeforeInput: '@/components/admin/BeforeTitleInput',
    },
  },
}
```

### Custom List Components

Replace entire list views for collections:

```typescript
// src/components/admin/PostsList.tsx
import React, { useState } from 'react'
import { useNavigate } from '@payloadcms/ui'

export const PostsList = () => {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '20px', display: 'flex', gap: '16px' }}>
        <input
          type="text"
          placeholder="Search posts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #e2e8f0',
            borderRadius: '6px',
            width: '300px',
          }}
        />
        <button
          onClick={() => navigate('/admin/posts/new')}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          New Post
        </button>
      </div>
      
      {/* Custom table or grid view */}
      <div>Your custom list implementation</div>
    </div>
  )
}
```

Usage in collection:

```typescript
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    components: {
      List: '@/components/admin/PostsList',
    },
  },
  fields: [/* ... */],
}
```

## Graph Components

Customize analytics graphs in collection views:

```typescript
// src/components/admin/PostsGraph.tsx
import React from 'react'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export const PostsGraph = ({ data }) => {
  // data contains aggregated document data
  
  const chartData = {
    labels: data?.map(item => item.label) || [],
    datasets: [
      {
        label: 'Posts Created',
        data: data?.map(item => item.value) || [],
        backgroundColor: '#3b82f6',
      },
    ],
  }

  return (
    <div style={{ height: '300px' }}>
      <Bar data={chartData} />
    </div>
  )
}
```

Usage:

```typescript
admin: {
  components: {
    graph: '@/components/admin/PostsGraph',
  },
}
```

## Form Components

### Custom Field Types

Create entirely new field types:

```typescript
// src/components/admin/ColorPickerField.tsx
import React, { useState } from 'react'

export const ColorPickerField = ({ value, onChange, path }) => {
  const [selectedColor, setSelectedColor] = useState(value || '#000000')

  const handleChange = (e) => {
    const newColor = e.target.value
    setSelectedColor(newColor)
    onChange(path, newColor)
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <input
        type="color"
        value={selectedColor}
        onChange={handleChange}
        style={{ width: '50px', height: '50px', border: 'none', cursor: 'pointer' }}
      />
      <input
        type="text"
        value={selectedColor}
        onChange={handleChange}
        style={{
          flex: 1,
          padding: '8px',
          border: '1px solid #e2e8f0',
          borderRadius: '4px',
          fontFamily: 'monospace',
        }}
      />
    </div>
  )
}
```

Usage with custom field type requires plugin development. For simple cases, use `richText` or `code` fields.

### Rich Text Custom Components

Extend Lexical editor with custom blocks:

```typescript
// src/components/admin/CalloutBlock.tsx
import React from 'react'
import { Block } from '@payloadcms/richtext-lexical'

export const CalloutBlock = () => {
  return Block({
    slug: 'callout',
    labels: {
      singular: 'Callout',
      plural: 'Callouts',
    },
    fields: [
      {
        name: 'type',
        type: 'select',
        options: [
          { label: 'Info', value: 'info' },
          { label: 'Warning', value: 'warning' },
          { label: 'Error', value: 'error' },
          { label: 'Success', value: 'success' },
        ],
        defaultValue: 'info',
      },
      {
        name: 'content',
        type: 'richText',
      },
    ],
  })
}
```

Register in editor config:

```typescript
// payload.config.ts
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import { CalloutBlock } from './components/admin/CalloutBlock'

export default buildConfig({
  editor: lexicalEditor({
    features: () => [
      // ... other features
      CalloutBlock(),
    ],
  }),
  // ... other config
})
```

## Dashboard Components

Customize the admin dashboard:

```typescript
// src/components/admin/Dashboard.tsx
import React from 'react'

export const Dashboard = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1>Welcome to the Admin Panel</h1>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginTop: '24px',
      }}>
        <div style={{
          padding: '20px',
          backgroundColor: '#f8fafc',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
        }}>
          <h3 style={{ margin: '0 0 8px 0' }}>Quick Actions</h3>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li><a href="/admin/posts/new">Create New Post</a></li>
            <li><a href="/admin/media/new">Upload Media</a></li>
            <li><a href="/admin/users">Manage Users</a></li>
          </ul>
        </div>
        
        <div style={{
          padding: '20px',
          backgroundColor: '#f8fafc',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
        }}>
          <h3 style={{ margin: '0 0 8px 0' }}>Resources</h3>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li><a href="https://payloadcms.com/docs" target="_blank">Documentation</a></li>
            <li><a href="https://discord.com/invite/payload" target="_blank">Community</a></li>
          </ul>
        </div>
      </div>
    </div>
  )
}
```

Register in config:

```typescript
export default buildConfig({
  admin: {
    components: {
      Dashboard: '@/components/admin/Dashboard',
    },
  },
  // ... other config
})
```

## Login/Register Components

Customize authentication screens:

```typescript
// src/components/admin/Login.tsx
import React from 'react'
import { LoginForm } from '@payloadcms/ui'

export const CustomLogin = () => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        padding: '32px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
      }}>
        <h1 style={{ textAlign: 'center', marginBottom: '24px' }}>
          Admin Login
        </h1>
        <LoginForm />
      </div>
    </div>
  )
}
```

Register in config:

```typescript
admin: {
  components: {
    Login: '@/components/admin/CustomLogin',
  },
}
```

## Navigation Customization

### Custom Menu Items

```typescript
// src/components/admin/NavLinks.tsx
import React from 'react'

export const NavLinks = () => {
  return (
    <>
      <a href="/admin/custom-reports" style={{
        display: 'block',
        padding: '8px 16px',
        color: '#3b82f6',
        textDecoration: 'none',
      }}>
        Custom Reports
      </a>
      <a href="/admin/settings" style={{
        display: 'block',
        padding: '8px 16px',
        color: '#3b82f6',
        textDecoration: 'none',
      }}>
        Settings
      </a>
    </>
  )
}
```

## Styling the Admin Panel

### Custom SCSS

The blank template includes `src/app/(payload)/custom.scss` for admin styling:

```scss
// src/app/(payload)/custom.scss

// Override Payload CSS variables
:root {
  --font-primary: 'Inter', system-ui, -apple-system, sans-serif;
  --color-focus-ring: rgb(59 130 246 / 0.5);
}

// Custom styles for admin panel
.payload-sidebar {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}

.document-header {
  border-bottom: 2px solid #3b82f6;
}

// Custom button styles
.btn {
  &.primary {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    transition: all 0.2s ease;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgb(59 130 246 / 0.4);
    }
  }
}

// List view customizations
.table-row {
  &:hover {
    background-color: rgb(59 130 246 / 0.1);
  }
}
```

### Dark Mode Support

```scss
// Add dark mode variants
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0f172a;
    --text-primary: #f8fafc;
    --border-color: #334155;
  }
}

// Or force dark mode
.payload-admin {
  background-color: #0f172a;
  color: #f8fafc;
  
  .card {
    background-color: #1e293b;
    border-color: #334155;
  }
}
```

## Component Best Practices

### TypeScript Types

Always type your components:

```typescript
import React from 'react'
import type { FieldProps, CellProps } from '@payloadcms/ui'

type CustomFieldProps = FieldProps & {
  customProp?: string
}

export const CustomField = (props: CustomFieldProps) => {
  const { value, onChange, path } = props
  
  // Component implementation
  return <div>{value}</div>
}
```

### Error Boundaries

Wrap custom components with error boundaries:

```typescript
// src/components/admin/ErrorBoundary.tsx
import React from 'react'

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', backgroundColor: '#fee2e2', borderRadius: '8px' }}>
          <h3>Something went wrong</h3>
          <p>Please refresh the page or contact support.</p>
        </div>
      )
    }

    return this.props.children
  }
}
```

### Lazy Loading

Use dynamic imports for large components:

```typescript
import dynamic from 'next/dynamic'

const HeavyGraphComponent = dynamic(
  () => import('@/components/admin/HeavyGraph'),
  { loading: () => <div>Loading...</div> }
)
```

## Common Patterns

### Rich Text with Custom UI

```typescript
// src/components/admin/EnhancedRichText.tsx
import React from 'react'
import { RichTextField } from '@payloadcms/ui/fields'

export const EnhancedRichText = (props) => {
  return (
    <div>
      <RichTextField {...props} />
      
      {/* Custom toolbar below editor */}
      <div style={{
        marginTop: '12px',
        padding: '12px',
        backgroundColor: '#f8fafc',
        borderRadius: '6px',
      }}>
        <h4 style={{ margin: '0 0 8px 0' }}>Formatting Tips</h4>
        <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px' }}>
          <li>Use H1 for page titles only</li>
          <li>Keep paragraphs under 200 words</li>
          <li>Add alt text to all images</li>
        </ul>
      </div>
    </div>
  )
}
```

### Conditional Field Display

```typescript
// src/components/admin/ConditionalField.tsx
import React from 'react'

export const ConditionalField = ({ value, siblingData, path }) => {
  const showAdvancedOptions = siblingData?.type === 'advanced'

  return (
    <div>
      <BasicField value={value} onChange={(val) => update(path, val)} />
      
      {showAdvancedOptions && (
        <AdvancedOptions 
          value={value} 
          onChange={(val) => update(path, val)} 
        />
      )}
    </div>
  )
}
```

See [API Integration](05-api-integration.md) for programmatic admin operations.
