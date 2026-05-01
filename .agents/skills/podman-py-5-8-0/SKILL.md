---
name: podman-py-5-8-0
description: Python client library for Podman container engine providing programmatic access to containers, images, pods, networks, volumes, manifests, secrets, and quadlets via RESTful API. Use when building Python applications that require container orchestration, automation scripts, CI/CD integration, or container management without Docker dependency.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "5.8.0"
tags:
  - podman
  - containers
  - python
  - docker-alternative
  - container-management
category: container-runtime
external_references:
  - https://github.com/containers/podman-py
  - https://podman-py.readthedocs.io/en/latest/
---

# Podman Python SDK 5.8.0

## Overview

PodmanPy is a Python3 library of bindings to the RESTful API of [Podman](https://github.com/containers/podman). It provides a Docker-compatible interface for managing containers, images, networks, volumes, pods, manifests, secrets, and quadlets programmatically from Python. The package connects to a running Podman service via Unix socket, TCP, or SSH.

The API design mirrors the Docker SDK for Python, making migration straightforward. PodmanPy requires Python 3.9+ and depends on `requests`, `urllib3`, and `tomli` (for Python < 3.11).

## When to Use

- Automating container lifecycle operations from Python scripts
- Building CI/CD pipelines that manage containers without Docker
- Creating container orchestration tools with Podman as backend
- Writing automation that needs pod support (not available in Docker)
- Managing quadlet systemd unit files programmatically
- Any scenario requiring programmatic access to Podman's REST API

## Installation / Setup

Install from PyPI:

```bash
pip install podman
```

Optional progress bar support:

```bash
pip install "podman[progress_bar]"
```

### Connecting to Podman Service

PodmanPy connects through a URL where the scheme determines the transport:

- **Unix socket** (local): `unix:///run/user/1000/podman/podman.sock` or `http+unix:///run/podman/podman.sock`
- **SSH**: `ssh://user@host:22/run/podman/podman.sock?secure=True` or `http+ssh://user@host/path`
- **TCP**: `tcp://hostname:port`

The scheme aliases `unix`, `ssh`, and `http+unix` are accepted as shorthand.

## Usage Examples

### Basic client usage with context manager

```python
from podman import PodmanClient

with PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock") as client:
    if client.ping():
        print("Podman service is running")
```

### Listing and managing containers

```python
with PodmanClient() as client:
    for container in client.containers.list():
        container.reload()  # refresh status from sparse list data
        print(container.id, container.name, container.status)
```

### Running a container

```python
with PodmanClient() as client:
    container = client.containers.run(
        "alpine:latest",
        ["echo", "hello world"],
        detach=True,
        name="my-container"
    )
    print(container.logs())
    container.remove(force=True)
```

### Working with images

```python
with PodmanClient() as client:
    # Pull an image
    image = client.images.pull("alpine", tag="3.19")
    print(image.id, image.tags)

    # List images
    for img in client.images.list():
        print(img.id, img.tags)

    # Remove image
    image.remove(force=True)
```

### Building images from Dockerfile

```python
with PodmanClient() as client:
    image, logs = client.images.build(
        path="./my-app",
        dockerfile="Dockerfile",
        tag="my-app:latest"
    )
    print(f"Built image: {image.id}")
```

## Core Concepts

- **PodmanClient** — Main entry point, implements context manager protocol. Access resource managers via properties: `containers`, `images`, `networks`, `volumes`, `pods`, `manifests`, `secrets`, `quadlets`.
- **Manager pattern** — Each resource type has a Manager (e.g., `ContainersManager`) providing `list()`, `get()`, `exists()`, `create()`, and `remove()` operations.
- **Resource objects** — Individual entities (Container, Image, Network, etc.) expose properties and methods for inspection and lifecycle control. All inherit from `PodmanResource` with common `id`, `short_id`, `reload()`.
- **Connection URL schemes** — `unix://`, `http+unix://`, `ssh://`, `http+ssh://`, `tcp://` determine transport. Default falls back to local Unix socket at `$XDG_RUNTIME_DIR/podman/podman.sock`.
- **Docker compatibility** — API mirrors Docker SDK for Python. `from_env()` classmethod reads `CONTAINER_HOST`/`DOCKER_HOST` environment variables for connection configuration.
- **Swarm not supported** — Podman does not support Swarm mode. Accessing `.configs`, `.nodes`, or `.services` raises `NotImplementedError`.

## Advanced Topics

**Container Operations**: Lifecycle management, exec, logs, stats, file transfer → [Container Operations](reference/01-container-operations.md)

**Image Management**: Build, pull, push, save, load, tag, prune → [Image Management](reference/02-image-management.md)

**Networks and Volumes**: Network creation, container connectivity, volume lifecycle → [Networks and Volumes](reference/03-networks-volumes.md)

**Pods**: Pod lifecycle, stats, multi-container grouping → [Pods](reference/04-pods.md)

**Manifests, Secrets, Quadlets**: Multi-arch manifests, secret management, systemd quadlet integration → [Manifests, Secrets, and Quadlets](reference/05-manifests-secrets-quadlets.md)

**Configuration and Events**: PodmanConfig, service connections, event streaming → [Configuration and Events](reference/06-configuration-events.md)

**Error Handling**: Exception hierarchy, error classification → [Error Handling](reference/07-error-handling.md)
