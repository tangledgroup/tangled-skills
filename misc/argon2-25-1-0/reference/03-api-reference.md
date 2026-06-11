# API Reference

## PasswordHasher

The high-level class for password hashing with sensible defaults. Uses Argon2id by default and generates a random salt for each hash.

### Construction

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,       # iterations (default: from RFC_9106_LOW_MEMORY)
    memory_cost=65536, # kibibytes
    parallelism=4,     # threads
    hash_len=32,       # output hash length in bytes
    salt_len=16,       # random salt length in bytes
    encoding="utf-8",  # encoding for str passwords
    type=Type.ID,      # Argon2 variant
)
```

### from_parameters()

Construct a `PasswordHasher` from a `Parameters` object:

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_HIGH_MEMORY

ph = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)
```

### hash(password, *, salt=None) → str

Hash a password and return an encoded Argon2 hash string.

```python
hash = ph.hash("my secret password")
# '$argon2id$v=19$m=65536,t=3,p=4$...'
```

- Accepts `str` or `bytes` for password
- If `salt` is `None`, a random salt is securely generated
- **Do not pass a custom salt unless you know exactly what you are doing**
- Raises `argon2.exceptions.HashingError` on failure

### verify(hash, password) → Literal[True]

Verify that a password matches a hash. Returns `True` on success; raises exception on failure.

```python
ph.verify(stored_hash, "correct password")  # returns True
ph.verify(stored_hash, "wrong password")    # raises VerifyMismatchError
```

- Accepts `str` or `bytes` for both arguments
- Automatically detects hash type from the `$argon2*` prefix
- Raises `VerifyMismatchError` if password is wrong (subclass of `VerificationError`)
- Raises `InvalidHashError` if hash format is clearly invalid

### check_needs_rehash(hash) → bool

Check whether a hash was created using the instance's current parameters.

```python
if ph.check_needs_rehash(stored_hash):
    # Rehash with current (possibly upgraded) parameters
    db.update_hash(user_id, ph.hash(cleartext_password))
```

- Accepts `str` or `bytes` for hash
- Returns `True` if the hash parameters differ from the hasher's parameters
- Best practice: check and rehash after each successful login

### Properties

Read-only access to current parameters:

- `ph.time_cost` → int
- `ph.memory_cost` → int
- `ph.parallelism` → int
- `ph.hash_len` → int
- `ph.salt_len` → int
- `ph.type` → Type

### Default Constants

```python
from argon2 import (
    DEFAULT_TIME_COST,       # 3
    DEFAULT_MEMORY_COST,     # 65536
    DEFAULT_PARALLELISM,     # 4
    DEFAULT_HASH_LENGTH,     # 32
    DEFAULT_RANDOM_SALT_LENGTH,  # 16
)
```

These are taken from `argon2.profiles.RFC_9106_LOW_MEMORY` but may vary by platform (e.g., WebAssembly).

---

## Profiles Module

```python
from argon2 import profiles
```

Predefined parameter sets:

- **RFC_9106_HIGH_MEMORY** — FIRST RECOMMENDED per RFC 9106 (2 GiB)
- **RFC_9106_LOW_MEMORY** — SECOND RECOMMENDED per RFC 9106 (64 MiB, default)
- **PRE_21_2** — pre-RFC defaults from argon2-cffi 18.2.0–21.1.0
- **CHEAPEST** — minimal parameters for testing only

```python
from argon2.profiles import get_default_parameters

params = get_default_parameters()
# Returns RFC_9106_LOW_MEMORY, adjusted for current platform
# (parallelism=1 on WebAssembly)
```

---

## Parameters Dataclass

```python
from argon2 import Parameters

params = Parameters(
    type=Type.ID,
    version=19,
    salt_len=16,
    hash_len=32,
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
)
```

Used by `extract_parameters()` and `PasswordHasher.from_parameters()`.

---

## extract_parameters(hash) → Parameters

Extract parameters from an encoded Argon2 hash string:

```python
from argon2 import extract_parameters

params = extract_parameters("$argon2id$v=19$m=65536,t=3,p=4$abc$def")
print(params.type)        # Type.ID
print(params.memory_cost) # 65536
print(params.time_cost)   # 3
print(params.parallelism) # 4
print(params.version)     # 19
```

