---
name: python-scrypt-0-9-4
description: Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, deriving encryption keys from passwords, or verifying passwords with memory-hard key derivation functions resistant to hardware-assisted attacks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - scrypt
  - password-hashing
  - key-derivation
  - cryptography
  - pbkdf
category: cryptography
external_references:
  - https://datatracker.ietf.org/doc/html/rfc7914
  - https://github.com/holgern/py-scrypt
---

# python-scrypt 0.9.4

## Overview

Python bindings for the scrypt key derivation function, as specified in RFC 7914. Scrypt is a memory-hard password-based key derivation function designed to resist brute-force attacks using custom hardware (ASICs, GPUs). Unlike traditional hash functions like MD5 or SHA that can be computed extremely fast on cheap hardware, scrypt requires significant memory and CPU time, making large-scale parallel attacks economically infeasible.

The library wraps the C implementation of scrypt (by Colin Percival) through ctypes, providing three main operations: encrypt/decrypt for password-protected data storage, and hash for deterministic key derivation. It is licensed under the 2-clause BSD license, matching the original scrypt library.

## When to Use

- Deriving cryptographic keys from passwords or passphrases
- Storing password hashes with memory-hard resistance against GPU/ASIC attacks
- Encrypting data with a human-memorable password
- Verifying passwords where timing resistance and hardware resistance matter
- Implementing key derivation for encryption at rest (disk encryption, database encryption)

## Core Concepts

### Memory-Hard Key Derivation

Traditional key derivation functions like PBKDF2 are CPU-hard but not memory-hard. An attacker can build cheap parallel hardware to compute billions of hashes per second. Scrypt adds a memory requirement: the algorithm must keep a large array in RAM throughout computation, making it expensive to parallelize on custom hardware.

### The scrypt Algorithm (RFC 7914)

The scrypt function takes these inputs:

- **P** — passphrase (octet string)
- **S** — salt (octet string, randomly generated per RFC 4086)
- **N** — CPU/memory cost parameter (must be a power of 2, greater than 1)
- **r** — block size parameter
- **p** — parallelization parameter
- **dkLen** — output length in octets

The algorithm proceeds in three steps:

1. Generate initial blocks using PBKDF2-HMAC-SHA-256
2. Process each block through scryptROMix (the memory-hard step)
3. Final key derivation using PBKDF2-HMAC-SHA-256 on the processed blocks

The recommended default parameters per RFC 7914 are `r=8, p=1`, with N chosen based on available resources. The library's `hash()` function defaults to `N=16384, r=8, p=1`.

### Parameter Tuning

- **N** controls both CPU and memory cost. Must be a power of 2 (e.g., 256, 1024, 16384, 1048576). Higher values increase security but slow down legitimate operations.
- **r** controls block size and memory usage. Higher values increase memory requirements.
- **p** controls parallelization. Higher values increase CPU cost without proportionally increasing memory usage.
- The library can auto-select optimal parameters via `pickparams()` based on available system resources and a target maximum time.

## API Reference

The module exports five public symbols: `encrypt`, `decrypt`, `hash`, `pickparams`, `checkparams`, and the `error` exception class.

### `scrypt.encrypt(input, password, ...)`

Encrypt data with a password. Returns bytes (input length + 128 bytes of metadata).

```python
import scrypt

data = scrypt.encrypt(b'a secret message', b'password', maxtime=0.1)
# data is bytes, prefixed with 'scrypt\0\r\0\0\0...' header containing parameters
```

Parameters:

- `input` — data to encrypt (bytes or str, str encoded as UTF-8)
- `password` — encryption password (bytes or str, str encoded as UTF-8)
- `maxtime` — maximum seconds to spend (default: 5.0)
- `maxmem` — maximum memory in bytes, 0 for unlimited (default: 0)
- `maxmemfrac` — fraction of available memory, 0.0–1.0 (default: 0.5)
- `logN`, `r`, `p` — explicit scrypt parameters; if all zero, auto-selected (default: all 0)
- `force` — skip resource limit checks (default: False)
- `verbose` — print parameter info (default: False)

