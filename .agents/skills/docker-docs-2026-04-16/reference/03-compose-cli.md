# Docker Compose CLI

## Commands

### Lifecycle

- `docker compose up` — Create and start containers
  - `-d` — Detached mode
  - `--build` — Build images before starting
  - `--no-deps` — Don't start linked services
  - `--force-recreate` — Recreate containers even if unchanged
  - `--no-recreate` — Skip recreation if already exists
  - `--scale service=N` — Scale a service to N replicas
  - `--profile name` — Enable services with specified profile

- `docker compose down` — Stop and remove containers, networks
  - `-v` — Remove volumes
  - `--rmi local` — Remove images
  - `--remove-orphans` — Remove containers not defined in Compose file

- `docker compose start` / `stop` / `restart` — Start, stop, or restart services
- `docker compose pause` / `unpause` — Pause or unpause containers
- `docker compose kill` — Force stop containers
- `docker compose rm` — Remove stopped containers

### Build

- `docker compose build` — Build or rebuild services
  - `--no-cache` — Don't use cache
  - `--parallel` — Build in parallel
  - `--progress=plain` — Plain progress output
  - `-t service:tag` — Set tag for image

### Images

- `docker compose pull` — Pull service images
- `docker compose push` — Push service images
- `docker compose create` — Create containers without starting

### Inspection

- `docker compose ps` — List containers
- `docker compose images` — List images used by services
- `docker compose config` — Validate and view resolved Compose file
- `docker compose top` — Display running processes
- `docker compose events` — Receive real-time events (json format)
- `docker compose port` — Print public port for a service port binding

### Execution

- `docker compose exec [service] command` — Execute command in a running container
  - `-d` — Detached mode
  - `-T` — Disable pseudo-tty
  - `--privileged` — Privileged mode
  - `--user username` — Username or UID

- `docker compose run [service] command` — Run a one-off command
  - `--no-deps` — Don't start linked services
  - `--rm` — Remove container after exit
  - `-d` — Detached mode

### Logs

- `docker compose logs [-f] [--tail=N] [services...]` — View output from containers
  - `-f` — Follow log output
  - `--tail=N` — Number of lines to show
  - `--no-color` — Disable color codes
  - `--timestamps` — Show timestamps
  - `--follow` — Follow log output

### Other

- `docker compose version` — Show version
- `docker compose wait` — Block until service containers stop
- `docker compose attach` — Attach to a service container

## Global Options

- `-f, --file FILE` — Specify Compose file (default: `compose.yaml`)
- `-p, --project-name NAME` — Project name
- `--project-directory PATH` — Working directory
- `--env-file PATH` — Environment file
- `--profile NAME` — Enable profiles
- `--compatibility` — Run in compatibility mode
- `--verbose` — Verbose output
- `--no-ansi` — Disable ANSI control characters
- `--log-level DEBUG|INFO|WARNING|ERROR|CRITICAL`

## Environment Variables

Compose reads environment variables from:
1. Shell environment
2. `.env` file in project directory
3. Files specified with `--env-file`

Special variables:
- `COMPOSE_PROJECT_NAME` — Override project name
- `COMPOSE_FILE` — Override default file paths
- `COMPOSE_PROFILES` — Default profiles (comma-separated)

## Profiles

Profiles allow conditional service activation:
```yaml
services:
  web:
    image: nginx
  admin:
    image: adminer
    profiles: ["admin"]
  debug-tools:
    image: nicolaka/netshoot
    profiles: ["debug"]
```

```bash
docker compose --profile admin up     # Starts web + admin
docker compose --profile debug up     # Starts web + debug-tools
```

Services without profiles are always started.
