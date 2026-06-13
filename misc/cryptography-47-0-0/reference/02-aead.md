# Authenticated Encryption (AEAD)

AEAD ciphers provide both confidentiality and integrity in a single operation. They are the recommended approach for symmetric encryption.

## AEAD API

The `cryptography.hazmat.primitives.ciphers.aead` module provides high-level AEAD interfaces that handle nonce management internally.

### AES-GCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)  # 32 bytes
aesgcm = AESGCM(key)

# Encrypt (nonce auto-generated)
ct = aesgcm.encrypt(nonce, b"plaintext", associated_data)

# Decrypt
pt = aesgcm.decrypt(nonce, ct, associated_data)
```

Key sizes: 128, 192, or 256 bits. Nonce: 12 bytes recommended (96-bit).

### AES-GCM with in-place encryption (since 47.0.0)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)

# encrypt_into writes directly to a pre-allocated buffer
output = bytearray(len(plaintext) + 16)  # plaintext + 16-byte tag
aesgcm.encrypt_into(nonce, plaintext, associated_data, output)

# decrypt_into similarly
output_pt = bytearray(len(ct) - 16)
aesgcm.decrypt_into(nonce, ct, associated_data, output_pt)
```

Available on: `AESGCM`, `AESCCM`, `AESGCMSIV`, `AESOCB3`, `AESSIV`, `ChaCha20Poly1305`.

### ChaCha20-Poly1305

```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

key = ChaCha20Poly1305.generate_key()  # 32 bytes
chacha = ChaCha20Poly1305(key)

ct = chacha.encrypt(nonce, b"plaintext", associated_data)
pt = chacha.decrypt(nonce, ct, associated_data)
```

Key: 256 bits. Nonce: 96 bits (12 bytes). No hardware acceleration needed — fast in software.

### AES-CCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESCCM

key = AESCCM.generate_key(bit_length=256)
aesccm = AESCCM(key)

ct = aesccm.encrypt(nonce, b"plaintext", associated_data)
pt = aesccm.decrypt(nonce, ct, associated_data)
```

Nonce sizes: 11, 12, or 13 bytes. Tag size: 12 bytes.

## Low-Level Cipher API

For fine-grained control, use the `Cipher` class directly. This is less safe — prefer AEAD APIs when possible.

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = b"32-byte-key-here-"
nonce = b"16-byte nonce!!"

cipher = Cipher(algorithms.AES(key), modes.CBC(nonce))
encryptor = cipher.encryptor()
ct = encryptor.update(b"data") + encryptor.finalize()

decryptor = cipher.decryptor()
pt = decryptor.update(ct) + decryptor.finalize()
```

**Warning**: Unauthenticated CBC mode is vulnerable to padding oracle attacks. Use AEAD modes (GCM, CCM, ChaCha20-Poly1305) instead.

## Nonce Management

- **Never reuse a nonce with the same key** — this breaks all security guarantees
- For GCM: 12-byte nonces are standard
- Use `os.urandom()` for random nonces, or maintain a counter
- AEAD APIs accept `None` for auto-generated nonces (nonce is prepended to ciphertext)

## Best Practices

- Prefer Fernet for simple authenticated encryption (handles key + nonce management)
- Use AES-GCM or ChaCha20-Poly1305 for performance-critical applications
- Always include associated data (AD) for any contextual information that must be verified but not encrypted
- Rotate keys periodically
