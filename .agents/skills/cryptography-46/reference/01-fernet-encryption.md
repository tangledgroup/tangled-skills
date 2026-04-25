# Fernet Encryption

Fernet provides high-level symmetric authenticated encryption. It guarantees that encrypted messages cannot be manipulated or read without the key, and includes built-in support for key rotation via MultiFernet.

## Core Concepts

Fernet combines:
- AES-128-CBC encryption
- HMAC-SHA256 authentication
- URL-safe base64 encoding
- Timestamp-based expiration (optional)

The resulting "token" is a self-contained, authenticated ciphertext.

## Basic Usage

### Generate and Use a Key

```python
from cryptography.fernet import Fernet

# Generate a new key (32 bytes, base64-encoded)
key = Fernet.generate_key()
# Save this key securely! Losing it means losing access to all encrypted data.

# Create Fernet instance
f = Fernet(key)

# Encrypt data (must be bytes)
token = f.encrypt(b"Secret message")
# Result: b'gAAAAAB...'

# Decrypt
message = f.decrypt(token)
# Returns: b'Secret message'
```

### Key Storage

**Critical:** Store Fernet keys securely. Anyone with the key can:
- Decrypt all messages encrypted with it
- Forge arbitrary authenticated messages

Recommended storage:
- Environment variables for applications
- Secret management systems (HashiCorp Vault, AWS Secrets Manager)
- Encrypted configuration files
- **Never** commit to version control

```python
import os
from cryptography.fernet import Fernet

# Load key from environment
key = os.environ["FERNET_KEY"].encode()
f = Fernet(key)
```

## Token Expiration

Fernet tokens include a timestamp. Use the `ttl` parameter to enforce expiration:

```python
from cryptography.fernet import Fernet

f = Fernet(key)

# Encrypt
token = f.encrypt(b"Temporary secret")

# Decrypt with 1-hour TTL (3600 seconds)
try:
    message = f.decrypt(token, ttl=3600)
except InvalidToken as e:
    print("Token expired or invalid:", e)
```

## Key Rotation with MultiFernet

MultiFernet enables seamless key rotation by maintaining multiple keys:

```python
from cryptography.fernet import Fernet, MultiFernet

# Create multiple Fernet instances with different keys
key1 = Fernet.generate_key()  # Old key
key2 = Fernet.generate_key()  # New key

fernet_old = Fernet(key1)
fernet_new = Fernet(key2)

# MultiFernet: new key first (for encryption), old key second (for decryption)
multi = MultiFernet([fernet_new, fernet_old])

# Encrypt with newest key
token = multi.encrypt(b"Message")

# Decrypt works with any known key
message = multi.decrypt(token)
```

### Rotation Workflow

1. Generate new key
2. Add new Fernet to front of MultiFernet list
3. Continue operating (encrypts with new, decrypts with either)
4. Re-encrypt old tokens using `rotate()`
5. Remove old key when all tokens rotated

```python
# Rotate a token to newest key
new_token = multi.rotate(old_token)
```

## Using Passwords with Fernet

Fernet requires a 32-byte key, not a password. Derive a key from a password:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import os

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Generate salt once, store with encrypted data
salt = os.urandom(16)
key = derive_key("user_password", salt)

f = Fernet(key)
token = f.encrypt(b"Secret")
```

## Advanced Features

### Encrypt at Specific Time (Testing)

Useful for testing token expiration:

```python
import time
from cryptography.fernet import Fernet

f = Fernet(key)

# Encrypt with specific timestamp
current_time = int(time.time())
token = f.encrypt_at_time(b"Test message", current_time)

# Decrypt with specific time and TTL
try:
    message = f.decrypt_at_time(token, ttl=3600, current_time=current_time + 7200)
except InvalidToken:
    print("Token expired (2 hours > 1 hour TTL)")
```

### Extract Token Timestamp

Check when a token was created without decrypting:

```python
import time
from cryptography.fernet import Fernet

f = Fernet(key)
timestamp = f.extract_timestamp(token)
age = time.time() - timestamp

print(f"Token is {age:.0f} seconds old")
```

## Error Handling

```python
from cryptography.fernet import Fernet, InvalidToken

f = Fernet(key)

try:
    message = f.decrypt(token)
except InvalidToken as e:
    # Token is malformed, corrupted, expired, or wrong key
    print("Invalid token:", str(e))
except TypeError as e:
    # Input is not bytes or string
    print("Type error:", str(e))
```

## Limitations

1. **Timestamp in plaintext:** Token creation time is visible (not encrypted)
2. **No forward secrecy:** Compromised key decrypts all past messages
3. **Single-key design:** Each Fernet instance uses one key (use MultiFernet for rotation)
4. **AES-128 only:** Cannot configure different cipher or key size

## Best Practices

1. **Generate keys securely:** Use `Fernet.generate_key()` not manual generation
2. **Store keys separately:** Keep keys separate from encrypted data
3. **Implement rotation:** Plan for periodic key rotation with MultiFernet
4. **Use TTLs:** Set appropriate token expiration for sensitive data
5. **Log errors carefully:** Don't expose decryption failures to users
6. **Backup keys:** Losing a key means losing access to all encrypted data

## Complete Example: Secure Message Storage

```python
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

class SecureMessageStore:
    def __init__(self, keys_file: str):
        self.keys_file = keys_file
        self._load_keys()
    
    def _load_keys(self):
        """Load encryption keys from file."""
        if not os.path.exists(self.keys_file):
            # Generate new key if none exists
            key = Fernet.generate_key()
            self._save_keys([key])
        else:
            with open(self.keys_file, 'rb') as f:
                keys = json.load(f)
            self.fernets = [Fernet(k) for k in keys]
        
        self.multi = MultiFernet(self.fernets)
    
    def _save_keys(self, keys: list):
        """Save keys to file."""
        with open(self.keys_file, 'w') as f:
            json.dump([k.decode() for k in keys], f)
    
    def add_key(self):
        """Rotate to new key."""
        new_key = Fernet.generate_key()
        self.fernets.insert(0, Fernet(new_key))
        self.multi = MultiFernet(self.fernets)
        self._save_keys([f.key for f in self.fernets])
    
    def encrypt_message(self, message: str, ttl: int = None) -> str:
        """Encrypt a message."""
        token = self.multi.encrypt(message.encode())
        return token.decode()
    
    def decrypt_message(self, token: str, ttl: int = None) -> str:
        """Decrypt a message."""
        try:
            decrypted = self.multi.decrypt(token.encode(), ttl=ttl)
            return decrypted.decode()
        except InvalidToken as e:
            raise ValueError(f"Invalid or expired token: {e}")

# Usage
store = SecureMessageStore("keys.json")

# Encrypt
token = store.encrypt_message("Secret data", ttl=3600)
print(f"Encrypted: {token}")

# Decrypt
message = store.decrypt_message(token)
print(f"Decrypted: {message}")

# Rotate key
store.add_key()

# Old tokens still decrypt, new ones use new key
```
