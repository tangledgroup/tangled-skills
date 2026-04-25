# Esbuild Plugin Development

## Overview

Plugins extend esbuild's functionality by intercepting the build process. They can:
- Resolve custom import paths
- Load virtual files
- Transform code before/after esbuild processes it
- Add build-time logic
- Integrate with external tools

**Important:** Plugins only work with the async JavaScript API and Go API, not CLI or sync JS API.

## Plugin Structure

Basic plugin template:

```javascript
const myPlugin = {
  name: 'my-plugin',
  setup(build) {
    // Register callbacks here
    build.onResolve({ filter: /\.myext$/ }, args => {
      // Handle resolution
    })

    build onLoad({ filter: /\.myext$/ }, args => {
      // Handle loading
    })
  },
}
```

## On-Resolve Callbacks

Intercept import path resolution:

### Basic Resolution

```javascript
const plugin = {
  name: 'resolve-plugin',
  setup(build) {
    build.onResolve({ filter: /^@myorg\/.*/ }, args => {
      return {
        path: './src/custom/' + args.path.slice(7) + '.js',
        external: false,
      }
    })
  },
}
```

### Resolution Options

```javascript
build.onResolve({
  filter: /\.custom$/,      // Regex to match paths
  namespace: 'custom',       // Or match by namespace
}, args => {
  return {
    path: 'resolved-path.js',     // Required: resolved path
    external: false,              // Optional: mark as external
    namespace: 'custom',          // Optional: custom namespace
    pluginData: { /* any data */ }, // Pass to onLoad
    sideEffects: true,            // Has side effects
  }
})
```

### Args Object Properties

- `path`: The import path being resolved
- `importer`: File that imported this path (empty for entry points)
- `namespace`: Namespace of the importer
- `pluginData`: Data from previous plugin
- `resolveDir`: Directory for relative resolution
- `kind`: How the path was imported (e.g., 'entry-point', 'import-statement')

### Marking as External

```javascript
build.onResolve({ filter: /^lodash/ }, args => ({
  path: args.path,
  external: true,  // Don't bundle this module
}))
```

## On-Load Callbacks

Intercept file loading:

### Basic Loading

```javascript
const plugin = {
  name: 'load-plugin',
  setup(build) {
    build.onLoad({ filter: /\.virtual$/ }, args => ({
      contents: 'export const value = 42',
      loader: 'js',
    }))
  },
}
```

### Load Options

```javascript
build.onLoad({
  filter: /\.custom$/,
  namespace: 'custom',
}, args => ({
  contents: 'code string or Uint8Array',  // Required
  loader: 'js',                            // js, ts, jsx, etc.
  resolveDir: '/path/to/dir',             // For relative imports
  pluginData: { /* pass to next plugin */ },
  watchFiles: ['/file/to/watch'],         // Files to watch
  watchDirs: ['/dir/to/watch'],           // Directories to watch
}))
```

### Virtual Files

Create files that don't exist on disk:

```javascript
build.onLoad({ filter: /^env:.*/ }, args => ({
  contents: `export const ENV = ${JSON.stringify(process.env)}`,
  loader: 'js',
}))

// Usage in code: import { ENV } from 'env:vars'
```

### Transforming Files

```javascript
build.onLoad({ filter: /\.txt$/ }, args => {
  const text = require('fs').readFileSync(args.path, 'utf8')
  return {
    contents: `export default ${JSON.stringify(text)}`,
    loader: 'js',
  }
})
```

## On-Start Callbacks

Run once when build starts:

```javascript
const plugin = {
  name: 'start-plugin',
  setup(build) {
    build.onStart(() => {
      console.log('Build starting...')

      // Return errors to fail the build
      return {
        errors: [{ text: 'Custom error' }],
        warnings: [{ text: 'Custom warning' }],
      }
    })
  },
}
```

### Use Cases

- Validate configuration
- Generate code before build
- Check external dependencies
- Set up build-time state

## On-End Callbacks

Run after each build completes:

