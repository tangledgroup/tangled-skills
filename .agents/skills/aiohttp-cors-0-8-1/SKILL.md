---
name: aiohttp-cors-0-8-1
description: A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching. Use when building aiohttp.web APIs that need to serve browsers from different origins, implementing CORS preflight handling, configuring per-route or global CORS policies, or working with web views that require CORS support.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.8.1"
tags:
  - cors
  - aiohttp
  - web-security
  - http-headers
  - cross-origin
category: web-development
external_references:
  - https://pypi.org/project/aiohttp-cors/
  - https://github.com/aio-libs/aiohttp-cors
  - https://aiohttp-cors.readthedocs.io/
---

# aiohttp-cors 0.8.1

## Overview

`aiohttp_cors` implements Cross-Origin Resource Sharing (CORS) support for aiohttp's asyncio-powered HTTP server. It handles both preflight (`OPTIONS`) requests and response header injection for actual cross-origin requests, following the W3C CORS specification.

The library is configured per-application via `aiohttp_cors.setup()`, which returns a `CorsConfig` instance. Routes are then explicitly added to CORS configuration with origin-to-options mappings. Each route can have its own CORS policy, or inherit from application-level defaults.

Version 0.8.1 requires Python 3.9+ and aiohttp 3.9+. It is licensed under Apache 2.0.

## When to Use

- Building aiohttp.web APIs that need to be accessed by browsers from different origins
- Configuring per-route or global CORS policies with specific origin allowlists
- Handling CORS preflight requests automatically with proper `OPTIONS` responses
- Enabling credential passing (cookies, HTTP auth) for cross-origin requests
- Exposing custom server headers to cross-origin clients
- Working with aiohttp `web.View` subclasses that need CORS support

## Core Concepts

### Same-Origin Policy (SOP)

Browsers enforce SOP: a page at one origin `(scheme, host, port)` cannot read resources from a different origin. Pages can embed resources (images, scripts, iframes) but cannot read their content. This protects against malicious pages reading authenticated data from other sites.

### How CORS Works

CORS allows servers to opt-in to cross-origin access:

1. Browser sends `Origin: https://client.example.com` header with the request
2. Server responds with `Access-Control-Allow-Origin: https://client.example.com`
3. Browser checks the header and allows or denies client-side access

For non-simple requests (custom headers, methods like `PUT`/`DELETE`), the browser first sends an `OPTIONS` preflight request to check if the actual request is allowed. The server responds with allowed methods, headers, and caching duration.

### Key Classes

- **`CorsConfig`** — Application-level CORS configuration container. Created by `setup()`. One instance per `web.Application`.
- **`ResourceOptions`** — Per-origin CORS options: credentials, exposed headers, allowed headers, max age, allowed methods.
- **`CorsViewMixin`** — Mixin for `web.View` subclasses to enable CORS on view handlers.
- **`custom_cors()`** — Decorator to override CORS config on individual view methods.

## Installation / Setup

Install via pip:

```bash
pip install aiohttp_cors
```

Requirements: Python 3.9+, aiohttp 3.9+.

## Usage Examples

### Basic Setup

Configure CORS for a single route with specific origin:

```python
from aiohttp import web
import aiohttp_cors

async def handler(request):
    return web.Response(
        text="Hello!",
        headers={"X-Custom-Server-Header": "Custom data"}
    )

app = web.Application()
cors = aiohttp_cors.setup(app)

resource = cors.add(app.router.add_resource("/hello"))
cors.add(resource.add_route("GET", handler), {
    "http://client.example.org": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers=("X-Custom-Server-Header",),
        allow_headers=("X-Requested-With", "Content-Type"),
        max_age=3600,
    )
})
```

### Wildcard Origin (`*`)

Allow all origins with restricted options:

```python
cors.add(route, {
    "*": aiohttp_cors.ResourceOptions(allow_credentials=False),
    "http://client.example.org": aiohttp_cors.ResourceOptions(
        allow_credentials=True
    ),
})
```

Specific origins take precedence over `*`. Note that `allow_credentials=True` cannot be combined with `*` origin in the same options entry — use specific origins when credentials are needed.

### Global Defaults

Set default CORS policy applied to all CORS-enabled routes:

```python
cors = aiohttp_cors.setup(app, defaults={
    "http://client.example.org": aiohttp_cors.ResourceOptions(),
})

# POST and PUT available only to http://client.example.org
hello_resource = cors.add(app.router.add_resource("/hello"))
cors.add(hello_resource.add_route("POST", handler_post))
cors.add(hello_resource.add_route("PUT", handler_put))

# GET additionally allowed from another origin
cors.add(hello_resource.add_route("GET", handler), {
    "http://other-client.example.org": aiohttp_cors.ResourceOptions(),
})
```

### Resource-Level Defaults with `allow_methods`

Avoid adding every route to CORS config by specifying allowed methods at the resource level:

```python
hello_resource = cors.add(app.router.add_resource("/hello"), {
    "http://client.example.org": aiohttp_cors.ResourceOptions(
        allow_methods=["POST", "PUT"]
    ),
})
# POST and PUT are CORS-enabled without calling cors.add() on each route.
hello_resource.add_route("POST", handler_post)
hello_resource.add_route("PUT", handler_put)

# DELETE still needs explicit CORS registration:
cors.add(hello_resource.add_route("DELETE", handler_delete))
```

