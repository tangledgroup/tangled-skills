# Key Wrapping

AES key wrap per RFC 3394 and padded key wrap per RFC 5649. Used to encrypt keys with other keys (key encryption keys).

## AES Key Wrap

```python
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap

key = b"32-byte-key"          # Key to be wrapped
enc_key = b"32-byte-enc-key"  # Key encryption key (16, 24, or 32 bytes)

wrapped = aes_key_wrap(key, enc_key)
unwrapped = aes_key_unwrap(wrapped, enc_key)
```

Input key must be a multiple of 8 bytes. Output is `len(key) + 8` bytes.

## AES Key Wrap with Padding

Supports keys of any length (padded internally):

```python
from cryptography.hazmat.primitives.keywrap import (
    aes_key_wrap_with_padding,
    aes_key_unwrap_with_padding,
)

wrapped = aes_key_wrap_with_padding(key, enc_key)
unwrapped = aes_key_unwrap_with_padding(wrapped, enc_key)
```

## Exceptions

- `InvalidUnwrap` — Raised when unwrapping fails (wrong key or corrupted data)
- `KeyIvWrongSize` — Raised when key/IV sizes are incorrect
