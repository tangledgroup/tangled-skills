# OpenTelemetry Integration

redis-py 7.4 includes native OpenTelemetry support for comprehensive metrics collection without external instrumentation packages.

## Installation

Install OpenTelemetry dependencies:

```bash
pip install "redis[otel]"

# Includes:
# - opentelemetry-api>=1.39.1
# - opentelemetry-sdk>=1.39.1
# - opentelemetry-exporter-otlp-proto-http>=1.39.1
```

## Basic Setup

Initialize OpenTelemetry observability at application startup:

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from redis.observability import get_observability_instance, OTelConfig

# 1. Set up OpenTelemetry MeterProvider
exporter = OTLPMetricExporter(
    endpoint="http://localhost:4318/v1/metrics",
    headers={"api-key": "your-api-key"}
)
reader = PeriodicExportingMetricReader(
    exporter=exporter,
    export_interval_millis=10000  # Export every 10 seconds
)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# 2. Initialize redis-py observability
otel = get_observability_instance()
otel.init(OTelConfig())

# 3. Use Redis as usual - metrics collected automatically
import redis
r = redis.Redis(host='localhost', port=6379)
r.set('key', 'value')  # Metrics collected automatically
r.get('key')

# 4. Shutdown observability at application exit
otel.shutdown()
```

## Configuration Options

Configure metric collection with `OTelConfig`:

```python
from redis.observability import OTelConfig, MetricGroup

config = OTelConfig(
    # Metric groups to enable (default: CONNECTION_BASIC | RESILIENCY)
    metric_groups=[
        MetricGroup.CONNECTION_BASIC,    # Connection creation time, relaxed timeout
        MetricGroup.CONNECTION_ADVANCED, # Connection wait time, timeouts, closed connections
        MetricGroup.COMMAND,             # Command execution duration
        MetricGroup.RESILIENCY,          # Error counts, maintenance notifications
        MetricGroup.PUBSUB,              # PubSub message counts
        MetricGroup.STREAMING,           # Stream message lag
        MetricGroup.CSC,                 # Client Side Caching metrics
    ],

    # Filter which commands to track
    include_commands=['GET', 'SET', 'HGET', 'HSET'],  # Only track these
    # OR
    exclude_commands=['DEBUG', 'SLOWLOG', 'INFO'],    # Track all except these

    # Privacy controls
    hide_pubsub_channel_names=True,  # Don't include channel names in metrics
    hide_stream_names=True,          # Don't include stream names in metrics

    # Histogram bucket customization
    buckets_operation_duration=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1],
    buckets_connection_create_time=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],
    buckets_connection_wait_time=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
    buckets_stream_processing_duration=[0.001, 0.01, 0.1, 1, 10],
)

otel = get_observability_instance()
otel.init(config)
```

## Metric Groups

Available metric groups and what they measure:

### CONNECTION_BASIC

Basic connection metrics:

```python
config = OTelConfig(metric_groups=[MetricGroup.CONNECTION_BASIC])

# Metrics collected:
# - db.client.connection.create_time (histogram): Time to create new connection
# - redis.client.connection.relaxed_timeout (up_down_counter): Relaxed timeout events
# - redis.client.connection.handoff (counter): Connection handoff events
```

### CONNECTION_ADVANCED

Advanced connection metrics:

```python
config = OTelConfig(metric_groups=[MetricGroup.CONNECTION_ADVANCED])

# Metrics collected:
# - db.client.connection.wait_time (histogram): Time to obtain connection from pool
# - db.client.connection.timeouts (counter): Number of connection timeouts
# - db.client.connection.count (observable_gauge): Current number of connections
# - redis.client.connection.closed (counter): Total closed connections
```

### COMMAND

Command execution metrics:

```python
config = OTelConfig(metric_groups=[MetricGroup.COMMAND])

# Metrics collected:
# - db.client.operation.duration (histogram): Command execution duration
#   Attributes: db.client.name, db.operation.name, error.type

# Example: Track only specific commands
config = OTelConfig(
    metric_groups=[MetricGroup.COMMAND],
    include_commands=['GET', 'SET', 'HGETALL', 'HMSET']
)
```

### RESILIENCY

Error and resiliency metrics:

```python
config = OTelConfig(metric_groups=[MetricGroup.RESILIENCY])

# Metrics collected:
# - redis.client.errors (counter): Error counts by error type
#   Attributes: error.type, error.message
# - redis.client.maintenance.notifications (counter): Server maintenance notifications
```

### PUBSUB

Pub/Sub messaging metrics:

```python
config = OTelConfig(
    metric_groups=[MetricGroup.PUBSUB],
    hide_pubsub_channel_names=True  # Privacy: don't expose channel names
)

