---
name: python-louvain-0-16
description: Python implementation of the Louvain algorithm for community detection in graphs. Produces modularity-optimized partitions of undirected NetworkX graphs with support for weighted edges, resolution parameters, dendrogram generation, and reproducible randomization. Use when detecting communities in social networks, biological networks, citation graphs, or any graph where modular structure reveals meaningful node groupings.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - community-detection
  - louvain
  - graph-algorithms
  - networkx
  - modularity
category: data-science
external_references:
  - https://github.com/taynaud/python-louvain
  - https://python-louvain.readthedocs.io/en/latest/
---

# python-louvain 0.16

## Overview

python-louvain implements the Louvain method for community detection in large networks. It finds partitions of graph nodes that maximize modularity — a quality measure comparing the density of edges inside communities to the density expected by chance.

The library depends on NetworkX and NumPy. The pip package is named `python-louvain` but imports as `community`:

```python
import community as community_louvain
```

It exposes six public functions: `best_partition`, `generate_dendrogram`, `partition_at_level`, `modularity`, `induced_graph`, and `load_binary`. The implementation follows the original Blondel et al. 2008 paper.

## When to Use

- Detecting communities in social networks (friend groups, influencer clusters)
- Finding modular structure in biological or protein-interaction networks
- Segmenting citation graphs into research topic clusters
- Analyzing any undirected graph where dense subgroups are expected
- Comparing community quality across different resolution parameters
- Building multi-scale hierarchical views of network structure via dendrograms

## Core Concepts

### Modularity

Modularity Q measures how well a partition separates the graph into communities. It compares actual intra-community edge density against a random null model:

```
Q = Σ[community c] (Lc / L) - (Dc / 2L)²
```

Where:
- `L` is total edge weight in the graph
- `Lc` is the sum of edge weights inside community c
- `Dc` is the sum of degrees of nodes in community c

Q ranges from approximately -1 to +1. Higher values mean stronger community structure. A value of 0 means no better than random; negative means worse than random.

For k disjoint cliques of equal size, modularity = 1 - 1/k (the theoretical maximum for that configuration).

### Resolution Parameter

The resolution parameter γ (default 1.0) controls the scale at which communities are detected:

- **γ < 1.0** — larger communities, merges finer structure
- **γ = 1.0** — standard modularity optimization
- **γ > 1.0** — smaller communities, reveals finer subdivisions

This parameter corresponds to the time described in "Laplacian Dynamics and Multiscale Modular Structure in Networks" (Lambiotte, Delvenne, Barahona). Lowering resolution produces fewer, bigger communities; raising it splits communities into smaller groups.

### Dendrogram

The Louvain algorithm is inherently hierarchical. Each aggregation step produces a coarser graph where nodes represent communities from the previous level. `generate_dendrogram` captures all levels:

- Level 0 — finest partition (smallest communities)
- Level N — coarsest partition (highest modularity, biggest communities)

Each level's dictionary maps original node IDs to community IDs. Higher-level dictionaries map community IDs from the previous level to merged community IDs.

## Algorithm Explanation

The Louvain method is a greedy, two-phase heuristic that iteratively optimizes modularity. It runs in near-linear time O(n log n), making it suitable for graphs with millions of nodes and edges.

### Phase 1: Local Movement

Each node is examined once (in random order). For each node, the algorithm computes the modularity gain of moving it to each neighboring community:

1. **Remove** the node from its current community
2. **Evaluate** the modularity change if the node were placed in each neighbor's community
3. **Insert** the node into the best community (the one yielding highest modularity gain)

The modularity gain of moving node i from community c_i to community c is:

```
ΔQ = [Σ_int(c ∪ {i}) - Σ_int(c)] / L - γ · deg(i) · [Σ_deg(c ∪ {i}) - Σ_deg(c)] / (2L²)
```

Where:
- `Σ_int` is the sum of edge weights inside the community
- `Σ_deg` is the sum of degrees in the community
- `deg(i)` is the weighted degree of node i
- `γ` is the resolution parameter

This is computed incrementally — the cost of removing from the current community is calculated once, then added to each candidate's benefit. The algorithm caches node degrees and internal edge weights in a `Status` structure for O(1) updates during remove/insert operations.

The phase repeats passes over all nodes until no single move improves modularity (convergence). A minimum threshold of 0.0000001 prevents premature stopping on floating-point noise.

### Phase 2: Aggregation

Once local movement converges, each community becomes a single node in a new graph:

- Community nodes replace groups of original nodes
- Edges between communities are weighted by the sum of original edge weights crossing between them
- Self-loops on community nodes represent edges that were entirely within that community

This induced graph is produced by `induced_graph()`, which sums edge weights between all node pairs in different communities.

### Iteration

Phases 1 and 2 repeat on the aggregated graph. Each iteration:

1. Runs local movement on the current graph
2. Computes the resulting modularity
3. If improvement exceeds threshold, aggregates and repeats
4. If improvement is below threshold, stops

The algorithm terminates when modularity gain falls below `__MIN = 0.0000001`. This typically takes very few iterations — often 2-5 for real-world graphs.

### Why It Works

The Louvain method achieves near-linear complexity because:
- Each node is moved at most once per phase (O(n) per pass)
- The modularity gain formula uses cached aggregates, not full recomputation (O(degree) per node)
- Graph size decreases with each aggregation level (fewer nodes to process)
- Convergence within each phase is typically reached in 1-2 passes

