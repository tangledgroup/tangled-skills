# Container Operations

## Contents
- Container Lifecycle
- Executing Commands
- Container Logs
- Container Statistics
- File Operations
- Container Inspection and Properties
- Commit Container to Image
- Update Container Configuration
- Wait for Container State
- Rename and Resize
- ContainersManager Operations

## Container Lifecycle

### Create a container

```python
container = client.containers.create(
    "alpine:latest",
    command=["sleep", "3600"],
    name="my-container",
    detach=True,
    ports={"8080/tcp": 8080},
    environment={"APP_ENV": "production"},
    volumes={"/host/path": {"bind": "/container/path", "mode": "rw"}},
    mem_limit="512m",
    cpu_shares=512,
    network_mode="bridge",
)
```

Key create parameters:

- `auto_remove` (bool): Remove container when process exits
- `blkio_weight` (int): Block IO weight, 10–1000
- `cap_add` / `cap_drop` (list[str]): Kernel capabilities
- `cgroup_parent` (str): Override default parent cgroup
- `cpu_period` / `cpu_quota` (int): CPU CFS scheduling
- `cpuset_cpus` (str): CPUs allowed for execution, e.g. `"0-3"` or `"0,1"`
- `devices` (list[str]): Host devices as `"<host>:<container>:<perms>"`
- `dns` / `dns_search` (list[str]): DNS configuration
- `entrypoint` (str | list[str]): Container entrypoint
- `extra_hosts` (dict[str, str]): Additional hostname-to-IP mappings
- `healthcheck` (dict): Health check specification
- `hostname` (str): Container hostname
- `init` (bool): Run init process for signal forwarding
- `ipc_mode` (str): IPC namespace mode
- `labels` (dict[str, str] | list[str]): Labels
- `log_config` (LogConfig): Logging driver configuration
- `mem_limit` (int | str): Memory limit, e.g. `"128m"`, `"1g"`
- `memswap_limit` (int | str): Memory + swap limit
- `mounts` (list[Mount]): Mount specifications with type, source, target
- `name` (str): Container name
- `network_mode` (str): `"bridge"`, `"none"`, `"host"`, `"container:<name>"`, `"ns:<path>"`
- `oom_kill_disable` (bool): Disable OOM killer
- `pid_mode` (str): `"host"` to use host PID namespace
- `pids_limit` (int): Max processes, -1 for unlimited
- `platform` (str): Platform format `os[/arch[/variant]]`
- `ports` (dict): Port bindings, e.g. `{"2222/tcp": 3333}`
- `privileged` (bool): Run in privileged mode
- `read_only_fs` (bool): Mount root filesystem as read-only
- `restart_policy` (dict): Restart behavior, e.g. `{"Name": "on-failure", "MaximumRetryCount": 5}`
- `security_opt` (list[str]): Security options
- `user` (str): User to run as
- `working_dir` (str): Working directory

### Start / Stop / Restart

```python
container.start()
container.stop(timeout=30)
container.restart(timeout=10)
```

`stop()` keyword arguments:
- `all` (bool): Stop all containers (Podman only)
- `ignore` (bool): Ignore error if already stopped (Podman only)
- `timeout` (int): Seconds before killing

### Pause / Unpause

```python
container.pause()
container.unpause()
```

### Kill

```python
container.kill(signal="SIGTERM")  # or signal number, e.g. 15
```

### Remove

```python
container.remove(v=True, force=True)
# or via manager:
client.containers.remove("my-container", v=True, force=True)
```

## Executing Commands

```python
exit_code, output = container.exec_run(
    ["sh", "-c", "echo hello && whoami"],
    stdout=True,
    stderr=True,
    demux=True,  # returns (stdout, stderr) tuple
)

# Streamed output
exit_code, stream = container.exec_run(
    ["ping", "-c", "5", "localhost"],
    stream=True,
)
for chunk in stream:
    print(chunk.decode())
```

Parameters:
- `cmd` (str | list[str]): Command to execute
- `stdout` / `stderr` / `stdin` (bool): Stream attachments
- `tty` (bool): Allocate pseudo-TTY
- `privileged` (bool): Run as privileged
- `user` (str): Execute as user
- `detach` (bool): Detach from exec
- `stream` (bool): Stream response data
- `environment` (dict | list[str]): Environment variables
- `workdir` (str): Working directory
- `demux` (bool): Return stdout/stderr separately

