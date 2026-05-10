---
name: docker-docs-2026-04-16
description: Comprehensive reference for Docker platform including Docker Engine,
  Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Swarm, Dockerfile
  syntax, networking, volumes, security, and Docker Hub. Use when building containerized
  applications, writing Dockerfiles, configuring multi-container stacks with Compose,
  setting up container orchestration, managing images and registries, or troubleshooting
  Docker environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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

# Docker Platform Reference (2026-04-16)

## Overview

Docker is a platform for building, shipping, and running containerized applications. It consists of several integrated components:

- **Docker Engine** — The core container runtime (daemon + CLI) that builds images, runs containers, manages networks and volumes
- **Docker Desktop** — Application for Mac, Windows, and Linux providing Docker Engine, CLI, Compose, BuildKit, Extensions, Kubernetes integration, and observability tools
- **Docker Compose** — Tool for defining and running multi-container applications using YAML configuration files (Compose Specification)
- **Docker Buildx / BuildKit** — Advanced build capabilities including multi-platform images, cache export/import, build provenance, LLB frontend, and GitHub Actions integration
- **Docker Hub** — Default public registry for image distribution with automated builds, webhooks, and vulnerability scanning
- **Docker Contexts** — Manage connections to multiple Docker Engine instances from a single client

## When to Use

- Writing or debugging Dockerfiles
- Configuring multi-container applications with Docker Compose
- Setting up container networking (bridge, host, overlay, macvlan)
- Managing persistent storage with volumes and bind mounts
- Building multi-platform container images
- Deploying containers with Swarm orchestration
- Working with Docker Engine API programmatically
- Troubleshooting Docker environments
- Configuring Docker Desktop features and extensions
- Implementing container security best practices

## Core Concepts

**Containers** are isolated, lightweight runtime instances of images. They package application code, dependencies, and configuration into a standardized unit that runs consistently across environments.

**Images** are read-only templates containing the filesystem layers and metadata needed to run containers. Images are built from Dockerfiles and stored in registries.

**Dockerfile** is a text file with instructions for building an image. Each instruction creates a layer, enabling caching and efficient rebuilds.

**Compose Specification** defines multi-container applications as YAML files. Services, networks, volumes, configs, and secrets are declared declaratively. Compose v2 (v1.27.0+) implements the unified specification, merging legacy 2.x and 3.x formats.

**BuildKit** is the modern build backend that replaces the legacy builder. It provides parallel builds, better caching, SSH/socket mounting during builds, multi-platform support, and export to various cache backends. Enabled by default in recent Docker versions.

## Advanced Topics

**Dockerfile Reference**: Complete instruction reference including FROM, RUN, COPY, ADD, CMD, ENTRYPOINT, ENV, ARG, EXPOSE, VOLUME, USER, WORKDIR, ONBUILD, STOPSIGNAL, HEALTHCHECK, SHELL, parser directives, BuildKit mount syntax, and here-documents → [Dockerfile Reference](reference/01-dockerfile-reference.md)

**Compose File Reference**: Services attributes (image, build, command, depends_on, ports, volumes, environment, networks, deploy, healthcheck, secrets, configs), top-level elements (networks, volumes, configs, secrets, profiles, include, extend), interpolation, merge rules → [Compose File Reference](reference/02-compose-file-reference.md)

**Docker Compose CLI**: Commands for managing multi-container applications including up/down/build/logs/exec/ps/pull/push/run/start/stop/restart/fkill/kill/events/top/wait/version, with profiles, project names, and environment file support → [Docker Compose CLI](reference/03-compose-cli.md)

**Docker Engine & CLI Reference**: Core Docker commands (container, image, volume, network, buildx, compose, context, system, swarm), daemon configuration, storage drivers, logging drivers, proxy configuration → [Docker Engine and CLI](reference/04-engine-cli-reference.md)

**Networking & Storage**: Network drivers (bridge, host, overlay, macvlan, ipvlan, none), port publishing, iptables/nftables integration, volumes vs bind mounts vs tmpfs, storage drivers (overlay2, btrfs, zfs, vfs) → [Networking and Storage](reference/05-networking-storage.md)

**BuildKit & Buildx**: Multi-platform builds, cache backends (registry, local, gha, s3), build provenance and attestations, GitHub Actions integration, LLB frontend, build checks, export targets → [BuildKit and Buildx](reference/06-buildkit-buildx.md)

**Swarm & Orchestration**: Swarm mode for container orchestration with service discovery, load balancing, rolling updates, secrets management, and distributed logging → [Swarm Orchestration](reference/07-swarm-orchestration.md)

**Docker APIs**: Engine API (RESTful, versions v1.24–v1.54), Docker Hub API, Registry API (OCI Distribution spec), Extensions SDK for Docker Desktop plugins → [Docker APIs](reference/08-docker-apis.md)
