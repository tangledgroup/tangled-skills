# Context Processors

Context processors add per-request variables to all templates. Unlike global variables (which are constant), context processors run on every request and can access request-specific data like the current user, session, or request metadata.

## Basic Usage

### Define a Context Processor

Context processors are async functions that take a request and return a dictionary:

```python
async def my_processor(request):
    return {
        'site_name': 'My Application',
        'current_year': 2024,
        'user_ip': request.remote,
    }
```

### Register Context Processors

Pass processors to `setup()`:

```python
import aiohttp_jinja2
import jinja2

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    context_processors=[my_processor],
)
```

### Use in Templates

Variables from context processors are available in all templates:

```jinja2
<!DOCTYPE html>
<html>
<head>
    <title>{{ site_name }} - {{ page_title }}</title>
</head>
<body>
    <p>Your IP: {{ user_ip }}</p>
    <footer>&copy; {{ current_year }} {{ site_name }}</footer>
</body>
</html>
```

## Built-in Context Processors

### request_processor()

Adds the `request` object to template context:

```python
import aiohttp_jinja2

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[aiohttp_jinja2.request_processor],
)
```

**Usage in templates:**

```jinja2
{# Access request URL #}
<a href="{{ request.url }}">Current Page</a>

{# Check query parameters #}
{% if request.query.get('debug') %}
    <div class="debug">Debug mode enabled</div>
{% endif %}

{# Access match info (route parameters) #}
<h1>User: {{ request.match_info['id'] }}</h1>

{# Check headers #}
{% if request.headers.get('X-Requested-With') == 'XMLHttpRequest' %}
    {# AJAX request handling #}
{% endif %}
```

## Common Context Processor Patterns

### Current User Authentication

```python
from aiohttp_security import authorized_userid

async def current_user_processor(request):
    userid = await authorized_userid(request)
    
    if userid:
        user = await get_user_from_database(userid)
        return {
            'current_user': user,
            'user_id': userid,
            'is_authenticated': True,
            'is_anonymous': False,
        }
    
    return {
        'current_user': None,
        'user_id': None,
        'is_authenticated': False,
        'is_anonymous': True,
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[current_user_processor],
)
```

**Template usage:**

```jinja2
<nav>
    {% if current_user.is_anonymous %}
        <a href="{{ url('login') }}">Login</a>
        <a href="{{ url('register') }}">Register</a>
    {% else %}
        <span>Hello, {{ current_user.name }}!</span>
        <a href="{{ url('profile') }}">Profile</a>
        <a href="{{ url('logout') }}">Logout</a>
    {% endif %}
</nav>
```

### Session Data

```python
async def session_processor(request):
    session = request.get('session', {})
    
    return {
        'flash_messages': session.pop('flash', []),
        'cart_items': session.get('cart', []),
        'preferred_language': session.get('language', 'en'),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[session_processor],
)
```

**Template usage:**

```jinja2
{# Display flash messages #}
{% for message in flash_messages %}
    <div class="alert">{{ message }}</div>
{% endfor %}

{# Show cart count #}
<span class="cart-icon">
    🛒 {{ cart_items|length }}
</span>
```

### Request Metadata

```python
from datetime import datetime

async def metadata_processor(request):
    return {
        'request_id': request.get('request_id', 'unknown'),
        'timestamp': datetime.now().isoformat(),
        'is_https': request.scheme == 'https',
        'is_xhr': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        'user_agent': request.headers.get('User-Agent', ''),
        'accept_language': request.headers.get('Accept-Language', 'en'),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[metadata_processor],
)
```

### Navigation and Breadcrumbs

```python
async def navigation_processor(request):
    current_route = request.match_info.get('section', 'home')
    
    return {
        'current_section': current_route,
        'navigation': [
            {'name': 'Home', 'url': url('home'), 'active': current_route == 'home'},
            {'name': 'Products', 'url': url('products'), 'active': current_route == 'products'},
            {'name': 'About', 'url': url('about'), 'active': current_route == 'about'},
            {'name': 'Contact', 'url': url('contact'), 'active': current_route == 'contact'},
        ],
        'breadcrumbs': get_breadcrumbs(request),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[navigation_processor],
)
```

**Template usage:**

```jinja2
<nav>
    {% for item in navigation %}
        <a href="{{ item.url }}" class="{% if item.active %}active{% endif %}">
            {{ item.name }}
        </a>
    {% endfor %}
</nav>

<ul class="breadcrumbs">
    {% for crumb in breadcrumbs %}
        <li>{% if crumb.url %}<a href="{{ crumb.url }}">{% endif %}
            {{ crumb.name }}
            {% if crumb.url %}</a>{% endif %}</li>
    {% endfor %}
</ul>
```

## Multiple Context Processors

### Combining Processors

Multiple processors are executed in order, with later processors able to override earlier ones:

