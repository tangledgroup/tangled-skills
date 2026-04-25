# Permissions and Security

Deno's security model requires explicit permission grants for accessing system resources. This page covers the permissions model, how to grant/revoke permissions, and security best practices.

## Permission Types

Deno has the following permission categories:

| Permission | CLI Flag | Description |
|------------|----------|-------------|
| `read` | `--allow-read` | Read files from filesystem |
| `write` | `--allow-write` | Write files to filesystem |
| `net` | `--allow-net` | Make network connections |
| `env` | `--allow-env` | Access environment variables |
| `run` | `--allow-run` | Execute subprocesses |
| `ffi` | `--allow-ffi` | Load native dynamic libraries |
| `sys` | `--allow-sys` | Access system information |
| `hrtime` | `--allow-hrtime` | Access high-resolution time |

## Granting Permissions

### Global Permissions

Grant permission for all resources:

```bash
# Allow all file reads
deno run --allow-read script.ts

# Allow all network access
deno run --allow-net script.ts

# Allow all environment variables
deno run --allow-env script.ts
```

### Path-Specific Permissions

Restrict access to specific paths:

```bash
# Read only from ./data directory
deno run --allow-read=./data script.ts

# Write only to ./output directory
deno run --allow-write=./output script.ts

# Multiple paths (comma-separated)
deno run --allow-read=./data,./config script.ts

# Load FFI libraries from specific path
deno run --allow-ffi=./lib script.ts
```

### Network Permissions

Restrict network access to specific hosts:

```bash
# Allow all network access
deno run --allow-net script.ts

# Allow specific hosts
deno run --allow-net=api.example.com,localhost script.ts

# Allow specific host and port
deno run --allow-net=api.example.com:443 script.ts

# Allow localhost on any port
deno run --allow-net=localhost:* script.ts
```

### Environment Variable Permissions

Control which environment variables are accessible:

```bash
# Allow all environment variables
deno run --allow-env script.ts

# Allow specific variables
deno run --allow-env=DATABASE_URL,API_KEY script.ts

# Allow variables matching pattern
deno run --allow-env=DATABASE_* script.ts
```

### Subprocess Permissions

Control which commands can be executed:

```bash
# Allow all subprocesses
deno run --allow-run script.ts

# Allow specific commands
deno run --allow-run=git,node script.ts

# Allow command with arguments (matches command only)
deno run --allow-run=git script.ts
# Allows: git, git status, git commit, etc.
```

## Denying Permissions

Use `--deny-*` flags to explicitly deny access even when broader permissions are granted:

```bash
# Allow reading from /data but deny /data/secrets
deno run --allow-read=/data --deny-read=/data/secrets script.ts

# Allow all network except localhost:8080
deno run --allow-net --deny-net=localhost:8080 script.ts
```

This creates a "partial" permission state where some paths are denied within allowed ranges.

## Runtime Permission API

Query and request permissions at runtime using `Deno.permissions`:

### Query Permissions

Check if a permission is granted:

```typescript
// Check read permission for specific path
const status = await Deno.permissions.query({
  name: "read",
  path: "/etc/passwd"
});

console.log(status.state); // "granted", "prompt", or "denied"
console.log(status.partial); // true if some subpaths are denied
```

Synchronous version:
```typescript
const status = Deno.permissions.querySync({
  name: "read",
  path: "/etc/passwd"
});
```

### Request Permissions

Request permission from user at runtime:

```typescript
// Request read permission
const status = await Deno.permissions.request({
  name: "read",
  path: "./data"
});

// User will be prompted if state is "prompt"
// If already granted or denied, returns current state
```

### Revoke Permissions

Revoke a previously granted permission:

```typescript
const status = await Deno.permissions.revoke({
  name: "read",
  path: "./data"
});

// State changes from "granted" to "prompt"
```

## Permission States

Permissions have three states:

| State | Description |
|-------|-------------|
| `granted` | Permission was granted via CLI or runtime request |
| `prompt` | Permission not yet decided; user will be prompted on request |
| `denied` | Permission was explicitly denied; won't prompt again |

## Permission Descriptors

Permission descriptors define what resource is being accessed:

```typescript
// Read permission descriptor
const readDesc = {
  name: "read",
  path: "/foo/bar"
} as const;

// Write permission descriptor
const writeDesc = {
  name: "write",
  path: "/foo/bar"
} as const;

// Network permission descriptor (host only)
const netDesc1 = {
  name: "net"
} as const;

// Network permission descriptor (host:port)
const netDesc2 = {
  name: "net",
  host: "127.0.0.1:8000"
} as const;

// Environment variable descriptor
const envDesc = {
  name: "env",
  variable: "DATABASE_URL"
} as const;

// Subprocess permission descriptor
const runDesc = {
  name: "run",
  command: "git"
} as const;

// FFI permission descriptor
const ffiDesc = {
  name: "ffi",
  path: "./lib/native.so"
} as const;

// High-resolution time descriptor
const hrtimeDesc = {
  name: "hrtime"
} as const;

// System information descriptor
const sysDesc = {
  name: "sys",
  kind: "osRelease"
} as const;
```

