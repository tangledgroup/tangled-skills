# Password Hashing with argon2-cffi

Complete guide to password hashing workflows and authentication patterns using the high-level API.

## Basic Operations

### Creating a PasswordHasher Instance

```python
from argon2 import PasswordHasher

# Default instance with RFC 9106 LOW_MEMORY profile
ph = PasswordHasher()

# Equivalent explicit parameters:
ph = PasswordHasher(
    time_cost=3,           # Number of iterations
    memory_cost=65536,     # Memory in KiB (64 MiB)
    parallelism=4,         # Number of threads
    hash_len=32,           # Hash length in bytes
    salt_len=16,           # Salt length in bytes
    type=argon2.low_level.Type.ID  # Argon2id (default)
)
```

### Hashing Passwords

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# String password
hash1 = ph.hash("my_secret_password")
print(hash1)
# $argon2id$v=19$m=65536,t=3,p=4$<base64-salt>$<base64-hash>

# Bytes password
hash2 = ph.hash(b"my_secret_password")

# With custom salt (not recommended unless necessary)
import os
custom_salt = os.urandom(16)
hash3 = ph.hash("password", salt=custom_salt)
```

**Important**: The hash includes the algorithm identifier, version, all parameters, salt, and hash value in a standardized format. Store this entire string in your database.

### Verifying Passwords

```python
from argon2 import PasswordHasher
import argon2.exceptions

ph = PasswordHasher()
stored_hash = "$argon2id$v=19$m=65536,t=3,p=4$..."

# Verify returns True on success
try:
    ph.verify(stored_hash, "user_provided_password")
    print("Authentication successful")
except argon2.exceptions.VerifyMismatchError:
    print("Wrong password")
except argon2.exceptions.InvalidHashError:
    print("Hash format is invalid")
except argon2.exceptions.VerificationError as e:
    print(f"Verification failed: {e}")
```

**Note**: `verify()` raises exceptions instead of returning False to prevent accidental silent failures (Pythonic EAFP principle).

### Checking for Rehash

```python
from argon2 import PasswordHasher

ph = PasswordHasher()
stored_hash = "$argon2id$v=19$m=65536,t=3,p=4$..."

# Check if hash was created with current parameters
if ph.check_needs_rehash(stored_hash):
    # Parameters have changed, rehash on next login
    print("Hash needs to be updated")
```

This is essential when upgrading argon2-cffi versions or changing security policies.

## Authentication Patterns

### Simple Login Function

```python
import argon2
from argon2.exceptions import VerifyMismatchError

ph = argon2.PasswordHasher()

def authenticate(username, password, user_db):
    """Authenticate user against stored hash."""
    user = user_db.get_user(username)
    
    if not user or not user.password_hash:
        # Perform constant-time comparison to prevent timing attacks
        argon2.low_level.compare_digest(b"", b"dummy")
        return False
    
    try:
        ph.verify(user.password_hash, password)
    except VerifyMismatchError:
        return False
    
    # Update hash if parameters changed
    if ph.check_needs_rehash(user.password_hash):
        new_hash = ph.hash(password)
        user_db.update_password_hash(username, new_hash)
    
    return True
```

### Web Application Integration (Flask)

```python
from flask import Flask, request, abort
import argon2

app = Flask(__name__)
ph = argon2.PasswordHasher()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = db.users.find_one({'username': username})
    
    if not user:
        abort(401)
    
    try:
        ph.verify(user['password_hash'], password)
    except argon2.exceptions.VerifyMismatchError:
        abort(401)
    
    # Rehash if needed
    if ph.check_needs_rehash(user['password_hash']):
        new_hash = ph.hash(password)
        db.users.update_one(
            {'username': username},
            {'$set': {'password_hash': new_hash}}
        )
    
    # Create session
    session['user_id'] = user['_id']
    return redirect('/dashboard')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Check if user exists
    if db.users.find_one({'username': username}):
        abort(400)  # User already exists
    
    # Hash password and store
    password_hash = ph.hash(password)
    user_id = db.users.insert_one({
        'username': username,
        'password_hash': password_hash
    }).inserted_id
    
    return redirect('/login')
```

### Async Authentication (FastAPI)

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import argon2
import asyncio

app = FastAPI()
ph = argon2.PasswordHasher()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(credentials: LoginRequest):
    user = await db.get_user(credentials.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
        # Run in thread pool to avoid blocking event loop
        await asyncio.get_event_loop().run_in_executor(
            None, ph.verify, user.hash, credentials.password
        )
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Rehash in background if needed
    if ph.check_needs_rehash(user.hash):
        new_hash = ph.hash(credentials.password)
        asyncio.create_task(db.update_hash(user.id, new_hash))
    
    return {"access_token": generate_token(user.id)}
```

