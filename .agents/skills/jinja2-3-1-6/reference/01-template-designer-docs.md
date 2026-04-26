# Template Designer Documentation

## Variables

Access any variable passed to the template. Dotted notation accesses attributes, items in mappings, or both:

```jinja
{{ user.username }}
{{ config.database.host }}
{{ items.0 }}
```

Calling Python methods on variables works as expected:

```jinja
{{ page.title.capitalize() }}
{{ "Hello, %s!" % name }}
{{ "Hello, {}!".format(name) }}
```

## Filters

Filters transform variable values using the pipe (`|`) operator. Multiple filters can be chained:

```jinja
{{ name|capitalize }}
{{ mystring|replace("a", "b")|title }}
{{ list|sort|reverse|join(", ") }}
```

### Key Builtin Filters

- **`default(value, boolean=false)`** — Return default if undefined. Alias: `d`
- **`escape` / `e`** — HTML-escape the string
- **`safe`** — Mark string as safe (skip escaping)
- **`lower` / `upper`** — Case conversion
- **`trim`** — Strip whitespace
- **`striptags`** — Strip HTML/XML tags
- **`length` / `count`** — Number of items
- **`first` / `last`** — First/last item of sequence
- **`sort`** — Sort items (supports `case_sensitive`, `attribute`, `reverse`)
- **`unique`** — Remove duplicates
- **`join(separator, attribute)`** — Join sequence into string
- **`list`** — Convert to list
- **`dictsort(case_sensitive=false, by="key", reverse=false)`** — Sort dict items
- **`batch(size, fill_with)`** — Split sequence into batches
- **`slice(number, fill_with)`** — Split into number of slices
- **`reverse`** — Reverse sequence
- **`map(attribute, default)`** — Extract attribute from each item
- **`select(test, *args)`** / **`reject(test, *args)`** — Filter by test
- **`selectattr(attr, *args)`** / **`rejectattr(attr, *args)`** — Filter by attribute
- **`groupby(attribute, default, case_sensitive=false)`** — Group by attribute
- **`format(value, *args)`** — Printf-style formatting
- **`truncate(length, end, leeway, kill_words)`** — Truncate text
- **`wordwrap(width, wrap_whitespace, break_long)`** — Wrap at word boundaries
- **`wordcount`** — Count words
- **`int(default, base=10)`** / **`float(default)`** — Type conversion
- **`abs(x)`** — Absolute value
- **`round(value, precision, method)`** — Round number
- **`filesizeformat(binary=false)`** — Human-readable file size
- **`pprint`** — Pretty print (debugging)
- **`tojson(indent)`** — JSON-encode for safe embedding in `<script>`
- **`urlencode(query, *args)`** — URL-encode dict or pairs
- **`urlize(max_length, nofollow)`** — Convert URLs to clickable links
- **`xmlattr(dict, quote)`** — Render as XML attributes
- **`indent(width, first, blank)`** — Indent lines
- **`items`** — Iterate over mapping items (safe for undefined)
- **`forceescape`** — Force HTML escape even on already-marked-safe strings

## Tests

Tests check if a value matches a condition. Used with the `is` operator:

```jinja
{% if user.email is defined %}
  Email: {{ user.email }}
{% endif %}

{% if value is string %}
  It's a string!
{% endif %}
```

Tests can take arguments and be chained with filters:

```jinja
{{ name|lower is matching("[a-z]+") }}
```

### Key Builtin Tests

- **`defined`** — Variable is defined
- **`undefined`** — Variable is undefined
- **`true` / `false`** — Value is true/false
- **`none`** — Value is None
- **`even` / `odd`** — Number parity
- **`number` / `integer` / `float`** — Type checks
- **`string`** — Is a string
- **`sequence` / `mapping`** — Collection type
- **`iterable` / `callable`** — Has iteration/call behavior
- **`lower` / `upper`** — All lowercase/uppercase
- **`sameas(obj)`** — Object identity check
- **`in(haystack)`** — Membership test
- **`matching(regex)`** — Regex match
- **`noneof(chars)`** — No characters from set present
- **`any(bool)` / `all(bool)`** — Boolean aggregation on sequences

## Comments

```jinja
{# This comment won't appear in the output #}
```

## Whitespace Control

Use `-` or `~` inside delimiters to strip whitespace:

- `{%- ... %}` — Strip whitespace before the tag
- `{% ... -%}` — Strip whitespace after the tag
- `{{- ... }}` / `{{ ... -}}` — Same for variable output
- `~` variant also strips the following newline

Environment-level options (set on Environment):
- `trim_blocks=True` — Remove first newline after a block tag
- `lstrip_blocks=True` — Strip leading whitespace/tabs before block tags

## Escaping

When autoescaping is enabled, all variable output is HTML-escaped by default. Use the `safe` filter to mark trusted content:

```jinja
{{ user.bio|safe }}
```

Use `{% autoescape %}` block to temporarily change escaping behavior:

