# Core Filters and Operators

## Identity and Access

```bash
# Pretty-print JSON input
cat data.json | jq '.'

# Extract single field
echo '{"name":"Alice","age":30}' | jq '.name'
# "Alice"

# Nested access
echo '{"user":{"name":"Alice"}}' | jq '.user.name'
# "Alice"

# Array element access
echo '[1,2,3,4,5]' | jq '.[2]'
# 3

# Array slice (start inclusive, end exclusive)
echo '[1,2,3,4,5]' | jq '.[1:4]'
# [2, 3, 4]

# Access with special characters in key
echo '{"foo-bar":1}' | jq '.["foo-bar"]'
# 1
```

### Object Identifier-Index

The `.foo` syntax only works for simple, identifier-like keys (alphanumeric + underscore, not starting with digit). For special characters or digits at start, use bracket notation:

```bash
echo '{"foo$":1}' | jq '.["foo$"]'       # Works
echo 'null' | jq '.["0key"]'              # Works (digit at start)
```

### Array-Object Value Iterator

`.[]` iterates over all elements of an array or values of an object:

```bash
# Iterate over array elements
echo '[1,2,3]' | jq '.[]'
# 1
# 2
# 3

# Iterate over object values
echo '{"a":1,"b":2}' | jq '.[]'
# 1
# 2

# Collect iteration results into an array
echo '[1,2,3]' | jq '[.[] * 2]'
# [2, 4, 6]
```

## Operators

### Pipe Operator (`|`)

Feeds output of one filter into another:

```bash
echo '{"users":[{"name":"Alice"},{"name":"Bob"}]}' \
  | jq '.users | map(.name)'
# ["Alice", "Bob"]
```

### Comma Operator (`,`)

Produces multiple results:

```bash
echo '{"a":1,"b":2}' | jq '.a, .b'
# 1
# 2
```

### Parentheses (`()`)

Group expressions and control precedence:

```bash
echo '[1,2,3]' | jq 'add / length'           # (1+2+3) / 3 = 2
echo '[1,2,3]' | jq 'add / (length * 2)'     # 6 / 6 = 1
```

## Arithmetic Operators

```bash
echo 'null' | jq -n '2 + 3 * 4'              # 14
echo 'null' | jq -n '10 / 3'                 # 3.333...
echo 'null' | jq -n '10 % 3'                 # 1 (modulo)
echo 'null' | jq -n '2 | pow(3)'             # 9 (a raised to power c)
echo 'null' | jq -n '16 | sqrt'              # 4
echo 'null' | jq -n '-5 | abs'               # 5
echo 'null' | jq -n '3.7 | floor'            # 3
```

## Comparison and Conditionals

### Equality and Ordering

```bash
# Equality / inequality
echo '{"a":1}' | jq '.a == 1'                # true
echo '{"a":1}' | jq '.a != 1'                # false

# Ordering (numbers and strings)
echo '[3,1,2]' | jq 'sort'                   # [1, 2, 3]
```

### If-Then-Else

```bash
echo 'null' | jq -n 'if 5 > 3 then "yes" else "no" end'
# "yes"
```

### Alternative Operator (`//`)

Returns left operand if not `false` or `null`, otherwise right:

```bash
echo '{"a":null}' | jq '.a // "default"'     # "default"
echo '{"a":1}'   | jq '.a // "default"'      # 1
```

### Try-Catch and Optional Access

```bash
# try-catch error handling
echo 'null' | jq -n 'try (error("oops")) catch "caught"'
# "caught"

# Optional access (?.) — no error on null path
echo '{"a":{"b":1}}' | jq '.a.b.c?'          # null (no error)
echo '{"a":null}' | jq '.a?.b'               # null

# Error suppression with ? at end of filter
```

## String Functions

### Split and Join

```bash
echo '"hello,world,foo"' | jq 'split(",") | .[]'
# "hello"  "world"  "foo"

echo '["a","b","c"]' | jq 'join("-")'        # "a-b-c"
```

### Trim and Case

```bash
echo '"  hello  "' | jq 'trim'               # "hello"
echo '"  hello  "' | jq 'ltrim'              # "hello  "
echo '"  hello  "' | jq 'rtrim'              # "  hello"
echo '"Hello World"' | jq 'ascii_upcase'     # "HELLO WORLD"
echo '"Hello World"' | jq 'ascii_downcase'   # "hello world"
```

### Explode / Implode

