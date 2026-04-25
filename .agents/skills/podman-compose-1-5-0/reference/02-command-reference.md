# Command Reference

Complete reference for all podman-compose commands with options and examples.

## Global Options

Available for all commands:

```bash
podman-compose [global-options] <command> [command-options] [services]
```

| Option | Description |
|--------|-------------|
| `-f, --file FILE` | Specify compose file (default: `compose.yaml` or `docker-compose.yml`) |
| `-p, --project NAME` | Specify project name (default: directory name) |
| `--profile PROFILE` | Specify a profile to enable |
| `--env-file FILE` | Specify an alternate environment file |
| `-c, --podman-cmd CMD` | Path to podman binary (default: use `$PATH`) |
| `--podman-args ARGS` | Custom global arguments passed to all podman commands |
| `--pod-args ARGS` | Custom arguments passed to `podman pod` commands |
| `-v, --version` | Show version information |
| `--help` | Show help message |
| `--no-ansi` | Do not print ANSI control characters |
| `--no-color` | Produce monochrome output |
| `-q, --quiet` | Show only minimal output |
| `--verbose` | Print debugging output |

## up

Create and start the entire stack or specific services.

```bash
podman-compose up [options] [services...]
```

### Options

| Option | Description |
|--------|-------------|
| `-d, --detach` | Run containers in background (detached mode) |
| `--no-build` | Don't build images, even if missing |
| `--build` | Build images before starting containers |
| `--no-recreate` | Don't recreate containers if configuration unchanged |
| `--force-recreate` | Recreate containers even if configuration unchanged |
| `--no-deps` | Don't start linked services (dependencies) |
| `--scale SERVICE=NUM` | Scale SERVICE to NUM instances |
| `--abort-on-container-exit` | Stop all containers if any container exits |
| `--remove-orphans` | Remove containers for services not in compose file |
| `--always-recreate-deps` | Recreate dependent containers (incompatible with --no-recreate) |
| `-t, --timeout SECS` | Shutdown timeout in seconds (default: 10) |
| `--attach ATTACH` | Attach to specific services instead of all |

### Examples

```bash
# Start all services in foreground
podman-compose up

# Start all services in background
podman-compose up -d

# Start only web and api services
podman-compose up web api

# Build images before starting
podman-compose up --build

# Scale web service to 3 replicas
podman-compose up -d --scale web=3

# Recreate containers even if unchanged
podman-compose up --force-recreate -d

# Don't rebuild, use existing images
podman-compose up --no-build

# Simulate without executing (dry run)
podman-compose up --dry-run
```

## down

Tear down the entire stack: stop and remove containers, networks, and optionally volumes.

```bash
podman-compose down [options]
```

### Options

| Option | Description |
|--------|-------------|
| `-v, --volumes` | Remove named volumes defined in the compose file |
| `--remove-orphans` | Remove containers not defined in compose file |
| `--timeout SECS` | Shutdown timeout in seconds |
| `--no-deps` | Don't stop/remove dependent services |

### Examples

```bash
# Stop and remove containers and networks
podman-compose down

# Also remove named volumes
podman-compose down -v

# Remove orphan containers too
podman-compose down --remove-orphans

# Custom shutdown timeout
podman-compose down --timeout 30
```

## start / stop / restart

Lifecycle management for specific services.

```bash
podman-compose start [services...]
podman-compose stop [options] [services...]
podman-compose restart [options] [services...]
```

### Options (stop/restart)

| Option | Description |
|--------|-------------|
| `-t, --timeout SECS` | Shutdown timeout in seconds |
| `--no-deps` | Don't affect linked services |

### Examples

```bash
# Start specific services
podman-compose start web api

# Stop all services
podman-compose stop

# Stop with custom timeout
podman-compose stop --timeout 30

# Restart database service
podman-compose restart db

# Restart without affecting dependencies
podman-compose restart --no-deps web
```

## ps

Show status of containers.

```bash
podman-compose ps [options] [services...]
```

### Options

| Option | Description |
|--------|-------------|
| `-a, --all` | Show all containers (including stopped) |
| `-q, --quiet` | Show only container IDs |

### Examples

```bash
# Show running containers
podman-compose ps

# Show all containers including stopped
podman-compose ps -a

# Show specific service status
podman-compose ps web

# Get container IDs only
podman-compose ps -q
```

## logs

Display logs from services.

```bash
podman-compose logs [options] [services...]
```

### Options

| Option | Description |
|--------|-------------|
| `-f, --follow` | Follow log output (stream mode) |
| `-t, --timestamps` | Show timestamps in output |
| `--since TIMESTAMP` | Show logs since timestamp |
| `--until TIMESTAMP` | Show logs until timestamp |
| `--tail LINES` | Number of lines to show (default: all) |
| `--no-color` | Disable colorized output |

### Examples

```bash
# Follow logs from all services
podman-compose logs -f

# Follow logs from specific service
podman-compose logs -f web api

# Show last 100 lines with timestamps
podman-compose logs --tail 100 -t

# Show logs since 2 hours ago
podman-compose logs --since 2h -f

# Monitor all services without color
podman-compose logs -f --no-color
```

## build

Build images for services.

```bash
podman-compose build [options] [services...]
```

### Options

| Option | Description |
|--------|-------------|
| `--parallel` | Build in parallel (not sequential) |
| `--pull` | Always attempt to pull a newer version of the image |
| `--no-cache` | Don't use cache when building images |
| `--compress` | Compress the build context using gzip |
| `--quiet` | Don't print build output |

### Examples

