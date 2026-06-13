# Deployment

## Deno Deploy

Deno Deploy is a serverless platform for running JavaScript and TypeScript applications at global scale. It provides a management dashboard at console.deno.com with built-in CI/CD, environment variables, CDN caching, and observability.

### Key Features

- Serverless execution with automatic scaling
- Edge deployment across multiple regions
- Built-in CI/CD from GitHub repositories
- Environment variables (separate dev/prod)
- CDN caching support
- Web Cache API for persistent caching
- Instant rollback
- Logs, tracing, and metrics
- Cron jobs support
- Deno KV database integration
- Self-hostable regions

### Deploying via CLI

```bash
# Authenticate
deno deploy login

# Deploy a project
deno deploy --project=my-project server.ts

# Deploy with specific region
deno deploy --project=my-project --region=ams server.ts
```

### Deploying from GitHub

Connect your GitHub repository in the Deno Deploy dashboard. Each push to the configured branch triggers an automatic deployment.

### Export Pattern for Deno Deploy

For Deno Deploy, export a `fetch` handler:

```typescript
export function fetch(request: Request): Response {
  return new Response("Hello from Deno Deploy!");
}
```

Or use `Deno.serve`:

```typescript
Deno.serve((req) => {
  return new Response("Hello from Deno Deploy!");
});
```

### Environment Variables

Set environment variables in the Deno Deploy dashboard or via CLI:

```bash
deno deploy --env=PRODUCTION=true --env=API_KEY=secret server.ts
```

Access in code:

```typescript
const apiKey = Deno.env.get("API_KEY");
```

## Deno KV

Deno KV is a serverless key-value database available on Deno Deploy and locally.

### Basic Operations

```typescript
// Open a KV instance (local by default)
const kv = await Deno.openKv();

// Set a value
await kv.set(["users", "alice"], { name: "Alice", age: 30 });

// Get a value
const { value: user } = await kv.get(["users", "alice"]);

// Delete a value
await kv.delete(["users", "alice"]);

// Close when done
kv.close();
```

### Key Expiration

```typescript
await kv.set(["sessions", sessionId], data, { expireIn: "1h" });
```

### Secondary Indexes

```typescript
// Create an index entry alongside a value
await kv.set(["users", "alice"], { name: "Alice", age: 30 })
  .set(["users_by_age_index", 30, "alice"], undefined);

// Query by index
const usersByAge = kv.query(["users_by_age_index", 30, "*"]);
for await (const entry of usersByAge) {
  console.log(entry.key, entry.value);
}
```

### Atomic Transactions

```typescript
await kv.atomic()
  .set(["counter"], 100)
  .delete(["old_key"])
  .commit();
```

### Remote KV on Deno Deploy

On Deno Deploy, use a project-scoped KV:

```typescript
const kv = await Deno.openKv({
  hostname: "my-project.deno.dev",
  accessToken: Deno.env.get("DENO_KV_ACCESS_TOKEN"),
});
```

## deno compile

Create standalone executables:

```bash
# Compile to a binary
deno compile --allow-net server.ts

# Custom output name
deno compile --output=my-server --allow-net server.ts

# Include icon (macOS)
deno compile --icon=icon.png --allow-net server.ts
```

The compiled binary includes the Deno runtime and all dependencies — no installation required on the target machine.

## Framework Support

Deno Deploy provides first-class support for:
- Next.js
- Astro
- SvelteKit
- Static sites

## Deno Sandbox

Deno Sandbox is a local testing environment that mimics Deno Deploy's execution model, allowing you to test edge deployment behavior locally.

```bash
deno sandbox server.ts
```
