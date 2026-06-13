# Python API Reference

## Environment

The `Environment` is the core object. Create one at application startup:

```python
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("yourapp"),
    autoescape=select_autoescape()
)
```

### Constructor Parameters

- **`block_start_string`** — Block delimiter start, default `'{%'`
- **`block_end_string`** — Block delimiter end, default `'%}'`
- **`variable_start_string`** — Variable delimiter start, default `'{{'`
- **`variable_end_string`** — Variable delimiter end, default `'}}'`
- **`comment_start_string`** — Comment delimiter start, default `'{#'`
- **`comment_end_string`** — Comment delimiter end, default `'#}'`
- **`line_statement_prefix`** — Prefix for line-based statements (e.g., `'#'`)
- **`line_comment_prefix`** — Prefix for line-based comments
- **`trim_blocks`** — Remove first newline after block tag, default `False`
- **`lstrip_blocks`** — Strip leading whitespace before block tags, default `False`
- **`newline_sequence`** — Newline sequence: `'\n'`, `'\r\n'`, or `'\r'`, default `'\n'`
- **`keep_trailing_newline`** — Preserve trailing newline, default `False`
- **`extensions`** — List of extension classes or import paths
- **`optimized`** — Enable optimizer, default `True`
- **`undefined`** — Undefined type class, default `Undefined`
- **`finalize`** — Callable to process variable output before rendering
- **`autoescape`** — Autoescaping setting (bool or callable), default `False`
- **`loader`** — Template loader instance
- **`cache_size`** — Template cache size, default `400`. Set `0` for no caching, `-1` for unlimited
- **`auto_reload`** — Reload templates on source change, default `True`
- **`bytecode_cache`** — Bytecode cache instance
- **`enable_async`** — Enable async template execution, default `False`

### Key Attributes

- **`filters`** — Dict of registered filters
- **`tests`** — Dict of registered tests
- **`globals`** — Dict of global variables available in all templates
- **`policies`** — Dict of runtime behavior policies
- **`shared`** — True if this is an auto-created shared environment
- **`sandboxed`** — True if this is a sandboxed environment

### Key Methods

```python
# Load template by name
template = env.get_template("name.html")

# Try multiple template names
template = env.select_template(["special.html", "default.html"])

# Load from string
template = env.from_string("Hello {{ name }}!")

# Compile a Jinja expression into a callable
expr = env.compile_expression("foo == 42")
result = expr(foo=23)  # False

# List all templates available through the loader
templates = env.list_templates(extensions=['.html'])

# Create an overlay (variant with different settings)
overlay_env = env.overlay(trim_blocks=True)

# Add extension after creation
env.add_extension('jinja2.ext.debug')

# Extend environment with custom attributes
env.extend(my_custom_attr="value")

# Compile all templates ahead-of-time to a zip file
env.compile_templates("compiled.zip", extensions=['.html'])
```

## Template

```python
template = env.get_template("hello.html")

# Render with keyword arguments
output = template.render(name="World", items=[1, 2, 3])

# Render with dict
output = template.render({"name": "World"})

# Stream large templates
for chunk in template.stream(name="World"):
    write(chunk)

# TemplateStream for buffered output
stream = template.stream(name="World")
stream.dump("output.html")

# Access exported macros/variables
t = env.from_string("{% macro foo() %}42{% endmacro %}23")
print(t.module.foo())  # '42'

# Async rendering (requires enable_async=True)
async def render():
    output = await template.render_async(name="World")
```

### Template Attributes

- **`name`** — Loading name of the template (None for from_string)
- **`filename`** — Filesystem path if loaded from file
- **`globals`** — Dict of global variables for this template

## Loaders

### BaseLoader

Abstract base class. Subclasses must implement `get_source(environment, name)` returning `(source, filename, uptodate)`.

### FileSystemLoader

Load from a filesystem directory:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("/path/to/templates"),
    autoescape=select_autoescape()
)
```

Accepts single path or list of paths. Searches in order.

### PackageLoader

Load from a Python package's `templates` folder:

```python
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader("mypackage"))
# Looks in mypackage/templates/
# Or mypackage.py/templates/ for single-file packages
```

### DictLoader

Load from an in-memory dict:

```python
from jinja2 import Environment, DictLoader

