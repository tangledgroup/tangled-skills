---
name: podman-compose-1-5-0
description: Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying containerized stacks, managing services defined in compose.yaml files, or migrating from docker-compose to a daemonless rootless workflow.
version: "0.2.0"
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
## Overview
Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying containerized stacks, managing services defined in compose.yaml files, or migrating from docker-compose to a daemonless rootless workflow.

A Python-based implementation of the [Compose Specification](https://compose-spec.io/) with a Podman backend. Provides daemonless, rootless container orchestration by directly executing podman commands without requiring a running daemon service.

## When to Use
- Deploying multi-container applications defined in `compose.yaml` or `docker-compose.yml` files
- Migrating from docker-compose workflows while maintaining compatibility
- Running containerized stacks in rootless mode for improved security
- Managing services, networks, and volumes with Podman instead of Docker
- Building images and orchestrating containers without a daemon process
- Creating systemd services for container orchestration

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Prerequisites

- **Podman** version 3.4 or newer (version 3.1.0+ for legacy podman-compose 0.1.x)
- **Python 3.9** or newer
- **PyYAML** Python package
- **python-dotenv** Python package
- **podman-dnsname plugin** (optional, required for container name resolution with CNI networks; not needed with netavark backend)

### Installation Methods

#### PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip3 install podman-compose
```

For user-level installation without root privileges:

```bash
pip3 install --user podman-compose
```

Install latest development version from GitHub:

```bash
pip3 install https://github.com/containers/podman-compose/archive/main.tar.gz
```

#### Package Managers

**Debian/Ubuntu:**
```bash
sudo apt install podman-compose
```

**Fedora (31+):**
```bash
sudo dnf install podman-compose
```

**Homebrew (macOS):**
```bash
brew install podman-compose
```

#### Manual Installation

Download the single Python script directly:

```bash
# System-wide installation
curl -o /usr/local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose

# User-level installation
curl -o ~/.local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x ~/.local/bin/podman-compose
```

#### Binary Generation via Container

Generate a binary using Podman/Docker locally:

```bash
sh -c "$(curl -sSL https://raw.githubusercontent.com/containers/podman-compose/main/scripts/download_and_build_podman-compose.sh)"
```

### Podman Integration

Podman Compose can work as a podman subcommand (`podman compose`) or as a standalone command (`podman-compose`).

**As podman subcommand (v4.0+):**
When using `podman compose`, it acts as a thin wrapper around external compose providers. Configure the provider in `containers.conf` or via environment variable:

```bash
# Set via environment variable
export PODMAN_COMPOSE_PROVIDER=/usr/local/bin/podman-compose

# Disable warning about external command execution
export PODMAN_COMPOSE_WARNING_LOGS=false
```

**As standalone command:**
```bash
podman-compose up
```

See [Core Concepts](reference/01-core-concepts.md) for detailed architecture explanation.

## Usage Examples
### Basic Usage

Navigate to a directory containing a `compose.yaml` file and start services:

```bash
# Start all services in foreground
podman-compose up

# Start all services in detached mode (background)
podman-compose up -d

# Start specific services only
podman-compose up web api

# Build images before starting
podman-compose up --build

# Stop and remove all containers, networks, and volumes
podman-compose down

# View service status
podman-compose ps

# View logs from services
podman-compose logs -f
```

See [Command Reference](reference/02-command-reference.md) for complete command documentation.

### Example Compose File

Create a `compose.yaml` file in your project directory:

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
    depends_on:
      - api

  api:
    build: ./api-service
    environment:
      - DATABASE_URL=postgres://db:5432/app
    networks:
      - frontend
      - backend
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend

volumes:
  db-data:

networks:
  frontend:
  backend:
```

See [Compose File Guide](reference/03-compose-file-guide.md) for complete file format documentation.

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Command Reference](reference/02-command-reference.md)
- [Compose File Guide](reference/03-compose-file-guide.md)
- [Troubleshooting](reference/04-troubleshooting.md)

## Troubleshooting
### Container Name Resolution Fails

If containers cannot resolve each other by service name:

```bash
# Install podman-dnsname plugin (for CNI networks)
sudo dnf install podman-dnsname  # Fedora/RHEL
sudo apt install podman-dnsname  # Debian/Ubuntu

# Or switch to netavark backend (no plugin needed)
podman system connection edit default --set-option=network_backend=netavark
```

### Permission Denied Errors

Run in rootless mode or check SELinux contexts:

```bash
# Ensure podman is configured for rootless operation
podman info | grep -i "rootless"

# For SELinux systems, add :Z flag to volume mounts
volumes:
  - ./data:/app/data:Z
```

### Podman Compose Not Found

Verify installation and PATH:

```bash
# Check installation location
which podman-compose
podman-compose --version

# Add to PATH if installed in ~/.local/bin
export PATH=$HOME/.local/bin:$PATH
```

See [Troubleshooting Guide](reference/04-troubleshooting.md) for comprehensive issue resolution.

