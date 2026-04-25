# Parameter Selection and Performance Tuning

Guide to choosing Argon2 parameters for your specific use case, including RFC 9106 profiles and performance optimization.

## Understanding Parameters

### Core Parameters

| Parameter | Description | Typical Values | Impact |
|-----------|-------------|----------------|--------|
| `time_cost` | Number of iterations | 1-10 | Higher = slower but more secure |
| `memory_cost` | Memory in KiB | 65536-2097152 | Higher = more GPU-resistant |
| `parallelism` | Thread count (lanes) | 1-8 | Match CPU cores, affects memory layout |
| `hash_len` | Output hash length (bytes) | 16-32 | 32 bytes sufficient for passwords |
| `salt_len` | Salt length (bytes) | 8-16 | 16 bytes recommended |

### Argon2 Variants

```python
from argon2.low_level import Type

# Type.ID - Argon2id (default, recommended)
# Hybrid of Argon2i and Argon2d, resistant to side-channel and GPU attacks

# Type.I - Argon2i  
# Side-channel resistant, more CPU-bound

# Type.D - Argon2d
# Fastest but vulnerable to side-channel attacks, GPU-optimized
```

**Use Argon2id unless you have a specific reason not to.**

## RFC 9106 Profiles

The official Internet standard (RFC 9106) provides two recommended parameter sets:

### RFC_9106_LOW_MEMORY (Default)

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY

ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)

# Parameters:
# - memory_cost: 65536 KiB (64 MiB)
# - time_cost: 3 iterations
# - parallelism: 4 threads
# - hash_len: 32 bytes
# - salt_len: 16 bytes
# - type: Argon2id
```

**Use case**: General-purpose password hashing, Docker containers, shared hosting.

**Expected verification time**: 40-50ms on modern hardware.

### RFC_9106_HIGH_MEMORY

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_HIGH_MEMORY

ph = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)

# Parameters:
# - memory_cost: 2097152 KiB (2 GiB)
# - time_cost: 1 iteration
# - parallelism: 4 threads
# - hash_len: 32 bytes
# - salt_len: 16 bytes
# - type: Argon2id
```

**Use case**: High-security applications, dedicated servers, offline credential protection.

**Expected verification time**: 800-1000ms on modern hardware.

## Choosing Parameters

### Step-by-Step Selection Process

1. **Choose the variant**: Use `Type.ID` (Argon2id) for all new applications.

2. **Determine parallelism**: Match to available CPU cores.
   ```python
   import os
   parallelism = min(os.cpu_count() or 4, 8)  # Cap at 8 threads
   ```

3. **Set memory cost**: Start with 64 MiB (65536 KiB) minimum.
   - Low-memory environments: 32-64 MiB
   - Standard applications: 64-128 MiB
   - High-security: 256 MiB - 2 GiB

4. **Choose hash length**: 32 bytes (256 bits) sufficient for passwords.

5. **Set salt length**: 16 bytes standard, 8 bytes if space-constrained.

6. **Tune time cost**: Adjust to achieve target verification time (see below).

### Performance Testing

Use the CLI to benchmark parameters:

```bash
# Test default low-memory profile
python -m argon2 --profile RFC_9106_LOW_MEMORY

# Output example:
# Running Argon2id 100 times with:
# hash_len: 32 bytes
# memory_cost: 65536 KiB
# parallelism: 4 threads
# time_cost: 1 iterations
# Measuring...
# 45.2ms per password verification

# Test high-memory profile
python -m argon2 --profile RFC_9106_HIGH_MEMORY

# Output example:
# 866.5ms per password verification

# Custom parameters
python -m argon2 -m 131072 -t 2 -p 2
```

### Target Verification Times

| Use Case | Target Time | Rationale |
|----------|-------------|-----------|
| Interactive login | 40-100ms | Good UX, reasonable security |
| API authentication | 50-200ms | Balance latency and security |
| High-security systems | 200-500ms | Maximum practical security |
| Offline credential storage | 500ms+ | No UX concerns, maximum security |

**Important**: Even 1 second verification won't protect against weak passwords from "top 10,000" lists. Use password strength requirements alongside hashing.

## Custom Parameter Configuration

### Creating Custom PasswordHasher

```python
from argon2 import PasswordHasher
from argon2.low_level import Type

# Custom configuration for specific needs
ph = PasswordHasher(
    time_cost=4,           # More iterations for security
    memory_cost=131072,    # 128 MiB memory
    parallelism=4,         # 4 threads
    hash_len=32,           # 256-bit hash
    salt_len=16,           # 128-bit salt
    type=Type.ID           # Argon2id (default)
)

# Hash and verify as normal
hash = ph.hash("password")
ph.verify(hash, "password")
```

