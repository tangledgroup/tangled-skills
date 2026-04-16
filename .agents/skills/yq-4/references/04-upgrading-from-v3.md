# Upgrading from yq v3 to v4

yq v4 is a complete rewrite with jq-like syntax. Most v3 commands map to expressions in v4's `eval` command (process each file sequentially) or `eval-all`/`ea` (load all files into memory for cross-file operations).

**Key changes in v4:**
- Uses jq-like expression syntax instead of separate subcommands
- Prints all documents by default (v3 only printed the first)
- Color output when writing to terminal
- Document separators (`---`) printed by default
- All flags moved into expression language for finer control

## Command Mapping: v3 → v4

### Navigating / Reading

```bash
# v3
yq r sample.yaml 'a.b.c'

# v4
yq '.a.b.c' sample.yaml
```

### Reading with default value

```bash
# v3
yq r sample.yaml --defaultValue frog path.not.there

# v4 (use alternative operator //)
yq '.path.not.there // "frog"' sample.yaml
```

### Finding nodes by value

```bash
# v3
yq r sample.yaml 'a.(b.d==cat).f'

# v4
yq '.a | select(.b.d == "cat") | .f' sample.yaml
```

### Recursive match (glob)

```bash
# v3
yq r sample.yaml 'thing.**.name'

# v4
yq '.thing | .. | select(has("name"))' sample.yaml
```

### Multiple documents (select specific doc)

```bash
# v3 (print second document)
yq r -d1 sample.yaml 'b.c'

# v4
yq 'select(documentIndex == 1) | .b.c' sample.yml
```

### Updating / Writing values

```bash
# v3
yq w sample.yaml 'a.b.c' fred

# v4
yq '.a.b.c = "fred"' sample.yaml
```

### Deleting values

```bash
# v3
yq d sample.yaml 'a.b.c'

# v4
yq 'del(.a.b.c)' sample.yaml
```

### Merging documents

```bash
# v3
yq m file1.yaml file2.yaml

# v4 (deep merge with multiply operator)
yq '. *= load("file2.yaml")' file1.yaml

# v4 compatibility: only merge new fields (like v3 default)
yq '. *n load("file2.yaml")' file1.yaml
```

### Prefix output under a key

```bash
# v3
yq p data1.yaml c.d

# v4
yq '{"c": {"d": . }}' data1.yml
```

### Create new YAML documents

```bash
# v3
yq n b.c cat

# v4 (use -n for null input)
yq -n '.b.c = "cat"' > newfile.yaml
```

**Important:** In v4 you cannot run expressions against empty files because there are no nodes to match. Use `-n` flag instead.

### Validate documents

```bash
# v3
yq validate some.file

# v4 (simple)
yq 'true' some.file > /dev/null

# v4 (sophisticated: check root is map or array)
yq --exit-status 'tag == "!!map" or tag == "!!seq"' some.file > /dev/null
```

### Compare YAML files

```bash
# v3
yq compare --prettyPrint file1.yml file2.yml

# v4 (use diff with normalized output)
diff <(yq -P file1.yml) <(yq -P file2.yml)
```

No built-in compare in v4, but you get full `diff` power. Remove comments for cleaner diffs: `... comments=""`

### Script files (batch operations)

```bash
# v3 format (script.yaml):
# - command: update 
#   path: a.key1
#   value: things
# - command: delete
#   path: a.ab.key2

# v4: combine into single expression
yq '
  .a.key1 = "things" |
  del(.a.ab.key2)
' ./examples/data1.yaml
```

v4 doesn't have script files, but multiple operations in one expression achieve the same result.

## New Capabilities in v4

### Dynamic map and array construction

```bash
# Create maps from input data
yq '{"result": .data}' input.yaml

# Union operator for multiple updates
yq '(.a = 1) + (.b = 2)' file.yaml
```

### Fine-grained merge control

The `*` operator supports flags:

| Flag | Effect | Example |
|------|--------|---------|
| `n` | Only new fields (v3-compatible) | `. *n load("override.yaml")` |
| `?` | Only existing fields | `. *? load("override.yaml")` |
| `+` | Append arrays | `. *+ load("override.yaml")` |
| `d` | Deep merge arrays | `. *d load("override.yaml")` |

### YAML metadata control

```bash
# Tags
yq 'tag' file.yaml           # Get tag (!!str, !!int, etc.)
yq '.field |= style("single")' file.yaml  # Set style

# Paths and positions
yq 'path(..)' file.yaml      # Get paths to all nodes
yq 'line' file.yaml           # Line number
yq 'column' file.yaml         # Column number

# Anchors and aliases
yq 'with(.defaults; . |= &defaults)' file.yaml  # Create anchor
yq '.ref |= *defaults' file.yaml                 # Reference alias

# Comments
yq '.a |= add_comment("note")' file.yaml    # Add comment above
```

### Multiple file operations (beyond merge)

```bash
# Process each file separately
yq '.data' file1.yaml file2.yaml file3.yaml

# Load multiple files with eval-all
yq ea 'select(fileIndex == 0) * load("common.yaml")' app1.yaml app2.yaml
```

### String interpolation and environment variables

```bash
# Environment variable as string
yq '.key = strenv(MY_VAR)' file.yaml

# Parse env var as YAML type
yq '.key = env(MY_VAR)' file.yaml

# Global env substitution
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml
```

### Date/time operations

```bash
yq '.date |= format_datetime("2006-01-02")' file.yaml
yq '.date |= tz("America/New_York")' file.yaml
yq '.expiry += "3h"' file.yaml
```

## Migration Checklist

| v3 Pattern | v4 Replacement |
|-----------|---------------|
| `yq r` (read) | `.path` expression |
| `yq w` (write) | `.path = value` |
| `yq d` (delete) | `del(.path)` |
| `yq m` (merge) | `* load()` or `*n load()` |
| `yq p` (prefix) | `{"key": .}` construction |
| `yq n` (new doc) | `-n '.key = val'` |
| `yq validate` | `'true' file.yaml > /dev/null` |
| `yq compare` | `diff <(yq -P f1) <(yq -P f2)` |
| `-d N` (doc index) | `select(documentIndex == N)` |
| `--defaultValue` | `// "default"` alternative |
| `**` (recursive glob) | `..` recursive descent |
| Script files | Single expression with `\|` |

## Common Pitfalls

### Empty files no longer work

```bash
# v3: worked on empty files
yq n b.c cat > empty.yaml

# v4: use -n flag instead
yq -n '.b.c = "cat"' > newfile.yaml
```

### Document separators are now default

If you don't want `---` in output, use `-N` flag:

```bash
yq -N '.data' file.yaml
```

### Multiple documents printed by default

v4 prints all documents. To process only the first:

```bash
yq 'select(documentIndex == 0) | .data' multi-doc.yaml
```

### Expression quoting in shell

Use single quotes for expressions to prevent shell expansion:

```bash
# Correct
yq '.data.key' file.yaml

# Wrong (shell may expand $)
yq ".data.key" file.yaml
```
