# python-scrypt Advanced Usage

This reference covers parameter selection guidelines, error handling patterns, and advanced usage.

## Parameter Selection

### Understanding Scrypt Parameters

| Parameter | Description | Impact | Recommended Values |
|-----------|-------------|--------|-------------------|
| `n` | CPU/memory cost factor (must be power of 2) | Controls iterations and memory usage | 2^14 (interactive), 2^20 (sensitive files) |
| `r` | Block size parameter | Affects memory cost | 8 (RFC 7914 default) |
| `p` | Parallelization factor | Increases CPU cost without affecting memory | 1 (RFC 7914 default) |
| `dklen`/`length` | Derived key length in bytes | Output size | 32 (256-bit), 64 (512-bit) |

### Memory Usage Calculation

Approximate memory usage: `n * r * 128` bytes

```python
def calculate_memory_usage(n: int, r: int) -> str:
    """Calculate approximate memory usage in human-readable format."""
    memory_bytes = n * r * 128
    
    if memory_bytes >= 1024**3:
        return f"{memory_bytes / (1024**3):.2f} GiB"
    elif memory_bytes >= 1024**2:
        return f"{memory_bytes / (1024**2):.2f} MiB"
    elif memory_bytes >= 1024:
        return f"{memory_bytes / 1024:.2f} KiB"
    else:
        return f"{memory_bytes} bytes"

# Examples
print(f"n=2^14, r=8: {calculate_memory_usage(2**14, 8)}")     # ~128 MiB
print(f"n=2^17, r=8: {calculate_memory_usage(2**17, 8)}")     # ~1 GiB
print(f"n=2^20, r=8: {calculate_memory_usage(2**20, 8)}")     # ~8 GiB
```

### Recommended Parameter Sets

| Use Case | n | r | p | Expected Time | Memory |
|----------|---|---|---|---------------|--------|
| Interactive login | 2^14 | 8 | 1 | < 100ms | ~128 MiB |
| Account registration | 2^16 | 8 | 1 | ~1s | ~512 MiB |
| Sensitive file encryption | 2^20 | 8 | 1 | < 5s | ~8 GiB |
| High-security storage | 2^22 | 8 | 1 | ~10s | ~32 GiB |

### Tuning Parameters for Your System

Measure performance and adjust accordingly:

```python
import hashlib
import os
import time

def benchmark_scrypt(n: int, r: int, p: int, iterations: int = 5) -> float:
    """Benchmark scrypt performance and return average time in seconds."""
    salt = os.urandom(16)
    times = []
    
    for _ in range(iterations):
        start = time.time()
        hashlib.scrypt(
            password=b"benchmark password",
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=32
        )
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    return avg_time

# Test different parameter sets
print("Benchmarking scrypt parameters:")
for n in [2**10, 2**12, 2**14, 2**16]:
    avg_time = benchmark_scrypt(n=n, r=8, p=1)
    memory = calculate_memory_usage(n, 8)
    print(f"n={n}, r=8, p=1: {avg_time:.3f}s, Memory: {memory}")
```

## Error Handling

### Common Errors and Solutions

```python
import hashlib
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# 1. n must be a power of 2
try:
    hashlib.scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=100,  # Not a power of 2!
        r=8,
        p=1,
        dklen=32
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use n=2^14, 2^16, etc.

# 2. n must be >= 2
try:
    hashlib.scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=1,  # Too small!
        r=8,
        p=1,
        dklen=32
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use n >= 2

# 3. r and p must be >= 1
try:
    kdf = Scrypt(
        salt=os.urandom(16),
        length=32,
        n=2**14,
        r=0,  # Too small!
        p=1
    )
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Use r >= 1, p >= 1

# 4. Salt must be bytes
try:
    hashlib.scrypt(
        password=b"password",
        salt="not bytes",  # String instead of bytes!
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
except TypeError as e:
    print(f"TypeError: {e}")
    # Solution: Use salt=b"..." or os.urandom(16)

# 5. Password must be bytes
try:
    hashlib.scrypt(
        password="password",  # String instead of bytes!
        salt=os.urandom(16),
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
except TypeError as e:
    print(f"TypeError: {e}")
    # Solution: Use password.encode('utf-8') or b"password"

# 6. Buffer size mismatch in derive_into()
try:
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    buffer = bytearray(16)  # Wrong size!
    kdf.derive_into(b"password", buffer)
except ValueError as e:
    print(f"ValueError: {e}")
    # Solution: Buffer must match length parameter

# 7. Already finalized (calling derive/verify multiple times)
try:
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key1 = kdf.derive(b"password")
    key2 = kdf.derive(b"password")  # Already used!
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    # Solution: Create new Scrypt instance for each derivation
```

### Memory Limit Exceeded

Handle cases where parameters exceed available memory:

```python
import hashlib
import os

def safe_scrypt(password: bytes, salt: bytes, n: int, r: int, p: int, 
                dklen: int, max_memory_mb: int = 512) -> bytes:
    """Derive key with memory limit protection."""
    estimated_memory_mb = (n * r * 128) / (1024 * 1024)
    
    if estimated_memory_mb > max_memory_mb:
        raise MemoryError(
            f"Parameters would use ~{estimated_memory_mb:.1f} MiB, "
            f"exceeds limit of {max_memory_mb} MiB"
        )
    
    maxmem_bytes = max_memory_mb * 1024 * 1024
    return hashlib.scrypt(
        password=password,
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen,
        maxmem=maxmem_bytes
    )

# Usage with memory protection
try:
    key = safe_scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=2**20,  # Would use ~8 GiB
        r=8,
        p=1,
        dklen=32,
        max_memory_mb=512  # Limit to 512 MiB
    )
except MemoryError as e:
    print(f"Memory limit exceeded: {e}")
    # Fallback to lower parameters
    key = safe_scrypt(
        password=b"password",
        salt=os.urandom(16),
        n=2**14,  # Uses ~128 MiB
        r=8,
        p=1,
        dklen=32,
        max_memory_mb=512
    )
```

## See Also

- [Advanced Usage and Examples](references/01-advanced-usage.md) - Complete examples, advanced patterns, and troubleshooting
