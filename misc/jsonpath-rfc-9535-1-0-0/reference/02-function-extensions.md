# Function Extensions

JSONPath defines an extension point for adding filter expression functionality through registered function extensions. Five built-in functions are defined as part of the specification, and additional functions can be registered via the IANA "Function Extensions" subregistry.

## Type System

Function extensions use a limited type system to enforce well-typedness:

- **ValueType** — JSON values or the special result `Nothing` (distinct from null)
- **LogicalType** — `LogicalTrue` or `LogicalFalse` (unrelated to JSON `true`/`false`)
- **NodesType** — nodelists

Each function parameter and result has a declared type. Well-typedness can be checked statically without the query argument.

### Type Conversion

- **NodesType → LogicalType**: A nodelist converts to `LogicalTrue` if it contains one or more nodes, `LogicalFalse` if empty. This allows a NodesType function to be used where LogicalType is expected.
- **No implicit NodesType → ValueType conversion** — use `value()` explicitly.
- **Singular query → ValueType**: When a singular query is used as a function argument expecting ValueType, the single node's value is used, or `Nothing` if the nodelist is empty.

### Well-Typedness Rules

A function expression must satisfy two conditions:

1. **Context-appropriate result type:**
   - As a test expression: result type must be LogicalType or NodesType
   - As a comparable in comparison: result type must be ValueType
   - As a function argument: result type must match the parameter's declared type (with conversion rules)

2. **Well-typed arguments:** Each argument must match its corresponding parameter's declared type according to the grammar rules for literals, queries, and logical expressions.

## Built-in Functions

### length()

Computes the length of a string, array, or object.

- **Parameters**: 1 × ValueType
- **Result**: ValueType (unsigned integer or Nothing)

Behavior:
- String → number of Unicode scalar values
- Array → number of elements
- Object → number of members
- Other (number, true, false, null) → Nothing

```
$[?length(@.authors) >= 5]    → items with 5+ authors
$[?length(@.name) > 0]        → items where name is non-empty string
```

**Well-typedness example**: `$[?length(@.*) < 3]` is NOT well-typed because `@.*` is a non-singular query (NodesType, not ValueType).

### count()

Counts the number of nodes in a nodelist.

- **Parameters**: 1 × NodesType
- **Result**: ValueType (unsigned integer)

No deduplication — if a node appears multiple times in the nodelist, it is counted each time.

```
$[?count(@..tag) >= 5]        → items with 5+ descendant "tag" nodes
$[?count(@.*) == 1]           → items with exactly one child
```

**Well-typedness example**: `$[?count(1) == 1]` is NOT well-typed because `1` is a literal, not a query or function expression.

### match()

Tests whether an entire string matches a regular expression (I-Regexp per RFC 9485).

- **Parameters**: 2 × ValueType (both must be strings)
- **Result**: LogicalType

The second argument must conform to I-Regexp syntax. If either argument is not a string, or the pattern is not valid I-Regexp, the result is `LogicalFalse`.

```
$[?match(@.date, "^1974-05-..")]     → dates matching 1974-05-XX
$[?match(@.timezone, "^Europe/.*")]  → timezones in Europe
```

### search()

Tests whether a string contains a substring matching a regular expression (I-Regexp per RFC 9485).

- **Parameters**: 2 × ValueType (both must be strings)
- **Result**: LogicalType

Unlike `match()` which requires the entire string to match, `search()` succeeds if any substring matches.

```
$[?search(@.author, "^[BR]ob")]   → authors starting with Rob or Bob
$[?search(@.name, "[0-9]+")]      → names containing digits
```

### value()

Extracts the value from a nodelist containing exactly one node.

- **Parameters**: 1 × NodesType
- **Result**: ValueType

Behavior:
- Single node → the value of that node
- Empty nodelist → Nothing
- Multiple nodes → Nothing

This function bridges NodesType to ValueType for comparisons.

```
$[?value(@..color) == "red"]     → items where unique descendant color is "red"
```

**Note**: A singular query can be used directly where ValueType is expected, so `value()` is only needed with non-singular queries (like descendant segments).

## Well-Typedness Examples

```
$[?length(@) < 3]               → well-typed
$[?count(@.*) == 1]             → well-typed
$[?match(@.tz, "^Europe/.*")]   → well-typed
$[?value(@..color) == "red"]    → well-typed

$[?length(@.*) < 3]             → NOT well-typed (@.* is non-singular, NodesType)
$[?count(1) == 1]               → NOT well-typed (1 is not a query)
$[?match(@.tz, "Europe/.*") == true]  → NOT well-typed (LogicalType in comparison)
$[?value(@..color)]             → NOT well-typed (ValueType in test expression)
```

## Function Expression Grammar

```
function-name     = function-name-first *function-name-char
function-name-first = LCALPHA          ; "a".."z"
function-name-char  = function-name-first / "_" / DIGIT

function-expr     = function-name "(" S [function-argument
                     *(S "," S function-argument)] S ")"
function-argument = literal /
                     filter-query /        ; includes singular-query
                     logical-expr /
                     function-expr
```

Function names start with a lowercase letter and contain only lowercase letters, digits, and underscores. Functions are side-effect free — all evaluation orders must produce the same result.

## IANA Registry

The "Function Extensions" subregistry under the "JSONPath" registry uses Expert Review policy. Each entry includes:

- Function Name (lowercase ASCII, `[a-z][_a-z0-9]*`)
- Brief Description
- Parameters (comma-separated declared types)
- Result (declared type)
- Reference document

The initial entries are the five built-in functions listed above.
