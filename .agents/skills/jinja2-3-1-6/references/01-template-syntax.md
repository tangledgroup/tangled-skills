# Jinja2 Template Syntax Reference

## Delimiters

Jinja2 uses three types of delimiters:

| Delimiter | Purpose | Example |
|-----------|---------|---------|
| `{% ... %}` | Statements (control structures) | `{% if user %}...{% endif %}` |
| `{{ ... }}` | Expressions (output values) | `{{ user.name }}` |
| `{# ... #}` | Comments (not in output) | `{# This is a comment #}`

## Variables

### Accessing Attributes and Items

```jinja
{{ user.name }}           # Attribute access
{{ user['name'] }}        # Item access (equivalent)
{{ config.database.host }}  # Nested access
{{ items[0] }}            # Index access
```

**Lookup order:** `foo.bar` first checks attribute, then item. `foo['bar']` checks item first, then attribute.

### Undefined Variables

By default, undefined variables render as empty strings when printed:

```jinja
{{ undefined_var }}        # Renders as ""
{% if undefined_var %}     # Evaluates to False
```

Use filters to handle undefined values:

```jinja
{{ name|default('Anonymous') }}
{{ items|default([])|length }}
```

## Filters

Filters modify variables using the pipe (`|`) symbol. Multiple filters can be chained:

```jinja
{{ name|striptags|title }}          # Remove HTML tags, then title-case
{{ list|join(', ') }}               # Join list with commas
{{ text|truncate(50) }}             # Truncate to 50 characters
{{ price|float|round(2)|string }}   # Chain multiple filters
```

### Common Builtin Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `e` or `escape` | HTML escape | `{{ user_input\|e }}` |
| `safe` | Mark as safe HTML | `{{ trusted_html\|safe }}` |
| `upper`/`lower` | Case conversion | `{{ text\|upper }}` |
| `title` | Title case | `{{ text\|title }}` |
| `capitalize` | Capitalize first letter | `{{ text\|capitalize }}` |
| `reverse` | Reverse sequence | `{{ list\|reverse }}` |
| `sort` | Sort iterable | `{{ items\|sort }}` |
| `length` or `count` | Count items | `{{ items\|length }}` |
| `first`/`last` | First/last item | `{{ items\|first }}` |
| `join(sep)` | Join with separator | `{{ list\|join(', ') }}` |
| `default(val)` | Default if undefined | `{{ var\|default('N/A') }}` |
| `dictsort` | Sort dict by keys | `{{ my_dict\|dictsort }}` |
| `int`/`float` | Type conversion | `{{ string\|int }}` |
| `string` | Convert to string | `{{ number\|string }}` |
| `list` | Convert to list | `{{ tuple\|list }}` |
| `sum(attribute)` | Sum values | `{{ items\|sum('price') }}` |
| `unique` | Remove duplicates | `{{ list\|unique }}` |
| `map(attribute)` | Extract attribute | `{{ users\|map('name') }}` |
| `selectattr(name, value)` | Filter by attribute | `{{ items\|selectattr('active', true) }}` |
| `rejectattr(name, value)` | Reject by attribute | `{{ items\|rejectattr('hidden', true) }}` |
| `tojson(indent)` | Serialize to JSON | `{{ data\|tojson(2) }}` |
| `wordwrap(width)` | Wrap text | `{{ text\|wordwrap(60) }}` |
| `urlize` | Convert URLs to links | `{{ text\|urlize }}` |
| `striptags` | Remove HTML tags | `{{ html\|striptags }}` |
| `truncate(length)` | Truncate string | `{{ text\|truncate(100) }}` |

### Filter with Arguments

```jinja
{{ list|join(', ') }}              # Single argument
{{ text|truncate(50, killwords=true) }}  # Multiple arguments
{{ items|sort(attribute='name', case_sensitive=false) }}
```

## Tests

Tests check variables against conditions using `is`:

```jinja
{% if variable is defined %}...{% endif %}
{% if number is even %}...{% endif %}
{% if value is divisibleby(3) %}...{% endif %}
```

### Common Builtin Tests

