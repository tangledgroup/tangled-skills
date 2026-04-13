# Fernet Encryption and Key Management

This document provides comprehensive coverage of Fernet symmetric encryption used by `EncryptedCookieStorage`, including key generation, key rotation with MultiFernet, password-based keys, and security best practices.

## Fernet Overview

Fernet is a symmetric (secret key) authenticated encryption implementation that guarantees:
- **Confidentiality**: Messages cannot be read without the key
- **Authenticity**: Messages cannot be manipulated without detection
- **Thread Safety**: Fernet instances are safe to use across threads

**Encryption Algorithm:**
- AES-128-CBC for encryption
- HMAC-SHA256 for authentication
- PKCS7 padding
- URL-safe base64 encoding

**Token Structure:**
```
Fernet Token = timestamp + IV + ciphertext + HMAC signature
               (8 bytes)  (16 bytes) (variable)  (32 bytes)
```

The timestamp is stored in plaintext to support TTL (time-to-live) validation.

---

## Key Generation

### Generate New Key

Always use cryptographically secure random key generation:

```python
from cryptography.fernet import Fernet

# Generate a new 32-byte URL-safe base64-encoded key
key = Fernet.generate_key()
print(key)  # e.g., b'gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i='

# Create Fernet instance
f = Fernet(key)
```

**Key Format:**
- 32 bytes of cryptographically secure random data
- URL-safe base64 encoded (44 characters)
- Contains both encryption key and signing key

### Key Storage

**Production - Environment Variable:**
```python
import os
from cryptography.fernet import Fernet

# Load from environment variable
key = os.environ['SESSION_ENCRYPTION_KEY']
f = Fernet(key)
```

**Generate and Save Once:**
```python
from cryptography.fernet import Fernet

# Run this once to generate a key
if __name__ == "__main__":
    key = Fernet.generate_key()
    print(f"Save this key securely: {key.decode()}")
    
    # Save to file (protect with proper permissions)
    with open("/path/to/fernet.key", "wb") as f:
        f.write(key)
    os.chmod("/path/to/fernet.key", 0o600)  # Owner read/write only
```

**Load from File:**
```python
from cryptography.fernet import Fernet

with open("/path/to/fernet.key", "rb") as f:
    key = f.read()

f = Fernet(key)
```

### Key Requirements

**Valid Key:**
```python
from cryptography.fernet import Fernet

# ✅ Valid: 32 bytes, base64 encoded
key = Fernet.generate_key()  # 44 characters when decoded

# ✅ Valid: Raw 32 bytes (will be base64 encoded internally)
key = b'Thirty  two  length  bytes  key.'  # Exactly 32 bytes

# ✅ Valid: Base64 string
key = "gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i="
```

**Invalid Keys:**
```python
# ❌ Too short
key = b'short'  # Will raise InvalidToken

# ❌ Not base64 encoded properly
key = b'not-valid-base64!!!'  # Will raise InvalidToken

# ❌ Wrong length after decoding
key = base64.b64encode(b'short')  # Decodes to < 32 bytes
```

---

## Basic Encryption/Decryption

### Encrypt Data

```python
from cryptography.fernet import Fernet

f = Fernet(key)

# Data must be bytes
message = b"my deep dark secret"
token = f.encrypt(message)

print(token)
# b'gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i=...'

# Token is URL-safe base64 encoded
# Can be safely stored in cookies, URLs, databases
```

### Decrypt Data

```python
from cryptography.fernet import Fernet

f = Fernet(key)

# Decrypt token
token = b'gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i=...'
message = f.decrypt(token)

print(message)  # b'my deep dark secret'
```

### With TTL (Time-To-Live)

```python
from cryptography.fernet import Fernet

f = Fernet(key)

# Encrypt
token = f.encrypt(b"secret message")

# Decrypt with 1-hour TTL (3600 seconds)
try:
    message = f.decrypt(token, ttl=3600)
    print("Valid:", message)
except InvalidToken:
    print("Token expired or invalid")
```

**TTL Behavior:**
- Token contains creation timestamp in plaintext
- If token age > TTL seconds, `InvalidToken` exception raised
- TTL enforced server-side only (timestamp is visible)
- Useful for session expiration without database queries

---

## Using with EncryptedCookieStorage

### Basic Setup

```python
from cryptography.fernet import Fernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Generate key
key = Fernet.generate_key()
f = Fernet(key)

# Create storage
storage = EncryptedCookieStorage(f)

# Setup in application
app = web.Application()
setup(app, storage)
```

