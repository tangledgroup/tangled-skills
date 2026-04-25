# Error Handling Reference

Complete guide to exception types, error codes, retry patterns, and troubleshooting common issues.

## Exception Types

PodmanPy raises specific exceptions for different error conditions. Understanding these helps build robust applications.

### Base Exceptions

```python
from podman.errors import PodmanError

# All PodmanPy exceptions inherit from PodmanError
try:
    # Some operation
    pass
except PodmanError as e:
    print(f"Podman error: {e}")
```

### API Error (Most Common)

```python
from podman.errors import APIError

try:
    container = client.containers.get("nonexistent")
except APIError as e:
    # Access HTTP status code
    print(f"Status code: {e.response.status_code}")
    
    # Access error explanation
    print(f"Explanation: {e.explanation}")
    
    # Access full response
    print(f"Response: {e.response.text}")
    
    # Handle specific status codes
    if e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 409:
        print("Conflict - resource exists or in use")
    elif e.response.status_code == 500:
        print("Internal server error")
```

### Image Not Found

```python
from podman.errors import ImageNotFound

try:
    image = client.images.get("nonexistent-image")
except ImageNotFound as e:
    print(f"Image not found: {e}")
    
    # Pull the image if not present
    print("Pulling image...")
    image = client.images.pull("nonexistent-image")
```

### Container Error

```python
from podman.errors import ContainerError

try:
    result = container.exec_run(["false"])  # Command that exits with error
    if result.exit_code != 0:
        raise ContainerError(
            command=["false"],
            exit_status=result.exit_code,
            output=result.output
        )
except ContainerError as e:
    print(f"Command failed with exit code: {e.exit_status}")
    print(f"Output: {e.stdout}")
```

### Build Error

```python
from podman.errors import BuildError

try:
    image, logs = client.images.build(path="./broken-dockerfile")
except BuildError as e:
    print(f"Build failed: {e}")
    
    # Access build log for details
    for line in e.build_log:
        print(line.decode())
    
    # Check cause if available
    if hasattr(e, 'cause'):
        print(f"Cause: {e.cause}")
```

### Connection Errors

```python
from podman.errors import PodmanError
import requests.exceptions

try:
    client = PodmanClient(base_url="unix:///nonexistent/socket")
    client.ping()
except (PodmanError, requests.exceptions.ConnectionError) as e:
    print(f"Connection failed: {e}")
    print("Check if Podman service is running")
```

## Error Codes and Meanings

### HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Missing or invalid registry credentials |
| 403 | Forbidden | Permission denied (SELinux, capabilities) |
| 404 | Not Found | Container/image/network/volume doesn't exist |
| 409 | Conflict | Resource already exists or in use |
| 500 | Internal Error | Podman service error |
| 502 | Bad Gateway | Service not responding properly |

### Handling by Status Code

```python
from podman.errors import APIError

def handle_api_error(e):
    """Handle API errors based on status code."""
    code = e.response.status_code
    
    if code == 400:
        return f"Invalid request: {e.explanation}"
    elif code == 401:
        return "Authentication required. Login to registry first."
    elif code == 403:
        return f"Permission denied: {e.explanation}"
    elif code == 404:
        return "Resource not found"
    elif code == 409:
        return f"Conflict: {e.explanation}"
    elif code >= 500:
        return f"Server error ({code}): {e.explanation}"
    else:
        return f"Unknown error ({code}): {e.explanation}"

try:
    # Some operation
    pass
except APIError as e:
    print(handle_api_error(e))
```

## Retry Patterns

### Simple Retry with Backoff

```python
import time
from podman.errors import APIError, PodmanError

def retry_with_backoff(func, max_attempts=5, base_delay=1.0):
    """Retry function with exponential backoff."""
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except (APIError, PodmanError) as e:
            last_exception = e
            
            # Don't retry on certain errors
            if e.response and e.response.status_code in [400, 401, 403, 404]:
                raise
            
            # Calculate delay with exponential backoff
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed. Retrying in {delay}s...")
            time.sleep(delay)
    
    # All attempts failed
    raise last_exception

# Usage
def get_container():
    return client.containers.get("my-container")

container = retry_with_backoff(get_container, max_attempts=5)
```

### Retry with Jitter

