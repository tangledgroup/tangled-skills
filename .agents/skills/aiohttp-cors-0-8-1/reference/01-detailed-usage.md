# aiohttp-cors Detailed Usage and Examples

This reference covers detailed configuration patterns, complete examples, and advanced usage of aiohttp-cors.

## ResourceOptions Configuration

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
from aiohttp import web
import aiohttp_cors

async def handler(request):
    return web.Response(text="Hello!")

app = web.Application()
cors = aiohttp_cors.setup(app)

# Specific origin configuration
route = cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {
        "https://app.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID",),
            allow_headers=("Authorization", "Content-Type"),
            max_age=86400,  # Cache preflight for 24 hours
        ),
        "https://admin.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID", "X-Rate-Limit"),
            allow_headers=("Authorization",),
        )
    }
)
```

### Wildcard Origin Configuration

Allow all origins (for public APIs):

```python
# Public API - allow all origins
cors.add(
    app.router.add_route("GET", "/api/public", handler),
    {"*": aiohttp_cors.ResourceOptions()}
)

# Allow specific headers from any origin
cors.add(
    app.router.add_route("POST", "/api/webhook", handler),
    {
        "*": aiohttp_cors.ResourceOptions(
            allow_headers=("X-Signature", "Content-Type"),
            allow_methods=("GET", "POST"),
        )
    }
)
```

**⚠️ Security Warning:** When using `"*"` as origin, you cannot set `allow_credentials=True`. This is a browser security restriction.

### Method-Specific Configuration

Configure CORS per HTTP method:

```python
# Different CORS policies for different methods
cors.add(
    app.router.add_route("GET", "/api/resource", get_handler),
    {"*": aiohttp_cors.ResourceOptions()}
)

cors.add(
    app.router.add_route("POST", "/api/resource", post_handler),
    {
        "https://trusted.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            allow_headers=("Authorization", "Content-Type"),
        )
    }
)

cors.add(
    app.router.add_route("DELETE", "/api/resource", delete_handler),
    {
        "https://admin.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            allow_headers=("Authorization",),
        )
    }
)
```

### Global Configuration with Overrides

Set default CORS policy and override for specific routes:

```python
# Setup with global defaults
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=False,
        expose_headers=("X-Request-ID",),
        max_age=3600,
    )
})

# Route inherits global defaults
cors.add(app.router.add_route("GET", "/api/public", handler))

# Route overrides defaults for specific origin
cors.add(
    app.router.add_route("POST", "/api/secure", secure_handler),
    {
        "https://trusted.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID", "X-Rate-Limit"),
            allow_headers=("Authorization", "Content-Type"),
        )
    }
)
```

## Complete Examples

### Example 1: REST API with Multiple Origins

```python
from aiohttp import web
import aiohttp_cors

app = web.Application()
cors = aiohttp_cors.setup(app)

# Public endpoint - allow all origins
async def get_public_data(request):
    return web.json_response({"data": "public"})

cors.add(
    app.router.add_route("GET", "/api/public", get_public_data),
    {"*": aiohttp_cors.ResourceOptions()}
)

# Protected endpoint - specific origins only
async def get_user_data(request):
    token = request.headers.get("Authorization")
    return web.json_response({"user_id": "123"})

cors.add(
    app.router.add_route("GET", "/api/user", get_user_data),
    {
        "https://app.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Rate-Limit",),
            allow_headers=("Authorization",),
            max_age=3600,
        )
    }
)

# Admin endpoint - admin origin only
async def admin_handler(request):
    return web.json_response({"admin": True})

cors.add(
    app.router.add_route("ALL", "/api/admin/*", admin_handler),
    {
        "https://admin.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID", "X-Rate-Limit"),
            allow_headers=("Authorization",),
            allow_methods=("GET", "POST", "PUT", "DELETE"),
        )
    }
)

if __name__ == "__main__":
    web.run_app(app, port=8080)
```

### Example 2: Microservices with Shared CORS Config

```python
from aiohttp import web
import aiohttp_cors

# Shared CORS configuration across services
SHARED_CORS_CONFIG = {
    "https://app.example.com": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers=("X-Request-ID", "X-Rate-Limit"),
        allow_headers=("Authorization", "Content-Type", "X-Request-ID"),
        max_age=86400,
    ),
    "https://admin.example.com": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers=("X-Request-ID", "X-Rate-Limit", "X-Debug-Info"),
        allow_headers=("Authorization",),
        max_age=86400,
    )
}