```jinja
{% autoescape false %}
  This will not be escaped: {{ data }}
{% endautoescape %}
```

## Line Statements

When configured with `line_statement_prefix`, entire lines can be Jinja statements:

```jinja
# with line_statement_prefix='#'
#set name = "World"
Hello, #name!
```

## Template Inheritance

### Extending Templates

```jinja
{% extends "base.html" %}
```

Must be the first tag in the template (whitespace and comments before it are allowed).

### Blocks

Define overridable sections:

```jinja
{% block header %}Default Header{% endblock %}
{% block content %}{% endblock %}
{% block footer %}&copy; 2024{% endblock %}
```

Access parent block content with `super()`:

```jinja
{% block content %}
  {{ super() }}
  <p>Additional content</p>
{% endblock %}
```

Block names can include dots for namespacing: `page.title`.

### Including Templates

```jinja
{% include "header.html" %}
{% include ["special_header.html", "header.html"] %}
```

The list form tries each template in order, using the first found. Use `ignore missing` to skip if none exist:

```jinja
{% include "sidebar.html" ignore missing %}
```

## Import Context Behavior

By default, imported templates share the current context. Use `with context` or `without context` to control this:

```jinja
{% from "forms.html" import input with context %}
{% from "forms.html" import input without context %}
```

`import` always imports without context. `from` imports with context by default (configurable via policy).

## Control Structures

### For Loop

```jinja
{% for user in users %}
  <li>{{ loop.index }}: {{ user.username }}</li>
{% endfor %}
```

Loop variable attributes:
- `loop.index` — Current iteration (1-indexed)
- `loop.index0` — Current iteration (0-indexed)
- `loop.revindex` — Reverse index (1-indexed)
- `loop.revindex0` — Reverse index (0-indexed)
- `loop.first` — True on first iteration
- `loop.last` — True on last iteration
- `loop.length` — Total number of items
- `loop.cycle(*seq)` — Cycle through a sequence
- `loop.parent` — Parent loop (for nested loops)

Else clause runs if sequence is empty:

```jinja
{% for user in users %}
  {{ user }}
{% else %}
  No users found
{% endfor %}
```

Filter items inline:

```jinja
{% for user in users if user.active %}
```

Sort during iteration:

```jinja
{% for user in users|sort(attribute="username") %}
```

Break and continue (requires `jinja2.ext.loopcontrols` extension):

```jinja
{% for item in items %}
  {% if item.skip %}{% continue %}{% endif %}
  {% if item.stop %}{% break %}{% endif %}
{% endfor %}
```

### If Statement

```jinja
{% if user.is_authenticated %}
  <p>Welcome {{ user.username }}!</p>
{% elif guest_mode %}
  <p>Welcome guest!</p>
{% else %}
  <p>Please log in.</p>
{% endif %}
```

Shorthand with `if` in output:

```jinja
{{ "[{}]".format(page.title) if page.title else "(no title)" }}
```

### Set Statement

```jinja
{% set name = "World" %}
{% set navigation = [("Home", "/"), ("About", "/about")] %}
{% set user, admin = fetch_user() %}
```

Block assignment (capture output):

```jinja
{% set html %}
  <strong>Bold text</strong>
{% endset %}
{{ html }}
```

### Macro Definition

```jinja
{% macro render_dialog(title, class='dialog') %}
  <div class="{{ class }}" title="{{ title }}">
    {% block content %}{% endblock %}
  </div>
{% endmacro %}

{{ render_dialog("Hello") }}
```

Macros have a `caller` special variable for calling blocks:

```jinja
{% macro render_content(content) %}
  <div>{{ caller(content) }}</div>
{% endmacro %}

{% call render_content("text") %}
  <p>Custom content</p>
{% endcall %}
```

### Do Statement

Requires `jinja2.ext.do` extension. Discards return value:

```jinja
{% do items.append(new_item) %}
{% do namespace.update(key="value") %}
```

### With Statement

Creates a local scope (built-in since 2.9):

```jinja
{% with user = fetch_user(), admin = is_admin(user) %}
  {{ user.username }} - {{ admin }}
{% endwith %}
```

## Expressions

Jinja supports Python-like expressions:

- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Boolean: `and`, `or`, `not`
- Membership: `in`
- Identity: `is`, `is not`
- Grouping: `(expr)`
- Subscript: `obj[key]`
- Attribute: `obj.attr`
- Function call: `func(arg1, arg2)`
- Tuples/lists: `(a, b)`, `[a, b]`
- Dicts: `{"key": value}`
- Booleans: `true`, `false`
- None: `none`
- Ternary: `a if condition else b`

## List of Global Functions

- **`range(start, stop, step)`** — Generate a sequence of numbers
- **`dict(**items)`** — Create a dict from keyword arguments
- **`lipsum(n=5, html=true, min=20, max=100)`** — Generate lorem ipsum text
- **`cycler(*items, reset=true)`** — Cycle through values
- **`joiner(sep=', ')**` — Join output with separator
