# Security and Authentication

Complete guide to ZeroMQ security mechanisms including CURVE (public-key cryptography), PLAIN (username/password), GSSAPI (Kerberos), and ZAP (ZeroMQ Authentication Protocol).

## Security Mechanism Overview

| Mechanism | Type | Use Case | Requirements |
|-----------|------|----------|--------------|
| NULL | None | Development/testing only | None |
| PLAIN | Username/Password | Simple authentication | Shared credentials |
| CURVE | Public-key crypto | Production security | libsodium, key pairs |
| GSSAPI | Kerberos/SASL | Enterprise environments | Kerberos infrastructure |

## NULL Mechanism (No Security)

Default mechanism with no authentication. Suitable only for trusted networks.

```python
import zmq

context = zmq.Context()

# Default mechanism is NULL
socket = context.socket(zmq.REQ)

# Explicitly set NULL mechanism
socket.setsockopt(zmq.MECHANISM, zmq.NULL)

# Check current mechanism
mechanism = socket.getsockopt(zmq.MECHANISM)
print(f"Security mechanism: {mechanism}")  # 0 (NULL)
```

**Warning:** NULL provides no security. Messages can be intercepted and forged. Never use in production with untrusted networks.

## PLAIN Mechanism (Username/Password)

Simple username/password authentication for basic security needs.

### Server Configuration

```python
import zmq

context = zmq.Context()

# Server socket with PLAIN authentication
server = context.socket(zmq.REP)
server.setsockopt(zmq.MECHANISM, zmq.PLAIN)

# Enable server mode (expects credentials from clients)
server.setsockopt(zmq.PLAIN_SERVER, 1)

# Set expected username and password
server.setsockopt_string(zmq.PLAIN_USERNAME, "admin")
server.setsockopt_string(zmq.PLAIN_PASSWORD, "secret123")

server.bind("tcp://*:5555")

# Handle requests
while True:
    request = server.recv_string()
    print(f"Authenticated request: {request}")
    server.send_string(f"Processed: {request}")
```

### Client Configuration

```python
import zmq

context = zmq.Context()

# Client socket with PLAIN authentication
client = context.socket(zmq.REQ)
client.setsockopt(zmq.MECHANISM, zmq.PLAIN)

# Set credentials (must match server expectations)
client.setsockopt_string(zmq.PLAIN_USERNAME, "admin")
client.setsockopt_string(zmq.PLAIN_PASSWORD, "secret123")

client.connect("tcp://localhost:5555")

# Send authenticated request
client.send_string("Hello")
response = client.recv_string()
print(f"Response: {response}")
```

### PLAIN with ZAP Handler

For centralized authentication using ZAP (ZeroMQ Authentication Protocol):

```python
import zmq
import threading

def zap_handler():
    """ZAP handler thread for centralized authentication"""
    context = zmq.Context()
    zap_socket = context.socket(zmq.REP)
    zap_socket.bind("tcp://127.0.0.1:5556")  # ZAP socket address
    
    while True:
        # Receive ZAP request
        identity = zap_socket.recv()
        requestId = zap_socket.recv()
        address = zap_socket.recv()
        protocol = zap_socket.recv()
        username = zap_socket.recv()
        password = zap_socket.recv()
        
        # Validate credentials (replace with real auth logic)
        if username == b"admin" and password == b"secret123":
            # Send ZAP reply: allow
            zap_socket.send_multipart([
                b"2.1",           # ZAP version
                requestId,        # Request ID
                b"200",           # Status code (200 = OK)
                b"Authentication OK",  # Status text
                b"",              # User ID
                b""               # Principal
            ])
        else:
            # Send ZAP reply: deny
            zap_socket.send_multipart([
                b"2.1",           # ZAP version
                requestId,        # Request ID
                b"400",           # Status code (400 = bad request)
                b"Authentication failed",  # Status text
                b"",              # User ID
                b""               # Principal
            ])

# Start ZAP handler in background thread
threading.Thread(target=zap_handler, daemon=True).start()

# Server socket with PLAIN and ZAP domain
context = zmq.Context()
server = context.socket(zmq.REP)
server.setsockopt(zmq.MECHANISM, zmq.PLAIN)
server.setsockopt(zmq.PLAIN_SERVER, 1)
server.setsockopt_string(zmq.ZAP_DOMAIN, "global")  # Must match ZAP protocol field
server.bind("tcp://*:5557")
```

