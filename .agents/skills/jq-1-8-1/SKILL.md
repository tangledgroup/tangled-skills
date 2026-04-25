---
name: jq-1-8-1
description: Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing, transforming, filtering, or generating JSON data from the shell, piping between commands, processing API responses, or writing reusable JSON transformation scripts with a concise declarative query language.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.8.1"
tags:
  - JSON
  - command-line
  - data transformation
  - shell scripting
  - text processing
category: developer-tools
external_references:
  - https://jqlang.org/
  - https://github.com/jqlang/jq/releases/tag/jq-1.8.1
  - https://play.jqlang.org
  - https://stackoverflow.com/questions/tagged/jq
  - https://web.libera.chat/#jq
  - https://jqlang.org/manual/
  - https://jqlang.org/tutorial/
  - https://github.com/jqlang/jq
---

# jq 1.8.1

## Overview

Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing, transforming, filtering, or generating JSON data from the shell, piping between commands, processing API responses, or writing reusable JSON transformation scripts with a concise declarative query language.

jq is a lightweight and flexible command-line JSON processor, often described as "sed for JSON". It is written in portable C with zero runtime dependencies — a single binary that can be copied to any machine of the same architecture and work immediately.

## When to Use

- **Parsing JSON**: Extract specific fields from JSON documents or API responses
- **Transforming JSON**: Restructure, reshape, or reformat JSON data between different schemas
- **Filtering JSON**: Select only elements matching certain criteria from arrays or objects
- **Generating JSON**: Construct JSON objects and arrays programmatically from non-JSON input
- **Shell pipelines**: Chain jq with curl, grep, awk, sed, or any command producing/consuming JSON
- **Data validation**: Validate JSON structure and extract values for shell variable assignment
- **Report generation**: Aggregate, sort, group, and summarize data from JSON sources

## Installation

### Download Pre-built Binary

```bash
# Linux (AMD64)
curl -L "https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-linux-amd64" -o jq
chmod +x jq && mv jq /usr/local/bin/

# Linux (ARM64)
curl -L "https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-linux-arm64" -o jq
chmod +x jq && mv jq /usr/local/bin/

# macOS (Apple Silicon)
curl -L "https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-macos-arm64" -o jq
chmod +x jq && mv jq /usr/local/bin/

# macOS (Intel Mac)
curl -L "https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-macos-amd64" -o jq
chmod +x jq && mv jq /usr/local/bin/

# Windows (AMD64)
# Download https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-windows-amd64.exe
```

### Package Managers

```bash
# Debian/Ubuntu, RHEL/Fedora, Arch, Alpine
sudo apt install jq          # Debian/Ubuntu
sudo dnf install jq          # Fedora/RHEL
sudo pacman -S jq            # Arch
sudo apk add jq              # Alpine

# macOS (Homebrew)
brew install jq

# Nix
nix-env -iA nixpkgs.jq

# Windows (winget)
winget install jqlang.jq
```

## Basic Usage

### Invoking jq

jq filters run on a stream of JSON data. The input is parsed as whitespace-separated JSON values, passed through the filter one at a time, and outputs are written to stdout as newline-separated JSON.

```bash
# Identity — pretty-print JSON input
cat data.json | jq '.'

# Read from file
jq '.foo' input.json

# From stdin pipe
curl -s 'https://api.github.com/repos/jqlang/jq' | jq '.name, .stargazers_count'

# Shell quoting: always single-quote the jq program on Unix
jq '.users | length' data.json
```

