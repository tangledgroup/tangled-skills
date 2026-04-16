# Logs API & SDK

**Status**: Stable (except where noted)

## Overview

The Logs API provides for logging library authors to build log appenders that bridge between existing logging libraries and the OpenTelemetry log data model. It can also be called directly by instrumentation libraries or applications.

```
graph TD
    A[LoggerProvider] -->|Get| B(Logger)
    B -->|Emit| C(LogRecord)
```

## LoggerProvider

### Get a Logger

```python
logger = logger_provider.get_logger(
    name: str,           # REQUIRED — instrumentation scope name
    version: str = "",   # OPTIONAL
    schema_url: str = "",# OPTIONAL
    attributes: dict = {}# OPTIONAL
) -> Logger
```

Same parameter semantics as TracerProvider and MeterProvider.

## Logger Operations

### Emit a LogRecord

```python
logger.emit(
    timestamp=None,              # Optional: event timestamp
    observed_timestamp=None,     # Optional: when observed by OTel
    context=current_context,     # Optional: associated context
    severity_number=None,        # Optional: structured severity level
    severity_text=None,          # Optional: human-readable severity
    body="User logged in",       # Optional: main log message
    attributes={"user.id": "abc"},# Optional: key-value attributes
    event_name=None              # Optional: event name for event semantics
)
```

### Enabled Check (Development)

```python
if logger.is_enabled(
    context=current_context,
    severity_number=SeverityNumber.INFO,
    event_name=None
):
    # Only compute expensive log message if enabled
    logger.emit(body=f"Expensive: {compute_log_message()}")
```

- Returns boolean indicating if a LogRecord would be emitted
- Can change over time — call each time before emitting
- Helps avoid expensive log message generation

## LogRecord Data Model

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | Timestamp | Optional | Time of the event |
| `observed_timestamp` | Timestamp | Optional | When observed by OTel SDK (for bridged logs) |
| `context` | Context | Optional | Associated trace context |
| `severity_number` | SeverityNumber enum | Optional | Structured severity level |
| `severity_text` | String | Optional | Original severity text from source |
| `body` | AnyValue | Optional | Main log message content |
| `attributes` | AttributeCollection | Optional | Key-value pairs |
| `event_name` | String | Optional | Event name for event semantics |

### Severity Levels

```python
from opentelemetry.logs import SeverityNumber, SeverityText

# Structured severity numbers (1-24)
SeverityNumber.DEBUG = 1
SeverityNumber.DEBUG2 = 2
SeverityNumber.DEBUG4 = 4
SeverityNumber.TRACE = 5
SeverityNumber.TRACE2 = 6
SeverityNumber.TRACE4 = 8
SeverityNumber.INFO = 9
SeverityNumber.INFO2 = 10
SeverityNumber.INFO4 = 12
SeverityNumber.WARN = 13
SeverityNumber.WARN2 = 14
SeverityNumber.WARN4 = 16
SeverityNumber.ERROR = 17
SeverityNumber.ERROR2 = 18
SeverityNumber.ERROR4 = 20
SeverityNumber.FATAL = 21
SeverityNumber.FATAL2 = 22
SeverityNumber.FATAL4 = 24

# Standard severity text labels
SeverityText.DEBUG = "DEBUG"
SeverityText.TRACE = "TRACE"
SeverityText.INFO = "INFO"
SeverityText.WARN = "WARN"
SeverityText.ERROR = "ERROR"
SeverityText.FATAL = "FATAL"
```

### Event Semantics

For event-based logging (following event semantics conventions):

```python
logger.emit(
    body="User authentication successful",
    severity_number=SeverityNumber.INFO,
    event_name="user.auth.success",
    attributes={
        "user.id": "abc123",
        "auth.method": "oauth2",
        "ip.address": "10.0.0.1"
    }
)
```

Event name follows pattern: `<domain>.<event-type>.<action>`

## SDK Components

### LoggerProvider (SDK)

```python
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "my-service"})
logger_provider = LoggerProvider(resource=resource)

# Bridge to Python standard logging
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
```

### LogRecordProcessor

Similar to SpanProcessor, processes log records:

| Method | Description |
|--------|-------------|
| `on_emit(log_record)` | Called when a LogRecord is emitted |
| `force_flush()` | Flush pending log records |
| `shutdown()` | Flush then release resources |

### LogRecordExporter

Exports finished log records to destinations:

| Method | Description |
|--------|-------------|
| export(batch) | Export a batch of log records |
| shutdown() | Release resources |
| force_flush() | Force flush pending exports |

## Log Record Limits

| Limit | Default Env Var | Default Value |
|-------|-----------------|---------------|
| Attribute count per log record | `OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT` | 128 |
| Attribute value length | `OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT` | no limit |

## Log Exporters

### Console/Stdout Exporter

```python
from opentelemetry.sdk.logs.export import ConsoleLogExporter
from opentelemetry.sdk.logs import LoggerProvider

exporter = ConsoleLogExporter()
logger_provider = LoggerProvider(log_record_processors=[SimpleLogRecordProcessor(exporter)])
```

Outputs JSON-formatted log records to stdout:

```json
{
  "body": "User logged in",
  "severity_number": 9,
  "severity_text": "INFO",
  "attributes": {"user.id": "abc123"},
  "trace_id": "0x...",
  "span_id": "0x...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### OTLP Log Exporter

```python
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter

exporter = OTLPLogExporter(
    endpoint="localhost:4317",
    headers={"authorization": "Bearer token"}
)
logger_provider = LoggerProvider(
    log_record_processors=[BatchLogRecordProcessor(exporter)]
)
```

### BatchLogRecordProcessor

```python
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor

processor = BatchLogRecordProcessor(
    exporter,
    schedule_delay_millis=1000,   # Env: OTEL_BLRP_SCHEDULE_DELAY
    export_timeout_millis=30000,  # Env: OTEL_BLRP_EXPORT_TIMEOUT
    max_queue_size=2048,          # Env: OTEL_BLRP_MAX_QUEUE_SIZE
    max_export_batch_size=512     # Env: OTEL_BLRP_MAX_EXPORT_BATCH_SIZE
)
```

## Concurrency Guarantees

- **LoggerProvider**: All methods MUST be safe for concurrent use by default
- **Logger**: All methods MUST be safe for concurrent use by default
- No locking required by callers — implementations handle thread safety

## Ergonomic API (Development)

Languages MAY provide a more convenient logging API following event semantics. This is in development and subject to change.
