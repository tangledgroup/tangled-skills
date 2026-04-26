# SIMD Backends and Optimizations

## Supported ISAs

NumKong ships 30+ SIMD backends across these architectures:

- **x86**: Haswell (AVX2/FMA), Skylake (AVX-512F/ER/SKX), Ice Lake (AVX-512_VNNI/BF16/IFMA/VP2INTERSECT), Alder Lake, Genoa (AMX-BF16), Sapphire Rapids (AMX-Int8/FP8/BF16), Diamond Rapids
- **Arm**: NEON, NEON+DotProd, NEON+FHM (FP16 FMLAL), NEON+BFDOT (BF16 dot), NEON+FP8DOT, SVE, SME (M4+, AppleClang 16+)
- **RISC-V**: RVV, RVV+Zvfh (FP16), RVV+Zvfbfwma (BF16)
- **WebAssembly**: v128relaxed (SIMD + relaxed SIMD)
- **Others**: LoongArch, PowerPC

## Design Philosophy

NumKong avoids loop unrolling and scalar tails by design:

- Modern CPUs with reorder buffers of 320-630 entries already "unroll" in hardware via out-of-order execution
- Unrolling inflates binary size (1,500+ kernel endpoints × 2x unrolling = megabytes)
- Larger loop bodies increase instruction-cache and micro-op-cache pressure
- Serial tails silently drop FMA fusion, compensated accumulation, and saturating arithmetic
- NumKong uses masked loads (`_mm512_maskz_loadu_ps`, predicated `svld1_f32`) instead

## Key Algorithmic Techniques

### Compensated Summation

Float64 serial: Neumaier algorithm. Float64 SIMD with FMA: Dot2 (TwoProd + TwoSum). Float32: widening to Float64 for accumulation, then downcast on finalization.

### VNNI Algebraic Domain Shifting

`DPBUSD` requires unsigned×signed operands. For signed Int8×Int8: XOR with `0x80` to shift to unsigned, compute `(a+128)×b`, subtract `128×sum(b)` via `VPSADBW` (runs on port 5, avoiding contention with DPBUSD on ports 0-1).

### Octave Decomposition for E4M3

Splits 4-bit exponent into 2 "octave" bits + 2 "remainder" bits. Bottom 5 bits map via `VPERMB` to u8 integers. Sign computed via `VPTERNLOGD`. Produces 7 accumulators grouped by octave sum, each scaled by exact power of 2.

### Deferred Sign-Flip in Complex Dot Products

Computes all products as positive, then single bitwise XOR with `0x80000000` flips sign bits after the loop. Avoids FMA/FMS port contention.

### Reciprocal Square Root with Newton-Raphson

For angular distance: `VRSQRT14PS` (14-bit estimate, ~4 cycles) + one Newton-Raphson iteration (~4 more cycles) = ~8 cycles total vs ~23 cycles for `VSQRTPS` + `VDIVPS`. Platform-specific iteration counts ensure consistent ULP bounds across ISAs.

### Three-Accumulator Angular Pattern

Angular distance requires three concurrent dot products in one pass: `sum(a*b)`, `sum(a^2)`, `sum(b^2)`. Triples register pressure but halves memory bandwidth compared to three-pass approach.

### SIMD Log2 Approximation for Probability Divergences

Skylake: `VGETEXP` + `VGETMANT` decompose float into exponent and mantissa, degree-4 minimax polynomial approximates log2(mantissa). NEON: integer bit extraction (reinterpret as int, shift out exponent, mask mantissa to [1, 2)).

### McAdams Branching-Free 3×3 SVD for Mesh Alignment

Jacobi eigenanalysis with fixed 16 iterations (no convergence check) for deterministic behavior. Quaternion-accumulated rotations. Approximate Givens angles via threshold test.

### Two-Stage Coarse-to-Fine MaxSim

i8-quantized screening at O(m·n·k) with 1 byte/element, followed by full-precision refinement at O(m·k) for only winning pairs. Break-even at ~4 documents per query.

### Dual Pre-Packing for MaxSim on SME

Both query and document pre-packed into identical contiguous formats. All 4 ZA tiles serve as accumulators (vs 3 for single-sided packing) — +33% MOPA throughput. Vertical column extraction for argmax: `svread_ver_za32_f32_m` reads one column of ZA per document, element-wise `svcmpgt` + `svsel` update running maximum.

## ISA-Specific Notes

### x86: Haswell (AVX2/FMA)

Baseline for modern x86. 256-bit YMM registers. FMA support. No AVX-512 features. Used as fallback for kernels requiring no AVX-512 extensions.

### x86: Skylake-X (AVX-512F/ER)

512-bit ZMM registers. Masked loads (`_mm512_maskz_loadu_ps`). `VGETEXP`/`VGETMANT` for log2 approximation. `VRSQRT28` achieves 2^-28 accuracy directly (no Newton-Raphson needed). Dot2 TwoProd via FMA.

### x86: Ice Lake (AVX-512_VNNI/BF16)

