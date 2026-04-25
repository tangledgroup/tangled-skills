# Core Concepts

This guide covers the fundamental setup and configuration of aiohttp-jinja2, including environment initialization, template loaders, autoescaping, and advanced configuration options.

## Basic Setup

### Minimal Configuration

```python
import jinja2
import aiohttp_jinja2
from aiohttp import web

app = web.Application()

# Required: initialize with a loader
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('/path/to/templates'),
)
```

### Complete Configuration

```python
import jinja2
import aiohttp_jinja2
from aiohttp import web

app = web.Application()

env = aiohttp_jinja2.setup(
    app,
    # Required: template loader
    loader=jinja2.FileSystemLoader('templates'),
    
    # Optional: context processors for per-request variables
    context_processors=[current_user_processor],
    
    # Optional: custom Jinja2 filters
    filters={
        'datetime': format_datetime,
        'currency': format_currency,
    },
    
    # Optional: disable default helpers (url, static)
    default_helpers=True,
    
    # Optional: pass any jinja2.Environment kwargs
    autoescape=True,
    undefined=jinja2.StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)
```

## Template Loaders

Jinja2 provides several loader types. Choose based on your project structure:

### FileSystemLoader (Most Common)

Load templates from a directory on disk:

```python
import jinja2
from pathlib import Path

# Single directory
loader = jinja2.FileSystemLoader('templates')

# Multiple directories (search in order)
loader = jinja2.FileSystemLoader([
    'overrides',      # Custom templates first
    'base_templates', # Fallback templates
])

# Using pathlib
template_dir = Path(__file__).parent / 'templates'
loader = jinja2.FileSystemLoader(str(template_dir))
```

**Template lookup:** If template is `user/profile.html`, FileSystemLoader looks for `templates/user/profile.html`.

### PackageLoader (For Packages)

Load templates from within a Python package:

```python
import jinja2

# Load from current package
loader = jinja2.PackageLoader('my_package', 'templates')

# Load from specific module
loader = jinja2.PackageLoader('my_package.views', 'templates')
```

**Directory structure:**
```
my_package/
    __init__.py
    templates/
        index.html
        user/
            profile.html
```

### ChoiceLoader (Fallback Strategy)

Try multiple loaders in sequence:

```python
import jinja2

loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader('custom_templates'),  # Override first
    jinja2.PackageLoader('myapp', 'templates'),   # Default templates
])
```

### BaseLoader + Custom Logic

For dynamic templates or database storage:

```python
import jinja2
from typing import Optional, Tuple

class DatabaseLoader(jinja2.BaseLoader):
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = {}
    
    def get_source(self, environment, template):
        if template not in self.cache:
            # Fetch from database
            row = self.db.query("SELECT content FROM templates WHERE name=?", (template,))
            if not row:
                raise jinja2.TemplateNotFound(template)
            self.cache[template] = row.content
        
        source = self.cache[template]
        return source, template, lambda: False  # No auto-reload
    
    def list_templates(self):
        return self.db.query("SELECT name FROM templates")
```

## Autoescaping

Autoescaping prevents XSS attacks by escaping dangerous characters in template output.

### Default Behavior (Recommended)

```python
# Autoescape enabled by default in aiohttp-jinja2
aiohttp_jinja2.setup(app, loader=loader)  # autoescape=True
```

**Autoescaped content types:**
- HTML (`text/html`) - escapes `<`, `>`, `&`, `"`, `'`
- JavaScript (`text/javascript`) - escapes JS special characters
- CSS (`text/css`) - escapes CSS special characters

### Manual Control in Templates

```jinja2
{# Explicitly escape #}
{{ user_input|e }}

{# Mark as safe (bypass escaping) #}
{{ trusted_html|safe }}

{# Autoescape block #}
{% autoescape true %}
    {{ unsafe_content }}  {# Will be escaped #}
{% endautoescape %}

{% autoescape false %}
    {{ trusted_html }}  {# Won't be escaped #}
{% endautoescape %}
```

### Disable Autoescaping (Not Recommended)

```python
aiohttp_jinja2.setup(
    app,
    loader=loader,
    autoescape=False,  # ⚠️ Security risk
)
```

**When to disable:** Only if you control all template content and use manual escaping.

### Selective Autoescaping

Use `SelectAutoEscape` for fine-grained control:

```python
import jinja2

def should_autoescape(filename):
    # Don't autoescape email templates
    if filename and filename.endswith('.email.jinja2'):
        return False
    # Autoescape HTML templates
    return filename and (filename.endswith('.html') or filename.endswith('.jinja2'))

aiohttp_jinja2.setup(
    app,
    loader=loader,
    autoescape=jinja2.select_autoescape(default=True, for_html=['.html', '.jinja2']),
)
```

