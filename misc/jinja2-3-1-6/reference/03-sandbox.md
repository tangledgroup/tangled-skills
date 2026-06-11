# Sandboxed Environments

## Overview

The sandboxed environment renders untrusted templates safely. It intercepts attribute access, method calls, operators, and data structure mutations. Use it when users or external sources provide template content.

```python
from jinja2.sandbox import SandboxedEnvironment

env = SandboxedEnvironment()
template = env.from_string("{{ func() }}")
result = template.render(func=lambda: "Hello!")
# 'Hello!'

# Accessing private attributes is blocked
template = env.from_string("{{ func.__code__.co_code }}")
result = template.render(func=lambda: "test")
# Raises SecurityError
```

## Security Considerations

The sandbox alone does not provide perfect security. Keep these in mind:

- Templates can still raise errors during compilation or rendering — catch all exceptions
- A small template can produce very large output (DoS risk) — set CPU/memory limits
- Jinja only renders text and doesn't understand the output format — post-process if needed
- Pass only relevant data — avoid global objects or objects with side-effect methods
- Use `ImmutableSandboxedEnvironment` to prevent modifying lists and dicts
- Decorate dangerous methods with `@unsafe` to prevent template access
- Override `is_safe_attribute()` for additional attribute restrictions

## SandboxedEnvironment

```python
from jinja2.sandbox import SandboxedEnvironment

env = SandboxedEnvironment()
```

Works like regular `Environment` but generates sandboxed code. Raises `SecurityError` on insecure operations.

### Key Methods

**`is_safe_attribute(obj, attr, value)`** — Called to check if an attribute is safe to access. By default blocks attributes starting with `_` and internal Python attributes (as determined by `is_internal_attribute()`).

Override for custom rules:

```python
class MySandbox(SandboxedEnvironment):
    def is_safe_attribute(self, obj, attr, value):
        if attr.startswith('_'):
            return False
        if isinstance(obj, dict) and attr == 'pop':
            return False
        return super().is_safe_attribute(obj, attr, value)
```

**`is_safe_callable(obj)`** — Check if a callable is safe. By default all callables are safe unless decorated with `@unsafe`. Also recognizes Django's `func.alters_data = True` convention.

## ImmutableSandboxedEnvironment

Prevents modifications to builtin mutable objects (list, set, dict):

```python
from jinja2.sandbox import ImmutableSandboxedEnvironment

env = ImmutableSandboxedEnvironment()
# {{ items.append(5) }} raises SecurityError
# {{ items }} works fine (read-only access)
```

## unsafe Decorator

Mark methods as unsafe for template access:

```python
from jinja2.sandbox import SandboxedEnvironment, unsafe

class MyData:
    def safe_method(self):
        return "safe"

    @unsafe
    def dangerous_method(self):
        import os
        os.system("rm -rf /")

env = SandboxedEnvironment()
data = MyData()
# {{ data.safe_method() }} works
# {{ data.dangerous_method() }} raises SecurityError
```

## Helper Functions

**`is_internal_attribute(obj, attr)`** — Test if an attribute is an internal Python attribute:

```python
from jinja2.sandbox import is_internal_attribute

is_internal_attribute(str, "mro")    # True
is_internal_attribute(str, "upper")  # False
```

**`modifies_known_mutable(obj, attr)`** — Check if calling an attribute on a mutable object would modify it:

```python
from jinja2.sandbox import modifies_known_mutable

modifies_known_mutable({}, "clear")   # True
modifies_known_mutable({}, "keys")    # False
modifies_known_mutable([], "append")  # True
modifies_known_mutable([], "index")   # False
```

## Operator Intercepting

By default, operators are compiled directly for performance. To intercept them, override `intercepted_binops` and `intercepted_unops`:

```python
from jinja2.sandbox import SandboxedEnvironment

class RestrictedEnv(SandboxedEnvironment):
    # Intercept the power operator
    intercepted_binops = frozenset(["**"])

    def call_binop(self, context, operator, left, right):
        if operator == "**":
            raise SecurityError("Power operator is not allowed")
        return super().call_binop(context, operator, left, right)
```

Interceptable binary operators: `//`, `%`, `+`, `*`, `-`, `/`, `**`
Interceptable unary operators: `+`, `-`

The `binop_table` and `unop_table` attributes provide default callback mappings from operator symbols to Python `operator` module functions. Intercepted calls are slower than native operators, so only intercept what you need.

## Practical Example

User-defined email template system:

```python
from jinja2.sandbox import SandboxedEnvironment

env = SandboxedEnvironment()

# Document available data for users
# Available variables: user_name, order_total, order_items, shipping_address

def render_user_template(template_source, context):
    try:
        template = env.from_string(template_source)
        return template.render(**context)
    except SecurityError:
        return "Template contains unsafe operations"
    except Exception as e:
        return f"Template error: {e}"

# User's template
user_template = """
Dear {{ user_name }},

Your order total is ${{ "%.2f"|format(order_total) }}.

{% for item in order_items %}
  - {{ item.name }}: ${{ "%.2f"|format(item.price) }}
{% endfor %}
"""

context = {
    "user_name": "Alice",
    "order_total": 99.99,
    "order_items": [
        {"name": "Widget", "price": 49.99},
        {"name": "Gadget", "price": 50.00}
    ]
}

output = render_user_template(user_template, context)
```
