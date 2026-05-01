# Runtime & Core

## Running Files

Use `bun run` to execute source files. TypeScript, JSX, and TSX are transpiled on the fly — no build step needed.

```bash
bun run index.js
bun run index.ts
bun run index.jsx
bun run index.tsx
```

Omit `run` for the "naked" form (identical behavior):

```bash
bun index.tsx
bun index.js
```

### Watch Mode

Restart automatically when files change:

```bash
bun --watch run index.tsx
```

Place Bun flags immediately after `bun`, not at the end of the command:

```bash
bun --watch run dev   # correct
bun run dev --watch   # wrong — flag passed to script, not bun
```

## Running package.json Scripts

```json
{
  "scripts": {
    "clean": "rm -rf dist && echo 'Done.'",
    "dev": "bun server.ts"
  }
}
```

```bash
bun run dev        # explicit form (recommended)
bun dev            # shorthand (fails if name conflicts with built-in bun command)
bun run            # list all available scripts
```

Bun executes scripts in a subshell (`bash`, `sh`, or `zsh` on Unix; bun shell on Windows). Lifecycle hooks (`pre<script>`, `post<script>`) are respected.

### `--bun` Flag

By default, Bun respects shebangs (e.g., `#!/usr/bin/env node`). Use `--bun` to force Bun runtime:

```bash
bun run --bun vite   # run vite with bun instead of node
```

### Filtering in Monorepos

Run scripts across multiple workspace packages:

```bash
bun run --filter "pkg-*" dev      # all packages matching pattern
bun run --filter "!pkg-c" dev     # exclude pkg-c
bun run --workspaces dev          # all workspaces
```

## bunfig.toml

Bun's behavior is configured via `bunfig.toml` in the project root. This file is optional — Bun works out of the box without it.

### Global vs Local

- **Local**: `bunfig.toml` in project root (alongside `package.json`)
- **Global**: `.bunfig.toml` at `$HOME/.bunfig.toml` or `$XDG_CONFIG_HOME/.bunfig.toml`

Local overrides global. CLI flags override bunfig settings.

### Runtime Configuration

```toml title="bunfig.toml"
# Scripts to run before any file or script execution
preload = ["./preload.ts"]

# JSX configuration (also supported in tsconfig.json)
jsx = "react"
jsxFactory = "h"
jsxFragment = "Fragment"
jsxImportSource = "react"

# Reduce memory at cost of performance
smol = true

# Log level: "debug" | "warn" | "error"
logLevel = "debug"

# Replace identifiers with constants
[define]
"process.env.API_URL" = "'https://api.example.com'"

# Custom file extension loaders
[loader]
".custom" = "tsx"

# Supported loaders: jsx, js, ts, tsx, css, file, json, toml, wasm, napi, base64, dataurl, text
```

### Environment Variables

Bun automatically loads `.env` files. Disable with:

```toml
env = false
# or
[env]
file = false
```

Explicit `--env-file` arguments still load even when default loading is disabled.

### Console Configuration

```toml
[console]
depth = 3   # default object inspection depth (default: 2)
```

### Serve Configuration

```toml
[serve]
port = 3000   # default port for Bun.serve
```

Also configurable via `--port` CLI flag or `BUN_PORT`, `PORT`, `NODE_PORT` environment variables.

### Test Runner Configuration

```toml
[test]
root = "./__tests__"
preload = ["./setup.ts"]
pathIgnorePatterns = ["vendor/**", "submodules/**"]
```

## TypeScript Setup

For editor autocomplete and type checking, install Bun's type declarations:

```bash
bun add -d @types/bun
```

Recommended `tsconfig.json`:

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "Preserve",
    "moduleDetection": "force",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true
  }
}
```

Note: Bun's transpiler is not a type checker. Use `tsc --noEmit` or a dedicated type checker for type validation.

## REPL

Bun includes an interactive REPL:

```bash
bun
```

The REPL supports TypeScript, JSX, and multi-line input. It has access to all Bun globals and built-in modules.

## Debugger

Debug Bun applications with the built-in debugger or external tools:

```bash
bun --inspect run server.ts    # start with debugger attached
bun --inspect-brk run server.ts # start and break on first line
```

Connect via Chrome DevTools at `chrome://inspect` or any protocol-compatible debugger. VS Code debug configuration:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Bun",
  "runtimeExecutable": "bun",
  "runtimeArgs": ["run", "${workspaceFolder}/server.ts"],
  "console": "integratedTerminal"
}
```

## Module Resolution

Bun supports both ES modules (ESM) and CommonJS:

- `.js` / `.cjs` → CommonJS by default
- `.mjs` → ES module
- `.ts` / `.tsx` → determined by `"type"` in package.json or `"module"` in tsconfig.json

Bun follows Node.js-style module resolution with support for:

- Relative imports (`./module`)
- Absolute imports from `node_modules`
- Bare specifiers (`react`, `lodash`)
- Conditional exports in package.json
- Field overrides and dual packages

## File System Router

Bun supports file-system based routing for full-stack applications. When using HTML imports with `Bun.serve`, files in specific directories can automatically map to routes, enabling framework-like patterns without external dependencies.
