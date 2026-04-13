# Jinja2 Python API Reference

## Environment Configuration

### Creating an Environment

```python
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('your_package'),
    autoescape=select_autoescape(),  # Auto-enable for .html, .xml, etc.
    trim_blocks=True,
    lstrip_blocks=True,
    cache_size=400,
    auto_reload=True  # Check for template changes (disable in production)
)
```

### Environment Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `block_start_string` | str | `{%` | Block start delimiter |
| `block_end_string` | str | `%}` | Block end delimiter |
| `variable_start_string` | str | `{{` | Variable start delimiter |
| `variable_end_string` | str | `}}` | Variable end delimiter |
| `comment_start_string` | str | `{#` | Comment start delimiter |
| `comment_end_string` | str | `#}` | Comment end delimiter |
| `line_statement_prefix` | str\|None | None | Prefix for line-based statements |
| `line_comment_prefix` | str\|None | None | Prefix for line-based comments |
| `trim_blocks` | bool | False | Remove first newline after block |
| `lstrip_blocks` | bool | False | Strip leading whitespace before blocks |
| `newline_sequence` | str | `\n` | Line ending: `\n`, `\r\n`, or `\r` |
| `keep_trailing_newline` | bool | False | Preserve trailing newline |
| `extensions` | list | [] | List of extension classes/strings |
| `optimized` | bool | True | Enable code optimization |
| `undefined` | type | `Undefined` | Class for undefined variables |
| `finalize` | callable\|None | None | Process output values |
| `autoescape` | bool\|callable | False | Autoescaping configuration |
| `loader` | BaseLoader\|None | None | Template loader instance |
| `cache_size` | int | 400 | Number of cached templates (0=always reload, -1=no limit) |
| `auto_reload` | bool | True | Check for template modifications |
| `bytecode_cache` | BytecodeCache\|None | None | Bytecode caching for faster loads |
| `enable_async` | bool | False | Enable async template execution |

### Custom Delimiters

```python
env = Environment(
    variable_start_string='{{',
    variable_end_string='}}',
    block_start_string='{%',
    block_end_string='%}'
)

# ERB-style delimiters
erb_env = Environment(
    variable_start_string='<%=',
    variable_end_string='%>',
    block_start_string='<%',
    block_end_string='%>'
)
```

### Autoescaping Configuration

```python
from jinja2 import select_autoescape

# Enable for common HTML/XML extensions
env = Environment(
    autoescape=select_autoescape(
        default=True,
        enabled_extensions=('html', 'htm', 'xml')
    )
)

# Custom function based on template name
def autoescape_func(template_name):
    return template_name.endswith('.html')

env = Environment(autoescape=autoescape_func)
```

## Template Loaders

### FileSystemLoader

Load templates from filesystem directories:

```python
from jinja2 import Environment, FileSystemLoader

# Single directory
env = Environment(
    loader=FileSystemLoader('templates')
)

# Multiple search paths
env = Environment(
    loader=FileSystemLoader(['templates', 'overrides'])
)

# Get and render template
template = env.get_template('page.html')
output = template.render(user='Alice')
```

### PackageLoader

Load templates from Python package:

```python
from jinja2 import Environment, PackageLoader

# Templates in 'templates' subdirectory of package
env = Environment(
    loader=PackageLoader('myapp')
)

# Custom template directory within package
env = Environment(
    loader=PackageLoader('myapp', 'views')
)
```

### DictLoader

Load templates from dictionary (useful for testing):

```python
from jinja2 import Environment, DictLoader

templates = {
    'hello': 'Hello {{ name }}!',
    'goodbye': 'Goodbye {{ name }}!'
}

env = Environment(loader=DictLoader(templates))
template = env.get_template('hello')
```

### ChoiceLoader

Try multiple loaders in order:

