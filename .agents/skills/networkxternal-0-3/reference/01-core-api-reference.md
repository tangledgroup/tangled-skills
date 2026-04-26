# Core API Reference

## BaseAPI Abstract Class

The `BaseAPI` class defines the graph interface all backends must implement. It is partially compatible with NetworkX's `MultiDiGraph`.

### Configuration Attributes

- `__max_batch_size__`: Maximum items per batch operation (default: 100)
- `__is_concurrent__`: Whether the backend supports concurrent access (default: True)
- `__edge_type__`: Edge class used by this backend (default: `Edge`)
- `__node_type__`: Node class used by this backend (default: `Node`)
- `__in_memory__`: Whether data is stored in memory (default: False)

### Constructor

```python
BaseAPI(directed=True, weighted=True, multigraph=True, **kwargs)
```

Parameters control graph type. By default creates a directed, weighted multigraph.

### Metadata Methods

```python
reduce_nodes() -> GraphDegree
```
Returns count and sum of weights for all nodes. Abstract — each backend implements its own query.

```python
reduce_edges(u=None, v=None, key=None) -> GraphDegree
```
Counts edges optionally filtered by source node `u`, target node `v`, or edge label `key`. Both `u` and `v` can be `None` to count all edges. If both are set to the same value, searches for edges containing that node in any role.

```python
biggest_edge_id() -> int
```
Returns the maximum edge ID currently in the graph. Used to generate incremental IDs during bulk import.

```python
number_of_nodes() -> int
number_of_edges(u=None, v=None, key=None) -> int
__len__() -> int
order() -> int
is_directed() -> bool
is_multigraph() -> bool
```

Standard graph metadata queries. `__len__` and `order` both delegate to `number_of_nodes`.

### Bulk Read Properties

```python
nodes -> Sequence[Node]
edges -> Sequence[Edge]
out_edges -> Sequence[Edge]
in_edges -> Sequence[Edge]
mentioned_nodes_ids -> Sequence[int]
```

Returns all nodes, edges, or node IDs referenced by edges. `mentioned_nodes_ids` can be expensive — it scans all edges to collect unique endpoint IDs. `in_edges` is derived from `out_edges` by inverting direction.

### Random Read Methods

```python
has_node(n) -> Optional[Node]
```
Returns the node with ID `n`, or `None` if not found. Non-integer `n` is hashed.

```python
has_edge(u, v, key=None) -> Sequence[Edge]
```
Returns all edges matching the given source `u`, target `v`, and optional label `key`. Either `u` or `v` can be `None` to match any endpoint. Returns empty sequence if no edges found (deviates from NetworkX's `bool` return).

```python
neighbors(n) -> Sequence[int]
successors(n) -> Sequence[int]
predecessors(n) -> Sequence[int]
```
Returns IDs of connected nodes. `successors` finds edges where `n` is the source. `predecessors` finds edges where `n` is the target. All exclude self-loops.

```python
neighbors_of_group(vs: Sequence[int]) -> Set[int]
neighbors_of_neighbors(v: int, include_related=False) -> Set[int]
```
Two-hop neighborhood queries. `neighbors_of_group` returns nodes connected to any member of `vs`. `neighbors_of_neighbors` returns nodes two hops away from `v`, optionally including first-hop neighbors.

```python
__iter__() -> Sequence[Node]
__contains__(n) -> bool
get_edge_data(u, v, key=None, default=None) -> dict
```

Iteration and containment checks. `get_edge_data` returns edge attributes as a dictionary for NetworkX compatibility.

### Random Write Methods

```python
add(obj, upsert=True) -> int
```
Adds a single `Edge`, `Node`, or sequence of either. Returns count of items added. With `upsert=True`, existing items are updated rather than duplicated.

```python
remove(obj) -> int
```
Removes a single `Edge`, `Node`, or sequence. Edges without known ID (`_id < 0`) are matched by endpoints and direction, which is slower.

```python
add_node(_id, **attrs) -> bool
add_edge(first, second, **attrs) -> bool
remove_node(n) -> int
```
NetworkX-compatible convenience methods. `add_node` accepts keyword arguments as payload attributes. `add_edge` passes extra kwargs through to edge creation. `remove_node` deletes the node and all its incident edges.

```python
add_missing_nodes() -> int
```
Scans all edges and creates `Node` records for any endpoint not yet registered as a node. Expects all node IDs to fit in RAM.

### Bulk Operations

```python
add_stream(stream, upsert=True) -> int
```
Imports data from an adjacency list stream. Each item should be an Edge or convertible to one. Uses `biggest_edge_id` for incremental ID generation. Processes in chunks of `__max_batch_size__`. Calls `add_missing_nodes` after import.

```python
clear()
clear_edges()
```
`clear` removes all nodes and edges. `clear_edges` removes only edges, preserving nodes.

### Helper Methods

```python
make_node_id(node_for_adding) -> int
make_label(key) -> int
make_node(node_for_adding, **attrs) -> Optional[Node]
make_edge(first, second, key, **attrs) -> Optional[Edge]
unique_members_of_edges(es: Sequence[Edge]) -> Set[int]
```

Internal utilities for ID conversion and object construction. Non-integer node IDs are hashed using Python's `hash()`. The `make_edge` helper auto-generates edge ID via `Edge.identify_by_members()` when not provided.

## Data Classes

### Node

```python
@dataclass(order=True)
class Node:
    _id: int = -1
    weight: float = 1
    label: int = -1
    payload: dict = field(default_factory=dict)
```

`__bool__` returns `True` when `_id >= 0`.

### Edge

```python
@dataclass(order=True)
class Edge:
    _id: int = -1
    first: int = -1
    second: int = -1
    weight: float = 1
    label: int = -1
    is_directed: bool = True
    payload: dict = field(default_factory=dict)
```

Supports tuple-like indexing: `edge[0]` returns `first`, `edge[1]` returns `second`. `__bool__` returns `True` when `_id >= 0`.

```python
Edge.identify_by_members(first: int, second: int) -> int
```
Static method generating deterministic edge ID from endpoints using Cantor pairing function modulo 2^31. Order-dependent: `identify_by_members(10, 20) != identify_by_members(20, 10)`.

```python
edge.inverted() -> Edge
```
Returns a new Edge with `first` and `second` swapped. Used by `in_edges` property.

### GraphDegree

```python
@dataclass
class GraphDegree:
    count: int = 0
    weight: float = 0
```

Simple holder for reduction results. `__int__` delegates to `count`.

## Utility Functions (helpers/algorithms.py)

- `is_sequence_of(objs, expected_class)` — checks if all items in a sequence are instances of a class
- `chunks(iterable, size)` — splits iterable into chunks of given size
- `extract_database_name(url, default="graph")` — parses URL to extract address and database name
- `remove_duplicate_edges(es)` — filters out edges with duplicate IDs
- `sample_reservoir(iterable, count_needed)` — reservoir sampling for random subsets
- `flatten(iterable)` — flattens nested iterables