env = Environment(
    loader=DictLoader({
        "index.html": "<h1>{{ title }}</h1>",
        "layout.html": "<html>{% block body %}{% endblock %}</html>"
    })
)
```

### ChoiceLoader

Try multiple loaders in order:

```python
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, DictLoader

env = Environment(
    loader=ChoiceLoader([
        DictLoader({"override.html": "..."}),
        FileSystemLoader("/path/to/templates")
    ])
)
```

### FunctionLoader

Load using a custom function:

```python
from jinja2 import Environment, FunctionLoader

def load_template(name):
    return f"<h1>{name}</h1>"

env = Environment(loader=FunctionLoader(load_template))
```

### PrefixLoader

Prefix template names with a namespace:

```python
from jinja2 import Environment, PrefixLoader, FileSystemLoader

env = Environment(
    loader=PrefixLoader({
        "admin": FileSystemLoader("/path/to/admin/templates"),
        "app": FileSystemLoader("/path/to/app/templates")
    })
)

# Usage: env.get_template("admin/index.html")
```

### ModuleLoader

Load pre-compiled templates from a zip file or directory:

```python
from jinja2 import Environment, ModuleLoader

env = Environment(loader=ModuleLoader("/path/to/compiled.zip"))
```

Used with `env.compile_templates()` for ahead-of-time compilation.

## Autoescaping

Use `select_autoescape` for filename-based autoescaping:

```python
from jinja2 import Environment, select_autoescape

# Enable for .html, .htm, .xml; disable for others
env = Environment(
    autoescape=select_autoescape(
        enabled_extensions=('html', 'htm', 'xml'),
        default_for_string=True,
    )
)

# Enable everywhere except .txt
env = Environment(
    autoescape=select_autoescape(
        disabled_extensions=('txt',),
        default=True,
    )
)
```

Custom autoescape function:

```python
def autoescape(name):
    if name is None:
        return False
    return name.endswith('.html')

env = Environment(autoescape=autoescape)
```

## Undefined Types

Control behavior when accessing undefined variables:

### Undefined (default)

Prints as empty string, evaluates to False, iteration returns nothing. Other operations raise `UndefinedError`.

### ChainableUndefined

Attribute and item access on undefined returns itself (chainable), preventing errors on deep chains:

```python
from jinja2 import Environment, ChainableUndefined

env = Environment(undefined=ChainableUndefined)
# {{ user.address.city }} returns '' if user is undefined
```

### DebugUndefined

Returns the template expression when printed:

```python
from jinja2 import Environment, DebugUndefined

env = Environment(undefined=DebugUndefined)
# {{ missing_var }} renders as "{{ missing_var }}"
```

### StrictUndefined

Raises `UndefinedError` on any operation including printing and boolean tests:

```python
from jinja2 import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
# {{ missing_var }} raises UndefinedError
```

### Logging Undefined

Log when undefined values are accessed:

```python
import logging
from jinja2 import Environment, make_logging_undefined

logger = logging.getLogger(__name__)
LoggingUndefined = make_logging_undefined(logger=logger, base=Undefined)
env = Environment(undefined=LoggingUndefined)
```

## The Context

The `Context` object holds variables during template rendering. Access in custom filters/tests:

```python
from jinja2 import pass_context

@pass_context
def my_filter(context, value):
    # Access other variables
    other_var = context.parent['some_variable']
    return value
```

## Bytecode Cache

Cache compiled template bytecode to avoid re-parsing:

```python
from jinja2 import Environment, FileSystemLoader, BytecodeCache

class SimpleBytecodeCache(BytecodeCache):
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def load_bytecode(self, bucket):
        path = self._get_cache_bucket(bucket)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                bucket.loadpickle(f)

    def dump_bytecode(self, bucket):
        path = self._get_bucket_path(bucket)
        with open(path, 'wb') as f:
            bucket.dumpickle(f)

    def _get_bucket_path(self, bucket):
        return os.path.join(self.cache_dir, f"{bucket.key}.cache")

