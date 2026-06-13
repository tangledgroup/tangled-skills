# JavaScript SDK

## Overview

Logfire offers first-class JavaScript/TypeScript integration for the most popular frameworks and runtimes. Where appropriate (Deno, Next.js), integration happens through the framework/runtime's built-in OTel mechanism. The `logfire` package mirrors the Python API for creating spans and reporting exceptions.

## Packages

- `@pydantic/logfire-node` — Node.js scripts
- `@pydantic/logfire-browser` — Browser tracing with sensible defaults
- `@pydantic/logfire-cf-workers` — Cloudflare Workers instrumentation
- `logfire` — Core package for spans and logs

## Node.js

```js
import * as logfire from '@pydantic/logfire-node'

logfire.configure({
  token: 'your-write-token',
  serviceName: 'my-service',
  serviceVersion: '1.0.0',
})

logfire.info('Hello from Node.js', { key: 'value' }, { tags: ['example'] })
```

## Browser

The `@pydantic/logfire-browser` package wraps OpenTelemetry browser tracing with sensible defaults. Provides a simple API for creating spans and reporting exceptions.

For proxying browser telemetry through a backend (to avoid exposing write tokens), use the experimental proxy handler in your FastAPI/Express backend.

## Next.js

Next.js has first-party OTel integration through `@vercel/otel`, fully compatible with Logfire. Client-side can be instrumented with `@pydantic/logfire-browser`.

## Cloudflare Workers

```bash
npm install @pydantic/logfire-cf-workers logfire
```

Add `compatibility_flags = ["nodejs_compat"]` to `wrangler.toml`. Store write token in `.dev.vars`:

```
LOGFIRE_TOKEN=your-write-token
LOGFIRE_ENVIRONMENT=development
```

Use the `tracerConfig` function to extract write token from the `env` object and provide necessary configuration.

## Express

Use the `logfire` package, optionally with `dotenv` for environment variables.

## Deno

Deno has built-in OpenTelemetry support. Configure OTel export to Logfire using environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://logfire-us.pydantic.dev
export OTEL_EXPORTER_OTLP_HEADERS='Authorization=your-write-token'
```