The result is a hierarchical community structure that maximizes modularity at the coarsest level while preserving meaningful subdivisions at finer levels.

## Usage Examples

### Basic Community Detection

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()
partition = community_louvain.best_partition(G)

# partition is {node_id: community_id, ...}
for node, comm in sorted(partition.items()):
    print(f"Node {node} -> Community {comm}")
```

### Visualizing Communities

```python
import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx

G = nx.karate_club_graph()
partition = community_louvain.best_partition(G)

pos = nx.spring_layout(G, seed=42)
cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
                       cmap=cmap, node_color=list(partition.values()))
nx.draw_networkx_edges(G, pos, alpha=0.5)
plt.show()
```

### Resolution Parameter

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()

# Default resolution (standard communities)
part_standard = community_louvain.best_partition(G, resolution=1.0)
print(f"Standard: {len(set(part_standard.values()))} communities")

# Lower resolution -> fewer, bigger communities
part_coarse = community_louvain.best_partition(G, resolution=0.5)
print(f"Coarse (γ=0.5): {len(set(part_coarse.values()))} communities")

# Higher resolution -> more, smaller communities
part_fine = community_louvain.best_partition(G, resolution=2.0)
print(f"Fine (γ=2.0): {len(set(part_fine.values()))} communities")
```

### Dendrogram — Multi-Scale Analysis

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()
dendrogram = community_louvain.generate_dendrogram(G)

# Inspect each level
for level in range(len(dendrogram)):
    partition = community_louvain.partition_at_level(dendrogram, level)
    n_communities = len(set(partition.values()))
    mod = community_louvain.modularity(partition, G)
    print(f"Level {level}: {n_communities} communities, Q = {mod:.4f}")
```

### Weighted Graphs

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()

# Assign custom weights
for u, v in G.edges():
    G[u][v]['strength'] = 1.0  # or any weight value

# Use the 'strength' attribute as edge weight
partition = community_louvain.best_partition(G, weight='strength')
```

### Reproducible Results

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()

# Deterministic results with a seed
part1 = community_louvain.best_partition(G, random_state=42)
part2 = community_louvain.best_partition(G, random_state=42)
assert part1 == part2  # always True

# Different seeds may produce different (but equally valid) partitions
part3 = community_louvain.best_partition(G, random_state=0)
```

### Computing Modularity of a Custom Partition

```python
import community as community_louvain
import networkx as nx

G = nx.karate_club_graph()

# Manually define a partition
my_partition = {node: (node % 2) for node in G.nodes()}
q = community_louvain.modularity(my_partition, G)
print(f"Modularity of my partition: {q:.4f}")
```

### Induced Graph

```python
import community as community_louvain
import networkx as nx

G = nx.erdos_renyi_graph(100, 0.05)
partition = community_louvain.best_partition(G)

# Create a graph where each node is a community
induced = community_louvain.induced_graph(partition, G)
print(f"Original: {G.number_of_nodes()} nodes")
print(f"Induced:  {induced.number_of_nodes()} nodes (one per community)")
```

## API Reference

### `best_partition(graph, partition=None, weight='weight', resolution=1.0, randomize=None, random_state=None)`

Compute the partition maximizing modularity using the Louvain heuristic. Returns a dictionary mapping each node to a community ID (0 to N-1).

Parameters:
- **graph** — undirected NetworkX graph
- **partition** — optional starting partition dict (node -> community)
- **weight** — edge attribute key for weights (default `'weight'`, fallback 1)
- **resolution** — float γ controlling community size (default 1.0)
- **randomize** — deprecated, use `random_state` instead
- **random_state** — int seed, numpy RandomState instance, or None

Raises `TypeError` if the graph is directed.

### `generate_dendrogram(graph, part_init=None, weight='weight', resolution=1.0, randomize=None, random_state=None)`

Find communities and return the full dendrogram (list of mapping dicts). Level 0 has the finest partition; `len(dendrogram) - 1` has the coarsest (highest modularity).

### `partition_at_level(dendrogram, level)`

Extract the node-to-community partition at a given dendrogram level. Maps original node IDs to community IDs at that granularity.

### `modularity(partition, graph, weight='weight')`

Compute modularity Q of a given partition. Returns a float.

Raises:
- `TypeError` — directed graph
- `ValueError` — graph with no edges
- `KeyError` — partition missing some nodes

### `induced_graph(partition, graph, weight='weight')`

Produce a graph where each node represents a community. Edge weights between community nodes equal the sum of original edge weights crossing between their members. Self-loop weight equals internal edge weight of that community.

### `load_binary(data)`

Load a binary graph file in the format used by the C++ implementation (findcommunities). Returns a NetworkX graph.

## Constraints and Edge Cases

- **Directed graphs** — not supported; raises `TypeError`. Convert to undirected first with `G.to_undirected()`.
- **Empty graphs** (no edges) — each node is placed in its own community. Modularity is undefined (raises `ValueError`).
- **Negative edge weights** — raises `ValueError` on negative degrees or non-positive edge weights.
- **Node types** — any hashable Python type works as node IDs (ints, strings, tuples, lambdas).
- **Determinism** — without `random_state`, results vary between runs due to randomized node ordering. Use `random_state=0` for fully deterministic output.
- **Self-loops** — handled correctly; self-loop weight is counted in full (not halved) when computing internal community edges.
