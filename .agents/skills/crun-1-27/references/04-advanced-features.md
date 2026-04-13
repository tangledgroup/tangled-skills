# Advanced crun Features

Comprehensive guide to crun-specific extensions, WebAssembly support, security features, and advanced mount options.

## OCI Extensions

crun provides several extensions to the OCI runtime specification via annotations.

### Handler Annotation

Run containers with custom handlers:

```json
{
  "annotations": {
    "run.oci.handler": "wasm"
  }
}
```

**Supported handlers:**
- `krun`: Use libkrun to launch container (requires `libkrun.so`)
- `wasm`: Run WebAssembly workload natively

### Seccomp Extensions

#### Seccomp Receiver Socket

Send seccomp listener to UNIX socket:

```json
{
  "annotations": {
    "run.oci.seccomp.receiver": "/var/run/seccomp-listener.sock"
  }
}
```

Or via environment variable:
```bash
export RUN_OCI_SECCOMP_RECEIVER=/var/run/seccomp-listener.sock
crun run container-id
```

**Must be an absolute path.** Experimental feature.

#### Seccomp Plugins

Handle seccomp listener FD through plugins:

```json
{
  "annotations": {
    "run.oci.seccomp.plugins": "/usr/lib/seccomp/plugin1.so:/usr/lib/seccomp/plugin2.so"
  }
}
```

Plugins can be:
- Absolute paths to shared objects
- Filenames looked up via `dlopen(3)`

#### Seccomp Unknown Syscall Handling

Fail on unknown syscalls in seccomp config:

```json
{
  "annotations": {
    "run.oci.seccomp_fail_unknown_syscall": "1"
  }
}
```

#### Raw Seccomp BPF Data

Use raw seccomp filter data (bypasses OCI config seccomp section):

```json
{
  "annotations": {
    "run.oci.seccomp_bpf_data": "base64-encoded-bpf-data"
  }
}
```

Data must be base64 encoded for `seccomp(SECCOMP_SET_MODE_FILTER)` syscall. Experimental feature.

### PID File Descriptor Receiver

Send container process pidfd to UNIX socket:

```json
{
  "annotations": {
    "run.oci.pidfd_receiver": "/var/run/container-pidfd.sock"
  }
}
```

Experimental feature, will be removed once in OCI runtime spec.

### Keep Original Groups

Skip `setgroups` syscall to preserve supplementary groups:

```json
{
  "annotations": {
    "run.oci.keep_original_groups": "1"
  }
}
```

Useful when container needs access to host groups.

### Mount Context Type (SELinux)

Set mount context type for SELinux-labeled volumes:

```json
{
  "annotations": {
    "run.oci.mount_context_type": "fscontext"
  }
}
```

**Valid context types:**
- `context` (default): Use default context
- `fscontext`: Set filesystem context
- `defcontext`: Use default type/context
- `rootcontext`: Use root context

See `mount(8)` man page for details on mount context flags.

## WebAssembly Support

crun can run WebAssembly workloads natively using the WASI handler.

### Running WASM Modules

**Configuration:**

```json
{
  "ociVersion": "1.1.0",
  "process": {
    "terminal": false,
    "user": {
      "uid": 0,
      "gid": 0
    },
    "args": ["/hello.wasm"],
    "env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "TERM=xterm"
    ],
    "cwd": "/"
  },
  "root": {
    "path": "rootfs",
    "readonly": true
  },
  "hostname": "wasm-container",
  "mounts": [
    {
      "destination": "/proc",
      "type": "proc",
      "source": "proc"
    }
  ],
  "annotations": {
    "run.oci.handler": "wasm"
  }
}
```

**Bundle structure:**

```
wasm-bundle/
├── config.json
└── rootfs/
    └── hello.wasm
```

**Run the container:**

```bash
crun run wasm-bundle
```

### Building WASM Images with Buildah

Create Containerfile:

```dockerfile
FROM scratch
COPY hello.wasm /
CMD ["/hello.wasm"]
```

Build image:

```bash
buildah build --platform=wasi/wasm -t mywasm-image .
```

Run with podman (ensure crun is the runtime):

```bash
podman run mywasm-image:latest
```

### Compiling to WASM

**Rust example:**

```rust
// src/main.rs
fn main() {
    println!("Hello from WebAssembly!");
}
```

Compile:

