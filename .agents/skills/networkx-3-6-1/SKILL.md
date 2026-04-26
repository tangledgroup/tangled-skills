---
name: networkx-3-6-1
description: A comprehensive toolkit for NetworkX 3.6.1, the Python package for creating, manipulating, and studying complex networks. Use when building graph analysis applications, implementing network algorithms (centrality, community detection, shortest paths, flow), generating random or classic graphs, computing linear algebra representations (adjacency, Laplacian, modularity matrices), reading/writing graphs in multiple formats (GraphML, GEXF, GML, JSON, edge list), performing graph operations (union, complement, subgraph, product), visualizing networks with Matplotlib or Graphviz, or working with directed/undirected/multigraph structures.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.6.1"
tags:
  - graph-theory
  - network-analysis
  - complex-networks
  - centrality
  - community-detection
  - shortest-paths
  - graph-generators
category: data-science
external_references:
  - https://networkx.org/documentation/stable/
  - https://networkx.org/documentation/stable/reference/index.html
  - https://networkx.org/documentation/stable/tutorial.html
  - https://github.com/networkx/networkx
compatibility: "Python 3.11, 3.12, 3.13, or 3.14"
---

# NetworkX 3.6.1

## Overview

NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks. It provides tools for studying social, biological, and infrastructure networks. Released December 2025, version 3.6.1 supports Python 3.11 through 3.14.

NetworkX is pure Python with minimal dependencies. Optional backends provide GPU acceleration (nx-cugraph), parallelization (nx-parallel), and persistence layers (nx-arangodb, nx-neptune) without changing user code.

## When to Use

- Building graph analysis applications (social networks, biological networks, infrastructure)
- Implementing network algorithms: centrality, community detection, shortest paths, max flow
- Generating classic or random graphs for testing and simulation
- Computing matrix representations: adjacency, Laplacian, modularity, Bethe Hessian
- Reading/writing graphs in formats: GraphML, GEXF, GML, JSON, DOT, edge list, Matrix Market
- Performing graph operations: union, complement, subgraph, cartesian product
- Visualizing networks with Matplotlib or Graphviz
- Working with directed/undirected graphs and multigraphs
- Converting between NetworkX graphs and NumPy arrays, SciPy sparse arrays, or Pandas DataFrames

## Core Concepts

### Graph Classes

NetworkX provides four basic graph types:

- **Graph** — undirected, allows self-loops, no parallel edges
- **DiGraph** — directed, allows self-loops, no parallel edges
- **MultiGraph** — undirected, allows self-loops and parallel edges
- **MultiDiGraph** — directed, allows self-loops and parallel edges

All graph classes accept any hashable Python object as nodes (strings, images, other Graphs) and any Python object as edge attributes. The only exception: `None` is not allowed as a node.

### Nodes and Edges

Nodes can be added individually or in bulk from iterables. Edge-tuples can be 2-tuples `(u, v)` or 3-tuples `(u, v, attr_dict)`. Both `G.nodes` and `G.edges` are dict-like views providing read-only access with attribute lookup.

### Attributes

Graphs, nodes, and edges each carry a key/value attribute dictionary:

- Graph-level: `G.graph`
- Node-level: `G.nodes[node]`
- Edge-level: `G.edges[u, v]` or `G[u][v]`

The special `weight` attribute on edges should be numeric, as algorithms expect it for weighted operations.

### Views

NetworkX provides read-only graph views for temporary morphing without copying:

- `subgraph_view(G, nodes)` — node-induced subgraph view
- `reverse_view(G)` — reverse edge directions (DiGraph)
- `generic_graph_view(G, create_using)` — cast to another graph type
- Filter functions: `hide_nodes()`, `show_nodes()`, `hide_edges()`, `show_edges()`

## Installation / Setup

Install with pip:

```bash
pip install networkx[default]
```

The `[default]` extra includes optional dependencies (NumPy, SciPy, Matplotlib, etc.). For minimal installation without dependencies:

```bash
pip install networkx
```

For development version:

```bash
git clone https://github.com/networkx/networkx.git
cd networkx
pip install -e .[default]
```

## Usage Examples

### Creating and Manipulating Graphs

