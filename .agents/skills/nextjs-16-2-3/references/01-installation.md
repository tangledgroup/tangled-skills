# Installation and Setup Guide

## System Requirements

Before installing Next.js 16.2.3, ensure your development environment meets these requirements:

### Node.js Version
- **Minimum:** Node.js 20.9 or higher
- **Recommended:** Latest LTS version (20.x or 22.x)

Check your Node.js version:
```bash
node --version
# Should output: v20.9.0 or higher
```

### Operating Systems
Next.js supports:
- **macOS** (10.15+)
- **Windows** (10+, including WSL 2)
- **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+)

### Supported Browsers
Next.js supports modern browsers with zero configuration:
- Chrome 111+
- Edge 111+
- Firefox 111+
- Safari 16.4+

For older browser support, configure polyfills in `next.config.js`.

## Installation Methods

### Method 1: create-next-app CLI (Recommended)

The quickest way to start a new Next.js project:

**With npm:**
```bash
npx create-next-app@latest my-app --yes
cd my-app
npm run dev
```

**With pnpm:**
```bash
pnpm create next-app@latest my-app --yes
cd my-app
pnpm dev
```

**With yarn:**
```bash
yarn create next-app@latest my-app --yes
cd my-app
yarn dev
```

**With bun:**
```bash
bun create next-app@latest my-app --yes
cd my-app
bun dev
```

### Understanding the `--yes` Flag

Using `--yes` skips all prompts and applies recommended defaults:
- ✅ TypeScript enabled
- ✅ ESLint for linting
- ✅ Tailwind CSS for styling
- ✅ App Router (recommended)
- ✅ Turbopack for faster builds
- ✅ Import alias `@/*` for cleaner imports
- ✅ `AGENTS.md` file for coding agents

### Interactive Installation

Run without `--yes` to customize:

```bash
npx create-next-app@latest my-app
```

**Prompts you'll encounter:**

1. **Project name:**
   ```
   What is your project named? my-app
   ```

2. **Use TypeScript?**
   ```
   Would you like to use TypeScript? No / Yes
   ```
   **Recommendation:** Yes - provides type safety and better DX

3. **Choose ESLint or Biome:**
   ```
   Which linter would you like to use? ESLint / Biome / None
   ```
   **Recommendation:** ESLint (more ecosystem support) or Biome (faster)

4. **Use React Compiler?**
   ```
   Would you like to use React Compiler? No / Yes
   ```
   **Recommendation:** Yes for production apps (automatic memoization)

5. **Use Tailwind CSS?**
   ```
   Would you like to use Tailwind CSS? No / Yes
   ```
   **Recommendation:** Yes for rapid UI development

6. **Use App Router?**
   ```
   Would you like to use the App Router? No / Yes
   ```
   **Recommendation:** Yes for new projects (Server Components, better performance)

7. **Import alias:**
   ```
   What import alias would you like configured? @/* or custom
   ```
   **Recommendation:** `@/*` (standard convention)

## Manual Installation

For existing projects or custom setups:

### 1. Create Project Directory

```bash
mkdir my-app
cd my-app
npm init -y
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install next@16.2.3 react@19 react-dom@19

# Development dependencies
npm install -D typescript @types/node @types/react @types/react-dom
npm install -D eslint eslint-config-next
```

### 3. Initialize TypeScript

```bash
npx tsc --init
```

Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 4. Create Basic Structure

```bash
mkdir app public
touch app/page.tsx app/layout.tsx
```

### 5. Configure Package Scripts

Update `package.json`:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

## Adding Tailwind CSS (Optional)

If you didn't select Tailwind during setup:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Configure `tailwind.config.ts`:
```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

export default config
```

Add to `app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## App Router vs Pages Router

### App Router (Recommended for New Projects)

**Location:** `app/` directory

**Features:**
- React Server Components by default
- Nested layouts
- Loading states (`loading.tsx`)
- Error boundaries (`error.tsx`)
- Route handlers (`route.ts`)
- Metadata API
- Better performance with streaming

**Use when:**
- Starting a new project
- Needing Server Components
- Wanting nested layouts
- Building complex applications

### Pages Router (Legacy, Still Supported)

**Location:** `pages/` directory

**Features:**
- Client-side rendering by default
- `getServerSideProps`, `getStaticProps` for data fetching
- API routes in `pages/api/`
- Mature ecosystem

**Use when:**
- Maintaining existing projects
- Needing specific third-party libraries
- Simpler applications without nested layouts

## Development Server

Start the development server:

```bash
# Using npm
npm run dev

# Using pnpm
pnpm dev

# Using yarn
yarn dev

# Using bun
bun dev
```

The server will start at `http://localhost:3000` by default.

**Dev server features:**
- Fast Refresh (Turbopack or SWC)
- Hot module replacement
- TypeScript checking
- ESLint integration

## Build and Production

### Build for Production

```bash
npm run build
```

This creates an optimized production build in `.next/` directory.

### Start Production Server

```bash
npm start
```

Runs the production server at `http://localhost:3000`.

### Environment Variables

**Server-side only:**
```env
DATABASE_URL=postgresql://user:pass@localhost/db
API_SECRET=your-secret-key
```

**Client and server:**
```env
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_APP_NAME=MyApp
```

Access in code:
```tsx
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

## IDE Setup

### VS Code Recommendations

Install these extensions:
- **ESLint** (dbaeumer.vscode-eslint)
- **Prettier** (esbenp.prettier-vscode)
- **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
- **TypeScript and JavaScript Language Features** (built-in)

**.vscode/settings.json:**
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": ["typescript", "typescriptreact"]
}
```

### WebStorm

WebStorm has built-in Next.js support:
- Enable "Next.js" in File → Settings → Languages & Frameworks
- Configure Node.js interpreter
- Run/Debug configurations auto-detected

## Troubleshooting Installation

### "command not found: next"

Ensure node_modules is installed:
```bash
npm install
```

### TypeScript errors on import

Clear cache and restart:
```bash
rm -rf .next node_modules/.cache
npm run dev
```

### Port 3000 already in use

Change port:
```bash
npx next dev -p 3001
```

Or in `package.json`:
```json
{
  "scripts": {
    "dev": "next dev -p 3001"
  }
}
```

### Node version too old

Update Node.js using nvm:
```bash
nvm install 20
nvm use 20
```

Or download from https://nodejs.org/

## Next Steps

After installation:
1. Start dev server: `npm run dev`
2. Visit http://localhost:3000
3. Edit `app/page.tsx` to see changes
4. Explore [Project Structure](references/02-project-structure.md)
5. Learn about [Server and Client Components](references/03-server-client-components.md)
