# Exceptions

## Exception Hierarchy

All Paramiko exceptions inherit from `paramiko.SSHException`.

## Core Exceptions

### SSHException

Base exception for SSH2 protocol negotiation failures or logic errors. Catch this for general SSH errors.

```python
try:
    client.connect("hostname", username="user", password="wrong")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
```

### AuthenticationException

Raised when authentication fails. May be retryable with different credentials. Subclass of `SSHException`.

```python
try:
    client.connect("hostname", username="user", password="wrong")
except paramiko.AuthenticationException:
    print("Authentication failed")
```

### UnableToAuthenticate

Subclass of `AuthenticationException`. Raised when using the newer `AuthStrategy` mechanism and authentication fails.

### BadAuthenticationType

Raised when an authentication type (e.g., password) is used but the server doesn't allow it. Provides `explanation` and `types` attributes listing allowed methods.

```python
try:
    transport.auth_none(username="user")
except paramiko.BadAuthenticationType as e:
    print(f"Server allows: {e.types}")  # e.g., "publickey,password"
```

### BadHostKeyException

Raised when the server's host key doesn't match the expected key. Provides `hostname`, `got_key`, and `expected_key` attributes.

```python
try:
    client.connect("hostname", username="user")
except paramiko.BadHostKeyException as e:
    print(f"Host key mismatch for {e.hostname}")
```

## Connection Exceptions

### NoValidConnectionsError

Raised when multiple connection attempts (e.g., IPv4 and IPv6) all fail. Wraps individual errors in an `errors` dict keyed by address tuples.

```python
try:
    client.connect("unresolvable-host")
except paramiko.NoValidConnectionsError as e:
    for addr, err in e.errors.items():
        print(f"Failed {addr}: {err}")
```

### ChannelException

Raised when opening a new `Channel` fails. Provides `code` and `text` from the server.

## Configuration Exceptions

### ConfigParseError

Raised when parsing an ssh_config file encounters fatal errors (invalid syntax, misuse of Match keywords). New in version 2.7.

### CouldNotCanonicalize

Raised when hostname canonicalization fails and fallback is disabled (`CanonicalizeFallbackLocal no`). New in version 2.7.

### ProxyCommandFailure

Raised when a ProxyCommand subprocess returns an error. Provides `command` and `error` attributes. New in version 2.10.

## Key Exceptions

### PasswordRequiredException

Raised when loading an encrypted private key without providing a password/passphrase.

```python
try:
    key = paramiko.RSAKey.from_private_key_file("/path/to/encrypted_key")
except paramiko.PasswordRequiredException:
    key = paramiko.RSAKey.from_private_key_file(
        "/path/to/encrypted_key", password="passphrase"
    )
```

### UnknownKeyType

Raised when attempting to read a key type not supported by the crypto backend. New in version 3.2.

## Protocol Exceptions

### IncompatiblePeer

Raised when there's an algorithm disagreement during key exchange (no common KEX, cipher, or MAC algorithms). New in version 2.9.

### MessageOrderError

Raised when out-of-order protocol messages violate "strict kex" mode. New in version 3.4.

## Internal Exceptions

### PartialAuthentication

Internal exception for partial authentication state. Typically not caught directly by application code. Provides `types` attribute listing remaining auth methods.

## Error Handling Best Practices

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()

try:
    client.connect(
        "hostname",
        username="user",
        key_filename="/path/to/key",
        timeout=10,
        auth_timeout=5
    )
except paramiko.BadHostKeyException:
    # Host key changed — possible MITM attack
    raise RuntimeError("Server host key has changed!")
except paramiko.AuthenticationException:
    # Wrong credentials or key not authorized
    raise RuntimeError("Authentication failed")
except paramiko.NoValidConnectionsError:
    # Network unreachable or connection refused
    raise RuntimeError("Cannot connect to host")
except paramiko.SSHException as e:
    # Other SSH protocol errors
    raise RuntimeError(f"SSH error: {e}")
finally:
    client.close()  # Always close to prevent hangs
```
