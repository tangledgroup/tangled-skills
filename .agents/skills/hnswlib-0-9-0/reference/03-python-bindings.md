# Python Bindings Deep Dive

## Architecture

The Python bindings are implemented in `python_bindings/bindings.cpp` using pybind11. The file defines two wrapper classes — `Index<dist_t, data_t>` and `BFIndex<dist_t, data_t>` — both instantiated as `Index<float, float>` and `BFIndex<float, float>` in the module definition.

### Module Registration

```cpp
PYBIND11_PLUGIN(hnswlib) {
    py::module m("hnswlib");

    py::class_<Index<float>>(m, "Index")
        .def(py::init(&Index<float>::createFromParams), py::arg("params"))
        .def(py::init(&Index<float>::createFromIndex), py::arg("index"))
        .def(py::init<const std::string &, const int>(), py::arg("space"), py::arg("dim"))
        // ... methods ...

    py::class_<BFIndex<float>>(m, "BFIndex")
        // ... methods ...

    return m.ptr();
}
```

The `Index` class exposes three constructors:
1. `Index(space, dim)` — Standard constructor
2. `Index(params)` — Pickle deserialization (`__setstate__`)
3. `Index(index)` — Deep copy from another Index

## Index Class Internals

### Member Variables

```cpp
template<typename dist_t, typename data_t = float>
class Index {
    std::string space_name;           // "l2", "ip", or "cosine"
    int dim;                          // Vector dimensionality
    size_t seed;                      // Random seed for level generation
    size_t default_ef;                // Default ef before index init

    bool index_inited;                // Whether init_index() has been called
    bool ep_added;                    // Whether the first element (entry point) is added
    bool normalize;                   // True for cosine space (normalizes vectors on insert/query)
    int num_threads_default;          // Default thread count (-1 → hardware_concurrency())

    hnswlib::labeltype cur_l;         // Next auto-assigned label counter
    hnswlib::HierarchicalNSW<dist_t>* appr_alg;  // The actual HNSW index
    hnswlib::SpaceInterface<float>* l2space;     // Distance space instance
};
```

### Space Selection

The constructor maps string space names to C++ space classes:

- `"l2"` → `hnswlib::L2Space(dim)`
- `"ip"` → `hnswlib::InnerProductSpace(dim)`
- `"cosine"` → `hnswlib::InnerProductSpace(dim)` with `normalize = true`

For cosine similarity, vectors are L2-normalized before insertion and querying. The distance is computed as `1.0 - dot(normalized_a, normalized_b)`, which equals the cosine distance. Normalization happens per-thread using a thread-local buffer to avoid race conditions.

### Cosine Normalization Implementation

```cpp
void normalize_vector(float* data, float* norm_array) {
    float norm = 0.0f;
    for (int i = 0; i < dim; i++)
        norm += data[i] * data[i];
    norm = 1.0f / (sqrtf(norm) + 1e-30f);  // Epsilon prevents div-by-zero
    for (int i = 0; i < dim; i++)
        norm_array[i] = data[i] * norm;
}
```

The `1e-30f` epsilon handles zero vectors gracefully. Note that `get_items()` returns the **normalized** vectors for cosine space, not the original input.

## Thread Model

### ParallelFor Utility

The bindings implement a custom parallel executor (borrowed from nmslib) that replaces OpenMP pragmas:

```cpp
template<class Function>
inline void ParallelFor(size_t start, size_t end, size_t numThreads, Function fn) {
    if (numThreads <= 0)
        numThreads = std::thread::hardware_concurrency();

    if (numThreads == 1) {
        for (size_t id = start; id < end; id++)
            fn(id, 0);
    } else {
        std::vector<std::thread> threads;
        std::atomic<size_t> current(start);

        // Exception propagation from worker threads
        std::exception_ptr lastException = nullptr;
        std::mutex lastExceptMutex;

        for (size_t threadId = 0; threadId < numThreads; ++threadId) {
            threads.push_back(std::thread([&, threadId] {
                while (true) {
                    size_t id = current.fetch_add(1);
                    if (id >= end) break;
                    try {
                        fn(id, threadId);
                    } catch (...) {
                        std::unique_lock<std::mutex> lock(lastExceptMutex);
                        lastException = std::current_exception();
                        current = end;  // Signal other threads to stop
                        break;
                    }
                }
            }));
        }
        for (auto &thread : threads) thread.join();
        if (lastException) std::rethrow_exception(lastException);
    }
}
```

Key design decisions:
- Lock-free work distribution via `std::atomic<size_t>::fetch_add`
- Worker threads pull IDs sequentially — no static partitioning
- Exception from any thread is captured and re-thrown after join
- `num_threads_default` defaults to `hardware_concurrency()`

### GIL Management

Both `addItems` and `knnQuery_return_numpy` release the GIL during computation:

```cpp
py::gil_scoped_release l;
ParallelFor(start, rows, num_threads, [&](size_t row, size_t threadId) {
    // Heavy computation here — no Python API calls
});
// GIL automatically reacquired when 'l' goes out of scope
```

This allows other Python threads to execute during index operations. However, the filter callback (a Python function) cannot be called inside `gil_scoped_release`, which is why filtered search with multithreading has degraded performance — the filter must be evaluated per-candidate within the parallel loop but requires GIL access.

