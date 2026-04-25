# Advanced Patterns

This guide covers advanced usage patterns for aiohttp-jinja2, including custom globals management, error handling strategies, multiple environments, subclassing, and integration with other aiohttp components.

## Custom Globals Management

### Adding Globals After Setup

```python
import aiohttp_jinja2

# Get environment
env = aiohttp_jinja2.get_env(app)

# Add constant values
env.globals['SITE_NAME'] = 'My Application'
env.globals['VERSION'] = '1.0.0'
env.globals['SUPPORT_EMAIL'] = 'support@example.com'

# Add functions
env.globals['current_year'] = lambda: datetime.now().year
env.globals['format_phone'] = lambda phone: f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
```

**Template usage:**
```jinja2
<footer>&copy; {{ current_year() }} {{ SITE_NAME }}</footer>
<p>Contact: {{ SUPPORT_EMAIL }}</p>
<p>Phone: {{ format_phone(user.phone) }}</p>
```

### Conditional Globals

```python
import os

env = aiohttp_jinja2.get_env(app)

if os.environ.get('ENV') == 'production':
    env.globals['ANALYTICS_ID'] = 'UA-12345678-1'
    env.globals['CDN_URL'] = 'https://cdn.example.com'
else:
    env.globals['ANALYTICS_ID'] = None
    env.globals['CDN_URL'] = '/static'
    env.globals['DEBUG_TOOLS'] = True
```

### Dynamic Globals from Database

```python
async def load_site_config(app):
    """Load configuration from database on startup."""
    config = await db.query("SELECT key, value FROM site_config")
    config_dict = {row['key']: row['value'] for row in config}
    
    env = aiohttp_jinja2.get_env(app)
    env.globals['site_config'] = config_dict

app.on_startup.append(lambda app: load_site_config(app))
```

**Template usage:**
```jinja2
<title>{{ site_config['meta_title'] }} - {{ site_config['site_name'] }}</title>
<meta name="description" content="{{ site_config['meta_description'] }}">
```

## Error Handling Strategies

### Template Not Found Handler

```python
import aiohttp_jinja2
from aiohttp import web
import jinja2

async def template_not_found_handler(request):
    """Custom handler for missing templates."""
    requested_template = request.match_info.get('template', 'unknown')
    
    # Log the error
    request.app['logger'].error(f"Template not found: {requested_template}")
    
    # Return friendly error page
    return aiohttp_jinja2.render_template(
        'errors/404.html',  # Fallback error template
        request,
        {
            'requested_template': requested_template,
            'error': f"Template '{requested_template}' not found",
        },
        status=404,
    )

app.router.add_get('/templates/{template}', template_not_found_handler)
```

### Template Rendering Error Handler

```python
import aiohttp_jinja2
from aiohttp import web
import jinja2

async def safe_render_template(template_name, request, context):
    """Render template with error handling."""
    try:
        return aiohttp_jinja2.render_template(
            template_name,
            request,
            context,
        )
    except jinja2.TemplateSyntaxError as e:
        request.app['logger'].error(f"Template syntax error in {template_name}: {e}")
        return web.HTTPInternalServerError(
            text=f"Template error: {str(e)}",
        )
    except jinja2.UndefinedError as e:
        request.app['logger'].error(f"Undefined variable in {template_name}: {e}")
        return web.HTTPInternalServerError(
            text="Template variable error",
        )
```

### Try-Except in Handlers

```python
@aiohttp_jinja2.template('user/profile.html')
async def user_profile(request):
    try:
        user_id = int(request.match_info['id'])
        user = await get_user(user_id)
        
        if not user:
            raise web.HTTPNotFound("User not found")
        
        return {
            'user': user,
            'posts': await get_user_posts(user_id),
        }
    except ValueError:
        raise web.HTTPBadRequest("Invalid user ID")
    except Exception as e:
        request.app['logger'].exception("Error loading profile")
        raise web.HTTPInternalServerError("Internal server error")
```

### Custom Undefined Handler

```python
import jinja2
import aiohttp_jinja2

class LoggingUndefined(jinja2.Undefined):
    """Log warnings for undefined variables."""
    
    def __init__(self, hint=None, obj=None, name=None, exc=None):
        super().__init__(hint, obj, name, exc)
        self.logger = None
    
    @classmethod
    def set_logger(cls, logger):
        cls.logger = logger
    
    def __str__(self):
        if self.logger:
            var_name = self.name if self.name else 'unknown'
            self.logger.warning(f"Undefined template variable: {var_name}")
        return ''

# Setup with custom undefined
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    undefined=LoggingUndefined,
)

# Set logger after app initialization
LoggingUndefined.set_logger(app['logger'])
```

