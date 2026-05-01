# Security and Permissions

## Key Principles

Deno is secure by default. Code has no access to sensitive APIs unless explicitly granted:

- **No I/O by default** — No filesystem, network, environment variable, or subprocess access
- **Code execution unrestricted** — Any JS/TS/Wasm code can be executed via eval, dynamic imports, web workers
- **Shared data between invocations** — Built-in caching and KV storage allow data sharing across runs of the same application
- **Same privilege level per thread** — All code on the same thread shares the same permissions
- **No privilege escalation** — Code cannot escalate privileges without explicit user consent
- **Static module graph** — Files in the initial static import graph can be imported without read permission restrictions

## Permission Flags

Grant permissions with command-line flags:

```bash
# Grant all permissions (disables sandbox — use with caution)
deno run -A script.ts
deno run --allow-all script.ts

# Individual permissions
deno run --allow-read script.ts
deno run --allow-write script.ts
deno run --allow-net script.ts
deno run --allow-env script.ts
deno run --allow-run script.ts
deno run --allow-ffi script.ts
```

### File System Access

```bash
# Allow all reads
deno run --allow-read script.ts

# Allow specific paths
deno run --allow-read=foo.txt,bar.txt script.ts
deno run --allow-read=node_modules script.ts  # Directory and subdirectories

# Allow all writes
deno run --allow-write script.ts
deno run --allow-write=foo.txt script.ts
```

### Network Access

```bash
# Allow all network
deno run --allow-net script.ts

# Allow specific hosts
deno run --allow-net=example.com,api.example.com:443 script.ts
```

### Environment Variables

```bash
# Allow all environment access
deno run --allow-env script.ts

# Allow specific variables
deno run --allow-env=DATABASE_URL,API_KEY script.ts
```

### Subprocesses

```bash
# Allow spawning any subprocess
deno run --allow-run script.ts

# Allow specific commands
deno run --allow-run=git,node script.ts
```

### FFI Access

```bash
# Allow loading native libraries
deno run --allow-ffi script.ts
deno run --allow-ffi=./libexample.so script.ts
```

## Deny Flags

Deny flags take precedence over allow flags:

```bash
# Allow /etc but deny /etc/shadow
deno run --allow-read=/etc --deny-read=/etc/shadow script.ts

# Deny all reads (disables prompts)
deno run --deny-read script.ts
```

Available deny flags: `--deny-read`, `--deny-write`, `--deny-net`, `--deny-env`, `--deny-run`.

## Permission Prompts

When running interactively, Deno prompts for permissions on first access. Prompts are suppressed when stdout/stderr are not a TTY or when `--no-prompt` is passed.

## Permissions in deno.json

Store permissions in the configuration file:

```jsonc
{
  "tasks": {
    "start": "deno run server.ts"
  },
  "permissions": {
    "read": true,
    "write": ["./data/"],
    "net": ["api.example.com"],
    "env": ["DATABASE_URL"],
    "run": ["node"]
  }
}
```

### Named Permission Sets

Define reusable permission sets:

```jsonc
{
  "permissions": {
    "default": {
      "read": true,
      "net": ["api.example.com"]
    }
  },
  "tasks": {
    "start": "deno run server.ts",
    "test": "deno test"
  },
  "test": {
    "permissions": {
      "read": true,
      "write": false
    }
  }
}
```

## Permission Audit

Track permission usage:

```bash
# Log all permission accesses to a file (JSONL format)
DENO_AUDIT_PERMISSIONS=./audit.log deno run script.ts

# Enable stack traces for permissions
DENO_TRACE_PERMISSIONS=1 deno run script.ts
```

## Security Warning for FFI

Native libraries loaded via FFI have the same access level as the Deno process itself. They can:
- Access the filesystem
- Make network connections
- Access environment variables
- Execute system commands

Always trust the native libraries you load through FFI.
