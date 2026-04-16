# yq Tips, Tricks & Troubleshooting

Common gotchas, patterns, and solutions. See main [SKILL.md](../SKILL.md) for basics.

## Validation

### Validate YAML structure

YAML is surprisingly lenient. A reasonable validation ensures the top level is a map or array:

```bash
yq --exit-status 'tag == "!!map" or tag == "!!seq"' file.txt > /dev/null
echo $?  # 0 = valid, 1 = invalid
```

### Normalize and diff YAML files

```bash
diff <(yq -P 'sort_keys(..)' -o=props file1.yaml) \
     <(yq -P 'sort_keys(..)' -o=props file2.yaml)
```

Remove comments for cleaner diffs: `... comments=""`

## Expression Formatting

### Multi-line expressions for readability

```bash
yq --inplace '
  with(.a.deeply.nested;
    . = "newValue" | . style="single" # line comment about styles
  ) |
  #
  # Block comment explaining what happens next
  #
  with(.b.another.nested; 
    . = "cool" | . style="folded"
  )
' my_file.yaml
```

### Comments in expressions

Use `#` for inline and block comments (same as YAML).

## Brackets Are Critical for Updates

When updating deeply selected paths, **always wrap the LHS in parentheses**:

```bash
# WRONG: returns only the updated subset
yq '(.foo.bar[] | select(.name == "fred") | .apple) = "cool"' file.yaml

# This pattern is essential: (selection) = value
```

Without brackets, yq filters first, then updates the filtered result separately.

## Shell Integration Patterns

### Create bash array from YAML list

```bash
readarray -t actions < <(yq '.coolActions[]' sample.yaml)
echo "${actions[1]}"  # Second element: "edit"
```

### Loop over JSON objects from YAML

```bash
readarray -t identities < <(yq -o=j -I=0 '.identities[]' test.yml)
for identity in "${identities[@]}"; do
    roleArn=$(echo "$identity" | yq '.arn' -)
    echo "Role: $roleArn"
done
```

### Update multiple files with find

```bash
find *.yaml -exec yq '. += "cow"' -i {} \;
```

Note: yq has no built-in multi-file update, use shell tools.

### Read from multiple STDIN sources

Like `diff`, you can pipe multiple streams:

```bash
yq '.apple' <(curl -s https://somewhere/data1.yaml) <(cat file.yml)
```

## Environment Variables

### Use env vars in expressions

```bash
# strenv() always returns string
NAME=mike yq -i '.person.name = strenv(NAME)' file.yaml

# env() parses as YAML type (map, array, string, number, bool)
yq --null-input '.a = env(MY_VAR)'

# Handle special characters safely
VAL='.a |!@  == "string2"' yq '.a = strenv(VAL)' example.yaml
```

### Replace all env vars in document

```bash
# Replace env vars in all string values
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml

# With strict options: fail on unset (ne) or empty (ne), fail fast (ff)
yq '.field |= envsubst(ne, ff)' file.yaml
```

## PowerShell Gotchas

PowerShell has unique quoting rules:

```powershell
# Use double-double-quotes for inner quotes
yq -n '.test = ""something""'

# Or use single quotes for expressions
yq '.a.b[0].c' file.yaml
```

