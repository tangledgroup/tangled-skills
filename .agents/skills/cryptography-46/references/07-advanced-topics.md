# Advanced Cryptographic Topics

This reference covers advanced features including HPKE, two-factor authentication, random number generation, and other specialized cryptographic operations.

## HPKE (Hybrid Public Key Encryption)

HPKE (RFC 9180) combines asymmetric key encapsulation with symmetric encryption for modern hybrid encryption.

### Basic Usage

```python
from cryptography.hazmat.primitives import hpke
from cryptography.hazmat.primitives.asymmetric import x25519

# Recipient generates key pair
recipient_private = x25519.X25519PrivateKey.generate()
recipient_public = recipient_private.public_key()

# Sender encrypts message
plaintext = b"Secret message"
ciphertext, encapsulated = hpke.seal(
    public_key=recipient_public,
    plaintext=plaintext,
    aad=b"additional-authenticated-data",  # Optional
)

# Recipient decrypts
decrypted = hpke.open(
    private_key=recipient_private,
    encapsulated=encapsulated,
    ciphertext=ciphertext,
    aad=b"additional-authenticated-data",
)
```

### HPKE with Different Key Types

```python
from cryptography.hazmat.primitives import hpke
from cryptography.hazmat.primitives.asymmetric import ec, x25519, x448

# X25519 keys (default)
x25519_private = x25519.X25519PrivateKey.generate()
ciphertext, enc = hpke.seal(x25519_private.public_key(), b"data")
hpke.open(x25519_private, enc, ciphertext)

# X448 keys (higher security)
x448_private = x448.X448PrivateKey.generate()
ciphertext, enc = hpke.seal(x448_private.public_key(), b"data")
hpke.open(x448_private, enc, ciphertext)

# EC P-256 keys
ec_private = ec.generate_private_key(ec.SECP256R1())
ciphertext, enc = hpke.seal(ec_private.public_key(), b"data")
hpke.open(ec_private, enc, ciphertext)
```

### Authenticated HPKE (with Authentication Key)

```python
from cryptography.hazmat.primitives import hpke

# Generate authentication key pair
auth_private = x25519.X25519PrivateKey.generate()
auth_public = auth_private.public_key()

# Encrypt with authentication
ciphertext, encapsulated = hpke.seal(
    public_key=recipient_public,
    plaintext=b"data",
    info=b"application-context",
    aad=b"authenticated-data",
)

# Decrypt with authentication
decrypted = hpke.open(
    private_key=recipient_private,
    encapsulated=encapsulated,
    ciphertext=ciphertext,
    info=b"application-context",
    aad=b"authenticated-data",
)
```

### Mode 1-3 HPKE Variants

HPKE supports different modes for various use cases:

```python
from cryptography.hazmat.primitives import hpke

# Mode 0: Base mode (standard)
ciphertext, enc = hpke.seal(public_key, plaintext)

# Mode 1: Pre-shared key mode
ciphertext, enc = hpke.seal(
    public_key=recipient_public,
    plaintext=b"data",
    psk=b"pre-shared-key",
)

# Mode 2: Authenticated sender
ciphertext, enc = hpke.seal(
    public_key=recipient_public,
    plaintext=b"data",
    auth_private=sender_auth_private,
)

# Mode 3: Authenticated sender with PSK
ciphertext, enc = hpke.seal(
    public_key=recipient_public,
    plaintext=b"data",
    auth_private=sender_auth_private,
    psk=b"pre-shared-key",
)
```

## Two-Factor Authentication (TOTP/HOTP)

Time-based and counter-based one-time passwords (RFC 6238, RFC 4226).

### TOTP (Time-Based OTP)

```python
from cryptography.hazmat.primitives.twofactor.totp import TOTP
import time

# Generate secret key (base32-encoded for user display)
secret = TOTP.generate_secret()
print(f"Share this secret: {secret}")

# Create TOTP object
totp = TOTP(secret)

# Generate current code
current_code = totp.now()
print(f"Current TOTP: {current_code}")  # 6-digit code

# Verify code (within ±1 time step for clock skew)
is_valid = totp.verify(current_code)
print(f"Valid: {is_valid}")

# Verify with specific time and window
is_valid = totp.verify(current_code, when=int(time.time()), window=1)
```

### TOTP Configuration

```python
from cryptography.hazmat.primitives.twofactor.totp import TOTP

totp = TOTP(
    secret=b"base32-encoded-secret",
    digits=6,  # 6 or 8 digit codes
    interval=30,  # Seconds per code (typically 30)
    algorithm="SHA1",  # SHA1, SHA256, SHA512
)

# Generate code at specific time
code = totp.at_time(int(time.time()))

# Verify with window for clock skew tolerance
is_valid = totp.verify(code, window=2)  # ±2 time steps
```

### HOTP (HMAC-Based OTP)

```python
from cryptography.hazmat.primitives.twofactor.hotp import HOTP

hotp = HOTP(secret=b"base32-encoded-secret")

# Generate code for counter
code1 = hotp.at(0)  # First code
code2 = hotp.at(1)  # Second code
code3 = hotp.at(2)  # Third code

# Verify with counter and window
is_valid = hotp.verify(code3, 2, window=1)  # Should match counter 2 ±1
```

### Generating QR Codes for TOTP

```python
from cryptography.hazmat.primitives.twofactor.totp import TOTP
import pyqrcode  # pip install pyqrcode

secret = TOTP.generate_secret()

# Build OTPAuth URI
uri = (
    f"otpauth://totp/MyApp:username?"
    f"secret={secret}&"
    f"issuer=MyApp&"
    f"algorithm=SHA1&"
    f"digits=6&"
    f"period=30"
)

# Generate QR code
qr = pyqrcode.create(uri)
qr.png("totp_qr_code.png", scale=3)

print(f"Scan QR code or enter secret: {secret}")
```

