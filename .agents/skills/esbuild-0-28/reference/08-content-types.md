# Esbuild Content Types

## JavaScript (`.js`, `.cjs`, `.mjs`)

**Loader:** `js`

Default loader for `.js`, `.cjs`, and `.mjs` files. Supports all modern JavaScript syntax up to ES2024.

### Supported Syntax

All ECMAScript features are supported including:
- ES2015: Classes, modules, arrow functions, let/const
- ES2016: Exponentiation operator (`**`)
- ES2017: Async/await, trailing commas
- ES2018: Object rest/spread, async iteration
- ES2019: Optional catch binding
- ES2020: Optional chaining, nullish coalescing, BigInt, import.meta
- ES2021: Logical assignment operators
- ES2022: Class fields, private methods, static blocks
- ES2023: Hashbang grammar
- ES2024: RegExp set notation

### Syntax Transformation

Esbuild transforms syntax based on target:

```bash
# Transform to ES2015 (removes modern syntax)
esbuild app.js --target=es2015 --outfile=app.es5.js

# Keep modern syntax (default)
esbuild app.js --target=esnext --outfile=app.modern.js
```

**Transformed features:**
- `a ** b` → `Math.pow(a, b)` for targets below es2016
- `async/await` → generators for targets below es2017
- `a?.b` → conditional checks for targets below es2020
- Class fields → constructor assignments for targets below es2022

### Caveats

**ES5 not fully supported:** Setting `--target=es5` prevents new syntax from being introduced but doesn't transform ES6+ to ES5.

**Direct eval breaks bundling:**
```javascript
// Avoid this in bundled code
let y = 1
eval('y')  // Can access variables from other files!

// Use indirect eval instead
(0, eval)('console.log("safe")')
```

## TypeScript (`.ts`, `.tsx`, `.mts`, `.cts`)

**Loader:** `ts` or `tsx`

Strips type annotations without type checking. Esbuild is a transpiler, not a type checker.

### Supported Features

- Type annotations removed: `let x: number = 1` → `let x = 1`
- Interfaces and types removed entirely
- Enums converted to JavaScript objects
- Namespaces inlined
- Decorators transformed (legacy or standard)
- Type-only imports/exports handled correctly

### TypeScript Configuration

Esbuild reads `tsconfig.json` for:
- `experimentalDecorators`: Legacy vs standard decorator transform
- `useDefineForClassFields`: Class field semantics
- `jsx`, `jsxFactory`, `jsxFragmentFactory`: JSX configuration
- `baseUrl`, `paths`: Module resolution paths
- `extends`: Config inheritance

**Not supported:**
- Type checking (run `tsc --noEmit` separately)
- Declaration file generation (`.d.ts`)
- `emitDecoratorMetadata`

### Usage Example

```bash
# Transform TypeScript
esbuild app.ts --bundle --outfile=app.js

# With JSX support
esbuild app.tsx --bundle --outfile=app.js

# Specify tsconfig
esbuild app.ts --bundle --tsconfig=tsconfig.strict.json --outfile=app.js
```

### TypeScript Caveats

**Isolated modules:** Enable `isolatedModules` in tsconfig:
```json
{
  "compilerOptions": {
    "isolatedModules": true
  }
}
```

**esModuleInterop:** Recommended for ESM/CommonJS interop:
```json
{
  "compilerOptions": {
    "esModuleInterop": true
  }
}
```

## JSX (`.jsx`, `.tsx`)

**Loader:** `jsx` or `tsx`

Transforms JSX syntax to JavaScript function calls.

### Default Transform (React)

```jsx
// Input
import Button from './button'
const element = <Button className="primary">Click</Button>

// Output (jsx: 'transform')
import Button from './button'
const element = React.createElement(Button, { className: "primary" }, "Click")
```

### Automatic Runtime (React 17+)

```bash
esbuild app.jsx --bundle --jsx=automatic --outfile=app.js
```

```jsx
// Input
import { memo } from 'react'
const Component = () => <div>Hello</div>

// Output
import { jsx as _jsx } from "react/jsx-runtime"
const Component = () => _jsx("div", { children: "Hello" })
```

### Custom Factory

```bash
esbuild app.jsx --bundle \
  --jsx=transform \
  --jsx-factory=h \
  --jsx-fragment=Fragment \
  --outfile=app.js
```

For Preact, Vue, or other libraries.

### JSX in .js Files

Enable JSX for `.js` extension:

```bash
esbuild app.js --bundle --loader:.js=jsx --outfile=app.js
```

Or with JavaScript API:
```javascript
await esbuild.build({
  entryPoints: ['app.js'],
  loader: { '.js': 'jsx' },
})
```

### JSX Configuration Options

```bash
# Transform mode (default)
esbuild app.jsx --jsx=transform

# Preserve JSX (don't transform)
esbuild app.jsx --jsx=preserve

# Automatic runtime
esbuild app.jsx --jsx=automatic --jsx-import-source=react

# Development mode (add line numbers)
esbuild app.jsx --jsx-dev=true

# Custom fragment
esbuild app.jsx --jsx-fragment=Fragment
```

## JSON (`.json`)

**Loader:** `json`

Converts JSON to JavaScript object exports.

### Default Behavior

```json
// data.json
{
  "name": "example",
  "version": "1.0.0"
}
```

```javascript
// Import in code
import data from './data.json'
console.log(data.name)  // "example"
```

```javascript
// Output
export default {
  "name": "example",
  "version": "1.0.0"
};
```

