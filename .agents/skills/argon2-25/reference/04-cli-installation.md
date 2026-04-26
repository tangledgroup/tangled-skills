# CLI and Installation

## CLI Interface

argon2-cffi provides a built-in CLI for benchmarking Argon2 performance in your environment:

### Basic Benchmark

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

Runs with `PasswordHasher`'s default values (RFC 9106 low-memory profile).

### Using Profiles

```console
$ python -m argon2 --profile RFC_9106_HIGH_MEMORY
Running Argon2id 100 times with:
hash_len: 32 bytes
memory_cost: 2097152 KiB
parallelism: 4 threads
time_cost: 1 iterations

Measuring...

866.5ms per password verification
```

Pass `--profile` followed by any name from `argon2.profiles`:
- `RFC_9106_HIGH_MEMORY`
- `RFC_9106_LOW_MEMORY`
- `PRE_21_2`
- `CHEAPEST`

When using `--profile`, other parameter arguments are ignored.

### Manual Parameters

Set parameters individually:

```console
$ python -m argon2 -t 4 -m 131072 -p 2 -l 32
```

Flags:
- `-t` — time_cost (iterations)
- `-m` — memory_cost (kibibytes)
- `-p` — parallelism (threads)
- `-l` — hash_len (bytes)

This helps determine the right parameters for your specific hardware and latency requirements.

---

## Installation

### Standard Installation

```console
$ python -Im pip install argon2-cffi
```

This installs argon2-cffi with vendored Argon2 C code via the `argon2-cffi-bindings` dependency. The vendored approach is the safest and most tested.

### Binary Wheels

Pre-compiled wheels are available on PyPI for:
- macOS (including Apple Silicon via universal2)
- Windows (amd64)
- Linux (amd64, arm64)
- musl libc / Alpine Linux (i686, amd64, arm64)
- PyPy 3.8+

With a recent pip, wheels are used automatically.

### Source Distribution

If no wheel is available for your platform, a working C compiler and CFFI environment are required to build `argon2-cffi-bindings`. The C code compiles on x86, ARM, and PPC. On x86, an SSE2-optimized version is used automatically.

If installation fails, update pip first:

```console
$ python -Im pip install -U pip
```

### System-Wide Argon2

To use a system-installed Argon2 library instead of the vendored code:

```console
$ env ARGON2_CFFI_USE_SYSTEM=1 \
    python -m pip install --no-binary=argon2-cffi-bindings argon2-cffi
```

**Warning:** This can lead to build chain problems and version incompatibilities. It is your own responsibility to deal with these risks.

### Override SSE2 Detection

The build process auto-detects SSE2 support on x86. To manually control this:

```console
# Force SSE2 support
$ env ARGON2_CFFI_USE_SSE2=1 pip install argon2-cffi

# Disable SSE2 support
$ env ARGON2_CFFI_USE_SSE2=0 pip install argon2-cffi

# Auto-detect (default)
$ pip install argon2-cffi
```

Any value other than `1` or `0` is ignored and auto-detection is used.

---

## Platform Support

- **Python versions**: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- **Implementations**: CPython, PyPy
- **Free Threading**: Supported (PEP 703)
- **WebAssembly**: Supported via Pyodide (parallelism must be 1)
- **Operating Systems**: macOS, Windows, Linux (POSIX)
- **Architectures**: x86, x86_64, ARM, ARM64, PPC

## Dependencies

- `argon2-cffi-bindings` — CFFI bindings to the Argon2 C library (vendored by default)
- `cffi` — transitive dependency of argon2-cffi-bindings

## Type Hints

The package is fully typed (`py.typed` marker present). Works with mypy, pyright, and other type checkers.
