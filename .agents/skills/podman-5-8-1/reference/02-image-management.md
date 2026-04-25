# Podman Image Management

This reference covers comprehensive image workflows including pulling, pushing, building, registry authentication, multi-architecture images, and image signing.

## Basic Image Operations

### Pull Images

```bash
# Pull latest tag (default)
podman pull fedora

# Pull specific tag
podman pull fedora:39

# Pull from specific registry
podman pull registry.fedoraproject.org/fedora:39
podman pull quay.io/podman/stable:latest

# Pull with authentication
podman login registry.example.com
podman pull registry.example.com/private/image:latest
```

### List Images

```bash
# All images
podman images

# Specific repository
podman images fedora

# Show digests
podman images --digests

# Dangling images only (untagged)
podman images -f "dangling=true"

# Before specific date
podman images -f "before=fedora:latest"

# Output formats
podman images --format table "{{.Repository}}\t{{.Tag}}\t{{.Size}}"
podman images --format json
```

### Remove Images

```bash
# Remove by name
podman rmi fedora:39

# Remove by ID
podman rmi abc123def456

# Force remove (even if in use)
podman rmi -f fedora:39

# Remove all images
podman rmi -a

# Remove dangling images only
podman image prune

# Remove all unused images
podman image prune -a
```

## Image Building

### Basic Build

```bash
# Build from current directory (looks for Containerfile)
podman build -t myapp:latest .

# Build from specific Containerfile
podman build -f Containerfile.prod -t myapp:prod .

# Build with context path
podman build -f ./docker/Dockerfile -t myapp .

# Build and clean up automatically
podman build --rm -t myapp .
```

### Containerfile Example

```dockerfile
# Use multi-stage build for smaller images
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Final stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Build with Arguments

```bash
# Pass build arguments
podman build --build-arg VERSION=1.0 \
  --build-arg ENV=production \
  -t myapp:latest .

# Containerfile with ARG
# ARG VERSION=0.1
# ARG ENV=development
# LABEL version="${VERSION}" env="${ENV}"
```

### Build Optimization

```bash
# Use squash to reduce layers (slower but smaller)
podman build --squash -t myapp .

# No cache for fresh build
podman build --no-cache -t myapp .

# Keep intermediate containers for debugging
podman build --rm=false -t myapp .

# Parallel builds (faster on multi-core)
podman build --parallel -t myapp .
```

### Build Context

```bash
# Use .dockerignore to exclude files
cat > .dockerignore << 'EOF'
.git
node_modules
*.md
.DS_Store
EOF

# Build with subdirectory context
podman build -f subdir/Containerfile -t myapp subdir/

# Build from URL (Git repository)
podman build -t myapp https://github.com/user/repo.git#main
```

## Image Inspection

### View Image Details

```bash
# Full inspection JSON
podman inspect fedora:39

# Specific fields
podman inspect --format '{{.Id}}' fedora:39
podman inspect --format '{{.Config.Cmd}}' fedora:39
podman inspect --format '{{json .Config.Env}}' fedora:39

# View labels
podman inspect --format '{{json .Config.Labels}}' fedora:39

# View environment variables
podman inspect --format '{{range .Config.Env}}{{.}}\n{{end}}' fedora:39
```

### Image History

```bash
# Layer history
podman history fedora:39

# Detailed history
podman history --no-trunc fedora:39

# Specific layer info
podman history --format table "{{.ID}}\t{{.Comment}}\t{{.Size}}" fedora:39
```

### Image Size Analysis

```bash
# Show size per layer
podman image inspect --format '{{range .RootFS.Layers}}{{.}} \n{{end}}' fedora:39

# Compare image sizes
podman images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -k2
```

## Registry Authentication

### Login to Registries

```bash
# Docker Hub
podman login

# Quay.io
podman login quay.io

# Private registry
podman login registry.example.com

# With credentials
podman login -u username -p password registry.example.com

# With password from stdin (more secure)
podman login -u username registry.example.com <<< "password"
```

### Manage Credentials

```bash
# View stored credentials
cat $XDG_RUNTIME_DIR/containers/auth.json

# Use custom auth file
podman --authfile=/path/to/auth.json login registry.example.com

# Logout from registry
podman logout registry.example.com

# Logout from all registries
podman logout -a
```

### Registry Configuration

Edit `~/.config/containers/registries.conf`:

```ini
unqualified-search-registries = ["docker.io", "quay.io"]

[[registry]]
prefix = "registry.example.com"
location = "private-registry"
verify = true

