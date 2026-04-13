---
name: stringzilla-4-6
description: High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in C/C++/Python/Rust. Use when optimizing string operations for big data processing, bioinformatics, or high-throughput applications requiring up to 10x faster CPU throughput.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - simd
  - string-processing
  - search
  - hashing
  - bioinformatics
  - performance
category: tooling
required_environment_variables: []
---

# StringZilla 4.6

StringZilla is a high-performance string processing library using SIMD (AVX2, AVX-512, NEON, SVE) and SWAR techniques to accelerate binary and UTF-8 string operations on modern CPUs and GPUs. It delivers up to **10x higher CPU throughput** in C, C++, Rust, Python, and other languages, and can be **100x faster than existing GPU kernels**.

## When to Use

- Optimizing substring search, character set matching, or string sorting in performance-critical applications
- Processing large text datasets (CommonCrawl, RedPajama, LAION) with memory efficiency
- Computing edit distances and alignment scores for bioinformatics (DNA/protein sequences)
- Implementing high-throughput hashing, fingerprinting, or similarity scoring
- Replacing LibC `<string.h>` or Python `str` operations in data engineering pipelines
- Building database operations like `LIKE`, `ORDER BY`, `GROUP BY` with SIMD acceleration

## Performance Highlights

| Operation | LibC/Python | StringZilla | Speedup |
|-----------|-------------|-------------|---------|
| Substring search (`strstr`) | 7.4 GB/s (x86) | 10.6 GB/s (x86) | 1.4x |
| Reverse substring search | N/A | 10.8 GB/s (x86) | - |
| Case-insensitive UTF-8 search | 0.02 GB/s (ICU) | 3.0 GB/s | 150x |
| Unicode case-folding | 0.4 GB/s | 1.3 GB/s | 3.25x |
| Character set splitting | 0.06 GB/s (Python `re`) | 4.08 GB/s | 68x |
| SHA-256 checksums | 12.6s (hashlib) | 4.0s | 3x |
| Levenshtein distance | 1.6M CUPS | 3.4B CUPS | 2,100x |

## Installation

### Python

```bash
pip install stringzilla           # Serial algorithms (stringzilla module)
pip install stringzillas-cpus     # Parallel multi-CPU backends
pip install stringzillas-cuda     # Parallel Nvidia GPU backend
```

Verify installation:

```bash
python -c "import stringzilla; print(stringzilla.__version__)"  # Should print 4.6.x
python -c "import stringzilla; print(stringzilla.__capabilities__)"  # Available SIMD features
```

### Rust

Add to `Cargo.toml`:

```toml
[dependencies]
stringzilla = { version = "4.6", features = ["std"] }
# For parallel backends:
# stringzilla = { version = "4.6", features = ["cpus"] }
# stringzilla = { version = "4.6", features = ["cuda"] }
```

### C/C++ (Header-Only)

Copy `stringzilla.h` or `stringzilla.hpp` into your project:

```bash
git submodule add https://github.com/ashvardanian/StringZilla.git external/stringzilla
```

Or use CMake FetchContent:

```cmake
FetchContent_Declare(
    stringzilla
    GIT_REPOSITORY https://github.com/ashvardanian/StringZilla.git
    GIT_TAG v4.6.0
)
FetchContent_MakeAvailable(stringzilla)
```

## Quick Start

### Python Basic Usage

StringZilla's `Str` class provides a `str`-like interface to byte arrays without copies:

```python
from stringzilla import Str, File

# Create from various sources (no copies, just views)
text_from_str = Str('some-string')
text_from_bytes = Str(b'some-array')
text_from_file = Str(File('large-file.txt'))  # Memory-mapped file

import numpy as np
alphabet_array = np.arange(ord("a"), ord("z"), dtype=np.uint8)
text_from_array = Str(memoryview(alphabet_array))
```

### Core Operations

