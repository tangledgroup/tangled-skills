# ML-KEM Key Encapsulation

ML-KEM (Module-Lattice Key Encapsulation Mechanism) is a post-quantum key encapsulation mechanism based on module lattices, standardized in FIPS 203.

**Warning**: This is a "Hazardous Materials" module. Only use if you understand the security implications.

**Availability**: Requires AWS-LC or BoringSSL backend. Standard OpenSSL wheels do not include ML-KEM support. See [State of OpenSSL](https://cryptography.io/en/stable/statements/state-of-openssl.html) for details.

## Encapsulation and Decapsulation

```python
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey

# Generate key pair
private_key = MLKEM768PrivateKey.generate()
public_key = private_key.public_key()

# Encapsulate (produces shared secret + ciphertext)
shared_secret, ciphertext = public_key.encapsulate()

# Decapsulate (recovers the same shared secret)
recovered_secret = private_key.decapsulate(ciphertext)

assert shared_secret == recovered_secret
```

## Security Levels

Three parameter sets corresponding to different security levels:

- **ML-KEM-512** (`MLKEM512PrivateKey`) — ~128-bit classical security, lowest performance
- **ML-KEM-768** (`MLKEM768PrivateKey`) — ~192-bit classical security, recommended default
- **ML-KEM-1038** (`MLKEM1038PrivateKey`) — ~256-bit classical security, highest overhead

## Key Interfaces

### MLKEM768PrivateKey

```python
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey

# Generate
private_key = MLKEM768PrivateKey.generate()

# From seed bytes (64-byte deterministic generation)
seed = private_key.private_bytes_raw()  # 64 bytes
same_key = MLKEM768PrivateKey.from_seed_bytes(seed)

# Get public key
public_key = private_key.public_key()

# Decapsulate ciphertext
shared_secret = private_key.decapsulate(ciphertext)

# Export raw seed
seed = private_key.private_bytes_raw()  # returns 64 bytes
```

### MLKEM768PublicKey

```python
# Encapsulate (produces shared secret and ciphertext)
shared_secret, ciphertext = public_key.encapsulate()

# Export
der_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.Raw,
)
```

## Exceptions

- `cryptography.exceptions.UnsupportedAlgorithm` — Raised if ML-KEM is not supported by the backend (e.g., standard OpenSSL)

## Use Cases

- Post-quantum key exchange in hybrid schemes (combine with X25519 or ECDH)
- Forward secrecy with quantum-resistant properties
- Key establishment for protocols requiring post-quantum security

## Best Practices

- Use ML-KEM-768 as the default security level
- Combine with classical key exchange (hybrid approach) for defense in depth
- Verify that your OpenSSL backend supports ML-KEM before using in production
- Store private keys securely — seed bytes can deterministically regenerate keys