See [GitHub issue #747](https://github.com/mikefarah/yq/issues/747) for more.

## String Handling

### String blocks and newlines

For multi-line strings, use YAML block scalars:

```bash
yq '.text = "line1\nline2"' file.yaml        # Escaped newline
yq '.text |= style("literal")' file.yaml      # Literal block (|)
yq '.text |= style("folded")' file.yaml       # Folded block (>)
```

### Style control

```bash
# All nodes to flow style (compact inline)
yq '... style=""' config.yaml

# Single quoted string
yq '.name |= style("single")' file.yaml

# Double quoted string  
yq '.name |= style("double")' file.yaml

# Literal block (preserves newlines)
yq '.text |= style("literal")' file.yaml

# Folded block (wraps long lines)
yq '.text |= style("folded")' file.yaml
```

## Merge Operations

### Merge all files into one

```bash
yq ea '. as $item ireduce ({}; . * $item )' file1.yml file2.yml ...
```

### Show source file and line in merged output

```bash
yq ea '(.. | lineComment |= filename + ":" + line) | select(fi==0) * select(fi==1)' data1.yaml data2.yaml
```

### Merge arrays of objects by key field

See [operators/multiply-merge](https://mikefarah.gitbook.io/yq/operators/multiply-merge#merge-arrays-of-objects-together-matching-on-a-key) for the working example. Use `reduce` to group and merge by a specific key.

## Creating New Documents

```bash
yq -n '.someNew="content"' > newfile.yml
yq -n '.a.b.c = "value" | .x.y = 123' > new.yaml
```

The `-n` flag means "null input" — don't read any file, just evaluate.

## Combining Multiple Files (Concatenation)

To combine multiple YAML files with `---` separators:

```bash
yq '.' somewhere/*.yaml
```

This processes each file in sequence and outputs them concatenated.

## Multiple Updates to Same Path

Use `with()` to set a nested context for multiple updates:

```bash
yq 'with(.a.deeply; .nested = "newValue" | .other = "newThing")' sample.yml
```

The first argument sets the root context; the second runs against it.

## Simulating if/elif/else Logic

yq has no `if` expression, but you can use `with()` + `select()`:

```bash
# Instead of: if .animal == "cat" then ... elif .animal == "dog" then ... else ...
yq '.[] |= (
  with(select(.animal == "cat"); 
    .noise = "meow" | .whiskers = true
  ) |
  with(select(.animal == "dog"); 
    .noise = "woof" | .happy = true
  ) |
  with(select(.noise == null); 
    .noise = "???"
  )
)' < file.yml
```

Note: no true `else` — use additional conditions.

## Merge Tags (YAML 1.1 Compatibility)

yq's underlying parser supports YAML 1.1 merge (`<<:`) and adds the explicit `!!merge` tag for compatibility:

```yaml
defaults: &defaults
  timeout: 30
  retries: 3
service:
  <<: *defaults
  host: localhost
# yq outputs this as:
# service:
#   !!merge <<: *defaults
#   timeout: 30
#   retries: 3
#   host: localhost
```

This is backward compatible with YAML 1.1 parsers.

## Performance Considerations

### eval vs eval-all

| Command | Memory | Use Case |
|---------|--------|----------|
| `eval` / `e` | Low (one file at a time) | Single file operations |
| `eval-all` / `ea` | High (all files in memory) | Cross-file merges, multi-document |

Use `eval` when possible for large files or many files.

### Use `--exit-status` in scripts

```bash
yq -e '.required_field' config.yaml || echo "Missing field!"
```

Exit status 1 if no matches or result is null/false — useful for CI/CD validation.

## Docker/Podman Tips

### Shell alias for convenience

```bash
yq() { docker run --rm -i -v "${PWD}":/workdir mikefarah/yq "$@"; }
# or with podman
yq() { podman run --rm -i -v "${PWD}":/workdir mikefarah/yq "$@"; }
```

### Restricted security profile

```bash
docker run --rm \
  --security-opt=no-new-privileges \
  --cap-drop=all \
  --network=none \
  -v "${PWD}":/workdir \
  mikefarah/yq '.data' file.yaml
```

### Timezone data for `tz` operator

The Alpine-based image doesn't include timezone data by default:

```dockerfile
FROM mikefarah/yq
USER root
RUN apk add --no-cache tzdata
USER yq
```

### Podman with SELinux

Use the `:z` flag on volume mounts:

```bash
podman run --rm -v "${PWD}":/workdir:z mikefarah/yq '.data' file.yaml
```

## Security

Disable dangerous operations in untrusted contexts:

```bash
# Disable file loading
yq --security-disable-file-ops '.data' file.yaml

# Disable environment variable operations
yq --security-disable-env-ops '.data' file.yaml
```

## Common Issues

### yq only returns the updated subset

When updating with selection, wrap LHS in parentheses (see "Brackets Are Critical" above).

### Merge returns unexpected results

Remember: `*` deeply merges objects but arrays override by default. Use flags (`+`, `d`) to change behavior. For shallow merge, use `+` instead of `*`.

### YAML 1.2 vs 1.1

yq uses YAML 1.2 standard where `"yes"`, `"no"` are strings (not booleans). This differs from some older parsers.

### Comment preservation

yq attempts to preserve comment positions and whitespace, but doesn't handle all scenarios. See [go-yaml/yaml#3](https://github.com/go-yaml/yaml/tree/v3) for details.
