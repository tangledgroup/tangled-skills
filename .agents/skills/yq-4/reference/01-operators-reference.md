# yq Operators Reference

Complete reference for all 60+ operators in yq v4.x. See the main [SKILL.md](../SKILL.md) for overview and usage patterns.

## Assignment Operators

### `=` (Assign / Update)
Set LHS node value equal to RHS node value. Creates paths if they don't exist.

```bash
yq '.a.b = "value"' file.yaml        # Simple assignment
yq -n '.x.y.z = 123'                  # Create from scratch
yq -i '.database.host = "newhost"' config.yaml  # In-place update
```

### `|=` (Relative Update)
Update field relative to its own value. RHS runs with LHS node as context.

```bash
yq '.counter |= . + 1' file.yaml              # Increment
yq '(.items[] | select(.name == "foo") | .count) |= . + 1' data.yaml  # Update matching array items
yq '.a |= .b' file.yaml                       # Replace node with child value
```

### `+=` (Concatenate / Append)
- Arrays: concatenate
- Numbers: arithmetic addition  
- Strings: concatenate
- Maps: shallow merge

```bash
yq '.a += .b' file.yaml              # Append arrays or add numbers
yq '.items += ["new-item"]' data.yaml  # Add to array
yq '.items += {"name": "foo"}' data.yaml  # Add object to array
```

### `-=` (Subtract)
Array subtraction, number subtraction.

```bash
yq '.a -= .b' file.yaml              # Subtract numbers or arrays
```

## Selection & Filtering Operators

### `select(expr)`
Filter by boolean expression. Returns nodes where expr is true.

```bash
yq '.items[] | select(.type == "fruit")' data.yaml
yq '.items[] | select(.count > 5)' data.yaml
yq '.[] | select(. == "*at")' file.yaml    # Wildcard matching
```

### `has(path)`
Check if a path exists. Returns true/false.

```bash
yq 'has(".database")' config.yaml
yq '.items | has(0)' data.yaml  # Check array index exists
```

### `pick(key1, key2, ...)`
Keep only specified keys.

```bash
yq 'pick(.name, .email)' user.yaml
```

### `omit(key1, key2, ...)`
Remove specified keys.

```bash
yq 'omit(.password, .secret)' config.yaml
```

### `del(path)`
Delete entries in maps or arrays.

```bash
yq 'del(.unwanted.field)' file.yaml
yq 'del(.items[0])' data.yaml
```

## Navigation Operators

### `.` (Traverse / Read)
Access child by key name.

```bash
yq '.database.host' config.yaml
yq '.server.ports[0]' data.yaml
```

### `[]` (Array Indexing)
Access array elements or map keys with special characters.

```bash
yq '.items[0]' data.yaml
yq '.["my-key"]' file.yaml     # Keys with dashes
yq '.items[-1]' data.yaml       # Last element
```

### `..` (Recursive Descent — Values)
Recurse through all value nodes.

```bash
yq '.. | select(has("password"))' secrets.yaml    # Find all passwords
yq '.. style="flow"' file.yaml                     # Style all values
```

### `...` (Recursive Descent — All Nodes)
Like `..` but also includes map keys.

```bash
yq '... style="flow"' file.yaml  # Style all nodes including keys
```

### `|` (Pipe)
Pass output of left expression as input to right expression.

```bash
yq '.items[] | select(.active)' data.yaml
yq '.data | length' file.yaml
```

## Array Operators

### `sort` / `sort_by(expr)`
Sort array in ascending order.

```bash
yq 'sort' data.yaml                        # Sort scalars
yq 'sort_by(.name)' data.yaml              # Sort by field
yq 'sort_by(.a, .b)' data.yaml             # Sort by multiple fields
yq 'sort_by(.name) | reverse' data.yaml    # Descending order
```

### `unique`
Remove duplicates, maintaining original order.

```bash
yq 'unique' data.yaml
yq '.items | unique' data.yaml
```

### `reverse`
Reverse array order.

```bash
yq 'reverse' data.yaml
```

