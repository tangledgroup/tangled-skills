# Plugin System

Plugins inject custom behavior into the build process. They are only available through the JavaScript and Go APIs — not the CLI. Plugins work with `build` but not with `transform`.

## Plugin Structure

A plugin is an object with a `name` and a `setup` function:

```js
let myPlugin = {
  name: 'my-plugin',
  setup(build) {
    build.onResolve({ filter: /\.myext$/ }, args => ({
      path: args.path,
      namespace: 'my-ns',
    }))

    build.onLoad({ filter: /\.myext$/, namespace: 'my-ns' }, async args => {
      let contents = await readFile(args.path)
      return { contents, loader: 'js' }
    })
  },
}
```

Use with build:

```js
await esbuild.build({
  entryPoints: ['app.js'],
  bundle: true,
  outfile: 'out.js',
  plugins: [myPlugin],
})
```

## Key Concepts

### Namespaces

Every module has an associated namespace. The default is `file` (file system). Plugins create virtual modules using custom namespaces to distinguish them from file system modules.

### Filters

Every callback must provide a regular expression filter. esbuild uses the filter to skip calling the callback when the path doesn't match, which avoids expensive cross-thread calls for maximum speed.

The regex syntax follows Go's regexp engine — no look-ahead, look-behind, or backreferences.

```js
build.onResolve({ filter: /^https?:\/\// }, args => ({
  path: args.path,
  external: true,
}))
```

## Callback Types

### onResolve

Runs on each import path in each module. Can redirect paths, mark them as external, or pass through to the next callback.

```js
build.onResolve({ filter: /^images\// }, args => ({
  path: path.join(args.resolveDir, 'public', args.path),
}))

build.onResolve({ filter: /^https?:\/\// }, args => ({
  path: args.path,
  external: true,
}))
```

**Arguments:** `path`, `importer`, `namespace`, `resolveDir`, `kind` (entry-point, import-statement, require-call, dynamic-import, etc.), `pluginData`, `with` (import attributes).

**Return values:** `path`, `external`, `namespace`, `errors`, `warnings`, `watchFiles`, `watchDirs`, `pluginData`, `pluginName`, `sideEffects`, `suffix`.

### onLoad

Runs for each unique path/namespace pair not marked as external. Returns module contents and tells esbuild how to interpret them.

```js
build.onLoad({ filter: /\.txt$/ }, async args => {
  let text = await fs.promises.readFile(args.path, 'utf8')
  return {
    contents: JSON.stringify(text.split(/\s+/)),
    loader: 'json',
  }
})
```

**Arguments:** `path`, `namespace`, `suffix`, `pluginData`, `with` (import attributes).

**Return values:** `contents` (string | Uint8Array), `loader`, `resolveDir`, `errors`, `warnings`, `watchFiles`, `watchDirs`, `pluginData`, `pluginName`.

### onStart

Runs once at the beginning of each build. Useful for initialization or validation.

```js
build.onStart(() => {
  console.log('Build started')
})
```

### onEnd

Runs once at the end of each build, even if canceled. Receives the build result.

```js
build.onEnd(result => {
  result.errors.forEach(err => console.error(err.text))
  result.warnings.forEach(warn => console.warn(warn.text))
})
```

### onDispose

Runs when the context is disposed. Useful for cleanup.

```js
build.onDispose(() => {
  // Clean up resources
})
```

## Resolving Paths from Plugins

Plugins can use `build.resolve()` to resolve import paths using esbuild's normal resolution logic:

```js
build.onResolve({ filter: /\.myext$/ }, async args => {
  let result = await build.resolve(args.path, {
    resolveDir: args.resolveDir,
    kind: 'import-statement',
  })
  return result
})
```

## Example: Environment Variables Plugin

```js
let envPlugin = {
  name: 'env',
  setup(build) {
    build.onResolve({ filter: /^env$/ }, args => ({
      path: args.path,
      namespace: 'env-ns',
    }))

    build.onLoad({ filter: /.*/, namespace: 'env-ns' }, () => ({
      contents: JSON.stringify(process.env),
      loader: 'json',
    }))
  },
}

// Usage in code:
// import { PATH } from 'env'
// console.log(`PATH is ${PATH}`)
```

## Example: HTTP Plugin

```js
let httpPlugin = {
  name: 'http',
  setup(build) {
    build.onResolve({ filter: /^https?:\/\// }, args => ({
      path: args.path,
      namespace: 'http-url',
    }))

    build.onLoad({ filter: /^https?:\/\//, namespace: 'http-url' }, async args => ({
      contents: await (await fetch(args.path)).text(),
      loader: 'js',
    }))
  },
}
```

## Plugin API Limitations

- Plugins are not available from the CLI
- Plugins work only with `build`, not `transform`
- JavaScript plugins run in a single-threaded context, so expensive synchronous operations block other builds. Use async callbacks for I/O.
- Not all esbuild internals are exposed — some features cannot be implemented as plugins by design

## Finding Plugins

Search for the `esbuild-plugin` keyword on npm, or check the central list at https://esbuild.github.io/plugins/#finding-plugins.

When publishing a plugin, add `"keywords": ["esbuild-plugin"]` to your `package.json`.