```python
from stringzilla import Str

text = Str('The quick brown fox jumps over the lazy dog')

# Basic operations
len(text)                    # Length
text[42]                     # Indexing -> str
text[4:8]                    # Slicing -> Str
'quick' in text              # Substring check -> bool
hash(text)                   # Hashing -> int (stable 64-bit across platforms)
str(text)                    # Convert to Python str

# Advanced search operations
import sys
contains = text.contains('substring', start=0, end=sys.maxsize)
offset = text.find('fox', start=0, end=sys.maxsize)      # First occurrence
count = text.count('o', start=0, end=sys.maxsize)        # Non-overlapping count

# Splitting (memory-efficient vs Python's str.split)
lines = text.split(separator='\n', maxsplit=sys.maxsize, keepseparator=False)
words = text.split_byteset(separator=' \t\n', keepseparator=False)  # Character set split

# Reverse operations
last_fox = text.rfind('fox')
rsplit_lines = text.rsplit(separator='\n')
```

### Character Set Operations

StringZilla provides native character set operations without regex overhead:

```python
from stringzilla import Str

text = Str('hello   world\n\ntest')

# Find first/last occurrence of any character from a set
first_ws = text.find_first_of(' \t\n\r', start=0, end=sys.maxsize)
last_ws = text.find_last_of(' \t\n\r', start=0, end=sys.maxsize)
first_alnum = text.find_first_not_of(' \t\n', start=0, end=sys.maxsize)

# Split by character sets (much faster than re.split)
tokens = text.split_byteset(separator=' \t\n\r')
tokens_rev = text.rsplit_byteset(separator=' \t\n\r')

# Trimming
stripped = text.strip(' \t\n')      # Both ends
lstripped = text.lstrip(' \t\n')    # Leading only
rstripped = text.rstrip(' \t\n')    # Trailing only
```

### Hashing

Single-shot and incremental hashing with stable 64-bit output:

```python
import stringzilla as sz

# One-shot hash (stable across all platforms)
one_shot = sz.hash(b"Hello, world!", seed=42)

# Incremental hashing (streaming)
hasher = sz.Hasher(seed=42)
hasher.update(b"Hello, ").update(b"world!")
streamed = hasher.digest()  # Same as one_shot
hex_digest = hasher.hexdigest()

assert one_shot == streamed

# SHA-256 cryptographic checksums
digest_bytes = sz.sha256(b"Hello, world!")  # 32 bytes
assert len(digest_bytes) == 32

# Incremental SHA-256 (faster for large files)
hasher = sz.Sha256()
hasher.update(b"Hello, ").update(b"world!")
digest_bytes = hasher.digest()
digest_hex = hasher.hexdigest()  # 64-char lowercase hex string

# HMAC-SHA-256 for message authentication
mac = sz.hmac_sha256(key=b"secret", message=b"Hello, world!")
```

### Large File Processing with Memory Mapping

Process gigabyte-scale files without loading into RAM:

```python
from stringzilla import Sha256, File

# Traditional approach (slow, loads file into memory)
import hashlib
with open("xlsum.csv", "rb") as f:
    hasher = hashlib.sha256()
    while chunk := f.read(4096):
        hasher.update(chunk)
checksum_old = hasher.hexdigest()

# StringZilla approach (3x faster, memory-mapped)
mapped_file = File("xlsum.csv")
checksum_new = Sha256().update(mapped_file).hexdigest()

assert checksum_old == checksum_new  # Same result: 7278165ce01a4ac1e8806c97f32feae908036ca3d910f5177d2cf375e20aeae1
```

### Unicode Case-Folding and Case-Insensitive Search

Full Unicode support for 1M+ codepoints (not just ASCII):

```python
import stringzilla as sz

# Case-folding with character expansion (ß → ss, ﬃ → ffi)
sz.utf8_case_fold('HELLO')       # b'hello'
sz.utf8_case_fold('Straße')      # b'strasse' — ß expands to "ss"
sz.utf8_case_fold('eﬃcient')     # b'efficient' — ﬃ ligature expands to "ffi"

# Case-insensitive search (handles expansions correctly)
offset1 = sz.utf8_case_insensitive_find('Der große Hund', 'GROSSE')  # 4 — finds "große"
offset2 = sz.utf8_case_insensitive_find('Straße', 'STRASSE')         # 0 — ß matches "SS"
offset3 = sz.utf8_case_insensitive_find('eﬃcient', 'EFFICIENT')      # 0 — ﬃ matches "FFI"

# Find ALL matches with iterator
haystack = 'Straße STRASSE strasse'
for match in sz.utf8_case_insensitive_find_iter(haystack, 'strasse'):
    print(match, match.offset_within(haystack))  # Yields: 'Straße', 'STRASSE', 'strasse'

# With overlapping matches
matches = list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa'))              # ['aa', 'aa'] — 2 non-overlapping
matches_overlap = list(sz.utf8_case_insensitive_find_iter('aaaa', 'aa', include_overlapping=True))  # 3 matches
```

