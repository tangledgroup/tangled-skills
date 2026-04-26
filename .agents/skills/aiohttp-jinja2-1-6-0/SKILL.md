---
name: aiohttp-jinja2-1-6-0
description: Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL helpers, and async template support. Use when building Python web applications with aiohttp that require HTML templating, dynamic content generation, or server-side rendering with Jinja2 syntax.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.6.0"
tags:
  - aiohttp
  - jinja2
  - templating
  - web-framework
  - async
category: library
external_references:
  - https://github.com/aio-libs/aiohttp_jinja2
  - https://aiohttp-jinja2.readthedocs.io/
---

# aiohttp-jinja2 1.6

## Overview

Jinja2 template renderer for `aiohttp.web`. It bridges the Jinja2 templating engine with aiohttp's async web framework, providing decorator-based rendering, context processors, URL generation helpers, and both sync and async template rendering modes.

Part of the official aio-libs family, maintained by Andrew Svetlov and the aio-libs team. Licensed under Apache 2.0.

## When to Use

- Building aiohttp.web applications that need server-side HTML rendering
- Integrating Jinja2 templates with aiohttp request/response lifecycle
- Adding per-request template variables via context processors
- Generating URLs inside templates using aiohttp's router
- Rendering templates asynchronously with Jinja2 3.x async support

## Core Concepts

**Template Environment**: A `jinja2.Environment` instance stored in the aiohttp application dictionary under the key `APP_KEY` (value: `"APP_KEY"`). This is the central rendering engine — all template operations route through it.

**Handler Decorator Pattern**: The most common usage pattern decorates view handlers with `@aiohttp_jinja2.template('template_name')`. The handler returns a context dictionary, and the decorator renders it into HTML automatically.

**Context Processors**: Async callables that receive the request and return a dictionary of template variables. They run before every request via middleware, injecting per-request data (e.g., current user, session state) into all templates. Last-wins strategy — later processors can override earlier ones.

**Default Helpers**: Two built-in template globals are registered by default: `url` (route URL generation) and `static` (static file URL generation). Both can be disabled with `default_helpers=False` in `setup()`.

## Installation / Setup

Install from PyPI:

```bash
pip install aiohttp-jinja2
```

Dependencies: `aiohttp` (3.6.3+), `jinja2` (3.x+), `yarl`. Supports Python 3.8–3.12.

## Usage Examples

### Basic Setup

Initialize the template engine before running the application:

```python
import jinja2
import aiohttp_jinja2
from aiohttp import web

app = web.Application()
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('/path/to/templates/folder'),
)
```

### Decorator-Based Rendering (Function Handler)

The simplest pattern — handler returns a context dict:

```python
@aiohttp_jinja2.template('index.html')
async def handler(request):
    return {'name': 'World', 'items': [1, 2, 3]}

app.router.add_get('/', handler)
```

### Decorator-Based Rendering (Class-Based View)

Works with `aiohttp.web.View` subclasses:

```python
class IndexView(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {'name': 'World'}

app.router.add_view('/', IndexView)
```

### Explicit Template Rendering

Use `render_template()` when you need to modify the response (headers, status code, etc.):

```python
async def handler(request):
    context = {'name': 'Andrew', 'surname': 'Svetlov'}
    response = aiohttp_jinja2.render_template('tmpl.html', request, context)
    response.headers['Content-Language'] = 'ru'
    return response
```

With custom status code:

```python
async def handler(request):
    response = aiohttp_jinja2.render_template(
        'error.html', request, {'code': 404}, status=404
    )
    return response
```

### Rendering to String

When you need the rendered HTML as a string (e.g., for email bodies):

```python
async def handler(request):
    html = aiohttp_jinja2.render_string('email_body.html', request, {'user': 'Alice'})
    # use html string...
    return web.Response(text=html, content_type='text/html')
```

### Context Processors

Inject per-request variables into every template:

```python
async def user_processor(request):
    # e.g., extract from session or auth
    user = await get_current_user(request)
    return {'current_user': user}

aiohttp_jinja2.setup(
    app,
    context_processors=[user_processor, aiohttp_jinja2.request_processor],
    loader=jinja2.FileSystemLoader('templates/'),
)
```

The built-in `request_processor` adds the current `aiohttp.web.Request` to template context under the name `'request'`.

Using the injected variables in a template:

```html+jinja
<body>
  {% if current_user.is_anonymous %}
    <a href="{{ url('login') }}">Login</a>
  {% else %}
    <a href="{{ url('logout') }}">Logout</a>
  {% endif %}
</body>
```

### Template URL Helpers

The `url` helper generates URLs from aiohttp route names:

```html+jinja
{# Simple route reference #}
<a href="{{ url('index') }}">Home</a>

{# With path parameters #}
<a href="{{ url('user', id=123) }}">User Profile</a>

{# With query string #}
<a href="{{ url('search', query_={'q': 'hello', 'page': 1}) }}">Search</a>
```

For a route defined as `app.router.add_get('/users/{id}', handler, name='user')`, `{{ url('user', id=123) }}` produces `/users/123`.

The `static` helper generates static file URLs. First configure the static root:

```python
app[aiohttp_jinja2.static_root_key] = '/static'
```

Then in templates:

```html+jinja
<link rel="stylesheet" href="{{ static('css/main.css') }}">
<script src="{{ static('js/app.js') }}"></script>
```

This produces `/static/css/main.css` and `/static/js/app.js`.

### Async Template Rendering

