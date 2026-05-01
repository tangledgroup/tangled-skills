---
name: opentelemetry-1-56-0
description: Complete OpenTelemetry 1.56.0 specification toolkit for implementing distributed tracing, metrics collection, and logging across polyglot applications. Use when instrumenting services with OTel SDKs, configuring OTLP exporters, implementing sampling strategies (including AlwaysRecord), setting up context propagation with environment variable carriers, or building observability pipelines following the official OTel 1.56.0 spec.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.56.0"
tags:
  - distributed-tracing
  - metrics
  - logging
  - observability
  - OTLP
  - context-propagation
  - sampling
  - semantic-conventions
  - prometheus-compatibility
category: observability
external_references:
  - https://opentelemetry.io/
  - https://github.com/open-telemetry/opentelemetry-collector
  - https://github.com/open-telemetry/opentelemetry-proto
  - https://github.com/open-telemetry/opentelemetry-specification
  - https://github.com/open-telemetry/semantic-conventions
  - https://opentelemetry.io/docs/
  - https://www.w3.org/TR/baggage/
  - https://www.w3.org/TR/trace-context/
  - https://opentelemetry.io/docs/specs/otel/overview/
---

# OpenTelemetry 1.56.0

## Overview

OpenTelemetry (OTel) is a vendor-neutral, open-source observability framework for instrumenting, generating, collecting, and exporting telemetry data — traces, metrics, logs, and profiles. It is a CNCF project supported by 90+ observability vendors and provides a unified standard across the industry.

At the highest architectural level, OpenTelemetry clients are organized into **signals**. Each signal provides a specialized form of observability and functions independently while sharing common subsystems like context propagation. OpenTelemetry is a **cross-cutting concern** — instrumentation code is mixed into application code to describe behavior without modifying business logic.

Each signal consists of four types of packages:

- **API** — Cross-cutting public interfaces for instrumentation. Imported by third-party libraries and application code.
- **SDK** — The implementation of the API, managed by the application owner. Includes constructors and plugin interfaces.
- **Semantic Conventions** — Standardized keys and values describing commonly observed concepts, protocols, and operations.
- **Contrib** — Optional plugins and instrumentation maintained by the OpenTelemetry project (API Contrib depends only on API; SDK Contrib also depends on SDK).

Required plugins like OTLP Exporters and TraceContext Propagators are included as part of the SDK.

## What Changed in 1.56.0

- **Tracer `enabled` operation stabilized** — The optional API for checking if a Tracer is enabled before creating spans is now stable.
- **`AlwaysRecord` sampler stabilized** — Sampler decorator that converts `DROP` decisions to `RECORD_ONLY`, enabling span-to-metrics processing without exporting dropped spans.
- **Environment Variables as Context Propagation Carriers** — Document promoted to Beta status, with decoupled carrier responsibilities and POSIX.1-2024 aligned name restrictions.
- **Event to Span Event Bridge** — New bridge API for converting log events into span events.
- **Prometheus Metrics Exporter** — Multiple stabilizations: host configuration, classic histogram to OTLP explicit histogram, timestamp transformations, native histogram to exponential histogram (including NHCB custom buckets), dropped types, attributes-to-labels, exemplar transformations, and metadata.
- **OpenTracing compatibility deprecated** — OpenTracing compatibility requirements are now deprecated in the specification.
- **Resource clarification** — Resource describes the observed entity, not the component that technically emits telemetry.
- **Entities merge algorithm** — Formal definition of the entities merge algorithm.
- **Declarative configuration** — Strict YAML parsing guidance added; spec changes must consider declarative config schema; in-development guidance for exposing effective `Resource` from `Create`.
- **Metric Reader** — Development `maxExportBatchSize` parameter added to Periodic exporting MetricReader.
- **Core packages term defined** — New terminology for core package classification.

## When to Use

