# Performance and Architecture

## ISA Dispatch

NumKong provides two dispatch mechanisms:

**Compile-time dispatch** selects the fastest kernel supported by the target platform at build time — thinner binaries, no indirection overhead, but requires knowing your deployment hardware.

**Run-time dispatch** compiles every supported kernel into the binary and picks the best one on the target machine via `nk_capabilities()` — one pointer indirection per call, but a single binary runs everywhere. Distributed artifacts (Rust crate, Python wheels, JS native modules, shared libs from the default CMake build) pin the translation-unit baseline to each architecture's ABI floor so the library runs on any CPU matching the ABI, not just the build host.

All kernel names follow the pattern `nk_{operation}_{type}_{backend}`. The first call to `nk_capabilities()` initializes the dispatch table; all subsequent calls are lock-free.

## SIMD Backend Coverage

NumKong covers 30+ SIMD backends across architectures:

### x86

- **Haswell** (2013): AVX2 + FMA, 256-bit YMM registers
- **Skylake** (2015): AVX-512 foundation, VGETEXP/VGETMANT
- **Ice Lake** (2019): AVX-512 VNNI (DPBUSD), VPERMB
- **Alder Lake** (2021): Hybrid P/E cores, VPDPBSSD
- **Genoa** (2022): AMX with DPBF16PS widening dot
- **Sapphire Rapids** (2023): AVX-512-FP16 (VFMADDPH), full AMX
- **Diamond Rapids** (2026): VCVTBF82PH/VCVTHF82PH native FP8→FP16, VDPPHPS widening dot

### Arm

- **NEON** (Graviton 1, 2018): Base SIMD
- **NEON+FP16FML** (Apple M1, 2020): FMLAL widening FMA
- **NEON+BFDOT** (Graviton 3+, 2021): BFloat16 dot product
- **NEON+DotProd** (2019+): SDOT for integer
- **NEON+FP8DOT** (2026): Native FDOT for FP8
- **SME** (Apple M4+, 2024): Streaming SVE Matrix Extension, FMOPA outer products
- **SVE** (Graviton 3+): Scalable vector extension

### RISC-V

- **RVV**: Base vector extension
- **RVV+Zvfh**: Half-precision floating point
- **RVV+Zvfbfwma**: BFloat16 widening FMA

### Other

- LoongArch, WebAssembly (SIMD + Relaxed SIMD), PowerPC

## Intel AMX vs Apple SME

Both provide extraordinary arithmetic density — thousands of multiply-accumulates per instruction:

**Intel AMX (Sapphire Rapids):**
- 8 TMM registers, 1 KB each
- Inner product: C += A_tile · B_tile^T
- Inputs: i8, u8, bf16
- BFloat16: 8,192 ops/instruction
- Int8: 16,384 ops/instruction
- Isolated from AVX-512 (no mixing)
- B layout: VNNI-like swizzling

**Apple SME (M4+):**
- 4 ZA registers, up to 512 elements each
- Outer product: C += a_col ⊗ b_row
- Inputs: u1, i8, u8, f16, bf16, f32, f64
- BFloat16: 512 ops/instruction
- Int8: 1,024 ops/instruction
- Streaming SVE available inside SME mode
- Boundary handling via `svwhilelt` predicates

## Key Optimization Techniques

### No Loop Unrolling

NumKong avoids loop unrolling by design. Modern CPUs already "unroll" in hardware — out-of-order engines with reorder buffers of 320-630 entries (Zen 4: 320, Golden Cove: 512, Apple Firestorm: ~630) keep a dozen loop iterations in-flight simultaneously. Unrolling would inflate the .text section by megabytes across 1,500+ kernel endpoints and increase instruction-cache pressure.

### Masked Loads Instead of Scalar Tails

NumKong often uses masked loads instead of scalar tails (`_mm512_maskz_loadu_ps` on AVX-512, predicated `svld1_f32` on SVE), processing every element through the same arithmetic path regardless of alignment. This avoids correctness hazards where scalar tails silently drop FMA fusion, compensated accumulation, and saturating arithmetic.

### VNNI Algebraic Domain Shifting

For Int8×Int8 on Ice Lake+, the asymmetric `DPBUSD` (unsigned×signed) is used for both signed and unsigned operations via XOR-based sign transformation with SAD-based correction terms computed on different execution ports.

### Octave Decomposition for E4M3

On Ice Lake, E4M3's 4-bit exponent splits into 2 "octave" + 2 "remainder" bits. The bottom 5 bits map via `VPERMB` to u8 integers, and the 4 octave bins per operand produce 16 `VPDPBUSD` cross-products accumulated into 7 registers grouped by octave sum. This processes 64 E4M3 bytes per iteration in u8, doubling element density of the BF16 upcast path.

### Deferred Sign-Flip in Complex Dot Products

For complex dot products, two accumulators collect interleaved products treating all as positive, then a single post-loop XOR flips sign bits. This avoids execution port contention between FMA and FMS instructions.

## Tile Architecture and Ozaki Scheme

### Ozaki Float64 Matrix Multiplication

