# Key Derivation Functions

Key derivation functions (KDFs) transform input key material (passwords, secrets, shared keys) into cryptographic keys suitable for specific purposes.

## Password-Based Key Derivation

### PBKDF2HMAC (Wide Compatibility)

PBKDF2 is widely supported but relatively slow. Use with high iteration counts.

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os

# Generate random salt (store with derived key)
salt = os.urandom(16)

# Derive 32-byte key from password
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100_000,  # Minimum recommended
)

key = kdf.derive(b"password")
```

### Verification Pattern

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def hash_password(password: str, iterations: int = 100_000) -> tuple:
    """Hash a password and return (salt, hashed)."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password.encode())
    return salt, key

def verify_password(password: str, salt: bytes, stored_key: bytes) -> bool:
    """Verify a password against stored hash."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    derived = kdf.derive(password.encode())
    return hmac.compare_digest(derived, stored_key)

# Usage
salt, hashed = hash_password("user_password")
is_valid = verify_password("user_password", salt, hashed)  # True
is_invalid = verify_password("wrong_password", salt, hashed)  # False
```

### Iteration Count Guidelines

| Algorithm | Minimum (2024) | Recommended |
|-----------|---------------|-------------|
| PBKDF2-SHA256 | 100,000 | 210,000+ |
| PBKDF2-SHA512 | 100,000 | 210,000+ |

Adjust based on target hardware and acceptable login latency.

### scrypt (Memory-Hard)

scrypt resists GPU/ASIC attacks by requiring significant memory.

```python
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os

salt = os.urandom(16)

kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,      # CPU/memory cost (must be power of 2)
    r=8,          # Block size
    p=1,          # Parallelization
)

key = kdf.derive(b"password")
```

### Parameter Guidelines

- **n:** Memory/CPU cost factor (2^14 to 2^20, must be power of 2)
- **r:** Block size (typically 8-16)
- **p:** Parallelization (typically 1)
- **Memory usage:** approximately `n * r * 128` bytes

### Argon2 (Recommended - Not Built-in)

Argon2 is the current best choice but requires external library:

```bash
pip install argon2-cffi
```

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

# Hash password
hashed = ph.hash("password")

# Verify
try:
    ph.verify(hashed, "password")
    print("Valid")
except VerifyMismatchError:
    print("Invalid")

# Check if needs rehashing (parameters too weak)
if ph.check_needs_rehash(hashed):
    hashed = ph.rehash(hashed)
```

## Key-Based Key Derivation

### HKDF (RFC 5869)

HKDF derives cryptographic keys from existing key material (not passwords).

### Basic Usage

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import os

# Input key material (e.g., from key exchange)
ikm = os.urandom(32)  # In practice, from X25519, ECDH, etc.

# Derive single key
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"application-key",
).derive(ikm)
```

### Parameters

- **algorithm:** Hash function (SHA256, SHA384, SHA512)
- **length:** Output key length in bytes
- **salt:** Random salt (recommended for security, can be None)
- **info:** Context/application-specific string (important for domain separation)

### Multiple Keys from Single Source

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Shared secret from key exchange
shared_secret = b"32-byte-shared-secret-from-x25519-or-similar"

# Derive multiple keys for different purposes
encryption_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"encryption-key-v1",
).derive(shared_secret)

mac_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"mac-key-v1",
).derive(shared_secret)

key_rotation_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"key-rotation-key-v1",
).derive(shared_secret)
```

### Two-Step Derivation (Explicit Extract-Expand)

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExtract, HKDFExpand
from cryptography.hazmat.primitives import hashes

# Step 1: Extract (weak IKM -> strong PRK)
prk = HKDFExtract(
    algorithm=hashes.SHA256(),
    salt=b"random-salt-or-none",
    key_material=weak_secret
)

# Step 2: Expand (PRK -> multiple OKMs)
key1 = HKDFExpand(
    algorithm=hashes.SHA256(),
    length=32,
    info=b"application-key-1"
).derive(prk)

key2 = HKDFExpand(
    algorithm=hashes.SHA256(),
    length=32,
    info=b"application-key-2"
).derive(prk)
```

## Key Stretching

### Simple Key Stretching

Increase key entropy through repeated hashing:

```python
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDF
from cryptography.hazmat.primitives import hashes

# Stretch weak key material
weak_key = b"short-key"

stretched = ConcatKDF(
    algorithm=hashes.SHA256(),
    length=64,  # Output longer key
    other_info=b"",
).derive(weak_key)
```

