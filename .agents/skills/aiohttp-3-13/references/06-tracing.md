# aiohttp Tracing Reference

## Client Tracing

### Overview

Client tracing allows monitoring and debugging of HTTP requests with hooks at various lifecycle points.

### TraceConfig

```python
from aiohttp import TraceConfig, TraceRequestStartParams

trace_configs = []

def create_trace_config():
    trace_config = TraceConfig()
    
    # Request start hook
    def on_request_start(session, trace_config_ctx, params):
        print(f"Request started: {params.method} {params.url}")
        trace_config_ctx['start_time'] = time.time()
    
    trace_config.on_request_start.append(on_request_start)
    
    # Request end hook
    def on_request_end(session, trace_config_ctx, params):
        duration = time.time() - trace_config_ctx.get('start_time', 0)
        print(f"Request ended: {params.method} {params.url} "
              f"status={params.response.status} duration={duration:.3f}s")
    
    trace_config.on_request_end.append(on_request_end)
    
    return trace_config

trace_configs.append(create_trace_config())

session = aiohttp.ClientSession(trace_configs=trace_configs)
```

### TraceRequestContext

Custom context for sharing data between hooks:

```python
async def custom_trace():
    ctx = {}  # Custom context dict
    
    trace_config = TraceConfig()
    
    def on_request_start(session, trace_req_ctx, params):
        trace_req_ctx['custom_data'] = {
            'request_id': uuid.uuid4().hex,
            'start': time.time()
        }
    
    def on_request_end(session, trace_req_ctx, params):
        data = trace_req_ctx.get('custom_data', {})
        request_id = data.get('request_id')
        duration = time.time() - data.get('start', 0)
        
        print(f"[{request_id}] {params.url} "
              f"status={params.response.status} time={duration:.3f}s")
    
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    
    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
        async with session.get('http://example.com') as resp:
            await resp.text()

asyncio.run(custom_trace())
```

### Available Trace Hooks

**Request lifecycle:**
- `on_request_start` - When request starts
- `on_request_redirect` - When redirected
- `on_request_chunk_sent` - When request chunk sent
- `on_response_chunk_received` - When response chunk received
- `on_request_end` - When request completes
- `on_request_exception` - When exception occurs

**DNS resolution:**
- `on_dns_cache_hit` - DNS cache hit
- `on_dns_cache_miss` - DNS cache miss
- `on_dns_host_resolved` - Host resolved

**Connection:**
- `on_connection_create_start` - Connection creation starts
- `on_connection_create_end` - Connection created
- `on_connection_queued_start` - Connection queued
- `on_connection_queued_end` - Connection dequeued
- `on_connection_reuseconn` - Connection reused

### Trace Parameters

**TraceRequestStartParams:**
- `method` - HTTP method (str)
- `url` - Request URL (yarl.URL)
- `headers` - Request headers (CIMultiDictProxy)

**TraceRequestRedirectParams:**
- `method` - HTTP method
- `url` - New URL after redirect
- `headers` - Headers
- `response` - Original response that redirected

**TraceRequestChunkSentParams:**
- `chunk` - Data chunk sent (bytes)

**TraceResponseChunkReceivedParams:**
- `chunk` - Response data chunk (bytes)

**TraceRequestEndParams:**
- Inherits from TraceRequestStartParams
- `response` - ClientResponse object
- `handle` - Request handle

### Example: Performance Monitoring

```python
from aiohttp import TraceConfig
import time
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.latencies = []
    
    def create_trace_config(self):
        trace_config = TraceConfig()
        
        def on_request_start(session, ctx, params):
            ctx['start_time'] = time.time()
        
        def on_request_end(session, ctx, params):
            duration = time.time() - ctx.get('start_time', 0)
            self.latencies.append(duration)
            
            if len(self.latencies) % 10 == 0:
                avg = statistics.mean(self.latencies[-10:])
                print(f"Last 10 requests avg: {avg*1000:.1f}ms")
        
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)
        
        return trace_config

monitor = PerformanceMonitor()
session = aiohttp.ClientSession(
    trace_configs=[monitor.create_trace_config()]
)
```

### Example: Request Logging

