# Numeric Types and Precision

> **Source:** NumKong README, Python/C++ SDK docs
> **Loaded from:** SKILL.md (via progressive disclosure)

## Type Overview

NumKong covers 17 numeric types across floating-point, integer, complex, and packed-bit categories. Every type has a defined storage layout, promotion rules, and SIMD kernel support.

## Floating-Point Types

### Float64 & Float32: IEEE Precision

**Float64** uses compensated summation for dot products. On serial paths, Neumaier's algorithm (improvement over Kahan-Babuška) achieves O(1) error growth instead of O(n). On SIMD paths with FMA support, the Dot2 algorithm (Ogita-Rump-Oishi, 2005) maintains separate error compensators for both multiplication and accumulation via TwoProd and TwoSum operations.

**Float32** SIMD implementations load Float32 values, upcast to Float64 for full-precision multiplication and accumulation, then downcast only during finalization. This avoids catastrophic cancellation at minimal cost since modern CPUs have dedicated Float64 vector units operating at nearly the same throughput as Float32.

```c
// Dot2 TwoProd: Capture multiplication rounding error
h = a * b;
r = fma(a, b, -h);  // Extracts rounding error

// Dot2 TwoSum: Capture addition rounding error
t = sum + product;
e = (sum - t) + product;  // Compensator term
```

### BFloat16 & Float16: Half Precision

**BFloat16** (1+8+7 bits, 2 bytes, range ±3.4×10³⁸) shares Float32's 8-bit exponent but truncates the mantissa to 7 bits, prioritizing dynamic range over precision. On old CPUs, upcasting is a simple 16-bit left shift (essentially free). Newer CPUs provide widening mixed-precision dot products: DPBF16PS (AVX-512 on Genoa/Sapphire Rapids) and BFDOT (NEON on ARMv8.6-A Graviton 3+).

**Float16** (1+5+10 bits, 2 bytes, range ±65504) is IEEE 754 half-precision, prioritizing precision over range (10 vs 7 mantissa bits). On x86, F16C extensions (Ivy Bridge+) provide fast Float16→Float32 conversion; Sapphire Rapids+ adds native AVX-512-FP16. On Arm, ARMv8.4-A FMLAL/FMLAL2 instructions fuse Float16→Float32 widening multiply-accumulate, reducing latency from 7 to 4 cycles.

### Float8: E4M3 & E5M2

Follow the OCP FP8 standard (1 byte each):

| Format | Bits | Range | Inf | NaN | Typical Use |
|--------|------|-------|-----|-----|-------------|
| E4M3FN | 1+4+3 | ±448 | no | yes (0x7F only) | Training (precision near zero) |
| E5M2FN | 1+5+2 | ±57344 | yes | yes | Inference (wider dynamic range) |

On x86 Genoa/Sapphire Rapids, E4M3/E5M2 values upcast to BFloat16 via lookup tables, then use native DPBF16PS for 2-per-lane dot products accumulating to Float32. This creates a three-tier precision hierarchy: Float8 for storage, BFloat16 for compute, Float32 for accumulation.

E5M2 shares Float16's exponent bias (15), so E5M2→Float16 conversion is a single left-shift by 8 bits. E4M3 on Ice Lake uses "octave decomposition": the 4-bit exponent splits into 2 octave + 2 remainder bits, yielding 7 integer accumulators post-scaled by powers of 2.

### Mini-Floats: E3M2 & E2M3 (6-bit)

Follow the OCP MX v1.0 standard. Their smaller range allows scaling to exact integers that fit in i8/i16, enabling integer VPDPBUSD/SDOT accumulation instead of the floating-point pipeline.

| Format | Bits (padded to byte) | Range | Integer Path |
|--------|----------------------|-------|-------------|
| E3M2FN | 1+3+2 → 8 bits | ±28 | Int16 → Int32 accumulation |
| E2M3FN | 1+2+3 → 8 bits | ±7.5 | Int8 → Int32 accumulation |

E3M2/E2M3 values map to exact integers via 32-entry LUTs, enabling integer accumulation with no rounding error. Float16 can also serve as an accumulator, accurately representing ~50 products of E3M2FN pairs or ~20 products of E2M3FN pairs before overflow.

**Why E2M3 avoids catastrophic cancellation:** Float32 accumulation of E5M2 products can lose all precision when large terms cancel (e.g., ±6.5M products leaving only 0.201 meaningful). At that magnitude the Float32 ULP is 0.5, so small terms get absorbed. E2M3's integer path avoids this entirely.

**Not supported:** Block-scaled variants (MXFP4, NVFP4, block-scaled E3M2/E2M3) are not implemented. AMD FNUZ encoding requires conversion before processing. NumKong follows the OCP convention.

