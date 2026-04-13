# Esbuild API Reference

## CLI API

### Basic Syntax

```bash
esbuild [options] [entry points]
```

### Common CLI Options

#### Input Options

```bash
# Entry points (files to bundle)
esbuild src/index.tsx src/admin.tsx --bundle

# Standard input
echo 'console.log("hello")' | esbuild --stdin=--loader=js

# Loader for file types
esbuild app.js --loader:.js=jsx  # Treat .js as JSX
```

#### Output Options

```bash
# Single output file
esbuild app.ts --bundle --outfile=dist/bundle.js

# Multiple output files (directory)
esbuild src/a.ts src/b.ts --bundle --outdir=dist

# Don't write to disk (output to stdout)
esbuild app.ts --bundle --stdout
```

#### Build Options

```bash
# Enable bundling
esbuild app.ts --bundle

# Platform target
esbuild app.ts --bundle --platform=node

# JavaScript/CSS target version
esbuild app.ts --bundle --target=es2015

# Output format
esbuild app.ts --bundle --format=cjs  # CommonJS
esbuild app.ts --bundle --format=esm   # ES modules
esbuild app.ts --bundle --format=iife  # IIFE (default)
```

#### Optimization Options

```bash
# Minify
esbuild app.js --minify

# Tree shaking
esbuild app.js --bundle --tree-shaking=true

# Define variables
esbuild app.js --define:process.env.NODE_ENV="'production'"

# Drop code
esbuild app.js --drop:console --drop:debugger
```

#### Source Map Options

```bash
# Inline source map
esbuild app.ts --sourcemap=inline

# External source map file
esbuild app.ts --sourcemap=external

# Both inline and external
esbuild app.ts --sourcemap=both
```

#### Development Options

```bash
# Watch mode
esbuild app.ts --bundle --watch

# Serve mode
esbuild app.ts --bundle --serve --servedir=dist

# Both watch and serve
esbuild app.ts --bundle --watch --serve
```

### Complete CLI Option List

See esbuild documentation for full list of 100+ CLI options.

## JavaScript API

### Async API (Recommended)

```javascript
import * as esbuild from 'esbuild'

// Build
const result = await esbuild.build({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outfile: 'dist/app.js',
})

// Transform
const result = await esbuild.transform(code, {
  loader: 'ts',
  minify: true,
})

// Context for incremental builds
const ctx = await esbuild.context(options)
await ctx.rebuild()
await ctx.watch()
const { hosts, port } = await ctx.serve()
await ctx.dispose()
```

### Sync API (Node.js Only)

```javascript
const esbuild = require('esbuild')

// Build sync
const result = esbuild.buildSync({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outfile: 'dist/app.js',
})

// Transform sync
const result = esbuild.transformSync(code, {
  loader: 'ts',
})
```

**Limitations:** No plugin support, blocks event loop.

### Build Options (JavaScript API)

