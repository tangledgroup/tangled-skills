# SSH Server Implementation

## Overview

Paramiko can run as an SSH server entirely in Python. This is useful for building custom sshd implementations, testing SSH clients, or creating specialized SSH services.

## ServerInterface Callbacks

The `ServerInterface` class defines callbacks that you override to control server behavior:

```python
import paramiko
import socket
import threading

class MyServer(paramiko.ServerInterface):
    def __init__(self):
        self.allowed_keys = [paramiko.Ed25519Key.from_path("~/.ssh/id_ed25519.pub")]

    def check_auth_password(self, username, password):
        if username == "user" and password == "secret":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        if key in self.allowed_keys:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        # Handle command execution
        channel.send(f"Executing: {command}\n".encode())
        channel.send_exit_status(0)
        channel.shutdown()
        return True

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                   pixelwidth, pixelheight, modes):
        return True

    def check_channel_subsystem_request(self, channel, name):
        if name == "sftp":
            return True
        return False

    def check_port_forward_request(self, address, port):
        # Reject or accept port forwarding
        return False
```

## Starting a Server

```python
import paramiko
import socket
import threading

# Load host key
host_key = paramiko.Ed25519Key.from_path("~/.ssh/id_ed25519")

# Create server interface
server = MyServer()

# Bind and listen
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", 2222))
sock.listen(10)
print("Listening for connection...")

client_conn, addr = sock.accept()
print(f"Got connection from {addr}")

# Create Transport and start server mode
transport = paramiko.Transport(client_conn)
transport.load_server_moduli()
transport.add_server_key(host_key)
transport.start_server(server=server)

# Wait for auth
chan = transport.accept(timeout=10)
if chan is None:
    raise Exception("No channel opened")

# Handle the channel
username = transport.get_username()
print(f"Authenticated as {username}")

transport.close()
sock.close()
```

## Server Mode with SFTP

Register the SFTP subsystem handler on the Transport:

```python
from paramiko.sftp_server import SFTPServer

transport.set_subsystem_handler("sftp", SFTPServer)
```

## Thread Safety

Each accepted channel runs in its own thread. The `SubsystemHandler.start_subsystem()` method is called in a new thread for each subsystem request. Ensure your handler checks `Transport.is_active()` to detect when the connection closes, otherwise threads may prevent Python from exiting.

## Authentication Return Values

- `paramiko.AUTH_FAILED` — authentication rejected
- `paramiko.AUTH_SUCCESSFUL` — authentication complete
- `paramiko.AUTH_PARTIALLY_SUCCESSFUL` — auth accepted but more required (stateful auth)

## GSS-API / Kerberos Server Auth

Override `enable_auth_gssapi()` to return `True`, and implement:

- `check_auth_gssapi_with_mic(username, gss_authenticated, cc_file)`
- `check_auth_gssapi_keyex(username, gss_authenticated, cc_file)`

Note: Kerberos credential delegation is not supported.

## Interactive Authentication

For keyboard-interactive auth, override:

```python
from paramiko.server import InteractiveQuery

def check_auth_interactive(self, username, submethods):
    return InteractiveQuery(
        name="keyboard-interactive",
        instructions="Please answer the following:",
        prompts=[("Password: ", False)]  # (text, echo)
    )

def check_auth_interactive_response(self, responses):
    if responses[0] == "correct_password":
        return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED
```
