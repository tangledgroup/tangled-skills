# Argon2 Algorithm

## Overview

Argon2 is a secure password hashing algorithm designed to have both configurable runtime and memory consumption. It was announced as the winner of the Password Hashing Competition (2012–2015) and standardized by IETF in [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html) in September 2021.

## Three Variants

### Argon2d

- Uses **data-dependent** memory access
- Faster execution
- Resistant to time–memory trade-off attacks
- Less suitable for password hashing due to vulnerability to side-channel cache timing attacks
- Better suited for cryptocurrencies and applications with no side-channel threats

### Argon2i

- Uses **data-independent** memory access
- Slower — makes more passes over memory to protect from tradeoff attacks
- Resistant to side-channel attacks
- Originally considered the correct choice for password hashing

### Argon2id (Recommended)

- Hybrid of Argon2d and Argon2i
- Combines data-dependent and data-independent memory accesses
- Provides Argon2i's resistance to side-channel cache timing attacks
- Provides much of Argon2d's resistance to GPU cracking attacks
- **The main variant** and the only one required by RFC 9106 to be implemented

## Why Memory-Hard?

Traditional password hashing workhorses are bcrypt and PBKDF2. While still fine to use, the password cracking community embraced GPUs and ASICs to crack passwords in highly parallel fashion.

An effective measure against extreme parallelism is making computation **memory-hard** — requiring significant RAM that cannot be easily parallelized on GPU/ASIC hardware. scrypt pioneered this approach, but Argon2 improves on it by eliminating trivial time-memory tradeoffs that allow compact implementations with the same energy cost.

## Password Hashing Competition

The Password Hashing Competition took place between 2012 and 2015 to find a new, secure, and future-proof password hashing algorithm. After concerns about NIST's integrity following certain revelations, a group of independent cryptographers and security researchers organized the competition. Argon2 was announced as the winner.

## Argon2 Versions

- **v1.0** — initial release
- **v1.2** — version 18 in hash encoding
- **v1.3** — version 19 in hash encoding (current default)

Old hashes remain functional but opportunistic rehashing to the latest version is recommended.

## Comparison with Other Algorithms

argon2-cffi's FAQ addresses migration from other algorithms:

- **bcrypt / PBKDF2 / scrypt / yescrypt** — Using non-memory-hard hashes carries certain risk but there is no immediate danger or need for action. If deciding how to hash passwords today, Argon2 is the superior, future-proof choice. If using scrypt or yescrypt, you will probably be fine long-term.

## GIL Behavior

argon2-cffi releases the GIL during hashing operations, allowing other Python threads to run concurrently while hashing proceeds in native code.