### Memory-Efficient Collections and Iterators

Avoid materializing lists for large datasets:

```python
from stringzilla import Str, Strs

text = Str(open("enwik9.txt", "r").read())  # 1 GB file

# Python's split() creates a full list in memory (8670 MiB)
# words_python = text.split()  # DON'T DO THIS FOR LARGE FILES

# StringZilla Strs uses 4 bytes per chunk overhead (530 MiB for same data)
words = Sz.split(text)  # Memory-efficient collection

# Lazy iterators use virtually zero memory
word_count = sum(1 for _ in Sz.split_iter(text))  # 0.00 MiB increment

# Collection operations on Strs
lines: Strs = text.split(separator='\n')
batch: Strs = lines.sample(seed=42)           # 10x faster than random.choices
shuffled: Strs = lines.shuffled(seed=42)      # Shuffle all lines
sorted_lines: Strs = lines.sorted()           # Return new Strs in sorted order
order: tuple = lines.argsort()                # Like numpy.argsort

# Slice operations for sharding between workers
every_third = lines[::3]
odd_lines = lines[1::1]
last_100_reversed = lines[:-100:-1]
```

### String Transformation with Lookup Tables

High-throughput character mapping for binary data processing:

```python
import stringzilla as sz

# Create identity lookup table (256 bytes)
lut = bytes(range(256))

# Transform image data in-place (useful for bioinformatics, image processing)
image = open("/path/to/image.jpeg", "rb").read()
sz.translate(image, lut, inplace=True)

# Custom transformation: uppercase ASCII letters
lut_custom = bytes([ord('A') + (i - ord('a')) if 97 <= i <= 122 else i for i in range(256)])
text = Str('hello world')
transformed = text.translate(lut_custom, inplace=False)  # b'HELLO WORLD'
```

### Random String Generation

Fast random string generation from custom alphabets:

```python
import stringzilla as sz

# Generate random DNA sequence
dna = sz.random(length=1000, seed=42, alphabet='ACGT')
print(dna[:50])  # b'GATCGAATCT...

# Generate UUID-like hex string
hex_str = sz.random(length=36, seed=12345, alphabet='0123456789abcdef-')

# Fill mutable buffer in-place
buffer = bytearray(1024)
sz.fill_random(buffer, seed=42, alphabet=None)  # Random bytes (0-255)
```

## Similarity Scoring and Bioinformatics

Compute edit distances and alignment scores at scale:

```python
import stringzilla as sz
import stringzillas as szs
import numpy as np

# Levenshtein edit distance (byte-level)
strings_a = sz.Strs(["kitten", "flaw"])
strings_b = sz.Strs(["sitting", "lawn"])

cpu_scope = szs.DeviceScope(cpu_cores=4)  # Use 4 CPU cores

engine = szs.LevenshteinDistances(
    match=0, mismatch=2,   # Custom costs
    open=3, extend=1,      # Gap penalties (for bioinformatics)
    capabilities=("serial",)  # Or omit for auto-detection
)

distances = engine(strings_a, strings_b, device=cpu_scope)
print(distances)  # [3, 2] — kitten→sitting=3 edits, flaw→lawn=2 edits

# UTF-8 codepoint-level distances (for Unicode text)
strings_unicode_a = sz.Strs(["café", "αβγδ"])
strings_unicode_b = sz.Strs(["cafe", "αγδ"])
engine_utf8 = szs.LevenshteinDistancesUTF8(capabilities=("serial",))
distances_utf8 = engine_utf8(strings_unicode_a, strings_unicode_b, device=cpu_scope)
print(distances_utf8)  # [1, 1]

# Needleman-Wunsch alignment scoring with substitution matrix
substitution_matrix = np.zeros((256, 256), dtype=np.int8)
substitution_matrix.fill(-1)                # Mismatch penalty
np.fill_diagonal(substitution_matrix, 0)    # Match score

engine_nw = szs.NeedlemanWunsch(
    substitution_matrix=substitution_matrix,
    open=1, extend=1
)

scores = engine_nw(strings_a, strings_b, device=cpu_scope)
print(scores)  # Alignment scores
```

