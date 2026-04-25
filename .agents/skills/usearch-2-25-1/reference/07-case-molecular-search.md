# Case Study: Molecular Search at Scale

> **Source:** https://ashvardanian.com/posts/usearch-molecules/
> **Loaded from:** SKILL.md (via progressive disclosure)

## Problem

Molecular similarity search requires comparing molecule graphs, which involves NP-complete subgraph isomorphism. The solution: convert molecules to binary fingerprints and search them with Tanimoto (Jaccard) distance using USearch's HNSW index.

**Scale:** 7 billion molecules from three datasets:
- PubChem: 115M molecules
- GDB-13: 977M molecules
- Enamine Real: 6B molecules

Each molecule fingerprinted with MACCS (166 bits), PubChem (881 bits), ECFP4 (2048 bits), and FCFP4 (2048 bits) — producing 28 billion structural embeddings totaling ~2.3 TB across 7,000 files on AWS S3 (`s3://usearch-molecules`).

## Molecule Fingerprints

Fingerprints convert molecule graphs into binary arrays where each bit indicates the presence of a sub-structural feature:

| Fingerprint | Dimensions | Description |
|-------------|-----------|-------------|
| MACCS Keys | 166 | Standard structural patterns (SMARTS) |
| PubChem | 881 | Substructure fingerprints |
| ECFP4 | 2048 | Extended Connectivity, diameter 4 |
| FCFP4 | 2048 | Functional Class, diameter 4 |

All evaluated using the Tanimoto coefficient (Jaccard distance on bit-strings):

```
Tanimoto(A, B) = 1 - |A ∩ B| / |A ∪ B|
```

## Basic Pipeline with RDKit + USearch

```python
from usearch.index import Index, MetricKind
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

molecules = [Chem.MolFromSmiles('CCOC'), Chem.MolFromSmiles('CCO')]
encoder = AllChem.GetRDKitFPGenerator()

fingerprints = np.vstack([encoder.GetFingerprint(x) for x in molecules])
fingerprints = np.packbits(fingerprints, axis=1)

index = Index(ndim=2048, metric=MetricKind.Tanimoto)
keys = np.arange(len(molecules))
index.add(keys, fingerprints)
matches = index.search(fingerprints, 10)
```

## Speed Optimization: AVX-512 Assembly

A baseline C++ Jaccard implementation using `std::bitset` is slow. The optimized version uses AVX-512's `vpopcntdq` instruction for population counts, achieving **56x speedup** over SciPy:

Key instructions on Sapphire Rapids (4th Gen Xeon Scalable):
- `vpopcntq` — population count in 3 cycles
- `vmovdqu8 zmm {z}` — masked loads bypass tail loops
- `bzhi` — compute mask in 1 cycle

## Speed Optimization: Numba JIT with Bit-Hacks

For known-length vectors (e.g., MACCS at exactly 166 bits = 21 bytes = 6 padded 32-bit words), unroll the loop and use a software population count:

```python
from numba import cfunc, types, carray, njit
from usearch.index import Index, CompiledMetric, MetricSignature, MetricKind

numba_signature = types.float32(
    types.CPointer(types.uint32),
    types.CPointer(types.uint32))

@njit("int_(uint32)")
def word_popcount(word):
    word = word - ((word >> 1) & 0x55555555)
    word = (word & 0x33333333) + ((word >> 2) & 0x33333333)
    c = types.uint32((word + (word >> 4) & 0xF0F0F0F) * 0x1010101) >> 24
    return c

@cfunc(numba_signature)
def tanimoto_maccs(a, b):
    a_array = carray(a, 6)  # 166 bits → 6 × uint32 (padded)
    b_array = carray(b, 6)
    ands = 0
    ors = 0
    for i in range(6):
        ands += word_popcount(a_array[i] & b_array[i])
        ors += word_popcount(a_array[i] | b_array[i])
    return 1 - types.float32(ands) / ors

index = Index(
    ndim=166,
    metric=CompiledMetric(
        pointer=tanimoto_maccs.address,
        signature=MetricSignature.ArrayArray,
        kind=MetricKind.Tanimoto,
    ),
)
```

