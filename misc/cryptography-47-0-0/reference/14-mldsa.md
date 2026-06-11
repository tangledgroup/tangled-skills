# ML-DSA Digital Signatures

ML-DSA (Module-Lattice Digital Signature Algorithm) is a post-quantum digital signature algorithm based on module lattices, standardized in FIPS 204.

**Warning**: This is a "Hazardous Materials" module. Only use if you understand the security implications.

**Availability**: Requires AWS-LC or BoringSSL backend. Standard OpenSSL wheels do not include ML-DSA support. See [State of OpenSSL](https://cryptography.io/en/stable/statements/state-of-openssl.html) for details.

## Signing and Verification

```python
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

# Generate key pair
private_key = MLDSA65PrivateKey.generate()

# Sign
signature = private_key.sign(b"my authenticated message")

# Verify
public_key = private_key.public_key()
public_key.verify(signature, b"my authenticated message")
```

## Context-Based Signing

ML-DSA supports context strings (up to 255 bytes) to bind additional information to signatures. The context differentiates signatures across different protocols or use cases.

```python
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

private_key = MLDSA65PrivateKey.generate()
context = b"email-signature-v1"

# Sign with context
signature = private_key.sign(b"my authenticated message", context)

# Verification requires the same context
public_key = private_key.public_key()
public_key.verify(signature, b"my authenticated message", context)
```

## Security Levels

Three parameter sets:

- **ML-DSA-44** (`MLDSA44PrivateKey`) — ~128-bit classical security, smallest signatures
- **ML-DSA-65** (`MLDSA65PrivateKey`) — ~192-bit classical security, recommended default
- **ML-DSA-87** (`MLDSA87PrivateKey`) — ~256-bit classical security, largest signatures

## Key Interfaces

### MLDSA65PrivateKey

```python
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

# Generate
private_key = MLDSA65PrivateKey.generate()

# From seed bytes (32-byte deterministic generation)
seed = private_key.private_bytes_raw()  # 32 bytes
same_key = MLDSA65PrivateKey.from_seed_bytes(seed)

# Sign (with optional context)
signature = private_key.sign(b"message")
signature = private_key.sign(b"message", b"context")

# Get public key
public_key = private_key.public_key()

# Export raw seed
seed = private_key.private_bytes_raw()  # returns 32 bytes
```

### MLDSA65PublicKey

```python
# Verify (with optional context)
public_key.verify(signature, b"message")
public_key.verify(signature, b"message", b"context")

# Export
der_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.Raw,
)
```

## Exceptions

- `cryptography.exceptions.UnsupportedAlgorithm` — Raised if ML-DSA is not supported by the backend (e.g., standard OpenSSL)
- `ValueError` — Raised if seed bytes are wrong length or context exceeds 255 bytes

## Use Cases

- Post-quantum code signing
- Post-quantum document authentication
- Hybrid signature schemes (combine with Ed25519 or ECDSA)
- X.509 certificates with post-quantum signatures

## Best Practices

- Use ML-DSA-65 as the default security level
- Always use context strings when signing in specific protocols
- Combine with classical signatures (hybrid approach) for defense in depth
- Verify that your OpenSSL backend supports ML-DSA before using in production
- Store private keys securely — seed bytes can deterministically regenerate keys
