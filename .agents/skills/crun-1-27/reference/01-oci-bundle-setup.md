# OCI Bundle Setup for crun

This guide covers creating OCI bundles and configuration files for running containers with crun.

## OCI Bundle Structure

An OCI bundle consists of:

```
bundle-directory/
├── config.json      # Container configuration (OCI runtime spec)
├── rootfs/          # Container filesystem
│   ├── bin/
│   ├── etc/
│   ├── lib/
│   └── ...
└── (optional) additional files for the container
```

## Generating config.json

Use crun's spec command to generate a base configuration:

```bash
# Create bundle directory
mkdir -p my-container/rootfs

# Generate default config.json
crun spec --bundle my-container

# Generate rootless-compatible config
crun spec --bundle my-container --rootless
```

## Minimal config.json Example

```json
{
  "ociVersion": "1.1.0",
  "process": {
    "terminal": true,
    "user": {
      "uid": 0,
      "gid": 0
    },
    "args": ["/bin/bash"],
    "env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "TERM=xterm"
    ],
    "cwd": "/root",
    "noNewPrivileges": false
  },
  "root": {
    "path": "rootfs",
    "readonly": false
  },
  "hostname": "container",
  "mounts": [
    {
      "destination": "/proc",
      "type": "proc",
      "source": "proc"
    },
    {
      "destination": "/sys",
      "type": "sysfs",
      "source": "sysfs",
      "options": ["nosuid", "noexec", "nodev", "ro"]
    },
    {
      "destination": "/dev",
      "type": "tmpfs",
      "source": "tmpfs",
      "options": ["nosuid", "strictatime", "mode=755", "size=65536k"]
    }
  ],
  "linux": {
    "namespaces": [
      {
        "type": "pid"
      },
      {
        "type": "network"
      },
      {
        "type": "ipc"
      },
      {
        "type": "uts"
      },
      {
        "type": "user"
      },
      {
        "type": "mount"
      }
    ],
    "resources": {
      "pids": {
        "limit": 100
      }
    }
  }
}
```

## Running a Container from Bundle

```bash
# Create and start container
crun run --bundle ./my-container container-name

# Specify custom config file
crun run --bundle ./my-container --config custom-config.json container-name

# Detach from container process
crun run --detach --bundle ./my-container container-name

# Save PID to file
crun run --pid-file /tmp/container.pid --bundle ./my-container container-name
```

## Process Configuration

### User and Groups

```json
{
  "process": {
    "user": {
      "uid": 1000,
      "gid": 1000,
      "additionalGids": [1001, 1002],
      "username": "myuser"
    }
  }
}
```

### Environment Variables

```json
{
  "process": {
    "env": [
      "PATH=/usr/local/bin:/usr/bin:/bin",
      "HOME=/root",
      "MY_APP_ENV=production",
      "DATABASE_URL=postgres://localhost:5432/mydb"
    ]
  }
}
```

### Command Arguments

```json
{
  "process": {
    "args": [
      "/usr/bin/python3",
      "-u",
      "app.py",
      "--host",
      "0.0.0.0",
      "--port",
      "8080"
    ]
  }
}
```

### Capabilities

```json
{
  "process": {
    "capabilities": {
      "bounding": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_MKNOD",
        "CAP_AUDIT_WRITE"
      ],
      "effective": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_MKNOD",
        "CAP_AUDIT_WRITE"
      ],
      "inheritable": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_MKNOD",
        "CAP_AUDIT_WRITE"
      ],
      "permitted": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_MKNOD",
        "CAP_AUDIT_WRITE"
      ],
      "ambient": []
    }
  }
}
```

## Mount Configuration

### Bind Mounts

```json
{
  "mounts": [
    {
      "destination": "/mnt/host-data",
      "type": "bind",
      "source": "/host/data/path",
      "options": ["rbind", "rw"]
    }
  ]
}
```

### tmpfs Mounts

