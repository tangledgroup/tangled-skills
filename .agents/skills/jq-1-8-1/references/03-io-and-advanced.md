# I/O, Modules, and Advanced Topics

## Input/Output Control

### Reading Non-JSON Input

```bash
# Read raw text lines as strings (not parsed as JSON)
echo -e "hello\nworld" | jq -R '.'
# "hello"
# "world"

# Slurp all input into a single string
echo -e "hello\nworld" | jq -Rs '.'
# "hello\nworld\n"

# Combine raw + slurp: entire input as one string
echo -e "line1\nline2" | jq -Rs 'split("\n")'
# ["line1", "line2", ""]
```

### Reading Files and Variables

```bash
# Pass shell variable as jq string variable
name="Alice"
jq --arg name "$name" '{user: $name}' <<< 'null'
# {"user":"Alice"}

# Pass shell variable as JSON value (not string)
count=42
jq --argjson count "$count" '{total: $count}' <<< 'null'
# {"total":42}

# Read all JSON from file into array
jq --slurpfile data other.json '. + $data' input.json

# Read raw file content as string
jq --rawfile content config.txt '{config: $content}' <<< 'null'

# Positional arguments (as strings)
jq -n --args '[.ARGS.positional[]]' -- foo bar baz
# ["foo", "bar", "baz"]

# JSON positional arguments
jq -n --jsonargs '[.ARGS.positional[]]' -- '{"a":1}' 2
# [{"a":1}, 2]
```

### Output Control

```bash
# Compact output (one object per line)
echo '[{"a":1},{"b":2}]' | jq -c '.[]'
# {"a":1}
# {"b":2}

# Raw output (strings without quotes)
echo '{"name":"Alice"}' | jq -r '.name'
# Alice

# NUL-separated raw output
jq --raw-output0 '.' data.json    # NUL after each output

# Sort keys in output
echo '{"z":3,"a":1,"m":2}' | jq -S '.'
# {"a":1,"m":2,"z":3}

# Color control (for scripting)
jq -M '.name' data.json          # monochrome (no color escapes)
```

### Input/Output Functions

```bash
# input — read next JSON value from stdin
echo '[{"a":1},{"b":2}]' | jq '[.[]] | input'   # reads second element

# inputs — iterate over all remaining JSON values
echo '{"a":1}' | jq '[inputs]'                   # [] (no more input after first)

# input_filename — name of current input file (with -f or multiple files)
jq '{file: input_filename, data: .}' file.json

# input_line_number — line number in current input file
```

## Assignment and Update

### Plain Assignment

```bash
echo '{"a":1,"b":2}' | jq '.a = 99'              # {"a":99,"b":2}
echo '[1,2,3]' | jq '.[0] = "x"'                 # ["x",2,3]
```

### Delete

```bash
echo '{"a":1,"b":2,"c":3}' | jq 'del(.b)'        # {"a":1,"c":3}
echo '[1,2,3]' | jq 'del(.[1])'                   # [1,3]
```

### Update Assignment (`|=`)

```bash
# Apply filter to existing value in-place
echo '[1,2,3]' | jq '.[1] |= . * 10'             # [1,20,3]
echo '{"a":1}' | jq '.a += 10'                    # {"a":11}

# Update nested values
echo '{"a":{"b":1}}' | jq '.a.b |= . * 100'      # {"a":{"b":100}}
```

### Complex Assignment with Paths

```bash
# setpath — set value at path (creates intermediate objects)
echo '{"a":{"b":1}}' | jq 'setpath(["c","d"]; 42)'   # adds {"c":{"d":42}}

# delpath — delete at specific path
echo '{"a":{"b":1,"c":2}}' | jq 'delpath(["a","b"])'  # {"a":{"c":2}}

# delpaths — delete multiple paths at once
echo '[{"a":1},{"b":2}]' | jq 'delpaths([[0,"a"]])'   # [{},{"b":2}]
```

## Error Handling

### try-catch

```bash
echo 'null' | jq -n 'try (error("oops")) catch "recovered"'
# "recovered"

# Multiple catches with different handlers
jq 'try process_data() catch (. // empty)' data.json
```

### halt and halt_error

```bash
# halt — stop processing immediately
echo 'null' | jq -n 'halt'                        # no output, exit 0

# halt_error(n) — stop with given exit status
echo 'null' | jq -n 'halt_error(1)'               # exit 1
```

### stderr Output

```bash
# Write to stderr (doesn't affect stdout JSON)
echo 'null' | jq -n '"processing..." | stderr'    # "processing..." on stderr
```

## Modules

### Creating and Using Modules

Create a module file `math.jq`:

```jq
def factorial: if . <= 1 then 1 else . * ((. - 1) | factorial) end;
def fibonacci: if . <= 1 then . else (. - 1 | fibonacci) + ((. - 2) | fibonacci) end;
```

Use with `include` or `import`:

```bash
# include — inline the module code
echo 'null' | jq -n 'include "math"; factorial(5)'   # 120

# import as binding
echo 'null' | jq -n 'import "math" as M; M.factorial(5)'

# List library path
jq --library-path /path/to/modules -n '1'
```

### Module Metadata

In the `.jq` file, declare metadata:

```jq
module meta { "author": "...", "version": "1.0" }

def my_function: ...;
```