## Multiple Environments

### Separate HTML and Email Templates

```python
from aiohttp import web
import jinja2
import aiohttp_jinja2

app = web.Application()

# HTML environment (autoescape enabled)
HTML_KEY = web.AppKey('html_env')
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates/html'),
    app_key=HTML_KEY,
    autoescape=True,
    undefined=jinja2.StrictUndefined,
)

# Email environment (no autoescape, different filters)
EMAIL_KEY = web.AppKey('email_env')
email_loader = jinja2.FileSystemLoader('templates/email')
email_env = aiohttp_jinja2.setup(
    app,
    loader=email_loader,
    app_key=EMAIL_KEY,
    autoescape=False,  # Email templates often have raw HTML
)

# Add email-specific filters
email_env.filters['strip_html'] = lambda text: re.sub(r'<.*?>', '', text)
email_env.filters['truncate_words'] = lambda text, n: ' '.join(str(text).split()[:n]) + '...'
```

**Usage:**
```python
async def web_handler(request):
    return aiohttp_jinja2.render_template(
        'page.html',
        request,
        {'title': 'Page'},
        app_key=HTML_KEY,
    )

async def email_handler(request):
    html = await aiohttp_jinja2.render_string_async(
        'welcome.email',
        request,
        {'user': 'John'},
        app_key=EMAIL_KEY,
    )
    await send_email('john@example.com', html)
    return web.Response(text='Email sent')
```

### Multi-Tenant Template Environments

```python
from aiohttp import web
import jinja2
import aiohttp_jinja2

app = web.Application()
tenant_envs = {}

def get_tenant_env(tenant_id):
    """Get or create environment for tenant."""
    if tenant_id not in tenant_envs:
        key = web.AppKey(f'tenant_{tenant_id}_env')
        
        # Load tenant-specific templates
        template_path = f'/templates/tenants/{tenant_id}'
        loader = jinja2.FileSystemLoader(template_path)
        
        env = aiohttp_jinja2.setup(
            app,
            loader=loader,
            app_key=key,
        )
        
        # Add tenant-specific configuration
        env.globals['tenant_id'] = tenant_id
        env.globals['tenant_brand'] = get_tenant_brand(tenant_id)
        
        tenant_envs[tenant_id] = key
    
    return tenant_envs[tenant_id]

async def tenant_handler(request):
    tenant_id = request.match_info['tenant_id']
    env_key = get_tenant_env(tenant_id)
    
    return aiohttp_jinja2.render_template(
        'index.html',
        request,
        {'data': 'value'},
        app_key=env_key,
    )
```

## Integration with aiohttp Components

### Integration with aiohttp-session

```python
from aiohttp_session import setup as session_setup
from aiohttp_session.redis import get_redis_storage
import aiohttp_jinja2

app = web.Application()

# Setup session
redis_storage = await get_redis_storage(redis_pool)
session_setup(app, redis_storage)

# Context processor for session data
async def session_processor(request):
    session = request.get('session', {})
    return {
        'flash_messages': session.pop('flash', []),
        'user_cart': session.get('cart', []),
        'preferred_language': session.get('language', 'en'),
    }

# Setup jinja2 with session processor
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    context_processors=[session_processor],
)

async def add_to_cart(request):
    session = request['session']
    session['cart'].append(request['item'])
    
    # Add flash message
    if 'flash' not in session:
        session['flash'] = []
    session['flash'].append('Item added to cart!')
    
    return web.Redirect('/cart')
```

**Template usage:**
```jinja2
{% for message in flash_messages %}
    <div class="alert alert-success">{{ message }}</div>
{% endfor %}

<div class="cart">
    {{ user_cart|length }} items
</div>
```

### Integration with aiohttp-security

