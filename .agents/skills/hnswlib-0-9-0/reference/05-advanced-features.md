# Advanced Search Features

## Filtering with BaseFilterFunctor

### C++ Implementation

Subclass `BaseFilterFunctor` and override `operator()`:

```cpp
class PickDivisibleIds : public hnswlib::BaseFilterFunctor {
    unsigned int divisor;
public:
    PickDivisibleIds(unsigned int d) : divisor(d) {
        assert(d != 0);
    }
    bool operator()(hnswlib::labeltype label_id) override {
        return label_id % divisor == 0;
    }
};

// Usage
PickDivisibleIds filter(2);  // Only even labels
auto results = index->searchKnn(query, k, &filter);
```

### Python Implementation

Pass a callable that takes an integer label and returns bool:

```python
# Lambda filter
filter_fn = lambda idx: idx % 2 == 0
labels, distances = p.knn_query(data, k=10, filter=filter_fn)

# Set-based filter (fast for small allowlists)
allowed = {1, 3, 5, 7, 9}
filter_fn = lambda idx: idx in allowed
labels, distances = p.knn_query(data, k=10, filter=filter_fn)
```

### Implementation Details

In the bindings, the Python filter is wrapped in a C++ functor:

```cpp
class CustomFilterFunctor : public hnswlib::BaseFilterFunctor {
    std::function<bool(hnswlib::labeltype)> filter;
public:
    explicit CustomFilterFunctor(const std::function<bool(hnswlib::labeltype)>& f) {
        filter = f;
    }
    bool operator()(hnswlib::labeltype id) {
        return filter(id);  // Calls back into Python (requires GIL)
    }
};
```

**Performance note**: Each filter evaluation crosses the C++/Python boundary via `std::function`, requiring GIL acquisition. In multithreaded mode, this creates contention. The recommended approach for Python filtering is `num_threads=1`.

### Filter Behavior in Search

Filtered elements are:
- Still traversed as graph nodes (their neighbors are explored)
- Excluded from the `top_candidates` result set
- Counted in distance computations

This means heavy filtering (e.g., allowing only 1% of elements) still incurs near-full search cost but returns fewer results. For extreme filtering, consider building a separate index for the filtered subset.

## Multi-Vector Document Search

### Concept

Multi-vector search allows multiple vectors to represent a single document (e.g., different chunks of text, different modalities). The search returns the top-N documents ranked by their best matching vector, not the top-N individual vectors.

### Architecture

Three components work together:

1. **MultiVector Space** — Stores document ID alongside each vector
2. **HierarchicalNSW** — Builds the graph as usual
3. **MultiVectorSearchStopCondition** — Custom stop condition that tracks unique documents

### Data Layout

```
[vector: float[dim]] [doc_id: DOCIDTYPE]
```

The `get_data_size()` of a multi-vector space returns `dim * sizeof(float) + sizeof(DOCIDTYPE)`. When inserting, you must set the document ID in the data buffer before calling `addPoint`:

```cpp
typedef unsigned int docidtype;
hnswlib::MultiVectorL2Space<docidtype> space(128);
hnswlib::HierarchicalNSW<float>* index =
    new hnswlib::HierarchicalNSW<float>(&space, max_elements, M, ef_construction);

// Prepare data with embedded doc_id
size_t data_point_size = space.get_data_size();
char* point_data = new char[data_point_size];
// Fill vector portion (first dim * sizeof(float) bytes)
for (int j = 0; j < dim; j++) {
    *(float*)(point_data + j * sizeof(float)) = vector_value[j];
}
// Set document ID (appended after vector)
space.set_doc_id(point_data, doc_id);

index->addPoint(point_data, label);
```

### Stop Condition Logic

`MultiVectorSearchStopCondition<DOCIDTYPE, dist_t>` implements `BaseSearchStopCondition`:

```cpp
template<typename DOCIDTYPE, typename dist_t>
class MultiVectorSearchStopCondition : public BaseSearchStopCondition<dist_t> {
    size_t curr_num_docs_;           // Unique documents in current result set
    size_t num_docs_to_search_;      // Target number of documents to return
    size_t ef_collection_;           // Expansion factor for document collection
    std::unordered_map<DOCIDTYPE, size_t> doc_counter_;  // How many vectors per doc
    std::priority_queue<std::pair<dist_t, DOCIDTYPE>> search_results_;
    BaseMultiVectorSpace<DOCIDTYPE>& space_;
};
```

The stop condition tracks:
- `ef_collection_` — Maximum number of unique documents to keep in the candidate set during search (analogous to `ef` for regular search). Higher values improve recall at the cost of speed.
- `num_docs_to_search_` — Final number of documents to return after filtering.

Search termination:
```
should_stop_search(candidate_dist, lowerBound):
  if candidate_dist > lowerBound AND curr_num_docs_ >= ef_collection_:
    return true  // Can't improve, enough docs collected
  return false
```

Result filtering (post-search):
```
filter_results(candidates):
  while curr_num_docs_ > num_docs_to_search_:
    Remove worst candidate and its associated doc_id
    Decrement doc_counter for that doc_id
    If doc_counter reaches 0, decrement curr_num_docs_
```

