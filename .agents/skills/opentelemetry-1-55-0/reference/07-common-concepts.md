# Common Concepts & Resources

**Status**: Stable (except where noted)

## AnyValue

The fundamental value type for all OpenTelemetry attributes, log bodies, and map values.

### Types

| Type | Description | Constraints |
|------|-------------|-------------|
| String | UTF-8 text | — |
| Boolean | true/false | — |
| Double | IEEE 754-1985 float64 | NaN, Infinity supported |
| Int64 | Signed 64-bit integer | — |
| Array | Homogeneous array of primitives | No mixed types within array |
| ByteArray | Raw bytes | Base64 for non-OTLP |
| Map\<string, AnyValue\> | String keys to AnyValue values | Unique keys, case-sensitive |
| Empty value | Language null equivalent | `None`, `nil`, `undefined`, etc. |

### Deep Nesting

Arbitrary deep nesting of arrays and maps is allowed (equivalent to JSON object structure).

### Semantics

- Empty values, zero values, empty strings, and empty arrays are **meaningful** — they MUST be stored and passed on
- `null` within homogeneous arrays SHOULD be avoided but preserved if language constraints make it impossible
- Maps with duplicate keys: implementations MUST enforce uniqueness by default; may offer performance option for duplicates

### map<string, AnyValue>

- Keys are unique (duplicates not allowed)
- Case-sensitive key comparison
- Map equality: same key-value pairs regardless of order
- Languages may implement as hash map, sorted map, or other structure

### Non-OTLP Encoding (Lossy)

For protocols without native AnyValue support:

| Type | Encoding | Example |
|------|----------|---------|
| String | As-is | `hello world` |
| Boolean | JSON | `true`, `false` |
| Integer | JSON number | `42`, `-123` |
| Float | JSON number | `3.14159`, `NaN`, `Infinity` |
| Byte Array | Base64 | `aGVsbG8gd29ybGQ=` |
| Empty Value | Empty string | `` |
| Array | JSON array | `[1, "-Infinity", "a"]` |
| Map | JSON object | `{"a": "-Infinity", "b": 2}` |

## Attributes

### Definition

An Attribute is a key-value pair with:
- **Key**: Non-null, non-empty string (case-sensitive)
- **Value**: AnyValue type

### Attribute Collections

Collections appear in Resources, InstrumentationScopes, MetricDataPoints, Spans, SpanEvents, SpanLinks, and LogRecords.

**Uniqueness enforcement**: Implementations MUST enforce unique keys by default. Overwriting a key replaces its value.

```python
span.set_attribute("http.method", "GET")       # First set
span.set_attribute("http.method", "POST")      # Overwrites to POST
span.set_attributes({"key1": "val1", "key2": 42})  # Multiple at once
```

### Attribute Limits

| Limit | Default | Env Var | Notes |
|-------|---------|---------|-------|
| Attribute count per record | 128 | `OTEL_ATTRIBUTE_COUNT_LIMIT` | Applies to spans, logs |
| Attribute value length | no limit | `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` | String/byte array truncation |

**Exemptions**: Resource attributes and metric data point attributes are exempt from general attribute limits. Model-specific limits (e.g., `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT`) take precedence over general limits.

### Truncation Behavior

When limits are exceeded:
- **Count limit**: Attribute is discarded if adding it would exceed the limit
- **Value length limit**: Value is truncated to the specified length
- Log emitted at most once per record where attribute was set (to prevent excessive logging)

## Instrumentation Scope

Identifies the component that emitted telemetry data.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | REQUIRED — instrumentation scope name (e.g., library name, module) |
| `version` | String | OPTIONAL — version of the instrumentation scope |
| `schema_url` | String | OPTIONAL — URL to schema definition (since 1.4.0) |
| `attributes` | AttributeCollection | OPTIONAL — scope-specific attributes (since 1.13.0) |

### Naming Convention

For OpenTelemetry-hosted instrumentation packages:
- Python: `opentelemetry-instrumentation-{component}`
- JavaScript: `@opentelemetry/instrumentation-{component}`

For third-party instrumentation:
- `{company}-opentelemetry-instrumentation-{component}` or similar to avoid collisions

## Resource

A `Resource` captures information about the entity producing telemetry.

