# REST API

## Overview

Podman exposes a RESTful API for programmatic container management. The API has two interfaces:

- **Libpod API** — Podman-native interface with full functionality
- **Compat API** — Docker-compatible interface for tooling that expects the Docker API

The API is accessible via a Unix socket (`podman.sock`) on Linux, or over SSH for remote clients.

## Starting the API Service

```bash
# Run as a foreground service
podman system service

# With timeout (shuts down after idle period)
podman system service --time-out 60

# Bind to TCP (for remote access)
podman system service tcp://0.0.0.0:8080

# Via systemd socket activation (recommended)
systemctl --user enable --now podman.socket
```

The rootless socket listens at `/run/user/${UID}/podman/podman.sock`.

## API Endpoints

### Containers (Libpod)

- `GET /libpod/containers/json` — List containers
- `POST /libpod/containers/create` — Create a container
- `GET /libpod/containers/{name}/json` — Inspect a container
- `POST /libpod/containers/{name}/start` — Start a container
- `POST /libpod/containers/{name}/stop` — Stop a container
- `DELETE /libpod/containers/{name}` — Remove a container
- `POST /libpod/containers/{name}/exec` — Execute command in container

### Containers (Docker Compat)

- `GET /v{version}/containers/json` — List containers
- `POST /v{version}/containers/create` — Create a container
- `GET /v{version}/containers/{id}/json` — Inspect
- `POST /v{version}/containers/{id}/start`
- `POST /v{version}/containers/{id}/stop`
- `DELETE /v{version}/containers/{id}`
- `GET /v{version}/_ping` — Health check

### Images

- `GET /libpod/images/json` — List images
- `POST /libpod/images/pull` — Pull an image
- `POST /libpod/images/build` — Build an image
- `DELETE /libpod/images/{name}` — Remove an image

### Artifacts (Podman 5.6+)

- `GET /libpod/artifacts/json` — List all artifacts
- `GET /libpod/artifacts/{name}/json` — Inspect an artifact
- `POST /libpod/artifacts/pull` — Pull an artifact
- `DELETE /libpod/artifacts/{name}` — Remove an artifact
- `POST /libpod/artifacts/add` — Add files to an artifact
- `POST /libpod/artifacts/{name}/push` — Push to registry
- `GET /libpod/artifacts/{name}/extract` — Extract contents

### System

- `GET /libpod/info` — System information
- `GET /libpod/healthcheck` — Health check
- `GET /v{version}/info` — Compat system info
- `GET /v{version}/_ping` — Compat ping

## Docker Compatibility Improvements

Podman 5.6 improvements:

- Compat Create endpoint accepts `HostConfig.CgroupnsMode` for cgroup namespace mode
- Compat System Info returns `DefaultAddressPools`
- Compat List for Images returns `shared-size` unconditionally
- Compat Inspect for Images no longer returns deprecated `VirtualSize` for API v1.44+
- Compat Ping sets `Builder-Version` to `1`
- Fixed: Compat Delete for Containers with `FORCE=true` now matches Docker behavior (only removes stopped containers)
- Fixed: Container status converted to Docker-compatible statuses in List and Inspect endpoints
- Fixed: Healthcheck timeout properly terminates checks (SIGTERM → SIGKILL after delay)
- Fixed: `application/json` responses no longer HTML-escape content

## Go Bindings

Podman provides Go bindings for the REST API. These can be vendored into applications for programmatic container management. The `podman-py` Python client is also available.

## Security Considerations

- The API socket should be protected with proper file permissions
- For TCP access, use TLS or SSH tunneling
- Rootless API runs with user privileges only
- Healthchecks that exceed timeout are now properly terminated (SIGTERM then SIGKILL)
