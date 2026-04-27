# HNSW Algorithm Internals

## Graph Structure

HNSW builds a multi-layer graph where each layer is a navigable small world (NSW) graph. The implementation in `hnswalg.h` uses the following memory model:

**Level 0 (Base Layer)**: Contains all elements. Each element stores its vector data, external label, and connections to neighbors in a single contiguous block within `data_level0_memory_`. The layout per element is:

```
[link_count (2 bytes)][flags (2 bytes)][neighbor_ids... (M0 * 4 bytes)]
[vector_data... (dim * 4 bytes)]
[label (8 bytes)]
```

The total size per element at level 0 is `size_data_per_element_ = size_links_level0_ + data_size_ + sizeof(labeltype)`, where `size_links_level0_ = maxM0_ * sizeof(tableint) + sizeof(linklistsizeint)`.

**Upper Layers (1 to maxlevel_)**: Stored per-element in `linkLists_[internal_id]`. Each layer occupies `size_links_per_element_ = maxM_ * sizeof(tableint) + sizeof(linklistsizeint)` bytes. Only elements with level > 0 allocate this memory.

**Key Data Structures**:

- `data_level0_memory_` — Single `char*` allocation for all level-0 data
- `linkLists_` — Array of `char*` pointers, one per element (null for level-0-only elements)
- `element_levels_` — `std::vector<int>` mapping internal ID to element level
- `label_lookup_` — `std::unordered_map<labeltype, tableint>` mapping external labels to internal IDs
- `enterpoint_node_` — Internal ID of the highest-level element (search entry point)
- `link_list_locks_` — Per-element mutexes for thread-safe link list modifications

## Element Level Assignment

When inserting a new element, its level is drawn from an exponential distribution:

```cpp
int getRandomLevel(double reverse_size) {
    std::uniform_real_distribution<double> distribution(0.0, 1.0);
    double r = -log(distribution(level_generator_)) * reverse_size;
    return (int)r;
}
```

Where `reverse_size = 1.0 / mult_` and `mult_ = 1.0 / log(M_)`. This produces:

- P(level >= L) = 1/M^L
- Expected fraction of elements at level >= L is 1/M^L
- For M=16, roughly 6.25% of elements reach level 1, 0.39% reach level 2, etc.

The first element always becomes the entry point with its assigned level as `maxlevel_`. Subsequent elements that exceed the current `maxlevel_` become the new entry point.

## Insertion Flow (`addPoint`)

### Step 1: Label Resolution

```
1. Lock label operation mutex for this label (hash-based lock striping)
2. Check label_lookup_ for existing label
   - If found: update existing element in-place (call updatePoint)
   - If not found: proceed with new insertion
3. If replace_deleted=True and allow_replace_deleted_:
   - Check deleted_elements set for a vacant slot
   - If found: reuse that internal ID, update label_lookup_, unmark deleted
4. Otherwise: allocate next internal ID (cur_element_count++)
```

### Step 2: Level Assignment and Memory Allocation

```
1. Generate random level for the element
2. Store level in element_levels_[internal_id]
3. Zero out memory at data_level0_memory_ + internal_id * size_data_per_element_
4. Copy label and vector data into the zeroed region
5. If level > 0: allocate linkLists_[internal_id] for upper layers
```

### Step 3: Graph Navigation (Finding Entry Point at Each Layer)

If the element's level is less than `maxlevel_`, navigate downward from the global entry point:

```cpp
for (int level = maxlevel_; level > curlevel; level--) {
    bool changed = true;
    while (changed) {
        changed = false;
        // Lock the current node's link list
        // For each neighbor at this level:
        for (int i = 0; i < size; i++) {
            tableint cand = datal[i];
            dist_t d = fstdistfunc_(data_point, getDataByInternalId(cand), ...);
            if (d < curdist) {
                curdist = d;
                currObj = cand;
                changed = true;
            }
        }
    }
}
```

This greedy descent finds the closest neighbor at each layer, moving downward until reaching the new element's level.

### Step 4: Connection at Each Layer

For each layer from `min(curlevel, maxlevelcopy)` down to 0:

```
1. Call searchBaseLayer(currObj, data_point, layer)
   - Expands a candidate set of size ef_construction_
   - Returns top_candidates priority queue
2. If entry point is deleted, re-add it to candidates
3. Call mutuallyConnectNewElement(data_point, cur_c, top_candidates, level, false)
   - Applies greedy heuristic to prune candidates to M neighbors
   - Creates bi-directional links between new element and selected neighbors
```

### The Greedy Connection Heuristic (`getNeighborsByHeuristic2`)

When selecting which of the `ef_construction_` candidates become actual graph connections (limited to `M`), hnswlib uses a greedy non-dominance heuristic:

```cpp
void getNeighborsByHeuristic2(top_candidates, M) {
    // Sort candidates by distance to query (farthest first via max-heap inversion)
    while (top_candidates.size() > 0) {
        queue_closest.emplace(-top_candidates.top().first, top_candidates.top().second);
        top_candidates.pop();
    }

    // Process from closest to farthest
    while (queue_closest.size()) {
        if (return_list.size() >= M) break;
        curent_pair = queue_closest.top();
        dist_to_query = -curent_pair.first;
        queue_closest.pop();

        bool good = true;
        // Check if any already-accepted neighbor is closer to this candidate
        // than the query is — if so, this candidate is "dominated"
        for (second_pair : return_list) {
            curdist = distance(second_pair, curent_pair);
            if (curdist < dist_to_query) {
                good = false;
                break;
            }
        }
        if (good) return_list.push_back(curent_pair);
    }
}
```