```javascript
const plugin = {
  name: 'end-plugin',
  setup(build) {
    build.onEnd(result => {
      console.log('Build finished')
      console.log('Errors:', result.errors.length)
      console.log('Warnings:', result.warnings.length)

      // Access output files
      result.outputFiles.forEach(file => {
        console.log(`${file.path}: ${file.contents.length} bytes`)
      })

      // Add errors/warnings
      return {
        errors: [],
        warnings: [{ text: 'Post-build warning' }],
      }
    })
  },
}
```

### Use Cases

- Analyze build output
- Generate reports
- Post-process files
- Deploy artifacts

## On-Dispose Callbacks

Cleanup when build context is disposed:

```javascript
const plugin = {
  name: 'dispose-plugin',
  setup(build) {
    let server

    build.onStart(() => {
      server = startExternalServer()
    })

    build.onDispose(() => {
      console.log('Cleaning up...')
      server.stop()
    })
  },
}
```

## Resolving Paths from Plugins

### Resolve Helper

Use `build.resolve()` to resolve paths:

```javascript
build.onResolve({ filter: /^@app\// }, async args => {
  const result = await build.resolve(args.path.slice(5), {
    importer: args.importer,
    resolveDir: args.resolveDir,
  })

  return {
    path: result.path,
    external: result.external,
  }
})
```

### Resolve Options

```javascript
const result = await build.resolve(path, {
  importer: './src/index.js',      // File doing the import
  namespace: 'custom',             // Namespace context
  pluginData: {},                  // Data from previous step
  kind: 'import-statement',        // How path was imported
  resolveDir: '/current/dir',      // For relative paths
  conditions: [],                  // Package export conditions
})

// Returns: { path, external, namespace, sideEffects }
```

## Plugin Data

Pass data between callbacks:

```javascript
const plugin = {
  name: 'data-plugin',
  setup(build) {
    build.onResolve({ filter: /\.custom$/ }, args => ({
      path: args.path,
      pluginData: { originalPath: args.path },
    }))

    build.onLoad({ filter: /\.custom$/ }, args => {
      console.log('Original path:', args.pluginData.originalPath)
      return { contents: 'export default 1', loader: 'js' }
    })
  },
}
```

## Example Plugins

### HTML Plugin

Serve HTML files and inject bundle scripts:

```javascript
const htmlPlugin = {
  name: 'html',
  setup(build) {
    build.onLoad({ filter: /\.html$/ }, args => ({
      contents: require('fs').readFileSync(args.path, 'utf8'),
      loader: 'text',
    }))

    build.onEnd(result => {
      result.outputFiles.forEach(file => {
        if (file.path.endsWith('.html')) {
          let html = file.text
          // Inject script tag for bundle
          html = html.replace(
            '</head>',
            `<script src="app.js"></script></head>`
          )
          file.contents = Buffer.from(html, 'utf8')
        }
      })
    })
  },
}
```

### Image Plugin

Convert images to data URLs:

```javascript
const imagePlugin = {
  name: 'image',
  setup(build) {
    build.onLoad({ filter: /\.(png|jpg|gif)$/ }, async args => {
      const data = require('fs').readFileSync(args.path)
      const base64 = data.toString('base64')
      const mime = { png: 'image/png', jpg: 'image/jpeg', gif: 'image/gif' }[args.path.split('.').pop()]

      return {
        contents: `export default "data:${mime};base64,${base64}"`,
        loader: 'js',
      }
    })
  },
}
```

### Markdown Plugin

Convert Markdown to JavaScript:

```javascript
const markdownPlugin = {
  name: 'markdown',
  setup(build) {
    build.onLoad({ filter: /\.md$/ }, async args => {
      const markdown = require('fs').readFileSync(args.path, 'utf8')
      const html = (await import('marked')).default(markdown)

      return {
        contents: `export default ${JSON.stringify(html)}`,
        loader: 'js',
      }
    })
  },
}
```

### Alias Plugin

