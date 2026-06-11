# OpenTelemetry Integration

## Native Metrics (Recommended)

redis-py includes built-in OpenTelemetry metrics collection. Initialize once at application startup — all Redis clients automatically collect metrics:

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# 1. Set up OpenTelemetry MeterProvider
exporter = OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
reader = PeriodicExportingMetricReader(exporter=exporter, export_interval_millis=10000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# 2. Initialize redis-py observability
from redis.observability import get_observability_instance, OTelConfig
otel = get_observability_instance()
otel.init(OTelConfig())

# 3. Use Redis as usual — metrics collected automatically
import redis
r = redis.Redis(host='localhost', port=6379)
r.set('key', 'value')
r.get('key')

# 4. Shutdown at application exit
otel.shutdown()
```

## Configuration Options

`OTelConfig` provides fine-grained control:

```python
from redis.observability import OTelConfig, MetricGroup

config = OTelConfig(
    # Metric groups to enable (default: CONNECTION_BASIC | RESILIENCY)
    metric_groups=[
        MetricGroup.CONNECTION_BASIC,   # Connection creation time, relaxed timeout
        MetricGroup.CONNECTION_ADVANCED,  # Wait time, timeouts, closed connections
        MetricGroup.COMMAND,             # Command execution duration
        MetricGroup.RESILIENCY,          # Error counts, maintenance notifications
        MetricGroup.PUBSUB,              # PubSub message counts
        MetricGroup.STREAMING,           # Stream message lag
        MetricGroup.CSC,                 # Client Side Caching metrics
    ],

    # Filter which commands to track
    include_commands=['GET', 'SET', 'HGET'],   # Only these
    # OR
    exclude_commands=['DEBUG', 'SLOWLOG'],     # All except these

    # Privacy controls
    hide_pubsub_channel_names=True,
    hide_stream_names=True,
)

otel.init(config)
```

## Metric Groups

- **CONNECTION_BASIC** — Connection creation time, relaxed timeout
- **CONNECTION_ADVANCED** — Connection wait time, timeouts, closed connections
- **COMMAND** — Command execution duration
- **RESILIENCY** — Error counts, maintenance notifications
- **PUBSUB** — PubSub message counts
- **STREAMING** — Stream message lag
- **CSC** — Client Side Caching metrics

Default metric groups: `CONNECTION_BASIC` and `RESILIENCY`.