```bash
# Add wasm32-wasip2 target
rustup target add wasm32-wasip2

# Build WASM module
cargo build --target wasm32-wasip2 --release

# Output: target/wasm32-wasip2/release/your-binary.wasm
```

**Using wasm-pack:**

```bash
wasm-pack build --target wasm
```

### Running Pre-built WASM Images

```bash
podman run -it -p 8080:8080 --name=wasm-example \
  --platform=wasi/wasm32 michaelirwin244/wasm-example
```

## Mount Options

### tmpcopyup

Copy shadowed content to tmpfs mount:

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

When tmpfs shadows a path, `tmpcopyup` recursively copies the shadowed content to the tmpfs itself.

### copy-symlink

Preserve symlinks instead of following them:

```json
{
  "mounts": [
    {
      "destination": "/mnt/link",
      "type": "bind",
      "source": "/host/symlink",
      "options": ["bind", "copy-symlink"]
    }
  ]
}
```

If source is a symlink, recreates the symlink at destination instead of mounting the target. Fails if destination exists and isn't the expected symlink.

### dest-nofollow

Mount to symlink destination without following:

```json
{
  "mounts": [
    {
      "destination": "/container/symlink",
      "type": "bind",
      "source": "/host/data",
      "options": ["bind", "dest-nofollow"]
    }
  ]
}
```

When destination is a symlink, mounts to the symlink itself rather than its target.

### src-nofollow

Use symlink source without resolving:

```json
{
  "mounts": [
    {
      "destination": "/mnt/target",
      "type": "bind",
      "source": "/host/symlink",
      "options": ["bind", "src-nofollow"]
    }
  ]
}
```

Uses the symlink itself as source rather than the file/directory it points to.

### Recursive Mount Flags

Apply flags recursively to child mounts:

```json
{
  "mounts": [
    {
      "destination": "/data",
      "type": "bind",
      "source": "/host/data",
      "options": ["bind", "rro"]  # Read-only recursive
    }
  ]
}
```

**Supported recursive flags:**
- `rro`: Read-only recursive
- `rrw`: Read-write recursive
- `rsuid` / `rnosuid`: Set/no setuid recursive
- `rdev` / `rnodev`: Device access recursive
- `rexec` / `rnoexec`: Execute permission recursive
- `rsync` / `rasync` / `rdirsync`: Sync behavior recursive
- `rmand` / `rnomand`: Mandatory locking recursive
- `ratime` / `rnoatime` / `rdiratime` / `rnodiratime` / `rrelatime` / `rnorelatime` / `rstrictatime` / `rnostrictatime`: Atime behavior recursive

### ID Mapped Mounts

Create ID-mapped mounts with custom mappings:

```json
{
  "mounts": [
    {
      "destination": "/mnt/idmapped",
      "type": "bind",
      "source": "/host/data",
      "options": ["bind", "idmap"]
    }
  ]
}
```

**Custom mapping:**

```json
{
  "mounts": [
    {
      "destination": "/mnt/idmapped",
      "type": "bind",
      "source": "/host/data",
      "options": ["bind", "idmap=uids=0-1-10#10-11-10;gids=0-100-10"]
    }
  ]
}
```

**Mapping format:** `idmap=uids=HOST_START-CONTAINER_START-LENGTH#...;gids=...`

Each triplet: `HOST_ID-CONTAINER_ID-LENGTH`

Multiple ranges separated by `#`.

**Relative mapping (to container user namespace):**

```json
{
  "mounts": [
    {
      "destination": "/mnt/idmapped",
      "type": "bind",
      "source": "/host/data",
      "options": ["bind", "idmap=uids=@1-3-10"]
    }
  ]
}
```

Prefix with `@` for relative mapping. Host ID calculated based on container user namespace position.

**Experimental feature** - can change without notice.

## Security Features

### AppArmor

Set AppArmor profile:

```bash
crun exec --apparmor my-profile container-id /bin/bash
```

Or in config.json:

```json
{
  "process": {
    "apparmorProfile": "my-profile"
  }
}
```

### SELinux

Set SELinux process label:

```bash
crun exec --process-label "system_u:object_r:container_t:s0" container-id /bin/bash
```

### Capabilities

Add capabilities to process:

```bash
crun exec --cap CAP_NET_ADMIN container-id /bin/bash
```

### No New Privileges

Prevent privilege escalation:

