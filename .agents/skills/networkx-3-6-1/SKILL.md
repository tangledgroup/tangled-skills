---
name: networkx-3-6-1
description: A comprehensive toolkit for NetworkX 3.6.1, the Python package for creating, manipulating, and studying complex networks. Use when building graph analysis applications, implementing network algorithms, generating random or classic graphs, computing centrality measures, finding shortest paths, detecting communities, analyzing bipartite networks, drawing visualizations, or reading/writing graphs in various formats.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - graph-theory
  - network-analysis
  - complex-networks
  - algorithms
  - data-science
category: data-science
external_references:
  - https://github.com/networkx/networkx/tree/networkx-3.6.1
  - https://networkx.org/en/
---

# NetworkX 3.6.1

## Overview

NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks. It provides tools for analyzing social, biological, and infrastructure networks, along with a standard programming interface and graph implementation suitable for many applications.

With NetworkX you can:
- Load and store networks in standard and nonstandard data formats
- Generate random and classic network models
- Analyze network structure using advanced algorithms
- Build network models and design new algorithms
- Draw and visualize networks
- Interface with numerical algorithms and code written in C, C++, and FORTRAN

## When to Use

Use this skill when:
- **Building graph analysis applications** - Social networks, biological pathways, infrastructure systems
- **Implementing network algorithms** - Shortest paths, centrality measures, community detection, flow optimization
- **Generating test networks** - Random graphs (Erdős-Rényi, Barabási-Albert), classic graphs (Petersen, grid)
- **Analyzing network structure** - Connectivity, clustering, degree distributions, path lengths
- **Working with graph data** - Import/export in GraphML, GEXF, GML, JSON, edge lists, adjacency matrices
- **Visualizing networks** - Layout algorithms, matplotlib integration, graphviz output
- **Research and education** - Prototyping graph algorithms, teaching graph theory concepts

## Core Concepts

### Graph Types

NetworkX provides four main graph classes:

| Class | Type | Self-loops | Parallel edges |
|-------|------|------------|----------------|
| `Graph` | Undirected | Yes | No |
| `DiGraph` | Directed | Yes | No |
| `MultiGraph` | Undirected | Yes | Yes |
| `MultiDiGraph` | Directed | Yes | Yes |

```python
import networkx as nx

# Create different graph types
G = nx.Graph()              # Undirected simple graph
DG = nx.DiGraph()           # Directed simple graph
MG = nx.MultiGraph()        # Undirected multigraph
MDG = nx.MultiDiGraph()     # Directed multigraph
```

### Nodes and Edges

- **Nodes** can be any hashable Python object (strings, integers, tuples, custom objects)
- **Edges** connect pairs of nodes and can have arbitrary attributes
- **Attributes** are stored as key-value pairs on graphs, nodes, and edges

```python
G = nx.Graph()

# Add nodes with attributes
G.add_node("Alice", age=30, role="manager")
G.add_node("Bob", age=25, role="developer")

# Add edges with attributes
G.add_edge("Alice", "Bob", weight=0.8, since="2020")

# Access attributes
print(G.nodes["Alice"]["age"])      # 30
print(G.edges["Alice", "Bob"]["weight"])  # 0.8
```

### Graph Views

NetworkX uses views for efficient access to nodes, edges, and neighbors without copying data:

```python
G = nx.complete_graph(5)

# Views (not copies)
nodes = G.nodes()           # NodeView
edges = G.edges()           # EdgeView
neighbors = G.neighbors("node")  # NeighborView

# Subgraph views (lightweight, share data with original)
subview = nx.subgraph_view(G, filter_node=lambda n: n % 2 == 0)
```

## Installation

### Basic Installation

```bash
pip install networkx
```

### With Optional Dependencies

```bash
# Recommended for full functionality
pip install networkx[default]

# For all optional features (visualization, etc.)
pip install networkx[all]
```

### Development Installation

```bash
git clone https://github.com/networkx/networkx.git
cd networkx
pip install -e ".[default]"
```

## Usage Examples

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

### Shortest Paths

See [Shortest Path Algorithms](references/02-shortest-paths.md) for comprehensive coverage.

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

See [Centrality and Importance](references/03-centrality.md) for detailed explanations.

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

See [Community Detection](references/04-community-detection.md) for algorithms and examples.

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

See [Visualization](references/05-visualization.md) for layout algorithms and styling.

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

See [File Formats](references/06-file-formats.md) for format-specific details.

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

## Advanced Topics

- [Shortest Path Algorithms](references/02-shortest-paths.md) - BFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson
- [Centrality and Importance](references/03-centrality.md) - Degree, betweenness, closeness, eigenvector, PageRank, and 15+ other measures
- [Community Detection](references/04-community-detection.md) - Louvain, label propagation, Girvan-Newman, spectral clustering
- [Visualization](references/05-visualization.md) - Layout algorithms, matplotlib integration, graphviz, styling options
- [File Formats](references/06-file-formats.md) - GraphML, GEXF, GML, JSON, edge lists, adjacency matrices
- [Graph Generators](references/07-generators.md) - Random graphs, classic graphs, small-world, scale-free networks
- [Backends and Performance](references/08-backends.md) - GPU acceleration, parallel processing, third-party backends

## Algorithm Complexity Reference

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| BFS shortest path | O(V + E) | Unweighted graphs, fewest hops |
| Dijkstra | O((V + E) log V) | Weighted graphs, non-negative weights |
| Bellman-Ford | O(VE) | Graphs with negative weights |
| Floyd-Warshall | O(V³) | All-pairs shortest paths, dense graphs |
| Johnson | O(V(V + E) log V) | All-pairs with negative weights |
| Betweenness centrality | O(VE) | Node importance via shortest paths |
| Eigenvector centrality | O(k(V + E)) | k iterations, importance propagation |
| Louvain community detection | O(kE) | k iterations, modularity optimization |

Where V = number of nodes, E = number of edges.

## References

- **Official documentation**: https://networkx.org/documentation/stable/
- **GitHub repository**: https://github.com/networkx/networkx
- **Tutorial**: https://networkx.org/documentation/stable/tutorial.html
- **Reference guide**: https://networkx.org/documentation/stable/reference/
- **Citation**: Hagberg, A.A., Schult, D.A. & Swart, P.J., "Exploring network structure, dynamics, and function using NetworkX", SciPy2008
- **SciPy Conference paper (PDF)**: http://conference.scipy.org.s3-website-us-east-1.amazonaws.com/proceedings/scipy2008/paper_2/full_text.pdf
- **Mailing list**: https://groups.google.com/forum/#!forum/networkx-discuss
- **GitHub Discussions**: https://github.com/networkx/networkx/discussions
- **Discord (Scientific Python)**: https://discord.com/invite/vur45CbwMz
