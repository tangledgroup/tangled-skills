# Dockerfile Reference

## Format

A Dockerfile is a text document containing all commands to assemble an image. It follows a specific format with parser directives at the top, followed by instructions.

### Parser Directives

Parser directives must appear before any comment, whitespace, or instruction:

- `# syntax=docker/dockerfile:1` — Selects the Dockerfile frontend (BuildKit). Use `docker/dockerfile:1` for latest version 1 syntax.
- `# escape=\` — Sets the escape character (backslash on Linux, backtick on Windows)
- `# check=...` — Configures build-time checks

### Environment Replacement

Variable expansion with `${VAR}` or `$VAR` is supported in:
- `ADD`, `COPY`, `ENV`, `EXPOSE`, `FROM`, `LABEL`, `STOPSIGNAL`, `USER`, `VOLUME`, `WORKDIR`, `ARG`, `ONBUILD`

Not supported in:
- `CMD`, `ENTRYPOINT`, `HEALTHCHECK`, `MAINTAINER`, `RUN`, `SHELL`

### .dockerignore

Use `.dockerignore` to exclude files from the build context. Patterns follow `.gitignore` syntax. This reduces build context size and improves build performance.

## Shell and Exec Form

Many instructions support two forms:

**Exec form** (preferred, uses JSON array):
```dockerfile
CMD ["executable", "param1", "param2"]
```

**Shell form**:
```dockerfile
RUN apt-get update && apt-get install -y python3
```

The exec form bypasses shell processing and is required for proper signal handling.

## Instructions

### FROM

Sets the base image. Must be the first instruction (except parser directives).

```dockerfile
FROM <image>[:<tag>|@<digest>] [AS <name>]
FROM <image> [--platform=<platform>] [:<tag>|@<digest>] [AS <name>]
```

- `AS <name>` names a build stage for multi-stage builds
- `--platform` specifies target platform (BuildKit only)
- `scratch` is a special empty base image

**Multi-stage build example:**
```dockerfile
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o /myapp

FROM alpine:3.19
COPY --from=builder /myapp /usr/local/bin/
CMD ["/myapp"]
```

**ARG and FROM interaction:**
```dockerfile
ARG VERSION=latest
FROM ubuntu:${VERSION}
```

The ARG must be declared before the FROM to be used in it.

### RUN

Executes commands in a new layer and commits the result.

```dockerfile
RUN <command>
RUN ["executable", "param1", "param2"]
```

**Best practices:**
- Chain commands with `&&` to reduce layers
- Clean up apt cache in same RUN: `apt-get clean && rm -rf /var/lib/apt/lists/*`
- Use `--mount` for BuildKit features (see below)

**RUN --mount (BuildKit only):**

```dockerfile
# Bind mount
RUN --mount=type=bind,source=./file,target=/file cat /file

# Cache mount (persists across builds)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install numpy

# tmpfs mount
RUN --mount=type=tmpfs,target=/tmp \
    some-command

# Secret mount (not persisted in image)
RUN --mount=type=secret,id=my_secret,dst=/run/secrets/my_secret \
    cat /run/secrets/my_secret

# SSH mount
RUN --mount=type=ssh \
    git clone git@github.com:user/private-repo.git
```

**RUN --network:**
```dockerfile
RUN --network=host apt-get update  # Access host network during build
RUN --network=none some-command     # No network access
```

**RUN --security:**
```dockerfile
RUN --security=sandbox some-command
```

### CMD

Sets default command and/or arguments for running the container. Only the last CMD takes effect. Overridden by `docker run` arguments.

```dockerfile
CMD ["executable", "param1", "param2"]  # exec form (preferred)
CMD command param1 param2                # shell form
```

### LABEL

Adds metadata as key-value pairs:
```dockerfile
LABEL version="1.0" description="A web application"
```

### EXPOSE

Documents which ports the container listens on (does not publish them):
```dockerfile
EXPOSE 80
EXPOSE 443/tcp 8080/tcp 8443
```

### ENV

Sets environment variables available in subsequent instructions and at runtime:
```dockerfile
ENV MY_VAR=value
ENV MY_VAR=value ANOTHER_VAR=other
ENV MY_VAR          # Declares variable (unset value)
```

### ADD

Copies files, directories, or remote URLs into the image. Supports automatic tar extraction and URL downloads.

```dockerfile
ADD <src> ... <dest>
ADD ["<src>", ... "<dest>"]
```

**Flags:**
- `--chmod=<perms>` — Set file permissions (octal or symbolic)
- `--chown=<user>:<group>` — Set ownership
- `--link` — Enhanced caching semantics
- `--checksum=<hash>` — Verify remote source checksum
- `--keep-git-dir` — Preserve .git directory from Git contexts
- `--unpack=<bool>` — Control tar extraction (default: true for local, false for remote)
- `--exclude=<pattern>` — Exclude files matching pattern

**Best practice:** Prefer `COPY` over `ADD` unless you need URL fetching or automatic tar extraction.

