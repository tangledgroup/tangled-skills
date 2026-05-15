---
name: python-prometheus-0-25-0
description: Official Prometheus Python client library v0.25.0 for instrumenting Python applications with metrics. Provides Counter, Gauge, Summary, Histogram, Info, and Enum metric types; HTTP/WSGI/ASGI exporters; framework integrations (Flask, Django, FastAPI, AIOHTTP, Twisted); Pushgateway support; multiprocess mode for Gunicorn; custom collectors; and Graphite bridge. Use when adding Prometheus metrics to Python applications, exposing metrics endpoints, or integrating with web frameworks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - prometheus
  - python
  - metrics
  - instrumentation
  - monitoring
  - observability
  - client-python
category: library
external_references:
  - https://github.com/prometheus/client_python/tree/v0.25.0
  - https://prometheus.github.io/client_python/
---

# Prometheus Python Client 0.25.0

## Overview

The official Prometheus client library for Python. Instrument applications with metrics that Prometheus scrapes via HTTP. Six metric types cover counting, gauging, distribution tracking, and metadata exposition. The library provides built-in HTTP servers, WSGI/ASGI adapters, and framework-specific integrations for serving metrics at `/metrics`.

## When to Use

- Adding Prometheus metrics to a Python application
- Exposing metrics endpoints in Flask, Django, FastAPI, AIOHTTP, or Twisted
- Instrumenting request latency, error rates, queue depths, or custom business metrics
- Running batch jobs that push metrics via Pushgateway
- Multiprocess deployments with Gunicorn workers
- Building custom collectors for external data sources

## Core Concepts

**Metric types** — Choose based on what the value does:

| Type | Update model | Use for |
| --- | --- | --- |
| Counter | only up | requests served, errors, bytes sent |
| Gauge | up and down | queue depth, active connections, temperature |
| Histogram | observations in buckets | latency/size distributions with quantile queries |
| Summary | observations (count + sum) | latency/size when average is enough |
| Info | static key-value pairs | build version, environment metadata |
| Enum | one of N states | task state, lifecycle phase |

**Naming** — `namespace`, `subsystem`, and `name` join with underscores: `myapp_http_requests_total`. Full metric names must match `[a-zA-Z_:][a-zA-Z0-9_:]*`.

**Labels** — Dimensions for grouping related time series. Declared via `labelnames=['method', 'status']`, applied via `.labels(method='GET', status='200')`.

**Registry** — `REGISTRY` is the global default. All metric constructors register with it automatically. Pass `registry=None` to skip registration (useful in tests).

## Installation / Setup

```bash
pip install prometheus-client
```

## Usage Examples

### Quick start with Summary decorator

```python
from prometheus_client import start_http_server, Summary
import random, time

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

@REQUEST_TIME.time()
def process_request(t):
    time.sleep(t)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        process_request(random.random())
```

Visit `http://localhost:8000/metrics` to view metrics. Prometheus `rate()` function computes both requests per second and latency from the `_count` and `_sum` series.

### Counter with labels

```python
from prometheus_client import Counter, start_http_server

REQUESTS = Counter(
    'requests_total',
    'Total HTTP requests received',
    labelnames=['method', 'status'],
    namespace='myapp',
)

def handle_request(method, status):
    REQUESTS.labels(method=method, status=status).inc()

if __name__ == '__main__':
    start_http_server(8000)
```

### Gauge tracking in-progress requests

```python
from prometheus_client import Gauge, start_http_server

ACTIVE = Gauge('inprogress_requests', 'Number of requests being processed', namespace='myapp')

@ACTIVE.track_inprogress()
def process():
    # ... work ...
    pass

if __name__ == '__main__':
    start_http_server(8000)
```

### Histogram with custom buckets

```python
from prometheus_client import Histogram, start_http_server

LATENCY = Histogram(
    'request_duration_seconds',
    'HTTP request latency',
    labelnames=['method', 'endpoint'],
    namespace='myapp',
    buckets=[.01, .05, .1, .25, .5, 1, 2.5, 5],
)

def handle_request(method, endpoint):
    with LATENCY.labels(method=method, endpoint=endpoint).time():
        # ... handle request ...
        pass

if __name__ == '__main__':
    start_http_server(8000)
```

## Advanced Topics

**Metric Types**: Complete reference for all 6 metric types with constructors, methods, and real-world examples → [Metric Types](reference/01-metric-types.md)

**Labels and Exemplars**: Label declaration, initialization, management, and trace-context exemplars → [Labels and Exemplars](reference/02-labels-and-exemplars.md)

**Exporting**: HTTP servers, WSGI/ASGI adapters, framework integrations (Flask, Django, FastAPI, AIOHTTP, Twisted), Pushgateway, textfile collector, Graphite bridge → [Exporting](reference/03-exporting.md)

**Advanced Patterns**: Registry management, custom collectors, multiprocess mode for Gunicorn, metrics parser, restricted registries → [Advanced Patterns](reference/04-advanced-patterns.md)
