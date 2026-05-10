---
name: jinja2-3-1-6
description: Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom filters/tests, sandboxed environments, and async support. Use when building Python applications requiring dynamic HTML generation, email templates, configuration files, or any text-based output with logic separation from presentation.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - templating
  - html
  - python
  - jinja
  - web
category: library
external_references:
  - https://jinja.palletsprojects.com/
  - https://github.com/pallets/jinja
---

# Jinja2 3.1.6

## Overview

Jinja is a fast, expressive, extensible templating engine for Python. Special placeholders in the template allow writing code similar to Python syntax. Then the template is passed data to render the final document. It is part of the Pallets project and depends on MarkupSafe for HTML escaping.

Key features:

- Template inheritance and inclusion
- Define and import macros within templates
- HTML autoescaping to prevent XSS from untrusted input
- Sandboxed environment for safely rendering untrusted templates
- Async support for generating templates with async functions without extra syntax
- I18N support with Babel
- Templates compiled to optimized Python code just-in-time and cached, or compiled ahead-of-time
- Exceptions point to the correct line in templates for easier debugging
- Extensible filters, tests, functions, and even syntax

Jinja's philosophy: application logic belongs in Python if possible, but it shouldn't make the template designer's job difficult by restricting functionality too much.

## When to Use

- Generating dynamic HTML pages from templates
- Creating email templates with variable content
- Producing configuration files, source code, or any text-based output
- Separating presentation logic from application logic in Python web applications
- Rendering untrusted templates safely with the sandboxed environment
- Building internationalized applications with gettext/Babel integration
- Generating output as native Python types (lists, dicts, ints) instead of strings

## Core Concepts

### Environment

The central object is `Environment`. It stores configuration, global objects, filters, tests, and is used to load templates. Most applications create one `Environment` at startup and use it throughout.

```python
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("yourapp"),
    autoescape=select_autoescape()
)
```

### Template Loading and Rendering

Load a template by name, then render it with context variables:

```python
template = env.get_template("mytemplate.html")
output = template.render(name="World", items=[1, 2, 3])
```

For templates from strings (no loader needed):

```python
template = env.from_string("Hello {{ name }}!")
output = template.render(name="World")
```

### Delimiters

- `{{ ... }}` — Variable expressions (output values)
- `{% ... %}` — Statements (control flow: for, if, macros, blocks)
- `{# ... #}` — Comments (not in output)

### Template Inheritance

Child templates extend a base template using `{% extends %}` and override named blocks:

```jinja
{# base.html #}
<html>
<head><title>{% block title %}Default{% endblock %}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>

{# child.html #}
{% extends "base.html" %}
{% block title %}My Page{% endblock %}
{% block content %}<p>Hello!</p>{% endblock %}
```

### Macros

Define reusable template fragments:

```jinja
{% macro input(name, value, type="text") %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{{ input("username", user.name) }}
```

## Advanced Topics

**Template Designer Documentation**: Variables, filters, tests, control structures, template inheritance, and the complete template language reference → [Template Designer Documentation](reference/01-template-designer-docs.md)

**Python API Reference**: Environment, Template, loaders, autoescaping, undefined types, context, bytecode cache, async support, custom filters/tests, and low-level API → [Python API Reference](reference/02-python-api.md)

**Sandboxed Environments**: Rendering untrusted templates safely with attribute/method interception, operator intercepting, and immutable sandboxed environments → [Sandboxed Environments](reference/03-sandbox.md)

**Extensions**: Built-in extensions (i18n, loop controls, do statement, debug), writing custom extensions, and the extension API → [Extensions](reference/04-extensions.md)

**Native Types and Advanced Topics**: NativeEnvironment for rendering to Python types instead of strings, ahead-of-time compilation, policies, meta API, and integration patterns → [Native Types and Advanced Topics](reference/05-native-types-advanced.md)
