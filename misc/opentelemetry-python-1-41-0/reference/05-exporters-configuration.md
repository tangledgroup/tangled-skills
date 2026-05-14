# Exporters and Configuration

## SpanExportResult

The `SpanExporter` interface returns one of two results:

```python
from opentelemetry.sdk.trace.export import SpanExportResult

SpanExportResult.SUCCESS  # Export succeeded
SpanExportResult.FAILURE  # Export failed
```

## Built-in Exporters

### ConsoleSpanExporter

Exports spans to stdout for debugging:

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

exporter = ConsoleSpanExporter(service_name="my-service")
processor = SimpleSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(processor)
```

### OTLP Exporters

The OpenTelemetry Protocol (OTLP) exporters send data to any OTLP-compatible backend:

**gRPC exporter** (`opentelemetry-exporter-otlp-proto-grpc`):

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="localhost:4317",   # Default
    insecure=True,               # Use TLS when False
    credentials=channel_creds,   # For mTLS
    headers={"Authorization": "Bearer token"},
    timeout=10,                  # Seconds
    compression=Compression.Gzip,
)
```

**HTTP exporter** (`opentelemetry-exporter-otlp-proto-http`):

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    headers={"Authorization": "Bearer token"},
    timeout=10,
)
```

## Span Processors

### SimpleSpanProcessor

Exports each span immediately on end. Not recommended for production due to performance impact:

```python
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

processor = SimpleSpanProcessor(exporter)
```

### BatchSpanProcessor

Batches spans before export. Recommended for production:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,        # OTEL_BSP_MAX_QUEUE_SIZE
    schedule_delay_millis=5000,  # OTEL_BSP_SCHEDULE_DELAY
    max_export_batch_size=512,   # OTEL_BSP_MAX_EXPORT_BATCH_SIZE
    export_timeout_millis=30000, # OTEL_BSP_EXPORT_TIMEOUT
)
```

## Resource

Resources identify the entity producing telemetry:

```python
from opentelemetry.sdk.resources import Resource, ResourceDetector

# Manual resource
resource = Resource.create({
    "service.name": "my-api",
    "service.instance.id": "instance-1",
    "deployment.environment": "production",
})

# Resource.create() auto-populates standard attributes:
# - telemetry.sdk.name = "opentelemetry"
# - telemetry.sdk.version = "<version>"
# - telemetry.sdk.language = "python"
# - process.pid, process.runtime.name, process.runtime.version
# - host.name, host.arch, os.type, os.description

# Merge resources
combined = resource.merge(Resource.create({"custom.key": "value"}))

# Pass to providers
provider = TracerProvider(resource=resource)
```

### Resource Detectors

Automatic detection of environment attributes:

```python
from opentelemetry.sdk.resources import (
    ProcessResourceDetector,
    HostResourceDetector,
    OSResourceDetector,
    PythonResourceDetector,
)

# Via environment variable
# OTEL_EXPERIMENTAL_RESOURCE_DETECTORS=process,host,os,python

# Manual detection
detectors = [ProcessResourceDetector(), HostResourceDetector()]
resource = Resource.create(detectors=detectors)
```

### Standard Resource Attributes

Key semantic convention attributes:

- `service.name` — Logical identification of the service (required for most backends)
- `service.instance.id` — Unique runtime instance identifier
- `service.version` — Service version
- `deployment.environment` — Deployment environment (e.g., "production", "staging")
- `cloud.provider` — Cloud provider ("aws", "gcp", "azure")
- `cloud.region` — Cloud region
- `cloud.availability_zone` — Cloud availability zone
- `container.name`, `container.id` — Container metadata
- `k8s.pod.name`, `k8s.namespace.name`, `k8s.deployment.name` — Kubernetes metadata
- `host.name`, `host.arch` — Host information
- `process.pid`, `process.runtime.name`, `process.runtime.version` — Process info

Set service name via environment variable:

```bash
export OTEL_SERVICE_NAME=my-python-service
# Equivalent to:
export OTEL_RESOURCE_ATTRIBUTES=service.name=my-python-service
```

