# Networking

## Overview

Podman uses [Netavark](https://github.com/containers/netavark) as its network backend and [Aardvark DNS](https://github.com/containers/aardvark-dns) for container name resolution. Rootless networking uses [pasta](https://passt.top/passt/about/).

## Network Backends

- **Netavark**: The primary networking backend, handling bridge networks, port forwarding, and DNS
- **Aardvark DNS**: Resolves container names to IPs within Podman networks
- **pasta**: User-mode networking tool for rootless containers (default since Podman 5.0)

## Default Network

The default bridge network is named `podman` with subnet `10.88.0.0/16`. When running as root, new containers join this network automatically. Equivalent to `--network bridge` or `--network podman`.

Change the default subnet in `containers.conf` under `[network]`:

```ini
[network]
default_subnet = "172.20.0.0/16"
```

## Creating Custom Networks

```bash
# Create a network with a specific subnet
podman network create --subnet 172.20.0.0/24 mynet

# Create without specifying subnet (auto-assigns from 10.89.0.0/24 to 10.255.255.0/24)
podman network create mynet

# Create with DNS options
podman network create --dns 8.8.8.8 mynet

# Create with custom interface name (Podman 5.4+)
podman network create --opt host_interface_name=mynet0 mynet

# Create using an existing bridge (Podman 5.4+)
podman network create --driver bridge --opt mode=unmanaged mynet
```

Custom subnet pool range is configurable in `containers.conf` under `[network]` with `default_subnet_pools`.

## Network Management

```bash
# List networks
podman network ls

# Inspect network configuration
podman network inspect mynet

# Connect/disconnect a container to/from a network
podman network connect mynet mycontainer
podman network disconnect mynet mycontainer

# Reload network configuration for running containers
podman network reload

# Remove unused networks
podman network prune

# Remove specific networks
podman network rm mynet

# Update an existing network (Podman 5.4+)
podman network update mynet
```

## Pasta (Rootless Networking)

Pasta is the default rootless networking tool since Podman 5.0. Key characteristics:

- Performs no NAT by default
- Copies IP addresses from the host's main interface into the container namespace
- Fully supports IPv6
- Runs in a separate process for architectural security
- Uses modern Linux mechanisms for isolation

Default pasta options can be set in `containers.conf` under `[network]` with the `pasta_options` key.

If pasta cannot find an interface with a default route, it selects one if only a single interface has a valid route. Specify explicitly with `-i` option to pasta.

### Podman 5.3 Pasta Fix

As of Podman 5.3, the limitation where containers could not communicate with the host through pasta has been resolved. Inter-container connections also work correctly.

## Port Mapping

```bash
# Map host port to container port
podman run -d -p 8080:80 nginx

# Map to specific host IP
podman run -d -p 127.0.0.1:8080:80 nginx

# Pod-level port mapping (shared across all containers in pod)
podman pod create --port 8080:80 mypod
```

## DNS Configuration

- Containers on the same network can resolve each other by name via Aardvark DNS
- Host search domains are included in container `resolv.conf` (fixed in Podman 5.5.1)
- Custom DNS options via `--dns-opt` replace rather than append (fixed in 5.5.1)

## Network Events

Podman 5.4+ generates events for network creation and removal, visible via `podman events`.
