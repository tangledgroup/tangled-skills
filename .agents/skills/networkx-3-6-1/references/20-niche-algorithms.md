# Niche Algorithms: Configuration, Randomness, and File Formats

NetworkX provides configuration utilities, random number generation helpers, and additional file format support.

# Niche Algorithms: Configuration, Randomness, File Formats, and Graph Theory

NetworkX provides configuration utilities, random number generation helpers, additional file formats, and specialized graph theory algorithms.

## Broadcast Trees (Tree Broadcasting)

Measures broadcast time and center in trees.

```python
import networkx as nx

T = nx.balanced_tree(2, 3)  # Binary tree of depth 3

# Find the broadcast center (node that minimizes max distance to all others)
broadcast_center = nx.tree_broadcast_center(T)
print(broadcast_center)  # Root node for balanced tree

# Broadcast time (minimum time to reach all nodes from center)
broadcast_time = nx.tree_broadcast_time(T)
print(broadcast_time)  # Height of the tree
```

## Perfect Graphs

A perfect graph has the property that the chromatic number of every induced subgraph equals the size of its largest clique.

```python
import networkx as nx

# Complete graphs are perfect
G = nx.complete_graph(5)
is_perfect = nx.is_perfect_graph(G)
print(is_perfect)  # True

# Bipartite graphs are perfect
BG = nx.complete_bipartite_graph(3, 4)
print(nx.is_perfect_graph(BG))  # True

# Odd cycles of length >= 5 are NOT perfect
odd_cycle = nx.cycle_graph(5)
print(nx.is_perfect_graph(odd_cycle))  # False

# Perfect graphs include:
# - Comparability graphs
# - Interval graphs
# - Chordal graphs (complement of chordal)
# - Bipartite graphs
```

## Planar Drawing (Combinatorial Embeddings)

Planar embedding represents a planar graph's cyclic order of edges around each vertex.

```python
import networkx as nx
from networkx.algorithms import planarity

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])

# Check planarity and get embedding
is_planar, embedding = nx.check_planarity(G)
print(is_planar)  # True

if is_planar:
    # PlanarEmbedding stores the cyclic order of edges around each vertex
    print(type(embedding))  # PlanarEmbedding
    
    # Get edges around each vertex in cyclic order
    for node in embedding.nodes():
        neighbors = list(embedding.neighbors(node))
        print(f"{node}: {neighbors}")
    
    # Convert combinatorial embedding to 2D positions
    pos = nx.combinatorial_embedding_to_pos(embedding)
    print(pos)  # Dict: node -> (x, y)
    
    # Draw with planar embedding
    import matplotlib.pyplot as plt
    nx.draw(G, pos=pos, with_labels=True)
    plt.show()
```

## NetworkX Configuration

Configure backend priorities, drawing settings, and algorithm parameters.

Configure backend priorities, drawing settings, and algorithm parameters.

```python
import networkx as nx

# Backend priority configuration
nx.config.backend_priority.algos = ["cugraph", "parallel"]
nx.config.backend_priority.generators = ["cugraph"]
nx.config.backend_priority.classes = ["cugraph"]

# Fallback behavior
nx.config.fallback_to_nx = True  # Fall back to pure NetworkX

# Caching
nx.config.cache_converted_graphs = True

# Drawing configuration
nx.config.drawing.element_limit = 10000  # Max elements for drawing
nx.config.drawing.np_float_weighted = True

# Check current configuration
print(nx.config.backend_priority.algos)
print(nx.config.fallback_to_nx)

# Use NetworkXConfig class for programmatic config
from networkx.utils.backends import _dispatchable
config = nx.utils.NetworkXConfig()

# Environment variable overrides
# Set before importing:
# NETWORKX_BACKEND_PRIORITY_ALGOS=cugraph,parallel
# NETWORKX_FALLBACK_TO_NX=True
```

## Randomness and Random Graph Generation

```python
import networkx as nx
from networkx import utils

# Generate random permutations
perm = nx.utils.random_permutation(10)
print(perm)  # e.g., [3, 7, 1, 9, 0, 5, 2, 8, 4, 6]

# Random element from sequence
elem = nx.utils.arbitrary_element([1, 2, 3, 4, 5])
print(elem)  # Random choice

# Random k elements without replacement
sample = nx.utils.random_sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], k=3)
print(sample)  # e.g., [4, 7, 2]

# Random power-law sequence
seq = nx.utils.powerlaw_sequence(100, exponent=2.5)
print(seq[:10])

# Reservoir sampling (for streaming data)
reservoir = nx.utils.reservoir(iterable=range(1000), size=10)
print(reservoir)

# Random node selection from graph
node = nx.utils.random_node(G, weight=None)

# Random edge selection
edge = nx.utils.random_edge(G, weight=None)
```

## Sparse6 / Graph6 Formats

Compact binary/text formats for storing graphs.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(0, 1), (1, 2), (2, 3)])

# Write/read Graph6 format (compact text)
nx.write_graph6(G, "graph.g6")
G_read = nx.read_graph6("graph.g6")

# Write/read Sparse6 format (even more compact for large graphs)
nx.write_sparse6(G, "graph.s6")
G_read = nx.read_sparse6("graph.s6")

# Parse from string
from_string = nx.parse_graph6(">>Graph6<<")
from_sparse = nx.parse_sparse6(">>Sparse6<<")