| Test | Description | Example |
|------|-------------|---------|
| `defined` | Variable exists | `{{\|var is defined }}` |
| `undefined` | Variable missing | `{{\|var is undefined }}` |
| `none` | Value is None | `{{\|var is none }}` |
| `boolean` | Is boolean type | `{{\|var is boolean }}` |
| `integer` | Is integer type | `{{\|var is integer }}` |
| `float` | Is float type | `{{\|var is float }}` |
| `number` | Is numeric | `{{\|var is number }}` |
| `string` | Is string type | `{{\|var is string }}` |
| `sequence` | Is iterable | `{{\|var is sequence }}` |
| `mapping` | Is dict-like | `{{\|var is mapping }}` |
| `callable` | Is callable | `{{\|var is callable }}` |
| `even`/`odd` | Even/odd number | `{{\|n is even }}` |
| `lower`/`upper` | Case check | `{{\|text is lower }}` |
| `escaped` | Is HTML-escaped | `{{\|html is escaped }}` |
| `in(seq)` | In sequence | `{{\|item in items }}` |
| `divisibleby(n)` | Divisible by n | `{{\|n is divisibleby(2) }}` |
| `eq(val)` or `==` | Equal to | `{{\|x eq 5 }}` |
| `ne(val)` or `!=` | Not equal | `{{\|x ne 5 }}` |
| `gt(val)` or `>` | Greater than | `{{\|x gt 5 }}` |
| `ge(val)` or `>=` | Greater or equal | `{{\|x ge 5 }}` |
| `lt(val)` or `<` | Less than | `{{\|x lt 5 }}` |
| `le(val)` or `<=` | Less or equal | `{{\|x le 5 }}` |
| `sameas(obj)` | Same object (is) | `{{\|x is sameas None }}` |

## Control Structures

### For Loops

```jinja
<ul>
{% for user in users %}
    <li>{{ user.name }}</li>
{% endfor %}
</ul>
```

**Loop variables:**

```jinja
{% for item in items %}
    {{ loop.index }}        # 1-indexed current position
    {{ loop.index0 }}       # 0-indexed current position
    {{ loop.revindex }}     # Count from end (1-indexed)
    {{ loop.revindex0 }}    # Count from end (0-indexed)
    {{ loop.first }}        # True if first iteration
    {{ loop.last }}         # True if last iteration
    {{ loop.length }}       # Total number of items
    {{ loop.depth }}        # Nesting level (1-indexed)
    {{ loop.previtem }}     # Previous item (undefined on first)
    {{ loop.nextitem }}     # Next item (undefined on last)
{% endfor %}
```

**Filter in loop:**

```jinja
{% for user in users if not user.hidden %}
    <li>{{ user.name }}</li>
{% endfor %}
```

**Else clause (empty sequence):**

```jinja
{% for item in items %}
    <li>{{ item }}</li>
{% else %}
    <li>No items found</li>
{% endfor %}
```

**Recursive loops:**

```jinja
<ul>
{%- for item in items recursive %}
    <li>{{ item.name }}
    {%- if item.children %}
        <ul>{{ loop(item.children) }}</ul>
    {%- endif %}</li>
{%- endfor %}
</ul>
```

**Cycling values:**

```jinja
{% for row in rows %}
    <tr class="{{ loop.cycle('odd', 'even') }}">
        {{ row }}
    </tr>
{% endfor %}
```

### If Statements

```jinja
{% if user.is_admin %}
    <p>Welcome, Admin!</p>
{% elif user.is_moderator %}
    <p>Welcome, Moderator!</p>
{% else %}
    <p>Welcome, User!</p>
{% endif %}
```

**Inline if expression:**

```jinja
{{ 'logged in' if user.is_authenticated else 'logged out' }}
```

### Macros

Macros are reusable template functions:

```jinja
{% macro input(name, value='', type='text', size=20) -%}
    <input type="{{ type }}" name="{{ name }}" 
           value="{{ value|e }}" size="{{ size }}">
{%- endmacro %}

{{ input('username') }}
{{ input('password', type='password') }}
```

**Macro with varargs:**

```jinja
{% macro items(*args) %}
    {% for item in args %}{{ item }}{% endfor %}
{% endmacro %}

{{ items('a', 'b', 'c') }}
```

### Call Block

Pass a block as callable to a macro:

