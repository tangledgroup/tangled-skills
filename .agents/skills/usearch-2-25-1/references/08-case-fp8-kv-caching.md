# Case Study: FP8 Search & KV-Caching

> **Source:** https://www.unum.cloud/blog/float8
> **Loaded from:** SKILL.md (via progressive disclosure)

## Problem

LLM inference is the most important datacenter workload. The bottleneck isn't compute — it's memory for attention kernels and their KV Caches. Attention is a special case of Vector Search: every token's query vector is compared against every cached key via inner products. At small scale this is dense matrix multiplication; at large scale it's approximate nearest neighbor search (ANN).

Memory constraints are severe: HBM sold out through 2026, DRAM prices up 50% year-over-year, shortage expected until 2030. Research like RetrievalAttention and Quest replaces full attention with ANN lookup over the KV Cache, scanning just 1–3% of cached keys per token and cutting decode latency by up to 5×.

## USearch v2.25: NumKong v7

USearch's internal linear algebra was spun out into [NumKong](https://github.com/ashvardanian/NumKong) — a massive redesign over three years producing 2,000+ hand-written SIMD kernels covering 17 numeric types across 30+ CPU backends (6 architectures: x86, Arm, RISC-V, Power, LoongArch, WASM).

| Engine | Backends | Architectures | FP8/FP6 Support |
|--------|----------|---------------|-----------------|
| FAISS | 5 | 2 (x86, Arm) | No |
| USearch pre-v2.25 (SimSIMD v6) | 15+ | 2 | No |
| USearch v2.25+ (NumKong v7) | 30+ | 6 | Yes |

## Mini-Float Formats

| Type | Bits | Exp | Man | Range | Standard | Used For |
|------|------|-----|-----|-------|----------|----------|
| BFloat16 | 16 | 8 | 7 | ±3.39e38 | Google | Training weights |
| Float16 | 16 | 5 | 10 | ±65,504 | IEEE 754 | NumPy, Arrow, ONNX storage |
| Float8 E5M2 | 8 | 5 | 2 | ±57,344 | OCP MX | Gradients, backward pass |
| Float8 E4M3FN | 8 | 4 | 3 | ±448 | OCP MX | Forward pass, KV caches |
| Float6 E3M2FN | 6 | 3 | 2 | ±28 | OCP MX | MX block-scaled weights |
| Float6 E2M3FN | 6 | 2 | 3 | ±7.5 | OCP MX | MX block-scaled weights |

## Bridging Search and KV-Caching

KV caches on NVIDIA H100/H200 already live in E4M3 by default. If your search engine requires Float32, you upcast on every query, every layer, every token — USearch doesn't.

USearch's dense index separates vector storage from HNSW graph links into independent allocators:

```cpp
// Graph structure (index.hpp)
template <typename distance_at = default_distance_t,
          typename key_at = default_key_t,
          typename compressed_slot_at = default_slot_t,
          typename dynamic_allocator_at = std::allocator<byte_t>, // scratch space
          typename tape_allocator_at = dynamic_allocator_at>      // graph node & link storage
class index_gt;

// Dense index with vector management (index_dense.hpp)
template <typename key_at, typename compressed_slot_at>
class index_dense_gt {
    index_t* typed_;                                    // HNSW graph
    vectors_tape_allocator_t vectors_tape_allocator_;   // vector data — allocated separately
    vectors_lookup_t vectors_lookup_;                   // maps each slot to its vector pointer
};
```

Point `vectors_tape_allocator_` at CUDA unified memory and the HNSW graph stays in system RAM — USearch traverses the graph on CPU while reading GPU-resident E4M3 vectors without an explicit copy step.

## FP8 Upcast Paths (No Native Hardware)

NumKong ships multiple kernels per ISA generation, picking the optimal path based on execution port pressure:

| Type | Approach | How It Works | Ports Used | Platforms |
|------|----------|-------------|------------|-----------|
| E5M2 | Free Float16 widen | Byte-to-word unpack — shared exponent bias makes it valid Float16 | p0 shuffle | x86 Haswell+ |
| E4M3 | Giesen fake-Float16 | Shift mantissa, reinject sign, `VCVTPH2PS` to Float32, × 256 for bias | p0 + p1 | x86 Skylake+ |
| E4M3 | LUT → BFloat16 | 8-entry subnormal LUT + arithmetic → BF16, then `VDPBF16PS` | p5 shuffle + p0 FMA | x86 Ice Lake+ |
| Both | Giesen magic-number | Shift magnitude into Float32 exponent, × magic constant to rebias | multiply unit | Arm NEON, RISC-V, WASM |