**Key Points:**
- PLAIN credentials are sent in cleartext (use TLS for encryption)
- Server must set `PLAIN_SERVER = 1` to require authentication
- Username/password comparison is case-sensitive
- ZAP allows centralized authentication logic

## CURVE Mechanism (Public-Key Cryptography)

CURVE provides strong security using elliptic curve cryptography (libsodium). This is the recommended mechanism for production use.

### Key Generation

```python
import zmq

# Generate key pair for server
server_public_key, server_secret_key = zmq.curve_keypair()
print(f"Server public key:  {zmq.z85_encode(server_public_key).decode()}")
print(f"Server secret key:  {zmq.z85_encode(server_secret_key).decode()}")

# Generate key pair for client
client_public_key, client_secret_key = zmq.curve_keypair()
print(f"Client public key:  {zqrt.z85_encode(client_public_key).decode()}")
print(f"Client secret key:  {zmq.z85_encode(client_secret_key).decode()}")

# Save keys securely (e.g., to files or environment variables)
# DO NOT hardcode keys in source code!
```

### Server Configuration with CURVE

```python
import zmq

context = zmq.Context()

# Server socket with CURVE authentication
server = context.socket(zmq.REP)
server.setsockopt(zmq.MECHANISM, zmq.CURVE)

# Enable server mode
server.setsockopt(zmq.CURVE_SERVER, 1)

# Set server's own key pair
server.setsockopt(zmq.CURVE_SECRETKEY, server_secret_key)

# Set client's public key (whitelist of allowed clients)
server.setsockopt(zmq.CURVE_SERVERKEY, client_public_key)

server.bind("tcp://*:5558")

# Handle authenticated requests
while True:
    request = server.recv_string()
    print(f"Authenticated request from client: {request}")
    server.send_string(f"Secure response: {request}")
```

### Client Configuration with CURVE

```python
import zmq

context = zmq.Context()

# Client socket with CURVE authentication
client = context.socket(zmq.REQ)
client.setsockopt(zmq.MECHANISM, zmq.CURVE)

# Set client's own key pair
client.setsockopt(zmq.CURVE_PUBLICKEY, client_public_key)
client.setsockopt(zmq.CURVE_SECRETKEY, client_secret_key)

# Set server's public key (for encryption)
client.setsockopt(zmq.CURVE_SERVERKEY, server_public_key)

client.connect("tcp://localhost:5558")

# Send authenticated request
client.send_string("Hello from authenticated client")
response = client.recv_string()
print(f"Response: {response}")
```

### CURVE with Multiple Clients

```python
import zmq

context = zmq.Context()

# Server that accepts multiple authenticated clients
server = context.socket(zmq.ROUTER)
server.setsockopt(zmq.MECHANISM, zmq.CURVE)
server.setsockopt(zmq.CURVE_SERVER, 1)
server.setsockopt(zmq.CURVE_SECRETKEY, server_secret_key)

# Whitelist multiple client public keys
allowed_clients = {
    "client1": zmq.z85_decode(b"client1_public_key_here"),
    "client2": zmq.z85_decode(b"client2_public_key_here"),
}

# For ROUTER, you can authenticate any whitelisted client
# CURVE_SERVERKEY should be set to one of the allowed keys
# or use ZAP for dynamic authentication

server.bind("tcp://*:5559")

while True:
    identity, message = server.recv_multipart()
    print(f"From {identity}: {message.decode()}")
    server.send_multipart([identity, b"Received"])
```

### Key Management Best Practices

