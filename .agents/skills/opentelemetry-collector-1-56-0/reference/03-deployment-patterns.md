# Deployment Patterns

## Overview

The OpenTelemetry Collector is a single binary that can be deployed in different
ways for different use cases. The two primary patterns are **agent** and
**gateway**, with a hybrid **agent-to-gateway** pattern combining both.

## Agent Deployment Pattern

In the agent pattern, each application or host runs its own Collector instance
that receives telemetry locally and exports to one or more backends.

### Architecture

```
Application ──OTLP──→ [Collector Agent] ──→ Backend 1
                                     ──→ Backend 2
```

The Collector runs alongside the application — as a sidecar container, DaemonSet
pod, or local process on the same host. Each instrumented SDK or downstream
component sends telemetry to its local Collector.

### Example Configuration

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlp/jaeger:
    endpoint: https://jaeger.example.com:4317
    sending_queue:
      queue_size: 1000
    retry_on_failure:
      max_elapsed_time: 5m
  prometheusremotewrite:
    endpoint: https://prw.example.com/v1/api/remote_write
    sending_queue:
      queue_size: 1000

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      exporters: [file]
```

### Application Configuration

Set the OTLP endpoint in the application's SDK:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

Or configure it programmatically in the SDK.

### Trade-offs

**Pros:**
- Straightforward to get started
- Clear one-to-one mapping between application and Collector
- Each agent handles retries, batching, and encryption independently
- Applications offload data quickly to local Collector

**Cons:**
- Limited scalability for large teams and infrastructure
- Inflexible for complex or evolving deployments
- Each agent needs its own backend credentials
- Configuration changes require updates across all agents

## Gateway Deployment Pattern

In the gateway pattern, applications send telemetry to a central OTLP endpoint
provided by one or more Collector instances running as a standalone service.
Typically one endpoint per cluster, data center, or region.

### Architecture

```
App 1 ──┐
App 2 ──┼──OTLP──→ [Load Balancer] ──→ [Gateway Collector 1] ──→ Backend
App 3 ──┘                               [Gateway Collector 2] ──→ Backend
                                        [Gateway Collector 3]
```

### Load Balancing with NGINX

```nginx
upstream collector4317 {
    server collector1:4317;
    server collector2:4317;
    server collector3:4317;
}

upstream collector4318 {
    server collector1:4318;
    server collector2:4318;
    server collector3:4318;
}

server {
    listen 4317 http2;
    location / {
        grpc_pass grpc://collector4317;
        grpc_next_upstream error timeout invalid_header http_500;
        grpc_connect_timeout 2s;
        grpc_set_header Host $host;
        grpc_set_header X-Real-IP $remote_addr;
        grpc_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

server {
    listen 4318;
    location / {
        proxy_pass http://collector4318;
        proxy_next_upstream error timeout invalid_header http_500;
        proxy_connect_timeout 2s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Load-Balancing Exporter

For cases where telemetry must reach specific Collectors (e.g., tail-based
sampling), use the load-balancing exporter with a two-tier setup:

```yaml
exporters:
  loadbalancing:
    protocol: grpc
    resolver:
      dns:
        hostname: collector-headless.default.svc.cluster.local
        port: 4317
    routing_key: traceID

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [loadbalancing]
```

The `routing_key` determines how spans are distributed:

- **traceID** — all spans for a trace go to the same downstream Collector
  (required for tail-based sampling)
- **service** — all spans for a service go to the same Collector
  (useful for spanmetrics connector)

### Trade-offs

**Pros:**
- Centralized configuration and credential management
- Better scalability with load balancing
- Easier to apply processing transformations centrally
- Single point for monitoring and observability of the pipeline

**Cons:**
- Requires load balancer or service mesh
- Potential single point of failure (mitigated by multiple instances)
- Network hop adds latency
- More complex initial setup

## Agent-to-Gateway Pattern

Combines agent and gateway patterns. Applications send to local agents, which
forward to a central gateway for aggregation and export.

### Architecture

```
App ──→ [Agent Collector] ──OTLP──→ [Gateway Collector] ──→ Backend
                                         [Gateway Collector] ──→ Backend
```

### Agent Configuration

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  otlp/gateway:
    endpoint: gateway-collector:4317
    tls:
      insecure: false
    sending_queue:
      queue_size: 5000
    retry_on_failure:
      max_elapsed_time: 10m

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/gateway]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/gateway]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/gateway]
```

### Gateway Configuration

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  otlp/jaeger:
    endpoint: https://jaeger.backend:4317
  prometheusremotewrite:
    endpoint: https://prometheus.backend:443/api/v1/write

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheusremotewrite]
```

### Trade-offs

**Pros:**
- Agents handle local retries and buffering
- Gateway provides centralized processing and export
- Tail-based sampling works correctly at the gateway
- Isolation between collection and export concerns

**Cons:**
- Two tiers to manage and monitor
- More complex configuration
- Additional network hop between agent and gateway

## No Collector Pattern

For simple setups, applications can send telemetry directly to backends without
a Collector. This is suitable for:

- Development and testing
- Small-scale environments
- Quick prototyping with OpenTelemetry

**Trade-offs:**
- No retries, batching, or encryption handling
- Each application needs backend-specific configuration
- Limited scalability
- No data transformation or enrichment

## Multi-Backend Scenarios

The Collector can export to multiple backends simultaneously from a single
pipeline:

```yaml
exporters:
  otlp/jaeger:
    endpoint: https://jaeger.example.com:4317
  otlp/datadog:
    endpoint: https://datadog.example.com:4318
    headers:
      DD-API-KEY: "${DD_API_KEY}"
  prometheusremotewrite:
    endpoint: https://prometheus.example.com/v1/api/remote_write

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp/jaeger, otlp/datadog]
    metrics:
      receivers: [otlp]
      exporters: [prometheusremotewrite, otlp/datadog]
```

## Cross-Environment Considerations

When deploying across multiple environments (dev, staging, production):

- Use environment variable substitution for environment-specific values
- Separate configuration files per environment
- Use the `--config` flag with multiple files for modular configuration
- Consider using OpAMP for centralized configuration management
- Apply different processor configurations per environment (e.g., higher
  sampling rates in dev)

## Kubernetes Deployment

In Kubernetes, common approaches include:

- **DaemonSet** — one Collector per node (agent pattern)
- **Deployment** — scalable set of Collectors (gateway pattern)
- **Sidecar** — Collector container alongside application pod
- **OpenTelemetry Operator** — CRD-based management of Collector deployments
- **Helm chart** — templated deployment with configurable values

The Kubernetes distribution (`otelcol-k8s`) includes components specific to
Kubernetes environments: k8s_cluster receiver, k8s_events receiver,
k8sobjects receiver, kubeletstats receiver, etc.
