# Checkpoint and Restore

crun integrates with CRIU (Checkpoint/Restore In Userspace) to checkpoint running containers and restore them later. This enables live migration, state preservation, and disaster recovery scenarios.

## checkpoint

Checkpoint a running container using CRIU.

```bash
crun [global options] checkpoint [options] CONTAINER-ID
```

Options:

- `--image-path=DIR` — directory for saving CRIU image files
- `--work-path=DIR` — directory for work files and logs
- `--leave-running` — leave the process running after checkpointing
- `--tcp-established` — allow open TCP connections to be checkpointed
- `--ext-unix-sk` — allow external UNIX sockets
- `--shell-job` — allow shell jobs (for processes not started by CRIU)
- `--pre-dump` — perform a pre-dump: checkpoint memory without stopping the container. A pre-dump cannot be restored from directly; it must be followed by a final checkpoint. Multiple pre-dumps are allowed to reduce downtime during the final checkpoint.
- `--parent-path=DIR` — path to a previous pre-dump (relative to `--image-path`). Required for subsequent pre-dumps or the final checkpoint after pre-dumps.
- `--manage-cgroups-mode=MODE` — CRIU cgroup management mode: `soft` (default), `ignore`, `full`, or `strict`

### Pre-dump Workflow

Pre-dump reduces container downtime during checkpointing by capturing most of the memory state while the container continues running, then performing a quick final checkpoint to capture only the delta.

```bash
# First pre-dump (container keeps running)
crun checkpoint --pre-dump --image-path /checkpoint/pre1 my-container

# Second pre-dump (optional, further reduces final downtime)
crun checkpoint --pre-dump --parent-path pre1 --image-path /checkpoint/pre2 my-container

# Final checkpoint (container stops briefly)
crun checkpoint --parent-path pre2 --image-path /checkpoint/final my-container
```

## restore

Restore a container from a CRIU checkpoint.

```bash
crun [global options] restore [options] CONTAINER-ID
```

Options:

- `-b DIR` / `--bundle=DIR` — container bundle directory (default: `.`)
- `--image-path=DIR` — path to CRIU image files
- `--work-path=DIR` — path for work files and logs
- `--tcp-established` — restore open TCP connections
- `--ext-unix-sk` — allow external UNIX sockets
- `--shell-job` — allow shell jobs
- `--detach` — detach from the container process
- `--pid-file=FILE` — file to write the restored container PID
- `--manage-cgroups-mode=MODE` — CRIU cgroup management mode: `soft` (default), `ignore`, `full`, or `strict`
- `--lsm-profile=TYPE:NAME` — LSM profile for restore. TYPE is `apparmor` or `selinux`
- `--lsm-mount-context=VALUE` — replace existing mount context with the specified value during restore. Useful when restoring into an existing Pod with different SELinux labels

## CRIU Configuration

crun reads CRIU configuration from:

1. `org.criu.config` annotation (highest priority)
2. `/etc/criu/crun.conf`
3. `/etc/criu/runc.conf` (fallback for runc compatibility)

Requires CRIU version 4.2 or newer. Configuration options override crun's default CRIU settings. Common options include `tcp-established`, `tcp-close`, and `log-file`.

## systemd Integration

When running under systemd, crun uses a proxy process during restore to initialize the cgroup so that all container processes are restored into the correct cgroup hierarchy.