[[registry]]
prefix = "internal.registry"
location = "registry.internal:5000"
verify = false  # For self-signed certs
```

### Insecure Registries

```bash
# Add to registries.conf for unencrypted registry
[[registry]]
prefix = "insecure-registry.local"
location = "insecure-registry.local:5000"
insecure = true
```

## Push Images

### Push to Registry

```bash
# Tag and push
podman tag myapp:latest registry.example.com/myapp:latest
podman push registry.example.com/myapp:latest

# Push with authentication
podman login registry.example.com
podman push registry.example.com/myapp:latest

# Push to multiple registries
podman push --all-tags docker://quay.io/user/myapp docker://registry.example.com/myapp
```

### Push Formats

```bash
# Default OCI format
podman push myapp:latest docker://registry.example.com/myapp:latest

# Docker V2S2 format (for older registries)
podman push --format docker myapp:latest docker://registry.example.com/myapp:latest

# OCI layout format
podman push myapp:latest oci:/path/to/image
```

### Multi-Arch Push

```bash
# Create manifest list
podman manifest create myapp:multi \
  myapp:amd64 \
  myapp:arm64

# Annotate architectures
podman manifest annotate myapp:multi myapp:amd64 --arch amd64 --os linux
podman manifest annotate myapp:multi myapp:arm64 --arch arm64 --os linux

# Push manifest list
podman manifest push myapp:multi docker://registry.example.com/myapp:latest
```

## Image Import/Export

### Save Images

```bash
# Save to OCI archive (default)
podman save fedora:39 -o fedora.tar

# Save as Docker format
podman save --format docker fedora:39 -o fedora-docker.tar

# Save multiple images
podman save fedora:39 ubuntu:22.04 -o multi.tar

# Save to directory
podman save --format docker-dir fedora:39 -o /tmp/fedora-image
```

### Load Images

```bash
# Load from OCI archive
podman load -i fedora.tar

# Load from Docker archive
podman load --input fedora-docker.tar

# Load from directory
podman load --input dir:/tmp/fedora-image
```

### Import Tarball as Image

```bash
# Import filesystem tarball
podman import http://example.com/filesystem.tar myimage:latest

# Import with comment
podman import --change='CMD ["/bin/bash"]' filesystem.tar myimage:latest

# Import from URL
podman import https://example.com/backup.tar backup-image:latest
```

### Export Container as Image

```bash
# Commit container to image
podman commit mycontainer myimage:custom

# Commit with changes
podman commit \
  --change='ENV VERSION=1.0' \
  --change='CMD ["/app/start.sh"]' \
  mycontainer myimage:custom

# Commit with author and message
podman commit \
  --author "Dev Team <dev@example.com>" \
  --message "Added custom configuration" \
  mycontainer myimage:custom
```

## Multi-Architecture Images

### Build for Different Architectures

```bash
# Build for specific architecture
podman build --arch arm64 -t myapp:arm64 .
podman build --arch amd64 -t myapp:amd64 .

# Run with architecture override
podman run --arch arm64 fedora uname -m
```

### Cross-Platform Builds

```bash
# Using qemu-user-static for testing
podman run --rm --arch arm64 fedora:39 /bin/bash -c "uname -a"

# Build manifest with multiple architectures
podman manifest create myapp:v1.0 \
  localhost/myapp:v1.0-amd64 \
  localhost/myapp:v1.0-arm64

podman manifest annotate myapp:v1.0 \
  localhost/myapp:v1.0-amd64 \
  --arch amd64 --os linux

podman manifest annotate myapp:v1.0 \
  localhost/myapp:v1.0-arm64 \
  --arch arm64 --os linux
```

### Push Multi-Arch Manifest

```bash
# Push individual architectures first
podman push localhost/myapp:v1.0-amd64 quay.io/user/myapp:v1.0-amd64
podman push localhost/myapp:v1.0-arm64 quay.io/user/myapp:v1.0-arm64

# Push manifest list
podman manifest push myapp:v1.0 quay.io/user/myapp:v1.0
```

## Image Signing

### Setup Signing Keys

```bash
# Generate GPG key pair
gpg --gen-key

# Export public key
gpg --armor --export keyid > pubkey.asc

# Import signing key into Podman
podman pull gpgpublickey:keyid@quay.io/user/pubkey:/path/to/pubkey.asc
```

### Sign Images

```bash
# Sign image with GPG
podman sign --signature-store /tmp/sigstore fedora:39

