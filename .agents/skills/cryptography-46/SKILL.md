---
name: cryptography-46
description: Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing encryption, decryption, hashing, digital signatures, key derivation, X.509 certificate handling, and other cryptographic primitives in Python applications.
version: 0.2.0
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

# cryptography 46.x

## Overview

`cryptography` is a Python package that provides both high-level cryptographic recipes and low-level interfaces to common cryptographic algorithms including symmetric ciphers, message digests, key derivation functions, and asymmetric (public-key) cryptography. It is maintained by the Python Cryptographic Authority (PyCA).

The library is broadly divided into two layers:

- **Recipes layer** — High-level, safe-to-use APIs that require minimal configuration. These are the recommended starting point for most use cases. Includes `Fernet` for symmetric encryption and `x509` for certificate handling.
- **Hazardous Materials (hazmat) layer** — Low-level cryptographic primitives in `cryptography.hazmat`. These are dangerous and can be used incorrectly, requiring deep knowledge of cryptographic concepts. Always prefer the recipes layer when possible.

The library is built on OpenSSL 3.x (or compatible backends like BoringSSL, LibreSSL, AWS-LC) with a Rust-based build system. It requires Python 3.9+.

## When to Use

- Encrypting and decrypting data at rest or in transit
- Generating and verifying digital signatures
- Computing cryptographic hashes (SHA-2, SHA-3, BLAKE2)
- Deriving cryptographic keys from passwords (PBKDF2, Argon2, HKDF, scrypt)
- Creating, parsing, and verifying X.509 certificates and CSRs
- Implementing two-factor authentication (HOTP/TOTP)
- Performing asymmetric key operations (RSA, EC, Ed25519, X25519)
- Key wrapping (AES-KW)
- HPKE (Hybrid Public Key Encryption) for post-quantum-ready encryption
- Message authentication codes (HMAC, CMAC, Poly1305)

## Core Concepts

**Two-layer architecture**: The library separates safe "recipes" from low-level "hazmat" primitives. Import paths starting with `cryptography.hazmat` signal that you are using dangerous building blocks.

**Authenticated encryption**: Plain encryption provides secrecy but not authenticity. Always use authenticated schemes (Fernet, AES-GCM, ChaCha20-Poly1305) to prevent tampering attacks.

**Nonce uniqueness**: For AEAD ciphers, never reuse a nonce with the same key — doing so compromises all messages encrypted with that key/nonce pair.

**Secure random**: Always use `os.urandom()` or the `secrets` module for cryptographic randomness. Never use the `random` module for security-sensitive values.

**Key management**: Keys should be randomly generated, kept secret, and rotated periodically. Use key derivation functions (KDFs) to derive keys from passwords.

## Installation / Setup

Install via pip or uv:

```bash
pip install cryptography
# or
uv add cryptography
```

Requires OpenSSL 3.0+ and a Rust compiler (for the build backend). Pre-built wheels are available for most platforms.

## Usage Examples

**Simple symmetric encryption with Fernet (recommended starting point):**

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"a secret message")
plaintext = f.decrypt(token)
```

**Hashing data:**

```python
from cryptography.hazmat.primitives import hashes

digest = hashes.Hash(hashes.SHA256())
digest.update(b"my data")
result = digest.finalize()
```

**Signing with Ed25519:**

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

private_key = Ed25519PrivateKey.generate()
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

## Advanced Topics

**Fernet (Symmetric Encryption)**: High-level recipe for authenticated symmetric encryption with key rotation → See [Fernet](reference/01-fernet.md)

**Authenticated Encryption (AEAD)**: ChaCha20-Poly1305, AES-GCM, AES-CCM, and other AEAD constructions → See [AEAD](reference/02-aead.md)

**Asymmetric Cryptography**: RSA, EC, Ed25519, X25519, ML-DSA, ML-KEM, Diffie-Hellman, DSA, and key serialization → See [Asymmetric](reference/03-asymmetric.md)

**Hashing**: SHA-2, SHA-3, BLAKE2, SHAKE (XOF), and the Hash/XOFHash APIs → See [Hashing](reference/04-hashing.md)

**Key Derivation Functions**: Argon2id/d/i, PBKDF2-HMAC, scrypt, HKDF, and KDF interfaces → See [KDFs](reference/05-kdf.md)

**Message Authentication Codes**: HMAC, CMAC, Poly1305 for integrity verification → See [MACs](reference/06-mac.md)

**X.509 Certificates**: Creating CSRs, self-signed certificates, CA hierarchies, certificate verification, OCSP, and extensions → See [X.509](reference/07-x509.md)

**Symmetric Encryption (Cipher API)**: Low-level Cipher class with AES, ChaCha20, SM4 and modes CBC, CTR, GCM, CFB, OFB, CCM → See [Symmetric](reference/08-symmetric.md)

**Two-Factor Authentication**: HOTP (RFC 4226) and TOTP (RFC 6238) for one-time passwords → See [2FA](reference/09-twofactor.md)

**HPKE**: Hybrid Public Key Encryption (RFC 9180) with post-quantum KEM support → See [HPKE](reference/10-hpke.md)

**Key Wrapping**: AES key wrap (RFC 3394) and padded key wrap (RFC 5649) → See [KeyWrap](reference/11-keywrap.md)

**Utilities**: Random number generation, constant-time comparison, exceptions, padding, and decrepit algorithms → See [Utilities](reference/12-utilities.md)
