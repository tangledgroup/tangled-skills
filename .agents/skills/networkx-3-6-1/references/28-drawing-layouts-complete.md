# Complete Drawing and Layout Reference

NetworkX provides 46+ layout functions for visualizing graphs, plus drawing primitives and export to LaTeX/TikZ.

## Layout Functions

### Force-Directed Layouts

```python
# Spring layout (Fruchterman-Reingold force-directed)
pos = nx.spring_layout(G, k=None, pos=None, fixed=None, iterations=50,
                       threshold=1e-4, weight="weight", scale=1,
                       center=None, dim=2, seed=None)

# Kamada-Kawai layout (energy-minimizing force-directed)
pos = nx.kamada_kawai_layout(G, dist=None, weight="weight", scale=1,
                             center=None, dim=2, seed=None)

# ARF (Adaptive Repulsion/Force) layout
pos = nx.arf_layout(G, seed=None, iterations=100, threshold=1e-4,
                    scale=1, center=None, dim=2)

# ForceAtlas2 layout (Gephi's algorithm, great for large social networks)
pos = nx.forceatlas2_layout(G, weights=True, iterations=100,
                            linearize_em=True, scaling_ratio=2.0,
                            strong_gravity=True, gravity=1.0,
                            outbound_attraction_distribution=False,
                            linlog_mode=False, edge_length=None,
                            node_size=None, split_force=0.0,
                            jitter_taper=0, repulsion_threshold=10)
```

### Structural Layouts

```python
# Circular layout (nodes on a circle)
pos = nx.circular_layout(G)

# Spectral layout (eigenvector-based positioning)
pos = nx.spectral_layout(G, weight="weight", scale=1,
                         center=None, dim=2)

# Planar layout (for planar graphs only, guaranteed no crossings)
is_planar, emb = nx.check_planarity(G)
if is_planar:
    pos = nx.planar_layout(G, embedding=emb)

# Shell layout (nodes in concentric rings)
nlist = [[1, 2], [3, 4, 5], [6]]
pos = nx.shell_layout(G, nlist=nlist, scale=1, center=None, dim=2)

# BFS layout (tree-like, follows BFS ordering from root)
pos = nx.bfs_layout(G, source=0, reverse=False, orientation='left',
                    scale=1, center=None, dim=2)

# Multipartite layout (nodes partitioned into sets, drawn as columns)
subset = [[1, 2], [3, 4], [5, 6]]
pos = nx.multipartite_layout(G, subset=subset, scale=1,
                             vertical_alignment='center')

# Random layout
pos = nx.random_layout(G, scale=1, center=None, dim=2, seed=None)

# Spiral layout (nodes arranged in a spiral)
pos = nx.spiral_layout(G, edge_pos=None, scale=1, center=None,
                       primary_rad=0.01, secondary_rad=0.01)
```

### Bipartite Layout

```python
from networkx.drawing import bipartite_layout

top_nodes = {n for n, d in G.nodes(data=True) if d.get('bipartite') == 0}
pos = nx.bipartite_layout(G, top_nodes, scale=1,
                          vertical_alignment='center',
                          horizontal_alignment='left')
```

### Layout Utilities

```python
# Rescale layout positions to specific range
pos_rescaled = nx.rescale_layout(pos, scale=(0, 1))

# Rescale layout dict (preserves node labels as keys)
pos_dict = nx.rescale_layout_dict(pos, scale=(0, 1))
```

## Drawing Primitives

### Core Drawing Functions

```python
import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
pos = nx.spring_layout(G, seed=42)

# Draw the whole graph at once
nx.draw(G, pos, with_labels=True, node_color="lightblue",
        edge_color="gray", node_size=500, font_size=12)

# Fine-grained drawing (draw each component separately for more control)
nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue",
                       alpha=0.8, linewidths=1, edgecolors="black")
nx.draw_networkx_edges(G, pos, width=2.0, edge_color="gray",
                       style="solid", arrowstyle="-|>", arrowsize=15)
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif",
                        font_weight="bold", alpha=0.9)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(1, 2): "weight=3"},
                             font_size=8, rotate=False)

plt.axis("off")
plt.show()
```

### Edge Drawing Options

```python
# Draw edges with different styles
nx.draw_networkx_edges(G, pos, edgelist=[(1, 2)], width=3,
                       edge_color="red", style="dashed",
                       connectionstyle="arc3,rad=0.1")

# Directed graph arrows
DG = nx.DiGraph([(1, 2), (2, 3)])
nx.draw_networkx_edges(DG, pos, arrowstyle="->",
                       arrowsize=20, edgecolors="black")

# Edge labels with custom positioning
edge_labels = {(1, 2): "A→B", (2, 3): "B→C"}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                             label_pos=0.5, font_size=9)
```

