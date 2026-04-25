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
  - https://networkx.org/documentation/stable/reference/index.html
  - http://conference.scipy.org.s3-website-us-east-1.amazonaws.com/proceedings/scipy2008/paper_2/full_text.pdf
  - https://discord.com/invite/vur45CbwMz
  - https://github.com/networkx/networkx
  - https://github.com/networkx/networkx/discussions
  - https://groups.google.com/forum/#!forum/networkx-discuss
  - https://networkx.org/documentation/stable/
  - https://networkx.org/documentation/stable/reference/
  - https://networkx.org/documentation/stable/tutorial.html
  - https://github.com/networkx/networkx/tree/networkx-3.6.1
  - https://networkx.org/en/
---
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
- **Implementing network algorithms** - Shortest paths, centrality measures, community detection, flow optimization, DAG scheduling, matching, isomorphism
- **Generating test networks** - Random graphs (Erdős-Rényi, Barabási-Albert), classic graphs (Petersen, grid), geometric graphs, social models
- **Analyzing network structure** - Connectivity, clustering, k-core decomposition, cycles, bridges, articulation points, planarity
- **Working with graph data** - Import/export in 15+ formats (GraphML, GEXF, GML, JSON, edge lists, adjacency matrices, Pajek, LEDA, DOT, Matrix Market)
- **Converting between representations** - Graph ↔ numpy arrays, scipy sparse matrices, pandas DataFrames, dict of dicts/lists
- **Visualizing networks** - Layout algorithms (15+), matplotlib integration, Graphviz, LaTeX/TikZ export, iplotx
- **Graph manipulation** - Union, intersection, difference, composition, graph products, relabeling, freezing, subgraph views
- **Optimization** - Max flow/min-cut, min-cost flow, maximum matching, graph coloring, minimum vertex cover
- **Research and education** - Prototyping graph algorithms, teaching graph theory concepts, spectral graph analysis

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

## Installation / Setup
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

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Shortest Paths](reference/02-shortest-paths.md)
- [Centrality](reference/03-centrality.md)
- [Community Detection](reference/04-community-detection.md)
- [Visualization](reference/05-visualization.md)
- [File Formats](reference/06-file-formats.md)
- [Generators](reference/07-generators.md)
- [Backends](reference/08-backends.md)
- [Graph Operations](reference/09-graph-operations.md)
- [Dag And Flow](reference/10-dag-and-flow.md)
- [Connectivity Components](reference/11-connectivity-components.md)
- [Clustering Core Cycles](reference/12-clustering-core-cycles.md)
- [Isomorphism Matching Coloring](reference/13-isomorphism-matching-coloring.md)
- [Linalg Conversion](reference/14-linalg-conversion.md)
- [Traversal And Trees](reference/15-traversal-and-trees.md)
- [Link Prediction And Analysis](reference/16-link-prediction-and-analysis.md)
- [Specialized Algorithms](reference/17-specialized-algorithms.md)
- [Specialized Algorithms 2](reference/18-specialized-algorithms-2.md)
- [Specialized Algorithms 3](reference/19-specialized-algorithms-3.md)
- [Niche Algorithms](reference/20-niche-algorithms.md)
- [Graphical And Sequence](reference/21-graphical-and-sequence.md)
- [Bipartite Networks](reference/22-bipartite-networks.md)
- [Planarity And Embeddings](reference/23-planarity-and-embeddings.md)
- [Graph Polynomials And Perfect](reference/24-graph-polynomials-and-perfect.md)
- [Approximation Algorithms](reference/25-approximation-algorithms.md)
- [Similarity And Edit Distance](reference/26-similarity-and-edit-distance.md)
- [Utils Randomness Config](reference/27-utils-randomness-config.md)
- [Drawing Layouts Complete](reference/28-drawing-layouts-complete.md)
- [Exceptions And Concepts](reference/29-exceptions-and-concepts.md)
- [Usage Examples](reference/30-usage-examples.md)
- [Algorithm Complexity Reference](reference/31-algorithm-complexity-reference.md)
- [Complete Reference Index](reference/32-complete-reference-index.md)

