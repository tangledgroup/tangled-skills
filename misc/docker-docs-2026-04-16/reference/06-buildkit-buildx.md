# BuildKit and Buildx

## BuildKit

BuildKit is the modern Docker build backend, replacing the legacy builder. It provides:

- Parallel build steps
- Better caching with content-addressable storage
- Mount support during RUN (secrets, SSH, cache)
- Multi-platform builds
- Export to various targets
- Build provenance and attestations

### Enabling BuildKit

Enabled by default in Docker 23.0+. For older versions:
```bash
export DOCKER_BUILDKIT=1
```

Or in daemon.json:
```json
{"features": {"buildkit": true}}
```

### Build Syntax Directive

Specify the Dockerfile frontend version:
```dockerfile
# syntax=docker/dockerfile:1
FROM alpine
```

Use `docker/dockerfile:1` for the latest v1 syntax. BuildKit auto-checks for updates.

## Buildx

Buildx is a CLI plugin that extends `docker build` with BuildKit capabilities.

### Creating and Managing Builders

```bash
docker buildx create --name mybuilder        # Create builder instance
docker buildx ls                             # List builders
docker buildx use mybuilder                  # Switch builder
docker buildx inspect                        # Inspect current builder
docker buildx stop mybuilder                 # Stop builder
docker buildx rm mybuilder                   # Remove builder
```

Driver options:
- `docker` — Default, builds directly in Docker daemon
- `docker-container` — Runs BuildKit in a container (supports multi-platform)
- `remote` — Connects to remote BuildKit instance

### Multi-Platform Builds

Build images for multiple platforms in one command:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .
```

The `--push` flag pushes directly to a registry (required for multi-platform as local storage supports only one platform).

### Build Cache

**Export cache:**
```bash
# To a registry
docker buildx build --cache-to type=registry,ref=myrepo/cache:latest --push .

# To local filesystem
docker buildx build --cache-to type=local,dest=/tmp/cache .

# GitHub Actions cache
docker buildx build --cache-to type=gha .
```

**Import cache:**
```bash
# From a registry
docker buildx build --cache-from type=registry,ref=myrepo/cache:latest .

# From local filesystem
docker buildx build --cache-from type=local,src=/tmp/cache .

# GitHub Actions cache
docker buildx build --cache-from type=gha .
```

**Inline cache (embedded in image):**
```bash
docker buildx build --build-arg BUILDKIT_INLINE_CACHE=1 -t myapp:latest .
```

### Export Targets

```bash
# OCI layout
docker buildx build --output type=oci,dest=/tmp/image.tar .

# Docker archive
docker buildx build --output type=docker,dest=/tmp/image.tar .

# Local directory
docker buildx build --output type=local,dest=/tmp/output .

# Containerd
docker buildx build --output type=containerd,name=myapp:latest .

# Tar to specific path
docker buildx build --output type=tar,dest=/tmp/image.tar .
```

### Build Provenance and Attestations

BuildKit attaches provenance metadata by default (since Docker 24.0):
```bash
# Enable (default)
docker buildx build --provenance=true -t myapp:latest .

# Disable
docker buildx build --provenance=false -t myapp:latest .

# View attestation
docker buildx attest inspect myapp:latest
```

Provenance includes build source, platform, and builder information. Can be verified with `cosign` or similar tools.

### Build Checks

BuildKit performs linting during builds:
```bash
# Enable specific check
docker buildx build --check=SecretsUsedInArgOrEnv .

# Disable all checks
docker buildx build --allow=security.insecure .
```

Common checks:
- `ConsistentInstructionCasing` — Instruction case consistency
- `CopyIgnoredFile` — COPY/ADD of files in .dockerignore
- `DuplicateStageName` — Duplicate build stage names
- `FromAsCasing` — FROM AS keyword casing
- `JSONArgsRecommended` — Use JSON form for CMD/ENTRYPOINT
- `MaintainerDeprecated` — MAINTAINER is deprecated
- `SecretsUsedInArgOrEnv` — Secrets in ARG/ENV
- `StageNameCasing` — Stage name casing consistency
- `UndefinedVar` — Undefined variable references
- `WorkdirRelativePath` — Relative WORKDIR paths

### GitHub Actions Integration

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myapp:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

### LLB Frontend

BuildKit's low-level build representation. Can be used programmatically or via the `docker/buildkit` image for advanced build definitions beyond Dockerfile syntax.
