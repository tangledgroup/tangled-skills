# Hashing

Cryptographic hash functions produce fixed-size digests from arbitrary input data.

## Hash API

### Incremental hashing with `Hash` context

```python
from cryptography.hazmat.primitives import hashes

digest = hashes.Hash(hashes.SHA256())
digest.update(b"abc")
digest.update(b"123")
result = digest.finalize()  # returns bytes, context is consumed
```

### One-shot hashing (since 47.0.0)

```python
from cryptography.hazmat.primitives import hashes

result = hashes.Hash.hash(hashes.SHA256(), b"my data")
```

After `finalize()` the context cannot be reused — raises `AlreadyFinalized`. Use `copy()` to snapshot state before finalizing.

## SHA-2 Family

Recommended for most use cases. Faster than SHA-3 with equivalent security.

- `SHA224` — 224-bit digest
- `SHA256` — 256-bit digest (most common)
- `SHA384` — 384-bit digest
- `SHA512` — 512-bit digest
- `SHA512_224` — 224-bit digest from SHA-512 core
- `SHA512_256` — 256-bit digest from SHA-512 core

## SHA-3 Family

Different internal structure than SHA-2. Use as a fallback if SHA-2 is ever broken. Slower than SHA-2.

- `SHA3_224` — 224-bit digest
- `SHA3_256` — 256-bit digest
- `SHA3_384` — 384-bit digest
- `SHA3_512` — 512-bit digest

## BLAKE2

RFC 7693. Immune to length-extension attacks (advantage over SHA family).

- `BLAKE2b(digest_size=64)` — Optimized for 64-bit platforms, 1–64 byte output (only 64 supported currently)
- `BLAKE2s(digest_size=32)` — Optimized for 8–32 bit platforms, 1–32 byte output (only 32 supported currently)

Note: Keying, personalization, and salting features from the RFC are not yet supported due to OpenSSL limitations.

## Extendable Output Functions (XOF)

XOFs produce arbitrary-length output via repeated `squeeze()` calls:

```python
import sys
from cryptography.hazmat.primitives import hashes

digest = hashes.XOFHash(hashes.SHAKE128(digest_size=sys.maxsize))
digest.update(b"abc")
chunk1 = digest.squeeze(16)  # first 16 bytes
chunk2 = digest.squeeze(16)  # next 16 bytes
```

- `SHAKE128(digest_size)` — XOF based on SHA-3
- `SHAKE256(digest_size)` — XOF based on SHA-3

After `squeeze()` the context cannot be updated further.

## Deprecated Algorithms

**SHA-1** (`SHA1`) — Practical collision attacks exist. Strongly discouraged.

**MD5** (`MD5`) — Practical collision attacks exist. Strongly discouraged.

**SM3** (`SM3`) — Chinese standard hash. Available for compatibility.

## Best Practices

- Use SHA-256 or SHA-384 for general-purpose hashing
- Plan for algorithm upgrades over time as cryptanalysis advances
- See [Lifetimes of cryptographic hash functions](https://valerieaurora.org/hash.html)
