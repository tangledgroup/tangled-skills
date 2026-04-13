# Bun Bundler

Bun's bundler is a fast, esbuild-compatible build tool that bundles JavaScript, TypeScript, JSX, CSS, and more. It supports hot module replacement (HMR), single-file executable generation, and bytecode compilation.

## Basic Usage

### CLI Commands

```bash
# Basic bundle
bun build ./index.tsx --outdir ./dist

# Multiple entrypoints
bun build ./src/index.tsx ./src/admin.tsx --outdir ./dist

# With sourcemaps
bun build ./index.tsx --outdir ./dist --sourcemap

# Minified production build
bun build ./index.tsx --outdir ./dist --minify

# Watch mode for development
bun build ./index.tsx --outdir ./dist --watch

# Target browser environment
bun build ./index.tsx --target browser --outdir ./dist

# Target Node.js environment
bun build ./index.tsx --target node --outdir ./dist

# Generate single-file executable
bun build ./server.ts --compile --outfile ./server-binary
```

### JavaScript API

```typescript title="build.ts"
const res = await Bun.build({
  entrypoints: ['./src/index.tsx', './src/admin.tsx'],
  outdir: './dist',
  minify: true,
  sourcemap: 'external',
  target: 'browser', // 'browser' | 'bun' | 'node'
  format: 'esm', // 'esm' | 'cjs' | 'iife'
});

if (res.success) {
  console.log('Build succeeded');
} else {
  console.error('Build failed:', res.errors);
}
```

## Configuration Options

### Entrypoints

Specify input files to bundle:

```typescript
await Bun.build({
  entrypoints: [
    './src/index.tsx',           // Absolute or relative path
    './src/admin.tsx',           // Multiple entrypoints
    './src/styles.css',          // CSS files
    './worker.ts',               // Web workers
  ],
});
```

### Output Directory

```typescript
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  outdir: './dist',              // Output directory (created if doesn't exist)
  
  // Or specify individual output files
  outfile: './dist/bundle.js',   // Single output file
});
```

### Build Targets

Specify the runtime environment:

```typescript
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  target: 'browser',  // Browser environment (default)
  // target: 'bun',    // Bun runtime
  // target: 'node',   // Node.js runtime
});
```

Target-specific behaviors:
- **browser**: Polyfills Node.js globals, inlines assets
- **bun**: Optimizes for Bun runtime, no polyfills needed
- **node**: Generates CommonJS by default, includes Node.js built-ins

### Output Formats

```typescript
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  format: 'esm',   // ES modules (default)
  // format: 'cjs',  // CommonJS (experimental)
  // format: 'iife', // IIFE wrapper (experimental, for <script> tags)
});
```

### Minification

```typescript
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  minify: true,              // Enable all minifications
  
  // Or fine-grained control
  minify: false,
  minifySyntax: true,        // Minify syntax (remove whitespace)
  minifyWhitespace: true,    // Remove whitespace
  minifyNames: true,         // Rename variables/functions
});
```

### Sourcemaps

```typescript
await Bun.build({
  entrypoints: ['./src/index.tsx'],
  sourcemap: false,          // No sourcemaps (default)
  // sourcemap: true,        // Inline sourcemaps
  // sourcemap: 'external',  // Separate .map files
  // sourcemap: 'inline',    // Base64 encoded in output
});
```

## Hot Module Replacement (HMR)

Development server with instant updates:

```bash
# Start dev server with HMR
bun build ./src/index.tsx --outdir ./dist --watch

# With custom port for HMR
bun build ./src/index.tsx --watch --hmr-port=1234
```

### JavaScript API with Watch Mode

```typescript title="dev-server.ts"
const { stdout } = await Bun.build({
  entrypoints: ['./src/index.tsx'],
  outdir: './dist',
  watch: true,
  hot: true,  // Enable HMR
});

console.log('Watching for changes...');
```

### HMR in Browser

Include HMR client in your HTML:

```html title="index.html"
<!DOCTYPE html>
<html>
<head>
  <script src="/__hmr__.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/index.tsx"></script>
</body>
</html>
```

## Single-File Executables

Compile TypeScript/JavaScript into standalone binaries:

```bash
# Create executable from TypeScript
bun build ./server.ts --compile --outfile ./my-server

# With specific target architecture
bun build ./app.ts --compile --target x64 --outfile ./app-x64

# Cross-compile for different platforms
bun build ./tool.ts --compile --target wasm32 --outfile ./tool-wasm

# Include all dependencies
bun build ./app.ts --compile --embed --outfile ./app-standalone
```