### Complete Example

```cpp
typedef unsigned int docidtype;
typedef float dist_t;

int dim = 16;
int max_elements = 10000;
int M = 16;
int ef_construction = 200;

int num_docs = 5;           // Documents to return
int ef_collection = 6;      // Document expansion factor

hnswlib::MultiVectorL2Space<docidtype> space(dim);
auto* index = new hnswlib::HierarchicalNSW<dist_t>(&space, max_elements, M, ef_construction);

// ... add data with doc_ids embedded ...

// Query
hnswlib::MultiVectorSearchStopCondition<docidtype, dist_t> stop_condition(
    space, num_docs, ef_collection);
auto results = index->searchStopConditionClosest(query_data, stop_condition);
```

Note: Multi-vector search is currently C++ only — not exposed in Python bindings.

## Epsilon-Radius Search

### Concept

Instead of returning exactly k neighbors, epsilon search returns all elements within a distance threshold (epsilon squared), with configurable minimum and maximum result counts.

### Stop Condition

```cpp
template<typename dist_t>
class EpsilonSearchStopCondition : public BaseSearchStopCondition<dist_t> {
    float epsilon_;                // Maximum squared distance
    size_t min_num_candidates_;    // Minimum results before early termination
    size_t max_num_candidates_;    // Maximum results to keep
    size_t curr_num_items_;        // Current count in result set
};
```

Search termination logic:

```
should_stop_search(candidate_dist, lowerBound):
  // Standard HNSW termination: can't improve, result set full
  if candidate_dist > lowerBound AND curr_num_items_ >= max_num_candidates_:
    return true

  // Epsilon termination: new candidate is outside radius and minimum met
  if candidate_dist > epsilon_ AND curr_num_items_ >= min_num_candidates_:
    return true

  return false  // Continue searching
```

Post-search filtering removes results beyond epsilon and caps at max:

```
filter_results(candidates):
  while candidates not empty AND candidates.back().dist > epsilon_:
    candidates.pop_back()
  while candidates.size() > max_num_candidates_:
    candidates.pop_back()
```

### Example

```cpp
hnswlib::L2Space space(16);
auto* index = new hnswlib::HierarchicalNSW<float>(&space, 10000, 16, 200);

// ... add data ...

float epsilon2 = 2.0;          // Squared distance threshold
int min_candidates = 100;      // Minimum results for early termination

hnswlib::EpsilonSearchStopCondition<float> stop_condition(
    epsilon2, min_candidates, 10000);
auto results = index->searchStopConditionClosest(query_data, stop_condition);
// results contains all vectors within sqrt(epsilon2) distance
```

Note: `epsilon` is the squared distance (consistent with L2Sqr returning squared distance). For actual Euclidean distance threshold of 1.0, use `epsilon = 1.0`. For threshold of 2.0, use `epsilon = 4.0`.

Epsilon search is currently C++ only — not exposed in Python bindings.

## Element Deletion and Replacement

### Soft Delete (C++ and Python)

```cpp
// C++
index->markDelete(label);     // Mark as deleted (excluded from search)
index->unmarkDelete(label);   // Restore element
```

```python
# Python
p.mark_deleted(label)
p.unmark_deleted(label)
```

Deleted elements remain in the graph structure but are excluded from search results. They continue to serve as routing nodes, which maintains graph connectivity.

### Memory Reuse

When `allow_replace_deleted=True` (C++) or `allow_replace_deleted=True` (Python `init_index`):

```python
p.init_index(max_elements=10000, allow_replace_deleted=True)
p.add_items(data1, ids1)
p.add_items(data2, ids2)  # Fill to capacity

# Delete some elements
for label in ids_to_delete:
    p.mark_deleted(label)

# Replace deleted slots with new data
p.add_items(new_data, new_ids, replace_deleted=True)
```

The replacement process:
1. Checks `deleted_elements` set for an available internal ID
2. Reuses that slot — copies new vector data and label
3. Removes old label from `label_lookup_`, adds new label
4. Calls `updatePoint` to re-wire graph connections
5. Decrements `num_deleted_` counter

This keeps the index size bounded while allowing continuous data turnover. Without replacement, the index would need periodic rebuilding to reclaim space from deleted elements.

## Graph Integrity Checking

```cpp
index->checkIntegrity();
```

Validates:
- All link targets are within valid range (`< cur_element_count`)
- No self-loops (element linked to itself)
- No duplicate links in any element's link list
- Every element has at least one inbound connection (when `cur_element_count > 1`)
- Prints min/max inbound connection counts for diagnostics

Useful for debugging corruption after concurrent operations or manual memory modifications.

## Metrics Collection

The HierarchicalNSW class tracks two atomic counters (disabled by default in v0.8.0+):

```cpp
std::atomic<long> metric_distance_computations{0};
std::atomic<long> metric_hops{0};
```

- `metric_hops` — Number of nodes visited during search
- `metric_distance_computations` — Total distance function calls

These are incremented in the `searchBaseLayerST` template when `collect_metrics=true`. Currently not exposed through the public API but available for profiling builds.
