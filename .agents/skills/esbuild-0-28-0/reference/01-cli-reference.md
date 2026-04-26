# CLI Reference

## Flag Forms

CLI flags come in three forms:

- `--foo` — boolean flags that are enabled by presence (e.g., `--minify`, `--bundle`)
- `--foo=bar` — single-value flags specified once (e.g., `--platform=node`, `--outfile=out.js`)
- `--foo:bar` — multi-value flags that can be repeated (e.g., `--external:lodash`, `--external:react`)

## Shell Considerations

The shell interprets arguments before esbuild sees them. For example, `echo *.json` may expand to filenames instead of the literal glob pattern. Use single quotes or escape characters as needed. When in doubt, use the JavaScript or Go API instead of CLI.

## Common Commands

### Bundle a single entry point

```bash
esbuild app.ts --bundle --outfile=dist/bundle.js
```

### Multiple entry points with output directory

```bash
esbuild src/index.ts src/utils.ts --bundle --outdir=dist
```

### Production bundle with minification and source maps

```bash
esbuild app.jsx --bundle --minify --sourcemap --target=chrome58,firefox57,safari11,edge16 --outfile=dist/bundle.js
```

### Bundle for Node.js

```bash
esbuild app.js --bundle --platform=node --target=node18 --outfile=dist/bundle.js
```

### Externalize packages (don't bundle dependencies)

```bash
esbuild app.jsx --bundle --platform=node --packages=external --outfile=dist/bundle.js
```

### Transform stdin

```bash
echo 'let x: number = 1' | esbuild --loader=ts
# Output: let x = 1;
```

### Bundle CSS

```bash
esbuild --bundle app.css --outfile=dist/bundle.css
```

### Watch mode

```bash
esbuild app.ts --bundle --outdir=dist --watch
```

### Local development server

```bash
esbuild app.ts --bundle --outdir=dist --serve
# Serves at http://127.0.0.1:8000/
```

### Watch + serve (live reload)

```bash
esbuild app.ts --bundle --outdir=www --watch --servedir=www
```

### Custom loader for file extension

```bash
esbuild app.js --bundle --loader:.js=jsx
```

### Path aliasing

```bash
esbuild app.ts --bundle --alias:react=preact/compat --outfile=dist/bundle.js
```

### Define runtime constants

```bash
esbuild app.ts --bundle --define:process.env.NODE_ENV='"production"' --outfile=dist/bundle.js
```

### Inject files (polyfills, globals)

```bash
esbuild app.ts --bundle --inject:./polyfill.js --outfile=dist/bundle.js
```

### Metafile for bundle analysis

```bash
esbuild app.ts --bundle --metafile=meta.json --outfile=dist/bundle.js
```

### Analyze bundle

```bash
esbuild app.ts --bundle --analyze --outfile=dist/bundle.js
```

## CLI Limitations

- Plugins are not available from the CLI — use JavaScript or Go API for plugins
- The `rebuild` incremental build API is not available from the CLI
- The `cancel` API is not available from the CLI
- When using the native binary directly (not via npm), only CLI access is available

## Supported Platforms

Native executables are available for: darwin-arm64, darwin-x64, linux-arm, linux-arm64, linux-ia32, linux-loong64, linux-mips64el, linux-ppc64, linux-riscv64, linux-s390x, linux-x64, win32-arm64, win32-ia32, win32-x64, freebsd-x64, freebsd-arm64, openbsd-x64, openbsd-arm64, netbsd-x64, netbsd-arm64, aix-ppc64, android-arm, android-arm64, android-x64, sunos-x64, openharmony-arm64.

Note: esbuild binaries are platform-specific. You cannot copy `node_modules` between OSes and expect esbuild to work. Run `npm install` on the target platform, or use `esbuild-wasm` for cross-platform compatibility (with ~10x performance cost).