**Quoting rules:**
- **Unix shells**: `jq '.["foo"]'` (single quotes around program)
- **PowerShell**: `jq '.[\"foo\"]'` (single quotes, escaped double quotes)
- **Windows cmd.exe**: `jq ".[\"foo\"]"` (double quotes, escaped inner quotes)

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--null-input` | `-n` | No input; filter runs once with `null`. Use for constructing JSON or as a calculator. |
| `--raw-input` | `-R` | Read each line of input as a string (not parsed as JSON). |
| `--slurp` | `-s` | Read all input into an array, run filter once. |
| `--compact-output` | `-c` | Output one JSON object per line (no pretty-printing). |
| `--raw-output` | `-r` | Output strings without quotes. |
| `--raw-output0` | — | Like `-r` but uses NUL (`\0`) instead of newline as separator. |
| `--join-output` | `-j` | Like `-r` but no trailing newline after each output. |
| `--ascii-output` | `-a` | Force ASCII output with escape sequences for non-ASCII. |
| `--sort-keys` | `-S` | Output object keys in sorted order. |
| `--color-output` / `--monochrome-output` | `-C` / `-M` | Force color or disable color on terminal output. |
| `--tab` | — | Use tab for indentation instead of two spaces. |
| `--indent n` | — | Use `n` spaces (1-7) for indentation. |
| `--unbuffered` | — | Flush output after each JSON object. |
| `--stream` | — | Streaming parse: outputs `[path, value]` arrays for leaf values. |
| `-f file` | `--from-file` | Read filter from a file. |
| `--arg name value` | — | Pass a string value as `$name` variable. |
| `--argjson name JSON-text` | — | Pass a JSON value (not string) as `$name`. |
| `--slurpfile var filename` | — | Read all JSON texts from file into array bound to `$var`. |
| `--rawfile var filename` | — | Read file content as a string bound to `$var`. |
| `--args` / `--jsonargs` | — | Positional string/JSON arguments (`$ARGS.positional`). |
| `--exit-status` | `-e` | Exit 0 if last output is not false/null; exit 1 if it is. |

## Core Concepts

### The Filter Model

A jq program is a **filter**: it takes an input and produces an output. Every filter has both an input and an output. Even literals like `"hello"` or `42` are filters — they take an input but always produce the same literal as output.

```
input → [filter] → output
```

Filters can be combined:
- **Pipe** (`|`): Feed output of one filter into another
- **Collect**: Wrap results in array with `[...]` or `...[]`
- **Compose**: Apply multiple operations on the same input

### Key Syntax Patterns

```jq
.                          # Identity — pass through unchanged
.foo                       # Extract field "foo" from object
.foo.bar                   # Chained: .foo | .bar
.["foo-bar"]               # Access keys with special characters
.[0]                       # Array index access
.[1:3]                     # Slice array elements 1 through 2
[]                         # Empty array — produces no output
{key: value}               # Construct object
[expr1, expr2]             # Construct array
.[]                        # Iterate over all elements of array/object
```

## Essential Operations

### Identity and Access

```bash
# Pretty-print JSON
echo '{"name":"Alice","age":30}' | jq '.'

# Extract single field
echo '{"name":"Alice","age":30}' | jq '.name'
# "Alice"

# Nested access
echo '{"user":{"name":"Alice"}}' | jq '.user.name'
# "Alice"

# Array element and slice
echo '[1,2,3,4,5]' | jq '.[2]'     # 3
echo '[1,2,3,4,5]' | jq '.[1:4]'   # [2, 3, 4]

# Special character keys
echo '{"foo-bar":1}' | jq '.["foo-bar"]'  # 1
```

### Iteration and Array Operations

```bash
# Iterate over all elements
echo '[1,2,3]' | jq '.[]'           # 1, 2, 3 (separate outputs)
echo '{"a":1,"b":2}' | jq '.[]'     # 1, 2

# Collect into array
echo '[1,2,3]' | jq '[.[] * 2]'    # [2, 4, 6]

# Get keys / entries
echo '{"a":1,"b":2}' | jq 'keys'              # ["a", "b"]
echo '{"a":1,"b":2}' | jq 'to_entries'        # [{"key":"a","value":1},...]
```

### Object Construction

```bash
echo '{"name":"Alice","age":30}' | jq '{full_name: .name, is_adult: (.age >= 18)}'
# {"full_name":"Alice","is_adult":true}
```

### Arithmetic and Comparison

```bash
echo 'null' | jq -n '2 + 3 * 4'          # 14
echo 'null' | jq -n '10 % 3'              # 1
echo 'null' | jq -n '16 | sqrt'            # 4
echo 'null' | jq -n '-5 | abs'             # 5