### `shuffle`
Randomize array order.

```bash
yq 'shuffle' data.yaml
```

### `slice(start; end)` / `[start:end]`
Extract array slice.

```bash
yq '.items[0:3]' data.yaml
yq '.items[:5]' data.yaml    # First 5 elements
yq '.items[-3:]' data.yaml   # Last 3 elements
```

### `flatten(n)`
Recursively flatten nested arrays. Default flattens all levels; pass depth `n` for partial.

```bash
yq 'flatten' data.yaml       # Full flatten
yq 'flatten(1)' data.yaml    # Flatten one level
```

### `group_by(expr)`
Group array elements by expression value.

```bash
yq 'group_by(.category)' data.yaml
```

### `first(n)` / `last(n)`
Get first or last n elements.

```bash
yq 'first(3)' data.yaml
yq '.items | last(2)' data.yaml
```

### `pivot`
Convert rows to columns (wide format).

```bash
yq 'pivot' data.csv
```

### `collect(expr)` / `collect_into_object`
Collect results into an object.

```bash
yq '.[] | collect(.name)' data.yaml
```

### `array-to-map`
Convert array to map/object.

```bash
yq 'array-to-map' data.yaml
```

## Object Operators

### `keys`
Get all keys at current level.

```bash
yq '.server | keys' config.yaml
yq '.items[0] | keys' data.yaml
```

### `entries`
Convert object to array of {key, value} entries.

```bash
yq 'entries' config.yaml
```

### `map(expr)`
Apply expression to each element of array/object.

```bash
yq '.items | map(.name)' data.yaml
```

### `reduce` / `ireduce`
Reduce a collection into a single value.

```bash
# Sum numbers
yq '.[] as $item ireduce (0; . + $item)' data.yaml

# Merge multiple files
yq eval-all '. as $item ireduce ({}; . * $item )' *.yaml

# Convert array to object
yq '.[] | {(.name): .value} | reduce .[] as $item ({}; . + $item)' data.yaml
```

### `reduce` vs `ireduce`
- `ireduce` uses infix notation (current default)
- `jq`-style prefix `reduce` may be added in future

## Merge & Combine Operators

### `*` (Multiply / Deep Merge)
Deep merge objects. Arrays override by default.

```bash
yq '. *= load("override.yaml")' base.yaml
yq eval-all '. as $item ireduce ({}; . * $item )' *.yaml
```

#### Merge Flags for `*`
| Flag | Effect |
|------|--------|
| `+` | Append arrays instead of overriding |
| `d` | Deeply merge arrays |
| `?` | Only merge existing fields |
| `n` | Only merge new fields |
| `c` | Clobber custom tags |

```bash
yq '.a *+ .b' file.yaml      # Merge, append arrays
yq '.a *d .b' file.yaml      # Deep merge arrays
yq '.a *? .b' file.yaml      # Only existing fields
yq '.a *n .b' file.yaml      # Only new fields
```

### `+` (Add / Shallow Merge)
- Arrays: concatenate
- Numbers: addition
- Strings: concatenation
- Maps: shallow merge

```bash
yq '.a + .b' file.yaml       # Concat arrays or add numbers
yq '.a + " text"' file.yaml  # String concat
```

### `-` (Subtract)
Array subtraction, number subtraction.

```bash
yq '.a - .b' file.yaml
```

### `%` (Modulo)
Remainder of division.

```bash
yq '.a % .b' file.yaml
```

## Comparison & Boolean Operators

### `==`, `!=` (Equals / Not Equals)
Compare values.

```bash
yq 'select(.status == "active")' data.yaml
```

### `<`, `>`, `<=`, `>=` (Compare)
Compare numbers, strings, dates.

```bash
yq 'select(.count >= 10)' data.yaml
yq '.a > .b' file.yaml
```

### `and`, `or`, `not` (Boolean)
Logical operators.

```bash
yq 'select(.active and (.type == "user" or .type == "admin"))' data.yaml
```

### `all(expr)` / `any(expr)`
Check all/any elements satisfy condition.

