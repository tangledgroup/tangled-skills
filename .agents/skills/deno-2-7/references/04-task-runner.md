# Task Runner Guide

Deno's built-in task runner allows you to define and execute custom commands specific to your codebase. This guide covers task syntax, dependencies, wildcards, and advanced features.

## Basic Usage

### Defining Tasks

Create `deno.json` in your project root:

```json
{
  "tasks": {
    "start": "deno run --allow-net server.ts",
    "test": "deno test --allow-read --allow-env",
    "build": "deno bundle src/mod.ts dist/bundle.js"
  }
}
```

### Running Tasks

```bash
# Run a task
deno task start

# List all tasks
deno task

# Run task with arguments
deno task build --arg1 --arg2
```

## Task Syntax

### Simple String Command

```json
{
  "tasks": {
    "dev": "deno run -A --watch=src/ server.ts"
  }
}
```

### Object Form with Description

```json
{
  "tasks": {
    "dev": {
      "description": "Start development server with hot reload",
      "command": "deno run -A --watch=src/ server.ts"
    }
  }
}
```

### Sequential Commands

Run multiple commands in sequence:

```json
{
  "tasks": {
    "deploy": [
      "deno task test",
      "deno task build",
      "deno run scripts/deploy.ts"
    ]
  }
}
```

All commands must succeed for the task to complete.

## Task Dependencies

### Declaring Dependencies

```json
{
  "tasks": {
    "build:client": "deno run -A client/build.ts",
    "build:server": "deno run -A server/build.ts",
    "build": {
      "command": "deno run -A build.ts",
      "dependencies": ["build:client", "build:server"]
    }
  }
}
```

Running `deno task build` will:
1. Execute `build:client` and `build:server` in parallel
2. Wait for both to complete successfully
3. Execute the `build` command

### Dependency Graph

```json
{
  "tasks": {
    "lint": "deno lint",
    "typecheck": "deno check",
    "test": "deno test -A",
    "validate": {
      "dependencies": ["lint", "typecheck", "test"]
    },
    "build": {
      "command": "deno bundle src/mod.ts dist/bundle.js",
      "dependencies": ["validate"]
    }
  }
}
```

Running `deno task build` executes:
- `lint`, `typecheck`, `test` (in parallel)
- `validate` (after all above complete)
- `build` command (after validate completes)

## Wildcard Matching

### Running Multiple Tasks

Use wildcards to run multiple tasks:

```bash
# Run all tasks starting with "build:"
deno task "build:*"

# Run all tasks ending with ":test"
deno task "*:test"

# Run tasks matching pattern
deno task "test:*"
```

Example:

```json
{
  "tasks": {
    "build:frontend": "deno run build/frontend.ts",
    "build:backend": "deno run build/backend.ts",
    "build:shared": "deno run build/shared.ts"
  }
}
```

```bash
# Runs all three build tasks in parallel
deno task "build:*"
```

### Important Notes

- Always quote wildcard patterns to prevent shell expansion: `"build:*"` not `build:*`
- Matching tasks run in parallel, not sequentially
- Use dependencies for ordered execution

## Environment Variables

### Inheriting Environment Variables

Tasks inherit environment variables from the parent process:

```bash
# API_KEY is available in task
API_KEY=secret deno task deploy
```

### Setting Environment Variables in Task

```json
{
  "tasks": {
    "test": {
      "command": "deno test -A",
      "env": {
        "NODE_ENV": "test",
        "DATABASE_URL": "postgresql://localhost/test"
      }
    }
  }
}
```

### Environment Variable Syntax

Use shell-like syntax in task commands:

```json
{
  "tasks": {
    "deploy": "deno run -A deploy.ts $ENVIRONMENT $REGION"
  }
}
```

Run with:
```bash
ENVIRONMENT=production REGION=us-east-1 deno task deploy
```

### Special Environment Variables

Deno provides these special variables:

| Variable | Description |
|----------|-------------|
| `INIT_CWD` | Directory where `deno task` was run from |
| `DENO_TASK_NAME` | Name of the current task |
| `DENO` | Path to the Deno binary |

