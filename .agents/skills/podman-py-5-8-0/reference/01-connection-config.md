# PodmanPy Connection Configuration

This reference covers all connection methods, authentication options, and environment configuration for connecting to Podman services.

## Connection URIs

PodmanPy supports multiple connection schemes via the `base_url` parameter:

### Unix Domain Socket (Default)

```python
from podman import PodmanClient

# Rootless socket (default user location)
client = PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock")

# Alternative rootless path
client = PodmanClient(base_url="unix://~/.local/share/containers/podman/podman.sock")

# Root socket (requires elevated privileges)
client = PodmanClient(base_url="unix:///run/podman/podman.sock")

# Short form (equivalent to unix://)
client = PodmanClient(base_url="/run/user/1000/podman/podman.sock")
```

**Starting the service:**
```bash
# Rootless (background)
podman system service --timeout=0 unix:///run/user/$(id -u)/podman/podman.sock &

# Root (requires sudo)
sudo podman system service --timeout=0 unix:///run/podman/podman.sock &
```

### TCP Connection

```python
from podman import PodmanClient

# Local TCP connection
client = PodmanClient(base_url="tcp://localhost:8888")

# Remote TCP connection
client = PodmanClient(base_url="tcp://podman-server:8888")

# With TLS (requires certificates)
client = PodmanClient(
    base_url="tcp://podman-server:8443",
    # TLS configuration via environment variables (see below)
)
```

**Starting TCP service:**
```bash
# Insecure TCP (development only)
podman system service --timeout=0 tcp:0.0.0.0:8888 &

# With TLS (production)
podman system service --timeout=0 tcp:0.0.0.0:8443 \
    --tls-verify=true \
    --cert-dir=/etc/podman/certs &
```

### SSH Connection

```python
from podman import PodmanClient

# SSH to remote host, then use local socket
client = PodmanClient(
    base_url="ssh://user@remote-host/run/user/1000/podman/podman.sock"
)

# With custom SSH port
client = PodmanClient(
    base_url="ssh://user@remote-host:2222/run/user/1000/podman/podman.sock"
)

# With specific SSH key
client = PodmanClient(
    base_url="ssh://user@remote-host/run/user/1000/podman/podman.sock",
    identity="/home/user/.ssh/id_ed25519"
)

# Secure SSH (verify host keys)
client = PodmanClient(
    base_url="http+ssh://user@remote-host/run/user/1000/podman/podman.sock?secure=True",
    identity="/home/user/.ssh/id_ed25519"
)
```

**SSH URI formats:**
- `ssh://[user@]host[:port]/<socket-path>`
- `http+ssh://[user@]host[:port]/<socket-path>?secure=True`

## Environment Variables

PodmanPy respects Docker-compatible environment variables for configuration:

### Connection Configuration

```python
import os
from podman import PodmanClient

# Set environment variables
os.environ["CONTAINER_HOST"] = "unix:///run/user/1000/podman/podman.sock"
# or use DOCKER_HOST (Docker-compatible)
os.environ["DOCKER_HOST"] = "unix:///run/user/1000/podman/podman.sock"

# Client will auto-detect from environment
client = PodmanClient.from_env()
```

**Supported environment variables:**
- `CONTAINER_HOST` or `DOCKER_HOST`: URL to Podman service
- `CONTAINER_TLS_VERIFY` or `DOCKER_TLS_VERIFY`: Verify TLS certificates ("1" or "true")
- `CONTAINER_CERT_PATH` or `DOCKER_CERT_PATH`: Path to TLS certificates directory

### Using from_env()

```python
from podman import PodmanClient

# Auto-detect from environment
client = PodmanClient.from_env()

# With custom timeout
client = PodmanClient.from_env(timeout=60)

# With custom API version
client = PodmanClient.from_env(version="5.0.0")

# Override environment with custom dict
custom_env = {
    "CONTAINER_HOST": "tcp://localhost:8888",
    "CONTAINER_TLS_VERIFY": "0"
}
client = PodmanClient.from_env(environment=custom_env)
```

## TLS Configuration

### Certificate-Based TLS

```python
import os
from podman import PodmanClient

# Set certificate path
os.environ["CONTAINER_CERT_PATH"] = "/etc/podman/certs"
os.environ["CONTAINER_TLS_VERIFY"] = "1"

# Client will use certificates from cert path
client = PodmanClient.from_env()
```

**Certificate directory structure:**
```
/etc/podman/certs/
├── ca.crt        # CA certificate (for verification)
├── client.crt    # Client certificate
└── client.key    # Client private key
```

### Programmatic TLS Setup

```python
from podman import PodmanClient

# TCP with TLS verification
client = PodmanClient(
    base_url="tcp://localhost:8443",
    # TLS config delegated to environment variables
)

# Note: PodmanPy delegates TLS configuration to environment variables
# for consistency with Docker SDK patterns
```

## SSH Authentication

### Using SSH Keys

```python
from podman import PodmanClient

# Default SSH key locations checked:
# - ~/.ssh/id_ed25519
# - ~/.ssh/id_rsa
# - ~/.ssh/id_dsa

client = PodmanClient(
    base_url="ssh://user@remote-host/run/podman/podman.sock"
)

# Specify custom key
client = PodmanClient(
    base_url="ssh://user@remote-host/run/podman/podman.sock",
    identity="/path/to/custom/key"
)

# With SSH agent (default behavior)
client = PodmanClient(
    base_url="ssh://user@remote-host/run/podman/podman.sock",
    use_ssh_client=True  # Use system ssh client (default)
)
```

