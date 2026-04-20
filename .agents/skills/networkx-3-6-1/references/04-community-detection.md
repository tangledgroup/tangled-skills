# Community Detection

Community detection algorithms identify groups of nodes that are more densely connected internally than with the rest of the network.

## Modularity

Modularity measures the quality of a community partition. Higher values indicate stronger community structure.

```python
import networkx as nx
from networkx.algorithms import community

G = nx.karate_club_graph()

# Calculate modularity for a given partition
communities = [{"node1", "node2"}, {"node3", "node4", "node5"}]
mod = community.modularity(G, communities)
print(f"Modularity: {mod:.4f}")  # Typically 0.3-0.7 for good partitions

# Modularity matrix (for spectral methods)
M = community.modularity_matrix(G)
```

**Interpretation**:
- Modularity > 0.3: Significant community structure
- Modularity > 0.7: Very strong community structure
- Modularity < 0.1: Weak or no community structure

## Louvain Method

Fast modularity optimization algorithm. Works well for large networks.

```python
# Basic Louvain community detection
communities = list(community.louvain_communities(G))
print(f"Found {len(communities)} communities")

# With edge weights
communities_weighted = list(community.louvain_communities(G, weight="weight"))

# Get community assignment for each node
partition = community.louvain_partitions(G)
first_partition = next(partition)  # Get first (best) partition

# Return level-1 communities (coarsest level)
communities_l1 = list(community.louvain_communities(G, level=1))

# With resolution parameter (higher = more communities)
communities_fine = list(community.louvain_communities(G, resolution=1.5))
communities_coarse = list(community.louvain_communities(G, resolution=0.5))

# Get modularity of result
mod = community.modularity(G, communities)
```

**Parameters**:
- `resolution`: Controls community size (default 1.0). Higher = more, smaller communities.
- `weight`: Edge attribute name for weights.
- `random_state`: Seed for reproducibility.

## Label Propagation

Fast algorithm that propagates labels based on neighbor majority.

```python
# Basic label propagation
communities = list(community.label_propagation_communities(G))

# With edge weights
communities_weighted = list(community.label_propagation_communities(G, weight="weight"))

# Get community labels for each node
labels = community.label_propagation_communities(G)
label_dict = {}
for i, comm in enumerate(labels):
    for node in comm:
        label_dict[node] = i

# With seed nodes (pre-assigned communities)
seed_labels = {"node1": 0, "node2": 1}
labels_seeded = community.label_propagation_communities(G, seed=seed_labels)
```

**Advantages**: Very fast (O(E)), no parameters to tune.
**Disadvantages**: Results can vary between runs; may find trivial solutions.

## Girvan-Newman Algorithm

Hierarchical method based on edge betweenness removal.

```python
# Get hierarchy of communities (dendrogram)
gn_hierarchy = community.girvan_newman(G)

# Extract k communities
k_communities = list(community.community_to_graphs(G, gn_hierarchy)[k-1])

# Or use next() to get successive levels
level1 = next(gn_hierarchy)  # Each node is its own community
level2 = next(gn_hierarchy)  # First merge
level3 = next(gn_hierarchy)  # Second merge

# Get number of communities at each level
for i, level in enumerate(gn_hierarchy):
    if len(list(level)) == 1:  # Single community remains
        break
print(f"Hierarchy depth: {i}")
```

**Time complexity**: O(VE²) - slow for large graphs. Use for networks with < 500 nodes.

## Spectral Clustering

Uses graph Laplacian eigenvectors for clustering.

```python
from sklearn.cluster import KMeans

# Get spectral embedding
embedding = community.spectral_clustering.embedding(G, k=2)

# Apply k-means clustering
kmeans = KMeans(n_clusters=2, random_state=42)
labels = kmeans.fit_predict(embedding)

# Convert to communities
communities = [{node for node, label in zip(G.nodes(), labels) if label == i} 
               for i in range(2)]

# Or use built-in spectral clustering
communities = list(community.spectral_clustering(G, n_clusters=2))
```

## Walktrap Algorithm

Hierarchical method based on random walks.

