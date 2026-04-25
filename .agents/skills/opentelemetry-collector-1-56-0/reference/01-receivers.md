# Receivers Reference

## OTLP Receiver (Primary)

Receives telemetry via OpenTelemetry Protocol over gRPC or HTTP.

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        max_recv_msg_size_mib: 4
        read_buffer_size: 256KiB
        write_buffer_size: 256KiB
        tls:
          cert_file: /path/to/cert.pem
          key_file: /path/to/key.pem
      http:
        endpoint: 0.0.0.0:4318
        cors:
          allowed_origins:
            - https://example.com
          allowed_headers:
            - Authorization
        tls:
          cert_file: /path/to/cert.pem
          key_file: /path/to/key.pem
```

## Jaeger Receiver

Receives traces from Jaeger agents and SDKs.

```yaml
receivers:
  jaeger:
    protocols:
      grpc:
        endpoint: 0.0.0.0:14250
      thrift_binary:
        endpoint: 0.0.0.0:6833
      thrift_compact:
        endpoint: 0.0.0.0:6831
      thrift_http:
        endpoint: 0.0.0.0:14268
```

## Zipkin Receiver

Receives traces from Zipkin SDKs and agents.

```yaml
receivers:
  zipkin:
    endpoint: 0.0.0.0:9411
    formats:
      zipkin_proto: false
      zipkin_json: true
```

## Prometheus Receiver

Scrapes metrics from targets (pull-based).

```yaml
receivers:
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          scrape_interval: 10s
          static_configs:
            - targets: ['localhost:8888']
        - job_name: 'myapp'
          scrape_interval: 15s
          static_configs:
            - targets: ['myapp:8080']
```

## Host Metrics Receiver

Scrapes host-level metrics (CPU, memory, disk, etc.).

```yaml
receivers:
  hostmetrics:
    collection_interval: 30s
    scrapers:
      cpu:
        metrics:
          system.cpu.utilization:
            enabled: true
      memory:
      disk:
      filesystem:
      load:
      network:
      paging:
      process:
        mute_system: true
        mute_os_policies: true
      processes:
```

## Fluent Forward Receiver

Receives logs from Fluentd agents.

```yaml
receivers:
  fluentforward:
    endpoint: 0.0.0.0:8006
```

## Kafka Receiver

Receives telemetry from Kafka topics.

```yaml
receivers:
  kafka:
    listening_port: 9092
    protocol_version: 2.0.0
    brokers:
      - kafka-broker-1:9092
      - kafka-broker-2:9092
    topics:
      - otel-traces
      - otel-metrics
      - otel-logs
```

## OpenCensus Receiver

Receives telemetry from OpenCensus SDKs.

```yaml
receivers:
  opencensus:
    endpoint: 0.0.0.0:55678
```