### SSH Configuration File

SSH connection options can be configured in `~/.ssh/config`:

```
Host podman-server
    HostName remote.example.com
    User deploy
    IdentityFile ~/.ssh/podman_key
    Port 22
    ForwardAgent yes
```

Then use in PodmanPy:
```python
client = PodmanClient(base_url="ssh://podman-server/run/podman/podman.sock")
```

## Client Configuration Options

### Timeout Settings

```python
from podman import PodmanClient

# Default timeout (uses socket._GLOBAL_DEFAULT_TIMEOUT)
client = PodmanClient()

# Custom timeout in seconds
client = PodmanClient(timeout=120)

# Short timeout for health checks
health_client = PodmanClient(timeout=5)
```

### API Version

```python
from podman import PodmanClient

# Auto-detect API version (default)
client = PodmanClient()

# Specify API version
client = PodmanClient(version="5.0.0")

# Use latest stable API
client = PodmanClient(version="auto")
```

### Connection Pooling

```python
from podman import PodmanClient

# Default pool size
client = PodmanClient()

# Custom pool size for high-concurrency scenarios
client = PodmanClient(max_pool_size=50)

# For batch operations
with PodmanClient(max_pool_size=100) as client:
    # Process many containers/images
    pass
```

### User Agent

```python
from podman import PodmanClient

# Custom user agent for identification
client = PodmanClient(
    user_agent="MyApp/1.0.0 (myapp@example.com)"
)

# Default: PodmanPy/<version>
```

## Connection Management

### Context Manager (Recommended)

```python
from podman import PodmanClient

# Automatic resource cleanup
with PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock") as client:
    # All operations here
    containers = client.containers.list()
    
# Client automatically closed here, connections released
```

### Manual Connection Management

```python
from podman import PodmanClient

client = PodmanClient()

try:
    # Perform operations
    image = client.images.pull("alpine:latest")
finally:
    client.close()  # Always close when done
```

### Health Check

```python
from podman import PodmanClient

def is_podman_available(base_url=None):
    """Check if Podman service is accessible."""
    client = PodmanClient(base_url=base_url)
    try:
        return client.ping()
    except Exception:
        return False
    finally:
        client.close()

# Usage
if is_podman_available():
    print("Podman service is running")
else:
    print("Start Podman service: podman system service --timeout=0")
```

## Connection Examples by Use Case

### Development (Local Rootless)

```python
from podman import PodmanClient

# Default rootless connection
client = PodmanClient()

# Or explicit path
client = PodmanClient(base_url="unix://~/.local/share/containers/podman/podman.sock")
```

### CI/CD Pipeline

```python
from podman import PodmanClient
import os

# Use environment variable for flexibility
client = PodmanClient(
    base_url=os.environ.get("CONTAINER_HOST", "unix:///run/podman/podman.sock"),
    timeout=300  # Longer timeout for CI
)
```

### Multi-Host Deployment

```python
from podman import PodmanClient

def get_client_for_host(host_config):
    """Get client configured for specific host."""
    if host_config["type"] == "local":
        return PodmanClient(base_url=host_config["socket_path"])
    elif host_config["type"] == "remote_tcp":
        return PodmanClient(
            base_url=f"tcp://{host_config['host']}:{host_config['port']}",
            timeout=60
        )
    elif host_config["type"] == "ssh":
        return PodmanClient(
            base_url=f"ssh://{host_config['user']}@{host_config['host']}{host_config['socket_path']}",
            identity=host_config.get("ssh_key"),
            timeout=60
        )

# Usage
hosts = [
    {"type": "local", "socket_path": "/run/podman/podman.sock"},
    {"type": "ssh", "user": "deploy", "host": "server1", "socket_path": "/run/podman/podman.sock"},
    {"type": "remote_tcp", "host": "podman-cluster", "port": 8443}
]

for host in hosts:
    client = get_client_for_host(host)
    print(f"Connected to {host}: {client.ping()}")
```

### Remote Registry Authentication

```python
from podman import PodmanClient

client = PodmanClient()

# Login to registry
client.login(
    username="myuser",
    password="mypassword",
    registry="quay.io"
)

# Pull private image
image = client.images.pull("quay.io/myorg/private-image")

# Or use auth_config per operation
image = client.images.pull(
    "quay.io/myorg/private-image",
    auth_config={"username": "myuser", "password": "mypassword"}
)
```

## Troubleshooting Connections

### Connection Refused

```python
from podman import PodmanClient
from podman.errors import APIError

try:
    client = PodmanClient(base_url="unix:///run/user/1000/podman/podman.sock")
    client.ping()
except APIError as e:
    print(f"Connection failed: {e}")
    print("Start service: podman system service --timeout=0 unix:///run/user/1000/podman/podman.sock &")
```

### Verify Socket Path

```python
import os
from pathlib import Path

def get_rootless_socket():
    """Get correct rootless socket path for current user."""
    uid = os.getuid()
    
    # Check common locations
    paths = [
        f"/run/user/{uid}/podman/podman.sock",
        Path.home() / ".local/share/containers/podman/podman.sock",
        f"/run/rootlessport/podman-{uid}.sock"
    ]
    
    for path in paths:
        if Path(path).exists():
            return f"unix://{path}"
    
    raise FileNotFoundError("No Podman socket found. Start service first.")

client = PodmanClient(base_url=get_rootless_socket())
```

### Debug Connection Issues

```python
import logging
from podman import PodmanClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("podman").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

client = PodmanClient()
# All connection details will be logged
```
