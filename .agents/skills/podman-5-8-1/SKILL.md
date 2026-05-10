---
name: podman-5-8-1
description: Comprehensive toolkit for Podman 5.8.1, a daemonless container engine providing Docker-compatible CLI for managing containers, pods, images, volumes, and networks. Supports rootless operation via user namespaces, Kubernetes integration through kube play/generate, systemd declarative management via Quadlet, virtual machine management on Mac/Windows via podman machine, remote client over SSH, REST API with Docker compatibility layer, OCI artifact support, and SQLite-based storage backend. Use when building, running, or managing containers without a daemon, implementing rootless container workflows, orchestrating pods, integrating with Kubernetes YAML, automating with systemd services, configuring container networking via Netavark and pasta, or migrating from Docker.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - containers
  - daemonless
  - rootless
  - oci
  - pods
  - kubernetes
  - quadlet
  - networking
  - podman-machine
category: container-runtime
external_references:
  - https://docs.podman.io/
  - https://github.com/containers/podman
compatibility: Linux native; Mac and Windows require podman machine VM. Go 1.23+ to build. Requires pasta for rootless networking.
---

# Podman 5.8.1

## Overview

Podman (the POD MANager) is a daemonless, open source, Linux native tool for managing OCI containers and container images. It provides a command line interface familiar to anyone who has used Docker — most users can simply alias `docker=podman` without issues. Podman manages the entire container ecosystem including pods, containers, images, and volumes using the libpod library.

Key differentiators from Docker:

- **No daemon** — improved security and lower resource utilization at idle
- **Rootless by design** — containers run as normal users via user namespaces, no setuid binary required
- **Pods support** — groups of containers sharing resources, similar to Kubernetes pods
- **Systemd integration** — declarative container management via Quadlet unit files
- **Remote client** — manage containers on remote Linux hosts over SSH from Mac/Windows/Linux
- **Kubernetes integration** — `kube play` and `kube generate` for bidirectional YAML conversion

Podman uses best-of-breed OCI libraries: crun or runc for runtime, Netavark for networking, pasta for rootless networking, Buildah for image builds, and containers/storage (SQLite backend, BoltDB deprecated in 6.0) for storage.

## When to Use

- Building, running, or managing OCI containers without a background daemon
- Implementing rootless container workflows where users run containers without root privileges
- Deploying container workloads on Mac or Windows via `podman machine` virtual machines
- Managing containers declaratively with systemd via Quadlet unit files
- Converting between Podman containers and Kubernetes YAML with `kube play`/`kube generate`
- Automating container lifecycle management in CI/CD pipelines
- Migrating from Docker to a daemonless alternative (`alias docker=podman`)
- Running containers remotely over SSH from any platform
- Managing OCI artifacts alongside container images
- Configuring complex container networking with Netavark and pasta

## Core Concepts

**Daemonless architecture**: Unlike Docker, Podman has no persistent daemon. Each `podman` command forks a new process. Containers are managed through fork-exec, making the system more resilient — killing the podman process does not affect running containers. Conmon monitors container processes and handles cleanup.

**Rootless containers**: Podman runs containers as a normal user without root privileges. User namespaces map the container's root UID to the host user's UID. The administrator configures `/etc/subuid` and `/etc/subgid` to allocate UID/GID ranges per user. Rootless containers never have more privileges than the launching user.

**Pods**: A pod is a group of containers that share the same network namespace, IPC namespace, and optionally other resources. Pods provide a Kubernetes-like grouping without requiring a full orchestrator. The infra container manages shared resources.

**Quadlet**: Declarative container management using systemd unit files. Quadlet translates `.container`, `.pod`, `.volume`, `.network`, `.image`, and `.build` unit files into Podman commands, enabling containers to be managed as systemd services with automatic restart, dependencies, and lifecycle management.

**Remote client**: Podman on Mac and Windows connects to a Linux backend (managed VM or external server) over SSH. The `podman-remote` binary or `podman --remote` communicates with the Podman REST API exposed via `podman.socket`.

## Installation / Setup

Podman is available on most Linux distributions via package managers (`apt`, `dnf`, `yum`, `zypper`). On Mac and Windows, install from podman.io — it includes a managed VM backend.

For rootless operation, the administrator must:

- Install pasta (rootless networking tool, package name `passt`)
- Configure subordinate UIDs/GIDs in `/etc/subuid` and `/etc/subgid`:

```bash
usermod --add-subuids 100000-165535 --add-subgids 100000-165535 johndoe
```

- Enable linger for persistent rootless socket (optional):

```bash
sudo loginctl enable-linger $USER
```

Configuration files are read in this order (later overrides earlier):

- `/usr/share/containers/containers.conf` → `/etc/containers/containers.conf` → `$HOME/.config/containers/containers.conf`
- `/etc/containers/storage.conf` → `$HOME/.config/containers/storage.conf`
- `/etc/containers/registries.conf` → `/etc/containers/registries.d/*` → `$HOME/.config/containers/registries.conf`

## Usage Examples

Run a simple container:

```bash
podman run --rm -it alpine sh
```

Run with port mapping and volume mount:

```bash
podman run -d --name web -p 8080:80 -v ./data:/data nginx
```

Build an image from a Containerfile:

```bash
podman build -t myapp:latest .
```

Manage pods:

```bash
podman pod create --name mypod --port 8080:80
podman run -d --pod mypod nginx
podman run -d --pod mypod redis
```

Rootless container with keep-id namespace:

```bash
podman run --rm --userns=keep-id -v $PWD:/work alpine ls -la /work
```

Kubernetes play:

```bash
podman kube play app.yaml
podman kube down app.yaml
```

## Advanced Topics

**Rootless Containers**: Detailed setup, user namespace configuration, volume semantics, and known limitations → [Rootless Containers](reference/01-rootless-containers.md)

**Pods and Pod Management**: Creating pods, shared namespaces, lifecycle management, pod stats → [Pod Management](reference/02-pod-management.md)

**Networking with Netavark and Pasta**: Bridge networks, pasta rootless networking, DNS, subnet pools, network options → [Networking](reference/03-networking.md)

**Quadlet and Systemd Integration**: Declarative container management via systemd unit files, `.container`, `.pod`, `.volume` units, service generation → [Quadlet and Systemd](reference/04-quadlet-systemd.md)

**Remote Client and podman machine**: Managing containers over SSH, Mac/Windows VM backends, connection configuration, libkrun/applehv providers → [Remote Client and Machine](reference/05-remote-client-machine.md)

**Kubernetes Integration**: `kube play`, `kube generate`, `kube down`, bidirectional YAML conversion, CDI device support → [Kubernetes Integration](reference/06-kubernetes-integration.md)

**Container Image Management**: Building, pulling, pushing, tagging, importing, OCI artifacts, trust policies → [Image Management](reference/07-image-management.md)

**Volumes and Storage**: Named volumes, bind mounts, volume plugins, storage drivers (overlay, VFS), SQLite backend → [Volumes and Storage](reference/08-volumes-storage.md)

**REST API and Docker Compatibility**: Libpod API, Docker-compatible API endpoints, healthchecks, service socket → [REST API](reference/09-rest-api.md)

**Command Reference**: Summary of all major Podman command groups — container, image, pod, network, volume, system, machine, quadlet, kube, artifact → [Command Reference](reference/10-command-reference.md)
