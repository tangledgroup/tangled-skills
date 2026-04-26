# Algorithms & Design Decisions

## Architecture Layers

StringZilla uses a layered architecture:

1. **StringZilla C library** — no dependencies, header-only
2. **StringZillas parallel extensions**:
   - Parallel C++ algorithms built with Fork Union
   - Parallel CUDA algorithms for Nvidia GPUs
   - Parallel ROCm algorithms for AMD GPUs (upcoming)

Where vectorization stops being effective, parallelism takes over.

## Exact Substring Search

Algorithms are divided into comparison-based, automaton-based, and bit-parallel families. StringZilla selects based on needle length and available backends:

### Short Needles (1-4 characters)

Brute force with SIMD is the fastest solution. For single-character needles, SWAR broadcasts the character across a 64-bit word and uses XOR + trailing-zero-count:

```c
uint64_t nnnnnnnn = n;
nnnnnnnn |= nnnnnnnn << 8;   // broadcast n into nnnnnnnn
nnnnnnnn |= nnnnnnnn << 16;
nnnnnnnn |= nnnnnnnn << 32;
for (; haystack + 8 <= end; haystack += 8) {
    uint64_t haystack_part = *(uint64_t const *)haystack;
    uint64_t match_indicators = ~(haystack_part ^ nnnnnnnn);
    match_indicators &= match_indicators >> 1;
    match_indicators &= match_indicators >> 2;
    match_indicators &= match_indicators >> 4;
    match_indicators &= 0x0101010101010101;
    if (match_indicators != 0)
        return haystack - begin + ctz64(match_indicators) / 8;
}
```

Performance on Apple M2 Pro for single-character search: STL 3.4 GB/s vs StringZilla 12.25 GB/s (3.6x).

### Mid-Length Needles (up to 256 bytes)

Boyer-Moore-Horspool with Raita heuristic variation. Stack-allocated shift table remains small. Uses unique-character pre-processing to handle non-English corpora effectively.

### Long Needles

Apostolico-Giancarlo adds an additional skip-table for O(h) worst-case complexity, though control-flow is too complex for efficient vectorization and was deprecated in practice.

SIMD backends compare characters at multiple strategically chosen offsets within the needle to reduce degeneracy. The offset selection heuristic (`sz_locate_needle_anomalies_`) locates unique characters in the needle.

### Deprecated Algorithms

- Apostolico-Giancarlo: control-flow too complex for vectorization
- Shift-Or Bitap: slower than SWAR
- Horspool-style bad-character check in SIMD: effective only for very long needles with uneven character distributions

## Levenshtein Edit Distance — Diagonal Approach

StringZilla evaluates **diagonals instead of rows** for the Levenshtein matrix. All cells within a diagonal are independent and can be computed in parallel:

- Stores 3 diagonals instead of 2 rows
- Each consecutive diagonal computed from the previous two
- Substitution costs from the sooner diagonal, insertion/deletion from the later diagonal
- Much better vectorization for intra-core parallelism
- Generalizes to weighted edit-distances (substitution cost varies by character pair)

This approach is used extensively in Unum's internal combinatorial optimization libraries. For proteins ~10k chars, 100 pairs: StringZilla 0.8s vs JellyFish 62.3s vs EditDistance 32.9s.

## Hashing

64-bit hash function inspired by AquaHash/aHash/GxHash design, optimized for modern CPUs. Passes SMHasher test suite including `--extra` with no collisions.

### Dual-State Design

- **AES State**: Initialized with seed XORed against pi constants
- **Sum State**: Accumulates shuffled input data with permutation

For strings ≤64 bytes: minimal state processes 16-byte blocks. For longer strings: 4x wider state (512 bits) processes 64-byte chunks, maximizing throughput on superscalar CPUs.

### Key Properties

- AES encryption rounds combined with shuffle-and-add for exceptional mixing
- Consistent output across all platforms
- Length not mixed into AES block at start — allows incremental construction when final length unknown
- With masked AVX-512 and predicated SVE loads, avoids expensive block-shuffling on non-divisible-by-16 lengths
- High port-level parallelism: VAESENC + VPSHUFB_Z + VPADDQ keep multiple CPU ports busy each cycle

## SHA-256

Hardware-accelerated SHA-256 following FIPS 180-4 specification with multiple backends. Supports AES-NI and SHA-NI instruction sets where available.

## Random Generation

Pseudorandom generator inspired by AES-CTR-128, reusing the same AES primitives as the hash function. Uses only one round of AES mixing (vs NIST SP 800-90A's multiple rounds) for performance while maintaining reproducible output across platforms.

Counter mode: `AESENC(nonce + lane_index, nonce XOR pi_constants)`, rotating through first 512 bits of pi for each 16-byte block. Only state required is a 64-bit nonce — much cheaper than Mersenne Twister.

## Sorting

Lexicographic sorting of string collections:

1. Export pointer-sized n-grams ("pgrams") into contiguous buffer for locality
2. Recursively QuickSort with 3-way partition
3. Dive into equal pgrams to compare deeper characters
4. Very small inputs fall back to insertion sort

Average: O(n log n). Worst-case: quadratic (mitigated by 3-way partitioning and n-gram staging). For 10 million tokens: StringZilla 214ms vs std::sort 1959ms (9x improvement).

## Unicode 17.0 Support

StringZilla uses proper 32-bit "runes" for unpacked Unicode codepoints, ensuring correct results across all operations. Implements Unicode 17.0 standard — practically the only library besides ICU and PCRE2 to do so, with orders of magnitude better performance.

### Case-Folding Expansions

| Character | Codepoint | UTF-8 Bytes | Case-Folds To | Result Bytes |
|-----------|-----------|-------------|---------------|--------------|
| `ß`       | U+00DF    | C3 9F       | `ss`          | 73 73        |
| `ﬃ`       | U+FB03    | EF AC 83    | `ffi`         | 66 66 69     |
| `İ`       | U+0130    | C4 B0       | `i` + `◌̇`     | 69 CC 87     |

Turkish `İ` and ASCII `I` are distinct: `İstanbul` folds to `i̇stanbul` (with combining dot), while `ISTANBUL` folds to `istanbul` (without). They do not match — correct Unicode behavior for Turkish locale handling.

## Memory Copying, Fills, and Moves

AVX-512 backend uses non-temporal stores to avoid cache pollution for large strings. Handles unaligned head and tails separately, ensuring writes in big copies are always aligned to cache-line boundaries (true for both AVX2 and AVX-512).

`SZ_OVERRIDE_LIBC` allows overriding `memcpy`/`memset` with StringZilla implementations — use with `LD_PRELOAD` to accelerate existing string-heavy applications without recompilation. Unlike libc, StringZilla is defined for NULL inputs (e.g., `memcpy(NULL, NULL, 0)` is well-defined).

## Rolling Fingerprints (MinHash)

For D hash functions and text of length L, MinHash involves computing O(D * L) hashes in the worst case. StringZillas provides batch-oriented fingerprint computation with configurable window widths for information retrieval applications.
