# Logfire Scrubbing Reference

## Default Patterns

Logfire automatically redacts values where the key matches:

```python
[
    'password', 'passwd', 'mysql_pwd', 'secret',
    'auth(?!ors?\\b)',  # auth but not authors/authors
    'credential',
    'private[._ -]?key',
    'api[._ -]?key',
    'session', 'cookie',
    'social[._ -]?security',
    'credit[._ -]?card',
    '(?:\\b|_)csrf(?:\\b|_)',
    '(?:\\b|_)xsrf(?:\\b|_)',
    '(?:\\b|_)jwt(?:\\b|_)',
    '(?:\\b|_)ssn(?:\\b|_)',
]
```

## Disabling Scrubbing

```python
import logfire

logfire.configure(scrubbing=False)
```

## Adding Custom Patterns

```python
import logfire

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(
        extra_patterns=['my_secret_pattern', 'internal_key'],
    )
)
```

Custom patterns are combined with default patterns.

## Scrubbing Callback

Use a callback to prevent redaction for specific fields:

```python
import logfire


def scrubbing_callback(match: logfire.ScrubMatch):
    # `my_safe_value` often contains 'password' but it's not sensitive
    if (match.path == ('attributes', 'my_safe_value') and
            match.pattern_match.group(0) == 'password'):
        return match.value  # Return original value to prevent redaction
    # Return None to apply default scrubbing behavior


logfire.configure(
    scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
)
```

The callback receives a `ScrubMatch` object with:
- `path`: Tuple showing where the match was found (e.g., `('attributes', 'field_name')`)
- `pattern_match`: The regex match object
- `value`: The original value that matched
- `key`: The key/attribute name that matched

## Security Best Practices

### Use Message Templates

```python
# ✅ Safe — arguments parsed separately, scrubbed if matching patterns
logfire.info('User details: {user}', user=User(id=123, password='secret'))
# Output: User details: [Scrubbed due to 'password']

# ❌ Unsafe — entire string logged as-is
user_str = str(User(id=123, password='secret'))
logfire.info(f'User details: {user_str}')
# Output: User details: User(id=123, password='secret')
```

### F-strings in Python 3.11+

F-strings are safe if `inspect_arguments` is enabled (default in Python 3.11+):
```python
logfire.info(f'User {user} logged in')  # Safe in Python 3.11+
```

### URLs and Database Queries

The following attributes are considered **safe** and not scrubbed:
- `http.url` — URLs may contain auth info but are standard OTel attributes
- `db.statement` — Use parameterized queries to keep sensitive data out of query strings

### LLM Messages

Scrubbing is **disabled** for LLM message attributes (`gen_ai.input.messages`, `gen_ai.output.messages`, `pydantic_ai.all_messages`) because:
1. LLMs frequently produce content with words like "password" or "secret" that aren't actually sensitive
2. Regex-based scrubbing can't detect all sensitive data in LLM output

To exclude LLM content entirely:
```python
logfire.instrument_pydantic_ai(include_content=False)
```
