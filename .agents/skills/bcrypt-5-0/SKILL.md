---
name: bcrypt-5-0
description: A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password storage, verifying passwords, or deriving cryptographic keys with bcrypt_pbkdf.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - password-hashing
  - cryptography
  - security
  - authentication
  - key-derivation
category: security
required_environment_variables: []
---

# bcrypt-5-0

A Python library for modern password hashing using the bcrypt algorithm. Provides secure password storage, verification, and key derivation functions implemented in Rust for performance and safety.

## When to Use

- Hashing passwords before storing them in a database
- Verifying user-provided passwords against stored hashes
- Deriving cryptographic keys from passwords using bcrypt_pbkdf
- Migrating from other password hashing libraries (py-bcrypt, passlib)
- Building authentication systems requiring industry-standard password protection

## Setup

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

## Troubleshooting

### "password cannot be longer than 72 bytes"

**Cause:** Password exceeds bcrypt's maximum length.

**Solution:** Pre-hash long passwords:

```python
import bcrypt
import hashlib
import base64

def hash_long_password(password: bytes) -> bytes:
    if len(password) <= 72:
        return bcrypt.hashpw(password, bcrypt.gensalt())
    else:
        # Hash with SHA-256 first
        password_hash = hashlib.sha256(password).digest()
        return bcrypt.hashpw(
            base64.b64encode(password_hash),
            bcrypt.gensalt()
        )
```

### "Invalid salt" ValueError

**Cause:** Malformed salt string passed to `hashpw()`.

**Solution:** Ensure salt is generated with `bcrypt.gensalt()` or is a valid bcrypt hash:

```python
import bcrypt

# Correct usage
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)

# Or reuse an existing hash as salt (for verification)
existing_hash = b'$2b$12$...'
hashed = bcrypt.hashpw(password, existing_hash)
```

### Build failures when installing from source

**Cause:** Missing Rust compiler or build dependencies.

**Solution:** Install required dependencies:

```bash
# Debian/Ubuntu
sudo apt-get install build-essential cargo

# Fedora/RHEL
sudo yum install gcc cargo

# Then reinstall bcrypt
pip install --force-reinstall bcrypt
```

### "Unsupported prefix" error

**Cause:** Using deprecated `2y` prefix or invalid prefix value.

**Solution:** Use supported prefixes only:

```python
import bcrypt

# Valid prefixes
salt = bcrypt.gensalt(prefix=b"2b")  # Recommended
salt = bcrypt.gensalt(prefix=b"2a")  # Legacy compatibility

# Invalid (raises ValueError)
# salt = bcrypt.gensalt(prefix=b"2y")  # Not supported in gensalt
```

## API Reference

### `bcrypt.gensalt(rounds=12, prefix=b"2b")`

Generate a random salt for password hashing.

**Parameters:**
- `rounds` (int, default 12): Logarithmic work factor, range 4-31
- `prefix` (bytes, default b"2b"): Version prefix, must be b"2a" or b"2b"

**Returns:** bytes - A base64-encoded salt string starting with `$2b$` or `$2a$`

**Raises:**
- `ValueError`: If rounds < 4 or > 31
- `ValueError`: If prefix is not b"2a" or b"2b"

### `bcrypt.hashpw(password, salt)`

Hash a password using bcrypt.

**Parameters:**
- `password` (bytes): The password to hash (max 72 bytes)
- `salt` (bytes): Salt from `gensalt()` or an existing hash

**Returns:** bytes - The hashed password (60 characters for default rounds)

**Raises:**
- `ValueError`: If password > 72 bytes
- `ValueError`: If salt is invalid

### `bcrypt.checkpw(password, hashed_password)`

Verify a password against a stored hash.

**Parameters:**
- `password` (bytes): The password to verify
- `hashed_password` (bytes): Previously hashed password

**Returns:** bool - True if password matches, False otherwise

**Note:** Performs constant-time comparison to prevent timing attacks.

### `bcrypt.kdf(password, salt, desired_key_bytes, rounds, ignore_few_rounds=False)`

Derive a cryptographic key using bcrypt_pbkdf.

**Parameters:**
- `password` (bytes): Password (must not be empty)
- `salt` (bytes): Salt (must not be empty)
- `desired_key_bytes` (int): Output key length, 1-512 bytes
- `rounds` (int): Number of iterations, must be >= 1
- `ignore_few_rounds` (bool, default False): Suppress warning for rounds < 50

**Returns:** bytes - Derived key of specified length

**Raises:**
- `ValueError`: If password or salt is empty
- `ValueError`: If desired_key_bytes < 1 or > 512
- `ValueError`: If rounds < 1

**Emits:**
- `UserWarning`: If rounds < 50 and ignore_few_rounds is False

## Version Control Integration

When working with bcrypt in version-controlled projects, follow these best practices:

### Add Password Hashing to Project

Install bcrypt as a dependency and add to your project:

```bash
# Add bcrypt to dependencies
pip install bcrypt

# Or add to requirements.txt
echo "bcrypt>=5.0.0" >> requirements.txt

# Commit the dependency change
git add requirements.txt
git commit -m "chore(deps): add bcrypt for password hashing"
```

### Commit Password Hashing Implementation

When implementing password hashing, use descriptive commit messages:

```bash
# Add authentication module with bcrypt
git add src/auth/password.py
git commit -m "feat(auth): implement secure password hashing with bcrypt

- Add hash_password() function using bcrypt.gensalt()
- Add verify_password() function using bcrypt.checkpw()
- Configure 12 rounds for production use
- Handle passwords > 72 bytes with SHA-256 pre-hashing"
```

### Push Authentication Changes

Before pushing password-related code, ensure secrets are not committed:

```bash
# Check for hardcoded passwords or keys
git diff --cached | grep -i "password\|secret\|key"

# Verify .gitignore excludes sensitive files
cat .gitignore
# Should include: .env, *.pem, secrets/, config/local.yml

# Push to remote
git push origin feature/password-authentication
```

### .gitignore for Password Security

Add these patterns to your `.gitignore`:

```gitignore
# Environment files with credentials
.env
.env.local
.env.*.local

# Local configuration with secrets
config/local.yml
settings_local.py

# Key files
*.pem
*.key
secrets/

# IDE password caches
.idea/inspectionProfiles/
.vscode/secrets
```

### Example: Full Workflow

Complete example of adding bcrypt to a project:

```bash
# 1. Install and add dependency
pip install bcrypt
echo "bcrypt>=5.0.0" >> requirements.txt

# 2. Create password utility
cat > src/utils/passwords.py << 'EOF'
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
EOF

# 3. Add and commit changes
git add requirements.txt src/utils/passwords.py
git commit -m "feat: add secure password hashing utilities

- Implement hash_password() with bcrypt
- Implement verify_password() for authentication
- Use 12 rounds for balanced security/performance"

# 4. Push to remote
git push origin main
```

## Alternatives

While bcrypt remains acceptable for password storage, consider these alternatives:

**Argon2id (recommended for new projects):**
```python
pip install argon2-cffi
```
- Winner of the Password Hashing Competition
- More resistant to GPU attacks
- Configable memory usage

**scrypt:**
```python
# Built into Python 3.6+
import hashlib
hashed = hashlib.scrypt(password, salt=salt, n=2**14, r=8, p=1)
```
- Available in Python standard library
- High memory usage deters brute-force attacks

**When to use bcrypt:**
- Legacy system compatibility required
- Simpler configuration than Argon2
- Proven track record in production systems
