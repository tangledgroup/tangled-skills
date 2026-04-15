# Visualization

NetworkX provides basic graph visualization capabilities through matplotlib and Graphviz integration. For advanced visualization, consider dedicated tools like Cytoscape, Gephi, or iplotx.

## Matplotlib Drawing

### Basic Drawing

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.karate_club_graph()

# Simplest drawing (auto-layout)
nx.draw(G)
plt.show()

# With labels
nx.draw(G, with_labels=True)
plt.show()

# Save to file
nx.draw(G)
plt.savefig("graph.png", dpi=300, bbox_inches='tight')
```

### Layout Algorithms

Layout determines node positions. Different layouts reveal different structural properties.

```python
# Spring layout (force-directed, default)
pos = nx.spring_layout(G)
# With parameters
pos = nx.spring_layout(G, k=0.2, iterations=50, seed=42)

# Circular layout
pos = nx.circular_layout(G)

# Planar layout (for planar graphs only)
if nx.check_planarity(G)[0]:
    pos = nx.planar_layout(G)

# Spectral layout (eigenvector-based)
pos = nx.spectral_layout(G)

# Random layout
pos = nx.random_layout(G, seed=42)

# Shell layout (nodes in concentric shells)
n1 = [node for i, node in enumerate(G.nodes()) if i % 2 == 0]
n2 = [node for i, node in enumerate(G.nodes()) if i % 2 == 1]
pos = nx.shell_layout(G, nlist=[n1, n2])

# Kamada-Kawai layout (force-directed, different energy function)
pos = nx.kamada_kawai_layout(G)

# Bipartite layout (for bipartite graphs)
top = [node for node, attr in G.nodes(data=True) if attr.get('bipartite') == 0]
bottom = [node for node, attr in G.nodes(data=True) if attr.get('bipartite') == 1]
pos = nx.bipartite_layout(G, top)

# BFS layout (tree-like from root)
pos = nx.bfs_layout(G, root="node1", orientation='top')

# Spiral layout
pos = nx.spiral_layout(G)

# ARF layout (for hierarchical graphs)
pos = nx.arf_layout(G)

# ForceAtlas2 layout (for large networks)
pos = nx.forceatlas2_layout(G)
```

### Drawing Components Separately

Fine-grained control over visualization elements:

```python
pos = nx.spring_layout(G, seed=42)

# Draw nodes with custom styling
nodes = nx.draw_networkx_nodes(
    G, pos,
    node_size=500,
    node_color='lightblue',
    node_shape='o',  # 'o' circle, 's' square, '^' triangle, 'D' diamond
    alpha=0.8,
    edgecolors='black',
    linewidths=1.0
)

# Draw edges with custom styling
edges = nx.draw_networkx_edges(
    G, pos,
    edge_color='gray',
    width=2.0,
    alpha=0.5,
    style='--',  # '-', '--', '-.', ':'
    arrows=True,  # For directed graphs
    arrowstyle='-|>',  # '-|>', '<|-', '-O', '<O', '->', '<-'
    arrowsize=20
)

# Draw node labels
labels = nx.draw_networkx_labels(
    G, pos,
    font_size=10,
    font_color='black',
    font_weight='bold',
    font_family='sans-serif'
)

# Draw edge labels (weights, etc.)
edge_labels = {(u, v): d.get('weight', 1) for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=edge_labels,
    font_size=8,
    font_color='red',
    label_pos=0.5  # Position along edge (0 to 1)
)

plt.axis('off')
plt.title("Karate Club Network")
plt.show()
```

### Node Color Mapping

```python
# Color by degree
degrees = dict(G.degree())
max_degree = max(degrees.values())
node_colors = [degrees[n] / max_degree for n in G.nodes()]
nx.draw(G, node_color=node_colors, cmap='viridis')

# Color by community membership
from networkx.algorithms import community
communities = list(community.louvain_communities(G))
node_to_community = {}
for i, comm in enumerate(communities):
    for node in comm:
        node_to_community[node] = i
node_colors = [node_to_community[n] for n in G.nodes()]
nx.draw(G, node_color=node_colors, cmap='Set3')

# Color by centrality
centrality = nx.degree_centrality(G)
max_centrality = max(centrality.values())
node_colors = [centrality[n] / max_centrality for n in G.nodes()]
nx.draw(G, node_color=node_colors, cmap='Reds')

# Color by node attribute
if G.nodes.data():
    colors = [G.nodes[n].get('attribute', 0) for n in G.nodes()]
    nx.draw(G, node_color=colors, cmap='coolwarm')

