# Keys & Authentication

## Key Types

Paramiko supports the following key types through `PKey` subclasses:

- **RSA** (`paramiko.rsakey.RSAKey`) — `ssh-rsa`, most widely supported
- **DSA** (`paramiko.dsskey.DSSKey`) — `ssh-dss`, legacy, limited to 1024 bits
- **ECDSA** (`paramiko.ecdsakey.ECDSAKey`) — `ecdsa-sha2-nistp256/384/521`
- **Ed25519** (`paramiko.ed25519key.Ed25519Key`) — `ssh-ed25519`, modern, recommended

## Loading Keys

### From File

```python
import paramiko

# Auto-detect key type from file
key = paramiko.PKey.from_path("/home/user/.ssh/id_ed25519")

# Or use the generic factory
key = paramiko.PKey.from_private_key_file("/home/user/.ssh/id_rsa", password="passphrase")

# From a file-like object
with open("/home/user/.ssh/id_rsa") as f:
    key = paramiko.RSAKey.from_private_key(f, password="passphrase")

# Specific key type
rsa_key = paramiko.RSAKey.from_private_key_file("/path/to/key")
ed25519_key = paramiko.Ed25519Key.from_private_key_file("/path/to/key")
```

### From Raw Bytes

```python
key = paramiko.PKey.from_type_string("ssh-ed25519", raw_public_bytes)
```

## Key Properties and Methods

```python
# Key name (SSH protocol identifier)
name = key.get_name()  # e.g., "ssh-rsa", "ssh-ed25519"

# Algorithm name
algo = key.algorithm_name  # e.g., "rsa", "ed25519"

# Bit strength
bits = key.get_bits()

# Fingerprint (SHA256, OpenSSH-compatible)
fp = key.fingerprint  # bytes, new in 3.2

# MD5 fingerprint (legacy)
md5_fp = key.get_fingerprint()  # 16 bytes binary

# Base64 public key
b64 = key.get_base64()

# Check if key has private part
has_private = key.can_sign()
```

## Key Generation

```python
rsa_key = paramiko.RSAKey.generate(4096)
ed25519_key = paramiko.Ed25519Key.generate()
ecdsa_key = paramiko.ECDSAKey.generate(bits=256)
dss_key = paramiko.DSSKey.generate(bits=1024)
```

## Writing Keys

```python
# Write private key to file (optionally encrypted)
key.write_private_key_file("/path/to/new_key", password="passphrase")

# Write to file-like object
with open("/path/to/key", "wb") as f:
    key.write_private_key(f, password=None)
```

## OpenSSH Certificates

Load a certificate onto a private key for certificate-based authentication:

```python
key = paramiko.Ed25519Key.from_path("~/.ssh/id_ed25519")
key.load_certificate("~/.ssh/id_ed25519-cert.pub")
```

When connecting, Paramiko will offer the certificate alongside the public key.

## SSH Agent

The `Agent` class connects to a local SSH agent and retrieves keys for authentication:

```python
import paramiko

agent = paramiko.Agent()
keys = agent.get_keys()  # tuple of AgentKey objects

for key in keys:
    print(key.get_name(), key.comment)

# Use an agent key directly
client.connect("hostname", username="user", pkey=keys[0])

# Always close the agent connection
agent.close()
```

`AgentKey` supports all standard `PKey` operations including signing, fingerprinting, and certificate loading.

## Host Keys

### Loading Known Hosts

```python
client = paramiko.SSHClient()

# Load system known_hosts (~/.ssh/known_hosts)
client.load_system_host_keys()

# Load custom host keys file
client.load_host_keys("/path/to/custom_known_hosts")

# Access the HostKeys object
host_keys = client.get_host_keys()
```

### HostKeys API

```python
from paramiko.hostkeys import HostKeys

hk = HostKeys()
hk.load("~/.ssh/known_hosts")

# Lookup keys for a hostname
keys = hk.lookup("example.com")  # dict of key_type -> PKey, or None

# Check if a specific key matches
is_match = hk.check("example.com", server_key)

# Add a host key entry
hk.add("newhost.com", "ssh-ed25519", key)

# Save to file
hk.save("~/.ssh/known_hosts")
```

### Missing Host Key Policies

```python
from paramiko.client import (
    RejectPolicy,   # default — reject unknown keys
    AutoAddPolicy,  # auto-accept and save
    WarningPolicy,  # log warning but accept
)

client.set_missing_host_key_policy(AutoAddPolicy())

# Custom policy
class MyPolicy(paramiko.client.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        fingerprint = key.fingerprint
        if input(f"Accept key {fingerprint} for {hostname}? ") == "yes":
            client.get_host_keys().add(hostname, key.get_name(), key)
        else:
            raise paramiko.SSHException("Host key rejected")
```

## Authentication with SSHClient.connect()

Authentication order of priority:

1. `pkey` or `key_filename` parameter (if provided)
2. Keys from SSH agent (if `allow_agent=True`)
3. Discoverable keys in `~/.ssh/` (`id_rsa`, `id_ecdsa`, `id_ed25519`) if `look_for_keys=True`
4. Password auth (if `password` given)

```python
client.connect(
    "hostname",
    port=22,
    username="user",
    password="secret",          # for password auth and key decryption
    passphrase="key_pass",      # specifically for key decryption
    key_filename=["~/.ssh/id_ed25519"],
    pkey=my_key,                # pre-loaded PKey
    timeout=10,                 # TCP connect timeout
    allow_agent=True,           # use SSH agent
    look_for_keys=True,         # search ~/.ssh/
    compress=False,             # enable compression
)
```

### Transport-Level Authentication

For fine-grained control:

```python
transport = client.get_transport()

# Password auth
transport.auth_password(username="user", password="secret")

# Public key auth
transport.auth_publickey(username="user", key=my_pkey)

# None auth (to discover supported methods)
try:
    transport.auth_none(username="user")
except paramiko.BadAuthenticationType as e:
    print(f"Server allows: {e.types}")
```

## AuthStrategy (New Authentication Mechanism)

Paramiko 3.2+ introduced `AuthStrategy` for pluggable authentication:

```python
from paramiko.auth_strategy import AuthStrategy, PasswordAuth, PublicKeyAuth

strategy = AuthStrategy()
strategy.add(PasswordAuth(username="user", password="secret"))
strategy.add(PublicKeyAuth(username="user", key=my_pkey))

client.connect("hostname", auth_strategy=strategy)
```

Note: `auth_strategy` is incompatible with legacy auth parameters (`password`, `key_filename`, `allow_agent`).
