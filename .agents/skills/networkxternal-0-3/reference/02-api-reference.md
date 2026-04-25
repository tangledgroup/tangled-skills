# API Reference - Complete Method Documentation

This reference documents all public methods, properties, and classes in NetworkXternal.

## Core Classes

### BaseAPI

Abstract base class defining the graph interface. All backends inherit from this.

```python
class BaseAPI:
    __max_batch_size__ = 100
    __is_concurrent__ = True
    __edge_type__ = Edge
    __node_type__ = Node
    __in_memory__ = False
    
    def __init__(
        self,
        directed=True,
        weighted=True,
        multigraph=True,
        **kwargs,
    )
```

**Properties:**
- `directed` (bool): Whether edges have direction
- `weighted` (bool): Whether edges have weights
- `multigraph` (bool): Whether multiple edges between same nodes allowed

### Node

Dataclass representing a graph node.

```python
@dataclass
class Node:
    _id: int = -1           # Integer identifier
    weight: float = 1       # Node weight
    label: int = -1         # Integer label/category
    payload: dict = {}      # Custom attributes (JSON-serializable)
    
    def __bool__(self) -> bool:
        """Returns True if _id >= 0"""
```

### Edge

Dataclass representing a graph edge.

```python
@dataclass
class Edge:
    _id: int = -1           # Integer identifier
    first: int = -1         # Source node ID
    second: int = -1        # Target node ID
    weight: float = 1       # Edge weight
    label: int = -1         # Integer label/category
    is_directed: bool = True  # Whether edge is directed
    payload: dict = {}      # Custom attributes (JSON-serializable)
    
    def __getitem__(self, key: int):
        """Tuple-like access: edge[0] -> first, edge[1] -> second"""
    
    def inverted(self) -> Edge:
        """Return edge with first/second swapped"""
    
    @staticmethod
    def identify_by_members(first: int, second: int) -> int:
        """Generate unique ID from node pair using Cantor pairing function"""
```

### GraphDegree

Dataclass for aggregation results.

```python
@dataclass
class GraphDegree:
    count: int = 0      # Number of items
    weight: float = 0   # Sum of weights
    
    def __int__(self) -> int:
        """Returns count for easy conversion"""
```

## Metadata Methods

### reduce_nodes() -> GraphDegree

Get total node count and weight sum.

```python
graph.reduce_nodes()
# Returns: GraphDegree(count=1000, weight=2500.5)
```

**NetworkX equivalent**: `len(G)` for count

### reduce_edges(u=None, v=None, key=None) -> GraphDegree

Get edge count and weight sum with optional filters.

```python
# All edges
graph.reduce_edges()
# Returns: GraphDegree(count=5000, weight=12500.0)

# Edges where v (target) = 1
graph.reduce_edges(v=1)
# Returns: GraphDegree(count=25, weight=62.5)

# Edges where u (source) = 1
graph.reduce_edges(u=1)
# Returns: GraphDegree(count=30, weight=75.0)

# Edges involving node 1 (either direction)
graph.reduce_edges(1, 1)
# Returns: GraphDegree(count=45, weight=112.5)
```

**NetworkX equivalent**: `G.number_of_edges(u, v, key)`

### biggest_edge_id() -> int

Get the largest edge ID currently in use.

```python
max_id = graph.biggest_edge_id()
# Returns: 987654
```

**Use case**: Generate new unique IDs for bulk inserts

### number_of_nodes() -> int

Count total nodes in graph.

```python
count = graph.number_of_nodes()
# Returns: 1000

# Also available via len()
count = len(graph)
```

**NetworkX equivalent**: `G.number_of_nodes()` or `len(G)`

### number_of_edges(u=None, v=None, key=None) -> int

Count edges with optional filters.

```python
# Total edges
total = graph.number_of_edges()

# Edges to specific node
incoming = graph.number_of_edges(v=42)

# Edges from specific node
outgoing = graph.number_of_edges(u=42)
```

**NetworkX equivalent**: `G.number_of_edges(u, v)`

### order() -> int

Alias for `number_of_nodes()`.

```python
n = graph.order()  # Same as graph.number_of_nodes()
```

**NetworkX equivalent**: `G.order()`

### is_directed() -> bool

Check if graph is directed.

```python
directed = graph.is_directed()
# Returns: True or False
```

**NetworkX equivalent**: `G.is_directed()`

### is_multigraph() -> bool

