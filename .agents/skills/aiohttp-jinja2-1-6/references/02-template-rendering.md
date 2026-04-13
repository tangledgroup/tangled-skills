# Template Rendering

This guide covers all template rendering methods in aiohttp-jinja2, including decorator-based rendering, explicit rendering functions, and async rendering support.

## Decorator-Based Rendering (Recommended)

The `@template` decorator is the most convenient way to render templates. It automatically handles context passing and response creation.

### Function-Based Handlers

```python
import aiohttp_jinja2
from aiohttp import web

@aiohttp_jinja2.template('index.html')
async def index_handler(request):
    return {
        'title': 'Home Page',
        'user': request['user'],
        'items': await get_items(),
    }

app.router.add_get('/', index_handler)
```

**How it works:**
1. Handler returns a dictionary (context)
2. Decorator renders template with context
3. Returns `web.Response` with rendered HTML

### Class-Based Views

```python
import aiohttp_jinja2
from aiohttp import web

class UserView(web.View):
    @aiohttp_jinja2.template('user/profile.html')
    async def get(self):
        user_id = self.request.match_info['id']
        user = await get_user(user_id)
        return {
            'user': user,
            'can_edit': self.request['user'].is_admin,
        }

app.router.add_route('GET', '/user/{id}', UserView)
```

### Decorator Parameters

```python
@aiohttp_jinja2.template(
    'error.html',           # Template name (required)
    app_key=APP_KEY,        # Custom environment key (optional)
    encoding='utf-8',       # Response encoding (default: 'utf-8')
    status=404,             # HTTP status code (default: 200)
)
async def not_found_handler(request):
    return {'error_message': 'Page not found'}
```

### Status Codes with Decorator

```python
# Return created resource
@aiohttp_jinja2.template('item.html', status=201)
async def create_item(request):
    data = await request.json()
    item = await create_item(data)
    return {'item': item}

# Redirect after POST
@aiohttp_jinja2.template('success.html', status=302)
async def submit_form(request):
    # ... process form
    return {'message': 'Form submitted'}
```

## Explicit Template Rendering

Use explicit rendering when you need more control over the response.

### render_template() - Synchronous

Returns a `web.Response` object that you can modify:

```python
import aiohttp_jinja2
from aiohttp import web

async def handler(request):
    context = {
        'title': 'Dynamic Page',
        'user': request['user'],
    }
    
    # Render template to response
    response = aiohttp_jinja2.render_template(
        'page.html',
        request,
        context,
    )
    
    # Modify response before returning
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Custom-Header'] = 'value'
    
    return response
```

### render_template() Parameters

```python
response = aiohttp_jinja2.render_template(
    'template.html',        # Template name (required)
    request,                # aiohttp.web.Request (required)
    context_dict,           # Context dictionary (optional, default: {})
    app_key=APP_KEY,        # Environment key (optional)
    encoding='utf-8',       # Response encoding (default: 'utf-8')
    status=200,             # HTTP status (default: 200)
)
```

### render_string() - Get Raw HTML

Returns rendered template as string (no response object):

```python
import aiohttp_jinja2

async def generate_email(request):
    context = {'user': 'John', 'order_id': 123}
    
    # Get raw HTML string
    html = aiohttp_jinja2.render_string(
        'email_template.html',
        request,
        context,
    )
    
    # Use string for email, file, etc.
    await send_email('user@example.com', html)
    
    return web.Response(text='Email sent')
```

## Async Template Rendering

Enable async rendering for templates with async filters or large datasets.

### Enable Async Mode

```python
import aiohttp_jinja2
import jinja2

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    enable_async=True,  # Enable async rendering
)
```

### render_template_async()

```python
async def handler(request):
    context = {
        'items': await fetch_large_dataset(),
        'user': request['user'],
    }
    
    response = await aiohttp_jinja2.render_template_async(
        'dashboard.html',
        request,
        context,
    )
    return response
```

### render_string_async()

```python
async def generate_report(request):
    context = {
        'data': await fetch_report_data(),
        'date': datetime.now(),
    }
    
    html = await aiohttp_jinja2.render_string_async(
        'report.html',
        request,
        context,
    )
    
    return web.Response(text=html, content_type='text/html')
```

### Decorator with Async Mode

The `@template` decorator automatically detects async mode:

```python
# Works with both sync and async rendering
@aiohttp_jinja2.template('page.html')
async def handler(request):
    return {'data': await fetch_data()}
```

**Note:** When `enable_async=True`, the decorator uses `render_template_async()` internally.

## Context Passing Patterns

### Empty Context

```python
@aiohttp_jinja2.template('static.html')
async def static_page(request):
    return {}  # Empty context, only globals available
```

### None Context

