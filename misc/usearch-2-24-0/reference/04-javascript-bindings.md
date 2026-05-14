# JavaScript Bindings

USearch for JavaScript supports Node.js and WASM environments. Keys are 64-bit integers represented as JavaScript `BigInt`.

## Installation

```sh
npm install usearch
```

## Quickstart

```js
const assert = require('node:assert');
const usearch = require('usearch');

const index = new usearch.Index({
    metric: 'l2sq',
    connectivity: 16,
    dimensions: 3
});

index.add(42n, new Float32Array([0.2, 0.6, 0.4]));
const results = index.search(new Float32Array([0.2, 0.6, 0.4]), 10);

assert(index.size() === 1);
assert.deepEqual(results.keys, new BigUint64Array([42n]));
assert.deepEqual(results.distances, new Float32Array([0]));

index.remove(42n);
```

## Advanced Configuration

```js
const index = new usearch.Index({
    dimensions: 128,
    metric: 'ip',
    quantization: 'f32',     // or 'bf16', 'f16', 'e5m2', 'e4m3', 'e3m2', 'e2m3', 'u8', 'i8', 'b1'
    connectivity: 10,
    expansion_add: 5,
    expansion_search: 3,
    multi: true              // Allow multiple vectors per key
});
```

## Serialization

```js
index.save('index.usearch');   // Save to file
index.load('index.usearch');   // Load from file
index.view('index.usearch');   // Memory-map without loading into memory
```

## Batch Operations

Use flattened `TypedArray` for performance:

```js
const keys = new BigUint64Array([15n, 16n]);
const vectors = new Float32Array([10, 20, 10, 25]);
index.add(keys, vectors);

// Multi-threaded batch operations
const threads_count = 0; // Zero for auto-detect
index.add(keys, vectors, threads_count);
const batchResults = index.search(vectors, 2, threads_count);

const firstMatch = batchResults.get(0);
```

## Index Introspection

```js
const dimensions = index.dimensions();   // Number of dimensions
const containsKey = index.contains(42n); // Check key existence
const count = index.count(42n);          // Count vectors for a key (multi-vector indexes)
```