## Random Number Generation

Cryptographically secure random number generation.

### Generating Random Bytes

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os

# Use os.urandom (recommended)
random_bytes = os.urandom(32)  # 32 cryptographically random bytes

# Or use backend's random generation
backend = default_backend()
random_bytes = backend.random_bytes(32)
```

### Generating Random Integers

```python
import secrets

# Random integer in range
random_int = secrets.randbelow(100)  # 0-99

# Random choice from sequence
choice = secrets.choice(["rock", "paper", "scissors"])

# Random token (URL-safe)
token = secrets.token_urlsafe(32)  # 32 bytes of randomness, URL-safe base64

# Random hex string
hex_token = secrets.token_hex(16)  # 16 bytes as 32 hex chars
```

## Constant-Time Operations

Prevent timing attacks with constant-time comparisons:

```python
from cryptography.hazmat.primitives import constant_time

# Constant-time comparison
secret = b"secret-value"
user_input = b"user-input"

if constant_time.bytes_eq(secret, user_input):
    print("Match!")

# Constant-time integer comparison
if constant_time.equal(42, user_provided_value):
    print("Correct!")
```

## ASN.1 Serialization

Advanced serialization for cryptographic structures:

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize to PKCS#1 (legacy RSA format)
pkcs1_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS1,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize to PKCS#8 (modern, recommended)
pkcs8_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Encrypted PKCS#8
encrypted_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"password")
)
```

## Decrepit Algorithms (Legacy Only)

These algorithms are deprecated and should only be used for legacy compatibility:

### DES and 3DES

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.decrepit.ciphers import algorithms as decrepit_algorithms
import os

# DES (insecure, 56-bit key)
key = os.urandom(8)  # 64 bits (8 parity bits)
iv = os.urandom(8)

cipher = Cipher(
    decrepit_algorithms.TripleDES(key),  # Use 3DES, not DES
    modes.CBC(iv),
)
```

### ARC4 (RC4)

```python
from cryptography.hazmat.decrepit.ciphers import algorithms as decrepit_algorithms

# RC4 (broken, avoid unless legacy required)
key = os.urandom(16)
cipher = Cipher(decrepit_algorithms.ARC4(key), mode=None)
```

**Warning:** These algorithms are cryptographically broken. Only use for:
- Legacy system compatibility
- decrypting old data
- Educational purposes

## Cloud HSM Integration

Use hardware security modules for key protection:

```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12

# Generate PKCS#12 archive for HSM import
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

cert = generate_certificate(private_key)  # Your cert generation

p12_data = pkcs12.pkcs12_encode(
    private_key,
    cert,
    [intermediate_cert],  # Certificate chain
    b"password",
    encryption_algorithm=serialization.BestAvailableEncryption(b"password"),
)

# Import p12_data into HSM using vendor-specific tools
```

## Performance Optimization

### Pre-computation for RSA

```python
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate with pre-computed values (faster decryption/signing)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    # Pre-computation happens automatically in modern versions
)
```

### Batch Verification

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# Verify multiple signatures efficiently
def batch_verify(public_key, messages, signatures):
    """Verify multiple signatures."""
    for msg, sig in zip(messages, signatures):
        try:
            public_key.verify(sig, msg)
        except Exception:
            return False
    return True
```

## Error Handling Best Practices

```python
from cryptography.exceptions import (
    InvalidSignature,
    InvalidTag,
    UnsupportedAlgorithm,
    AlreadyFinalized,
)

def safe_decrypt(ciphertext, key):
    """Decrypt with proper error handling."""
    try:
        aesgcm = AESGCM(key)
        nonce = ciphertext[:12]
        data = ciphertext[12:]
        return aesgcm.decrypt(nonce, data, None)
    except InvalidTag:
        # Decryption failed (wrong key or corrupted data)
        # Don't reveal why - just return None or raise generic error
        return None
    except UnsupportedAlgorithm:
        # Key size or algorithm not supported
        logger.error("Unsupported encryption")
        return None

def safe_verify_signature(signature, message, public_key):
    """Verify signature with proper error handling."""
    try:
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return False
```

## Testing and Development

### Deterministic Key Generation for Tests

```python
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.backends import default_backend

# For tests only - use fixed seed or pre-generated keys
def generate_test_key():
    """Generate reproducible test key (tests only!)."""
    # Load from file or use known key
    with open("test_key.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
```

### Mocking Cryptographic Operations

```python
from unittest.mock import patch, MagicMock

# Mock slow operations in tests
with patch('cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC.derive'):
    # Test code that uses KDF without actual derivation
    result = derive_key_from_password("test")
```

## Security Checklist

When implementing cryptographic features:

- [ ] Use AEAD modes (GCM, CCM, Poly1305) not plain encryption
- [ ] Generate random nonces with `os.urandom()` or `secrets`
- [ ] Never reuse (key, nonce) pairs
- [ ] Use constant-time comparison for secrets
- [ ] Derive keys properly with PBKDF2/scrypt/Argon2 for passwords
- [ ] Use HKDF for key-based derivation
- [ ] Protect private keys with passwords when storing
- [ ] Implement proper error handling (don't leak information)
- [ ] Use appropriate algorithms for your threat model
- [ ] Plan for key rotation and algorithm upgrades
- [ ] Log security events without exposing sensitive data
- [ ] Test edge cases (empty data, max sizes, invalid inputs)
