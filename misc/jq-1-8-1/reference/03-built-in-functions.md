# Built-in Functions

## Types and Values

**`type`**: Returns the type of input as a string: `"null"`, `"boolean"`, `"number"`, `"string"`, `"array"`, `"object"`.

```bash
jq -n 'null | type'
# "null"
```

**`tojson`**: Converts any value to its JSON representation as a string.

**`@json`**: Alias for `tojson`.

## Type Predicates

These select only inputs matching the given type (pass through if match, no output otherwise):

- `arrays` — arrays
- `objects` — objects
- `iterables` — arrays or objects
- `booleans` — true/false
- `numbers` — numeric values
- `normals` — normal (non-NaN, non-Infinity) numbers
- `finites` — finite numbers
- `strings` — string values
- `nulls` — null
- `values` — non-null values
- `scalars` — non-iterable values (null, boolean, number, string)

```bash
echo '[[],{},1,"foo",null,true]' | jq '.[] | numbers'
# 1
```

## Type Conversion

**`tonumber`**: Converts strings to numbers. Rejects strings with leading/trailing whitespace (use `trim` first).

```bash
jq -n '"42" | tonumber'
# 42
```

**`tostring`**: Converts any value to its string representation.

**`toboolean`** (1.8+): Converts `"true"` to `true`, `"false"` to `false`.

```bash
jq -n '"true" | toboolean'
# true
```

## Math

**`abs`**: Absolute value. Preserves precision for decimal numbers.

**`floor`**: Round down to nearest integer.

**`sqrt`**: Square root.

**`exp`, `log`, `log10`, `exp10`**: Exponential and logarithmic functions.

**`sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`**: Trigonometric functions.

**`infinite`**: Produces positive infinity.

**`nan`**: Produces NaN.

**`isinfinite`**, **`isnan`**, **`isfinite`**, **`isnormal`**: Test numeric properties.

## Arithmetic

Standard operators: `+`, `-`, `*`, `/`, `%`.

```bash
jq -n '10 / 3'
# 3.333...
```

**`add` / `add(generator)`** (1.8+): Sums array elements or generator outputs. Returns `null` for empty arrays.

```bash
echo '[1,2,3]' | jq 'add'
# 6

jq -n '{"xs":[1,2,3]} | .sum = add(.xs[])'
# {"xs":[1,2,3],"sum":6}
```

**`any`**, **`all`**: Boolean aggregation over arrays or generators.

```bash
echo '[true,false]' | jq 'any'
# true

echo '[1,2,3]' | jq 'any(. > 2)'
# true
```

## String Operations

**`length`**: Length of string (code points), array (elements), or object (keys). For numbers, digit count.

**`utf8bytelength`**: Byte length of a string in UTF-8 encoding.

**`split(str)`**: Split string by delimiter.

**`join(str)`**: Join array of strings with delimiter.

```bash
echo '"a,b,c"' | jq 'split(",")'
# ["a","b","c"]

echo '["a","b","c"]' | jq 'join("-")'
# "a-b-c"
```

**`explode`**: String to array of code point numbers.

**`implode`**: Array of code points to string.

**`indices(s)`**: All starting positions of substring `s`. Uses code point indices (1.8+).

**`index(s)`**, **`rindex(s)`**: First/last occurrence of substring.

**`startswith(str)`**, **`endswith(str)`**: Prefix/suffix tests.

**`ltrimstr(str)`**, **`rtrimstr(str)`**: Remove prefix/suffix string.

**`trimstr(str)`** (1.8+): Remove string from both ends.

```bash
jq -n '"foobarfoo" | trimstr("foo")'
# "bar"
```

**`trim`** (1.8+), **`ltrim`** (1.8+), **`rtrim`** (1.8+): Trim whitespace.

```bash
jq -n '"  hello  " | trim, ltrim, rtrim'
# "hello"
# "hello "
# "  hello"
```

**`ascii_downcase`**, **`ascii_upcase`**: Case conversion (ASCII only).

## Array Operations

**`sort`**, **`sort_by(expr)`**: Sort arrays. `sort_by` sorts by the expression applied to each element.

**`reverse`**: Reverse array order.

