# API Reference

Complete documentation of argon2-cffi APIs including high-level, low-level, and exception classes.

## High-Level API

### PasswordHasher

Main class for password hashing operations.

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=argon2.low_level.Type.ID
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_cost` | int | 3 | Number of iterations |
| `memory_cost` | int | 65536 | Memory in KiB |
| `parallelism` | int | 4 | Thread count |
| `hash_len` | int | 32 | Hash length in bytes |
| `salt_len` | int | 16 | Salt length in bytes |
| `type` | Type | Type.ID | Argon2 variant (ID, I, or D) |

#### Methods

##### hash()

```python
hash = ph.hash(password, *, salt=None)
```

Hash a password and return encoded hash string.

**Parameters:**
- `password` (str | bytes): Password to hash
- `salt` (bytes | None, optional): Custom salt (not recommended)

**Returns:** str - Encoded Argon2 hash

**Raises:**
- `HashingError`: If hashing fails

**Example:**
```python
ph = PasswordHasher()
hash = ph.hash("secret_password")
# $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
```

##### verify()

```python
ph.verify(hash, password)
```

Verify password matches hash.

**Parameters:**
- `hash` (str | bytes): Encoded Argon2 hash
- `password` (str | bytes): Password to verify

**Returns:** Literal[True] on success

**Raises:**
- `VerifyMismatchError`: Password doesn't match
- `InvalidHashError`: Hash format is invalid
- `VerificationError`: Other verification failures

**Example:**
```python
try:
    ph.verify(stored_hash, "user_password")
    print("Authentication successful")
except VerifyMismatchError:
    print("Wrong password")
```

##### check_needs_rehash()

```python
needs_rehash = ph.check_needs_rehash(hash)
```

Check if hash was created with current parameters.

**Parameters:**
- `hash` (str | bytes): Encoded Argon2 hash

**Returns:** bool - True if parameters differ from instance

**Example:**
```python
if ph.check_needs_rehash(user_hash):
    new_hash = ph.hash(password)
    db.update_hash(user_id, new_hash)
```

##### from_parameters() (classmethod)

```python
ph = PasswordHasher.from_parameters(params)
```

Create PasswordHasher from parameter profile.

**Parameters:**
- `params`: Parameter profile object

**Returns:** PasswordHasher instance

**Example:**
```python
from argon2.profiles import RFC_9106_LOW_MEMORY

ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
```

## Profiles Module

Standardized parameter profiles from RFC 9106.

```python
from argon2.profiles import RFC_9106_LOW_MEMORY, RFC_9106_HIGH_MEMORY
```

### RFC_9106_LOW_MEMORY

"SECOND RECOMMENDED" profile for general use.

- memory_cost: 65536 KiB (64 MiB)
- time_cost: 3 iterations
- parallelism: 4 threads
- hash_len: 32 bytes
- salt_len: 16 bytes
- type: Argon2id

### RFC_9106_HIGH_MEMORY

"FIRST RECOMMENDED" profile for high-security applications.

- memory_cost: 2097152 KiB (2 GiB)
- time_cost: 1 iteration
- parallelism: 4 threads
- hash_len: 32 bytes
- salt_len: 16 bytes
- type: Argon2id

### get_default_parameters()

```python
params = argon2.profiles.get_default_parameters()
```

Get current platform's default parameters.

**Returns:** Parameter profile object

## Low-Level API

Direct access to Argon2 functions for advanced use cases.

### hash_password()

```python
from argon2.low_level import hash_password, Type

hash = hash_password(
    password=b"secret",
    salt=b"16_byte_salt_!!",
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID
)
```

Hash password with explicit parameters.

**Returns:** bytes - Raw hash (not encoded)

### verify_password()

```python
from argon2.low_level import verify_password

try:
    verify_password(
        password=b"secret",
        hash=$argon2id$v=19$m=65536,t=3,p=4$...
    )
except VerifyMismatchError:
    print("Wrong password")
```

Verify password against encoded hash.

### Type Enum

Argon2 variant selection:

```python
from argon2.low_level import Type

