# Nuitka Performance Guide

Optimization strategies, compiler selection, caching, LTO, PGO, and benchmarking techniques for maximum performance.

## Performance Characteristics

### Expected Speedups

Benchmark results from pystone (higher is better):

| Python | Uncompiled | Compiled (LTO) | Compiled (PGO) |
|--------|------------|----------------|----------------|
| Debian Python 2.7 | 137,497 (1.0x) | 460,995 (3.35x) | 503,681 (3.66x) |
| Nuitka Python 2.7 | 144,074 (1.05x) | 479,271 (3.49x) | 511,247 (3.72x) |

**Typical improvements**:
- **Startup time**: 2-5x faster (no bytecode interpretation overhead)
- **Tight loops**: 2-4x faster (constant propagation, type inference)
- **Function calls**: Reduced overhead through inlining
- **Numeric operations**: Near C speed for simple arithmetic

### What Gets Optimized

1. **Constant propagation** - Values determined at compile time
2. **Type specialization** - int, float, str operations optimized
3. **Function inlining** - Small functions inlined at call sites
4. **Dead code elimination** - Unreachable code removed
5. **Loop optimizations** - Loop invariant code motion

### What Doesn't Get Optimized

1. **Dynamic behavior** - `eval()`, `exec()`, dynamic imports
2. **C extension calls** - Still go through Python C API
3. **Interpreter overhead** - GIL still acquired for Python calls
4. **Runtime-discovered types** - Type inference is compile-time only

## Compiler Selection

### Windows Compiler Comparison

| Compiler | Speed | Quality | Memory Usage | Recommendation |
|----------|-------|---------|--------------|----------------|
| MinGW64 | Fastest | Excellent | Medium | **Recommended** |
| MSVC 2022 | Fast | Excellent | Low | Good alternative |
| clang-cl | Medium | Good | Medium | Not recommended |

**MinGW64 advantages**:
- ~20% faster generated binaries (pystone benchmark)
- Auto-downloaded by Nuitka
- C11 support built-in
- No Visual Studio installation required

**MSVC advantages**:
- Lower memory usage during compilation
- Better integration with Windows SDK
- Required for Python 3.13+ on Windows

### Linux/macOS Compiler Comparison

| Compiler | Speed | Quality | Availability |
|----------|-------|---------|--------------|
| clang | Fastest | Excellent | macOS default, Linux optional |
| gcc 5.1+ | Fast | Excellent | Most Linux distros |

**Recommendation**: Use clang if available, otherwise gcc.

### Using Specific Compilers

```bash
# Use MinGW64 (Windows, auto-downloaded)
python -m nuitka --mingw64 program.py

# Use MSVC (Windows)
python -m nuitka --msvc=2022 program.py

# Use clang (Linux/macOS/Windows)
python -m nuitka --clang program.py

# Use zig compiler (all platforms)
python -m nuitka --zig program.py
```

## Link-Time Optimization (LTO)

### What is LTO?

LTO performs optimization across compilation unit boundaries:
- Cross-module inlining
- Dead code elimination across modules
- Better register allocation
- Whole-program analysis

### Enabling LTO

```bash
# Enable LTO (recommended for release builds)
python -m nuitka --lto=yes --standalone program.py

# Disable LTO (faster compilation, smaller speedup)
python -m nuitka --lto=no program.py

# Auto-detect (default)
python -m nuitka --lto=auto program.py
```

### LTO Trade-offs

| Aspect | With LTO | Without LTO |
|--------|----------|-------------|
| Compilation time | 2-3x slower | Fast |
| Memory usage | Higher | Lower |
| Binary size | Smaller | Larger |
| Runtime speed | 10-30% faster | Baseline |
| Incremental builds | Slower | Faster |

### When to Use LTO

**Use LTO**:
- Release builds for distribution
- Performance-critical applications
- When binary size matters
- Final compilation (not development)