```python
async def handler(request):
    response = aiohttp_jinja2.render_template(
        'page.html',
        request,
        None,  # Treated as empty dict
    )
    return response
```

### Nested Context

```python
@aiohttp_jinja2.template('dashboard.html')
async def dashboard(request):
    return {
        'user': {
            'name': 'John',
            'email': 'john@example.com',
            'roles': ['admin', 'editor'],
        },
        'stats': {
            'total_users': 1000,
            'active_sessions': 42,
        },
        'recent_activity': [
            {'action': 'login', 'time': '2023-01-01'},
            {'action': 'edit', 'time': '2023-01-02'},
        ],
    }
```

### Dynamic Context Building

```python
@aiohttp_jinja2.template('results.html')
async def search_handler(request):
    context = {
        'query': request.query.get('q', ''),
    }
    
    # Add conditional context
    if request['user'].is_authenticated:
        context['saved_searches'] = await get_saved_searches(
            request['user']['id']
        )
    
    # Add search results
    context['results'] = await search_database(context['query'])
    context['result_count'] = len(context['results'])
    
    return context
```

## Response Modification Patterns

### Set Custom Headers

```python
async def handler(request):
    response = aiohttp_jinja2.render_template(
        'page.html',
        request,
        {'title': 'Page'},
    )
    
    # Add cache control
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['ETag'] = '"abc123"'
    
    # Add custom headers
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response
```

### Set Content Type

```python
async def handler(request):
    response = aiohttp_jinja2.render_template(
        'article.html',
        request,
        {'article': article},
    )
    
    # Default is text/html, but can be changed
    response.content_type = 'text/html; charset=utf-8'
    
    return response
```

### Conditional Rendering

```python
async def handler(request):
    if request.query.get('format') == 'json':
        data = {'item': await get_item()}
        return web.json_response(data)
    
    # Otherwise render template
    return aiohttp_jinja2.render_template(
        'item.html',
        request,
        {'item': await get_item()},
    )
```

## Template Not Found Handling

### Default Behavior (500 Error)

```python
@aiohttp_jinja2.template('nonexistent.html')
async def handler(request):
    return {}  # Raises HTTPInternalServerError (500)
```

### Manual Error Handling

```python
import aiohttp_jinja2
from aiohttp import web

async def handler(request):
    try:
        template = aiohttp_jinja2.get_env(request.app).get_template('dynamic.html')
        html = template.render({'data': 'value'})
        return web.Response(text=html, content_type='text/html')
    except jinja2.TemplateNotFound:
        return web.HTTPNotFound(text='Template not found')
```

### Fallback Template

```python
async def handler(request):
    template_name = request.match_info.get('page', 'index')
    
    # Check if template exists
    env = aiohttp_jinja2.get_env(request.app)
    try:
        env.get_template(f'{template_name}.html')
    except jinja2.TemplateNotFound:
        template_name = 'not_found'  # Fallback
    
    return aiohttp_jinja2.render_template(
        f'{template_name}.html',
        request,
        {'requested_page': template_name},
    )
```

## Performance Considerations

### Template Caching

Templates are cached by default. For development, disable cache:

```python
# Development: disable cache
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=0,
)

# Production: unlimited cache (default)
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=-1,
)
```

### Manual Cache Clearing

```python
env = aiohttp_jinja2.get_env(app)
env.cache.clear()  # Clear all cached templates
```

### Avoid Expensive Operations in Templates

**Bad:**
```jinja2
{# Don't do expensive operations in templates #}
{% for item in fetch_from_database() %}
    {{ item.name }}
{% endfor %}
```

**Good:**
```python
@aiohttp_jinja2.template('list.html')
async def list_handler(request):
    items = await fetch_from_database()  # Do it in handler
    return {'items': items}
```

## Common Patterns

### Render with Default Values

```python
@aiohttp_jinja2.template('page.html')
async def page_handler(request):
    return {
        'title': request.query.get('title', 'Default Title'),
        'count': len(await get_items()),
    }
```

### Conditional Template Selection

```python
async def handler(request):
    template_name = 'mobile/page.html' if is_mobile(request) else 'desktop/page.html'
    
    return aiohttp_jinja2.render_template(
        template_name,
        request,
        {'data': await get_data()},
    )
```

### Multi-Step Rendering

```python
async def wizard_handler(request):
    step = request.match_info['step']
    
    if step == 'confirm':
        # Render confirmation page
        return aiohttp_jinja2.render_template(
            'wizard/confirm.html',
            request,
            {'data': request['wizard_data']},
        )
    
    # Show form
    return aiohttp_jinja2.render_template(
        f'wizard/step_{step}.html',
        request,
        {'current_step': step},
    )
```