### BioPython Integration Example

Convert BioPython alignment matrices to StringZilla format:

```python
import numpy as np
from Bio import Align
from Bio.Align import substitution_matrices
import stringzillas as szs

# Original BioPython setup
aligner = Align.PairwiseAligner()
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = 1
aligner.extend_gap_score = 1

# Convert matrix to NumPy array
subs_packed = np.array(aligner.substitution_matrix).astype(np.int8)
subs_reconstructed = np.full((256, 256), 127, dtype=np.int8)  # Max penalty for invalid chars

for row_idx, row_aa in enumerate(aligner.substitution_matrix.alphabet):
    for col_idx, col_aa in enumerate(aligner.substitution_matrix.alphabet):
        subs_reconstructed[ord(row_aa), ord(col_aa)] = subs_packed[row_idx, col_idx]

# Compare results
glutathione = "ECG"
trh = "QHP"  # Thyrotropin-releasing hormone

score_biopython = aligner.score(glutathione, trh)

engine = szs.NeedlemanWunsch(substitution_matrix=subs_reconstructed, open=1, extend=1)
score_stringzilla = int(engine(sz.Strs([glutathione]), sz.Strs([trh]))[0])

assert score_biopython == score_stringzilla  # Both equal 6
# StringZilla: 7.8s vs BioPython: 25.8s for 100 pairs of 10k-char proteins
```

### Rolling Fingerprints (MinHash)

Generate compact document fingerprints for similarity detection:

```python
import numpy as np
import stringzilla as sz
import stringzillas as szs

texts = sz.Strs([
    "quick brown fox jumps over the lazy dog",
    "quick brown fox jumped over a very lazy dog",
])

cpu = szs.DeviceScope(cpu_cores=4)
ndim = 1024  # Fingerprint dimensionality
window_widths = np.array([4, 6, 8, 10], dtype=np.uint64)

engine = szs.Fingerprints(
    ndim=ndim,
    window_widths=window_widths,    # Optional n-gram windows
    alphabet_size=256,              # Default for byte strings
    capabilities=("serial",),
)

hashes, counts = engine(texts, device=cpu)

print(hashes.shape)  # (2, 1024) — 2 documents, 1024-dim fingerprints
print(counts.shape)  # (2, 1024) — Hash collision counts
print(hashes.dtype)  # uint32
```

## C/C++ API

### Basic C Usage (C99+)

```c
#include <stringzilla/stringzilla.h>

// Initialize string views (not necessarily null-terminated)
sz_string_view_t haystack = {your_text, your_text_length};
sz_string_view_t needle = {your_subtext, your_subtext_length};

// Substring search (auto-dispatch to best SIMD backend)
sz_cptr_t ptr = sz_find(haystack.start, haystack.length, needle.start, needle.length);
sz_size_t position = ptr ? (sz_size_t)(ptr - haystack.start) : SZ_SIZE_MAX;  // SZ_SIZE_MAX if not found

// Manual backend dispatch for specific CPU features
sz_cptr_t ptr_skylake = sz_find_skylake(haystack.start, haystack.length, needle.start, needle.length);
sz_cptr_t ptr_neon = sz_find_neon(haystack.start, haystack.length, needle.start, needle.length);

// Hashing
sz_u64_t hash = sz_hash(haystack.start, haystack.length, 42);  // Seed=42
sz_u64_t checksum = sz_bytesum(haystack.start, haystack.length);

// Incremental hashing
sz_hash_state_t state;
sz_hash_state_init(&state, 42);
sz_hash_state_update(&state, haystack.start, 1);  // First char
sz_hash_state_update(&state, haystack.start + 1, haystack.length - 1);  // Rest
sz_u64_t streamed_hash = sz_hash_state_digest(&state);

// SHA-256
sz_u8_t digest[32];
sz_sha256_state_t sha_state;
sz_sha256_state_init(&sha_state);
sz_sha256_state_update(&sha_state, haystack.start, haystack.length);
sz_sha256_state_digest(&sha_state, digest);

// Collection operations (sorting)
sz_sequence_t array = {your_handle, your_count, your_get_start, your_get_length};
sz_sorted_idx_t order[your_count];
sz_sequence_argsort(&array, NULL, order);  // NULL uses default allocator
```

