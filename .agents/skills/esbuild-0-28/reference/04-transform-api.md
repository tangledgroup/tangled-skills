# Esbuild Transform API

## Overview

The transform API processes a single file in isolation without file system access. Ideal for:
- Transforming TypeScript to JavaScript
- Minifying code snippets
- Processing code from stdin or in-memory strings
- IDE plugins and linting tools

## CLI Transform

### Basic Transformation

```bash
# Transform TypeScript to JavaScript
echo 'let x: number = 1' | esbuild --loader=ts
# Output: let x = 1;

# Minify JavaScript
echo 'function add(a, b) { return a + b }' | esbuild --minify
# Output: function add(a,b){return a+b}
```

### Transform with Options

```bash
# TypeScript with JSX
echo 'const x: JSX.Element = <div>Hello</div>' | esbuild --loader=tsx

# Minify and target older browsers
echo 'async function f() { await x }' | esbuild --minify --target=es2015

# Add source maps
echo 'let x: number = 1' | esbuild --loader=ts --sourcemap=inline
```

### Available CLI Flags for Transform

- `--loader=<type>` - File type (ts, jsx, css, etc.)
- `--minify` - Minify output
- `--target=<version>` - Target JavaScript version
- `--sourcemap=[inline|external]` - Generate source maps
- `--define:<var>=<value>` - Replace variables
- `--supported:<feature>=true/false` - Enable/disable features

## JavaScript API

### Async Transform (Recommended)

```javascript
import * as esbuild from 'esbuild'

const code = 'let x: number = 1'
const result = await esbuild.transform(code, {
  loader: 'ts',
  sourcemap: 'inline',
})

console.log(result.code)      // Transformed code
console.log(result.map)       // Source map (if enabled)
console.log(result.errors)    // Any errors
```

### Sync Transform (Node.js only)

```javascript
const esbuild = require('esbuild')

const code = 'let x: number = 1'
const result = esbuild.transformSync(code, {
  loader: 'ts',
})

console.log(result.code)
```

**Limitations of sync API:**
- No plugin support
- Blocks event loop
- No parallelization

## Transform Options

### Loader Types

Specify input file type:

```javascript
await esbuild.transform(code, { loader: 'ts' })    // TypeScript
await esbuild.transform(code, { loader: 'tsx' })   // TypeScript + JSX
await esbuild.transform(code, { loader: 'jsx' })   // JSX
await esbuild.transform(code, { loader: 'js' })    // JavaScript (default)
await esbuild.transform(code, { loader: 'css' })   // CSS
await esbuild.transform(code, { loader: 'json' })  // JSON
await esbuild.transform(code, { loader: 'text' })  // Text file
await esbuild.transform(code, { loader: 'base64' }) // Base64 encode
await esbuild.transform(code, { loader: 'binary' }) // Binary data
await esbuild.transform(code, { loader: 'dataurl' }) // Data URL
await esbuild.transform(code, { loader: 'empty' })  // Empty output
```

### Minification

```javascript
// Full minification
await esbuild.transform(code, { minify: true })

// Minify whitespace only
await esbuild.transform(code, {
  minifyWhitespace: true,
  minifyIdentifiers: false,
  minifySyntax: false,
})

// Minify identifiers only (rename variables)
await esbuild.transform(code, {
  minifyWhitespace: false,
  minifyIdentifiers: true,
  minifySyntax: false,
})
```

### Target Version

```javascript
// Transform to ES2015
await esbuild.transform(code, { target: 'es2015' })

// Transform to specific browser
await esbuild.transform(code, {
  target: ['chrome58', 'firefox57', 'safari11'],
})

// Transform to Node version
await esbuild.transform(code, { target: 'node18' })
```

### Source Maps

```javascript
// Inline source map (base64 in comment)
await esbuild.transform(code, { sourcemap: 'inline' })

// External source map
await esbuild.transform(code, { sourcemap: 'external' })

// Both inline and linked
await esbuild.transform(code, { sourcemap: 'both' })

// With source position
await esbuild.transform(code, {
  sourcemap: 'external',
  sourcefile: 'input.ts',  // Filename in source map
})
```

### JSX Configuration

```javascript
// Default React JSX
await esbuild.transform(code, { loader: 'jsx' })

// Custom factory function
await esbuild.transform(code, {
  loader: 'jsx',
  jsxFactory: 'h',
  jsxFragment: 'Fragment',
})

// Automatic runtime (React 17+)
await esbuild.transform(code, {
  loader: 'jsx',
  jsx: 'automatic',
  jsxImportSource: 'preact',  // Or 'react'
})

// Development mode (add line numbers)
await esbuild.transform(code, {
  loader: 'jsx',
  jsxDev: true,
})
```

### Define Variables

Replace variables at transform time:

```javascript
await esbuild.transform(code, {
  define: {
    'process.env.NODE_ENV': '"production"',
    '__VERSION__': '"1.0.0"',
    'Math.random': '() => 0.5',
  },
})
```

