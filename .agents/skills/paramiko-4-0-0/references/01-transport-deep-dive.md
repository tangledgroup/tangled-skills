# Transport Deep Dive

## Transport Class Overview

The `Transport` class is the core of Paramiko. It attaches to a stream (usually a socket), negotiates an encrypted session, authenticates, and creates channels for data transfer.

```python
import paramiko
import socket

sock = socket.create_connection(('host.example.com', 22))
transport = paramiko.Transport(sock)
transport.start_client()  # or start_server() for server mode
```

### Constructor Parameters

```python
Transport(
    sock,                          # socket or socket-like object
    default_window_size=2097152,   # 2MB default window size
    default_max_packet_size=32768, # 32KB default max packet
    gss_kex=False,                 # Enable GSSAPI key exchange
    gss_deleg_creds=True,          # Enable GSSAPI credential delegation
    disabled_algorithms=None,      # Dict to disable specific algorithms
    server_sig_algs=True,          # Send supported pubkey algos (server mode)
    strict_kex=True,               # Strict key exchange mode
    packetizer_class=None          # Custom packetizer class
)
```

### Client Connection Flow

```python
transport = paramiko.Transport(('host.example.com', 22))
transport.start_client()          # Negotiate SSH2 session
remote_key = transport.get_remote_server_key()  # Get server's host key
transport.auth_password('user', 'password')     # Authenticate
# OR
transport.auth_publickey('user', private_key)

# Now open channels
chan = transport.open_session()
chan.exec_command('uptime')
print(chan.recv(1024).decode())
```

### Server Connection Flow

```python
import paramiko

transport = paramiko.Transport(('0.0.0.0', 2222))
transport.add_server_key(ed25519_key)
transport.start_server(server=my_server_interface)

# Wait for client
chan = transport.accept(20)
if chan:
    chan.send("Welcome!\n")
```

## SecurityOptions

Control allowed algorithms via `Transport.get_security_options()`:

```python
transport = paramiko.Transport(sock)
sec = transport.get_security_options()

# Ciphers (ordered by preference, first is preferred)
sec.ciphers = [
    'aes128-gcm@openssh.com',
    'aes256-gcm@openssh.com',
    'chacha20-poly1305@openssh.com',
]

# Key exchange algorithms
sec.kex = [
    'curve25519-sha256',
    'curve25519-sha256@libssh.org',
    'diffie-hellman-group16-sha512',
]

# Digest (MAC) algorithms
sec.digests = [
    'hmac-sha2-256-etm@openssh.com',
    'hmac-sha2-512-etm@openssh.com',
]

# Server key types (key exchange/algorithms for host keys)
sec.key_types = [
    'ssh-ed25519',
    'rsa-sha2-512',
    'rsa-sha2-256',
]
```

### Disabling Algorithms at Transport Level

```python
transport = paramiko.Transport(
    sock,
    disabled_algorithms={
        "ciphers": ["3des-cbc"],       # Disable weak cipher
        "kex": ["diffie-hellman-group1-sha1"],  # Disable weak KEX
    }
)
```

## Channel Types

| Type | Description | Use Case |
|------|-------------|----------|
| `"session"` | Standard session channel | `exec_command`, shell |
| `"direct-tcpip"` | Local port forwarding | Tunnel local → remote |
| `"forwarded-tcpip"` | Remote port forwarding | Tunnel remote → local |
| `"x11"` | X11 forwarding | GUI applications |
| `"auth-agent@openssh.com"` | SSH agent forwarding | Forward agent keys |

### Opening Channels

```python
# Session channel (via Transport)
chan = transport.open_session()

# Direct TCP forwarding (local → remote)
transport.open_channel(
    "direct-tcpip",
    dest_addr=('remote-host.com', 80),   # destination
    src_addr=('localhost', 12345)         # source
)

# X11 channel
transport.open_x11_channel(src_addr=('localhost', 6010))

# SSH agent forwarding channel
agent_chan = transport.open_forward_agent_channel()
```

## Port Forwarding

### Request Remote Port Forwarding

```python
def handle_channel(channel, origin_addr, server_addr):
    # Called when a connection arrives on the forwarded port
    print(f"Connection from {origin_addr}")
    channel.send("Hello!")
    channel.close()

transport.request_port_forward('0.0.0.0', 8080, handler=handle_channel)
```

### Cancel Port Forwarding

```python
transport.cancel_port_forward('0.0.0.0', 8080)
```

## Transport Properties and Methods

| Method/Property | Description |
|-----------------|-------------|
| `is_active()` | Returns True if session is open |
| `is_authenticated()` | Returns True if authenticated |
| `get_remote_server_key()` | Get the server's host key (PKey) |
| `get_security_options()` | Get SecurityOptions for algorithm tuning |
| `open_session()` | Open a new session channel |
| `open_channel(kind, ...)` | Open any type of channel |
| `close()` | Close the transport and all channels |
| `atfork()` | Clean up after fork (don't close session) |

## Context Manager Support

Both Transport and Channel support context managers:

```python
with paramiko.Transport(('host.example.com', 22)) as transport:
    transport.start_client()
    transport.auth_password('user', 'pass')
    
    with transport.open_session() as chan:
        chan.exec_command('hostname')
        print(chan.recv(1024).decode())
```