**`unique`**, **`unique_by(expr)`**: Remove duplicates.

**`min`**, **`max`**, **`min_by(expr)`**, **`max_by(expr)`**: Find minimum/maximum.

**`first(expr)`, `last(expr)`, `nth(n; expr)`**: Get first, last, or nth output of a generator.

**`limit(n; expr)`**: Limit to n outputs.

**`skip(n; expr)`** (1.8+): Skip first n outputs — counterpart to `limit`.

```bash
jq -nc '[1,2,3,4,5] | [skip(2; .[])]'
# [3,4,5]
```

**`combinations` / `combinations(n)`**: Cartesian product of arrays.

**`flatten` / `flatten(depth)`**: Flatten nested arrays.

**`bsearch(x)`**: Binary search for sorted arrays. Returns index or `-(insertion_point+1)` if not found.

## Object Operations

**`keys`**, **`keys_unsorted`**: Object keys as sorted/unsorted array. Also works on arrays (returns indices).

**`has(key)`**: Test if object has key or array has index.

**`to_entries`**, **`from_entries`**, **`with_entries(f)`**: Convert between objects and `[{"key":k,"value":v}]` arrays.

```bash
echo '{"a":1,"b":2}' | jq 'with_entries(.key |= "K_\(.)")'
# {"K_a":1,"K_b":2}
```

**`del(path)`**: Delete keys from objects or elements from arrays.

**`getpath(PATHS)`**: Get value at path (path is array of strings/numbers).

**`setpath(PATHS; VALUE)`**: Set value at path, creating intermediate structures as needed.

**`delpaths(PATHS)`**: Delete multiple paths (array of path arrays).

**`pick(pathexps)`** (1.7+): Emit projection defined by path expressions.

```bash
jq -n '{"a":1,"b":{"c":2,"d":3},"e":4} | pick(.a, .b.c, .x)'
# {"a":1,"b":{"c":2},"x":null}
```

## Map Operations

**`map(f)`**: Apply filter to each array element.

**`map_values(f)`**: Apply filter to each value in an object.

## Containment and Comparison

**`contains(element)`**: Test if input contains the given value (substring for strings, sub-structure for arrays/objects).

**`inside`**: Reverse of `contains` — test if input is inside the argument.

## Recursion

**`recurse` / `recurse(f)`**: Recursively apply filter. Without argument, equivalent to `..`. With argument, applies `f` to each output and recurses.

**`recurse(f; condition)`**: Recurse only while condition is true.

**`walk(f)`**: Apply filter to every element in the data structure, bottom-up.

```bash
echo '{"a":{"b":1},"c":{"d":2}}' | jq 'walk(if type == "number" then . * 2 else . end)'
# {"a":{"b":2},"c":{"d":2}}
```

## Conditionals

**`select(expr)`**: Pass input through if expr is true, produce no output otherwise.

```bash
echo '[1,5,3,0,7]' | jq 'map(select(. >= 2))'
# [5,3,7]
```

**`if-then-elif-else-end`**: Conditional expression (1.7+ allows `if` without `else`).

```bash
jq -n '1 | if . == 1 then "one" end'
# "one"
```

**`//` (alternative operator)**: If left side produces no output or is `false`/`null`, produce right side.

```bash
echo '{"a":1}' | jq '.b // "default"'
# "default"
```

## Logical Operators

**`and`**, **`or`**, **`not`**: Boolean logic. `not` is also available as `!`.

**`==`**, **`!=`**, **`>`**, **`>=`**, **`<`**, **`<=`**: Comparison operators.

## Error Handling

**`try expr catch handler`**: Catch errors from expr. Handler receives the error value.

**`error` / `error(message)`**: Produce an error.

**`?` (error suppression)**: Suppress errors, producing no output on failure. Equivalent to `try . catch empty`.

## Control Flow

**`while(cond; update)`**: Loop while condition is true, applying update each iteration.

**`until(cond; next)`**: Loop until condition is true.

**`repeat(expr)`**: Repeat expr indefinitely (use with `limit`).

**`empty`**: Produces no output at all. Useful for filtering.

