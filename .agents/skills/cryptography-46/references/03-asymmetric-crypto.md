# Asymmetric Cryptography

Asymmetric cryptography uses key pairs (public/private) for encryption, decryption, signing, and verification. This reference covers RSA, elliptic curve cryptography, and modern algorithms like Ed25519.

## Core Concepts

### Key Pairs

- **Private key:** Must be kept secret, used for decryption and signing
- **Public key:** Can be shared openly, used for encryption and verification

### Use Cases

1. **Confidentiality:** Encrypt with public key, decrypt with private key
2. **Authentication:** Sign with private key, verify with public key
3. **Key Exchange:** Derive shared secret from key pairs

## Ed25519 (Recommended for Signing)

Ed25519 provides fast, secure digital signatures with fixed 32-byte keys.

### Key Generation

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate private key
private_key = ed25519.Ed25519PrivateKey.generate()

# Get corresponding public key
public_key = private_key.public_key()
```

### Signing and Verification

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Sign a message
message = b"Message to sign"
signature = private_key.sign(message)

# Verify signature
try:
    public_key.verify(signature, message)
    print("Signature valid")
except Exception as e:
    print("Signature invalid:", e)
```

### Key Serialization

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

private_key = ed25519.Ed25519PrivateKey.generate()

# Export private key (PEM format, unencrypted)
pem_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Export with password protection
pem_encrypted = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"password")
)

# Export public key
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Load private key (unencrypted)
loaded_private = serialization.load_pem_private_key(
    pem_bytes,
    password=None
)

# Load private key (encrypted)
loaded_private = serialization.load_pem_private_key(
    pem_encrypted,
    password=b"password"
)

# Load public key
loaded_public = serialization.load_pem_public_key(public_pem)
```

## X25519 (Key Exchange)

X25519 enables two parties to derive a shared secret over an insecure channel.

### Key Agreement

```python
from cryptography.hazmat.primitives.asymmetric import x25519

# Alice generates key pair
alice_private = x25519.X25519PrivateKey.generate()
alice_public = alice_private.public_key()

# Bob generates key pair
bob_private = x25519.X25519PrivateKey.generate()
bob_public = bob_private.public_key()

# Exchange public keys, then derive shared secret
alice_shared = alice_private.exchange(bob_public)
bob_shared = bob_private.exchange(alice_public)

# Both derive the same shared secret
assert alice_shared == bob_shared
print(f"Shared secret: {alice_shared.hex()}")
```

### Key Serialization

```python
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

private_key = x25519.X25519PrivateKey.generate()

# Export private key (32 bytes raw)
raw_private = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)

# Export public key (32 bytes raw)
raw_public = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

# Load from raw bytes
loaded_private = x25519.X25519PrivateKey.from_private_bytes(raw_private)
loaded_public = x25519.X25519PublicKey.from_public_bytes(raw_public)
```

## RSA (Legacy but Widely Supported)

RSA supports both encryption and signing. Use 2048-bit minimum, 4096-bit recommended.

### Key Generation

```python
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate 2048-bit key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()
```

### RSA Signing (PSS)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Sign with PSS (recommended)
message = b"Message to sign"
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.AUTO
    ),
    hashes.SHA256()
)

# Verify
try:
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.AUTO
        ),
        hashes.SHA256()
    )
    print("Signature valid")
except Exception as e:
    print("Signature invalid")
```

### RSA Signing (PKCS#1 v1.5)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Sign with PKCS#1 v1.5 (legacy)
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)

# Verify
public_key.verify(
    signature,
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)
```

### RSA Encryption (OAEP)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Encrypt (message must be smaller than key size)
message = b"Short message"
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decrypt
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

**Note:** RSA encryption has size limits. For larger data, use hybrid encryption (encrypt with symmetric key, encrypt key with RSA).

## Elliptic Curve Cryptography (ECC)

### ECDSA Signing

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

# Generate P-256 (secp256r1) key pair
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Sign
message = b"Message to sign"
signature = private_key.sign(
    message,
    ec.ECDSA(hashes.SHA256())
)

# Verify
try:
    public_key.verify(
        signature,
        message,
        ec.ECDSA(hashes.SHA256())
    )
    print("Valid")
except Exception as e:
    print("Invalid")
```

### Available Curves

```python
from cryptography.hazmat.primitives.asymmetric import ec

# NIST curves
ec.SECP256R1()  # P-256, most common
ec.SECP384R1()  # P-384, higher security
ec.SECP521R1()  # P-521, highest security

# Brainpool curves
ec.BRAINPOOLP256R1()
ec.BRAINPOOLP384R1()
ec.BRAINPOOLP512R1()

# Generate with specific curve
private_key = ec.generate_private_key(ec.SECP384R1())
```

### ECDH Key Exchange

