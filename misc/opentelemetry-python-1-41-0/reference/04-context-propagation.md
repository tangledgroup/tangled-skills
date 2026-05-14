# Context Propagation

## Overview

Context propagation enables distributed tracing across service boundaries. The OpenTelemetry Python SDK implements the W3C TraceContext and Baggage propagation standards via the `TextMapPropagator` interface.

## TextMapPropagator Interface

The propagator interface defines two operations:

```python
from opentelemetry.propagators.textmap import TextMapPropagator, Getter, Setter

class MyPropagator(TextMapPropagator):
    @property
    def fields(self) -> set[str]:
        """Return the set of headers this propagator reads/writes."""
        return {"traceparent", "tracestate"}

    def inject(
        self,
        carrier: dict,
        setter: Setter[dict] = default_setter,
        context: Context = None,
    ) -> None:
        """Inject context into the carrier (outgoing request)."""
        pass

    def extract(
        self,
        getter: Getter[dict] = default_getter,
        carrier: dict = None,
        context: Context = None,
    ) -> Context:
        """Extract context from the carrier (incoming request)."""
        pass
```

## Global Propagator

The global propagator is accessed via `opentelemetry.propagate`:

```python
from opentelemetry import propagate

propagator = propagate.get_global_textmap()

# Extract context from incoming HTTP headers
context = propagator.extract(carrier=request_headers, getter=header_getter)

# Inject context into outgoing HTTP headers
propagator.inject(carrier=outgoing_headers, setter=header_setter, context=context)
```

Helper functions:

```python
# Extract with defaults
from opentelemetry.propagate import extract, inject

ctx = extract(carrier=headers)
inject(carrier=outgoing_headers, context=ctx)
```

## W3C TraceContext Propagator

The `TraceContextTextMapPropagator` implements the W3C TraceContext standard. It reads and writes two headers:

- `traceparent` — Contains trace ID, span ID, trace flags
- `tracestate` — Vendor-specific trace state (vendor list)

```python
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

propagator = TraceContextTextMapPropagator()

# Example: Flask server extracting incoming context
def flask_getter(carrier, key):
    return carrier.get(key)

context = propagator.extract(flask.request.headers, getter=flask_getter)

# Example: requests library injecting outgoing context
def requests_setter(carrier, key, value):
    carrier[key] = value

propagator.inject(request.headers, setter=requests_setter)
```

## Baggage Propagator

Baggage carries key-value pairs across service boundaries:

```python
from opentelemetry.baggage import get_baggage, set_baggage, remove_baggage
from opentelemetry.baggage.propagation import W3CBaggagePropagator

# Set baggage values
import opentelemetry.baggage as baggage
ctx = baggage.set_baggage("user.id", "12345", context=get_current())
ctx = baggage.set_baggage("session.token", "abc", context=ctx)

# Read baggage
user_id = get_baggage("user.id", context=ctx)

# Remove a baggage entry
ctx = remove_baggage("session.token", context=ctx)

# Propagate via HTTP
from opentelemetry.propagate import inject
inject(carrier=outgoing_headers, context=ctx)
```

The `W3CBaggagePropagator` reads/writes the `baggage` header.

## Composite Propagator

Combine multiple propagators:

```python
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

composite = CompositePropagator([
    TraceContextTextMapPropagator(),
    W3CBaggagePropagator(),
])
```

## Configuration

The global propagator is configured via the `OTEL_PROPAGATORS` environment variable:

```bash
# Default: tracecontext,baggage
export OTEL_PROPAGATORS=tracecontext,baggage
```

Available built-in propagators (registered as `opentelemetry_propagator` entry points):

- `tracecontext` — W3C TraceContext
- `baggage` — W3C Baggage

## HTTP Framework Integration

### Flask

```python
from flask import Flask, request, jsonify
from opentelemetry import trace, propagate
from opentelemetry.trace.propagation.textmap import DefaultGetter

app = Flask(__name__)
tracer = trace.get_tracer(__name__)
getter = DefaultGetter()

@app.route("/api")
def api():
    # Extract incoming context
    context = propagate.extract(request.headers, getter=getter)

    with tracer.start_as_current_span("handle-api", context=context) as span:
        span.set_attribute("http.method", request.method)

        # Make downstream call with propagated context
        import requests
        downstream = requests.Request("GET", "http://downstream/api")
        propagate.inject(downstream.headers)

        session = requests.Session()
        response = session.send(downstream.prepare())

        return jsonify({"status": "ok"})
```

### FastAPI / Starlette

```python
from fastapi import FastAPI, Request
from opentelemetry import trace, propagate
from opentelemetry.trace.propagation.textmap import DefaultGetter

app = FastAPI()
tracer = trace.get_tracer(__name__)

@app.get("/api")
async def api(request: Request):
    context = propagate.extract(dict(request.headers), getter=DefaultGetter())

    with tracer.start_as_current_span("handle-api", context=context) as span:
        # Use propagate.inject on outgoing requests
        pass
```

### WSGI Middleware

```python
from opentelemetry import propagate
from opentelemetry.trace.propagation.textmap import DefaultGetter

class OTelMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Extract from WSGI environ (HTTP_ prefixed headers)
        getter = DefaultGetter()
        context = propagate.extract(environ, getter=getter)

        # Make context active for the request
        with propagate.set_httpbaggage(context):
            return self.app(environ, start_response)
```

## Context API

The context module manages implicit context propagation:

```python
from opentelemetry.context import (
    get_current,
    set_value,
    attach,
    detach,
    get_value,
)

# Get current context
ctx = get_current()

# Create new context with a value
new_ctx = set_value("key", "value", ctx)

# Make context the current (implicit) context
token = attach(new_ctx)

# Restore previous context
detach(token)

# Read a value from current context
value = get_value("key")
```

## TraceState

The `TraceState` carries vendor-specific information in the W3C tracestate header:

```python
from opentelemetry.trace.span import TraceState

# Create trace state
ts = TraceState.from_header("vendor1=val1,vendor2=val2")

# Access entries
entries = list(ts.keys())  # ['vendor1', 'vendor2']
value = ts.get("vendor1")  # 'val1'
```

Samplers can modify `TraceState` to include sampling decisions for downstream services.