When logN, r, and p are all zero, the library calls `pickparams()` automatically. If any are provided, all three must be non-zero.

### `scrypt.decrypt(input, password, ...)`

Decrypt data produced by `encrypt()`. Returns str or bytes depending on encoding.

```python
import scrypt

plaintext = scrypt.decrypt(data, b'password', maxtime=0.1)
# plaintext is 'a secret message' (str by default)

raw_bytes = scrypt.decrypt(data, b'password', encoding=None)
# raw_bytes is b'a secret message'
```

Parameters:

- `input` — encrypted data (bytes or str)
- `password` — decryption password (bytes or str, str encoded as UTF-8)
- `maxtime` — maximum seconds to spend (default: 300.0)
- `maxmem` — maximum memory in bytes, 0 for unlimited (default: 0)
- `maxmemfrac` — fraction of available memory (default: 0.5)
- `encoding` — output encoding, None for raw bytes (default: 'utf-8')
- `verbose` — print parameter info (default: False)
- `force` — skip resource limit checks (default: False)

### `scrypt.hash(password, salt, ...)`

Compute a deterministic scrypt hash. Returns bytes of fixed length. This is the raw key derivation function — no encryption wrapper, just `scrypt(P, S, N, r, p, dkLen)`.

```python
import scrypt

h = scrypt.hash(b'password', b'random salt')
# h is 64 bytes by default
print(len(h))  # 64
print(h.hex()[:20])  # first 10 bytes as hex

# Deterministic: same inputs always produce same output
assert scrypt.hash(b'password', b'salt') == scrypt.hash(b'password', b'salt')
```

Parameters:

- `password` — the password to hash (bytes or str, str encoded as UTF-8)
- `salt` — salt value (bytes or str, str encoded as UTF-8)
- `N` — CPU/memory cost parameter, must be power of 2 > 1 (default: 16384)
- `r` — block size parameter (default: 8)
- `p` — parallelization parameter (default: 1)
- `buflen` — output length in bytes (default: 64)

Constraints: `r * p < 2^30`, `buflen <= (2^32 - 1) * 32`, N must be a power of 2 greater than 1.

### `scrypt.pickparams(maxmem, maxmemfrac, maxtime, verbose)`

Automatically choose optimal scrypt parameters based on system resources. Returns `(logN, r, p)` tuple.

```python
import scrypt

logN, r, p = scrypt.pickparams(maxtime=2.0)
print(f"N=2^{logN} ({2**logN}), r={r}, p={p}")
# e.g., "N=2^16 (65536), r=8, p=1"
```

Parameters:

- `maxmem` — maximum memory in bytes, 0 for unlimited (default: 0)
- `maxmemfrac` — fraction of available memory (default: 0.5)
- `maxtime` — maximum time in seconds (default: 5.0)
- `verbose` — print info (default: 0)

### `scrypt.checkparams(logN, r, p, ...)`

Validate that parameters are within resource limits. Returns 0 on success, raises `scrypt.error` otherwise.

```python
import scrypt

# Check if parameters are feasible
scrypt.checkparams(16, 8, 1, maxtime=2.0)
# returns 0 (success) or raises scrypt.error
```

### `scrypt.error`

Exception class raised on errors. The error message maps to the underlying C scrypt return code:

- `1` — getrlimit or sysctl failed
- `2` — clock_getres or clock_gettime failed
- `3` — error computing derived key
- `4` — could not obtain cryptographically secure random bytes
- `5` — error in OpenSSL
- `6` — malloc failed
- `7` — data is not a valid scrypt-encrypted block
- `8` — unrecognized scrypt format
- `9` — decrypting file would take too much memory
- `10` — decrypting file would take too long
- `11` — password is incorrect
- `15` — error in explicit parameters

## Usage Examples

### Password Hashing and Verification

The most common use case: store a password hash and verify against it later. The `encrypt`/`decrypt` pair provides a simple pattern — encrypt random data with the password, then attempt decryption to verify.

