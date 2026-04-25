# Graph Similarity and Edit Distance

NetworkX provides algorithms for measuring similarity between graphs, computing graph edit distances, and performing random walk-based similarity measures.

## Graph Edit Distance

The minimum cost sequence of node/edge operations (insert, delete, substitute) to transform one graph into another.

```python
from networkx.algorithms import similarity

G1 = nx.Graph()
G1.add_edges_from([(1, 2), (2, 3)])

G2 = nx.Graph()
G2.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Compute optimal edit paths with costs
paths = similarity.optimal_edit_paths(G1, G2)
for path, cost in paths:
    print(f"Cost: {cost}")
    for op in path:
        print(f"  {op}")

# Optimized (faster, approximate) graph edit distance
opt_cost = similarity.optimize_graph_edit_distance(G1, G2)
print(f"Optimized GED: {opt_cost}")

# Optimize edit paths (find near-optimal transformation)
opt_paths = similarity.optimize_edit_paths(G1, G2)
for path, cost in opt_paths:
    print(f"Cost: {cost}, Operations: {len(path)}")
```

**Edit operations:**
- **Node insertion**: Add a node to G1
- **Node deletion**: Remove a node from G1
- **Edge insertion**: Add an edge to G1
- **Edge deletion**: Remove an edge from G1
- **Node label substitution**: Change a node's label
- **Edge label substitution**: Change an edge's label

## Panther Similarity

Based on random walks between graphs. Measures structural similarity.

```python
# Panther similarity (0 to 1, higher = more similar)
panther_sim = similarity.panther_similarity(G1, G2)
print(panther_sim)

# Panther vector similarity (feature-based comparison)
panther_vec = similarity.panther_vector_similarity(G1, G2)
print(panther_vec)
```

## SimRank Similarity

Measures similarity based on the idea that two nodes are similar if they are referenced by similar nodes. Uses random walks with restarts.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

# SimRank similarity between pairs of nodes
sr = nx.simrank_similarity(
    G,
    source=[1],  # Reference nodes
    max_iter=100,
    epsilon=1e-6,
    target=None  # Compare against all nodes
)

# Get similarity scores
for (u, v), score in sr.items():
    print(f"SimRank({u}, {v}) = {score:.4f}")

# SimRank is useful for:
# - Link prediction
# - Node similarity search
# - Graph clustering
```

## Random Path Generation

Generate random paths between source and target nodes.

```python
# Generate random simple paths
paths = list(similarity.generate_random_paths(
    G,
    source=1,
    target=4,
    length=3,
    trials=10
))
for path in paths:
    print(path)  # e.g., [1, 3, 4] or [1, 2, 4]

# Useful for Monte Carlo estimation of connectivity metrics
```

## Practical Applications

### Document Similarity via Graph Edit Distance

```python
# Compare two documents represented as word-adjacency graphs
doc1 = nx.Graph()
doc1.add_edges_from([("the", "cat"), ("cat", "sat"), ("sat", "on")])

doc2 = nx.Graph()
doc2.add_edges_from([("the", "dog"), ("dog", "sat"), ("sat", "on")])

ged = similarity.optimal_edit_paths(doc1, doc2)
for path, cost in ged:
    print(f"Edit distance: {cost}")  # Lower = more similar documents
```

### Network Alignment via SimRank

```python
# Compare two social networks for structural similarity
G_A = nx.karate_club_graph()
G_B = nx.Graph()
G_B.add_edges_from([(u + 100, v + 100) for u, v in G_A.edges()])  # Copy with offset

# Find similar node pairs across networks
sr = nx.simrank_similarity(G_A, source=[0], target=list(range(1, 34)))
top_similar = sorted(sr.items(), key=lambda x: x[1], reverse=True)[:5]
print("Most similar to node 0:", top_similar)
```

## Summary

| Function | Description | Output |
|----------|-------------|--------|
| `optimal_edit_paths(G1, G2)` | Exact GED with edit sequences | List of (path, cost) |
| `optimize_graph_edit_distance(G1, G2)` | Fast approximate GED | Float cost |
| `optimize_edit_paths(G1, G2)` | Near-optimal edit paths | List of (path, cost) |
| `panther_similarity(G1, G2)` | Random walk-based similarity | Float 0-1 |
| `panther_vector_similarity(G1, G2)` | Feature-based similarity | Float vector |
| `simrank_similarity(G, source, ...)` | Walk-based node similarity | Dict (u,v) → score |
| `generate_random_paths(G, ...)` | Random path generation | Iterator of paths |
