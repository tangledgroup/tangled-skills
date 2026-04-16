# Configuration & Environment Variables

**Status**: Stable (except where noted)

## General SDK Configuration

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `OTEL_SDK_DISABLED` | `false` | Boolean | Disable all signals (no-op SDK). Does NOT affect propagators. |
| `OTEL_ENTITIES` | — | String | Entity information for resource |
| `OTEL_RESOURCE_ATTRIBUTES` | — | String | Key=value pairs for resource attributes, comma-separated |
| `OTEL_SERVICE_NAME` | — | String | Sets `service.name` resource attribute (takes precedence over OTEL_RESOURCE_ATTRIBUTES) |
| `OTEL_LOG_LEVEL` | `info` | Enum | SDK internal logger level |
| `OTEL_PROPAGATORS` | `tracecontext,baggage` | Enum | Comma-separated list of propagators to use |
| `OTEL_TRACES_SAMPLER` | `parentbased_always_on` | Enum | Sampler type for traces |
| `OTEL_TRACES_SAMPLER_ARG` | — | String | Argument for sampler (sampler-dependent) |

### Propagator Values

| Value | Protocol | Status |
|-------|----------|--------|
| `tracecontext` | W3C TraceContext | Standard |
| `baggage` | W3C Baggage | Standard |
| `b3` | B3 Single-header | Standard |
| `b3multi` | B3 Multi-header | Standard |
| `jaeger` | Jaeger | Deprecated |
| `xray` | AWS X-Ray | Third-party |
| `ottrace` | OT Trace | Deprecated |
| `none` | No propagator | — |

### Sampler Values

| Value | Description | OTEL_TRACES_SAMPLER_ARG |
|-------|-------------|------------------------|
| `always_on` | Record all spans | — |
| `always_off` | Record no spans | — |
| `traceidratio` | Sample by probability | Float ∈ [0, 1], default 1.0 |
| `parentbased_always_on` | Respect parent, always on for root | — |
| `parentbased_always_off` | Respect parent, always off for root | — |
| `parentbased_traceidratio` | Respect parent, ratio for root | Float ∈ [0, 1] |
| `parentbased_jaeger_remote` | Respect parent, remote for root | endpoint=pollingIntervalMs=initialSamplingRate= |
| `jaeger_remote` | Remote sampling from Jaeger agent | Same format as above |
| `xray` | AWS X-Ray centralized sampling | — |

### Sampler Arg Format (Jaeger Remote)

```
endpoint=http://localhost:14250,pollingIntervalMs=5000,initialSamplingRate=0.25
```

## Batch Span Processor

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `OTEL_BSP_SCHEDULE_DELAY` | 5000 ms | Duration | Delay between exports |
| `OTEL_BSP_EXPORT_TIMEOUT` | 30000 ms | Timeout | Max time for export |
| `OTEL_BSP_MAX_QUEUE_SIZE` | 2048 | Integer | Maximum queue size |
| `OTEL_BSP_MAX_EXPORT_BATCH_SIZE` | 512 | Integer | Max batch size (≤ queue size) |

## Batch LogRecord Processor

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `OTEL_BLRP_SCHEDULE_DELAY` | 1000 ms | Duration | Delay between exports |
| `OTEL_BLRP_EXPORT_TIMEOUT` | 30000 ms | Timeout | Max time for export |
| `OTEL_BLRP_MAX_QUEUE_SIZE` | 2048 | Integer | Maximum queue size |
| `OTEL_BLRP_MAX_EXPORT_BATCH_SIZE` | 512 | Integer | Max batch size (≤ queue size) |

## Attribute Limits

### General Attribute Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` | no limit | Max attribute value length |
| `OTEL_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per record |

### Span-Specific Limits (Override General)

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` | no limit | Max span attribute value length |
| `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` | 128 | Max span attributes |
| `OTEL_SPAN_EVENT_COUNT_LIMIT` | 128 | Max events per span |
| `OTEL_SPAN_LINK_COUNT_LIMIT` | 128 | Max links per span |
| `OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per span event |
| `OTEL_LINK_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per span link |

