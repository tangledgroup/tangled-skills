# C++ API Reference

## Header Structure

The library consists of six header files included transitively through `hnswlib.h`:

- `hnswlib.h` — Public entry point. Defines core types, interfaces, and includes all sub-headers
- `hnswalg.h` — HierarchicalNSW implementation (core algorithm)
- `space_l2.h` — L2 distance space with SIMD kernels
- `space_ip.h` — Inner product distance space with SIMD kernels
- `visited_list_pool.h` — Thread-safe visited list pool for search
- `bruteforce.h` — Brute-force k-NN baseline implementation
- `stop_condition.h` — Multi-vector and epsilon search stop conditions

## Core Types

```cpp
typedef size_t labeltype;        // External element identifier (user-facing)
typedef unsigned int tableint;   // Internal element identifier (0 to max_elements-1)
typedef unsigned int linklistsizeint;  // Link list size type (4 bytes, lower 2 bytes = count)
typedef unsigned short int vl_type;    // Visited list tag type

template<typename MTYPE>
using DISTFUNC = MTYPE(*)(const void *, const void *, const void *);
// Distance function signature: (vector_a, vector_b, param_ptr) -> distance
```

## SpaceInterface

Abstract base class for distance spaces. All distance computations go through this interface.

```cpp
template<typename dist_t>
class SpaceInterface {
public:
    virtual size_t get_data_size() = 0;
        // Returns bytes per element (e.g., dim * sizeof(float))

    virtual DISTFUNC<dist_t> get_dist_func() = 0;
        // Returns pointer to the distance computation function

    virtual void *get_dist_func_param() = 0;
        // Returns pointer to parameters passed to dist func (typically &dim)

    virtual ~SpaceInterface() {}
};
```

### L2Space

Squared Euclidean distance: `d = sum((Ai - Bi)^2)`

```cpp
hnswlib::L2Space space(128);  // 128-dimensional float vectors
// Data size: 128 * sizeof(float) = 512 bytes per vector
// Distance function: auto-selected SIMD kernel based on dim and CPU capabilities
```

Selects distance kernel at construction time:
- `dim % 16 == 0` → SIMD16 kernel (processes 16 floats per iteration)
- `dim % 4 == 0` → SIMD4 kernel (processes 4 floats per iteration)
- `dim > 16` → SIMD16 + residual scalar loop
- `dim > 4` → SIMD4 + residual scalar loop
- Otherwise → pure scalar loop

### InnerProductSpace

Inner product distance: `d = 1.0 - sum(Ai * Bi)`

Note: This is not a true metric — an element can be closer to another element than to itself. The `1.0 -` transformation converts similarity to distance for the min-heap search logic.

```cpp
hnswlib::InnerProductSpace space(128);
// Same SIMD dispatch strategy as L2Space
```

### L2SpaceI

Squared Euclidean distance for unsigned char vectors (e.g., byte-quantized embeddings or image histograms):

```cpp
hnswlib::L2SpaceI space(256);  // 256-dimensional uint8 vectors
// Data size: 256 * sizeof(unsigned char) = 256 bytes per vector
// Distance returns int (not float)
```

### MultiVector Spaces

Extend standard spaces to store a document ID alongside each vector. Used for multi-vector document search where multiple vectors belong to the same document and results are ranked at the document level.

```cpp
typedef unsigned int docidtype;

// Data layout: [vector_data...][doc_id]
hnswlib::MultiVectorL2Space<docidtype> space(128);
// get_data_size() returns dim * sizeof(float) + sizeof(docidtype)

// Set document ID on a data point before insertion:
space.set_doc_id(point_data, doc_id);

// Read document ID from a stored point:
docidtype doc_id = space.get_doc_id(stored_point_data);
```

Available variants: `MultiVectorL2Space<T>`, `MultiVectorInnerProductSpace<T>`.

## AlgorithmInterface

Abstract base class for search algorithms:

```cpp
template<typename dist_t>
class AlgorithmInterface {
public:
    virtual void addPoint(const void *datapoint, labeltype label, bool replace_deleted = false) = 0;

    virtual std::priority_queue<std::pair<dist_t, labeltype>>
        searchKnn(const void*, size_t k, BaseFilterFunctor* isIdAllowed = nullptr) const = 0;

    virtual std::vector<std::pair<dist_t, labeltype>>
        searchKnnCloserFirst(const void* query_data, size_t k,
                             BaseFilterFunctor* isIdAllowed = nullptr) const;
    // Default implementation: calls searchKnn and reverses order

    virtual void saveIndex(const std::string &location) = 0;
    virtual ~AlgorithmInterface() {}
};
```

## HierarchicalNSW

The main HNSW index class. Template parameter `dist_t` is the distance type (typically `float`).

### Construction

```cpp
// New empty index
HierarchicalNSW(SpaceInterface<dist_t> *space,
                size_t max_elements,
                size_t M = 16,
                size_t ef_construction = 200,
                size_t random_seed = 100,
                bool allow_replace_deleted = false);

// Load from file
HierarchicalNSW(SpaceInterface<dist_t> *space,
                const std::string &location,
                bool nmslib = false,       // unused, kept for compatibility
                size_t max_elements = 0,   // 0 = use saved capacity
                bool allow_replace_deleted = false);
```

### Public Methods