### Node Drawing Options

```python
# Different node shapes
nx.draw_networkx_nodes(G, pos, node_shape="o",  # circle (default)
                       node_shape="s",  # square
                       node_shape="^",  # triangle
                       node_shape="*",  # star
                       node_shape="p",  # pentagon
                       node_shape="D",  # diamond
                       node_shape="d")  # thin diamond

# Gradient coloring based on degree
degrees = dict(G.degree())
nx.draw_networkx_nodes(G, pos, node_color=list(degrees.values()),
                       cmap=plt.cm.viridis, alpha=0.8)
plt.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.viridis),
             label="Degree")
```

## LaTeX/TikZ Export

```python
# Generate LaTeX/TikZ code for the graph
latex_code = nx.to_latex(G, root_node=None, edge_label_func=None,
                         preamble=r'\usepackage{tikz}',
                         position_func=lambda n: (0, 0))

# Write to file
nx.write_latex(G, 'graph.tex')

# With custom node positioning
pos = nx.spring_layout(G)
latex_code = nx.to_latex(
    G,
    root_node=None,
    edge_label_func=lambda e: str(e[2].get('weight', '')),
    position_func=lambda n: pos[n],  # Use computed positions
    preamble=r'\usepackage{tikz}'
)

with open('graph.tex', 'w') as f:
    f.write(latex_code)
```

## Graphviz Integration

```python
# Using pygraphviz (preferred, full Graphviz support)
try:
    import pygraphviz as pgv
    
    A = nx.nx_agraph.to_agraph(G)
    A.layout(prog="dot")  # dot, neato, twopi, circo, fdp, sfdp
    A.draw("graph.png")
    
    # Read back
    A2 = pgv.AGraph("graph.dot")
    H = nx.nx_agraph.from_agraph(A2)
    
except ImportError:
    print("pygraphviz not installed")

# Using pydot (lighter dependency)
try:
    import pydot
    
    P = nx.nx_pydot.to_pydot(G)
    P.write_dot("graph.dot")
    
    # Read back
    P2 = pydot.graph_from_dot_file("graph.dot")[0]
    H = nx.nx_pydot.from_pydot(P2)
    
except ImportError:
    print("pydot not installed")
```

## Layout Function Reference

| Function | Description | Best For |
|----------|-------------|----------|
| `spring_layout(G, k=None, ...)` | Force-directed (Fruchterman-Reingold) | General purpose, default |
| `circular_layout(G)` | Nodes on circle | Cyclic structure |
| `planar_layout(G, embedding)` | Planar embedding | Planar graphs only |
| `spectral_layout(G, weight=None)` | Eigenvector-based | Clusters, spectral properties |
| `random_layout(G, scale=1, seed=None)` | Random placement | Baseline, animation |
| `shell_layout(G, nlist=None, ...)` | Concentric rings | Layered structure |
| `kamada_kawai_layout(G, dist=None)` | Energy-minimizing | Small graphs, clarity |
| `bfs_layout(G, source, reverse=False)` | BFS tree ordering | Tree-like graphs |
| `multipartite_layout(G, subset, ...)` | Nodes in partitions | Bipartite/layered graphs |
| `arf_layout(G, seed=None)` | Adaptive Repulsion/Force | Large graphs |
| `spiral_layout(G, edge_pos, ...)` | Spiral arrangement | Visual variety |
| `forceatlas2_layout(G, ...)` | ForceAtlas2 (Gephi's algorithm) | Large social networks |
| `rescale_layout(pos, scale)` | Normalize position dict | Consistent scaling |
| `rescale_layout_dict(pos, scale)` | Dict version of rescale | Preserves node labels |
| `bipartite_layout(G, top_nodes, ...)` | Bipartite-specific layout | Bipartite graphs |

## Drawing Function Reference

| Function | Description |
|----------|-------------|
| `draw(G, pos, ...)` | Full graph drawing |
| `draw_networkx_nodes(G, pos, ...)` | Draw nodes only |
| `draw_networkx_edges(G, pos, ...)` | Draw edges only |
| `draw_networkx_labels(G, pos, ...)` | Draw node labels |
| `draw_networkx_edge_labels(G, pos, ...)` | Draw edge labels |
| `to_latex(G, ...)` | Generate LaTeX/TikZ code |
| `write_latex(G, path, ...)` | Write LaTeX file |
| `nx_agraph.to_agraph(G)` | Convert to PyGraphviz AGraph |
| `nx_agraph.from_agraph(A)` | Convert from AGraph |
| `nx_pydot.to_pydot(G)` | Convert to PyDot graph |
| `nx_pydot.from_pydot(P)` | Convert from PyDot |
