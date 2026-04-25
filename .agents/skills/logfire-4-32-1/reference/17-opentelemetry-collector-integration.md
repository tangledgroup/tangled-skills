# OpenTelemetry Collector Integration

Use the OTel Collector for centralized configuration, data transformation, and enrichment:

```yaml title="config.yaml"
receivers:
  otlp:
    protocols:
      http:
        endpoint: "0.0.0.0:4318"
exporters:
  otlphttp:
    endpoint: "https://logfire-us.pydantic.dev"
    headers:
      Authorization: "Bearer ${env:LOGFIRE_TOKEN}"
processors:
  batch:
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp]
```

Use cases: centralized credentials, data scrubbing, Kubernetes metadata enrichment, backing up to S3.

See [reference/09-otel-collector.md](reference/09-otel-collector.md) for deployment examples.
