# Transformation Functions

## Contents
- Inclusion and Exclusion Transforms
- Character-Wise Transform Table
- String-Wise Operations
- Position Tie-Breaking
- Update Operations
- Code Examples
- Design Considerations

## Inclusion and Exclusion Transforms

OT systems use two categories of transformation functions:

**Inclusion Transformation (IT)**, also called forward transformation: `T(Oa, Ob)` transforms operation `Oa` against concurrent operation `Ob` so the impact of `Ob` is included. This is the primary transform used for consistency maintenance.

**Exclusion Transformation (ET)**, also called backward transformation: `T⁻¹(Oa, Ob)` transforms `Oa` against `Ob` so the impact of `Ob` is excluded. Required when supporting undo — inverse operations must be transformed to exclude the effects they're reversing.

Some OT systems use both IT and ET. Others (like Google Wave/Docs) use only IT functions with operation composition, avoiding ET entirely.

## Character-Wise Transform Table

For a linear address space with character-wise `Insert[p, c]` and `Delete[p, n]` operations, the complete inclusion transform table for transforming `Op1` against concurrent `Op2`:

### Insert vs Insert

```
T(Insert[p1, c1], Insert[p2, c2]) =
  if p1 < p2:              Insert[p1, c1]
  elif p1 == p2 and sid1 < sid2:  Insert[p1, c1]
  else:                    Insert[p1+1, c1]
```

Both users insert at the same position. The tie-break uses site identifiers to establish a deterministic total order.

### Insert vs Delete

```
T(Insert[p1, c1], Delete[p2, n]) =
  if p1 <= p2:             Insert[p1, c1]
  elif p1 > p2 + n:        Insert[p1 - n, c1]
  else:                    Insert[p2 + n, c1]
```

If the insert is before the delete range, position unchanged. If after, shift left by deleted length. If within the deleted range, place at the end of where the deletion occurred.

### Delete vs Insert

```
T(Delete[p1, n], Insert[p2, c2]) =
  if p2 <= p1:             Delete[p1 + 1, n]
  else:                    Delete[p1, n]
```

If the insert precedes or equals the delete start, shift delete right by 1. Otherwise unchanged.

### Delete vs Delete

```
T(Delete[p1, n], Delete[p2, m]) =
  if p1 >= p2 + m:         Delete[p1 - m, n]
  elif p1 + n <= p2:       Delete[p1, n]
  elif p1 == p2 and n == m: NoOp (fully overlapped)
  elif p1 >= p2:           Delete[p2, (p1 + n) - (p2 + m)]
  else:                    Delete[p1 + m, n - m]
```

Non-overlapping deletes adjust positions. Partial overlaps reduce to the non-overlapping remainder. Full overlap produces a no-op.

## String-Wise Operations

Character-wise transforms operate on single characters. String-wise operations handle sequences:

- `Insert[p, "abc"]` — insert multiple characters at once
- `Delete[p, 3]` — delete a range of characters

String-wise transforms reduce network traffic (one operation instead of three) but complicate the transform logic. When two string-wise inserts occur at the same position, the tie-breaking policy determines interleaving order. The CSM and CA consistency models address how to specify total ordering for these cases.

## Position Tie-Breaking

When concurrent operations target the same position, a deterministic tie-breaking policy is required:

- **Site ID ordering**: Compare `sid` values — lower site ID inserts first
- **Timestamp ordering**: Compare generation timestamps
- **Content-based**: Deterministic comparison of inserted content

The choice affects the final document state when concurrent inserts collide. The policy must be consistent across all replicas.

## Update Operations

Rich-text editing adds a third primitive: `Update[p, n, attributes]` — apply formatting (bold, italic, color) to a range.

Transform rules for `Update` against `Insert` and `Delete` follow similar positional adjustment logic:

```
T(Update[p1, n1, attr], Insert[p2, c]) =
  if p2 <= p1:             Update[p1 + 1, n1, attr]
  elif p2 <= p1 + n1:      Update[p1, n1 + 1, attr]
  else:                    Update[p1, n1, attr]

T(Update[p1, n1, attr], Delete[p2, m]) =
  if p2 >= p1 + n1:        Update[p1 - m, n1, attr]
  elif p2 <= p1:           Update[p2, max(0, p1 + n1 - p2 - m), attr]
  else:                    Update[p1, (p1 + n1) - (p2 + m), attr]
```

Update vs Update transforms must handle attribute merging (e.g., bold + italic = bold-italic).

## Code Examples

### Inclusion Transform for Plain Text (Python)

```python
def transform_insert_against_insert(op1, op2):
    """Transform Insert[p1,c1] against concurrent Insert[p2,c2]."""
    p1, c1, sid1 = op1
    p2, c2, sid2 = op2
    if p1 < p2 or (p1 == p2 and sid1 < sid2):
        return ("insert", p1, c1)
    else:
        return ("insert", p1 + 1, c1)

def transform_insert_against_delete(op1, op2):
    """Transform Insert[p1,c1] against concurrent Delete[p2,n]."""
    p1, c1 = op1
    p2, n = op2
    if p1 <= p2:
        return ("insert", p1, c1)
    elif p1 > p2 + n:
        return ("insert", p1 - n, c1)
    else:
        return ("insert", p2 + n, c1)

def transform_delete_against_insert(op1, op2):
    """Transform Delete[p1,n] against concurrent Insert[p2,c2]."""
    p1, n = op1
    p2, _ = op2
    if p2 <= p1:
        return ("delete", p1 + 1, n)
    else:
        return ("delete", p1, n)
```

### Google Wave-Style Transform with Composition

Google Wave's OT uses operation composition rather than separate IT/ET functions. Operations are represented as sequences of retain/insert/delete segments:

```
# Operation format: [(type, count/chars), ...]
# Types: "retain", "insert", "delete"

op1 = [("retain", 2), ("insert", "hello"), ("retain", 1)]
op2 = [("retain", 3), ("delete", 2)]

# transform(op3, op_context) transforms op3 against the context
# of operations already applied
```

This representation supports rich-text natively (retain segments can carry attribute changes) and simplifies the composition property required for correctness.

## Design Considerations

Transformation function complexity depends on:

1. **System functionality**: Consistency-only systems need fewer properties than those supporting undo, locking, or awareness
2. **Correctness responsibility division**: What properties the control algorithm maintains vs what the transform functions must guarantee
3. **Operation model**: Generic primitives (insert/delete/update) allow reuse across applications; application-specific operations require m² transform functions for m operation types
4. **Data model**: Character-wise is simplest; string-wise, hierarchical (tree), and structured data each add complexity
5. **IT-only vs IT+ET**: Using only inclusion transforms simplifies the function set but requires different control algorithm design
