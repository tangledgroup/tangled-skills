# Error Handling

## Contents
- Exception Hierarchy
- APIError
- BuildError
- ContainerError
- NotFound and ImageNotFound
- InvalidArgument
- Best Practices

## Exception Hierarchy

```
DockerException (docker-py)
└── PodmanError (base)
    ├── BuildError        — Error during image build
    ├── ContainerError    — Container exited with non-zero code
    ├── InvalidArgument   — Invalid argument to API call
    └── StreamParseError  — Error parsing streamed response

HTTPError (stdlib)
└── APIError              — Wraps HTTP errors from Podman service
    ├── NotFound          — Resource not found on service
    └── ImageNotFound     — Image not found on service
```

## APIError

The primary exception for service-reported errors. Wraps HTTP responses with helper methods:

```python
from podman import PodmanClient
from podman.errors import APIError

try:
    with PodmanClient() as client:
        container = client.containers.get("nonexistent")
except APIError as e:
    print(e.status_code)   # HTTP status code
    print(e.is_error())     # True for any error (4xx or 5xx)
    print(e.is_client_error())  # True for 4xx
    print(e.is_server_error())  # True for 5xx
```

Properties:
- `status_code` (int | None): HTTP status code from response
- `response`: Original HTTP Response object

## BuildError

Raised when image build fails. Includes build log output:

```python
from podman.errors import BuildError

try:
    image, logs = client.images.build(path="./broken-dockerfile")
except BuildError as e:
    print(f"Build failed: {e.reason}")
    for line in e.build_log:
        print(line)
```

Properties:
- `reason` (str): Error description
- `build_log` (Iterable[str]): Build log output

## ContainerError

Raised when a container exits with non-zero code during `run()`:

```python
from podman.errors import ContainerError

try:
    client.containers.run("alpine", ["sh", "-c", "exit 1"])
except ContainerError as e:
    print(f"Container {e.container.name} exited with code {e.exit_status}")
    print(f"Command: {e.command}")
    print(f"Image: {e.image}")
```

Properties:
- `container` (Container): Container that reported error
- `exit_status` (int): Non-zero exit code
- `command` (str | list[str]): Command passed to container
- `image` (str): Image name used
- `stderr` (Iterable[str] | None): Error output

## NotFound

Raised when a resource does not exist. Inherits from `APIError`:

```python
from podman.errors import NotFound

try:
    container = client.containers.get("does-not-exist")
except NotFound:
    print("Container not found")
```

## ImageNotFound

Specialized for image operations. Inherits from `APIError`:

```python
from podman.errors import ImageNotFound

try:
    image = client.images.get("nonexistent-image")
except ImageNotFound:
    print("Image not found on Podman service")
```

## InvalidArgument

Raised for invalid API arguments:

```python
from podman.errors import InvalidArgument

try:
    # Example: invalid tag name in image.save()
    image.save(named="invalid/tag/name!")
except InvalidArgument as e:
    print(f"Invalid argument: {e}")
```

## Best Practices

### Catching specific errors

```python
from podman.errors import APIError, NotFound, BuildError, ContainerError

try:
    with PodmanClient() as client:
        container = client.containers.get("my-container")
        container.start()
except NotFound:
    print("Container does not exist")
except APIError as e:
    if e.is_client_error():
        print(f"Client error ({e.status_code}): {e}")
    elif e.is_server_error():
        print(f"Server error ({e.status_code}): {e}")
```

### Handling build failures

```python
try:
    image, logs = client.images.build(path=".", tag="app:latest")
    print(f"Built: {image.id}")
except BuildError as e:
    print(f"Build failed: {e.reason}")
    # Inspect build log for details
    for line in e.build_log:
        print(line)
```

### Handling container run failures

```python
try:
    client.containers.run(
        "my-app:latest",
        ["./run.sh"],
        remove=True,
    )
except ContainerError as e:
    print(f"Exit code {e.exit_status} from container {e.container.name}")
```