Check if multiple edges between same nodes are allowed.

```python
multi = graph.is_multigraph()
# Returns: True or False
```

**NetworkX equivalent**: `G.is_multigraph()`

## Bulk Read Properties

### nodes -> Sequence[Node]

Get all nodes in graph.

```python
all_nodes = list(graph.nodes)
# Returns: [Node(_id=1, ...), Node(_id=2, ...), ...]

# Iterate directly
for node in graph.nodes:
    process(node)
```

**⚠️ Warning**: Can be very expensive for large graphs. Use streaming when possible.

**NetworkX equivalent**: `G.nodes()`

### edges -> Sequence[Edge]

Get all edges in graph.

```python
all_edges = list(graph.edges)
# Returns: [Edge(first=1, second=2, ...), ...]

# Iterate directly
for edge in graph.edges:
    process(edge)
```

**⚠️ Warning**: Can be very expensive for large graphs.

**NetworkX equivalent**: `G.edges()`

### out_edges -> Sequence[Edge]

Get all directed edges (where `is_directed=True`).

```python
directed_edges = list(graph.out_edges)
```

**NetworkX equivalent**: `G.out_edges()`

### in_edges -> Sequence[Edge]

Get all incoming edges (inverted out_edges).

```python
incoming_edges = list(graph.in_edges)
```

**NetworkX equivalent**: `G.in_edges()`

### mentioned_nodes_ids -> Sequence[int]

Get all node IDs that appear in any edge.

```python
ids = graph.mentioned_nodes_ids
# Returns: {1, 2, 3, 42, 99, ...}
```

**⚠️ Warning**: Very expensive operation - scans all edges.

## Random Read Methods

### has_node(n) -> Optional[Node]

Check if node exists and return it.

```python
# Integer ID
node = graph.has_node(42)
# Returns: Node(_id=42, ...) or None

# String ID (will be hashed)
node = graph.has_node("node_name")
# Returns: Node(_id=<hash>, ...) or None
```

**NetworkX equivalent**: `n in G` or `G.has_node(n)`

### has_edge(u, v, key=None) -> Sequence[Edge]

Find edges between two nodes.

```python
# Find edge from 1 to 2
edges = graph.has_edge(1, 2)
# Returns: [Edge(...), ...] or None

# Undirected (finds both directions)
edges = graph.has_edge(1, 2)
# In undirected graph: finds 1->2 and 2->1

# With key filter
edges = graph.has_edge(1, 2, key=42)
```

**Note**: Returns list of edges (for multigraphs), not bool like NetworkX.

**NetworkX equivalent**: `G.has_edge(u, v)` or `G[u][v]`

### neighbors(n) -> Sequence[int]

Get IDs of nodes connected to given node (undirected).

```python
neighbor_ids = graph.neighbors(42)
# Returns: {1, 5, 10, 23}  # Set of node IDs
```

**NetworkX equivalent**: `G.neighbors(n)`

### successors(n) -> Sequence[int]

Get IDs of nodes reachable from given node (directed).

```python
successor_ids = graph.successors(42)
# Returns: {5, 10}  # Nodes where 42->X exists
```

**NetworkX equivalent**: `G.successors(n)`

### predecessors(n) -> Sequence[int]

Get IDs of nodes that point to given node (directed).

```python
predecessor_ids = graph.predecessors(42)
# Returns: {1, 3}  # Nodes where X->42 exists
```

**NetworkX equivalent**: `G.predecessors(n)`

### neighbors_of_group(vs: Sequence[int]) -> Set[int]

Get neighbors of a group of nodes.

```python
group = [1, 2, 3]
all_neighbors = graph.neighbors_of_group(group)
# Returns: {4, 5, 6, 7}  # Excludes original group members
```

### neighbors_of_neighbors(v: int, include_related=False) -> Set[int]

Get neighbors-of-neighbors (distance-2 nodes).

```python
# Exclude direct neighbors
distance_2 = graph.neighbors_of_neighbors(42, include_related=False)
# Returns: {nodes at exactly distance 2}

# Include direct neighbors
distance_1_or_2 = graph.neighbors_of_neighbors(42, include_related=True)
# Returns: {nodes at distance 1 or 2}
```

### get_edge_data(u, v, key=None, default=None) -> dict

Get edge attributes as dictionary.