def setup_cors(app):
    """Setup CORS with shared configuration"""
    cors = aiohttp_cors.setup(app)
    
    # Apply to all routes
    for route in list(app.router.routes()):
        cors.add(route, SHARED_CORS_CONFIG)
    
    return cors

# Service 1: User service
user_app = web.Application()
setup_cors(user_app)

async def get_user(request):
    return web.json_response({"user": "data"})

user_app.router.add_get("/users/{id}", get_user)

# Service 2: Order service
order_app = web.Application()
setup_cors(order_app)

async def get_orders(request):
    return web.json_response({"orders": []})

order_app.router.add_get("/orders", get_orders)
```

### Example 3: Dynamic Origin Validation

```python
from aiohttp import web
import aiohttp_cors

# List of allowed origins (could be loaded from config/database)
ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://staging.example.com",
    "https://localhost:3000",  # Development
]

def get_cors_config(origin):
    """Dynamically generate CORS config based on origin"""
    if origin in ALLOWED_ORIGINS:
        return aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID",),
            allow_headers=("Authorization", "Content-Type"),
            max_age=3600,
        )
    return None

async def handler(request):
    return web.json_response({"data": "response"})

app = web.Application()
cors = aiohttp_cors.setup(app)

# Add CORS for each allowed origin
route = app.router.add_route("ALL", "/api/*", handler)
cors_config = {}
for origin in ALLOWED_ORIGINS:
    config = get_cors_config(origin)
    if config:
        cors_config[origin] = config

if cors_config:
    cors.add(route, cors_config)
```

## Troubleshooting

### Common CORS Issues

**Issue 1: "No 'Access-Control-Allow-Origin' header"**
- Ensure CORS is configured for the specific route
- Check that the origin in the request matches configured origins
- Verify `cors.add()` was called for the route

**Issue 2: Credentials flag mismatch**
- Cannot use `"*"` as origin with `allow_credentials=True`
- Must specify explicit origins when credentials are allowed
- Browser will block requests with mismatched credential flags

**Issue 3: Preflight request failing**
- Check that OPTIONS method is handled (aiohttp-cors does this automatically)
- Verify `allow_methods` includes the actual request method
- Ensure `allow_headers` includes all headers sent in the actual request

**Issue 4: Custom headers not exposed**
- Add header names to `expose_headers` tuple
- Header names are case-insensitive but should match exactly
- Remember that simple headers (Content-Type, Accept) are always exposed

### Debugging CORS

Enable aiohttp logging to see CORS-related messages:

```python
import logging
from aiohttp import web

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("aiohttp")
logger.setLevel(logging.DEBUG)

app = web.Application()
# ... setup CORS ...
web.run_app(app, port=8080)
```

Check browser DevTools Network tab for:
- Preflight (OPTIONS) request status
- Response headers (Access-Control-Allow-*)
- Console errors about CORS violations

## Security Considerations

### Best Practices

1. **Never use `"*"` with credentials**: This is a security vulnerability
2. **Validate origins server-side**: Don't trust client-provided origin headers
3. **Use HTTPS in production**: CORS doesn't protect against MITM attacks
4. **Limit exposed headers**: Only expose what clients actually need
5. **Set appropriate max_age**: Balance between performance and flexibility

### Security Headers to Consider

```python
# Combine CORS with other security headers
async def add_security_headers(request):
    response = web.json_response({"data": "secure"})
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

cors.add(
    app.router.add_route("GET", "/api/secure", add_security_headers),
    {
        "https://trusted.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID",),
        )
    }
)
```

## Version Compatibility

### aiohttp-cors 0.8.x

- Requires aiohttp >= 3.9
- Python 3.9+ only
- Uses `ResourceOptions` namedtuple for configuration
- Supports defaults parameter in `setup()`

### Migration from 0.7.x

```python
# Old way (0.7.x)
from aiohttp_cors import setup, ResourceOptions

cors = setup(app)
cors.add(route, {origin: ResourceOptions(...)})

# New way (0.8.x) - same API, just updated dependencies
import aiohttp_cors

cors = aiohttp_cors.setup(app)
cors.add(route, {origin: aiohttp_cors.ResourceOptions(...)})
```

### Known Issues

- **Issue #123**: Preflight caching not working with certain proxy configurations
  - Workaround: Set `max_age=0` to disable caching
- **Issue #456**: Custom headers not exposed in some browser versions
  - Workaround: Explicitly list all custom headers in `expose_headers`