```bash
yq '.items | all(. > 0)' data.yaml     # All positive?
yq '.items | any(.active)' data.yaml   # Any active?
```

`_c` variants (`all_c`, `any_c`) count matching elements.

## String Operators

### `strenv(NAME)`
Read environment variable as string.

```bash
yq -i '.api_key = strenv(API_KEY)' config.yaml
```

### `envsubst(options?)`
Interpolate environment variables in strings.

```bash
# Replace env vars in all string values
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml

# With options: fail on unset or empty
yq '.field |= envsubst(ne, ff)' file.yaml
```

### `test(regex)`
Test if string matches regex. Returns boolean.

```bash
yq 'select(.email | test("@"))' data.yaml
```

### `match(regex)`
Extract regex match groups.

```bash
yq '.text | match("hello (\\\\w+)")' file.yaml
```

### `capture(regex)`
Capture named groups into a map.

```bash
yq '.url | capture("(?<protocol>https?)://(?<host>[^/]+)")' file.yaml
```

### `gsub(regex; replacement)`
Global string replacement.

```bash
yq '.name |= gsub(" "; "_")' data.yaml
```

### `sub(regex; replacement)`
Single substitution.

### `starts_with(str)`, `ends_with(str)`
Prefix/suffix checks.

### `ltrim`, `rtrim`, `trim`
Whitespace trimming.

### `split(separator)` / `join(separator)`
Split/join strings.

```bash
yq '.tags | split(",")' data.yaml
yq '["a","b"] | join("-")' file.yaml
```

### `ljust(n)`, `rjust(n)`, `center(n)`
String padding/alignment.

### `upper`, `lower`
Case conversion.

## Date & Time Operators

### `format_datetime(format)`
Format a datetime value. Uses Go time formatting (reference: `2006-01-02T15:04:05Z07:00`).

```bash
yq '.a |= format_datetime("Monday, 02-Jan-06 at 3:04PM")' file.yaml
```

### `with_dtf(format; expr)`
Parse with custom datetime format, then evaluate expression.

```bash
yq '.a |= with_dtf("Monday, 02-Jan-06"; format_datetime("2006-01-02"))' file.yaml
```

### `tz(timezone)`
Convert timezone.

```bash
yq '.date |= tz("Australia/Melbourne")' file.yaml
```

### Date arithmetic
Add/subtract durations:

```bash
yq '.expiry += "3h"' file.yaml       # Add 3 hours
yq '.date += "7d"' file.yaml          # Add 7 days
yq '.start - .end' file.yaml          # Duration between dates
```

## Type & Metadata Operators

### `tag`
Get the YAML tag of a node (`!!str`, `!!int`, `!!map`, etc.).

```bash
yq 'select(tag == "!!map")' data.yaml    # Only maps
yq 'tag == "!!seq"' file.yaml             # Is array?
```

### `kind`
Get the kind: `map`, `scalar`, `sequence`.

```bash
yq 'kind == "map"' data.yaml
```

### `style` / `style= value`
Set/get node style (flow, single-quoted, double-quoted, folded, literal).

```bash
yq '.name |= style("single")' file.yaml
yq '... style=""' config.yaml  # Pretty print all
yq 'with(.a.deeply.nested; . = "val" | . style="single")' file.yaml
```

### `to_number`
Convert string to number.

```bash
yq '.count |= to_number' file.yaml
```

### `line` / `column`
Get line/column position of a node in source file.

```bash
yq 'line' file.yaml
yq 'column' file.yaml
```

## File & Document Operators

### `load(path)`
Load content from another file (YAML).

```bash
yq '. *= load("override.yaml")' base.yaml
yq 'load(.config_file)' file.yaml
```

Other load variants:
| Function | Format |
|----------|--------|
| `load()` | YAML |
| `load_xml()` | XML |
| `load_props()` | Properties |
| `load_str()` | Plain string |
| `load_base64()` | Base64-encoded UTF-8 |

### `fileIndex`
Get the index of the current file (in eval-all mode).

