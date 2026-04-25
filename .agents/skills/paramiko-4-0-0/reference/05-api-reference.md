# API Reference

### Client API

| Class | Module | Description |
|-------|--------|-------------|
| `SSHClient` | `paramiko.client` | High-level SSH client wrapping Transport, Channel, SFTP |
| `MissingHostKeyPolicy` | `paramiko.client` | Base class for host key verification policies |
| `AutoAddPolicy` | `paramiko.client` | Auto-accept unknown host keys |
| `RejectPolicy` | `paramiko.client` | Reject unknown hosts (secure default) |
| `WarningPolicy` | `paramiko.client` | Warn but accept unknown hosts |

### Transport API

| Class | Module | Description |
|-------|--------|-------------|
| `Transport` | `paramiko.transport` | Core SSH protocol, handles encryption and channels |
| `SecurityOptions` | `paramiko.transport` | Configure allowed ciphers, digests, key types, KEX |

### Channel API

| Class | Module | Description |
|-------|--------|-------------|
| `Channel` | `paramiko.channel` | Socket-like tunnel for data transfer |
| `ChannelFile` | `paramiko.channel` | File-like wrapper around a Channel |
| `open_only()` | `paramiko.channel` | Open-only context manager for channels |

### SFTP API

| Class | Module | Description |
|-------|--------|-------------|
| `SFTPClient` | `paramiko.sftp_client` | SFTP client for remote file operations |
| `SFTPFile` | `paramiko.sftp_client` | File-like object from SFTP operations |

### Server API

| Class | Module | Description |
|-------|--------|-------------|
| `ServerInterface` | `paramiko.server` | Base class for SSH server behavior control |
| `SubsystemHandler` | `paramiko.server` | Handler base for subsystem requests (e.g., SFTP) |

### Key Management

| Class | Module | Description |
|-------|--------|-------------|
| `PKey` | `paramiko.pkey` | Base class for all key types |
| `RSAKey` | `paramiko.rsakey` | RSA key support |
| `DSSKey` | `paramiko.dsskey` | DSS/SSH-2 key support |
| `ECDSAKey` | `paramiko.ecdsakey` | ECDSA key support |
| `Ed25519Key` | `paramiko.ed25519key` | Ed25519 key support |

### Other Modules

| Module | Description |
|--------|-------------|
| `paramiko.agent` | SSH agent client for loading keys from local agent |
| `paramiko.proxy` | ProxyCommand support for jump hosts |
| `paramiko.ssh_exception` | All Paramiko exception classes |
| `paramiko.config` | OpenSSH config file parser (`SSHConfig`) |

### Key Exceptions

| Exception | Description |
|-----------|-------------|
| `AuthenticationException` | Authentication failed, may retry with different credentials |
| `BadAuthenticationType` | Wrong auth type used (e.g., password when only key allowed) |
| `BadHostKeyException` | Server's host key doesn't match expected |
| `SSHException` | Base exception for all Paramiko errors |