```python
from aiohttp_security import setup as security_setup, AuthorizedKeyword
from aiohttp_security.policy import BasicSecurityPolicy
import aiohttp_jinja2

app = web.Application()

# Setup security
async def check_identity(request):
    # Your authentication logic
    if request.get('user'):
        return request['user']['id']
    return None

async def get_permissions(request, identity):
    user = await get_user(identity)
    return set(user['roles'])

security_setup(app, BasicSecurityPolicy(), check_identity, get_permissions)

# Context processor for security
from aiohttp_security import authorized_userid, has_permission

async def security_processor(request):
    userid = await authorized_userid(request)
    
    return {
        'is_authenticated': userid is not None,
        'is_anonymous': userid is None,
        'can_edit': await has_permission(request, 'edit'),
        'can_delete': await has_permission(request, 'delete'),
        'can_admin': await has_permission(request, 'admin'),
    }

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    context_processors=[security_processor],
)
```

**Template usage:**
```jinja2
{% if is_authenticated %}
    <a href="{{ url('profile') }}">Profile</a>
    {% if can_edit %}
        <a href="{{ url('edit', id=item.id) }}">Edit</a>
    {% endif %}
    {% if can_admin %}
        <a href="{{ url('admin') }}">Admin Panel</a>
    {% endif %}
{% else %}
    <a href="{{ url('login') }}">Login</a>
{% endif %}
```

### Integration with aiohttp-cors

```python
from aiohttp_cors import setup as cors_setup
import aiohttp_jinja2

app = web.Application()

# Setup CORS
cors = cors_setup(app)

async def handler(request):
    response = aiohttp_jinja2.render_template(
        'api_docs.html',
        request,
        {'endpoints': api_endpoints},
    )
    
    # Add CORS headers
    await cors.add(response)
    return response
```

## Template Inheritance and Layouts

### Base Layout Pattern

**base.html:**
```jinja2
<!DOCTYPE html>
<html lang="{{ preferred_language|default('en') }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ SITE_NAME }}{% endblock %}</title>
    
    {% block css %}
    <link rel="stylesheet" href="{{ static('css/base.css') }}">
    {% endblock %}
    
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            {% for item in navigation %}
                <a href="{{ item.url }}" class="{% if item.active %}active{% endif %}">
                    {{ item.name }}
                </a>
            {% endfor %}
        </nav>
    </header>
    
    <main>
        {% for message in flash_messages %}
            <div class="alert">{{ message }}</div>
        {% endfor %}
        
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; {{ current_year() }} {{ SITE_NAME }}</p>
    </footer>
    
    {% block scripts %}
    <script src="{{ static('js/app.js') }}"></script>
    {% endblock %}
</body>
</html>
```

**page.html:**
```jinja2
{% extends "base.html" %}

{% block title %}{{ page_title }} - {{ SITE_NAME }}{% endblock %}

{% block css %}
    {{ super() }}
    <link rel="stylesheet" href="{{ static('css/page.css') }}">
{% endblock %}

{% block content %}
    <h1>{{ page_title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
{% endblock %}

{% block scripts %}
    {{ super() }}
    <script src="{{ static('js/page.js') }}"></script>
{% endblock %}
```

### Macro Libraries

**macros.html:**
```jinja2
{% macro form_field(field_name, field_label, field_type='text', value='', errors=[]) %}
<div class="form-group">
    <label for="{{ field_name }}">{{ field_label }}</label>
    <input 
        type="{{ field_type }}" 
        id="{{ field_name }}" 
        name="{{ field_name }}" 
        value="{{ value|e }}"
        {% if errors %}class="error"{% endif %}
    >
    {% for error in errors %}
        <span class="error-message">{{ error }}</span>
    {% endfor %}
</div>
{% endmacro %}

{% macro pagination(current_page, total_pages, url_func) %}
<nav class="pagination">
    {% if current_page > 1 %}
        <a href="{{ url_func(current_page - 1) }}" class="prev">&laquo; Previous</a>
    {% endif %}
    
    <span class="current">Page {{ current_page }} of {{ total_pages }}</span>
    
    {% if current_page < total_pages %}
        <a href="{{ url_func(current_page + 1) }}" class="next">Next &raquo;</a>
    {% endif %}
</nav>
{% endmacro %}

{% macro card(title, content, actions=[]) %}
<div class="card">
    <div class="card-header">
        <h3>{{ title }}</h3>
    </div>
    <div class="card-body">
        {{ content }}
    </div>
    {% if actions %}
    <div class="card-actions">
        {% for action in actions %}
            <a href="{{ action.url }}" class="btn btn-{{ action.style|default('secondary') }}">
                {{ action.label }}
            </a>
        {% endfor %}
    </div>
    {% endif %}
</div>
{% endmacro %}
```