Type.ID  # Argon2id - hybrid mode (recommended)
Type.I   # Argon2i - side-channel resistant
Type.D   # Argon2d - fastest, GPU-optimized
```

## Exceptions

All exceptions inherit from `argon2.exceptions.Argon2Error`.

### VerifyMismatchError

Raised when password doesn't match hash.

```python
from argon2.exceptions import VerifyMismatchError

try:
    ph.verify(hash, "wrong_password")
except VerifyMismatchError:
    print("Authentication failed")
```

### InvalidHashError

Raised when hash format is malformed or corrupted.

```python
from argon2.exceptions import InvalidHashError

try:
    ph.verify("$invalid_hash_format", "password")
except InvalidHashError as e:
    print(f"Invalid hash: {e}")
```

### VerificationError

Base class for verification failures (includes VerifyMismatchError).

```python
from argon2.exceptions import VerificationError

try:
    ph.verify(hash, password)
except VerificationError as e:
    # Catches both mismatch and other verification errors
    print(f"Verification failed: {e}")
```

### HashingError

Raised when hash creation fails.

```python
from argon2.exceptions import HashingError

try:
    ph.hash("password")
except HashingError as e:
    print(f"Hashing failed: {e}")
```

## Constants

Default parameter values used by PasswordHasher:

```python
import argon2

argon2.DEFAULT_RANDOM_SALT_LENGTH  # 16 bytes
argon2.DEFAULT_HASH_LENGTH         # 32 bytes
argon2.DEFAULT_TIME_COST           # 3 iterations
argon2.DEFAULT_MEMORY_COST         # 65536 KiB (64 MiB)
argon2.DEFAULT_PARALLELISM         # 4 threads
```

These values come from `RFC_9106_LOW_MEMORY` profile but may vary by platform.

## CLI Interface

Command-line tool for testing and benchmarking.

### Basic Usage

```bash
# Hash a password
echo "mypassword" | python -m argon2

# Verify a hash
python -m argon2 --verify "$argon2id$v=19$m=65536,t=3,p=4$..."

# Benchmark with profile
python -m argon2 --profile RFC_9106_LOW_MEMORY
python -m argon2 --profile RFC_9106_HIGH_MEMORY
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--profile NAME` | Use predefined profile |
| `-m KIB` | Memory cost in KiB |
| `-t ITER` | Time cost (iterations) |
| `-p THREADS` | Parallelism (threads) |
| `--verify HASH` | Verify password against hash |

### Benchmarking Example

```bash
$ python -m argon2 --profile RFC_9106_LOW_MEMORY

Running Argon2id 100 times with:
hash_len: 32 bytes
memory_cost: 65536 KiB
parallelism: 4 threads
time_cost: 3 iterations

Measuring...

45.2ms per password verification
```

## Type Hints

Full type annotations for static analysis:

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from typing import Literal

ph: PasswordHasher = PasswordHasher()

def authenticate(password_hash: str, password: str) -> bool:
    """Verify password and return success status."""
    try:
        result: Literal[True] = ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

def needs_update(password_hash: str) -> bool:
    """Check if hash parameters are outdated."""
    return ph.check_needs_rehash(password_hash)
```

## Platform Notes

### GIL Release

argon2-cffi releases the Python GIL during hashing operations, allowing concurrent hashing in multiple threads:

```python
import threading
import argon2

ph = argon2.PasswordHasher()

def hash_in_thread(password, result_list, index):
    result_list[index] = ph.hash(password)

# Multiple threads can hash simultaneously
threads = []
results = [None] * 10
for i in range(10):
    t = threading.Thread(target=hash_in_thread, args=("password", results, i))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# All hashes completed in parallel
```

### Async Support

For async applications, run hashing in thread pool:

```python
import asyncio
import argon2

ph = argon2.PasswordHasher()

async def hash_async(password: str) -> str:
    """Hash password without blocking event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, ph.hash, password)

async def verify_async(hash: str, password: str) -> bool:
    """Verify password without blocking event loop."""
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, ph.verify, hash, password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
```