## Hash Format

Argon2 hashes follow the PHC string format:

```
$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
              ↑    ↑     ↑    ↑  ↑        ↑
              |    |     |    |  |        └─ Base64-encoded hash (32 bytes → 43 chars)
              |    |     |    |  └────────── Base64-encoded salt (16 bytes → 22 chars)
              |    |     |    └────────────── Parallelism (threads)
              |    |     └─────────────────── Time cost (iterations)
              |    └───────────────────────── Memory cost in KiB
              └────────────────────────────── Argon2 variant (id, i, or d)
```

### Example Hash Breakdown

```
$argon2id$v=19$m=65536,t=3,p=4$MIIRqgvgQbgj220jfp0MPA$YfwJSVjtjSU0zzV/P3S9nnQ/USre2wvJMjfCIjrTQbg
```

- Algorithm: `argon2id` (hybrid mode)
- Version: `19` (Argon2 version 1.9)
- Memory: `65536` KiB = 64 MiB
- Time: `3` iterations
- Parallelism: `4` threads
- Salt: `MIIRqgvgQbgj220jfp0MPA` (base64, 16 bytes)
- Hash: `YfwJSVjtjSU0zzV/P3S9nnQ/USre2wvJMjfCIjrTQbg` (base64, 32 bytes)

## Best Practices

### Do's

✅ Always use the high-level `PasswordHasher` API for password hashing
✅ Store the complete hash string (includes all parameters and salt)
✅ Call `check_needs_rehash()` after successful authentication
✅ Use adequate memory cost (at least 64 MiB for new applications)
✅ Test verification time in your deployment environment

### Don'ts

❌ Never implement your own salt generation (PasswordHasher handles this)
❌ Don't store passwords in plaintext or reversible encryption
❌ Don't use Argon2 for non-password purposes without understanding implications
❌ Don't reduce parameters below recommended minimums without testing
❌ Don't ignore `check_needs_rehash()` in production systems

### Security Considerations

1. **Memory cost**: Higher is more secure against GPU attacks. Minimum 64 MiB recommended.

2. **Time cost**: Balance security vs user experience. 40-500ms verification time typical.

3. **Parallelism**: Match to available CPU cores. Default of 4 works well on most systems.

4. **Hash length**: 32 bytes (256 bits) is sufficient for password verification.

5. **Salt length**: 16 bytes prevents rainbow table attacks. Never reuse salts.

## Common Use Cases

### Password Reset Tokens

```python
import secrets
import argon2

ph = argon2.PasswordHasher()

def generate_reset_token(user_id):
    """Generate and hash a password reset token."""
    token = secrets.token_urlsafe(32)
    token_hash = ph.hash(token)
    
    # Store token_hash with expiration in database
    db.reset_tokens.insert_one({
        'user_id': user_id,
        'token_hash': token_hash,
        'expires_at': datetime.now() + timedelta(hours=1)
    })
    
    # Send plaintext token to user's email
    send_email(user.email, f"Reset link: https://app.com/reset/{token}")

def verify_reset_token(user_id, token):
    """Verify reset token is valid."""
    record = db.reset_tokens.find_one({
        'user_id': user_id,
        'expires_at': {'$gt': datetime.now()}
    })
    
    if not record:
        return False
    
    try:
        ph.verify(record['token_hash'], token)
        # Delete token after use
        db.reset_tokens.delete_one({'_id': record['_id']})
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
```

### API Key Hashing

```python
import secrets
import argon2

ph = argon2.PasswordHasher()

def create_api_key(user_id):
    """Generate and store hashed API key."""
    # Generate secure random key
    api_key = secrets.token_urlsafe(32)
    
    # Hash for storage
    api_key_hash = ph.hash(api_key)
    
    # Store hash, return plaintext key once
    db.api_keys.insert_one({
        'user_id': user_id,
        'key_hash': api_key_hash,
        'created_at': datetime.now()
    })
    
    return api_key  # Show to user once!

def verify_api_key(provided_key):
    """Find API key by verifying against stored hashes."""
    for record in db.api_keys.find({}):
        try:
            ph.verify(record['key_hash'], provided_key)
            return record['user_id']
        except argon2.exceptions.VerifyMismatchError:
            continue
    
    return None
```
