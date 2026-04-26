# Extensions

## Overview

Extensions add extra filters, tests, globals, or even extend the parser. They are added to the Environment at creation time:

```python
from jinja2 import Environment

env = Environment(extensions=['jinja2.ext.i18n'])
```

Or after creation:

```python
env.add_extension('jinja2.ext.debug')
```

## Built-in Extensions

### i18n Extension (`jinja2.ext.i18n`)

Provides the `trans` statement for marking text as translatable. Works with Python's `gettext` or Babel.

After enabling, provide `gettext`, `ngettext`, and optionally `pgettext`/`npgettext`:

```python
import gettext
from jinja2 import Environment

env = Environment(extensions=['jinja2.ext.i18n'])
translations = gettext.translation('messages', localedir='locale')
env.install_gettext_translations(translations)
```

Or install no-op functions for development:

```python
env.install_null_translations()
```

In templates:

```jinja
{# Standard gettext #}
{{ gettext("Hello, World!") }}
{{ gettext("Hello, %(name)s!")|format(name=name) }}

{# Plural forms #}
{{ ngettext("%(num)d apple", "%(num)d apples", count)|format(num=count) }}

{# With context (disambiguation) #}
{{ pgettext("greeting", "Hello") }}

{# New style (less error-prone, better autoescaping) #}
{{ gettext("Hello, %(name)s!", name=name) }}
{{ ngettext("%(num)d apple", "%(num)d apples", count) }}
```

Enable new-style gettext:

```python
env.install_gettext_translations(translations, newstyle=True)
# or
env.newstyle_gettext = True
```

Whitespace trimming in trans blocks (via policy):

```python
env.policies["ext.i18n.trimmed"] = True
```

### Loop Controls (`jinja2.ext.loopcontrols`)

Adds `break` and `continue` to for loops:

```python
env = Environment(extensions=['jinja2.ext.loopcontrols'])
```

```jinja
{% for item in items %}
  {% if item.skip %}{% continue %}{% endif %}
  {% if item.stop %}{% break %}{% endif %}
  {{ item }}
{% endfor %}
```

### Do Statement (`jinja2.ext.do`)

Adds the `do` tag for expressions that discard their return value:

```python
env = Environment(extensions=['jinja2.ext.do'])
```

```jinja
{% do items.append(new_item) %}
{% do namespace.update(key="value") %}
```

### Debug Extension (`jinja2.ext.debug`)

Adds `{% debug %}` tag to dump current context, filters, and tests:

```python
env = Environment(extensions=['jinja2.ext.debug'])
```

```jinja
{% debug %}
{# Outputs: vars, loader, filters, tests available in current context #}
```

### Deprecated Extensions (built-in since 2.9)

- **`jinja2.ext.autoescape`** — Now built-in, enabling does nothing
- **`jinja2.ext.with_`** — Now built-in, enabling does nothing

## Writing Custom Extensions

Extensions extend `jinja2.ext.Extension`. They can add custom tags by defining a `tags` set and implementing `parse()`:

```python
from jinja2 import Environment, nodes
from jinja2.ext import Extension


class FragmentCacheExtension(Extension):
    """Caches template fragments using an external cache."""
    tags = {"cache"}

    def __init__(self, environment):
        super().__init__(environment)
        # Store configuration on the environment
        environment.extend(fragment_cache_prefix="", fragment_cache=None)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # Parse cache key expression
        args = [parser.parse_expression()]

        # Optional timeout
        if parser.stream.skip_if("comma"):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        # Parse body until endcache
        body = parser.parse_statements(["name:endcache"], drop_needle=True)

        return nodes.CallBlock(
            self.call_method("_cache_support", args), [], [], body
        ).set_lineno(lineno)

    def _cache_support(self, name, timeout, caller):
        key = self.environment.fragment_cache_prefix + name
        rv = self.environment.fragment_cache.get(key)
        if rv is not None:
            return rv
        rv = caller()
        self.environment.fragment_cache.add(key, rv, timeout)
        return rv
```

Usage:

```python
from cachelib import SimpleCache

env = Environment(extensions=[FragmentCacheExtension])
env.fragment_cache = SimpleCache()
```

```jinja
{% cache 'sidebar', 300 %}
  <div class="sidebar">...</div>
{% endcache %}
```

## Extension API

### Extension Base Class

```python
from jinja2.ext import Extension

class MyExtension(Extension):
    identifier = "myapp.myextension.MyExtension"  # Auto-set, don't change
    tags = {"mytag"}  # Set of tag names this extension handles
```

### Key Methods

**`preprocess(source, name, filename)`** — Called before lexing to preprocess source:

```python
def preprocess(self, source, name, filename=None):
    return source.replace("{{{{", "{{")
```

**`filter_stream(stream)`** — Filter tokens during lexing. Must return iterable of Tokens:

```python
def filter_stream(self, stream):
    for token in stream:
        if token.type == "data":
            yield token._replace(value=token.value.upper())
        else:
            yield token
```

**`parse(parser)`** — Called when a tag in `self.tags` is encountered. Returns one or more AST nodes:

```python
def parse(self, parser):
    lineno = next(parser.stream).lineno
    # Parse arguments...
    body = parser.parse_statements(["name:endmytag"], drop_needle=True)
    return nodes.Output([nodes.Const("hello")]).set_lineno(lineno)
```

**`attr(name, lineno=None)`** — Return an AST node referencing an attribute on this extension:

```python
self.attr('_my_config', lineno=lineno)
```

**`call_method(name, args, kwargs, dyn_args, dyn_kwargs, lineno)`** — Shortcut for calling a method on the extension:

```python
self.call_method('_render_widget', [arg1, arg2], lineno=lineno)
```

### Parser Methods

The parser provides methods for building extensions:

- **`parser.parse_expression()`** — Parse a Jinja expression
- **`parser.parse_statements(ends, drop_needle=False)`** — Parse statements until one of the end tokens
- **`parser.stream`** — Current TokenStream
- **`parser.stream.skip_if(name)`** — Skip token if it matches name
- **`parser.stream.expect(name)`** — Expect and consume a token of given name

### Common AST Nodes

- `nodes.Const(value)` — Constant value
- `nodes.Name(name, ctx='load')` — Variable reference
- `nodes.Output(nodes)` — Output nodes
- `nodes.Call(func, args, keywords, dyn_args, dyn_kwargs)` — Function call
- `nodes.CallBlock(call, args, kwargs, body)` — Call with block body
- `nodes.Block(name, body)` — Named block
- `nodes.If(test, body, else_=`) — If statement
- `nodes.For(target, iter, body, else_, test)` — For loop
- `nodes.Macro(name, arguments, body)` — Macro definition
- `nodes.Import(name, target, context)` — Import statement
- `nodes.Include(name, skip_if_unfound)` — Include statement