```c
// E4M3 → F32 via Giesen's magic-number trick for Arm NEON
uint32x4_t magnitude = vandq_u32(input_e4m3, vdupq_n_u32(0x7F));       // strip sign
uint32x4_t positioned = vshlq_n_u32(magnitude, 20);                    // align in f32 space
float32x4_t converted = vmulq_f32(                                     // rebias exponent:
    vreinterpretq_f32_u32(positioned),
    vreinterpretq_f32_u32(vdupq_n_u32(0x7B800000)));                   // × 2^120 (bias 7 → 127)
```

Float6 types get an even better deal — every E2M3 value multiplied by 16 is an exact integer in [-120, 120], so Float6 dot products reduce to Int8 arithmetic with zero rounding error.

## Int8 and Cosine on Legacy Hardware

For quantized representations, **cosine distance is more robust than raw dot product** because it normalizes out magnitude distortion that quantization introduces. Integer dot products on most hardware require unsigned × signed operands, but embeddings are signed × signed. The workaround:

```
a · b = (a XOR 0x80) · b - 128 × Σb
```

XOR one operand to shift [-128, 127] → [0, 255], compute the biased product, subtract the correction. The right instruction varies by platform:

| Platform | Instruction | Signed × Signed? | NumKong Approach |
|----------|------------|-------------------|-----------------|
| x86 Haswell | `VPMADDUBSW` + `VPMADDWD` | No — u8 × i8 | XOR bias + widening chain |
| x86 Ice Lake | `VPDPBUSD` with AVX-512 VNNI | No — u8 × i8 | XOR bias + SAD correction |
| x86 Sierra Forest | `VPDPBSSD` | Yes — native | Direct |
| Arm NEON | `SDOT` via ARMv8.2+DotProd | Yes — native | Direct |
| IBM Power 9+ | `VMSUMMBM` | No — i8 × u8 | XOR bias + correction |
| WASM Relaxed SIMD | `relaxed_dot_i8x16_i7x16` | 7-bit signed | Sign mask + correction |

## Scaling Benchmarks (10M × 100D, Granite Rapids)

Tested on dual-socket Intel Xeon 6 Granite Rapids (96 cores, 192 threads), Microsoft Turing-ANNS dataset:

| Engine | Dtype | Recall@10 | Add/s | Search/s | Memory |
|--------|-------|-----------|-------|----------|--------|
| FAISS | Float32 | 0.9944 | 7,491 | 16,486 | 14.1 GB |
| FAISS | BFloat16 | 0.9944 | 3,800 | 10,391 | 12.1 GB |
| FAISS | Float16 | 0.9944 | 2,545 | 10,032 | 12.1 GB |
| USearch | Float32 | 0.9929 | 8,532 | 12,331 | 13.0 GB |
| USearch | BFloat16 | 0.9929 | 10,496 | 16,940 | 10.9 GB |
| USearch | Float16 | 0.9929 | 10,969 | 20,246 | 10.9 GB |
| **USearch** | **E5M2** | **0.9919** | **10,526** | **20,534** | **9.8 GB** |
| USearch | E4M3 | 0.9930 | 7,353 | 12,106 | 9.8 GB |
| USearch | E3M2 | 0.9728 | 10,398 | 18,022 | 9.8 GB |
| USearch | E2M3 | 0.7941 | 10,935 | 21,313 | 9.8 GB |

Key findings:
- **E5M2 is the standout** — 99.2% recall at highest throughput and ¼ the memory of Float32
- E4M3 matches Float32's 99.3% recall but pays an emulation cost on current hardware
- E3M2/E2M3 trade recall for speed — useful for coarse re-ranking stages
- FAISS doesn't support mini-floats; its half-precision paths don't improve throughput (memory-only benefit)
- Beyond 50M entries, the throughput gap grows to 10–100×

## At 100M Scale

| Dtype | Memory |
|-------|--------|
| Float32 | 139.6 GB |
| BFloat16 | 105.2 GB |
| Float16 | 105.2 GB |
| E5M2 | 88 GB |

## Python Quickstart with NumKong + USearch

```python
import usearch.index as ui
import numkong as nk, numpy as np

keys = np.arange(1000)
vectors = nk.Tensor(np.random.randn(1000, 768)).astype("bf16")
queries = nk.Tensor(np.random.randn(10, 768)).astype("bf16")

index = ui.Index(ndim=768, metric="cos", dtype="e5m2")
index.add(keys, vectors, dtype="bf16", log=True)
matches = index.search(queries, 10, dtype="bf16")
```

## When to Use This Pattern

Use FP8/mini-float quantization when:
- Building KV-cache-aware search systems for LLM inference
- Working with memory-constrained deployments (edge, mobile)
- Needing maximum throughput on legacy hardware without native FP8
- Storing vectors that originated from AI models (BFloat16 → E5M2 pipeline)
- Targeting upcoming platforms: Intel Xeon7 Diamond Rapids (AVX 10.2 FP8), NVIDIA Vera (native Float8 dot products)
