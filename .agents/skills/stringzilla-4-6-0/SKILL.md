---
name: stringzilla-4-6-0
description: High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in C/C++/Python/Rust/JavaScript/Swift/Go. Use when optimizing string operations for big data processing, bioinformatics, or high-throughput applications requiring up to 10x faster CPU throughput and up to 100x faster GPU kernels via StringZillas parallel backends.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - simd
  - string-processing
  - search
  - hashing
  - sorting
  - bioinformatics
  - performance
  - swar
  - cuda
category: library
external_references:
  - https://pypi.org/project/stringzilla/
  - https://github.com/ashvardanian/StringZilla
  - https://docs.rs/stringzilla
  - https://crates.io/crates/stringzilla
  - https://ashvardanian.com/posts/stringzilla/
---

# StringZilla 4.6.0

## Overview

StringZilla is a high-performance string library using SIMD and SWAR to accelerate binary and UTF-8 string operations on modern CPUs and GPUs. It delivers up to 10x higher CPU throughput in C, C++, Rust, Python, and other languages, and can be 100x faster than existing GPU kernels.

The library is split into two layers:

1. **StringZilla** — single-header C library and C++ wrapper for serial string operations
2. **StringZillas** — parallel CPU/GPU backends for large-batch operations (multi-CPU, CUDA, ROCm)

It accelerates exact and fuzzy string matching, hashing, edit distance computations, sorting, provides allocation-free lazily-evaluated smart-iterators, random-string generators, rolling fingerprints, and Unicode case-folding with full Unicode 17.0 support.

Compatible across little-endian and big-endian architectures, 32-bit and 64-bit hardware, all operating systems and compilers, and both ASCII and UTF-8 encoded inputs. Header-only for C/C++ (no build step required), with bindings for Python, Rust, JavaScript, Swift, and Go.

## When to Use

- Data-engineers parsing large datasets like CommonCrawl, RedPajama, or LAION
- Software engineers optimizing string-heavy applications and services
- Bioinformaticians computing edit distances for sequence alignment
- DBMS developers optimizing `LIKE`, `ORDER BY`, and `GROUP BY` operations
- Hardware designers needing a SWAR baseline for string-processing
- Applications requiring fast SHA-256 checksums with memory-mapped file support
- Unicode-aware case-insensitive search across 1M+ codepoints
- MinHash-based document similarity via rolling fingerprints

## Core Concepts

**SIMD (Single Instruction, Multiple Data)**: StringZilla exploits vector instructions (SSE4.2, AVX2, AVX-512 on x86; NEON, SVE, SVE2 on ARM) to process multiple characters per CPU cycle.

**SWAR (SIMD Within A Register)**: When no SIMD is available, 64-bit SWAR algorithms still outperform libc and STL baselines on most platforms.

**Dynamic Dispatch**: StringZilla auto-detects the best backend at runtime. You can also force specific backends (`sz_find_westmere`, `sz_find_neon`, etc.) for guaranteed performance profiles.

**StringZillas Parallel Layer**: The `stringzillas` module (Python: `pip install stringzillas-cpus` or `stringzillas-cuda`) provides batch-oriented Levenshtein distances, Needleman-Wunsch/Smith-Waterman alignment scores, and rolling fingerprints across multi-core CPUs and Nvidia GPUs.

**Memory Efficiency**: The Python `Str` class views existing memory without copying. The `File` class memory-maps files from disk. Lazy iterators (`split_iter`) achieve near-zero memory overhead for tokenization — processing 1 GB of text with 0.00 MiB increment vs 8670 MiB for native Python `str.split()`.

## Installation / Setup

### Python

```bash
pip install stringzilla         # serial algorithms
pip install stringzillas-cpus   # parallel multi-CPU backends
pip install stringzillas-cuda   # parallel Nvidia GPU backend
```

Check installed version and capabilities:

```python
import stringzilla
print(stringzilla.__version__)       # "4.6.0"
print(stringzilla.__capabilities__)  # ('serial', 'haswell', 'skylake', 'ice', 'neon', 'sve', 'sve2+aes')
```

### C/C++

Header-only — copy `stringzilla.h` (C) or `stringzilla.hpp` (C++) into your project. Or use CMake:

```cmake
FetchContent_Declare(
    stringzilla
    GIT_REPOSITORY https://github.com/ashvardanian/StringZilla.git
    GIT_TAG main
)
FetchContent_MakeAvailable(stringzilla)
```

### Rust

```toml
[dependencies]
stringzilla = ">=3"                                      # serial algorithms
stringzilla = { version = ">=3", features = ["cpus"] }   # parallel multi-CPU
stringzilla = { version = ">=3", features = ["cuda"] }   # parallel GPU
```

### JavaScript

```bash
npm install stringzilla
```

### Swift

Add to `Package.swift`:

```swift
.package(url: "https://github.com/ashvardanian/stringzilla")
```

### Go

```bash
go get github.com/ashvardanian/stringzilla/golang@latest
```

Then build the shared C library:

```bash
cmake -B build_shared -D STRINGZILLA_BUILD_SHARED=1 -D CMAKE_BUILD_TYPE=Release
cmake --build build_shared --target stringzilla_shared --config Release
export LD_LIBRARY_PATH="$PWD/build_shared:$LD_LIBRARY_PATH"
```

## Advanced Topics

**Python API**: `Str`, `Strs`, `File` classes, hashing, SHA-256, similarity scores, fingerprints → [Python API](reference/01-python-api.md)

**C/C++ API**: C99 interface, C++11 classes, compilation flags, LibC mapping → [C/C++ API](reference/02-c-cpp-api.md)

**Rust API**: Crate usage, `StringZilla` extension trait, hash integration with `std::collections` → [Rust API](reference/03-rust-api.md)

**Other Bindings**: JavaScript (Node.js), Swift, Go bindings with examples → [Other Bindings](reference/04-other-bindings.md)

**Algorithms & Design**: Search algorithms, Levenshtein diagonal approach, hashing internals, sorting strategy, Unicode case-folding → [Algorithms & Design](reference/05-algorithms.md)
