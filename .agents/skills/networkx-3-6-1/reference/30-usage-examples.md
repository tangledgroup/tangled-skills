# Usage Examples

### Creating Graphs

```python
import networkx as nx

# From scratch
G = nx.Graph()
G.add_node(1)
G.add_edge(1, 2, weight=2.5)
G.add_edges_from([(2, 3), (3, 4)])

# From edge list
edge_list = [(1, 2), (2, 3), (3, 4), (4, 1)]
G = nx.Graph(edge_list)

# Using generators
G = nx.erdos_renyi_graph(n=100, p=0.1)      # Random graph
G = nx.barabasi_albert_graph(n=100, m=3)    # Scale-free network
G = nx.watts_strogatz_graph(n=100, k=4, p=0.1)  # Small-world
G = nx.complete_graph(10)                   # Complete graph K₁₀
G = nx.cycle_graph(10)                      # Cycle graph C₁₀
G = nx.path_graph(10)                       # Path graph P₁₀
```

### Basic Analysis

```python
# Graph properties
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"Density: {nx.density(G)}")
print(f"Diameter: {nx.diameter(G)}")

# Degree statistics
degrees = [d for n, d in G.degree()]
print(f"Average degree: {sum(degrees) / len(degrees)}")
print(f"Max degree: {max(degrees)}")

# Connectivity
print(f"Is connected: {nx.is_connected(G)}")
print(f"Number of components: {nx.number_connected_components(G)}")
```

### Core Graph Operations

See [Core Concepts and Graph Classes](reference/01-core-concepts.md) for graph types, views, attributes, set operations, and relabeling.

```python
import networkx as nx

# Graph creation from scratch
g = nx.Graph()
g.add_node(1)
g.add_edges_from([(1, 2), (2, 3)])

# Set operations
G1 | G2   # union
G1 & G2   # intersection
G1 - G2   # difference

# Relabeling
H = nx.relabel_nodes(G, {1: "a", 2: "b"})

# Frozen graphs
g.freeze()  # prevents modification
```

### Shortest Paths

See [Shortest Path Algorithms](reference/02-shortest-paths.md) for comprehensive coverage.

```python
# Single shortest path
path = nx.shortest_path(G, source="A", target="D")
length = nx.shortest_path_length(G, "A", "D")

# Weighted shortest paths
path = nx.shortest_path(G, source="A", target="D", weight="weight")

# All pairs shortest paths
lengths = dict(nx.all_pairs_shortest_path_length(G))

# Single-source shortest paths
paths = nx.single_source_shortest_path(G, "A")
```

### Centrality Measures

See [Centrality and Importance](reference/03-centrality.md) for detailed explanations.

```python
# Degree centrality (normalized degree)
dc = nx.degree_centrality(G)

# Betweenness centrality (how often node lies on shortest paths)
bc = nx.betweenness_centrality(G)

# Closeness centrality (average distance to all other nodes)
cc = nx.closeness_centrality(G)

# Eigenvector centrality (importance based on neighbors' importance)
ec = nx.eigenvector_centrality(G)

# PageRank (variant of eigenvector centrality)
pr = nx.pagerank(G)
```

### Community Detection

See [Community Detection](reference/04-community-detection.md) for algorithms and examples.

```python
from networkx.algorithms import community

# Louvain method (modularity optimization)
louvain_communities = list(community.louvain_communities(G))

# Label propagation
lp_communities = list(community.label_propagation_communities(G))

# Girvan-Newman (edge betweenness-based)
gn_communities = list(community.girvan_newman(G))

# Check modularity (quality of partition)
mod = community.modularity(G, louvain_communities)
```

### Graph Drawing

See [Visualization](reference/05-visualization.md) for layout algorithms and styling.

```python
import matplotlib.pyplot as plt

# Basic drawing
nx.draw(G, with_labels=True, node_color="lightblue", edge_color="gray")
plt.show()

# Different layouts
pos = nx.spring_layout(G)      # Force-directed layout
pos = nx.circular_layout(G)    # Circular arrangement
pos = nx.planar_layout(G)      # Planar embedding (if planar)
pos = nx.spectral_layout(G)    # Spectral embedding
pos = nx.kamada_kawai_layout(G)  # Kamada-Kawai force-directed

# Custom drawing
nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue")
nx.draw_networkx_edges(G, pos, edge_color="gray", width=2)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
plt.axis("off")
plt.show()
```

### Reading and Writing Graphs

See [File Formats](reference/06-file-formats.md) for format-specific details.

```python
# GraphML (XML-based, preserves attributes)
nx.write_graphml(G, "graph.graphml")
G = nx.read_graphml("graph.graphml")

# GEXF (Gephi format)
nx.write_gexf(G, "graph.gexf")

# GML (Graph Description Language)
nx.write_gml(G, "graph.gml")

# Edge list
nx.write_edgelist(G, "graph.edgelist", delimiter=",")
G = nx.read_edgelist("graph.edgelist")

# Adjacency list
nx.write_adjlist(G, "graph.adjlist")

# JSON (with Python objects)
import json
data = nx.node_link_data(G)
with open("graph.json", "w") as f:
    json.dump(data, f)
G = nx.node_link_graph(json.load(open("graph.json")))
```