## Streaming

For very large JSON files that won't fit in memory:

```bash
# Stream parse — outputs [path, value] for each leaf
jq --stream '[.[] | select(.path[0] == 3)]' huge.json

# tostream / fromstream — convert between streaming and normal format
echo '{"a":[1,2],"b":[3,4]}' | jq 'tostream'
# [0,"a"] [0,0] 1 ... etc.

# truncate_stream — limit recursion depth in streaming
```

## Type System

### Type Checking

```bash
echo '"hello"' | jq 'type'                       # "string"
echo '42' | jq 'type'                            # "number"
echo 'true' | jq 'type'                          # "boolean"
echo 'null' | jq 'type'                          # "null"
echo '[1,2]' | jq 'type'                         # "array"
echo '{"a":1}' | jq 'type'                       # "object"

# Check for empty
echo 'empty' | jq 'isempty'                      # true (produces no output)
echo '42' | jq 'isempty'                         # false
```

### Number Checks

```bash
echo '1.5' | jq 'isfinite'                        # true
echo 'nan' | jq 'isnan'                           # true
echo 'inf' | jq 'is_infinite'                     # true
echo '1' | jq 'isnormal'                          # true
```

### Type Conversion

```bash
# String to number / number to string
echo '"42"' | jq 'tonumber'                       # 42
echo '42' | jq 'tostring'                         # "42"

# Boolean conversion
echo '"true"' | jq 'toboolean'                    # true
echo '0' | jq 'toboolean'                        # false
echo '1' | jq 'toboolean'                        # true

# Number to JSON / JSON to number
echo '42' | jq 'tojson'                           # "42"
echo '"42"' | jq 'tonumber'                       # 42

# String encoding
echo '"hello"' | jq '[. | explode]'              # [104, 101, 108, 108, 111]
echo '[104,101,108,108,111]' | jq 'implode'      # "hello"

# UTF-8 byte length
echo '"café"' | jq 'utf8bytelength'               # 5 (UTF-8 bytes)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JQ_COLORS` | Configure terminal output colors (7 values, format: `"BOLD;FG;BG;effects~..."`) |
| `NO_COLOR` | If set, disables colored output by default |

```bash
# Custom color scheme
export JQ_COLORS="1;36;40;0~1;31;40;0~1;32;40;0~1;33;40;0~1;34;40;0~1;35;40;0~1;37;40;0"
```

## Defining User-Defined Functions

```bash
# Define a function in a file or inline
echo '[1,2,3,4,5]' | jq 'def double: . * 2; [., double]'
# [[1,2,3,4,5], [2,4,6,8,10]]

# Function with parameters
echo 'null' | jq -n 'def add($a; $b): $a + $b; add(3; 4)'   # 7

# Recursive function
echo 'null' | jq -n 'def fac: if . <= 1 then 1 else . * ((. - 1) | fac) end; fac(5)'  # 120
```

## Scoping and Variable Binding

```bash
# Variable binding with `as`
echo '[1,2,3]' | jq '. as $arr | [$arr, ($arr | length)]'
# [[1,2,3], 3]

# Multiple variable bindings
echo '{"a":1,"b":2}' | jq '(.a as $x | .b as $y | {sum: ($x + $y), prod: ($x * $y)})'
# {"sum":3,"prod":2}

# $env — access environment variables
echo 'null' | jq -n '$env.HOME'
```

## Build Configuration Info

```bash
# Check if decnum (high-precision decimal) is available
echo 'null' | jq -n 'have_decnum'                       # true or false

# Check literal number support
echo 'null' | jq -n 'have_literal_numbers'              # true or false

# Access build configuration as $jq.build_configuration
echo 'null' | jq -n '$jq.build_configuration'
```

## Performance Tips

```bash
# ✅ Use select() early to filter before expensive operations
jq '[.[] | select(.active) | expensive_operation]' data.json

# ✅ Bind intermediate results to variables with `as`
jq '[.users as $u | $u | map(.name)]' data.json

# ✅ Use `walk()` for deep transforms instead of manual recursion
jq 'walk(if type == "number" then . * 2 else . end)' data.json

# ❌ Avoid unnecessary iteration in nested loops
# Instead of: [.[] | .items[] | .value]
# Consider: [.[].items[].value]

# ✅ For large files, use --stream to process incrementally
jq --stream '[.[] | select(.path[0] == "users")]' huge.json

# ✅ Use -c (compact output) when piping between commands
jq -c '.users | length' data.json
```

## Common Pitfalls

```bash
# . produces no output for empty — use // or ? to handle
echo 'null' | jq '.a.b // "default"'     # "default"
echo 'null' | jq '.a.b?'                  # null (no error)

# String interpolation requires proper input context
jq -n --arg name Alice '"Hello, \($name)"'   # Correct
echo '{"name":"Alice"}' | jq '"Hello, \(.name)"'  # Also works

# reduce state variable scope — use standard pattern:
# reduce .[] as $item ($init; update)

# Division by zero produces null in some builds
echo 'null' | jq -n '5 / 0'                  # null (in some builds)

# Empty produces no output — wrap in array if needed
echo '[1,2,3]' | jq '[.[] | select(. > 10)]'   # [] (empty array, not empty)
```