## Environment Configuration

### Access the Jinja2 Environment

```python
import aiohttp_jinja2

# Get environment from application
env = aiohttp_jinja2.get_env(app)

# Modify after setup
env.globals['site_name'] = 'My Application'
env.filters['uppercase'] = lambda s: s.upper()
```

### Custom Undefined Behavior

Control how undefined variables are handled:

```python
import jinja2

# Strict: raise exception on undefined (development)
aiohttp_jinja2.setup(
    app,
    loader=loader,
    undefined=jinja2.StrictUndefined,
)

# Silent: render empty string (production)
aiohttp_jinja2.setup(
    app,
    loader=loader,
    undefined=jinja2.ChainableUndefined,
)

# Custom: show debug info
class DebugUndefined(jinja2.Undefined):
    def __str__(self):
        return f'[UNDEFINED: {self.name}]'

aiohttp_jinja2.setup(
    app,
    loader=loader,
    undefined=DebugUndefined,
)
```

### Template Caching

Control template cache behavior:

```python
# Default: cache all templates (production)
aiohttp_jinja2.setup(app, loader=loader)  # cache_size=-1 (unlimited)

# Development: disable cache for live reloading
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=0,  # No caching
)

# Limited cache size
aiohttp_jinja2.setup(
    app,
    loader=loader,
    cache_size=100,  # Keep 100 templates
)

# Manual cache invalidation
env = aiohttp_jinja2.get_env(app)
env.cache.clear()
```

### Block Streaming

Enable block-level streaming for large templates:

```python
aiohttp_jinja2.setup(
    app,
    loader=loader,
    enable_async=True,  # Required for async rendering
)

# In template, use block streaming
async def handler(request):
    response = await aiohttp_jinja2.render_template_async(
        'streaming.html',
        request,
        {'items': large_dataset},
    )
    return response
```

## Application Key Customization

Use custom app key for multiple environments:

```python
from aiohttp import web

# Default key
APP_KEY = web.AppKey('aiohttp_jinja2_environment')

# Custom key for secondary environment
CUSTOM_KEY = web.AppKey('custom_jinja2_env')

# Setup with custom key
aiohttp_jinja2.setup(
    app,
    loader=loader,
    app_key=CUSTOM_KEY,
)

# Access with same key
env = aiohttp_jinja2.get_env(app, app_key=CUSTOM_KEY)
```

## Multiple Environments

Setup different environments for different purposes:

```python
from aiohttp import web
import jinja2
import aiohttp_jinja2

app = web.Application()

# HTML templates (autoescape enabled)
HTML_KEY = web.AppKey('html_env')
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates/html'),
    app_key=HTML_KEY,
    autoescape=True,
)

# Email templates (no autoescape)
EMAIL_KEY = web.AppKey('email_env')
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates/email'),
    app_key=EMAIL_KEY,
    autoescape=False,
)

# Use specific environment
async def html_handler(request):
    return await aiohttp_jinja2.render_template_async(
        'page.html',
        request,
        {'title': 'Page'},
        app_key=HTML_KEY,
    )

async def email_handler(request):
    return await aiohttp_jinja2.render_template_async(
        'welcome.email',
        request,
        {'user': 'John'},
        app_key=EMAIL_KEY,
    )
```

## Best Practices

1. **Always enable autoescape** unless you have a specific reason not to
2. **Use FileSystemLoader for development**, PackageLoader for distributions
3. **Set cache_size=0 in development** for live template reloading
4. **Use StrictUndefined in development** to catch template bugs early
5. **Store templates outside web root** for security
6. **Use ChoiceLoader for template overrides** (themes, localization)

## Common Patterns

### Template Inheritance Setup

```python
# Base layout
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    extensions=[
        'jinja2.ext.loopcontrols',  # {% break %}, {% continue %}
        'jinja2.ext.do',            # {% set x = y %} in blocks
    ],
)
```

### Production Configuration

```python
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('/opt/app/templates'),
    cache_size=-1,              # Unlimited cache
    autoescape=True,            # Security
    undefined=jinja2.Missing,   # Silent failures
    trim_blocks=True,           # Clean output
    lstrip_blocks=True,         # Remove indentation
)
```

### Development Configuration

```python
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('templates'),
    cache_size=0,                      # No cache
    autoescape=True,
    undefined=jinja2.StrictUndefined,  # Catch errors
    debug=True,                        # Debug mode
)
```