```python
from jinja2 import ChoiceLoader, FileSystemLoader, DictLoader

loader = ChoiceLoader([
    FileSystemLoader('custom_templates'),  # Try first
    FileSystemLoader('default_templates')  # Fallback
])

env = Environment(loader=loader)
```

### BaseLoader Methods

All loaders implement:

- `get_environment()` - Return environment using this loader
- `get_source(environment, template)` - Load template source (returns source, filename, uptodate callable)
- `list_templates()` - List all available templates
- `resolve_or_legacy(name, parent)` - Resolve template name with parent context

## Template Rendering

### Basic Rendering

```python
template = env.get_template('page.html')

# Render with keyword arguments
output = template.render(
    username='Alice',
    items=['a', 'b', 'c'],
    show_footer=True
)

# Render with dictionary
context = {'username': 'Alice', 'items': ['a', 'b', 'c']}
output = template.render(**context)
```

### Stream Rendering

For large templates:

```python
stream = template.stream(user='Alice')
for chunk in stream:
    write_to_output(chunk)

# Or save to file
with open('output.html', 'w') as f:
    template.stream(user='Alice').dump(f)
```

### Making Environment Global

```python
from jinja2 import Environment, PackageLoader

# Create once at application startup
env = Environment(
    loader=PackageLoader('myapp'),
    autoescape=True
)

# Use throughout application
def render_template(name, **context):
    return env.get_template(name).render(**context)
```

## Custom Filters

### Registering Filters

```python
from jinja2 import Environment

env = Environment()

# Add filter after environment creation
@env.filter
def reverse(s):
    return s[::-1]

# Or use dictionary
env.filters['reverse'] = lambda s: s[::-1]

# With arguments
@env.filter
def repeat(s, times):
    return s * times
```

### Filter in Template

```jinja
{{ 'hello'|reverse }}           # olleh
{{ 'ha'|repeat(3) }}            # hahahahaha
{{ items|custom_filter(arg1, kwarg=value) }}
```

### Context-Aware Filters

Access template context in filters:

```python
from jinja2 import pass_context

@env.filter
@pass_context
def link_to_user(context, user_id):
    # Access other variables from context
    base_url = context.get('base_url', 'http://example.com')
    return f'<a href="{base_url}/users/{user_id}">{user_id}</a>'
```

### Environment-Aware Filters

Access environment in filters:

```python
from jinja2 import pass_environment

@env.filter
@pass_environment
def get_source_length(env, template_name):
    source, _, _ = env.get_source(env, template_name)
    return len(source)
```

## Custom Tests

### Registering Tests

```python
from jinja2 import Environment

env = Environment()

@env.test
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Or use dictionary
env.tests['is_prime'] = lambda n: n in [2, 3, 5, 7, 11]
```

### Test in Template

```jinja
{% if number is prime %}
    {{ number }} is a prime number
{% endif %}

{% if value is custom_test(arg1, arg2) %}...{% endif %}
```

## Undefined Types

Handle undefined variables gracefully:

### Undefined (Default)

Renders as empty string, raises error on operations:

```python
from jinja2 import Environment

env = Environment()
template = env.from_string('{{ missing }}')
print(template.render())  # Empty string

# But this raises UndefinedError
template2 = env.from_string('{{ missing|upper }}')
template2.render()  # UndefinedError
```

### DebugUndefined

Shows variable name when undefined:

```python
from jinja2 import Environment, DebugUndefined

env = Environment(undefined=DebugUndefined)
template = env.from_string('{{ missing }}')
print(template.render())  # Outputs: {{ missing }}
```

### StrictUndefined

Raises error on any access to undefined:

```python
from jinja2 import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
template = env.from_string('{{ missing }}')
template.render()  # Raises UndefinedError immediately
```

### ChainableUndefined

Allows filter chaining on undefined:

```python
from jinja2 import Environment, ChainableUndefined

env = Environment(undefined=ChainableUndefined)
template = env.from_string('{{ missing|default("fallback") }}')
print(template.render())  # fallback
```

