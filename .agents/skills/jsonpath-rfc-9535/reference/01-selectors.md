# Selectors

Selectors appear inside child segments (`[<selectors>]`) and descendant segments (`..[<selectors>]`). Each selector takes an input value and produces a nodelist of zero or more children of that value.

Multiple selectors can be combined within a single segment using comma separation: `$[0, 3]` selects both the first and fourth elements.

## Name Selector

Selects at most one object member value by name.

### Syntax

```
name-selector = string-literal
string-literal = %x22 *double-quoted %x22 /    ; "string"
                 %x27 *single-quoted %x27       ; 'string'
```

JSONPath allows both single and double quotes for strings (unlike JSON which only allows double quotes). Within a single-quoted string, double quotes need no escaping (and vice versa).

Escape sequences supported (same as JSON plus `\'`):

- `\b` — backspace (U+0008)
- `\t` — horizontal tab (U+0009)
- `\n` — line feed (U+000A)
- `\f` — form feed (U+000C)
- `\r` — carriage return (U+000D)
- `\"` — quotation mark (U+0022)
- `\'` — apostrophe (U+0027)
- `\/` — slash (U+002F)
- `\\` — backslash (U+005C)
- `\uXXXX` — Unicode code point (with surrogate pair support)

### Semantics

The name selector string is converted to a member name by removing surrounding quotes and processing escape sequences. Applied to an object node, it selects the member value whose name equals the computed member name, or selects nothing if no such member exists. Nothing is selected from non-object values.

**String comparison**: Two strings are equal if and only if they are identical sequences of Unicode scalar values. No normalization is applied.

### Examples

```json
// Given: { "o": {"j j": {"k.k": 3}}, "'": {"@": 2} }
$.o['j j']           → {"k.k": 3}
$.o['j j']['k.k']    → 3
$["'"]["@"]          → 2
```

## Wildcard Selector

Selects all children of an object or array.

### Syntax

```
wildcard-selector = "*"
```

Shorthand: `.*` is equivalent to `[*]`, and `..*` is equivalent to `..[*]`.

### Semantics

- Applied to an **object**: selects all member values. Order is non-deterministic (JSON objects are unordered).
- Applied to an **array**: selects all elements in array order.
- Applied to a **primitive** (number, string, true, false, null): selects nothing.

When the wildcard appears multiple times in a segment (`$[*, *]`), each occurrence may produce results in a distinct order when applied to objects with 2+ members.

### Examples

```json
// Given: { "o": {"j": 1, "k": 2}, "a": [5, 3] }
$[*]    → {"j": 1, "k": 2} and [5, 3]   (order of these two is non-deterministic)
$.o[*]  → 1, 2                           (order may vary)
$.a[*]  → 5, 3                           (array order preserved)
```

## Index Selector

Selects at most one array element by zero-based index.

### Syntax

```
index-selector = int
int            = "0" / (["-"] DIGIT1 *DIGIT)
DIGIT1         = %x31-39    ; 1-9, no leading zeros
```

To be valid, the index value MUST be within the I-JSON exact range: `[-(2^53)+1, (2^53)-1]`.

No leading zeros are allowed (e.g., `01` and `-01` are invalid).

### Semantics

- **Non-negative index**: selects the element at that zero-based position. Nothing selected if index is out of range (not an error).
- **Negative index**: counts from the end. Equivalent non-negative index = array length + negative index. `-1` selects the last element, `-2` the penultimate. Nothing selected if the resulting position doesn't exist (not an error).
- Applied to a non-array value: selects nothing.

### Examples

```json
// Given: ["a", "b"]
$[1]   → "b"
$[-2]  → "a"    (normalized path: $[0])
$[5]   → (empty, index out of range, not an error)
```

## Array Slice Selector

Selects a range of array elements with start, end, and step parameters.

### Syntax

```
slice-selector = [start S] ":" S [end S] [":" [S step ]]
start          = int    ; included in selection
end            = int    ; not included in selection
step           = int    ; default: 1
```

The second colon can be omitted when step is omitted. All three parameters are optional.

### Semantics

Inspired by Python slice expressions and JavaScript's `Array.prototype.slice`. The expression `start:end:step` selects elements at indices starting at `start`, incrementing by `step`, up to (but not including) `end`.