Custom path aliases:

```javascript
const aliasPlugin = (aliases) => ({
  name: 'alias',
  setup(build) {
    for (const [from, to] of Object.entries(aliases)) {
      build.onResolve({ filter: new RegExp('^' + from + '$') }, args => ({
        path: to,
      }))
    }
  },
})

// Usage
await esbuild.build({
  plugins: [aliasPlugin({
    '@components/': './src/components/',
    '@utils/': './src/utils/',
  })],
})
```

### Side Effects Plugin

Mark modules as having side effects:

```javascript
const sideEffectsPlugin = {
  name: 'side-effects',
  setup(build) {
    build.onResolve({ filter: /\.css$/ }, args => ({
      path: args.path,
      sideEffects: true,  // Prevent tree shaking
    }))
  },
}
```

### Environment Variable Plugin

Inject environment variables:

```javascript
const envPlugin = (env) => ({
  name: 'env',
  setup(build) {
    build.onResolve({ filter: /^env:.*/ }, args => ({
      path: args.path,
      namespace: 'env',
    }))

    build.onLoad({ namespace: 'env' }, args => ({
      contents: `export default ${JSON.stringify(env)}`,
      loader: 'js',
    }))
  },
})

// Usage
await esbuild.build({
  plugins: [envPlugin(process.env)],
})

// In code: import env from 'env:vars'
```

## Using Plugins

### Single Plugin

```javascript
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  plugins: [myPlugin],
})
```

### Multiple Plugins

```javascript
await esbuild.build({
  plugins: [
    aliasPlugin({ '@/' : './src/' }),
    imagePlugin(),
    markdownPlugin(),
  ],
})
```

Plugins run in order - earlier plugins can transform paths for later plugins.

## Plugin API Limitations

### No File System Access in Browser

Plugins cannot read/write files when using esbuild-wasm in browser:

```javascript
// Won't work in browser
build.onLoad({ filter: /\.txt$/ }, args => {
  require('fs').readFileSync(args.path)  // Error: fs not available
})
```

### Async Only

Plugins only work with async API:

```javascript
// ❌ Won't work
esbuild.buildSync({ plugins: [myPlugin] })

// ✅ Works
await esbuild.build({ plugins: [myPlugin] })
```

### No CLI Support

Plugins cannot be used from command line. Use JavaScript API instead.

## Finding Plugins

Community plugins are available on npm:

- `esbuild-plugin-react-refresh` - Fast refresh for React
- `esbuild-plugin-html` - HTML minification and injection
- `esbuild-plugin-less` / `esbuild-plugin-sass` - CSS preprocessors
- `esbuild-plugin-css-modules` - Advanced CSS modules
- `esbuild-plugin-node-polyfills` - Node.js polyfills for browser

Search npm for `esbuild-plugin-*` to find more.

## Debugging Plugins

### Log Messages

```javascript
build.onResolve({ filter: /.*/ }, args => {
  console.log('Resolving:', args.path, 'from', args.importer)
})
```

### Error Inspection

```javascript
build.onEnd(result => {
  result.errors.forEach(err => console.error(err))
  result.warnings.forEach(warn => console.warn(warn))
})
```

### Plugin Order Debugging

```javascript
const debugPlugin = (name) => ({
  name,
  setup(build) {
    console.log(`Plugin ${name} loaded`)

    build.onStart(() => console.log(`Plugin ${name} start`))
    build.onEnd(() => console.log(`Plugin ${name} end`))
    build.onDispose(() => console.log(`Plugin ${name} dispose`))
  },
})
```

## Best Practices

1. **Use filters selectively:** Match only necessary paths to avoid performance impact
2. **Return early:** Exit callbacks quickly when not handling a path
3. **Cache results:** Store resolved paths to avoid redundant work
4. **Handle errors gracefully:** Return errors in onStart/onEnd, don't throw
5. **Document plugin behavior:** Clear name and setup comments
6. **Test with watch mode:** Ensure plugins work with incremental builds