```python
import time
import random
from podman.errors import APIError

def retry_with_jitter(func, max_attempts=5, base_delay=1.0, max_jitter=0.5):
    """Retry with exponential backoff and jitter to prevent thundering herd."""
    for attempt in range(max_attempts):
        try:
            return func()
        except APIError as e:
            if e.response and e.response.status_code < 500:
                raise
            
            # Add jitter to delay
            delay = base_delay * (2 ** attempt) + random.uniform(0, max_jitter)
            print(f"Retry {attempt + 1}/{max_attempts} in {delay:.2f}s")
            time.sleep(delay)
    
    raise RuntimeError(f"Failed after {max_attempts} attempts")

# Usage
image = retry_with_jitter(lambda: client.images.pull("alpine:latest"))
```

### Retry for Specific Status Codes

```python
from podman.errors import APIError
import time

def retry_on_5xx(func, max_retries=3):
    """Retry only on 5xx server errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            # Retry only on server errors (5xx)
            if not (e.response and 500 <= e.response.status_code < 600):
                raise
            
            wait_time = (attempt + 1) * 2
            print(f"Server error {e.response.status_code}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    raise RuntimeError("Max retries exceeded")

# Usage
result = retry_on_5xx(lambda: client.containers.run("alpine", ["echo", "test"]))
```

### Circuit Breaker Pattern

```python
from podman.errors import APIError, PodmanError
from collections import defaultdict
import time

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = defaultdict(int)
        self.last_failure_time = {}
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        current_time = time.time()
        
        # Check if circuit should close
        if self.state == "open":
            if current_time - self.last_failure_time.get(func, 0) > self.recovery_timeout:
                print("Circuit breaker transitioning to half-open")
                self.state = "half-open"
            else:
                raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failures
            self.failures[func] = 0
            if self.state == "half-open":
                self.state = "closed"
                print("Circuit breaker closed")
            
            return result
            
        except (APIError, PodmanError) as e:
            self.failures[func] += 1
            self.last_failure_time[func] = current_time
            
            if self.failures[func] >= self.failure_threshold:
                self.state = "open"
                print("Circuit breaker opened")
            
            raise

class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

def pull_image():
    return client.images.pull("alpine:latest")

try:
    image = circuit_breaker.call(pull_image)
except CircuitOpenError:
    print("Service unavailable - circuit breaker open")
except APIError as e:
    print(f"Pull failed: {e}")
```

## Context Manager for Resource Cleanup

### Safe Client Usage

```python
from podman import PodmanClient
from podman.errors import PodmanError

def safe_client_operation(operation_func):
    """Execute operation with proper client cleanup."""
    client = None
    try:
        client = PodmanClient()
        return operation_func(client)
    except PodmanError as e:
        print(f"Operation failed: {e}")
        raise
    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass  # Ignore cleanup errors

# Usage
def list_containers(client):
    return client.containers.list(all=True)

containers = safe_client_operation(list_containers)
```

### Container Lifecycle Management

```python
from contextlib import contextmanager

@contextmanager
def temporary_container(image, **kwargs):
    """Create container that's automatically cleaned up."""
    client = PodmanClient()
    container = None
    
    try:
        container = client.containers.run(image, detach=True, **kwargs)
        yield container
        
        # Container yielded - user does work here
        
    except Exception:
        # Re-raise after cleanup
        raise
    finally:
        if container:
            try:
                container.stop(timeout=5)
                container.remove(force=True)
            except Exception as e:
                print(f"Warning: Failed to cleanup container: {e}")
        finally:
            client.close()

# Usage
with temporary_container("alpine", command=["sleep", "30"]) as container:
    # Do work with container
    result = container.exec_run(["echo", "hello"])
    print(result.output.decode())

# Container automatically stopped and removed here
```

## Validation and Pre-flight Checks

### Check Resource Exists

```python
def check_container_exists(client, name_or_id):
    """Check if container exists."""
    try:
        client.containers.get(name_or_id)
        return True
    except APIError as e:
        if e.response.status_code == 404:
            return False
        raise

def check_image_exists(client, name):
    """Check if image exists locally."""
    try:
        client.images.get(name)
        return True
    except APIError as e:
        if e.response.status_code == 404:
            return False
        raise

# Usage
if not check_image_exists(client, "alpine:latest"):
    print("Pulling image...")
    client.images.pull("alpine:latest")
```

