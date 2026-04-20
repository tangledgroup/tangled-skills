# Link Prediction and Link Analysis

NetworkX provides algorithms for predicting missing links in networks and analyzing link importance (PageRank, HITS).

## Link Prediction Algorithms

### Jaccard Coefficient

Measures similarity based on shared neighbors.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Jaccard coefficient for a specific pair
jaccard = nx.jaccard_coefficient(G, [(1, 4), (1, 5)])
for u, v, score in jaccard:
    print(f"J({u}, {v}) = {score:.4f}")
# J(1, 4) = 0.333 (1 shared neighbor out of 3 unique)
# J(1, 5) = 0.250 (1 shared neighbor out of 4 unique)

# For all nodes
all_jaccard = list(nx.jaccard_coefficient(G))
```

**Formula**: |N(u) ∩ N(v)| / |N(u) ∪ N(v)|

### Adamic-Adar Index

Weights shared neighbors by inverse log degree (rare neighbors count more).

```python
# Adamic-Adar index
adamic_adar = nx.adamic_adar_index(G, [(1, 4), (1, 5)])
for u, v, score in adamic_adar:
    print(f"AA({u}, {v}) = {score:.4f}")

# For all node pairs
all_aa = list(nx.adamic_adar_index(G))
```

**Formula**: Σ_{w ∈ N(u) ∩ N(v)} 1 / log(degree(w))

### Resource Allocation Index

Similar to Adamic-Adar but without log weighting.

```python
# Resource allocation index
ra = nx.resource_allocation_index(G, [(1, 4), (1, 5)])
for u, v, score in ra:
    print(f"RA({u}, {v}) = {score:.4f}")
```

**Formula**: Σ_{w ∈ N(u) ∩ N(v)} 1 / degree(w)

### RA Index of Soundarajan-Hopcroft

Combines within-cluster and between-cluster similarity.

```python
# RA index with cluster awareness
ra_sh = nx.ra_index_soundarajan_hopcroft(G, [(1, 4)])
for u, v, score in ra_sh:
    print(f"RA_SH({u}, {v}) = {score:.4f}")
```

### Common Neighbor Centrality

Combines common neighbors with their centrality.

```python
# Common neighbor centrality
cn = nx.common_neighbor_centrality(G, [(1, 4), (1, 5)])
for u, v, score in cn:
    print(f"CNC({u}, {v}) = {score:.4f}")
```

### Preferential Attachment

Predicts links based on product of degrees (rich-get-richer).

```python
# Preferential attachment score
pa = nx.preferential_attachment(G, [(1, 4), (1, 5)])
for u, v, score in pa:
    print(f"PA({u}, {v}) = {score:.4f}")
# Higher for pairs where at least one node has high degree
```

**Formula**: degree(u) × degree(v)

### Within-Inter Cluster Similarity

Measures if two nodes are more likely connected within same cluster.

```python
# Within-inter cluster similarity
wic = nx.within_inter_cluster(G, [(1, 4)])
for u, v, score in wic:
    print(f"WIC({u}, {v}) = {score:.4f}")
```

## Link Analysis

### PageRank (from link_analysis module)

While centrality covers basic PageRank, the link_analysis module provides additional utilities.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])

# Standard PageRank
pr = nx.pagerank(G)

# Google matrix (detailed control over teleportation)
G_matrix = nx.google_matrix(G, alpha=0.85)
# Returns the full transition matrix for PageRank computation

# Personalized PageRank via google_matrix
import numpy as np
personalization = {1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
G_personalized = nx.google_matrix(G, alpha=0.85, personalization=personalization)
# Use G_personalized for custom teleportation

# PageRank with restarts
pr_custom = nx.pagerank(
    G,
    alpha=0.85,
    personalization={1: 1.0},  # Restart at node 1
    max_iter=1000,
    tol=1e-8
)
```

### HITS (Hyperlink-Induced Topic Search)

Computes hubs and authorities scores.

```python
G = nx.DiGraph()
G.add_edges_from([
    (1, 2), (1, 3),  # Node 1 is a hub pointing to authorities
    (2, 4), (3, 4),  # Node 4 is an authority
])

# HITS algorithm
hubs, authorities = nx.hits(G)
print(hubs)       # {'1': high, '4': low}
print(authorities)  # {'4': high, '1': low}

# With custom parameters
hubs, authorities = nx.hits(
    G,
    max_iter=1000,
    tol=1e-8,
    nstart={1: 1.0}  # Initial distribution
)

# HITS is particularly useful for web graph analysis
# where hubs point to many pages and authorities are pointed to by many hubs
```

## Combining Link Prediction Measures

```python
import networkx as nx

G = nx.karate_club_graph()

# Predict missing links using multiple measures
candidate_pairs = [(u, v) for u in G.nodes() for v in G.nodes() if u < v and not G.has_edge(u, v)]

predictions = []
for u, v in candidate_pairs[:100]:  # Test on first 100 pairs
    jaccard_score = list(nx.jaccard_coefficient(G, [(u, v)]))[0][2]
    aa_score = list(nx.adamic_adar_index(G, [(u, v)]))[0][2]
    ra_score = list(nx.resource_allocation_index(G, [(u, v)]))[0][2]
    pa_score = list(nx.preferential_attachment(G, [(u, v)]))[0][2]
    
    predictions.append({
        'pair': (u, v),
        'jaccard': jaccard_score,
        'adamic_adar': aa_score,
        'resource_allocation': ra_score,
        'preferential_attachment': pa_score
    })

# Sort by combined score
predictions.sort(key=lambda x: x['adamic_adar'], reverse=True)
print("Top predicted links:")
for pred in predictions[:10]:
    print(f"  {pred['pair']}: AA={pred['adamic_adar']:.4f}, J={pred['jaccard']:.4f}")
```

