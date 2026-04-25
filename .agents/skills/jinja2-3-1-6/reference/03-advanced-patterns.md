# Jinja2 Advanced Patterns and Best Practices

## Macro Patterns

### Reusable Form Elements

```jinja
{# macros/forms.html #}
{% macro text_field(name, value='', placeholder='', required=false) -%}
    <input type="text" 
           name="{{ name }}" 
           value="{{ value|e }}"
           {% if placeholder %}placeholder="{{ placeholder|e }}"{% endif %}
           {% if required %}required{% endif %}>
{%- endmacro %}

{% macro select_field(name, options, selected='', empty_option='---') -%}
    <select name="{{ name }}">
        {% if empty_option %}<option value="">{{ empty_option }}</option>{% endif %}
        {% for value, label in options %}
            <option value="{{ value|e }}" 
                    {% if value == selected %}selected{% endif %}>
                {{ label|e }}
            </option>
        {% endfor %}
    </select>
{%- endmacro %}

{% macro checkbox(name, checked=false, label='') -%}
    <label>
        <input type="checkbox" name="{{ name }}" 
               {% if checked %}checked{% endif %}>
        {{ label }}
    </label>
{%- endmacro %}
```

Usage:

```jinja
{% from 'macros/forms.html' import text_field, select_field, checkbox %}

{{ text_field('username', user.name, 'Enter username', required=true) }}
{{ select_field('country', countries, user.country) }}
{{ checkbox('subscribe', user.subscribed, 'Subscribe to newsletter') }}
```

### Macro with Caller (Higher-Order Macros)

```jinja
{% macro card(title, icon='') -%}
    <div class="card">
        <div class="card-header">
            {% if icon %}<i class="icon-{{ icon }}"></i>{% endif %}
            <h3>{{ title }}</h3>
        </div>
        <div class="card-body">
            {{ caller() }}
        </div>
    </div>
{%- endmacro %}

{% macro modal(title, size='md') -%}
    <div class="modal modal-{{ size }}" tabindex="-1">
        <div class="modal-content">
            <div class="modal-header">
                <h2>{{ title }}</h2>
                <button class="close">&times;</button>
            </div>
            <div class="modal-body">
                {{ caller() }}
            </div>
        </div>
    </div>
{%- endmacro %}
```

Usage:

```jinja
{% call card('User Profile', 'user') %}
    <p>User details go here</p>
    <button>Edit Profile</button>
{% endcall %}

{% call modal('Confirm Delete', 'sm') %}
    <p>Are you sure you want to delete this item?</p>
{% endcall %}
```

### Macro with Arguments from Caller

```jinja
{% macro user_list(users) -%}
    <ul class="user-list">
    {%- for user in users %}
        <li class="user-item">
            <span class="username">{{ user.name|e }}</span>
            {{ caller(user) }}
        </li>
    {%- endfor %}
    </ul>
{%- endmacro %}

{% call(user) user_list(all_users) %}
    <span class="email">{{ user.email|e }}</span>
    <button class="edit">Edit</button>
{% endcall %}
```

## Template Inheritance Patterns

### Layout with Optional Blocks

```jinja
{# layouts/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {% block meta %}{% endblock %}
    <title>{% block title %}Default Title{% endblock %}</title>
    {% block head_css %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    {% endblock %}
    {% block head_js %}{% endblock %}
</head>
<body>
    {% block body_start %}{% endblock %}
    
    {% if not hide_nav %}
        {% include 'partials/navigation.html' %}
    {% endif %}
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    {% block footer %}
        {% include 'partials/footer.html' %}
    {% endblock %}
    
    {% block body_js %}{% endblock %}
    {% block body_end %}{% endblock %}
</body>
</html>
```

### Multi-Level Inheritance

```jinja
{# layouts/admin_base.html #}
{% extends 'layouts/base.html' %}

{% block title %}Admin - {{ page_title|default('Dashboard') }}{% endblock %}

{% block head_css %}
    {{ super() }}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/admin.css') }}">
{% endblock %}

{% block content %}
    <aside class="admin-sidebar">
        {% include 'partials/admin_menu.html' %}
    </aside>
    <main class="admin-content">
        {% block admin_content %}{% endblock %}
    </main>
{% endblock %}
```

```jinja
{# pages/user_list.html #}
{% extends 'layouts/admin_base.html' %}

{% set page_title = 'User Management' %}

{% block admin_content %}
    <h1>Users</h1>
    {% for user in users %}
        <div class="user-row">
            <span>{{ user.name }}</span>
            <span>{{ user.email }}</span>
            <a href="{{ url_for('edit_user', user.id) }}">Edit</a>
        </div>
    {% endfor %}
{% endblock %}
```

### Conditional Layout Selection

```jinja
{# pages/article.html #}
{% if standalone %}
    <!DOCTYPE html>
    <html>
    <head><title>{{ title }}</title></head>
    <body>
{% else %}
    {% extends 'layouts/base.html' %}
    {% block content %}
{% endif %}

    <article>
        <h1>{{ title }}</h1>
        <div class="content">{{ body }}</div>
    </article>

{% if not standalone %}
    {% endblock %}
    </body>
    </html>
{% endif %}
```

