# Operators Reference

## Assign (Update)

Plain form (`=`) sets LHS to RHS evaluated against root context. Relative form (`|=`) evaluates RHS with each LHS node as context.

```bash
# Create from scratch
yq -n '.a.b = "cat" | .x = "frog"'

# Update value
yq '.a.b = "frog"' file.yaml

# Update multiple paths
yq '(.a, .c) = "potato"' file.yaml

# Relative update (increment)
yq '.[] |= . * 2' file.yaml

# Use `c` flag to clobber custom tags
yq '.a =c .b' file.yaml
```

## Add (`+`, `+=`)

Behavior depends on LHS type:

- **Arrays**: concatenate
- **Numbers**: arithmetic addition
- **Strings**: concatenate
- **Maps**: shallow merge (use `*` for deep merge)
- **Dates**: add duration strings

```bash
# Concatenate arrays
yq '.a + .b' file.yaml

# Append to array
yq '.a += "cat"' file.yaml

# String concatenation
yq '.a += .b' file.yaml

# Number addition
yq '.a = .a + .b' file.yaml

# Increment all values
yq '.[] += 1' file.yaml

# Date addition
yq '.a += "3h10m"' file.yaml
```

## Multiply / Merge (`*`, `*=`)

Deep merge for objects. Arrays override by default (not deeply merged). Supports flags:

- `+` — append arrays
- `d` — deeply merge arrays
- `?` — only merge existing fields
- `n` — only merge new fields
- `c` — clobber custom tags

```bash
# Merge two files
yq '. *= load("file2.yml")' file1.yml

# Merge, only existing fields
yq '.a *? .b' file.yaml

# Merge, only new fields
yq '.a *n .b' file.yaml

# Merge, appending arrays
yq '.a *+ .b' file.yaml

# Merge all files
yq ea '. as $item ireduce ({}; . * $item )' *.yml

# Multiply numbers
yq '.a *= .b' file.yaml

# Repeat string N times
yq '"hello" * 3' -n
```

## Subtract (`-`, `-=`)

- **Numbers**: arithmetic subtraction
- **Arrays**: remove matching elements
- **Dates**: subtract duration strings

```bash
# Array subtraction
yq -n '[1,2] - [2,3]'

# Number subtraction
yq '.a = .a - .b' file.yaml

# Decrement
yq '.[] -= 1' file.yaml
```

## Divide (`/`)

- **Strings**: split by divider (returns array)
- **Numbers**: arithmetic division

```bash
# String split
yq '.c = .a / .b' file.yaml    # splits .a by .b

# Number division
yq '.a = .a / .b' file.yaml
```

## Alternative / Default (`//`)

Returns LHS if defined and not null/false, otherwise returns RHS.

```bash
# Default value
yq '.a // "default"' file.yaml

# Initialize then increment
yq '(.a // (.a = 0)) += 1' file.yaml
```

## Select

Filter by boolean expression. Supports wildcards (`*`) and regex via `test()`.

```bash
# Filter array elements
yq '.[] | select(.name == "Foo")' file.yaml

# Wildcard prefix
yq '.[] | select(. == "*at")' file.yaml   # matches cat, goat

# Regex
yq '.[] | select(test("[a-zA-Z]+_[0-9]$"))' file.yaml

# Filter map keys
yq 'with_entries(select(.key | test("ame$")))' file.yaml

# Combine with update (note parentheses!)
yq '(.a.[] | select(. == "cat" or . == "goat")) |= "rabbit"' file.yaml
```

## Delete (`del()`)

```bash
# Delete map entry
yq 'del(.b)' file.yaml

# Delete array element by index
yq 'del(.[1])' file.yaml

# Delete matching entries
yq 'del(.[] | select(. == "*at"))' file.yaml

# Recursively delete keys named "name"
yq 'del(.. | select(has("name")).name)' file.yaml
```

## Traverse (Read)

