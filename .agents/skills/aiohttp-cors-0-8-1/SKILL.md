---
name: aiohttp-cors-0-8-1
description: A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - cors
  - aiohttp
  - web-security
  - http-headers
  - cross-origin
category: web-development
required_environment_variables: []
compatibility:
  python: ">=3.9"
  aiohttp: ">=3.9"
---

# aiohttp-cors 0.8.1

A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.

## When to Use

- Building aiohttp web APIs that need to serve clients from different domains
- Enabling frontend applications (React, Vue, Angular) hosted on different domains to call backend APIs
- Configuring which origins can access specific routes or resources
- Handling CORS preflight requests (OPTIONS) automatically
- Exposing custom response headers to client-side JavaScript
- Allowing or restricting credential sharing (cookies, HTTP authentication)
- Implementing fine-grained CORS policies per route or resource

## Setup

### Installation

Install aiohttp-cors from PyPI:

```bash
pip install aiohttp-cors
```

**Requirements:**
- Python >= 3.9
- aiohttp >= 3.9

### Basic Configuration

CORS must be explicitly enabled for each route or resource. The library does not automatically apply CORS to all routes:

```python
from aiohttp import web
import aiohttp_cors

async def handler(request):
    return web.Response(text="Hello!")

app = web.Application()

# Setup CORS configuration for the application
cors = aiohttp_cors.setup(app)

# Enable CORS on specific route
route = cors.add(
    app.router.add_route("GET", "/hello", handler),
    {
        "http://client.example.org": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Custom-Server-Header",),
            allow_headers=("X-Requested-With", "Content-Type"),
            max_age=3600,
        )
    }
)
```

## Usage

### ResourceOptions Configuration

The `ResourceOptions` namedtuple defines CORS behavior for specific origins. Available parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_credentials` | bool | False | Allow clients to send cookies and HTTP authentication headers |
| `expose_headers` | sequence or "*" | () | Server headers exposed to client JavaScript |
| `allow_headers` | sequence or "*" | () | Client headers allowed in actual requests |
| `max_age` | int or None | None | Preflight cache duration in seconds |
| `allow_methods` | sequence, "*", or None | None | Allowed HTTP methods (for resource-level config) |

**Important constraints:**
- `expose_headers` and `allow_headers` can be `"*"` for all headers
- `allow_credentials=True` requires explicit origin (cannot use `"*"`)
- `max_age` must be non-negative integer
- Header values are normalized to uppercase internally

### Origin-Specific Configuration

Configure CORS for specific client origins:

```python
cors = aiohttp_cors.setup(app)

# Allow only specific origin
cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {
        "https://trusted-client.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID", "X-Rate-Limit"),
            allow_headers=("Authorization", "Content-Type"),
        )
    }
)

# Allow multiple specific origins
cors.add(
    app.router.add_route("POST", "/api/submit", submit_handler),
    {
        "https://app1.example.com": aiohttp_cors.ResourceOptions(),
        "https://app2.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
        ),
    }
)
```

### Wildcard Origin Configuration

Allow all origins (useful for public APIs):

```python
cors = aiohttp_cors.setup(app)

# Allow all origins with default options
cors.add(
    app.router.add_route("GET", "/public/data", handler),
    {
        "*": aiohttp_cors.ResourceOptions()
    }
)

# Allow all origins with full CORS features (not recommended for sensitive data)
cors.add(
    app.router.add_route("GET", "/open/api", handler),
    {
        "*": aiohttp_cors.ResourceOptions(
            expose_headers="*",
            allow_headers="*",
        )
    }
)
```

**Security note:** When using `allow_credentials=True`, the origin cannot be `"*"`. Must specify explicit origins.

### Default CORS Configuration

Set default CORS options applied to all routes unless overridden:

```python
# Apply defaults to all CORS-enabled routes
cors = aiohttp_cors.setup(app, defaults={
    "http://client.example.org": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    ),
})

# All these routes inherit the default configuration
cors.add(app.router.add_route("GET", "/api/users", get_users))
cors.add(app.router.add_route("POST", "/api/users", create_user))
cors.add(app.router.add_route("PUT", "/api/users/{id}", update_user))

# Override defaults for specific route
cors.add(
    app.router.add_route("DELETE", "/api/users/{id}", delete_user),
    {
        "http://admin.example.org": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
        )
    }
)
```

### Resource-Level Configuration

Configure CORS at the resource level (all methods on a path):

```python
# Create resource with default CORS configuration
cors = aiohttp_cors.setup(app)

hello_resource = cors.add(
    app.router.add_resource("/hello"),
    {
        "http://client.example.org": aiohttp_cors.ResourceOptions(
            allow_methods=["POST", "PUT"],  # Explicitly list allowed methods
        )
    }
)

# These routes inherit resource-level CORS config automatically
hello_resource.add_route("POST", post_handler)
hello_resource.add_route("PUT", put_handler)