```cpp
// Insert or update an element
void addPoint(const void *data_point, labeltype label, bool replace_deleted = false);

// Search for k nearest neighbors
// Returns priority queue ordered by distance (largest first — pop for closest)
std::priority_queue<std::pair<dist_t, labeltype>>
searchKnn(const void *query_data, size_t k, BaseFilterFunctor* isIdAllowed = nullptr) const;

// Search with custom stop condition (for epsilon search, multi-vector search)
std::vector<std::pair<dist_t, labeltype>>
searchStopConditionClosest(const void *query_data,
                           BaseSearchStopCondition<dist_t>& stop_condition,
                           BaseFilterFunctor* isIdAllowed = nullptr) const;

// Set query-time search parameter
void setEf(size_t ef);

// Serialization
void saveIndex(const std::string &location);
void loadIndex(const std::string &location, SpaceInterface<dist_t> *s, size_t max_elements_i = 0);

// Resize capacity (NOT thread-safe)
void resizeIndex(size_t new_max_elements);

// Soft deletion
void markDelete(labeltype label);
void unmarkDelete(labeltype label);

// Retrieve stored vector data
template<typename data_t>
std::vector<data_t> getDataByLabel(labeltype label) const;

// Graph integrity check (asserts bi-directional links, no self-loops)
void checkIntegrity();
```

### Public Members

```cpp
size_t max_elements_;           // Maximum capacity
std::atomic<size_t> cur_element_count;  // Current number of elements
std::atomic<size_t> num_deleted_;       // Number of soft-deleted elements
size_t M_;                      // Max connections per element (upper layers)
size_t maxM_;                   // Same as M_ (used in heuristic)
size_t maxM0_;                  // Max connections at level 0 (= 2 * M_)
size_t ef_construction_;        // Construction-time candidate list size
size_t ef_;                     // Query-time candidate list size
double mult_;                   // 1 / log(M_) — for level generation
double revSize_;                // log(M_) — reverse of mult_
int maxlevel_;                  // Highest layer in the graph
tableint enterpoint_node_;      // Internal ID of entry point element
```

### Binary File Format

`saveIndex` writes a compact binary file with this structure:

```
Header (POD values, written sequentially):
  offsetLevel0_    : size_t
  max_elements_    : size_t
  cur_element_count: size_t
  size_data_per_element_: size_t
  label_offset_    : size_t
  offsetData_      : size_t
  maxlevel_        : int
  enterpoint_node_ : tableint (uint32)
  maxM_            : size_t
  maxM0_           : size_t
  M_               : size_t
  mult_            : double
  ef_construction_ : size_t

Level 0 Data:
  cur_element_count * size_data_per_element_ bytes (raw memory)

Upper Layer Data (per element):
  linkListSize     : unsigned int (0 if level == 0)
  linkListData     : linkListSize bytes (if non-zero)
```

No version number or magic bytes — the format is opaque and tied to the exact compilation. Files are not portable across different dimension sizes, M values, or data types.

## BruteforceSearch

Linear scan k-NN implementation for baseline comparison:

```cpp
hnswlib::BruteforceSearch<float> bf(&space, max_elements);
bf.addPoint(vector_data, label);
auto results = bf.searchKnn(query_data, k);
bf.removePoint(label);  // Actual removal (swaps with last element)
bf.saveIndex("bf.bin");
```

Stores vectors in a flat `char*` array with an embedded label per element. Search iterates all elements, maintaining a top-k heap. Thread-safe for concurrent searches but not concurrent modifications.

## BaseFilterFunctor

Interface for runtime filtering during search:

```cpp
class BaseFilterFunctor {
public:
    virtual bool operator()(hnswlib::labeltype id) { return true; }
    virtual ~BaseFilterFunctor() {}
};
```

Implement by subclassing and overriding `operator()`:

```cpp
class MyFilter : public hnswlib::BaseFilterFunctor {
    std::unordered_set<labeltype> allowed_ids_;
public:
    bool operator()(labeltype id) override {
        return allowed_ids_.count(id) > 0;
    }
};
```

Filtered elements are excluded from results but still traversed as graph nodes during search. This means filtering adds latency proportional to the number of filtered-out neighbors encountered, not just the final result set size.

## BaseSearchStopCondition

Interface for custom search termination logic (used by `searchStopConditionClosest`):

```cpp
template<typename dist_t>
class BaseSearchStopCondition {
public:
    // Called when a candidate is added to results
    virtual void add_point_to_result(labeltype label, const void *datapoint, dist_t dist) = 0;

    // Called when a candidate is removed from results
    virtual void remove_point_from_result(labeltype label, const void *datapoint, dist_t dist) = 0;

    // Should the search terminate?
    virtual bool should_stop_search(dist_t candidate_dist, dist_t lowerBound) = 0;

    // Should this candidate be explored?
    virtual bool should_consider_candidate(dist_t candidate_dist, dist_t lowerBound) = 0;

    // Should extra results be pruned?
    virtual bool should_remove_extra() = 0;

    // Post-search result filtering
    virtual void filter_results(std::vector<std::pair<dist_t, labeltype >> &candidates) = 0;

    virtual ~BaseSearchStopCondition() {}
};
```

Built-in implementations: `MultiVectorSearchStopCondition` and `EpsilonSearchStopCondition` (see Advanced Features reference).
