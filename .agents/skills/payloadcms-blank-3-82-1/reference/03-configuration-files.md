# Configuration Files

## payload.config.ts

The main Payload configuration file. It defines the admin panel settings, collections, database adapter, editor, and plugins.

```ts
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { buildConfig } from 'payload'
import { fileURLToPath } from 'url'
import sharp from 'sharp'

import { Users } from './collections/Users'
import { Media } from './collections/Media'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: Users.slug,
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Media],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URL || '',
  }),
  sharp,
  plugins: [],
})
```

Configuration sections:

- **`admin`** — admin panel settings. `user` specifies which collection handles authentication. `importMap.baseDir` sets the base directory for the admin import map, used for custom React components.
- **`collections`** — array of all collection configurations. Order does not matter.
- **`editor`** — rich-text editor configuration. `lexicalEditor()` enables the Lexical editor with default features. Accepts options for plugins, features, and node overrides.
- **`secret`** — encryption secret for cookies and authentication tokens. Must be set via `PAYLOAD_SECRET` environment variable in production.
- **`typescript`** — TypeScript generation settings. `outputFile` specifies where generated types are written.
- **`db`** — database adapter configuration. The blank template uses MongoDB via `mongooseAdapter`.
- **`sharp`** — image processing library for media uploads.
- **`plugins`** — array of Payload plugins. Empty by default in the blank template.

### Lexical Editor Configuration

The Lexical editor can be customized with features and nodes:

```ts
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import {
  boldPlugin,
  italicPlugin,
  headingPlugin,
  linkPlugin,
} from '@payloadcms/richtext-lexical/plugins'

editor: lexicalEditor({
  features: () => [
    boldPlugin(),
    italicPlugin(),
    headingPlugin({
      enabledHeadings: ['h1', 'h2', 'h3', 'h4'],
      defaultHeadingLevel: 'h2',
    }),
    linkPlugin({
      collections: {
        link: {
          fields: [
            // custom link fields
          ],
        },
      },
    }),
  ],
}),
```

## next.config.ts

The Next.js configuration is wrapped with Payload's `withPayload` helper, which bundles server packages and configures the admin panel correctly.

```ts
import { withPayload } from '@payloadcms/next/withPayload'
import type { NextConfig } from 'next'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(__filename)

const nextConfig: NextConfig = {
  images: {
    localPatterns: [
      {
        pathname: '/api/media/file/**',
      },
    ],
  },
  webpack: (webpackConfig) => {
    webpackConfig.resolve.extensionAlias = {
      '.cjs': ['.cts', '.cjs'],
      '.js': ['.ts', '.tsx', '.js', '.jsx'],
      '.mjs': ['.mts', '.mjs'],
    }
    return webpackConfig
  },
  turbopack: {
    root: path.resolve(dirname),
  },
}

export default withPayload(nextConfig, { devBundleServerPackages: false })
```

Key settings:

- **`images.localPatterns`** — allows Next.js `<Image>` component to serve images from Payload's media API endpoint
- **`webpack.extensionAlias`** — resolves `.js` imports to `.ts`/`.tsx` files for TypeScript support
- **`turbopack.root`** — sets the root directory for Turbopack (Next.js's experimental bundler)
- **`withPayload()`** — wraps the config to enable Payload-specific Next.js behavior. `devBundleServerPackages: false` avoids bundling server packages in development for faster builds

## tsconfig.json

TypeScript configuration with Path aliases for clean imports:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "strict": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "target": "ES2022",
    "paths": {
      "@/*": ["./src/*"],
      "@payload-config": ["./src/payload.config.ts"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

Path aliases:

- `@/*` maps to `./src/*` — use `import config from '@/payload.config'` instead of relative paths
- `@payload-config` maps directly to the Payload config file — used by Payload internals and the admin layout

## Environment Variables

The blank template requires two environment variables (see `.env.example`):

- **`DATABASE_URL`** — MongoDB connection string. Local development: `mongodb://127.0.0.1/your-database-name`. Docker compose: `mongodb://mongo/your-database-name` (hostname matches the service name).
- **`PAYLOAD_SECRET`** — random string used for signing JWT tokens and encrypting cookies. Generate with any secure random string generator. Must be at least 32 characters in production.

Example `.env`:

```
DATABASE_URL=mongodb://127.0.0.1/my-project
PAYLOAD_SECRET=a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5
```