### Usage

```bash
esbuild app.js --bundle --outfile=app.js
# JSON files automatically loaded with json loader
```

## CSS (`.css`)

**Loader:** `css`

Bundles CSS files and inlines them into JavaScript for browser use.

### Browser Bundling

```css
/* styles.css */
.container {
  display: flex;
  padding: 1rem;
}
```

```javascript
import './styles.css'
```

CSS is injected via `<style>` tags when bundle loads in browser.

### CSS Modules

Use CSS modules for scoped styles:

```bash
esbuild app.jsx --bundle --outfile=app.js
```

```jsx
// Component.jsx
import styles from './Component.module.css'

function Component() {
  return <div className={styles.container}>Hello</div>
}
```

```css
/* Component.module.css */
.container {
  display: flex;
  padding: 1rem;
}
```

```javascript
// Output
import _styles from "./Component.module.css"
function Component() {
  return React.createElement("div", { className: _styles.container }, "Hello")
}
// _styles.container = "container_abc123"
```

### CSS in Node.js

CSS is discarded by default for Node platform:

```bash
esbuild app.js --bundle --platform=node --outfile=app.js
# CSS imports removed
```

Preserve CSS files:
```bash
esbuild app.js --bundle \
  --platform=node \
  --loader:.css=copy \
  --outfile=app.js
```

### CSS Minification

```bash
esbuild app.css --minify --outfile=app.min.css
```

Or bundle with JS minification:
```bash
esbuild app.js --bundle --minify --outfile=app.js
# CSS is also minified
```

## Text Files (`.txt`, `.md`, etc.)

**Loader:** `text`

Loads file contents as a string.

### Usage

```bash
esbuild app.js --bundle --loader:.txt=text --outfile=app.js
```

```javascript
import readme from './README.txt'
console.log(readme)  // String contents of file
```

```javascript
// Output
const readme = "File contents here...";
```

### Common Use Cases

- Load template files
- Include documentation
- Embed configuration as strings

## Binary Files (`.png`, `.jpg`, etc.)

**Loader:** `binary`

Loads file as binary data (ArrayBuffer in Node, string in browser).

### Usage

```bash
esbuild app.js --bundle --loader:.png=binary --outfile=app.js
```

```javascript
import logo from './logo.png'
// logo is binary data
```

## Base64 Encoding (`.bin`, `.dat`)

**Loader:** `base64`

Encodes file contents as base64 string.

### Usage

```bash
esbuild app.js --bundle --loader:.bin=base64 --outfile=app.js
```

```javascript
import data from './data.bin'
// data is "base64-encoded-string"
```

Useful for embedding binary data in JavaScript.

## Data URL (`.woff`, `.ttf`)

**Loader:** `dataurl`

Converts file to data URL scheme.

### Usage

```bash
esbuild app.js --bundle --loader:.ttf=dataurl --outfile=app.js
```

```javascript
import font from './font.ttf'
// font is "data:application/font-ttf;base64,..."

// Use in CSS
const style = document.createElement('style')
style.textContent = `
  @font-face {
    font-family: 'CustomFont';
    src: url('${font}');
  }
`
```

Common for fonts and small assets.

## External Files (`.woff2`, custom)

**Loader:** `file`

Copies file to output directory and returns path.

### Usage

```bash
esbuild app.js --bundle \
  --loader:.woff2=file \
  --outdir=dist \
  --outfile=dist/app.js
```

```javascript
import font from './font.woff2'
// font is "/font.abc123.woff2" (path in output directory)
```

File is copied to output directory with hashed filename.

## Empty Files

**Loader:** `empty`

Produces empty output for any file.

### Usage

```bash
esbuild app.js --bundle --loader:.placeholder=empty --outfile=app.js
```

Useful for:
- Stubbing out optional dependencies
- Conditional feature loading
- Type-only imports

## Custom Loaders

Define custom file extensions:

### CLI

```bash
esbuild app.js --bundle \
  --loader:.custom=my-loader \
  --outfile=app.js
```

### JavaScript API

```javascript
await esbuild.build({
  entryPoints: ['app.js'],
  loader: {
    '.custom': 'text',  // Use built-in loader
  },
})
```

For truly custom loaders, use plugins (see Plugin Development guide).

## Loader Precedence

1. Explicit `--loader` flag overrides defaults
2. File extension determines default loader
3. Plugins can intercept before loader runs

### Default Loaders by Extension

| Extension | Loader |
|-----------|--------|
| `.js`, `.cjs`, `.mjs` | `js` |
| `.ts`, `.cts` | `ts` |
| `.tsx` | `tsx` |
| `.jsx` | `jsx` |
| `.json` | `json` |
| `.css` | `css` |
| `.txt`, `.html`, `.xml` | `text` |
| Unknown | Error (must specify loader) |

## Content-Type Caveats

### JavaScript/TypeScript

- Top-level await only works with `--format=esm`
- Private fields (`#field`) use WeakMap transform (performance impact)
- `toString()` on functions not preserved after bundling

### CSS

- Only subset of CSS features supported (no custom properties in all contexts)
- CSS imports must be side-effect-free for tree shaking
- URL() paths rewritten relative to output

### JSON

- Must be valid JSON (no comments, trailing commas)
- Use `--loader:.json=text` to load as string instead

### Binary/Base64/DataURL

- Large files increase bundle size significantly
- Consider using `file` loader for assets > 10KB
- Browser may have limits on data URL sizes