### LibC to StringZilla Mapping

| LibC Function | StringZilla Equivalent |
|--------------|------------------------|
| `memchr(haystack, needle, len)` | `sz_find_byte(haystack, len, needle)` |
| `memrchr(haystack, needle, len)` | `sz_rfind_byte(haystack, len, needle)` |
| `strcmp`, `memcmp` | `sz_order`, `sz_equal` |
| `strlen(haystack)` | `sz_find_byte(haystack, len, '\0')` |
| `strcspn(haystack, reject)` | `sz_find_byteset(haystack, len, reject_bitset)` |
| `strspn(haystack, accept)` | `sz_find_byte_not_from(haystack, len, accept, accept_len)` |
| `strstr`, `memmem` | `sz_find(haystack, h_len, needle, n_len)` |
| `memcpy(dest, src, len)` | `sz_copy(dest, src, len)` |
| `memmove(dest, src, len)` | `sz_move(dest, src, len)` |
| `memset(dest, val, len)` | `sz_fill(dest, len, val)` |

### C++ API (C++11+)

```cpp
#include <stringzilla/stringzilla.hpp>

namespace sz = ashvardanian::stringzilla;

// String types with Small String Optimization (SSO)
sz::string haystack = "some string";
sz::string_view needle = sz::string_view(haystack).substr(0, 4);

// STL-like operations
auto position = haystack.find(needle);  // Or rfind, contains, starts_with, ends_with
auto hash = std::hash<sz::string_view>{}(haystack);  // Compatible with std::hash

// Iterators
haystack.begin(), haystack.end();  // Forward iterators
haystack.rbegin(), haystack.rend();  // Reverse iterators

// Character set operations
auto first_ws = haystack.find_first_of(" \v\t");  // Or find_last_of, find_first_not_of, find_last_not_of

// In-place modifications
haystack.remove_prefix(needle.size());  // Why is this in-place?!

// Comparison
haystack.compare(needle);  // Returns sz_ordering_t
haystack <=> needle;  // C++20 spaceship operator

// String literals for type resolution
using sz::literals::operator""_sv;
auto view = "some string"_sv;  // sz::string_view (not std::string_view)
```

## CUDA GPU Acceleration

For bulk operations on Nvidia GPUs:

```python
import stringzillas as szs

# Use GPU if available
gpu_scope = szs.DeviceScope(gpu_device=0)  # Pick GPU 0

strings_a = sz.Strs(["kitten", "flaw"])
strings_b = sz.Strs(["sitting", "lawn"])

# Optional: transfer to device ahead of time
strings_a = szs.to_device(strings_a)
strings_b = szs.to_device(strings_b)

engine = szs.LevenshteinDistances(match=0, mismatch=2, open=3, extend=1)
distances = engine(strings_a, strings_b, device=gpu_scope)

# CUDA can be 100x faster than CPU for large batches
# Example: 93B CUPS (CUDA Update Per Second) vs 3.4B on x86 CPU
```

## Platform Support and Capabilities

StringZilla auto-detects and dispatches to the best available SIMD backend:

**x86_64 CPUs:**
- Westmere (SSE4.2 + AES-NI)
- Haswell (AVX2)
- Skylake (AVX-512)
- Ice Lake (AVX-512 VBMI + wider AES)

**ARM64 CPUs:**
- NEON
- NEON + AES
- NEON + SHA
- SVE (Scalable Vector Extension)
- SVE2 + AES

**GPUs:**
- CUDA (Kepler through Hopper architectures)
- ROCm (AMD GPUs)

Check available capabilities:

```python
import stringzilla
print(stringzilla.__capabilities__)  # ['serial', 'haswell', 'neon', ...]
```

## Compilation Options

Customize StringZilla behavior via compile-time macros:

