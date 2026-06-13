# Fernet (Symmetric Encryption)

Fernet is the recommended high-level recipe for symmetric authenticated encryption. It guarantees that encrypted messages cannot be manipulated or read without the key. Built on AES-CBC with HMAC-SHA256 authentication.

## Fernet Class

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # URL-safe base64-encoded 32-byte key
f = Fernet(key)
token = f.encrypt(b"secret message")
plaintext = f.decrypt(token)
```

### Methods

- `Fernet.generate_key()` — Generates a fresh 32-byte key. Keep it safe; losing it means permanent data loss.
- `f.encrypt(data: bytes) -> bytes` — Encrypts data into a Fernet token (URL-safe base64). Note: the token contains a plaintext timestamp.
- `f.decrypt(token: bytes | str, ttl: int | None = None) -> bytes` — Decrypts a token. Optional `ttl` rejects tokens older than N seconds.
- `f.encrypt_at_time(data, current_time)` — Encrypt with explicit timestamp (for testing expiration).
- `f.decrypt_at_time(token, ttl, current_time)` — Decrypt with explicit current time.
- `f.extract_timestamp(token) -> int` — Returns the Unix timestamp embedded in a token without decrypting.

### MultiFernet (Key Rotation)

Supports encrypting with one key while being able to decrypt tokens from multiple keys:

```python
from cryptography.fernet import Fernet, MultiFernet

key1 = Fernet(Fernet.generate_key())
key2 = Fernet(Fernet.generate_key())
f = MultiFernet([key1, key2])  # encrypts with first key, tries all for decrypt

token = f.encrypt(b"Secret message!")
plaintext = f.decrypt(token)

# Rotate a token to the primary key
rotated = f.rotate(token)
```

`MultiFernet.rotate(msg)` re-encrypts a token under the primary (first) key while preserving the original timestamp.

### Using Passwords with Fernet

Derive a Fernet key from a password using Argon2id:

```python
import base64, os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

password = b"password"
salt = os.urandom(16)
kdf = Argon2id(salt=salt, length=32, iterations=1, lanes=4, memory_cost=2**21)
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)
```

Store the salt alongside encrypted data to re-derive the key later. RFC 9106 recommends `iterations=1, memory_cost=2**21` for general apps or `iterations=3, memory_cost=2**16` for memory-constrained environments.

### Implementation Details

- AES in CBC mode with a 128-bit key for encryption (PKCS7 padding)
- HMAC-SHA256 for authentication with the other 128-bit half of the key
- IVs generated via `os.urandom()`
- See [Fernet specification](https://github.com/fernet/spec/blob/master/Spec.md)

### Limitations

Fernet loads the entire message into memory — it is unsuitable for very large files. It does not expose unauthenticated bytes by design.

### InvalidToken Exception

Raised when a token is malformed, has an invalid signature, or exceeds the TTL.
