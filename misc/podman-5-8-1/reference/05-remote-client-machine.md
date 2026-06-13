# Remote Client and Machine

## Overview

Podman's core runtime only runs on Linux. On Mac and Windows, Podman uses a virtual machine backend managed by `podman machine`. The remote client allows any platform to manage containers on a Linux server over SSH.

## podman machine

`podman machine` manages the Linux VM that runs containers on non-Linux platforms. All machine commands are rootless only.

### Providers

- **MacOS**: libkrun (default), applehv
- **Windows**: wsl (default), hyperv
- **Linux**: qemu (default)

On M3+ Macs running macOS 15+, nested virtualization is enabled by default for libkrun VMs.

### Machine Commands

```bash
# Initialize a new VM
podman machine init --cpus 4 --memory 8192 --disk 100

# With swap (Podman 5.6+)
podman machine init --swap 2048

# With Ansible playbook for first-boot config (Podman 5.4+)
podman machine init --playbook setup.yml

# Start the VM
podman machine start

# List VMs
podman machine list

# Inspect VM configuration
podman machine inspect

# SSH into the VM
podman machine ssh

# Copy files to/from the VM (Podman 5.5+)
podman machine cp localfile.txt machine:/home/user/

# Stop the VM
podman machine stop

# Set VM settings
podman machine set --cpus 8 mymachine

# Reset machines and environment
podman machine reset

# Remove a VM
podman machine rm mymachine

# Manage VM OS
podman machine os
```

### Configuration

Machine configuration is stored in `$XDG_CONFIG_HOME/containers/podman/machine/`. Changing `XDG_CONFIG_HOME` while machines are running causes unexpected behavior.

Behavior can be modified via the `[machine]` section in `containers.conf`.

### Rosetta Support (Mac)

Rosetta support in podman machine VMs was disabled by default in Podman 5.6 due to issues with newer Linux kernels. It may be re-enabled in future releases once fixes are widely available.

## Remote Client Architecture

The remote client uses a client-server model:

1. Client executes `podman` command locally
2. Connects to the server via SSH
3. Reaches the Podman REST API through systemd socket activation at `podman.sock`
4. Commands execute on the server
5. Results return to the client

From the client's perspective, Podman appears to run locally.

## Setting Up Remote Access

### Server Side (Linux)

Enable the podman socket:

```bash
systemctl --user enable --now podman.socket
sudo loginctl enable-linger $USER
```

The rootless socket listens at `/run/user/${UID}/podman/podman.sock`.

Enable SSH daemon:

```bash
sudo systemctl enable --now sshd
```

### Client Side

Generate SSH keys (ed25519 recommended):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
```

Copy public key to server:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server-ip
```

Add the connection:

```bash
podman system connection add myserver \
  --identity ~/.ssh/id_ed25519 \
  ssh://user@server-ip/run/user/1000/podman/podman.sock
```

List connections:

```bash
podman system connection list
```

Use a specific connection:

```bash
podman --connection myserver ps
```

### podman-remote vs podman --remote

- `podman-remote` — standalone binary that only acts as a remote client
- `podman --remote` — full Podman with remote capability enabled

Both have identical CLI for remote operations. Some flags are removed from remote mode as they do not apply (e.g., `--latest`).

## Mac and Windows Setup

Install Podman from podman.io. The installer includes the client and manages the VM backend.

Initialize and start the machine:

```bash
podman machine init
podman machine start
```

On macOS, use `macos_autostart.md` tutorial to start Podman on login via launchd.

## Image Sources

VM images are pulled as artifacts from `quay.io/podman/machine-os` (consistent across all providers since Podman 5.6).
