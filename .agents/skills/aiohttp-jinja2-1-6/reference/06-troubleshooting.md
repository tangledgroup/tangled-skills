# Troubleshooting

This guide covers common issues, error messages, debugging techniques, and performance problems when using aiohttp-jinja2.

## Common Errors

### RuntimeError: aiohttp_jinja2.setup(...) must be called first

**Cause:** Trying to use template rendering before calling `setup()`.

```python
# Wrong: setup called after routes are added
app = web.Application()

@aiohttp_jinja2.template('index.html')  # Error!
async def handler(request):
    return {}

app.router.add_get('/', handler)

aiohttp_jinja2.setup(app, loader=loader)  # Too late!
```

**Solution:** Call `setup()` before adding routes:

```python
# Correct: setup called first
app = web.Application()

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

@aiohttp_jinja2.template('index.html')
async def handler(request):
    return {}

app.router.add_get('/', handler)
```

### Template 'X' not found

**Cause:** Template file doesn't exist or loader path is incorrect.

**Debugging steps:**

1. **Check template path:**
```python
import os

# Verify template exists
template_path = '/path/to/templates/index.html'
print(f"Template exists: {os.path.exists(template_path)}")
print(f"Directory contents: {os.listdir('/path/to/templates')}")
```

2. **Check loader configuration:**
```python
import jinja2

loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=loader)

# List available templates
try:
    templates = loader.list_templates()
    print(f"Available templates: {templates}")
except Exception as e:
    print(f"Error listing templates: {e}")
```

3. **Verify relative path:**
```python
# Wrong: relative to wrong directory
loader = jinja2.FileSystemLoader('templates')  # Relative to CWD

# Correct: absolute path or relative to script
from pathlib import Path
template_dir = Path(__file__).parent / 'templates'
loader = jinja2.FileSystemLoader(str(template_dir))
```

**Common path issues:**

| Issue | Solution |
|-------|----------|
| Template in subdirectory | Use `subdir/template.html` in code |
| Wrong file extension | Ensure template is `.html` or `.jinja2` |
| Case sensitivity | Linux: `Index.html` ≠ `index.html` |
| Symlink issues | Resolve symlinks: `Path.resolve()` |

### app does not define a static root url

**Cause:** Using `{{ static() }}` without setting the static root.

```python
# Missing setup causes error in template
aiohttp_jinja2.setup(app, loader=loader)
# app[aiohttp_jinja2.static_root_key] NOT SET!
```

**Solution:** Set static root after setup:

```python
import aiohttp_jinja2

app = web.Application()
aiohttp_jinja2.setup(app, loader=loader)

# Set static root URL
app[aiohttp_jinja2.static_root_key] = "/static"

# Or with CDN
app[aiohttp_jinja2.static_root_key] = "https://cdn.example.com/static"
```

**Template usage:**
```jinja2
{# Now works #}
<link rel="stylesheet" href="{{ static('css/style.css') }}">
{# Generates: /static/css/style.css #}
```

### UndefinedError: 'X' is undefined

**Cause:** Template references variable that doesn't exist in context.

**Template:**
```jinja2
<h1>{{ user.name }}</h1>  {# Error if user not in context #}
```

**Solutions:**

1. **Provide default value:**
```jinja2
<h1>{{ user.name|default('Guest') }}</h1>
<h1>{{ user.name if user else 'Guest' }}</h1>
```

2. **Use StrictUndefined in development:**
```python
import jinja2

aiohttp_jinja2.setup(
    app,
    loader=loader,
    undefined=jinja2.StrictUndefined,  # Raises error on undefined
)
```

3. **Use CondenseUndefined in production:**
```python
import jinja2

aiohttp_jinja2.setup(
    app,
    loader=loader,
    undefined=jinja2.ChainableUndefined,  # Returns empty string
)
```

4. **Check context in handler:**
```python
@aiohttp_jinja2.template('profile.html')
async def profile_handler(request):
    context = {
        'user': await get_user(request.match_info['id']),
    }
    
    # Debug: log context keys
    request.app['logger'].debug(f"Context keys: {list(context.keys())}")
    
    return context
```

## Debugging Techniques

### Enable Debug Mode

```python
import aiohttp_jinja2

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    debug=True,  # Enable debug mode
)
```

### Add Debug Context Processor

```python
async def debug_processor(request):
    import traceback
    
    return {
        '_debug': True,
        '_request_id': request.get('request_id', 'unknown'),
        '_context_vars': list(request.get('aiohttp_jinja2_context', {}).keys()),
        '_traceback': ''.join(traceback.format_stack()[-5:]),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[debug_processor],
)
```