### Executable Options

```bash
# Specify entry function (for libraries)
bun build ./lib.ts --compile --main-function processInput --outfile ./processor

# Add shebang for Unix executables
bun build ./cli.ts --compile --shebang --outfile ./my-cli

# Strip debug symbols (smaller binary)
bun build ./app.ts --compile --strip --outfile ./app-release
```

### Platform Targets

```bash
# Linux x64
bun build ./app.ts --compile --target x64 --outfile ./app-linux

# macOS ARM64 (Apple Silicon)
bun build ./app.ts --compile --target aarch64 --outfile ./app-macos-arm

# Windows x64
bun build ./app.ts --compile --target x64-windows --outfile ./app.exe

# WebAssembly
bun build ./app.ts --compile --target wasm32 --outfile ./app.wasm
```

## CSS Support

### Basic CSS Bundling

```bash
# Bundle with CSS
bun build ./src/index.tsx --outdir ./dist
```

CSS files are automatically inlined or extracted:

```typescript title="index.tsx"
import './styles.css';        // Auto-imported
import styles from './module.css';  // CSS modules
```

### CSS Modules

```css title="Button.module.css"
.button {
  color: blue;
  padding: 10px 20px;
}
```

```typescript title="Button.tsx"
import styles from './Button.module.css';

function Button() {
  return <button className={styles.button}>Click me</button>;
}
```

Generated classes are scoped and hashed.

### PostCSS Integration

Create `postcss.config.js`:

```javascript title="postcss.config.js"
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

Bun automatically detects and uses PostCSS configuration.

## Asset Handling

### Image Assets

```typescript title="App.tsx"
import logo from './logo.png';      // URL to bundled asset
import icon from './icon.svg';

function App() {
  return <img src={logo} alt="Logo" />;
}
```

Assets are hashed and cached: `/assets/logo.abc123.png`

### Font Files

```typescript title="styles.css"
@font-face {
  font-family: 'CustomFont';
  src: url('./fonts/custom.woff2') format('woff2');
}
```

Fonts are bundled and served with proper MIME types.

### Data URLs

Embed small files as data URLs:

```typescript title="bunfig.toml"
[build]
# Inline assets under 4KB as data URLs
assetLimit = 4096
```

## Full-Stack Applications

Build both server and client in one command:

```bash
# Build full-stack app
bun build ./src/server.tsx ./src/client.tsx --outdir ./dist

# Server entrypoint (Node.js target)
bun build ./server.ts --target node --outdir ./dist/server

# Client entrypoint (browser target)
bun build ./client.tsx --target browser --outdir ./dist/client
```

### HTML Import

Bundle entire app including HTML:

```bash
# Build with HTML entrypoint
bun build ./index.html --outdir ./dist --public-dir ./public
```

```html title="index.html"
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>My App</title>
</head>
<body>
  <div id="root"></div>
  <!-- Bun injects bundled scripts here -->
</body>
</html>
```

## Bytecode Compilation

Compile to bytecode for faster startup:

```bash
# Build with bytecode
bun build ./app.ts --bytecode --outdir ./dist

# Run bytecode directly (faster than interpreting .js)
bun run ./dist/app.js
```

Bytecode benefits:
- 2-5x faster startup time
- Smaller file sizes
- Obfuscation (harder to reverse engineer)

## Tree Shaking

Automatic dead code elimination:

```bash
# Enable tree shaking (default in production builds)
bun build ./src/index.tsx --minify --outdir ./dist
```

Ensure ES module syntax for best results:

```typescript
// Good: Tree-shakable
export function used() { return 1; }
export function unused() { return 2; }

// Bad: Not tree-shakable
const lib = { used: () => 1, unused: () => 2 };
export default lib;
```

## Plugins

Extend bundler with custom plugins:

```typescript title="plugin.ts"
const myPlugin = {
  name: 'my-plugin',
  
  // Transform code before bundling
  async transform(path, content) {
    if (path.endsWith('.custom')) {
      return {
        content: `export default "${content}"`,
        type: 'js',
      };
    }
  },
  
  // Resolve custom imports
  resolve(importer, imported) {
    if (imported.startsWith('custom:')) {
      return { path: './custom-handler.js' };
    }
  },
};