```python
import zmq
import os
import json
from pathlib import Path

class CurveKeyManager:
    """Secure key management for CURVE authentication"""
    
    def __init__(self, key_directory: str = ".zmq_keys"):
        self.key_dir = Path(key_directory)
        self.key_dir.mkdir(exist_ok=True)
    
    def generate_and_save(self, name: str):
        """Generate new key pair and save securely"""
        public_key, secret_key = zmq.curve_keypair()
        
        # Save public key (can be shared)
        public_path = self.key_dir / f"{name}.public.key"
        public_path.write_bytes(public_key)
        
        # Save secret key with restricted permissions
        secret_path = self.key_dir / f"{name}.secret.key"
        secret_path.write_bytes(secret_key)
        secret_path.chmod(0o600)  # Owner read/write only
        
        return public_key, secret_key
    
    def load_public(self, name: str) -> bytes:
        """Load public key"""
        path = self.key_dir / f"{name}.public.key"
        return path.read_bytes()
    
    def load_secret(self, name: str) -> bytes:
        """Load secret key (ensure file permissions are secure!)"""
        path = self.key_dir / f"{name}.secret.key"
        return path.read_bytes()
    
    def from_environment(self, prefix: str):
        """Load keys from environment variables (for containers)"""
        public_key = zmq.z85_decode(os.environ[f"{prefix}_PUBLIC_KEY"])
        secret_key = zmq.z85_decode(os.environ[f"{prefix}_SECRET_KEY"])
        return public_key, secret_key

# Usage example
key_manager = CurveKeyManager()

# Generate keys (do this once, save securely)
# server_public, server_secret = key_manager.generate_and_save("server")
# client_public, client_secret = key_manager.generate_and_save("client")

# Load existing keys
server_public = key_manager.load_public("server")
server_secret = key_manager.load_secret("server")
client_public = key_manager.load_public("client")
client_secret = key_manager.load_secret("client")
```

**Key Points:**
- CURVE provides encryption and authentication
- Server must set `CURVE_SERVER = 1`
- Each client needs unique key pair
- Server whitelists client public keys via `CURVE_SERVERKEY`
- Keys should be stored securely (files with restricted permissions, env vars, or secrets manager)
- libsodium must be available (included in pyzmq wheels)

## GSSAPI Mechanism (Kerberos)

GSSAPI provides enterprise-grade authentication using Kerberos.

### Server Configuration

```python
import zmq

context = zmq.Context()

# Server socket with GSSAPI authentication
server = context.socket(zmq.REP)
server.setsockopt(zmq.MECHANISM, zmq.GSSAPI)

# Enable server mode
server.setsockopt(zmq.GSSAPI_SERVER, 1)

# Set service principal (Kerberos service name)
server.setsockopt_string(zmq.GSSAPI_SERVICE_PRINCIPAL, "zmq-server@EXAMPLE.COM")

# Optional: require plaintext after authentication
# server.setsockopt(zmq.GSSAPI_PLAINTEXT, 0)  # Encrypt messages

server.bind("tcp://*:5560")

while True:
    request = server.recv_string()
    print(f"Kerberos-authenticated request: {request}")
    server.send_string(f"Response: {request}")
```

### Client Configuration

```python
import zmq

context = zmq.Context()

# Client socket with GSSAPI authentication
client = context.socket(zmq.REQ)
client.setsockopt(zmq.MECHANISM, zmq.GSSAPI)

# Set client principal (optional if using Kerberos ticket cache)
client.setsockopt_string(zmq.GSSAPI_PRINCIPAL, "user@EXAMPLE.COM")

client.connect("tcp://localhost:5560")

client.send_string("Hello from Kerberos user")
response = client.recv_string()
print(f"Response: {response}")
```

**Key Points:**
- Requires Kerberos infrastructure (KDC, tickets)
- Client uses Kerberos ticket cache (`KRB5CCNAME` env var)
- Service principal must be registered in KDC
- Messages can be encrypted after authentication
- Suitable for enterprise environments with existing Kerberos

## ZAP (ZeroMQ Authentication Protocol)

ZAP provides centralized authentication that works with all mechanisms.

### ZAP Handler Implementation