# Can still add specific route config for additional methods
cors.add(
    hello_resource.add_route("DELETE", delete_handler),
    {
        "http://client.example.org": aiohttp_cors.ResourceOptions()
    }
)
```

**Benefits of resource-level configuration:**
- No need to call `cors.add()` for every route method
- Centralized CORS policy for all methods on same path
- Use `allow_methods` to explicitly list permitted HTTP methods

### Enable CORS on All Routes

Apply CORS to all existing routes in the router:

```python
# Setup application routes first
app.router.add_route("GET", "/api/users", get_users)
app.router.add_route("POST", "/api/users", create_user)
app.router.add_route("PUT", "/api/users/{id}", update_user)
app.router.add_route("DELETE", "/api/users/{id}", delete_user)

# Configure CORS defaults
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# Enable CORS on all routes
for route in list(app.router.routes()):
    cors.add(route)
```

**Important:** Use `list()` to convert routes to list before iterating (modifies router during iteration).

### Using CorsViewMixin with web.View

Enable CORS for aiohttp View classes:

```python
from aiohttp import web
import aiohttp_cors
from aiohttp_cors import CorsViewMixin, ResourceOptions, custom_cors

class APIResource(web.View, CorsViewMixin):
    # Default CORS config for all methods in this view
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="X-Request-ID",
        )
    }

    async def get(self):
        return web.Response(text="GET request")

    @custom_cors({
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",  # Override for POST method only
        )
    })
    async def post(self):
        return web.Response(text="POST request")

app = web.Application()
cors = aiohttp_cors.setup(app, defaults={
    "*": ResourceOptions(
        expose_headers="*",
        allow_headers="*",
    )
})

# Add view to router (webview parameter deprecated in 0.7.0+)
cors.add(app.router.add_route("*", "/resource", APIResource))
```

**View configuration hierarchy:**
1. Method-level config (`@custom_cors` decorator) - highest priority
2. Class-level config (`cors_config` attribute)
3. Application defaults (`cors.setup(defaults=...)`) - lowest priority

Configuration is merged using `ChainMap`, with method-level taking precedence.

### Preflight Request Handling

CORS preflight requests (OPTIONS method) are handled automatically:

```python
# No need to implement OPTIONS handler manually
# aiohttp-cors intercepts and responds to preflight requests

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        max_age=86400,  # Cache preflight for 24 hours
    )
})

cors.add(app.router.add_route("POST", "/api/upload", upload_handler))
```

**Preflight response headers:**
- `Access-Control-Allow-Origin`: Origin from request (or "*" if configured)
- `Access-Control-Allow-Methods`: Allowed HTTP methods
- `Access-Control-Allow-Headers`: Allowed request headers
- `Access-Control-Max-Age`: Cache duration (if specified)
- `Access-Control-Allow-Credentials`: "true" if credentials allowed

### Exposing Custom Response Headers

By default, only simple response headers are exposed to client JavaScript. To expose custom headers:

```python
async def handler(request):
    return web.Response(
        text="Data",
        headers={
            "X-Request-ID": "abc123",
            "X-Rate-Limit-Remaining": "42",
            "X-Custom-Metadata": "value",
        }
    )

cors = aiohttp_cors.setup(app)
cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {
        "*": aiohttp_cors.ResourceOptions(
            # Expose specific headers to client JavaScript
            expose_headers=("X-Request-ID", "X-Rate-Limit-Remaining", "X-Custom-Metadata"),
        )
    }
)

# Or expose all custom headers
cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {
        "*": aiohttp_cors.ResourceOptions(
            expose_headers="*",  # Expose all non-simple headers
        )
    }
)
```

**Simple response headers (always exposed):**
- Cache-Control
- Content-Language
- Content-Type
- Expires
- Last-Modified
- Pragma

### Credential Handling

Allow clients to send cookies and authentication headers:

```python
cors = aiohttp_cors.setup(app)

# Enable credentials for specific origin (NOT "*" wildcard)
cors.add(
    app.router.add_route("GET", "/api/protected", handler),
    {
        "https://trusted-client.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,  # Client can send cookies/auth headers
        )
    }
)
```

**Important:** When `allow_credentials=True`:
- Origin must be explicit (cannot use `"*"`)
- Browser sends cookies and HTTP authentication automatically
- Server responds with `Access-Control-Allow-Credentials: true`

## Complete Examples

### Public API (All Origins, No Credentials)

```python
from aiohttp import web
import aiohttp_cors

async def get_public_data(request):
    return web.json_response({"data": "public"})

async def post_public_data(request):
    data = await request.json()
    return web.json_response({"status": "received"})

app = web.Application()

# Allow all origins for public API
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        expose_headers="*",
        allow_headers="*",
        max_age=3600,
    )
})

# Enable CORS on all routes
for route in list(app.router.routes()):
    cors.add(route)

app.router.add_route("GET", "/api/public", get_public_data)
app.router.add_route("POST", "/api/public", post_public_data)
```

### Protected API (Specific Origins with Credentials)

```python
from aiohttp import web
import aiohttp_cors

TRUSTED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
    "https://staging.example.com",
]

async def get_user_data(request):
    # Access cookies, session, etc.
    session_cookie = request.cookies.get("session")
    return web.json_response({"user": "authenticated"})

app = web.Application()

