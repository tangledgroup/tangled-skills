---
name: argon2-25
description: Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi. Use when implementing secure password storage, user authentication systems, or migrating legacy password hashes to modern standards.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - password-hashing
  - authentication
  - cryptography
  - argon2
  - security
category: security

external_references:
  - https://argon-cffi.readthedocs.io/
  - https://github.com/hynek/argon2_cffi
---

# argon2-25 (argon2-cffi)

## Overview

Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi. Use when implementing secure password storage, user authentication systems, or migrating legacy password hashes to modern standards.


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi. Use when implementing secure password storage, user authentication systems, or migrating legacy password hashes to modern standards.

Comprehensive Python toolkit for secure password hashing and verification using the Argon2 algorithm, winner of the Password Hashing Competition. Provides both high-level APIs for common use cases and low-level access for advanced customization.

## When to Use

- Implementing password storage in new applications
- Migrating legacy password hashes (bcrypt, PBKDF2, scrypt) to Argon2
- Building authentication systems requiring modern cryptographic standards
- Needing RFC 9106 compliant password hashing parameters
- Requiring async password hashing for non-blocking operations
- Customizing hash parameters for specific security/performance requirements

## Setup

Install the library:

```bash
pip install argon2-cffi
```

For async support:

```bash
pip install argon2-cffi-bindings
```

## Quick Start

### Basic Password Hashing

The high-level API uses RFC 9106 recommended parameters by default:

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hash a password
hash = ph.hash("correct horse battery staple")
# Output: $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>

# Verify a password
ph.verify(hash, "correct horse battery staple")  # Returns True

# Wrong password raises exception
try:
    ph.verify(hash, "wrong_password")
except argon2.exceptions.VerifyMismatchError:
    print("Password incorrect")
```

### Production Login Pattern

```python
import argon2

ph = argon2.PasswordHasher()

def login(db, user, password):
    """Authenticate user and rehash if parameters outdated."""
    hash = db.get_password_hash_for_user(user)
    
    # Verify password - raises exception if wrong
    ph.verify(hash, password)
    
    # Check if hash needs rehashing due to parameter changes
    if ph.check_needs_rehash(hash):
        new_hash = ph.hash(password)
        db.set_password_hash_for_user(user, new_hash)
    
    return True
```

See [Password Hashing Guide](references/01-password-hashing.md) for detailed examples and best practices.

## Preconfigured Profiles

Use standardized parameter profiles from RFC 9106:

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY, RFC_9106_HIGH_MEMORY

# Low memory profile (default) - 64 MiB, ~50ms verification
ph_low = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)

# High memory profile - 2 GiB, ~866ms verification
ph_high = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)
```

See [Parameter Selection Guide](references/02-parameters.md) for choosing the right profile.

## Reference Files

- [`references/01-password-hashing.md`](references/01-password-hashing.md) - Complete password hashing workflows and authentication patterns
- [`references/02-parameters.md`](references/02-parameters.md) - Parameter selection, RFC 9106 profiles, and performance tuning
- [`references/03-api-reference.md`](references/03-api-reference.md) - Full API documentation including low-level functions and exceptions
- [`references/04-migration.md`](references/04-migration.md) - Migrating from bcrypt, PBKDF2, scrypt to Argon2

## Troubleshooting

### Memory Issues in Docker

The default 64 MiB memory requirement can cause swapping in constrained environments:

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY

# Use lower memory profile for containers
ph = PasswordHasher(
    memory_cost=131072,  # 128 MiB instead of 64 MiB
    time_cost=2,         # Lower iterations
    parallelism=2        # Fewer threads
)
```

### Verification Time Tuning

Test performance with the CLI before deploying:

```bash
# Benchmark default parameters
python -m argon2 --profile RFC_9106_LOW_MEMORY

# Output: "866.5ms per password verification"
```

Adjust parameters to achieve 40-500ms verification time depending on use case.

### Common Errors

- `VerifyMismatchError`: Password doesn't match hash (expected for wrong passwords)
- `InvalidHashError`: Hash format is malformed or corrupted
- `VerificationError`: Verification failed for reasons other than mismatch
- `HashingError`: Hash creation failed (usually parameter issues)

See [API Reference](references/03-api-reference.md) for complete exception documentation.


## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.

