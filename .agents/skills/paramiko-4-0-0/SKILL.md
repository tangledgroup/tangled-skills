---
name: paramiko-4-0-0
description: Complete toolkit for Paramiko 4.0.0, a pure-Python SSHv2 implementation providing both client and server functionality. Use when building Python applications that need SSH connections, remote command execution, SFTP file transfers, port forwarding, or running an SSH server in Python.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.0.0"
tags:
  - SSH
  - SFTP
  - SCP
  - networking
  - remote execution
category: networking
external_references:
  - https://www.paramiko.org/
  - https://docs.paramiko.org/
  - https://github.com/paramiko/paramiko
  - https://www.paramiko.org/faq.html
  - https://www.paramiko.org/installing.html
  - https://github.com/paramiko/paramiko/tree/4.0.0
---
## Overview
Paramiko is a pure-Python implementation of the SSHv2 protocol, providing both client and server functionality. It relies on the `cryptography` library for cryptographic operations. Paramiko provides the foundation for higher-level libraries like Fabric.

**Key capabilities:**
- SSH client connections (password, key-based, GSSAPI authentication)
- SSH server implementation with custom authentication
- SFTP file transfers (upload, download, directory listing)
- Port forwarding (local and remote TCP forwarding)
- X11 forwarding
- SSH agent integration
- Shell sessions and command execution

## When to Use
Use this skill when:
- Connecting to remote servers via SSH from Python
- Executing remote commands and capturing output
- Transferring files via SFTP
- Building an SSH server in Python
- Implementing port forwarding or tunneling
- Automating server administration tasks
- Integrating with SSH agents for key-based auth

**Note:** For simple remote shell commands, consider using [Fabric](https://fabfile.org) instead, which is built on top of Paramiko.

## Installation / Setup
```bash
pip install paramiko
# paramiko depends on: cryptography, pynacl (optional)
```

## Core Concepts
### Architecture Overview

Paramiko has three main layers:

1. **Transport** (`paramiko.transport.Transport`) — Core protocol implementation. Attaches to a stream, negotiates encryption, authenticates, and creates channels.
2. **Channel** (`paramiko.channel.Channel`) — Socket-like objects for data transfer across the encrypted session. Multiple channels can be multiplexed over one transport.
3. **Client/Server** (`paramiko.client.SSHClient`, `paramiko.server.ServerInterface`) — High-level APIs wrapping Transport and Channel.

### Authentication Methods

- **Password authentication** — `Transport.auth_password(username, password)`
- **Public key authentication** — `Transport.auth_publickey(username, key)`
- **GSSAPI/Kerberos** — Supported via `gss_auth`, `gss_kex` parameters
- **Keyboard-interactive** — Falls back automatically when password auth is disabled

### Key Types

Paramiko supports multiple key types through the `PKey` base class:

| Key Type | Class | Loading |
|----------|-------|---------|
| RSA | `paramiko.RSAKey` | `RSAKey.from_private_key_file(path)` |
| DSS/SSH-2 | `paramiko.DSSKey` | `DSSKey.from_private_key_file(path)` |
| ECDSA | `paramiko.ECDSAKey` | `ECDSAKey.from_private_key_file(path)` |
| Ed25519 | `paramiko.Ed25519Key` | `Ed25519Key.from_private_key_file(path)` |

All key types inherit from `paramiko.pkey.PKey`. Use `PKey.from_private_key_file()` as a factory to auto-detect the key type.

### Host Key Policies

When connecting, Paramiko needs to verify the server's host key:

| Policy | Behavior |
|--------|----------|
| `AutoAddPolicy` | Automatically adds unknown host keys (default for many use cases) |
| `RejectPolicy` | Automatically rejects unknown hosts (most secure default) |
| `WarningPolicy` | Logs a warning but accepts unknown hosts |
| Custom | Subclass `MissingHostKeyPolicy` and implement `missing_host_key()` |

## Advanced Topics
## Advanced Topics

- [Transport Deep Dive](reference/01-transport-deep-dive.md)
- [Server Mode Guide](reference/02-server-mode-guide.md)
- [Sftp Reference](reference/03-sftp-reference.md)
- [Usage Examples](reference/04-usage-examples.md)
- [Api Reference](reference/05-api-reference.md)

