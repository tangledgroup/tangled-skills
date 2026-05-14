---
name: grafana-13-0-1
description: Grafana 13.0.1 observability platform for querying, visualizing, alerting on, and exploring metrics, logs, traces, and profiles. Covers installation, data source configuration, dashboard building with dynamic dashboards, alert rule management, Explore queries, provisioning with Git Sync, and administration. Use when setting up Grafana monitoring, building dashboards, configuring alerts, provisioning resources via YAML or GitOps, or administering a Grafana instance.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - grafana
  - observability
  - dashboards
  - alerting
  - metrics
  - logs
  - traces
category: tooling
external_references:
  - https://github.com/grafana/grafana/tree/v13.0.1
  - https://grafana.com/docs/grafana/latest/
---

# Grafana 13.0.1

## Overview

Grafana is an open-source visualization and analytics platform for metrics, logs, traces, and profiles. It connects to dozens of data sources — Prometheus, Loki, Tempo, PostgreSQL, CloudWatch, Elasticsearch, and more — and provides dashboards, alerting, and ad-hoc exploration.

The Grafana ecosystem includes complementary OSS projects: **Loki** (log aggregation), **Tempo** (distributed tracing), **Mimir** (long-term metrics storage for Prometheus), and **Pyroscope** (continuous profiling). Together they form the LGTM stack.

Grafana 13.0 introduces Dynamic Dashboards (GA) with a new layout engine and auto-migration, Git Sync (GA) for bidirectional GitOps, dashboard templates, saved queries, and a new Gauge panel type.

## When to Use

- Installing or configuring a Grafana instance (bare metal, Docker, Kubernetes)
- Setting up data sources and writing queries against Prometheus, Loki, Tempo, SQL databases, or cloud providers
- Building dashboards with panels, variables, templating, or dynamic layouts
- Creating alert rules, contact points, and notification policies
- Exploring data ad-hoc using the Explore interface
- Provisioning Grafana resources via YAML or Git Sync for GitOps workflows
- Managing users, roles, permissions, service accounts, or plugins
- Upgrading Grafana instances or troubleshooting common issues

## Quick Start

### Docker Deployment

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:13.0.1
```

Access at `http://localhost:3000`, log in with `admin` / `admin`.

### Minimal Data Source Provisioning

Create `/etc/grafana/provisioning/datasources/prometheus.yaml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
```

Ensure the provisioning loader references it in `grafana.ini` or `/etc/grafana/provisioning/provisioners.yaml`:

```yaml
apiVersion: 1
providers:
  - name: 'default'
    folder: ''
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards
```

### First Dashboard Query (Prometheus)

In Explore or a panel query editor, use PromQL:

```promql
up{job="node-exporter"}
```

This returns `1` for healthy targets and `0` for down targets. Add it to a Time series panel to visualize service availability.

## Core Concepts

- **Data source** — connection to a storage backend (Prometheus, Loki, SQL, etc.) with its own query editor
- **Dashboard** — collection of panels arranged in a layout, each panel displaying data from one or more queries
- **Panel** — individual visualization (Time series, Stat, Gauge, Table, Logs, Trace, Heatmap, Canvas, Node Graph)
- **Explore** — ad-hoc query interface for investigating data without creating a dashboard
- **Alert rule** — condition evaluated against query results that triggers notifications when breached
- **Contact point** — notification destination (email, Slack, PagerDuty, webhook)
- **Variable** — templated value in dashboards that lets users filter or switch between dimensions at runtime
- **Provisioning** — managing Grafana resources (data sources, dashboards, plugins) via YAML configuration files
- **Git Sync** — bidirectional GitOps integration connecting Grafana to GitHub, GitLab, or Bitbucket for dashboard/folder management

## Advanced Topics

**Installation and Setup**: Supported OS, hardware requirements, package managers, Docker deployment, `grafana.ini` configuration → [Installation and Setup](reference/01-installation-setup.md)

**Data Sources**: Managing data sources, built-in sources (Prometheus, Loki, Tempo, SQL), query editors, plugin installation, YAML provisioning → [Data Sources](reference/02-data-sources.md)

**Dashboards and Visualizations**: Dashboard creation, dynamic dashboards (GA in v13), panel types, variables and templating, annotations, sharing → [Dashboards and Visualizations](reference/03-dashboards-visualizations.md)

**Alerting**: Alert rules, contact points, notification policies, alert states, external integrations, performance considerations → [Alerting](reference/04-alerting.md)

**Explore and Queries**: Explore interface, query management, ad hoc filters, saved queries, correlations → [Explore and Queries](reference/05-explore-queries.md)

**Administration**: User management, roles and permissions, service accounts, provisioning system, Git Sync (GA in v13), plugin management, CLI → [Administration](reference/06-administration.md)

**Upgrade and Troubleshooting**: Upgrade process, breaking changes in v13.0, database migrations, backup/restore, common issues → [Upgrade and Troubleshooting](reference/07-upgrade-troubleshooting.md)