# Custom color list
node_colors = ['red' if G.degree(n) > 5 else 'blue' for n in G.nodes()]
nx.draw(G, node_color=node_colors)
```

### Node Size Mapping

```python
# Scale by degree
degrees = dict(G.degree())
min_degree = min(degrees.values())
max_degree = max(degrees.values())
node_sizes = [100 + 500 * (d - min_degree) / (max_degree - min_degree) 
              for n, d in degrees.items()]
nx.draw(G, node_size=node_sizes)

# Scale by centrality
centrality = nx.betweenness_centrality(G)
max_centrality = max(centrality.values())
node_sizes = [100 + 1000 * c / max_centrality for n, c in centrality.items()]
nx.draw(G, node_size=node_sizes)
```

### Edge Styling

```python
# Vary edge width by weight
edge_widths = [d.get('weight', 1) for u, v, d in G.edges(data=True)]
nx.draw(G, width=edge_widths)

# Color edges by weight
edge_colors = [d.get('weight', 1) for u, v, d in G.edges(data=True)]
nx.draw(G, edge_color=edge_colors, edge_cmap='viridis')

# Draw only certain edges
edges_to_draw = [(u, v) for u, v, d in G.edges(data=True) if d.get('weight', 1) > 0.5]
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos, edgelist=edges_to_draw)

# Directed graph with arrows
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1)])
pos = nx.circular_layout(DG)
nx.draw(DG, pos, arrows=True, arrowstyle='-|>', arrowsize=20)
```

### Colormaps

```python
# Sequential colormaps (for single variable)
cmaps_sequential = ['viridis', 'plasma', 'inferno', 'magma', 
                    'Blues', 'Reds', 'Greens', 'Oranges']

# Diverging colormaps (for positive/negative values)
cmaps_diverging = ['RdBu', 'coolwarm', 'PiYG', 'PRGn', 'BrBG']

# Qualitative colormaps (for categorical data)
cmaps_qualitative = ['Set1', 'Set2', 'Set3', 'Paired', 'Pastel1', 'tab10']

# Use colormap
nx.draw(G, node_color=node_values, cmap='viridis')

# Add colorbar
import matplotlib.cm as cm
from matplotlib import colors

norm = colors.Normalize(vmin=min(node_values), vmax=max(node_values))
sm = cm.ScalarMappable(cmap='viridis', norm=norm)
sm.set_array([])
plt.colorbar(sm, label='Value')
```

## Specialized Drawing Functions

```python
# Draw with specific layouts (convenience functions)
nx.draw_circular(G)
nx.draw_kamada_kawai(G)
nx.draw_planar(G)  # Raises error if not planar
nx.draw_random(G)
nx.draw_spectral(G)
nx.draw_spring(G)
nx.draw_shell(G)

# Bipartite graph drawing
G = nx.complete_bipartite_graph(3, 4)
top = list(range(3))
nx.draw_bipartite(G, top)

# Display (new in NetworkX 3.0, returns figure for further customization)
fig = nx.display(G, with_labels=True)
fig.show()
```

## Graphviz Integration

Requires `pygraphviz` or `pydot` installation.

```python
# Using pygraphviz
try:
    import pygraphviz as pgf
    
    # Convert NetworkX graph to AGraph
    A = nx.nx_agraph.to_agraph(G)
    
    # Set graph attributes
    A.graph_attr['rankdir'] = 'LR'  # TB, BT, LR, RL
    A.node_attr['style'] = 'filled'
    A.node_attr['fillcolor'] = 'lightblue'
    
    # Draw
    nx.nx_agraph.draw(A)
    
    # Get layout positions
    pos = nx.nx_agraph.graphviz_layout(A, prog='dot')
    
    # Save to file
    A.draw('graph.png', prog='dot')  # dot, neato, fdp, sfdp, twopi, circo
    
except ImportError:
    print("pygraphviz not installed")

# Using pydot (alternative)
try:
    import pydot
    
    P = nx.nx_pydot.to_pydot(G)
    P.set_graph_attr('rankdir', 'LR')
    
    # Get layout
    pos = nx.nx_pydot.graphviz_layout(P, prog='dot')
    
    # Save
    graph_viz = nx.nx_pydot.to_pydot(G)
    graph_viz.write_png('graph.png')
    
except ImportError:
    print("pydot not installed")
```

## LaTeX Export

Export graphs for publication-quality figures:

```python
# Generate LaTeX code (TikZ/PGF)
latex_code = nx.to_latex(G)
print(latex_code)

# Write to file
with open('graph.tex', 'w') as f:
    f.write(nx.to_latex(G))

# With custom preamble and options
latex_code = nx.to_latex(
    G, 
    doc_type='standalone',
    preamble=r'\usepackage{tikz}',
    edge_properties={'color': 'blue', 'line width': 1},
    node_properties={'fill': 'lightblue', 'minimum size': 10}
)

