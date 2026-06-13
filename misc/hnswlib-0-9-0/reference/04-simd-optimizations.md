# SIMD Distance Optimizations

## Overview

hnswlib auto-selects the optimal distance computation kernel at Space construction time based on two factors: CPU instruction set availability and vector dimension alignment. The selection happens once per Space instance and is cached in the `fstdistfunc_` function pointer.

## CPU Feature Detection

Defined in `hnswlib.h`, the library detects SIMD capabilities at compile time and runtime:

### Compile-Time Detection

```cpp
#ifndef NO_MANUAL_VECTORIZATION
#if (defined(__SSE__) || _M_IX86_FP > 0 || defined(_M_AMD64) || defined(_M_X64))
#define USE_SSE
#ifdef __AVX__
#define USE_AVX
#ifdef __AVX512F__
#define USE_AVX512
#endif
#endif
#endif
#endif
```

- `USE_SSE` — Set on any x86/x86_64 target (SSE is ubiquitous)
- `USE_AVX` — Set when `__AVX__` macro is defined (typically via `-mavx`)
- `USE_AVX512` — Set when `__AVX512F__` is defined (via `-mavx512f`)

### Runtime Detection

Even if compiled with AVX/AVX512 support, the library checks at runtime whether the OS supports XSAVE/XRSTORE (required for safe AVX usage):

```cpp
static bool AVXCapable() {
    // 1. Check CPU reports AVX support via CPUID leaf 1, ECX bit 28
    // 2. Check OS supports XSAVE/XRSTORE via CPUID leaf 1, ECX bit 27
    // 3. Verify XCR feature mask has SSE+AVX states enabled (bits 1 and 2)
    uint64_t xcrFeatureMask = xgetbv(_XCR_XFEATURE_ENABLED_MASK);
    return (xcrFeatureMask & 0x6) == 0x6;
}

static bool AVX512Capable() {
    // Same OS check + CPUID leaf 7, EBX bit 16 for AVX512F
    uint64_t xcrFeatureMask = xgetbv(_XCR_XFEATURE_ENABLED_MASK);
    return (xcrFeatureMask & 0xe6) == 0xe6;
}
```

The XCR mask `0xe6` checks bits 1 (SSE), 2 (AVX/YMM), and 5 (OPMASK), 6 (ZMM_Hi256), 7 (Hi16_ZMM) required for AVX512 state management.

## L2 Distance Kernels

### Scalar Baseline

```cpp
static float L2Sqr(const void *pVect1v, const void *pVect2v, const void *qty_ptr) {
    float *pVect1 = (float *) pVect1v;
    float *pVect2 = (float *) pVect2v;
    size_t qty = *((size_t *) qty_ptr);

    float res = 0;
    for (size_t i = 0; i < qty; i++) {
        float t = *pVect1 - *pVect2;
        pVect1++; pVect2++;
        res += t * t;
    }
    return res;
}
```

### SSE Kernel (L2SqrSIMD16ExtSSE)

Processes 16 floats per loop iteration (4 vectors of 4 floats each):

```cpp
__m128 sum = _mm_set1_ps(0);
while (pVect1 < pEnd1) {
    v1 = _mm_loadu_ps(pVect1);   // Load 4 floats (unaligned)
    v2 = _mm_loadu_ps(pVect2);
    diff = _mm_sub_ps(v1, v2);   // Element-wise subtraction
    sum = _mm_add_ps(sum, _mm_mul_ps(diff, diff));  // Accumulate squared diffs
    // Repeat 4x to process 16 floats total
}
_mm_store_ps(TmpRes, sum);
return TmpRes[0] + TmpRes[1] + TmpRes[2] + TmpRes[3];  // Horizontal sum
```

Uses `_mm_loadu_ps` (unaligned load) to avoid alignment requirements. The horizontal sum of the 4 accumulator lanes gives the final result.

### AVX Kernel (L2SqrSIMD16ExtAVX)

Same structure but with 256-bit registers processing 8 floats per load:

```cpp
__m256 sum = _mm256_set1_ps(0);
while (pVect1 < pEnd1) {
    v1 = _mm256_loadu_ps(pVect1);   // 8 floats
    v2 = _mm256_loadu_ps(pVect2);
    diff = _mm256_sub_ps(v1, v2);
    sum = _mm256_add_ps(sum, _mm256_mul_ps(diff, diff));
    // Repeat 2x per iteration for 16 floats
}
_mm256_store_ps(TmpRes, sum);
return TmpRes[0] + ... + TmpRes[7];  // Sum 8 lanes
```

### AVX512 Kernel (L2SqrSIMD16ExtAVX512)

Processes 16 floats per load with 512-bit registers:

```cpp
__m512 sum = _mm512_set1_ps(0);
while (pVect1 < pEnd1) {
    v1 = _mm512_loadu_ps(pVect1);   // 16 floats in one load
    v2 = _mm512_loadu_ps(pVect2);
    diff = _mm512_sub_ps(v1, v2);
    sum = _mm512_add_ps(sum, _mm512_mul_ps(diff, diff));
}
_mm512_store_ps(TmpRes, sum);
return TmpRes[0] + ... + TmpRes[15];  // Sum 16 lanes
```

### Residual Handling

When dimension is not evenly divisible by the SIMD width, a residual scalar loop handles the remainder:

```cpp
static float L2SqrSIMD16ExtResiduals(const void *pVect1v, const void *pVect2v, const void *qty_ptr) {
    size_t qty = *((size_t *) qty_ptr);
    size_t qty16 = qty >> 4 << 4;           // Round down to multiple of 16
    float res = L2SqrSIMD16Ext(pVect1v, pVect2v, &qty16);

    // Process remaining elements with scalar loop
    float *pVect1 = (float *) pVect1v + qty16;
    float *pVect2 = (float *) pVect2v + qty16;
    size_t qty_left = qty - qty16;
    return res + L2Sqr(pVect1, pVect2, &qty_left);
}
```

