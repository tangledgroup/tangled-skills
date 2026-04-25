# Processors Reference

## Batch Processor

Batches telemetry for efficient export. **Highly recommended** in production.

```yaml
processors:
  batch:
    send_batch_size: 8192
    timeout: 5s
    send_batch_max_size: 16384
```

- `send_batch_size`: Target batch size (default: 8192)
- `timeout`: Max time before sending partial batch (default: 200ms)
- `send_batch_max_size`: Hard limit on batch size (default: 0 = unlimited)

## Memory Limiter Processor

Protects collector from OOM by dropping data when memory exceeds limits.

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 4000       # Max memory before dropping data
    spike_limit_mib: 800   # Allowed spike above limit
```

## Attributes Processor

Manipulates attributes on spans, metrics, and logs.

```yaml
processors:
  attributes:
    trace:
      actions:
        - key: environment
          value: production
          action: insert
        - key: db.statement
          action: delete
        - key: user.email
          action: hash
        - key: service.version
          action: uppercase
```

Actions: `insert`, `upsert`, `update`, `delete`, `hash`, `md5`, `sha256`, `lowercase`, `uppercase`.

## Filter Processor

Filters telemetry by CEL expressions.

```yaml
processors:
  filter:
    error_mode: ignore
    traces:
      span:
        - 'attributes["container.name"] == "app_container_1"'
        - 'resource.attributes["host.name"] == "localhost"'
        - 'name == "healthcheck"'
      spanevent:
        - 'IsMatch(name, ".*grpc.*")'
    metrics:
      metric:
        - 'name == "my.metric"'
        - 'type == METRIC_DATA_TYPE_HISTOGRAM'
      datapoint:
        - 'resource.attributes["service.name"] == "my_service"'
    logs:
      log_record:
        - 'IsMatch(body, ".*password.*")'
        - 'severity_number < SEVERITY_NUMBER_WARN'
```

## Resource Processor

Adds, modifies, or deletes resource attributes.

```yaml
processors:
  resource:
    attributes:
      - key: cloud.zone
        value: us-east-1
        action: upsert
      - key: k8s.cluster.name
        from_attribute: k8s-cluster
        action: insert
      - key: redundant.attribute
        action: delete
```

## Transform Processor

Transforms telemetry using CEL expressions.

```yaml
processors:
  transform:
    error_mode: ignore
    trace_statements:
      - context: span
        select: resource.attributes["k8s.namespace.name"]
        actions:
          - key: deployment.namespace
            value: "my-namespace"
            action: insert
      - context: span
        select: name
        conditions:
          - 'name == "/api/v1/users"'
        set:
          name: "users.getUsers"

    metric_statements:
      - context: datapoint
        select: resource.attributes["service.name"]
        actions:
          - key: service.tier
            value: "backend"
            action: insert

    log_statements:
      - context: logRecord
        select: body
        conditions:
          - 'IsMatch(body, ".*error.*")'
        set:
          severity_text: "ERROR"
```

## Probabilistic Sampler Processor

Samples traces based on a percentage.

```yaml
processors:
  probabilistic_sampler:
    hash_seed: 0           # Default 0; set to non-zero for custom distribution
    sampling_percentage: 15 # Percentage of traces to keep
```

## K8s Attributes Processor

Enriches telemetry with Kubernetes metadata (requires RBAC).

```yaml
processors:
  k8sattributes:
    filter:
      node_name_from: envvar
    passthrough: false
    pod_association:
      - sources:
          - source_type: resource_attribute
            attributes:
              - name: k8s.pod.ip
          - source_type: resource_attribute
            attributes:
              - name: k8s.pod.uid
```

## Tail Sampling Processor

Samples entire traces based on conditions evaluated at the end of a trace.

```yaml
processors:
  tail_sampling:
    policies:
      - name: error-policy
        type: status_code
        status_code:
          status_codes: [ERROR, UNAUTHENTICATED]
      - name: slow-policy
        type: latency
        latency:
          threshold_ms: 5000
      - name: regex-policy
        type: string
        string:
          attributes:
            - key: http.url
              value: ".*admin.*"
          values: ["true"]
    max_total_spans: 100000
    policy_wait_time: 5s
```

## Resilient Exporter Helper

Not a processor, but the built-in retry/queue mechanism for exporters.

```yaml
exporters:
  otlp_grpc:
    endpoint: backend:4317
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
