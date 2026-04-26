# Compose Specification

The Compose Specification defines a developer-centric, platform-agnostic standard for describing container-based applications in YAML. Podman Compose implements this specification with Podman as the backend runtime.

## File Naming

Default compose file names (checked in order):
- `compose.yaml` (preferred)
- `compose.yml`
- `docker-compose.yaml` (backward compatibility)
- `docker-compose.yml` (backward compatibility)

Override with `-f` flag:

```bash
podman-compose -f staging.yaml up
```

## Top-Level Elements

A compose file defines these top-level keys:

- **`services`** (required) — Map of service definitions
- **`networks`** — Named networks for inter-service communication
- **`volumes`** — Named volumes for persistent data
- **`configs`** — Configuration files mounted into containers
- **`secrets`** — Sensitive data mounted as files
- **`name`** — Project name override
- **`version`** (obsolete) — Kept for backward compatibility only

## Networks

Named networks isolate service communication. Services not connected to a shared network cannot communicate with each other.

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

Key attributes:
- `driver` — Network driver (`bridge`, `macvlan`, etc.)
- `internal` — When `true`, creates an externally isolated network (no external access)
- `external` — When `true`, lifecycle is managed outside compose; compose won't create it
- `name` — Custom name, not scoped with project name
- `ipam` — Custom IPAM configuration with subnet, gateway, and IP range
- `enable_ipv6` — Enable IPv6 address assignment
- `attachable` — Allow standalone containers to attach
- `labels` — Metadata as key-value pairs

IPAM example:

```yaml
networks:
  appnet:
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.5.254
```

## Volumes

Named volumes provide persistent storage managed by the container engine.

```yaml
volumes:
  db-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=10.40.0.199,nolock,soft,rw
      device: ":/docker/example"
```

Key attributes:
- `driver` — Volume driver (default: `local`)
- `driver_opts` — Driver-specific options
- `external` — Pre-existing volume managed outside compose
- `name` — Custom volume name
- `labels` — Metadata

## Configs

Configs mount non-sensitive configuration files into containers. Mounted read-only at `/<config-name>` by default.

```yaml
configs:
  httpd-config:
    file: ./httpd.conf
  app-config:
    content: |
      debug=${DEBUG}
      app.name=${COMPOSE_PROJECT_NAME}
```

Sources:
- `file` — Content from a local file
- `content` — Inline content with variable interpolation
- `environment` — Value from an environment variable
- `external: true` — Lookup from platform (not managed by compose)

## Secrets

Secrets are configs focused on sensitive data. Mounted read-only at `/run/secrets/<secret-name>`.

```yaml
secrets:
  server-cert:
    file: ./server.cert
  api-token:
    environment: "OAUTH_TOKEN"
  external-key:
    external: true
    name: "${CERTIFICATE_KEY}"
```

At the service level, secrets support long syntax for fine-grained control:

```yaml
services:
  web:
    secrets:
      - source: server-cert
        target: server.crt
        uid: "103"
        gid: "103"
        mode: 0o440
```

## Fragments (Anchors and Aliases)

YAML anchors (`&`) and aliases (`*`) reduce repetition:

```yaml
services:
  web:
    environment: &env
      TZ: utc
      PORT: "80"
  api:
    environment:
      <<: *env
      PORT: "8080"
```

Merge key (`<<`) applies anchor values then overrides. Only works with mappings, not sequences.

## Extensions

Fields prefixed with `x-` are silently ignored by compose, allowing custom metadata:

```yaml
x-my-metadata:
  author: team@example.com
  version: "1.0"
```

## Merge

Multiple compose files can be combined. Later files override earlier ones:

```bash
podman-compose -f compose.yaml -f compose.override.yaml up
```

- Mappings: keys in later files override earlier keys
- Lists: items are appended
- Relative paths: resolved from the first compose file's directory

## Include

Reuse other compose files as dependencies:

```yaml
include:
  - ./common/compose.yaml
  - path: ./monitoring/compose.yaml
    project_name: monitoring
```