**Skip LTO**:
- Development/iteration cycles
- Memory-constrained systems (< 8GB RAM)
- Very large projects (compilation takes hours)
- When incremental compilation is important

### LTO and Memory

LTO increases memory usage significantly:

```bash
# If running out of memory with LTO:
python -m nuitka --lto=no --low-memory program.py

# Or limit parallel jobs
python -m nuitka --lto=yes --jobs=2 program.py
```

## Profile-Guided Optimization (PGO)

### What is PGO?

PGO uses runtime profiling data to optimize:
- Hot paths identified and optimized more aggressively
- Branch prediction tuned to actual usage
- Function ordering for better cache locality
- Inlining decisions based on call frequency

### Two-Pass PGO Process

**Pass 1: Instrumentation**
```bash
# Compile with instrumentation
python -m nuitka --pgo-c --standalone program.py

# Run with representative workload
./program.dist/program --typical-workload

# Multiple runs for better data
for i in {1..10}; do ./program.dist/program --test-case-$i; done
```

**Pass 2: Optimization**
```bash
# Recompile using profile data
python -m nuitka --pgo-c=yes --standalone program.py

# Deploy optimized binary
./program.dist/program
```

### PGO Workload Selection

Choose workloads that represent typical usage:

```python
# good_workload.py - represents real usage patterns
def main():
    # Load typical data
    data = load_realistic_dataset()
    
    # Perform common operations
    for item in data:
        process_item(item)
        maybe_do_something_expensive(item)
    
    # Save results
    save_results(compute_summary(data))
```

**Avoid**:
- Synthetic benchmarks (not representative)
- Edge cases (rarely hit in production)
- Testing/debugging paths

### PGO Trade-offs

| Aspect | With PGO | Without PGO |
|--------|----------|-------------|
| Compilation time | 2x (two passes) | Baseline |
| Setup complexity | Higher (need workload) | Simple |
| Runtime speed | 5-20% faster than LTO alone | Baseline |
| Optimization quality | Best possible | Very good |

### When to Use PGO

**Use PGO**:
- Performance-critical applications
- Well-understood workload patterns
- Final release builds
- When every percent of speed matters

**Skip PGO**:
- Development builds
- Variable/unpredictable workloads
- When LTO is already too slow
- Applications dominated by I/O or external calls

## Caching Strategies

### Nuitka's Internal Caches

Nuitka caches various artifacts to speed up repeated compilations:

| Cache Type | Purpose | Environment Variable |
|------------|---------|---------------------|
| Downloads | External tools (MinGW, ccache) | `NUITKA_CACHE_DIR_DOWNLOADS` |
| CCache | GCC object files | `NUITKA_CACHE_DIR_CCACHE` |
| ClCache | MSVC object files | `NUITKA_CACHE_DIR_CLCACHE` |
| Bytecode | Demoted module bytecode | `NUITKA_CACHE_DIR_BYTECODE` |
| DLL Dependencies | Windows DLL analysis | `NUITKA_CACHE_DIR_DLL_DEPENDENCIES` |

### Global Cache Directory

```bash
# Override default cache location
export NUITKA_CACHE_DIR=/path/to/cache
python -m nuitka --standalone program.py

# Per-cache overrides
export NUITKA_CACHE_DIR_CCACHE=/fast_disk/ccache
export NUITKA_CACHE_DIR_BYTECODE=/fast_disk/bytecode
```

### CCache for GCC

**What is ccache**: C compiler caching system that stores compilation results.

**Benefits**:
- Repeated compilations are instant
- Changes to unrelated files don't recompile everything
- Can share cache across builds/machines

**Setup (Linux)**:
```bash
sudo apt install ccache
ccache -s  # Show stats
```

**Setup (macOS)**:
```bash
brew install ccache
```

**Setup (Windows)**:
Nuitka auto-downloads ccache for MinGW64. For MSVC, use clcache (built-in).

**Configuration**:
```bash
# Set cache size limit
ccache -M 10G

# Show statistics
ccache -s

# Clear cache
ccache -C
```

