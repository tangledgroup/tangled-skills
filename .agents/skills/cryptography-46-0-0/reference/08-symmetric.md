# Symmetric Encryption (Cipher API)

Low-level symmetric encryption using the `Cipher` class. Combines an algorithm with a mode of operation.

> **WARNING**: Plain symmetric encryption provides secrecy but NOT authenticity. An attacker can create bogus messages and force decryption. In most contexts you should use Fernet or AEAD instead.

## Cipher Class

```python
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)  # 256-bit key
iv = os.urandom(16)   # 128-bit IV

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()

decryptor = cipher.decryptor()
pt = decryptor.update(ct) + decryptor.finalize()
```

## Algorithms

- `AES(key)` — 128, 192, or 256-bit key. Default choice.
- `AES128(key)` / `AES256(key)` — Fixed key length variants (since 38.0.0)
- `ChaCha20(key, nonce)` — Stream cipher, 256-bit key, 128-bit nonce. Use ChaCha20Poly1305 AEAD instead for authenticated encryption.
- `SM4(key)` — Chinese standard block cipher, 128-bit key. Compatibility only.

**Deprecated** (moved to `decrepit` module):
- `TripleDES(key)` — 64/128/192-bit key. Slow and has known flaws.
- `ARC4(key)` — Stream cipher. Broken, do not use.
- `Camellia(key)` — 128/192/256-bit key.

## Modes

- `CBC(iv)` — Cipher Block Chaining. Requires PKCS7 padding. IV must be random and unique.
- `CTR(nonce)` — Counter mode. Stream-like, no padding needed. Nonce must be unique.
- `GCM(nonce, mac_len=128)` — Galois/Counter Mode. Authenticated encryption. Use AESGCM AEAD class instead for simpler API.
- `CFB(segment_size, iv)` — Cipher Feedback. Self-synchronizing stream mode.
- `OFB(iv)` — Output Feedback. Stream mode.
- `CCM(nonce, mac_len=128)` — Counter with CBC-MAC. Authenticated encryption. Use AESCCM AEAD class instead.
- `None` — For stream ciphers like ChaCha20 that don't use a separate mode.

## Padding

For block cipher modes that require padding (CBC, CFB):

```python
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms

padder = padding.PKCS7(algorithms.AES.block_size).padder()
padded_data = padder.update(data) + padder.finalize()

unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
data = unpadder.update(padded_data) + unpadder.finalize()
```

Padding schemes: `PKCS7`, `ANSIX923`.

## Encrypt-then-MAC Pattern

When using non-authenticated modes, combine encryption with HMAC:

1. Encrypt the plaintext
2. Compute HMAC over the ciphertext (not the plaintext)
3. On decrypt, verify HMAC first, then decrypt

This is what Fernet does internally — prefer Fernet for this pattern.
