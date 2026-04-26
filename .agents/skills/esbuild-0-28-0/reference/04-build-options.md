# Build Options

Options are organized by category. The build API accepts all categories; the transform API accepts a subset.

## General Options

**`bundle`** (boolean) — Inline imported dependencies recursively into the output. Must be explicitly enabled. Multiple entry points create multiple separate bundles, not concatenated files.

**`platform`** (string: `browser` | `node`) — Target platform. Default is `browser`. Setting to `node` automatically marks built-in node packages (`fs`, `path`, etc.) as external and disables the `browser` field in `package.json`.

**`tsconfig`** (string) — Path to a `tsconfig.json` file. esbuild reads specific fields: `experimentalDecorators`, `target`, `useDefineForClassFields`, `baseUrl`, `paths`, `jsx`, `jsxFactory`, `jsxFragmentFactory`, `jsxImportSource`, `alwaysStrict`, `strict`, `verbatimModuleSyntax`, `importsNotUsedAsValues`, `preserveValueImports`, `extends`.

**`watch`** (boolean | object) — Enable watch mode. Automatically rebuilds when source files change.

**`serve`** (object) — Start a local development server. Options include `port`, `host`, `servedir`, `fonPort`.

## Input Options

**`entryPoints`** (string[]) — Entry point file paths. Can also use an object map `{ "name": "path" }` to control output filenames.

**`stdin`** (object) — Read from stdin instead of files. Properties: `contents` (string), `loader` (string), `resolveDir` (string).

**`loader`** (object) — Map file extensions to loaders. Example: `{ '.js': 'jsx', '.png': 'binary' }`.

## Output Contents Options

**`format`** (string: `iife` | `cjs` | `esm`) — Output module format. Default depends on platform and entry point extension. Use `iife` with `<script src="...">`, `esm` with `<script type="module">`.

**`globalName`** (string) — Global variable name for IIFE format output.

**`minify`** (boolean) — Enable minification (whitespace, identifiers, and syntax). Equivalent to `minifyWhitespace`, `minifyIdentifiers`, `minifySyntax` all true.

**`minifyWhitespace`** (boolean) — Remove unnecessary whitespace.

**`minifyIdentifiers`** (boolean) — Shorten variable/function names.

**`minifySyntax`** (boolean) — Transform syntax to shorter equivalents.

**`treeShaking`** (boolean) — Enable tree shaking (dead code elimination). Default is true when bundling.

**`target`** (string[]) — Target JavaScript environments. Examples: `['chrome58', 'firefox57', 'safari11', 'edge16']`, `['node18']`, or ES version like `['es2020']`. Controls which modern syntax features are transformed to older equivalents.

**`sourcemap`** (boolean | string) — Generate source maps. Values: `true` (linked external file), `'inline'` (embedded in output), `'external'` (separate .map file).

**`sourceRoot`** (string) — The `sourceRoot` field in the generated source map.

**`sourcefile`** (string) — The `file` field in the generated source map.

**`sourcesContent`** (boolean) — Include original source content in source maps. Default is true.

**`charset`** (string: `utf8` | `ascii`) — Output character encoding. Default is `utf8`. Use `ascii` to escape non-ASCII characters.

**`banner`** (object) — Text to prepend to output files. Example: `{ js: '// banner', css: '/* banner */' }`.

**`footer`** (object) — Text to append to output files.

**`lineLimit`** (number) — Maximum line length for minified output. Default is 0 (no limit).

**`legalComments`** (string: `none` | `inline` | `eof` | `linked` | `external`) — How to handle legal comments (license headers). Default is `inline`.

**`splitting`** (boolean) — Enable code splitting to create separate chunks.

## Output Location Options

**`outfile`** (string) — Output file path. Use with a single entry point.

**`outdir`** (string) — Output directory. Use with multiple entry points.

**`outbase`** (string) — The base path for computing output filenames when using `outdir`.

**`outExtension`** (object) — Map output extensions. Example: `{ '.js': '.mjs' }`.

**`entryNames`** (string) — Template for entry point output filenames. Default is `[dir]/[name]`.

**`chunkNames`** (string) — Template for chunk filenames. Default is `[dir]/[name]-[hash]`.

**`assetNames`** (string) — Template for asset filenames. Default is `[dir]/[name][ext]`.

**`publicPath`** (string) — Public URL path for loading output files in the browser.

**`assetNames`** (string) — Pattern for non-entry-point asset file names.

**`allowOverwrite`** (boolean) — Allow writing output files that already exist. Default is true when using `outfile`, false when using `outdir`.

**`write`** (boolean) — Write output to disk. Set to false to get output in memory instead.

## Path Resolution Options

**`alias`** (object) — Map package names to other packages. Example: `{ 'react': 'preact/compat' }`.

**`external`** (string[]) — Mark paths as external (not bundled). Example: `['^https?://', '^npm:']`.

**`packages`** (string: `bundle` | `external`) — How to handle node_modules. Default is `bundle`.

**`mainFields`** (string[]) — Order of fields to check in `package.json`. Default depends on platform.

**`conditions`** (string[]) — Export conditions to match in `package.json` exports field.

**`resolveExtensions`** (string[]) — File extensions to try when resolving imports. Default: `['.js', '.jsx', '.ts', '.tsx']`.

**`nodePaths`** (string[]) — Directories to search for packages (like `NODE_PATH`).

**`preserveSymlinks`** (boolean) — Don't resolve symlinks to their targets during path resolution.

**`workingDir`** (string) — The directory in which to resolve relative paths. Default is the current working directory.

## Transformation Options

**`jsx`** (string: `transform` | `preserve` | `automatic`) — How to handle JSX. Default is `transform`. Use `automatic` for React 17+ auto-import.

**`jsxFactory`** (string) — The function called for JSX elements. Default: `React.createElement`.

**`jsxFragment`** (string) — The function called for JSX fragments. Default: `React.Fragment`.

**`jsxImportSource`** (string) — The package from which to import JSX helpers when using `automatic` mode. Default: `react`.

**`jsxSideEffects`** (boolean) — Treat JSX expressions as having side effects. Default is false.

**`jsxDev`** (boolean) — Enable development-mode JSX transforms (adds file/line info).

**`define`** (object) — Replace global identifiers with values at compile time. Example: `{ 'process.env.NODE_ENV': '"production"' }`.

**`drop`** (string[]) — Remove specific language constructs. Example: `['console']`, `['debugger']`.

**`dropLabels`** (string[]) — Remove code inside labeled statements. Example: `['__DEBUG__']`.

**`inject`** (string[]) — Inject files at the top of every chunk. Useful for polyfills.

**`keepNames`** (boolean) — Preserve function and class names through minification.

**`mangleProps`** (object) — Mangle property names with regex patterns.

**`pure`** (string[]) — Mark functions as pure (safe to tree-shake). Example: `['classCallCheck']`.

**`ignoreAnnotations`** (boolean) — Ignore bundle annotations like `webpackIgnore` and `webpackChunkName`.

## Build Metadata Options

**`metafile`** (boolean | string) — Generate a metafile describing inputs, outputs, and dependencies. Use with the Bundle Size Analyzer at https://esbuild.github.io/analyze/.

**`analyze`** (boolean) — Print a breakdown of bundle contents to stderr after building.

## Logging Options

**`logLevel`** (string: `debug` | `info` | `warn` | `error` | `silent`) — Control log output verbosity.

**`logLimit`** (number) — Maximum number of log messages to show. Default is 15.

**`logOverride`** (object) — Override log level for specific plugins or rules.
