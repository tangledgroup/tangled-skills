# Volumes and Storage

## Volume Management

Podman manages named volumes through the `podman volume` command group.

### Creating and Managing Volumes

```bash
# Create a volume
podman volume create mydata

# With UID/GID (Podman 5.6+)
podman volume create --uid 1000 --gid 1000 mydata

# List volumes
podman volume ls

# Inspect a volume
podman volume inspect mydata

# Check if volume exists
podman volume exists mydata

# Mount/unmount a volume filesystem
podman volume mount mydata
podman volume unmount mydata

# Export/import volume contents
podman volume export mydata > backup.tar
podman volume import mydata < backup.tar

# Remove volumes
podman volume rm mydata
podman volume prune  # remove unused volumes

# Reload volumes from plugins
podman volume reload
```

### Mount Types

**Bind mounts** — mount a host directory into the container:

```bash
podman run -v /host/path:/container/path nginx
# With options
podman run -v /host/path:/container/path:ro,z nginx
```

**Named volumes** — managed by Podman:

```bash
podman run -v mydata:/container/path nginx
```

**Anonymous volumes**:

```bash
podman run -v /container/path nginx
```

**Overlay mounts** (Windows remote client):

```bash
podman run -v source:destination:O nginx
```

### Mount Options (Podman 5.4+)

The `--mount` option supports subpath for volumes:

```bash
podman run --mount type=volume,source=mydata,destination=/data,subpath=app alpine
```

The `--mount` option defaults to `type=volume` when not specified (fixed in Podman 5.6).

### Volume Semantics in Rootless Mode

When running rootless, files created by the container's root user inside mounted volumes are actually owned by the host user (due to UID mapping). Use `--userns=keep-id` to preserve UID consistency.

## Storage Architecture

Podman uses the containers/storage library with a SQLite backend (BoltDB deprecated, will be removed in Podman 6.0).

### Storage Drivers

- **overlay** — default on most systems, requires kernel support
- **fuse-overlayfs** — FUSE-based overlay for rootless without kernel support
- **VFS** — fallback driver, slower but works everywhere

In rootless mode, only overlay (with optional fuse-overlayfs) and VFS are supported. Native overlayfs requires kernel >= 5.12.

### Storage Paths

- **Rootful**: graphroot at `/var/lib/containers/storage`, runroot at `/run/containers/storage`
- **Rootless**: graphroot at `$XDG_DATA_HOME/containers/storage`, runroot at `$XDG_RUNTIME_DIR/containers`

### Configuration

Storage is configured in `storage.conf`:

- `/etc/containers/storage.conf` (system-wide)
- `$HOME/.config/containers/storage.conf` (user-specific, rootless)

In rootless mode, `graphroot` and `runroot` from the system config are ignored.

### Disk Usage

```bash
# Show disk usage
podman system df

# Verbose disk usage
podman system df -v

# Prune unused resources
podman system prune
```

### Storage Consistency Checks

```bash
# Full consistency check
podman system check

# Quick check (skips layer digests, Podman 5.6+)
podman system check --quick
```

### Migration

When updating Podman or changing storage configuration:

```bash
# Migrate containers to new version
podman system migrate

# Reset storage to initial state
podman system reset
```

## Volume Plugins

Podman supports volume plugins for external storage backends. The `podman volume reload` command reloads all volumes from registered plugins.
