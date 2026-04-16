# Common yq Recipes

Practical examples combining multiple operators for real-world data manipulation. See main [SKILL.md](../SKILL.md) for basics.

## Array Operations

### Find items in an array

```bash
yq '.[] | select(.name == "Foo")' sample.yml
```

Splat `.[]` to iterate, then `select()` to filter.

### Find and update items in an array

```bash
yq '(.[] | select(.name == "Foo") | .numBuckets) |= . + 1' sample.yml
```

Use parentheses to group the LHS of `|=`, updating only matching elements.

### Deeply prune a tree

Keep only specific child keys at any depth:

```bash
yq '(
  .. |
  select(has("child1") or has("child2")) |
  (.child1, .child2) |
  select(.)
) as $i ireduce({}; setpath($i | path; $i))' sample.yml
```

Uses recursive descent `..`, `select()`, and `ireduce()` to rebuild a filtered tree.

### Update multiple array items with context

```bash
yq 'with(.myArray[]; .name = .name + " - " + .type)' sample.yml
```

`with()` loops through each element, running the second expression with that element as context.

### Sort an array by a field

```bash
yq '.myArray |= sort_by(.numBuckets)' sample.yml
```

Use `|=` to update in place, or pipe: `.myArray | sort_by(.field)`.

For descending: `.items | sort_by(.field) | reverse`

### Filter, flatten, sort, and unique

Extract unique values from nested arrays:

```bash
yq '[.[] | select(.type == "foo") | .names] | flatten | sort | unique' sample.yml
```

Wrap in `[]` to collect results back into an array after splatting.

### Sort keys of an object

```bash
yq 'sort_keys' config.yaml
```

## Merge Operations

### Merge two files

```bash
yq '. *= load("override.yaml")' base.yaml
```

Deep merge: matching keys in objects are merged recursively.

### Merge multiple files with eval-all

```bash
yq ea '. as $item ireduce ({}; . * $item )' path/to/*.yml
```

Loads all documents into memory, then reduces by deep merging.

### Merge using globs with globstar

```bash
shopt -s globstar
yq ea '. as $item ireduce ({}; . * $item )' path/to/**/*.yml
```

### Merge arrays of objects by a key field

Use `reduce` to group and merge:

```bash
yq eval-all '
  . as $item ireduce ({};
    . as $acc |
    if has($item.id) then
      .[$item.id] = (.[$item.id] * $item)
    else
      .[$item.id] = $item
    end
  )
' file1.yaml file2.yaml
```

### Merge with flags

| Flag | Effect | Example |
|------|--------|---------|
| `+` | Append arrays | `.a *+ .b` |
| `d` | Deep merge arrays | `.a *d .b` |
| `?` | Only existing fields | `.a *? .b` |
| `n` | Only new fields | `.a *n .b` |

## Format Conversion

### YAML to JSON

```bash
yq -o=json config.yaml > config.json
# Or shorthand: yq -j config.yaml
```

### JSON to pretty YAML

```bash
yq -Poy sample.json
```

### XML to YAML

```bash
yq -p xml input.xml
```

### YAML to XML

```bash
yq -o xml config.yaml
```

### CSV/TSV to YAML

```bash
yq -p csv data.csv
yq -p tsv data.tsv
```

### Properties to YAML

```bash
yq -p props app.properties
```

## Shell Integration

### Extract value for shell variable

```bash
DB_HOST=$(yq '.database.host' config.yaml)
API_KEY=$(yq '.api.key' secrets.yaml)
```

### Create bash array from YAML list

```bash
readarray -t items < <(yq '.coolActions[]' sample.yaml)
echo "${items[1]}"  # Second element
```

### Loop over array elements in bash

```bash
for item in $(yq '.items[].name' data.yaml); do
    echo "Processing: $item"
done
```

### Process JSON from another command

```bash
curl -s https://api.example.com/data | yq '.results[] | .name'
```

### Use environment variables in expressions

```bash
NAME=mike yq -i '.person.name = strenv(NAME)' file.yaml
yq --null-input '.a = env(MY_VAR)'              # Parse as YAML type
yq --null-input '.a = strenv(MY_VAR)'            # Always string
```

### Export all values as environment variables

```bash
# Simple: one per line
yq -o=json '.' config.yaml | jq -r 'to_entries[] | "\(.key)=\(.value)"' | xargs export

# Custom format (see recipes below for complex patterns)
```

### Update multiple files with find

```bash
find *.yaml -exec yq '. += "cow"' -i {} \;
```

## XML-Specific Recipes

### Read XML attributes

Attributes are prefixed with `+@` by default:

```bash
yq '.element."+@attr"' file.xml
```

Change prefix: `yq --xml-attribute-prefix "_@" '.' file.xml`

### Read XML text content

Content node named `+content` by default:

```bash
yq '.element."+content"' file.xml
```

Change name: `yq --xml-content-name "_text" '.' file.xml`

### Set XML attribute

```bash
yq -i '.element."+@id" = "new-id"' file.xml
```

