---
name: gunicorn-26-0-0
description: Complete toolkit for Gunicorn 26.0.0 — Python WSGI/ASGI HTTP server with pre-fork worker model. Covers installation, configuration, worker selection (sync, gthread, gevent, ASGI), deployment behind Nginx/systemd/Docker, SSL/TLS, HTTP/2, Dirty Arbiters for heavy workloads, uWSGI protocol, and runtime control via gunicornc. Use when deploying Python web applications (Django, Flask, FastAPI, Starlette) to production, tuning Gunicorn worker counts and timeouts, configuring reverse proxy integration, or setting up async/ASGI workloads with streaming and Dirty Arbiters.
---

# Gunicorn 26.0.0

## Overview

Gunicorn (Green Unicorn) is a Python WSGI HTTP server for UNIX, using a pre-fork worker model ported from Ruby's Unicorn. It is broadly compatible with web frameworks, simply implemented, light on resources, and production-proven since 2010.

Version 26.0.0 builds on v25 features including Dirty Arbiters (separate process pools for heavy workloads), HTTP/2 support, the native ASGI worker, and the `gunicornc` control interface. Requires **Python 3.12+**.

## When to Use

- Deploying a Python web application (Django, Flask, FastAPI, Starlette) to production
- Tuning Gunicorn worker counts, timeouts, or thread pools
- Configuring reverse proxy integration (Nginx, HAProxy) with Gunicorn
- Setting up ASGI workloads with WebSockets, streaming, or Dirty Arbiters
- Managing Gunicorn at runtime via signals or the `gunicornc` control interface
- Choosing between worker types (sync, gthread, gevent, ASGI) for a specific workload

## Core Concepts

### Pre-fork Worker Model

Gunicorn runs an **arbiter** (master) process that manages a pool of **worker** processes. The arbiter listens on sockets and distributes connections to workers. Workers handle requests independently — a worker crash affects only its in-flight requests.

### Configuration Priority Chain

Gunicorn reads configuration from five sources, increasing priority:

1. Environment variables (per-setting support)
2. Framework-specific config (Paste Deploy)
3. Python config file (`gunicorn.conf.py`, auto-loaded from working directory)
4. `GUNICORN_CMD_ARGS` environment variable
5. Command-line arguments (highest priority)

Print fully resolved config: `gunicorn --print-config APP_MODULE`
Validate and exit: `gunicorn --check-config APP_MODULE`

### Worker Types

| Worker | Concurrency | Keep-Alive | Best For |
|--------|-------------|------------|----------|
| `sync` (default) | 1 request/worker | No | CPU-bound apps behind a buffering proxy |
| `gthread` | Thread pool | Yes | Mixed workloads, moderate concurrency |
| `gevent` | Greenlets | Yes | I/O-bound, WebSockets, streaming |
| `asgi` | AsyncIO | Yes | FastAPI, Starlette, Quart (async frameworks) |
| `tornado` | Tornado IOLoop | Yes | Native Tornado applications |

## Installation / Setup

```bash
# Quick install
pip install gunicorn

# With async extras
pip install gunicorn[gevent,setproctitle]

# In a virtual environment (recommended)
python -m venv venv && source venv/bin/activate
pip install gunicorn

# Docker
docker pull ghcr.io/benoitc/gunicorn:latest
```

## Usage Examples

### Basic WSGI (Flask)

```bash
gunicorn app:app --workers 4
```

### Django

```bash
gunicorn myproject.wsgi --workers 4
```

### FastAPI (ASGI)

```bash
gunicorn main:app --worker-class asgi --workers 4
```

### With a Configuration File

Create `gunicorn.conf.py`:

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

Run (auto-loads `gunicorn.conf.py` from current directory):

```bash
gunicorn app:app
```

### Worker Count Formula

Start with `2 * CPU_CORES + 1` workers, adjust under load. Use `TTIN`/`TTOU` signals to scale at runtime.

## Advanced Topics

**Configuration Settings**: Full reference of all Gunicorn settings with defaults and descriptions → [Configuration Settings](reference/01-configuration-settings.md)

**Deployment Patterns**: Nginx proxy, systemd socket activation, Docker, PROXY protocol, process managers → [Deployment Patterns](reference/02-deployment.md)

**Workers and Customization**: Worker type selection, ASGI worker details, Dirty Arbiters for heavy workloads, custom applications → [Workers and Customization](reference/03-workers-and-customization.md)

**Operations**: Signal handling, binary upgrades, logging, statsD instrumentation, FAQ → [Operations](reference/04-operations.md)
