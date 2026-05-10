---
name: paramiko-4-0-0
description: >-
  Complete toolkit for Paramiko 4.0.0, a pure-Python SSHv2 protocol implementation providing both client and server functionality. Use when building Python applications that require SSH connections, remote command execution, SFTP file transfers, SSH tunneling/port forwarding, running an in-Python sshd, or programmatic SSH authentication with password, public key, agent, certificate, or GSS-API/Kerberos methods.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ssh
  - sshv2
  - sftp
  - remote-execution
  - file-transfer
  - tunneling
  - port-forwarding
  - authentication
  - networking
category: library
external_references:
  - https://www.paramiko.org/
  - https://docs.paramiko.org/
  - https://github.com/paramiko/paramiko
  - https://www.paramiko.org/faq.html
  - https://www.paramiko.org/installing.html
  - https://github.com/paramiko/paramiko/tree/4.0.0
---

# Paramiko 4.0.0

## Overview

Paramiko is a pure-Python implementation of the SSHv2 protocol, providing both client and server functionality. It provides the foundation for the high-level SSH library Fabric, which is recommended for common client use-cases such as running remote shell commands or transferring files.

Direct use of Paramiko itself is intended for users who need advanced/low-level primitives or want to run an in-Python sshd.

Paramiko relies on the `cryptography` library for cryptographic functionality (which uses C and Rust extensions with precompiled wheels available), plus `bcrypt` and `pynacl` for Ed25519 key support.

## When to Use

- Connecting to SSH servers from Python applications
- Executing remote shell commands programmatically
- Transferring files via SFTP (upload, download, directory operations)
- Setting up SSH tunnels and port forwarding (local, remote, dynamic)
- Building an in-Python SSH server (sshd)
- Programmatic SSH authentication with multiple methods (password, public key, agent, certificate, GSS-API/Kerberos)
- X11 forwarding over SSH
- SSH agent forwarding
- Parsing OpenSSH-style `ssh_config` files programmatically

## Core Concepts

### Two API Levels

Paramiko provides two levels of API:

- **High-level (`SSHClient`)** — convenient client API for connecting, executing commands, and opening SFTP sessions. Handles host key verification, authentication ordering, and connection management automatically.
- **Low-level (`Transport`)** — direct control over SSH negotiation, encryption setup, and channel management. Used for both client and server modes.

### Key Classes

- `SSHClient` — high-level client API, starting point for most use cases
- `Transport` — core SSH session, handles encryption negotiation and channel multiplexing
- `Channel` — socket-like object for data transfer across an encrypted session
- `SFTPClient` / `SFTPFile` — SFTP protocol client for file operations
- `ServerInterface` — callback interface for implementing an SSH server
- `SFTPServer` — server-side SFTP subsystem handler

### Authentication Methods

Paramiko supports multiple authentication strategies:

- Password authentication
- Public key authentication (RSA, DSA, ECDSA, Ed25519)
- SSH agent keys (`Agent` class)
- OpenSSH certificates
- GSS-API / Kerberos authentication
- Interactive (keyboard-interactive) authentication
- `AuthStrategy` — newer pluggable authentication mechanism

### Host Key Verification

By default, `SSHClient` uses `RejectPolicy` which rejects unknown host keys. Load known hosts from the system file or a custom file using `load_system_host_keys()` and `load_host_keys()`. For development/testing, `AutoAddPolicy` automatically accepts new host keys.

## Installation / Setup

Install via pip:

```bash
pip install paramiko
```

Direct dependencies:

- `cryptography` — low-level encryption algorithms (has its own sub-dependencies)
- `bcrypt` and `pynacl` — Ed25519 key support

Optional dependency for GSS-API/Kerberos:

```bash
pip install "paramiko[gssapi]"
```

On Linux, you may need a C build toolchain plus development headers for Python, OpenSSL, and libffi if cryptography wheels are not available. Cryptography 3.4+ also requires Rust tooling for source installs.

## Usage Examples

### Basic SSH Connection and Command Execution

```python
import paramiko

# Create client and auto-accept host keys (use AutoAddPolicy for dev only)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect with password
client.connect("hostname", username="user", password="secret")

# Execute a command
stdin, stdout, stderr = client.exec_command("ls -la /tmp")
print(stdout.read().decode())
print(stderr.read().decode())

# Always close explicitly to avoid end-of-process hangs
client.close()
```

### Key-Based Authentication

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()  # load ~/.ssh/known_hosts

# Connect with private key file
client.connect(
    "hostname",
    username="user",
    key_filename="/home/user/.ssh/id_ed25519",
    passphrase="key_passphrase"  # optional, for encrypted keys
)

stdin, stdout, stderr = client.exec_command("whoami")
print(stdout.read().decode().strip())
client.close()
```

### SFTP File Transfer

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("hostname", username="user", password="secret")

# Open SFTP session
sftp = client.open_sftp()

# Upload a file
sftp.put("/local/path/file.txt", "/remote/path/file.txt")

# Download a file
sftp.get("/remote/path/file.txt", "/local/path/file.txt")

# List directory with attributes
for attr in sftp.listdir_attr("/remote/dir"):
    print(attr.filename, attr.st_size)

# Create directory
sftp.mkdir("/remote/newdir", mode=0o755)

# Remove file
sftp.remove("/remote/path/old_file.txt")

sftp.close()
client.close()
```

### SSH Tunnel / Port Forwarding

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("jump_host", username="user", password="secret")

# Local port forwarding: bind local port 8080 to remote target
transport = client.get_transport()
transport.set_keepalive(60)
channel = transport.open_channel(
    "direct-tcpip",
    dest_addr=("target_host_internal", 443),
    src_addr=("127.0.0.1", 8080)
)

client.close()
```

### Using SSH Agent

```python
import paramiko

# Connect to local SSH agent
agent = paramiko.Agent()
keys = agent.get_keys()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Try each agent key
for key in keys:
    try:
        client.connect("hostname", username="user", pkey=key)
        break
    except paramiko.AuthenticationException:
        continue

agent.close()
client.close()
```

## Advanced Topics

**SSH Server Implementation**: Building an in-Python sshd with custom authentication and channel handling → [SSH Server](reference/01-ssh-server.md)

**Transport and Channels**: Low-level Transport API, channel types, port forwarding, keepalive, X11 forwarding → [Transport & Channels](reference/02-transport-channels.md)

**Keys and Authentication**: Key types (RSA, DSA, ECDSA, Ed25519), key generation, loading, certificates, host keys, SSH agent, AuthStrategy → [Keys & Authentication](reference/03-keys-authentication.md)

**SFTP Operations**: SFTPClient file operations, SFTPFile streaming, server-side SFTPServer → [SFTP Operations](reference/04-sftp-operations.md)

**Configuration and Proxy**: SSHConfig parser for ssh_config files, ProxyCommand support, expansion tokens → [Configuration & Proxy](reference/05-config-proxy.md)

**Exceptions**: Complete exception hierarchy for error handling → [Exceptions](reference/06-exceptions.md)
