# Graphical Degree Sequences and Validation

NetworkX provides algorithms for checking whether degree sequences can be realized as graphs, and for validating graph types.

## Graphical Sequence Validation

A **graphical sequence** is a sequence of non-negative integers that can be realized as the degree sequence of a simple graph.

### Erdős–Gallai Theorem

A sequence is graphical iff the sum is even and the Erdős–Gallai conditions hold for all k.

```python
import networkx as nx

# Valid graphical sequence (can form a graph)
valid_seq = [3, 3, 2, 2, 2, 1]
is_valid_eg = nx.is_valid_degree_sequence_erdos_gallai(valid_seq, "eg")
print(is_valid_eg)  # True

# Invalid sequence (sum is odd → impossible)
invalid_seq = [3, 3, 2, 2, 2]
is_valid = nx.is_valid_degree_sequence_erdos_gallai(invalid_seq, "eg")
print(is_valid)  # False
```

### Havel–Hakimi Algorithm

Constructive algorithm: repeatedly connect highest-degree node to next-highest.

```python
# Havel-Hakimi validation
is_valid_hh = nx.is_valid_degree_sequence_havel_hakimi(valid_seq, "hh")
print(is_valid_hh)  # True

# Both methods agree for simple graphs
is_valid_both_eg = nx.is_valid_degree_sequence_erdos_gallai(valid_seq, "eg")
is_valid_both_hh = nx.is_valid_degree_sequence_havel_hakimi(valid_seq, "hh")
```

## Graph Type Validation

Check if a degree sequence can be realized as specific graph types.

```python
# Simple graph (no self-loops, no parallel edges)
is_simple = nx.is_graphical([3, 2, 2, 1], method="eg")
print(is_simple)  # True

# Directed graph (sequence of in/out degrees)
in_seq = [2, 1, 1]
out_seq = [1, 2, 1]
is_digraphical = nx.is_digraphical(in_seq, out_seq)
print(is_digraphical)  # True

# Multigraph (allows parallel edges, no self-loops)
is_multigraphical = nx.is_multigraphical([3, 3, 0])
print(is_multigraphical)  # True (edges between nodes 1 and 2)

# Pseudograph (allows both parallel edges AND self-loops)
is_pseudographical = nx.is_pseudographical([3, 3, 0])
print(is_pseudographical)  # True
```

## Practical Applications

### Validate Generated Graph Sequences

```python
import networkx as nx

# Generate a random graph and check its degree sequence
G = nx.erdos_renyi_graph(20, 0.3)
deg_seq = sorted([d for n, d in G.degree()], reverse=True)

# Verify the sequence is graphical
is_valid = nx.is_valid_degree_sequence_erdos_gallai(deg_seq, "eg")
print(f"Generated graph degree sequence valid: {is_valid}")  # Always True

# Check if realizable as directed graph
in_deg = [d for n, d in G.in_degree()] if isinstance(G, nx.DiGraph) else deg_seq
out_deg = [d for n, d in G.out_degree()] if isinstance(G, nx.DiGraph) else deg_seq
if len(in_deg) == len(out_deg):
    is_directed = nx.is_digraphical(in_deg, out_deg)
    print(f"Realizable as directed graph: {is_directed}")
```

### Degree Sequence Generation

```python
from networkx.generators.degree_seq import configuration_model, random_degree_graph_sequence

# Create a graph with a specific degree sequence
degree_sequence = [5, 4, 4, 3, 3, 2, 2, 1]

# Validate first
if nx.is_valid_degree_sequence_havel_hakimi(degree_sequence, "hh"):
    # Generate random graph with this degree sequence
    G = configuration_model(degree_sequence)
    G = nx.Graph(G)  # Remove parallel edges/self-loops
    print(f"Created graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
else:
    print("Invalid degree sequence - cannot form a simple graph")
```

## Complete Graphical Sequence Function Reference

| Function | Description | Method |
|----------|-------------|--------|
| `is_graphical(seq)` | Realizable as simple graph? | Erdős–Gallai |
| `is_digraphical(in_seq, out_seq)` | Realizable as directed graph? | Gale-Ryser |
| `is_multigraphical(seq)` | Realizable as multigraph (no self-loops)? | Handshaking lemma |
| `is_pseudographical(seq)` | Realizable as pseudograph (self-loops ok)? | Any sequence ≥ 0 |
| `is_valid_degree_sequence_erdos_gallai(seq, method="eg")` | Erdős–Gallai check | O(n²) |
| `is_valid_degree_sequence_havel_hakimi(seq, method="hh")` | Havel-Hakimi check | O(n²) |

## Summary

| Function | Description | Use Case |
|----------|-------------|----------|
| `is_valid_degree_sequence_erdos_gallai()` | Erdős–Gallai theorem check | Validate sequences |
| `is_valid_degree_sequence_havel_hakimi()` | Havel-Hakimi algorithm | Constructive validation |
| `is_graphical()` | Realizable as simple graph | Basic validation |
| `is_digraphical()` | Realizable as directed graph | Directed networks |
| `is_multigraphical()` | Realizable as multigraph | Parallel edges allowed |
| `is_pseudographical()` | Realizable as pseudograph | Self-loops + parallel |
