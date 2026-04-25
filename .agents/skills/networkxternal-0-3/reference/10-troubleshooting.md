# Troubleshooting

### Common Issues

**Issue**: "Java heap space" error with Neo4J
- **Solution**: Reduce batch size to 1,000 or use a different backend (SQLite/PostgreSQL)

**Issue**: Slow imports with SQLite
- **Solution**: Ensure WAL mode is enabled (automatic on first launch); increase `page_size` pragma

**Issue**: Edge not found after adding
- **Solution**: Check if node IDs are integers; non-integers are hashed via Python's `hash()`. Use `graph.has_edge(u, v)` and check the returned list (not truthiness).

**Issue**: Memory usage still high
- **Solution**: Use streaming (`for edge in graph.edges`) instead of loading all at once. Avoid `list(graph.edges)` on large graphs.

**Issue**: `has_edge()` returns empty list but I expected a boolean
- **Solution**: NetworkXternal deviates from NetworkX here — `has_edge()` returns `list[Edge]`. Check with `if graph.has_edge(u, v):` or `len(graph.has_edge(u, v)) > 0`.

**Issue**: Multiple edges between same nodes all return the same ID
- **Solution**: Use the `key` parameter in `add_edge()` to assign different labels. Edges with the same `(first, second)` but different `label` are distinct.

**Issue**: Integer overflow on edge IDs in large graphs
- **Solution**: Edge IDs use 31-bit signed integers. For very large graphs, ensure your database uses `BigInteger` type (SQLAlchemy does this by default).

**Issue**: `in_edges` returns unexpected results
- **Solution**: `in_edges` is computed as an inverted copy of `out_edges` — it's not stored separately. It swaps `first` and `second` for all directed edges.

### Backend Selection Guide

| Requirement | Recommended Backend |
|-------------|-------------------|
| < 20 MB graph, single process | SQLiteMem or SQLite |
| Multi-process access | PostgreSQL |
| Existing MongoDB infra | MongoDB |
| Existing MySQL infra | MySQL |
| Native graph queries (small) | Neo4J (use with caution) |
| Production, large scale | PostgreSQL |
