# Docker APIs

## Engine API

The Docker Engine exposes a RESTful API over a Unix socket (`/var/run/docker.sock`) or TCP. Current versions support API v1.24 through v1.54.

### Base URL

```
http://localhost/v{version}/
```

Or with TCP:
```
http://host:port/v{version}/
```

### Authentication

Unix socket (default on Linux): no authentication required for socket access.
TCP: Use TLS certificates or API keys.

### Key Endpoints

**Images:**
- `GET /images/json` — List images
- `GET /images/{name}/json` — Inspect image
- `POST /images/create` — Create image (pull or push)
- `DELETE /images/{name}` — Remove image
- `GET /images/{name}/history` — Image history
- `POST /build` — Build image

**Containers:**
- `GET /containers/json` — List containers
- `POST /containers/create` — Create container
- `POST /containers/{id}/start` — Start container
- `POST /containers/{id}/stop` — Stop container
- `POST /containers/{id}/kill` — Kill container
- `POST /containers/{id}/exec` — Create exec instance
- `POST /containers/{id}/archive` — Get/put archive
- `GET /containers/{id}/logs` — Container logs
- `GET /containers/{id}/json` — Inspect container
- `DELETE /containers/{id}` — Remove container

**Volumes:**
- `GET /volumes` — List volumes
- `POST /volumes` — Create volume
- `GET /volumes/{name}` — Inspect volume
- `DELETE /volumes/{name}` — Remove volume

**Networks:**
- `GET /networks` — List networks
- `POST /networks/create` — Create network
- `GET /networks/{id}` — Inspect network
- `POST /networks/{id}/connect` — Connect container
- `POST /networks/{id}/disconnect` — Disconnect container
- `DELETE /networks/{id}` — Remove network

**System:**
- `GET /info` — System information
- `GET /version` — API version
- `GET /events` — Real-time events (SSE)
- `GET /system.df` — Disk usage

### API Versioning

The API version is specified in the URL path. Docker supports multiple versions simultaneously. Check the latest version with:
```bash
docker version --format '{{.ApiVersion}}'
```

## Docker Hub API

Docker Hub provides a REST API for managing repositories, automated builds, and user data.

### Authentication

OAuth2 or basic auth with username/password.

### Key Endpoints

- `GET /v2-repositories/{username}/{repo}/tags/` — List repository tags
- `GET /v2-repositories/{username}/{repo}/tags/{tag}` — Tag details
- `GET /v2/user/{username}/repos/` — User repositories
- `POST /v2/repo/{namespace}/{repo}/trigger-service/` — Trigger automated build

## Registry API (OCI Distribution)

Docker uses the OCI Distribution Specification for image registry communication.

### Authentication

Token-based authentication via authorization service:
```
GET /v2/
WWW-Authenticate: Bearer realm="https://auth.docker.io/token",service="registry.docker.io",scope="repository:*:pull"
```

### Key Operations

**Pull:**
```
HEAD /v2/<name>/manifests/<reference>
GET /v2/<name>/blobs/<digest>
```

**Push:**
```
POST /v2/<name>/blobs/uploads/
PUT /v2/<name>/blobs/uploads/<uuid>?digest=<digest>
PUT /v2/<name>/manifests/<reference>
```

**Delete:**
```
DELETE /v2/<name>/manifests/<digest>
```

## Extensions SDK

Docker Desktop provides an Extensions SDK for building plugins with:
- Backend services (Node.js)
- UI components (React)
- CLI commands
- Docker integration via `docker` API

Key interfaces:
- `Extension` — Main extension definition
- `BackendV0` — Backend service interface
- `Docker` — Docker API access
- `Exec` — Command execution
- `HttpService` — HTTP server

## DVP Data API

Docker Data Visualization Platform API for metrics and observability data.
