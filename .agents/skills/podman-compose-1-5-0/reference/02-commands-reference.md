# Commands Reference

Podman Compose provides commands that mirror docker-compose, translating compose file directives into native `podman` CLI calls.

## Global Options

```
-f, --file         Specify compose file (default: compose.yaml)
-p, --project-name Project name override
--project-directory Directory containing the compose file
--env-file         Specify dotenv file (default: .env)
--verbose          Verbose output
--no-pod           Disable pod creation
--pod-args         Extra args for podman pod create
--userns           User namespace mode
--infer-hostname   Infer hostname from service name
```

## Lifecycle Commands

### up

Create and start services. Prepares images (pull or build), creates networks and volumes, then starts containers in dependency order.

```bash
podman-compose up [-d] [--build] [--force-recreate] [--no-deps] [--scale SERVICE=NUM] [SERVICE...]
```

Flags:
- `-d` — Detached mode (run in background)
- `--build` — Build images before starting
- `--force-recreate` — Recreate containers even if config unchanged
- `--no-deps` — Don't start linked services
- `--no-cache` — Don't use cache when building images
- `--timeout` — Shutdown timeout in seconds
- `--remove-orphans` — Remove containers for services not defined in compose file
- `--renew-anon-volumes` — Recreate anonymous volumes instead of existing ones
- `--scale SERVICE=NUM` — Scale a service to N replicas (podman-compose specific)

### down

Tear down the entire stack — stops containers, removes networks and volumes.

```bash
podman-compose down [--timeout SECS] [-v] [--remove-orphans]
```

Flags:
- `-v` — Remove named volumes
- `--timeout` — Seconds to wait before killing containers
- `--remove-orphans` — Remove containers not defined in compose file

### start / stop / restart

Control service lifecycle individually:

```bash
podman-compose start [SERVICE...]
podman-compose stop [--timeout SECS] [SERVICE...]
podman-compose restart [--timeout SECS] [SERVICE...]
```

## Image Commands

### build

Build or rebuild service images using `podman build`.

```bash
podman-compose build [--no-cache] [--pull] [--pull-always] [SERVICE...]
```

Flags:
- `--no-cache` — Don't use cache when building
- `--pull` — Attempt to pull a newer version of the base image
- `--pull-always` — Always pull, error if image exists locally
- `--ssh` — SSH agent socket or keys to expose during build

### pull

Pull service images from registries.

```bash
podman-compose pull [--policy always|never|missing] [SERVICE...]
```

### push

Push service images to registries.

```bash
podman-compose push [SERVICE...]
```

### images

List images used by created containers.

```bash
podman-compose images [--quiet]
```

## Execution Commands

### run

Create a container similar to a service and run a one-off command.

```bash
podman-compose run [--no-deps] [-d] [--rm] [--name NAME] SERVICE [COMMAND...]
```

Flags:
- `--no-deps` — Don't start linked services
- `-d` — Detached mode
- `--rm` — Remove container after exit
- `--name` — Custom container name
- `--entrypoint` — Override entrypoint
- `-e KEY=VAL` — Set environment variable
- `-v HOST:CONTAINER` — Add volume mount

### exec

Execute a command in a running container.

```bash
podman-compose exec [-d] [--index N] [--env KEY=VAL] SERVICE COMMAND [ARGS...]
```

Flags:
- `-d` — Detached mode
- `--index N` — Target the Nth container of a scaled service (1-based)
- `-e KEY=VAL` — Set environment variable
- `--privileged` — Run in privileged mode
- `--user USERNAME` — Username or UID
- `--workdir PATH` — Working directory inside container
- `-T` — Disable pseudo-TTY allocation

## Inspection Commands

### ps

Show status of containers.

```bash
podman-compose ps [--quiet] [--format FORMAT] [SERVICE...]
```

Flags:
- `--quiet` — Only display container IDs
- `--format` — Custom format string

### logs

Show logs from services.

```bash
podman-compose logs [-f] [--tail N] [--no-color] [SERVICE...]
```

Flags:
- `-f` — Follow log output
- `--tail N` — Number of lines to show
- `--no-color` — Disable colorized output
- `--follow` — Alias for `-f`

### port

Print the public port for a port binding.

```bash
podman-compose port SERVICE PRIVATE_PORT [--index N]
```

### config

Display the resolved compose file configuration.

```bash
podman-compose config [--services] [--hash] [--quiet]
```

Flags:
- `--services` — Print service names, one per line
- `--hash` — Print service hash
- `--quiet` — Only print service names

### stats

Display resource usage statistics for services.

```bash
podman-compose stats [--no-stream] [SERVICE...]
```

### images

List images used by created containers.

```bash
podman-compose images [--quiet]
```

### version

Show podman-compose version.

```bash
podman-compose version [--short] [--format json|pretty]
```

## Control Commands

### pause / unpause

Pause or unpause all running containers.

```bash
podman-compose pause [SERVICE...]
podman-compose unpause [SERVICE...]
```

### kill

Kill containers with a specific signal.

```bash
podman-compose kill [-s SIGNAL] [--all] [SERVICE...]
```

Flags:
- `-s` — Signal to send (default: SIGKILL)
- `--all` — Kill all running containers in the stack

### wait

Wait for running containers to stop.

```bash
podman-compose wait [SERVICE...]
```

### format

Format and normalize a compose file.

```bash
podman-compose format
```

## Systemd Integration

Generate systemd unit files for compose stacks, enabling rootless service management.

```bash
podman-compose systemd [-a create-unit] [--dir DIR] [--name NAME]
```

Flags:
- `-a` — Action (`create-unit` to generate unit file)
- `--dir` — Output directory for unit files
- `--name` — Custom unit name

First-time setup requires registering the unit template:

```bash
sudo podman-compose systemd -a create-unit
```

Then generate per-project units:

```bash
podman-compose systemd --dir ~/.config/systemd/user
```

## Command Decorator System

Commands are registered using Python decorators. `@cmd_run` registers a command handler, `@cmd_parse` adds argument parsing. This enables clean separation of command logic and CLI argument definition.
