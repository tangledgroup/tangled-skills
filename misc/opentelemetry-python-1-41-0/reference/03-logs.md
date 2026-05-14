# Logs

## Status

The logs signal is in **development** status as of v1.41.0. Breaking changes may occur before stabilization. The API and SDK provide the foundation for structured logging with trace correlation.

## LoggerProvider and Logger

```python
from opentelemetry._logs import LoggerProvider, get_logger, get_logger_provider
from opentelemetry.sdk._logs import LoggerProvider as SDKLoggerProvider
from opentelemetry.sdk._logs.export import (
    ConsoleLogExporter,
    BatchLogRecordProcessor,
)

# Configure the SDK logger provider
provider = SDKLoggerProvider()
provider.add_log_record_processor(
    BatchLogRecordProcessor(ConsoleLogExporter())
)

# Get a logger by instrumentation scope name
logger = get_logger("my-app")
```

## LogRecord

A `LogRecord` represents an emitted log event:

```python
from opentelemetry._logs import LogRecord, SeverityNumber
from opentelemetry.context import get_current

record = LogRecord(
    timestamp=None,                        # Auto-filled if None
    observed_timestamp=None,               # When the record was observed
    context=get_current(),                 # Current context (for trace correlation)
    severity_text="INFO",                  # Human-readable severity
    severity_number=SeverityNumber.INFO,   # Numeric severity
    body="Request processed successfully", # Log message
    attributes={                           # Structured attributes
        "http.method": "GET",
        "http.status_code": 200,
    },
)
```

### SeverityNumber

Maps to OTLP severity levels. Common values:

- `SeverityNumber.DEBUG` (5)
- `SeverityNumber.INFO` (9)
- `SeverityNumber.WARNING` (13)
- `SeverityNumber.ERROR` (17)
- `SeverityNumber.FATAL` (21)

The full enum provides granularity from TRACE (1) through FATAL (21+).

## Logger Emission

The SDK Logger emits log records:

```python
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry._logs import SeverityNumber

logger = provider.get_logger("my-app")

# Emit a log record
logger.emit(
    LogRecord(
        severity_text="ERROR",
        severity_number=SeverityNumber.ERROR,
        body="Connection failed",
        attributes={"host": "db.example.com"},
    )
)
```

## LoggingHandler

Bridge Python's standard `logging` module to OpenTelemetry:

```python
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogExporter, BatchLogRecordProcessor

# Create logger provider with processor
provider = LoggerProvider()
provider.add_log_record_processor(
    BatchLogRecordProcessor(ConsoleLogExporter())
)

# Attach handler to Python's root logger
handler = LoggingHandler(logger_provider=provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

# Standard Python logging now emits OpenTelemetry log records
logging.info("Application started", extra={"service": "api"})
logging.error("Database connection failed", exc_info=True)
```

The `LoggingHandler` automatically:

- Maps Python log levels to OTLP `SeverityNumber`
- Attaches the current trace context (trace_id, span_id, trace_flags)
- Includes exception info when `exc_info=True`
- Preserves standard logging attributes as OpenTelemetry attributes

## LogRecordProcessor

Similar to span processors, log record processors hook into the log lifecycle:

```python
from opentelemetry.sdk._logs import LogRecordProcessor

class CustomLogProcessor(LogRecordProcessor):
    def emit(self, log_record):
        # Called synchronously when a log record is emitted
        pass

    def shutdown(self):
        # Called on LoggerProvider shutdown
        pass

    def force_flush(self, timeout_millis=30000):
        # Flush pending records
        return True
```

## Log Export

The log export module provides `LogRecordExporter` and processors:

```python
from opentelemetry.sdk._logs.export import (
    LogRecordExporter,
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
)

# Batch processor — batches records before export (recommended for production)
processor = BatchLogRecordProcessor(
    exporter,
    schedule_delay_millis=1000,   # OTEL_BLRP_SCHEDULE_DELAY
    max_export_batch_size=512,    # OTEL_BLRP_MAX_EXPORT_BATCH_SIZE
    max_queue_size=2048,          # OTEL_BLRP_MAX_QUEUE_SIZE
    export_timeout_millis=30000,  # OTEL_BLRP_EXPORT_TIMEOUT
)

# Simple processor — exports each record immediately
processor = SimpleLogRecordProcessor(exporter)
```

## LogRecordLimits

Controls memory usage for log records:

```python
from opentelemetry.sdk._logs import LogRecordLimits

limits = LogRecordLimits(
    max_attributes=128,            # OTEL_ATTRIBUTE_COUNT_LIMIT
    max_attribute_length=None,     # OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT
)

provider = LoggerProvider(log_record_limits=limits)
```

## Environment Variables

- `OTEL_BLRP_SCHEDULE_DELAY` — Delay between batch exports (ms), default: 1000
- `OTEL_BLRP_EXPORT_TIMEOUT` — Maximum export time (ms), default: 30000
- `OTEL_BLRP_MAX_QUEUE_SIZE` — Maximum queue size, default: 2048
- `OTEL_BLRP_MAX_EXPORT_BATCH_SIZE` — Maximum batch size, default: 512
- `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` — Enable auto-instrumentation for stdlib logging (deprecated, use `opentelemetry-instrumentation-logging` instead)