env = Environment(
    loader=FileSystemLoader("templates"),
    bytecode_cache=SimpleBytecodeCache("/tmp/jinja_cache")
)
```

## Async Support

Enable async mode on the Environment:

```python
from jinja2 import Environment

env = Environment(enable_async=True)

async def fetch_data():
    return {"items": [1, 2, 3]}

template = env.from_string("{% for item in items %}{{ item }}{% endfor %}")
result = await template.render_async(items=await fetch_data())

# Async generation
async for chunk in template.generate_async(items=[1, 2, 3]):
    process(chunk)
```

Async mode automatically handles both sync and async functions in templates without extra syntax.

## Policies

Configure runtime behavior:

```python
env.policies["urlize.rel"] = ["noopener", "nofollow"]
env.policies["truncate.leeway"] = 5
env.policies["json.dumps_function"] = lambda obj: import('orjson'). dumps(obj)
```

Available policies:
- **`urlize.rel`** — Default rel attributes for urlize filter
- **`truncate.leeway`** — Default leeway for truncate filter
- **`json.dumps_function`** — Custom JSON serialization function
- **`json.dumps_kwargs`** — Kwargs for JSON serialization
- **`ext.i18n.trimmed`** — Trim whitespace in trans blocks

## Custom Filters

Register functions as filters:

```python
from jinja2 import Environment

def reverse_word(s):
    return s[::-1]

env = Environment()
env.filters['reverse_word'] = reverse_word
```

In template: `{{ "hello"|reverse_word }}` → `olleh`

Access environment in filter:

```python
from jinja2 import pass_environment

@pass_environment
def my_filter(env, value):
    # env available for configuration access
    return value.upper()
```

Access context in filter:

```python
from jinja2 import pass_context

@pass_context
def my_filter(context, value):
    other = context.parent['other_var']
    return f"{value} {other}"
```

Access eval context (for evaluation-time info):

```python
from jinja2 import pass_eval_context

@pass_eval_context
def my_filter(eval_ctx, value):
    if eval_ctx.autoescape:
        # Handle escaping
        pass
    return value
```

## Custom Tests

Register test functions:

```python
def is_palindrome(s):
    return str(s) == str(s)[::-1]

env.tests['palindrome'] = is_palindrome
```

In template: `{% if "racecar" is palindrome %}`

Decorators work the same as filters: `@pass_environment`, `@pass_context`, `@pass_eval_context`.

## The Global Namespace

Globals are available in every render without passing them:

```python
env.globals['app_name'] = 'MyApp'
env.globals['current_year'] = 2024
```

Template globals (per-template, via get_template):

```python
template = env.get_template("page.html", globals={"page_title": "Home"})
```

## Meta API

Introspect templates programmatically:

```python
from jinja2 import meta

# Find all referenced templates
ast = env.parse("{% extends 'base.html' %}{% include 'header.html' %}")
referenced = meta.find_referenced_templates(ast)
# {'base.html', 'header.html'}

# Find all assigned variables
assignments = meta.find_undefined_references(ast)

# Find all extracted i18n strings
from jinja2.ext import Extension
extracted = env.extract_translations(ast)
```

## Exceptions

- **`TemplateSyntaxError`** — Syntax error in template
- **`TemplatesNotFound`** — Template(s) not found by loader
- **`UndefinedError`** — Operation on undefined value
- **`TemplateRuntimeError`** — Runtime error during rendering
- **`SecurityError`** — Sandboxed environment security violation
- **`TemplateAssertionError`** — Assertion failed in template

## Low-Level API

For advanced use (extensions, custom compilers):

```python
from jinja2 import Environment, nodes
from jinja2.compiler import CodeGenerator
from jinja2.parser import Parser
from jinja2.lexer import get_lexer, TokenStream
```

Key classes:
- **`Environment.compile()`** — Parse template source to AST
- **`Environment.parse()`** — Return parsed AST
- **`Environment.lex()`** — Return token stream
- **`nodes`** — AST node types for building custom extensions
