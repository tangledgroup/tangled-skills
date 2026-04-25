# Testing

Assert emitted spans and logs in unit tests:

```python
import pytest
import logfire
from logfire.testing import CaptureLogfire

def test_observability(capfire: CaptureLogfire):
    with pytest.raises(Exception):
        with logfire.span('a span!'):
            logfire.info('a log!')
            raise Exception('an exception!')

    spans = capfire.exporter.exported_spans_as_dict()
    assert len(spans) == 2
```

When running under pytest, `send_to_logfire=False` by default.

See [reference/11-testing.md](reference/11-testing.md).
