---
name: logfire-4-32-1
description: Production-grade AI observability platform built on OpenTelemetry by the Pydantic team. Native SDKs for Python, JavaScript/TypeScript, and Rust with support for any OTel-compatible language. Use when instrumenting applications with distributed tracing, spans, metrics, and logs; configuring auto-instrumentation for FastAPI, OpenAI, LangChain, databases, and web frameworks; querying trace data via SQL; scrubbing sensitive data; implementing sampling strategies; deploying self-hosted; or integrating with the Logfire cloud platform.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.32.1"
tags:
  - observability
  - tracing
  - opentelemetry
  - logging
  - metrics
  - ai-observability
  - llm
  - python
  - javascript
  - rust
category: developer-tools
external_references:
  - https://github.com/pydantic/logfire/tree/v4.32.1/docs
  - https://github.com/pydantic/logfire-js
  - https://github.com/pydantic/logfire-mcp
  - https://github.com/pydantic/logfire-rust
  - https://github.com/pydantic/logfire/tree/v4.32.1
  - https://opentelemetry.io/
  - https://pydantic.dev/logfire/docs/
---

# Pydantic Logfire 4.32.1

## Overview

From the team behind Pydantic Validation, **Pydantic Logfire** is an observability platform built on OpenTelemetry with native SDKs for **Python**, **JavaScript/TypeScript**, and **Rust** — plus support for **any language** via standard OpenTelemetry exporters. It unifies traces, metrics, and structured logs into a single platform with SQL-based querying powered by Apache DataFusion.

Logfire is AI-native: it provides purpose-built features for LLM applications including conversation panels, token tracking, cost monitoring, tool call inspection, streaming support, and multi-turn conversation tracing. Unlike AI-only observability tools, Logfire traces your entire application stack so you can debug whether a problem is in the AI layer or the backend.

Key differentiators:
- **SQL-based analysis** — query all observability data using PostgreSQL-compatible SQL
- **MCP server** — LLMs can directly query production telemetry via the Model Context Protocol
- **Deep Python integration** — rich display of Python objects, event-loop telemetry, profiling, auto-tracing
- **Pydantic integration** — automatic validation analytics and structured model display
- **No lock-in** — built on OpenTelemetry; data export to any OTel-compatible backend

## When to Use

- Instrumenting Python, JavaScript/TypeScript, or Rust applications with distributed tracing
- Adding auto-tracing to web frameworks (FastAPI, Django, Flask, Starlette, AIOHTTP)
- Monitoring LLM/AI application calls (OpenAI, Anthropic, LangChain, LlamaIndex, Pydantic AI)
- Setting up metrics collection (counters, histograms, gauges, callbacks)
- Querying observability data with SQL or via the MCP server
- Configuring sampling strategies (head, tail, combined)
- Scrubbing sensitive data from logs and spans
- Deploying self-hosted Logfire on Kubernetes
- Integrating alternative OTel clients (Go, Java, .NET, etc.)

## Core Concepts

Logfire is built on four key observability concepts:

**Span** — The atomic unit of telemetry data. A span has a start and end time (thus a duration), can carry structured attributes, and nests within other spans. Think of spans as logs with extra functionality.

**Trace** — A tree structure of spans showing the path of any request through your application. Spans are ordered and nested, like a stack trace showing all services touched.

**Metric** — Calculated values collected at regular intervals (request latency, CPU load, queue length). Aggregated over time for charting trends, SLOs, and alerts.

**Log** — A timestamped text record with no duration. Structured logs (recommended) carry attributes as JSON.

## Installation / Setup

### Python

```bash
logfire auth                          # authenticate (stores credentials in ~/.logfire/default.toml)
logfire projects use <project-name>   # select project
```

```python
import logfire

logfire.configure()                   # initialize once before logging
logfire.info('Hello, {name}!', name='world')
```

### JavaScript/TypeScript

```js
import * as logfire from '@pydantic/logfire-node'

logfire.configure({
  token: 'your-write-token',
  serviceName: 'my-service',
})

logfire.info('Hello from Node.js', { key: 'value' }, { tags: ['example'] })
```

### Rust

Use the `logfire` crate from crates.io. Configuration follows standard OTel patterns with Logfire-specific defaults.

### CLI Commands

- `logfire auth` — authenticate with browser login
- `logfire clean [--logs]` — clean generated files
- `logfire inspect` — identify missing OTel instrumentation packages
- `logfire projects list` — list accessible projects
- `logfire projects use <name>` — select active project
- `logfire projects new <name>` — create a new project
- `logfire --region eu auth` or `--region us auth` — specify data region

## Advanced Topics

**Concepts Deep Dive**: Spans, traces, metrics, logs with examples → [Concepts](reference/01-concepts.md)

**Manual Tracing**: Spans, attributes, messages, f-strings, exceptions, log levels → [Manual Tracing](reference/02-manual-tracing.md)

**Auto-Tracing**: Automatic function-level tracing with module filtering and duration thresholds → [Auto-Tracing](reference/03-auto-tracing.md)

**Integrations**: Web frameworks, databases, HTTP clients, LLMs, task queues, logging libraries → [Integrations](reference/04-integrations.md)

**AI Observability**: LLM panels, token tracking, cost monitoring, tool call inspection, evaluations → [AI Observability](reference/05-ai-observability.md)

**Metrics**: Counters, histograms, up-down counters, gauges, callback metrics → [Metrics](reference/06-metrics.md)

**Configuration**: Programmatic, environment variables, pyproject.toml, multiple configs → [Configuration](reference/07-configuration.md)

**Sampling**: Head sampling, tail sampling by level/duration, combined strategies → [Sampling](reference/08-sampling.md)

**Distributed Tracing**: Context propagation, thread/pool executors, cross-service traces → [Distributed Tracing](reference/09-distributed-tracing.md)

**SQL Querying**: Records table schema, columns, JSON operators, time bucketing → [SQL Reference](reference/10-sql-reference.md)

**Scrubbing**: Sensitive data redaction, custom patterns, callbacks, security tips → [Scrubbing](reference/11-scrubbing.md)

**Alternative Backends**: Jaeger, OTel Collector, environment variable configuration → [Alternative Backends](reference/12-alternative-backends.md)

**JavaScript SDK**: Browser, Next.js, Cloudflare Workers, Express, Node.js, Deno → [JavaScript SDK](reference/13-javascript-sdk.md)

**MCP Server**: Remote MCP for LLM access to telemetry data → [MCP Server](reference/14-mcp-server.md)

**Self-Hosted**: Kubernetes deployment, Helm chart, system requirements → [Self-Hosted](reference/15-self-hosted.md)