```python
import zmq
import threading
import hashlib
import hmac

class ZAPHandler:
    """Centralized authentication handler"""
    
    def __init__(self, domain: str = "global"):
        self.domain = domain
        self.context = zmq.Context()
        self.zap_socket = self.context.socket(zmq.REP)
        self.zap_socket.bind("tcp://127.0.0.1:5561")  # ZAP address
        
        # In-memory credential store (use database in production)
        self.credentials = {
            "admin": self._hash_password("admin123"),
            "user": self._hash_password("user123"),
        }
    
    def _hash_password(self, password: str) -> bytes:
        """Hash password for comparison"""
        return hashlib.sha256(password.encode()).digest()
    
    def handle_zap_requests(self):
        """Main loop for handling ZAP requests"""
        while True:
            try:
                # Receive ZAP request frames
                identity = self.zap_socket.recv()
                request_id = self.zap_socket.recv()
                address = self.zap_socket.recv()
                protocol = self.zap_socket.recv()
                username = self.zap_socket.recv()
                password = self.zap_socket.recv()
                
                # Authenticate
                status, status_text, user_id, principal = self._authenticate(
                    username, password, address
                )
                
                # Send ZAP response
                self.zap_socket.send_multipart([
                    b"2.1",        # ZAP version
                    request_id,    # Request ID (must match)
                    status.encode(),      # Status code
                    status_text.encode(), # Status text
                    user_id.encode() if user_id else b"",  # User ID
                    principal.encode() if principal else b""  # Principal
                ])
                
            except zmq.Again:
                continue
    
    def _authenticate(self, username: bytes, password: bytes, address: bytes):
        """Custom authentication logic"""
        username_str = username.decode()
        password_hash = hashlib.sha256(password.encode()).digest()
        
        if username_str in self.credentials:
            if hmac.compare_digest(self.credentials[username_str], password_hash):
                return "200", "Authentication successful", username_str, f"user:{address.decode()}"
        
        return "400", "Authentication failed", "", ""
    
    def start(self):
        """Start ZAP handler in background thread"""
        self.thread = threading.Thread(target=self.handle_zap_requests, daemon=True)
        self.thread.start()

# Usage
zap = ZAPHandler(domain="global")
zap.start()

# Server socket using ZAP
context = zmq.Context()
server = context.socket(zmq.REP)
server.setsockopt(zmq.MECHANISM, zmq.PLAIN)  # or CURVE
server.setsockopt_string(zmq.ZAP_DOMAIN, "global")  # Must match ZAP handler domain
server.bind("tcp://*:5562")
```

### ZAP Response Codes

| Code | Meaning |
|------|---------|
| 200 | Authentication successful |
| 400 | Bad/missing request |
| 500 | Server error |
| 501 | Mechanism not supported |
| 502 | Security context mismatch |

## Socket Monitoring

Monitor socket events for security auditing and debugging.

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)

# Enable socket monitoring
monitor_socket = socket.get_monitor_socket(
    events=zmq.EVENT_ALL,  # Monitor all events
    address="inproc://monitor"  # Use inproc for same-process monitoring
)

# Connect to monitor socket
monitor = context.socket(zmq.PAIR)
monitor.connect("inproc://monitor")

socket.bind("tcp://*:5563")

while True:
    # Monitor events
    event, value, address = zmq.utils.monitor.parse_monitor_message(
        monitor.recv_multipart()
    )
    
    print(f"Event: {event}, Value: {value}, Address: {address}")
    
    # Handle regular messages
    try:
        request = socket.recv_string(flags=zmq.DONTWAIT)
        print(f"Request: {request}")
        socket.send_string(f"Response: {request}")
    except zmq.Again:
        continue

# Disable monitoring
socket.disable_monitor()
```

### Monitor Events

| Event | Description |
|-------|-------------|
| `EVENT_CONNECTED` | Socket connected successfully |
| `EVENT_CONNECT_DELAYED` | Connection delayed, will retry |
| `EVENT_CONNECT_RETRIED` | Retry timeout expired |
| `EVENT_LISTENING` | Bind successful, socket listening |
| `EVENT_BIND_FAILED` | Bind failed |
| `EVENT_ACCEPTED` | Client accepted |
| `EVENT_ACCEPT_FAILED` | Accept failed |
| `EVENT_CLOSED` | Socket closed |
| `EVENT_CLOSE_FAILED` | Close failed |
| `EVENT_DISCONNECTED` | Peer disconnected |
| `EVENT_HANDSHAKE_SUCCEEDED` | Authentication successful |
| `EVENT_HANDSHAKE_FAILED_AUTH` | Authentication failed |

## Security Best Practices

1. **Never use NULL in production**: Always enable authentication
2. **Use CURVE for most applications**: Strong security with manageable complexity
3. **Store keys securely**: Use file permissions, environment variables, or secrets managers
4. **Rotate keys periodically**: Implement key rotation procedures
5. **Monitor authentication events**: Log successful and failed attempts
6. **Use ZAP for centralized auth**: Single point for authentication logic
7. **Enable TLS for transport encryption**: Combine CURVE with TCP+TLS for end-to-end encryption
8. **Validate all inputs**: Even authenticated messages can contain malicious data
9. **Set appropriate timeouts**: Prevent hanging connections
10. **Implement rate limiting**: Prevent denial-of-service attacks
