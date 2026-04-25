---
name: docker-docs-2026-04-16
description: Comprehensive reference for Docker platform including Docker Engine, Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Swarm, Dockerfile syntax, networking, volumes, security, and Docker Hub. Use when building containerized applications, writing Dockerfiles, configuring multi-container stacks with Compose, setting up container orchestration, managing images and registries, or troubleshooting Docker environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026.4.16"
tags:
  - containers
  - docker-engine
  - docker-desktop
  - docker-compose
  - dockerfile
  - buildkit
  - swarm
  - kubernetes
  - container-orchestration
  - container-security
category: devops
external_references:
  - https://docs.docker.com/
  - https://docs.docker.com/build/concepts/dockerfile/
  - https://docs.docker.com/compose/
  - https://docs.docker.com/compose/compose-file/
  - https://docs.docker.com/engine/api/
  - https://docs.docker.com/engine/reference/builder/
  - https://github.com/compose-spec/compose-spec
  - https://github.com/docker/awesome-compose
  - https://github.com/docker/buildx
  - https://github.com/docker/compose
  - https://github.com/docker/docs
  - https://github.com/moby/buildkit/tree/master/frontend/dockerfile
  - https://github.com/moby/moby
---
## Overview
This skill provides comprehensive reference material from the official [Docker documentation](https://docs.docker.com/) repository. It covers the entire Docker platform including Docker Engine, Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Swarm, container networking, storage, security, and Docker Hub.

The Docker documentation is organized into four main sections:
- **Get Started** — Installation guides, core concepts (containers, images, registries), and a hands-on workshop
- **Guides** — In-depth tutorials for common workflows (databases, orchestration, CI/CD, security, AI/ML)
- **Reference** — CLI commands, Dockerfile syntax, Compose file specification, glossary
- **Manuals** — Product-specific documentation (Docker Desktop, Docker Build, Swarm, Engine internals)

## When to Use
Use this skill when:
- Writing or debugging `Dockerfile` instructions
- Configuring multi-container applications with `docker compose`
- Setting up container orchestration (Swarm or Kubernetes)
- Understanding Docker networking drivers (bridge, overlay, host, macvlan, ipvlan, none)
- Managing volumes and storage drivers
- Configuring the Docker daemon (`daemon.json`)
- Working with Docker Build/BuildKit for multi-stage builds and multi-platform images
- Publishing/pulling images to/from registries (Docker Hub or custom)
- Setting up resource constraints (memory limits, CPU limits, cgroups)
- Understanding container security best practices
- Troubleshooting Docker Engine issues

## Core Concepts
### Containers vs. Images vs. Volumes

| Concept | Description |
|---------|-------------|
| **Container** | An isolated process running on the host, with its own filesystem, network, and PID namespace. Created from an image. |
| **Image** | A read-only template with instructions for creating a container. Composed of stacked layers (each layer = one Dockerfile instruction). Immutable once created. |
| **Volume** | Persistent storage managed by Docker, stored outside the container's writable layer. Survives container removal. |
| **Bind Mount** | Maps a host filesystem path into a container. Tightly coupled to the host OS. |

### Container Lifecycle

```
docker pull <image>          # Download image from registry
docker run <image>           # Create and start a new container
docker ps                    # List running containers
docker stop <container>      # Stop a running container
docker start <container>     # Start a stopped container
docker rm <container>        # Remove a stopped container
docker rmi <image>           # Remove an image
```

### Docker Architecture

Docker uses a client-server architecture:
- **Docker Client** (`docker` CLI) — Sends commands to the daemon
- **Docker Daemon** (`dockerd`) — Receives and executes commands, manages objects (images, containers, networks, volumes)
- **REST API** — Interface between the CLI and daemon
- **Registry** — Stores Docker images (Docker Hub is the default)

### Build Architecture (Buildx + BuildKit)

- **Buildx** — The CLI client for running builds. `docker build` is a wrapper around `docker buildx build`.
- **BuildKit** — The server/backend that executes build workloads. Resolves Dockerfile instructions and executes build steps.
- **Builders** — BuildKit daemon instances. Docker Engine creates a default builder automatically.

## Installation / Setup
### Get Docker

Choose the appropriate installation path:

| Platform | Product | Link |
|----------|---------|------|
| Mac | Docker Desktop for Mac | `/desktop/setup/install/mac-install/` |
| Windows | Docker Desktop for Windows | `/desktop/setup/install/windows-install/` |
| Linux | Docker Desktop for Linux | `/desktop/setup/install/linux/` |
| Linux (Engine only) | Docker Engine | `/engine/install/` |

### Docker Desktop vs. Docker Engine

- **Docker Desktop** — A full application including Docker Engine, Docker CLI, Docker Compose, Docker Buildx, Kubernetes, Docker Scout, and a GUI dashboard. Recommended for development.
- **Docker Engine** — The core container runtime + CLI. Installed manually on servers/production. No GUI.

## Advanced Topics
## Advanced Topics

- [Dockerfile Reference](reference/01-dockerfile-reference.md)
- [Compose File Specification](reference/02-compose-file-specification.md)
- [Docker Cli Reference](reference/03-docker-cli-reference.md)
- [Networking Storage Security](reference/04-networking-storage-security.md)
- [Usage Examples](reference/05-usage-examples.md)