### Structure

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    # Required by SDK
    "service.name": "my-service",
    # Optional but recommended
    "service.version": "1.0.0",
    "service.instance.id": "abc-123",
    "deployment.environment.name": "production",
    # Cloud provider info
    "cloud.provider": "aws",
    "cloud.region": "us-east-1",
    "cloud.availability_zone": "us-east-1a",
    # Container info
    "container.id": "abc123def456",
    "container.image.name": "myapp",
    "container.image.tag": "v1.0.0",
    # Host info
    "host.name": "web-server-01",
    "host.id": "i-0abc123def456",
    # Process info
    "process.pid": 12345,
    "process.executable.name": "python",
    "process.runtime.name": "CPython",
    "process.runtime.version": "3.12.0",
})
```

### Resource Detectors

Built-in detectors auto-populate resource attributes:

| Detector | Attributes Populated |
|----------|---------------------|
| `TelemetrySDKResourceDetector` | `telemetry.sdk.*` attributes |
| `HostDetector` | `host.*` attributes |
| `OsDetector` | `os.*` attributes (type, description) |
| `ProcessDetector` | `process.*` attributes (pid, parent_pid, command, args, runtime.*) |
| `ServiceDetector` | `service.*` attributes from env vars |

### Custom Resource Detector

```python
from opentelemetry.sdk.resources import Resource, ResourceDetector, get_all_resources

class CloudResourceDetector(ResourceDetector):
    def detect(self) -> Resource:
        # Detect cloud provider from metadata service
        try:
            with urllib.request.urlopen(
                "http://169.254.169.254/latest/meta-data/"
            ) as response:
                provider = "aws"
        except Exception:
            provider = "unknown"
        
        return Resource.create({"cloud.provider": provider})

# Combine all detectors
resource = get_all_resources()
```

### Environment Variable Resource Attributes

```bash
# Set resource attributes via environment variable
export OTEL_RESOURCE_ATTRIBUTES=key1=value1,key2=value2

# Values with commas or equals must be URL-encoded
export OTEL_RESOURCE_ATTRIBUTES=service.version=1.0.0,team=my%2Cteam

# service.name can also be set separately (takes precedence)
export OTEL_SERVICE_NAME=my-service
```

## Error Handling

### SDK Logger

The SDK has an internal logger for self-diagnostics:

| Level | Env Var Value | Description |
|-------|--------------|-------------|
| DEBUG | `debug` | Debug-level diagnostic messages |
| INFO | `info` | Default — informational messages |
| WARNING | `warn`, `warning` | Warnings about configuration issues |
| ERROR | `error` | Error conditions |
| OFF | `off` | Disable all SDK logging |

```bash
export OTEL_LOG_LEVEL=debug
```

### Error Callbacks

SDK components MAY provide error callback mechanisms for applications to handle export failures, configuration errors, and other SDK-level issues.

## Document Status Levels

| Status | Description |
|--------|-------------|
| **Stable** | Ready for production use, backward-compatible guarantees apply |
| **Development** | In development, breaking changes possible, opt-in recommended |
| **Deprecated** | Being replaced, same support guarantees as stable until removed |
| **Removed** | No longer available, major version bump required |

## Library Design Principles

### Cross-Cutting Concerns

OpenTelemetry is a cross-cutting concern — it's mixed into many other pieces of software. This requires extra care:

1. **API/SDK Separation**: API packages are imported by application code; SDK is installed separately
2. **Instrumentation authors** MUST NOT directly reference any SDK package — only the API
3. **Application owners** install and manage the SDK
4. **Plugin authors** use SDK plugin interfaces (SpanProcessor, Exporter, Sampler)

### Package Layout

```
opentelemetry-api/          # API packages (imported by apps/libraries)
opentelemetry-sdk/          # SDK implementation (installed by app owner)
opentelemetry-semantic-conventions/  # Semantic convention constants
opentelemetry-instrumentation-*    # Contrib instrumentation packages
opentelemetry-exporter-*          # Contrib exporter packages
```

### Versioning Independence

- API, SDK, Semantic Conventions, and Contrib have **independent** version numbers
- Different languages have independent version numbers
- A single Python release may implement a different spec version than Java
- The project has no plans for v2.0 — new incompatible signals coexist with old ones