```jinja
{% macro dialog(title) -%}
    <div class="dialog">
        <h2>{{ title }}</h2>
        <div>{{ caller() }}</div>
    </div>
{%- endmacro %}

{% call dialog('Hello') %}
    This is the dialog content.
{% endcall %}
```

### Filter Block

Apply filter to entire block:

```jinja
{% filter upper %}
    This text becomes uppercase
{% endfilter %}

{% filter center(80) %}
    This text is centered in 80 chars
{% endfilter %}
```

### Assignments

```jinja
{% set myvar = 'hello' %}
{% set name, value = call_function() %}

{{ myvar }}
```

**Scope note:** Variables set inside blocks or loops don't persist outside. Use macros or pass variables explicitly.

## Template Inheritance

### Base Template

```jinja
{# base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    {% block head %}
    <link rel="stylesheet" href="style.css">
    <title>{% block title %}{% endblock %} - My Site</title>
    {% endblock %}
</head>
<body>
    <div id="content">{% block content %}{% endblock %}</div>
    <footer>{% block footer %}&copy; 2024{% endblock %}</footer>
</body>
</html>
```

### Child Template

```jinja
{# page.html #}
{% extends "base.html" %}

{% block title %}Home Page{% endblock %}

{% block head %}
    {{ super() }}  {# Include parent content #}
    <style>.special { color: red; }</style>
{% endblock %}

{% block content %}
    <h1>Welcome!</h1>
    <p>This is the home page.</p>
{% endblock %}
```

### Super() in Blocks

Call parent block content:

```jinja
{% block sidebar %}
    <h3>Custom Content</h3>
    {{ super() }}  {# Parent sidebar content #}
{% endblock %}
```

**Multi-level inheritance:** Use `super.super()` to skip levels.

### Named Block End Tags

```jinja
{% block sidebar %}
    {% block inner %}...{% endblock inner %}
{% endblock sidebar %}
```

### Scoped Blocks

Access outer scope variables in blocks:

```jinja
{% for item in items %}
    <li>{% block item scoped %}{{ item }}{% endblock %}</li>
{% endfor %}
```

### Required Blocks

Force child templates to override:

```jinja
{% block content required %}{% endblock %}
```

## Include and Import

### Include

```jinja
{% include 'header.html' %}
{% include 'sidebar.html' with context %}  {# Pass current context #}
{% include optional_template ignore missing %}  {# Ignore if not found #}
```

### Import

```jinja
{% import 'macros.html' as m %}
{{ m.input('username') }}
{{ m.button('Submit') }}
```

**Import specific macros:**

```jinja
{% from 'macros.html' import input, button %}
{{ input('email') }}
```

**Ignore context:**

```jinja
{% from 'macros.html' import input as input_field %}
```

## Raw Block

Output literal delimiters without interpretation:

```jinja
{% raw %}
    {{ This will be output literally, not interpreted }}
    {% for x in y %}...{% endfor %}
{% endraw %}
```

## Whitespace Control

### Environment Settings

```python
env = Environment(
    trim_blocks=True,   # Remove first newline after block
    lstrip_blocks=True  # Strip leading whitespace before blocks
)
```

### Manual Control

```jinja
{%- if condition -%}  {# Strip whitespace before and after #}
    Content
{% endif %}

{{- variable }}  {# Strip preceding whitespace #}
{{ variable -}}  {# Strip following whitespace #}
```

## Comments

```jinja
{# This is a single-line comment #}

{#
    This is a multi-line comment
    It can span multiple lines
    And is completely ignored
#}
```

## Global Functions

Available in all templates:

- `range(n)` - Generate number sequence: `{% for i in range(5) %}{{ i }}{% endfor %}`
- `cycler(*items)` - Cycle through values across loops
- `joiner(sep)` - Join multiple sections with separator
- `lipsum(n)` - Generate lorem ipsum text

## Expressions

Full Python expression support:

```jinja
{{ a + b }}              # Arithmetic
{{ a and b }}            # Logical AND
{{ a or b }}             # Logical OR
{{ not condition }}      # Logical NOT
{{ a == b }}             # Comparison
{{ item in list }}       # Membership
{{ 'hello' ~ ' ' ~ name }}  # String concatenation

# Dict literal
{{ {'key': 'value', 'num': 42} }}

# List comprehension-like with filters
{{ items|map('name')|list }}
```