Same pattern exists for SIMD4 residuals. The combined approach ensures correctness for any dimension while maximizing SIMD throughput on the bulk of the data.

## Inner Product Kernels

### Scalar Baseline

```cpp
static float InnerProduct(const void *pVect1, const void *pVect2, const void *qty_ptr) {
    size_t qty = *((size_t *) qty_ptr);
    float res = 0;
    for (unsigned i = 0; i < qty; i++)
        res += ((float *) pVect1)[i] * ((float *) pVect2)[i];
    return res;
}

static float InnerProductDistance(const void *pVect1, const void *pVect2, const void *qty_ptr) {
    return 1.0f - InnerProduct(pVect1, pVect2, qty_ptr);
}
```

### AVX512 Kernel (InnerProductSIMD16ExtAVX512)

Uses fused multiply-add (`_mm512_fmadd_ps`) for better throughput:

```cpp
__m512 sum512 = _mm512_set1_ps(0);
size_t loop = qty16 / 4;  // Process 4 blocks of 16 per outer iteration
while (loop--) {
    v1 = _mm512_loadu_ps(pVect1); v2 = _mm512_loadu_ps(pVect2);
    v3 = _mm512_loadu_ps(pVect1+16); v4 = _mm512_loadu_ps(pVect2+16);
    // ... load v5,v6 and v7,v8 ...
    sum512 = _mm512_fmadd_ps(v1, v2, sum512);
    sum512 = _mm512_fmadd_ps(v3, v4, sum512);
    sum512 = _mm512_fmadd_ps(v5, v6, sum512);
    sum512 = _mm512_fmadd_ps(v7, v8, sum512);
}
float sum = _mm512_reduce_add_ps(sum512);  // Hardware horizontal sum (AVX512ER)
return sum;
```

The loop unrolling (4 FMADDs per iteration) reduces loop overhead and improves instruction-level parallelism. The `_mm512_reduce_add_ps` intrinsic uses AVX512's dedicated reduction hardware.

### SSE/AVX Kernels

Follow the same pattern as L2 — accumulate in SIMD registers, then horizontal sum at the end. Distance variant wraps with `1.0f - result`.

## Kernel Selection Logic

At Space construction time, the kernel is selected based on dimension alignment and CPU capabilities:

```
For L2Space(dim):
  if AVX512 capable:
    set L2SqrSIMD16Ext = L2SqrSIMD16ExtAVX512
  elif AVX capable:
    set L2SqrSIMD16Ext = L2SqrSIMD16ExtAVX

  if dim % 16 == 0:
    fstdistfunc_ = L2SqrSIMD16Ext          # Full SIMD, no residual
  elif dim % 4 == 0:
    fstdistfunc_ = L2SqrSIMD4Ext           # SIMD-4, no residual
  elif dim > 16:
    fstdistfunc_ = L2SqrSIMD16ExtResiduals # SIMD-16 + scalar tail
  elif dim > 4:
    fstdistfunc_ = L2SqrSIMD4ExtResiduals  # SIMD-4 + scalar tail
  else:
    fstdistfunc_ = L2Sqr                   # Pure scalar
```

The function pointer is stored as a global variable (`L2SqrSIMD16Ext`) that gets updated at runtime based on CPU detection. This means all L2Space instances share the same SIMD16 kernel selection — the first constructed Space determines which kernel is active for all subsequent Spaces.

## Performance Characteristics

- **SIMD16 (full alignment)**: Best throughput — processes 16 floats per inner loop iteration with SSE, 16 per load with AVX512
- **SIMD4**: Good for dimensions divisible by 4 but not 16
- **Residual mode**: SIMD handles the bulk, scalar handles <15 (SIMD16) or <3 (SIMD4) remaining elements — negligible overhead
- **Scalar fallback**: Used only for very small dimensions (<4 for SSE, <16 without alignment)

## Prefetching

During graph traversal in `searchBaseLayer` and `searchBaseLayerST`, the code uses `_mm_prefetch` hints to preload neighbor data:

```cpp
#ifdef USE_SSE
_mm_prefetch((char *)(visited_array + *(data + 1)), _MM_HINT_T0);
_mm_prefetch(getDataByInternalId(*datal), _MM_HINT_T0);
_mm_prefetch(getDataByInternalId(*(datal + 1)), _MM_HINT_T0);
#endif
```

The `_MM_HINT_T0` hint suggests the data will be used very soon and should be placed in the most cache-friendly location. Prefetch targets include:
- Visited array entries (to check if neighbor was already visited)
- Neighbor vector data (for distance computation)
- Link list data (for further traversal)

## Integer L2 Distance

For byte vectors (`L2SpaceI`), two kernels exist:

```cpp
// Unrolled 4x version (dim % 4 == 0)
static int L2SqrI4x(...) {
    for (size_t i = 0; i < qty; i++) {
        res += ((*a) - (*b)) * ((*a) - (*b)); a++; b++;
        // Repeat 4x
    }
}

// Scalar version (any dim)
static int L2SqrI(...) {
    for (size_t i = 0; i < qty; i++) {
        res += ((*a) - (*b)) * ((*a) - (*b)); a++; b++;
    }
}
```

No SIMD vectorization for integer distances — the manual loop unrolling in `L2SqrI4x` provides sufficient speedup for typical use cases (e.g., 256-dimensional byte histograms).