```python
data = graph.get_edge_data(1, 2)
# Returns: {
#   'weight': 3.5,
#   'label': 0,
#   'directed': True,
#   **edge.payload
# } or default
```

**NetworkX equivalent**: `G[u][v]` or `G.get_edge_data(u, v)`

## Random Write Methods

### add(obj, upsert=True) -> int

Add node(s) or edge(s) to graph.

```python
# Single node
count = graph.add(Node(_id=42, weight=2.5))
# Returns: 1

# Single edge
count = graph.add(Edge(first=1, second=2, weight=3.5))
# Returns: 1

# Batch of edges
edges = [Edge(first=i, second=i+1) for i in range(100)]
count = graph.add(edges)
# Returns: 100

# With upsert=False (fail if exists)
count = graph.add(edge, upsert=False)
```

**NetworkX equivalent**: `G.add_node()` or `G.add_edge()`

### remove(obj) -> int

Remove node(s) or edge(s) from graph.

```python
# Single edge
count = graph.remove(edge)
# Returns: 1

# Batch of edges
count = graph.remove(edges)
# Returns: number removed

# Edge without ID (slower - requires search)
edge_no_id = Edge(first=1, second=2)  # No _id set
count = graph.remove(edge_no_id)
```

**NetworkX equivalent**: `G.remove_edge()` or `G.remove_node()`

### remove_node(n) -> int

Remove node and all connected edges.

```python
removed_count = graph.remove_node(42)
# Returns: number of edges removed
```

**NetworkX equivalent**: `G.remove_node(n)`

### add_node(_id, **attrs) -> bool

Add single node with attributes.

```python
# Integer ID
success = graph.add_node(42, weight=2.5, category="source")

# String ID (will be hashed)
success = graph.add_node("node_name", weight=1.0)
```

**NetworkX equivalent**: `G.add_node(n, **attr)`

### add_edge(first, second, **attrs) -> bool

Add single edge with attributes.

```python
# Integer node IDs
success = graph.add_edge(1, 2, weight=3.5, label="connects")

# String node IDs (will be hashed)
success = graph.add_edge("node_a", "node_b", weight=1.0)
```

**NetworkX equivalent**: `G.add_edge(u, v, **attr)`

### add_missing_nodes() -> int

Ensure all nodes referenced in edges exist as node records.

```python
added_count = graph.add_missing_nodes()
# Returns: number of nodes added
```

**Use case**: After bulk edge import, register implied nodes

## Bulk Operations

### add_stream(stream, upsert=True) -> int

Import edges from CSV-like stream.

```python
# From file
with open("edges.csv") as f:
    count = graph.add_stream(f)

# Expected format: first,second,weight (with header)
# 1,2,3.5
# 2,3,4.0
# ...

# From generator
def edge_generator():
    for i in range(1000):
        yield Edge(first=i, second=i+1, weight=float(i))

count = graph.add_stream(edge_generator())
```

**Features:**
- Uses `biggest_edge_id()` to generate new IDs
- Batches inserts at `__max_batch_size__`
- Calls `add_missing_nodes()` after import

### clear()

Remove all nodes and edges.

```python
graph.clear()
# Graph is now empty
```

**NetworkX equivalent**: `G.clear()`

### clear_edges()

Remove all edges but keep nodes.

```python
graph.clear_edges()
# Nodes remain, edges removed
```

**NetworkX equivalent**: `G.remove_edges_from(G.edges())`

## Helper Methods

### make_node_id(node_for_adding) -> int

Convert various node representations to integer ID.

```python
# Integer stays integer
id1 = graph.make_node_id(42)  # Returns: 42

# Node object extracts _id
id2 = graph.make_node_id(Node(_id=42))  # Returns: 42

# String is hashed
id3 = graph.make_node_id("node_name")  # Returns: <hash>

# None becomes -1
id4 = graph.make_node_id(None)  # Returns: -1
```

### make_label(key) -> int

Convert key to integer label.

```python
label1 = graph.make_label(42)     # Returns: 42
label2 = graph.make_label(None)   # Returns: -1
label3 = graph.make_label("key")  # Returns: <hash>
```

### make_node(node_for_adding, **attrs) -> Optional[Node]

Create Node object from various inputs.

```python
# From integer
node1 = graph.make_node(42, weight=2.5, category="source")
# Returns: Node(_id=42, weight=2.5, label=0, payload={"category": "source"})

# From string
node2 = graph.make_node("name", weight=1.0)
# Returns: Node(_id=<hash>, ..., payload={"_id": "name"})
```

