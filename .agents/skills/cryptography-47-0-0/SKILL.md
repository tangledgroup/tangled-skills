---
name: cryptography-47-0-0
description: Comprehensive toolkit for Python cryptographic operations using the cryptography library v47.0.0. Use when implementing encryption, decryption, hashing, digital signatures, key derivation, X.509 certificate handling, post-quantum cryptography (ML-KEM, ML-DSA), ASN.1 encoding/decoding, and other cryptographic primitives in Python applications.
version: "0.1.0"
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
- post-quantum
- ml-kem
- ml-dsa
- asn1
category: security
external_references:
- https://cryptography.io/en/stable/
- https://github.com/pyca/cryptography
---

# cryptography 47.x

## Overview

`cryptography` is a Python package that provides both high-level cryptographic recipes and low-level interfaces to common cryptographic algorithms including symmetric ciphers, message digests, key derivation functions, and asymmetric (public-key) cryptography. It is maintained by the Python Cryptographic Authority (PyCA).

The library is broadly divided into two layers:

- **Recipes layer** — High-level, safe-to-use APIs that require minimal configuration. These are the recommended starting point for most use cases. Includes `Fernet` for symmetric encryption and `x509` for certificate handling.
- **Hazardous Materials (hazmat) layer** — Low-level cryptographic primitives in `cryptography.hazmat`. These are dangerous and can be used incorrectly, requiring deep knowledge of cryptographic concepts. Always prefer the recipes layer when possible.

The library is built on OpenSSL 3.0+ (or compatible backends like BoringSSL, LibreSSL 4.1+, AWS-LC) with a Rust-based build system. It requires Python 3.9+.

## When to Use

- Encrypting and decrypting data at rest or in transit
- Generating and verifying digital signatures
- Computing cryptographic hashes (SHA-2, SHA-3, BLAKE2)
- Deriving cryptographic keys from passwords (PBKDF2, Argon2, HKDF, scrypt)
- Creating, parsing, and verifying X.509 certificates and CSRs
- Implementing two-factor authentication (HOTP/TOTP)
- Performing asymmetric key operations (RSA, EC, Ed25519, X25519)
- Post-quantum cryptography: ML-KEM key encapsulation, ML-DSA signing
- Key wrapping (AES-KW)
- HPKE (Hybrid Public Key Encryption) for post-quantum-ready encryption
- Message authentication codes (HMAC, CMAC, Poly1305)
- ASN.1 encoding and decoding of custom types

## Core Concepts

**Two-layer architecture**: The library separates safe "recipes" from low-level "hazmat" primitives. Import paths starting with `cryptography.hazmat` signal that you are using dangerous building blocks.

**Authenticated encryption**: Plain encryption provides secrecy but not authenticity. Always use authenticated schemes (Fernet, AES-GCM, ChaCha20-Poly1305) to prevent tampering attacks.

**Nonce uniqueness**: For AEAD ciphers, never reuse a nonce with the same key — doing so compromises all messages encrypted with that key/nonce pair.

**Secure random**: Always use `os.urandom()` or the `secrets` module for cryptographic randomness. Never use the `random` module for security-sensitive values.

**Key management**: Keys should be randomly generated, kept secret, and rotated periodically. Use key derivation functions (KDFs) to derive keys from passwords.

**Post-quantum readiness**: ML-KEM (FIPS 203) and ML-DSA (FIPS 24) provide lattice-based post-quantum cryptography. Requires AWS-LC or BoringSSL backend — not available with standard OpenSSL wheels.

**In-place operations**: Since 47.0.0, many primitives support `*_into()` methods that write directly to pre-allocated buffers, reducing memory allocations in high-throughput scenarios.

## Breaking Changes (46.x → 47.x)

- **Binary elliptic curves removed**: `SECT*` classes are no longer available
- **OpenSSL 1.1.x support dropped**: OpenSSL 3.0+ is now required
- **LibreSSL < 4.1**: No longer supported
- **`UnsupportedAlgorithm` instead of `ValueError`**: Key loading functions now raise `UnsupportedAlgorithm` for unsupported algorithms or explicit curve encodings
- **EC private key length validation**: Keys with incorrectly encoded wrong-length private keys are now rejected

## Deprecated (47.x, removed in future)

