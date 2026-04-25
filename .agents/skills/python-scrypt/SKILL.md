---
name: python-scrypt
description: Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, deriving encryption keys from passwords, or verifying passwords with memory-hard key derivation functions resistant to hardware-assisted attacks.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - cryptography
  - key-derivation
  - password-hashing
  - scrypt
  - kdf
  - security
category: security
required_environment_variables: []
---

# Scrypt


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, deriving encryption keys from passwords, or verifying passwords with memory-hard key derivation functions resistant to hardware-assisted attacks.

Python toolkit for scrypt-based key derivation functions (KDF) using both the standard library `hashlib.scrypt` and the `cryptography` library's `Scrypt` class. Scrypt is a memory-hard KDF designed by Colin Percival to be resistant against hardware-assisted attackers (GPU/ASIC) by having tunable memory cost, as specified in [RFC 7914](https://datatracker.ietf.org/doc/html/rfc7914).

## When to Use

- Deriving encryption keys from passwords for disk encryption or file encryption
- Storing password hashes with resistance to brute-force and hardware attacks
- Implementing authentication systems requiring memory-hard key derivation
- Generating cryptographic keys from low-entropy input (passwords, passphrases)
- Migrating from weaker KDFs like PBKDF2 to more secure alternatives

## Setup

### Standard Library (Python 3.6+)

No installation required - `hashlib.scrypt` is built into Python 3.6+:

```python
import hashlib
import os
```

### Cryptography Library

For advanced features like constant-time verification:

```bash
pip install cryptography
```

```python
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
```

## Usage

### Basic Key Derivation with hashlib

Derive a 32-byte key from a password:

```python
import hashlib
import os

# Generate a random salt (16+ bytes recommended)
salt = os.urandom(16)

# Derive key using scrypt
key = hashlib.scrypt(
    password=b"my secure password",
    salt=salt,
    n=2**14,      # CPU/memory cost factor (must be power of 2)
    r=8,          # Block size parameter
    p=1,          # Parallelization factor
    dklen=32      # Derived key length in bytes
)

print(f"Derived key: {key.hex()}")
```

### Password Hashing and Verification with hashlib

Store password hash for later verification:

```python
import hashlib
import os
import json

def hash_password(password: str) -> dict:
    """Hash a password and return parameters for storage."""
    salt = os.urandom(16)
    key = hashlib.scrypt(
        password=password.encode('utf-8'),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
    
    # Store parameters needed for verification
    return {
        'salt': salt.hex(),
        'key': key.hex(),
        'n': 2**14,
        'r': 8,
        'p': 1,
        'dklen': 32
    }

def verify_password(password: str, stored: dict) -> bool:
    """Verify a password against stored hash."""
    key = hashlib.scrypt(
        password=password.encode('utf-8'),
        salt=bytes.fromhex(stored['salt']),
        n=stored['n'],
        r=stored['r'],
        p=stored['p'],
        dklen=stored['dklen']
    )
    
    # Use constant-time comparison to prevent timing attacks
    import hmac
    return hmac.compare_digest(key, bytes.fromhex(stored['key']))

# Usage
password_hash = hash_password("user_secret_password")
print(f"Store this: {password_hash}")

# Later, verify
is_valid = verify_password("user_secret_password", password_hash)
print(f"Password valid: {is_valid}")  # True

is_invalid = verify_password("wrong_password", password_hash)
print(f"Wrong password valid: {is_invalid}")  # False
```

### Using Cryptography Library with Verification

The `cryptography` library provides a `verify()` method for constant-time comparison:

```python
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# Generate salt and derive key
salt = os.urandom(16)
kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,
    r=8,
    p=1
)
key = kdf.derive(b"my great password")

# Verify password (constant-time comparison built-in)
kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,
    r=8,
    p=1
)

try:
    kdf.verify(b"my great password", key)
    print("Password verified successfully")
except Exception as e:
    print(f"Password verification failed: {e}")
```

### Deriving Multiple Keys

Derive multiple keys from a single password for different purposes:

```python
import hashlib
import os

salt = os.urandom(16)

# Derive 96 bytes and split into three 32-byte keys
long_key = hashlib.scrypt(
    password=b"master password",
    salt=salt,
    n=2**14,
    r=8,
    p=1,
    dklen=96
)

encryption_key = long_key[0:32]
hmac_key = long_key[32:64]
authentication_key = long_key[64:96]

print(f"Encryption key: {encryption_key.hex()}")
print(f"HMAC key: {hmac_key.hex()}")
print(f"Auth key: {authentication_key.hex()}")
```

### Deriving Keys with Context/Domain Separation

Use different salts or domain separators for different purposes:

```python
import hashlib
import os

base_salt = os.urandom(16)

# Domain separation using salt prefix
def derive_key_with_domain(password: bytes, domain: str, base_salt: bytes):
    """Derive a key with domain separation to prevent key reuse."""
    domain_salt = domain.encode('utf-8')[:16].ljust(16, b'\x00') + base_salt
    
    return hashlib.scrypt(
        password=password,
        salt=domain_salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )

# Derive separate keys for different purposes
db_key = derive_key_with_domain(b"password", "database", base_salt)
api_key = derive_key_with_domain(b"password", "api_token", base_salt)
file_key = derive_key_with_domain(b"password", "file_encryption", base_salt)

print(f"DB key: {db_key.hex()}")
print(f"API key: {api_key.hex()}")
print(f"File key: {file_key.hex()}")
```

### Memory-Constrained Environments

Use `maxmem` parameter to limit memory usage (hashlib only):

```python
import hashlib
import os

salt = os.urandom(16)

# Limit memory to 16 MiB
key = hashlib.scrypt(
    password=b"password",
    salt=salt,
    n=2**14,
    r=8,
    p=1,
    dklen=32,
    maxmem=16 * 1024 * 1024  # 16 MiB limit
)
```

### Using derive_into() for Memory Efficiency

The `cryptography` library supports writing directly into a pre-allocated buffer:

```python
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os

salt = os.urandom(16)
kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,
    r=8,
    p=1
)

# Pre-allocate buffer
buffer = bytearray(32)

# Write derived key directly into buffer
bytes_written = kdf.derive_into(b"password", buffer)
print(f"Wrote {bytes_written} bytes to buffer")
print(f"Key: {bytes(buffer).hex()}")
```


## See Also

- [Advanced Usage](references/01-advanced-usage.md) - Parameter selection, error handling, and advanced patterns

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