For Jinja2 3.x async template support, enable `enable_async` in setup:

```python
aiohttp_jinja2.setup(
    app,
    enable_async=True,
    loader=jinja2.FileSystemLoader('templates/'),
)
```

Then use the async rendering functions:

```python
async def handler(request):
    return await aiohttp_jinja2.render_template_async('index.html', request, {})
```

Or render to string asynchronously:

```python
html = await aiohttp_jinja2.render_string_async('template.html', request, context)
```

The `@aiohttp_jinja2.template` decorator works with both sync and async modes — it detects the environment mode automatically.

### Custom Jinja2 Filters

Pass custom filters through setup:

```python
def format_currency(value):
    return f"${value:,.2f}"

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates/'),
    filters={'currency': format_currency},
)
```

Use in templates: `{{ price | currency }}`

### Modifying the Jinja2 Environment

Access and modify the environment after setup using `get_env()`:

```python
env = aiohttp_jinja2.get_env(app)
env.globals['year'] = 2024
env.globals['zip'] = zip  # expose builtins not available by default
```

The `app` object is always available in templates via the `'app'` global:

```html+jinja
<h1>Welcome to {{ app['site_name'] }}</h1>
```

### Disabling Default Helpers

Skip the built-in `url` and `static` helpers:

```python
aiohttp_jinja2.setup(app, loader=loader, default_helpers=False)
```

## API Reference

### setup(app, \*args, app_key=APP_KEY, context_processors=(), autoescape=True, filters=None, default_helpers=True, \*\*kwargs)

Initialize the templating system on an aiohttp application. Must be called before running the app.

- `app` — `aiohttp.web.Application` instance
- `app_key` — custom key for storing the environment (default: `APP_KEY`)
- `context_processors` — list of async callables `(request) -> dict`
- `autoescape` — passed to `jinja2.Environment`, defaults to `True`
- `filters` — dict of custom Jinja2 filters
- `default_helpers` — whether to register `url` and `static` globals (default: `True`)
- `*args`, `**kwargs` — forwarded to `jinja2.Environment` constructor (e.g., `loader=...`)

Returns the created `jinja2.Environment`.

### template(template_name, *, app_key=APP_KEY, encoding='utf-8', status=200)

Decorator for view handlers. Renders the returned context dict through the named template.

- `template_name` — template file name as resolved by the loader
- `encoding` — charset on the response (default: `'utf-8'`)
- `status` — HTTP status code on the response (default: `200`)

Works with both function handlers and class-based views. If the handler returns a `web.StreamResponse`, it passes through unchanged.

### render_template(template_name, request, context, *, app_key=APP_KEY, encoding='utf-8', status=200)

Render a template and return an `aiohttp.web.Response`. Use when you need to modify response headers or status before returning.

- `context` can be `None` (treated as empty dict)
- Raises `HTTPInternalServerError` if template not found or engine not initialized

### render_template_async(template_name, request, context, *, ...)

Async version of `render_template()`. Used when `enable_async=True` was passed to `setup()`.

### render_string(template_name, request, context, *, app_key=APP_KEY)

Render a template and return the resulting HTML string. Does not create an HTTP response.

### render_string_async(template_name, request, context, *, app_key=APP_KEY)

Async version of `render_string()`. Used when `enable_async=True` was passed to `setup()`.

### get_env(app, *, app_key=APP_KEY)

Retrieve the `jinja2.Environment` from an application. Raises `RuntimeError` if `setup()` was not called.

### request_processor(request)

Built-in context processor that adds the current request to template context under `'request'`.

### APP_KEY

The `aiohttp.web.AppKey` used to store the Jinja2 environment in the application dictionary. Value: `"APP_KEY"`.

### static_root_key

The `aiohttp.web.AppKey` for storing the static URL root. Set it with `app[aiohttp_jinja2.static_root_key] = '/static'` before using the `static()` template helper.

## Advanced Topics

### Context Processor Middleware Internals

Context processors are registered as an aiohttp middleware via `context_processors_middleware`. Results are accumulated in `request[REQUEST_CONTEXT_KEY]` and merged into the template context at render time. This means:

- Processors run on every request, even those not using templates
- Results persist across the full request lifecycle
- Later processors override earlier ones (last-wins)
- Parent application context processors compose with sub-applications

### Error Handling

When a template is not found or the engine is not initialized, aiohttp-jinja2 raises `web.HTTPInternalServerError` with both `reason` and `text` set to a descriptive message. This ensures the error appears in both console output and the rendered response body.

If a handler decorated with `@template` returns a `web.StreamResponse` instead of a dict, it is passed through unchanged — this allows conditional non-template responses from the same handler.

### AppKey Migration (1.6)

Version 1.6 switched to `aiohttp.web.AppKey` for type-safe application dictionary access. The old `'static_root_url'` string key is deprecated — use `aiohttp_jinja2.static_root_key` instead. A `DeprecationWarning` is emitted if the old key is detected.

### Version History Highlights

- **1.6** (2023) — Switch to `AppKey`, deprecate old static root key, Python 3.12 support
- **1.5.1** (2023) — Drop non-async handler support (deprecated since 0.16)
- **1.5** (2021) — Require Jinja2 3+, drop `typing_extensions` on Python 3.8+
- **1.4** (2020) — Async rendering support (`render_template_async`, `render_string_async`)
- **1.1** (2018) — Use `request.config_dict` for environment access (parent app reuse)
- **0.15** (2018) — Autoescape enabled by default