```bash
echo '"hello"' | jq '[. | explode]'           # [104, 101, 108, 108, 111]
echo '[104,101,108,108,111]' | jq 'implode'   # "hello"
```

### String Interpolation

```bash
echo 'null' | jq -n --arg name Alice '"Hello, \($name)!"'
# "Hello, Alice!"
```

### Substring Operations

```bash
echo '"hello world"' | jq 'startswith("hel")' # true
echo '"hello world"' | jq 'endswith("rld")'   # true
echo '"hello world"' | jq 'ltrimstr("hel")'   # "lo world"
echo '"hello world"' | jq 'rtrimstr("rld")'   # "hello wo"
```

## Array Functions

### Sort and Unique

```bash
echo '[3,1,4,1,5,9,2,6]' | jq 'sort'          # [1, 1, 2, 3, 4, 5, 6, 9]
echo '[3,1,4,1,5,9,2,6]' | jq 'unique'        # [1, 2, 3, 4, 5, 6, 9]
echo '[{"a":3},{"a":1}]' | jq 'sort_by(.a)'   # sorted by field a
```

### Grouping

```bash
echo '[{"g":"a","v":1},{"g":"b","v":2},{"g":"a","v":3}]' \
  | jq 'group_by(.g)'
# [[{"g":"a","v":1},{"g":"a","v":3}],[{"g":"b","v":2}]]
```

### Min / Max

```bash
echo '[3,1,4,1,5]' | jq 'min'                 # 1
echo '[3,1,4,1,5]' | jq 'max'                 # 5
echo '[3,1,4,1,5]' | jq 'min_by(. + 0)'       # 1
```

### Flatten and Transpose

```bash
echo '[[1],[2],[3]]' | jq 'flatten'           # [1, 2, 3]
echo '[[[1]], [[2]]]' | jq 'flatten(1)'       # [[1], [2]]
echo '[[1,2],[3,4]]' | jq 'transpose'         # [[1,3],[2,4]]
```

### Map Operations

```bash
echo '[1,2,3]' | jq 'map(. * 2)'              # [2, 4, 6]
echo '[{"a":1},{"a":2}]' | jq 'map_values(.a + 10)'  # [{"a":11},{"a":12}]
```

### Combinations (Cartesian Product)

```bash
# All length-3 arrays from [1,2]
echo '[1,2]' | jq 'combinations(3)'
# [1,1,1] [1,1,2] [1,2,1] [1,2,2] [2,1,1] ... [2,2,2]
```

## Object Manipulation

### Keys and Has

```bash
echo '{"b":2,"a":1,"c":3}' | jq 'keys'        # ["a","b","c"]
echo '{"b":2,"a":1}' | jq 'has("a")'          # true
echo '{"b":2,"a":1}' | jq 'has("z")'          # false

# to_entries / from_entries / with_entries
echo '{"a":1,"b":2}' | jq 'to_entries'
# [{"key":"a","value":1},{"key":"b","value":2}]
```

### Del and Path Operations

```bash
# Delete field
echo '{"a":1,"b":2,"c":3}' | jq 'del(.b)'     # {"a":1,"c":3}

# setpath — set value at path
echo '{"a":{"b":1}}' | jq 'setpath(["x","y"]; 42)'
# {"a":{"b":1},"x":{"y":42}}

# delpath — delete at path
echo '{"a":{"b":1}}' | jq 'delpath(["a","b"])' # {"a":{}}

# delpaths — delete multiple paths
echo '[{"a":1},{"b":2}]' | jq 'delpaths([[0,"a"]])'  # [{},{"b":2}]

# getpath — get value at path
echo '{"a":{"b":1}}' | jq 'getpath(["a","b"])'   # 1

# pick — extract multiple fields
echo '{"a":1,"b":2,"c":3}' | jq 'pick(.a, .c)'  # {"a":1,"c":3}
```

### Recursive Descent

```bash
# //. — descend into all nested objects/arrays
echo '{"a":{"b":1},"c":{"d":{"b":2}}}' | jq '[.. | .b?]'
# [1, 2]

# walk() — recursively transform every element
echo '{"a":[1,2],"b":{"c":[3,4]}}' \
  | jq 'walk(if type == "array" then sort else . end)'
```

## Select and Filtering

```bash
# select() — keep only matching elements
echo '[1,2,3,4,5]' | jq '.[] | select(. > 3)'    # 4, 5
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 3)]'  # [4, 5]

# inside — check containment
echo '{"a":1}' | jq 'inside({"a":1,"b":2})'      # true
```