**Nuitka integration**: Automatic if ccache is in PATH.

### ClCache for MSVC

Built into Nuitka for MSVC compilation:

```bash
# ClCache is automatic with MSVC
python -m nuitka --msvc=2022 program.py

# Show clcache stats
clcache -s

# Clear clcache
clcache -z
```

### Bytecode Cache

For demoted modules (uncompiled Python):

```bash
# Bytecode is cached automatically
python -m nuitka --demote=pandas --standalone program.py

# Clear bytecode cache
export NUITKA_CACHE_DIR_BYTECODE=/tmp/fresh_bytecode_cache
```

## Low-Memory Compilation

### Memory-Constrained Builds

For systems with limited RAM:

```bash
# Enable low-memory mode
python -m nuitka --low-memory --standalone program.py

# Limit parallel jobs
python -m nuitka --jobs=1 --standalone program.py

# Disable LTO (uses less memory)
python -m nuitka --lto=no --low-memory program.py
```

### Low-Memory Trade-offs

| Option | Memory Savings | Time Cost |
|--------|----------------|-----------|
| `--low-memory` | ~50% | +20-50% time |
| `--jobs=1` | ~80% (on 8-core) | +300-700% time |
| `--lto=no` | ~40% | No time cost |
| Combined | ~90% | +100-200% time |

### Memory Error Solutions

**Error**: `fatal error: error writing to -: Invalid argument`

**Solutions**:
1. Enable `--low-memory`
2. Reduce `--jobs` count
3. Disable LTO
4. Add swap space
5. Use 64-bit compiler (not 32-bit)

**Error**: `fatal error C1002: compiler is out of heap space`

**Solutions**:
1. Use MSVC instead of MinGW64 (lower memory)
2. Reduce `--jobs`
3. Increase system RAM or swap

## Job Parallelism

### Controlling Parallel Jobs

```bash
# Use all available CPU cores (default)
python -m nuitka --standalone program.py

# Limit to 4 jobs
python -m nuitka --jobs=4 --standalone program.py

# Single-threaded compilation
python -m nuitka --jobs=1 --standalone program.py

# Explicit job count
python -m nuitka -j8 --standalone program.py
```

### Optimal Job Count

**Formula**: `jobs = CPU cores - 1` (leave one core free)

| System | Recommended Jobs |
|--------|------------------|
| 4-core | 3-4 |
| 8-core | 6-7 |
| 16-core | 12-14 |
| Memory-constrained | 1-2 |

### Job Count vs Memory

More jobs = more memory:

```bash
# High memory system (32GB+)
python -m nuitka --jobs=16 --lto=yes program.py

# Medium memory (16GB)
python -m nuitka --jobs=8 --lto=yes program.py

# Low memory (8GB)
python -m nuitka --jobs=4 --lto=no program.py

# Very low memory (4GB)
python -m nuitka --jobs=1 --low-memory --lto=no program.py
```

## Benchmarking Compiled Code

### Pystone Benchmark

Nuitka includes pystone for performance testing:

```bash
# Run benchmark
BENCH=1 python tests/benchmarks/pystone.py

# Compile and benchmark
python -m nuitka --lto=yes tests/benchmarks/pystone.py
BENCH=1 ./pystone.bin

# Statistical benchmark (1000 runs)
RUNS=1000
for i in $(seq 1 $RUNS); do
    BENCH=1 ./pystone.bin
done | sort -n | head -n 1  # Best time
```

### Custom Benchmarking

```python
# benchmark.py
import timeit

def function_to_benchmark():
    # Code to benchmark
    total = 0
    for i in range(10000):
        total += i * i
    return total

if __name__ == "__main__":
    # Warmup
    function_to_benchmark()
    
    # Benchmark
    time = timeit.timeit(function_to_benchmark, number=1000)
    print(f"1000 calls: {time:.3f}s ({time/1000*1000:.3f}ms per call)")
```

