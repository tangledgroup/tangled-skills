# Asymmetric Cryptography

Asymmetric cryptography uses key pairs: a public key (shareable) and a private key (secret). Primary use cases are authentication (signing/verification) and confidentiality (encryption/decryption).

## Key Types

### RSA

```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15, PSS, OAEP
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

# Generate
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Sign / Verify
signature = private_key.sign(b"message", PKCS1v15(), hashes.SHA256())
public_key = private_key.public_key()
public_key.verify(signature, b"message", PKCS1v15(), hashes.SHA256())

# Encrypt / Decrypt (OAEP)
ct = public_key.encrypt(b"secret", OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
pt = private_key.decrypt(ct, OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
```

Recommended key sizes: 2048+ bits. PSS padding is preferred over PKCS1v15 for new applications.

### Elliptic Curve (EC)

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA

# Generate on P-256 curve
private_key = ec.generate_private_key(ec.SECP256R1())

# Sign / Verify with ECDSA
signature = private_key.sign(b"message", ECDSA(hashes.SHA256()))
private_key.public_key().verify(signature, b"message", ECDSA(hashes.SHA256()))

# ECDH key exchange
shared_key = private_key.exchange(ec.ECDH(), other_public_key)
```

Supported curves: SECP256R1 (P-256), SECP384R1 (P-384), SECP521R1 (P-521), X25519, X448.

### Ed25519 Signing

Fast, simple Edwards-curve signature scheme. No hash algorithm parameter needed.

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

private_key = Ed25519PrivateKey.generate()
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

### Ed448 Signing

Larger Edwards-curve signature scheme for higher security.

```python
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey

private_key = Ed448PrivateKey.generate()
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

### X25519 Key Exchange

```python
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

private_key = X25519PrivateKey.generate()
shared_key = private_key.exchange(other_public_key)  # returns 32 bytes
```

### X448 Key Exchange

```python
from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey

private_key = X448PrivateKey.generate()
shared_key = private_key.exchange(other_public_key)  # returns 56 bytes
```

### ML-DSA (Module-Lattice Digital Signature Algorithm)

Post-quantum signature algorithm (FIPS 204). Available on backends that support it.

```python
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSAPrivateKey

private_key = MLDSAPrivateKey.generate()  # ML-DSA-65, -87, or -174
signature = private_key.sign(b"message")
private_key.public_key().verify(signature, b"message")
```

### ML-KEM (Module-Lattice Key Encapsulation Mechanism)

Post-quantum key encapsulation (FIPS 203). Used for key exchange.

```python
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey

private_key = MLKEM768PrivateKey.generate()
ciphertext, shared_secret = private_key.public_key().encapsulate()
decrypted_secret = private_key.decapsulate(ciphertext)
```

### Diffie-Hellman (DH)

```python
from cryptography.hazmat.primitives.asymmetric import dh

parameters = dh.generate_parameters(generator=2, key_size=2048)
private_key = parameters.generate_private_key()
shared_key = private_key.exchange(dh.DH(), other_public_key)
```

### DSA

```python
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import hashes

private_key = dsa.generate_private_key(key_size=2048)
signature = private_key.sign(b"message", hashes.SHA256())
private_key.public_key().verify(signature, b"message", hashes.SHA256())
```

## Key Serialization

### Loading Keys

```python
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    load_der_private_key, load_ssh_private_key,
)

# PEM
private_key = load_pem_private_key(pem_data, password=None)
public_key = load_pem_public_key(pem_data)

# DER
private_key = load_der_private_key(der_data, password=None)

# SSH format
private_key = load_ssh_private_key(ssh_data, password=None)
```

### Saving Keys

Call methods on the key object itself:

```python
from cryptography.hazmat.primitives import serialization

pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
)

# Unencrypted
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

# Public key
pub_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
```

Formats: `PKCS8`, `TraditionalOpenSSL`, `PSS` (SSH). Encodings: `PEM`, `DER`.

### Type Checking After Loading

Serialization functions return the appropriate key type. Use `isinstance` to check:

```python
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa

if isinstance(key, rsa.RSAPrivateKey):
    # RSA operations
elif isinstance(key, ec.EllipticCurvePrivateKey):
    # EC operations
```

Type aliases are available for type hints: `PublicKeyTypes`, `PrivateKeyTypes`, `CertificatePublicKeyTypes`.