Code example:
```javascript
const env = process.env.NODE_ENV  // Replaced with "production"
const version = __VERSION__       // Replaced with "1.0.0"
```

### Tree Shaking in Transform

```javascript
await esbuild.transform(code, {
  treeShaking: true,  // Remove unused code
})

// Or disable
await esbuild.transform(code, {
  treeShaking: false,
})
```

### Drop Statements

Remove specific statements:

```javascript
// Remove console statements
await esbuild.transform(code, { drop: ['console'] })

// Remove debugger statements
await esbuild.transform(code, { drop: ['debugger'] })

// Remove both
await esbuild.transform(code, { drop: ['console', 'debugger'] })
```

### Keep Names

Preserve function and class names after minification:

```javascript
await esbuild.transform(code, {
  minify: true,
  keepNames: true,  // Don't rename functions/classes
})
```

Useful for libraries where names are part of the API.

## Use Cases

### TypeScript to JavaScript Converter

```javascript
import * as esbuild from 'esbuild'

async function transpileTypeScript(tsCode) {
  const result = await esbuild.transform(tsCode, {
    loader: 'ts',
    sourcemap: 'inline',
    target: 'es2015',
  })

  if (result.errors.length > 0) {
    throw new Error(result.errors[0].text)
  }

  return result.code
}
```

### Code Minifier

```javascript
import * as esbuild from 'esbuild'

async function minify(code) {
  const result = await esbuild.transform(code, {
    minify: true,
    drop: ['console', 'debugger'],
  })

  return result.code
}
```

### JSX to JavaScript

```javascript
import * as esbuild from 'esbuild'

async function transformJSX(jsxCode) {
  const result = await esbuild.transform(jsxCode, {
    loader: 'jsx',
    jsx: 'automatic',
    jsxImportSource: 'react',
  })

  return result.code
}
```

### CSS in JavaScript

```javascript
import * as esbuild from 'esbuild'

async function embedCSS(cssCode) {
  const result = await esbuild.transform(cssCode, {
    loader: 'css',
  })

  // CSS is minified and ready to inject
  return result.code
}
```

### JSON to JavaScript Module

```javascript
import * as esbuild from 'esbuild'

const json = '{"name": "example", "version": "1.0.0"}'

const result = await esbuild.transform(json, {
  loader: 'json',
})

// Output: export default {"name":"example","version":"1.0.0"};
```

### Base64 Encoding

```javascript
import * as esbuild from 'esbuild'

const binaryData = '\x00\x01\x02\x03'

const result = await esbuild.transform(binaryData, {
  loader: 'base64',
})

// Output: export default "AAECBg=="
```

## Error Handling

### CLI Error Handling

```bash
echo 'let x: number = "string"' | esbuild --loader=ts 2>&1
# Esbuild outputs syntax errors to stderr
```

### JavaScript API Error Handling

```javascript
import * as esbuild from 'esbuild'

try {
  const result = await esbuild.transform(invalidCode, { loader: 'ts' })

  if (result.errors.length > 0) {
    console.error('Transform errors:')
    result.errors.forEach(err => {
      console.error(`  ${err.location?.file}:${err.location?.line}: ${err.text}`)
    })
  }
} catch (err) {
  console.error('Fatal error:', err.message)
}
```

### Error Location Information

```javascript
const result = await esbuild.transform(code, { loader: 'ts' })

result.errors.forEach(err => {
  console.log({
    text: err.text,
    location: err.location?.file + ':' + err.location?.line + ':' + err.location?.column,
    notes: err.notes?.map(n => n.text),
  })
})
```

## Performance Tips

### Transform Multiple Files

```javascript
import * as esbuild from 'esbuild'

const files = ['file1.ts', 'file2.ts', 'file3.ts']

// Transform in parallel for better performance
const results = await Promise.all(
  files.map(file => esbuild.transform(readFile(file), { loader: 'ts' }))
)
```

### Reuse Context (Not Available for Transform)

Unlike `build`, the `transform` API doesn't support contexts. Each transform is independent.

### Use Sync API Carefully

```javascript
const esbuild = require('esbuild')

// Blocks event loop - avoid in high-traffic servers
const result = esbuild.transformSync(code, { loader: 'ts' })
```

## Browser Usage (WASM)

Transform code in the browser:

```javascript
import * as esbuild from 'esbuild-wasm'

await esbuild.initialize({
  wasmURL: './node_modules/esbuild-wasm/esbuild.wasm',
})

const result = await esbuild.transform('let x: number = 1', {
  loader: 'ts',
})

console.log(result.code)
```

**Note:** WASM version is 10x slower than native. Use only when necessary.

## Comparison: Transform vs Build

| Feature | Transform | Build |
|---------|-----------|-------|
| File system access | No | Yes |
| Bundling | No | Yes |
| Plugins | No | Yes |
| Multiple files | Independent | Linked |
| Resolution | N/A | Full path resolution |
| Use case | Single file processing | Full project bundling |

Use `transform` for isolated file processing, `build` for full projects.
