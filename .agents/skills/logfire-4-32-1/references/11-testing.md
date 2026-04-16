# Logfire Testing Reference

## Overview

Use `logfire.testing` to assert that your code emits the correct spans and logs. This is different from observing test runs — it tests your instrumentation.

## pytest Integration

```bash
pytest --logfire
```

When running under pytest, `send_to_logfire=False` by default to prevent accidental data sending.

## capfire Fixture

The `capfire` fixture provides access to exported spans and metrics:

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

## CaptureLogfire Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `exporter` | `TestExporter` | OTel-compatible span exporter keeping spans in memory |
| `log_exporter` | — | Separate log exporter |
| `metrics_reader` | — | Read recorded metrics |

## TestExporter Methods

### `exported_spans_as_dict()`

Returns a plain dict representation of exported spans. Performs data massaging for readability:
- Replaces line numbers with `123`
- Replaces file paths with just the filename
- Makes output deterministic

```python
def test_span_attributes(capfire: CaptureLogfire):
    with logfire.span('processing', item_id=42, count=3):
        logfire.info('done')

    spans = capfire.exporter.exported_spans_as_dict()
    assert len(spans) == 1
    span = spans[0]
    assert span['name'] == 'processing'
    assert span['attributes']['item_id'] == 42
```

## Testing with Inline Snapshots

```python
import pytest
from inline_snapshot import snapshot
import logfire
from logfire.testing import CaptureLogfire


def test_observability(capfire: CaptureLogfire) -> None:
    with pytest.raises(Exception):
        with logfire.span('a span!'):
            logfire.info('a log!')
            raise Exception('an exception!')

    assert capfire.exporter.exported_spans_as_dict() == snapshot([
        {
            'name': 'a span!',
            'context': {'trace_id': ..., 'span_id': ...},
            'attributes': {},
            'events': [
                {'name': 'a log!', 'timestamp': ..., 'attributes': {}},
                {
                    'name': 'exception',
                    'timestamp': ...,
                    'attributes': {
                        'exception.type': 'Exception',
                        'exception.message': 'an exception!',
                    },
                },
            ],
        }
    ])
```

## Testing Metrics

```python
def test_metrics(capfire: CaptureLogfire):
    request_duration = logfire.metric_histogram(
        'request_duration', unit='ms', description='Request latency'
    )
    request_duration.record(150.5)
    request_duration.record(200.3)

    # Access metrics through the metrics_reader
    metrics = capfire.metrics_reader.get_metrics()
    assert len(metrics) == 1
```