Compare uncompiled vs compiled:
```bash
# Uncompiled
python benchmark.py

# Compile and run
python -m nuitka --lto=yes benchmark.py
./benchmark.bin
```

### Real-World Benchmarking

```python
# realistic_benchmark.py
import time

def main_workflow():
    # Simulate real application workflow
    start = time.time()
    
    # Phase 1: Initialization
    data = load_large_dataset()
    
    # Phase 2: Processing
    results = []
    for item in data:
        results.append(process_item(item))
    
    # Phase 3: Aggregation
    summary = aggregate(results)
    
    elapsed = time.time() - start
    print(f"Total time: {elapsed:.3f}s")
    return summary

if __name__ == "__main__":
    # Multiple runs for average
    times = []
    for _ in range(10):
        main_workflow()
```

## Static vs Dynamic Linking

### Static Linking Benefits

```bash
# Static link libpython (when available)
python -m nuitka --static-libpython=yes --standalone program.py
```

**Advantages**:
- Fewer runtime dependencies
- Better compatibility across systems
- Potentially smaller distribution size
- Faster startup (no dynamic loading)

**Disadvantages**:
- Larger binary size (sometimes)
- Not available on all platforms
- Requires static libpython build

### Platform Availability

| Platform | Static Linking | Notes |
|----------|----------------|-------|
| Windows | No | Always dynamic |
| Linux | Yes (some builds) | Anaconda, self-compiled Python |
| macOS | Yes (some builds) | Anaconda with `libpython-static` |
| FreeBSD | Limited | Depends on Python build |

### Installing Static libpython

**Anaconda (Linux/macOS)**:
```bash
conda install libpython-static
python -m nuitka --static-libpython=yes program.py
```

**Self-compiled Python**:
```bash
# Configure without shared libraries
./configure --disable-shared
make
make install
```

## Unexpected Slowdowns

### Unicode String Overhead

Calling into Python DLL from compiled code has overhead, especially for Unicode:

**Problem**: Mixed compiled/uncompiled code with heavy Unicode processing

**Solution**: 
- Compile more modules (reduce boundary crossings)
- Use static linking when possible
- Keep Unicode-heavy code in same compilation unit

### GIL Contention

Nuitka doesn't remove the GIL - multi-threaded Python code still has GIL overhead:

```python
# This won't be faster with Nuitka (GIL-bound)
from threading import Thread

def worker():
    for i in range(1000000):
        process_data(i)  # Python operations

# Use multiprocessing instead for CPU-bound work
from multiprocessing import Pool

with Pool() as p:
    results = p.map(process_data, range(1000000))
```

### I/O-Bound Applications

Nuitka provides minimal benefit for I/O-bound code:

**Little improvement**:
- File I/O heavy applications
- Network I/O dominated code
- Database query heavy applications

**Good improvement**:
- CPU-intensive data processing
- Numeric computations
- String manipulation
- Algorithm-heavy code

## Optimization Checklist

### For Maximum Performance

1. ✅ Use `--lto=yes` for final builds
2. ✅ Enable PGO with representative workload
3. ✅ Use MinGW64 (Windows) or clang (Linux/macOS)
4. ✅ Static link libpython if available
5. ✅ Compile all performance-critical modules
6. ✅ Enable ccache/clcache for faster iteration
7. ✅ Use `--follow-imports` to compile dependencies
8. ✅ Demote only truly large/unnecessary packages

### For Fast Development

1. ✅ Skip LTO during development
2. ✅ Use ccache/clcache
3. ✅ Demote third-party libraries
4. ✅ Use `--jobs` appropriate for system
5. ✅ Compile only main modules, not dependencies

### Monitoring Compilation

```bash
# Show progress
python -m nuitka --show-progress program.py

# Show memory usage
python -m nuitka --show-memory program.py

# Show included modules
python -m nuitka --show-modules program.py

# Verbose output
python -m nuitka --verbose program.py
```
