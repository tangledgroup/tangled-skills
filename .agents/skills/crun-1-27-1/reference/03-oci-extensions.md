# OCI Extensions

crun extends the OCI runtime specification through annotations and custom mount options. These features are crun-specific and may not be portable to other runtimes.

## Handler Annotations

### `run.oci.handler=HANDLER`

Experimental feature to run a custom handler for exec'ing the container process. Supported values:

- **`krun`** — loads `libkrun.so` to launch the container as a microVM using libkrun. Supports external kernels, virtio-gpu, nitro enclaves, and passt-based networking.
- **`wasm`** — run WebAssembly workloads natively. Accepts `.wasm` binaries and `.wat` text files (wasmer-only for on-the-fly compilation). Supported runtimes: wasmedge, wasmer, wasmtime, wamr.

## Seccomp Extensions

### `run.oci.seccomp.receiver=PATH`

Send the seccomp listener to a UNIX socket at the specified absolute path. Can also be set via `RUN_OCI_SECCOMP_RECEIVER` environment variable. Experimental.

### `run.oci.seccomp.plugins=PATH`

Handle the seccomp listener FD through specified plugins. Plugin must be an absolute path or loadable via `dlopen(3)`. Multiple plugins separated by `:`.

### `run.oci.seccomp_fail_unknown_syscall=1`

Fail when an unknown syscall is encountered in the seccomp configuration.

### `run.oci.seccomp_bpf_data=PATH`

Ignore the seccomp section in OCI config and use base64-encoded raw BPF data directly for `seccomp(SECCOMP_SET_MODE_FILTER)`. Experimental.

## SELinux / LSM Extensions

### `run.oci.mount_context_type=context`

Set the mount context type on volumes mounted with SELinux labels. Valid values: `context` (default), `fscontext`, `defcontext`, `rootcontext`. See `mount(8)` for details.

## Group Management

### `run.oci.keep_original_groups=1`

Skip the `setgroups` syscall, preserving the original supplementary groups instead of setting or resetting them per the OCI config.

## PID File Descriptor

### `run.oci.pidfd_receiver=PATH`

Send the pidfd for the container process to a UNIX socket at the specified path. Experimental.

## systemd Annotations

### `run.oci.systemd.force_cgroup_v1=/PATH`

Override the specified mount point with a cgroup v1 mount (`none,name=systemd`). Useful for running containers with older systemd versions that lack cgroup v2 support on a cgroup v2 host. The cgroup v1 mount must already exist on the host.

### `run.oci.systemd.subgroup=SUBGROUP`

Override the name of the systemd sub-cgroup created under the scope. Final path: `/sys/fs/cgroup/$PATH/$SUBGROUP`. Set to empty string to skip sub-cgroup creation. Defaults to `container` on cgroup v2, `""` on cgroup v1.

### `run.oci.delegate-cgroup=DELEGATED-CGROUP`

Create an additional sub-cgroup under the subgroup and move the container process there. The runtime applies limits only to `$PATH/$SUBGROUP`; the container payload fully manages `$DELEGATED-CGROUP`. Supported only on cgroup v2 (delegation is not safe on v1).

## Hooks Output

### `run.oci.hooks.stdout=FILE`

Redirect hook process stdout to the specified file (append mode, created if missing).

### `run.oci.hooks.stderr=FILE`

Redirect hook process stderr to the specified file (append mode, created if missing).

## CRIU Configuration

### `org.criu.config=FILE`

Specify a CRIU RPC configuration file. If not provided, crun checks `/etc/criu/crun.conf`, then falls back to `/etc/criu/runc.conf`. Requires CRIU 4.2+. Options in the config override default CRIU values set by crun.

## Custom Mount Options

### tmpcopyup

For tmpfs mounts, recursively copy the shadowed path content into the tmpfs.

### copy-symlink

If the source of a bind mount is a symlink, recreate the symlink at the destination instead of resolving it. Fails if the destination exists and is not a matching symlink.

### dest-nofollow

When the destination of a bind mount is a symbolic link, mount the symlink itself rather than its target.

### src-nofollow

When the source of a bind mount is a symbolic link, use the symlink itself rather than its target.

### r$FLAG (recursive mount flags)

Set mount flags recursively for all child mounts. Supported flags: `rro`, `rrw`, `rsuid`, `rnosuid`, `rdev`, `rnodev`, `rexec`, `rnoexec`, `rsync`, `rasync`, `rdirsync`, `rmand`, `rnomand`, `ratime`, `rnoatime`, `rdiratime`, `rnodiratime`, `rrelatime`, `rnorelatime`, `rstrictatime`, `rnostrictatime`.

### idmap

ID-mapped mounts using the container target user namespace. Supports custom mappings:

```
idmap=uids=0-1-10#10-11-10;gids=0-100-10
```

Each triplet is `start-hostID-start-containerID-length`. Multiple ranges separated by `#`. Prepend `@` for relative mappings to the container user namespace.

## Automatic User Namespace

When running as a non-root user, crun automatically creates a user namespace even if not specified in the config. The current user is mapped to ID 0 inside the container, and additional IDs from `/etc/subuid` and `/etc/subgid` are added starting at ID 1.