```python
import logging
from aiohttp import TraceConfig

logger = logging.getLogger('http_client')
logger.setLevel(logging.INFO)

def create_logging_trace():
    trace_config = TraceConfig()
    
    def on_request_start(session, ctx, params):
        logger.info(f"REQUEST: {params.method} {params.url}")
        
        # Log headers (excluding sensitive ones)
        safe_headers = {k: v for k, v in params.headers.items() 
                       if k.lower() not in ('authorization', 'cookie')}
        logger.debug(f"Headers: {safe_headers}")
    
    def on_request_end(session, ctx, params):
        logger.info(f"RESPONSE: {params.method} {params.url} "
                   f"-> {params.response.status}")
    
    def on_request_exception(session, ctx, params):
        exc = params.get('exception')
        logger.error(f"ERROR: {params.method} {params.url} - {exc}")
    
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_exception.append(on_request_exception)
    
    return trace_config

session = aiohttp.ClientSession(
    trace_configs=[create_logging_trace()]
)
```

### Example: Distributed Tracing

```python
from aiohttp import TraceConfig
import uuid

def create_distributed_tracing_trace(service_name):
    trace_config = TraceConfig()
    
    def on_request_start(session, ctx, params):
        # Generate or extract trace ID
        trace_id = ctx.get('trace_id') or uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        
        ctx['trace_id'] = trace_id
        ctx['span_id'] = span_id
        
        # Add tracing headers
        params.headers['X-Trace-ID'] = trace_id
        params.headers['X-Span-ID'] = span_id
        params.headers['X-Service'] = service_name
    
    def on_request_end(session, ctx, params):
        trace_id = ctx.get('trace_id')
        span_id = ctx.get('span_id')
        
        # Could send to tracing backend (Jaeger, Zipkin, etc.)
        print(f"Trace: {trace_id}, Span: {span_id} "
              f"Status: {params.response.status}")
    
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    
    return trace_config

session = aiohttp.ClientSession(
    trace_configs=[create_distributed_tracing_trace('my-service')]
)
```

## Server Tracing

### Server Trace Hooks

Server tracing provides similar hooks for monitoring server-side requests.

```python
from aiohttp import web

async def on_request_start(request):
    request['trace_start'] = time.time()
    print(f"[START] {request.method} {request.path}")

async def on_request_finish(request, response):
    duration = time.time() - request.get('trace_start', 0)
    print(f"[END] {request.method} {request.path} "
          f"status={response.status} duration={duration:.3f}s")

async def on_response_prepare(request, response):
    # Add custom headers based on tracing
    if 'trace_id' in request:
        response.headers['X-Trace-ID'] = request['trace_id']

app = web.Application()
app.on_request_start.append(on_request_start)
app.on_request_finish.append(on_request_finish)
app.on_response_prepare.append(on_response_prepare)
```

### Server Connection Tracing

```python
async def on_connection_made(request, transport):
    peer = transport.get_extra_info('peername')
    print(f"Connection from {peer}")

async def on_connection_lost(request, exc):
    if exc:
        print(f"Connection lost: {exc}")
    else:
        print("Connection closed cleanly")

app.on_connection_made.append(on_connection_made)
app.on_connection_lost.append(on_connection_lost)
```

### Request Timing Middleware with Tracing

```python
import time
from aiohttp import web

class RequestTimer:
    def __init__(self):
        self.requests = []
    
    async def middleware(self, app, handler):
        async def middleware(request):
            start = time.time()
            
            try:
                response = await handler(request)
                status = response.status
            except Exception as e:
                status = 500
                raise
            
            finally:
                duration = time.time() - start
                self.requests.append({
                    'method': request.method,
                    'path': request.path,
                    'status': status,
                    'duration': duration,
                    'time': time.time()
                })
                
                # Keep last 1000 requests
                if len(self.requests) > 1000:
                    self.requests.pop(0)
            
            return response
        
        return middleware
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.requests:
            return {}
        
        durations = [r['duration'] for r in self.requests]
        
        return {
            'total_requests': len(self.requests),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'error_rate': sum(1 for r in self.requests if r['status'] >= 400) / len(self.requests)
        }

timer = RequestTimer()
app = web.Application(middlewares=[timer.middleware])
```

### Integration with External Tracing

```python
from aiohttp import web
import requests

async def opentracing_middleware(app, handler):
    from opentracing import tracer
    
    async def middleware(request):
        # Extract tracing context from headers
        span_ctx = tracer.extract(
            format='http_headers',
            carrier=dict(request.headers)
        )
        
        # Create new span
        span = tracer.start_span(
            operation_name=f"{request.method} {request.path}",
            child_of=span_ctx
        )
        
        try:
            response = await handler(request)
            span.set_tag('http.status_code', response.status)
            return response
        except Exception as e:
            span.log_exception(e)
            raise
        finally:
            span.finish()
    
    return middleware

app = web.Application(middlewares=[opentracing_middleware])
```
