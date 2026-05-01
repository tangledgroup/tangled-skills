# Configuration (deno.json)

## Overview

Configure Deno using a `deno.json` or `deno.jsonc` file. The configuration file supports JSON and JSON with comments (`.jsonc`). Deno auto-detects the file in the current working directory or parent directories. Override location with `--config` flag.

```bash
deno run --config ./custom/deno.json script.ts
```

## Dependencies

The `imports` field maps bare specifiers to URLs or paths:

```jsonc
{
  "imports": {
    "@std/assert": "jsr:@std/assert@^1.0.0",
    "chalk": "npm:chalk@5",
    "lodash": "npm:lodash@^4.17.21"
  }
}
```

Then use bare specifiers in code:

```typescript
import { assertEquals } from "@std/assert";
import chalk from "chalk";
```

### Custom Path Mappings

Map specifiers to local files or directories:

```jsonc
{
  "imports": {
    "foo": "./some/long/path/foo.ts",
    "bar/": "./some/folder/bar/",
    "@/": "./"
  }
}
```

```typescript
import * as foo from "foo";
import * as bar from "bar/file.ts";
import { MyUtil } from "@/util.ts";
```

### Overriding Packages with Links

Override dependencies with local packages (similar to `npm link`):

```jsonc
{
  "links": [
    "../some-local-package"
  ]
}
```

## Tasks

Define custom commands in the `tasks` field:

```jsonc
{
  "tasks": {
    "start": "deno run --allow-net --watch=static/,routes/,data/ dev.ts",
    "test": "deno test --allow-net",
    "lint": "deno lint",
    "format": "deno fmt"
  }
}
```

Execute tasks:

```bash
deno task start
deno task test
deno task lint
```

Deno also supports the `scripts` field in `package.json`:

```jsonc
{
  "scripts": {
    "dev": "vite dev",
    "build": "vite build"
  }
}
```

## Linting Configuration

Configure the built-in linter:

```jsonc
{
  "lint": {
    "include": ["src/"],
    "exclude": ["src/testdata/", "src/fixtures/**/*.ts"],
    "rules": {
      "tags": ["recommended"],
      "include": ["ban-untagged-todo"],
      "exclude": ["no-unused-vars"]
    }
  }
}
```

## Formatting Configuration

Configure the built-in formatter:

```jsonc
{
  "fmt": {
    "useTabs": false,
    "lineWidth": 80,
    "indentWidth": 2,
    "semiColons": true,
    "singleQuote": false,
    "proseWrap": "preserve",
    "include": ["src/"],
    "exclude": ["src/testdata/"]
  }
}
```

Available format options:

- `useTabs` — Use tabs instead of spaces
- `lineWidth` — Maximum line width
- `indentWidth` — Number of spaces per indent level
- `semiColons` — Whether to use semicolons
- `singleQuote` — Use single quotes instead of double quotes
- `proseWrap` — How to wrap prose text (`always`, `never`, `preserve`)
- `bracePosition` — Brace position (`sameLine`, `nextLine`, `maintain`, `sameLineUnlessHanging`)
- `trailingCommas` — Trailing comma style (`es5`, `none`)
- `jsx.bracketPosition` — JSX bracket position (`sameLine`, `nextLine`, `maintain`)
- `operatorPosition` — Operator position for line breaks (`before`, `after`)

## Lockfile

Generate a lockfile for reproducible dependency resolution:

```jsonc
{
  "lock": true
}
```

Or specify a custom path:

```jsonc
{
  "lock": "./custom/lock.json"
}
```

Run `deno install --lock=deno.lock --lock-write` to create or update the lockfile.

## TypeScript Compiler Options

Configure the TypeScript compiler:

```jsonc
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "checkJs": true,
    "jsx": "react-jsx",
    "jsxImportSource": "npm:preact"
  }
}
```

Deno runs TypeScript in strict mode by default.

## Unstable Features

Enable unstable features:

```jsonc
{
  "unstable": ["kv", "temporal", "ffi"]
}
```

Or via CLI: `deno run --unstable-kv script.ts`

## Publish Configuration

Configure publishing to JSR:

```jsonc
{
  "name": "@scope/my-package",
  "version": "1.0.0",
  "exports": "./mod.ts",
  "publish": {
    "include": ["src/**/*.ts"],
    "exclude": ["**/*.test.ts", "**/_testdata/"]
  }
}
```

## Permissions Configuration

Store default permissions in the config file:

```jsonc
{
  "permissions": {
    "read": true,
    "write": ["./data/"],
    "net": ["api.example.com"],
    "env": ["DATABASE_URL"],
    "run": ["node"]
  }
}
```

Per-task permissions override defaults:

```jsonc
{
  "permissions": {
    "read": true
  },
  "tasks": {
    "start": "deno run server.ts",
    "build": "deno run build.ts"
  },
  "test": {
    "permissions": {
      "read": true,
      "write": false,
      "net": false
    }
  },
  "bench": {
    "permissions": {
      "read": true
    }
  }
}
```

## Top-Level Exclude

Exclude files from Deno's analysis:

```jsonc
{
  "exclude": ["vendor/", "node_modules/legacy/"]
}
```
