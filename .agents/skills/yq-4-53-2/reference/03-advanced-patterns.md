# Advanced Patterns

## Merging Files

Use `eval-all` (`ea`) to load all files into memory before merging.

```bash
# Merge file2 into file1 (in place)
yq ea -i 'select(fi == 0) * select(fi == 1)' f1.yml f2.yml

# Merge using load operator
yq '. *= load("file2.yml")' file1.yml

# Merge all files in a directory
yq ea '. as $item ireduce ({}; . * $item )' path/to/*.yml

# Merge with stdin
cat extra.yml | yq ea -i 'select(fi == 0) * select(fi == 1)' f1.yml -

# Show source file and line in merged result
yq ea '(.. lineComment |= filename + ":" + line) | select(fi==0) * select(fi==1)' d1.yaml d2.yaml
```

## Merge Arrays of Objects by Key

Complex pattern to merge arrays matching on a key field. Set environment variables for the paths and key:

```bash
idPath=".a" originalPath=".myArray" otherPath=".newArray" yq ea '
(
  (( (eval(strenv(originalPath)) + eval(strenv(otherPath))) | .[] | {(eval(strenv(idPath))): .}) as $item ireduce ({}; . * $item )) as $uniqueMap
  | ($uniqueMap | to_entries | .[]) as $item ireduce([]; . + $item.value)
) as $mergedArray
| select(fi == 0) | (eval(strenv(originalPath))) = $mergedArray
' file1.yml file2.yml
```

## Deep Prune — Keep Only Specific Keys

```bash
yq '(
  .. | select(has("child1") or has("child2")) | (.child1, .child2) | select(.)
) as $i ireduce({}; setpath($i | path; $i))' file.yaml
```

## Create from Scratch

Use `-n` (`--null-input`) to create YAML without reading any input file.

```bash
# Simple creation
yq -n '.a.b.c = "cat"' > newfile.yml

# Multi-field creation
yq -n '.a.b = "foo" | .d.e = "bar"' > newfile.yml

# With environment variables
PORT=8080 yq -n '.server.port = env(PORT) | .server.host = strenv(HOST)'
```

## Load Files into Expressions

Load content from other files within expressions. Supports YAML, XML, Properties, plain strings, and base64.

```bash
# Load YAML
yq 'load("config.yml")' file.yaml

# Replace node with loaded file
yq '.config |= load("settings.yml")' file.yaml

# Load as string (any text file)
yq '.content = load_str("readme.txt")' file.yaml

# Load XML
yq '.data = load_xml("data.xml")' file.yaml

# Load properties
yq '.config = load_props("app.properties")' file.yaml

# Load base64
yq '.secret = load_base64("encoded.txt")' file.yaml

# Recursively replace all nodes with a "file" attribute
yq '(.. | select(has("file"))) |= load("../../examples/" + .file)' file.yaml
```

Security: disable with `--security-disable-file-ops`.

## Environment Variables in Expressions

Three operators for environment variable integration:

```bash
# env() — parses value as YAML node
myenv="true" yq -n '.flag = env(myenv)'       # boolean true
myenv="{b: fish}" yq -n '.a = env(myenv)'      # map

# strenv() — always a string
myenv="true" yq -n '.a = strenv(myenv)'        # string "true"

# envsubst() — interpolate ${VAR} in strings
myenv="cat" yq -n '"the ${myenv} meows" | envsubst'

# Replace all string values in document
yq '(.. | select(tag == "!!str")) |= envsubst' file.yaml

# Dynamic path from environment variable
pathEnv=".a.b[0].name" valueEnv="moo" yq 'eval(strenv(pathEnv)) = strenv(valueEnv)' file.yaml
```

Security: disable with `--security-disable-env-ops`.

## Bash Integration

### Create Bash Array from YAML

```bash
readarray actions < <(yq '.coolActions[]' sample.yaml)
echo "${actions[1]}"   # edit
```

### Loop Over YAML Entries in Bash

```bash
readarray items < <(yq -o=j -I=0 '.items[]' file.yml)
for item in "${items[@]}"; do
    name=$(echo "$item" | yq '.name' -)
    echo "Name: $name"
done
```

### yq in a Find Loop

```bash
find *.yaml -exec yq '. += "cow"' -i {} \;
```

