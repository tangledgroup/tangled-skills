# Scrubbing

## Overview

The Logfire SDK scans for and redacts potentially sensitive data from logs and spans before exporting them. Enabled by default.

## Disabling Scrubbing

```python
import logfire
logfire.configure(scrubbing=False)
```

## Custom Patterns

Add your own regex patterns with `extra_patterns`:

```python
import logfire

logfire.configure(scrubbing=logfire.ScrubbingOptions(extra_patterns=['my_pattern']))

logfire.info('Hello', data={
    'key_matching_my_pattern': 'Redacted (key matches)',
    'other_key': 'Also redacted if value matches MY_PATTERN case-insensitively',
    'password': 'Redacted (default pattern still applies)',
})
```

### Default Scrubbing Patterns

```python
[
    'password', 'passwd', 'mysql_pwd', 'secret',
    'auth(?!ors?\\b)', 'credential',
    'private[._ -]?key', 'api[._ -]?key',
    'session', 'cookie',
    'social[._ -]?security', 'credit[._ -]?card',
    '(?:\\b|_)csrf(?:\\b|_)', '(?:\\b|_)xsrf(?:\\b|_)',
    '(?:\\b|_)jwt(?:\\b|_)', '(?:\\b|_)ssn(?:\\b|_)',
]
```

## Scrubbing Callback

Prevent over-aggressive scrubbing with a callback function:

```python
import logfire

def scrubbing_callback(match: logfire.ScrubMatch):
    # my_safe_value often contains 'password' but isn't sensitive
    if match.path == ('attributes', 'my_safe_value') and match.pattern_match.group(0) == 'password':
        return match.value  # Return original value to prevent redaction
    # Return None (implicit) to redact

logfire.configure(scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback))
```

The callback receives `logfire.ScrubMatch` with `path`, `pattern_match`, and `value` attributes. Return `None` to redact, or return a value to replace the matched value.

## Security Tips

### Use message templates (not string concatenation)

The full span/log message is not scrubbed — only fields within it are:

```python
# Safe — uses template
logfire.info('User details: {user}', user=User(id=123, password='secret'))
# Output: "User details: [Scrubbed due to 'password']"

# UNSAFE — string concatenation bypasses scrubbing
user = User(id=123, password='secret')
logfire.info('User details: ' + str(user))
# Output: "User details: User(id=123, password='secret')" — PASSWORD LEAKED
```

F-strings are safe if `inspect_arguments` is enabled (default in Python 3.11+).

### Keep sensitive data out of URLs

The `http.url` attribute is considered safe so URLs like `http://example.com/users/123/authenticate` are not redacted. Put sensitive data in request body or headers, not query parameters.

### Use parameterized database queries

The `db.statement` attribute is considered safe. Use parameterized queries (prepared statements) so sensitive data is not interpolated into the query string.

### LLM messages

Scrubbing is **disabled** for LLM message attributes (`gen_ai.input.messages`, `gen_ai.output.messages`, `pydantic_ai.all_messages`). If LLM interactions might contain sensitive data, exclude message content entirely:

```python
logfire.instrument_pydantic_ai(include_content=False)
```
