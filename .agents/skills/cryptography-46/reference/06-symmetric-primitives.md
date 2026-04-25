# Symmetric Encryption Primitives

This reference covers low-level symmetric encryption algorithms including AES, ChaCha20, and AEAD modes. Use these only when Fernet is insufficient.

## AEAD (Authenticated Encryption with Associated Data)

AEAD provides both confidentiality and integrity. **Always prefer AEAD over plain encryption.**

### AES-GCM (Galois/Counter Mode)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Generate 256-bit key (also supports 128-bit and 192-bit)
key = os.urandom(32)  # 256 bits

# Create AESGCM instance
aesgcm = AESGCM(key)

# Generate random nonce (12 bytes recommended for GCM)
nonce = os.urandom(12)

# Encrypt
plaintext = b"Secret message"
ciphertext = aesgcm.encrypt(nonce, plaintext, None)

# Decrypt
decrypted = aesgcm.decrypt(nonce, ciphertext, None)
assert decrypted == plaintext
```

### AES-GCM with Associated Data

Associated data is authenticated but not encrypted:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = os.urandom(32)
aesgcm = AESGCM(key)
nonce = os.urandom(12)

# Associated data (authenticated, not encrypted)
aad = b"header-or-metadata"

ciphertext = aesgcm.encrypt(nonce, plaintext, aad)

# Decrypt with same AAD
decrypted = aesgcm.decrypt(nonce, ciphertext, aad)

# Wrong AAD raises exception
try:
    aesgcm.decrypt(nonce, ciphertext, b"wrong-aad")
except ValueError as e:
    print("Authentication failed:", e)
```

### AES-CCM Mode

CCM is an alternative AEAD mode (used in IEEE 802.15.4):

```python
from cryptography.hazmat.primitives.ciphers.aead import AESSIV

# CCM requires specifying tag length and nonce size
key = os.urandom(32)
nonce = os.urandom(13)  # CCM typically uses 13-byte nonce
tag_length = 16  # 128-bit tag

# Encrypt
ciphertext_with_tag = aes_ccm.encrypt(nonce, plaintext, None, tag_length)

# Decrypt
decrypted = aes_ccm.decrypt(nonce, ciphertext_with_tag, None, tag_length)
```

### ChaCha20-Poly1305

Modern AEAD that doesn't require hardware acceleration:

```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os

# 256-bit key, 96-bit nonce
key = os.urandom(32)
nonce = os.urandom(12)

chacha = ChaCha20Poly1305(key)

# Encrypt
ciphertext = chacha.encrypt(nonce, plaintext, None)

# Decrypt
decrypted = chacha.decrypt(nonce, ciphertext, None)
```

### XChaCha20-Poly1305

Extended nonce variant (256-bit nonce):

```python
from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305

key = os.urandom(32)
nonce = os.urandom(19)  # 152-bit nonce for XChaCha20

chacha = XChaCha20Poly1305(key)
ciphertext = chacha.encrypt(nonce, plaintext, None)
decrypted = chacha.decrypt(nonce, ciphertext, None)
```

## Non-AEAD Modes (Use with Caution)

### AES-CTR (Counter Mode)

Stream mode - no authentication, **must** combine with separate MAC:

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
import os

key = os.urandom(32)
iv = os.urandom(16)

# Encrypt with CTR mode
cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
encryptor = cipher.encryptor()
ciphertext = encryptor.update(plaintext) + encryptor.finalize()

# IMPORTANT: Also compute MAC
mac = hmac.HMAC(key, hashes.SHA256())
mac.update(iv + ciphertext)
tag = mac.finalize()

# To decrypt: verify MAC first, then decrypt
```

### AES-CBC (Cipher Block Chaining)

Block mode with IV - no authentication, **must** combine with separate MAC:

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
import os

key = os.urandom(32)
iv = os.urandom(16)

# Pad plaintext to block size (16 bytes for AES)
padder = PKCS7(128).padder()
padded_data = padder.update(plaintext) + padder.finalize()

# Encrypt
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()

# Decrypt
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
decryptor = cipher.decryptor()
padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

# Unpad
unpadder = PKCS7(128).unpadder()
plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
```

### AES-OFB and AES-CFB

Legacy modes - avoid in new designs:

```python
# OFB mode
cipher = Cipher(algorithms.AES(key), modes.OFB(iv))

# CFB mode
cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
```

## Stream Ciphers

### ChaCha20 (Without Poly1305)

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)
nonce = os.urandom(16)  # 128-bit nonce for raw ChaCha20

cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
encryptor = cipher.encryptor()
ciphertext = encryptor.update(plaintext) + encryptor.finalize()

# Decrypt
cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
decryptor = cipher.decryptor()
decrypted = decryptor.update(ciphertext) + decryptor.finalize()
```

## Padding Schemes

### PKCS7 Padding

Standard padding for block ciphers:

```python
from cryptography.hazmat.primitives.padding import PKCS7

# Pad
padder = PKCS7(128).padder()  # 128-bit (16-byte) block size
padded = padder.update(b"short") + padder.finalize()
# Result: b'short\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b'

# Unpad
unpadder = PKCS7(128).unpadder()
original = unpadder.update(padded) + unpadder.finalize()
# Result: b'short'
```

### PKCS5 Padding

Same as PKCS7 for 8-byte blocks (legacy):

```python
from cryptography.hazmat.primitives.padding import PKCS5

