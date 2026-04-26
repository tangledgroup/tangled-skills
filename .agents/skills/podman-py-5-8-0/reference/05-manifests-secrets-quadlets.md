# Manifests, Secrets, and Quadlets

## Manifest Lists

Manifest lists enable multi-architecture image support.

### Creating Manifest Lists

```python
manifest = client.manifests.create("my-manifest", "amd64-image:latest")
```

Parameters:
- `name` (str): Name of manifest list
- `images` (str | Image): Initial image to add
- `insecure` (bool): Allow insecure registry connections

### Adding Images

```python
manifest.add([image1, "registry.com/image2:tag"])
```

Parameters:
- `images` (list[Image | str]): Images to add
- `arch` (str): Architecture annotation
- `os` (str): OS annotation
- `os_version` (str): OS version
- `variant` (str): Architecture variant
- `features` (list[str]): Feature annotations
- `annotation` (dict[str, str]): Custom annotations
- `all` (bool): Add all tags

### Removing Images from Manifest

```python
manifest.remove("sha256:abc123...")
```

### Pushing Manifest

```python
manifest.push("registry.com/my-multiarch-image:latest", all=True)
```

Parameters:
- `destination` (str): Target registry/repository
- `all` (bool): Push all images
- `auth_config` (dict): Override credentials with `username` and `password`

### Manifest Properties

```python
print(manifest.id)        # Manifest ID
print(manifest.name)      # Human-formatted name
print(manifest.names)     # List of names
print(manifest.media_type)  # Media/MIME type
print(manifest.version)    # Schema version
```

## Secrets

Secrets store sensitive data for container use.

### Creating Secrets

```python
secret = client.secrets.create(
    "my-secret",
    b"sensitive-data-here",
    driver="file",  # or "env"
)
```

Parameters:
- `name` (str): Secret name
- `data` (bytes): Secret data
- `labels` (dict): Labels (ignored by Podman)
- `driver` (str | None): Secret driver

### Listing Secrets

```python
secrets = client.secrets.list()
```

### Getting and Checking Secrets

```python
secret = client.secrets.get("my-secret")
exists = client.secrets.exists("my-secret")
```

### Removing Secrets

```python
secret.remove()
# or via manager:
client.secrets.remove("my-secret")

# Delete all secrets
client.secrets.remove(all=True)
```

### Secret Properties

```python
print(secret.id)       # Secret ID
print(secret.name)     # Secret name
print(secret.short_id) # Truncated ID
```

## Quadlets

Quadlets are systemd unit files that describe Podman resources. The QuadletsManager provides programmatic access to quadlet lifecycle operations.

### Listing Quadlets

```python
quadlets = client.quadlets.list()

# Filter by name (supports wildcards)
quadlets = client.quadlets.list(filters={"name": "myapp*"})
```

### Getting and Checking Quadlets

```python
quadlet = client.quadlets.get("myapp.container")
exists = client.quadlets.exists("myapp.container")
```

### Reading Quadlet Contents

```python
# Get as string
content = quadlet.get_contents()

# Print to stdout (stripped)
quadlet.print_contents()
```

### Installing Quadlets

```python
# Install from file path
result = client.quadlets.install("/path/to/myapp.container")

# Install with associated files (e.g., Containerfile)
result = client.quadlets.install([
    "/path/to/myapp.container",
    "/path/to/Containerfile",
])

# Install from inline content
result = client.quadlets.install(
    ("myapp.container", "[Container]\nImage=alpine\n"),
)

# Install with replace and no systemd reload
result = client.quadlets.install(
    "myapp.container",
    replace=True,
    reload_systemd=False,
)

# Install from tar archive
result = client.quadlets.install("/path/to/quadlets.tar")
```

Parameters:
- `files`: Single file or list of files. Each item can be:
  - Path (str | PathLike): File on disk
  - Tuple `(filename, content)`: Inline content as str or bytes
- `replace` (bool): Replace existing files, default False
- `reload_systemd` (bool): Reload systemd after install, default True

Returns dict with `InstalledQuadlets` (path mappings) and `QuadletErrors` (error messages).

### Deleting Quadlets

```python
# Delete single quadlet
removed = client.quadlets.delete("myapp.container")

# Force removal of running quadlet
removed = client.quadlets.delete("myapp.container", force=True)

# Delete all quadlets
removed = client.quadlets.delete(all=True)
```

Parameters:
- `name` (str | Quadlet): Quadlet to remove
- `all` (bool): Remove all quadlets
- `force` (bool): Stop running quadlet first, default False
- `ignore` (bool): Don't error if not found, default False
- `reload_systemd` (bool): Reload systemd after removal, default True

### Quadlet Properties

```python
print(quadlet.name)        # Quadlet file name
print(quadlet.unit_name)   # Systemd unit name
print(quadlet.path)        # Filesystem path
print(quadlet.status)      # Status
print(quadlet.application) # Application type
```
