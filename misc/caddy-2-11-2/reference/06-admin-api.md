# Admin API Reference

Caddy's admin API provides RESTful endpoints for dynamic configuration with zero-downtime reloads. Default address: `localhost:2019`. Override with `CADDY_ADMIN` environment variable or the `admin` global option.

## Endpoints

### POST /load

Set or replace the active configuration. Blocks until reload completes or fails. Automatic rollback on error.

```bash
# Load JSON config
curl -X POST "http://localhost:2019/load" \
    -H "Content-Type: application/json" \
    -d @caddy.json

# Load Caddyfile (use --data-binary to preserve newlines)
curl -X POST "http://localhost:2019/load" \
    -H "Content-Type: text/caddyfile" \
    --data-binary @Caddyfile
```

If the new config is identical, no reload occurs. Set `Cache-Control: must-revalidate` to force.

### POST /stop

Gracefully shut down and exit the process:

```bash
curl -X POST "http://localhost:2019/stop"
```

To stop the running config without exiting, use `DELETE /config/`.

### GET /config/[path]

Export current configuration at a path:

```bash
# Full config
curl "http://localhost:2019/config/" | jq

# Specific scope
curl "http://localhost:2019/config/apps/http/servers/myserver/listen"
# Output: [":443"]
```

### POST /config/[path]

Set or replace config at a path. Appends to arrays, creates/replaces objects:

```bash
# Add a listener address
curl -X POST \
    -H "Content-Type: application/json" \
    -d '":8080"' \
    "http://localhost:2019/config/apps/http/servers/myserver/listen"

# Add multiple addresses (use /... suffix)
curl -X POST \
    -H "Content-Type: application/json" \
    -d '[":8080", ":5133"]' \
    "http://localhost:2019/config/apps/http/servers/myserver/listen/..."
```

### PUT /config/[path]

Create new value or insert into array at position:

```bash
curl -X PUT \
    -H "Content-Type: application/json" \
    -d '":8080"' \
    "http://localhost:2019/config/apps/http/servers/myserver/listen/0"
```

### PATCH /config/[path]

Replace existing value or array element:

```bash
curl -X PATCH \
    -H "Content-Type: application/json" \
    -d '[":8081", ":8082"]' \
    "http://localhost:2019/config/apps/http/servers/myserver/listen"
```

### DELETE /config/[path]

Delete config at path:

```bash
# Unload entire config (process keeps running)
curl -X DELETE "http://localhost:2019/config/"

# Stop one server
curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"
```

### POST /adapt

Adapt config to JSON without loading:

```bash
curl -X POST "http://localhost:2019/adapt" \
    -H "Content-Type: text/caddyfile" \
    --data-binary @Caddyfile
```

### GET /pki/ca/<id>

Get PKI CA information:

```bash
curl "http://localhost:2019/pki/ca/local" | jq
```

Returns CA name, root certificate, intermediate certificate.

### GET /pki/ca/<id>/certificates

Get CA certificate chain (PEM format):

```bash
curl "http://localhost:2019/pki/ca/local/certificates"
```

Used by `caddy trust` to install root certificates.

### GET /reverse_proxy/upstreams

Get reverse proxy upstream status:

```bash
curl "http://localhost:2019/reverse_proxy/upstreams" | jq
# Output:
# [
#   {"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
#   {"address": "10.0.1.2:80", "num_requests": 5, "fails": 4}
# ]
```

### GET /metrics

Prometheus metrics endpoint (when metrics enabled):

```bash
curl "http://localhost:2019/metrics"
```

## Using @id in JSON

Embed `@id` fields in JSON for easier direct access:

```json
{
    "@id": "my_proxy",
    "handler": "reverse_proxy",
    "upstreams": [...]
}
```

Then access via `/id/` endpoint:

```bash
curl "http://localhost:2019/id/my_proxy/upstreams"
```

Instead of the full path: `/config/apps/http/servers/myserver/routes/1/handle/0/upstreams`.

## Concurrent Config Changes

Use `Etag` and `If-Match` headers for optimistic concurrency control:

1. `GET /config/foo` — Store the `Etag` header from response
2. Make desired changes to returned config
3. `POST|PUT|PATCH|DELETE /config/foo/...` with `If-Match: <stored-etag>`
4. If HTTP 412 (Precondition Failed), repeat from step 1

Only overlapping scopes cause collisions — simultaneous changes to different config parts don't require retry.

## Admin API Security

The admin API controls the entire server. Default binding to `localhost` restricts access. For production:

- Bind to unix socket for file-permission control: `admin unix//run/caddy-admin.sock`
- Configure `origins` and `enforce_origin` for CORS protection
- Never expose the admin API to untrusted networks
- Disable entirely with `admin off` (prevents config reloads)