```json
{
  "mounts": [
    {
      "destination": "/tmp",
      "type": "tmpfs",
      "source": "tmpfs",
      "options": ["rw", "nosuid", "noexec", "size=65m", "mode=1777"]
    }
  ]
}
```

### tmpcopyup Option

Copy shadowed content to tmpfs:

```json
{
  "mounts": [
    {
      "destination": "/etc/container",
      "type": "tmpfs",
      "source": "tmpfs",
      "options": ["rw", "nosuid", "noexec", "tmpcopyup"]
    }
  ]
}
```

## Namespace Configuration

### All Available Namespaces

```json
{
  "linux": {
    "namespaces": [
      {"type": "pid"},
      {"type": "network"},
      {"type": "ipc"},
      {"type": "uts"},
      {"type": "user"},
      {"type": "mount"},
      {"type": "cgroup"}
    ]
  }
}
```

### Custom Namespace Paths

Share namespaces with other containers:

```json
{
  "linux": {
    "namespaces": [
      {
        "type": "pid",
        "path": "/proc/1234/ns/pid"
      },
      {
        "type": "network",
        "path": "/proc/1234/ns/net"
      }
    ]
  }
}
```

## Rootless Container Configuration

For unprivileged containers:

```bash
# Generate rootless config
crun spec --bundle my-container --rootless
```

Key differences in rootless mode:
- User namespace automatically created
- Current user mapped to UID 0 in container
- Additional IDs from `/etc/subuid` and `/etc/subgid` added
- State stored in `$XDG_RUNTIME_DIR/crun` instead of `/run/crun`

## Device Nodes

```json
{
  "linux": {
    "devices": [
      {
        "path": "/dev/tty0",
        "type": "c",
        "major": 4,
        "minor": 0,
        "fileMode": 0666,
        "uid": 0,
        "gid": 0
      },
      {
        "path": "/dev/sda",
        "type": "b",
        "major": 8,
        "minor": 0,
        "fileMode": 0666,
        "uid": 0,
        "gid": 0
      }
    ]
  }
}
```

## Hooks

OCI hooks for lifecycle events:

```json
{
  "hooks": {
    "prestart": [
      {
        "path": "/usr/libexec/container-hooks/prestart.sh",
        "args": ["hook", "container-id"],
        "timeout": 5
      }
    ],
    "poststart": [
      {
        "path": "/usr/libexec/container-hooks/poststart.sh"
      }
    ],
    "poststop": [
      {
        "path": "/usr/libexec/container-hooks/poststop.sh"
      }
    ]
  }
}
```

### crun Hook Annotations

Redirect hook output:

```json
{
  "annotations": {
    "run.oci.hooks.stdout": "/var/log/hooks.log",
    "run.oci.hooks.stderr": "/var/log/hooks-errors.log"
  }
}
```

## Annotations

Custom metadata and crun-specific features:

```json
{
  "annotations": {
    "io.kubernetes.container.name": "my-app",
    "run.oci.handler": "wasm",
    "run.oci.keep_original_groups": "1"
  }
}
```

See [Advanced Features](04-advanced-features.md) for crun-specific annotations.

## Validation Checklist

Before running a container:

- [ ] `config.json` exists in bundle directory
- [ ] `rootfs/` directory contains valid filesystem
- [ ] Process `args` point to executable in rootfs
- [ ] Required namespaces specified
- [ ] Mounts have valid source paths (for bind mounts)
- [ ] User UID/GID exist in container
- [ ] Working directory (`cwd`) exists in container

## Common Issues

**"No such file or directory" for process:**
- Verify the executable path in `process.args[0]` exists in rootfs
- Check filesystem is populated correctly

**Permission denied on mounts:**
- Ensure source paths exist and are readable
- Check bind mount options don't conflict with permissions

**User namespace errors:**
- For rootless: verify `/etc/subuid` and `/etc/subgid` have available ranges
- Check user mappings in config match container filesystem ownership
