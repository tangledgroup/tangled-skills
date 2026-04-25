# Template Helpers

aiohttp-jinja2 provides built-in helper functions available in all templates. This guide covers the default helpers (`url()`, `static()`, `app`) and how to create custom helpers and filters.

## Built-in Helpers

### url() - URL Generation

Generate URLs from route names instead of hardcoding paths:

```jinja2
{# Basic usage with route name #}
<a href="{{ url('index') }}">Home</a>
<a href="{{ url('about') }}">About</a>

{# With route parameters #}
<a href="{{ url('user_profile', id=123) }}">View Profile</a>
<a href="{{ url('post', slug='my-first-post') }}">Read Post</a>

{# Multiple parameters #}
<a href="{{ url('comment', post_id=42, comment_id=123) }}">Comment</a>

{# With query parameters #}
<a href="{{ url('search', query_={'q': 'python', 'page': 1}) }}">Search</a>
<a href="{{ url('products', category='electronics', query_={'sort': 'price'}) }}">Products</a>
```

**Python equivalent:**
```python
# Route definition
app.router.add_get('/user/{id}', user_handler, name='user_profile')

# Template: {{ url('user_profile', id=123) }}
# Generates: /user/123
```

### url() with Query Parameters

The `query_` parameter adds query strings to generated URLs:

```jinja2
{# Single query param #}
<a href="{{ url('search', query_={'q': 'python'}) }}">Search Python</a>
{# Generates: /search?q=python #}

{# Multiple query params #}
<a href="{{ url('products', query_={'category': 'books', 'sort': 'price', 'page': 2}) }}">
    Books by Price
</a>
{# Generates: /products?category=books&sort=price&page=2 #}

{# Route params + query params #}
<a href="{{ url('user_posts', id=42, query_={'sort': 'date'}) }}">
    User Posts
</a>
{# Generates: /user/42/posts?sort=date #}
```

### static() - Static File URLs

Generate URLs for static files (CSS, JS, images):

```jinja2
{# Basic usage #}
<link rel="stylesheet" href="{{ static('css/style.css') }}">
<script src="{{ static('js/app.js') }}"></script>
<img src="{{ static('images/logo.png') }}" alt="Logo">

{# Nested paths #}
<link rel="stylesheet" href="{{ static('css/components/buttons.css') }}">
<script src="{{ static('vendor/jquery/jquery.min.js') }}"></script>
```

**Setup required:**
```python
import aiohttp_jinja2

app = web.Application()
aiohttp_jinja2.setup(app, loader=loader)

# Set static root URL
app[aiohttp_jinja2.static_root_key] = "/static"

# Or with CDN
app[aiohttp_jinja2.static_root_key] = "https://cdn.example.com/static"
```

**Generated URLs:**
- `{{ static('css/style.css') }}` → `/static/css/style.css`
- `{{ static('images/logo.png') }}` → `/static/images/logo.png`
- With CDN: `{{ static('js/app.js') }}` → `https://cdn.example.com/static/js/app.js`

### app - Application Dictionary

Access application-wide variables:

```jinja2
{# Access app configuration #}
<h1>{{ app['name'] }}</h1>
<p>Version: {{ app['version'] }}</p>

{# Conditional based on app settings #}
{% if app['debug_mode'] %}
    <div class="debug-panel">Debug tools enabled</div>
{% endif %}

{# Use app settings in URLs #}
<a href="{{ app['api_base_url'] }}/users">API Users</a>
```

**Setup:**
```python
app = web.Application()
app['name'] = 'My Application'
app['version'] = '1.0.0'
app['debug_mode'] = True
app['api_base_url'] = 'https://api.example.com'

aiohttp_jinja2.setup(app, loader=loader)
```

## Disabling Default Helpers

Disable built-in helpers if not needed:

```python
aiohttp_jinja2.setup(
    app,
    loader=loader,
    default_helpers=False,  # Disable url(), static(), app
)
```

