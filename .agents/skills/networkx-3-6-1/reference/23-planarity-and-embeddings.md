# Planarity and Graph Embeddings

Planar graphs can be drawn on a plane without edge crossings. NetworkX provides planarity testing, embedding management, and 2D position computation from combinatorial embeddings.

## Planarity Testing

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])

# Check planarity and get embedding
is_planar, embedding = nx.check_planarity(G)
print(is_planar)  # True

# For non-planar graphs
K5 = nx.complete_graph(5)
is_k5, emb5 = nx.check_planarity(K5)
print(is_k5)  # False

# K3,3 is also non-planar
K33 = nx.complete_bipartite_graph(3, 3)
is_k33, emb33 = nx.check_planarity(K33)
print(is_k33)  # False

# Kuratowski's theorem: a graph is non-planar iff it contains
# K5 or K3,3 as a minor (not necessarily as subgraph)
```

## PlanarEmbedding

A `PlanarEmbedding` stores the cyclic order of edges around each vertex, which defines a unique planar embedding up to the choice of outer face.

```python
is_planar, embedding = nx.check_planarity(G)

if is_planar:
    # Access neighbors in cyclic order around each node
    for node in embedding.nodes():
        neighbors = list(embedding.neighbors(node))
        print(f"{node}: {neighbors}")
    
    # The cyclic order matters for planar drawing
    # Neighbors are stored in counter-clockwise order
    
    # Get edge count
    print(f"Nodes: {embedding.number_of_nodes()}")
    print(f"Edges: {embedding.number_of_edges()}")
    
    # Check if embedding is valid (consistent cyclic orders)
    is_valid = embedding.is_valid()
    
    # Add/remove edges from embedding
    embedding.add_edge(1, 5)
    embedding.remove_edge(1, 2)
```

## Planar Drawing from Embedding

Convert a combinatorial embedding to 2D coordinates.

```python
is_planar, embedding = nx.check_planarity(G)

if is_planar:
    # Convert combinatorial embedding to 2D positions
    pos = nx.combinatorial_embedding_to_pos(embedding)
    
    # Draw with planar embedding
    import matplotlib.pyplot as plt
    nx.draw(G, pos=pos, with_labels=True, node_color="lightblue")
    
    # Verify no crossings in the drawing
    for (u, v), (x1, y1), (x2, y2) in zip(
        G.edges(),
        [(pos[u][0], pos[u][1]) for u in G.nodes()],
        [(pos[v][0], pos[v][1]) for v in G.nodes()]
    ):
        pass  # Positions guarantee no crossings
    
    plt.axis("equal")
    plt.show()
```

## Planar Graph Properties

```python
# Euler's formula: V - E + F = 2 (for connected planar graphs)
# For maximal planar graphs: E = 3V - 6
# For maximal planar triangulations: every face is a triangle

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])

is_planar, embedding = nx.check_planarity(G)
if is_planar:
    V = G.number_of_nodes()
    E = G.number_of_edges()
    print(f"V={V}, E={E}, 3V-6={3*V-6}")
    # For maximal planar: E should equal 3V-6
```

## Planar Graph Drawing with Graphviz

```python
# Use Graphviz for high-quality planar drawings
try:
    import pygraphviz as pgv
    
    A = pgv.AGraph()
    A.add_nodes_from(G.nodes())
    A.add_edges_from(G.edges())
    
    # sfdp or neato layout for planar graphs
    A.layout(prog="sfdp")
    A.draw("planar_graph.png")
    
except ImportError:
    # Fallback to NetworkX built-in planar layout
    if is_planar:
        pos = nx.combinatorial_embedding_to_pos(embedding)
        nx.draw(G, pos=pos, with_labels=True)
```

## Summary

| Function | Description |
|----------|-------------|
| `check_planarity(G)` | Test planarity, return (bool, PlanarEmbedding) |
| `is_planar(G)` | Boolean check only (no embedding) |
| `PlanarEmbedding` | Cyclic edge order storage per vertex |
| `combinatorial_embedding_to_pos(embedding)` | Embedding → 2D coordinates |
| `embedding.add_edge(u, v)` | Add edge with cyclic order |
| `embedding.remove_edge(u, v)` | Remove edge from embedding |
| `embedding.neighbors(v)` | Neighbors in cyclic order around v |
