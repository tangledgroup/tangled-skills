# Rust SDK

## Installation

```toml
[dependencies]
usearch = "2.25.1"
```

Feature flags:
- `numkong` (default) — SIMD-accelerated distance kernels via NumKong
- `openmp` — OpenMP runtime for parallelism (better performance on Linux multi-core)
- `fp16lib` — C-layer fp16 emulation for older CPUs without native half-precision

Disable defaults:
```toml
usearch = { version = "2.25.1", default-features = false }
```

Enable specific features:
```toml
usearch = { version = "2.25.1", features = ["numkong", "openmp", "fp16lib"] }
```

## Quickstart

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let options = IndexOptions {
    dimensions: 3,
    metric: MetricKind::IP,
    quantization: ScalarKind::BF16,
    connectivity: 0,   // auto-tune
    expansion_add: 0,  // auto-tune
    expansion_search: 0, // auto-tune
};

let index: Index = new_index(&options).unwrap();
index.reserve(10).unwrap();

let vec = [0.2f32, 0.1, 0.2];
index.add(42, &vec).unwrap();
index.add(43, &vec).unwrap();

let results = index.search(&vec, 10).unwrap();
assert_eq!(results.keys.len(), 2);
```

## Serialization

```rust
index.save("index.usearch").unwrap();
index.load("index.usearch").unwrap();
index.view("index.usearch").unwrap();  // Memory-map, no RAM load

// In-memory buffer operations
let mut buffer = Vec::new();
index.save_to_buffer(&mut buffer).unwrap();
index.load_from_buffer(&buffer).unwrap();
index.view_from_buffer(&buffer).unwrap();
```

## Built-in Metrics

USearch ships with NumKong providing 100+ SIMD-accelerated distance kernels for x86 and ARM:

- `MetricKind::IP` — Inner Product: `1 - sum(a[i] * b[i])`
- `MetricKind::L2sq` — Squared Euclidean: `sum((a[i] - b[i])^2)`
- `MetricKind::Cos` — Cosine Similarity
- `MetricKind::Pearson` — Pearson Correlation
- `MetricKind::Haversine` — Great Circle Distance (GIS)
- `MetricKind::Divergence` — Jensen-Shannon Divergence
- `MetricKind::Hamming` — Bit-level Hamming Distance
- `MetricKind::Tanimoto` — Tanimoto (Jaccard) for bit-strings
- `MetricKind::Sorensen` — Sorensen-Dice for bit-strings

## User-Defined Metrics

Define custom distance functions with stateful callbacks:

```rust
use numkong::SpatialSimilarity;

let image_dims: usize = 768;
let text_dims: usize = 512;
let img_weight: f32 = 0.7;
let text_weight: f32 = 0.9;

let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, image_dims + text_dims);
    let b_slice = std::slice::from_raw_parts(b, image_dims + text_dims);
    let img_sim = f32::cosine(&a_slice[0..image_dims], &b_slice[0..image_dims]);
    let txt_sim = f32::cosine(&a_slice[image_dims..], &b_slice[image_dims..]);
    let sim = (img_weight * img_sim + text_weight * txt_sim) / (img_weight + text_weight);
    1.0 - sim
});

index.change_metric(weighted_distance);
```

Revert to native metric:
```rust
index.change_metric_kind(MetricKind::Cos);
```

## Filtering with Predicates

Apply filter functions during graph traversal (no post-filtering needed):

```rust
let is_odd = |key: usearch::Key| key % 2 == 1;
let query = vec![0.2, 0.1, 0.2, 0.1, 0.3];
let results = index.filtered_search(&query, 10, is_odd).unwrap();
assert!(results.keys.iter().all(|&k| k % 2 == 1));
```

## Scalar Types

Rust-native types: `f32`, `f64`, `i8`.

USearch-provided types:
- `f16` — Half-precision floating point (transparent wrapper around i16, interoperable with the `half` crate)
- `b1x8` — Byte-wide bit vector with low-level individual bit control

## Hardware Acceleration

```rust
// Check compiled ISAs
let compiled = usearch::hardware_acceleration_compiled();
// Check runtime-available ISAs
let available = usearch::hardware_acceleration_available();
```

## Crate Re-exports

```rust
use usearch::IndexOptions;   // Configuration struct for index creation
use usearch::MemoryStats;    // Memory usage statistics
use usearch::MetricKind;     // Distance metric enum
use usearch::ScalarKind;     // Data type enum (F32, BF16, F16, I8, etc.)
```

## Type Aliases

```rust
usearch::Key       // u64 — vector identifier
usearch::Distance  // f32 — similarity distance value
```