### Validate Parameters

```python
def validate_container_name(name):
    """Validate container name."""
    import re
    
    if not name:
        raise ValueError("Container name cannot be empty")
    
    # Container names must match ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$', name):
        raise ValueError(
            f"Invalid container name '{name}'. "
            "Must start with alphanumeric and contain only [a-zA-Z0-9_.-]"
        )
    
    return True

def validate_port_mapping(ports):
    """Validate port mapping dictionary."""
    if not isinstance(ports, dict):
        raise TypeError("Ports must be a dictionary")
    
    for container_port, host_config in ports.items():
        # Validate container port format
        if '/' in str(container_port):
            port, proto = container_port.split('/')
            if proto not in ['tcp', 'udp', 'sctp']:
                raise ValueError(f"Invalid protocol: {proto}")
        else:
            try:
                int(container_port)
            except ValueError:
                raise ValueError(f"Invalid port number: {container_port}")
        
        # Validate host config
        if host_config is not None:
            if isinstance(host_config, int):
                if not (0 <= host_config <= 65535):
                    raise ValueError(f"Port out of range: {host_config}")
            elif isinstance(host_config, tuple):
                if len(host_config) != 2:
                    raise ValueError("Host config tuple must be (address, port)")
                if not (0 <= host_config[1] <= 65535):
                    raise ValueError(f"Port out of range: {host_config[1]}")

# Usage
try:
    validate_container_name("my-container")
    validate_port_mapping({"80/tcp": 8080, "443/tcp": ("127.0.0.1", 8443)})
except ValueError as e:
    print(f"Validation error: {e}")
```

## Logging and Debugging

### Enable Debug Logging

```python
import logging
from podman import PodmanClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable PodmanPy debug logging
podman_logger = logging.getLogger("podman")
podman_logger.setLevel(logging.DEBUG)

# Enable HTTP connection debugging
urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.DEBUG)

client = PodmanClient()

# All API calls will now be logged
containers = client.containers.list()
```

### Custom Error Logging

```python
import logging
from podman.errors import APIError, PodmanError

logger = logging.getLogger(__name__)

def log_safe_operation(name, func, *args, **kwargs):
    """Execute operation with comprehensive error logging."""
    logger.info(f"Starting operation: {name}")
    
    try:
        result = func(*args, **kwargs)
        logger.info(f"Operation '{name}' completed successfully")
        return result
        
    except APIError as e:
        logger.error(
            f"API error in '{name}': "
            f"status={e.response.status_code}, "
            f"explanation={e.explanation}"
        )
        raise
        
    except PodmanError as e:
        logger.error(f"Podman error in '{name}': {e}")
        raise
        
    except Exception as e:
        logger.exception(f"Unexpected error in '{name}': {e}")
        raise

# Usage
try:
    container = log_safe_operation(
        "get_container",
        client.containers.get,
        "my-container"
    )
except APIError:
    # Handle after logging
    pass
```

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def timed_operation(name):
    """Time an operation and log duration."""
    start = time.time()
    try:
        yield
        duration = time.time() - start
        print(f"{name}: {duration:.3f}s")
    except Exception as e:
        duration = time.time() - start
        print(f"{name} FAILED after {duration:.3f}s: {e}")
        raise

# Usage
with timed_operation("pull_image"):
    image = client.images.pull("alpine:latest")

with timed_operation("container_start"):
    container = client.containers.run("alpine", ["echo", "test"])
```

## Troubleshooting Common Issues

### Connection Issues

```python
def troubleshoot_connection():
    """Diagnose connection problems."""
    from podman import PodmanClient
    
    print("=== Connection Troubleshooting ===")
    
    # Test 1: Can we create a client?
    try:
        client = PodmanClient()
        print("✓ Client created successfully")
    except Exception as e:
        print(f"✗ Failed to create client: {e}")
        return
    
    # Test 2: Can we ping the service?
    try:
        if client.ping():
            print("✓ Service is responding")
        else:
            print("✗ Service not responding to ping")
    except Exception as e:
        print(f"✗ Ping failed: {e}")
        print("\nTry starting Podman service:")
        print("  podman system service --timeout=0 unix:///run/user/$(id -u)/podman/podman.sock &")
        return
    
    # Test 3: Can we get version?
    try:
        version = client.version()
        print(f"✓ Version: {version['Version']}")
    except Exception as e:
        print(f"✗ Failed to get version: {e}")
    
    # Test 4: Can we list containers?
    try:
        containers = client.containers.list()
        print(f"✓ Listed {len(containers)} running containers")
    except Exception as e:
        print(f"✗ Failed to list containers: {e}")
    
    client.close()

