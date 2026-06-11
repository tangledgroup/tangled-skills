# Alternative Backends

## Overview

Logfire uses the OpenTelemetry standard. Configure the SDK to export to any OTel-compatible backend using environment variables. Data is encoded using Protobuf over HTTP (not gRPC).

Set `OTEL_EXPORTER_OTLP_ENDPOINT` as a base URL — the SDK appends `/v1/traces` and `/v1/metrics`. Or set separate endpoints:

- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`
- `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`
- `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`

## Example: Jaeger

Start Jaeger:

```bash
docker run --rm \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Configure Logfire to export to Jaeger:

```python
import os
import logfire

os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://localhost:4318/v1/traces'

logfire.configure(
    service_name='my_logfire_service',
    send_to_logfire=False,  # Don't also send to Logfire cloud
)

with logfire.span('This is a span'):
    logfire.info('Hello from Logfire to Jaeger!')
```

Open http://localhost:16686/search?service=my_logfire_service.

## Alternative Clients

Any language with an OpenTelemetry SDK can send data to Logfire. Set these environment variables:

```bash
# US region
export OTEL_EXPORTER_OTLP_ENDPOINT=https://logfire-us.pydantic.dev
# EU region: https://logfire-eu.pydantic.dev

export OTEL_EXPORTER_OTLP_HEADERS='Authorization=your-write-token'
```

### Python (standard OTel SDK)

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = OTLPSpanExporter(
    endpoint='https://logfire-us.pydantic.dev/v1/traces',
    headers={'Authorization': 'your-write-token'},
)
span_processor = BatchSpanProcessor(exporter)
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(span_processor)
tracer = tracer_provider.get_tracer('my_tracer')
tracer.start_span('Hello World').end()
```

### Node.js

```js
import {NodeSDK} from "@opentelemetry/sdk-node";
import {OTLPTraceExporter} from "@opentelemetry/exporter-trace-otlp-proto";
import {BatchSpanProcessor} from "@opentelemetry/sdk-trace-node";
import {trace} from "@opentelemetry/api";
import {Resource} from "@opentelemetry/resources";
import {ATTR_SERVICE_NAME} from "@opentelemetry/semantic-conventions";

const sdk = new NodeSDK({
  spanProcessor: new BatchSpanProcessor(new OTLPTraceExporter()),
  resource: new Resource({[ATTR_SERVICE_NAME]: "my_service"}),
});
sdk.start();
trace.getTracer("my_tracer").startSpan("Hello World").end();
```

### Rust

Use `opentelemetry-otlp` crate with `HttpBinary` protocol. Note: `reqwest-rustls` feature is necessary to avoid cryptic export failures.

### Go

Use `go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp`.

## Other Environment Variables

If `OTEL_TRACES_EXPORTER` and/or `OTEL_METRICS_EXPORTER` are set to any non-empty value other than `otlp`, Logfire ignores the corresponding `OTEL_EXPORTER_OTLP_*` variables. See [OpenTelemetry Python documentation](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html) for additional headers like `OTEL_EXPORTER_OTLP_HEADERS`.