Navigate deeply into structures with dot notation. Use `[]` to splat arrays. Use quotes with brackets for special characters.

```bash
# Navigate
yq '.a.b.c' file.yaml

# Splat array
yq '.items[]' file.yaml

# Multiple indices
yq '.a[0, 2]' file.yaml

# Special characters in keys
yq '.["{}"]' file.yaml

# Recursive descent — values only (..)
yq '.. | select(. == "frog")' file.yaml

# Recursive descent — values and keys (...)
yq '... style=""' file.yaml   # pretty print including keys
```

## Union (`,`)

Combine results from multiple expressions.

```bash
# Combine scalars
yq -n '1, true, "cat"'

# Read multiple paths
yq '.a, .c' file.yaml
```

## Collect into Array (`[]`)

Create arrays from expressions.

```bash
# Empty array
yq -n '[]'

# Collect values
yq '[.a, .b]' file.yaml
```

## Create / Collect into Object (`{}`)

Construct maps.

```bash
# Wrap (prefix) existing object
yq '{"wrap": .}' file.yaml

# Create from scratch
yq -n '{"wrap": "frog"}'
```

## Sort and Unique

```bash
# Sort by field
yq '.myArray |= sort_by(.numBuckets)' file.yaml

# Sort descending
yq 'sort_by(.a) | reverse' file.yaml

# Sort keys recursively
yq 'sort_keys(..)' file.yaml

# Unique values
yq 'unique' file.yaml

# Flatten nested arrays
yq 'flatten' file.yaml
yq 'flatten(1)' file.yaml   # depth of one
```

## Group By and Filter

```bash
# Group by field
yq 'group_by(.foo)' file.yaml

# Filter array
yq 'filter(. < 3)' file.yaml

# First matching element
yq 'first(.a == "cat")' file.yaml
```

## Reduce / ireduce

Process a collection into a new form.

```bash
# Sum numbers
yq '.[] as $item ireduce (0; . + $item)' file.yaml

# Merge all files
yq ea '. as $item ireduce ({}; . * $item )' *.yml

# Array to object
yq '.[] as $item ireduce ({}; .[$item.name] = $item.has)' file.yaml
```

## Slice (`.[start:end]`)

Works on arrays and strings. Negative indices count from end.

```bash
# Array slice
yq '.[1:3]' file.yaml

# String slice
yq '.country[0:5]' file.yaml

# From start / to end
yq '.[:2]' file.yaml
yq '.[2:]' file.yaml

# Negative index
yq '.[-5:]' file.yaml
```

## Reverse and Shuffle

```bash
# Reverse array
yq 'reverse' file.yaml

# Shuffle (not cryptographically secure)
yq 'shuffle' file.yaml
```

## Split into Documents (`split_doc`)

Split matches into separate YAML documents.

```bash
yq '.[] | split_doc' file.yaml
```

## Has and Keys

```bash
# Check key exists
yq '.[] | has("a")' file.yaml

# Get map keys
yq 'keys' file.yaml

# Get array indices
yq '.items | keys' file.yaml

# Get current key
yq '.a | key' file.yaml
```

## Length

```bash
yq '.a.b | length' file.yaml
```

## Kind and Tag

```bash
# Node kind: scalar, seq (array), map (object)
yq '.a | kind' file.yaml

# YAML tag: !!str, !!int, !!bool, etc.
yq '.. | tag' file.yaml

# type is an alias for tag
yq '.. | type' file.yaml
```

## Line and Column

Returns source position of matching nodes.

```bash
yq '.a | line' file.yaml
yq '.b | column' file.yaml
```

## Document Index (`documentIndex`, `di`)

Select nodes from specific documents in multi-document files.

```bash
# Get document index
yq '.a | di' file.yaml

# Filter by document index
yq 'select(di == 1)' file.yaml
```

## File Index (`fileIndex`, `fi`) and Filename

Used with `eval-all` to identify which file each node came from.