### make_edge(first, second, **attrs) -> Edge

Create Edge object from node IDs.

```python
edge = graph.make_edge(1, 2, weight=3.5, label="connects")
# Returns: Edge(
#   _id=<auto-generated>,
#   first=1, second=2,
#   weight=3.5,
#   label=0,
#   is_directed=graph.directed,
#   payload={"label": "connects"}
# )
```

### unique_members_of_edges(es: Sequence[Edge]) -> Set[int]

Extract unique node IDs from edge list.

```python
edges = [Edge(first=1, second=2), Edge(first=2, second=3)]
ids = graph.unique_members_of_edges(edges)
# Returns: {1, 2, 3}
```

## Special Methods

### __iter__() -> Sequence[Node]

Iterate over nodes.

```python
for node in graph:
    process(node)
```

**NetworkX equivalent**: `for n in G:`

### __contains__(n) -> bool

Check if node exists.

```python
if 42 in graph:
    print("Node exists")
```

**NetworkX equivalent**: `n in G`

### __len__() -> int

Get node count.

```python
count = len(graph)  # Same as graph.number_of_nodes()
```

**NetworkX equivalent**: `len(G)`

## SQL-Specific Methods (BaseSQL)

### get_session()

Context manager for database session.

```python
with graph.get_session() as session:
    # Use SQLAlchemy session
    result = session.query(NodeSQL).filter(NodeSQL._id == 42).first()
```

### engine

SQLAlchemy engine object.

```python
# Access underlying engine
engine = graph.engine

# Execute raw SQL
with graph.get_session() as s:
    result = s.execute("SELECT COUNT(*) FROM main_nodes")
```

## MongoDB-Specific Methods

### pipe_match_edge_members(u, v)

Build aggregation pipeline stage for edge matching.

```python
stage = graph.pipe_match_edge_members(1, 2)
# Returns: {$match: {$or: [{first: 1, second: 2}, {first: 2, second: 1}]}}
```

### pipe_match_label(key)

Build aggregation pipeline stage for label matching.

```python
stage = graph.pipe_match_label(42)
# Returns: {$match: {label: 42}} or None if key is None
```

### pipe_compute_degree()

Build aggregation pipeline stage for counting/summing.

```python
stage = graph.pipe_compute_degree()
# Returns: {$group: {_id: null, count: {$sum: 1}, weight: {$sum: "$weight"}}}
```

## Neo4J-Specific Methods

### get_constraints() -> List[str]

List all constraints in database.

```python
constraints = graph.get_constraints()
# Returns: ['constraintvgraph', 'constraineedge', ...]
```

### get_indexes() -> List[str]

List all indexes in database.

```python
indexes = graph.get_indexes()
# Returns: ['indexvgraph', 'indextest', ...]
```

### create_index_nodes()

Create index on node IDs.

```python
graph.create_index_nodes()
# Executes: CREATE INDEX indexVERTEX FOR (v:VERTEX) ON (v._id)
```

### create_constraint_nodes()

Create uniqueness constraint on nodes.

```python
graph.create_constraint_nodes()
# Executes: CREATE CONSTRAINT ... ASSERT (v._id) IS UNIQUE
```

## Utility Functions

### is_sequence_of(objs, expected_class) -> bool

Check if object is sequence of expected type.

```python
from networkxternal.helpers.algorithms import is_sequence_of

edges = [Edge(first=1, second=2)]
is_seq = is_sequence_of(edges, Edge)  # Returns: True
```

### chunks(iterable, size) -> Generator[list]

Split iterable into chunks of given size.

```python
from networkxternal.helpers.algorithms import chunks

edges = list(range(1000))
for chunk in chunks(edges, 100):
    process_batch(chunk)  # Each chunk has 100 items
```

### extract_database_name(url, default="graph") -> Tuple[str, str]

Parse database URL into address and name.

```python
from networkxternal.helpers.algorithms import extract_database_name

address, name = extract_database_name("mongodb://localhost:27017/mygraph")
# Returns: ("mongodb://localhost:27017", "mygraph")
```

### sample_reservoir(iterable, count_needed: int) -> list

Reservoir sampling for large iterables.

```python
from networkxternal.helpers.algorithms import sample_reservoir

# Get 100 random edges from potentially infinite stream
sample = sample_reservoir(graph.edges, 100)
```