**Debug template footer:**
```jinja2
{% if _debug %}
<div style="background: #f0f0f0; padding: 10px; font-family: monospace; font-size: 12px;">
    <strong>Debug Info:</strong><br>
    Request ID: {{ _request_id }}<br>
    Context vars: {{ _context_vars|join(', ') }}<br>
    Available globals: {{ namespace|keys|sort|join(', ') }}
</div>
{% endif %}
```

### Template Source Inspector

```python
async def inspect_template(request):
    """Debug endpoint to inspect template."""
    template_name = request.query.get('name', 'index.html')
    
    env = aiohttp_jinja2.get_env(request.app)
    
    try:
        template = env.get_template(template_name)
        source, filename, uptodate = env.loader.get_source(env, template_name)
        
        return aiohttp_jinja2.render_template(
            'debug/inspect.html',
            request,
            {
                'template_name': template_name,
                'source': source,
                'filename': filename,
                'globals': dict(env.globals),
                'filters': list(env.filters.keys()),
                'tests': list(env.tests.keys()),
            },
        )
    except jinja2.TemplateNotFound:
        return web.HTTPNotFound(f"Template '{template_name}' not found")

app.router.add_get('/_debug/template', inspect_template)
```

### Context Logger

```python
import logging

logger = logging.getLogger(__name__)

async def logging_processor(request):
    """Log all context processor output."""
    context = await your_processor(request)
    
    # Log context (be careful with sensitive data)
    safe_context = {k: v for k, v in context.items() if not k.startswith('_')}
    logger.debug(f"Template context for {request.path}: {safe_context}")
    
    return context
```

## Performance Issues

### Slow Template Rendering

**Symptoms:** High CPU usage, slow response times.

**Causes and solutions:**

1. **Expensive operations in templates:**
```jinja2
{# Bad: database query in template #}
{% for item in fetch_from_db() %}
    {{ item.name }}
{% endfor %}
```

```python
# Good: do it in handler
@aiohttp_jinja2.template('list.html')
async def list_handler(request):
    items = await fetch_from_db()  # Query once
    return {'items': items}
```

2. **Complex filters called repeatedly:**
```jinja2
{# Bad: filter called N times in loop #}
{% for item in items %}
    {{ expensive_filter(item) }}
{% endfor %}
```

```python
# Good: pre-compute in handler
async def handler(request):
    items = await fetch_items()
    processed_items = [expensive_filter(item) for item in items]
    return {'processed_items': processed_items}
```

3. **Large context dictionaries:**
```jinja2
{# Bad: pass entire database result #}
{{ all_users|length }}  {# Forces iteration over all users #}
```

```python
# Good: pass only needed data
return {
    'user_count': len(all_users),
    'featured_users': all_users[:10],
}
```

### Memory Leaks

**Symptoms:** Increasing memory usage over time.

**Causes and solutions:**

1. **Unbounded template cache:**
```python
# Default: unlimited cache (can cause memory issues)
aiohttp_jinja2.setup(app, loader=loader)  # cache_size=-1
```

```python
# Solution: limit cache size
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=100,  # Keep only 100 templates
)
```

2. **Context processor caching everything:**
```python
# Bad: cache grows indefinitely
class BadProcessor:
    def __init__(self):
        self.cache = {}
    
    async def __call__(self, request):
        key = request['user_id']
        if key not in self.cache:
            self.cache[key] = await fetch_user_data(key)  # Never expires!
        return self.cache[key]
```

```python
# Good: use TTL-based cache
from aiohttp import web

class CachedProcessor:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    async def __call__(self, request):
        key = 'global'  # Or request-specific cache key
        now = datetime.now().timestamp()
        
        if key in self.cache and (now - self.timestamps[key]) < self.ttl:
            return self.cache[key]
        
        result = await fetch_data()
        self.cache[key] = result
        self.timestamps[key] = now
        
        return result
```

### Template Cache Issues

**Symptoms:** Template changes not reflected.

**Solutions:**

1. **Development: disable cache:**
```python
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=0,  # No caching
)
```

2. **Manual cache clear:**
```python
env = aiohttp_jinja2.get_env(app)
env.cache.clear()
```

3. **Auto-reload with file watcher:**
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TemplateHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
    
    def on_modified(self, event):
        if event.src_path.endswith('.html'):
            env = aiohttp_jinja2.get_env(self.app)
            env.cache.clear()
            print(f"Template changed: {event.src_path}, cache cleared")

