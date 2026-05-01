---
name: crun-1-27-1
description: Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high performance. Use when deploying containers via podman, building container orchestration tools, checkpointing/restoring containers with CRIU, running WebAssembly workloads, or needing faster container startup than runc provides.
version: "1.27.1"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - oci-runtime
  - containers
  - podman
  - checkpointing
  - criu
  - wasi
  - webassembly
  - cgroups
category: devops
external_references:
  - https://github.com/containers/crun
  - https://github.com/containers/crun/blob/main/Documentation/crun.md
---

# crun 1.27

## Overview

crun is a fast and lightweight OCI container runtime fully written in C. It conforms to the [OCI Container Runtime Specification](https://github.com/opencontainers/runtime-spec) and is designed as a lower-level alternative to runc (which is written in Go). crun can also be used as a library (`libcrun`) that can be embedded directly into programs without requiring an external process for managing OCI containers.

crun is significantly faster than runc and has a much lower memory footprint. Benchmarks show approximately 50% faster container startup times (100 sequential `/bin/true` runs: 1.69s vs 3.34s). Its low resource usage allows running containers under extremely tight memory limits — as low as 512KB where runc fails at 4MB.

## When to Use

- Running containers via Podman (crun is the default runtime on many distributions)
- Needing faster container startup and lower memory overhead than runc
- Checkpointing and restoring containers with CRIU (live migration, state preservation)
- Running WebAssembly/WASI workloads natively inside containers
- Building container orchestration tools that embed `libcrun` directly
- Deploying containers in resource-constrained environments (edge, embedded)
- Working with cgroup v2 systems requiring automatic v1-to-v2 conversion

## Changelog (1.27.0 → 1.27.1)

- **linux**: fix bind mount propagation regression — mounts hot-plugged after container start (e.g. USB drives) were invisible or owned by nobody inside the container because propagation peer groups were destroyed
- **utils**: fix AppArmor profile inside a user namespace
- **cgroup**: fix recursive cgroup cleanup failure that could cause EBADF errors when deleting containers with sub-cgroups
- **libcrun**: do not check the cgroup file system type when cgroups are disabled with `--cgroup-manager=disabled`, fixing startup failures on systems where `/sys/fs/cgroup` is not a standard mount (e.g. Android with Linux Deploy)
- **libcrun**: fix "unlink /dev/console: Read-only file system" error when running containers with `--read-only`
- **krun**: add support for passt-based networking in microVMs via the `krun.use_passt` annotation
- **krun**: ignore RAM configurations below 128MB

## Core Concepts

**OCI Runtime**: crun implements the OCI runtime specification, meaning it works with any OCI-compliant bundle (a directory containing `config.json` and a root filesystem). It is interoperable with container managers like Podman, CRI-O, and containerd.

**C-based Architecture**: Unlike runc which is written in Go and re-executes itself, crun is entirely in C. This eliminates the overhead of Go runtime initialization and enables tighter integration with Linux syscalls for container setup (namespaces, cgroups, mounts).

**libcrun**: The shared library component that can be built with `./configure --enable-shared`. It provides a C API for managing OCI containers programmatically, including Lua bindings.

**Cgroup Management**: crun supports both cgroupfs and systemd backends for resource control. On cgroup v2 systems, it automatically converts cgroup v1 OCI configurations using well-defined formulas for memory, CPU, blkio, and other controllers.

## Global Options

- `--debug` — produce verbose output
- `--log=BACKEND:SPECIFIER` — set log destination (`file:PATH`, `journald:IDENTIFIER`, `syslog:IDENTIFIER`). Default is `file:`.
- `--log-format=FORMAT` — log format: `text` (default) or `json`
- `--log-level=LEVEL` — log level: `debug`, `warning`, or `error` (default: `error`)
- `--no-pivot` — use `chroot(2)` instead of `pivot_root(2)` (not safe, avoid if possible)
- `--root=DIR` — override the state directory (default: `/run/crun` as root, `$XDG_RUNTIME_DIR/crun` for unprivileged users)
- `--systemd-cgroup` / `--cgroup-manager=MANAGER` — use systemd for cgroups. Values: `cgroupfs`, `systemd`, `disabled`

## Commands

- **create** — create a container (detached from process, requires subsequent `start`)
- **run** — create and immediately start a container
- **delete** — remove container definition (`--force` to delete running containers, `--regex` for pattern matching)
- **exec** — execute a command in a running container
- **list** — list known containers (`-q` / `--quiet` for IDs only)
- **kill** — send signal to container init process (default: SIGTERM, `--all` for all processes)
- **ps** — show processes in a container (`--format=table|json`)
- **spec** — generate an OCI `config.json` (`--rootless` for unprivileged, `-b DIR` for bundle path)
- **start** — start a previously created container (cannot be started multiple times)
- **state** — output container state as JSON
- **pause** / **resume** — pause and resume all processes in the container
- **update** — update container resource constraints (memory, CPU, pids, etc.)
- **checkpoint** — checkpoint a running container using CRIU
- **restore** — restore a container from a CRIU checkpoint
- **mounts add** / **mounts remove** — dynamically add or remove mounts from a running container (experimental)

## Usage Examples

Run a container with podman using crun:

```bash
podman run --rm fedora echo "hello from crun"
```

Generate an OCI spec for rootless containers:

```bash
crun spec --rootless -b /path/to/bundle
```

Create and start a container in two steps:

```bash
crun create -b /path/to/bundle my-container
crun start my-container
```

Execute a command inside a running container:

```bash
crun exec --tty -u 0:0 my-container /bin/bash
```

Update memory limit on a running container:

```bash
crun update --memory=536870912 my-container
```

## Advanced Topics

**CLI Reference**: Complete command options for create, run, exec, checkpoint, restore, and more → [CLI Reference](reference/01-cli-reference.md)

**Cgroup Configuration**: cgroup v2 support, automatic v1-to-v2 conversion formulas, memory/CPU/blkio/pids controllers → [Cgroup Configuration](reference/02-cgroup-configuration.md)

**OCI Extensions**: crun-specific annotations for seccomp, SELinux, systemd integration, mount options, idmapped mounts, and handlers → [OCI Extensions](reference/03-oci-extensions.md)

**Checkpoint and Restore**: CRIU integration for live migration with pre-dump, TCP handling, and cgroup management modes → [Checkpoint and Restore](reference/04-checkpoint-restore.md)

**WebAssembly / WASI**: Running wasm workloads natively with wasmedge, wasmer, wasmtime, and wamr runtimes → [WebAssembly Support](reference/05-webassembly-support.md)