## Sandboxed Environment

Render untrusted templates safely:

```python
from jinja2.sandbox import SandboxedEnvironment

env = SandboxedEnvironment()

# Safe - renders normally
template = env.from_string('Hello {{ name }}!')
print(template.render(name='User'))  # Hello User!

# Unsafe - raises SecurityError
template = env.from_string('{{ func.__code__.co_code }}')
try:
    template.render(func=print)
except SecurityError as e:
    print(f"Blocked: {e}")
```

### ImmutableSandboxedEnvironment

Prevent modification of mutable objects:

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

env = ImmutableSandboxedEnvironment()

# This would fail - lists are immutable in this environment
template = env.from_string('{% set items = [] %}{{ items.append(1) }}')
try:
    template.render()
except SecurityError:
    print("Cannot modify lists")
```

### Customizing Sandbox

```python
from jinja2.sandbox import SandboxedEnvironment

class CustomSandboxedEnvironment(SandboxedEnvironment):
    def is_safe_attribute(self, obj, attr, value):
        # Block additional attributes
        if attr.startswith('_'):
            return False
        if attr in ['delete', 'remove', 'execute']:
            return False
        return super().is_safe_attribute(obj, attr, value)

env = CustomSandboxedEnvironment()
```

## Async Support

Enable async template execution:

```python
from jinja2 import Environment

env = Environment(enable_async=True)

async def fetch_user_data(user_id):
    # Simulate async operation
    await asyncio.sleep(0.1)
    return {'id': user_id, 'name': f'User {user_id}'}

template = env.from_string('{{ (await get_user(1)).name }}')
result = await template.render_async(get_user=fetch_user_data)
```

### Async Filters and Tests

```python
from jinja2 import pass_environment

@env.filter
async def async_filter(value):
    # Perform async operation
    await asyncio.sleep(0.01)
    return value.upper()
```

## Meta API

Inspect templates programmatically:

```python
from jinja2 import Environment

env = Environment()
template = env.from_string('''
    {% for item in items %}
        {{ item.name }}
    {% endfor %}
''')

# Get undefined variables
undefined_vars = env.parse_template(template).undefined_names
print(undefined_vars)  # {'items'}

# Get all variable names
all_vars = env.get_template('page.html').get_coroutine().variable_names
```

## Bytecode Caching

Improve performance with bytecode caching:

```python
from jinja2 import Environment, FileSystemLoader
from jinja2.bccache import FileSystemBytecodeCache

bc_cache = FileSystemBytecodeCache('/tmp/jinja_cache')

env = Environment(
    loader=FileSystemLoader('templates'),
    bytecode_cache=bc_cache
)
```

## Global Namespace

Add global variables and functions:

```python
env = Environment()

# Add global variable
env.globals['site_name'] = 'My Website'

# Add global function
@env.global_function
def current_year():
    from datetime import datetime
    return datetime.now().year

# In template: {{ site_name }} and {{ current_year() }}
```

## Policies

Configure runtime behavior:

```python
env = Environment()

# Configure URLize filter schemes
env.policies['urlize.extra_schemes'] = ['ftp', 'news']

# Truncate leeway (default 5)
env.policies['truncate.leeway'] = 10
```

## Utilities

### Markup and Escape

```python
from markupsafe import Markup, escape

# Mark string as safe HTML
safe_html = Markup('<em>Emphasized</em>')

# Escape unsafe content
unsafe = '<script>alert("XSS")</script>'
escaped = escape(unsafe)  # &lt;script&gt;...

# In templates: {{ html\|safe }} or {{ user_input\|e }}
```

### Template Expression

Compile and evaluate expressions:

```python
env = Environment()

# Compile expression
expr = env.compile_expression('foo + bar')
result = expr(foo=10, bar=20)  # 30

# With undefined handling
expr = env.compile_expression('missing_var', undefined_to_none=False)
result = expr()  # Returns Undefined object
```
