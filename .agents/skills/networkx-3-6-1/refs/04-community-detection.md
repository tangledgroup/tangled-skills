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

## Quality Metrics

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

## Practical Tips

1. **Louvain** is the best general-purpose algorithm (fast, good quality)
2. **Label propagation** for very large graphs (millions of nodes)
3. **Girvan-Newman** only for small graphs (< 500 nodes)
4. **Try multiple algorithms** and compare modularity scores
5. **Use resolution parameter** in Louvain to find communities at different scales
6. **Validate results** with domain knowledge when possible
7. **Check stability** by running stochastic algorithms multiple times

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