# Metrics collected:
# - redis.client.pubsub.messages (counter): Published and received messages
#   Attributes: pubsub.type (publish/receive), pubsub.channel (if not hidden)
```

### STREAMING

Stream processing metrics:

```python
config = OTelConfig(
    metric_groups=[MetricGroup.STREAMING],
    hide_stream_names=True  # Privacy: don't expose stream names
)

# Metrics collected:
# - redis.client.stream.lag (histogram): End-to-end message lag
#   Attributes: stream.name (if not hidden), consumer.group
```

### CSC (Client-Side Caching)

Client-side caching metrics:

```python
config = OTelConfig(metric_groups=[MetricGroup.CSC])

# Metrics collected:
# - redis.client.csc.requests (counter): Cache requests with hit/miss result
#   Attributes: csc.result (hit/miss)
# - redis.client.csc.evictions (counter): Cache evictions
# - redis.client.csc.network_saved (counter): Bytes saved by caching
# - redis.client.csc.items (observable_gauge): Current cache size
```

## Command Filtering

Control which commands are tracked:

```python
from redis.observability import OTelConfig, MetricGroup

# Track only specific commands
config = OTelConfig(
    metric_groups=[MetricGroup.COMMAND],
    include_commands=['GET', 'SET', 'HGET', 'HSET', 'INCR', 'DECR']
)

# Track all except noisy/debug commands
config = OTelConfig(
    metric_groups=[MetricGroup.COMMAND],
    exclude_commands=['DEBUG', 'SLOWLOG', 'INFO', 'CLIENT LIST']
)

# No filtering (track all commands)
config = OTelConfig(metric_groups=[MetricGroup.COMMAND])
```

## Privacy Controls

Hide sensitive information in metrics:

```python
from redis.observability import OTelConfig, MetricGroup

config = OTelConfig(
    metric_groups=[MetricGroup.PUBSUB, MetricGroup.STREAMING],
    
    # Don't include channel names in PubSub metrics
    hide_pubsub_channel_names=True,
    
    # Don't include stream names in streaming metrics
    hide_stream_names=True
)

# Without privacy controls (channel/stream names appear as metric attributes):
# redis.client.pubsub.messages{channel="user:123:events", type="publish"} = 42

# With privacy controls (generic names used):
# redis.client.pubsub.messages{channel="(hidden)", type="publish"} = 42
```

## Context Manager Usage

Use context manager for automatic cleanup:

```python
from redis.observability import get_observability_instance, OTelConfig
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

# Set up meter provider
provider = MeterProvider()  # Configured with exporters
metrics.set_meter_provider(provider)

otel = get_observability_instance()

# Use context manager for automatic shutdown
with otel.get_provider_manager():
    # Initialize observability
    otel.init(OTelConfig())
    
    # Use Redis - metrics collected automatically
    import redis
    r = redis.Redis(host='localhost', port=6379)
    
    for i in range(1000):
        r.set(f'key:{i}', f'value:{i}')
        r.get(f'key:{i}')

# Metrics automatically flushed, resources cleaned up on exit
```

## Exporter Configuration

Configure different metric exporters:

### OTLP HTTP Exporter

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

exporter = OTLPMetricExporter(
    endpoint="http://otel-collector:4318/v1/metrics",
    headers={"api-key": "your-api-key"},
    timeout=10  # Timeout in seconds
)

reader = PeriodicExportingMetricReader(
    exporter=exporter,
    export_interval_millis=10000,
    max_export_batch_size=1000,
    max_export_timeout_millis=5000
)
```

### OTLP gRPC Exporter

```python
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

exporter = OTLPMetricExporter(
    endpoint="otel-collector:4317",
    insecure=True,  # Use TLS=False for local development
    headers={"api-key": "your-api-key"}
)

reader = PeriodicExportingMetricReader(exporter=exporter)
```

### Console Exporter (Development)

```python
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter

# Print metrics to console (useful for debugging)
exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(exporter=exporter)
```

### Multiple Exporters

Export to multiple destinations:

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter

# Export to both OTLP and console
otel_exporter = OTLPMetricExporter(endpoint="http://otel:4318/v1/metrics")
console_exporter = ConsoleMetricExporter()

otel_reader = PeriodicExportingMetricReader(exporter=otel_exporter)
console_reader = PeriodicExportingMetricReader(exporter=console_exporter)

provider = MeterProvider(metric_readers=[otel_reader, console_reader])
metrics.set_meter_provider(provider)
```

## Metrics Attributes

Metrics include contextual attributes for filtering and analysis:

### Connection Metrics Attributes

```python
# db.client.connection.create_time
# Attributes:
# - db.system: "redis"
# - net.peer.name: "localhost"
# - net.peer.port: 6379

