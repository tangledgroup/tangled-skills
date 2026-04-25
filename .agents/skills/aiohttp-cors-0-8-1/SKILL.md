---
name: aiohttp-cors-0-8-1
description: A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
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
required_environment_variables: []
compatibility:
  python: ">=3.9"
  aiohttp: ">=3.9"
---
## Overview
A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.

## When to Use
- Building aiohttp web APIs that need to serve clients from different domains
- Enabling frontend applications (React, Vue, Angular) hosted on different domains to call backend APIs
- Configuring which origins can access specific routes or resources
- Handling CORS preflight requests (OPTIONS) automatically
- Exposing custom response headers to client-side JavaScript
- Allowing or restricting credential sharing (cookies, HTTP authentication)
- Implementing fine-grained CORS policies per route or resource

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.

A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors 0.8.1, enabling secure cross-origin HTTP requests with configurable origins, credentials, headers, and preflight caching.

## Installation / Setup
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

## Quick Examples
### Allow Specific Origins

```python
cors.add(
    app.router.add_route("GET", "/api/data", handler),
    {
        "https://app.example.com": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Request-ID",),
            allow_headers=("Authorization", "Content-Type"),
            max_age=86400,
        )
    }
)
```

### Public API (All Origins)

```python
cors.add(
    app.router.add_route("GET", "/api/public", handler),
    {"*": aiohttp_cors.ResourceOptions()}
)
```

**⚠️ Note:** Cannot use `"*"` with `allow_credentials=True`.

### Method-Specific Configuration

```python
# Different CORS for different methods
cors.add(app.router.add_route("GET", "/api/resource", get_handler), {"*": aiohttp_cors.ResourceOptions()})
cors.add(
    app.router.add_route("POST", "/api/resource", post_handler),
    {"https://trusted.example.com": aiohttp_cors.ResourceOptions(allow_credentials=True)}
)
```

## Configuration Options
### ResourceOptions Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_credentials` | bool | False | Allow cookies and HTTP auth headers |
| `expose_headers` | sequence or "*" | () | Headers exposed to client JavaScript |
| `allow_headers` | sequence or "*" | () | Client headers allowed in requests |
| `max_age` | int or None | None | Preflight cache duration (seconds) |
| `allow_methods` | sequence, "*", or None | None | Allowed HTTP methods |

For detailed configuration examples and advanced patterns, see [Detailed Usage](reference/01-detailed-usage.md).

## Troubleshooting
### Common Issues

**"No 'Access-Control-Allow-Origin' header"**
- Ensure CORS is configured for the specific route
- Check that request origin matches configured origins
- Verify `cors.add()` was called for the route

**Credentials flag mismatch**
- Cannot use `"*"` as origin with `allow_credentials=True`
- Must specify explicit origins when credentials are allowed

**Preflight request failing**
- Verify `allow_methods` includes the actual request method
- Ensure `allow_headers` includes all headers sent in the actual request

For comprehensive troubleshooting and debugging tips, see [Detailed Usage](reference/01-detailed-usage.md).

## Security Considerations
### Best Practices

1. **Never use `"*"` with credentials**: This is a security vulnerability
2. **Validate origins server-side**: Don't trust client-provided origin headers
3. **Use HTTPS in production**: CORS doesn't protect against MITM attacks
4. **Limit exposed headers**: Only expose what clients actually need
5. **Set appropriate max_age**: Balance between performance and flexibility

For security best practices and advanced patterns, see [Detailed Usage](reference/01-detailed-usage.md).

## Version Compatibility
- **aiohttp-cors 0.8.x**: Requires aiohttp >= 3.9, Python 3.9+
- Uses `ResourceOptions` namedtuple for configuration
- Supports defaults parameter in `setup()`

For migration guides and known issues, see [Detailed Usage](reference/01-detailed-usage.md).

## See Also
- [Detailed Usage and Examples](reference/01-detailed-usage.md) - Complete configuration patterns, examples, troubleshooting, and security best practices

## Advanced Topics
## Advanced Topics

- [Detailed Usage](reference/01-detailed-usage.md)

