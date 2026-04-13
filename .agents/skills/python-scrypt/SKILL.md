---
name: python-scrypt
description: Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, deriving encryption keys from passwords, or verifying passwords with memory-hard key derivation functions resistant to hardware-assisted attacks.
version: "0.2.0"
author: Your Name <email@example.com>
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

## Parameter Selection

### Understanding Scrypt Parameters

| Parameter | Description | Impact | Recommended Values |
|-----------|-------------|--------|-------------------|
| `n` | CPU/memory cost factor (must be power of 2) | Controls iterations and memory usage | 2^14 (interactive), 2^20 (sensitive files) |
| `r` | Block size parameter | Affects memory cost | 8 (RFC 7914 default) |
| `p` | Parallelization factor | Increases CPU cost without affecting memory | 1 (RFC 7914 default) |
| `dklen`/`length` | Derived key length in bytes | Output size | 32 (256-bit), 64 (512-bit) |

### Memory Usage Calculation

Approximate memory usage: `n * r * 128` bytes

```python
def calculate_memory_usage(n: int, r: int) -> str:
    """Calculate approximate memory usage in human-readable format."""
    memory_bytes = n * r * 128
    
    if memory_bytes >= 1024**3:
        return f"{memory_bytes / (1024**3):.2f} GiB"
    elif memory_bytes >= 1024**2:
        return f"{memory_bytes / (1024**2):.2f} MiB"
    elif memory_bytes >= 1024:
        return f"{memory_bytes / 1024:.2f} KiB"
    else:
        return f"{memory_bytes} bytes"

# Examples
print(f"n=2^14, r=8: {calculate_memory_usage(2**14, 8)}")     # ~128 MiB
print(f"n=2^17, r=8: {calculate_memory_usage(2**17, 8)}")     # ~1 GiB
print(f"n=2^20, r=8: {calculate_memory_usage(2**20, 8)}")     # ~8 GiB
```

### Recommended Parameter Sets

| Use Case | n | r | p | Expected Time | Memory |
|----------|---|---|---|---------------|--------|
| Interactive login | 2^14 | 8 | 1 | < 100ms | ~128 MiB |
| Account registration | 2^16 | 8 | 1 | ~1s | ~512 MiB |
| Sensitive file encryption | 2^20 | 8 | 1 | < 5s | ~8 GiB |
| High-security storage | 2^22 | 8 | 1 | ~10s | ~32 GiB |

### Tuning Parameters for Your System

Measure performance and adjust accordingly:

```python
import hashlib
import os
import time

def benchmark_scrypt(n: int, r: int, p: int, iterations: int = 5) -> float:
    """Benchmark scrypt performance and return average time in seconds."""
    salt = os.urandom(16)
    times = []
    
    for _ in range(iterations):
        start = time.time()
        hashlib.scrypt(
            password=b"benchmark password",
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=32
        )
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    return avg_time

# Test different parameter sets
print("Benchmarking scrypt parameters:")
for n in [2**10, 2**12, 2**14, 2**16]:
    avg_time = benchmark_scrypt(n=n, r=8, p=1)
    memory = calculate_memory_usage(n, 8)
    print(f"n={n}, r=8, p=1: {avg_time:.3f}s, Memory: {memory}")
```

## Error Handling

### Common Errors and Solutions

```python
import hashlib
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# 1. n must be a power of 2
try:
    hashlib.scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=100,  # Not a power of 2!
        r=8,
        p=1,
        dklen=32
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use n=2^14, 2^16, etc.

# 2. n must be >= 2
try:
    hashlib.scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=1,  # Too small!
        r=8,
        p=1,
        dklen=32
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use n >= 2

# 3. r and p must be >= 1
try:
    kdf = Scrypt(
        salt=os.urandom(16),
        length=32,
        n=2**14,
        r=0,  # Too small!
        p=1
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use r >= 1, p >= 1

# 4. Salt must be bytes
try:
    hashlib.scrypt(
        password=b"password",
        salt="not bytes",  # String instead of bytes!
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
except TypeError as e:
    print(f"TypeError: {e}")
    # Solution: Use salt=b"..." or os.urandom(16)

# 5. Password must be bytes
try:
    hashlib.scrypt(
        password="password",  # String instead of bytes!
        salt=os.urandom(16),
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
except TypeError as e:
    print(f"TypeError: {e}")
    # Solution: Use password.encode('utf-8') or b"password"

# 6. Buffer size mismatch in derive_into()
try:
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    buffer = bytearray(16)  # Wrong size!
    kdf.derive_into(b"password", buffer)
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Buffer must match length parameter

# 7. Already finalized (calling derive/verify multiple times)
try:
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key1 = kdf.derive(b"password")
    key2 = kdf.derive(b"password")  # Already used!
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    # Solution: Create new Scrypt instance for each derivation
```