**Usage in templates:**
```jinja2
{% from "macros.html" import form_field, pagination, card %}

{# Use macros #}
{{ form_field('email', 'Email Address', 'email', user.email, form_errors.get('email', [])) }}

{{ pagination(page, total_pages, lambda p: url('list', query_={'page': p})) }}

{{ card(
    user.name,
    '<p>' ~ user.bio ~ '</p>',
    [
        {'url': url('edit_user', id=user.id), 'label': 'Edit', 'style': 'primary'},
        {'url': url('delete_user', id=user.id), 'label': 'Delete', 'style': 'danger'},
    ]
)}}
```

## Performance Optimization

### Template Pre-compilation

```python
import jinja2
import aiohttp_jinja2
from pathlib import Path

class PrecompiledLoader(jinja2.BaseLoader):
    def __init__(self, template_dir, cache_dir):
        self.template_dir = Path(template_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}
    
    def precompile(self):
        """Pre-compile all templates on startup."""
        for template_file in self.template_dir.rglob('*.html'):
            relative_path = template_file.relative_to(self.template_dir)
            self.templates[str(relative_path)] = template_file.read_text()
    
    def get_source(self, environment, template):
        if template in self.templates:
            source = self.templates[template]
            return source, template, lambda: False
        raise jinja2.TemplateNotFound(template)

# Usage
loader = PrecompiledLoader('templates', '/tmp/jinja_cache')
loader.precompile()

aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=-1,  # Keep all templates in memory
)
```

### Caching Expensive Context Processors

```python
from functools import lru_cache

class CachedProcessor:
    def __init__(self, func, ttl=300):
        self.func = func
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    async def __call__(self, request):
        cache_key = request.get('cache_key', 'default')
        
        now = datetime.now().timestamp()
        if cache_key in self.cache:
            if now - self.timestamps[cache_key] < self.ttl:
                return self.cache[cache_key]
        
        result = await self.func(request)
        self.cache[cache_key] = result
        self.timestamps[cache_key] = now
        
        return result

# Usage
@CachedProcessor(ttl=300)  # Cache for 5 minutes
async def site_config_processor(request):
    return {
        'features': await fetch_feature_flags(),
        'announcements': await fetch_announcements(),
    }

aiohttp_jinja2.setup(
    app,
    loader=loader,
    context_processors=[site_config_processor],
)
```

## Debugging Techniques

### Template Debug Mode

```python
import aiohttp_jinja2

# Development setup with debugging
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    debug=True,  # Enable debug mode
    undefined=jinja2.StrictUndefined,  # Fail on undefined variables
)
```

### Template Source Debugging

```python
async def debug_template(request):
    """Show template source and context."""
    template_name = request.query.get('template', 'index.html')
    
    env = aiohttp_jinja2.get_env(request.app)
    template = env.get_template(template_name)
    
    # Get template source
    source, filename, _ = env.loader.get_source(env, template_name)
    
    return aiohttp_jinja2.render_template(
        'debug.html',
        request,
        {
            'template_name': template_name,
            'source': source,
            'filename': filename,
            'globals': list(env.globals.keys()),
            'filters': list(env.filters.keys()),
        },
    )
```

### Context Inspector

```python
async def context_inspector_processor(request):
    """Add context inspection tools."""
    return {
        '_debug': True,
        '_context_keys': [],  # Will be populated by middleware
        '_request_info': {
            'method': request.method,
            'path': request.path,
            'query': dict(request.query),
            'headers': dict(request.headers),
        },
    }
```

**Debug template:**
```jinja2
{% if _debug %}
<div class="debug-panel">
    <h3>Context Variables</h3>
    <pre>{% for key in namespace|keys %}{{ key }}: {{ type(namespace[key]) }}{% endfor %}</pre>
    
    <h3>Request Info</h3>
    <pre>{{ _request_info|tojson(indent=2) }}</pre>
</div>
{% endif %}
```

## Best Practices

1. **Use multiple environments for different purposes** (HTML, email, API docs)
2. **Implement proper error handling** for template rendering
3. **Cache expensive context processor data**
4. **Use template inheritance** for consistent layouts
5. **Create macro libraries** for reusable components
6. **Enable debug mode only in development**
7. **Use StrictUndefined in development** to catch bugs early
8. **Pre-compile templates in production** for better performance
