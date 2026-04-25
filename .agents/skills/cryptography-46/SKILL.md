---
name: cryptography-46
description: Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing encryption, decryption, hashing, digital signatures, key derivation, X.509 certificate handling, and other cryptographic primitives in Python applications.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - cryptography
  - encryption
  - hashing
  - asymmetric
  - symmetric
  - x509
  - tls
  - python
  - security
category: security
external_references:
  - https://cryptography.io/en/latest/
  - https://github.com/pyca/cryptography
---
## Overview
Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing encryption, decryption, hashing, digital signatures, key derivation, X.509 certificate handling, and other cryptographic primitives in Python applications.

A comprehensive toolkit for cryptographic operations in Python using the `cryptography` library (version 46.x). This skill covers both high-level safe recipes and low-level hazardous materials (hazmat) primitives for encryption, hashing, digital signatures, key derivation, X.509 certificates, and more.

## When to Use
- Implementing symmetric encryption with Fernet or AES/GCM
- Creating and verifying digital signatures (RSA, ECDSA, Ed25519)
- Hashing data with SHA-2, BLAKE2, or other algorithms
- Deriving keys from passwords using PBKDF2, scrypt, or Argon2
- Generating and managing X.509 certificates
- Performing key exchange (ECDH, X25519)
- Implementing two-factor authentication (TOTP/HOTP)
- Working with HPKE (Hybrid Public Key Encryption)
- Serializing cryptographic keys (PEM, DER, PKCS#8)

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
Install the cryptography library:

```bash
pip install cryptography
```

Or with uv:

```bash
uv add cryptography
```

**Supported platforms:** Linux, macOS, Windows, FreeBSD. Python 3.9+.

## Architecture Overview
The `cryptography` library is divided into two layers:

1. **Recipes layer** - High-level, safe cryptographic recipes requiring minimal configuration
   - `cryptography.fernet` - Symmetric authenticated encryption
   - `cryptography.x509` - X.509 certificate handling

2. **Hazmat layer** - Low-level primitives for experts (use with caution)
   - `cryptography.hazmat.primitives.*` - Cryptographic algorithms
   - Always includes danger warnings in documentation

**Recommendation:** Use the recipes layer whenever possible. Fall back to hazmat only when necessary.

## Usage Examples
### Symmetric Encryption with Fernet

```python
from cryptography.fernet import Fernet

# Generate a key (store securely!)
key = Fernet.generate_key()

# Create Fernet instance
f = Fernet(key)

# Encrypt
token = f.encrypt(b"Secret message")

# Decrypt
message = f.decrypt(token)
```

See [Fernet Encryption](reference/01-fernet-encryption.md) for detailed usage including key rotation.

### Hashing Data

```python
from cryptography.hazmat.primitives import hashes

# One-shot hash
digest = hashes.Hash.hash(hashes.SHA256(), b"data to hash")

# Incremental hashing
digest_obj = hashes.Hash(hashes.SHA256())
digest_obj.update(b"part1")
digest_obj.update(b"part2")
result = digest_obj.finalize()
```

See [Hashing and MACs](reference/02-hashing-macs.md) for algorithm options.

### Digital Signatures with Ed25519

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate key pair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Sign
signature = private_key.sign(b"message to sign")

# Verify
public_key.verify(signature, b"message to sign")
```

See [Asymmetric Cryptography](reference/03-asymmetric-crypto.md) for RSA, ECDSA, and more.

### Key Derivation from Password

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

# Generate salt
salt = os.urandom(16)

# Derive key
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100_000,
)
key = kdf.derive(b"password")
```

See [Key Derivation](reference/04-key-derivation.md) for PBKDF2, scrypt, Argon2.

### X.509 Certificate Generation

```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

# Generate RSA key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Build certificate
subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(subject)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.utcnow() + datetime.timedelta(days=365))
    .sign(private_key, hashes.SHA256())
)
```

See [X.509 Certificates](reference/05-x509-certificates.md) for complete guide.

## Advanced Topics
## Advanced Topics

- [Fernet Encryption](reference/01-fernet-encryption.md)
- [Hashing Macs](reference/02-hashing-macs.md)
- [Asymmetric Crypto](reference/03-asymmetric-crypto.md)
- [Key Derivation](reference/04-key-derivation.md)
- [X509 Certificates](reference/05-x509-certificates.md)
- [Symmetric Primitives](reference/06-symmetric-primitives.md)
- [Advanced Topics](reference/07-advanced-topics.md)

## Troubleshooting
### Common Issues

**"UnsupportedAlgorithm" exception:** The algorithm is not available in your backend. Ensure OpenSSL/LibreSSL/BoringSSL is properly installed.

**"InvalidToken" with Fernet:** Token was corrupted, signed with different key, or expired (if TTL specified).

**Key serialization errors:** Use `PrivateFormat.PKCS8` with `Encryption.Unencrypted` for modern applications. Legacy PKCS#1 format is deprecated.

### Backend Requirements

The library requires one of: OpenSSL, LibreSSL, BoringSSL, or AWS-LC. Most systems have OpenSSL pre-installed. For custom builds, see [Installation documentation](https://cryptography.io/en/latest/installation/).

### Thread Safety

Most cryptography objects are **not** thread-safe. Create separate instances per thread or use locks when sharing state. Fernet and MultiFernet are explicitly thread-safe.

## Version Notes
This skill targets cryptography 46.x (released September 2025). Key features:
- Python 3.9+ support
- ML-DSA post-quantum signatures (new in 47, not available in 46)
- HPKE (RFC 9180) implementation
- Ed25519/Ed448/X25519/X448 native support
- X.509 certificate transparency and OCSP

For latest changes, check [Changelog](https://cryptography.io/en/latest/changelog/).