This approach achieved **30% additional speedup** over the AVX-512 baseline for short known-length vectors. Sustained throughput exceeded 100K entries/sec (3.5B molecules/hour).

## Accuracy Improvement: Concatenated Embeddings

Combining multiple fingerprints (e.g., MACCS + ECFP4) lowers error rates by up to 3.5x:

| Config | Construction Speed | Memory | Search Speed | Recall |
|--------|-------------------|--------|-------------|--------|
| MACCS only | 115K/s | 2.5 GB | 129K/s | 96.6% |
| ECFP4 only | 75K/s | 6.5 GB | 119K/s | 99.3% |
| MACCS + ECFP4 | 79K/s | 6.5 GB | 79K/s | 99.3% |

## Accuracy Improvement: Conditional Similarity Metrics

To regain performance from concatenated embeddings, use a **two-stage conditional metric** — compare the cheaper fingerprint first, only proceed to the expensive one if similarity is above threshold:

```python
@cfunc(numba_signature)
def tanimoto_conditional(a, b):
    threshold = 0.2
    a_array = carray(a, 6 + 64)  # 6 words MACCS + 64 words ECFP4
    b_array = carray(b, 6 + 64)

    # Stage 1: Compare MACCS prefix (cheap)
    ands_maccs = 0
    ors_maccs = 0
    for i in range(6):
        ands_maccs += word_popcount(a_array[i] & b_array[i])
        ors_maccs += word_popcount(a_array[i] | b_array[i])
    maccs = 1 - types.float32(ands_maccs) / ors_maccs
    if maccs > threshold:
        return maccs  # Early exit — too dissimilar

    # Stage 2: Compare ECFP4 suffix (expensive)
    ands_ecfp4 = 0
    ors_ecfp4 = 0
    for i in range(64):
        ands_ecfp4 += word_popcount(a_array[6 + i] & b_array[6 + i])
        ors_ecfp4 += word_popcount(a_array[6 + i] | b_array[6 + i])
    ecfp4 = 1 - types.float32(ands_ecfp4) / ors_ecfp4
    return ecfp4 * threshold
```

This maintained 99% recall while regaining **60% throughput** (staying above 100K queries/sec).

## HNSW Hyper-Parameter Tuning

For 10M molecules from GDB-13, tuning `expansion_search` controls the speed/accuracy tradeoff:

| Expansion@Search | Recall@1 | Speed@Search | Comparisons | Efficiency |
|-------------------|----------|-------------|-------------|------------|
| 4 | 64.35% | 271K/s | 380 | 99.999962% |
| 16 | 78.52% | 193K/s | 670 | 99.999933% |
| 64 | 87.10% | 107K/s | 1,520 | 99.999848% |
| 256 | 93.76% | 40K/s | 4,410 | 99.999559% |
| 1024 | 98.06% | 12K/s | 14,820 | 99.998518% |
| 4096 | 99.41% | 3,728/s | 52,560 | 99.994744% |

At expansion=4096: 99.41% recall at 3,728 queries/sec, examining only 0.005% of the dataset per query (vs. 100% for brute-force). This is ~3,700x more efficient than full-scan search.

## Key Takeaways

- Binary fingerprints + Tanimoto distance enable fast molecular similarity search
- AVX-512 assembly provides 56x speedup over SciPy for Jaccard/Tanimoto
- Numba JIT with problem-specific optimizations (known lengths, bit-hacks) adds another 30%
- Concatenated embeddings improve recall but cost throughput — use conditional metrics to balance
- HNSW expansion parameters let you precisely control the speed/accuracy tradeoff
- At billion-scale, expect ~1K queries/sec; reduce dimensions and JIT distance functions to optimize

## When to Use This Pattern

Use this approach when:
- Searching for similar molecules by structure (cheminformatics)
- Working with any binary fingerprint data (genomics, hash-based features)
- Needing sub-quadratic similarity search on bit-vectors
- Building drug discovery or molecular property prediction pipelines
