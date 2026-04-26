# Architecture and Pipelines

## Pipeline Construction

A pipeline is constructed during Collector startup based on the pipeline
definition in the configuration file. Each pipeline has a type (traces, metrics,
or logs) and defines which receivers, processors, and exporters participate.

The pipeline structure follows this pattern:

```
Receiver 1 ──┐
Receiver 2 ──┤
   ...       ├──→ Processor 1 → Processor 2 → ... → Processor N → Fan-out
Receiver N ──┘                                                        ├─ Exporter 1
                                                                      ├─ Exporter 2
                                                                      └─ Exporter N
```

All receivers push data to the first processor. Processors chain sequentially —
each receives from one predecessor and sends to one successor. The last
processor uses a `fanoutconsumer` to distribute copies of each data element to
all exporters in the pipeline.

## Pipeline Configuration

Pipelines are defined under `service.pipelines` in the configuration:

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp, zipkin]
      processors: [memory_limiter, batch]
      exporters: [otlp, debug]
```

The pipeline type (traces, metrics, logs) determines which data types the
pipeline processes. Receivers, processors, and exporters used in a pipeline must
support that data type, otherwise `pipeline.ErrSignalNotSupported` is reported
at configuration load time.

### Multiple Pipelines of the Same Type

You can define multiple pipelines of the same signal type using the
`type[/name]` naming convention:

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter]
      exporters: [otlp]
    traces/2:
      receivers: [otlp/2]
      processors: [transform]
      exporters: [otlp/2]
```

## Shared Components Across Pipelines

### Receiver Fan-out

The same receiver can be referenced in multiple pipelines. The Collector creates
only one receiver instance at runtime that sends data to a fan-out consumer,
which then routes to the first processor of each pipeline.

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: localhost:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter]
      exporters: [otlp]
    traces/2:
      receivers: [otlp]
      processors: [transform]
      exporters: [otlp]
```

**Warning**: Data propagation from receiver to fan-out consumer and then to
processors is synchronous. If one processor blocks, all pipelines attached to
that receiver are blocked, and the receiver stops processing newly received data.

### Shared Exporters

Multiple pipelines can send data to the same exporter:

```yaml
exporters:
  otlp:
    endpoint: backend:4317

service:
  pipelines:
    traces:
      receivers: [zipkin]
      processors: [memory_limiter]
      exporters: [otlp]
    traces/2:
      receivers: [otlp]
      processors: [transform]
      exporters: [otlp]
```

### Shared Processors

When the same processor name is referenced in multiple pipelines, each pipeline
gets a separate instance with the same configuration. This ensures independent
processing state per pipeline.

## Component Lifecycle

Each component type has a defined lifecycle:

1. **Create** — component is instantiated with its configuration
2. **Start** — component begins operation (opens ports, connects to backends)
3. **Run** — component processes telemetry data
4. **Shutdown** — component gracefully stops and releases resources

The Collector manages this lifecycle automatically based on the configuration.
Extensions are started before pipelines, and pipelines are shut down before
extensions.

## Component Stability Levels

Components have stability levels documented in their README:

- **Stable** — production-ready, backward-compatible API
- **Beta** — functional with possible breaking changes
- **Alpha** — early-stage, may have significant changes
- **Development** — experimental, not recommended for production
- **Deprecated** — scheduled for removal
- **Deleted** — removed from the codebase

Check the [component registry](https://opentelemetry.io/ecosystem/registry/?language=collector)
for stability status of each component.

## Extensions

Extensions provide capabilities without direct access to telemetry data. They are
enabled through the `service.extensions` list:

```yaml
extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679
  file_storage:
    directory: /var/lib/otelcol

service:
  extensions: [health_check, pprof, zpages, file_storage]
```

Common extensions:

- **health_check** — HTTP health endpoint for load balancers and orchestrators
- **pprof** — Go profiling endpoint for performance debugging
- **zpages** — debug UI showing trace data and component status
- **file_storage** — persistent storage backend for sending queues (WAL)
- **oidc** — OpenID Connect authentication
- **oauth2client** — OAuth 2.0 client credentials for exporters

## Connectors

Connectors are a unique component type that act as both an exporter and a
receiver, bridging two pipelines. They can:

- Route data between pipelines of different signal types
- Transform data from one signal type to another
- Aggregate data across traces to produce metrics

Example — spanmetrics connector converts trace spans into service-level metrics:

```yaml
connectors:
  spanmetrics:
    dimensions:
      - name: http.method
        default: GET
    metrics_flush_interval: 15s

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [spanmetrics, otlp]
    metrics:
      receivers: [spanmetrics]
      exporters: [prometheusremotewrite]
```

## Internal Telemetry

The Collector emits its own telemetry for monitoring and troubleshooting. By
default:

- **Metrics** — exposed via Prometheus endpoint on port `8888`
- **Logs** — emitted to stderr
- **Resource attributes** — automatically includes `service.name`,
  `service.version`, and `service.instance.id`

Configure internal telemetry under `service.telemetry`:

```yaml
service:
  telemetry:
    resource:
      cluster.name: production-us-east
    metrics:
      level: detailed
      readers:
        - pull:
            exporter:
              prometheus:
                host: 0.0.0.0
                port: 8888
        - periodic:
            exporter:
              otlp:
                protocol: http/protobuf
                endpoint: https://backend:4318
    logs:
      level: info
      encode: json
    traces:
      processors: [batch]
```

### Metric Verbosity Levels

- **none** — no telemetry collected
- **basic** — essential service telemetry
- **normal** — default level, adds standard indicators
- **detailed** — most verbose, includes dimensions and views

Key internal metrics for monitoring:

- `otelcol_processor_refused_spans` — spans rejected by memory_limiter
- `otelcol_exporter_queue_size` — current queue depth
- `otelcol_exporter_queue_capacity` — maximum queue capacity
- `otelcol_exporter_enqueue_failed_spans` — spans dropped due to full queue

## Service Section

The `service` section is the orchestration layer that ties everything together:

```yaml
service:
  extensions: [list of enabled extensions]
  telemetry:
    resource: {custom resource attributes}
    metrics: {metrics configuration}
    logs: {logs configuration}
    traces: {traces configuration}
  pipelines:
    traces: {receivers, processors, exporters}
    metrics: {receivers, processors, exporters}
    logs: {receivers, processors, exporters}
```

The service section determines which components are active and how they connect
into pipelines. Components defined in the top-level sections but not referenced
in any pipeline or the extensions list are not loaded.