## Container Logs

```python
# Get all logs as bytes
logs = container.logs()

# Stream logs
for line in container.logs(stream=True, follow=True):
    print(line.decode())

# Tail last 100 lines
logs = container.logs(tail=100)

# With timestamps
logs = container.logs(timestamps=True)
```

Parameters:
- `stdout` / `stderr` (bool): Include streams
- `stream` (bool): Return generator
- `timestamps` (bool): Show timestamps
- `tail` (str | int): Number of lines or `"all"`
- `since` (datetime | int): Logs since this time
- `follow` (bool): Follow log output
- `until` (datetime | int): Logs before this time

## Container Statistics

```python
# Single snapshot
stats = container.stats(stream=False, decode=True)
print(stats["cpu_percent"], stats["mem_usage"])

# Streamed statistics
for stat in container.stats(stream=True, decode=True):
    print(stat["name"], stat["cpu_percent"])
```

## File Operations

### Export filesystem as tar

```python
with open("container.tar", "wb") as f:
    for chunk in container.export(chunk_size=2*1024*1024):
        f.write(chunk)
```

### Download file from container

```python
tar_data, stat_info = container.get_archive("/path/in/container")
```

### Upload file to container

```python
# Upload a tar archive
container.put_archive("/path/in/container", data=tar_bytes)

# Auto-build tar from local path
container.put_archive("/dest/path", data=None)  # reads local /dest/path
```

### Inspect filesystem changes

```python
changes = container.diff()
# Returns list of {"Kind": 0|1|2, "Path": "/path"}
# Kind: 0=added, 1=modified, 2=deleted
```

## Container Inspection and Properties

```python
attrs = container.inspect()  # full JSON from service

# Common properties
print(container.id)        # Full ID
print(container.short_id)  # Truncated ID
print(container.name)      # Container name
print(container.status)    # "running", "stopped", "exited", etc.
print(container.image)     # Image object
print(container.labels)    # dict[str, str]
print(container.ports)     # Port mappings
```

## Commit Container to Image

```python
new_image = container.commit(
    repository="my-repo/my-image",
    tag="v1.0",
    message="Snapshot of running container",
    author="Dev Team",
    pause=True,
)
```

## Update Container Configuration

```python
container.update(
    restart_policy="on-failure",
    restart_retries=5,
    memory={"limit": 1_073_741_824},  # 1GB
    pids={"limit": 100},
)
```

## Wait for Container State

```python
exit_code = container.wait(
    condition="exited",
    interval="5s",
    timeout=60,
)
```

Conditions: `"configured"`, `"created"`, `"running"`, `"stopped"`, `"paused"`, `"exited"`, `"removing"`, `"stopping"`.

## Rename and Resize

```python
container.rename("new-name")
container.resize(height=40, width=120)
```

### Init Container

```python
container.init()  # Initialize container (run init process)
```

## ContainersManager Operations

```python
# List containers
containers = client.containers.list()
containers = client.containers.list(all=True)
containers = client.containers.list(filters={"status": "running"})

# Get by name or ID
container = client.containers.get("my-container")

# Check existence
exists = client.containers.exists("my-container")

# Prune stopped containers
result = client.containers.prune()
```

## Run a Container (RunMixin)

```python
# Run and wait for completion, return logs
container = client.containers.run("alpine", ["echo", "hello"])

# Run detached
container = client.containers.run(
    "alpine:latest",
    ["sleep", "3600"],
    detach=True,
    name="long-running",
)

# Auto-remove after exit
container = client.containers.run(
    "alpine",
    ["echo", "temporary"],
    remove=True,
)
```

Parameters beyond `create()`:
- `stdout` (bool): Include stdout, default True
- `stderr` (bool): Include stderr, default False
- `remove` (bool): Delete container on client side after exit

Pull parameters (when image not found locally):
- `auth_config` (dict): Override credentials with `username` and `password`
- `platform` (str): Platform format `os[/arch[/variant]]`
- `policy` (str): Pull policy — `"missing"` (default), `"always"`, `"never"`, `"newer"`

Raises:
- `ContainerError` — when container exits with non-zero code
- `ImageNotFound` — when image not found by Podman service
- `APIError` — when Podman service reports an error
