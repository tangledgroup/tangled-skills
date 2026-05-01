# Logs

## LoggerProvider

The entry point of the Logs API. Provides access to Loggers.

- SHOULD provide a way to set/register and access a global default LoggerProvider
- Used by logging library authors to build log appenders bridging existing libraries to OTel
- Can also be called directly by instrumentation libraries or applications

### Get a Logger

```
logger = logger_provider.get_logger(name, version, schema_url, attributes)
```

- `name` (required): Identifies the instrumentation scope
- `version` (optional): Library version
- `schema_url` (optional): Schema URL
- `attributes` (optional): Instrumentation scope attributes

For log sources that define a logger name (e.g., Java Logger Name), the Logger Name should be recorded as the instrumentation scope name.

## Logger

Responsible for emitting LogRecords.

### Emit a LogRecord

```python
logger.emit(
    timestamp=now,
    observed_timestamp=now,
    context=current_context,
    severity_text="INFO",
    severity_number=9,
    body="Request processed successfully",
    attributes={"http.status_code": 200}
)
```

Required parameters:

- **Context**: Associated with the LogRecord (optional if implicit Context is supported)
- **Body**: The log message (AnyValue)

Optional parameters:

- **Timestamp**: Time when the event occurred
- **Observed Timestamp**: Time when the event was processed
- **SeverityText**: Human-readable severity label
- **SeverityNumber**: Numeric severity level
- **Exception** (Stable in 1.56.0): Optional Exception parameter to Emit LogRecord, allowing structured exception data to be passed directly during log emission

### Enabled

Reports whether a Logger is enabled for a given severity level. Used by logging libraries to skip formatting when logging is disabled.

## LogRecord Data Model

A log record contains two kinds of fields:

1. **Named top-level fields** of specific type and meaning
2. **Attribute Collections** (key-value pairs with AnyValue values)

### Field Definitions

- **Timestamp**: Time when the event occurred (optional)
- **ObservedTimestamp**: Time when the event was ingested/processed
- **TraceId**: 16-byte trace identifier (if associated with a trace)
- **SpanId**: 8-byte span identifier (if associated with a span)
- **TraceFlags**: Trace flags from the associated SpanContext
- **SeverityText**: Human-readable severity (e.g., "INFO", "ERROR")
- **SeverityNumber**: Numeric severity level
- **Body**: The log message content (AnyValue — can be string, structured, etc.)
- **Resource**: Entity for which telemetry is recorded
- **InstrumentationScope**: Source of the telemetry
- **Attributes**: Additional key-value pairs

### Severity Mapping

SeverityNumber follows a scale where lower values are less severe:

- 1–4: Trace/Debug levels
- 5–8: Information levels
- 9–12: Warning levels
- 13–16: Error levels (ERROR = 17, FATAL = 21 in some mappings)

The spec defines a reverse mapping from common log formats to SeverityNumber.

## Events

Events are OpenTelemetry's standardized format for LogRecords. All semantic conventions defined for logs SHOULD be formatted as Events.

- Events include an `event.name` attribute
- Not all LogRecords need to be formatted as Events
- Designed for use by OpenTelemetry instrumentation

## Event to Span Event Bridge (New in 1.56.0)

The specification adds a bridge from log events to span events, allowing log-based event data to be converted into span events for correlation with tracing data.

This bridge enables:

- Converting structured log records (especially Events) into Span Events
- Associating log data with the corresponding trace/span context
- Bridging the gap between logging and tracing signals for unified observability

## Design Goals

The Logs Data Model was designed to:

1. Unambiguously map existing log formats (Syslog, Apache logs, etc.)
2. Preserve semantics of particular elements
3. Support efficient serialization/deserialization
4. Represent system formats, third-party application logs, and first-party application logs

## Ergonomic API

Languages may provide more ergonomic APIs for direct usage beyond the core Logger/LoggerProvider pattern. This is language-specific and not mandated by the spec.