## Multiple Updates to Same Path

Use `with` for multiple updates to a deeply nested path:

```bash
yq 'with(.a.deeply.nested; .field1 = "val1" | .field2 = "val2")' file.yaml
```

## Conditional Logic (Without if/else)

yq does not have `if` expressions. Use `with` + `select` instead:

```bash
yq '.[] |= (
  with(select(.animal == "cat"); .noise = "meow" | .whiskers = true) |
  with(select(.animal == "dog"); .noise = "woof" | .happy = true) |
  with(select(.noise == null); .noise = "???")
)' < file.yaml
```

## Comparing YAML Files

Normalize both files then diff:

```bash
diff <(yq -P 'sort_keys(..)' file1.yml) <(yq -P 'sort_keys(..)' file2.yml)

# Without comments
diff <(yq -P '... comments="" | sort_keys(..)' f1.yml) <(yq -P '... comments="" | sort_keys(..)' f2.yml)

# Compare as properties for flat comparison
diff <(yq -P -o=props 'sort_keys(..)' f1.yml) <(yq -P -o=props 'sort_keys(..)' f2.yml)
```

## Validating YAML Files

```bash
# Check top level is map or array
yq --exit-status 'tag == "!!map" or tag == "!!seq"' file.txt > /dev/null

# Validate by parsing (simple)
yq 'true' some.file > /dev/null
```

## Reading Multiple Streams

Use process substitution to pipe multiple streams:

```bash
yq '.apple' <(curl -s https://somewhere/data1.yaml) <(cat file.yml)
```

## Combining Multiple Files

Combine YAML files with `---` separators:

```bash
yq '.' somewhere/*.yaml
```

## Updating Deeply Selected Paths

Wrap the entire LHS in parentheses:

```bash
yq '(.foo.bar[] | select(.name == "fred") | .apple) = "cool"' file.yaml
```

Without parentheses, yq filters first then updates the filtered result and returns only that subset.

## String Blocks and Newlines

Bash `$(exp)` trims trailing newlines. Use `printf` or multiline variables:

```bash
# printf approach
printf -v m "cat\n"; m="$m" yq -n '.a = strenv(m)'

# Multiline variable
m="cat
" yq -n '.a = strenv(m)'

# From file with trailing newline
IFS= read -rd '' output < <(cat my_file)
output=$output yq '.data.values = strenv(output)' first.yml
```

## Special Characters in Strings

Use `strenv` to avoid complex quoting:

```bash
VAL='.a |!@ == "string2"' yq '.a = strenv(VAL)' example.yaml
```

## Merge Anchor Tag (`!!merge`)

yq automatically adds the `!!merge` tag to merge keys (`<<:`) since this was removed from YAML 1.2 spec. This is backwards compatible with YAML 1.1 parsers.

Use `--yaml-fix-merge-anchor-to-spec=true` for correct merge anchor behavior per the YAML spec (keys earlier in merge sequence override later ones).

## Export as Environment Variables

Generate shell scripts from YAML:

```bash
yq '.[] | (
  (select(kind == "scalar") | key + "='\''" + . + "'\''"),
  (select(kind == "seq") | key + "=(" + (map("'\''" + . + "'\''") | join(",")) + ")")
)' file.yaml
```

## GitHub Actions

```yaml
- name: Get value from config
  id: getValue
  uses: mikefarah/yq@master
  with:
    cmd: yq '.config.value' 'config.yml'
- name: Use the value
  run: echo ${{ steps.getValue.outputs.result }}
```

## Tips and Troubleshooting

### Why is yq only returning the updated snippet?

You forgot parentheses around the LHS. Always wrap complex selection expressions:

```bash
# Wrong
yq '.items[] | select(.name == "x") | .value = "new"' file.yaml

# Right
yq '(.items[] | select(.name == "x") | .value) = "new"' file.yaml
```

### Quotes in Windows PowerShell

PowerShell uses `""` for literal quotes:

```powershell
yq -n '.test = ""something"""'
```

### yq adds `!!merge` tag automatically

This is expected behavior. The `!!merge` tag explicitly marks merge keys per YAML 1.2 spec. It is backwards compatible with YAML 1.1 parsers.

### PowerShell quoting issues

See <https://github.com/mikefarah/yq/issues/747> for workarounds.