```javascript
await esbuild.build({
  // Input
  entryPoints: ['src/index.tsx'],  // Array of entry files
  stdin: {                          // Or stdin options
    contents: 'console.log("hello")',
    resolveDir: '.',
    loader: 'js',
  },

  // Output
  outfile: 'dist/app.js',           // Single output file
  outdir: 'dist',                   // Or output directory
  outbase: 'src',                   // Strip from output paths
  metafile: 'meta.json',            // Build metadata file

  // Bundling
  bundle: true,                     // Enable bundling
  splitting: false,                 // Code splitting
  chunks: true,                     // Allow chunking

  // Platform
  platform: 'browser',              // browser, node, or neutral
  target: ['chrome91', 'firefox89'], // Or 'es2015', 'node18'
  format: 'iife',                   // iife, cjs, esm

  // Transformation
  loader: { '.ts': 'tsx' },         // Custom loaders
  resolveExtensions: ['.ts', '.js'], // File extensions to try
  mainFields: ['browser', 'module'], // package.json fields
  conditions: [],                   // Package export conditions
  alias: { '@/': './src/' },        // Path aliases
  external: ['lodash'],             // External packages
  packages: 'external',             // all, external, or external-if-in-externals

  // Optimization
  minify: false,                    // Full minification
  minifyWhitespace: true,           // Minify whitespace only
  minifyIdentifiers: true,          // Rename variables
  minifySyntax: true,               // Optimize syntax
  treeShaking: true,                // Remove unused code
  keepNames: false,                 // Preserve function names
  define: { 'process.env.NODE_ENV': '"production"' },
  drop: ['console', 'debugger'],    // Remove statements
  dropLabels: [],                   // Remove labeled blocks
  inject: ['./polyfills.js'],       // Inject into all modules
  supported: { 'optional-chaining': true },

  // Source maps
  sourcemap: false,                 // false, 'inline', 'external', 'both'
  sourcesContent: true,             // Include source in maps
  sourceRoot: '',                   // Prefix for source paths
  sourcefile: '',                   // Filename in source map

  // JSX
  jsx: 'transform',                 // transform, preserve, automatic
  jsxFactory: 'React.createElement',
  jsxFragment: 'React.Fragment',
  jsxImportSource: 'react',
  jsxDev: false,                    // Development mode
  jsxSideEffects: true,

  // Output content
  banner: { js: '"use strict";' },  // Code at start
  footer: { js: '// End of file' }, // Code at end
  globalName: 'MyApp',              // IIFE global name
  inject: [],                       // Injected files
  legalComments: 'inline',          // inline, eof, external, none

  // Advanced
  tsconfig: 'tsconfig.json',        // TypeScript config path
  tsconfigRaw: { compilerOptions: {} }, // Or inline config
  logLevel: 'info',                 // info, warning, error, silent
  logLimit: 10,                     // Max errors to show
  color: true,                      // Colored output
  metafile: true,                   // Return metadata
  write: true,                      // Write output files
  allowOverwrite: false,            // Overwrite existing files
  watch: false,                     // Watch mode (use context instead)
  serve: false,                     // Serve mode (use context instead)

  // Plugins
  plugins: [],                      // Plugin array
})
```

### Transform Options (JavaScript API)

```javascript
await esbuild.transform(code, {
  // Input
  loader: 'ts',              // ts, jsx, css, json, etc.
  sourcefile: 'input.ts',    // Filename for errors/source maps

  // Output
  format: 'esm',             // esm, cjs, iife
  charset: 'utf8',           // utf8 or ascii

  // Transformation
  target: 'es2015',
  jsx: 'transform',
  jsxFactory: 'h',

  // Optimization
  minify: false,
  treeShaking: true,
  drop: ['console'],
  define: { '__ENV__': '"production"' },

  // Source maps
  sourcemap: 'inline',
  sourcesContent: true,

  // Platform
  platform: 'browser',

  // Logging
  logLevel: 'warning',
  color: false,
})
```

### Context API (Incremental Builds)

```javascript
const ctx = await esbuild.context({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
})

// Rebuild manually
const result = await ctx.rebuild()

// Watch mode
await ctx.watch({
  onRebuild(error, result) {
    if (error) {
      console.error('Build failed:', error)
    } else {
      console.log('Build succeeded')
    }
  },
})

// Serve mode
const serveResult = await ctx.serve({
  port: 8080,
  host: '0.0.0.0',
  servedir: 'dist',
  certFile: 'cert.pem',
  keyFile: 'key.pem',
  requestTimeout: 0,  // No timeout (milliseconds)
})

console.log(`Server at http://${serveResult.hosts[0]}:${serveResult.port}`)

// Cancel ongoing build
await ctx.cancel()

// Cleanup
await ctx.dispose()
```

## Go API

### Build Function

```go
package main

import "github.com/evanw/esbuild/pkg/api"