`VPDPBUSD` for VNNI integer dot products. `VDPBF16PS` for BFloat16 widening dot. `VPERMB` for byte permutation (E4M3 octave decomposition). E4M3 via VNNI octave decomposition: 64 elements per iteration in u8.

### x86: Genoa (AMX-BF16)

Advanced Matrix Extensions with BFloat16. `TDPBF16PS` for tile dot product. Packed matrix kernels use AMX tiles with VNNI-interleaved layout (pairs of BFloat16 in DWORDs across K dimension).

### x86: Sapphire Rapids (AMX-Int8/FP8)

AMX extended to Int8 and FP8. E2M3 packed kernel reaches 1,195 gso/s on 1024³. E5M2 via AMX: 407 gso/s. Int8 packed: 1,610 gso/s on 1024³.

### Arm: NEON + FHM

ARMv8.4-A `FMLAL`/`FMLSL` fuse FP16-to-FP32 conversion with multiply-accumulate in single operation. `vfmlalq_low_f16` and `vfmlalq_high_f16` process lower/upper 4 elements of 8-wide FP16 vector. Reduces latency from 7 to 4 cycles.

### Arm: NEON + BFDOT

ARMv8.6-A `BFDOT` provides widening BFloat16 dot products (Graviton 3+, Apple M2+). Native BF16×BF16→F32 accumulation.

### Arm: SME (M4+)

Scalable Matrix Extension. `FMOPA` outer-product instructions. SVL=512 on M4+. Packed matrix kernels use ZA tiles for accumulation. E2M3 packed reaches 1,404 gso/s on 1024³. SME not used for mesh alignment — 3×3 outer products waste 99.6% of tile capacity (9 useful cells out of 256).

### RISC-V: RVV + Zvfbfwma

`vfwmaccbf16` for fused BFloat16×BFloat16→Float32 widening multiply-accumulate. Float8 via LUT to BFloat16, then same path. Variable vector length adapts to hardware.

### WebAssembly: v128relaxed

SIMD + relaxed SIMD extension. `i32x4_relaxed_dot_i8x16_i7x16_add` computes Int8×Int7 (sign bit of one operand masked). Requires windowed correction for full Int8×Int8.

## Performance Benchmarks

Throughput measured in GB/s (dense) or GSO/s (matrix). Accuracy as mean ULP. Each kernel runs ≥20 seconds per configuration.

### Intel Sapphire Rapids — Dense Dot Products (1024 elements)

- `nk_dot_f64_skylake`: 28.6 gb/s, 0 ulp
- `nk_dot_f32_skylake`: 29.8 gb/s, 0 ulp
- `nk_dot_bf16_genoa`: 29.7 gb/s, 0.2 ulp
- `nk_dot_e2m3_icelake`: 46.0 gb/s, 0 ulp
- `nk_dot_i8_icelake`: 46.2 gb/s

### Intel Sapphire Rapids — Packed Matrix (1024³)

- `nk_dots_packed_f64_skylake`: 9.27 gso/s, 0 ulp
- `nk_dots_packed_f32_skylake`: 41.4 gso/s, 0 ulp
- `nk_dots_packed_bf16_sapphireamx`: 706 gso/s, 0.7 ulp
- `nk_dots_packed_e2m3_sapphireamx`: 1,195 gso/s, 0 ulp
- `nk_dots_packed_i8_sapphireamx`: 1,610 gso/s

### Apple M5 — Dense Dot Products (1024 elements)

- `nk_dot_f64_neon`: 42.3 gb/s, 0 ulp
- `nk_dot_f32_neon`: 38.0 gb/s, 0 ulp
- `nk_dot_bf16_neonbfdot`: 60.8 gb/s, 0.6 ulp
- `nk_dot_e2m3_neonsdot`: 47.5 gb/s, 0 ulp
- `nk_dot_i8_serial`: 102 gb/s

### Apple M5 — Packed Matrix (1024³)

- `nk_dots_packed_f64_smef64`: 46.3 gso/s, 1.1 ulp
- `nk_dots_packed_f32_smef64`: 268 gso/s, 15 ulp
- `nk_dots_packed_bf16_sme`: 1,208 gso/s, 4.2 ulp
- `nk_dots_packed_e2m3_sme`: 1,404 gso/s, 0 ulp
- `nk_dots_packed_i8_sme`: 2,687 gso/s

## Comparison with Other Libraries

| Package | Size | Parallelism & Memory | Available For |
| ------- | ---- | -------------------- | ------------- |
| PyTorch + MKL | 705 MB | Vector & Tile SIMD, OpenMP Threads, Hidden Allocs | Python, C++, Java |
| JAX + jaxlib | 357 MB | Vector SIMD, XLA Threads, Hidden Allocs | Python |
| NumPy + OpenBLAS | 30 MB | Vector SIMD, Built-in Threads, Hidden Allocs | Python |
| mathjs | 9 MB | No SIMD, No Threads, Many Allocs | JS |
| NumKong | 5 MB | Vector & Tile SIMD, Your Threads, Your Allocs | 7 languages |
