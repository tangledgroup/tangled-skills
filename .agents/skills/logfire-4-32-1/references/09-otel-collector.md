# Logfire OpenTelemetry Collector Reference

## Use Cases

1. **Centralized configuration**: Keep credentials in one place, update without app changes
2. **Data transformation**: Filter/modify data before sending to Logfire (advanced scrubbing)
3. **Data enrichment**: Add host/container metadata to logs
4. **Collecting existing sources**: Kubernetes logs, Prometheus metrics

## Basic Configuration

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
    timeout: 10s
    send_batch_size: 32768

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp]
```

Run locally:
```bash
docker run \
    -v ./config.yaml:/etc/otelcol-contrib/config.yaml \
    -e LOGFIRE_TOKEN=$LOGFIRE_TOKEN \
    -p 4318:4318 \
    otel/opentelemetry-collector-contrib
```

## Backup to AWS S3

```yaml title="config-s3.yaml"
receivers:
  otlp:
    protocols:
      http:
        endpoint: "0.0.0.0:4318"

exporters:
  awss3:
    s3uploader:
      region: us-east-1
      s3_bucket: my-logfire-backup-bucket

processors:
  batch:
    timeout: 10s
    send_batch_size: 32768

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [awss3]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [awss3]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [awss3]
```

Send data to both Logfire and S3:
```python
import os
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'
logfire.configure(send_to_logfire=True)  # Also sends to Logfire directly
```

## Kubernetes Log Collection (DaemonSet)

For collecting stdout/stderr logs from Kubernetes pods without modifying applications:

```yaml title="collector-k8s.yaml"
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |-
    receivers:
      filelog:
        include_file_path: true
        include:
          - /var/log/pods/*/*/*.log
        exclude:
          - /var/log/pods/*/otel-collector/*.log
        operators:
          - id: container-parser
            type: container
          - id: json_parser
            type: json_parser
            if: 'hasPrefix(body, "{\"")'
            parse_from: body
            parse_to: attributes
    exporters:
      otlphttp:
        endpoint: "https://logfire-eu.pydantic.dev"
        headers:
          Authorization: "Bearer ${env:LOGFIRE_TOKEN}"
    service:
      pipelines:
        logs:
          receivers: [filelog]
          exporters: [otlphttp]
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: otel-collector
spec:
  selector:
    matchLabels:
      app: opentelemetry
  template:
    spec:
      serviceAccountName: otel-collector
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:0.128.0
          env:
            - name: LOGFIRE_TOKEN
              valueFrom:
                secretKeyRef:
                  name: logfire-token
                  key: logfire-token
          volumeMounts:
            - mountPath: /var/log
              name: varlog
              readOnly: true
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
```

## Kubernetes Metadata Enrichment

Add pod/deployment/namespace attributes to all telemetry:

```yaml
processors:
  k8sattributes:
    extract:
      metadata:
        - k8s.cluster.uid
        - k8s.pod.name
        - k8s.deployment.name
        - k8s.namespace.name
        - k8s.node.name
        - k8s.container.name
service:
  pipelines:
    traces:
      processors: [k8sattributes]
      exporters: [otlphttp]
```

## Deployment Patterns

| Pattern | Description | Best For |
|---------|-------------|----------|
| Sidecar | Collector container alongside app pod | Specific apps, less permissions needed |
| DaemonSet | One collector per node | Cluster-wide log collection |
| Gateway/Standalone | Separate collector service | Centralized aggregation |

## Region Endpoints

| Region | Endpoint |
|--------|----------|
| US | `https://logfire-us.pydantic.dev` |
| EU | `https://logfire-eu.pydantic.dev` |