```bash
yq ea 'select(fi == 0) * select(filename == "file2.yaml")' f1.yml f2.yml
yq 'filename' file.yaml
```

## Array to Map (`array_to_map`)

Convert array indices to map keys (skips nulls).

```bash
yq '.cool |= array_to_map' file.yaml
```

## Pick and Omit

```bash
# Pick specific paths (like jq)
yq 'pick(.a, .c.d)' file.yaml

# Omit paths
yq 'omit(.b)' file.yaml
```

## Parent

Navigate to parent node.

```bash
yq '.a.b | parent' file.yaml
```

## Path and Eval

```bash
# Get path expression
yq '.a.b.c | path' file.yaml

# Dynamic expression evaluation
yq 'eval(.pathExp)' file.yaml
```

## Pivot

Transpose rows and columns.

```bash
yq 'pivot' file.yaml
```

## With

Make multiple updates to a deeply nested path or array elements.

```bash
# Multiple updates to same path
yq 'with(.a.deeply.nested; . = "newValue" | . style="single")' file.yaml

# Update array elements relatively
yq 'with(.myArray[]; .b = .a + " yum")' file.yaml
```

## Pipe (`pipe`)

Execute another yq expression as a string.

```bash
yq '.a | pipe(".b | .c")' file.yaml
```

## Style

Control YAML formatting of nodes.

```bash
# Set style on specific node
yq '.a.b = "new" | .a.b style="double"' file.yaml

# Styles: "single", "double", "literal", "folded", "flow", "tagged", "" (reset)
yq '.. style="single"' file.yaml

# Pretty print (reset all styles including keys)
yq '... style=""' file.yaml
yq -P file.yaml   # shorthand
```

## Comment Operators

Set or retrieve head, line, and foot comments.

```bash
# Set line comment
yq '.a line_comment="single"' file.yaml

# Set head comment
yq '. head_comment="single"' file.yaml

# Remove all comments
yq '... comments=""' file.yaml

# Get comments
yq '.a | line_comment' file.yaml
yq '. | head_comment' file.yaml
yq '. | foot_comment' file.yaml
```

## Entries (`to_entries`, `from_entries`, `with_entries`)

Convert between maps and arrays of key-value pairs.

```bash
# Map to entries
yq 'to_entries' file.yaml

# Update keys
yq 'with_entries(.key |= "KEY_" + .)' file.yaml

# Filter map
yq 'with_entries(select(.value | has("b")))' file.yaml

# Custom sort
yq 'to_entries | sort_by(.key) | reverse | from_entries' file.yaml
```

## Boolean Operators

```bash
yq -n 'true or false'
yq -n 'true and false'
yq -n 'true | not'

# any / all on arrays
yq 'any' file.yaml       # true if any element is true
yq 'all' file.yaml       # true if all elements are true
yq '.[] |= any_c(. == "x")' file.yaml
yq '.[] |= all_c(tag == "!!str")' file.yaml
```

## Compare Operators

`>`, `>=`, `<`, `<=` for numbers, strings, and datetimes.

```bash
yq '.a > .b' file.yaml
```

## Equals (`==`, `!=`)

Supports wildcards (`*`).

```bash
yq '.[] | (. == "*at")' file.yaml   # matches cat, goat
```

## Contains

Returns true if context contains the parameter.

```bash
# String substring
yq 'contains("bar")' file.yaml

# Array subset
yq 'contains(["a", "b"])' file.yaml
```

## Min / Max

```bash
yq 'min' file.yaml   # minimum value in array
yq 'max' file.yaml   # maximum value in array
```

## Map

