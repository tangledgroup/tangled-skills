# Image Management Reference

Complete guide to image operations including pull, push, build, load, save, and registry authentication.

## Image Pull Operations

### Basic Pull

```python
from podman import PodmanClient

client = PodmanClient()

# Pull latest tag (default)
image = client.images.pull("alpine")

# Pull specific tag
image = client.images.pull("alpine", tag="3.18")

# Pull from specific registry
image = client.images.pull("quay.io/podman/stable", tag="latest")

# Pull with full name
image = client.images.pull("docker.io/library/nginx:latest")
```

### Pull with Progress

```python
# Stream pull progress
for line in client.images.pull("alpine", tag="3.18", stream=True, decode=True):
    print(line)

# With progress bar (requires rich)
from podman import PodmanClient

client = PodmanClient()
image = client.images.pull("alpine:3.18", progress_bar=True)
```

### Pull All Tags

```python
# Pull all tags from repository
images = client.images.pull("alpine", all_tags=True)

for img in images:
    print(f"Pulled: {img.repository}:{img.tag}")
```

### Pull with Authentication

```python
# Login first
client.login(
    username="myuser",
    password="mypassword",
    registry="quay.io"
)

# Then pull private image
image = client.images.pull("quay.io/myorg/private-image")

# Or provide auth_config directly
image = client.images.pull(
    "quay.io/myorg/private-image",
    auth_config={"username": "myuser", "password": "mypassword"}
)

# With identity token (OAuth)
image = client.images.pull(
    "gcr.io/project/image",
    auth_config={"identitytoken": "oauth-token"}
)
```

### Pull Policy Options

```python
# Always pull (default)
image = client.images.pull("alpine:latest", policy="always")

# If not present
image = client.images.pull("alpine:latest", policy="if_not_present")

# Never pull (use local only)
image = client.images.pull("alpine:latest", policy="never")

# Missing (error if not present)
image = client.images.pull("alpine:latest", policy="missing")
```

### Platform-Specific Images

```python
# Pull for specific platform
image = client.images.pull(
    "multiarch-image",
    tag="latest",
    platform="linux/amd64"
)

# Other platforms
image = client.images.pull(
    "image",
    platform="linux/arm64"
)

image = client.images.pull(
    "image",
    platform="linux/arm/v7"
)
```

## Image Push Operations

### Basic Push

```python
from podman import PodmanClient

client = PodmanClient()

# Push image to registry
image = client.images.get("my-app:latest")
client.images.push("my-app", tag="latest")

# Push with full repository name
client.images.push("docker.io/myuser/my-app", tag="v1.0")
```

### Push with Authentication

```python
# Login first
client.login(
    username="myuser",
    password="mypassword",
    registry="docker.io"
)

# Then push
client.images.push("my-app", tag="latest")

# Or provide auth_config directly
client.images.push(
    "my-app",
    tag="latest",
    auth_config={"username": "myuser", "password": "mypassword"}
)
```

### Push with Progress

```python
# Stream push progress
for line in client.images.push("my-app", tag="latest", stream=True, decode=True):
    print(line)

# Without decoding (raw bytes)
for line in client.images.push("my-app", tag="latest", stream=True):
    print(line.decode())
```

### Push All Tags

```python
# Push all tags of repository
client.images.push("my-app", all_tags=True)
```

### Push Format Options

```python
# Push as OCI format (default for Podman)
client.images.push("my-app", tag="latest", format="oci")

# Push as Docker v2 schema 2
client.images.push("my-app", tag="latest", format="v2s2")

# Push as Docker v2 schema 1 (legacy)
client.images.push("my-app", tag="latest", format="v2s1")
```

### Push to Multiple Destinations

```python
# Push to primary registry
client.images.push("docker.io/myuser/my-app", tag="latest")

# Push to backup registry
client.images.push(
    "my-app",
    tag="latest",
    destination="quay.io/myuser/my-app"
)

# Push to local storage (airgap)
client.images.push("my-app", tag="latest", destination="dir:/path/to/export")
```

## Image Build Operations

### Basic Build

```python
from podman import PodmanClient

client = PodmanClient()

# Build from current directory (Dockerfile)
image, logs = client.images.build(
    path=".",
    tag="my-app:latest"
)

# Print build logs
for line in logs:
    print(line.decode())

print(f"Built image: {image.id}")
```

### Build with Custom Dockerfile

```python
# Build with custom Dockerfile name
image, logs = client.images.build(
    path="./my-project",
    dockerfile="Dockerfile.production",
    tag="my-app:prod"
)

# Build from Dockerfile in subdirectory
image, logs = client.images.build(
    path="./",
    dockerfile="./docker/Dockerfile",
    tag="my-app:latest"
)
```

### Build with Arguments

```python
# Pass build arguments
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    buildargs={
        "BUILD_VERSION": "1.0.0",
        "BUILD_DATE": "2024-01-15",
        "GIT_COMMIT": "abc123"
    }
)

# Multi-stage build with target
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    target="production"  # Build up to 'production' stage
)
```