## TLS-Style Key Derivation

### TKPD (TLS 1.3 Style)

Derive keys following TLS 1.3 pattern:

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def tls_key_schedule(shared_secret: bytes, transcript_hash: bytes) -> dict:
    """Derive TLS-style keys from shared secret."""
    
    # Initial key derivation
    initial = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"tls-1-3",
    ).derive(shared_secret)
    
    # Client write key
    client_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=initial,
        info=b"client write" + transcript_hash,
    ).derive(b"")
    
    # Server write key
    server_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=initial,
        info=b"server write" + transcript_hash,
    ).derive(b"")
    
    return {
        "client_write_key": client_key,
        "server_write_key": server_key,
    }
```

## Best Practices

### Salt Management

1. **Generate random salts:** Use `os.urandom(16)` or more
2. **Store with hash:** Salts don't need to be secret
3. **Unique per password:** Never reuse salts
4. **Adequate length:** 16 bytes minimum, 32 bytes ideal

```python
import os
import base64

# Generate and encode salt for storage
salt = os.urandom(16)
salt_encoded = base64.b64encode(salt).decode()

# Store format: "algorithm$salt$hash"
stored = f"pbkdf2_sha256${salt_encoded}$<hashed_value>"
```

### Parameter Selection

| Use Case | Algorithm | Parameters |
|----------|-----------|------------|
| Password storage (general) | PBKDF2-SHA256 | 210,000+ iterations |
| Password storage (high security) | Argon2id | memory=64MB, time=3, parallelism=4 |
| Password storage (GPU protection) | scrypt | n=2^14, r=8, p=1 |
| Key exchange -> encryption key | HKDF-SHA256 | salt=random, info=context |
| Master key -> multiple keys | HKDF-SHA256 | different info per key |

### Domain Separation

Always use unique `info` parameters when deriving multiple keys:

```python
# GOOD: Clear domain separation
enc_key = HKDF(..., info=b"app-name-v1-encryption").derive(ikm)
mac_key = HKDF(..., info=b"app-name-v1-mac").derive(ikm)

# BAD: Same key for different purposes
bad_key = HKDF(..., info=b"key").derive(ikm)  # Don't do this
```

## Complete Example: Password-Based Encryption

```python
import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet

class PasswordBasedEncryption:
    ITERATIONS = 100_000
    
    def __init__(self):
        pass
    
    def encrypt(self, password: str, plaintext: bytes) -> dict:
        """Encrypt data with password."""
        # Generate salt and nonce
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        key = kdf.derive(password.encode())
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Return package (salt and nonce not secret)
        return {
            "salt": salt.hex(),
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
            "iterations": self.ITERATIONS,
        }
    
    def decrypt(self, password: str, package: dict) -> bytes:
        """Decrypt data with password."""
        # Recover components
        salt = bytes.fromhex(package["salt"])
        nonce = bytes.fromhex(package["nonce"])
        ciphertext = bytes.fromhex(package["ciphertext"])
        
        # Derive same key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=package["iterations"],
        )
        key = kdf.derive(password.encode())
        
        # Decrypt
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext

# Usage
pbe = PasswordBasedEncryption()

# Encrypt
package = pbe.encrypt("my-secret-password", b"Sensitive data")
print(json.dumps(package))

# Decrypt later
data = pbe.decrypt("my-secret-password", package)
print(data)  # b"Sensitive data"
```

## Common Pitfalls

### Don't Use Hashing for Passwords

```python
# WRONG: Plain hashing is not secure for passwords
from cryptography.hazmat.primitives import hashes
password_hash = hashes.Hash.hash(hashes.SHA256(), b"password")  # DON'T DO THIS

# RIGHT: Use key derivation with salt and iterations
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
salt = os.urandom(16)
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000)
password_hash = kdf.derive(b"password")  # DO THIS
```

### Don't Reuse Salts

```python
# WRONG: Same salt for all passwords
GLOBAL_SALT = b"fixed-salt"  # DON'T DO THIS

# RIGHT: Unique salt per password
salt = os.urandom(16)  # DO THIS
```

### Don't Use Low Iteration Counts

```python
# WRONG: Too fast, vulnerable to brute force
kdf = PBKDF2HMAC(..., iterations=1000)  # DON'T DO THIS

# RIGHT: Sufficient iterations
kdf = PBKDF2HMAC(..., iterations=100_000)  # DO THIS
```
