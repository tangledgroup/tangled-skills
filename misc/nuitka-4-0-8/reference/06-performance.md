# Performance

## Overview

Nuitka typically provides significant performance improvements over uncompiled CPython. The exact speedup depends on the program characteristics, optimization flags used, and workload type.

## Pystone Benchmark Results

Pystone is a standard Python benchmark (higher values = better performance). Results show compiled Nuitka vs uncompiled Python:

**Debian Python 2.7:**

- Uncompiled: 137,497 stones/sec (1.000x baseline)
- Compiled with LTO: 460,995 stones/sec (3.35x speedup)
- Compiled with PGO: 503,682 stones/sec (3.66x speedup)

**Nuitka-compiled Python 2.7:**

- Uncompiled: 144,075 stones/sec (1.05x baseline)
- Compiled with LTO: 479,272 stones/sec (3.49x speedup)
- Compiled with PGO: 511,247 stones/sec (3.72x speedup)

## Optimization Flags

### Link-Time Optimization (LTO)

```bash
python -m nuitka --lto=yes program.py
```

LTO enables cross-module optimization at the C compiler level. It typically provides 2-4x speedup over uncompiled Python for CPU-bound code. Compilation time increases significantly.

### Profile-Guided Optimization (PGO)

```bash
python -m nuitka --pgo program.py
```

PGO uses runtime profiling to guide compiler decisions. It provides additional speedup on top of LTO (roughly 10-15% more). Requires running the program with representative workloads during the training phase.

### Combined LTO + PGO

```bash
python -m nuitka --lto=yes --pgo program.py
```

For maximum performance, use both together. This is the recommended approach for production builds of performance-critical applications.

## Tips for Maximizing Performance

- **Use `--deployment`** — disables runtime safety checks and helpers, reducing overhead
- **Use `--python-flag=no_docstrings`** — removes docstrings to reduce memory usage
- **Use `--python-flag=no_asserts`** — removes assert statements for production builds
- **Minimize compiled modules** — compiling fewer modules (using normal Python for some) can be faster at runtime due to reduced startup overhead
- **Choose the fastest C compiler** — GCC and Clang generally produce better optimized code than MinGW on Linux. On Windows, MSVC is the best choice.

## Caching Compilation Results

Nuitka caches compiled C object files to speed up repeated builds. The cache persists between compilations of the same code.

### Controlling Cache Storage

Use environment variables or command-line options to control where the cache is stored:

```bash
# Set custom cache directory
export NuitkaCacheDir=/path/to/cache
python -m nuitka --follow-imports program.py
```

### Choosing the Fastest C Compilers

- **Linux:** GCC or Clang from the system. Clang often produces smaller binaries; GCC may produce faster code in some cases.
- **Windows:** MSVC (Visual Studio) is the default and best choice. MinGW64 is an alternative but slower for Python 3.13+.
- **macOS:** System Clang via Xcode tools.
- **Cross-compilation:** Use Zig (`--zig`) for cross-platform compilation.

## Addressing Unexpected Slowdowns

If a compiled program runs slower than uncompiled Python:

1. Check that `--follow-imports` is used — compiling only the entry point means most code still runs as bytecode
2. Verify the C compiler is working correctly
3. Try with `--lto=yes` for optimization
4. Use `--report=report.html` to check which modules were compiled
5. Ensure you're not hitting deployment mode safety checks — use `--deployment` for production

## Compilation Time Optimization

- Use ccache or sccache for C compilation caching (Nuitka integrates with these automatically)
- Compile fewer modules when possible — let Python handle modules that don't need acceleration
- Use incremental builds — Nuitka only recompiles changed files
- Consider parallel compilation if the C compiler supports it
