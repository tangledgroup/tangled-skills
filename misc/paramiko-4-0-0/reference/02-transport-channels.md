# Transport & Channels

## Transport — The Core SSH Session

`Transport` is the fundamental class managing the SSH session. It handles encryption negotiation, authentication, and multiplexes multiple channels over a single encrypted connection.

### Client Mode

```python
import paramiko
import socket

# Create a raw socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("hostname", 22))

# Wrap in Transport
transport = paramiko.Transport(sock)

# Start client mode (negotiate encryption)
transport.start_client()

# Verify server host key
server_key = transport.get_remote_server_key()
assert server_key.get_name() == "ssh-ed25519"

# Authenticate
transport.auth_password(username="user", password="secret")
# or
transport.auth_publickey(username="user", key=my_pkey)

# Shortcut: connect() combines start_client + host key check + auth
transport.connect(hostkey=expected_key, username="user", password="secret")
```

### Transport Properties and Methods

- `is_active()` — returns True if session is open
- `is_authenticated()` — returns True if authenticated successfully
- `get_username()` — returns authenticated username (or None)
- `get_banner()` — returns server banner string
- `get_remote_server_key()` — returns the server's host key as a PKey
- `close()` — close session and all open channels

### Keepalive

```python
# Send keepalive packets every 60 seconds to prevent NAT timeouts
transport.set_keepalive(60)

# Alternative: send manual ignore packets
transport.send_ignore(byte_count=20)
```

### Key Renegotiation

Keys are automatically renegotiated after a certain number of packets/bytes. Force manual renegotiation:

```python
transport.renegotiate_keys()
```

## Channels — Socket-like Data Streams

Channels are multiplexed over a single Transport. They act like sockets but send/receive data over the encrypted session.

### Channel Types

- `"session"` — standard shell or command execution channel
- `"direct-tcpip"` — direct TCP forwarding (local port forward)
- `"forwarded-tcpip"` — reverse TCP forwarding (remote port forward)
- `"x11"` — X11 forwarding

### Opening Channels

```python
# Session channel (alias for open_channel("session"))
chan = transport.open_session()

# Direct TCP IP channel
chan = transport.open_channel(
    "direct-tcpip",
    dest_addr=("target.internal", 443),
    src_addr=("127.0.0.1", 8080)
)

# With custom window/packet sizes
chan = transport.open_channel(
    "session",
    window_size=2097152,
    max_packet_size=34816
)

# With timeout (default 3600s)
chan = transport.open_channel("session", timeout=30)
```

### Channel I/O

```python
# Execute command on session channel
chan.exec_command("ls -la")

# Read output
data = chan.recv(1024)  # returns bytes, empty string = closed
exit_code = chan.recv_exit_status()  # blocks until command finishes

# Check if data is ready
if chan.recv_ready():
    data = chan.recv(4096)

# Send data
bytes_sent = chan.send(b"hello\n")
chan.sendall(b"complete message")  # sends all or raises error

# Stderr (only without pty)
chan.set_combine_stderr(True)  # merge stderr into stdout
# or read separately:
if chan.recv_stderr_ready():
    err = chan.recv_stderr(1024)
```

### Interactive Shell

```python
chan = transport.open_session()
chan.get_pty(term="vt100", width=80, height=24)
chan.invoke_shell()

# Resize terminal
chan.resize_pty(width=120, height=40)
```

### Channel Timeout and Blocking

```python
chan.settimeout(10.0)  # 10 second timeout
chan.settimeout(None)  # no timeout (blocking)
chan.setblocking(0)    # non-blocking mode
```

### Closing Channels

```python
chan.shutdown_read()   # close incoming direction
chan.shutdown_write()  # close outgoing direction
chan.shutdown(2)       # close both directions
chan.close()           # fully close
```

## Port Forwarding

### Local Port Forwarding (via direct-tcpip channel)

```python
# Connect through jump host to internal target
transport = client.get_transport()
chan = transport.open_channel(
    "direct-tcpip",
    dest_addr=("internal-server", 3306),
    src_addr=("127.0.0.1", 0)
)
```

### Remote Port Forwarding (server-side listening)

```python
# Ask server to listen on port 8888 and forward to client
transport.request_port_forward("0.0.0.0", 8888, handler=my_handler)

# Handler signature:
def my_handler(channel, origin_addr, server_addr):
    # channel is the forwarded connection
    pass

# Cancel forwarding
transport.cancel_port_forward("0.0.0.0", 8888)
```

## X11 Forwarding

```python
# On client side, request X11 on a session channel
auth_cookie = chan.request_x11(
    screen_number=0,
    single_connection=False,
    handler=x11_handler
)

# Handler signature:
def x11_handler(channel, (address, port)):
    # Handle incoming X11 connection
    pass
```

## SSH Agent Forwarding

```python
# On server side, handle forwarded agent requests
chan.request_forward_agent(handler=agent_handler)
```