# Setup watcher
observer = Observer()
observer.schedule(TemplateHandler(app), 'templates', recursive=True)
observer.start()
```

## Security Issues

### XSS Vulnerabilities

**Symptoms:** User input rendered as HTML.

**Bad:**
```jinja2
{# Autoescape disabled or |safe used incorrectly #}
{{ user_input|safe }}  {# Never do this with untrusted input! #}
```

**Good:**
```jinja2
{# Autoescape enabled (default) #}
{{ user_input }}  {# Automatically escaped #}

{# Only use |safe for trusted content #}
{{ trusted_html_content|safe }}
```

**Ensure autoescape is enabled:**
```python
aiohttp_jinja2.setup(
    app,
    loader=loader,
    autoescape=True,  # Default, but explicit is good
)
```

### Template Injection

**Symptoms:** Users can modify template logic.

**Prevention:**

1. **Never use user input as template name:**
```python
# Bad: vulnerable to template injection
template_name = request.query.get('template')  # User-controlled!
return aiohttp_jinja2.render_template(template_name, request, {})
```

```python
# Good: whitelist template names
ALLOWED_TEMPLATES = {'welcome', 'goodbye', 'thanks'}
template_name = request.query.get('template', 'welcome')

if template_name not in ALLOWED_TEMPLATES:
    raise web.HTTPBadRequest("Invalid template")

return aiohttp_jinja2.render_template(f'{template_name}.html', request, {})
```

2. **Don't expose dangerous globals:**
```python
# Bad: exposes Python functions
env.globals['__import__'] = __import__
env.globals['open'] = open

# Good: only expose safe functions
env.globals['url'] = url_for
env.globals['static'] = static_url
```

## Async Rendering Issues

### Forgetting await with async rendering

**Error:**
```python
# Wrong: missing await
response = aiohttp_jinja2.render_template_async('page.html', request, {})
return response  # Returns coroutine, not response!
```

**Solution:**
```python
# Correct: use await
response = await aiohttp_jinja2.render_template_async('page.html', request, {})
return response
```

### Mixing sync and async

**Problem:**
```python
# Inconsistent: some handlers use sync, some async
@aiohttp_jinja2.template('page1.html')  # Uses render_template
async def handler1(request):
    return {}

async def handler2(request):
    # Wrong: should use render_template_async when enable_async=True
    return aiohttp_jinja2.render_template('page2.html', request, {})
```

**Solution:** Use decorator consistently or match rendering function to setup:

```python
# Setup with async
aiohttp_jinja2.setup(app, loader=loader, enable_async=True)

# All handlers should use async rendering
async def handler(request):
    return await aiohttp_jinja2.render_template_async('page.html', request, {})
```

## Migration Issues

### From aiohttp-jinja2 <1.6

**Breaking change:** `static_root_url` deprecated in favor of `static_root_key`.

**Old code (<1.6):**
```python
app['static_root_url'] = '/static'
```

**New code (1.6+):**
```python
import aiohttp_jinja2

app[aiohttp_jinja2.static_root_key] = '/static'
```

### From Flask

**Different patterns:**

| Flask | aiohttp-jinja2 |
|-------|----------------|
| `@app.template_filter()` | `filters={'name': func}` in setup() |
| `@app.context_processor()` | `context_processors=[func]` in setup() |
| `url_for('name')` | `{{ url('name') }}` (same) |
| `current_app` | `{{ app }}` in templates |
| `g.variable` | Context processor variable |

**Migration example:**
```python
# Flask
@app.template_filter('datetime')
def format_dt(value):
    return value.strftime('%Y-%m-%d')

@app.context_processor
def utility_processor():
    return {'site_name': 'My Site'}

# aiohttp-jinja2
def format_datetime(value, format='%Y-%m-%d'):
    return value.strftime(format)

async def site_processor(request):
    return {'site_name': 'My Site'}

aiohttp_jinja2.setup(
    app,
    loader=loader,
    filters={'datetime': format_datetime},
    context_processors=[site_processor],
)
```

## Best Practices Checklist

- [ ] Call `setup()` before adding routes
- [ ] Use absolute paths for template directories
- [ ] Enable autoescape (default)
- [ ] Set `static_root_key` if using `{{ static() }}`
- [ ] Use `StrictUndefined` in development
- [ ] Disable template cache in development (`cache_size=0`)
- [ ] Limit cache size in production
- [ ] Never use user input as template name
- [ ] Use `await` with async rendering functions
- [ ] Log context processor errors
- [ ] Test templates with edge cases (None, empty lists)
- [ ] Use macros for reusable components
- [ ] Implement proper error handling for template rendering

## Getting Help

**Resources:**

- **Documentation:** https://aiohttp-jinja2.aio-libs.org/
- **GitHub Issues:** https://github.com/aio-libs/aiohttp-jinja2/issues
- **aiohttp Documentation:** https://docs.aiohttp.org/
- **Jinja2 Documentation:** https://jinja.palletsprojects.com/

**When reporting issues:**

1. Include aiohttp-jinja2 version: `pip show aiohttp-jinja2`
2. Include aiohttp and Jinja2 versions
3. Provide minimal reproducible example
4. Include full error traceback
5. Describe expected vs actual behavior