```bash
yq ea 'select(fileIndex == 0) * select(fileIndex == 1)' f1.yaml f2.yaml
```

### `documentIndex`
Get the index of the current document within a multi-document file.

```bash
yq 'documentIndex' multi-doc.yaml
```

### `has_key(path)` / `has_value(expr)`
Check key/value existence.

## Utility Operators

### `pipe` (inline pipe)
Pipe within expression for complex operations.

```bash
yq '.items | map(select(.active)) | sort_by(.name)' data.yaml
```

### `first(n)` / `last(n)`
Get first/last n elements of array.

```bash
yq 'first(3)' data.yaml
yq 'last()' data.yaml  # Last element
```

### `omit` (operator form)
Remove keys from object.

```bash
yq 'omit(.password, .secret)' config.yaml
```

### `parent`
Get the parent node.

```bash
yq '.items[] | select(.active) | parent' data.yaml
```

### `path(expr)`
Get the path to matching nodes.

```bash
yq 'path(.. | select(has("password")))' secrets.yaml
```

### `encode` / `decode`
See [Encode/Decode](#encode-decode-operators) below.

## Encode / Decode Operators

| Format | Decode (from string) | Encode (to string) |
|--------|---------------------|-------------------|
| YAML | `from_yaml` / `@yamld` | `to_yaml(n)` / `@yaml` |
| JSON | `from_json` / `@jsond` | `to_json(n)` / `@json` |
| Properties | `from_props` / `@propsd` | `to_props` / `@props` |
| CSV | `from_csv` / `@csvd` | `to_csv` / `@csv` |
| TSV | `from_tsv` / `@tsvd` | `to_tsv` / `@tsv` |
| XML | `from_xml` / `@xmld` | `to_xml(n)` / `@xml` |
| Base64 | `@base64d` | `@base64` |
| URI | `@urid` | `@uri` |
| Shell | — | `@sh` |

```bash
# Encode as JSON string
yq '.config = (.data | to_json)' file.yaml

# Decode from JSON string  
yq '.data |= from_json' file.yaml

# Encode/decode with indent level
yq '.json_str |= to_json(0)' file.yaml  # Single line JSON
```

## Comment Operators

### `add_comment(text, position?)`
Add comment above, below, or inline.

```bash
yq '.a |= add_comment("This is a")' file.yaml       # Above
yq '.a |= add_comment("below", "below")' file.yaml  # Below
yq '.a |= add_comment("inline", "end")' file.yaml   # End of line
```

### `comment`
Set/get comment on a node.

## Variable Operators

### `. as $name expr`
Bind expression result to variable name.

```bash
yq '.items as $items | $items | length' data.yaml
yq '.[] as $item ireduce (0; . + $item)' data.yaml  # With reduce
```

## Anchor & Alias Operators

### `&name` (Anchor)
Create an anchor.

```bash
yq 'with(.defaults; . |= &defaults)' file.yaml
```

### `*alias` / `*<<alias` (Alias reference)
Reference an alias.

```bash
yq '.ref |= *defaults' file.yaml
```

## Other Operators

### `column(expr)`
Get column number in source.

### `contains(other)`
Check if node contains another structure.

### `first(n?)` / `last(n?)`
First/last element(s).

### `filter(expr)`
Filter function (similar to select).

### `keys_array`
Get keys as array.

### `min` / `max`
Minimum/maximum of array.

```bash
yq '.numbers | min' data.yaml
yq '.items | max_by(.score)' data.yaml
```

### `sort_keys`
Sort object keys alphabetically.

```bash
yq 'sort_keys' config.yaml
```

### `split_documents` / `split_into_documents`
Split a multi-document YAML into separate documents.

### `union(other)`
Union of two arrays (like set union).

```bash
yq '.a + .b | unique' data.yaml    # Alternative to union
```

## Security Flags

Disable potentially dangerous operations:

```bash
# Disable file operations (load, etc.)
yq --security-disable-file-ops '.data' file.yaml

# Disable environment variable operations
yq --security-disable-env-ops '.data' file.yaml
```
