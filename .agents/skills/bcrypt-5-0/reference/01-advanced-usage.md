# bcrypt-5-0 - Advanced Usage

This reference covers advanced topics, complete examples, and detailed configuration.

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