## Integer Types

### Int8 & UInt8

Both signed and unsigned 8-bit integers use Int32 accumulation to prevent overflow. A key optimization is the VNNI algebraic transform on Ice Lake+: the native DPBUSD instruction is asymmetric (unsigned×signed→signed), but NumKong uses it for both Int8×Int8 and UInt8×UInt8:

```c
// Asymmetric transform for i8×i8 using DPBUSD (unsigned×signed)
a_unsigned = a XOR 0x80;           // Convert signed→unsigned
result = DPBUSD(a_unsigned, b);    // Computes (a+128)×b
correction = 128 * sum(b);         // Parallel on different port
final = result - correction;       // True a×b value
```

### Int4 & UInt4

Int4 values pack two nibbles per byte, requiring bitmask extraction: low nibbles `(byte & 0x0F)` and high nibbles `(byte >> 4)`. For signed Int4, the transformation `(nibble ⊕ 8) - 8` maps [0,15] to [-8,7]. Separate accumulators for low and high nibbles avoid expensive nibble-interleaving.

## Binary: Packed Bits

The `u1x8` type packs 8 binary values per byte, enabling Hamming distance and Jaccard similarity via population-count instructions. On x86, VPOPCNTDQ (Ice Lake+) counts set bits in 512-bit registers directly; on Arm, CNT (NEON) operates on 8-bit lanes with horizontal add. Results accumulate into u32 — sufficient for vectors up to 4 billion bits.

## Complex Types

Four complex types: `f16c`, `bf16c`, `f32c`, `f64c` — stored as interleaved real/imaginary pairs. Essential in quantum simulation (state vectors, density matrices), signal processing (FFT coefficients, filter design), and electromagnetic modeling.

The `dot` operation computes the unconjugated dot product Σaₖbₖ, while `vdot` computes the conjugated inner product Σāₖbₖ standard in physics and signal processing.

For complex dot products, NumKong defers sign flips until after the accumulation loop: instead of using separate FMA and FMS instructions for the real component, it computes all products as positive, then applies a single bitwise XOR with `0x80000000` to flip sign bits. This avoids execution port contention between FMA and FMS.

```c
for (...) { // Complex multiply optimization: XOR sign flip after the loop
    sum_real = fma(a, b, sum_real);
    sum_imag = fma(a, b_swapped, sum_imag);
}
sum_real = xor(sum_real, 0x80000000);  // Single XOR after loop
```

## Python Scalar Types

NumKong exposes Python scalar objects for low-precision formats:

| Type | Bits | Bytes | Range | Inf | NaN |
|------|------|-------|-------|-----|-----|
| `nk.float16` | 1+5+10 | 2 | ±65504 | yes | yes |
| `nk.bfloat16` | 1+8+7 | 2 | ±3.4×10³⁸ | yes | yes |
| `nk.float8_e4m3` | 1+4+3 | 1 | ±448 | no | yes |
| `nk.float8_e5m2` | 1+5+2 | 1 | ±57344 | yes | yes |
| `nk.float6_e2m3` | 1+2+3 | 1 | ±7.5 | no | no |
| `nk.float6_e3m2` | 1+3+2 | 1 | ±28 | no | no |

## ml_dtypes Interoperability

NumKong accepts `ml_dtypes` arrays directly — no `.view(np.uint8)` workaround needed:

```python
import ml_dtypes
a = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
b = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
result = nk.cdist(a, b, metric="dot")  # just works
```

Type name mapping:

| ml_dtypes | NumKong | Status |
|-----------|---------|--------|
| `ml_dtypes.bfloat16` | `nk.bfloat16` / `"bfloat16"` | Identical format |
| `ml_dtypes.float8_e4m3fn` | `nk.float8_e4m3` / `"e4m3"` | Identical (E4M3FN = no inf) |
| `ml_dtypes.float8_e5m2` | `nk.float8_e5m2` / `"e5m2"` | Identical format |
| `ml_dtypes.float6_e2m3fn` | `nk.float6_e2m3` / `"e2m3"` | Identical (MX E2M3) |
| `ml_dtypes.float6_e3m2fn` | `nk.float6_e3m2` / `"e3m2"` | Identical (MX E3M2) |
| `ml_dtypes.int4` | `"int4"` | Compatible via buffer protocol |
| `ml_dtypes.uint4` | `"uint4"` | Compatible via buffer protocol |

Rejected types: FNUZ variants (different bias/NaN/zero), e4m3b11fnuz (bias=11), e8m0fnu (exponent-only MX scale), e3m4, float4_e2m1fn, int2, uint2.