padder = PKCS5().padder()
padded = padder.update(data) + padder.finalize()
```

### ANSIX.923, ISO78164, ZeroPadding

Alternative padding schemes:

```python
from cryptography.hazmat.primitives.padding import ANSIX923, ISO7816, ZeroPadding

# ANSI X.923
padder = ANSIX923(128).padder()

# ISO 7816
padder = ISO7816(128).padder()

# Zero padding (not self-identifying)
padder = ZeroPadding(128).padder()
```

## Key Wrapping

Key wrapping encrypts cryptographic keys:

```python
from cryptography.hazmat.primitives import keywrap

# Wrap key
key_encryption_key = os.urandom(32)  # KEK
data_key = os.urandom(16)  # Key to wrap

wrapped = keywrap.aes_key_wrap(key_encryption_key, data_key)

# Unwrap
unwrapped = keywrap.aes_key_unwrap(key_encryption_key, wrapped)
assert unwrapped == data_key
```

## Stream Cipher Operations

### Incremental Encryption

For large data:

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)
nonce = os.urandom(16)

cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
encryptor = cipher.encryptor()

# Process in chunks
chunk1 = encryptor.update(b"First part of data")
chunk2 = encryptor.update(b"Second part of data")
final = encryptor.finalize()

ciphertext = chunk1 + chunk2 + final
```

### Copy Cipher State

```python
cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
encryptor = cipher.encryptor()

# Encrypt some data
partial = encryptor.update(b"initial")

# Copy state for parallel processing
encryptor_copy = encryptor.copy()

# Continue on original
more = encryptor.update(b"more data")

# Use copy independently
copy_result = encryptor_copy.update(b"parallel data")
```

## Security Considerations

### Nonce Management

**Critical:** Never reuse (key, nonce) pairs!

```python
import os

# GOOD: Generate fresh nonce for each encryption
nonce = os.urandom(12)

# BAD: Counter-based without proper management
counter = 0  # DON'T DO THIS without careful design

# BAD: Reusing nonce
nonce = b"fixed-nonce"  # NEVER DO THIS
```

### Key Management

- Use separate keys for different purposes
- Store keys securely (HSM, KMS, encrypted storage)
- Rotate keys periodically
- Use appropriate key sizes (256-bit for AES recommended)

### Algorithm Selection

| Use Case | Recommended Algorithm |
|----------|----------------------|
| General encryption | AES-256-GCM or ChaCha20-Poly1305 |
| High performance (with AES-NI) | AES-256-GCM |
| Mobile/embedded (no AES-NI) | ChaCha20-Poly1305 |
| Long-term security | XChaCha20-Poly1305 |
| Legacy compatibility | AES-128-GCM |

### Don't Roll Your Own

```python
# WRONG: ECB mode is insecure
cipher = Cipher(algorithms.AES(key), modes.ECB())  # DON'T DO THIS

# WRONG: Reusing IVs in CBC mode
iv = b"fixed-iv"  # DON'T DO THIS

# WRONG: Encrypting without authentication
# Always use AEAD or encrypt-then-MAC pattern
```

## Complete Example: Secure File Encryption

```python
import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class FileEncryptor:
    CHUNK_SIZE = 1024 * 1024  # 1 MB chunks
    
    def __init__(self, password: str):
        self.password = password.encode()
    
    def encrypt_file(self, input_path: str, output_path: str):
        """Encrypt a file."""
        # Generate random values
        salt = os.urandom(16)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = kdf.derive(self.password)
        
        # Initialize AESGCM
        aesgcm = AESGCM(key)
        
        header = {
            "salt": salt.hex(),
            "iterations": 100_000,
        }
        
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Write header
            nonce = os.urandom(12)
            header["nonce"] = nonce.hex()
            outfile.write(json.dumps(header).encode() + b"\n")
            
            # Encrypt in chunks (GCM doesn't support streaming, so encrypt whole file or use different approach)
            # For large files, consider using AES-CTR with separate HMAC
            
            # Simple approach: read all, encrypt, write
            plaintext = infile.read()
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            outfile.write(ciphertext)
        
        print(f"Encrypted {input_path} to {output_path}")
    
    def decrypt_file(self, input_path: str, output_path: str):
        """Decrypt a file."""
        with open(input_path, 'rb') as infile:
            # Read header
            header_line = infile.readline()
            header = json.loads(header_line)
            
            salt = bytes.fromhex(header["salt"])
            nonce = bytes.fromhex(header["nonce"])
            
            # Derive key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=header["iterations"],
            )
            key = kdf.derive(self.password)
            
            # Read ciphertext and decrypt
            ciphertext = infile.read()
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(plaintext)
        
        print(f"Decrypted {input_path} to {output_path}")

# Usage
encryptor = FileEncryptor("my-password")
encryptor.encrypt_file("secret.txt", "secret.enc")
encryptor.decrypt_file("secret.enc", "secret_decrypted.txt")
```

## Performance Tips

1. **Use AEAD:** Built-in authentication is faster than separate MAC
2. **Batch operations:** Process data in chunks when possible
3. **Reuse cipher objects:** Create once, encrypt multiple messages with different nonces
4. **Parallel processing:** Use `copy()` for parallel encryption of independent data
5. **Hardware acceleration:** AES-GCM benefits from AES-NI instructions
