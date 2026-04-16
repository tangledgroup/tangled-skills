# Dockerfile Reference

## Overview

A Dockerfile is a text document containing all commands a user could call on the command line to assemble an image. Docker builds images automatically by reading instructions from a Dockerfile.

**Source:** https://docs.docker.com/engine/reference/builder/

## Format

```dockerfile
# Comment
INSTRUCTION arguments
```

- Instructions are **not case-sensitive** but convention is UPPERCASE
- A Dockerfile **must begin with a `FROM` instruction** (after parser directives, comments, and ARGs)
- BuildKit treats lines beginning with `#` as comments (unless they're parser directives)
- Comments don't support line continuation characters

## Parser Directives

Parser directives are optional and affect how subsequent lines are handled. They must be at the top of the Dockerfile.

| Directive | Description |
|-----------|-------------|
| `# syntax=docker/dockerfile:1` | Specifies the Dockerfile syntax version (enables BuildKit features) |
| `# escape=\` | Sets the escape character (Windows default is `%`, Linux default is `\`) |
| `# check=skip=<check-name>` | Skips a specific build check |

```dockerfile
# syntax=docker/dockerfile:1

FROM ubuntu:24.04
RUN echo "hello"
```

## Instructions Reference

### FROM

Creates a new build stage from a base image.

```dockerfile
FROM <image>[:<tag>|@<digest>] [AS <name>]
```

- `<tag>` is optional; defaults to `latest`
- `<digest>` pins the image by content hash (immutable)
- `AS <name>` names the stage for reference in subsequent stages

```dockerfile
FROM golang:1.23 AS builder
FROM scratch AS final
COPY --from=builder /app /app
```

### RUN

Executes commands in a new layer on top of the current image and commits the result.

**Shell form:**
```dockerfile
RUN <command>
```

**Exec form (recommended):**
```dockerfile
RUN ["executable", "param1", "param2"]
```

- Shell form uses `/bin/sh -c` on Linux, `cmd /S /C` on Windows
- Exec form bypasses the shell (no variable expansion in shell form)
- Multiple RUN commands create multiple layers; chain with `&&` to reduce layers

```dockerfile
# Bad: creates 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# Good: creates 1 layer, cleans up in same layer
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

### CMD

Specifies the default command to run when starting a container.

```dockerfile
CMD ["executable", "param1", "param2"]   # Exec form (recommended)
CMD command param1 param2                  # Shell form
CMD ["param1", "param2"]                   # Default exec form for ENTRYPOINT
```

- Only the **last CMD** takes effect if multiple are specified
- CMD can be overridden at `docker run` time
- If ENTRYPOINT is not set, CMD is the default command

### ENTRYPOINT

Configures a container to run as an executable.

```dockerfile
ENTRYPOINT ["executable", "param1"]
ENTRYPOINT command param1                  # Shell form
```

- Unlike CMD, ENTRYPOINT is **not easily overridden** at runtime
- Arguments from CMD are appended to ENTRYPOINT (unless CMD uses exec form)
- Use `docker run --entrypoint` to override entirely

### ENV

Sets environment variables.

```dockerfile
ENV <key>=<value> ...
ENV <key> <value>
```

```dockerfile
ENV APP_HOME /app
ENV JAVA_HOME=/opt/java NODE_HOME=/opt/node
WORKDIR $APP_HOME
```

- Environment variables persist in the container and can be overridden with `-e` flag
- ENV is preferred over ARG for runtime values; use ARG for build-time-only values

### ARG

Defines build-time variables.

```dockerfile
ARG <name>[=<default-value>]
```

```dockerfile
ARG VERSION=1.0
ARG BUILD_DATE
RUN echo "Building version $VERSION"
```

- ARG values are **not available at runtime** (unlike ENV)
- Default values can be specified with `=`
- Values can be passed at build time: `docker build --build-arg VERSION=2.0 .`
- ARG must come before FROM to be available in the FROM line

### COPY

Copies files from the build context into the image.

```dockerfile
COPY [--chown=<user>:<group>] <src>... <dest>
COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
```

- `<src>` paths are relative to the build context
- Multiple sources require `<dest>` to be a directory
- Supports JSON array syntax for paths with special characters

```dockerfile
COPY requirements.txt /app/
COPY --chown=appuser:appuser src/ /app/src/
```

### ADD

Like COPY, but with additional features.

```dockerfile
ADD [--chown=<user>:<group>] <src>... <dest>
```

**Additional features vs COPY:**
- Automatically extracts tar archives
- Supports URLs as source (downloads via wget/curl)
- Supports glob patterns in `<src>`

> **Recommendation:** Use `COPY` unless you need ADD's special features.

### WORKDIR

Sets the working directory for subsequent instructions.

```dockerfile
WORKDIR /path/to/workdir
```

- Can be absolute or relative to previous WORKDIR
- Applied to RUN, CMD, ENTRYPOINT, COPY, ADD instructions
- Can be used multiple times; only the last value before each instruction matters

### VOLUME

Creates a mount point marked as external persistent data.

```dockerfile
VOLUME ["/data"]
```

- Creates a volume that can be managed outside the container's filesystem
- Data in volumes persists after container removal
- Multiple containers can share the same volume

### EXPOSE

Documents which port the container listens on at runtime.

```dockerfile
EXPOSE <port> [<port>/<protocol>...]
```

- Does **not** actually publish the port; use `-p` or `-P` with `docker run`
- Default protocol is TCP; can specify UDP: `EXPOSE 53/udp`

```dockerfile
EXPOSE 80/tcp 443/tcp 53 53/udp
```

### USER

Sets the user for RUN, CMD, and ENTRYPOINT.

```dockerfile
USER <user>[:<group>]
USER <UID>[:<GID>]
```

- Default is `root` (UID 0)
- Use numeric IDs for portability across images

```dockerfile
RUN useradd -r appuser
USER appuser
```

### LABEL

Adds metadata to the image.

```dockerfile
LABEL <key>=<value> ...
LABEL maintainer="name@example.com" version="1.0" description="My app"
```

- Multiple key-value pairs can be specified on one line
- Use `docker inspect` to view labels

### HEALTHCHECK

Configure a health check command for the container.

```dockerfile
HEALTHCHECK [OPTIONS] CMD <command>
HEALTHCHECK NONE  # Disable healthcheck from base image
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--interval=30s` | 30s | Time between checks |
| `--timeout=30s` | 30s | Time before check is considered failed |
| `--start-period=5s` | 0s | Initialization time for the container |
| `--retries=3` | 3 | Consecutive failures before unhealthy |

```dockerfile
HEALTHCHECK --interval=10s --timeout=3s CMD curl -f http://localhost/ || exit 1
```

### STOPSIGNAL

Sets the system call signal to exit the container.

```dockerfile
STOPSIGNAL SIGTERM
STOPSIGNAL 15
```

- Default is `SIGTERM` (15)
- Use for containers that need a specific shutdown signal

### SHELL

Sets the default shell for shell-form instructions.

```dockerfile
SHELL ["executable", "parameters"]
SHELL command parameters
```

```dockerfile
# Use PowerShell on Windows
SHELL ["powershell", "-command"]

# Use bash on Linux
SHELL ["/bin/bash", "-c"]
```

### ONBUILD

Adds a trigger instruction that executes when the image is used as a base for another build.

```dockerfile
ONBUILD RUN npm install
```

- The ONBUILD instruction **does not** execute during the current build
- It triggers when another Dockerfile uses `FROM <this-image>`
- Can be disabled with `--no-cache` or overridden in child image

### STAGE (implicit)

Each `FROM` starts a new stage. Named stages can be referenced:

```dockerfile
FROM golang:1.23 AS build-stage
RUN go build -o /app

FROM alpine:3.20 AS production
COPY --from=build-stage /app /app
CMD ["/app"]
```

## Dockerfile Best Practices

### Layer Caching Strategy

Order instructions from **least to most frequently changing**:

```dockerfile
# 1. Base image (rarely changes)
FROM python:3.13-slim

# 2. System dependencies (changes occasionally)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 3. Working directory
WORKDIR /app

# 4. Copy dependency files only (these change less often than source)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code (changes frequently)
COPY . .

# 6. Environment and metadata
ENV APP_ENV=production
EXPOSE 8080

# 7. Runtime user
RUN useradd -r appuser
USER appuser

# 8. Default command
CMD ["python", "app.py"]
```

### Using .dockerignore

Create a `.dockerignore` file to exclude unnecessary files from the build context:

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
.env
venv/
.venv/
node_modules
*.md
.dockerignore
Dockerfile
compose.yaml
```

### Multi-Stage Build Patterns

**Pattern 1: Compile and ship binary**
```dockerfile
FROM golang:1.23 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -a -installsuffix cgo -o /app .

FROM alpine:3.20
COPY --from=builder /app /app
CMD ["/app"]
```

**Pattern 2: Build frontend, serve with nginx**
```dockerfile
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

**Pattern 3: Dev vs Production**
```dockerfile
FROM python:3.13 AS base
WORKDIR /app

FROM base AS dev
RUN pip install pytest black flake8
COPY . .

FROM base AS production
COPY --from=dev /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=dev /app/src ./src
USER appuser
CMD ["python", "src/app.py"]
```

### ARG vs ENV Decision Guide

| Use Case | Instruction |
|----------|-------------|
| Build-time version pinning | `ARG` |
| Runtime configuration | `ENV` |
| Registry mirror URL (build) | `ARG` |
| Database connection string (runtime) | `ENV` or secret mount |
| API key (build time only) | `ARG` with `--secret` |
| Feature flag (runtime) | `ENV` |