Example using `INIT_CWD`:

```json
{
  "tasks": {
    "show-cwd": "echo $INIT_CWD",
    "run-from-here": "cd $INIT_CWD && pwd"
  }
}
```

## Shell Features

### Command Substitution

```json
{
  "tasks": {
    "version": "echo Version: $(deno --version | cut -d' ' -f2)",
    "timestamp": "date +%Y%m%d_%H%M%S"
  }
}
```

### Pipelines

```json
{
  "tasks": {
    "list-typescript": "find . -name '*.ts' | grep -v node_modules",
    "count-lines": "cat src/*.ts | wc -l"
  }
}
```

### Redirects

```json
{
  "tasks": {
    "log-output": "deno task build > build.log 2>&1",
    "append-log": "deno task test >> test-results.log"
  }
}
```

### Conditional Execution

```json
{
  "tasks": {
    "build-if-changed": "[ -f .git/HEAD ] && deno task build || echo 'No changes'",
    "test-or-skip": "deno task test || echo 'Tests failed, continuing...'"
  }
}
```

### Negate Exit Code

```json
{
  "tasks": {
    "check-not-exists": "! test -f dist/bundle.js",
    "ensure-missing": "! deno test --filter skipped"
  }
}
```

### Boolean Lists

Run commands with short-circuit evaluation:

```json
{
  "tasks": {
    "safe-rm": "[ -d dist ] && rm -rf dist",
    "create-if-missing": "[ ! -d logs ] && mkdir logs"
  }
}
```

## Working Directory

### Default Behavior

Tasks run with the directory containing `deno.json` as the working directory, regardless of where you execute `deno task` from.

### Overriding Working Directory

Use `INIT_CWD` to change to the directory where the task was invoked:

```json
{
  "tasks": {
    "show-both": [
      "echo 'Config dir: $(pwd)'",
      "echo 'Invoked from: $INIT_CWD'",
      "cd $INIT_CWD && echo 'Now in: $(pwd)'"
    ]
  }
}
```

## Async Commands

Run commands without waiting for completion:

```json
{
  "tasks": {
    "dev": [
      "& deno run -A --watch=src/ server.ts",
      "& deno run -A --watch=src/ client.ts"
    ]
  }
}
```

The `&` prefix runs the command in the background. The task completes immediately, but the processes continue running.

## Cross-Platform Shebang

Use `deno run` for cross-platform script execution:

```json
{
  "tasks": {
    "migrate": "deno run -A scripts/migrate.ts",
    "seed": "deno run -A scripts/seed.ts"
  }
}
```

Instead of relying on shebang lines which don't work consistently on Windows.

## Glob Expansion

Expand file patterns:

```json
{
  "tasks": {
    "lint-all": "deno lint src/**/*.ts",
    "format-all": "deno fmt src/**/*.ts"
  }
}
```

Note: Glob expansion depends on the shell. For consistent behavior, use Deno's file APIs in scripts.

## Shell Options

Configure shell behavior:

```json
{
  "tasks": {
    "strict": {
      "command": "set -e && deno task build",
      "description": "Run build with strict mode (exit on error)"
    }
  }
}
```

## Built-in Commands

Deno task supports these built-in commands:

### `deno`

Execute Deno subcommands:

```json
{
  "tasks": {
    "check": "deno check --all",
    "lint": "deno lint",
    "fmt": "deno fmt --check",
    "test": "deno test -A",
    "cache": "deno cache src/mod.ts",
    "bundle": "deno bundle src/mod.ts dist/bundle.js",
    "compile": "deno compile -A -o myapp src/main.ts",
    "info": "deno info",
    "outdated": "deno outdated",
    "remove": "deno remove --force"
  }
}
```

### `node` and `npx`

If Node.js is installed, you can use it in tasks:

```json
{
  "tasks": {
    "prettier": "npx prettier --write .",
    "eslint": "node node_modules/eslint/bin/eslint.js ."
  }
}
```

## Package.json Support

