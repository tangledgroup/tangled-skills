---
name: bcrypt-5-0
description: A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password storage, verifying passwords, or deriving cryptographic keys with bcrypt_pbkdf.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - password-hashing
  - cryptography
  - security
  - authentication
  - key-derivation
category: security
required_environment_variables: []

external_references:
  - https://bcrypt.readthedocs.io/
  - https://github.com/pyca/bcrypt
---
## Overview
A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password storage, verifying passwords, or deriving cryptographic keys with bcrypt_pbkdf.

## When to Use
- Hashing passwords before storing them in a database
- Verifying user-provided passwords against stored hashes
- Deriving cryptographic keys from passwords using bcrypt_pbkdf
- Migrating from other password hashing libraries (py-bcrypt, passlib)
- Building authentication systems requiring industry-standard password protection

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password storage, verifying passwords, or deriving cryptographic keys with bcrypt_pbkdf.

A Python library for modern password hashing using the bcrypt algorithm. Provides secure password storage, verification, and key derivation functions implemented in Rust for performance and safety.

## Installation / Setup
### Installation

Install bcrypt via pip:

```bash
pip install bcrypt
```

### Build Dependencies (for source installation)

When building from source, the following are required:

- **Rust compiler** (minimum version 1.74.0 for bcrypt 5.0)
- **C compiler** (gcc or clang)

**Debian/Ubuntu:**
```bash
sudo apt-get install build-essential cargo
```

**Fedora/RHEL:**
```bash
sudo yum install gcc cargo
```

**Alpine Linux:**
```bash
apk add --update musl-dev gcc cargo
```

### Python Version Support

bcrypt 5.0 supports:
- Python 3.8 through 3.14
- Free-threaded Python 3.14 (Python without GIL)
- PyPy 3.8+
- Windows on ARM

## Usage
### Password Hashing

Hash a password with a randomly-generated salt:

```python
import bcrypt

password = b"super secret password"
# Hash a password for the first time, with a randomly-generated salt
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# Check that an unhashed password matches one that has previously been hashed
if bcrypt.checkpw(password, hashed):
    print("It Matches!")
else:
    print("It Does not Match :(")
```

**Important:** Passwords must be passed as bytes, not strings. Use `password.encode('utf-8')` to convert strings.

### Verifying Passwords

The `checkpw()` function safely compares a password against a stored hash:

```python
import bcrypt

# Stored hash from database
hashed_password = b'$2b$12$KRoVgjD04ktnSuyOJNlM2.t3Oj96e5FwP8xXQlg6t1o7vLsEh'

# User-provided password
password = b"user_password_123"

if bcrypt.checkpw(password, hashed_password):
    print("Authentication successful")
else:
    print("Authentication failed")
```

`checkpw()` performs constant-time comparison to prevent timing attacks.

### Adjustable Work Factor

bcrypt uses a logarithmic work factor (number of rounds) that determines computational cost. Higher values increase security but also hashing time.

**Default rounds (12):**
```python
hashed = bcrypt.hashpw(password, bcrypt.gensalt())  # Default: 12 rounds
```

**Custom rounds:**
```python
import bcrypt

password = b"super secret password"
# Hash with 14 rounds (4x slower than 12 rounds)
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=14))

if bcrypt.checkpw(password, hashed):
    print("It Matches!")
```

**Valid round range:** 4-31

**Recommended values:**
- **Minimum:** 10 rounds (for legacy systems)
- **Recommended:** 12 rounds (default, good balance)
- **High security:** 14+ rounds (if performance allows)

**Timing reference** (on modern hardware):
- 10 rounds: ~50ms
- 12 rounds: ~200ms
- 14 rounds: ~800ms

### Password Length Limitation

bcrypt has a maximum password length of **72 bytes**. Passwords longer than this raise a `ValueError`:

```python
import bcrypt

long_password = b"an incredibly long password" * 10

try:
    hashed = bcrypt.hashpw(long_password, bcrypt.gensalt())
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: password cannot be longer than 72 bytes...
```

