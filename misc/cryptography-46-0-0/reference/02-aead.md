# Authenticated Encryption (AEAD)

AEAD schemes provide both confidentiality and integrity in a single construction. They also support authenticating associated data that is not encrypted.

> **WARNING**: Never reuse a nonce with the same key. Nonce reuse compromises all messages encrypted with that key/nonce pair.

## ChaCha20Poly1305

Stream cipher + MAC defined in RFC 7539. Uses a 32-byte key and 12-byte nonce.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

key = ChaCha20Poly1305.generate_key()  # 32 bytes
chacha = ChaCha20Poly1305(key)
nonce = os.urandom(12)

ct = chacha.encrypt(nonce, b"secret message", b"unencrypted but authenticated")
pt = chacha.decrypt(nonce, ct, b"unencrypted but authenticated")
```

Methods: `encrypt(nonce, data, associated_data)`, `decrypt(nonce, data, associated_data)`.

Since 47.0.0: `encrypt_into()` and `decrypt_into()` write directly to a pre-allocated buffer for zero-copy operations.

## AESGCM

AES in Galois Counter Mode. Supports 128, 192, or 256-bit keys. NIST recommends 96-bit (12-byte) nonces for best performance.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)

ct = aesgcm.encrypt(nonce, b"secret message", b"aad")
pt = aesgcm.decrypt(nonce, ct, b"aad")
```

Only supports 128-bit (16-byte) tags. For tag truncation (not recommended), use the low-level `Cipher` with `GCM` mode instead.

## AESGCMSIV

AES-GCM with a random IV and salt. The caller does not manage nonces — the construction generates them internally using a CTR_DRBG seeded from a 16-byte salt.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

key = AESGCMSIV.generate_key(bit_length=256)
aesgcm_siv = AESGCMSIV(key)
ct = aesgcm_siv.encrypt(b"secret message", b"aad")
pt = aesgcm_siv.decrypt(ct, b"aad")
```

## AESOCB3

AES in OCB mode (RFC 7253). Requires a patent license for commercial use in some jurisdictions.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESOCB3

key = AESOCB3.generate_key(bit_length=256)
nonce = os.urandom(12)
ocb3 = AESOCB3(key)
ct = ocb3.encrypt(nonce, b"secret message", b"aad")
pt = ocb3.decrypt(nonce, ct, b"aad")
```

## AESSIV

AES-SIV (RFC 5297) — deterministic authenticated encryption. Does not take a nonce; the same plaintext always produces the same ciphertext. Useful for disk encryption or format-preserving scenarios.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESSIV

key = AESSIV.generate_key(bit_length=256)  # requires two AES keys
aes_siv = AESSIV(key)
ct = aes_siv.encrypt(b"secret message", b"aad")
pt = aes_siv.decrypt(ct, b"aad")
```

## AESCCM

AES in CCM mode. Similar to GCM but with different tag placement.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESCCM

key = AESCCM.generate_key(bit_length=128)
nonce = os.urandom(11)
aesccm = AESCCM(key)
ct = aesccm.encrypt(nonce, b"secret message", b"aad")
pt = aesccm.decrypt(nonce, ct, b"aad")
```

## Common Patterns

- Generate nonces with `os.urandom(12)` for most AEAD schemes
- `associated_data` can be `None` if not needed
- Output of `encrypt()` is ciphertext with 16-byte tag appended
- `InvalidTag` exception on failed authentication during decrypt
