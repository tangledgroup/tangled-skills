# Configuration and Events

## PodmanConfig

Read connection configuration from `containers.conf` in XDG_CONFIG_HOME.

```python
from podman.domain.config import PodmanConfig

config = PodmanConfig()
print(config.id)  # Path to containers.conf

# List configured services
for name, service in config.services.items():
    print(name, service.url.geturl())
    print("  Identity:", service.identity)

# Active service
active = config.active_service
if active:
    print("Active:", active.id, active.url.geturl())
```

### ServiceConnection Properties

- `id` (str): Connection identifier
- `url` (ParseResult): URL for the service connection
- `identity` (Path): Path to SSH identity file

## PodmanClient.from_env()

Create client from environment variables:

```python
from podman import PodmanClient

# Reads CONTAINER_HOST or DOCKER_HOST
client = PodmanClient.from_env()
```

Environment variables:
- `CONTAINER_HOST` / `DOCKER_HOST`: URL to Podman service
- `CONTAINER_TLS_VERIFY` / `DOCKER_TLS_VERIFY`: Verify host against CA
- `CONTAINER_CERT_PATH` / `DOCKER_CERT_PATH`: Path to TLS certificates

Parameters:
- `version` (str): API version, default `"auto"`
- `timeout` (int | None): Timeout in seconds
- `max_pool_size` (int | None): Connection pool size
- `environment` (dict[str, str]): Override os.environ
- `credstore_env` (dict[str, str]): Environment for credential store

## System Information

### Ping

```python
if client.ping():
    print("Podman service is available")
```

### Version

```python
version_info = client.version()
print(version_info["Version"])       # Podman version
print(version_info["ApiVersion"])    # API version

# Include API version property
version_info = client.version(api_version=True)
```

### Info

```python
info = client.info()
# Returns comprehensive dict with:
# - Hostname, KernelVersion, OSVersion
# - CPUs, Memory, SwapTotal
# - Running/Paused/Stopped/Containers count
# - Images count
# - Storage driver info
# - Security options
# etc.
```

### Disk Usage

```python
usage = client.df()
# Returns dict keyed by resource categories:
# - Containers: space used by containers
# - Images: space used by images
# - Volumes: space used by volumes
# - BuildCache: builder cache size
```

### Registry Login

```python
result = client.login(
    username="myuser",
    password="secret",
    registry="https://quay.io/v2",
)
```

Parameters:
- `username` (str): Registry username
- `password` (str): Plaintext password
- `email` (str | None): Account email
- `registry` (str | None): Registry URL, e.g. `"https://quay.io/v2"`
- `identitytoken` (str | None): OAuth identity token
- `registrytoken` (str | None): Bearer token
- `tls_verify` (bool | str | None): TLS verification

## Events

Stream Podman service events:

```python
# Stream all events
for event in client.events():
    print(event)

# Filtered and decoded events
for event in client.events(
    filters={"type": "container", "event": "start"},
    decode=True,
):
    print(event["from"], event["status"])

# Time-bounded events
for event in client.events(
    since="2024-01-01T00:00:00Z",
    until="2024-01-31T23:59:59Z",
    decode=True,
):
    print(event)
```

Parameters:
- `since` (datetime | int | None): Events newer than this time
- `until` (datetime | int | None): Events older than this time
- `filters` (dict[str, Any] | None): Event filter criteria
- `decode` (bool): Return dicts instead of raw strings, default False

Returns `Iterator[str]` when decode=False, `Iterator[dict[str, Any]]` when decode=True.