### With Raw Bytes Key

```python
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# 32-byte raw key (will be base64 encoded internally)
secret_key = b'Thirty  two  length  bytes  key.'  # Exactly 32 bytes

storage = EncryptedCookieStorage(secret_key)
setup(app, storage)
```

### With Base64 String Key

```python
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Base64-encoded key (from Fernet.generate_key())
secret_key = "gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i="

storage = EncryptedCookieStorage(secret_key)
setup(app, storage)
```

### With TTL Support

```python
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

f = Fernet(key)

storage = EncryptedCookieStorage(
    f,
    max_age=3600  # Sessions expire after 1 hour
)

# Fernet will validate token TTL on each request
# If token is older than max_age, new session created automatically
setup(app, storage)
```

---

## Key Rotation with MultiFernet

**MultiFernet** enables seamless key rotation by maintaining multiple keys. New tokens are encrypted with the first key, but decryption tries all keys in order.

### Setup MultiFernet

```python
from cryptography.fernet import Fernet, MultiFernet

# Create multiple Fernet instances
key1 = Fernet(Fernet.generate_key())  # Old key
key2 = Fernet(Fernet.generate_key())  # New key

# MultiFernet: encrypt with first key, decrypt with any
f = MultiFernet([key2, key1])  # key2 is primary for encryption

# Encrypt (uses key2)
token = f.encrypt(b"Secret message!")

# Decrypt (tries key2, then key1)
message = f.decrypt(token)
print(message)  # b'Secret message!'
```

### Key Rotation Process

**Step 1: Generate New Key**
```python
from cryptography.fernet import Fernet

new_key = Fernet(Fernet.generate_key())
old_key = Fernet(os.environ['CURRENT_KEY'])

# Deploy with both keys (new first for encryption)
f = MultiFernet([new_key, old_key])
```

**Step 2: Active Rotation (Optional)**

Actively re-encrypt existing tokens with new key:
```python
from cryptography.fernet import MultiFernet

# Old token encrypted with old_key
old_token = b'...'

# Rotate to new key
new_token = f.rotate(old_token)

# New token encrypted with primary key (new_key)
# Original timestamp preserved
```

**Step 3: Remove Old Key**

After all old tokens expire:
```python
# Remove old_key from list
f = MultiFernet([new_key])  # Only new key now
```

### Complete Rotation Example

```python
import os
from cryptography.fernet import Fernet, MultiFernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

def get_fernet_instance():
    """Get Fernet with key rotation support."""
    
    # Primary key (newest, used for encryption)
    primary_key = os.environ['SESSION_KEY_PRIMARY']
    
    # Secondary keys (older, for decrypting existing tokens)
    secondary_keys = os.environ.get('SESSION_KEY_SECONDARY', '').split(',')
    
    fernet_instances = [Fernet(primary_key.encode())]
    
    for key in secondary_keys:
        if key.strip():
            fernet_instances.append(Fernet(key.strip().encode()))
    
    if len(fernet_instances) > 1:
        return MultiFernet(fernet_instances)
    else:
        return fernet_instances[0]

# Usage
app = web.Application()
f = get_fernet_instance()
storage = EncryptedCookieStorage(f)
setup(app, storage)
```

### Environment Configuration

```bash
# .env or environment variables
SESSION_KEY_PRIMARY="new-base64-key-here-1234567890abcdef"
SESSION_KEY_SECONDARY="old-key-1,old-key-2"
```

**Deployment Process:**
1. Generate new primary key
2. Update `SESSION_KEY_PRIMARY`
3. Add old primary to `SESSION_KEY_SECONDARY`
4. Deploy (old sessions still work)
5. Wait for all old sessions to expire (~max_age)
6. Remove from `SESSION_KEY_SECONDARY`

### Token Rotation Utility

```python
from cryptography.fernet import MultiFernet
import redis

async def rotate_all_session_tokens(multi_fernet: MultiFernet, redis_client):
    """Rotate all tokens in Redis storage."""
    
    # Get all session keys
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(match="AIOHTTP_SESSION_*", count=100)
        
        for key in keys:
            try:
                # Get current token (cookie value stored as part of key)
                session_data = await redis_client.get(key)
                
                # Extract and rotate token
                # (implementation depends on your storage format)
                rotated_token = multi_fernet.rotate(session_data)
                
                # Save rotated token
                await redis_client.set(key, rotated_token)
                
            except InvalidToken:
                # Skip invalid tokens
                continue
        
        if cursor == 0:
            break
```