This ensures that no selected neighbor is "shadowed" by another — each connection provides unique routing value.

### Bi-Directional Link Creation (`mutuallyConnectNewElement`)

After the heuristic selects up to `M` neighbors:

```
1. Write neighbor list to new element's link list (locked)
2. For each selected neighbor:
   a. Lock neighbor's link list
   b. If neighbor has capacity (< Mcurmax links):
      - Append new element ID directly
   c. Otherwise:
      - Build candidate pool: existing neighbors + new element
      - Score each by distance to the neighbor (not to query)
      - Run getNeighborsByHeuristic2 with Mcurmax limit
      - Rewrite neighbor's link list with pruned set
3. Return farthest selected neighbor as next entry point candidate
```

Key distinction: level 0 uses `maxM0_ = 2 * M_` as the connection limit, while upper layers use `maxM_ = M_`. This gives the base layer denser connectivity for thorough final-layer search.

## Search Flow (`searchKnn`)

### Phase 1: Entry Point Navigation (Same as Insertion)

Identical greedy descent from `enterpoint_node_` through upper layers to find the closest element at level 0. This establishes the starting point for base layer search.

### Phase 2: Base Layer Search (`searchBaseLayerST`)

Two modes exist controlled by compile-time template parameter `bare_bone_search`:

**Bare-bone mode** (no deletions, no filter, no stop condition):
- Skips all deletion checks and filter evaluations
- Minimal branching for maximum throughput
- Activated when `num_deleted_ == 0` and `isIdAllowed == nullptr`

**Full mode** (with deletions, filters, or custom stop conditions):
- Checks `isMarkedDeleted()` before adding to top_candidates
- Evaluates filter functor on each candidate's external label
- Supports custom `BaseSearchStopCondition` for epsilon/multi-vector search

The base layer search algorithm:

```
1. Initialize top_candidates (min-heap, keeps closest) and candidate_set (max-heap, exploration frontier)
2. Add entry point to both sets
3. While candidate_set is not empty:
   a. Pop closest unvisited from candidate_set
   b. Early termination: if its distance > lowerBound AND top_candidates is full
   c. Lock node's link list
   d. For each unvisited neighbor:
      - Mark as visited (via VisitedList tag)
      - Compute distance to query
      - If closer than worst in top_candidates or candidates not full:
        * Add to candidate_set for future exploration
        * If not deleted and passes filter: add to top_candidates
        * If top_candidates exceeds ef: pop the farthest
        * Update lowerBound = top_candidates.top().first
4. Return top_candidates (truncate to k results in caller)
```

**Visited List Mechanism**: To avoid revisiting nodes during search, each search uses a `VisitedList` from a thread-local pool. Instead of clearing the visited array between searches, it increments a global tag counter (`curV`). A node is considered "visited" if `visited_array[node_id] == current_tag`. When `curV` wraps to 0, the entire array is zeroed. This O(1) reset avoids O(N) memset per query.

```cpp
class VisitedList {
    vl_type curV;           // Current tag (increments each search)
    vl_type *mass;          // Array of tags, indexed by internal ID
    void reset() {
        curV++;
        if (curV == 0) {    // Handle wraparound
            memset(mass, 0, sizeof(vl_type) * numelements);
            curV++;
        }
    }
};
```

## Element Updates (`updatePoint`)

When an existing element's vector data changes:

```
1. Replace the vector data in-place (memcpy into data_level0_memory_)
2. For each layer the element exists on (0 to elemLevel):
   a. Collect 1-hop and 2-hop neighbors into sCand set
   b. For each 1-hop neighbor (with probability updateNeighborProbability):
      - Collect its connections into sNeigh
      - Build candidate pool from sCand
      - Run heuristic to select best connections
      - Rewrite neighbor's link list
3. Call repairConnectionsForUpdate() to re-wire the element's own connections
```

The `repairConnectionsForUpdate` method navigates from the entry point to find optimal routing for the updated element, then calls `mutuallyConnectNewElement` with `isUpdate=true` to re-establish connections at each layer.

## Soft Deletion

Deletion is soft — elements are not removed from the graph structure:

```cpp
void markDeletedInternal(tableint internalId) {
    // Sets DELETE_MARK (0x01) bit in the upper 16 bits of link list size field
    unsigned char *ll_cur = ((unsigned char *)get_linklist0(internalId)) + 2;
    *ll_cur |= DELETE_MARK;
    num_deleted_++;
    if (allow_replace_deleted_) {
        deleted_elements.insert(internalId);
    }
}
```

The delete flag occupies bits in the link count field, which limits `maxM0_` to the lower 16 bits (values up to 65535, capped at 10000 in practice). Deleted elements are skipped during search (not added to top_candidates) but remain as graph structure — they can still serve as routing nodes.

When `allow_replace_deleted=true`, deleted element slots can be reused by new insertions via `addPoint(..., replace_deleted=true)`. The old label is removed from `label_lookup_` and the slot is unmarked.

## Thread Safety Model

- **Concurrent searches**: Safe — each search uses its own VisitedList and read-only access to link lists
- **Concurrent insertions**: Safe — label lock striping + per-element link list mutexes
- **Search during insertion**: NOT safe — structural changes can corrupt search state
- **resizeIndex**: NOT thread-safe with any operation
- **saveIndex/loadIndex**: NOT thread-safe

The `ParallelFor` utility in bindings.cpp distributes work across threads using a lock-free atomic counter for task assignment, with exception propagation from worker threads.
