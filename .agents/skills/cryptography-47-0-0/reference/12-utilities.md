# Utilities

Helper functions and constants for cryptographic operations.

## Random Number Generation

Use `os.urandom()` or the `secrets` module for cryptographic randomness:

```python
import os, secrets

random_bytes = os.urandom(32)       # 32 random bytes
random_token = secrets.token_hex(32)  # hex-encoded token
```

Never use the `random` module for security-sensitive values.

## Constant-Time Comparison

Prevent timing attacks when comparing sensitive values:

```python
from cryptography.utils import int_cmp, fixed_unordered_compare

# Compare integers in constant time
result = int_cmp(a, b)  # returns True if equal

# Compare byte strings in constant time
result = fixed_unordered_compare(a, b)  # returns 0 if equal
```

## Exceptions

Key exceptions:

- `UnsupportedAlgorithm` — Raised when loading keys with unsupported algorithms or explicit curve encodings (since 47.0.0, replaces `ValueError` for this case)
- `AlreadyFinalized` — Raised when reusing a finalized hash/KDF/cipher context
- `InvalidTag` — Raised when AEAD authentication fails during decryption
- `InternalError` — Internal OpenSSL errors

## Padding

PKCS7 padding for block ciphers:

```python
from cryptography.hazmat.primitives.padding import PKCS7

padder = PKCS7(128).padder()
padded = padder.update(b"data") + padder.finalize()

unpadder = PKCS7(128).unpadder()
unpadded = unpadder.update(padded) + unpadder.finalize()
```

## Decrepit Module

The `cryptography.hazmat.decrepit` module contains outdated and insecure primitives that are still available for backwards compatibility but should not be used in new code:

- **Ciphers**: `TripleDES`, `ARC4` (RC4), `Camellia` (moved to decrepit in 47.0.0)
- **Modes**: `CFB`, `OFB`, `CFB8` (moved to decrepit in 47.0.0)
- **Legacy ciphers**: `CAST5`, `SEED`, `IDEA`, `Blowfish`

## Environment Variables

- `CRYPTOGRAPHY_OPENSSL_NO_LEGACY` — Disables the OpenSSL legacy provider at runtime
- `CRYPTOGRAPHY_BUILD_OPENSSL_NO_LEGACY` — Prevents loading the legacy provider during build time
