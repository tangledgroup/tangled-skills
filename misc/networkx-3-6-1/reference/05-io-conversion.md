# I/O and Conversion

## File Formats

NetworkX supports reading and writing graphs in many formats.

### GraphML

XML-based format with full attribute support, readable by Cytoscape and Gephi:

```python
nx.write_graphml(G, "graph.graphml")
G = nx.read_graphml("graph.graphml")
```

### GEXF

Graph Exchange XML Format, used by Gephi:

```python
nx.write_gexf(G, "graph.gexf")
G = nx.read_gexf("graph.gexf")
```

### GML

Graph Description Language, used by many tools:

```python
nx.write_gml(G, "graph.gml")
G = nx.read_gml("graph.gml")
```

### DOT (Graphviz)

Requires pygraphviz or pydot:

```python
# Using pygraphviz
A = nx.nx_agraph.to_agraph(G)
A.draw("graph.png", prog="dot")

# Or write DOT format
nx.write_dot(G, "graph.dot")
G = nx.read_dot("graph.dot")
```

### Edge List

Simple text format, one edge per line:

```python
nx.write_edgelist(G, "edges.txt", delimiter=",")
G = nx.read_edgelist("edges.txt", delimiter=",")
G = nx.read_weighted_edgelist("edges.txt", delimiter=",")
```

### Adjacency List

```python
nx.write_adjlist(G, "adj.txt")
G = nx.read_adjlist("adj.txt")
```

### JSON

Node-link format for web applications:

```python
data = nx.node_link_data(G)
H = nx.node_link_graph(data)

# Cytoscape format
cyto = nx.cytoscape_data(G)
H = nx.cytoscape_graph(cyto)
```

### Other Formats

- **Pajek**: `nx.read_pajek()`, `nx.write_pajek()`
- **Matrix Market**: `nx.read_matrix_market()`, `nx.write_matrix_market()`
- **LEDA**: `nx.read_leda()`
- **Graph6/Sparse6**: compact binary encoding for small graphs
- **Network Text**: simple text format

## Drawing and Visualization

NetworkX provides basic visualization. For production-quality visualizations, export to dedicated tools (Cytoscape, Gephi, Graphviz).

### Matplotlib

```python
import matplotlib.pyplot as plt

G = nx.complete_graph(5)
nx.draw(G)
plt.show()

# With layout and styling
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_color="red", node_size=500)
nx.draw_networkx_edges(G, pos, edge_color="blue")
nx.draw_networkx_labels(G, pos)
plt.show()
```

### Layout Functions

Layout functions compute node positions for visualization:

```python
pos = nx.spring_layout(G)          # force-directed
pos = nx.circular_layout(G)        # circular arrangement
pos = nx.planar_layout(G)          # planar embedding
pos = nx.random_layout(G)          # random positions
pos = nx.spectral_layout(G)        # spectral 2D
pos = nx.kamada_kawai_layout(G)    # Kamada-Kawai force-directed
pos = nx.shell_layout(G, nlist)    # shell arrangement
pos = nx.bipartite_layout(G, nodes) # bipartite layout
```

### Convenience Drawing Functions

```python
nx.draw(G)                        # draw with spring layout
nx.draw_circular(G)
nx.draw_kamada_kawai(G)
nx.draw_planar(G)
nx.draw_random(G)
nx.draw_spectral(G)
nx.draw_spring(G)
nx.draw_shell(G, nlist=[[1,2],[3,4]])
nx.draw_bipartite(G, nodes=top_nodes)
```

### Graphviz Integration

```python
# Using pygraphviz (AGraph)
A = nx.nx_agraph.to_agraph(G)
A.layout("dot")
A.draw("output.png")

# Using pydot
P = nx.nx_pydot.to_pydot(G)
P.write_png("output.png")
```

## Relabeling Nodes

Rename nodes while preserving structure:

```python
# Using a mapping dictionary
mapping = {old: new for old, new in zip(G.nodes(), range(G.number_of_nodes()))}
G_relabelled = nx.relabel_nodes(G, mapping)

# Using a function
G_relabelled = nx.relabel_nodes(G, lambda n: f"node_{n}")
```

## Exceptions

NetworkX defines specific exception types for error handling:

- `NetworkXError` — base exception
- `NetworkXPointlessConcept` — operation makes no sense
- `NetworkXAlgorithmError` — algorithm failed (e.g., no path exists)
- `NetworkXUnfeasible` — problem has no solution
- `NetworkXNoPath` — no path between nodes
- `NetworkXNoCycle` — no cycle found
- `NodeNotFound` — node does not exist in graph
- `HasACycle` — graph has a cycle (when it shouldn't)
- `NetworkXUnbounded` — unbounded solution
- `NetworkXNotImplemented` — feature not implemented
- `AmbiguousSolution` — multiple valid solutions
- `ExceededMaxIterations` — iteration limit reached
- `PowerIterationFailedConvergence` — power iteration did not converge
