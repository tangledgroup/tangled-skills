# Key Derivation Functions (KDFs)

KDFs derive cryptographic keys from passwords or other input material. Different KDFs suit different tasks.

## Variable-Cost Algorithms

These allow tuning computational cost to resist brute-force attacks.

### Argon2 Family (Recommended for Password Storage)

Defined in RFC 9106. Three variants:

- `Argon2id` — Blend of Argon2d and Argon2i. **Recommended default** per RFC 9106.
- `Argon2d` — Maximizes resistance to time-memory-trade-off attacks, but has side-channel risks. Available with OpenSSL 3.2.0+ (since 47.0.0).
- `Argon2i` — Resists side-channel attacks, but vulnerable to time-memory-trade-off. Available with OpenSSL 3.2.0+ (since 47.0.0).

```python
import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

salt = os.urandom(16)
kdf = Argon2id(
    salt=salt,
    length=32,
    iterations=1,
    lanes=4,
    memory_cost=64 * 1024,  # kibibytes
)
key = kdf.derive(b"my password")

# Verify
kdf.verify(b"my password", key)
```

Parameters: `salt` (16+ bytes recommended), `length` (output bytes), `iterations` (passes), `lanes` (parallelism), `memory_cost` (KiB, minimum 8 * lanes).

RFC 9106 parameter recommendations:
- General applications: `iterations=1, memory_cost=2**21`
- Memory-constrained: `iterations=3, memory_cost=2**16`

**PHC-encoded format** (since 45.0.0):

```python
encoded = kdf.derive_phc_encoded(b"password")
# Returns: $argon2id$v=19$m=65536,t=1,p=4$<salt>$<key>

Argon2id.verify_phc_encoded(b"password", encoded)
```

**derive_into()** (since 47.0.0): Writes directly to a pre-allocated buffer.

```python
output = bytearray(32)
kdf.derive_into(b"my password", output)
```

### PBKDF2-HMAC

```python
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=1_200_000,
)
key = kdf.derive(b"my password")
kdf.verify(b"my password", key)
```

Good for key derivation from passwords. Better alternatives exist for password storage (Argon2, scrypt).

### Scrypt

```python
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

salt = os.urandom(16)
kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
key = kdf.derive(b"my password")
kdf.verify(b"my password", key)
```

Memory-hard KDF. Parameters: `n` (CPU/memory cost, power of 2), `r` (block size), `p` (parallelism).

### HKDF

Extract-then-expand key derivation from RFC 5869. Used to derive multiple keys from a single input keying material.

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b"random-salt",
    info=b"application context",
).derive(b"input keying material")
```

Parameters: `algorithm` (hash), `length`, `salt` (optional, recommended 32 bytes for SHA-256), `info` (context/application-specific string).

**HKDF.extract()** (since 47.0.0): Extract step is now publicly accessible.

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"salt", info=b"info")
okm = hkdf.extract(b"input keying material")  # returns extracted key
```

**derive_into()** (since 47.0.0):

```python
output = bytearray(32)
hkdf.derive_into(b"input keying material", output)
```

## Fixed-Cost Algorithms

### PBKDF2 (without HMAC) / TLS KDF / HKDFExpand / KBKDF

These have fixed computational cost and are not suitable for password hashing. They are used for key derivation from already-high-entropy material.

## Common Interface

All KDFs implement:
- `derive(key_material: bytes) -> bytes` — Derive a key
- `verify(key_material: bytes, expected_key: bytes)` — Verify by deriving and comparing (constant-time)
- Can only be used once (raises `AlreadyFinalized` on reuse)

**Since 47.0.0**, the following KDFs also support `derive_into(key_material, buffer)` for in-place derivation:
- `HKDF`, `HKDFExpand`
- `ConcatKDFHash`, `ConcatKDFHMAC`
- `Argon2id`
- `PBKDF2HMAC`
- `KBKDFHMAC`, `KBKDFCMAC`
- `Scrypt`
- `X963KDF`
