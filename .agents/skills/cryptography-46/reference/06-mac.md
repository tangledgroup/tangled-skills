# Message Authentication Codes (MACs)

MACs verify both integrity and authenticity of a message using a secret key.

## HMAC

Hash-based MAC per RFC 2104. Combines a hash function with a secret key.

```python
from cryptography.hazmat.primitives import hashes, hmac

key = b"secret-key-at-least-as-long-as-hash-digest"
h = hmac.HMAC(key, hashes.SHA256())
h.update(b"message to authenticate")
signature = h.finalize()  # returns bytes

# Verify
h2 = hmac.HMAC(key, hashes.SHA256())
h2.update(b"message to authenticate")
h2.verify(signature)  # raises InvalidSignature if wrong
```

Key should be randomly generated and equal in length to the hash function's digest size. After `finalize()` or `verify()`, the context is consumed (raises `AlreadyFinalized`). Use `copy()` before finalizing if you need to reuse state.

## CMAC

Cipher-based MAC using a block cipher (typically AES).

```python
from cryptography.hazmat.primitives import cmac, hashes

key = b"32-byte-key-for-aes-256"
c = cmac.CMAC(algorithms.AES(key))
c.update(b"message")
mac_tag = c.finalize()

# Verify
c2 = cmac.CMAC(algorithms.AES(key))
c2.update(b"message")
c2.verify(mac_tag)
```

## Poly1305

Fast one-time authenticator. Typically used as part of ChaCha20-Poly1305 AEAD rather than standalone.

```python
from cryptography.hazmat.primitives.poly1305 import Poly1305

key = os.urandom(32)  # 32-byte key
p = Poly1305(key)
p.update(b"message")
tag = p.finalize()

# Verify
p2 = Poly1305(key)
p2.update(b"message")
p2.verify(tag)
```

Key must be unique per message — never reuse a Poly1305 key.
