# Self-Hosted

## Overview

Logfire can be deployed on-premises using the official Logfire Helm Chart. This is included in the Enterprise plan. Contact sales@pydantic.dev for details.

Key benefits:
- Simplified deployment with single-command installation
- Flexible configuration (resources, ingress, authentication)
- Production-ready defaults (high availability, resource limits, health checks)
- Repeatable and versioned as code
- Compliance-friendly — full data control on your infrastructure

## System Requirements

- **Kubernetes** cluster
- **PostgreSQL** database version 16 or greater
- **Object Storage** — Amazon S3, Azure Blob Storage, or Google Cloud Storage
- At least **512GB** local SSD scratch disk for ingest, compaction, and caching
- A **DNS/Hostname** accessible over HTTP from any client
- An **Identity Provider** for authentication (GitHub, Google, Microsoft) — Logfire uses Dex
- (Optional) **Kubernetes Gateway API** for advanced traffic management

## Client Configuration

After deploying the Helm chart, configure clients to send data to your instance:

```python
import logfire

logfire.configure(
    advanced=logfire.AdvancedOptions(base_url='https://<your_logfire_hostname>'),
)
```

CLI authentication:

```bash
logfire --base-url="https://<your_logfire_hostname>" auth
```

## Service Architecture

Logfire self-hosted is horizontally scalable with independently scaleable components:

**Entry Point**:
- `logfire-service` (Port 8080) — main proxy for the system

**Core Services**:
- `logfire-backend` (Port 8000) — business logic, frontend, authentication
- `logfire-ff-ingest` (Port 8012) — data ingestion API
- `logfire-ff-query-api` (Port 8011) — data querying API
- `logfire-redis` — live query streaming and autocomplete cache
- `logfire-ff-cache-*` — cache services with consistent hashing
- `logfire-ff-compaction-worker` — data compaction jobs
- `logfire-ff-maintenance-worker` — maintenance jobs
- `logfire-otel-collector` — internal OpenTelemetry collector
- `logfire-dex` — identity provider service

**External Dependencies**:
- PostgreSQL database
- Object storage (S3/Azure/GCS)

## Scaling

Each component can be scaled independently based on utilization. The architecture shares the same code as the public cloud deployment, supporting high volumes of traffic.
