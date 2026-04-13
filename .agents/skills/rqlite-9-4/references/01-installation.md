# Installation

How to download and install rqlite on various platforms.

## Overview

rqlite is delivered as a single self-contained binary with no external dependencies. Pre-built binaries are available for Linux, macOS, Windows, and many CPU architectures including x86, AMD, MIPS, RISC, PowerPC, and ARM.

## Installation Methods

### Docker (Recommended for Quick Start)

Docker images are available on Docker Hub and GitHub Container Registry:

```bash
# Docker Hub
docker run -p 4001:4001 rqlite/rqlite

# GitHub Container Registry
docker pull ghcr.io/rqlite/rqlite
docker run -p 4001:4001 ghcr.io/rqlite/rqlite
```

**Multi-platform support:** Images are available for linux/amd64, linux/arm64, and other platforms.

#### Docker with Persistent Storage

```bash
docker run -d \
  --name rqlite \
  -p 4001:4001 \
  -v rqlite-data:/rqlite \
  rqlite/rqlite

# Or with host directory
docker run -d \
  --name rqlite \
  -p 4001:4001 \
  -v /var/lib/rqlite:/rqlite \
  rqlite/rqlite
```

### Pre-built Binaries

Download from the [GitHub releases page](https://github.com/rqlite/rqlite/releases):

**Linux (x86_64):**
```bash
wget https://github.com/rqlite/rqlite/releases/download/v8.21.1/rqlite_v8.21.1_linux_amd64.tar.gz
tar xzf rqlite_v8.21.1_linux_amd64.tar.gz
sudo mv rqlited rqlite /usr/local/bin/
```

**macOS (Apple Silicon):**
```bash
wget https://github.com/rqlite/rqlite/releases/download/v8.21.1/rqlite_v8.21.1_darwin_arm64.tar.gz
tar xzf rqlite_v8.21.1_darwin_arm64.tar.gz
sudo mv rqlited rqlite /usr/local/bin/
```

**Windows:**
Download the `.zip` file from releases, extract, and add to PATH.

### Homebrew (macOS/Linux)

```bash
# Install rqlite
brew install rqlite

# Start a node
rqlited -node-id=1 /var/lib/rqlite

# Verify installation
rqlite --version
rqlited --version
```

### Building from Source

Requirements: Go 1.21 or later.

```bash
# Clone repository
git clone https://github.com/rqlite/rqlite.git
cd rqlite

# Build binaries
make

# Binaries will be in ./rqlited and ./rqlite

# Cross-compile for different platforms
GOOS=linux GOARCH=arm64 make
```

See the [Building from Source](https://rqlite.io/docs/install-rqlite/building-from-source/) guide for detailed build instructions.

## Starting rqlite

### Single Node (Development)

```bash
# Start with default settings
rqlited -node-id=1 /var/lib/rqlite

# Specify HTTP address
rqlited -node-id=1 -http-addr=:4001 /var/lib/rqlite

# Listen on all interfaces (for containers/VMs)
rqlited -node-id=1 -http-addr=0.0.0.0:4001 -raft-addr=0.0.0.0:4002 /var/lib/rqlite
```

### Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `-node-id` | Unique identifier for this node | Required |
| `-http-addr` | HTTP API address (host:port) | `:4001` |
| `-raft-addr` | Raft protocol address (host:port) | `:4002` |
| `-http-adv-addr` | Advertised HTTP address (for NAT/Docker) | Same as `-http-addr` |
| `-raft-adv-addr` | Advertised Raft address (for NAT/Docker) | Same as `-raft-addr` |
| `-join` | Comma-separated list of nodes to join | None (bootstrap node) |
| `-raft-badger` | Use Badger instead of BoltDB for Raft storage | `false` |
| `-no-recovery` | Skip automatic recovery on startup | `false` |

### Verify Installation

```bash
# Check if rqlite is running
curl localhost:4001/status

# Expected response:
{
  "raft": {
    "leader_addr": ":4002",
    "state": "Leader",
    "term": 1
  },
  "store": {
    "db_size": 8192,
    "num_wal_snapshots": 0,
    "num_wals": 1
  }
}
```

## Platform-Specific Notes

### Linux Systemd Service

Create `/etc/systemd/system/rqlite.service`:

```ini
[Unit]
Description=rqlite Distributed SQL Database
After=network.target

[Service]
Type=simple
User=rqlite
ExecStart=/usr/local/bin/rqlited -node-id=1 /var/lib/rqlite
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rqlite
sudo systemctl start rqlite
```

### Windows Service

Use NSSM (Non-Sucking Service Manager):

```powershell
nssm install rqlite "C:\rqlite\rqlited.exe" "-node-id=1" "C:\data\rqlite"
nssm start rqlite
```

## Next Steps

- Connect using the [rqlite shell](02-shell.md)
- Form a [cluster](03-clustering.md) for production
- Learn the [HTTP API](04-api.md) for application integration
- Set up [backups](05-backup-restore.md) for data protection