echo '{"a":1}' | jq '.a == 1'              # true
echo '[3,1,2]' | jq 'sort'                  # [1, 2, 3]
echo 'null' | jq -n 'if 5 > 3 then "yes" else "no" end'  # "yes"

# Alternative operator (//) — returns left if not false/null
echo '{"a":null}' | jq '.a // "default"'   # "default"
```

### String Operations

```bash
echo '"hello,world"' | jq 'split(",") | .[]'      # "hello"  "world"
echo '["a","b"]' | jq 'join("-")'                  # "a-b"
echo '"  hello  "' | jq 'trim'                      # "hello"
echo '"Hello"' | jq 'ascii_upcase'                  # "HELLO"
echo 'null' | jq -n --arg name Alice '"Hi, \($name)"'  # "Hi, Alice!"
```

### Array Functions

```bash
echo '[3,1,4,1,5]' | jq 'sort'           # [1, 1, 3, 4, 5]
echo '[3,1,4,1,5]' | jq 'unique'         # [1, 3, 4, 5]
echo '[{"g":"a","v":1},{"g":"a","v":2}]' | jq 'group_by(.g)'
echo '[3,1,4]' | jq 'min'                # 1
echo '[[1],[2]]' | jq 'flatten'          # [1, 2]
echo '[1,2,3]' | jq 'map(. * 2)'         # [2, 4, 6]
```

### Object Manipulation

```bash
echo '{"b":2,"a":1}' | jq 'keys'              # ["a","b"]
echo '{"a":1}' | jq 'has("a")'                # true
echo '{"a":1,"b":2}' | jq 'del(.b)'           # {"a":1}
echo '{"a":{"b":1}}' | jq 'setpath(["x"]; 42)' # adds {"x":42}
echo '{"a":1,"b":2,"c":3}' | jq 'pick(.a,.c)' # {"a":1,"c":3}

# Recursive descent — find all .b values in nested objects
echo '{"a":{"b":1},"c":{"d":{"b":2}}}' | jq '[.. | .b?]'  # [1, 2]
```

### Selection and Filtering

```bash
echo '[1,2,3,4,5]' | jq '.[] | select(. > 3)'     # 4, 5
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 3)]'   # [4, 5]
```

### Generators and Iteration

```bash
echo 'null' | jq -n '[range(5)]'                  # [0, 1, 2, 3, 4]
echo 'null' | jq -n '[range(2;6)]'                # [2, 3, 4, 5]
echo '[1,2,3]' | jq 'reduce .[] as $x (0; . + $x)'  # 6 (sum)
```

## Input/Output Control

### Reading Non-JSON Input

```bash
# Read raw text lines as strings
echo -e "hello\nworld" | jq -R '.'
# "hello"  "world"

# Slurp all input into a single string
echo -e "line1\nline2" | jq -Rs 'split("\n")'     # ["line1", "line2", ""]
```

### Reading Files and Variables

```bash
name="Alice"
jq --arg name "$name" '{user: $name}' <<< 'null'      # {"user":"Alice"}

count=42
jq --argjson count "$count" '{total: $count}' <<< 'null'  # {"total":42}

jq --slurpfile data other.json '. + $data' input.json
jq --rawfile content config.txt '{config: $content}' <<< 'null'
```

### Output Control

```bash
echo '[{"a":1},{"b":2}]' | jq -c '.[]'       # one per line, no pretty-print
echo '{"name":"Alice"}' | jq -r '.name'       # Alice (no quotes)
echo '{"z":3,"a":1}' | jq -S '.'              # {"a":1,"z":3} (sorted keys)
```

## Type System and Conversion

### Type Checking

```bash
echo '"hello"' | jq 'type'     # "string"
echo '42' | jq 'type'          # "number"
echo 'true' | jq 'type'        # "boolean"
echo 'null' | jq 'type'        # "null"
echo '[1,2]' | jq 'type'       # "array"
echo '{"a":1}' | jq 'type'     # "object"
```

### Type Conversion

```bash
echo '"42"' | jq 'tonumber'        # 42
echo '42' | jq 'tostring'          # "42"
echo '"true"' | jq 'toboolean'     # true
echo '0' | jq 'toboolean'         # false
echo '42' | jq 'tojson'            # "42"
```

## Real-World Examples

### API Responses

```bash
# Get repo name and star count
curl -s 'https://api.github.com/repos/jqlang/jq' \
  | jq '{name: .name, stars: .stargazers_count}'