- Instrumenting applications with distributed tracing, metrics, or logs following the official spec
- Configuring OTLP exporters with environment variables for endpoint, headers, TLS/mTLS
- Implementing sampling strategies (AlwaysOn, AlwaysOff, TraceIdRatioBased, ProbabilitySampler, ParentBased, AlwaysRecord)
- Setting up context propagation across service boundaries using W3C TraceContext and Baggage
- Using environment variables as context propagation carriers (Beta in 1.56.0)
- Building observability pipelines with the OpenTelemetry Collector
- Applying semantic conventions for attributes, resources, and instrumentation scope
- Designing metrics with Views, aggregations (Sum, Gauge, Histogram, ExponentialHistogram), and exemplars
- Working with the OTLP data model for traces, metrics, logs, and profiles
- Configuring Prometheus compatibility (stabilized transformations in 1.56.0)
- Using Tracer `enabled` API to avoid expensive span creation
- Using `AlwaysRecord` sampler for accurate span-to-metrics processing

## Core Concepts

**Signals**: The primary observability dimensions — Traces (distributed request flows), Metrics (numerical measurements over time), Logs (structured events), Baggage (propagated name/value pairs), and Profiles (CPU/memory flame graphs).

**Context**: An immutable propagation mechanism carrying execution-scoped values across API boundaries. All signals share the same Context for in-process state access. Supports explicit and implicit (thread-local/async-local) modes. Environment variables can serve as context propagation carriers (Beta in 1.56.0).

**Span**: A single operation within a trace, containing name, start/end timestamps, attributes, events, status, parent reference, and SpanContext. Traces are directed acyclic graphs (DAGs) of spans.

**SpanContext**: The propagated portion of a span — TraceId (16 bytes), SpanId (8 bytes), TraceFlags (1 byte bitmap with sampling bit `0x1`), and TraceState (vendor-specific key-value list).

**Resource**: Captures information about the entity for which telemetry is recorded. Composed of Entities (structured identity) and raw attributes. The Resource describes the **observed entity**, not the component that technically emits telemetry. Examples: cloud provider, Kubernetes pod, container, process, service name.

**Instrumentation Scope**: Identifies the source of telemetry — typically a library name, version, schema URL, and optional attributes. Distinct from Resource which identifies the observed entity.

**OTLP (OpenTelemetry Protocol)**: The standard wire protocol for exporting telemetry. Supports both HTTP/protobuf (port 4318) and gRPC (port 4317). Per-signal paths are appended: `/v1/traces`, `/v1/metrics`, `/v1/logs`.

## Advanced Topics

**Tracing API & SDK**: TracerProvider, Tracer, Span creation, sampling strategies (including stabilized AlwaysRecord), Tracer `enabled` API → [Tracing](reference/01-tracing.md)

**Metrics API & SDK**: MeterProvider, instruments (Counter, Histogram, Gauge, UpDownCounter), Views, aggregations, exemplars, temporality, Prometheus exporter compatibility → [Metrics](reference/02-metrics.md)

**Logs API & Data Model**: LoggerProvider, LogRecord fields, severity mapping, events format, event-to-span-event bridge → [Logs](reference/03-logs.md)

**Context Propagation**: Context API, TextMapPropagator, W3C TraceContext headers, Baggage propagation, environment variables as carriers (Beta) → [Context and Propagation](reference/04-context-propagation.md)

**OTLP Protocol & Exporter**: Configuration options, environment variables, retry behavior, endpoint URLs → [OTLP Protocol](reference/05-otlp-protocol.md)

**Resources & Semantic Conventions**: Resource data model with entities (merge algorithm defined in 1.56.0), merging rules, attribute conventions → [Resources and Semantic Conventions](reference/06-resources-semantic-conventions.md)

**Versioning & Stability**: Signal lifecycle (Development → Stable → Deprecated → Removed), API/SDK stability guarantees, declarative configuration → [Versioning and Stability](reference/07-versioning-stability.md)