```bash
crun exec --no-new-privs container-id /bin/bash
```

Or in config.json:

```json
{
  "process": {
    "noNewPrivileges": true
  }
}
```

## Systemd Integration

### Force cgroup v1 on Specific Mount

Run cgroup v1 containers on cgroup v2 system:

```json
{
  "annotations": {
    "run.oci.systemd.force_cgroup_v1": "/sys/fs/cgroup/systemd"
  }
}
```

**Setup (as root):**

```bash
mkdir /sys/fs/cgroup/systemd
mount cgroup -t cgroup /sys/fs/cgroup/systemd -o none,name=systemd,xattr
chown -R the_user.the_user /sys/fs/cgroup/systemd
```

Container host must have cgroup v1 mount present. For rootless, user needs permissions to mountpoint.

### Systemd Subgroup

Override systemd sub-cgroup name:

```json
{
  "annotations": {
    "run.oci.systemd.subgroup": "custom-name"
  }
}
```

Creates cgroup at: `/sys/fs/cgroup/$PATH/custom-name`

Empty string disables sub-cgroup creation.

Defaults:
- cgroup v2: `container`
- cgroup v1: `` (empty)

### Cgroup Delegation

Create delegated sub-cgroup for container management:

```json
{
  "annotations": {
    "run.oci.systemd.subgroup": "app",
    "run.oci.delegate-cgroup": "delegated"
  }
}
```

Creates: `/sys/fs/cgroup/$PATH/app/delegated`

- Runtime applies limits to `$PATH/app`
- Container manages `$PATH/app/delegated`
- Parent limits still apply to delegated cgroup
- **cgroup v2 only** (unsafe on v1)

## Hooks Output Redirection

Redirect hook process output:

```json
{
  "annotations": {
    "run.oci.hooks.stdout": "/var/log/hooks.log",
    "run.oci.hooks.stderr": "/var/log/hooks-errors.log"
  }
}
```

Files opened in append mode, created if they don't exist.

## Unprivileged Container Support

### Automatic User Namespace

When running as non-root user:

- User namespace automatically created
- Current user mapped to UID 0 in container
- Additional IDs from `/etc/subuid` and `/etc/subgid` added starting with ID 1

No special configuration needed - crun handles this automatically.

### Rootless State Directory

State stored in `$XDG_RUNTIME_DIR/crun` instead of `/run/crun`.

Override with:

```bash
crun --root /custom/path run container-id
```

## Logging Configuration

### Log Destination

```bash
# Log to file (default)
crun --log file:/var/log/crun.log run container-id

# Log to journald
crun --log journald:mycontainer run container-id

# Log to syslog
crun --log syslog:myapp run container-id
```

### Log Format

```bash
# JSON format (default is text)
crun --log-format json run container-id
```

### Log Level

```bash
# Debug level
crun --log-level debug run container-id

# Warning level
crun --log-level warning run container-id

# Error level (default)
crun --log-level error run container-id
```

## Debug Mode

Enable verbose output:

```bash
crun --debug run container-id
```

## Experimental Features

The following features are experimental and may change or be removed:

- `run.oci.seccomp.receiver` - Seccomp listener socket
- `run.oci.seccomp.plugins` - Seccomp plugins
- `run.oci.seccomp_bpf_data` - Raw seccomp BPF data
- `run.oci.pidfd_receiver` - PID file descriptor receiver
- `run.oci.handler` - Custom handlers (krun, wasm)
- ID mapped mounts (`idmap` option)
- Mount options: `copy-symlink`, `dest-nofollow`, `src-nofollow`

## Best Practices

1. **Use seccomp profiles** for additional security hardening
2. **Enable noNewPrivileges** unless privilege escalation is required
3. **Drop unnecessary capabilities** rather than adding them
4. **Test experimental features** in non-production environments
5. **Use tmpcopyup** when containers need to modify mounted configurations
6. **Prefer cgroup v2** for new deployments (v1 is deprecated)
7. **Leverage systemd integration** on systemd-based systems
8. **Document custom annotations** for team knowledge sharing

## Compatibility Notes

- WebAssembly support requires crun built with WASI handler
- ID mapped mounts require kernel 5.10+
- Some mount options may not be available on all kernels
- cgroup v2 features require unified hierarchy enabled
- SELinux/AppArmor profiles must exist on host system
