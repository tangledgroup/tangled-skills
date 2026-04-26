# Segments and Paths

## Child Segment

Selects children of each node in the input nodelist — one level deeper into the structure.

### Syntax

```
child-segment = bracketed-selection /
                ("." (wildcard-selector / member-name-shorthand))

bracketed-selection = "[" S selector *(S "," S selector) S "]"
```

**Shorthand forms:**
- `.*` is shorthand for `[*]`
- `.name` is shorthand for `['name']` (only when the name matches `member-name-shorthand`)

The `member-name-shorthand` rule allows: letters, underscore, Unicode characters U+80 and above (excluding surrogates), followed by any of those plus digits. Thus `$.foo.bar` is shorthand for `$['foo']['bar']`, but names with spaces or special characters require bracket notation.

### Semantics

For each node in the input nodelist, the child segment applies each of its selectors and concatenates the results in selector order. A node matched by multiple selectors appears that many times (duplicates are preserved).

Where a selector can produce results in multiple valid orderings (e.g., wildcard on an object), each occurrence of the selector may produce a distinct ordering.

### Examples

```json
// Given: ["a", "b", "c", "d", "e", "f", "g"]
$[0, 3]     → "a", "d"           (indices 0 and 3)
$[0:2, 5]   → "a", "b", "f"      (slice + index)
$[0, 0]     → "a", "a"           (duplicated entries preserved)
```

## Descendant Segment

Selects descendants at any depth — drills down one or more levels.

### Syntax

```
descendant-segment = ".." (bracketed-selection /
                           wildcard-selector /
                           member-name-shorthand)
```

**Shorthand forms:**
- `..*` is shorthand for `..[*]`
- `..name` is shorthand for `..['name']`

Note: `..` alone (without a following selector) is not a valid segment.

### Semantics

For each node in the input nodelist, a descendant segment visits the input node itself and all its descendants in a depth-first traversal:

- Array elements are visited in array order
- Nodes are visited before their descendants
- Object child ordering is non-deterministic

The child segment (after converting shorthand to bracket notation) is applied at each visited node, and results are concatenated in visitation order.

### Examples

```json
// Given: { "o": {"j": 1, "k": 2}, "a": [5, 3, [{"j": 4}, {"k": 6}]] }
$..j        → 1, 4               (or 4, 1 — object order non-deterministic)
$..[0]      → 5, {"j": 4}
$..*        → all values at every depth (parent before children)
$.a..[0,1]  → 5, 3, {"j": 4}, {"k": 6}   (applied to each visited node)
```

For `$..*`, the ordering guarantees that parents appear before children, and within arrays, earlier elements appear before later ones.

## Segment Depth Property

The number of segments in a query determines the minimum depth of selected nodes:

- A query with N segments produces nodes at depth N or greater
- If all N segments are child segments, nodes are at exactly depth N
- Descendant segments produce nodes at depth >= N (one or more levels per descendant segment)

## Normalized Paths

A Normalized Path is a unique, canonical representation of a node's location within a value. It is a JSONPath query with restricted syntax that identifies exactly one node.

### Syntax Rules

- Uses canonical bracket notation (not dot notation)
- Single quotes for string member names
- Non-negative integer indices only (no negative indexes)
- No wildcards, slices, or filters
- Specific characters are escaped in exactly one way

```
normalized-path = root-identifier *(normal-index-segment)
```

### Examples

```
$.a              → $['a']            (object member)
$[1]             → $[1]              (array index)
$[-3]            → $[2]              (for array of length 5, normalized)
$.a.b[1:2]       → $['a']['b'][1]    (slice resolved to single index)
$["\u000B"]      → $['\u000b']       (Unicode escape, lowercase hex)
$["\u0061"]      → $['a']            (resolved to the actual character)
```

Normalized Paths are useful for:
- Compact JSON representation of nodelists as arrays of strings
- Predictable format for testing and post-processing
- Deduplication of nodelists (compare normalized paths)

## Semantics of null

JSON `null` is treated as a regular value — it does not mean "undefined" or "missing".

### Examples

```json
// Given: {"a": null, "b": [null], "c": [{}], "null": 1}
$.a            → null               (the value is null)
$.a[0]         → (empty)            (null is not an array, nothing selected)
$.a.d          → (empty)            (null is not an object, nothing selected)
$.b[0]         → null               (array element is the value null)
$.b[*]         → null               (wildcard selects the null element)
$.b[?@]        → null               (existence test: null is a value, so it exists)
$.b[?@ == null]→ null               (comparison: the value equals null)
$.c[?@.d == null] → (empty)         (@.d selects nothing, which != null)
$.null         → 1                  ("null" is just a member name string)
```

Key distinction: `!@.foo` tests whether the node doesn't exist (returns false if value is null, because the node exists). Use `@.foo == null` to test for an actual null value.