```python
import os
import scrypt

def hash_password(password, maxtime=0.5, datalength=64):
    """Create a secure password hash using scrypt."""
    return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)

def verify_password(stored_hash, guessed_password, maxtime=0.5):
    """Verify a password against its stored hash."""
    try:
        scrypt.decrypt(stored_hash, guessed_password, maxtime=maxtime, encoding=None)
        return True
    except scrypt.error as e:
        if "password is incorrect" in str(e):
            return False
        raise  # Re-raise resource limit errors

# Store a password
stored = hash_password("my_secure_password")

# Verify correct password
assert verify_password(stored, "my_secure_password")

# Reject wrong password
assert not verify_password(stored, "wrong_password")
```

### Deterministic Key Derivation

Use `hash()` when you need a fixed-size, reproducible derived key (e.g., for encrypting data at rest where the same key must be derived each time).

```python
import scrypt

# Derive a 32-byte AES key from a password
key = scrypt.hash(b"master_password", b"fixed_salt_value", N=16384, r=8, p=1, buflen=32)
# key is 32 bytes suitable for AES-256
```

### Auto-Tuned Encryption

Let the library choose optimal parameters for your hardware:

```python
import scrypt

# Encrypt with auto-tuned parameters targeting 0.1 second
encrypted = scrypt.encrypt(b"confidential data", b"user_password", maxtime=0.1)

# Decrypt (auto-detects parameters from encrypted blob header)
decrypted = scrypt.decrypt(encrypted, b"user_password")
```

### Handling Resource Limits

When `maxtime` is too low for the chosen parameters, scrypt raises an error. Use `force=True` to bypass the check:

```python
import scrypt

data = scrypt.encrypt(b"message", b"password", maxtime=0.5)

# This fails because 0.001s is too short for the parameters used
try:
    scrypt.decrypt(data, b"password", maxtime=0.001)
except scrypt.error as e:
    print(e)  # "decrypting file would take too long"

# Force decryption regardless of time estimate
result = scrypt.decrypt(data, b"password", maxtime=0.001, force=True)
```

### Using RFC 7914 Test Vectors

Verify correctness against the RFC test vectors:

```python
import scrypt

# RFC 7914 Section 12: P="pleaseletmein", S="SodiumChloride", N=16384, r=8, p=1, dkLen=64
result = scrypt.hash(b"pleaseletmein", b"SodiumChloride", N=16384, r=8, p=1, buflen=64)
expected = bytes.fromhex(
    "7023bcdc3afd7348461c06cd81fd38eb"
    "fda8fbba904f8e3ea9b543f6545da1f2"
    "d5432955613f0fcf62d49705242a9af9"
    "e61e85dc0d651e40dfcf017b45575887"
)
assert result == expected
```

## Security Considerations

### Parameter Selection

- **N** should be as large as practical for your use case. For password storage, target 0.1–0.5 seconds per hash on your server hardware.
- Never reduce memory usage so much that it undermines the algorithm's memory-hard properties.
- Use `pickparams()` to let the library auto-tune, or benchmark manually with `checkparams()`.

### Salt Generation

- Always use a unique, cryptographically random salt per password when using `hash()`.
- Generate salts with `os.urandom(16)` or similar (16–32 bytes recommended).
- Never reuse salts across different passwords.

### Denial-of-Service Protection

- Scrypt can require large amounts of memory depending on parameters.
- When accepting user-supplied encrypted data, validate that `maxmem` and `maxtime` are bounded to prevent DoS via unreasonably large embedded parameters.
- The `force=False` default protects against this by raising `scrypt.error` when limits would be exceeded.

### Error Handling

- Distinguish between "wrong password" (error code 11) and resource limit errors (codes 9, 10).
- Resource limit errors should be handled by increasing limits or using `force=True`.
- Wrong password errors are authentication failures — do not retry with higher limits.

### Sensitive Data in Memory

- Passwords and intermediate values may remain in memory, core dumps, or swap after processing.
- Consider running in environments with protected memory (e.g., `mlock()` on Linux) for high-security applications.
