# Server Mode Guide

## ServerInterface Base Class

`ServerInterface` defines the behavior of Paramiko in server mode. Methods are called from Paramiko's primary thread — avoid blocking or sleeping operations.

```python
import paramiko

class MyServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    # Required: Allow/deny channel requests
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    # Optional: Control authentication methods
    def get_allowed_auths(self, username):
        return "password"  # or "publickey,password" etc.
    
    # Optional: Password authentication handler
    def check_auth_password(self, username, password):
        if username == "admin" and password == "secret":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    # Optional: Public key authentication handler
    def check_auth_publickey(self, username, key):
        # Check if key is authorized
        if self.is_key_authorized(username, key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

# Start server
transport = paramiko.Transport(('0.0.0.0', 2222))
transport.add_server_key(host_key)
transport.start_server(server=MyServer())
chan = transport.accept(30)
```

## Channel Request Handlers

Override these methods to control what's allowed on a channel after authentication:

| Method | Purpose | Default |
|--------|---------|---------|
| `check_channel_pty_request(channel, term, width, height)` | PTY allocation | Rejected |
| `check_channel_shell_request(channel)` | Interactive shell | Rejected |
| `check_channel_subsystem_request(channel, name)` | Subsystem (e.g., SFTP) | Rejected |
| `check_channel_window_change_request(channel, width, height)` | Resize PTY | Rejected |
| `check_channel_x11_request(channel, screen)` | X11 forwarding | Rejected |
| `check_channel_forward_agent_request(channel)` | Agent forwarding | Rejected |

### Return Codes

| Constant | Value | Meaning |
|----------|-------|---------|
| `OPEN_SUCCEEDED` | 0 | Allow request |
| `OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED` | 1 | Administratively prohibited |
| `OPEN_FAILED_CONNECT_FAILED` | 2 | Connection failed |
| `OPEN_FAILED_UNKNOWN_CHANNEL_TYPE` | 3 | Unknown channel type |
| `OPEN_FAILED_RESOURCE_SHORTAGE` | 4 | Resource shortage |

## Complete Server Example with Multiple Auth Methods

```python
import paramiko
import threading

class MultiAuthServer(paramiko.ServerInterface):
    def __init__(self, authorized_keys):
        """authorized_keys: dict of username -> list of PKey objects"""
        self.authorized_keys = authorized_keys
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        return "publickey,password"
    
    def check_auth_password(self, username, password):
        # Simple demo auth - in production, use proper credential store
        if username == "user1" and password == "password1":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        if username in self.authorized_keys:
            if key in self.authorized_keys[username]:
                return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_channel_shell_request(self, channel):
        return True  # Allow shell access for authenticated users

# Setup
host_key = paramiko.Ed25519Key.generate()
authorized_keys = {
    "user1": [paramiko.RSAKey.from_private_key_file('/path/to/key1')],
}

server = MultiAuthServer(authorized_keys)
transport = paramiko.Transport(('0.0.0.0', 2222))
transport.add_server_key(host_key)
transport.start_server(server=server)

# Accept client connection
channel = transport.accept(30)
if channel:
    channel.send("Welcome to the server!\n")
    channel.close()
```

## Subsystem Handlers

For custom subsystems (like SFTP), subclass `SubsystemHandler`:

```python
import paramiko

class MySubsystem(paramiko.SubsystemHandler):
    def start_subsystem(self):
        # Called when a client requests this subsystem
        channel = self.channel
        name = self.name  # e.g., "sftp"
        
        channel.send("Subsystem started\n")
        
        # Handle data from client
        while True:
            data = channel.recv(1024)
            if not data:
                break
            channel.send(f"Echo: {data.decode()}\n")

# Register the subsystem handler
transport.set_subsystem_handler('myapp', MySubsystem)
```

## Server-Side Port Forwarding

When a client requests port forwarding, handle incoming connections:

```python
class ForwardingServer(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == "direct-tcpip":
            # Client wants to forward a connection
            return paramiko.OPEN_SUCCEEDED
        elif kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_request(self, kind, chanid):
        if kind in ("direct-tcpip", "forwarded-tcpip", "session"):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
```

## Transport Methods for Server Mode

| Method | Purpose |
|--------|---------|
| `add_server_key(key)` | Add host key (required before start_server) |
| `get_server_key()` | Get the negotiated host key |
| `start_server(server)` | Begin server negotiation with given interface |
| `load_server_moduli(filename)` | Load prime moduli for group-exchange KEX |

## Authentication Flow Summary

1. Client connects → Transport negotiates protocol version
2. Key exchange → Both sides agree on algorithms and keys
3. Server sends host key → Client verifies (or applies policy)
4. Client requests authentication type
5. Server's `ServerInterface` methods handle each auth attempt:
   - `check_auth_none()` — Check if user can authenticate without credentials
   - `check_auth_password()` — Handle password auth
   - `check_auth_publickey()` — Handle public key auth
   - `check_auth_keyboard_interactive()` — Handle keyboard-interactive
6. On success → Client can open channels