# db.client.connection.wait_time
# Attributes:
# - db.system: "redis"
# - connection.pool.size: 10
```

### Command Metrics Attributes

```python
# db.client.operation.duration
# Attributes:
# - db.system: "redis"
# - db.name: "0" (database number)
# - db.operation.name: "GET", "SET", etc.
# - error.type: None or error class name
# - error.message: Error message (if error occurred)

# Example metric:
# db.client.operation.duration{db.system="redis", db.operation.name="GET", error.type=None} = 0.001
```

### Error Metrics Attributes

```python
# redis.client.errors
# Attributes:
# - error.type: "ConnectionError", "TimeoutError", etc.
# - error.message: Error message (truncated)
# - db.system: "redis"
```

### PubSub Metrics Attributes

```python
# redis.client.pubsub.messages
# Attributes:
# - pubsub.type: "publish" or "receive"
# - pubsub.channel: Channel name (or "(hidden)" if privacy enabled)
```

### Stream Metrics Attributes

```python
# redis.client.stream.lag
# Attributes:
# - stream.name: Stream name (or "(hidden)" if privacy enabled)
# - consumer.group: Consumer group name
```

## Monitoring and Alerting

### Prometheus Exporter

Export metrics in Prometheus format:

```python
from opentelemetry.exporter.prometheus import PrometheusMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import start_http_server

# Start Prometheus scrape endpoint
start_http_server(8000)

# Export to Prometheus
exporter = PrometheusMetricExporter()
reader = PeriodicExportingMetricReader(exporter=exporter)

provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

otel = get_observability_instance()
otel.init(OTelConfig())

# Prometheus can now scrape http://localhost:8000/metrics
```

### Common Alerting Thresholds

Example alerting rules for Redis metrics:

```yaml
# Example Prometheus alerting rules
groups:
  - name: redis
    rules:
      # High command latency
      - alert: RedisHighLatency
        expr: histogram_quantile(0.99, db_client_operation_duration_seconds_bucket) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 99th percentile latency > 100ms"

      # High error rate
      - alert: RedisHighErrorRate
        expr: rate(redis_client_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Redis error rate > 1%"

      # Connection pool exhaustion
      - alert: RedisConnectionPoolExhausted
        expr: db_client_connection_count / on() redis_client_connection_max == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis connection pool at capacity"

      # High connection wait time
      - alert: RedisHighConnectionWaitTime
        expr: histogram_quantile(0.95, db_client_connection_wait_time_seconds_bucket) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis connection wait time (p95) > 10ms"
```

## Troubleshooting

### Verify Metrics Are Being Collected

```python
from redis.observability import get_observability_instance, OTelConfig
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry import metrics

# Use console exporter to see metrics
exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(exporter=exporter, export_interval_millis=5000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

otel = get_observability_instance()
otel.init(OTelConfig(metric_groups=[MetricGroup.COMMAND, MetricGroup.CONNECTION_BASIC]))

import redis
r = redis.Redis(host='localhost', port=6379)

# Perform operations - metrics printed to console every 5 seconds
for i in range(100):
    r.set(f'key:{i}', f'value:{i}')
    r.get(f'key:{i}')

# Wait for final export
import time
time.sleep(6)

otel.shutdown()
```

### Check Configuration

```python
from redis.observability import get_observability_instance

otel = get_observability_instance()

# Check if initialized
if otel.is_initialized:
    print("OpenTelemetry is initialized")
    config = otel.get_config()
    print(f"Metric groups: {config.metric_groups}")
else:
    print("OpenTelemetry not initialized")
```

### Common Issues

**Metrics not appearing:**
1. Verify `otel.init()` was called before creating Redis clients
2. Check metric groups include desired metrics
3. Ensure exporter is configured correctly
4. Check command filtering isn't excluding all commands

**High overhead:**
1. Reduce number of metric groups enabled
2. Use command filtering to track only important commands
3. Increase export interval
4. Enable privacy controls to reduce attribute cardinality

**Missing attributes:**
1. Verify metric group is enabled for desired attributes
2. Check privacy controls aren't hiding attributes
3. Ensure Redis operation actually triggers the metric

## Comparison: Native vs External Instrumentation

### Native Integration (Recommended)

```python
from redis.observability import get_observability_instance, OTelConfig

otel = get_observability_instance()
otel.init(OTelConfig())

# Metrics collected automatically for all Redis operations
import redis
r = redis.Redis()
```

**Advantages:**
- No monkey-patching required
- Comprehensive metric coverage
- Lower overhead (instrumented at source)
- Supports all metric groups including CSC and streaming
- Maintained by Redis team

### External Instrumentation (Alternative)

```python
from opentelemetry.instrumentation.redis import RedisInstrumentor

RedisInstrumentor().instrument()

import redis
r = redis.Redis()
```

**Limitations:**
- Uses monkey-patching
- May miss some metrics
- Higher overhead
- Limited to basic metrics
- Not recommended for production with redis-py 7.4+
