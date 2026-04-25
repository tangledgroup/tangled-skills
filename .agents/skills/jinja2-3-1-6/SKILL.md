---
name: jinja2-3-1-6
description: Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom filters/tests, sandboxed environments, and async support. Use when building Python applications requiring dynamic HTML generation, email templates, configuration files, or any text-based output with logic separation from presentation.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - templating
  - python
  - html
  - web-development
  - template-engine
  - jinja
category: development
required_environment_variables: []

external_references:
  - https://jinja.palletsprojects.com/
  - https://github.com/pallets/jinja
---
## Overview
Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom filters/tests, sandboxed environments, and async support. Use when building Python applications requiring dynamic HTML generation, email templates, configuration files, or any text-based output with logic separation from presentation.

Jinja2 is a fast, expressive, and extensible templating engine for Python. It uses a Python-like syntax that allows embedding logic in templates while maintaining separation of concerns between application code and presentation layer. Templates are compiled to optimized Python code for high performance.

## When to Use
- Generating HTML pages from dynamic data
- Creating email templates with personalized content
- Producing configuration files from templates
- Building documentation from template sources
- Separating business logic from presentation in web applications
- Processing any text-based format requiring conditional logic and iteration

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
Install Jinja2 via pip:

```bash
pip install jinja2
```

Jinja2 requires Python 3.8+ and depends on MarkupSafe for HTML escaping.

## Usage Examples
### Basic Usage

Create a simple template and render it with variables:

```python
from jinja2 import Environment, FileSystemLoader

# Create environment with loader
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True  # Enable autoescaping for HTML safety
)

# Load and render template
template = env.get_template('hello.html')
output = template.render(name='World', items=['a', 'b', 'c'])
print(output)
```

See [Template Syntax](reference/01-template-syntax.md) for complete syntax reference.

### Common Operations

**Render from string:**

```python
from jinja2 import Template

template = Template('Hello {{ name }}!')
print(template.render(name='User'))  # Hello User!
```

**Package-based loading (recommended for applications):**

```python
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('your_package'),
    autoescape=select_autoescape()  # Auto-enable for .html, .xml files
)
```

**Template inheritance:**

```jinja
{# base.html #}
<!DOCTYPE html>
<html>
<head><title>{% block title %}Default{% endblock %}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>
```

```jinja
{# page.html #}
{% extends "base.html" %}
{% block title %}My Page{% endblock %}
{% block content %}<h1>Hello!</h1>{% endblock %}
```

Refer to [Template Inheritance](reference/01-template-syntax.md#template-inheritance) for details.

## Advanced Topics
## Advanced Topics

- [Template Syntax](reference/01-template-syntax.md)
- [Python Api](reference/02-python-api.md)
- [Advanced Patterns](reference/03-advanced-patterns.md)

## Troubleshooting
**Undefined variable errors:** Use the `default` filter or check with `is defined` test:

```jinja
{{ undefined_var|default('fallback value') }}
{% if variable is defined %}...{% endif %}
```

**Whitespace issues:** Configure `trim_blocks` and `lstrip_blocks` in Environment, or use `{%-` and `-%}` to manually strip whitespace.

**Autoescaping problems:** Mark trusted HTML as safe with `|safe` filter, or escape untrusted content with `|e` filter.

See reference files for detailed solutions to common issues.