Apply expression to each element (like jq's `map`).

```bash
yq 'map(. * 2)' file.yaml
```

## Modulo

```bash
yq '.a % .b' file.yaml
```

## To Number

Parse strings as numbers.

```bash
yq '.[] | to_number' file.yaml
```

## String Operators

```bash
# Interpolation
yq '.msg = "I like \(.value)"' file.yaml

# Case conversion
yq 'upcase' file.yaml
yq 'downcase' file.yaml

# Join
yq 'join("; ")' file.yaml

# Trim
yq '.[] | trim' file.yaml

# Regex match
yq '[match("foo"; "g")]' file.yaml

# Named capture groups
yq 'capture("(?P<a>[a-z]+)-(?P<n>[0-9]+)")' file.yaml

# Test regex
yq '.[] | test("at")' file.yaml

# Substitute
yq '.a |= sub("dogs", "cats")' file.yaml

# Split string
yq 'split("; ")' file.yaml

# To string
yq '.[] |= to_string' file.yaml

# Length
yq '.a | length' file.yaml
```

## Date Time Operators

Uses Go's time library. Default format is RFC3339.

```bash
# Format datetime
yq '.a |= format_datetime("Monday, 02-Jan-06")' file.yaml

# Current time
yq '.updated = now' file.yaml

# Unix conversion
yq -n '1675301929 | from_unix | tz("UTC")'
yq -n 'now | to_unix'

# Timezone
yq '.a |= tz("Australia/Sydney")' file.yaml

# Custom format
yq 'with_dtf("Monday, 02-Jan-06 at 3:04PM MST"; .a += "3h1m")' file.yaml
```

## Encode / Decode

```bash
# JSON encode/decode
yq '.b = (.a | to_json)' file.yaml
yq '.a | from_json' file.yaml

# YAML encode/decode (for embedded yaml strings)
yq '.a |= (from_yaml | .foo = "cat" | to_yaml)' file.yaml

# CSV / TSV
yq '@csv' file.yaml        # array to CSV string
yq '.a |= @csvd' file.yaml  # CSV string to array

# XML
yq '.a | to_xml' file.yaml
yq '.a | from_xml' file.yaml

# Base64
yq '.coolData | @base64' file.yaml
yq '.coolData | @base64d' file.yaml

# URI
yq '.coolData | @uri' file.yaml
yq '@urid' file.yaml

# Shell-safe string
yq '.coolData | @sh' file.yaml

# Shorthand aliases: @json, @yaml, @csv, @tsv, @xml, @props, @base64d, @urid
```

## Anchor and Alias Operators

```bash
# Get anchor name
yq '.a | anchor' file.yaml

# Set anchor
yq '.a anchor = "foobar"' file.yaml

# Get alias target
yq '.a | alias' file.yaml

# Set alias
yq '.a alias = "meow"' file.yaml

# Explode (dereference) aliases and anchors
yq 'explode(.f)' file.yaml
yq 'explode(.)' file.yaml   # entire document

# Use --yaml-fix-merge-anchor-to-spec=true for correct merge anchor behavior
```

## Variable Operators

```bash
# Single value variable
yq '.a as $foo | $foo' file.yaml

# Multi value variable
yq '.[] as $foo | $foo' file.yaml

# Lookup table
yq '.realnames as $names | .posts[] | {"title": .title, "author": $names[.author]}' file.yaml

# Swap values
yq '.a as $x | .b as $y | .b = $x | .a = $y' file.yaml

# ref operator — holds a reference (not copy) to a path
yq '.a.b ref $x | $x = "new" | $x style="double"' file.yaml
```

## Environment Variable Operators

```bash
# env() — parses as YAML node (string, number, bool, map, array)
myenv="cat" yq -n '.a = env(myenv)'

# strenv() — always parses as string
myenv="true" yq -n '.a = strenv(myenv)'

# envsubst() — interpolates ${VAR} in strings
myenv="cat" yq -n '"the ${myenv} meows" | envsubst'

# Default values
yq -n '"the ${missing-dog} meows" | envsubst'

# Replace all strings in document
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml

# Security: disable with --security-disable-env-ops
```

## System Operator

Run external commands (disabled by default).

```bash
yq --security-enable-system-operator '.a = system("/usr/bin/echo"; "hello")' file.yaml
```
