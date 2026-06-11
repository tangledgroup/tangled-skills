# Metrics

## Overview

Logfire collects metrics from your application and sends them to a metrics backend. Metrics record numerical values where you want to see aggregation over time rather than individual values.

The `metrics` table contains pre-aggregated numerical data, usually more efficient to query than `records`. Query it directly using SQL in the Explore view, Dashboards, Alerts, or the API.

## System Metrics

Enable system metrics via the [System Metrics integration](integrations/system-metrics.md):

```python
import logfire
logfire.configure()
logfire.instrument_system_metrics()
```

## Counter

Measure frequency or occurrence of events (exceptions caught, requests received, items processed).

```python
import logfire

counter = logfire.metric_counter(
    name='exceptions',
    unit='1',
    description='Number of exceptions caught',
)

try:
    raise Exception('oops')
except Exception:
    counter.add(1)
```

## Histogram

Measure distribution of values (request duration, file size, list length).

```python
import logfire

histogram = logfire.metric_histogram(
    'request_duration',
    unit='ms',
    description='Duration of requests',
)

for duration in [10, 20, 30, 40, 50]:
    histogram.record(duration)
```

## Up-Down Counter

Track values that can increase or decrease (active connections, queue items, users online).

```python
import logfire

active_users = logfire.metric_up_down_counter(
    'active_users',
    unit='1',
    description='Number of active users',
)

def user_logged_in():
    active_users.add(1)

def user_logged_out():
    active_users.add(-1)
```

## Gauge

Measure current value of a state (temperature, memory usage, active connections).

```python
import logfire

temperature = logfire.metric_gauge(
    'temperature',
    unit='C',
    description='Temperature',
)

def set_temperature(value: float):
    temperature.set(value)
```

## Callback Metrics

Callback (observable) metrics are automatically emitted every 60 seconds in a background thread.

### Counter Callback

```python
from typing import Iterable
from opentelemetry.metrics import CallbackOptions, Observation
import logfire

def cpu_time_callback(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    with open('/proc/stat') as procstat:
        procstat.readline()  # skip header
        for line in procstat:
            if not line.startswith('cpu'):
                break
            cpu, user_time, nice_time, system_time = line.split()
            observations.append(Observation(int(user_time) // 100, {'cpu': cpu, 'state': 'user'}))
            observations.append(Observation(int(system_time) // 100, {'cpu': cpu, 'state': 'system'}))
    return observations

logfire.metric_counter_callback(
    'system.cpu.time',
    unit='s',
    callbacks=[cpu_time_callback],
    description='CPU time',
)
```

### Gauge Callback

Use `logfire.metric_gauge_callback()` with callback functions for automatically observed gauge values.

## Metrics in Spans

Logfire supports recording metrics within spans, allowing correlation between trace data and metric data. This is useful for adding contextual measurements to specific operations.
