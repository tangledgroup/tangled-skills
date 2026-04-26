# Concepts

## Spans

A **span** is the building block of a trace — a single row in the Live view. Spans let you add context to logs and measure code execution time. Multiple spans combine to form a trace, providing a complete picture of an operation's journey through your system.

```python
from pathlib import Path
import logfire

logfire.configure()

cwd = Path.cwd()
total_size = 0

with logfire.span('counting size of {cwd=}', cwd=cwd):
    for path in cwd.iterdir():
        if path.is_file():
            with logfire.span('reading {path}', path=path.relative_to(cwd)):
                total_size += len(path.read_bytes())

    logfire.info('total size of {cwd} is {size} bytes', cwd=cwd, size=total_size)
```

The outer span measures total directory processing time. Inner spans measure individual file reads. The final log records the result without a duration.

## Traces

A trace is a tree structure of spans showing the path of any client request, LLM run, or API call through your application. Spans are ordered and nested — like a stack trace showing all services touched and all responses returned.

Traces are not limited to a single service. They can be propagated across completely different and isolated services. A single trace could contain HTTP requests to both a Python API and a SQL database.

## Metrics

Metrics are calculated values measuring your application through time:

- Collected at regular intervals (request latency, CPU load, queue length)
- Aggregated over time
- Used for charting long-term trends, establishing SLOs, and triggering alerts

Alongside logs and traces, metrics complete the "three pillars" of observability.

## Logs

Logs record something which happened in your application. Importantly, they do not have a duration compared to spans and traces. A log is a timestamped text record, either structured (recommended) or unstructured, with optional metadata.

Log levels available: `trace`, `debug`, `info`, `notice`, `warn`, `error`, `fatal`.