```bash
jq -n '[1, 2, empty, 3]'
# [1,2,3]
```

**`halt`**: Stop jq program with exit status 0.

**`halt_error` / `halt_error(exit_code)`**: Stop with error message on stderr and given exit code (default 5).

**`$__loc__`**: Object with `"file"` and `"line"` keys showing where `$__loc__` occurs in the filter.

## Paths

**`path(expr)`**: Outputs array representation of a path expression.

**`paths` / `paths(node_filter)`**: Outputs paths to all elements (or matching elements).

```bash
echo '[1,[[],{"a":2}]]' | jq '[paths(type == "number")]'
# [[0],[1,1,"a"]]
```

## Grouping

**`group_by(expr)`**: Group array elements by expression. Produces sorted groups.

```bash
echo '[{"t":"a","v":1},{"t":"b","v":2},{"t":"a","v":3}]' | \
  jq 'group_by(.t) | map({type: .[0].t, values: [.[].v]})'
```

## String Interpolation

`\(expr)` embeds expression output within a string.

```bash
jq -n '"The answer is \((6 * 7))"'
# "The answer is 42"
```

## Format Strings

**`@text`**: Human-readable text output.

**`@json`**: JSON encoding.

**`@html`**: HTML-escaped output.

**`@xml`**: XML-escaped output.

**`@csv`**: CSV row output.

**`@tsv`**: TSV row output.

**`@sh`**: Shell-escaped output.

**`@base64`**, **`@base64d`**: Base64 encode/decode.

**`@base64url`**, **`@base64url`**: URL-safe base64.

**`@uri`**, **`@urid`** (1.8+): URI encode/decode.

```bash
jq -n '"hello world" | @uri'
# "hello%20world"

jq -Rr '@urid' <<< '%6a%71'
# jq
```

## Dates

All date functions work in UTC.

**`now`**: Current time as seconds since Unix epoch.

**`fromdateiso8601`**: Parse ISO 8601 datetime string to epoch seconds.

**`todateiso8601`** / **`todate`**: Epoch seconds to ISO 8601 string.

**`fromdate`**: Parse datetime string (currently ISO 8601 only).

Low-level C library interfaces:

- `strptime(fmt)` — parse string to date-time array
- `strftime(fmt)` — format date-time array to string (UTC)
- `strflocaltime(fmt)` — format with local timezone
- `mktime` — date-time array to epoch seconds
- `gmtime` — epoch seconds to UTC date-time array
- `localtime` — epoch seconds to local date-time array

Date-time arrays: `[year, month(0-based), day, hour, minute, second, day_of_week, day_of_year]`.

## Regular Expressions

Uses Oniguruma library (PCRE-compatible). Flags: `g` (global), `i` (case-insensitive), `m` (multiline), `s` (dotall), `p` (paragraph).

**`test(re)` / `test(re; flags)`**: Test if string matches regex.

**`match(re)` / `match(re; flags)`**: Return match object with `.string`, `.line`, `.lineoffset`, `.offset`, and `.captures[]`.

**`capture(re)` / `capture(re; flags)`**: Extract named capture groups as an object.

```bash
jq -n '"foo=1&bar=2" | capture("(?<key>[^=]+)=(?<val>[^&]+)")'
# {"key":"foo","val":"1"}
```

**`scan(re)` / `scan(re; flags)`** (1.7+): Find all non-overlapping matches.

**`split(re; flags)`**: Split by regex pattern.

**`splits(re)`**: Generate each piece between regex matches.

**`sub(re; to)` / `sub(re; to; flags)`**: Replace first match.

**`gsub(re; to)` / `gsub(re; to; flags)`**: Replace all matches.

```bash
jq -n '"hello world" | gsub("o"; "0")'
# "hell0 w0rld"
```

## Miscellaneous

**`builtins`**: List all available builtin functions.

**`builtins("pattern")`**: Filter builtins by pattern.

**`have_literal_numbers`**: `true` if jq was built with decimal number support.

**`have_decnum`**: `true` if jq was built with libdecnumber.

**`$JQ_BUILD_CONFIGURATION`**: Build configuration object (read-only).

**`transpose`**: Transpose a matrix (array of arrays).
