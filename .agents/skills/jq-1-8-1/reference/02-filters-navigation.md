# Filters and Navigation

## Identity: `.`

The simplest filter — takes input and produces it unchanged. Main use is validating and pretty-printing JSON.

```bash
echo '{"a":1}' | jq '.'
```

## Object Identifier-Index: `.foo`, `.foo.bar`

Access object fields by name. Chained access navigates nested structures.

```bash
echo '{"user":{"name":"Alice"}}' | jq '.user.name'
# "Alice"
```

## Optional Access: `.foo?`

Like `.foo` but suppresses errors if the key doesn't exist (produces no output instead of `null`).

```bash
echo '{"a":1}' | jq '.b?'
# (no output)
```

## Object Index: `.[<string>]`

Access object fields using string expressions. Supports variables and computed keys.

```bash
jq -n '"name" as $key | {"name":"Alice"} | .[$key]'
# "Alice"
```

## Array Index: `.[<number>]`

Access array elements by zero-based index. Negative indices count from the end.

```bash
echo '[10,20,30]' | jq '.[-1]'
# 30
```

Multiple indices produce multiple outputs:

```bash
echo '[10,20,30]' | jq '.[0, 2]'
# 10
# 30
```

## Array/String Slice: `.[<number>:<number>]`

Extract a range of elements (start inclusive, end exclusive). Works on both arrays and strings.

```bash
echo '[0,1,2,3,4,5]' | jq '.[2:4]'
# [2, 3]

echo '"hello"' | jq '.[1:4]'
# "ell"
```

## Array/Object Value Iterator: `.[]`

Iterates over array elements (by index) or object values (by key). Produces one output per element/value.

```bash
echo '[1,2,3]' | jq '.[]'
# 1
# 2
# 3

echo '{"a":1,"b":2}' | jq '.[]'
# 1
# 2
```

## `.[]?`

Like `.[]` but suppresses errors on non-iterable inputs.

## Comma: `,`

The comma operator produces multiple outputs from a single input — left side first, then right side. Both sides receive the same input.

```bash
jq -n '1, 2, 3'
# 1
# 2
# 3

echo '{"a":1,"b":2}' | jq '.a, .b'
# 1
# 2
```

## Pipe: `|`

Feeds the output of the left filter into the input of the right filter. The fundamental composition operator.

```bash
echo '[1,2,3]' | jq '.[] | . * 2'
# 2
# 4
# 6
```

## Parenthesis: `( )`

Groups expressions and controls precedence. Also used to capture multiple outputs of a generator.

```bash
jq -n '[(1, 2, 3)]'
# [1, 2, 3]
```

## Array Construction: `[]`

Collects all outputs into an array.

```bash
echo '[1,2,3]' | jq '[.[] | . + 1]'
# [2, 3, 4]
```

## Object Construction: `{}`

Builds objects. Keys can be identifiers (unquoted) or expressions (in parentheses). Values reference `.` for the current input.

```bash
echo '{"firstName":"Alice","lastName":"Smith"}' | \
  jq '{first: .firstName, last: .lastName}'
# {"first":"Alice","last":"Smith"}
```

Shorthand when key name matches field name:

```bash
echo '{"name":"Alice","age":30}' | jq '{name, age}'
# {"name":"Alice","age":30}
```

Computed keys using variables (jq 1.7+):

```bash
jq -n '"dynamicKey" as $key | {$key: 123}'
# {"dynamicKey":123}
```

## Recursive Descent: `..`

Recursively descends into the data structure, producing every sub-value. Equivalent to `. , (..[]? // empty)`.

```bash
echo '{"a":[1,{"b":2}]}' | jq '..'
# {"a":[1,{"b":2}]}
# [1,{"b":2}]
# 1
# {"b":2}
# 2
```

## SQL-Style Operators

**`?//` (destructuring alternative)**: Like `//` but works during destructuring patterns.

```bash
jq -n '{"a":1} | (.c ?// 42)'
# 42
```

## Comments

jq supports C-style (`#`), C++-style (`//`), and Tcl-style multiline comments:

```jq
# Single line comment
// Also single line
# Start of block \
  this is all a comment
# End of block
```

Tcl-style blocks use trailing backslash to continue the comment on the next line.
