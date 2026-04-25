# Data Scrubbing

Logfire automatically redacts sensitive data matching these default patterns:
- `password`, `passwd`, `mysql_pwd`, `secret`, `auth` (not authours), `credential`
- `private_key`, `api_key`, `session`, `cookie`
- `social_security`, `credit_card`, `csrf`, `xrf`, `jwt`, `ssn`

### Custom Patterns

```python
import logfire

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(
        extra_patterns=['my_custom_pattern'],
    )
)
```

### Scrubbing Callback

```python
def scrubbing_callback(match: logfire.ScrubMatch):
    if match.path == ('attributes', 'my_safe_value'):
        return match.value  # Prevent redaction for this field

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
)
```

### LLM Message Content

Scrubbing is **disabled** for LLM message attributes (`gen_ai.input.messages`, `gen_ai.output.messages`) to avoid false positives. To exclude content entirely:

```python
logfire.instrument_pydantic_ai(include_content=False)
```

See [reference/04-scrubbing.md](reference/04-scrubbing.md) for complete scrubbing guide.