### Build Options

```python
# Don't use cache
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    nocache=True
)

# Remove intermediate containers
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    rm=True
)

# Pull base images
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    pull=True
)

# Quiet mode (suppress output)
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    quiet=True
)

# Squash layers (reduce image size)
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    squash=True
)
```

### Build Resource Limits

```python
# Set build resource limits
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    container_limits={
        "memory": 536870912,      # 512MB
        "memswap": -1,            # No swap limit
        "cpushares": 512,         # 50% CPU weight
        "cpusetcpus": "0-1",      # CPUs 0 and 1
        "cpuperiod": 100000,      # CPU period
        "cpuquota": 50000         # CPU quota (50%)
    }
)
```

### Build with Cache From

```python
# Use specific image as build cache
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    cache_from=["alpine:3.18", "my-base-image:latest"]
)
```

### Build Network Mode

```python
# Build without network access
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    network_mode="none"
)

# Build with host network
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    network_mode="host"
)
```

### Build Output Formats

```python
# Build to Docker format (default)
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    outputformat="docker"
)

# Build to OCI format
image, logs = client.images.build(
    path=".",
    tag="my-app:latest",
    outputformat="oci"
)
```

### Build from File Object

```python
import io

# Read Dockerfile content
with open("Dockerfile", "rb") as f:
    dockerfile_content = f.read()

# Build from file object
image, logs = client.images.build(
    fileobj=io.BytesIO(dockerfile_content),
    path=".",  # Context still needed
    tag="my-app:latest"
)
```

## Image Listing and Inspection

### List Images

```python
from podman import PodmanClient

client = PodmanClient()

# List all images
images = client.images.list(all=True)

for image in images:
    print(f"{image.repository}:{image.tag} - {image.short_id}")

# List images by name
images = client.images.list(name="alpine")

# List dangling images (untagged)
images = client.images.list(filters={"dangling": True})

# List by label
images = client.images.list(
    filters={"label": {"com.example.service": "api"}}
)

# List untagged images only
images = client.images.list(filters={"dangling": True})
```

### Get Image

```python
# Get image by name
image = client.images.get("alpine:latest")

# Get image by ID
image = client.images.get("sha256:abc123...")

# Check if image exists
if client.images.exists("alpine:latest"):
    print("Image exists")
```

### Image Properties

```python
image = client.images.get("alpine:latest")

# Basic properties
print(f"ID: {image.id}")
print(f"Short ID: {image.short_id}")
print(f"Repository: {image.repository}")
print(f"Tag: {image.tag}")
print(f"Created: {image.created}")
print(f"Size: {image.size} bytes")
print(f"Virtual Size: {image.virtual_size} bytes")

# Tags list
print(f"Tags: {image.tags}")

# Full attributes
attrs = image.attrs
print(f"Architecture: {attrs['Architecture']}")
print(f"OS: {attrs['Os']}")
print(f"Config: {attrs['Config']}")
```

### Image History

```python
image = client.images.get("alpine:latest")

# Get layer history
history = image.history()

for layer in history:
    print(f"{layer['created_by']}: {layer['size']} bytes")
```

## Image Tagging

### Tag Image

```python
image = client.images.get("alpine:latest")

# Add new tag
image.tag(repository="my-alpine", tag="3.18")

# Tag for registry
image.tag(repository="docker.io/myuser/alpine", tag="v1")

# Multiple tags
image.tag("my-app", "latest")
image.tag("my-app", "v1.0")
image.tag("my-app", "v1.0.0")
```

### Untag Image

```python
image = client.images.get("my-app:old-tag")

# Remove tag (image remains if other tags exist)
image.untag()
```

## Image Load and Save

### Load Image from Tarball

```python
from podman import PodmanClient

client = PodmanClient()

# Load from file
with open("image.tar", "rb") as f:
    images = list(client.images.load(f.read()))

for image in images:
    print(f"Loaded: {image.repository}:{image.tag}")

# Load from file path
images = list(client.images.load(file_path="image.tar"))

# Load from bytes
with open("image.tar", "rb") as f:
    tar_data = f.read()

images = list(client.images.load(data=tar_data))
```

### Save Image to Tarball

```python
image = client.images.get("alpine:latest")

# Save single image
with open("alpine.tar", "wb") as f:
    for chunk in image.save():
        f.write(chunk)

# Save multiple images
images = [
    client.images.get("alpine:latest"),
    client.images.get("nginx:latest")
]

with open("multi-image.tar", "wb") as f:
    for chunk in client.images.save(images=images):
        f.write(chunk)

# Save with compression
with open("alpine.tar.gz", "wb") as f:
    for chunk in image.save(compress=True):
        f.write(chunk)
```

### Export Image (Different from Save)

```python
image = client.images.get("alpine:latest")

# Export single layer (no history)
with open("alpine-export.tar", "wb") as f:
    for chunk in image.export():
        f.write(chunk)
```

## Image Removal

### Remove Single Image

