# Rust Bindings

Full documentation: [docs.rs/usearch](https://docs.rs/usearch/latest/usearch/struct.Index.html)

## Installation

```toml
[dependencies]
usearch = "2.24"
```

By default, NumKong is used for dynamic SIMD dispatch. Customize features:

```toml
[dependencies]
usearch = { version = "2.24", default-features = false }
# or
usearch = { version = "2.24", features = ["numkong", "openmp", "fp16lib"] }
```

- `openmp` — uses OpenMP runtime for parallelism (better performance on Linux multi-core)
- `fp16lib` — C-layer fp16 library for older CPUs without native half-precision support

## Quickstart

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let options = IndexOptions {
    dimensions: 3,
    metric: MetricKind::IP,          // or ::L2sq, ::Cos ...
    quantization: ScalarKind::BF16,  // or ::F32, ::F16, ::E5M2, etc.
    connectivity: 0,                 // zero for auto
    expansion_add: 0,                // zero for auto
    expansion_search: 0,             // zero for auto
};

let index: Index = new_index(&options).unwrap();

assert!(index.reserve(10).is_ok());
assert_eq!(index.dimensions(), 3);
assert_eq!(index.size(), 0);

let first: [f32; 3] = [0.2, 0.1, 0.2];
assert!(index.add(42, &first).is_ok());
assert_eq!(index.size(), 2);

let results = index.search(&first, 10).unwrap();
assert_eq!(results.keys.len(), 2);
```

## Serialization

```rust
// File-based
index.save("index.usearch").unwrap();
index.load("index.usearch").unwrap();
index.view("index.usearch").unwrap();  // Memory-map from disk

// Buffer-based
let mut buffer = Vec::new();
index.save_to_buffer(&mut buffer).unwrap();
index.load_from_buffer(&buffer).unwrap();
index.view_from_buffer(&buffer).unwrap();
```

## Filtering with Predicates

Pass a closure to filter during graph traversal:

```rust
let is_odd = |key: Key| key % 2 == 1;
let query = vec![0.2, 0.1, 0.2, 0.1, 0.3];
let results = index.filtered_search(&query, 10, is_odd).unwrap();

assert!(results.keys.iter().all(|&key| key % 2 == 1));
```

## User-Defined Metrics

Define a custom weighted distance for joint embeddings:

```rust
use numkong::SpatialSimilarity;

let image_dimensions: usize = 768;
let text_dimensions: usize = 512;
let image_weights: f32 = 0.7;
let text_weights: f32 = 0.9;

let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, image_dimensions + text_dimensions);
    let b_slice = std::slice::from_raw_parts(b, image_dimensions + text_dimensions);

    let image_sim = f32::cosine(a_slice[0..image_dimensions], b_slice[0..image_dimensions]);
    let text_sim = f32::cosine(a_slice[image_dimensions..], b_slice[image_dimensions..]);
    let similarity = image_weights * image_sim + text_weights * text_sim / (image_weights + text_weights);

    1.0 - similarity
});

index.change_metric(weighted_distance);
```

Revert to a native metric:

```rust
index.change_metric_kind(MetricKind::Cos);
```

## Half-Precision Floats

USearch provides `usearch::f16` as a transparent wrapper around `i16`:

```rust
use usearch::f16 as USearchF16;
use half::f16 as HalfF16;

let vector_a: Vec<HalfF16> = /* ... */;
let buffer_a: &[USearchF16] = unsafe {
    std::slice::from_raw_parts(vector_a.as_ptr() as *const USearchF16, vector_a.len())
};
index.add(42, buffer_a);
```

## Binary Vectors

Use `b1x8` for packed binary vectors with Hamming/Tanimoto/Sorensen metrics:

```rust
let index = Index::new(&IndexOptions {
    dimensions: 8,
    metric: MetricKind::Hamming,
    quantization: ScalarKind::B1x8,
    ..Default::default()
}).unwrap();

let vector42: Vec<b1x8> = vec![b1x8(0b00001111)];
let vector43: Vec<b1x8> = vec![b1x8(0b11110000)];
let query: Vec<b1x8> = vec![b1x8(0b01111000)];

index.reserve(10).unwrap();
index.add(42, &vector42).unwrap();
index.add(43, &vector43).unwrap();

let results = index.search(&query, 5).unwrap();
assert_eq!(results.distances[0], 2.0); // 2 bits differ
```

## Performance Tuning

```rust
// Check expansion values
println!("Add expansion: {}", index.expansion_add());
println!("Search expansion: {}", index.expansion_search());

// Adjust
index.change_expansion_add(32);
index.change_expansion_search(32);

// Check hardware acceleration and memory
println!("Hardware: {}", index.hardware_acceleration());
println!("Memory: {} bytes", index.memory_usage());
```

## Available Metrics

- `MetricKind::IP` — Inner Product: `1 - sum(a[i] * b[i])`
- `MetricKind::L2sq` — Squared Euclidean: `sum((a[i] - b[i])^2)`
- `MetricKind::Cos` — Cosine Similarity
- `MetricKind::Pearson` — Pearson Correlation
- `MetricKind::Haversine` — Great Circle Distance (GIS)
- `MetricKind::Divergence` — Jensen-Shannon Divergence
- `MetricKind::Hamming` — Bit-level Hamming Distance
- `MetricKind::Tanimoto` — Bit-level Tanimoto (Jaccard)
- `MetricKind::Sorensen` — Bit-level Sorensen