func main() {
  result := api.Build(api.BuildOptions{
    EntryPoints: []string{"src/index.tsx"},
    Bundle:      true,
    Outfile:     "dist/app.js",
    Minify:      true,
  })

  if len(result.Errors) > 0 {
    // Handle errors
    for _, err := range result.Errors {
      println(err.Text)
    }
  }
}
```

### Build Options (Go API)

```go
api.BuildOptions{
  // Input
  EntryPoints: []string{"src/index.tsx"},
  Stdin: &api.StdinOptions{
    Contents:   `console.log("hello")`,
    ResolveDir: ".",
    Loader:     api.LoaderJS,
  },

  // Output
  Outfile: "dist/app.js",
  Outdir:  "dist",
  Outbase: "src",

  // Bundling
  Bundle:   true,
  Splitting: false,

  // Platform
  Platform: api.PlatformBrowser,  // Browser, Node, Neutral
  Target:   api.ES2015,           // Or ES2015, ES2016, ..., Chrome91, etc.
  Format:   api.FormatIIFE,       // IIFE, CJS, ESM

  // Transformation
  Loader: map[string]api.Loader{
    ".ts": api.LoaderTSX,
  },
  ResolveExtensions: []string{".ts", ".js"},
  MainFields:        []string{"browser", "module"},
  Conditions:        []string{},
  Alias: map[string]string{
    "@/": "./src/",
  },
  External: []string{"lodash"},

  // Optimization
  MinifyWhitespace:  true,
  MinifyIdentifiers: true,
  MinifySyntax:      true,
  TreeShaking:       api.TreeShakingTrue,
  KeepNames:         false,
  Define: map[string]string{
    "process.env.NODE_ENV": `"production"`,
  },
  Drop: []string{"console", "debugger"},

  // Source maps
  Sourcemap: api.SourceMapInline,
  SourcesContent: true,

  // JSX
  JSX:            api.JSXTransform,
  JSXFactory:     "React.createElement",
  JSXFragment:    "React.Fragment",
  JSXImportSource: "react",
  JSXDev:         false,

  // Advanced
  Tsconfig:        "tsconfig.json",
  LogLevel:        api.LogLevelInfo,
  Color:           true,
  Metafile:        true,
  Write:           true,
}
```

### Context (Go API)

```go
ctx, err := api.Context(api.BuildOptions{
  EntryPoints: []string{"src/index.tsx"},
  Bundle:      true,
  Outdir:      "dist",
})
if err != nil {
  log.Fatal(err)
}
defer ctx.Dispose()

// Rebuild
result := ctx.Rebuild()

// Watch
err = ctx.Watch(api.WatchOptions{})

// Serve
serveResult, err := ctx.Serve(api.ServeOptions{
  Port:     8080,
  Host:     "0.0.0.0",
  Servedir: "dist",
})

// Cancel
ctx.Cancel()
```

### Transform (Go API)

```go
result := api.Transform(`let x: number = 1`, api.TransformOptions{
  Loader: api.LoaderTS,
  Minify: true,
})

if len(result.Errors) == 0 {
  println(result.Code)
}
```

## Browser API (WASM)

### Initialize and Use

```javascript
import * as esbuild from 'esbuild-wasm'

// Initialize WASM
await esbuild.initialize({
  wasmURL: './node_modules/esbuild-wasm/esbuild.wasm',
  // worker: false,  // Run in current thread (if already in worker)
})

// Use API (same as Node.js async API)
const result = await esbuild.build({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  // Note: write must be false in browser (no file system)
  write: false,
})

console.log(result.outputFiles[0].text)

// Cleanup
await esbuild.stop()
```

### Browser Limitations

- No file system access (`write: false`)
- Output returned in `result.outputFiles` array
- Sync API not available
- Slower than native version

## API Comparison

| Feature | CLI | JS Async | JS Sync | Go | Browser |
|---------|-----|----------|---------|----|---------|
| Bundling | ✅ | ✅ | ✅ | ✅ | ✅ |
| Transform | ✅ | ✅ | ✅ | ✅ | ✅ |
| Plugins | ❌ | ✅ | ❌ | ✅ | ❌ |
| Watch mode | ✅ | ✅ | ❌ | ✅ | ❌ |
| Serve mode | ✅ | ✅ | ❌ | ✅ | ❌ |
| Incremental builds | Implicit | ✅ (context) | ❌ | ✅ | ❌ |
| File system access | ✅ | ✅ | ✅ | ✅ | ❌ |
| Parallelization | ❌ | ✅ | ❌ | ✅ | ❌ |

## Error Handling

### JavaScript API Errors

```javascript
try {
  const result = await esbuild.build(options)
} catch (err) {
  console.error('Build error:', err.message)
}
```

### Transform Result Errors

```javascript
const result = await esbuild.transform(code, { loader: 'ts' })

if (result.errors.length > 0) {
  result.errors.forEach(err => {
    console.error({
      text: err.text,
      location: `${err.location.file}:${err.location.line}:${err.location.column}`,
      notes: err.notes.map(n => n.text),
    })
  })
}
```

### Go API Errors

```go
result := api.Build(options)

if len(result.Errors) > 0 {
  for _, err := range result.Errors {
    fmt.Printf("%s\n", err.Text)
  }
  os.Exit(1)
}
```