## Loop Patterns

### Alternating Row Classes

```jinja
<table>
<thead>
    <tr><th>Name</th><th>Email</th><th>Role</th></tr>
</thead>
<tbody>
{% for user in users %}
    <tr class="{% if loop.index is even %}even{% else %}odd{% endif %}">
        <td>{{ user.name|e }}</td>
        <td>{{ user.email|e }}</td>
        <td>{{ user.role|e }}</td>
    </tr>
{% endfor %}
</tbody>
</table>
```

Or using `loop.cycle`:

```jinja
<tbody>
{% for user in users %}
    <tr class="{{ loop.cycle('row-1', 'row-2', 'row-3') }}">
        <td>{{ user.name }}</td>
    </tr>
{% endfor %}
</tbody>
```

### Grouped Loops

```jinja
{% for category, items in items_by_category.items() %}
    <h2>{{ category }}</h2>
    <ul>
    {% for item in items %}
        <li>{{ item.name }}</li>
    {% endfor %}
    </ul>
{% endfor %}
```

### Loop with Index-Based Logic

```jinja
<div class="grid">
{% for item in items %}
    <div class="grid-item 
                {% if loop.first %}first{% endif %} 
                {% if loop.last %}last{% endif %}
                {% if loop.index is divisibleby(3) %} highlight{% endif %}">
        <span class="index">{{ loop.index }}</span>
        {{ item.content }}
    </div>
{% endfor %}
</div>
```

### Nested Loop with Parent Access

```jinja
<table>
{% for row in table_data %}
    <tr>
        {% set row_loop = loop %}  {# Save parent loop #}
        {% for cell in row %}
            <td data-row="{{ row_loop.index }}" 
                data-col="{{ loop.index }}">
                {{ cell }}
            </td>
        {% endfor %}
    </tr>
{% endfor %}
</table>
```

### Recursive Directory Tree

```jinja
<ul class="directory-tree">
{%- for item in directory recursive %}
    <li>
        <span class="{% if item.is_dir %}folder{% else %}file{% endif %}">
            {{ item.name }}
        </span>
        {%- if item.children %}
            <ul>{{ loop(item.children) }}</ul>
        {%- endif %}
    </li>
{%- endfor %}
</ul>
```

## Conditional Patterns

### Ternary-Like Expressions

```jinja
{{ 'active' if page == current_page else '' }}
{{ user.display_name if user.display_name else user.username }}
{{ badge_color(status) if status in statuses else 'gray' }}
```

### Multiple Conditions

```jinja
{% if user.is_admin %}
    <span class="badge admin">Admin</span>
{% elif user.is_moderator %}
    <span class="badge mod">Moderator</span>
{% elif user.joined_days < 7 %}
    <span class="badge new">New User</span>
{% endif %}
```

### Inline Conditionals in Attributes

```jinja
<input type="text" name="email" 
       value="{{ user.email }}"
       {% if required_fields.includes('email') %}required{% endif %}
       {% if placeholder_email %}placeholder="{{ placeholder_email }}"{% endif %}>

<div class="card {% if featured %}featured{% endif %} {% if hidden %}hidden{% endif %}">
```

## Include Patterns

### Optional Includes

```jinja
{% include 'partials/sidebar.html' ignore missing %}
{% include optional_template ignore missing %}
```

### Include with Context

```jinja
{# Without context - isolated namespace #}
{% include 'partial.html' %}

{# With context - inherits all variables #}
{% include 'partial.html' with context %}

{# With specific variables #}
{% include 'partial.html' with items=my_items, title='Custom Title' %}
```

### Loop Includes

```jinja
{% for tab in tabs %}
    {% include 'partials/tab_' ~ tab.name ~ '.html' %}
{% endfor %}
```

## Import Patterns

### Central Macro Library

```jinja
{# macros/common.html #}
{% macro button(text, type='primary', size='md') -%}
    <button class="btn btn-{{ type }} btn-{{ size }}">{{ text|e }}</button>
{%- endmacro %}

{% macro link(text, url, new_tab=false) -%}
    <a href="{{ url }}" 
       {% if new_tab %}target="_blank" rel="noopener"{% endif %}>
        {{ text|e }}
    </a>
{%- endmacro %}

{% macro avatar(url, size=40, alt='') -%}
    <img src="{{ url }}" 
         class="avatar" 
         width="{{ size }}" 
         height="{{ size }}"
         {% if alt %}alt="{{ alt|e }}"{% endif %}>
{%- endmacro %}
```

Usage across templates:

```jinja
{% from 'macros/common.html' import button, link, avatar %}

{{ button('Submit', 'primary', 'lg') }}
{{ link('Learn More', '/docs', new_tab=true) }}
{{ avatar(user.photo, 60, user.name) }}
```

### Import with Aliases