### LogRecord-Specific Limits (Override General)

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT` | no limit | Max log attribute value length |
| `OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT` | 128 | Max log record attributes |

**Note**: Resource attributes are exempt from limits. Metric attributes are also exempt at this time. Model-specific limits take precedence over general limits when both are set.

## Exporter Selection

### Trace Exporters

| Variable | Default | Values |
|----------|---------|--------|
| `OTEL_TRACES_EXPORTER` | `otlp` | `otlp`, `zipkin`, `console`, `logging` (deprecated), `none`, `otlp/stdout` (dev) |

### Metric Exporters

| Variable | Default | Values |
|----------|---------|--------|
| `OTEL_METRICS_EXPORTER` | `otlp` | `otlp`, `prometheus`, `console`, `logging` (deprecated), `none`, `otlp/stdout` (dev) |

### Log Exporters

| Variable | Default | Values |
|----------|---------|--------|
| `OTEL_LOGS_EXPORTER` | `otlp` | `otlp`, `console`, `logging` (deprecated), `none`, `otlp/stdout` (dev) |

Multiple exporters can be enabled via comma-separated values.

## OTLP Exporter Configuration

### Common Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | Target URL (overrides OTEL_EXPORTER_OTLP_*_ENDPOINT) |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | — | OTLP traces endpoint |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | — | OTLP metrics endpoint |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | — | OTLP logs endpoint |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | 10000 ms | Max export time (all signals) |
| `OTEL_EXPORTER_OTLP_TRACES_TIMEOUT` | 10000 ms | Trace export timeout |
| `OTEL_EXPORTER_OTLP_METRICS_TIMEOUT` | 30000 ms | Metric export timeout |
| `OTEL_EXPORTER_OTLP_LOGS_TIMEOUT` | 10000 ms | Log export timeout |

### Headers & Credentials

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_HEADERS` | — | Comma-separated key=value pairs for headers |
| `OTEL_EXPORTER_OTLP_TRACES_HEADERS` | — | Headers for trace exporter |
| `OTEL_EXPORTER_OTLP_CERTIFICATE` | — | Path to certificate file |
| `OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE` | — | Trace exporter certificate path |
| `OTEL_EXPORTER_OTLP_CLIENT_KEY` | — | Client key file (mTLS) |
| `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` | — | Client cert file (mTLS) |

### Protocol

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | Transport protocol: `grpc`, `http/protobuf`, `http/json` |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` | — | Trace exporter protocol override |

### Compression

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_COMPRESSION` | — | Compression: `gzip`, `none` |
| `OTEL_EXPORTER_OTLP_TRACES_COMPRESSION` | — | Trace exporter compression override |

## Zipkin Exporter (Deprecated)

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_ZIPKIN_ENDPOINT` | `http://localhost:9411/api/v2/spans` | Zipkin collector URL |
| `OTEL_EXPORTER_ZIPKIN_TIMEOUT` | 10000 ms | Max export time |

## Prometheus Exporter (Development)

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_PROMETHEUS_HOST` | `localhost` | Bind host |
| `OTEL_EXPORTER_PROMETHEUS_PORT` | 9464 | Bind port |

## Metrics Exemplar Filter

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_METRICS_EXEMPLAR_FILTER` | `trace_based` | Exemplar selection: `always_on`, `always_off`, `trace_based` |

## Metric Export Timing

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_METRIC_EXPORT_INTERVAL` | 60000 ms | Time between export attempts |
| `OTEL_METRIC_EXPORT_TIMEOUT` | 30000 ms | Max time for each export |

## Declarative Configuration

### Configuration File

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_CONFIG_FILE` | — | Path to YAML/JSON SDK config file (takes precedence over all env vars) |
| `OTEL_EXPERIMENTAL_CONFIG_FILE` | — | Deprecated, use OTEL_CONFIG_FILE |

When `OTEL_CONFIG_FILE` is set:
- The file is parsed and creates a fully configured SDK
- All other environment variables are IGNORED (except those used for substitution in the file)
- Use `otel-sdk-migration-config.yaml` or `otel-sdk-config.yaml` as starting points from the opentelemetry-configuration repo

### Environment Variable Substitution

Configuration files support `${ENV_VAR}` syntax for referencing environment variables within config values.

## Parsing Rules

### Boolean
- Case-insensitive `"true"` = true
- Everything else (including empty/unset) = false
- Invalid non-false values: warning logged, falls back to false
- All boolean env vars SHOULD default to false (safe default)

### Numeric
- Unparseable values: warning logged, treated as unset
- New implementations MUST treat this as an error

### String/Enum
- Case-insensitive interpretation
- Unrecognized values: warning logged, setting ignored

### Empty Values
- Empty value = same as unset

## Language-Specific Variables

Language-specific variables follow the pattern: `OTEL_{LANGUAGE}_{FEATURE}`

Examples:
- `OTEL_PYTHON_DISABLED_DIALECTS` (Python)
- `OTEL_NODE_DISABLE_PLUGIN` (Node.js)
- `OTEL_GO_AUTO_*` (Go)