- Python 3.8 support (removed in next release)
- `TripleDES` with 64-bit or 128-bit keys (only 192-bit accepted in future)
- `CFB`, `OFB`, `CFB8` modes moved to `decrepit` module
- `Camellia` cipher moved to `decrepit` module
- macOS `x86_64` wheels (switching to `arm64` only)
- 32-bit Windows wheels

## Installation / Setup

Install via pip or uv:

```bash
pip install cryptography
# or
uv add cryptography
```

Requires OpenSSL 3.0+ and a Rust compiler (MSRV 1.83.0). Pre-built wheels are available for most platforms. For post-quantum algorithms (ML-KEM, ML-DSA), you need AWS-LC or BoringSSL as the backend — standard OpenSSL wheels do not include these.

## Usage Examples

**Simple symmetric encryption with Fernet (recommended starting point):**

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"a secret message")
plaintext = f.decrypt(token)
```

**One-shot hashing (new in 47.0.0):**

```python
from cryptography.hazmat.primitives import hashes

result = hashes.Hash.hash(hashes.SHA256(), b"my data")
```

**Signing with Ed25519:**

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

private_key = Ed25519PrivateKey.generate()
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

**ML-DSA post-quantum signing (requires AWS-LC/BoringSSL):**

```python
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

private_key = MLDSA65PrivateKey.generate()
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

**ML-KEM post-quantum key encapsulation (requires AWS-LC/BoringSSL):**

```python
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey

private_key = MLKEM768PrivateKey.generate()
shared_secret, ciphertext = private_key.public_key().encapsulate()
recovered_secret = private_key.decapsulate(ciphertext)
```

## Advanced Topics

**Fernet (Symmetric Encryption)**: High-level recipe for authenticated symmetric encryption with key rotation → [Fernet](reference/01-fernet.md)

**Authenticated Encryption (AEAD)**: ChaCha20-Poly1305, AES-GCM, AES-CCM, and other AEAD constructions with new `encrypt_into`/`decrypt_into` methods → [AEAD](reference/02-aead.md)

**Asymmetric Cryptography**: RSA, EC (no binary curves), Ed25519, X25519, Diffie-Hellman, DSA, and key serialization → [Asymmetric](reference/03-asymmetric.md)

**Post-Quantum ML-KEM**: Module-Lattice Key Encapsulation Mechanism (FIPS 203) with MLKEM768/1038/512 → [ML-KEM](reference/13-mlkem.md)

**Post-Quantum ML-DSA**: Module-Lattice Digital Signature Algorithm (FIPS 204) with MLDSA65/87/44 and context-based signing → [ML-DSA](reference/14-mldsa.md)

**Hashing**: SHA-2, SHA-3, BLAKE2, SHAKE (XOF), and the new `Hash.hash()` one-shot API → [Hashing](reference/04-hashing.md)

**Key Derivation Functions**: Argon2id/d/i, PBKDF2-HMAC, scrypt, HKDF (with new `extract()` and `derive_into()`), and KDF interfaces → [KDFs](reference/05-kdf.md)

**Message Authentication Codes**: HMAC, CMAC, Poly1305 for integrity verification → [MACs](reference/06-mac.md)

**X.509 Certificates**: Creating CSRs, self-signed certificates, CA hierarchies, certificate verification, OCSP, and extensions → [X.509](reference/07-x509.md)

**Symmetric Encryption (Cipher API)**: Low-level Cipher class with AES, ChaCha20, SM4 and modes CBC, CTR, GCM, OFB, CCM (CFB/OFB/CFB8 moved to decrepit) → [Symmetric](reference/08-symmetric.md)

**Two-Factor Authentication**: HOTP (RFC 4226) and TOTP (RFC 6238) for one-time passwords → [2FA](reference/09-twofactor.md)

**HPKE**: Hybrid Public Key Encryption (RFC 9180) with post-quantum KEM support → [HPKE](reference/10-hpke.md)

**Key Wrapping**: AES key wrap (RFC 3394) and padded key wrap (RFC 5649) → [KeyWrap](reference/11-keywrap.md)

**ASN.1**: Declarative ASN.1 type definitions with encoding/decoding (new in 47.0.0, API unstable) → [ASN.1](reference/15-asn1.md)

**Utilities**: Random number generation, constant-time comparison, exceptions, padding, and decrepit algorithms → [Utilities](reference/12-utilities.md)