### COPY

Copies files or directories from the build context into the image.

```dockerfile
COPY <src> ... <dest>
COPY ["<src>", ... "<dest>"]
```

**Flags:**
- `--from=<name>` — Copy from another build stage, named context, or image
- `--chmod=<perms>` — Set file permissions
- `--chown=<user>:<group>` — Set ownership
- `--link` — Enhanced caching semantics
- `--parents` — Preserve parent directory structure
- `--exclude=<pattern>` — Exclude files matching pattern

**Copy from another stage:**
```dockerfile
COPY --from=builder /app/bin/ /usr/local/bin/
```

**Copy from an image:**
```dockerfile
COPY --from=nginx:latest /etc/nginx/nginx.conf /nginx.conf
```

### ENTRYPOINT

Configures the container to run as an executable. Command-line arguments to `docker run` are appended.

```dockerfile
ENTRYPOINT ["executable", "param1", "param2"]  # exec form (preferred)
ENTRYPOINT command param1 param2                # shell form
```

**CMD and ENTRYPOINT interaction:**

| | No ENTRYPOINT | ENTRYPOINT exec_entry p1_entry |
|---|---|---|
| No CMD | error | `/bin/sh -c exec_entry p1_entry` |
| CMD ["exec_cmd", "p1_cmd"] | `exec_cmd p1_cmd` | `exec_entry p1_entry exec_cmd p1_cmd` |
| CMD exec_cmd p1_cmd | `/bin/sh -c exec_cmd p1_cmd` | `exec_entry p1_entry /bin/sh -c exec_cmd p1_cmd` |

### VOLUME

Creates a mount point for externally mounted volumes:
```dockerfile
VOLUME ["/data"]
VOLUME /var/log /var/db
```

### USER

Sets user (and optionally group) for subsequent instructions and runtime:
```dockerfile
USER docker
USER postgres:postgres
USER 1000:1000
```

### WORKDIR

Sets the working directory for subsequent instructions:
```dockerfile
WORKDIR /app
WORKDIR subdir    # Relative to previous WORKDIR
WORKDIR $HOME/app # ENV variable expansion
```

Creates directories if they don't exist.

### ARG

Defines build-time variables (not persisted in image):
```dockerfile
ARG VERSION=1.0
ARG USERNAME
```

Passed at build time: `docker build --build-arg VERSION=2.0 .`

**Predefined ARGs:** `HTTP_PROXY`, `http_proxy`, `HTTPS_PROXY`, `https_proxy`, `FTP_PROXY`, `ftp_proxy`, `NO_PROXY`, `no_proxy`, `ALL_PROXY`, `all_proxy`

**BuildKit automatic platform ARGs:**
- `TARGETPLATFORM`, `TARGETOS`, `TARGETARCH`, `TARGETVARIANT`
- `BUILDPLATFORM`, `BUILDOS`, `BUILDARCH`, `BUILDVARIANT`

**BuildKit built-in build args:**
- `BUILDKIT_BUILD_NAME`, `BUILDKIT_INLINE_CACHE`, `BUILDKIT_MULTI_PLATFORM`
- `BUILDKIT_CONTEXT_KEEP_GIT_DIR`, `SOURCE_DATE_EPOCH`

### ONBUILD

Registers triggers to execute when the image is used as a base:
```dockerfile
ONBUILD ADD . /app/src
ONBUILD RUN /usr/local/bin/python-build --dir /app/src
```

### STOPSIGNAL

Sets the system call signal for container exit (default: `SIGTERM`):
```dockerfile
STOPSIGNAL SIGINT
```

### HEALTHCHECK

Configures container health monitoring:
```dockerfile
HEALTHCHECK --interval=5m --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

HEALTHCHECK NONE  # Disable inherited healthcheck
```

Options: `--interval`, `--timeout`, `--start-period`, `--start-interval` (Docker 25.0+), `--retries`

Exit codes: `0` = healthy, `1` = unhealthy, `2` = reserved

### SHELL

Overrides the default shell for shell-form commands:
```dockerfile
SHELL ["/bin/bash", "-c"]
SHELL ["powershell", "-command"]  # Windows
```

Default on Linux: `["/bin/sh", "-c"]`
Default on Windows: `["cmd", "/S", "/C"]`

## Here-Documents

Here-documents allow multi-line input for `RUN` and `COPY`:

```dockerfile
# Multi-line script
RUN <<EOT bash
  set -ex
  apt-get update
  apt-get install -y vim
EOT

# Inline file creation with COPY
COPY <<EOF /etc/config.txt
hello world
EOF

# Variable expansion (unquoted delimiter)
ARG FOO=bar
COPY <<-EOT /script.sh
  echo "hello ${FOO}"
EOT

# No variable expansion (quoted delimiter)
COPY <<-"EOT" /script.sh
  echo "hello ${FOO}"
EOT
```

## MAINTAINER (deprecated)

Use `LABEL` instead:
```dockerfile
LABEL maintainer="user@example.com"
```