**Use case:** When you want to implement custom versions or use different naming.

## Custom Filters

Custom filters transform template variables.

### Adding Custom Filters

```python
import aiohttp_jinja2
import jinja2
from datetime import datetime

# Define filter functions
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime object to string."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

def currency(value, symbol='$'):
    """Format number as currency."""
    return f"{symbol}{float(value):,.2f}"

def word_count(value):
    """Count words in string."""
    return len(str(value).split())

# Register filters
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    filters={
        'datetime': format_datetime,
        'currency': currency,
        'word_count': word_count,
    },
)
```

### Using Custom Filters in Templates

```jinja2
{# Datetime formatting #}
<p>Published: {{ post.created_at|datetime }}</p>
<p>Published: {{ post.created_at|datetime('%B %d, %Y') }}</p>

{# Currency formatting #}
<p>Price: {{ product.price|currency }}</p>
<p>Price: {{ product.price|currency('€') }}</p>
<p>Price: {{ product.price|currency('¥') }}</p>

{# Word count #}
<p>{{ article.content|word_count }} words</p>

{# Chain filters #}
<p>{{ text|truncate(100)|upper }}</p>
<p>{{ price|round(2)|currency }}</p>
```

### Common Custom Filter Patterns

#### Text Processing Filters

```python
def truncate(value, length=100, suffix='...'):
    """Truncate string to length with suffix."""
    if len(str(value)) <= length:
        return value
    return str(value)[:length] + suffix

def slugify(value):
    """Convert string to URL-friendly slug."""
    import re
    value = str(value).lower()
    value = re.sub(r'[^\w\s-]', '', value)
    value = re.sub(r'[-\s]+', '-', value)
    return value.strip('-')

def highlight(value, keyword):
    """Highlight keyword in text."""
    import html
    value = html.escape(str(value))
    keyword = html.escape(str(keyword))
    return value.replace(keyword, f'<mark>{keyword}</mark>')

filters = {
    'truncate': truncate,
    'slugify': slugify,
    'highlight': highlight,
}
```

**Template usage:**
```jinja2
<p>{{ article.title|slugify }}</p>
<p>{{ description|truncate(200) }}</p>
<p>{{ content|highlight(search_query) }}</p>
```

#### Data Formatting Filters

```python
def human_readable_size(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_value) < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def time_ago(value):
    """Format datetime as 'X minutes ago'."""
    from datetime import datetime
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    
    delta = datetime.now() - value
    
    if delta.total_seconds() < 60:
        return 'Just now'
    elif delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    else:
        days = int(delta.total_seconds() / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'

filters = {
    'filesize': human_readable_size,
    'ago': time_ago,
}
```

**Template usage:**
```jinja2
<p>File size: {{ file.size|filesize }}</p>
<p>Posted {{ post.created_at|ago }}</p>
```

#### List Processing Filters

```python
def first_item(value, default=None):
    """Get first item from list."""
    return value[0] if value else default

def last_item(value, default=None):
    """Get last item from list."""
    return value[-1] if value else default

def random_item(value):
    """Get random item from list."""
    import random
    return random.choice(value) if value else None

def join_list(value, separator=', '):
    """Join list items with separator."""
    return separator.join(str(item) for item in value)

filters = {
    'first': first_item,
    'last': last_item,
    'random': random_item,
    'join': join_list,
}
```

**Template usage:**
```jinja2
<p>First tag: {{ tags|first }}</p>
<p>Tags: {{ tags|join(', ') }}</p>
<p>Random quote: {{ quotes|random }}</p>
```

## Custom Global Functions

Add custom functions to template globals.

### Using get_env()

```python
import aiohttp_jinja2

# Get environment after setup
env = aiohttp_jinja2.get_env(app)

# Add custom global function
def current_year():
    from datetime import datetime
    return datetime.now().year

def site_url(path=''):
    base = app['site_base_url']
    return f"{base.rstrip('/')}/{path.lstrip('/')}"

env.globals.update(
    year=current_year,
    site_url=site_url,
)
```

