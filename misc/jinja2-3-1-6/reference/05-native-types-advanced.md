# Native Types and Advanced Topics

## NativeEnvironment

The default Environment renders templates to strings. `NativeEnvironment` renders to native Python types — useful when using Jinja outside text generation:

```python
from jinja2.nativetypes import NativeEnvironment

env = NativeEnvironment()

# Arithmetic returns an int, not a string
t = env.from_string('{{ x + y }}')
result = t.render(x=4, y=2)
print(result)      # 6
print(type(result))  # <class 'int'>

# List syntax produces a list
t = env.from_string('[{% for item in data %}{{ item + 1 }},{% endfor %}]')
result = t.render(data=range(5))
print(result)      # [1, 2, 3, 4, 5]
print(type(result))  # <class 'list'>

# Non-Python-literal output falls back to string
t = env.from_string('{{ x }} * {{ y }}')
result = t.render(x=4, y=2)
print(result)      # 4 * 2
print(type(result))  # <class 'str'>

# Single object passthrough
class Foo:
    def __init__(self, value):
        self.value = value

result = env.from_string('{{ x }}').render(x=Foo(15))
print(type(result).__name__)  # Foo
print(result.value)            # 15
```

### Sandboxed Native Environment

Combine sandbox and native types:

```python
from jinja2.sandbox import SandboxedEnvironment
from jinja2.nativetypes import NativeEnvironment

class SandboxedNativeEnvironment(SandboxedEnvironment, NativeEnvironment):
    pass
```

## Ahead-of-Time Compilation

Compile templates at build time for faster runtime performance:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
env.compile_templates(
    "compiled_templates.zip",
    extensions=['.html', '.jinja'],
    zip='deflated',       # 'deflated' or 'stored', None for directory
    ignore_errors=True,   # Set False to abort on syntax errors
    log_function=print    # Log compilation progress
)

# At runtime, use ModuleLoader
from jinja2 import Environment, ModuleLoader

runtime_env = Environment(loader=ModuleLoader("compiled_templates.zip"))
template = runtime_env.get_template("index.html")
```

## Environment Overlay

Create variant environments sharing data with the original:

```python
env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape()
)

# Strict mode overlay
strict_env = env.overlay(
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True
)

# Async overlay
async_env = env.overlay(enable_async=True)
```

Extensions cannot be removed in overlays but can be added. Creating overlays should happen after the initial environment is fully configured.

## finalize Callback

Process variable output before rendering:

```python
from jinja2 import Environment

def none_to_empty(value):
    if value is None:
        return ''
    return value

env = Environment(finalize=none_to_empty)
# {{ some_none_value }} renders as empty string instead of nothing
```

## compile_expression

Use Jinja expression syntax in Python code (e.g., for config files):

```python
from jinja2 import Environment

env = Environment()
expr = env.compile_expression('foo == 42 and bar > 0')

print(expr(foo=42, bar=5))    # True
print(expr(foo=23, bar=5))    # False
print(expr(foo=42))           # None (bar is undefined, converted to None)

# Keep undefined values
expr_strict = env.compile_expression('var', undefined_to_none=False)
result = expr_strict()
print(result)  # Undefined (jinja2.Undefined instance)
```

## Evaluation Context

The `EvalContext` tracks evaluation-time state:

```python
from jinja2 import pass_eval_context, Environment

@pass_eval_context
def my_filter(eval_ctx, value):
    if eval_ctx.autoescape:
        from markupsafe import Markup
        return Markup(value)
    return value
```

EvalContext attributes:
- **`autoescape`** — Current autoescaping state
- **`uuid`** — Unique identifier for this evaluation context

## Integration Patterns

### Flask

Flask uses Jinja2 by default. Access the environment via `app.jinja_env`:

```python
from flask import Flask

app = Flask(__name__)

# Add custom filter
@app.template_filter('reverse_word')
def reverse_word(s):
    return s[::-1]

# Add global variable
@app.context_processor
def inject_globals():
    return {'app_name': 'MyApp'}
```

### Django

Use `jinja2.ext.i18n` with Django's translation system:

```python
from django.utils.translation import gettext as _, ngettext
from jinja2 import Environment

env = Environment(extensions=['jinja2.ext.i18n'])
env.install_gettext_callables(_, ngettext, newstyle=True)
```

### Babel

Extract translatable strings from Jinja templates with Babel:

```bash
pybabel extract -F babel.cfg -o messages.pot .
```

`babel.cfg` configuration:

```ini
[jinja2: **.jinja]
encoding = utf-8
extensions = jinja2.ext.i18n
```

## Complete Example: Production Setup

```python
from jinja2 import (
    Environment, PackageLoader, select_autoescape,
    FileSystemLoader, BytecodeCache
)
import os

# Template environment with best practices
env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape(
        enabled_extensions=('html', 'htm', 'xml'),
        default_for_string=True,
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    cache_size=-1,  # Unlimited cache
    auto_reload=True,  # Disable in production
    enable_async=False,
)

# Add extensions
env.add_extension('jinja2.ext.i18n')
env.add_extension('jinja2.ext.loopcontrols')

# Configure i18n
import gettext
translations = gettext.translation('messages', localedir='locale', fallback=True)
env.install_gettext_translations(translations, newstyle=True)

# Add custom filters
def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

env.filters['slugify'] = slugify

# Add globals
env.globals['version'] = '1.0.0'
```

## Version 3.1.x Changes

Key changes in the 3.1 series:

- **3.1.6** — Bug fixes and stability improvements
- **3.1.5** — `enable_async` applied correctly in overlays
- **3.1.4** — Various security and compatibility fixes
- **3.1.3** — Bug fixes
- **3.1.2** — Added `newline_sequence`, `keep_trailing_newline`, and `enable_async` to overlay parameters
- **3.1.1** — Bug fixes
- **3.1.0** — Major release with Python 3.7+ support, new policies system, improved async support, `items` filter, various API improvements
