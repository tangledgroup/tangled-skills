# Esbuild FAQ and Troubleshooting

## Performance

### Why is esbuild fast?

Esbuild achieves 10-100x speed improvements through:

1. **Written in Go:** Compiled to native code, no JavaScript overhead
2. **Parallel processing:** Uses all CPU cores automatically
3. **No caching needed:** Fast enough that cache adds complexity without benefit
4. **Efficient parsing:** Custom parser optimized for bundling (not full ECMAScript compliance)
5. **Minimal abstractions:** Direct code generation without intermediate representations

### Benchmark Details

Default benchmark: 10 copies of three.js library bundled from scratch

| Tool | Time | Speed vs esbuild |
|------|------|------------------|
| esbuild | 0.39s | 1x (baseline) |
| parcel 2 | 14.91s | 38x slower |
| rollup 4 + terser | 34.10s | 87x slower |
| webpack 5 | 41.21s | 106x slower |

**Test conditions:**
- Production build (minified)
- Source maps enabled
- Cold cache (no previous build)
- Default settings for each tool

## Production Readiness

### Is esbuild production-ready?

Yes. Esbuild is used in production by:
- Next.js (default bundler for some configurations)
- Remix
- Fresh (Deno fullstack framework)
- Vite (for dependency pre-bundling)
- Millions of npm packages

### What doesn't esbuild support?

Esbuild prioritizes speed and simplicity over feature completeness:

**Not supported:**
- CSS custom properties (variables) in all contexts
- Full CSS @import resolution
- PostCSS plugins (use separate CSS build step)
- TypeScript type checking (transpilation only)
- Declaration file generation (.d.ts)
- Run-time code splitting (only static import())
- Legacy JavaScript (IE11 and below)

**Work arounds available:**
- Use Parcel or webpack for full CSS support
- Run tsc --noEmit for type checking
- Use separate tool for .d.ts generation
- Target ES2015+ browsers only

## Common Issues

### Anti-virus Software False Positives

Esbuild downloads platform-specific binaries that some anti-virus software flags.

**Symptoms:**
- `esbuild` command not found after npm install
- Build fails with "binary not found" error
- Anti-virus quarantine logs show esbuild binaries

**Solutions:**

1. **Add exclusion (recommended):**
   - Add `node_modules` to anti-virus exclusion list
   - Or exclude `*.tgz` files from scanning

2. **Use --ignore-scripts:**
   ```bash
   npm install esbuild --ignore-scripts
   # Binary still works but CLI is slightly slower
   ```

3. **Manual binary download:**
   ```bash
   curl -fsSL https://esbuild.github.io/dl/v0.28.0 | sh
   ```

### Outdated Go Version Error

**Error:**
```
This version of esbuild requires Go 1.19 or later
```

**Solution:**
Update Go compiler:
```bash
# Download latest Go from https://go.dev/dl/
go version  # Should show go1.19 or later
```

### Minified Newlines Issue

**Problem:** Minified code has unexpected newlines.

**Cause:** Esbuild preserves some newlines for JavaScript engine compatibility.

**Solution:** This is intentional and correct. Some JavaScript engines have line length limits. If you need stricter minification, use terser as a post-processing step:

```json
{
  "scripts": {
    "build": "esbuild src/index.js --bundle --minify --outfile=dist/app.js && terser dist/app.js -o dist/app.js"
  }
}
```

### Top-Level Name Collisions

**Problem:** Variables from different modules collide after bundling.

**Example:**
```javascript
// module-a.js
export const config = { api: 'https://a.com' }

// module-b.js  
export const config = { api: 'https://b.com' }  // Collision!
```

**Solutions:**

1. **Use different variable names** (best practice)
2. **Wrap modules in IIFE:**
   ```bash
   esbuild app.js --bundle --format=iife --global-name=MyApp
   ```
3. **Use namespace imports:**
   ```javascript
   import * as A from './module-a'
   import * as B from './module-b'
   // Access as A.config, B.config
   ```

### Strict Mode Issues

**Problem:** Code relies on non-strict mode behavior.

**Symptoms:**
- `with` statement errors
- Implicit global variable errors
- `this` is undefined in functions

**Solutions:**

1. **Enable strict mode explicitly:**
   ```bash
   esbuild app.js --banner:js="'use strict';"
   ```

2. **Fix code for strict mode:**
   - Declare all variables with `let`, `const`, or `var`
   - Remove `with` statements
   - Use explicit `this` binding

3. **Disable for TypeScript files:**
   ```json
   {
     "compilerOptions": {
       "alwaysStrict": false
     }
   }
   ```

### Top-Level var in Modules

**Problem:** Using `var` at top level of ES modules causes issues.

**Example:**
```javascript
// module.js (ESM)
var globalVar = 1  // Problem: var is function-scoped, not module-scoped
```

**Solution:** Use `let` or `const`:
```javascript
export const globalVar = 1  // Correct: block-scoped
```

## Platform-Specific Issues

### Windows Path Issues

**Problem:** Forward slashes in paths don't work on Windows.

**Solution:** Esbuild handles path separators automatically, but for custom code:
```javascript
import { posix } from 'path'
const path = posix.join('dir', 'file.js')  // Uses forward slashes
```

### macOS ARM (Apple Silicon) vs Intel

**Problem:** esbuild installed on ARM Mac doesn't work with Rosetta (x64 Node).

**Solutions:**

1. **Use ARM version of Node.js:**
   ```bash
   # Download from https://nodejs.org/ (universal build includes ARM)
   node -v  # Should show ARM64 architecture
   ```

