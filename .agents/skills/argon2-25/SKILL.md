---
name: argon2-25
description: Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi 25.x. Use when implementing secure password storage, user authentication systems, migrating legacy password hashes to modern standards, or benchmarking Argon2 parameters for your environment.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "25.1.0"
tags:
  - password-hashing
  - authentication
  - cryptography
  - argon2
  - security
  - key-derivation
category: security
external_references:
  - https://argon-cffi.readthedocs.io/
  - https://github.com/hynek/argon2_cffi
---

# argon2-cffi 25.1.0

## Overview

**argon2-cffi** is the simplest way to use [Argon2](https://github.com/p-h-c/phc-winner-argon2) in Python. Argon2 won the [Password Hashing Competition](https://www.password-hashing.net/) (2012–2015) and was standardized by the IETF in [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html) (September 2021).

Argon2 is a memory-hard password hashing algorithm with configurable runtime and memory consumption. It comes in three variants:

- **Argon2d** — resistant to time–memory trade-offs, uses data-dependent memory access. Better for cryptocurrencies and applications without side-channel threats.
- **Argon2i** — resistant to side-channel cache timing attacks, uses data-independent memory access (more passes over memory).
- **Argon2id** — hybrid of d and i. Combines resistance to both GPU cracking and side-channel attacks. This is the main variant and the only one required by RFC 9106.

The library provides:

- **High-level API** — `PasswordHasher` class with sensible defaults (Argon2id, RFC 9106 low-memory profile).
- **Low-level API** — `argon2.low_level` module for building custom abstractions.
- **Profiles** — Predefined parameter sets from RFC 9106 (`argon2.profiles`).
- **CLI** — Benchmark tool via `python -m argon2`.

Version 25.1.0 supports Python 3.9–3.14 (including Free Threading and PyPy). The library is fully typed (`py.typed`) and releases the GIL during hashing.

## When to Use

- Hashing passwords for user authentication systems
- Migrating from bcrypt, PBKDF2, or scrypt to Argon2
- Implementing opportunistic rehashing when parameters change
- Benchmarking Argon2 performance in your environment
- Building custom password hashing abstractions with the low-level API
- Verifying existing Argon2 hashes (any variant: d, i, id)

## Core Concepts

### Hash Format

Encoded Argon2 hashes are self-contained strings that include all parameters and the salt:

```
$argon2id$v=19$m=65536,t=3,p=4$<base64-salt>$<base64-hash>
```

Components:
- `$argon2id` — variant identifier (also `argon2i`, `argon2d`)
- `v=19` — Argon2 version (19 = v1.3, 18 = v1.2)
- `m=65536` — memory cost in kibibytes
- `t=3` — time cost (iterations)
- `p=4` — parallelism (lanes/threads)
- Salt and hash are base64-encoded

### Key Parameters

- **time_cost** — number of iterations over the memory
- **memory_cost** — memory usage in kibibytes (KiB)
- **parallelism** — number of threads (called "lanes" in RFC 9106)
- **hash_len** — length of output hash in bytes (32 recommended, 16 sufficient for password verification)
- **salt_len** — length of random salt in bytes (16 recommended, 8 minimum for space-constrained systems)

### Default Parameters (v21.2.0+)

Since version 21.2.0, `PasswordHasher` defaults to the RFC 9106 low-memory profile:

- type: Argon2id
- time_cost: 3
- memory_cost: 65536 KiB (64 MiB)
- parallelism: 4
- hash_len: 32 bytes
- salt_len: 16 bytes

Verification targets ~40–50ms on recent hardware. On WebAssembly platforms, parallelism is automatically set to 1.

## Usage Examples

### Basic Password Hashing and Verification

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hash a password (accepts str or bytes)
hash = ph.hash("correct horse battery staple")
# '$argon2id$v=19$m=65536,t=3,p=4$MIIRqgvgQbgj220jfp0MPA$...'

# Verify a password (returns True on success, raises on failure)
ph.verify(hash, "correct horse battery staple")  # True

# Wrong password raises VerifyMismatchError
ph.verify(hash, "wrong password")  # raises VerifyMismatchError
```

### Login Function with Opportunistic Rehashing

```python
import argon2

ph = argon2.PasswordHasher()

def login(db, user, password):
    stored_hash = db.get_password_hash_for_user(user)

    # Verify password — raises exception if wrong
    ph.verify(stored_hash, password)

    # Check if hash parameters are outdated and rehash if needed
    if ph.check_needs_rehash(stored_hash):
        db.set_password_hash_for_user(user, ph.hash(password))
```

### Using RFC 9106 Profiles

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_HIGH_MEMORY, RFC_9106_LOW_MEMORY

# Use the high-memory profile (2 GiB, for beefy servers)
ph = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)

# Or explicitly with low-memory profile
ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
```

### Extracting Parameters from a Hash

```python
from argon2 import extract_parameters

params = extract_parameters(
    "$argon2id$v=19$m=65536,t=3,p=4$abc$def"
)
print(params.type)        # Type.ID
print(params.memory_cost) # 65536
print(params.time_cost)   # 3
print(params.parallelism) # 4
```

## Advanced Topics

**Argon2 Algorithm Details**: Three variants, memory-hard design, RFC 9106 standardization → See [Argon2 Algorithm](reference/01-argon2-algorithm.md)

**Parameter Selection Guide**: How to choose time_cost, memory_cost, parallelism, and hash_len for your environment → See [Choosing Parameters](reference/02-choosing-parameters.md)

**API Reference**: Complete documentation of PasswordHasher, low-level API, exceptions, profiles, and utilities → See [API Reference](reference/03-api-reference.md)

**CLI and Installation**: Benchmark tool usage, installation options (vendored vs system Argon2), SSE2 override → See [CLI and Installation](reference/04-cli-installation.md)