## SDK Configuration via Environment Variables

### Core Settings

- `OTEL_SDK_DISABLED=true` — Disable all SDK telemetry
- `OTEL_LOG_LEVEL=info` — SDK logger level (debug, info, warn, error)
- `OTEL_PROPAGATORS=tracecontext,baggage` — Context propagators to use

### Traces

- `OTEL_TRACES_SAMPLER=parentbased_always_on` — Sampler selection
- `OTEL_TRACES_SAMPLER_ARG=1.0` — Sampler argument (for ratio-based)
- `OTEL_TRACES_EXPORTER=otlp` — Trace exporter (otlp, none)

### Metrics

- `OTEL_METRICS_EXPORTER=otlp` — Metric exporter (otlp, prometheus, none)
- `OTEL_METRIC_EXPORT_INTERVAL=60000` — Export interval in ms
- `OTEL_METRIC_EXPORT_TIMEOUT=30000` — Export timeout in ms

### Logs

- `OTEL_LOGS_EXPORTER=otlp` — Log exporter (otlp, none)

### OTLP Protocol Settings

- `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` — Default protocol (grpc or http/protobuf)
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` — Default endpoint
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` — Signal-specific endpoint
- `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`
- `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`
- `OTEL_EXPORTER_OTLP_HEADERS=key1=val1,key2=val2` — Auth headers
- `OTEL_EXPORTER_OTLP_TIMEOUT=10` — Export timeout in seconds
- `OTEL_EXPORTER_OTLP_COMPRESSION=gzip` — Compression (gzip, deflate)

### Batch Processor Settings

- `OTEL_BSP_SCHEDULE_DELAY=5000` — Span batch delay (ms)
- `OTEL_BSP_MAX_QUEUE_SIZE=2048` — Span queue size
- `OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512` — Max batch size
- `OTEL_BSP_EXPORT_TIMEOUT=30000` — Export timeout (ms)
- `OTEL_BLRP_SCHEDULE_DELAY=1000` — Log batch delay (ms)
- `OTEL_BLRP_MAX_QUEUE_SIZE=2048` — Log queue size
- `OTEL_BLRP_MAX_EXPORT_BATCH_SIZE=512` — Log max batch size
- `OTEL_BLRP_EXPORT_TIMEOUT=30000` — Log export timeout (ms)

### Attribute Limits

- `OTEL_ATTRIBUTE_COUNT_LIMIT=128` — Global attribute count limit
- `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT=128` — Per-span attribute limit
- `OTEL_SPAN_EVENT_COUNT_LIMIT=128` — Max events per span
- `OTEL_SPAN_LINK_COUNT_LIMIT=128` — Max links per span
- `OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT=128` — Max attributes per event
- `OTEL_LINK_ATTRIBUTE_COUNT_LIMIT=128` — Max attributes per link
- `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` — Max attribute value length (unlimited by default)

### TLS / mTLS

- `OTEL_EXPORTER_OTLP_CERTIFICATE` — CA certificate path
- `OTEL_EXPORTER_OTLP_CLIENT_KEY` — Client private key path
- `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` — Client certificate path
- Signal-specific variants: `OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE`, etc.

## Full Example

Complete setup with OTLP exporter, resource, and all three signals:

```python
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Define resource
resource = Resource.create({
    "service.name": os.getenv("OTEL_SERVICE_NAME", "my-service"),
    "service.version": "1.0.0",
})

# Configure tracing
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(trace_provider)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
)
metrics.set_meter_provider(meter_provider)

# Use tracers and meters
tracer = trace.get_tracer("my-app")
meter = metrics.get_meter("my-app")
```

## Shutdown

Properly flush and shutdown providers:

```python
# Manual shutdown
trace.get_tracer_provider().shutdown()
metrics.get_meter_provider().shutdown()

# Or via atexit (enabled by default with shutdown_on_exit=True)
provider = TracerProvider(shutdown_on_exit=True)
```

`force_flush()` exports all pending data within a timeout:

```python
trace.get_tracer_provider().force_flush(timeout_millis=5000)
```
