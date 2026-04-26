# CLI Reference

## Execution Commands

**`deno run`** — Run a script

```bash
deno run script.ts
deno run --allow-net --allow-read server.ts
deno run --check script.ts          # Type check before running
deno run --watch script.ts          # Watch mode (restart on file change)
deno run --unstable-kv script.ts    # Enable unstable features
```

**`deno serve`** — Run a web server with automatic restart and signal handling

```bash
deno serve server.ts
```

**`deno task`** — Run a task defined in deno.json

```bash
deno task start
deno task test
deno run -N task build              # List available tasks
```

**`deno repl`** — Start an interactive read-eval-print loop

```bash
deno repl
```

**`deno eval`** — Evaluate a script from the command line

```bash
deno eval 'console.log("Hello")'
```

## Dependency Management

**`deno add`** — Add dependencies to deno.json

```bash
deno add jsr:@std/fs
deno add npm:express@4
```

**`deno install`** — Install a dependency or create a script alias

```bash
# Resolve all dependencies
deno install

# Create a global script alias
deno install -n my-server --allow-net ./server.ts
```

**`deno uninstall`** — Remove an installed script alias

```bash
deno uninstall my-server
```

**`deno remove`** — Remove dependencies from deno.json

```bash
deno remove jsr:@std/fs
```

**`deno outdated`** — View or update outdated dependencies

```bash
deno outdated
deno outdated --update              # Update to latest versions
```

**`deno audit`** — Audit dependencies for known vulnerabilities

```bash
deno audit
deno audit --json                   # JSON output
```

**`deno approve-scripts`** — Manage lifecycle scripts of npm packages

```bash
deno approve-scripts
```

## Tooling Commands

**`deno check`** — Type check without running

```bash
deno check module.ts
deno check --all module.ts          # Include remote modules and npm packages
deno check --doc module.ts          # Check JSDoc code snippets
deno check --doc-only README.md     # Check markdown code blocks
```

**`deno test`** — Run tests

```bash
deno test
deno test --allow-read=.
deno test --parallel
deno test --filter="database"
deno test --coverage=cov/
deno test --fail-fast
```

**`deno bench`** — Run benchmarks

```bash
deno bench
deno bench --filter="regex"
```

**`deno lint`** — Lint code

```bash
deno lint
deno lint src/
```

**`deno fmt`** — Format code

```bash
deno fmt
deno fmt src/
deno fmt --check                    # Check without modifying files
```

**`deno compile`** — Compile to standalone executable

```bash
deno compile --allow-net server.ts
deno compile --output=my-server server.ts
```

**`deno bundle`** — Bundle module and dependencies into a single file

```bash
deno bundle app.ts bundled.js
```

**`deno coverage`** — Generate coverage reports

```bash
deno coverage cov/
deno coverage cov/ --html
deno coverage cov/ --lcov
```

**`deno doc`** — Generate documentation

```bash
deno doc module.ts
deno doc --json module.ts > docs.json
```

**`deno info`** — Inspect module and dependencies

```bash
deno info module.ts
deno info --json module.ts
```

**`deno types`** — Print runtime type definitions

```bash
deno types > deno.d.ts
```

**`deno init`** — Create a new project

```bash
deno init my-project
```

**`deno create`** — Scaffold from a template

```bash
deno create
```

**`deno publish`** — Publish to JSR

```bash
deno publish
deno publish --dry-run
deno publish --token=<token>
```

**`deno deploy`** — Deploy to Deno Deploy

```bash
deno deploy --project=my-project server.ts
```

**`deno lsp`** — Start the language server

```bash
deno lsp
```

**`deno completions`** — Generate shell completions

```bash
deno completions bash
deno completions zsh
deno completions fish
```

**`deno upgrade`** — Upgrade Deno

```bash
deno upgrade
deno upgrade 2.0.0
deno upgrade --canary
```

**`deno clean`** — Clean the cache

```bash
deno clean
deno clean -f                       # Force clean
```

**`deno jupyter`** — Run a Jupyter notebook kernel

```bash
deno jupyter
```

**`deno x`** — Run an npm or JSR package directly

```bash
deno x jsr:@std/http/file-server
deno x npm:chalk@5 "Hello"
```

## Debugging Flags

```bash
deno run --inspect script.ts       # Start inspector, run immediately
deno run --inspect-wait script.ts  # Wait for debugger before running
deno run --inspect-brk script.ts   # Break on first line (most common)
```
