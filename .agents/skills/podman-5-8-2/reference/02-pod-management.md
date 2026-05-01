# Pod Management

## Overview

A pod is a group of containers that share resources and are managed together, similar to Kubernetes pods. Containers in a pod share the same network namespace (they can communicate via `localhost`), IPC namespace, and optionally UTS namespace.

The infra container manages shared networking and lifecycle for the pod. Since Podman 5.5, the default infra uses a root filesystem with only the `catatonit` binary instead of a pause image.

## Creating Pods

```bash
# Create a pod with port mappings
podman pod create --name myapp --port 8080:80 --port 8443:443

# Create a pod with a specific hostname
podman pod create --name myapp --hostname app-host

# Create a pod with shared memory size
podman pod create --name myapp --shm-size 512m
```

## Running Containers in Pods

```bash
# Add containers to an existing pod
podman run -d --name web --pod myapp nginx
podman run -d --name cache --pod myapp redis

# Create and run in one step
podman run -d --pod new:myapp nginx
```

## Pod Lifecycle

```bash
# List pods
podman pod ps

# Start/stop/restart all containers in a pod
podman pod start myapp
podman pod stop myapp
podman pod restart myapp

# Pause/unpause all containers in a pod
podman pod pause myapp
podman pod unpause myapp

# View pod logs (aggregated from all containers)
podman pod logs myapp

# View resource usage for all containers in the pod
podman pod stats myapp

# Kill processes in all containers
podman pod kill --signal SIGTERM myapp

# Inspect pod configuration
podman pod inspect myapp

# Remove a stopped pod and its containers
podman pod rm myapp
```

## Pod Networking

Containers within a pod share the same network namespace. They communicate via `localhost` on mapped ports:

- Container A binds to port 80
- Container B can reach it at `localhost:80`
- External traffic reaches the pod through `--port` mappings defined on the pod

## Pod Cloning

```bash
# Create a copy of an existing pod
podman pod clone --name myapp-copy myapp
```

## Exit Policies and Labels (Podman 5.6+)

Pods support exit policies and labels, configurable via Quadlet `.pod` units with `ExitPolicy=` and `Label=` keys.

## Container Stop Order

In Podman 5.5+, containers in pods are stopped in dependency order, with the infra container stopping last. This prevents application containers from losing networking before graceful shutdown completes.