## Evaluating Link Predictors

```python
from sklearn.metrics import roc_auc_score

# Split edges into training and test sets
import random
edges = list(G.edges())
random.seed(42)
random.shuffle(edges)
split = len(edges) // 2
train_edges = edges[:split]
test_edges = edges[split:]

# Build training graph
G_train = G.copy()
G_train.remove_edges_from(test_edges)

# Compute scores on test edges
positive_scores = []
for u, v in test_edges:
    if G_train.has_edge(u, v):
        continue  # Already exists
    score = list(nx.jaccard_coefficient(G_train, [(u, v)]))[0][2]
    positive_scores.append(score)

# Scores for non-edges (negative examples)
non_edges = list(nx.non_edges(G_train))
random.seed(42)
sample_non_edges = random.sample(non_edges, min(len(positive_scores), len(non_edges)))
negative_scores = []
for u, v in sample_non_edges:
    score = list(nx.jaccard_coefficient(G_train, [(u, v)]))[0][2]
    negative_scores.append(score)

# AUC-ROC
all_scores = positive_scores + negative_scores
labels = [1] * len(positive_scores) + [0] * len(negative_scores)
auc = roc_auc_score(labels, all_scores)
print(f"AUC-ROC: {auc:.4f}")
```

## Practical Applications

### Recommendation System Using Link Prediction

```python
# User-item bipartite graph for recommendations
G = nx.Graph()

# Users and items
users = [f"user_{i}" for i in range(10)]
items = [f"item_{i}" for i in range(20)]
G.add_nodes_from(users, bipartite=0)
G.add_nodes_from(items, bipartite=1)

# Known interactions
interactions = [
    ("user_0", "item_0"), ("user_0", "item_1"),
    ("user_1", "item_1"), ("user_1", "item_2"),
    ("user_2", "item_0"), ("user_2", "item_3"),
]
G.add_edges_from(interactions)

# Predict new interactions for user_0
candidates = [(u, v) for v in items if not G.has_edge("user_0", v)]
scores = list(nx.preferential_attachment(G, candidates))
recommended = sorted(scores, key=lambda x: x[2], reverse=True)[:5]

print("Top recommendations for user_0:")
for item, score in recommended:
    print(f"  {item}: score={score:.4f}")
```

### Web Graph Analysis with HITS

```python
# Simulate a web graph
G = nx.DiGraph()

# Hubs (directories, aggregators)
hubs = ["dmoz", "yahoo", "alexa"]
# Authorities (content pages)
authorities = ["wikipedia", "nytimes", "reddit", "github"]

# Hubs point to authorities
for hub in hubs:
    for auth in authorities:
        G.add_edge(hub, auth)

# Some authority-to-authority links
G.add_edges_from([
    ("wikipedia", "github"),
    ("nytimes", "github"),
])

hubs_scores, auth_scores = nx.hits(G)
print("Top hubs:", sorted(hubs_scores.items(), key=lambda x: x[1], reverse=True)[:3])
print("Top authorities:", sorted(auth_scores.items(), key=lambda x: x[1], reverse=True)[:3])
```

## Complete Link Prediction Function Reference

| Function | Description | Formula/Note |
|----------|-------------|-------------|
| `jaccard_coefficient(G, nodes=None)` | Jaccard coefficient for node pairs or all | \|N(u)∩N(v)\| / \|N(u)∪N(v)\| |
| `adamic_adar_index(G, nodes=None)` | Adamic-Adar index | Σ 1/log(degree(w)) for shared neighbors |
| `resource_allocation_index(G, nodes=None)` | Resource allocation index | Σ 1/degree(w) for shared neighbors |
| `ra_index_soundarajan_hopcroft(G, nodes=None)` | Cluster-aware RA | Considers within-cluster edges |
| `common_neighbor_centrality(G, nodes=None)` | Common neighbor centrality | Weights by neighbor centrality |
| `preferential_attachment(G, nodes=None)` | Preferential attachment | degree(u) × degree(v) |
| `within_inter_cluster(G, nodes=None)` | Within/inter cluster similarity | Same-cluster preference |

## Complete Link Analysis Function Reference

| Function | Description |
|----------|-------------|
| `pagerank(G, alpha=0.85, personalization=None)` | Standard PageRank |
| `hits(G, max_iter=1000)` | HITS hubs and authorities |
| `google_matrix(G, alpha=0.85, personalization=None)` | PageRank transition matrix |

## Summary

| Algorithm | Function | Use Case |
|-----------|----------|----------|
| Jaccard coefficient | `nx.jaccard_coefficient()` | Shared neighbor ratio |
| Adamic-Adar index | `nx.adamic_adar_index()` | Weighted shared neighbors (rare = important) |
| Resource allocation | `nx.resource_allocation_index()` | Inverse degree weighted sharing |
| RA Soundarajan-Hopcroft | `nx.ra_index_soundarajan_hopcroft()` | Cluster-aware resource allocation |
| Common neighbor centrality | `nx.common_neighbor_centrality()` | Centrality-weighted sharing |
| Preferential attachment | `nx.preferential_attachment()` | Degree product (rich-get-richer) |
| Within-inter cluster | `nx.within_inter_cluster()` | Same-cluster preference |
| HITS (hubs/authorities) | `nx.hits()` | Web graph analysis, hub authority scoring |
| Google matrix | `nx.google_matrix()` | PageRank transition matrix with personalization |
