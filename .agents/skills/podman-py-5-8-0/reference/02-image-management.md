# Image Management

## Pulling Images

```python
# Pull specific tag
image = client.images.pull("alpine", tag="3.19")

# Pull latest (default)
image = client.images.pull("python", tag="3.12-slim")

# Pull all tags from repository
images = client.images.pull("alpine", all_tags=True)

# Stream pull progress
for line in client.images.pull("ubuntu", tag="22.04", stream=True, decode=True):
    print(line)
```

Parameters:
- `repository` (str): Repository name
- `tag` (str): Image tag, default `"latest"`
- `all_tags` (bool): Pull all tags
- `auth_config` (dict): Override credentials with `username` and `password` keys
- `platform` (str): Platform format `os[/arch]`
- `stream` (bool): Stream progress output
- `decode` (bool): Decode stream into dicts
- `tls_verify` (bool): Verify TLS certificates, default True
- `policy` (str): Pull policy

## Listing Images

```python
# List all images
images = client.images.list()

# List with filters
images = client.images.list(all=True)
images = client.images.list(name="alpine")
images = client.images.list(filters={"dangling": True})
images = client.images.list(filters={"label": "com.example.app"})
```

Filters:
- `dangling` (bool): Only untagged images
- `label` (str | list[str]): Filter by label, format `"key"` or `"key=value"`

## Getting and Checking Images

```python
image = client.images.get("alpine:3.19")  # by name
image = client.images.get("sha256:abc123...")  # by ID

exists = client.images.exists("alpine:3.19")
```

## Building Images

```python
# Build from directory with Dockerfile
image, logs = client.images.build(
    path="./my-app",
    tag="my-app:latest",
)

# Build with build args and options
image, logs = client.images.build(
    path=".",
    dockerfile="Dockerfile.prod",
    tag="my-app:v1",
    buildargs={"BUILD_ENV": "production"},
    nocache=True,
    rm=True,
    labels={"version": "1.0"},
    platform="linux/amd64",
)

# Build from file-like object
import io
dockerfile = io.BytesIO(b"FROM alpine\nRUN echo hello")
image, logs = client.images.build(
    fileobj=dockerfile,
    custom_context=True,
    tag="custom:latest",
)
```

Build parameters:
- `path` (str): Path to Dockerfile directory
- `fileobj`: File object with Dockerfile content
- `tag` (str): Tag for built image
- `dockerfile` (str): Dockerfile name, default `"Dockerfile"`
- `buildargs` (dict[str, str]): Build-time variables
- `nocache` (bool): Don't use cache
- `rm` (bool): Remove intermediate containers
- `forcerm` (bool): Always remove intermediate containers
- `labels` (dict[str, str]): Labels for image
- `platform` (str): Target platform
- `network_mode` (str): Network mode during build
- `container_limits` (dict): Resource limits during build — keys: `memory`, `memswap`, `cpushares`, `cpusetcpus`, `cpuperiod`, `cpuquota`, `shmsize`
- `cache_from` (list[str]): Images to consider as cache sources
- `target` (str): Target build stage
- `squash` (bool): Squash layers
- `extra_hosts` (dict[str, str]): Host mappings during build
- `http_proxy` (bool): Inject HTTP proxy env vars (Podman only)
- `layers` (bool): Build with layer caching
- `output` (str): Build output destination
- `outputformat` (str): Output image format
- `pull` (bool): Pull base images during build

## Pushing Images

```python
# Push single image
client.images.push("my-registry.com/my-app", tag="v1")

# Stream push progress
for line in client.images.push("my-registry.com/my-app", tag="latest", stream=True, decode=True):
    print(line)
```

Parameters:
- `repository` (str): Target registry/repository
- `tag` (str): Tag to push
- `auth_config` (dict): Override credentials
- `stream` (bool): Stream progress
- `decode` (bool): Decode stream into dicts
- `tls_verify` (bool): Verify TLS

## Saving and Loading Images

```python
# Save image as tarball
with open("image.tar", "wb") as f:
    for chunk in image.save(chunk_size=2*1024*1024):
        f.write(chunk)

# Save with tag information
for chunk in image.save(named=True):  # uses first tag
    ...

# Load image from tarball
loaded_images = client.images.load(file_path="image.tar")

# Load from bytes
tar_data = open("image.tar", "rb").read()
loaded_images = client.images.load(data=tar_data)
```

## Tagging Images

```python
image.tag("my-registry.com/my-app", tag="v1.0")
```

Parameters:
- `repository` (str): Target repository
- `tag` (str | None): Tag name
- `force` (bool): Ignore client errors

## Removing Images

```python
# Remove single image
result = image.remove(force=True)

# Via manager
client.images.remove("alpine:3.19", force=True)
```

Returns list of dicts with keys `Deleted`, `Untagged`, `Errors`, `ExitCode`.

Parameters:
- `force` (bool): Delete even if in use (Podman only)

## Pruning Images

```python
# Remove dangling images
result = client.images.prune()

# Remove all unused images
result = client.images.prune(all=True)

# With filters
result = client.images.prune(
    filters={"until": "24h", "dangling": True}
)
```

Returns dict with `ImagesDeleted` (list) and `SpaceReclaimed` (int).

Filters:
- `dangling` (bool): Only untagged images
- `label` (dict): Filter by label
- `until` (str): Delete images older than timestamp

## Image History

```python
history = image.history()
# Returns list of dicts with Created, CreatedBy, Size, etc.
```

## Image Properties

```python
print(image.id)       # Full image ID
print(image.short_id) # Truncated ID
print(image.tags)     # List of tags
print(image.labels)   # Dict of labels
```

## Pruning Build Cache

```python
result = client.images.prune_builds()
# Returns {"CachesDeleted": [], "SpaceReclaimed": 0}
# Note: Always returns empty for Podman
```
