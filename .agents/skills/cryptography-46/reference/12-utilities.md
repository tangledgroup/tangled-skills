# Utilities

## Random Number Generation

Always use the OS cryptographic random number generator for security-sensitive values:

```python
import os

iv = os.urandom(16)           # 16 bytes of cryptographically secure randomness
serial = int.from_bytes(os.urandom(16), byteorder="big")  # as integer
```

Do NOT use the `random` module for cryptographic purposes. Also consider the `secrets` module for text-based secrets.

## Constant-Time Comparison

Compare sensitive values in constant time to prevent timing attacks:

```python
from cryptography.hazmat.primitives.constant_time import bytes_eq

bytes_eq(b"secret1", b"secret2")  # False, constant-time
```

## Exceptions

- `UnsupportedAlgorithm` — Requested algorithm or combination not supported by the backend
- `AlreadyFinalized` — Context used after finalize/verify
- `InvalidSignature` — Signature verification failed (HMAC or asymmetric)
- `InvalidTag` — AEAD authentication tag validation failed
- `NotYetFinalized` — AEAD tag accessed before finalize
- `AlreadyUpdated` — Additional data added after update was called
- `InvalidKey` — KDF verify: derived key does not match expected

## Decrepit Algorithms

Deprecated algorithms moved to `cryptography.hazmat.decrepit`:

- `decrepit.ciphers.algorithms.ARC4` — Broken stream cipher
- `decrepit.ciphers.algorithms.TripleDES` — Slow, known flaws
- `decrepit.ciphers.algorithms.Camellia` — Less studied than AES
- `decrepit.modes.ECB` — Electronic Codebook mode (deterministic, insecure)

These will be removed from the main namespace in future versions. Import from `decrepit` if needed for legacy interoperability.

## Padding

```python
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.algorithms import AES

# PKCS7 padding (most common)
padder = padding.PKCS7(AES.block_size).padder()
padded = padder.update(data) + padder.finalize()

unpadder = padding.PKCS7(AES.block_size).unpadder()
data = unpadder.update(padded) + unpadder.finalize()

# ANSI X.923 padding
padder = padding.ANSIX923(AES.block_size).padder()
```

## OpenSSL Backend

The library uses OpenSSL 3.x (or compatible: BoringSSL, LibreSSL, AWS-LC) as its cryptographic backend. Access the backend via:

```python
from cryptography.hazmat.backends.openssl import backend
print(backend.openssl_version_text)
```

## Known Limitations

- **Secure memory wiping**: Not guaranteed — Python's memory management may retain copies of sensitive data
- **RSA PKCS1 v1.5 constant-time decryption**: Not fully constant-time in all OpenSSL versions