---

## Password-Based Keys

Derive encryption keys from passwords using key derivation functions (KDF). **Requires storing salt separately.**

### Using PBKDF2-HMAC

```python
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Step 1: Generate salt (do once, store securely)
salt = os.urandom(16)

# Save salt to file or database
with open("fernet_salt.bin", "wb") as f:
    f.write(salt)

# Step 2: Derive key from password
password = b"your-secure-password"

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=1_200_000,  # Django recommendation (2025)
)

key = base64.urlsafe_b64encode(kdf.derive(password))

# Step 3: Use derived key
f = Fernet(key)
token = f.encrypt(b"Secret message!")
message = f.decrypt(token)
```

### Using Argon2id (Recommended)

```python
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# Generate salt
salt = os.urandom(16)

# Derive key using Argon2id
kdf = Argon2id(
    salt=salt,
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Parallel threads
    hash_len=32,        # Output length (bytes)
)

password = b"your-secure-password"
key = base64.urlsafe_b64encode(kdf.derive(password))

f = Fernet(key)
```

### Using Scrypt

```python
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

salt = os.urandom(16)

kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,     # CPU/memory cost factor
    r=8,         # Block size
    p=1,         # Parallelization
)

password = b"your-secure-password"
key = base64.urlsafe_b64encode(kdf.derive(password))

f = Fernet(key)
```

**Important:** Store salt securely and retrievably. Without the exact same salt, key derivation will produce different keys.

---

## Advanced Features

### Encrypt at Specific Time (Testing)

Useful for testing token expiration without waiting:

```python
from cryptography.fernet import Fernet
import time

f = Fernet(key)

# Encrypt with specific timestamp
current_time = int(time.time())
token = f.encrypt_at_time(b"test message", current_time)

# Decrypt with explicit time and TTL
try:
    message = f.decrypt_at_time(token, ttl=3600, current_time=current_time + 7200)
except InvalidToken:
    print("Token expired (2 hours > 1 hour TTL)")
```

### Extract Token Timestamp

Check when a token was created without decrypting:

```python
from cryptography.fernet import Fernet
import time

f = Fernet(key)
token = f.encrypt(b"message")

# Get creation timestamp
timestamp = f.extract_timestamp(token)
age_seconds = time.time() - timestamp

print(f"Token created {age_seconds:.0f} seconds ago")

# Check if about to expire (e.g., within 5 minutes)
if age_seconds > 3600 - 300:  # Less than 5 minutes until 1-hour expiry
    print("Token expiring soon, consider re-encrypting")
```

### Token Validation Without Decryption

```python
from cryptography.fernet import Fernet, InvalidToken

f = Fernet(key)
token = b'some-token'

try:
    # Validate token signature without caring about content
    f.decrypt(token)
    print("Token is valid")
except InvalidToken:
    print("Token is invalid (bad signature, tampered, or expired)")
```

---

## Error Handling

### InvalidToken Exception

Raised when decryption fails for any reason:

```python
from cryptography.fernet import Fernet, InvalidToken

f = Fernet(key)

try:
    message = f.decrypt(token)
except InvalidToken as e:
    # Token is invalid for one of these reasons:
    # - Malformed (not valid base64 or wrong structure)
    # - Bad signature (tampered with)
    # - Wrong key (encrypted with different key)
    # - Expired (older than TTL)
    
    print(f"Invalid token: {e}")
    
    # Handle appropriately:
    # - Create new session
    # - Log security event
    # - Reject request
```

### Common Invalid Token Scenarios

**Wrong Key:**
```python
key1 = Fernet.generate_key()
key2 = Fernet.generate_key()

f1 = Fernet(key1)
f2 = Fernet(key2)

token = f1.encrypt(b"message")

try:
    f2.decrypt(token)  # Encrypted with key1, decrypting with key2
except InvalidToken:
    print("Wrong key used for decryption")
```

**Tampered Token:**
```python
f = Fernet(key)
token = f.encrypt(b"message")

# Tamper with token
tampered = token[:10] + b'X' * 10 + token[20:]

try:
    f.decrypt(tampered)
except InvalidToken:
    print("Token was tampered with (signature invalid)")
```

**Expired Token:**
```python
f = Fernet(key)
token = f.encrypt(b"message")

try:
    f.decrypt(token, ttl=0)  # TTL of 0 seconds
except InvalidToken:
    print("Token expired")
```