```python
image = client.images.get("alpine:old")

# Remove image (fails if in use)
result = client.images.remove(image)

# Force remove (even if in use)
result = client.images.remove(image, force=True)

# Don't prune dangling images
result = client.images.remove(image, noprune=True)

# Check removal result
print(f"Deleted: {result[0].get('Deleted', [])}")
print(f"Untagged: {result[0].get('Untagged', [])}")
```

### Remove by Name

```python
# Remove by name string
result = client.images.remove("alpine:old")

# Force remove by name
result = client.images.remove("alpine:old", force=True)
```

### Prune Images

```python
# Remove dangling images (untagged, not used)
result = client.images.prune()

print(f"Deleted: {result['ImagesDeleted']}")
print(f"Space reclaimed: {result['SpaceReclaimed']} bytes")

# Remove all unused images
result = client.images.prune(all=True)

# Remove external images (used by other tools)
result = client.images.prune(external=True)

# Prune with filters
result = client.images.prune(
    filters={
        "until": "2024-01-01T00:00:00Z",  # Older than date
        "label": {"keep": "false"}        # Exclude labeled images
    }
)

# Prune build cache
result = client.images.prune_builds()
```

## Image Search

### Search Registries

```python
from podman import PodmanClient

client = PodmanClient()

# Search for images
results = client.images.search("postgres")

for result in results:
    print(f"{result['repo_name']}: {result['description']}")

# Limit results
results = client.images.search("nginx", limit=10)

# Search with filters
results = client.images.search(
    "redis",
    filters={
        "is-official": True,   # Only official images
        "stars": 5             # At least 5 stars
    }
)

# Don't truncate descriptions
results = client.images.search("alpine", noTrunc=True)

# List available tags
results = client.images.search(
    "python",
    listTags=True
)
```

## Registry Operations

### Login to Registry

```python
from podman import PodmanClient

client = PodmanClient()

# Login with username/password
client.login(
    username="myuser",
    password="mypassword",
    registry="docker.io"
)

# Login to Quay
client.login(
    username="myuser",
    password="mypassword",
    registry="quay.io"
)

# Login with email (Docker Hub)
client.login(
    username="myuser",
    password="mypassword",
    email="user@example.com",
    registry="docker.io"
)

# Login with identity token (OAuth)
client.login(
    identitytoken="oauth-token",
    registry="gcr.io"
)

# Login with TLS verification disabled
client.login(
    username="myuser",
    password="mypassword",
    registry="registry.internal:5000",
    tls_verify=False
)
```

### Logout from Registry

```python
# Logout from specific registry
client.logout(registry="docker.io")

# Logout from all registries
client.logout()
```

### Registry Data

```python
# Get registry authentication data
registry_data = client.images.get_registry_data(
    "docker.io/myuser/myapp",
    auth_config={"username": "myuser", "password": "mypassword"}
)

print(registry_data.attrs)
```

## Image Copy (SCP)

### Copy Between Hosts

```python
from podman import PodmanClient

# Source client
source_client = PodmanClient(base_url="ssh://user@host1/run/podman/podman.sock")

# Destination client
dest_client = PodmanClient(base_url="ssh://user@host2/run/podman/podman.sock")

# Copy image between hosts
result = source_client.images.scp(
    source="alpine:latest",
    dest="host2:alpine:latest"
)

print(f"Copied: {result}")
```

## Advanced Image Operations

### Inspect Image

```python
image = client.images.get("alpine:latest")

# Full inspection
attrs = image.attrs

print(f"ID: {attrs['Id']}")
print(f"Architecture: {attrs['Architecture']}")
print(f"OS: {attrs['Os']}")
print(f"Layers: {len(attrs['RootFS']['Layers'])}")
print(f"Config: {attrs['Config']}")
```

### Get Image Layers

```python
image = client.images.get("alpine:latest")

# Layer information
layers = image.attrs['RootFS']['Layers']
print(f"Number of layers: {len(layers)}")

for i, layer in enumerate(layers):
    print(f"Layer {i}: {layer}")
```

### Compare Images

```python
image1 = client.images.get("alpine:3.17")
image2 = client.images.get("alpine:3.18")

# Compare by ID
if image1.id == image2.id:
    print("Images are identical")
else:
    print(f"Different images: {image1.short_id} vs {image2.short_id}")

# Compare sizes
print(f"Size difference: {image2.size - image1.size} bytes")
```

## Error Handling

```python
from podman.errors import APIError, ImageNotFound, BuildError

try:
    image = client.images.pull("nonexistent-image:latest")
except APIError as e:
    if e.response.status_code == 404:
        print("Image not found in registry")
    else:
        print(f"Pull failed: {e.explanation}")

try:
    image = client.images.get("nonexistent-image")
except ImageNotFound as e:
    print(f"Local image not found: {e}")

try:
    image, logs = client.images.build(path="./broken-dockerfile")
except BuildError as e:
    print(f"Build failed: {e}")
    for line in e.build_log:
        print(line.decode())
```
