# Esbuild Installation Methods

## Using npx (No Installation Required)

The quickest way to use esbuild without any installation:

```bash
# Use specific version
npx esbuild@0.28.0 app.js --bundle --outfile=bundle.js

# Use latest version
npx esbuild@latest app.js --bundle --outfile=bundle.js

# Transform via stdin
echo 'let x: number = 1' | npx esbuild@0.28.0 --loader=ts
```

**Pros:** No installation needed, always uses latest version
**Cons:** Downloads on first use, slightly slower startup

## Using npm (Recommended)

Install esbuild as a development dependency:

```bash
npm install --save-dev esbuild
# or
yarn add -D esbuild
# or
pnpm add -D esbuild
```

This installs the `esbuild` package which includes:
- A JavaScript shim for the API
- Platform-specific native binary (optional dependency)

Run the CLI:

```bash
./node_modules/.bin/esbuild app.js --bundle --outfile=bundle.js
```

Add to package.json scripts:

```json
{
  "scripts": {
    "build": "esbuild src/index.tsx --bundle --minify --outdir=dist",
    "dev": "esbuild src/index.tsx --bundle --sourcemap --watch"
  }
}
```

Then run with `npm run build` or `npm run dev`.

### NPM Installation Flags

**Default (recommended):**
```bash
npm install esbuild
```
Installs binary and runs install script for optimization.

**With --ignore-scripts:**
```bash
npm install esbuild --ignore-scripts
```
Binary still installs but uses JavaScript shim (slightly slower CLI).

**With --no-optional:**
```bash
npm install esbuild --no-optional
```
Install script downloads binary manually (may fail behind proxies).

**Both flags (broken):**
```bash
npm install esbuild --ignore-scripts --no-optional
```
DO NOT USE - package will be broken without binary.

## Direct Binary Download (Unix)

Download pre-built binary without npm:

```bash
# Download specific version
curl -fsSL https://esbuild.github.io/dl/v0.28.0 | sh

# Download latest
curl -fsSL https://esbuild.github.io/dl/latest | sh
```

Or manually download from npm registry:

```bash
# Linux x64 example
curl -O https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.28.0.tgz
tar xzf ./linux-x64-0.28.0.tgz
./package/bin/esbuild --version
```

**Supported platforms:**

| Package | OS | Architecture |
|---------|-----|--------------|
| `@esbuild/linux-x64` | Linux | x64 |
| `@esbuild/linux-arm64` | Linux | arm64 |
| `@esbuild/darwin-x64` | macOS | x64 |
| `@esbuild/darwin-arm64` | macOS | arm64 (Apple Silicon) |
| `@esbuild/win32-x64` | Windows | x64 |
| `@esbuild/win32-arm64` | Windows | arm64 |
| `@esbuild/android-arm64` | Android | arm64 |
| `@esbuild/freebsd-x64` | FreeBSD | x64 |
| `@esbuild/openbsd-x64` | OpenBSD | x64 |

**Pros:** No npm required, works in minimal environments
**Cons:** Unix only (needs shell), no plugin support without API

## WebAssembly Version (Cross-Platform)

Install `esbuild-wasm` for platforms without native binaries:

```bash
npm install --save-dev esbuild-wasm
```

Usage is identical to native version but 10x slower:

```bash
./node_modules/.bin/esbuild app.js --bundle --outfile=bundle.js
```

**Pros:** Works on any platform, no native binary needed
**Cons:** 10x slower, no plugins, no serve mode, single-threaded

Use only when native version unavailable (unsupported platforms, browser-only environments).

## Deno Support

Esbuild works with Deno via deno.land:

```typescript
// Native version (requires --allow-run)
import * as esbuild from 'https://deno.land/x/esbuild@v0.28.0/mod.js'

let result = await esbuild.transform('let x: number = 1', { loader: 'ts' })
console.log(result.code)

await esbuild.stop() // Required for Deno to exit
```

WebAssembly version (no --allow-run needed):

```typescript
import * as esbuild from 'https://deno.land/x/esbuild@v0.28.0/wasm.js'

let result = await esbuild.transform('let x: number = 1', { loader: 'ts' })
console.log(result.code)

await esbuild.stop()
```

**Note:** Must call `stop()` when done - Deno won't exit otherwise.

## Building from Source

Build esbuild from source code:

```bash
# Install Go (https://go.dev/dl/)
go version  # Should be Go 1.19+

# Clone and build
git clone --depth 1 --branch v0.28.0 https://github.com/evanw/esbuild.git
cd esbuild
go build ./cmd/esbuild

# Build for different platform
GOOS=linux GOARCH=arm64 go build ./cmd/esbuild
```

**Pros:** Latest development version, custom builds
**Cons:** Requires Go compiler, CLI-only (no plugins without API)

## Cross-Platform Installation Issues

### Docker and WSL

Cannot copy `node_modules` between platforms. Solutions:

1. **Don't copy node_modules:** Copy package.json only, run `npm ci` in container
2. **Use Yarn with supportedArchitectures:**

```yaml
# .yarnrc.yml
supportedArchitectures:
  cpu:
    - x64
    - arm64
  os:
    - linux
    - darwin
    - win32
```

### macOS ARM (Apple Silicon) vs Intel

If installing with ARM npm but running under Rosetta (x64 node):

1. Use ARM version of Node.js instead
2. Reinstall esbuild after switching architectures
3. Use `esbuild-wasm` as fallback

### Yarn Plug'n'Play

Esbuild supports Yarn PnP natively. Ensure current working directory contains `.pnp.cjs` or `.pnp.js`:

```bash
# Run esbuild from project root with PnP manifest
yarn esbuild app.tsx --bundle --outfile=dist/bundle.js
```

For best performance, run esbuild directly without Yarn CLI wrapper (10x faster).

## Verification

Verify installation:

```bash
# Check version
esbuild --version

# Test basic transformation
echo 'let x: number = 1' | esbuild --loader=ts
# Should output: let x = 1;
```