# Write LaTeX file
nx.write_latex(G, 'graph.tex')
```

## Interactive Visualization with iplotx

For interactive web-based visualization:

```python
try:
    import iplotx as ipx
    
    G = nx.cycle_graph(20)
    
    # Simple interactive plot
    ipx.network(G)
    
    # With layout from NetworkX
    pos = nx.circular_layout(G)
    ipx.network(G, layout=pos)
    
    # Custom styling
    ipx.network(
        G, 
        layout=pos,
        vertex_facecolor=["tomato" if i % 2 == 0 else "gold" for i in range(len(G))],
        vertex_size=15,
        edge_color="gray",
        edge_width=2
    )
    
except ImportError:
    print("iplotx not installed. Install with: pip install iplotx")
```

## Large Graph Visualization Tips

```python
# For graphs with many nodes, use sampling or aggregation

# 1. Show only high-degree nodes
G = nx.erdos_renyi_graph(1000, 0.01)
high_degree_nodes = [n for n, d in G.degree() if d > 10]
G_sub = G.subgraph(high_degree_nodes)
nx.draw(G_sub, node_size=50)

# 2. Show only largest component
G = nx.erdos_renyi_graph(1000, 0.005)
largest_component = max(nx.connected_components(G), key=len)
G_largest = G.subgraph(largest_component)
nx.draw(G_largest)

# 3. Use smaller node sizes for large graphs
nx.draw(G, node_size=10, width=0.5)

# 4. Show only edges above threshold
edges_to_show = [(u, v) for u, v, d in G.edges(data=True) 
                 if d.get('weight', 1) > 0.5]
nx.draw_networkx_nodes(G, pos, node_size=20)
nx.draw_networkx_edges(G, pos, edgelist=edges_to_show, width=1)

# 5. Use edge bundling or force-directed with repulsion
pos = nx.spring_layout(G, k=1.0 / np.sqrt(len(G)), iterations=100)
```

## Common Customizations

```python
# Hide axes and grid
plt.axis('off')
plt.grid(False)

# Set figure size
plt.figure(figsize=(12, 10))

# Add title and annotations
plt.title("Network Visualization", fontsize=16, fontweight='bold')
plt.annotate('Important node', xy=pos['node1'], 
             xytext=(10, 10), textcoords='offset points',
             arrowprops=dict(arrowstyle='->'))

# Save with high quality
plt.savefig('graph.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('graph.pdf', bbox_inches='tight')  # Vector format

# Multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

nx.draw(G, ax=axes[0, 0], with_labels=False)
axes[0, 0].set_title('Spring Layout')

nx.draw_circular(G, ax=axes[0, 1], with_labels=False)
axes[0, 1].set_title('Circular Layout')

nx.draw_spectral(G, ax=axes[1, 0], with_labels=False)
axes[1, 0].set_title('Spectral Layout')

nx.draw_kamada_kawai(G, ax=axes[1, 1], with_labels=False)
axes[1, 1].set_title('Kamada-Kawai Layout')

plt.tight_layout()
plt.show()
```

## Troubleshooting

```python
# Graph won't display? Check:
# 1. Matplotlib backend
import matplotlib
matplotlib.use('Agg')  # For non-interactive environments

# 2. Show the plot
plt.show()  # Required in scripts (not needed in Jupyter)

# Nodes overlap too much?
# Increase spacing or use different layout
pos = nx.spring_layout(G, k=2.0 / np.sqrt(len(G)), iterations=200)

# Too many labels to read?
# Show only some labels
labels = {n: n for n in list(G.nodes())[:20]}  # First 20 nodes
nx.draw(G, labels=labels)

# Colors don't show correctly?
# Ensure values are normalized or use vmin/vmax
nx.draw(G, node_color=node_values, vmin=0, vmax=100, cmap='viridis')
```

## Recommended Tools for Advanced Visualization

For publication-quality or interactive visualizations, consider:

- **Cytoscape**: Desktop application for biological networks
- **Gephi**: Desktop application for large network exploration
- **iplotx**: Python library for interactive web-based visualization
- **D3.js**: JavaScript library for custom web visualizations
- **Graphviz**: Command-line tools for automatic layout

Export your NetworkX graph to appropriate formats:
```python
# For Cytoscape (GraphML)
nx.write_graphml(G, 'graph.graphml')

# For Gephi (GEXF)
nx.write_gexf(G, 'graph.gexf')

# For Graphviz (DOT)
A = nx.nx_agraph.to_agraph(G)
A.write('graph.dot')
```
