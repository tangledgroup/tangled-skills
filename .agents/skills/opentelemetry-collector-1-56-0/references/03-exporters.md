# Exporters Reference

## OTLP gRPC Exporter

Sends telemetry via OTLP over gRPC (most efficient).

```yaml
exporters:
  otlp_grpc:
    endpoint: jaeger:14250
    tls:
      insecure: true
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
```

## OTLP HTTP Exporter

Sends telemetry via OTLP over HTTP/JSON.

```yaml
exporters:
  otlp_http:
    endpoint: https://otlp.example.com:4318
    compression: none # or gzip
    tls:
      ca_file: /path/to/ca.pem
```

## Debug Exporter

Writes telemetry to stdout/stderr. Use for development and debugging.

```yaml
exporters:
  debug:
    verbosity: basic     # basic, detailed, normal
    sampling_initial: 5  # samples per tick
    sampling_thereafter: 100
```

## Prometheus Exporter

Exposes metrics in Prometheus format for scraping (pull-based).

```yaml
exporters:
  prometheus:
    endpoint: '0.0.0.0:8889'
    namespace: myapp
    const_labels:
      label1: value1
      label2: value2
    send_timestamps: true
```

## Prometheus Remote Write Exporter

Pushes metrics to Prometheus-compatible backends via remote write API.

```yaml
exporters:
  prometheusremotewrite:
    endpoint: 'http://prometheus:9090/api/v1/write'
    tls:
      insecure: true
    resource_to_telemetry_conversion:
      enabled: true
    sending_queue:
      enabled: true
```

## Jaeger Exporter

Sends traces to Jaeger via gRPC or HTTP.

```yaml
exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
    # gRPC options
    compression: none
    retry_on_failure:
      enabled: true
```

## Zipkin Exporter

Sends traces to Zipkin.

```yaml
exporters:
  zipkin:
    endpoint: http://zipkin:9411/api/v2/spans
    format: proto # or json
```

## Kafka Exporter

Publishes telemetry to Kafka topics.

```yaml
exporters:
  kafka:
    brokers:
      - kafka-broker-1:9092
      - kafka-broker-2:9092
    topic: otel-traces
    protocol_version: 2.0.0
    tls:
      insecure: true
```

## File Exporter

Writes telemetry to local files (useful for debugging/testing).

```yaml
exporters:
  file:
    path: /var/log/otel-collector/output.json
    rotation:
      max_megabytes: 100
      max_days: 7
```

## Load Balancing Exporter

Distributes telemetry across multiple backends using DNS or static resolution. Useful for gateway pattern.

```yaml
exporters:
  loadbalancing:
    resolver:
      dns:
        hostname: collectors.example.com
        port: 4317
    # or static:
    # resolver:
    #   static:
    #     hostnames:
    #       - collector-1:4317
    #       - collector-2:4317
    routing_key: traceID # or service, or empty for round-robin
    protocol:
      otlp:
        tls:
          insecure: true
```

## AWS CloudWatch Logs Exporter

Sends logs to AWS CloudWatch Logs.

```yaml
exporters:
  awsemf:
    endpoint: emf.us-east-1.amazonaws.com
    region: us-east-1
    namespace: MyNamespace
```

## AWS X-Ray Exporter

Sends traces to AWS X-Ray.

```yaml
exporters:
  awsxray:
    region: us-east-1
    local_mode: false
```

## Elastic Search Exporter

Sends telemetry to Elasticsearch.

```yaml
exporters:
  elasticsearch:
    urls:
      - https://es-host:9200
    tls:
      insecure: true
    logs_index: otel
    sending_queue:
      enabled: true
```
