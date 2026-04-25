# Case Study: Scaling Vector Search with Intel Sapphire Rapids

> **Source:** https://www.unum.cloud/blog/scaling-vector-search-with-intel
> **Loaded from:** SKILL.md (via progressive disclosure)

## Problem

Vector search is core to Retrieval Augmented Generation (RAG) and conversational AI. Both FAISS and USearch implement HNSW, but differ significantly in design:

| | FAISS | USearch |
|---|-------|---------|
| Codebase size | 84K SLOC | 3K SLOC |
| Supported metrics | 9 fixed | user-defined |
| Supported languages | C++, Python | C++, Python, JS, Rust, Go, Java, Swift, C#, and more |
| Dependencies | BLAS, OpenMP | None |

This case study benchmarks USearch against FAISS on Intel Sapphire Rapids hardware.

## Hardware Setup

- Dual Intel Xeon 8480+ Platinum CPUs (56 cores each, 224 vCPUs total)
- 1 TB DDR5 memory across 16 channels at 4.8 GHz
- Using Deep1B dataset (1 billion 96-dimensional GoogLeNet image embeddings)

## Key Design Decisions

### No Standard Library Data Structures

Where FAISS and HNSWlib use C++ STL for arrays and priority queues, USearch relies on "tapes" and implicit/succinct data structures. Despite being a single-file implementation, it encompasses custom bit-sets, hash-tables, arrays, and mutexes — avoiding unwanted memory allocations and fragmentation.

### No Exceptions

USearch avoids raising exceptions in its core implementation. In concurrent HNSW updates from 200 threads, if one thread encounters a memory allocation error mid-update, reverting partial changes without impacting remaining threads is critical. Exceptions introduce deceptive simplicity for this scenario.

### Specialized SIMD Kernels

Three optimization approaches exist:
1. **Basic**: Trust the compiler (slowest)
2. **Intermediate**: Integrate BLAS libraries
3. **Expert**: Design specialized kernels (USearch's SimSIMD/NumKong)

Moving from approach 1 to 3 can elevate performance by up to 2,500×.

## Benchmark Results: 100M × 96D Vectors

### Indexing Speed

FAISS indexing speed decreased notably as the dataset grew. Beyond the 5M mark, FAISS tapered while USearch maintained consistent performance:

- FAISS at 100M: ~5,500 vectors/sec
- USearch at 100M: ~105,000 vectors/sec (**19× advantage**)

| Description | FAISS | USearch | Speedup |
|-------------|-------|---------|---------|
| Indexing f32 vectors | 157.6 min | 16.4 min | **9.6×** |
| Indexing f16 vectors | 154.0 min | 14.8 min | **10.4×** |
| Indexing i8 vectors | 157.9 min | 14.6 min | **10.8×** |

FAISS consistently took ~2.5 hours for each type; USearch averaged ~15 minutes.

### Search Speed

- FAISS at 100M: ~600 vectors/sec
- USearch at 100M: ~115,000 vectors/sec (**189× advantage**)

FAISS search performance decreased with a noticeable dip around the 35M entry point.

### Scaling to 1 Billion Vectors

USearch was tested alone at 1B scale (FAISS dropped out):

- Indexing speed remained above 50,000 insertions/sec at 1B entries
- Search: ~150,000 queries/sec for f32, ~225,000 for i8
- Top-1 recall decreased from 92% (100M) to 82% (1B) — adjustable via higher connectivity parameter
- Memory: < 600 GB total index (~200 bytes overhead per entry beyond the raw vectors)

### Scaling to 1536 Dimensions (100M vectors)

| Description | FAISS | USearch | Speedup |
|-------------|-------|---------|---------|
| Indexing f32 | 5.0 hours | 2.1 hours | **2.3×** |
| Indexing f16 | 4.1 hours | 1.1 hours | **3.6×** |
| Indexing i8 | 3.8 hours | 0.8 hours | **4.4×** |
| Searching f32 | 32.6 hours | 0.14 hours | **233×** |
| Searching f16 | 33.6 hours | 0.08 hours | **398×** |
| Searching i8 | 33.5 hours | 0.06 hours | **557×** |

## Hyper-Parameter Defaults

| Implementation | Connectivity | Expansion @ Construction | Expansion @ Search |
|---------------|-------------|--------------------------|-------------------|
| USearch | 16 | 128 | 64 |
| FAISS | 32 | 40 | 16 |
| HNSWlib | 16 | 200 | 10 |

## CPU vs GPU Comparison

NVIDIA RAFT (CAGRA algorithm) on A100 GPU with 80 GB HBM2:

- RAFT indexing 100M vectors: 21.8 minutes
- USearch indexing 100M vectors: 14.6–16.4 minutes

GPU memory is limited and costly — datasets beyond 100M exceed VRAM. For search latency, GPU kernel scheduling overhead (3–50 μs per kernel) limits single-stream throughput to ~20K searches/sec, while CPU USearch exceeds 100K searches/sec at 93% recall.

## Cost Comparison: 100M Vectors

| | Pinecone (SaaS) | USearch (self-hosted) |
|---|---|---|
| Throughput | 150 RPS | 150,000 RPS |
| Monthly cost | $11,989–$17,982 | ~$2,365 (AWS c7a.16xlarge) |
| Languages | 2 | 10+ |
| Open-source | No | Yes |

## Assembly Optimization Example

AVX-512 FP16 on Sapphire Rapids for cosine distance:

```asm
mov             edx, -1                         ; Load -1 into edx
bzhi            eax, edx, eax                   ; Zero high bits from bit index
kmovd           k1, eax                         ; Move to mask register k1
vmovdqu16       zmm1{k1}{z}, ZMMWORD PTR [rdi]  ; Masked load half-precision
vmovdqu16       zmm2{k1}{z}, ZMMWORD PTR [rsi]  ; Masked load half-precision
vfmadd231ph     zmm0, zmm2, zmm1                ; Fused multiply-add half-precision
```

Masked loads (`{z}`) eliminate tail loops — no need to handle remaining elements after the main vectorized loop.

## When to Use This Pattern

Use these optimization strategies when:
- Benchmarking vector search on Intel Sapphire Rapids or Granite Rapids
- Needing 10–100× speedup over FAISS at 100M+ scale
- Deploying on CPUs rather than GPUs (lower latency, no VRAM limits)
- Building self-hosted alternatives to SaaS vector databases (5–7.6× cost reduction)
- Tuning HNSW hyper-parameters for specific recall/throughput tradeoffs
- Migrating from FAISS to USearch for better scaling behavior