On Apple M4, the Ozaki scheme decomposes Float64 multiplication into three non-overlapping mantissa slices of 19+17+17 bits. Every slice fits within Float32's 24-bit significand, so each pairwise product is exact in Float64. Six `FMOPA` instructions across three ZA tile accumulators compute all cross-products where slice indices sum to ≤ 2.

The tile schedule is carefully ordered (ZA3, ZA2, ZA1, ZA3, ZA2, ZA3) to minimize write-after-write pipeline stalls: nine cycles instead of fifteen with naive round-robin.

On Apple M4 at 4096³:
- `nk_dots_packed_f64_serial`: 1.8 gso/s, 6 ULP
- `nk_dots_packed_f64_neon`: 5.2 gso/s, 0 ULP
- `nk_dots_packed_f64_smef64`: 12.9 gso/s, 0.9 ULP

The Ozaki SME path is 2.5x faster than the Dot2 NEON path while achieving sub-1 mean ULP.

## Performance Comparison

### Single Vector Dot Product (2048-d, Intel Sapphire Rapids, single-threaded)

| Input | NumPy + OpenBLAS | PyTorch + MKL | JAX | NumKong |
| --- | --- | --- | --- | --- |
| `f64` | 12.2 gso/s, 1e-15 err | 12.5 gso/s, 1e-15 err | ~2.8 gso/s, 1e-15 err | 2.3 gso/s, 1e-16 err |
| `f32` | 27.0 gso/s, 9e-7 err | 27.5 gso/s, 1e-6 err | ~13.0 gso/s, 1e-6 err | 15.0 gso/s, 4e-7 err |
| `bf16` | — | 425 gso/s, 1.8% err | ~13.0 gso/s, 3.4% err | 229 gso/s, 3.6% err |
| `f16` | 0.15 gso/s, 0.25% err | 70.0 gso/s, 0.37% err | ~13.1 gso/s, 0.35% err | 51.5 gso/s, 0.26% err |
| `e5m2` | — | 0.2 gso/s, 4.6% err | ~13.1 gso/s, 4.6% err | 199 gso/s, 0% err |
| `i8` | 1.1 gso/s, overflow | 0.5 gso/s, overflow | 0.5 gso/s, overflow | 14.8 gso/s, 0% err |

### Matrix Multiplication (2048×2048)², Intel Sapphire Rapids

| Input | NumPy + OpenBLAS | PyTorch + MKL | JAX | NumKong |
| --- | --- | --- | --- | --- |
| `f64` | 65.5 gso/s, 1e-15 err | 68.2 gso/s, 1e-15 err | ~14.3 gso/s, 1e-15 err | 8.6 gso/s, 1e-16 err |
| `f32` | 140 gso/s, 9e-7 err | 145 gso/s, 1e-6 err | ~60.5 gso/s, 1e-6 err | 37.7 gso/s, 4e-7 err |
| `bf16` | — | 851 gso/s, 1.8% err | ~25.8 gso/s, 3.4% err | 458 gso/s, 3.6% err |
| `f16` | 0.3 gso/s, 0.25% err | 140 gso/s, 0.37% err | ~26.1 gso/s, 0.35% err | 103 gso/s, 0.26% err |
| `e5m2` | — | 0.4 gso/s, 4.6% err | ~26.4 gso/s, 4.6% err | 398 gso/s, 0% err |
| `i8` | 0.4 gso/s, overflow | 50.0 gso/s, overflow | ~0.0 gso/s, overflow | 1279 gso/s, 0% err |

### Package Size Comparison

| Package | Size | Parallelism & Memory | Available For |
| --- | --- | --- | --- |
| PyTorch + MKL | 705 MB | Vector & Tile SIMD, OpenMP Threads, Hidden Allocs | Python, C++, Java |
| JAX + jaxlib | 357 MB | Vector SIMD, XLA Threads, Hidden Allocs | Python |
| NumPy + OpenBLAS | 30 MB | Vector SIMD, Built-in Threads, Hidden Allocs | Python |
| mathjs | 9 MB | No SIMD, No Threads, Many Allocs | JS |
| NumKong | 5 MB | Vector & Tile SIMD, Your Threads, Your Allocs | 7 languages |

## Validation

Every kernel is validated against 118-bit extended-precision baselines with per-type ULP budgets across log-normal, uniform, and Cauchy input distributions. Tests check triangle inequality, Cauchy-Schwarz bounds, NaN propagation, overflow detection, and probability-simplex constraints for each ISA variant. Results are cross-validated against OpenBLAS, Intel MKL, and Apple Accelerate.

## Thread Model

NumKong exposes row-range parameters that let the caller partition work across any threading model. For GEMM-shaped `dots_packed`, pass a slice of A's rows and the full packed B to compute the corresponding slice of C. For SYRK-shaped `dots_symmetric`, explicit `start_row` / `end_row` parameters control which rows of the symmetric output matrix a given thread computes.

Each thread must call `nk_configure_thread` before any kernel — it flushes denormals to zero on x86 to avoid 100x slowdowns on subnormal inputs, requests AMX tile permission from the Linux kernel via `ARCH_REQ_XCOMP_PERM`, and sets the rounding mode.

For NUMA-aware parallelism, each node gets a local copy of the small-ish packed B, works on the slice of A that lives in its local memory, and writes to the corresponding row block of C — also local.
