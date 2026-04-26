# Debugging and Profiling

## Chrome DevTools Integration

Deno supports the V8 Inspector Protocol, enabling debugging with Chrome DevTools, VSCode, and JetBrains IDEs.

### Inspect Flags

```bash
# Start inspector, run code immediately
deno run --inspect script.ts

# Wait for debugger to connect before running
deno run --inspect-wait script.ts

# Break on first line (most commonly used)
deno run --inspect-brk script.ts
```

The `--inspect-brk` flag is the most practical — it waits for a debugger connection and breaks on the first line, giving you time to set breakpoints.

### Using Chrome DevTools

1. Run with `--inspect-brk`:
   ```bash
   deno run --inspect-brk -RN jsr:@std/http/file-server
   ```
2. Open `chrome://inspect` in Chrome or Edge
3. Click "Inspect" next to the Deno target
4. DevTools opens with execution paused on the first line
5. Set breakpoints, step through code, inspect variables

### VSCode Integration

Create a `.vscode/launch.json`:

```jsonc
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Deno Debug",
      "program": "${workspaceFolder}/server.ts",
      "runtimeExecutable": "deno",
      "runtimeArgs": ["run", "--allow-all"],
      "console": "integratedTerminal"
    }
  ]
}
```

### JetBrains IDEs

JetBrains IDEs (WebStorm, IntelliJ) use `--inspect-brk` by default when debugging Deno scripts. Configure the run configuration to use `deno` as the interpreter.

## Logging

Control log verbosity:

```bash
# Show debug-level logs
deno run --log-level=debug script.ts
```

## System Call Tracing

Trace system operations:

```bash
deno run --strace-ops script.ts
```

## CPU Profiling

Generate CPU profiles:

```bash
# Profile for 10 seconds, output to file
deno run --profile=profile.cpuprofile script.ts
```

### Analyzing Profiles

Open the `.cpuprofile` file in Chrome DevTools:
1. Open `chrome://inspect`
2. Go to the Performance tab
3. Load the profile file
4. View flamegraph and timeline

### Example: Markdown Report

```bash
deno run --profile=profile.cpuprofile script.ts
# Then use a tool to convert to readable format
```

## TypeScript Debugging

Deno compiles TypeScript on-the-fly and provides source maps automatically. When debugging in DevTools, you see the original TypeScript code, not compiled JavaScript.

## Permission Debugging

Enable stack traces for permission requests:

```bash
# Show where each permission is requested from
DENO_TRACE_PERMISSIONS=1 deno run script.ts
```

Log all permission accesses:

```bash
# Write JSONL audit log
DENO_AUDIT_PERMISSIONS=./audit.log deno run script.ts
```

## TLS Debugging

Debug TLS certificate issues:

```bash
# Use Mozilla's CA store instead of system
DENO_TLS_CA_STORE=mozilla deno run script.ts
```
