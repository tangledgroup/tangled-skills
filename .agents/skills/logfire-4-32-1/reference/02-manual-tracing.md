# Manual Tracing

## Spans and Logs

```python
import time
import logfire

logfire.configure()

with logfire.span('This is a span'):
    time.sleep(1)
    logfire.info('This is an info log')
    time.sleep(2)
```

Key behaviors:
- Any spans or logs created inside `with logfire.span(...):` become children of that span
- Spans have start/end times and thus a duration
- Logs have no duration (start and end time are the same)
- New traces are created when a span/log is created with no active parent span

## Attributes

Spans and logs can carry structured data:

```python
logfire.info('Hello', name='world')
```

Attributes are stored as JSON in the `attributes` column. Query with `attributes->>'name' = 'world'`.

Set attributes after span creation:

```python
with logfire.span('Calculating...') as span:
    result = 1 + 2
    span.set_attribute('result', result)
```

Keyword arguments become attributes as long as they don't start with underscore (`_`). The `_` namespace is reserved for logfire-specific arguments.

## Messages and Span Names

The first argument becomes the `span_name` (low cardinality, indexed). It's also used as a `str.format`-style template to produce the `message`:

```python
for name in ['Alice', 'Bob', 'Carol']:
    logfire.info('Hello {name}', name=name)
```

This creates three records with `span_name = 'Hello {name}'` and messages `'Hello Alice'`, `'Hello Bob'`, `'Hello Carol'`.

Set message after span start:

```python
with logfire.span('Calculating...') as span:
    result = 1 + 2
    span.message = f'Calculated: {result}'
```

Use `_span_name` to decouple span name from message template:

```python
logfire.info('Hello {name}', name='world', _span_name='Hello')
```

**Keep span names low cardinality.** Don't concatenate variable data into span names:

```python
# Bad — high cardinality span_name
name = get_username()
logfire.info('Hello ' + name, name=name)

# Good — low cardinality
word = 'Goodbye' if leaving else 'Hello'
logfire.info(word + ' {name}', name=name)
```

## F-strings

In Python 3.11+, Logfire uses source inspection to automatically extract f-string variables:

```python
# Equivalent to: logfire.info('Hello {name}', name=name)
logfire.info(f'Hello {name}')
```

Logfire sets `span_name` to `'Hello {name}'` and `name` attribute to the variable value. This is enabled by default in Python 3.11+. Disable with `logfire.configure(inspect_arguments=False)`.

Caveats:
- Source code must be available (deploying only `.pyc` files will cause failure)
- Values inside f-strings are evaluated a second time — avoid expensive functions
- First argument must be an actual f-string literal, not a variable

## Exceptions

`logfire.span` automatically records unhandled exceptions:

```python
with logfire.span('This is a span'):
    raise ValueError('This is an error')
```

For caught exceptions, use `span.record_exception()`:

```python
with logfire.span('This is a span') as span:
    try:
        raise ValueError('Catch this error, but record it')
    except ValueError as e:
        span.record_exception(e)
```

Or use `logfire.exception()` for logging exceptions without creating a span:

```python
try:
    raise ValueError('This is an error')
except ValueError:
    logfire.exception('Something went wrong')
```

## Tags

Tags are optional string arrays for grouping records:

```python
logfire.warn('beware: {thing}', thing='bad', _tags=['a tag'])
```

Query tags with `array_has(tags, 'a tag')`. Alternatively, use `logfire.with_tags('a tag')` to get a new Logfire instance that auto-includes the tag.