# Configure CORS for trusted origins only
cors_config = {
    origin: aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers=("X-Request-ID",),
        allow_headers=("Authorization", "Content-Type", "X-Request-ID"),
        max_age=86400,
    )
    for origin in TRUSTED_ORIGINS
}

cors = aiohttp_cors.setup(app, defaults=cors_config)

app.router.add_route("GET", "/api/user", get_user_data)
cors.add(app.router["get_user_data"])  # Enable CORS on route
```

### Multi-Tenant API (Dynamic Origin Configuration)

```python
from aiohttp import web
import aiohttp_cors

# Load allowed origins from configuration/database
ALLOWED_ORIGINS = {
    "tenant-a": "https://app.tenant-a.com",
    "tenant-b": "https://app.tenant-b.com",
}

async def tenant_api(request):
    tenant_id = request.match_info.get("tenant")
    return web.json_response({"tenant": tenant_id})

app = web.Application()
cors = aiohttp_cors.setup(app)

# Configure CORS for each tenant's origin
for tenant_id, origin in ALLOWED_ORIGINS.items():
    cors.add(
        app.router.add_route("GET", f"/api/{tenant_id}/data", tenant_api),
        {
            origin: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        }
    )
```

## Troubleshooting

### CORS Not Working

**Symptom:** Browser console shows "CORS policy" errors.

**Checklist:**
1. Route is added to CORS config: `cors.add(route, {...})`
2. Origin in request matches configured origin exactly (including protocol and port)
3. If using credentials, origin is not `"*"` wildcard
4. Preflight (OPTIONS) request succeeds with 200 OK

**Debug:** Add logging to see CORS requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### "No 'Access-Control-Allow-Origin' header" Error

**Cause:** Route not added to CORS configuration or origin mismatch.

**Solution:** Ensure route is explicitly added:

```python
# WRONG - route not CORS-enabled
app.router.add_route("GET", "/api/data", handler)

# CORRECT - route added to CORS config
cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {"*": aiohttp_cors.ResourceOptions()}
)
```

### Credentials with Wildcard Origin Error

**Cause:** Using `allow_credentials=True` with `"*"` origin.

**Error:** Browser rejects response because credentials require explicit origin.

**Solution:** Specify exact origins:

```python
# WRONG - will be rejected by browser
cors.add(route, {
    "*": aiohttp_cors.ResourceOptions(allow_credentials=True)
})

# CORRECT - explicit origins only
cors.add(route, {
    "https://app.example.com": aiohttp_cors.ResourceOptions(allow_credentials=True),
    "https://admin.example.com": aiohttp_cors.ResourceOptions(allow_credentials=True),
})
```

### Custom Headers Not Visible in Browser

**Cause:** Headers not listed in `expose_headers`.

**Solution:** Add headers to expose list:

```python
cors.add(
    route,
    {
        "*": aiohttp_cors.ResourceOptions(
            expose_headers=("X-Custom-Header", "X-Another-Header")
        )
    }
)
```

### Preflight Request Fails

**Cause:** OPTIONS handler not configured or headers mismatch.

**Solution:** Ensure preflight is handled (automatic if route added to CORS):

```python
# Preflight handled automatically when route is in CORS config
cors.add(
    app.router.add_route("POST", "/api/upload", upload_handler),
    {
        "*": aiohttp_cors.ResourceOptions(
            allow_headers=("Content-Type", "X-Custom-Header"),
            max_age=3600,  # Cache preflight response
        )
    }
)
```

### Development vs Production Origins

**Solution:** Use environment-specific configuration:

```python
import os

IS_DEV = os.environ.get("ENV") == "development"

if IS_DEV:
    CORS_ORIGINS = {
        "http://localhost:3000": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        ),
        "http://localhost:8080": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        ),
    }
else:
    CORS_ORIGINS = {
        "https://app.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID",),
            allow_headers=("Authorization", "Content-Type"),
            max_age=86400,
        ),
    }

cors = aiohttp_cors.setup(app, defaults=CORS_ORIGINS)
```

## Security Considerations

### Principle of Least Privilege

- Only allow origins that need access
- Use explicit origins instead of `"*"` when possible
- Restrict `allow_headers` to only required headers
- Set reasonable `max_age` values (avoid excessive caching)

### Credential Security

- Never use `allow_credentials=True` with `"*"` origin
- Validate origin against whitelist in production
- Use HTTPS for all cross-origin requests with credentials

### Header Exposure

- Only expose necessary headers via `expose_headers`
- Avoid exposing sensitive headers (internal IDs, debug info)
- Simple response headers are always exposed (cannot be restricted)

## Version Compatibility

| aiohttp-cors Version | Python | aiohttp |
|---------------------|--------|---------|
| 0.8.1 | >=3.9 | >=3.9 |
| 0.8.0 | >=3.9 | >=3.9 |
| 0.7.0 | >=3.5 | >=3.0 |
| 0.6.0 | >=3.4 | >=2.0 |

**Breaking changes in 0.8.0:**
- Dropped Python 3.8 support
- Requires aiohttp 3.9+

**Breaking changes in 0.7.0:**
- Dropped Python 3.4 support
- View detection is now implicit (no `webview=True` needed)