## Permission Strength

Permissions have a hierarchical relationship. A permission is "stronger than" another if granting the first implies granting the second:

```typescript
// Global read is stronger than path-specific read
const globalRead = { name: "read" } as const;
const pathRead = { name: "read", path: "/foo" } as const;
// globalRead is stronger than pathRead

// Parent directory is stronger than child
const parentRead = { name: "read", path: "/foo" } as const;
const childRead = { name: "read", path: "/foo/bar" } as const;
// parentRead is stronger than childRead
```

Implications:
1. If `desc1` is stronger than `desc2`, and `desc1` queries to "granted", then `desc2` must also be "granted"
2. If `desc2` queries to "denied", then `desc1` must also be "denied"

## Security Best Practices

### Principle of Least Privilege

Always grant the minimum permissions required:

```bash
# ❌ Bad: Grant all permissions
deno run -A script.ts

# ✅ Good: Grant only needed permissions
deno run --allow-read=./config --allow-net=api.example.com script.ts
```

### Use Path Restrictions

Restrict filesystem access to specific directories:

```bash
# ❌ Bad: Allow all file reads
deno run --allow-read script.ts

# ✅ Good: Restrict to project directory
deno run --allow-read=./ script.ts
```

### Validate External Input

Never trust external input even with restricted permissions:

```typescript
// ❌ Dangerous: User-controlled path
const filename = req.url.searchParams.get("file");
const content = await Deno.readTextFile(filename);

// ✅ Safe: Validate and restrict path
const filename = req.url.searchParams.get("file");
const safePath = new URL(`./uploads/${filename}`, import.meta.url);
if (!safePath.pathname.startsWith("./uploads/")) {
  throw new Error("Invalid path");
}
const content = await Deno.readTextFile(safePath);
```

### Handle Permission Errors Gracefully

Check permissions before operations and provide helpful errors:

```typescript
async function readConfig(path: string): Promise<string> {
  const status = await Deno.permissions.query({ name: "read", path });
  
  if (status.state === "denied") {
    throw new Error(
      `Permission denied: Cannot read ${path}. ` +
      `Run with --allow-read=${path}`
    );
  }
  
  if (status.state === "prompt") {
    const requested = await Deno.permissions.request({ name: "read", path });
    if (requested.state === "denied") {
      throw new Error(`Permission denied: Cannot read ${path}`);
    }
  }
  
  return Deno.readTextFile(path);
}
```

### Use Permissions in CI/CD

Explicitly grant permissions in CI workflows:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: denoland/setup-deno@main
        with:
          deno-version: stable
      - run: deno test --allow-read --allow-net --allow-env
```

## Common Permission Patterns

### Web Server

```bash
# Serve static files from ./static, allow all incoming connections
deno run --allow-read=./static --allow-net=localhost:8000 server.ts
```

### CLI Tool with Config

```bash
# Read config file, write output, run git commands
deno run --allow-read=./config.json --allow-write=./output --allow-run=git cli.ts
```

### Data Processing Script

```bash
# Read input files, write results, access environment variables
deno run --allow-read=./input --allow-write=./output --allow-env=AWS_* process.ts
```

### Development Server with Hot Reload

```bash
# Watch mode requires read permissions for file watching
deno run --allow-read --allow-net --watch=src/ server.ts
```

## Permission Troubleshooting

### "Permission denied" Errors

If you get a permission error, Deno will suggest the required flag:

```
error: Uncaught (in promise) NotCapable: Permission denied (os access): "./data.json"
Run again with the --allow-env flag to allow access.
```

Add the suggested flag:
```bash
deno run --allow-env script.ts
```

### Partial Permissions

When using `--deny-*` flags, some operations may fail even with granted permissions:

```bash
# Allow /data but deny /data/secrets
deno run --allow-read=/data --deny-read=/data/secrets script.ts

// This works:
await Deno.readTextFile("/data/public.txt");

// This fails:
await Deno.readTextFile("/data/secrets/key.txt"); // Permission denied
```

Check `status.partial` to detect partial permissions:

```typescript
const status = await Deno.permissions.query({ name: "read", path: "/data" });
if (status.partial) {
  console.log("Some subpaths are denied");
}
```

### Inspecting Current Permissions

List all granted permissions:

```typescript
// Check multiple permissions
const perms = ["read", "write", "net", "env", "run"];
for (const perm of perms) {
  const status = await Deno.permissions.query({ name: perm as any });
  console.log(`${perm}: ${status.state}`);
}
```

## Related Topics

- [Building Web Servers](02-web-servers.md) - Using network permissions for HTTP servers
- [API Reference](06-api-reference.md) - Deno namespace APIs that require permissions
- [Testing Guide](05-testing.md) - Permission requirements for tests