---

## Security Best Practices

### Key Management

**DO:**
- ✅ Generate keys with `Fernet.generate_key()`
- ✅ Store keys in environment variables or secret management
- ✅ Use MultiFernet for key rotation
- ✅ Set appropriate file permissions (0600) for key files
- ✅ Backup keys securely (lost key = lost all data)
- ✅ Use different keys for different environments

**DON'T:**
- ❌ Hardcode keys in source code
- ❌ Commit keys to version control
- ❌ Use weak or predictable keys
- ❌ Share keys across unrelated applications
- ❌ Skip key rotation planning

### Token Security

**DO:**
- ✅ Set reasonable TTL for session tokens
- ✅ Use `secure=True` cookie flag in production
- ✅ Use `httponly=True` to prevent JavaScript access
- ✅ Use `samesite="Lax"` for CSRF protection
- ✅ Monitor for InvalidToken exceptions (security events)

**DON'T:**
- ❌ Store sensitive data in tokens (they're visible in base64)
- ❌ Rely on token secrecy for security (use signatures)
- ❌ Skip TTL validation for time-sensitive operations
- ❌ Reuse tokens across different purposes

### Key Rotation Best Practices

```python
# Recommended rotation schedule
# - High-security apps: Every 90 days
# - Standard apps: Every 6-12 months
# - After any suspected key compromise: Immediately

def should_rotate_keys(current_key_age_days):
    """Determine if keys should be rotated."""
    return current_key_age_days > 90  # 90-day rotation
```

### Incident Response

**If Key is Compromised:**
1. Generate new key immediately
2. Deploy with MultiFernet ([new, compromised])
3. Force all users to re-authenticate (invalidate old sessions)
4. Remove compromised key after all sessions expired
5. Investigate compromise vector
6. Document incident

**If Tokens are Being Tampered:**
1. Check for InvalidToken exceptions in logs
2. Verify key hasn't been changed
3. Check for man-in-the-middle attacks (ensure HTTPS)
4. Review cookie security flags
5. Consider adding additional authentication

---

## Comparison: Fernet vs Other Encryption

| Feature | Fernet | AES-CBC | RSA |
|---------|--------|---------|-----|
| **Type** | Symmetric + Auth | Symmetric only | Asymmetric |
| **Authentication** | ✅ Built-in HMAC | ❌ Separate needed | ✅ Digital signature |
| **Key Size** | 32 bytes (128-bit) | 16-32 bytes | 2048+ bits |
| **Speed** | Fast | Fast | Slow |
| **Use Case** | Sessions, tokens | Bulk data | Key exchange |
| **TTL Support** | ✅ Built-in | ❌ Manual | ❌ Manual |
| **Key Rotation** | ✅ MultiFernet | ⚠️ Manual | N/A |

**Why Fernet for Sessions:**
- Authentication built-in (detect tampering)
- TTL support for automatic expiration
- Key rotation with MultiFernet
- URL-safe encoding (cookie-friendly)
- Well-tested, battle-proven implementation

---

## Troubleshooting

### "InvalidToken" on Valid Data

**Cause:** Key mismatch or corruption

**Solution:**
```python
# Verify key length
key = Fernet.generate_key()
print(len(base64.urlsafe_b64decode(key)))  # Should be 32

# Verify key encoding
with open("key.txt") as f:
    key = f.read().strip()  # Remove newlines
    
f = Fernet(key)
```

### "Token Expired" Immediately

**Cause:** System clock skew or TTL too short

**Solution:**
```python
# Check system time
import time
print(time.time())  # Verify correct Unix timestamp

# Increase TTL
storage = EncryptedCookieStorage(f, max_age=86400)  # 24 hours
```

### MultiFernet Not Decrypting Old Tokens

**Cause:** Old key not in list or wrong order

**Solution:**
```python
# Ensure all historical keys are in list
f = MultiFernet([newest, older, oldest])  # Newest first for encryption

# All keys must be Fernet instances, not raw keys
keys = [Fernet(k) for k in key_list]
f = MultiFernet(keys)
```

### Password-Based Key Not Working

**Cause:** Salt mismatch or different KDF parameters

**Solution:**
```python
# Ensure exact same salt and parameters
with open("salt.bin", "rb") as f:
    salt = f.read()  # Must be identical

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,  # Same salt
    iterations=1_200_000,  # Same iterations
)
```