```bash
# Build all services
podman-compose build

# Build specific service
podman-compose build api

# Pull latest base images before building
podman-compose build --pull

# Build without cache (clean build)
podman-compose build --no-cache

# Build in parallel for faster builds
podman-compose build --parallel
```

## config

Display the parsed compose file configuration.

```bash
podman-compose config [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--quiet` | Only validate, don't show config |
| `--services` | Print service names, one per line |
| `-h, --help` | Show help |

### Examples

```bash
# Show full parsed configuration
podman-compose config

# Validate compose file (exit code indicates success/failure)
podman-compose config --quiet

# List all service names
podman-compose config --services

# Check for syntax errors
podman-compose config || echo "Invalid compose file"
```

## run

Run a one-off command in a service container.

```bash
podman-compose run [options] SERVICE [COMMAND [ARGS...]]
```

### Options

| Option | Description |
|--------|-------------|
| `-d, --detach` | Detached mode: run container in background |
| `--name NAME` | Assign a custom name to the container |
| `-e KEY=VALUE` | Set environment variable |
| `-u, --user USER` | Run as specified user |
| `--no-deps` | Don't start linked services |
| `--rm` | Remove container after command completes |
| `-T` | Disable pseudo-tty allocation |

### Examples

```bash
# Run command in web service
podman-compose run web npm test

# Run interactive shell in api service
podman-compose run --rm api bash

# Run as specific user
podman-compose run -u nginx web ls -la /usr/share/nginx/html

# Set environment variable for one-off run
podman-compose run -e DEBUG=true api python debug.py

# Detached execution
podman-compose run -d --name worker-job worker process-data
```

## exec

Execute a command in a running container.

```bash
podman-compose exec [options] SERVICE [COMMAND [ARGS...]]
```

### Options

| Option | Description |
|--------|-------------|
| `-e KEY=VALUE` | Set environment variable |
| `-u, --user USER` | Run as specified user |
| `-T` | Disable pseudo-tty allocation |

### Examples

```bash
# Execute command in running container
podman-compose exec web ls -la

# Interactive shell in api service
podman-compose exec api bash

# Run as root (if container supports it)
podman-compose exec -u 0 db psql -U postgres

# Set environment variable for command
podman-compose exec -e NODE_ENV=test web npm test
```

## pull / push

Pull or push service images.

```bash
podman-compose pull [options] [services...]
podman-compose push [options] [services...]
```

### Options (pull)

| Option | Description |
|--------|-------------|
| `--ignore-pull-failures` | Continue with other pulls on failure |
| `--no-parallel` | Disable parallel pulling |

### Examples

```bash
# Pull all service images
podman-compose pull

# Pull specific service images
podman-compose pull web api

# Push all service images
podman-compose push

# Push only db image
podman-compose push db
```

## images

List images used by created containers.

```bash
podman-compose images [options]
```

### Options

| Option | Description |
|--------|-------------|
| `-q, --quiet` | Show only image IDs |

### Examples

```bash
# List all images
podman-compose images

# Show only image IDs
podman-compose images -q
```

## port

Print the public port for a port binding.

```bash
podman-compose port SERVICE PRIVATE_PORT [OPTIONS]
```

### Examples

```bash
# Get published port for service's port 80
podman-compose port web 80

# Output: 0.0.0.0:8080 (or similar)
```

## kill

Kill running containers with a specific signal.

```bash
podman-compose kill [options] [services...]
```

### Options

| Option | Description |
|--------|-------------|
| `-s, --signal SIGNAL` | Signal to send (default: KILL) |

### Examples

```bash
# Kill all containers
podman-compose kill

# Send SIGTERM to specific service
podman-compose kill -s TERM web

# Send SIGINT to api service
podman-compose kill -s INT api
```

## pause / unpause

Suspend and resume container processes.

```bash
podman-compose pause [services...]
podman-compose unpause [services...]
```

### Examples

```bash
# Pause all services
podman-compose pause

# Pause specific service
podman-compose pause web

# Resume paused services
podman-compose unpause

# Resume specific service
podman-compose unpause api
```

## wait

Wait for running containers to stop.

```bash
podman-compose wait [services...]
```

### Examples

```bash
# Wait for all services to stop
podman-compose wait

# Wait for specific service
podman-compose wait web
```

## version

Show version information.

```bash
podman-compose version [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--short` | Show only version number |

### Examples

```bash
# Show full version info
podman-compose version

# Show version number only
podman-compose version --short
```

## systemd

Generate systemd unit files for the compose stack.

```bash
podman-compose systemd [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--restart POLICY` | Restart policy (no, on-failure, always) |
| `--timeout SECS` | Shutdown timeout |

### Examples

```bash
# Generate systemd unit file
podman-compose systemd > myapp.service

# With custom restart policy
podman-compose systemd --restart=always > myapp.service

# Install as systemd service
podman-compose systemd | sudo tee /etc/systemd/system/myapp.service
sudo systemctl daemon-reload
sudo systemctl enable --now myapp.service
```

## Command Combinations

### Common Workflows

**Full deployment cycle:**
```bash
# Build and start
podman-compose build && podman-compose up -d

# Monitor logs
podman-compose logs -f

# Check status
podman-compose ps

# Stop and cleanup
podman-compose down
```

**Development workflow:**
```bash
# Start services with auto-recreate on code changes
podman-compose up --force-recreate -d

# Run tests in isolated container
podman-compose run --rm api pytest

# Debug specific service
podman-compose exec web bash
```

**Production deployment:**
```bash
# Pull latest images
podman-compose pull

# Build any custom services
podman-compose build

# Rolling restart with health checks
podman-compose stop -t 30
podman-compose up -d

# Verify deployment
podman-compose ps
podman-compose logs --tail 50
```