### Skip processing instructions

```bash
yq --xml-skip-proc-inst '.' file.xml
```

### Strict XML parsing

```bash
yq --xml-strict-mode '.' file.xml
```

### Keep namespaces

```bash
yq --xml-keep-namespace '.' file.xml
```

## Multi-Document Processing

### Process each document separately (default)

```bash
yq '.items' multi-doc.yaml    # Only first document
```

### Process all documents together

```bash
yq ea 'select(fileIndex == 0) * load("other.yaml")' doc1.yaml doc2.yaml
```

### Split output into separate files

```bash
yq --split-exp '."+@id"' multi-output.xml
# Creates files named by the id attribute value
```

### Count documents in a file

```bash
yq 'documentIndex' multi-doc.yaml | tail -1 | awk '{print $1+1}'
```

## Front Matter Processing

### Extract front matter from Markdown

```bash
yq -f extract file.md
```

### Process front matter, preserve body

```bash
yq -f process 'del(.date)' file.md
```

### Write back in-place

```bash
yq -fi process 'del(.date)' file.md
```

## Validation & Inspection

### Validate YAML structure (top-level is map or array)

```bash
yq --exit-status 'tag == "!!map" or tag == "!!seq"' file.txt > /dev/null
echo $?  # 0 = valid, 1 = invalid
```

### Get all keys at a path

```bash
yq '.server | keys' config.yaml
```

### Get path to nodes matching condition

```bash
yq 'path(.. | select(has("password")))' secrets.yaml
```

### Get line/column of a node

```bash
yq 'line' file.yaml       # Line number
yq 'column' file.yaml      # Column number
```

### Check if value exists

```bash
yq --exit-status 'has(".database")' config.yaml
```

## Data Transformation Patterns

### Convert array to object

```bash
yq '.[] | {(.name): .value} | reduce .[] as $item ({}; . + $item)' data.yaml
```

### Group by field

```bash
yq 'group_by(.category)' data.yaml
```

### Pivot rows to columns

```bash
yq 'pivot' data.csv
```

### Flatten nested arrays

```bash
yq 'flatten' data.yaml       # All levels
yq 'flatten(1)' data.yaml    # One level only
```

### Encode/decode embedded strings

```bash
# Encode object as JSON string
yq '.config = (.data | to_json)' file.yaml

# Decode JSON string back to object
yq '.config |= from_json' file.yaml

# Encode/decode with specific indent
yq '.json_str |= to_json(0)' file.yaml  # Single line
```

### Add comments to YAML nodes

```bash
# Comment above node
yq '.a |= add_comment("This is a")' file.yaml

# Comment below node
yq '.a |= add_comment("below", "below")' file.yaml

# Inline/end-of-line comment
yq '.a |= add_comment("inline", "end")' file.yaml
```

### Style control for output

```bash
# Pretty print all (shorthand)
yq -P config.yaml

# Set all nodes to flow style
yq '... style=""' config.yaml

# Set specific node to single-quoted string
yq '.name |= style("single")' file.yaml

# Use with() for multiple styled updates
yq 'with(.a.deeply.nested; . = "val" | . style="single")' file.yaml
```

### Date/time formatting

```bash
# Format RFC3339 to custom format
yq '.date |= format_datetime("Monday, 02-Jan-06 at 3:04PM")' file.yaml

# Parse custom format then reformat
yq '.date |= with_dtf("Monday, 02-Jan-06"; format_datetime("2006-01-02"))' file.yaml

# Convert timezone
yq '.date |= tz("America/New_York")' file.yaml

# Add duration to date
yq '.expiry += "3h"' file.yaml
```

### String interpolation from environment

```bash
# Replace env vars in all string values
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml

# With strict mode (fail on unset/empty)
yq '.field |= envsubst(ne, ff)' file.yaml
```

### Create bash array from YAML

```bash
readarray -t actions < <(yq '.coolActions[]' sample.yaml)
echo "${actions[1]}"  # Second element
```

### Loop over YAML entries in bash

```bash
readarray -t identities < <(yq -o=j -I=0 '.identities[]' test.yml)
for identity in "${identities[@]}"; do
    roleArn=$(echo "$identity" | yq '.arn' -)
    echo "Role: $roleArn"
done
```

### Export as shell-compatible variables

```bash
yq '.[] | (
  select(kind == "scalar") | key + "='"'"'" + . + "'"'"'"),
  (select(kind == "seq") | key + "=(" + (map("'"'"'" + . + "'"'"'") | join(",")) + ")")
)' sample.yml
```

Output: `var0='string0'` and `fruit=('apple','banana')`

### Custom nested export with paths

```bash
yq '.. | (
  select(kind == "scalar" and parent | kind != "seq") |
    (path | join("_")) + "='"'"'" + . + "'"'"'"),
  (select(kind == "seq") |
    (path | join("_")) + "=(" + (map("'"'"'" + . + "'"'"'") | join(",")) + ")")
)' sample.yml
```

Output: `deep_property='value'`, `simpleArray=('apple','banana')`