Raises `InvalidHashError` if the hash format is invalid. Supports both v1.2 (version 18) and v1.3 (version 19) hashes.

---

## Low-Level API

The `argon2.low_level` module provides direct access to Argon2 functions. This is a "Hazardous Materials" module — use only if you know exactly what you are doing.

### Type Enum

```python
from argon2.low_level import Type

Type.D   # Argon2d
Type.I   # Argon2i
Type.ID  # Argon2id
```

### ARGON2_VERSION

The latest supported Argon2 version number (currently 19 = v1.3).

### hash_secret() → bytes

Hash a secret and return an **encoded** hash string (as bytes):

```python
from argon2.low_level import hash_secret, Type

result = hash_secret(
    secret=b"my secret",
    salt=os.urandom(16),
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID,
    version=19,  # optional, defaults to ARGON2_VERSION
)
# b'$argon2id$v=19$m=65536,t=3,p=4$...'
```

Returns an encoded hash that can be passed directly to `verify_secret()`. Raises `HashingError` on failure.

### hash_secret_raw() → bytes

Same as `hash_secret()` but returns raw hash bytes (not encoded):

```python
from argon2.low_level import hash_secret_raw, Type

raw = hash_secret_raw(
    secret=b"secret",
    salt=b"somesalt",
    time_cost=1,
    memory_cost=8,
    parallelism=1,
    hash_len=8,
    type=Type.D,
)
# b'\xe4n\xf5\xc8|\xa3>\x1d'
```

### verify_secret(hash, secret, type) → Literal[True]

Verify a secret against an encoded hash:

```python
from argon2.low_level import verify_secret, Type

verify_secret(encoded_hash, b"correct secret", Type.ID)  # returns True
verify_secret(encoded_hash, b"wrong secret", Type.ID)    # raises VerifyMismatchError
```

Raises `VerifyMismatchError` on wrong password, `VerificationError` for other failures.

### core(context, type) → int

Direct binding to the C `argon2_ctx` function. Works on raw CFFI data structures. You are responsible for all sanity checks and buffer management. Use at your own peril — argon2-cffi itself does not use this binding.

Requires access to `argon2.low_level.ffi` and `argon2.low_level.lib`:

```python
from argon2.low_level import Type, core, ffi, lib

# Build an argon2_context struct with pwd, salt, secret, ad fields
# Call core(ctx, Type.ID.value)
# Check return value against lib.ARGON2_OK
```

Useful for testing RFC 9106 test vectors that include secret and associated data.

### error_to_str(error) → str

Convert an Argon2 error code to a human-readable string:

```python
from argon2.low_level import error_to_str

msg = error_to_str(rv)  # rv from core() or other low-level calls
```

---

## Exceptions

All exceptions inherit from `Argon2Error` (except `InvalidHashError` which inherits from `ValueError`).

### VerificationError

Base exception for verification failures. Contains the original Argon2 error message in `args[0]`.

### VerifyMismatchError

Subclass of `VerificationError`. Raised when verification fails because the password does not match the hash. This is the specific "wrong password" case.

### HashingError

Raised when hashing fails. Contains the original Argon2 error message in `args[0]`.

### InvalidHashError

Raised when a hash is so clearly invalid it cannot be passed to Argon2 (e.g., wrong prefix, malformed structure). Inherits from `ValueError`.

Added in 23.1.0 as replacement for the deprecated `InvalidHash` alias.

### UnsupportedParametersError

Raised when the current platform does not support the given parameters. For example, parallelism must be 1 in WebAssembly environments. Added in 25.1.0.

---

## Deprecated APIs

The following functions from the original release are deprecated (raise `DeprecationWarning` since 23.1.0, scheduled for removal):

- `argon2.hash_password()` — use `PasswordHasher.hash()` instead
- `argon2.hash_password_raw()` — use `argon2.low_level.hash_secret_raw()` instead
- `argon2.verify_password()` — use `PasswordHasher.verify()` or `argon2.low_level.verify_secret()` instead
- `argon2.exceptions.InvalidHash` — use `InvalidHashError` instead