# Graph6 example: "I>" = K4 (complete graph on 4 nodes)
# Sparse6 example: "&B" = single edge

# These formats are used by:
# - Brendan McKay's graph generation tools
# - Nauty/traces package
# - Graph databases
# - Benchmark suites (SNAP, LBL)
```

## Text / Graphviz Text Export

Export graphs as human-readable text or Graphviz DOT text.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3)])

# Write graph as simple text format
nx.write_network_text(G, "graph.txt")
# Output:
# 1 2
# 2 3

# Read from text
G_read = nx.read_network_text("graph.txt")

# Text export with attributes
with open("graph_with_attrs.txt", "w") as f:
    nx.write_network_text(G, f, data={"weight": "default"})

# Graphviz DOT text (for rendering with Graphviz)
dot_text = nx.nx_agraph.to_agraph(G).to_string()
print(dot_text)

# Or via pydot
import pydot
P = nx.nx_pydot.to_pydot(G)
dot_text = P.to_string()
```

## Non-Randomness Measure

Quantifies structural deviation from random graphs.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Non-randomness measure
nr = nx.non_randomness(G)
print(nr)  # Higher = more structured, lower = random-like
```

## Isolate Functions Reference

| Function | Description |
|----------|-------------|
| `isolates(G)` | List of nodes with no edges |
| `number_of_isolates(G)` | Count isolated nodes |
| `is_isolate(G, n)` | Check if single node is isolated |

## Configuration / Backend Dispatch Reference

| Function/Config | Description |
|-----------------|-------------|
| `nx.config.backend_priority.algos` | Priority list for algorithm backends |
| `nx.config.backend_priority.generators` | Priority for generator backends |
| `nx.config.backend_priority.classes` | Priority for class backends |
| `nx.config.fallback_to_nx` | Fall back to pure NetworkX |
| `nx.config.cache_converted_graphs` | Cache graph conversions |
| `nx.utils.decorators.argmap` | Function argument mapping decorator |
| `nx.utils.decorators.nodes_or_number` | Accept node count or node list |
| `nx.utils.decorators.not_implemented_for` | Skip for certain graph types |
| `nx.utils.decorators.np_random_state` | NumPy random state handling |
| `nx.utils.decorators.py_random_state` | Python random state handling |
| `nx.utils.decorators.open_file` | Auto-open file path arguments |

## Complete Randomness Reference

| Function | Description |
|----------|-------------|
| `random_permutation(n)` | Permutation of 0..n-1 |
| `arbitrary_element(seq)` | Random element from sequence |
| `random_sample(population, k)` | k elements without replacement |
| `powerlaw_sequence(n, exponent=2.0)` | Power-law distributed values |
| `reservoir(iterable, size, seed=None)` | Reservoir sampling for streams |

## Complete Graph6/Sparse6 Reference

| Function | Description |
|----------|-------------|
| `write_graph6(G, path, delimiter='\n')` | Write Graph6 format |
| `read_graph6(path, create_using=None)` | Read Graph6 format |
| `write_sparse6(G, path, delimiter='\n')` | Write Sparse6 format |
| `read_sparse6(path, create_using=None)` | Read Sparse6 format |
| `parse_graph6(string)` | Parse Graph6 from string |
| `parse_sparse6(string)` | Parse Sparse6 from string |

## Summary

| Module | Function | Description |
|--------|----------|-------------|
| **Config** | `nx.config.backend_priority` | Backend selection priority |
| | `nx.config.fallback_to_nx` | Enable/disable fallback |
| | `nx.config.cache_converted_graphs` | Graph conversion caching |
| | `nx.config.drawing.element_limit` | Max elements for drawing |
| **Randomness** | `nx.utils.random_permutation()` | Random permutation of 0..n-1 |
| | `nx.utils.arbitrary_element()` | Random element from sequence |
| | `nx.utils.random_sample()` | Random k elements without replacement |
| | `nx.utils.powerlaw_sequence()` | Power-law distributed values |
| | `nx.utils.reservoir()` | Reservoir sampling for streams |
| **Broadcast** | `nx.tree_broadcast_center()` | Minimize max distance in tree |
| | `nx.tree_broadcast_time()` | Minimum broadcast time |
| **Perfect graphs** | `nx.is_perfect_graph()` | Test perfect graph property |
| **Planar drawing** | `nx.check_planarity()` | Planarity test + embedding |
| | `nx.combinatorial_embedding_to_pos()` | Embedding → 2D positions |
| | `planarity.PlanarEmbedding` | Cyclic edge order storage |
| **Graph6** | `nx.write_graph6()` / `read_graph6()` | Compact graph text format |
| | `nx.write_sparse6()` / `read_sparse6()` | Ultra-compact sparse format |
| | `nx.parse_graph6()` / `parse_sparse6()` | Parse from string |
| **Text** | `nx.write_network_text()` | Simple edge-list text export |
| | `nx.read_network_text()` | Read text edge list |
| **Isolates** | `nx.isolates()` | Nodes with no edges |
| | `nx.number_of_isolates()` | Count isolated nodes |
| | `nx.is_isolate(G, n)` | Check single node |
| **Non-randomness** | `nx.non_randomness()` | Structure vs randomness measure |
| **DOT** | `nx.nx_agraph.to_agraph()` | Convert to Graphviz AGraph |
| | `nx.nx_pydot.to_pydot()` | Convert to PyDot graph |