await Bun.build({
  entrypoints: ['./src/index.ts'],
  plugins: [myPlugin],
});
```

### Plugin Hooks

Available plugin hooks:
- `resolve(importer, imported)` - Resolve module paths
- `load(path)` - Load file content
- `transform(path, content)` - Transform code
- `onLoad(filters, options)` - Handle specific file types
- `onResolve(options, specifiers)` - Intercept imports

## Macros

Code transformations at build time:

```typescript title="src/index.ts"
import { macro } from 'some-macro';

// Macro transforms code during build
const result = macro`template literal`;
```

Create custom macros:

```typescript title="macro-plugin.ts"
export default {
  name: 'custom-macro',
  macros: {
    'version': () => `'${process.env.npm_package_version}'`,
    'env': () => `'${process.env.NODE_ENV}'`,
  },
};
```

## Migration from esbuild

Bun's bundler is esbuild-compatible:

```bash
# esbuild command
esbuild src/index.tsx --bundle --outdir=dist --minify

# Equivalent Bun command
bun build src/index.tsx --outdir dist --minify
```

### Configuration Mapping

| esbuild | Bun |
|---------|-----|
| `--bundle` | (default) |
| `--outdir=dist` | `--outdir ./dist` |
| `--minify` | `--minify` |
| `--sourcemap` | `--sourcemap` |
| `--watch` | `--watch` |
| `--target=browser` | `--target browser` |
| `--format=esm` | `--format esm` |
| `--platform=browser` | `--target browser` |

## Performance Tips

1. **Use bytecode compilation** for production: `--bytecode`
2. **Enable minification** for smaller bundles: `--minify`
3. **Use watch mode** in development: `--watch`
4. **Split code with dynamic imports**: `import('./module')`
5. **Exclude dev-only code** from production builds
6. **Use CSS modules** instead of global CSS for better tree shaking

## Common Patterns

### Library Build

```bash
# Build library for distribution
bun build ./src/index.ts --target bun --format esm --outdir ./dist

# Also build CommonJS version
bun build ./src/index.ts --target node --format cjs --outdir ./dist/cjs
```

### Web Application

```bash
# Development with HMR
bun build ./src/index.tsx --watch --hmr

# Production build
bun build ./src/index.tsx --minify --sourcemap --outdir ./dist
```

### CLI Tool

```bash
# Create standalone executable
bun build ./cli.ts --compile --shebang --outfile ./my-cli

# Make executable
chmod +x ./my-cli

# Run directly
./my-cli --help
```

### Server Application

```bash
# Build server with dependencies
bun build ./server.ts --target node --outdir ./dist

# Or create single binary
bun build ./server.ts --compile --outfile ./server-binary
```

## Troubleshooting

### Common Issues

**Module not found**: Check import paths and ensure files exist:
```bash
bun build --verbose ./index.ts
```

**CSS not loading**: Ensure CSS is imported in entrypoint:
```typescript
import './styles.css';  // Add to main entry file
```

**HMR not working**: Check browser console for HMR client errors, ensure `--hmr` flag is set.

**Large bundle size**: Enable minification and tree shaking:
```bash
bun build --minify --sourcemap ./index.tsx
```

**TypeScript errors**: Ensure `tsconfig.json` is valid or use `--bun` flag.

## Advanced Configuration

### bunfig.toml Build Options

```toml title="bunfig.toml"
[build]
# Output settings
outdir = "./dist"
minify = false
sourcemap = false

# Target settings
target = "browser"  # "browser" | "bun" | "node"
format = "esm"      # "esm" | "cjs" | "iife"

# Advanced options
loader = { ".png" = "file", ".jpg" = "file" }
define = { "process.env.API_URL" = '"https://api.example.com"' }
external = ["lodash"]  # Don't bundle these packages
```

### Define Replacements

Replace values at build time:

```bash
# Replace process.env variables
bun build ./index.ts --define process.env.API_URL='"https://api.example.com"'

# Replace __VERSION__ globally
bun build ./index.ts --define __VERSION__='"1.0.0"'
```

### External Dependencies

Exclude packages from bundle:

```bash
# Don't bundle lodash (assume available at runtime)
bun build ./index.ts --external lodash --external axios

# Or in bunfig.toml
```

```toml
[build]
external = ["lodash", "axios", "@aws-sdk/*"]
```
