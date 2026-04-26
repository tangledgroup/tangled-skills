# Choosing Parameters

## Quick Start

Use `PasswordHasher` with its default values — they are based on the RFC 9106 low-memory profile and work well for most environments. Verify the timing is appropriate for your hardware using the CLI:

```console
$ python -m argon2
Running Argon2id 100 times with:
hash_len: 32 bytes
memory_cost: 65536 KiB
parallelism: 4 threads
time_cost: 3 iterations

Measuring...

45.7ms per password verification
```

## RFC 9106 Recommendations

[RFC 9106 Section 4](https://www.rfc-editor.org/rfc/rfc9106.html#section-4) provides two recommended parameter sets, available in `argon2.profiles`:

### FIRST RECOMMENDED (RFC_9106_HIGH_MEMORY)

```python
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_HIGH_MEMORY

ph = PasswordHasher.from_parameters(RFC_9106_HIGH_MEMORY)
```

- type: Argon2id
- memory_cost: 2,097,152 KiB (2 GiB)
- time_cost: 1
- parallelism: 4
- hash_len: 32 bytes
- salt_len: 16 bytes

Requires beefy 2 GiB per hash — be careful in memory-constrained systems.

### SECOND RECOMMENDED (RFC_9106_LOW_MEMORY) — Default

```python
from argon2.profiles import RFC_9106_LOW_MEMORY
```

- type: Argon2id
- memory_cost: 65,536 KiB (64 MiB)
- time_cost: 3
- parallelism: 4
- hash_len: 32 bytes
- salt_len: 16 bytes

This is the default profile used by `PasswordHasher`.

### Other Profiles

- **PRE_21_2** — defaults from argon2-cffi 18.2.0 to 21.1.0 (100 MiB, parallelism 8)
- **CHEAPEST** — minimal parameters for testing only, do not use in production

## Fine-Tuning Parameters

If you need custom parameters, follow this process:

1. **Choose variant** (`type`). Default: Argon2id (`argon2.low_level.Type.ID`).

2. **Choose parallelism** — number of threads per call. RFC recommends 4. Consider your server's thread model.

3. **Choose memory_cost** — how much RAM each call can afford, in kibibytes (1 KiB = 1024 bytes). The 64 MiB default is conservative; Docker containers with limited memory may experience swapping.

4. **Choose salt_len** — 16 bytes is sufficient for all applications. Reduce to 8 bytes only under space constraints.

5. **Choose hash_len** — 32 bytes recommended, 16 bytes sufficient for password verification.

6. **Determine target time** — more time means more security, less time means better user experience. RFC used to recommend under 500ms. A recommendation for concurrent logins is under 0.5ms (but that's very low). The truth is somewhere between: defaults land at ~50ms.

   Note: Even 1 second of hashing won't protect against bad passwords from "top 10,000 passwords" lists.

7. **Measure** — start with `time_cost=1` and measure. Increase `time_cost` until within your target time. If `time_cost=1` is too slow, lower `memory_cost`.

## Memory-Constrained Environments

The 64 MiB default can cause problems in Docker containers or embedded systems, leading to apparent freezes caused by swapping. In such environments:

- Use a lower `memory_cost`
- Test with the CLI: `python -m argon2 -m 32768` (32 MiB)
- Consider the `CHEAPEST` profile for quick testing, then find a production-appropriate balance

## WebAssembly Environments

In Pyodide/WebAssembly environments, parallelism must be set to 1. The `get_default_parameters()` function handles this automatically as of version 25.1.0. Attempting to use parallelism > 1 raises `UnsupportedParametersError`.

## OWASP Reference

The [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#argon2id) provides additional guidance on Argon2 parameter selection.