**Workaround for long passwords:** Hash the password with SHA-256 first, then base64 encode:

```python
import bcrypt
import hashlib
import base64

long_password = b"an incredibly long password" * 10

# Hash with SHA-256, then base64 encode to avoid NULL byte issues
hashed = bcrypt.hashpw(
    base64.b64encode(hashlib.sha256(long_password).digest()),
    bcrypt.gensalt()
)
```

### Salt Prefix Configuration

bcrypt supports different version prefixes for compatibility:

```python
import bcrypt

# Default prefix: $2b$ (recommended)
hashed = bcrypt.hashpw(password, bcrypt.gensalt(prefix=b"2b"))

# Legacy prefix: $2a$ (for compatibility with older systems)
hashed = bcrypt.hashpw(password, bcrypt.gensalt(prefix=b"2a"))
```

**Supported prefixes:**
- `b"2b"` - Default, recommended for new hashes
- `b"2a"` - Legacy, use for compatibility only
- `b"2y"` - Deprecated (still supported in hashpw but not recommended)

### Key Derivation Function (KDF)

bcrypt provides `bcrypt_pbkdf` for deriving cryptographic keys from passwords. This is used in OpenSSH's encrypted private key format:

```python
import bcrypt

key = bcrypt.kdf(
    password=b'password',
    salt=b'salt',
    desired_key_bytes=32,  # Output 32 bytes (256 bits)
    rounds=100
)
```

**Parameters:**
- `password`: Password bytes (must not be empty)
- `salt`: Salt bytes (must not be empty, at least 16 bytes recommended)
- `desired_key_bytes`: Output key length (1-512 bytes)
- `rounds`: Number of iterations (must be >= 1, recommended >= 50)
- `ignore_few_rounds`: Suppress warning for low round counts (default: False)

**Important:** Unlike bcrypt's password hashing rounds, the KDF rounds parameter is **linear**, not logarithmic. Use at least 50 rounds for security.

```python
# Warning will be emitted for rounds < 50
key = bcrypt.kdf(
    password=b'password',
    salt=b'salt',
    desired_key_bytes=32,
    rounds=10  # Emits UserWarning
)

# Suppress warning if intentionally using few rounds for testing
key = bcrypt.kdf(
    password=b'password',
    salt=b'salt',
    desired_key_bytes=32,
    rounds=10,
    ignore_few_rounds=True
)
```

## Common Usage Patterns
### Add, Hash, Store (Registration Flow)

The typical password registration workflow:

```python
import bcrypt

def register_user(username: str, password: str) -> dict:
    """Register a new user with hashed password."""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # Store in database (example)
    user_data = {
        'username': username,
        'password_hash': hashed_password.decode('utf-8'),  # Store as string
        'created_at': '2024-01-01'
    }
    
    return user_data

# Usage
user = register_user("john_doe", "SecureP@ss123!")
print(f"User registered: {user['username']}")
print(f"Hash stored: {user['password_hash'][:20]}...")
```

### Verify Password (Login Flow)

The typical authentication workflow:

```python
import bcrypt

def authenticate_user(username: str, password: str, stored_hash: bytes) -> bool:
    """Verify user password against stored hash."""
    password_bytes = password.encode('utf-8')
    
    # Use checkpw for secure comparison
    is_valid = bcrypt.checkpw(password_bytes, stored_hash)
    
    return is_valid

# Usage from database
stored_hash = user['password_hash'].encode('utf-8')  # Convert back to bytes
if authenticate_user("john_doe", "SecureP@ss123!", stored_hash):
    print("Login successful")
else:
    print("Invalid credentials")
```

### Push to Production (Deployment Checklist)

Before deploying password hashing to production:

