# Deployment Patterns Reference

## Agent Pattern

Collector runs as a sidecar or DaemonSet alongside application pods. Each pod sends to its local collector.

### Kubernetes DaemonSet Example

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: otel-collector-agent
spec:
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      serviceAccountName: otel-collector
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:1.56.0
          args:
            - --config=/conf/collector-config.yaml
          volumeMounts:
            - name: config
              mountPath: /conf
          ports:
            - containerPort: 4317 # OTLP gRPC
            - containerPort: 4318 # OTLP HTTP
            - containerPort: 8888  # Prometheus metrics
      volumes:
        - name: config
          configMap:
            name: otel-collector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318

    processors:
      memory_limiter:
        check_interval: 1s
        limit_mib: 1000
        spike_limit_mib: 200
      batch:
        send_batch_size: 5120
        timeout: 2s

    exporters:
      otlp:
        endpoint: otel-gateway:4317
        tls:
          insecure: true

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp]
```

### Docker Compose Agent Example

```yaml
services:
  myapp:
    image: myapp:latest
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-agent:4317
      - OTEL_SERVICE_NAME=my-app
    depends_on:
      - otel-agent

  otel-agent:
    image: otel/opentelemetry-collector-contrib:1.56.0
    volumes:
      - ./otel-config.yaml:/etc/otel/config.yaml
    command: ["--config=/etc/otel/config.yaml"]
    ports:
      - "4317:4317"
      - "4318:4318"
```

## Gateway Pattern

Centralized collectors receive from agents/apps and forward to backends.

### NGINX Load Balancer for Gateway Collectors

```nginx
upstream otel_collectors {
    server collector-1:4317;
    server collector-2:4317;
    server collector-3:4317;
}

server {
    listen 4317 http2;
    location / {
        grpc_pass grpc://otel_collectors;
        grpc_next_upstream error timeout invalid_header http_500;
        grpc_connect_timeout 2;
    }
}
```

### Gateway Collector Config

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    send_batch_size: 10240
    timeout: 3s

exporters:
  otlp_grpc/jaeger:
    endpoint: jaeger.example.com:4317
    tls:
      ca_file: /path/to/ca.pem
  prometheusremotewrite:
    endpoint: 'http://prometheus:9090/api/v1/write'

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_grpc/jaeger]
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheusremotewrite]
```

## Two-Tier Architecture (Gateway + Tail Sampling)

First tier collectors use load-balancing exporter to route to second tier where tail sampling is applied.

```yaml
# First-tier collector config
exporters:
  loadbalancing:
    protocol:
      otlp:
        tls:
          insecure: true
    resolver:
      dns:
        hostname: second-tier-collectors.example.com

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [loadbalancing]
```

```yaml
# Second-tier collector config (receives from first tier)
processors:
  tail_sampling:
    policies:
      - name: errors-only
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: slow-traces
        type: latency
        latency:
          threshold_ms: 2000

exporters:
  otlp_grpc/jaeger:
    endpoint: jaeger.example.com:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling]
      exporters: [otlp_grpc/jaeger]
```

## Hybrid Pattern (Agent + Gateway)

Agents collect from local apps and forward to gateway collectors. Gateways aggregate and export to backends.

```
[App Pods] → [Agent Collector (DaemonSet)] → [Gateway Collector (Deployment)] → [Backends]
```

### Agent Config
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch: {}

exporters:
  otlp/gateway:
    endpoint: gateway-collector:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/gateway]
```

### Gateway Config
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch: {}

exporters:
  otlp_grpc/jaeger:
    endpoint: jaeger.example.com:4317
  prometheusremotewrite:
    endpoint: 'http://prometheus:9090/api/v1/write'

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_grpc/jaeger]
    metrics:
      receivers: [otlp, hostmetrics]
      processors: [batch]
      exporters: [prometheusremotewrite]
```

## Kubernetes Deployment Example (Gateway)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otel-collector-gateway
  template:
    metadata:
      labels:
        app: otel-collector-gateway
    spec:
      serviceAccountName: otel-collector
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:1.56.0
          args: ["--config=/conf/collector-config.yaml"]
          ports:
            - containerPort: 4317
            - containerPort: 8888
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: otel-gateway
spec:
  selector:
    app: otel-collector-gateway
  ports:
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: metrics
      port: 8888
      targetPort: 8888
```
