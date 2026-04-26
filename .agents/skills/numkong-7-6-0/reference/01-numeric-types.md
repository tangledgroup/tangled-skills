# Numeric Types and Precision

## IEEE Float64 and Float32

### Float64 (f64)

NumKong uses compensated summation that tracks numerical errors separately.

**Serial path:** Neumaier's algorithm (1974), an improvement over Kahan-Babuška that correctly handles cases where added terms are larger than the running sum, achieving O(1) error growth instead of O(n).

**SIMD path with FMA:** Dot2 algorithm (Ogita-Rump-Oishi, 2005), maintaining separate error compensators for both multiplication and accumulation via `TwoProd` and `TwoSum` operations.

```c
// Dot2 TwoProd: Capture multiplication rounding error
h = a * b;
r = fma(a, b, -h);  // Extracts rounding error

// Dot2 TwoSum: Capture addition rounding error
t = sum + product;
e = (sum - t) + product;  // Compensator term
```

Compensated Float64 suits scientific computing where numerical stability matters more than raw speed.

### Float32 (f32)

SIMD implementations load Float32 values, upcast to Float64 for full-precision multiplication and accumulation, then downcast only during finalization. This avoids catastrophic cancellation at minimal cost since modern CPUs have dedicated Float64 vector units operating at nearly the same throughput as Float32. The same compensated accumulation strategy applies to Mahalanobis distance, bilinear forms, and KL/JS divergences.

## BFloat16 and Float16

### BFloat16 (bf16)

Not an IEEE 754 standard type, but widely adopted for AI workloads. BFloat16 shares Float32's 8-bit exponent but truncates the mantissa to 7 bits, prioritizing dynamic range over precision (±3.4×10³⁸ with coarser granularity).

- On old CPUs, upcasting BFloat16 to Float32 requires just an unpack and left-shift by 16 bits (essentially free)
- On newer CPUs, both Arm and x86 provide widening mixed-precision dot products via `DPBF16PS` (AVX-512 on Genoa/Sapphire Rapids) and `BFDOT` (NEON on ARMv8.6-A Graviton 3+)
- NumKong's Float8 types (E4M3/E5M2) upcast to BFloat16 before using DPBF16PS, creating a three-tier precision hierarchy: Float8 for storage, BFloat16 for compute, Float32 for accumulation

### Float16 (f16)

IEEE 754 half-precision with 1 sign bit, 5 exponent bits (bias=15), and 10 mantissa bits, giving a range of ±65504. Float16 prioritizes precision over range (10 vs 7 mantissa bits), making it better suited for values near zero and gradients during training.

- On x86, older CPUs use F16C extensions (Ivy Bridge+) for fast Float16 → Float32 conversion; Sapphire Rapids+ adds native AVX-512-FP16
- On Arm, ARMv8.4-A adds FMLAL/FMLAL2 instructions for fused Float16 → Float32 widening multiply-accumulate, reducing total latency from 7 cycles to 4 cycles

## Mini-Floats: E4M3, E5M2, E3M2, and E2M3

### 8-bit Floats (E4M3 & E5M2)

Follow the OCP FP8 standard.

- **E4M3FN** (no infinities, NaN only): 4 exponent bits, 3 mantissa bits, range ±448. Preferred for training where precision near zero matters.
- **E5M2FN** (with infinities): 5 exponent bits, 2 mantissa bits, range ±57344. Provides wider dynamic range for inference.

On x86 Genoa/Sapphire Rapids, E4M3/E5M2 values upcast to BFloat16 via lookup tables, then use native `DPBF16PS` for 2-per-lane dot products accumulating to Float32. On Arm Graviton 3+, the same BFloat16 upcast happens via NEON table lookups, then `BFDOT` instructions complete the computation.

**E5M2 → Float16 conversion** is a single left-shift by 8 bits (SHL 8) because E5M2 shares Float16's exponent bias (15). **E4M3 on Ice Lake** uses "octave decomposition": the 4-bit exponent splits into 2 octave + 2 remainder bits, yielding 7 integer accumulators post-scaled by powers of 2.

### 6-bit Floats (E3M2 & E2M3)

Follow the OCP MX v1.0 standard. Their smaller range allows scaling to exact integers that fit in `i8`/`i16`, enabling integer `VPDPBUSD`/`SDOT` accumulation instead of the floating-point pipeline. Float16 can also serve as an accumulator, accurately representing ~50 products of E3M2FN pairs or ~20 products of E2M3FN pairs before overflow.

E3M2/E2M3 values map to exact integers via 32-entry LUTs (magnitudes up to 448 for E3M2, 120 for E2M3), enabling integer accumulation with no rounding error. On NEON+FP8DOT, E3M2 is first promoted to E5M2 and E2M3 to E4M3 before the hardware `FDOT` instruction.

### Why E2M3/E3M2 Avoid Catastrophic Cancellation

E4M3 and E5M2 cannot use the integer path. E4M3 scaled by 16 reaches 7,680 — too large for Int8. E5M2's range (±57,344) makes the scaled product exceed Int32 entirely. Without the integer path, E5M2 falls back to Float32 accumulation — where its 2-bit mantissa (only 4 values per binade) creates a catastrophic cancellation risk that E2M3's integer path avoids completely:

