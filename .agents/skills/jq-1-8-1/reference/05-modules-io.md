# Modules and I/O

## Module System

jq has a library/module system. Modules are files ending in `.jq`.

### Import and Include

**`import RelativePathString as NAME [<metadata>];`**: Imports a module. The module's symbols are prefixed with `NAME::`. A `.jq` suffix is added automatically.

```jq
import "mylib" as M;
M::myfunction
```

**`include RelativePathString [<metadata>];`**: Like import but symbols are imported directly into the current namespace (no prefix).

### Search Path

Modules are searched in a default search path:

1. Paths given with `-L` / `--library-path`
2. `~/.jq`
3. `$ORIGIN/../lib/jq`
4. `$ORIGIN/../lib`

Path substitutions:
- `~/` → user's home directory
- `$ORIGIN/` → directory containing jq executable
- `./` or `.` → directory of the including file (current directory for top-level programs)

A dependency with relative path `foo/bar` searches for `foo/bar.jq` and `foo/bar/bar.jq`. Consecutive components with the same name are not allowed (e.g., `foo/foo`).

If `.jq` exists in the user's home directory as a file, it is automatically sourced into every program.

### Module Declaration

**`module <metadata>;`**: Optional metadata declaration at the top of a module file.

```jq
module {description: "Math utilities", version: "0.1.0"};
def add($x; $y): $x + $y;
def subtract($x; $y): $x - $y;
```

**`modulemeta`**: Read-only variable containing the current module's metadata object.

## I/O Functions

### input / inputs

**`input`**: Read the next JSON value from the input stream (not from stdin directly, but from jq's parsed input).

**`inputs`**: Read all remaining JSON values from the input stream as a generator.

These work with multiple input files or when `-n` is used:

```bash
echo '{"a":1} {"b":2}' | jq -n '[inputs]'
# [{"a":1},{"b":2}]
```

### input_filename / input_line_number

**`input_filename`**: Returns the filename of the current input source.

**`input_line_number`**: Returns the line number of the current input value.

### debug / stderr

**`debug`**: Write the current input to stderr as a JSON array `["DEBUG:", <value>]`. Passes input through unchanged.

**`debug(msgs)`** (1.7+): Like debug but applies a filter to produce debug messages.

```bash
jq -n '1 as $x | 2 | debug("x is \($x)", .) | (. + 1)'
# ["DEBUG:","x is 1"]
# ["DEBUG:",2]
# 3
```

**`stderr`**: Write the current value to stderr as raw output (strings without quotes).

## Streaming

With `--stream`, jq parses input in streaming fashion, outputting `[path, leaf-value]` arrays. This allows processing very large JSON files without loading them entirely into memory.

Streaming forms:
- `[path, leaf-value]` — scalar value, empty array, or empty object at the given path
- `[path]` — end of an array or object

### tostream

Converts a value to its streamed form:

```bash
echo '["a",["b"]]' | jq 'tostream'
# [[0],"a"]
# [[1,0],"b"]
# [[1,0]]
# [[1]]
```

### fromstream

Reconstructs values from stream expressions:

```bash
jq -n 'fromstream([[0],"a"],[[1,0],"b"],[[1,0]],[[1]])'
# ["a",["b"]]
```

### truncate_stream

Truncates path elements from the left of stream outputs. Takes a number as input:

```bash
jq -n '1 | truncate_stream([[0],"a"],[[1,0],"b"],[[1,0]],[[1]])'
# [[0],"b"]
# [[0]]
```

### Practical Streaming

Combine `--stream` with `reduce` to process large files incrementally:

```bash
jq -n --stream '
  [0] as $trunc |
  reduce (inputs | truncate_stream($trunc)) as $x (
    {};
    if ($x | length) == 2 then
      . + {($x[1]): null}
    else . end
  )
' large-file.json
```

## Environment Variables

**`$ENV`**: Read-only object mapping environment variable names to values.

```bash
jq -n '$ENV.HOME'
# "/home/user"
```

**`env`**: Same as `$ENV` — returns the environment as an object.