```python
# Get hierarchy
walktrap_hierarchy = community.walktrap communities(G)

# Extract k levels
k_communities = next(walktrap_hierarchy)  # Iterate to desired level

# Number of steps for random walk (default 4)
wt_hierarchy = community.walktrap_communities(G, nsteps=6)
```

## Centrality-Based Methods

### Leading Eigenvector

Uses leading eigenvector of modularity matrix.

```python
# Binary split based on leading eigenvector
communities = list(community.leading_eigenvector_communities(G))

# Iterate for more communities
for _ in range(3):
    communities = list(community.leading_eigenvector_communities(G)
```

### Edge Cluster

Groups edges based on edge clustering coefficient.

```python
edge_clusters = community.edge_cluster(G)

# Get k clusters
k_edge_clusters = community.edge_cluster(G, k=5)
```

## Asyn_fluid Communities

Label propagation with asynchronous updates.

```python
communities = list(community.asyn_fluid_communities(G))

# With edge weights
communities_weighted = list(community.asyn_fluid_communities(G, weight="weight"))

# Maximum iterations
communities = list(community.asyn_fluid_communities(G, max_iter=1000))
```

## Graph Cut Quality Metrics

NetworkX provides built-in functions for evaluating graph cuts and partition quality.

```python
import networkx as nx

G = nx.karate_club_graph()
communities = list(community.louvain_communities(G))

# Volume: sum of degrees of nodes in a set
vol = nx.cuts.volume(G, set(communities[0]))
print(f"Volume of community 0: {vol}")

# Conductance: ratio of boundary edges to total volume
cond = nx.cuts.conductance(G, set(communities[0]))
print(f"Conductance: {cond:.4f}")

# Cut size: number of edges crossing the partition
cut_sz = nx.cuts.cut_size(G, set(communities[0]))
print(f"Cut size: {cut_sz}")

# Edge expansion: cut_size / min(volume(S), volume(V\S))
edge_exp = nx.cuts.edge_expansion(G, set(communities[0]))
print(f"Edge expansion: {edge_exp:.4f}")

# Node expansion: |boundary(S)| / min(|S|, |V\S|)
node_exp = nx.cuts.node_expansion(G, set(communities[0]))
print(f"Node expansion: {node_exp:.4f}")

# Boundary expansion: |edge_boundary(S)| / min(|S|, |V\S|)
bound_exp = nx.cuts.boundary_expansion(G, set(communities[0]))
print(f"Boundary expansion: {bound_exp:.4f}")

# Normalized cut size: cut_size / (volume(S) × volume(V\S))
norm_cut = nx.cuts.normalized_cut_size(G, set(communities[0]))
print(f"Normalized cut: {norm_cut:.6f}")

# Mixing expansion (for node classification)
mix_exp = nx.cuts.mixing_expansion(G, set(communities[0]))
```

**Quality metrics interpretation:**
- **Conductance**: Lower is better. 0 = perfect community, 1 = no internal edges.
- **Cut size**: Absolute number of crossing edges. Lower is better.
- **Edge expansion**: Per-node boundary cost. Lower is better.
- **Normalized cut**: Balanced measure penalizing small partitions.

## Custom Quality Metrics

Beyond modularity, evaluate community quality:

```python
# Conductance (fraction of edges leaving community)
def conductance(graph, community_nodes):
    community_set = set(community_nodes)
    internal_edges = sum(1 for u, v in graph.edges() 
                        if u in community_set and v in community_set)
    boundary_edges = sum(1 for u, v in graph.edges() 
                        if (u in community_set) != (v in community_set))
    total_degree = sum(graph.degree(n) for n in community_nodes)
    return boundary_edges / total_degree if total_degree > 0 else 0

# Coverage (fraction of edges within communities)
def coverage(graph, communities):
    total_edges = graph.number_of_edges()
    internal_edges = sum(len(set(graph.edges(c))) for c in communities)
    return internal_edges / total_edges if total_edges > 0 else 0

# Example usage
communities = list(community.louvain_communities(G))
for i, comm in enumerate(communities):
    cond = conductance(G, comm)
    print(f"Community {i}: conductance = {cond:.4f}")
```

