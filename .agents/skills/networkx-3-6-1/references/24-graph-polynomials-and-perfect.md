# Graph Polynomials and Perfect Graphs

NetworkX provides functions for computing chromatic and Tutte polynomials, and testing the perfect graph property.

## Chromatic Polynomial

The chromatic polynomial P(G, k) counts the number of valid k-colorings of a graph G. Evaluating at integer k gives the exact count.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])  # Triangle

# Compute chromatic polynomial
cp = nx.chromatic_polynomial(G)
print(cp)  # Poly1([1, -3, 2]) → k³ - 3k² + 2k

# Evaluate at specific k values
num_2_colorings = cp(2)   # 0 (triangle needs 3 colors)
num_3_colorings = cp(3)   # 6 (3! ways to assign 3 colors)
num_4_colorings = cp(4)   # 24 (4×3×2 = 24)
print(f"3-colorings: {num_3_colorings}")
print(f"4-colorings: {num_4_colorings}")

# For complete graph K_n: P(K_n, k) = k(k-1)(k-2)...(k-n+1)
K5 = nx.complete_graph(5)
cp_K5 = nx.chromatic_polynomial(K5)
print(f"K5 with 5 colors: {cp_K5(5)}")  # 120

# Chromatic number is the smallest k where P(G, k) > 0
for k in range(1, 10):
    if cp(k) > 0:
        print(f"Chromatic number χ(G) = {k}")
        break
```

## Tutte Polynomial

The Tutte polynomial T(G; x, y) is a two-variable generalization that encodes many graph invariants.

```python
# Compute Tutte polynomial
tp = nx.tutte_polynomial(G)
print(tp)  # Symbolic expression

# Evaluate at specific points to get graph invariants:
# - T(1, 1) = number of spanning trees
# - T(2, 1) = number of connected subgraphs
# - T(2, 2) = 2^(number of edges)
# - T(0, 0) = 0 (undefined for most graphs)
# - T(x, 0) relates to reliability polynomial
# - T(1, y) is the flow polynomial

# Number of spanning trees
spanning_trees = tp.subs({x: 1, y: 1})
print(f"Spanning trees: {spanning_trees}")

# The Tutte polynomial specializes to:
# Chromatic polynomial: P(G, λ) = (-1)^(n-c) λ^c T(G; 1-λ, 0)
# Flow polynomial: F(G, λ) = (-1)^(m-n+c) T(G; 0, 1-λ)
```

## Perfect Graphs

A graph is **perfect** if for every induced subgraph H, the chromatic number χ(H) equals the clique number ω(H).

```python
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

# Even cycles are perfect
even_cycle = nx.cycle_graph(6)
print(nx.is_perfect_graph(even_cycle))  # True

# Perfect graphs include:
# - Complete graphs
# - Bipartite graphs
# - Chordal graphs (complements of chordal are also perfect)
# - Comparability graphs
# - Interval graphs
# - Line graphs of bipartite graphs (König's theorem)
```

## Summary

| Function | Description |
|----------|-------------|
| `chromatic_polynomial(G)` | Compute chromatic polynomial P(G,k) |
| `tutte_polynomial(G)` | Compute Tutte polynomial T(G; x, y) |
| `is_perfect_graph(G)` | Test perfect graph property |

## Key Evaluations of Tutte Polynomial

| Evaluation | Meaning |
|------------|---------|
| T(1, 1) | Number of spanning trees |
| T(2, 1) | Number of connected subgraphs |
| T(2, 2) | 2^|E| (total subgraphs) |
| T(0, y) | Flow polynomial evaluation |
| T(x, 0) | Reliability polynomial |
