# Symmetric Encryption (Cipher API)

The low-level `Cipher` class provides fine-grained control over symmetric encryption. Prefer the AEAD APIs when possible — this module is in the "hazardous materials" layer.

## Cipher Class

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = b"32-byte-key-here-"
iv = b"16-byte iv here!"

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ct = encryptor.update(b"data") + encryptor.finalize()

decryptor = cipher.decryptor()
pt = decryptor.update(ct) + decryptor.finalize()
```

## Supported Algorithms

- **AES** — Advanced Encryption Standard. Key sizes: 128, 192, 256 bits. The most widely used symmetric cipher.
- **ChaCha20** — Stream cipher, often paired with Poly1305 for AEAD. Use via the AEAD API.
- **SM4** — Chinese standard block cipher (GB/T 32907). Available for compatibility.

## Supported Modes

### Authenticated (Recommended)

- **GCM** — Galois/Counter Mode. Provides both encryption and authentication. Preferred for AES.
- **CCM** — Counter with CBC-MAC. Alternative authenticated mode for AES.

### Unauthenticated (Use With Caution)

- **CBC** — Cipher Block Chaining. Vulnerable to padding oracle attacks without separate MAC.
- **CTR** — Counter Mode. Turns a block cipher into a stream cipher. No authentication.
- **CFB** — Cipher Feedback. Moved to `decrepit` module in 47.0.0 (removed from `modes` in 49.0.0).
- **OFB** — Output Feedback. Moved to `decrepit` module in 47.0.0 (removed from `modes` in 49.0.0).
- **CFB8** — 8-bit Cipher Feedback. Moved to `decrepit` module in 47.0.0 (removed from `modes` in 49.0.0).

## Decrepit Algorithms and Modes (since 47.0.0)

The following have been moved to `cryptography.hazmat.decrepit` and deprecated in their original modules:

- `CFB`, `OFB`, `CFB8` modes — from `modes` module
- `Camellia` cipher — from `algorithms` module
- `TripleDES` (with 64/128-bit keys deprecated) — from `algorithms` module
- `ARC4` (RC4) — from `algorithms` module

Import from decrepit if you must use them:

```python
from cryptography.hazmat.decrepit.ciphers.modes import CFB
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES, Camellia
```

## CipherContext Methods

- `update(data)` — Encrypt/decrypt data in chunks
- `finalize()` — Finalize and return remaining bytes (consumes the context)
- `reset_nonce(nonce)` — Alter the nonce without reinitializing (since 43.0.0)

## Best Practices

- Prefer AEAD modes (GCM, CCM, ChaCha20-Poly1305) over unauthenticated modes
- Never reuse an IV/nonce with the same key
- Use AES-GCM for most applications
- Use ChaCha20-Poly1305 when hardware AES acceleration is unavailable
