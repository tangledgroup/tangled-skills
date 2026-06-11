# Quadlet and Systemd

## Overview

Quadlet enables declarative container management using systemd unit files. Instead of running `podman run` commands, you write `.container`, `.pod`, `.volume`, `.network`, `.image`, `.build`, or `.kube` unit files that systemd manages with automatic restart, dependencies, and lifecycle control.

Quadlet translates these unit files into Podman commands at runtime. The syntax is documented in `podman-systemd.unit(5)`.

## Quadlet Unit Types

- **`.container`** — Defines a single container
- ****.pod** — Defines a pod (group of containers)
- **`.volume`** — Defines a named volume
- **`.network`** — Defines a Podman network
- **`.image`** — Manages image pulling and updates
- **`.build`** — Builds an image from a Containerfile
- **`.kube`** — Deploys Kubernetes YAML

## Example: Container Unit

```ini
# /etc/containers/systemd/web.container
[Unit]
Description=Web Server Container
Requires=web.network
After=web.network

[Container]
Image=nginx:latest
Port=8080:80
Volume=data:/usr/share/nginx/html:ro

[Install]
WantedBy=default.target
```

## Example: Pod Unit (Podman 5.6+)

```ini
# /etc/containers/systemd/app.pod
[Unit]
Description=Application Pod

[Pod]
HostName=app-pod
Label=version=1.0
ExitPolicy=kill
ShmSize=256m

[Install]
WantedBy=default.target
```

## Example: Volume Unit

```ini
# /etc/containers/systemd/data.volume
[Unit]
Description=Application Data Volume

[Volume]
Driver=local

[Install]
WantedBy=default.target
```

## Key Features

### Environment Variables (Podman 5.6+)

`.container` units can specify environment variables without values, retrieving them from the host at startup:

```ini
[Container]
Environment=DATABASE_URL
Environment=API_KEY=
```

### Retry and RetryDelay (Podman 5.5+)

`.container`, `.image`, and `.build` units support pull retry configuration:

```ini
[Container]
Image=myregistry/app:latest
Retry=3
RetryDelay=10s
```

### Memory Limits (Podman 5.5+)

```ini
[Container]
Memory=512m
```

### Reload Support (Podman 5.5+)

Containers can be configured for graceful reload via systemd:

```ini
[Container]
ReloadCmd=/usr/local/bin/reload
ReloadSignal=SIGHUP
```

### Pull Policy (Podman 5.6+)

`.image` units support `Policy=` to control when images are pulled:

```ini
[Image]
Name=myregistry/app:latest
Policy=newer
```

### Network Interface Name (Podman 5.6+)

`.network` units support `InterfaceName=`:

```ini
[Network]
Driver=bridge
Subnet=172.20.0.0/24
InterfaceName=mynet0
```

## Managing Quadlets

Install, list, print, and remove Quadlet files using the `podman quadlet` commands (Podman 5.6+):

```bash
# Install a Quadlet for the current user
podman quadlet install myapp.container

# List installed Quadlets
podman quadlet list

# Print contents of a Quadlet
podman quadlet print myapp

# Remove an installed Quadlet
podman quadlet rm myapp
```

Note: These commands are not available with the remote Podman client yet.

## Generated Systemd Services

When you place Quadlet files in the appropriate directory, Podman generates corresponding `.service` files that systemd manages. Start containers as normal systemd services:

```bash
# Start the container service
systemctl --user start web.container

# Enable auto-start on login
systemctl --user enable web.container

# Check status
systemctl --user status web.container
```

## Installation Paths

Quadlet files can be placed in:

- `/etc/containers/systemd/` — system-wide (root)
- `$HOME/.config/containers/systemd/` — user-specific (rootless)
- Drop-in directories for overrides

Names in systemd dependencies are automatically translated — `Wants=my.container` is valid.

## Warnings and Compatibility

- Quadlet warns when skipping lines to help identify malformed files
- Podman 5.6+ warns about problematic systemd options like `User=`, `Group=`, `DynamicUser=` in `[Service]` sections
- Stopping a `.network` unit deletes the network if no containers are actively using it (Podman 5.5+)
- Quadlet `.pod` files include `RequiresMountsFor` for volume mounts with `Type=bind`
- Semicolons (`;`) define comments, not colons — matching systemd convention