Deno task can read tasks from `package.json`:

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "dev": "ts-node-dev src/index.ts"
  }
}
```

Run with:
```bash
deno task build
deno task test
```

Deno will execute these using Node.js if available, or show an error.

## Advanced Patterns

### Multi-Step Build Pipeline

```json
{
  "tasks": {
    "clean": "rm -rf dist",
    "typecheck": "deno check --all",
    "lint": "deno lint",
    "test": "deno test -A --coverage",
    "bundle": "deno bundle src/mod.ts dist/bundle.js",
    "minify": "deno run -A scripts/minify.ts dist/bundle.js dist/bundle.min.js",
    "hash": "deno run -A scripts/hash.ts dist/bundle.min.js",
    "build": {
      "command": "echo 'Build complete!'",
      "dependencies": ["clean", "typecheck", "lint", "test", "bundle", "minify", "hash"]
    }
  }
}
```

### Development Workflow

```json
{
  "tasks": {
    "dev:server": "deno run -A --watch=src/ server.ts",
    "dev:client": "deno run -A --watch=static/ client.ts",
    "dev": {
      "command": "echo 'Starting development mode...'",
      "dependencies": ["dev:server", "dev:client"]
    },
    "debug": "deno run --inspect-brk -A server.ts"
  }
}
```

### Database Migrations

```json
{
  "tasks": {
    "migrate": "deno run -A scripts/migrate.ts up",
    "migrate:down": "deno run -A scripts/migrate.ts down",
    "migrate:status": "deno run -A scripts/migrate.ts status",
    "seed": "deno run -A scripts/seed.ts",
    "db:setup": {
      "command": "deno task seed",
      "dependencies": ["migrate"]
    },
    "db:reset": {
      "command": "deno task db:setup",
      "dependencies": ["migrate:down"]
    }
  }
}
```

### Testing with Coverage

```json
{
  "tasks": {
    "test": "deno test -A",
    "test:watch": "deno test -A --watch",
    "test:coverage": "deno test -A --coverage=coverage",
    "coverage": "deno coverage coverage --lcov > coverage.lcov",
    "coverage:html": "genhtml coverage.lcov -o coverage/html"
  }
}
```

## Options

### Task Command Options

```bash
# List all tasks with descriptions
deno task

# Run task from specific config file
deno task --config=deno.prod.json build

# Don't follow dependencies
deno task --no-deps build

# Show task execution graph
deno task --help
```

### Configuration File Options

Specify custom config location:

```bash
deno task --config=deno.dev.json dev
```

## Error Handling

### Exit Codes

Tasks inherit exit codes from commands:
- `0`: Success
- Non-zero: Failure (stops dependency chain)

### Error Messages

Deno provides helpful error messages:

```
error: Task not found: 'deploy'
Available tasks:
  - build
  - test
  - lint
```

### Handling Failures

Use shell operators to handle errors:

```json
{
  "tasks": {
    "test-or-continue": "deno test -A || echo 'Tests failed but continuing'",
    "retry": "deno task build || sleep 5 && deno task build"
  }
}
```

## Best Practices

### Organize Tasks by Category

```json
{
  "tasks": {
    "build:frontend": "...",
    "build:backend": "...",
    "test:unit": "...",
    "test:integration": "...",
    "deploy:staging": "...",
    "deploy:production": "..."
  }
}
```

### Document Task Purpose

```json
{
  "tasks": {
    "deploy:production": {
      "description": "Deploy to production (requires PROD_KEY env var)",
      "command": "deno run -A deploy.ts production"
    }
  }
}
```

### Use Dependencies for Ordering

```json
{
  "tasks": {
    "build": "...",
    "test": {
      "command": "...",
      "dependencies": ["build"]  // Ensure build runs first
    }
  }
}
```

### Keep Tasks Idempotent

Design tasks to be safe to run multiple times:

```json
{
  "tasks": {
    "clean": "rm -rf dist",  // Safe to run multiple times
    "build": "deno bundle src/mod.ts dist/bundle.js"  // Overwrites existing
  }
}
```

## Related Topics

- [TypeScript Configuration](03-typescript.md) - Type-checking tasks
- [Testing Guide](05-testing.md) - Test runner integration
- [API Reference](06-api-reference.md) - Running subprocesses from code