## Visualizing Communities

```python
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
communities = list(community.louvain_communities(G))

# Create color mapping for communities
node_colors = {}
for i, comm in enumerate(communities):
    for node in comm:
        node_colors[node] = i

# Draw with community colors
pos = nx.spring_layout(G, seed=42)
colors = plt.cm.Set3([node_colors[n] / len(communities) for n in G.nodes()])

nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500)
nx.draw_networkx_edges(G, pos, alpha=0.3)
nx.draw_networkx_labels(G, pos, font_size=8)

plt.axis('off')
plt.title(f"Louvain Communities (modularity = {community.modularity(G, communities):.4f})")
plt.show()
```

## Comparing Algorithms

```python
G = nx.karate_club_graph()

# Run multiple algorithms
algorithms = {
    'Louvain': list(community.louvain_communities(G)),
    'Label Propagation': list(community.label_propagation_communities(G)),
    'Walktrap': list(next(community.walktrap_communities(G))),
    'Leading Eigenvector': list(community.leading_eigenvector_communities(G)),
}

# Compare results
for name, comms in algorithms.items():
    mod = community.modularity(G, comms)
    print(f"{name}: {len(comms)} communities, modularity = {mod:.4f}")

# Compare with ground truth (if available)
from sklearn.metrics import adjusted_rand_score

def communities_to_labels(communities):
    labels = {}
    for i, comm in enumerate(communities):
        for node in comm:
            labels[node] = i
    return [labels[n] for n in sorted(G.nodes())]

# Compare two partitions
labels1 = communities_to_labels(algorithms['Louvain'])
labels2 = communities_to_labels(algorithms['Label Propagation'])
ari = adjusted_rand_score(labels1, labels2)
print(f"Adjusted Rand Index: {ari:.4f}")  # 1.0 = identical, 0.0 = random
```

## Dynamic Communities

Track how communities evolve over time:

```python
def track_community_evolution(graphs):
    """Track communities across a sequence of graphs."""
    all_communities = []
    
    for t, G in enumerate(graphs):
        comms = list(community.louvain_communities(G))
        mod = community.modularity(G, comms)
        all_communities.append({
            'time': t,
            'num_communities': len(comms),
            'modularity': mod,
            'communities': comms
        })
    
    return all_communities

# Example: evolving network
G = nx.karate_club_graph()
graphs = [G]  # Add more snapshots here

evolution = track_community_evolution(graphs)
for snapshot in evolution:
    print(f"t={snapshot['time']}: {snapshot['num_communities']} communities, "
          f"modularity={snapshot['modularity']:.4f}")
```

## Leiden Algorithm

Improved version of Louvain that guarantees well-connected communities.

```python
# Basic Leiden community detection
communities = list(community.leiden_communities(G, weight="weight"))

# Get all partitions at each optimization level
partitions = list(community.leiden_partitions(G, seed=42))
best_partition = next(partitions)

# With resolution and timeout parameters
communities = list(community.leiden_communities(G, resolution_parameter=1.0,
                                                seed=42, max_iter=10,
                                                threshold=1e-7))
```

**Advantage over Louvain**: Always produces well-connected communities; better partition quality.

## Greedy Modularity Community Detection

Fast agglomerative algorithm that merges communities greedily.

```python
# Standard greedy modularity (uses heap for efficiency)
greedy_comms = list(community.greedy_modularity_communities(G, weight="weight"))

# Naive version (slower, but simpler implementation)
naive_comms = list(community.naive_greedy_modularity_communities(G))
```

## k-Clique Community Detection

Finds communities as unions of all k-cliques sharing k-1 nodes.

```python
# Find k-clique communities
k = 4
communities = list(community.k_clique_communities(G, k))

# Check if a node partition is valid
is_valid = community.community_utils.is_partition(communities)
```

**Use case**: Good for overlapping community detection when communities are dense.

## Local Greedy Community Detection

Fast local algorithm based on source expansion.