## API Methods

### init_index

```python
p.init_index(max_elements, M=16, ef_construction=200, random_seed=100, allow_replace_deleted=False)
```

Creates the underlying `HierarchicalNSW<float>` instance. Throws if already initialized. Sets `appr_alg->ef_ = default_ef` (which starts at 10).

### add_items

```python
p.add_items(data, ids=None, num_threads=-1, replace_deleted=False)
```

- `data`: numpy array of shape `(N, dim)` or `(dim,)`, must be float32
- `ids`: Optional numpy array of shape `(N,)` with integer labels. If None, auto-assigned from `cur_l`
- First element is inserted outside the parallel loop (held as entry point)
- Subsequent elements are distributed via `ParallelFor`
- For cosine space: each thread normalizes its vectors into a thread-local buffer before insertion
- Auto-reduces thread count when `rows <= num_threads * 4` (avoids thread overhead for small batches)

### knn_query

```python
labels, distances = p.knn_query(data, k=1, num_threads=-1, filter=None)
```

Returns two numpy arrays of shape `(N, k)`:
- `labels`: External labels of nearest neighbors
- `distances`: Corresponding distance values

Results are ordered by ascending distance (closest first). The C++ `searchKnn` returns a max-heap (farthest first), so the binding pops from the heap in reverse order to fill the output array closest-first.

Throws if fewer than k results are found (indicates graph corruption or ef/M too small for the dataset size).

### save_index / load_index

```python
p.save_index(path)
p.load_index(path, max_elements=0, allow_replace_deleted=False)
```

`save_index` writes the binary format directly from `HierarchicalNSW::saveIndex`. `load_index` constructs a new `HierarchicalNSW` from file, replacing any existing index (with a warning).

Note: `ef` is **not** persisted in the binary format. After loading, call `p.set_ef(value)` or access `p.ef` to set it explicitly. The binding stores `default_ef` separately, but the C++ layer resets to 10 on load.

### Pickle Serialization

The Index class implements `__getstate__` and `__setstate__` via pybind11's `.def(py::pickle(...))`:

**`__getstate__`** (`getIndexParams`):
Returns a dict containing:
- Constructor parameters: `space`, `dim`, `seed`, `num_threads`, `ep_added`, `normalize`, `index_inited`
- Runtime state: `ef`, `max_elements`, `cur_element_count`, `M`, `max_M`, `max_M0`, `mult`, `ef_construction`
- Raw memory buffers as numpy arrays: `data_level0`, `link_lists`, `element_levels`, `label_lookup_external`, `label_lookup_internal`
- Flags: `has_deletions`, `allow_replace_deleted`

Memory is copied into numpy arrays with pybind11 capsules for automatic cleanup:

```cpp
py::capsule free_when_done(data_ptr, [](void* f) { delete[] f; });
py::array_t<char>({size}, {sizeof(char)}, data_ptr, free_when_done);
```

**`__setstate__`** (`createFromParams` + `setAnnData`):
Reconstructs the index from the parameter dict. Allocates memory, copies buffers back into C++ structures, rebuilds `label_lookup_`, and processes deletion flags.

⚠️ **Thread safety warning**: Pickle serialization is NOT thread-safe with concurrent `add_items`. The `getAnnData` method acquires `appr_alg->global` lock, but the copy window creates a race condition.

### Properties

```python
# Read-only (set at construction/init)
p.space            # "l2", "ip", or "cosine"
p.dim              # Vector dimensionality
p.M                # Max connections (upper layers)
p.ef_construction  # Construction parameter
p.max_elements     # Current capacity
p.element_count    # Current number of elements

# Read-write
p.ef               # Query-time search parameter
p.num_threads      # Default thread count
```

## BFIndex Class

Brute-force baseline for recall measurement. API mirrors Index but without M/ef_construction parameters:

```python
bf = hnswlib.BFIndex(space='l2', dim=128)
bf.init_index(max_elements=100000)
bf.add_items(data, ids)
labels, distances = bf.knn_query(query_data, k=10)
bf.delete_vector(label)  # Actual removal (not soft delete)
```

Methods: `init_index`, `add_items`, `knn_query`, `delete_vector`, `save_index`, `load_index`, `set_num_threads`, `get_max_elements`, `get_current_count`.

Property: `num_threads` (read-write).

## LazyIndex

`python_bindings/LazyIndex.py` provides a thin wrapper that defers index initialization until the first `add_items` call. Useful when index parameters need to be determined from data at runtime:

```python
from hnswlib import LazyIndex

lazy = LazyIndex(space='l2', dim=128)
# No init_index needed — called automatically on first add_items
lazy.add_items(data, max_elements=len(data), M=16, ef_construction=200)
```

## Building from Source

The `setup.py` uses setuptools with a custom `BuildExt` class:

- Compiler flags: `-O3 -march=native` (unix), `/O2 /openmp` (msvc)
- On macOS: adds `-stdlib=libc++ -mmacosx-version-min=10.7`
- On Linux: adds `-fopenmp -pthread`
- Detects C++14 vs C++11 support at build time
- Set `HNSWLIB_NO_NATIVE` env var to skip `-march=native` (for cross-compilation)

Dependencies: `numpy`, `pybind11` (pulled in by setuptools).