```
Example E5M2 products:  -0.04883, 6553600, 1.5625, -0.000114, -1.3125, -6553600, ≈ 0
Accurate sum: ~0.201
Float32 accumulation result: 0.0  (large terms cancel exactly, small terms absorbed below ULP)
```

## Integer Types

### Int8 and UInt8 (i8, u8)

Both signed and unsigned 8-bit integers use Int32 accumulation to prevent overflow. A notable optimization is the VNNI algebraic transform: on Ice Lake+ with AVX-512 VNNI, the native `DPBUSD` instruction is asymmetric (unsigned × signed → signed), but NumKong uses it for both Int8×Int8 and UInt8×UInt8:

```c
// Asymmetric transform for i8×i8 using DPBUSD (unsigned×signed)
a_unsigned = a XOR 0x80;           // Convert signed→unsigned
result = DPBUSD(a_unsigned, b);    // Computes (a+128)×b
correction = 128 * sum(b);         // Parallel on different port
final = result - correction;       // True a×b value
```

### Int4 and UInt4 (i4, u4)

Int4 values pack two nibbles per byte, requiring bitmask extraction: low nibbles `(byte & 0x0F)` and high nibbles `(byte >> 4)`. For signed Int4, the transformation `(nibble ⊕ 8) - 8` maps the unsigned range [0,15] to signed range [-8,7]. Separate accumulators for low and high nibbles avoid expensive nibble-interleaving.

## Binary: Packed Bits (u1)

The `u1` type packs 8 binary values per byte, enabling Hamming distance and Jaccard similarity via population-count instructions. On x86, `VPOPCNTDQ` (Ice Lake+) counts set bits in 512-bit registers directly; on Arm, `CNT` (NEON) operates on 8-bit lanes with a horizontal add. Results accumulate into `u32` — sufficient for vectors up to 4 billion bits.

## Complex Types

NumKong supports four complex types — `f16c`, `bf16c`, `f32c`, and `f64c` — stored as interleaved real/imaginary pairs. Essential in quantum simulation (state vectors, density matrices), signal processing (FFT coefficients, filter design), and electromagnetic modeling.

- `dot` computes the unconjugated dot product: Σ a_k · b_k
- `vdot` computes the conjugated inner product: Σ ā_k · b_k (standard in physics)

For complex dot products, NumKong defers sign flips until after the accumulation loop. Instead of using separate FMA and FMS (fused multiply-subtract) instructions for the real component, it computes a_r·b_r + a_i·b_i treating all products as positive, then applies a single bitwise XOR with `0x80000000` to flip sign bits. This avoids execution port contention between FMA and FMS.

```c
for (...) { // Complex multiply optimization: XOR sign flip after the loop
    sum_real = fma(a, b, sum_real);        // No sign flip in loop
    sum_imag = fma(a, b_swapped, sum_imag);
}
sum_real = xor(sum_real, 0x80000000);      // Single XOR after loop
```

## Python Scalar Types

NumKong exposes Python scalar objects for low-precision formats:

| Type | Bits | Bytes | Range | Inf | NaN |
| --- | --- | --- | --- | --- | --- |
| `nk.float16` | 1+5+10 | 2 | ±65504 | yes | yes |
| `nk.bfloat16` | 1+8+7 | 2 | ±3.4×10³⁸ | yes | yes |
| `nk.float8_e4m3` | 1+4+3 | 1 | ±448 | no | yes |
| `nk.float8_e5m2` | 1+5+2 | 1 | ±57344 | yes | yes |
| `nk.float6_e2m3` | 1+2+3 | 1 | ±7.5 | no | no |
| `nk.float6_e3m2` | 1+3+2 | 1 | ±28 | no | no |

The Bytes column is the stable payload size; `float8_*` and `float6_*` both store 1 byte because sub-byte formats are padded to byte alignment. Use `Tensor.itemsize` and `Tensor.nbytes` for the stable payload sizes of array storage.

## ml_dtypes Interoperability

NumKong accepts `ml_dtypes` arrays directly — no `.view(np.uint8)` workaround needed:

```python
import ml_dtypes
a = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
b = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
result = nk.cdist(a, b, "dot")  # just works
```

Type name mapping:

- `ml_dtypes.bfloat16` → `nk.bfloat16` / `"bfloat16"` (identical format)
- `ml_dtypes.float8_e4m3` / `ml_dtypes.float8_e4m3fn` → `nk.float8_e4m3` / `"e4m3"`
- `ml_dtypes.float8_e5m2` → `nk.float8_e5m2` / `"e5m2"`
- `ml_dtypes.float6_e2m3fn` → `nk.float6_e2m3` / `"e2m3"`
- `ml_dtypes.float6_e3m2fn` → `nk.float6_e3m2` / `"e3m2"`
- `ml_dtypes.int4` / `ml_dtypes.uint4` → compatible via buffer protocol

Rejected formats: FNUZ variants (`float8_e4m3fnuz`, `float8_e5m2fnuz`) have different bias, NaN, and zero encoding. `float8_e8m0fnu` is exponent-only MX scale format (not supported).