```python
import bcrypt
import time

def validate_bcrypt_config():
    """Validate bcrypt configuration for production."""
    test_password = b"test_password_123"
    
    # Test 1: Verify default rounds performance
    start = time.time()
    hashed = bcrypt.hashpw(test_password, bcrypt.gensalt(rounds=12))
    elapsed = time.time() - start
    
    print(f"Hashing time (12 rounds): {elapsed:.3f}s")
    
    # Recommended: 0.1-0.5 seconds per hash
    if elapsed < 0.1:
        print("WARNING: Hashing too fast, consider increasing rounds")
    elif elapsed > 1.0:
        print("WARNING: Hashing too slow, may impact performance")
    else:
        print("OK: Hashing time is acceptable")
    
    # Test 2: Verify checkpw works
    if bcrypt.checkpw(test_password, hashed):
        print("OK: Password verification working")
    else:
        print("ERROR: Password verification failed")
    
    # Test 3: Check hash format
    hash_str = hashed.decode('utf-8')
    if hash_str.startswith('$2b$12$'):
        print("OK: Hash format is correct ($2b$ prefix, 12 rounds)")
    else:
        print(f"WARNING: Unexpected hash format: {hash_str[:10]}...")

# Run validation before deployment
validate_bcrypt_config()
```

## Complete Authentication Example
A complete user registration and login system:

```python
import bcrypt

class PasswordManager:
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash_password(self, password: str) -> bytes:
        """Hash a password for storage."""
        if not isinstance(password, bytes):
            password = password.encode('utf-8')
        
        if len(password) > 72:
            raise ValueError("Password must be 72 bytes or less")
        
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password, salt)
    
    def verify_password(self, password: str, hashed: bytes) -> bool:
        """Verify a password against a stored hash."""
        if not isinstance(password, bytes):
            password = password.encode('utf-8')
        
        return bcrypt.checkpw(password, hashed)

# Usage
password_manager = PasswordManager(rounds=12)

# User registration
user_password = "SecureP@ssw0rd!"
hashed_password = password_manager.hash_password(user_password)
# Store hashed_password in database

# User login
input_password = "SecureP@ssw0rd!"
if password_manager.verify_password(input_password, hashed_password):
    print("Login successful")
else:
    print("Invalid credentials")
```

## Best Practices
### Security Recommendations

1. **Always use bcrypt.gensalt()** - Never reuse salts or use static salts
2. **Use at least 12 rounds** - Adjust based on your performance requirements
3. **Store full hash** - The hash includes the salt and work factor, store the entire output
4. **Handle long passwords** - Either enforce a 72-byte limit or pre-hash with SHA-256
5. **Use checkpw() for verification** - Don't manually compare hashes

### Migration from Other Libraries

**From py-bcrypt:**
```python
# py-bcrypt (old)
import bcrypt
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# bcrypt 5.0 (same API)
import bcrypt
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
```

**From passlib:**
```python
# passlib (old)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password")
verified = pwd_context.verify("password", hashed)

# bcrypt 5.0 (new)
import bcrypt
hashed = bcrypt.hashpw(b"password", bcrypt.gensalt())
verified = bcrypt.checkpw(b"password", hashed)
```

### Database Storage

Store the complete hash string in a VARCHAR column:

```sql
-- PostgreSQL example
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL  -- bcrypt hashes are 60 characters
);
```

```python
import bcrypt
import psycopg2

# Register user
password = b"user_password"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

conn = psycopg2.connect("dbname=test user=postgres")
cur = conn.cursor()
cur.execute(
    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
    ("username", hashed.decode('utf-8'))
)
conn.commit()

# Verify password
cur.execute("SELECT password_hash FROM users WHERE username = %s", ("username",))
stored_hash = cur.fetchone()[0].encode('utf-8')

if bcrypt.checkpw(password, stored_hash):
    print("Authentication successful")
```

## See Also
- [Advanced Usage and Examples](reference/01-advanced-usage.md) - Complete examples, advanced patterns, and troubleshooting

## Advanced Topics
## Advanced Topics

- [Advanced Usage](reference/01-advanced-usage.md)