```python
import networkx as nx

# Create an empty graph
G = nx.Graph()

# Add nodes individually or in bulk
G.add_node(1)
G.add_nodes_from([2, 3])
G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})])

# Add edges
G.add_edge(1, 2)
G.add_edges_from([(1, 2), (1, 3)])
G.add_edge(1, 2, weight=4.7)
G.add_edges_from([(3, 4), (4, 5)], color="red")

# Examine the graph
list(G.nodes)        # [1, 2, 3, 4, 5]
list(G.edges)        # [(1, 2), (1, 3), (3, 4), (4, 5)]
list(G.adj[1])       # neighbors of node 1: [2, 3]
G.degree[1]          # number of edges incident to 1

# Set attributes
G.graph["day"] = "Friday"
G.nodes[1]["room"] = 714
G.edges[(1, 2)]["weight"] = 10
```

### Directed Graphs

```python
DG = nx.DiGraph()
DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
DG.out_degree(1, weight="weight")   # 0.5
DG.degree(1, weight="weight")       # 1.25 (in + out)
list(DG.successors(1))              # [2]
list(DG.predecessors(1))            # [3]
```

### Multigraphs

```python
MG = nx.MultiGraph()
MG.add_weighted_edges_from([(1, 2, 0.5), (1, 2, 0.75), (2, 3, 0.5)])
dict(MG.degree(weight="weight"))    # {1: 1.25, 2: 1.75, 3: 0.5}
```

### Shortest Path

```python
G = nx.Graph()
G.add_edge("A", "B", weight=4)
G.add_edge("B", "D", weight=2)
G.add_edge("A", "C", weight=3)
G.add_edge("C", "D", weight=4)
nx.shortest_path(G, "A", "D", weight="weight")  # ['A', 'B', 'D']
```

### Graph Generators

```python
# Classic graphs
complete = nx.complete_graph(10)
path = nx.path_graph(20)
cycle = nx.cycle_graph(12)
star = nx.star_graph(10)
petersen = nx.petersen_graph()
lollipop = nx.lollipop_graph(5, 10)

# Random graphs
er = nx.erdos_renyi_graph(100, 0.1)
barabasi = nx.barabasi_albert_graph(100, 3)
watts = nx.watts_strogatz_graph(100, 4, 0.1)

# Lattice/grid
grid = nx.grid_2d_graph(5, 5)
hypercube = nx.hypercube_graph(3)
```

### Graph Operations

```python
# Subgraph
H = G.subgraph([1, 2, 3])

# Union
U = nx.union(G1, G2, rename=("G1_", "G2_"))

# Complement
C = nx.complement(G)

# Convert between types
undirected = nx.to_undirected(DG)
directed = nx.to_directed(G)
```

### Reading and Writing Graphs

```python
# Write to GraphML (readable by Cytoscape, Gephi)
nx.write_graphml(G, "graph.graphml")

# Read edge list from file
G = nx.read_edgelist("edges.txt", delimiter=",")

# JSON node-link format
data = nx.node_link_data(G)
H = nx.node_link_graph(data)
```

### Converting to/from NumPy and Pandas

```python
import numpy as np

# Graph to adjacency matrix
A = nx.to_numpy_array(G)

# Adjacency matrix to graph
DG = nx.from_numpy_array(A, create_using=nx.DiGraph)

# To Pandas DataFrame
adj_df = nx.to_pandas_adjacency(G)
edge_df = nx.to_pandas_edgelist(G)
```

### Graph Views (Read-Only, No Copy)

```python
# Subgraph view — no copy, O(1) creation
view = nx.subgraph_view(G, filter_node=lambda n: n % 2 == 0)

# Hide specific nodes
from networkx.classes.filters import hide_nodes
hidden = nx.subgraph_view(G, filter_node=hide_nodes({1, 2}))
```

## Advanced Topics

**Graph Classes and Views**: Four graph types, graph views, core views, filters → [Graph Classes and Views](reference/01-graph-classes.md)

**Algorithms Reference**: 70+ algorithm modules covering centrality, community detection, shortest paths, flow, isomorphism, and more → [Algorithms Reference](reference/02-algorithms.md)

**Graph Generators**: Classic graphs, random graphs, lattices, expanders, trees, social networks → [Graph Generators](reference/03-generators.md)

**Linear Algebra**: Adjacency, Laplacian, modularity, and Bethe Hessian matrices; spectrum analysis → [Linear Algebra](reference/04-linear-algebra.md)

**Reading, Writing, and Converting**: File formats (GraphML, GEXF, GML, JSON, DOT, edge list), NumPy/SciPy/Pandas conversion → [I/O and Conversion](reference/05-io-conversion.md)

**Backends and Configuration**: Backend dispatch system, nx-parallel, nx-cugraph, nx-arangodb, configuration options → [Backends and Configuration](reference/06-backends-config.md)