# Sign and push signature
podman sign --push --signature-store /tmp/sigstore fedora:39

# Sign specific digest
podman sign sha256:abc123def456...
```

### Verify Signatures

```bash
# Import public keys for verification
podman push gpgpublickey:keyid@docker.io/library/fedora:/path/to/pubkey.asc

# Verify image signature
podman verify fedora:39

# Verify specific signature file
podman verify --signature /tmp/image.json.signature
```

### Policy Configuration

Create `~/.config/containers/signature/policy.json`:

```json
{
  "default": ["reject"],
  "transports": {
    "docker": {
      "registry.example.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-example"
        }
      ]
    }
  }
}
```

## Image Tags

### Tag Management

```bash
# Add tag to image
podman tag fedora:39 myregistry/fedora:custom

# List tags for image
podman images --format "{{.Repository}}:{{.Tag}}" | grep fedora

# Remove tag (untag)
podman untag myregistry/fedora:custom

# Bulk tag operations
for tag in 38 39 40; do
  podman tag fedora:$tag myregistry/fedora:$tag
done
```

### Tag Best Practices

```bash
# Use semantic versioning
podman tag myapp:latest myregistry/myapp:1.2.3
podman tag myapp:latest myregistry/myapp:1.2
podman tag myapp:latest myregistry/myapp:1

# Use digest for immutability
podman tag myapp@sha256:abc123... myregistry/myapp:1.2.3-pin

# Avoid using :latest in production
# Prefer specific versions or digests
```

## Image Pruning

### Clean Up Images

```bash
# Remove dangling images (untagged)
podman image prune

# Remove all unused images
podman image prune -a

# Remove images not used by containers
podman image prune --filter "until=24h"

# Dry run to see what would be removed
podman image prune --dry-run

# Remove specific image and unused parents
podman rmi --prune fedora:39
```

### Storage Management

```bash
# Check storage usage
podman system df

# Detailed storage info
podman system df -v

# Inspect storage driver
podman info --format '{{.Storage.Driver}}'
```

## Common Patterns

### Development Workflow

```bash
# Build with latest code
podman build --no-cache -t myapp:dev .

# Run with volume mounts
podman run -it --rm \
  -v $(pwd):/app \
  -w /app \
  myapp:dev \
  npm run dev

# Push to registry for testing
podman tag myapp:dev registry.example.com/myapp:dev-$(date +%s)
podman push registry.example.com/myapp:dev-$(date +%s)
```

### CI/CD Pipeline

```bash
# Login to registry
podman login -u $CI_USER -p $CI_TOKEN registry.example.com

# Build with version tag
VERSION=$(git describe --tags)
podman build --build-arg VERSION=$VERSION -t myapp:$VERSION .

# Tag as latest and version
podman tag myapp:$VERSION myapp:latest
podman tag myapp:$VERSION registry.example.com/myapp:$VERSION
podman tag myapp:$VERSION registry.example.com/myapp:latest

# Push all tags
podman push --all registry.example.com/myapp
```

### Backup and Restore

```bash
# Backup critical images
podman save \
  postgres:15 \
  redis:7 \
  nginx:latest \
  -o /backup/images.tar

# Compress backup
tar czf /backup/images.tar.gz -C /backup images.tar

# Restore from backup
podman load -i /backup/images.tar
```

## Troubleshooting

### Pull Failures

```bash
# Check registry connectivity
curl -I https://registry.example.com/v2/

# Verify authentication
podman login registry.example.com

# Try with explicit transport
podman pull docker://registry.example.com/image:tag

# Check for TLS issues
podman pull --tls-verify=false registry.example.com/image:tag
```

### Build Failures

```bash
# Debug build process
podman build --debug -t myapp .

# Keep intermediate containers
podman build --rm=false -t myapp .

# Check Containerfile syntax
podman build --check-context -t myapp .

# Increase builder resources
podman build --build-arg BUILDER_MEMORY=4G -t myapp .
```

### Large Images

```bash
# Use multi-stage builds to reduce size
# See Containerfile example above

# Squash layers
podman build --squash -t myapp .

# Use smaller base images
# FROM alpine:latest instead of FROM ubuntu:latest

# Remove unnecessary files in build
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
```

## See Also

- [Core Concepts](01-core-concepts.md) - Container lifecycle and operations
- [Pod Management](03-pod-management.md) - Multi-container orchestration
- [Kubernetes Integration](04-kubernetes-integration.md) - Generate and play K8s manifests
