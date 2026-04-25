# Hashing and Message Authentication Codes

This reference covers cryptographic hash functions (message digests) and MACs for data integrity verification.

## Hash Functions Overview

Cryptographic hash functions transform arbitrary data into fixed-size digests with these properties:
- **Deterministic:** Same input always produces same output
- **Fast:** Quick to compute
- **Pre-image resistant:** Cannot reverse to find original input
- **Collision resistant:** Hard to find two inputs with same digest

**Warning:** Hash algorithms weaken over time. Plan for algorithm upgrades. See [Lifetimes of cryptographic hash functions](https://valerieaurora.org/hash.html).

## Basic Hashing API

### One-Shot Hashing (Recommended)

```python
from cryptography.hazmat.primitives.hashes import Hash

# Simple one-shot hash
digest = Hash.hash(Hash.SHA256(), b"data to hash")
print(digest.hex())  # Hex-encoded digest
```

### Incremental Hashing

For large data or streaming:

```python
from cryptography.hazmat.primitives import hashes

# Create hash object
digest_obj = hashes.Hash(hashes.SHA256())

# Update in chunks
digest_obj.update(b"part1")
digest_obj.update(b"part2")
digest_obj.update(b"part3")

# Finalize to get digest
result = digest_obj.finalize()
```

### Copy Hash Context

Get intermediate digests while continuing:

```python
from cryptography.hazmat.primitives import hashes

digest_obj = hashes.Hash(hashes.SHA256())
digest_obj.update(b"initial data")

# Get intermediate hash
intermediate = digest_obj.copy().finalize()

# Continue hashing
digest_obj.update(b"more data")
final = digest_obj.finalize()
```

## Available Hash Algorithms

### SHA-2 Family (Recommended)

```python
from cryptography.hazmat.primitives import hashes

# SHA-256 (most common)
h = hashes.Hash(hashes.SHA256())
h.update(b"data")
sha256_digest = h.finalize()  # 32 bytes

# SHA-384
h = hashes.Hash(hashes.SHA384())
digest = h.finalize()  # 48 bytes

# SHA-512
h = hashes.Hash(hashes.SHA512())
digest = h.finalize()  # 64 bytes

# SHA-224 (less common)
h = hashes.Hash(hashes.SHA224())
digest = h.finalize()  # 28 bytes
```

### SHA-3 Family (RFC 7692)

```python
from cryptography.hazmat.primitives import hashes

# SHA3-256
h = hashes.Hash(hashes.SHA3_256())
digest = h.finalize()  # 32 bytes

# SHA3-512
h = hashes.Hash(hashes.SHA3_512())
digest = h.finalize()  # 64 bytes

# SHA3-224, SHA3-384 also available
```

### BLAKE2 (Fast and Secure)

```python
from cryptography.hazmat.primitives import hashes

# BLAKE2b (default, 64-byte digest)
h = hashes.Hash(hashes.BLAKE2b())
digest = h.finalize()  # 64 bytes

# Custom digest size
h = hashes.Hash(hashes.BLAKE2b(digest_size=32))
digest = h.finalize()  # 32 bytes

# With key (functions as MAC)
key = b"secret-key-16-bytes"
h = hashes.Hash(hashes.BLAKE2b(key=key, digest_size=32))
h.update(b"data")
mac = h.finalize()

# BLAKE2s (faster on 32-bit systems)
h = hashes.Hash(hashes.BLAKE2s(digest_size=32))
digest = h.finalize()  # 32 bytes
```

### MD5 and SHA-1 (Deprecated)

**Warning:** MD5 and SHA-1 are cryptographically broken. Only use for:
- Non-security checksums
- Legacy system compatibility
- Hash-based non-cryptographic purposes

```python
from cryptography.hazmat.primitives import hashes

# MD5 (broken, avoid for security)
h = hashes.Hash(hashes.MD5())
digest = h.finalize()  # 16 bytes

# SHA-1 (broken, avoid for security)
h = hashes.Hash(hashes.SHA1())
digest = h.finalize()  # 20 bytes
```

### Extendable Output Functions (XOF)

SHAKE128 and SHAKE256 produce arbitrary-length output:

```python
from cryptography.hazmat.primitives import hashes

# SHAKE128 with 64-byte output
h = hashes.XOFHash(hashes.SHAKE128(digest_size=64))
h.update(b"data")
digest = h.finalize()  # 64 bytes

# Or squeeze incrementally
h = hashes.XOFHash(hashes.SHAKE256(digest_size=32))
h.update(b"data")
part1 = h.squeeze(16)  # First 16 bytes
part2 = h.squeeze(16)  # Next 16 bytes
```

## Message Authentication Codes (MACs)

MACs provide authenticated hashing using a secret key.

### HMAC (Hash-based MAC)

```python
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes

# Create HMAC with SHA-256
key = b"secret-key-at-least-32-bytes"
hmac_obj = hmac.HMAC(key, hashes.SHA256())

# Update and finalize
hmac_obj.update(b"data to authenticate")
signature = hmac_obj.finalize()

# Verify
hmac_obj2 = hmac.HMAC(key, hashes.SHA256())
hmac_obj2.update(b"data to authenticate")

try:
    hmac.compare_digest(signature, hmac_obj2.finalize())
    print("Signature valid")
except ValueError:
    print("Signature invalid")
```

### HMAC One-Shot

```python
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes

key = b"secret-key"
data = b"message"

# Compute and verify in one step
signature = hmac.HMAC(key, hashes.SHA256()).finalize(data)

# Constant-time comparison
if hmac.compare_digest(signature, stored_signature):
    print("Valid")
```

### HMAC with Different Algorithms

```python
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes

key = b"secret-key"

# HMAC-SHA256
sig = hmac.HMAC(key, hashes.SHA256()).update(b"data").finalize()

# HMAC-SHA512
sig = hmac.HMAC(key, hashes.SHA512()).update(b"data").finalize()

# HMAC-BLAKE2b
sig = hmac.HMAC(key, hashes.BLAKE2b()).update(b"data").finalize()
```

## Poly1305 MAC

High-speed MAC often paired with ChaCha20:

```python
from cryptography.hazmat.primitives import poly1305

# Generate random 32-byte key
key = poly1305.Poly1305.generate_key()

# Create MAC
mac = poly1305.Poly1305(key)
mac.update(b"data to authenticate")
tag = mac.finalize()

# Verify
mac2 = poly1305.Poly1305(key)
mac2.update(b"data to authenticate")

try:
    mac2.verify(tag)
    print("Valid")
except ValueError:
    print("Invalid")
```

## Security Considerations

### Timing Attacks

Always use constant-time comparison for MACs and signatures:

```python
import hmac
from cryptography.hazmat.primitives import hashes

# CORRECT: Constant-time comparison
if hmac.compare_digest(computed, stored):
    print("Valid")

# WRONG: Vulnerable to timing attacks
if computed == stored:  # DON'T DO THIS
    print("Valid")
```

### Key Management

- Use cryptographically random keys (os.urandom or generate_key())
- Store keys securely (environment variables, secret managers)
- Use separate keys for different purposes
- Rotate keys periodically

```python
import os

# Generate secure random key
key = os.urandom(32)  # 256-bit key
```

### Algorithm Selection

| Use Case | Recommended Algorithm |
|----------|----------------------|
| General hashing | SHA-256 |
| High security | SHA-384 or SHA-512 |
| Performance-critical | BLAKE2b |
| MAC with hash | HMAC-SHA256 |
| MAC with ChaCha20 | Poly1305 |
| Variable output | SHAKE128/256 |

## Common Patterns

### Password Hashing (Not for Passwords!)

**Important:** Do NOT use these hashes directly for passwords. Use dedicated password hashing:

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# See Key Derivation reference for proper password handling
```

### Data Integrity Checksum

```python
from cryptography.hazmat.primitives import hashes

def compute_checksum(data: bytes) -> str:
    """Compute SHA-256 checksum of data."""
    return hashes.Hash.hash(hashes.SHA256(), data).hex()

def verify_checksum(data: bytes, expected: str) -> bool:
    """Verify data matches expected checksum."""
    actual = compute_checksum(data)
    return hmac.compare_digest(actual.encode(), expected.encode())
```

### File Hashing

```python
from cryptography.hazmat.primitives import hashes

def hash_file(filepath: str, chunk_size: int = 65536) -> bytes:
    """Hash a file incrementally."""
    digest = hashes.Hash(hashes.SHA256())
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    
    return digest.finalize()

# Usage
file_hash = hash_file("large_file.bin")
print(f"SHA-256: {file_hash.hex()}")
```

### Merkle Tree (Data Structure Integrity)

```python
from cryptography.hazmat.primitives import hashes

def merkle_root(leaves: list) -> bytes:
    """Compute Merkle root from list of data leaves."""
    if not leaves:
        return hashes.Hash.hash(hashes.SHA256(), b"")
    
    # Hash all leaves
    hashed = [hashes.Hash.hash(hashes.SHA256(), leaf) for leaf in leaves]
    
    # Build tree
    while len(hashed) > 1:
        if len(hashed) % 2 == 1:
            hashed.append(hashed[-1])  # Duplicate last if odd
        
        hashed = [
            hashes.Hash.hash(
                hashes.SHA256(),
                hashed[i] + hashed[i+1]
            )
            for i in range(0, len(hashed), 2)
        ]
    
    return hashed[0]

# Usage
data = [b"transaction1", b"transaction2", b"transaction3"]
root = merkle_root(data)
print(f"Merkle root: {root.hex()}")
```
