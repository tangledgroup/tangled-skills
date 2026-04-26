# Image Management

## Overview

Podman manages OCI and Docker container images through the `podman image` command group. It uses the containers/image library for pulling, pushing, and storing images. Podman delegates image building to Buildah's Go API.

## Core Operations

### Pulling Images

```bash
# Pull from a registry
podman pull nginx:latest

# With pull policy (Podman 5.6+)
podman pull --policy newer myregistry/app:v1

# Search before pulling
podman search nginx
```

### Building Images

```bash
# Build from Containerfile (or Dockerfile)
podman build -t myapp:latest .

# With build context (remote client supported in 5.6+)
podman build --build-context data=/path/to/data -t myapp .

# Control label inheritance (Podman 5.5+)
podman build --inherit-labels=false -t myapp .

# Inspect buildx builder (Docker compat, Podman 5.6+)
podman buildx inspect
```

### Pushing and Saving

```bash
# Push to a registry
podman push myapp:latest quay.io/user/myapp:latest

# Save to docker-archive
podman save -o myapp.tar myapp:latest

# Save in OCI format
podman save -o myapp.oci myapp:latest

# Load from archive
podman load -i myapp.tar
```

### Tagging

```bash
# Add a tag
podman tag myapp:latest myapp:v1.0

# Remove a tag
podman untag myapp:v1.0

# List images
podman images
```

### Inspection and History

```bash
# Inspect image configuration
podman image inspect myapp:latest

# View build history
podman history myapp:latest

# Show filesystem changes
podman image diff myapp:latest

# Print layer hierarchy in tree format
podman image tree myapp:latest
```

### Importing and Signing

```bash
# Import a tarball as an image
podman import myfilesystem.tar myimage:latest

# Sign an image
podman image sign myapp:latest
```

## OCI Artifacts

Podman 5.4+ (stable since 5.6) supports OCI artifacts — non-image content stored in registries:

```bash
# Pull an artifact
podman artifact pull oci-artifact-ref

# Add files to an artifact
podman artifact add myartifact /path/to/file
podman artifact add --append myartifact /another/file
podman artifact add --file-type application/json myartifact config.json

# Inspect artifacts
podman artifact inspect myartifact
podman artifact ls

# Extract artifact contents (Podman 5.5+)
podman artifact extract myartifact /output/path

# Mount artifact into container (Podman 5.5+)
podman run --mount type=artifact,name=myfile,source=myartifact,dst=/data alpine

# Remove artifacts
podman artifact rm myartifact
podman artifact rm --all  # remove all (Podman 5.5+)

# Push artifacts to registry
podman artifact push myartifact registry.io/artifact:tag
```

## Trust Policies

```bash
# Manage image trust policy
podman image trust
```

## Image Security

- Images are verified during pull with signature support
- Trust policies control which registries and signatures are accepted
- Podman supports multiple image formats (OCI, Docker)

## Registry Configuration

Registries are configured in `registries.conf`:

- `/etc/containers/registries.conf` (system-wide)
- `/etc/containers/registries.d/*` (system-wide drops)
- `$HOME/.config/containers/registries.conf` (user-specific)

Authentication is stored in `$XDG_RUNTIME_DIR/containers/auth.json`.

```bash
# Login to a registry
podman login quay.io

# Logout
podman logout quay.io
```

## Image SCP (Podman 5.5+)

Securely copy images between hosts:

```bash
podman image scp myapp:latest user@remote:/path/
```
