# CLI Reference

## create

Create a container. The runtime detaches from the container process once the environment is set up. Use `start` to begin execution.

```bash
crun [global options] create [options] CONTAINER-ID
```

Options:

- `--bundle=PATH` — path to the OCI bundle (default: current directory)
- `--config=FILE` — override configuration file (default: `config.json`)
- `--console-socket=SOCKET` — UNIX socket for the container TTY ptmx end
- `--no-new-keyring` — keep the same session keyring
- `--preserve-fds=N` — additional file descriptors to pass into the container
- `--pid-file=PATH` — file to write the container process PID

## run

Create and immediately start a container.

```bash
crun [global options] run [options] CONTAINER-ID
```

Options: same as `create`, plus:

- `--detach` — detach the container process from the current session

## delete

Remove container definition.

```bash
crun [global options] delete [options] CONTAINER-ID
```

Options:

- `--force` — delete even if the container is still running
- `--regex=REGEX` — delete all containers matching the regex pattern

## exec

Execute a command in a running container.

```bash
crun [global options] exec [options] CONTAINER-ID CMD [ARGS...]
```

Options:

- `--apparmor=PROFILE` — set AppArmor profile for the process
- `--cap=CAP` — additional capability to add
- `--console-socket=SOCKET` — UNIX socket for TTY
- `--cwd=PATH` — working directory for the process
- `--detach` — detach from the container process
- `--cgroup=PATH` — sub-cgroup path inside the container cgroup (must already exist)
- `--env=ENV` — environment variable to set
- `--no-new-privs` — set no-new-privileges for the process
- `--preserve-fds=N` — additional file descriptors to pass in
- `--process=FILE` — path to a JSON process configuration file
- `--process-label=VALUE` — SELinux process label
- `--pid-file=PATH` — file to write the new process PID
- `-t` / `--tty` — allocate a pseudo TTY
- `-u USERSPEC` / `--user=USERSPEC` — user in form `UID[:GID]`

## list

List known containers.

```bash
crun [global options] list [-q | --quiet]
```

## kill

Send signal to the container init process. Default signal is SIGTERM.

```bash
crun [global options] kill [options] CONTAINER-ID [SIGNAL]
```

Options:

- `--all` — kill all processes in the container
- `--regex=REGEX` — kill all containers matching the regex

## ps

Show processes running in a container.

```bash
crun [global options] ps [options] CONTAINER-ID
```

Options:

- `--format=FORMAT` — output format: `table` (default) or `json`

## spec

Generate an OCI configuration file.

```bash
crun [global options] spec [-b DIR | --bundle=DIR] [--rootless]
```

## start

Start a previously created container. A container cannot be started multiple times.

```bash
crun [global options] start CONTAINER-ID
```

## state

Output the state of a container as JSON.

```bash
crun [global options] state CONTAINER-ID
```

## pause / resume

Pause or resume all processes in the container.

```bash
crun [global options] pause CONTAINER-ID
crun [global options] resume CONTAINER-ID
```

## update

Update container resource constraints at runtime.

```bash
crun [global options] update [options] CONTAINER-ID
```

Options:

- `--blkio-weight=VALUE` — per-cgroup I/O weight
- `--cpu-period=VALUE` — CPU CFS period for hardcapping
- `--cpu-quota=VALUE` — CPU CFS hardcap limit
- `--cpu-rt-period=VALUE` — CPU realtime period
- `--cpu-rt-runtime=VALUE` — CPU realtime hardcap limit
- `--cpu-share=VALUE` — CPU shares
- `--cpuset-cpus=VALUE` — CPU(s) to use
- `--cpuset-mems=VALUE` — memory node(s) to use
- `--kernel-memory=VALUE` — kernel memory limit
- `--kernel-memory-tcp=VALUE` — kernel memory limit for TCP buffer
- `--memory=VALUE` — memory limit
- `--memory-reservation=VALUE` — memory reservation (soft limit)
- `--memory-swap=VALUE` — total memory usage (memory + swap)
- `--pids-limit=VALUE` — maximum number of PIDs allowed
- `-r` / `--resources=FILE` — path to a JSON resources configuration file

## mounts add / remove

Dynamically modify mounts while the container is running (experimental).

```bash
crun [global options] mounts add CONTAINER-ID MOUNTS-JSON
crun [global options] mounts remove CONTAINER-ID MOUNTS-JSON
```

`MOUNTS-JSON` is a file containing the `mounts` section of an OCI config. For `remove`, only the `destination` attribute of each mount is used.