```jinja
{% from 'macros/forms.html' import text_field as tf %}
{% from 'macros/forms.html' import select_field as sf %}

{{ tf('username') }}
{{ sf('country', countries) }}
```

## Variable and Assignment Patterns

### Default Values

```jinja
{% set username = username|default('Guest') %}
{% set limit = limit|default(10)|int %}
{% set sort_by = sort_by|default('name') %}
```

### Conditional Assignment

```jinja
{% set css_class = 'active' if current else 'inactive' %}
{% set icon = 'check' if success else 'error' %}
```

### String Concatenation

```jinja
{% set full_path = base_path ~ '/' ~ relative_path %}
{% set filename = name ~ '.' ~ extension %}
```

### Complex Data Construction

```jinja
{% set config = {
    'api_url': api_endpoint,
    'timeout': 30,
    'retry': 3,
    'features': ['auth', 'logging']
} %}

{{ config|tojson }}
```

## Performance Optimization

### Minimize Template Logic

**Bad:** Complex logic in templates

```jinja
{% for item in items %}
    {% if process(item) and validate(item) and transform(item) %}
        {{ render(transformed_item) }}
    {% endif %}
{% endfor %}
```

**Good:** Pre-process in view layer

```python
# In Python view
processed_items = [
    transform(item) 
    for item in items 
    if process(item) and validate(item)
]
```

```jinja
{# In template #}
{% for item in processed_items %}
    {{ render(item) }}
{% endfor %}
```

### Use Cache for Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(key):
    # Complex calculation
    return result
```

```jinja
{{ expensive_computation(cache_key) }}
```

### Disable Auto-Reload in Production

```python
env = Environment(
    loader=FileSystemLoader('templates'),
    auto_reload=False,  # Don't check for template changes
    cache_size=400      # Cache 400 templates
)
```

### Use Bytecode Cache

```python
from jinja2 import FileSystemBytecodeCache

env = Environment(
    loader=FileSystemLoader('templates'),
    bytecode_cache=FileSystemBytecodeCache('/tmp/jinja_cache')
)
```

### Batch Template Rendering

```python
# Compile all templates at startup
for name in env.list_templates():
    env.get_template(name)  # Pre-compile
```

## Security Best Practices

### Always Escape User Input

```jinja
{{ user_input|e }}                    # Explicit escape
{{ user_input }}                     # If autoescape enabled
{{ trusted_html|safe }}              # Only for trusted content
```

### Use Sandboxed Environment for User Templates

```python
from jinja2.sandbox import SandboxedEnvironment

env = SandboxedEnvironment()

# Store user templates in database
user_template = env.from_string(user_stored_template)
output = user_template.render(allowed_data=safe_data)
```

### Validate Template Names

```python
import re

def is_safe_template_name(name):
    return bool(re.match(r'^[a-zA-Z0-9_/\.]+$', name))

if is_safe_template_name(requested_template):
    template = env.get_template(requested_template)
else:
    raise ValueError("Invalid template name")
```

### Limit Template Complexity

```python
# Monitor render time
import time

start = time.time()
output = template.render(**context)
duration = time.time() - start

if duration > 1.0:  # Warn if takes more than 1 second
    logger.warning(f"Slow template render: {duration}s")
```

## Debugging Techniques

### Debug Undefined Variables

```python
from jinja2 import DebugUndefined

env = Environment(undefined=DebugUndefined)
# Undefined variables show as {{ variable_name }} in output
```

### Strict Mode for Development

```python
from jinja2 import StrictUndefined

env = Environment(undefined=StrictUndefined)
# Raises error immediately on undefined access
```

### Template Source Inspection

```python
source, filename, uptodate = env.get_source(env, 'template.html')
print(f"Template from: {filename}")
print(source[:500])  # First 500 chars
```

### Render with Extra Context

```jinja
{# Add debug info to templates in dev mode #}
{% if debug %}
    <div class="debug-info">
        <h3>Template Variables</h3>
        <pre>{{ vars()|tojson(indent=2) }}</pre>
    </div>
{% endif %}
```

## Common Gotchas

### Block Scope Isolation

```jinja
{# Parent template #}
{% for item in items %}
    <li>{% block item %}{% endblock %}</li>
{% endfor %}

{# Child template - item is NOT available in block #}
{% extends 'parent.html' %}

{% block item %}
    {{ item }}  {# This won't work! #}
{% endblock %}

{# Use scoped modifier instead #}
{% block item scoped %}
    {{ item }}  {# Now works #}
{% endblock %}
```

### Macro Scope Isolation

```jinja
{% macro show_name() %}
    {{ name }}  {# Uses macro's local 'name' parameter #}
{% endmacro %}

{% set name = 'Global' %}
{{ show_name() }}  {# May not use global 'name' #}
```

### Variable Assignment in Loops

```jinja
{# This doesn't work as expected #}
{% for item in items %}
    {% set total = total + item.value %}
{% endfor %}
{{ total }}  {# May be undefined or wrong #}

{# Do the summation in Python instead #}
{{ items|sum(attribute='value') }}
```