**Template usage:**
```jinja2
<footer>&copy; {{ year() }} My Site</footer>
<a href="{{ site_url('/about') }}">About</a>
```

### Common Global Function Patterns

#### Utility Functions

```python
env.globals.update(
    # Generate random string
    random_string=lambda length=8: ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    ),
    
    # Format ISO datetime
    iso_now=lambda: datetime.now().isoformat(),
    
    # Check if list is empty
    is_empty=lambda x: len(x) == 0 if x else True,
    
    # Safe get with default
    get=lambda d, key, default=None: d.get(key, default) if isinstance(d, dict) else default,
)
```

**Template usage:**
```jinja2
<input type="hidden" name="token" value="{{ random_string(32) }}">
<meta name="generated" content="{{ iso_now() }}">
{% if items|is_empty %}No items found{% endif %}
<p>{{ config|get('title', 'Default Title') }}</p>
```

#### URL Helper Functions

```python
def absolute_url(relative_path):
    """Convert relative path to absolute URL."""
    base = app['site_url']
    return f"{base.rstrip('/')}{relative_path}"

def api_endpoint(resource, id=None):
    """Generate API endpoint URL."""
    base = app['api_base_url']
    url = f"{base}/{resource}"
    if id:
        url += f"/{id}"
    return url

env.globals.update(
    absolute_url=absolute_url,
    api_endpoint=api_endpoint,
)
```

**Template usage:**
```jinja2
<link rel="canonical" href="{{ absolute_url(request.path) }}">
<script>
    const API_URL = "{{ api_endpoint('users', user_id) }}";
</script>
```

## Jinja2 Built-in Filters

Jinja2 provides many built-in filters:

```jinja2
{# String filters #}
{{ text|lower }}
{{ text|upper }}
{{ text|title }}
{{ text|capitalize }}
{{ text|trim }}
{{ text|striptags }}
{{ text|escape }}
{{ text|e }}
{{ text|safe }}

{# List filters #}
{{ items|length }}
{{ items|first }}
{{ items|last }}
{{ items|reverse }}
{{ items|sort }}
{{ items|unique }}
{{ items|sum }}

{# Number filters #}
{{ number|round(2) }}
{{ number|int }}
{{ number|float }}
{{ number|abs }}

{# Date filters (with custom filter) #}
{{ datetime_obj|datetime('%Y-%m-%d') }}

{# Dictionary filters #}
{{ dict|keys }}
{{ dict|values }}
{{ dict|items }}
{{ dict|tojson }}
```

## Best Practices

1. **Use `url()` instead of hardcoded paths** - Makes refactoring easier
2. **Register filters in setup()** - Keeps configuration centralized
3. **Name filters descriptively** - Use verbs like `format_`, `convert_`
4. **Handle None values gracefully** - Check for None in filters
5. **Use built-in filters when possible** - They're optimized and tested
6. **Document custom filters** - Add docstrings to filter functions
7. **Test filters independently** - Unit test complex filters

## Common Pitfalls

### Forgetting query_ Prefix

```jinja2
{# Wrong: 'q' treated as route parameter #}
{{ url('search', q='python') }}  {# Error if route has no 'q' param #}

{# Correct: use query_ prefix #}
{{ url('search', query_={'q': 'python'}) }}  {# /search?q=python #}
```

### Static Root Not Set

```python
# Missing setup will cause error in template
aiohttp_jinja2.setup(app, loader=loader)
# app[aiohttp_jinja2.static_root_key] NOT SET!

# Template: {{ static('css/style.css') }}
# RuntimeError: app does not define a static root url
```

### Filter Name Conflicts

```python
# Problem: overwrites built-in filter
filters = {
    'length': my_custom_length,  # Overwrites {{ items|length }}
}

# Solution: use unique name
filters = {
    'my_length': my_custom_length,  # {{ items|my_length }}
}
```
