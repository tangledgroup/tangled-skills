# Scaling and Resiliency

## Scaling Strategies

### What to Scale

Different telemetry signal types have different scaling characteristics:

- **Logs** — typically high volume, stateless receivers can scale horizontally
- **Metrics** — scraping requires coordination (which scraper hits which target)
- **Traces** — tail-based sampling requires all spans for a trace to reach the
  same Collector instance

Consider your workload to determine scaling strategy:

- Elastic workloads with peak hours may need auto-scaling
- Steady-state workloads benefit from right-sizing
- Mixed signal types may need separate Collector clusters per signal

### When to Scale

Monitor these internal metrics to determine scaling needs:

**Memory pressure:**
- `otelcol_processor_refused_spans` — spans rejected by memory_limiter
- `otelcol_processor_refused_metric_points` — metric points rejected
- `otelcol_processor_refused_log_records` — log records rejected

If data is being refused too frequently, scale up the Collector cluster. Scale
down when memory consumption across nodes is significantly below the limit.

**Queue pressure:**
- `otelcol_exporter_queue_size` — current number of batches in queue
- `otelcol_exporter_queue_capacity` — maximum queue capacity
- `otelcol_exporter_enqueue_failed_spans` — spans dropped due to full queue

When `queue_size` approaches `queue_capacity`, consider scaling up.

### When NOT to Scale

Adding more Collectors is not always the right answer:

- If the backend is the bottleneck, adding Collectors increases pressure on it
- If queues are full because of slow export, adding workers may not help
- Check backend rate limits and capacity before scaling collectors
- Consider reducing data volume (sampling, filtering) instead

### How to Scale

**Stateless receivers** (OTLP, Jaeger, Zipkin):
- Scale horizontally behind a load balancer
- Each instance independently receives and processes data
- Use Kubernetes HPA or manual replica adjustments

**Stateful components** (scrapers, tail sampling):
- Prometheus receiver: use workload splitting to avoid duplicate scrapes
- Tail sampling: ensure all spans for a trace reach the same instance using
  load-balancing exporter with `routing_key: traceID`
- Kubernetes cluster receiver: use leader election or split by namespace

## Resiliency Mechanisms

### Sending Queue (In-Memory Buffering)

The sending queue is the primary resilience mechanism built into exporters. It
buffers data in memory when the backend is unavailable.

**How it works:**
1. Exporter attempts to send data to the endpoint
2. If the endpoint is unavailable, data is added to the in-memory queue
3. Collector retries with exponential backoff and jitter
4. Default retry duration: 5 minutes
5. Default queue size: 1000 batches

**Configuration:**

```yaml
exporters:
  otlp:
    endpoint: backend:4317
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 10m
```

**Data loss scenarios:**
- Queue fills up (endpoint unavailable too long) → incoming data is dropped
- Retry timeout expires (default 5 minutes) → oldest data in queue is dropped
- Collector crashes → all in-memory queue data is lost

### Persistent Storage (Write-Ahead Log)

To protect against Collector crashes, enable persistent storage using the
`file_storage` extension:

```yaml
extensions:
  file_storage:
    directory: /var/lib/otelcol/storage

exporters:
  otlp:
    endpoint: backend:4317
    sending_queue:
      storage:
        id: file_storage
      queue_size: 5000
    retry_on_failure:
      max_elapsed_time: 10m

service:
  extensions: [file_storage]
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp]
```

**How it works:**
1. Data is written to a WAL on disk before export attempts
2. If the Collector crashes, data persists on disk
3. On restart, the Collector reads the WAL and resumes sending

**Data loss scenarios:**
- Disk failure or out-of-space
- Endpoint unavailable beyond retry limits after restart
- Guarantees are not as strong as dedicated message queues

### Message Queues

For stronger durability guarantees, use external message queues:

- **Kafka** — high-throughput distributed queue
- **RabbitMQ** — reliable message broker
- **NATS** — lightweight messaging system

```yaml
exporters:
  kafka:
    brokers: [kafka1:9092, kafka2:9092]
    topic:
      resolve_available: false
      logs: otel-logs
      traces: otel-traces
      metrics: otel-metrics
```

## Circumstances of Data Loss

Understanding when data loss can occur:

| Scenario | In-Memory Queue | Persistent Storage | Message Queue |
|----------|----------------|-------------------|---------------|
| Backend temporarily down | Protected (within queue size and retry time) | Protected | Protected |
| Collector crash | Lost | Protected | Protected |
| Disk failure | N/A | Lost | Protected (if replicated) |
| Queue overflow | Lost | Lost | Depends on queue config |
| Retry timeout exceeded | Lost | Lost | Protected (redelivery) |

## Recommendations for Preventing Data Loss

1. **Always enable sending queues** for remote exporters
2. **Use persistent storage** (WAL) for critical pipelines
3. **Monitor queue metrics** — alert when queue_size approaches capacity
4. **Set appropriate retry limits** based on expected backend downtime
5. **Size queues based on available memory** — avoid OOM kills
6. **Use memory_limiter processor** as the first processor in each pipeline
7. **Configure graceful shutdown** to flush queues on restart
8. **For highest durability**, use external message queues

### Memory Limiter Configuration

The `memory_limiter` processor protects the Collector from running out of memory:

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128
```

- `limit_mib` — hard memory limit (MiB)
- `spike_limit_mib` — additional buffer for memory spikes
- `check_interval` — how often to check memory usage

Place `memory_limiter` as the first processor in every pipeline. When memory
approaches the limit, it blocks new data from entering the pipeline and
increments the refused signals counter.

## Backpressure Handling

The Collector handles backpressure through:

1. **Memory limiter** — rejects data when memory is high
2. **Sending queues** — buffers data when export is slow
3. **Export worker count** — controls parallelism of export operations
4. **Retry with backoff** — reduces pressure on slow backends

Monitor backpressure indicators:

- `otelcol_processor_refused_*` metrics
- `otelcol_exporter_queue_size` vs `otelcol_exporter_queue_capacity`
- `otelcol_exporter_enqueue_failed_*` metrics
- Collector CPU and memory usage via internal telemetry

## High Availability

For production deployments:

- Deploy multiple Collector instances behind a load balancer
- Use health_check extension for liveness probes
- Configure sending queues with persistent storage on each instance
- Monitor all instances through internal telemetry
- Plan for graceful degradation when instances are removed
- Use Kubernetes with pod disruption budgets for managed environments
