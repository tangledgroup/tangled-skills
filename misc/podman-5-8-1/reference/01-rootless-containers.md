# Rootless Containers

## Overview

Rootless Podman runs containers without root privileges. It uses Linux user namespaces to map UIDs and GIDs, so that `root` inside the container maps to the regular user on the host. Podman is not a setuid binary — it gains no elevated privileges.

## Administrator Setup

### Subordinate UID/GID Ranges

Each user who will run containers needs entries in `/etc/subuid` and `/etc/subgid`:

```
# /etc/subuid
johndoe:100000:65536
test:165536:65536
```

Format: `USERNAME:START_UID:RANGE`

Use `usermod` to assign ranges:

```bash
usermod --add-subuids 100000-165535 --add-subgids 100000-165535 johndoe
```

After updating subuid/subgid, the user must run `podman system migrate` to apply changes.

### Pasta Networking

Podman 5.x uses [pasta](https://passt.top/passt/about/) as the default rootless networking tool. Install the `passt` package from your distribution's repositories.

Pasta copies IP addresses from the host's main interface into the container namespace and performs no NAT by default. As of Podman 5.3, host-to-container communication works correctly with pasta.

### Enabling Linger

For the rootless podman socket to work when the user is not logged in:

```bash
sudo loginctl enable-linger $USER
```

## User Configuration

Configuration files for rootless users reside in `$XDG_CONFIG_HOME/containers/` (default: `$HOME/.config/containers/`).

Key directories:

- Graph root (image/container storage): `$XDG_DATA_HOME/containers/storage` (default: `$HOME/.local/share/containers/storage`)
- Run root (temporary data): `$XDG_RUNTIME_DIR/containers` (default: `/run/user/$UID/containers`)
- Auth file: `$XDG_RUNTIME_DIR/containers/auth.json`

### Storage Driver

In rootless mode, only overlay (with optional `fuse-overlayfs`) and VFS drivers are supported. Native overlayfs requires kernel >= 5.12; otherwise `fuse-overlayfs` is used automatically.

Fields `graphroot` and `runroot` in `/etc/containers/storage.conf` are ignored in rootless mode — they always use the XDG paths above.

## Volume Semantics

When mounting host directories into a rootless container, UID mapping applies:

- `root` inside the container = your user on the host
- Files created as `root` in the container appear owned by your user on the host

Use `--userns=keep-id` to map your UID/GID directly inside the container:

```bash
podman run --rm --userns=keep-id -v $PWD:/work alpine ls -la /work
```

If the container image specifies a non-root `USER`, you **must** use `--userns=keep-id` when mounting volumes, otherwise the container user cannot access mounted paths.

## Known Limitations

- Cannot bind to ports < 1024 (kernel restriction without `CAP_NET_BIND_SERVICE`). Workaround: set `sysctl net.ipv4.ip_unprivileged_port_start=443` or use a proxy/redirection tool.
- With pasta networking, inter-container connections require explicit network configuration if only one host interface exists.
- No resource limits on cgroups v1 systems.
- Does not work on NFS or parallel filesystem home directories (GPFS) — these do not understand user namespaces.
- Requires a writable home directory not mounted with `noexec` or `nodev`.
- Standard rootless config provides 65536 UIDs/GIDs — images with higher UIDs cannot be used.
- `podman container checkpoint` and `restore` require root (CRIU limitation).
- Cannot create device nodes inside containers, even in privileged mode (kernel requires `CAP_MKNOD`).
- Some systemd options like `PrivateNetwork` fail in rootless containers — use an override with `PrivateNetwork=no` or add `--cap-add SYS_ADMIN`.
- Container images cannot easily be shared between users.
- `podman mount` and `podman unmount` directories are only visible inside the user namespace (access via `podman unshare`).