```python
from cryptography.hazmat.primitives.asymmetric import ec

# Alice generates key pair
alice_private = ec.generate_private_key(ec.SECP256R1())
alice_public = alice_private.public_key()

# Bob generates key pair
bob_private = ec.generate_private_key(ec.SECP256R1())
bob_public = bob_private.public_key()

# Derive shared secret
alice_shared = alice_private.exchange(ec.ECDH(), bob_public)
bob_shared = bob_private.exchange(ec.ECDH(), alice_public)

assert alice_shared == bob_shared
```

## Ed448 and X448 (Higher Security)

Ed448/X448 provide higher security than Ed25519/X25519 with larger keys.

### Ed448 Signing

```python
from cryptography.hazmat.primitives.asymmetric import ed448

private_key = ed448.Ed448PrivateKey.generate()
public_key = private_key.public_key()

# Sign (phased approach for context binding)
message = b"Message"
signature = private_key.sign(message)

# Verify
public_key.verify(signature, message)
```

### X448 Key Exchange

```python
from cryptography.hazmat.primitives.asymmetric import x448

alice_private = x448.X448PrivateKey.generate()
bob_private = x448.X448PrivateKey.generate()

# Derive shared secret
shared = alice_private.exchange(bob_private.public_key())
```

## Key Serialization Formats

### PEM Format (Base64-encoded, human-readable)

```python
from cryptography.hazmat.primitives import serialization

# Private key to PEM
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Public key to PEM
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
```

### DER Format (Binary, compact)

```python
# Private key to DER
der = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
```

### Password Protection

```python
from cryptography.hazmat.primitives import serialization

# Encrypt with password
encrypted_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"strong-password")
)

# Decrypt when loading
private_key = serialization.load_pem_private_key(
    encrypted_pem,
    password=b"strong-password"
)
```

## Best Practices

1. **Prefer Ed25519** for signing (faster, simpler, secure)
2. **Prefer X25519** for key exchange
3. **Use RSA-4096** if RSA required (2048 minimum)
4. **Use P-256 or P-384** for ECC (avoid secp256k1 unless Bitcoin)
5. **Protect private keys** with passwords when storing
6. **Use PKCS#8 format** for private keys (not legacy PKCS#1)
7. **Use PSS padding** for RSA signing (not PKCS#1 v1.5)
8. **Use OAEP padding** for RSA encryption (not PKCS#1 v1.5)

## Complete Example: Secure Message Exchange

```python
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os

class SecureChannel:
    def __init__(self):
        # Key exchange key pair
        self.x25519_private = x25519.X25519PrivateKey.generate()
        self.x25519_public = self.x25519_private.public_key()
        
        # Signing key pair
        self.ed25519_private = ed25519.Ed25519PrivateKey.generate()
        self.ed25519_public = self.ed25519_private.public_key()
        
        self.shared_key = None
    
    def establish_connection(self, remote_x25519_public):
        """Derive shared secret with remote party."""
        raw_shared = self.x25519_private.exchange(remote_x25519_public)
        
        # Derive AES key using HKDF
        self.shared_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"encryption-key",
        ).derive(raw_shared)
    
    def send_message(self, message: bytes, remote_ed25519_public):
        """Encrypt and sign a message."""
        # Generate nonce
        nonce = os.urandom(12)
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(self.shared_key)
        ciphertext = aesgcm.encrypt(nonce, message, None)
        
        # Sign nonce + ciphertext
        signature = self.ed25519_private.sign(nonce + ciphertext)
        
        return {
            "nonce": nonce,
            "ciphertext": ciphertext,
            "signature": signature,
            "public_key": self.ed25519_public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        }
    
    def receive_message(self, packet, sender_public_key_bytes):
        """Verify and decrypt a message."""
        from cryptography.hazmat.primitives import serialization
        
        # Load sender's public key
        sender_public = ed25519.Ed25519PublicKey.from_public_bytes(
            sender_public_key_bytes
        )
        
        # Verify signature
        try:
            sender_public.verify(
                packet["signature"],
                packet["nonce"] + packet["ciphertext"]
            )
        except Exception:
            raise ValueError("Invalid signature")
        
        # Decrypt
        aesgcm = AESGCM(self.shared_key)
        plaintext = aesgcm.decrypt(
            packet["nonce"],
            packet["ciphertext"],
            None
        )
        
        return plaintext

# Usage
alice = SecureChannel()
bob = SecureChannel()

# Establish connection
alice.establish_connection(bob.x25519_public)
bob.establish_connection(alice.x25519_public)

# Alice sends message
packet = alice.send_message(b"Secret message", bob.ed25519_public)

# Bob receives and decrypts
message = bob.receive_message(packet, packet["public_key"])
print(message)  # b"Secret message"
```
