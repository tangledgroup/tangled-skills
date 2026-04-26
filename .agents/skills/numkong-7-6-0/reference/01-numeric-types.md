# Numeric Types and Precision

## IEEE Floats: Float64 and Float32

__Float64__ uses compensated summation for numerical stability. Serial paths use Neumaier's algorithm (an improvement over Kahan-Babuška that handles cases where added terms exceed the running sum), achieving O(1) error growth instead of O(n). SIMD paths with FMA implement the Dot2 algorithm (Ogita-Rump-Oishi, 2005), maintaining separate error compensators for multiplication and accumulation via TwoProd and TwoSum operations.

__Float32__ SIMD implementations load Float32 values, upcast to Float64 for full-precision multiplication and accumulation, then downcast only during finalization. This avoids catastrophic cancellation at minimal cost since modern CPUs have dedicated Float64 vector units operating at nearly the same throughput as Float32.

```c
// Dot2 TwoProd: Capture multiplication rounding error
h = a * b;
r = fma(a, b, -h);  // Extracts rounding error

// Dot2 TwoSum: Capture addition rounding error
t = sum + product;
e = (sum - t) + product;  // Compensator term
```

## Half Precision: BFloat16 and Float16

__BFloat16__ shares Float32's 8-bit exponent but truncates mantissa to 7 bits, prioritizing dynamic range over precision (±3.4×10³⁸). On old CPUs, upcasting is just an unpack and left-shift by 16 bits. Newer CPUs provide widening mixed-precision dot products: `VDPBF16PS` (AVX-512 on Genoa/Sapphire Rapids) and `BFDOT` (NEON on ARMv8.6-A Graviton 3+).

__Float16__ is IEEE 754 half-precision with 1 sign bit, 5 exponent bits, and 10 mantissa bits, giving range ±65504. Float16 prioritizes precision over range (10 vs 7 mantissa bits), making it better suited for values near zero and gradients during training. On x86, F16C extensions (Ivy Bridge+) provide fast Float16 → Float32 conversion. On Arm, ARMv8.4-A adds `FMLAL`/`FMLAL2` for fused Float16 → Float32 widening multiply-accumulate.

## Float8: E4M3 and E5M2

Follow the OCP FP8 standard. E4M3FN (no infinities, NaN only) is preferred for training where precision near zero matters. E5M2FN (with infinities) provides wider dynamic range for inference.

On x86 Genoa/Sapphire Rapids, Float8 values upcast to BFloat16 via lookup tables, then use native `DPBF16PS` for 2-per-lane dot products accumulating to Float32. On Arm Graviton 3+, the same BFloat16 upcast happens via NEON table lookups, then `BFDOT` instructions complete the computation.

E5M2 shares Float16's exponent bias (15), so E5M2 → Float16 conversion is a single left-shift by 8 bits. E4M3 on Ice Lake uses "octave decomposition": the 4-bit exponent splits into 2 octave + 2 remainder bits, yielding 7 integer accumulators post-scaled by powers of 2.

__Catastrophic cancellation risk__: E5M2's 2-bit mantissa (only 4 values per binade) creates catastrophic cancellation in Float32 accumulation. E2M3's integer path avoids this completely.

## Mini-Floats: E3M2 and E2M3 (6-bit MX Formats)

Follow the OCP MX v1.0 standard. Their smaller range allows scaling to exact integers that fit in i8/i16, enabling integer `VPDPBUSD`/`SDOT` accumulation instead of the floating-point pipeline. E3M2/E2M3 values map to exact integers via 32-entry LUTs (magnitudes up to 448 for E3M2, 120 for E2M3), enabling integer accumulation with no rounding error.

NumKong does not implement block-scaled variants (MXFP4, NVFP4, or block-scaled E3M2/E2M3). Block scaling couples elements through a shared exponent per block — NumKong treats each element independently. Block-scaled inputs should be dequantized before processing.

## Integer Types: Int8, UInt8, Int4, UInt4

Both signed and unsigned 8-bit and 4-bit integers are supported with Int32 accumulation to prevent overflow.

__VNNI algebraic transform__: On Ice Lake+ with AVX-512 VNNI, the native `DPBUSD` instruction is asymmetric (unsigned × signed → signed). NumKong uses it for both Int8×Int8 and UInt8×UInt8:

- For __signed Int8×Int8__: XOR operand with `0x80` to shift to unsigned, compute `(a+128)×b`, subtract correction `128×sum(b)`
- For __unsigned UInt8×UInt8__: XOR second operand to make signed, compute `a×(b-128)`, add correction `128×sum(a)`

__Int4__ values pack two nibbles per byte. Signed Int4 uses `(nibble ⊕ 8) - 8` to map unsigned [0,15] to signed [-8,7]. Separate accumulators for low and high nibbles avoid expensive nibble-interleaving.

## Binary: Packed Bits (u1x8)

The `u1x8` type packs 8 binary values per byte. Hamming distance and Jaccard similarity use population-count instructions: `VPOPCNTDQ` (Ice Lake+, 512-bit) on x86, `CNT` (NEON, 8-bit lanes with horizontal add) on Arm. Results accumulate into u32 — sufficient for vectors up to 4 billion bits.

## Complex Types

Four complex types: `f16c`, `bf16c`, `f32c`, `f64c` — stored as interleaved real/imaginary pairs. Essential for quantum simulation (state vectors, density matrices), signal processing (FFT coefficients), and electromagnetic modeling.

- `dot` computes unconjugated dot product: sum(a_k · b_k)
- `vdot` computes conjugated inner product: sum(conj(a_k) · b_k) — standard in physics

Complex multiply optimization: NumKong defers sign flips until after the accumulation loop. Instead of separate FMA and FMS instructions, it computes all products as positive, then applies single bitwise XOR with `0x80000000` to flip sign bits. This avoids execution port contention between FMA and FMS.

## Type Promotion Rules

| Input Type | Dot Output | Distance Output | Notes |
| ---------- | ---------- | --------------- | ----- |
| f64 | f64 | f64 | Compensated summation (Neumaier/Dot2) |
| f32 | f64 | f32 | Widened to f64 for dot, f32 for distance |
| bf16 | f32 | f32 | Automatic widening |
| f16 | f32 | f32 | Automatic widening |
| e4m3 | f32 | f32 | Via BF16 intermediate on modern CPUs |
| e5m2 | f32 | f32 | Via BF16 or direct F32 accumulation |
| e3m2 | f32 | f32 | Integer path via LUT |
| e2m3 | f32 | f32 | Integer path via LUT |
| i8 | i32 | f32 | Int32 accumulation for dot, f32 for distance |
| u8 | u32 | f32 | Int32 accumulation for dot, f32 for distance |
| i4 | i32 | f32 | Packed nibble pairs |
| u4 | u32 | f32 | Packed nibble pairs |
| u1 | u32 | — | Binary, popcount-based |