```c
// Debug mode
#define SZ_DEBUG 1

// Avoid LibC dependencies (for embedded systems)
#define SZ_AVOID_LIBC 1

// Enable dynamic runtime dispatch
#define SZ_DYNAMIC_DISPATCH 1

// Use misaligned loads (faster on most modern CPUs)
#define SZ_USE_MISALIGNED_LOADS 1

// Performance tuning
#define SZ_SWAR_THRESHOLD 24  // Switch to SWAR over serial for strings > 24 bytes
#define SZ_CACHE_LINE_WIDTH 64  // CPU cache line size
#define SZ_CACHE_SIZE 1048576  // L1d + L2 cache combined

// Enable/disable specific SIMD backends
#define SZ_USE_WESTMERE 1  // SSE4.2 + AES-NI
#define SZ_USE_HASWELL 1   // AVX2
#define SZ_USE_SKYLAKE 1   // AVX-512
#define SZ_USE_ICE 1       // AVX-512 VBMI
#define SZ_USE_NEON 1      // ARM NEON
#define SZ_USE_SVE 1       // ARM SVE
#define SZ_USE_SVE2 1      // ARM SVE2
```

## Troubleshooting

### Issue: Hash values differ between platforms

**Solution:** StringZilla uses stable 64-bit hashing with seed parameter. Ensure you use the same seed value across platforms:

```python
hash1 = sz.hash(b"test", seed=42)  # Always same value on any platform
```

### Issue: Case-folding output buffer too small

**Solution:** Unicode case-folding can expand characters (ß → ss, ﬃ → ffi). Allocate output buffer at least 3× input size:

```python
output = bytearray(len(input_text) * 3)
sz.utf8_case_fold(input_text, output)
```

### Issue: SIMD backend not detected

**Solution:** Check capabilities and ensure compilation flags match CPU features:

```python
import stringzilla
print(stringzilla.__capabilities__)  # Should show available backends

# For C/C++, compile with appropriate flags:
# -mavx2 -mavx512f for x86, or enable NEON/SVE for ARM
```

### Issue: Memory mapping fails on Windows

**Solution:** Use `File` class which handles platform-specific memory mapping:

```python
from stringzilla import File
mapped = File("large-file.txt")  # Works cross-platform
```

### Issue: CUDA backend not available

**Solution:** Install CUDA-specific package and verify GPU availability:

```bash
pip install stringzillas-cuda
python -c "import stringzillas; print(stringzillas.__capabilities__)"  # Should show 'cuda'
```

## Benchmarks and Testing

StringZilla includes benchmark suites in `./scripts` directory. Run with:

```bash
# Python benchmarks
python scripts/benchmark_stringzilla.py

# C/C++ benchmarks (requires compilation)
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j8
./bin/stringzilla_benchmarks
```

See [`CONTRIBUTING.md`](https://github.com/ashvardanian/StringZilla/blob/main/CONTRIBUTING.md) for detailed benchmark instructions.

## Related Projects

- **[StringWars](https://github.com/ashvardanian/StringWars)**: Head-to-head benchmarks against Rust and Python libraries
- **[HashEvals](https://github.com/ashvardanian/HashEvals)**: Collision resistance and distribution analysis for hashers
- **[StringTape](https://github.com/ashvardanian/StringTape)**: Tape-like string storage format used by StringZilla collections
- **[USearch](https://github.com/unum-cloud/usearch)**: Vector search library using StringZilla for edit distances

## Limitations

- Python `Str.splitlines()` matches fewer line break characters than native `str.splitlines()` (avoids 2-byte Unicode runes)
- Some features require specific CPU instruction sets (check capabilities before use)
- CUDA backend requires Nvidia GPU with compute capability ≥ Kepler
- Case-folding output can be up to 3× input size for certain Unicode characters

## References

- [StringZilla GitHub Repository](https://github.com/ashvardanian/StringZilla)
- [StringZilla Blog Post](https://ashvardanian.com/posts/stringzilla/)
- [Rust Documentation](https://docs.rs/stringzilla)
- [PyPI Package](https://pypi.org/project/stringzilla/)
- [Crates.io Package](https://crates.io/crates/stringzilla)