```python
async def base_processor(request):
    return {
        'site_name': 'My Site',
        'version': '1.0',
        'debug': False,
    }

async def user_processor(request):
    return {
        'current_user': await get_current_user(request),
        'user_preferences': await get_user_prefs(request),
    }

async def debug_processor(request):
    # Override debug flag in development
    return {
        'debug': app['debug_mode'],
        'request_start_time': request.get('start_time'),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[base_processor, user_processor, debug_processor],
)
```

### Last-Win Strategy

Later processors override earlier ones for the same key:

```python
async def processor_one(request):
    return {'theme': 'light', 'language': 'en'}

async def processor_two(request):
    return {'theme': 'dark'}  # Overrides theme from processor_one

# Result in template: theme='dark', language='en'
aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[processor_one, processor_two],
)
```

## Conditional Context Processors

### Environment-Based Processors

```python
import os

async def production_processor(request):
    return {
        'analytics_id': 'UA-12345678-1',
        'cdn_url': 'https://cdn.example.com',
    }

async def development_processor(request):
    return {
        'analytics_id': None,
        'cdn_url': '/static',
        'debug_tools': True,
    }

# Choose processor based on environment
processors = [development_processor] if os.environ.get('ENV') == 'dev' else [production_processor]

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=processors,
)
```

### Request-Based Conditional Logic

```python
async def adaptive_processor(request):
    context = {}
    
    # Add mobile-specific variables
    if is_mobile(request):
        context['is_mobile'] = True
        context['mobile_menu'] = await get_mobile_menu()
    else:
        context['is_mobile'] = False
        context['desktop_menu'] = await get_desktop_menu()
    
    # Add API context for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context['api_base_url'] = '/api/v1'
        context['csrf_token'] = request['csrf_token']
    
    return context

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[adaptive_processor],
)
```

## Context Processor Middleware

Context processors run as middleware, executing before the handler:

```python
# Middleware execution order:
# 1. Context processor middleware (all processors run)
# 2. Your request handler
# 3. Template rendering (with accumulated context)

async def profiling_processor(request):
    request['profile_start'] = datetime.now()
    return {'profile_id': generate_profile_id()}

async def handler(request):
    # Handler runs here
    await do_expensive_operation()
    
    return {'data': 'result'}

# After handler, in template:
# {{ profile_id }} is available
```

## Debugging Context Processors

### Log Processor Output

```python
import logging

logger = logging.getLogger(__name__)

async def debug_processor(request):
    context = {
        'debug_info': True,
        'processor_output': {},
    }
    
    # Log what each processor adds
    for processor_name in ['user', 'session', 'metadata']:
        processor_context = await get_processor_context(request, processor_name)
        context['processor_output'][processor_name] = processor_context
        logger.debug(f"{processor_name} processor: {processor_context}")
    
    return context
```

### Inspect Context in Template

```jinja2
{# Debug template to see all available variables #}
<pre>
{% for key, value in namespace|dictsort %}
{{ key }}: {{ value }}
{% endfor %}
</pre>
```

## Performance Considerations

### Avoid Expensive Operations

**Bad:**
```python
async def slow_processor(request):
    # Don't query database on every request
    return {
        'all_users': await fetch_all_users(),  # Expensive!
        'site_stats': await calculate_stats(),  # Expensive!
    }
```

**Good:**
```python
async def efficient_processor(request):
    # Use cached data or lightweight operations
    cache = request.app['cache']
    
    return {
        'site_stats': await cache.get('site_stats', default={}),
        'featured_items': await cache.get('featured', default=[]),
    }
```

### Lazy Evaluation

```python
class LazyContext:
    def __init__(self, request, loader_func):
        self.request = request
        self.loader = loader_func
        self._data = None
    
    async def load(self):
        if self._data is None:
            self._data = await self.loader(self.request)
        return self._data

async def lazy_processor(request):
    return {
        'expensive_data': LazyContext(
            request,
            lambda req: fetch_expensive_data(req)
        ),
    }
```

## Best Practices

1. **Keep processors lightweight** - Avoid expensive database queries
2. **Use caching** - Cache expensive data in app context
3. **Name variables clearly** - Use descriptive names to avoid conflicts
4. **Document processor output** - Comment what each processor provides
5. **Test processors independently** - Unit test each processor
6. **Order matters** - Place override processors last
7. **Use request_processor for request access** - Built-in processor is optimized

## Common Pitfalls

### Variable Name Conflicts

```python
# Problem: Both processors define 'user'
async def processor_one(request):
    return {'user': await get_current_user()}

async def processor_two(request):
    return {'user': await get_guest_user()}  # Overrides processor_one!

# Solution: Use unique names
async def processor_one(request):
    return {'current_user': await get_current_user()}

async def processor_two(request):
    return {'guest_user': await get_guest_user()}
```

### Forgetting Async

```python
# Wrong: sync function (won't work)
def bad_processor(request):
    return {'data': get_data()}  # Must be async!

# Correct: async function
async def good_processor(request):
    return {'data': await get_data()}
```

### Modifying Request Directly

```python
# Bad: modifies request object
async def bad_processor(request):
    request['user'] = await get_user()  # Don't do this!
    return {}

# Good: return context dict
async def good_processor(request):
    return {'user': await get_user()}
```