**Default values:**

- `step`: defaults to 1
- When `step >= 0`: `start` defaults to 0, `end` defaults to array length
- When `step < 0`: `start` defaults to `len - 1`, `end` defaults to `-len - 1`

**Negative indices** are normalized: `Normalize(i, len)` returns `i` if `i >= 0`, otherwise `len + i`.

**Bounds clamping:** After normalization, bounds are clamped to `[0, len]` for positive step and `[-1, len-1]` for negative step.

**When step = 0**: no elements are selected (result is empty). This differs from Python which raises an error.

### Examples

```json
// Given: ["a", "b", "c", "d", "e", "f", "g"]
$[1:3]     → "b", "c"           (indices 1, 2)
$[5:]      → "f", "g"           (indices 5, 6)
$[1:5:2]   → "b", "d"           (indices 1, 3)
$[5:1:-2]  → "f", "d"           (indices 5, 3, reverse order)
$[::-1]    → "g","f","e","d","c","b","a"   (full reverse)
```

## Filter Selector

Selects children matching a logical expression. Iterates over elements of arrays or members of objects.

### Syntax

```
filter-selector = "?" S logical-expr
logical-expr    = logical-or-expr
logical-or-expr = logical-and-expr *(S "||" S logical-and-expr)
logical-and-expr = basic-expr *(S "&&" S basic-expr)
basic-expr      = paren-expr / comparison-expr / test-expr
```

The current node within a filter is accessed via `@`. Nested filters can only access their directly enclosing `@` — there is no syntax to reach outer filter contexts.

### Logical Operators

- `||` — logical OR (disjunction, binds least tightly)
- `&&` — logical AND (conjunction, binds more tightly than OR)
- `!` — logical NOT
- `(...)` — grouping parentheses

Operator precedence (highest to lowest):

1. Grouping, function expressions
2. Logical NOT (`!`)
3. Comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`)
4. Logical AND (`&&`)
5. Logical OR (`||`)

### Test Expressions (Existence Tests)

A query by itself in a logical context is an existence test:

```
$[?@.isbn]           → selects nodes where @.isbn returns at least one result
$[?!@.optional]      → selects nodes where @.optional returns no results
```

Key distinction: `!@.foo` tests whether `@.foo` selects no nodes (returns true if the node doesn't exist). To test for a null value, use `@.foo == null` instead — `!@.foo` would return false even when the value is null because the node exists.

### Comparison Expressions

Comparisons work between primitive values (numbers, strings, true, false, null) and can also compare structured values (arrays, objects) for equality.

```
comparison-expr = comparable S comparison-op S comparable
comparable      = literal / singular-query / function-expr
comparison-op   = "==" / "!=" / "<=" / ">=" / "<" / ">"
```

**Literals** in filter expressions: numbers (decimal, with optional fraction and exponent), strings (single or double quoted), `true`, `false`, `null`.

**Singular queries**: only name segments (`['name']` or `.name`) and index segments (`[N]`) — no wildcards, slices, or filters. Can be relative (`@.foo`) or absolute (`$.bar`).

### Comparison Semantics

- **`==` between numbers**: normal mathematical equality for I-JSON range values
- **`==` between strings**: exact Unicode scalar value sequence comparison
- **`<` between numbers**: normal mathematical ordering
- **`<` between strings**: lexicographic by Unicode scalar value (empty string < any non-empty)
- **Type mismatch** (e.g., number vs string): `==` yields false, `<` yields false
- **Objects/arrays**: `==` works (structural equality), but `<` is not supported
- **Empty nodelist on one side of comparison**: `==` yields true only if other side is also empty; `<` yields false

### Examples

```json
// Given: { "a": [3, 5, 1, 2, 4, 6, {"b":"j"}, {"b":"k"}, {"b":{}}, {"b":"kilo"}] }
$.a[?@.b == 'kilo']     → {"b": "kilo"}
$.a[?@ > 3.5]           → 5, 4, 6
$.a[?@.b]               → all elements with a "b" member (4 objects)
$.a[?@ < 2 || @.b == "k"]   → 1, {"b": "k"}
```

### Nested Filters

Filters can be nested, but each `@` only refers to its directly enclosing filter:

```
$[?@[?@.b]]    → selects top-level members whose children include elements with a "b" member
```