### Enable CORS on All Routes

Bulk-enable CORS on all existing routes with global defaults:

```python
# Setup application routes normally.
app.router.add_route("GET", "/hello", handler_get)
app.router.add_route("PUT", "/hello", handler_put)
app.router.add_route("POST", "/hello", handler_post)
app.router.add_route("DELETE", "/hello", handler_delete)

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# Apply CORS to all routes.
for route in list(app.router.routes()):
    cors.add(route)
```

### Wildcard Headers

Use `"*"` to allow or expose all headers:

```python
cors.add(route, {
    "http://client.example.org": aiohttp_cors.ResourceOptions(
        expose_headers="*",
        allow_headers="*",
    ),
})
```

When `expose_headers="*"`, all non-simple response headers are automatically exposed. Simple response headers (`Cache-Control`, `Content-Language`, `Content-Type`, `Expires`, `Last-Modified`, `Pragma`) are always accessible and don't need to be listed.

### Web Views with `CorsViewMixin`

Enable CORS on `web.View` subclasses:

```python
from aiohttp_cors import CorsViewMixin, ResourceOptions, custom_cors

class MyView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="X-Request-ID",
        )
    }

    async def get(self):
        return web.Response(text="GET response")

    @custom_cors({
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
        )
    })
    async def post(self):
        return web.Response(text="POST response")
```

Register the view with CORS:

```python
cors.add(app.router.add_route("*", "/resource", MyView))
```

The `webview=True` argument to `cors.add()` is deprecated — views are detected automatically by type.

Configuration priority for views: method-level `@custom_cors` decorator > class-level `cors_config` > global defaults from `setup()`. These are merged using `collections.ChainMap`.

## ResourceOptions Reference

`ResourceOptions` is a named tuple with five fields. All parameters are keyword-only.

### `allow_credentials` (bool, default: `False`)

Allow passing client credentials (cookies, HTTP auth) to the resource from another origin. When `True`, the server responds with `Access-Control-Allow-Credentials: true`.

### `expose_headers` (sequence of strings or `"*"`, default: `()`)

Server headers that the client is allowed to read. Simple response headers are always accessible. Use `"*"` to expose all non-simple headers in the response.

### `allow_headers` (sequence of strings or `"*"`, default: `()`)

Client headers that are allowed in the actual request. Validated during preflight. Use `"*"` to allow any header. Header names are normalized to uppercase internally.

### `max_age` (int or None, default: `None`)

How long (in seconds) the browser may cache the preflight response. Sets `Access-Control-Max-Age` header. Must be a non-negative integer.

### `allow_methods` (sequence of strings or `"*"`, default: `None`)

Explicitly list allowed HTTP methods for CORS. When set, routes for those methods don't need individual `cors.add()` calls — the resource-level config handles them. Use `"*"` for all methods. Method names are normalized to uppercase internally.

When `allow_methods` is `None`, CORS availability depends on which routes have been explicitly added via `cors.add()`.

## Preflight Request Handling

The library automatically handles CORS preflight (`OPTIONS`) requests. When a browser sends a preflight request:

1. The `Origin` header is validated
2. `Access-Control-Request-Method` is parsed
3. `Access-Control-Request-Headers` are checked against `allow_headers`
4. If allowed, the server responds with:
   - `Access-Control-Allow-Origin` — matching the request origin
   - `Access-Control-Allow-Credentials` — if credentials are allowed
   - `Access-Control-Max-Age` — if `max_age` is set
   - `Access-Control-Allow-Methods` — the requested method
   - `Access-Control-Allow-Headers` — the requested headers

If any check fails, `HTTP 403 Forbidden` is returned with a descriptive error message.

## Non-Preflight Request Processing

For actual cross-origin requests (non-OPTIONS), the library hooks into aiohttp's `on_response_prepare` signal to inject CORS headers:

1. Checks if the route has CORS enabled
2. Reads the `Origin` header from the request
3. Looks up matching origin or `"*"` in configuration
4. Sets `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, and `Access-Control-Expose-Headers` on the response

If no `Origin` header is present or the origin is not configured, CORS headers are not added (same-origin request proceeds normally).

## Configuration Validation

The library validates configuration at setup time:

- Origin keys must be strings
- `allow_credentials` must be boolean
- `expose_headers` and `allow_headers` must be sequences of strings or `"*"`
- `max_age` must be a non-negative integer or `None`
- `allow_methods` must be a sequence of strings, `"*"`, or `None`
- Config mappings passed to `setup()` defaults or `cors.add()` can use either `ResourceOptions` instances or plain dicts with the same keys

## Migration Notes

### From 0.7.x to 0.8.x

- Python 3.9+ is now required (3.8 support dropped)
- aiohttp 3.9+ is now required
- The `webview=True` parameter on `cors.add()` is deprecated — views are detected automatically by checking if the handler is a subclass of both `web.View` and `CorsViewMixin`

### From 0.4.x to 0.5.x

- aiohttp 0.21.4+ required (new Resources API)
- `allow_methods` option added for resource-level method control
- `AbstractRouterAdapter` rewritten for better router agnosticism
