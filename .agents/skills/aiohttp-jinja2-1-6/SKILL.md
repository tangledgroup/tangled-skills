---
name: aiohttp-jinja2-1-6
description: Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL helpers, and async template support. Use when building Python web applications with aiohttp that require HTML templating, dynamic content generation, or server-side rendering with Jinja2 syntax.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - jinja2
  - templating
  - aiohttp
  - web-framework
  - html-rendering
  - context-processors
category: development
required_environment_variables: []

external_references:
  - https://github.com/aio-libs/aiohttp_jinja2
  - https://aiohttp-jinja2.readthedocs.io/
---
## Overview
Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL helpers, and async template support. Use when building Python web applications with aiohttp that require HTML templating, dynamic content generation, or server-side rendering with Jinja2 syntax.

## When to Use
- Building aiohttp.web applications that require HTML templating
- Need server-side rendering with Jinja2 syntax in async handlers
- Want decorator-based template rendering (`@aiohttp_jinja2.template()`)
- Require per-request context variables (current user, request object)
- Need URL generation helpers in templates (`{{ url('route-name') }}`)
- Building web applications with dynamic content and reusable layouts

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL helpers, and async template support. Use when building Python web applications with aiohttp that require HTML templating, dynamic content generation, or server-side rendering with Jinja2 syntax.

Jinja2 template renderer for aiohttp.web applications that integrates Jinja2 templating engine with async HTTP handlers. Provides decorator-based rendering, context processors for per-request variables, URL generation helpers, and both synchronous and asynchronous template rendering support.

**Version:** 1.6 (latest as of 2023-11-18)  
**License:** Apache 2  
**Python:** 3.8+  
**Dependencies:** aiohttp ≥3.6.3, Jinja2 ≥3.0

## Installation / Setup
Install the package:

```bash
pip install aiohttp-jinja2
```

Basic initialization requires setting up a Jinja2 environment on the aiohttp application:

```python
import jinja2
import aiohttp_jinja2
from aiohttp import web

app = web.Application()

# Initialize with template loader
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('/path/to/templates/folder'),
)

# Optional: set static file root for {{ static() }} helper
app[aiohttp_jinja2.static_root_key] = "/static"
```

See [Core Concepts](reference/01-core-concepts.md) for detailed setup options and configuration.

## Usage Examples
### Decorator-Based Rendering (Recommended)

The most convenient way to render templates is using the `@template` decorator:

**Function-based handlers:**
```python
@aiohttp_jinja2.template('index.html')
async def handler(request):
    return {'name': 'Andrew', 'surname': 'Svetlov'}
```

**Class-based views:**
```python
class Handler(web.View):
    @aiohttp_jinja2.template('user-profile.html')
    async def get(self):
        return {'user_id': self.request.match_info['id']}
```

See [Template Rendering](reference/02-template-rendering.md) for all rendering methods.

### Context Processors

Add per-request variables to all templates:

```python
async def current_user_processor(request):
    userid = await authorized_userid(request)
    return {
        'current_user': {'is_anonymous': not bool(userid)},
        'user_id': userid,
    }

aiohttp_jinja2.setup(
    app,
    context_processors=[current_user_processor],
    loader=loader,
)
```

See [Context Processors](reference/03-context-processors.md) for advanced usage.

### Built-in Template Helpers

Three helpers are available by default in all templates:

- `{{ app['name'] }}` - Access application dictionary
- `{{ url('route-name', id=123) }}` - Generate URLs from route names
- `{{ static('file.css') }}` - Generate static file URLs

See [Template Helpers](reference/04-template-helpers.md) for usage examples.

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Template Rendering](reference/02-template-rendering.md)
- [Context Processors](reference/03-context-processors.md)
- [Template Helpers](reference/04-template-helpers.md)
- [Advanced Patterns](reference/05-advanced-patterns.md)
- [Troubleshooting](reference/06-troubleshooting.md)

## Troubleshooting
**Common issues:**

- `RuntimeError: aiohttp_jinja2.setup(...) must be called first` - Call setup() before adding routes
- `Template 'X' not found` - Check template path and loader configuration
- Static files not loading - Set `app[aiohttp_jinja2.static_root_key] = "/static"`

See [Troubleshooting Guide](reference/06-troubleshooting.md) for detailed solutions.

**Key differences from other frameworks:**

- Unlike Flask, aiohttp-jinja2 requires explicit setup() call
- Template decorator works with both sync and async handlers automatically
- Context processors run as middleware, not template globals
- Async rendering (`enable_async=True`) requires `render_template_async()`

## Version Compatibility
| aiohttp-jinja2 | Python | aiohttp | Jinja2 |
|----------------|--------|---------|--------|
| 1.6+           | 3.8-3.12 | ≥3.6.3  | ≥3.0   |
| 1.5.x          | 3.7-3.11 | ≥3.6.3  | ≥3.0   |
| 1.4.x          | 3.6-3.9  | ≥3.6.3  | ≥2.10.1|

**Breaking changes in 1.6:**
- Switched to `aiohttp.web.AppKey` for type safety
- Deprecated `app['static_root_url']`, use `app[aiohttp_jinja2.static_root_key]` instead
- Dropped Python 3.7 support

## Migration Notes
**From Flask/Jinja2:**
```python
# Flask style (not compatible)
@app.template_filter('datetime')
def format_dt(value): ...

# aiohttp-jinja2 style
filters = {'datetime': format_dt}
aiohttp_jinja2.setup(app, loader=loader, filters=filters)
```

**From aiohttp-jinja2 <1.6:**
```python
# Old way (deprecated)
app['static_root_url'] = '/static'

# New way (1.6+)
app[aiohttp_jinja2.static_root_key] = '/static'
```

See [Advanced Patterns](reference/05-advanced-patterns.md) for migration strategies and custom configurations.