# Usage
troubleshoot_connection()
```

### Permission Issues

```python
def check_permissions():
    """Check for permission-related issues."""
    import os
    from pathlib import Path
    
    print("=== Permission Check ===")
    
    # Check socket permissions
    socket_paths = [
        f"/run/user/{os.getuid()}/podman/podman.sock",
        "/run/podman/podman.sock",
        Path.home() / ".local/share/containers/podman/podman.sock"
    ]
    
    for socket_path in socket_paths:
        path = Path(socket_path)
        if path.exists():
            print(f"\nSocket: {socket_path}")
            print(f"  Exists: Yes")
            print(f"  Readable: {path.readable()}")
            print(f"  Writable: {path.writable()}")
            
            # Check SELinux context if available
            try:
                import subprocess
                result = subprocess.run(
                    ["ls", "-Z", str(path)],
                    capture_output=True,
                    text=True
                )
                print(f"  SELinux: {result.stdout.strip()}")
            except Exception:
                pass
        else:
            print(f"\nSocket: {socket_path}")
            print(f"  Exists: No")
```

### Image Pull Issues

```python
def troubleshoot_image_pull(image_name):
    """Diagnose image pull failures."""
    from podman.errors import APIError
    
    print(f"=== Troubleshooting pull of {image_name} ===")
    
    # Check if already exists
    if client.images.exists(image_name):
        print(f"✓ Image already exists locally")
        return
    
    # Try to pull with detailed error handling
    try:
        print(f"Attempting to pull {image_name}...")
        image = client.images.pull(image_name)
        print(f"✓ Pull successful: {image.id}")
        
    except APIError as e:
        print(f"✗ Pull failed with status {e.response.status_code}")
        
        if e.response.status_code == 404:
            print("  Image not found in registry")
            print(f"  Check if '{image_name}' is correct")
            
        elif e.response.status_code == 401:
            print("  Unauthorized - authentication required")
            print("  Try logging in first:")
            print(f"  client.login(username='...', password='...', registry='...')")
            
        elif e.response.status_code == 403:
            print("  Forbidden - access denied")
            print("  Check if you have permission to pull this image")
            
        else:
            print(f"  Explanation: {e.explanation}")
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
```

## Best Practices

### 1. Always Use Context Managers

```python
# Good
with PodmanClient() as client:
    containers = client.containers.list()

# Avoid
client = PodmanClient()
containers = client.containers.list()
# Forgot to close!
```

### 2. Catch Specific Exceptions

```python
# Good
from podman.errors import ImageNotFound, APIError

try:
    image = client.images.get("alpine")
except ImageNotFound:
    print("Image not found locally")
except APIError as e:
    print(f"API error: {e}")

# Avoid
try:
    image = client.images.get("alpine")
except Exception:
    print("Error")  # Too broad!
```

### 3. Validate Inputs Early

```python
# Good
def run_container(name, image):
    validate_container_name(name)
    validate_image_name(image)
    
    return client.containers.run(image, name=name)

# Avoid
def run_container(name, image):
    # Let it fail with cryptic error from API
    return client.containers.run(image, name=name)
```

### 4. Clean Up Resources

```python
# Good
@contextmanager
def temporary_container(image):
    container = client.containers.run(image, detach=True)
    try:
        yield container
    finally:
        container.remove(force=True)

# Avoid
container = client.containers.run(image, detach=True)
# Container left running forever!
```

### 5. Log Errors Appropriately

```python
# Good
logger.error(f"Failed to start container {name}: {e}")
if e.response:
    logger.debug(f"Response: {e.response.text}")

# Avoid
print(e)  # No context, no logging framework
```