# List commit authors
curl -s 'https://api.github.com/repos/jqlang/jq/commits?per_page=30' \
  | jq '[.[] | {author: .commit.author.name}]'

# Search results
curl -s 'https://api.github.com/search/repositories?q=jq&per_page=5' \
  | jq '.items[] | {name: .full_name, stars: .stargazers_count}'
```

### Data Transformation

```bash
# Flatten nested arrays
echo '[[1,2],[3,4]]' | jq 'flatten'              # [1, 2, 3, 4]

# Group and aggregate
echo '[{"dept":"eng","sal":80},{"dept":"eng","sal":90}]' \
  | jq 'group_by(.dept) | map({dept: .[0].dept, avg: ([.[].sal]|add/length)})'

# Deduplicate by field
echo '[{"id":1,"v":"a"},{"id":2,"v":"b"},{"id":1,"v":"c"}]' \
  | jq '[group_by(.id)[] | .[0]]'
```

### Shell Script Integration

```bash
#!/bin/bash
# Extract values for use in shell scripts
STARS=$(curl -s 'https://api.github.com/repos/jqlang/jq' | jq '.stargazers_count')

# Multiple values with raw output
read -r NAME VERSION < <(curl -s 'https://api.github.com/repos/jqlang/jq' \
  | jq -r '[.name, .default_branch] | @sh')

# Process JSON file line by line
while IFS=$'\t' read -r id name; do
  echo "User $id: $name"
done < <(jq -r '.[] | [.id, .name] | @tsv' users.json)

# Conditional with exit status
curl -s 'https://api.github.com/repos/jqlang/jq' | jq -e '.fork == false' \
  && echo "Original repo" || echo "Fork"
```

### JSON Generation

```bash
# Build JSON from scratch
jq -n '{name: "jq", version: "1.8.1", features: ["filtering","transformation"]}'

# Use --arg for shell variable interpolation
NAME="myapp" jq -n --arg name "$NAME" '{"application": $name}'

# Generate array of objects
jq -n '[range(3) | {id: ., label: ("item-\(.)")}]'
```

## Performance Tips

```bash
# ✅ Use select() early to filter before expensive operations
jq '[.[] | select(.active) | expensive_operation]' data.json

# ✅ Bind intermediate results to variables with `as`
jq '[.users as $u | $u | map(.name)]' data.json

# ✅ For large files, use --stream to process incrementally
jq --stream '[.[] | select(.path[0] == "users")]' huge.json

# ❌ Avoid unnecessary iteration in nested loops
```

## Common Pitfalls

```bash
# Empty produces no output — use // or ? to handle
echo 'null' | jq '.a.b // "default"'     # "default"
echo 'null' | jq '.a.b?'                  # null (no error)

# Wrap empty results in array if needed
echo '[1,2,3]' | jq '[.[] | select(. > 10)]'   # [] (empty array)
```

## Reference Files

For detailed coverage of advanced topics, see the reference files:

- [`references/01-core-filters.md`](references/01-core-filters.md) — Core filters, operators, built-in functions, string/array/object operations
- [`references/02-regex-and-iteration.md`](references/02-regex-and-iteration.md) — Regular expressions, generators (range/repeat/while/until), reduce/foreach, walk/recursion
- [`references/03-io-and-advanced.md`](references/03-io-and-advanced.md) — I/O control, assignment, error handling, modules, streaming, type system, user-defined functions
- [`references/04-real-world-examples.md`](references/04-real-world-examples.md) — API responses, data transformation pipelines, shell integration, log parsing, validation, patterns cheat sheet

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
