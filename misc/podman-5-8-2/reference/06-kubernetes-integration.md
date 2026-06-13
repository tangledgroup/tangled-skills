# Kubernetes Integration

## Overview

Podman provides bidirectional conversion between Podman containers/pods and Kubernetes YAML. This enables testing Kubernetes deployments locally and generating Kubernetes manifests from running Podman workloads.

The kube commands focus on simplifying the process of moving containers between Podman and Kubernetes environments. Podman does not replicate `kubectl` — once workloads are deployed to a cluster, use `kubectl`.

## Commands

### podman kube play

Create containers, pods, and volumes from Kubernetes YAML:

```bash
# Deploy from a YAML file
podman kube play app.yaml

# Deploy with log level
podman kube play --log-level debug app.yaml
```

The `play` command automatically starts containers. It supports:

- Pods, Deployments, Services, ConfigMaps, Secrets, Volumes
- Container Device Interface (CDI) devices (Podman 5.4+)
- CPU and memory node pinning via annotations (Podman 5.6+):
  - `io.podman.annotations.cpuset/$ctrname` — restrict to specific CPU cores
  - `io.podman.annotations.memory-nodes/$ctrname` — restrict to specific memory nodes
- PID limit preservation via annotation (Podman 5.5+):
  - `io.podman.annotation.pids-limit/$containername`
- Stop signal via `lifecycle.stopSignal` in Pod YAML (Podman 5.6+)

### podman kube generate

Generate Kubernetes YAML from running containers or pods:

```bash
# Generate YAML from a container
podman kube generate mycontainer > deployment.yaml

# Generate YAML from a pod
podman kube generate mypod > pod.yaml
```

This creates valid Kubernetes manifests that can be applied to a cluster. Volume mount subpaths are correctly preserved (fixed in Podman 5.5).

### podman kube down

Remove containers and pods created by `kube play`:

```bash
podman kube down app.yaml
```

### podman kube apply

Apply Kubernetes YAML to a Kubernetes cluster (requires cluster access):

```bash
podman kube apply app.yaml
```

## Annotations

Podman supports several custom annotations in Kubernetes YAML:

- `io.podman.annotations.cpuset/$ctrname` — CPU pinning
- `io.podman.annotations.memory-nodes/$ctrname` — Memory node pinning
- `io.podman.annotation.pids-limit/$containername` — PID limit preservation

## Limitations

- Podman kube commands are for local testing and manifest generation, not cluster management
- Use `kubectl` for managing workloads in actual Kubernetes clusters
- Not all Kubernetes resource types are supported
- CDI devices require compatible hardware and drivers
