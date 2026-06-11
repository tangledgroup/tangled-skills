# HPKE (Hybrid Public Key Encryption)

HPKE (RFC 9180) combines a Key Encapsulation Mechanism (KEM), a Key Derivation Function (KDF), and an AEAD scheme for authenticated public-key encryption.

Each `encrypt()` call generates a fresh ephemeral key pair — encrypting the same plaintext twice produces different ciphertexts.

## Basic Usage

```python
from cryptography.hazmat.primitives.hpke import Suite, KEM, KDF, AEAD
from cryptography.hazmat.primitives.asymmetric import x25519

suite = Suite(KEM.X25519, KDF.HKDF_SHA256, AEAD.AES_128_GCM)

# Recipient generates key pair
private_key = x25519.X25519PrivateKey.generate()
public_key = private_key.public_key()

# Sender encrypts
ciphertext = suite.encrypt(b"secret message", public_key, info=b"app-context")

# Recipient decrypts
plaintext = suite.decrypt(ciphertext, private_key, info=b"app-context")
```

The `info` parameter binds encryption to a specific application context. Use a unique string per use case (e.g., `"MyApp-v1-UserMessages"`).

## KEM Algorithms

- `KEM.X25519` — DHKEM(X25519, HKDF-SHA256)
- `KEM.P256` — DHKEM(P-256, HKDF-SHA256)
- `KEM.P384` — DHKEM(P-384, HKDF-SHA384)
- `KEM.P521` — DHKEM(P-521, HKDF-SHA512)
- `KEM.MLKEM768` — Post-quantum ML-KEM-768
- `KEM.MLKEM1024` — Post-quantum ML-KEM-1024
- `KEM.MLKEM768_X25519` — Hybrid (X-Wing): ML-KEM-768 + X25519
- `KEM.MLKEM1024_P384` — Hybrid: ML-KEM-1024 + P-384

ML-KEM variants require backend support and use hybrid key types (`MLKEM768X25519PrivateKey` / `MLKEM768X25519PublicKey`).

## KDF Algorithms

- `KDF.HKDF_SHA256`
- `KDF.HKDF_SHA384`
- `KDF.HKDF_SHA512`

## AEAD Algorithms

- `AEAD.AES_128_GCM`
- `AEAD.AES_256_GCM`
- `AEAD.CHACHA20_POLY1305`