2. **Reinstall esbuild after switching architectures:**
   ```bash
   rm -rf node_modules/esbuild
   npm install
   ```

3. **Use esbuild-wasm as fallback:**
   ```bash
   npm install esbuild-wasm
   # Slower but works on all architectures
   ```

### Linux musl vs glibc

**Problem:** esbuild binary linked against glibc doesn't work on musl-based systems (Alpine Linux).

**Solution:** Alpine Linux uses `@esbuild/linux-musl-*` packages. Esbuild npm package should auto-detect, but if not:

```bash
# Manual installation for Alpine
npm install @esbuild/linux-musl-x64
```

## Build Configuration Issues

### TypeScript Not Transforming

**Problem:** TypeScript syntax remains in output.

**Causes and fixes:**

1. **Wrong loader:**
   ```bash
   # Wrong
   esbuild app.ts --outfile=app.js
   
   # Correct (need --bundle for TypeScript)
   esbuild app.ts --bundle --outfile=app.js
   ```

2. **File extension not detected:**
   ```bash
   esbuild app.txt --loader:.txt=ts --outfile=app.js
   ```

3. **Using transform API without loader:**
   ```javascript
   // Wrong
   await esbuild.transform(code)
   
   // Correct
   await esbuild.transform(code, { loader: 'ts' })
   ```

### JSX Not Transforming

**Problem:** JSX syntax errors in output.

**Solutions:**

1. **Use .jsx or .tsx extension:**
   ```bash
   mv app.js app.jsx
   esbuild app.jsx --bundle --outfile=app.js
   ```

2. **Specify loader for .js files:**
   ```bash
   esbuild app.js --loader:.js=jsx --bundle --outfile=app.js
   ```

3. **Configure JSX transform:**
   ```bash
   esbuild app.jsx --jsx=automatic --jsx-import-source=react --outfile=app.js
   ```

### CSS Not Included in Bundle

**Problem:** CSS imports don't appear in browser bundle.

**Cause:** Platform is set to node (CSS discarded for Node.js).

**Solution:** Ensure platform is browser:
```bash
# Default (browser)
esbuild app.js --bundle --outfile=app.js

# Explicit browser platform
esbuild app.js --bundle --platform=browser --outfile=app.js
```

### External Dependencies Not Working

**Problem:** External packages throw "module not found" at runtime.

**Cause:** Package marked as external but not installed.

**Solution:** Install external dependencies:
```bash
# If using --external:lodash
npm install lodash

# Or ensure package available in deployment environment
```

### Source Maps Not Working

**Problem:** Source maps don't map back to original files.

**Solutions:**

1. **Enable source maps:**
   ```bash
   esbuild app.ts --bundle --sourcemap=external --outfile=dist/app.js
   ```

2. **Set sourcefile option:**
   ```javascript
   await esbuild.build({
     sourcemap: 'external',
     sourcefile: 'src/app.ts',  // Filename in source map
   })
   ```

3. **Check browser DevTools:** Source maps must be loaded from same origin or CORS enabled.

## Advanced Topics

### Custom Target Environments

Define custom browser targets:

```bash
# Target specific versions
esbuild app.js --target=chrome91,firefox89,safari14,edge91 --outfile=app.js

# Or use ES version
esbuild app.js --target=es2020 --outfile=app.js
```

### Incremental Build Performance

**Tip:** Use context API for repeated builds:

```javascript
const ctx = await esbuild.context({
  entryPoints: ['src/index.ts'],
  bundle: true,
  outdir: 'dist',
})

// Fast incremental rebuilds
await ctx.rebuild()
await ctx.rebuild()
await ctx.rebuild()

await ctx.dispose()
```

### Memory Usage

Esbuild uses minimal memory compared to other bundlers. For very large projects:

1. **Use code splitting:**
   ```bash
   esbuild app.js --bundle --splitting --outdir=dist
   ```

2. **Exclude unnecessary files:**
   ```bash
   esbuild app.js --bundle --external:*/node_modules/* --outfile=app.js
   ```

3. **Use multiple builds:** Split large monorepos into separate builds.

### Debugging Build Errors

**Enable verbose logging:**
```bash
esbuild app.js --bundle --log-level=info --outfile=app.js
```

**Get detailed error locations:**
```javascript
const result = await esbuild.build(options)

result.errors.forEach(err => {
  console.error({
    text: err.text,
    location: `${err.location.file}:${err.location.line}:${err.location.column}`,
    notes: err.notes.map(n => n.text),
  })
})
```

### Migration from Other Bundlers

**From webpack:**
- Replace loaders with esbuild's built-in support or plugins
- Use `--external` for what was `externals` config
- CSS requires separate processing (use postcss)

**From rollup:**
- Similar plugin API but different callback names
- Esbuild has fewer plugins available
- Some rollup plugins may not have esbuild equivalents

**From parcel:**
- Esbuild is faster but less "zero-config"
- Manual configuration required for some features
- CSS/asset handling more explicit

## Getting Help

### Documentation

- Official docs: https://esbuild.github.io/
- GitHub repo: https://github.com/evanw/esbuild
- API reference: /api/ in official docs

### Community

- GitHub Issues: For bugs and feature requests
- Stack Overflow: Tag with `esbuild`
- Discord: Various JS framework Discords have esbuild channels

### Reporting Bugs

When reporting issues, include:
1. Esbuild version (`esbuild --version`)
2. Operating system and architecture
3. Minimal reproduction case
4. Command or API call that fails
5. Expected vs actual behavior
