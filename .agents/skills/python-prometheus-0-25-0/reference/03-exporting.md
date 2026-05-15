# Exporting

## Contents
- Built-in HTTP Server
- HTTPS and mTLS
- WSGI
- ASGI
- Framework Integrations
  - Flask
  - Django
  - FastAPI + Gunicorn
  - AIOHTTP
  - Twisted
- Pushgateway
- Node Exporter Textfile Collector
- Graphite Bridge

## Built-in HTTP Server

Start a standalone HTTP server in a daemon thread:

```python
from prometheus_client import start_http_server

start_http_server(8000)  # exposes metrics at http://localhost:8000/metrics
```

Returns server and thread objects for graceful shutdown:

```python
server, t = start_http_server(8000)
server.shutdown()
server.server_close()
t.join()
```

The server handles `OPTIONS` and `GET` methods. Other methods return HTTP 405 with an Allow header.

## HTTPS and mTLS

Enable HTTPS by providing certificate and key files:

```python
from prometheus_client import start_http_server

start_http_server(8000, certfile="server.crt", keyfile="server.key")
```

Enable mutual TLS (mTLS) by setting `client_auth_required=True`. Optionally specify `client_cafile` or `client_capath` for CA certificate validation.

## WSGI

Create a WSGI application:

```python
from prometheus_client import make_wsgi_app

app = make_wsgi_app()
```

Or start in a separate thread:

```python
from prometheus_client import start_wsgi_server

start_wsgi_server(8000)
```

Disable gzip compression with `disable_compression=True`.

## ASGI

Create an ASGI application:

```python
from prometheus_client import make_asgi_app

app = make_asgi_app()
```

Respects `Accept-Encoding: gzip` by default. Disable with `disable_compression=True`.

## Framework Integrations

### Flask

Mount the WSGI app via DispatcherMiddleware:

```python
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app(),
})
```

Run with uWSGI:

```bash
uwsgi --http 127.0.0.1:8000 --wsgi-file myapp.py --callable app
```

### Django

Use the provided view class in `urls.py`:

```python
from django.urls import path
from prometheus_client.django import PrometheusDjangoView

urlpatterns = [
    path("metrics/", PrometheusDjangoView.as_view(), name="prometheus-metrics"),
]
```

Multiprocessing activates automatically when `PROMETHEUS_MULTIPROC_DIR` is set. Override with:

```python
path("metrics/", PrometheusDjangoView.as_view(multiprocess_mode=False), name="prometheus-metrics")
```

For ready-made Django metrics, see the external [django-prometheus](https://github.com/django-commons/django-prometheus/) package.

### FastAPI + Gunicorn

Mount the ASGI app:

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI(debug=False)
app.mount("/metrics", make_asgi_app())
```

With multiprocessing support:

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app, CollectorRegistry
from prometheus_client import multiprocess

def make_metrics_app():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)

app = FastAPI(debug=False)
app.mount("/metrics", make_metrics_app())
```

Run with Gunicorn:

```bash
gunicorn -b 127.0.0.1:8000 myapp:app -k uvicorn.workers.UvicornWorker
```

### AIOHTTP

Create an async handler:

```python
from aiohttp import web
from prometheus_client.aiohttp import make_aiohttp_handler

app = web.Application()
app.router.add_get("/metrics", make_aiohttp_handler())
```

Disable auto-compression with `disable_compression=True`.

### Twisted

Use MetricsResource:

```python
from prometheus_client.twisted import MetricsResource
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

root = Resource()
root.putChild(b'metrics', MetricsResource())

factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
```

## Pushgateway

For batch jobs and ephemeral tasks that cannot be scraped directly. Push metrics to a Pushgateway instance, which Prometheus then scrapes.

### Basic usage

```python
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

registry = CollectorRegistry()
g = Gauge('job_last_success_unixtime', 'Last batch job success', registry=registry)
g.set_to_current_time()
push_to_gateway('localhost:9091', job='batchA', registry=registry)
```

Use a separate registry to avoid pushing process-level metrics from the default `REGISTRY`.

### Functions

| Function | HTTP Method | Behavior |
| --- | --- | --- |
| `push_to_gateway` | PUT | Replace all metrics with same job/grouping key |
| `pushadd_to_gateway` | POST | Replace only metrics with same name, job, and grouping key |
| `delete_from_gateway` | DELETE | Delete metrics for given job and grouping key |

### Grouping keys

```python
from prometheus_client.exposition import instance_ip_grouping_key

push_to_gateway('localhost:9091', job='batchA', registry=registry,
                grouping_key=instance_ip_grouping_key())
```

### Authentication handlers

**Basic Auth**:

```python
from prometheus_client.exposition import basic_auth_handler

def my_handler(url, method, timeout, headers, data):
    return basic_auth_handler(url, method, timeout, headers, data, 'user', 'pass')

push_to_gateway('localhost:9091', job='batchA', registry=registry, handler=my_handler)
```

**TLS client certificate**:

```python
from prometheus_client.exposition import tls_auth_handler

def my_handler(url, method, timeout, headers, data):
    return tls_auth_handler(url, method, timeout, headers, data, 'client-crt.pem', 'client-key.pem')

push_to_gateway('localhost:9091', job='batchA', registry=registry, handler=my_handler)
```

### Compression

Set `compression='gzip'` or `compression='snappy'` (requires `python-snappy` package).

## Node Exporter Textfile Collector

Write metrics to a `.prom` file for the Node exporter textfile collector. Useful for cronjobs and machine-level statistics.

```python
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile

registry = CollectorRegistry()
g = Gauge('raid_status', '1 if raid array is okay', registry=registry)
g.set(1)
write_to_textfile('/var/lib/node_exporter/textfile_collector/raid.prom', registry)
```

File is written atomically (temp file + rename). Path must end in `.prom`.

## Graphite Bridge

Push metrics over TCP in Graphite plaintext format:

```python
from prometheus_client.bridge.graphite import GraphiteBridge

gb = GraphiteBridge(('graphite.your.org', 2003))
gb.push()                    # push once
gb.start(10.0)               # push every 10 seconds in daemon thread
```

Enable Graphite tags:

```python
gb = GraphiteBridge(('graphite.your.org', 2003), tags=True)
```