### Memory Limit Exceeded

Handle cases where parameters exceed available memory:

```python
import hashlib
import os

def safe_scrypt(password: bytes, salt: bytes, n: int, r: int, p: int, 
                dklen: int, max_memory_mb: int = 512) -> bytes:
    """Derive key with memory limit protection."""
    estimated_memory_mb = (n * r * 128) / (1024 * 1024)
    
    if estimated_memory_mb > max_memory_mb:
        raise MemoryError(
            f"Parameters would use ~{estimated_memory_mb:.1f} MiB, "
            f"exceeds limit of {max_memory_mb} MiB"
        )
    
    maxmem_bytes = max_memory_mb * 1024 * 1024
    return hashlib.scrypt(
        password=password,
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen,
        maxmem=maxmem_bytes
    )

# Usage with memory protection
try:
    key = safe_scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=2**20,  # Would use ~8 GiB
        r=8,
        p=1,
        dklen=32,
        max_memory_mb=512  # Limit to 512 MiB
    )
except MemoryError as e:
    print(f"Memory limit exceeded: {e}")
    # Fallback to lower parameters
    key = safe_scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=2**14,  # Uses ~128 MiB
        r=8,
        p=1,
        dklen=32,
        max_memory_mb=512
    )
```

## Troubleshooting

### Password Verification Fails

**Problem:** Password verification returns False even with correct password.

**Causes:**
- Salt was not stored or regenerated incorrectly
- Parameters (n, r, p, dklen) don't match original values
- Password encoding mismatch (UTF-8 vs Latin-1)

**Solution:** Always store salt and parameters with the hash:

```python
import json

# Store all necessary data
hash_data = {
    'salt': salt.hex(),
    'key': derived_key.hex(),
    'params': {'n': 2**14, 'r': 8, 'p': 1, 'dklen': 32}
}
storage_string = json.dumps(hash_data)

# Retrieve and verify
stored = json.loads(storage_string)
salt = bytes.fromhex(stored['salt'])
params = stored['params']
```

### Slow Performance

**Problem:** Key derivation takes too long.

**Solution:** Reduce `n` parameter (must remain power of 2):

```python
# Fast but less secure (for testing only)
key = hashlib.scrypt(password=b"pwd", salt=salt, n=2**10, r=8, p=1, dklen=32)

# Production: use n >= 2**14 for interactive, higher for sensitive data
```

### High Memory Usage

**Problem:** Application runs out of memory.

**Solution:** Calculate memory requirements and adjust parameters:

```python
# Check memory before deriving
n, r = 2**14, 8
memory_mb = (n * r * 128) / (1024 * 1024)
print(f"Will use approximately {memory_mb:.1f} MiB")

# Reduce if needed: n=2**12, r=4 uses less memory
```

### OpenSSL Version Issues with cryptography Library

**Problem:** `UnsupportedAlgorithm` exception when using `cryptography`.

**Cause:** Scrypt requires OpenSSL 1.1.0+.

**Solution:** Upgrade OpenSSL or use `hashlib.scrypt` instead:

```python
# Fallback to hashlib if cryptography doesn't support scrypt
try:
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    use_cryptography = True
except Exception:
    use_cryptography = False

if use_cryptography:
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(b"password")
else:
    key = hashlib.scrypt(password=b"password", salt=salt, n=2**14, r=8, p=1, dklen=32)
```

## Security Best Practices

1. **Always use random salts:** Generate with `os.urandom(16)` or more bytes
2. **Store salts with hashes:** Salts are not secrets and must be stored for verification
3. **Use constant-time comparison:** Prevent timing attacks with `hmac.compare_digest()` or `cryptography`'s `verify()`
4. **Limit password length:** Reject passwords > 1024 bytes to prevent DoS
5. **Choose appropriate parameters:** Higher `n` for sensitive data, tune for your system
6. **Keep parameters consistent:** Store n, r, p values and use same values for verification
7. **Use domain separation:** Different salts/prefixes for different key purposes

## Comparison with Other KDFs

| KDF | Memory-Hard | Hardware-Resistant | Python Support | Best For |
|-----|-------------|-------------------|----------------|----------|
| scrypt | Yes | Yes | hashlib, cryptography | Password storage, encryption keys |
| PBKDF2 | No | Partial | hashlib | Legacy systems, FIPS compliance |
| Argon2 | Yes | Yes | argon2-cffi | Modern password hashing (recommended) |
| bcrypt | Limited | Partial | bcrypt | Password hashing (simpler alternative) |

For new applications, consider Argon2id (winner of Password Hashing Competition) as it provides similar security with better parameters. Use scrypt when:
- Argon2 is not available in your environment
- Interoperability with existing scrypt systems
- Specific regulatory or compliance requirements