```python
communities = list(community.local.greedy_source_expansion(G, weight="weight"))
```

## Edge Betweenness Partitioning

Divisive method using edge betweenness to split communities recursively.

```python
# Standard edge betweenness partition
partitions = community.divisive.edge_betweenness_partition(G)

# Current flow betweenness variant
partitions_cf = community.divisive.edge_current_flow_betweenness_partition(G)
```

## Lukes Partitioning

Hierarchical clustering method for finding communities.

```python
partition = community.lukes.lukes_partitioning(G, weight="weight")
# Returns list of sets (community partition)
```

## Bipartite Community Methods

Community detection methods specific to bipartite graphs.

```python
from networkx.algorithms.community import bipartitions

# Kernighan-Lin bisection
partition = bipartitions.kernighan_lin_bisection(G, partition)

# Greedy node swap for bipartition
greedy_part = bipartitions.greedy_node_swap_bipartition(G, partition)

# Spectral modularity-based bipartition
spectral_part = bipartitions.spectral_modularity_bipartition(G, n_clusters=2)
```

## Community Detection Function Reference

| Function | Module | Description |
|----------|--------|-------------|
| `louvain_communities(G, weight=None)` | community.louvain | Fast modularity optimization |
| `louvain_partitions(G, seed=None)` | community.louvain | All partition levels |
| `leiden_communities(G, seed=None)` | community.leiden | Well-connected communities |
| `leiden_partitions(G, seed=None)` | community.leiden | All Leiden partition levels |
| `label_propagation_communities(G)` | community.label_propagation | Fast label propagation |
| `asyn_lpa_communities(G)` | community.label_propagation | Asynchronous LPA |
| `fast_label_propagation_communities(G)` | community.label_propagation | Optimized LPA |
| `girvan_newman(G)` | community.centrality | Hierarchical edge removal |
| `greedy_modularity_communities(G)` | community.modularity_max | Greedy agglomerative merge |
| `naive_greedy_modularity_communities(G)` | community.modularity_max | Naive greedy (slower) |
| `k_clique_communities(G, k)` | community.kclique | k-clique union communities |
| `greedy_source_expansion(G, weight=None)` | community.local | Local source expansion |
| `lukes_partitioning(G, weight=None)` | community.lukes | Hierarchical clustering |
| `edge_betweenness_partition(G)` | community.divisive | Divisive edge betweenness |
| `edge_current_flow_betweenness_partition(G)` | community.divisive | Divisive CF betweenness |
| `modularity(G, communities)` | community.quality | Partition quality measure |
| `partition_quality(G, communities)` | community.quality | Full partition quality metrics |
| `is_partition(communities)` | community.community_utils | Validate partition |

## Practical Tips

1. **Louvain/Leiden** are the best general-purpose algorithms (fast, good quality)
2. **Label propagation** for very large graphs (millions of nodes)
3. **Girvan-Newman** only for small graphs (< 500 nodes)
4. **Try multiple algorithms** and compare modularity scores
5. **Use resolution parameter** in Louvain/Leiden to find communities at different scales
6. **Validate results** with domain knowledge when possible
7. **Check stability** by running stochastic algorithms multiple times
8. **Leiden > Louvain**: Leiden guarantees connected communities and typically finds better partitions
9. **k-clique** for overlapping communities where dense subgraphs matter

## Common Pitfalls

```python
# WRONG: Assuming communities are stable across runs
comm1 = list(community.label_propagation_communities(G))
comm2 = list(community.label_propagation_communities(G))
# comm1 may differ from comm2!

# RIGHT: Set random state for reproducibility
comm1 = list(community.label_propagation_communities(G, seed=42))
comm2 = list(community.label_propagation_communities(G, seed=42))

# WRONG: Using too few communities
# Some algorithms may return trivial solutions (all nodes in one community)

# RIGHT: Check modularity and number of communities
comms = list(community.louvain_communities(G))
if len(comms) == 1:
    print("Warning: Algorithm found only one community")
    # Try with different resolution parameter
    comms = list(community.louvain_communities(G, resolution=2.0))
```