### Memory-Constrained Environments

For Docker containers or embedded systems:

```python
from argon2 import PasswordHasher

# Reduced parameters for constrained environments
ph_container = PasswordHasher(
    time_cost=2,           # Fewer iterations
    memory_cost=32768,     # 32 MiB (minimum recommended)
    parallelism=2,         # 2 threads
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

# Test verification time first!
import time
start = time.time()
for _ in range(10):
    ph_container.hash("test")
avg_time = (time.time() - start) / 10 * 1000
print(f"Average verification time: {avg_time:.1f}ms")
```

**Warning**: Memory costs below 32 MiB significantly reduce security against GPU attacks.

### High-Performance Tuning

For systems needing faster verification:

```python
from argon2 import PasswordHasher

# Profile for lower latency (reduced security)
ph_fast = PasswordHasher(
    time_cost=1,           # Minimum iterations
    memory_cost=65536,     # Keep memory high for GPU resistance
    parallelism=8,         # Use more cores
    hash_len=32,
    salt_len=16,
    type=Type.ID
)
```

## Parameter Migration Strategy

### Detecting Outdated Hashes

```python
from argon2 import PasswordHasher

# Current configuration
ph_current = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4
)

# Legacy configuration (older system)
ph_legacy = PasswordHasher(
    time_cost=1,
    memory_cost=32768,
    parallelism=2
)

def migrate_user_hash(user_hash):
    """Check if hash needs migration to current parameters."""
    if ph_current.check_needs_rehash(user_hash):
        print("Hash uses outdated parameters")
        return True
    return False
```

### Progressive Rehashing

```python
import argon2

ph = argon2.PasswordHasher()

def authenticate_and_migrate(username, password):
    """Authenticate and rehash if parameters changed."""
    user = db.get_user(username)
    
    try:
        ph.verify(user.password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
    
    # Rehash with current parameters
    if ph.check_needs_rehash(user.password_hash):
        new_hash = ph.hash(password)
        db.update_password_hash(username, new_hash)
        print(f"Rehashed password for {username}")
    
    return True
```

This approach migrates hashes gradually as users log in, avoiding bulk reprocessing.

## Environment-Specific Recommendations

### Web Applications

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY

# Standard web app configuration
ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
# ~50ms verification, good UX for login forms
```

### APIs and Mobile Backends

```python
from argon2 import PasswordHasher

# API configuration - slightly faster for latency-sensitive endpoints
ph_api = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)
# ~30-40ms verification
```

### High-Security Systems

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_HIGH_MEMORY

# Maximum security for financial/admin systems
ph_secure = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)
# ~800-1000ms verification, acceptable for infrequent logins
```

### Containerized Applications

```python
from argon2 import PasswordHasher

# Docker/container configuration - watch memory limits!
ph_container = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # Ensure container has >100MiB memory limit
    parallelism=2,       # Match container CPU limits
    hash_len=32,
    salt_len=16
)
```

**Critical**: Set appropriate memory limits in Docker:
```dockerfile
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M  # Must exceed argon2 memory_cost
```

## Troubleshooting Parameter Issues

### Memory Exhaustion

**Symptom**: Application crashes or swaps heavily during hashing.

**Solution**: Reduce `memory_cost` or increase container memory limits.

```python
# Check available memory
import psutil
available_mb = psutil.virtual_memory().available / (1024 * 1024)
print(f"Available memory: {available_mb:.0f} MB")

# Adjust accordingly
safe_memory_cost = min(65536, int(available_mb * 0.1 * 1024))  # Use 10% of available
ph = PasswordHasher(memory_cost=safe_memory_cost)
```

### Slow Verification

**Symptom**: Login takes too long (>500ms).

**Solution**: Reduce `time_cost` first, then `memory_cost` if needed.

```python
# Benchmark current performance
import time

ph = PasswordHasher()
times = []
for _ in range(10):
    start = time.time()
    ph.hash("test_password")
    times.append((time.time() - start) * 1000)

avg_time = sum(times) / len(times)
print(f"Average hash time: {avg_time:.1f}ms")

# If >200ms, reduce time_cost
if avg_time > 200:
    ph_faster = PasswordHasher(time_cost=2, memory_cost=65536)
```

### CPU Starvation

**Symptom**: High CPU usage during peak login times.

**Solution**: Argon2-cffi releases the GIL, but consider async patterns:

```python
import asyncio
import argon2

ph = argon2.PasswordHasher()

async def verify_async(password_hash, password):
    """Run verification in thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, ph.verify, password_hash, password
    )
```
