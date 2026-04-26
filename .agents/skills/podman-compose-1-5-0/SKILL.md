---
name: podman-compose-1-5-0
description: Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying containerized stacks, managing services defined in compose.yaml files, or migrating from docker-compose to a daemonless rootless workflow.
version: "1.5.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - podman
  - compose
  - containers
  - orchestration
  - devops
  - docker-compose-alternative
category: devops
external_references:
  - https://github.com/containers/podman-compose
  - https://compose-spec.io
---

# Podman Compose 1.5.0

## Overview

Podman Compose is an implementation of the [Compose Specification](https://compose-spec.io/) with a Podman backend. It enables multi-container application orchestration using `compose.yaml` files, translating Compose directives into native `podman` commands — no daemon required. The project focuses on rootless operation and a daemon-less process model where `podman-compose` directly executes `podman` CLI commands.

It is formed as a single Python file script (Python 3.9+) that can be dropped into your PATH. Dependencies are minimal: `podman`, the `dnsname` plugin (for container name resolution on CNI networks), `PyYAML`, and `python-dotenv`.

## When to Use

- Deploying multi-container applications defined in Compose specification files with Podman instead of Docker
- Migrating from `docker-compose` to a rootless, daemon-less workflow
- Managing complex container stacks (web apps, databases, caches) on Linux without systemd or Docker socket
- Running compose-based development environments in CI/CD pipelines
- Generating systemd unit files for compose stacks via `podman-compose systemd`

## Core Concepts

**Compose file** (`compose.yaml` or `compose.yml`) defines services, networks, volumes, configs, and secrets. Podman Compose parses this YAML and translates each service into one or more `podman` commands. Unlike Docker Compose which talks to a daemon API, podman-compose forks `podman` directly — making it truly daemon-less.

**Project name** groups all resources (containers, networks, volumes) together. By default derived from the directory containing the compose file. Override with `-p` flag or top-level `name` in the compose file. Exposed as `COMPOSE_PROJECT_NAME` for interpolation.

**Services** are the primary building block — each service maps to one or more containers running identically configured images. Services can depend on each other, share networks, mount volumes, and expose ports.

**Podman pods vs containers** — Podman Compose can group related containers into a single pod (sharing network namespace and IPC) using the `--pod` flag or `pod: true` in service config. This mirrors Docker's default behavior where linked containers share networking.

## Installation / Setup

Install from PyPI:

```bash
pip3 install podman-compose
```

Or from package managers:

```bash
# Debian/Ubuntu
sudo apt install podman-compose

# Fedora
sudo dnf install podman-compose

# Homebrew
brew install podman-compose
```

Manual single-file install:

```bash
curl -o /usr/local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose
```

Prerequisites:
- `podman` (version 3.4+ recommended for full compatibility)
- `podman dnsname` plugin (`podman-plugins` or `podman-dnsname` package) — required for container name resolution on CNI networks. Not needed when using netavark as network backend.
- Python 3.9+
- `PyYAML` and `python-dotenv`

## Usage Examples

Basic compose file:

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    networks:
      - frontend

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend

networks:
  frontend:
  backend:

volumes:
  db-data:
```

Start the stack:

```bash
podman-compose up -d
```

Stop and tear down:

```bash
podman-compose down
```

Build local images then start:

```bash
podman-compose up --build
```

Run a one-off command in a service:

```bash
podman-compose run web nginx -v
```

Execute inside a running container:

```bash
podman-compose exec db psql -U postgres
```

## Advanced Topics

**Compose Specification**: Top-level elements, service configuration, networks, volumes, configs, and secrets → [Compose Specification](reference/01-compose-specification.md)

**Podman Compose Commands**: Complete reference of all supported CLI commands with flags and options → [Commands Reference](reference/02-commands-reference.md)

**Service Configuration**: Detailed service-level settings including build, deploy, environment, ports, volumes, healthchecks, and dependencies → [Service Configuration](reference/03-service-configuration.md)

**Environment and Variables**: Variable interpolation, env_file handling, dotenv integration, and override files → [Environment and Variables](reference/04-environment-and-variables.md)

**Advanced Patterns**: Profiles, extends, fragments, multi-compose merge, systemd generation, and migration from docker-compose → [Advanced Patterns](reference/05-advanced-patterns.md)
