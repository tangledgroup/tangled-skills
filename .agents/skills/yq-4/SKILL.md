---
name: yq-4
description: Complete toolkit for yq v4.x, the lightweight portable command-line YAML, JSON, XML, INI, TOML, HCL, CSV/TSV, Properties, Base64, and Lua processor using jq-like syntax. Use when reading, writing, merging, or transforming YAML/JSON/XML files from the terminal, scripting, CI/CD pipelines, or Docker containers without needing Python or Node.js dependencies.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.52"
tags:
  - yaml
  - json
  - xml
  - jq
  - command-line
  - data-transformation
  - config-management
category: developer-tools
external_references:
  - https://mikefarah.gitbook.io/yq/
  - https://github.com/mikefarah/yq/discussions
  - https://mikefarah.gitbook.io/yq/llms-full.txt
  - https://mikefarah.gitbook.io/yq/sitemap.md
  - https://github.com/mikefarah/yq
---

# yq v4.x

## Overview

Complete toolkit for yq v4.x, the lightweight portable command-line YAML, JSON, XML, INI, TOML, HCL, CSV/TSV, Properties, Base64, and Lua processor using jq-like syntax. Use when reading, writing, merging, or transforming YAML/JSON/XML files from the terminal, scripting, CI/CD pipelines, or Docker containers without needing Python or Node.js dependencies.

A lightweight and portable command-line **YAML, JSON, INI, XML, TOML, HCL, CSV/TSV, Properties, Base64, and Lua** processor. `yq` uses [jq](https://github.com/stedolan/jq) like syntax but works with YAML files as well as JSON, XML, and more. It is written in Go — a single dependency-free binary for any platform.

## When to Use

- **Read values** from YAML/JSON/XML config files via CLI
- **Update/patch** configuration files in-place (`-i`)
- **Merge** multiple YAML/JSON files together
- **Convert** between formats (YAML ↔ JSON, XML → YAML, etc.)
- **Filter and transform** data arrays with jq-like expressions
- **Extract values** for shell scripting and environment variables
- **Validate** YAML structure in CI/CD pipelines
- **Work with XML** including attributes, namespaces, and processing instructions
- **Process front matter** in Markdown documents

## Quick Start

```bash
# Read a value from YAML
yq '.a.b[0].c' file.yaml

# Pipe from STDIN
cat file.yaml | yq '.a.b[0].c'

# Update in-place
yq -i '.a.b[0].c = "cool"' file.yaml

# Use environment variables in expressions
NAME=mike yq -i '.person.name = strenv(NAME)' file.yaml

# Merge two files
yq -n 'load("file1.yaml") * load("file2.yaml")'

# Convert JSON to YAML
yq -Poy sample.json

# Create a new document from scratch
yq -n '.a.b.c = "cat"'
```

## Core Concepts

### Expression Model

In yq, expressions are made up of **operators** and **pipes**. A context of nodes is passed through the expression, and each operation takes the context as input and returns a new context. That output is piped to the next operation.

```
root.context | filter | select(condition) | .field
```

### Dot Notation & Splatting

- `.root.items[0].name` — access nested structures
- `.root.items[]` — "splat" an array so each element becomes its own context node
- `..` — recursive descent (glob), recurse through all nodes at any depth

### Operator Precedence

Like math expressions, operators have precedence. The pipe `|` has the lowest precedence. Most assignments like `.a = "cat" | .b = "dog"` are effectively `(.a = "cat") | (.b = "dog")`. Use parentheses for complex LHS/RHS expressions.

### Relative Update (`|=`)

The `|=` operator updates fields relative to their own value:
```bash
yq '(.items[] | select(.name == "foo") | .count) |= . + 1' file.yaml
```

### Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `eval` | `e` | Apply expression to each file in sequence (default) |
| `eval-all` | `ea` | Load ALL documents from ALL files, run expression once |
| `shell-completion` | — | Generate shell autocompletion scripts |

### Global Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--colors` | `-C` | Force colored output |
| `--no-colors` | `-M` | Force no colors |
| `--exit-status` | `-e` | Exit status 1 if no matches or null/false returned |
| `--inplace` | `-i` | Update first file in place |
| `--prettyPrint` | `-P` | Pretty print (shorthand for `... style=""`) |
| `--indent` | `-I` | Set indent level (default: 2) |
| `--null-input` | `-n` | Don't read input, evaluate expression only (create docs) |
| `--no-doc` | `-N` | Don't print document separators (`---`) |
| `--input-format` | `-p` | Force input format: `auto\|yaml\|json\|xml\|kyaml\|props\|csv\|tsv\|toml\|hcl\|lua\|ini\|base64\|uri` |
| `--output-format` | `-o` | Force output format: `auto\|yaml\|json\|xml\|kyaml\|props\|csv\|tsv\|toml\|hcl\|lua\|ini\|shell\|base64\|uri` |
| `--unwrapScalar` | `-r` | Print scalar value without quotes (default: true for YAML) |
| `--expression` | — | Forcibly set expression argument |
| `--from-file` | — | Load expression from file |
| `--front-matter` | `-f` | `(extract\|process)` front matter handling |
| `--split-exp` | — | Split output into files named by expression result |
| `--verbose` | `-v` | Verbose mode |

### Format Shortcuts

- **YAML**: `y`, `yaml`
- **JSON**: `j`, `json` (use `-j` or `-o json`)
- **XML**: `x`, `xml`
- **Kubernetes YAML**: `kyaml`, `ky`
- **Properties**: `p`, `props`
- **CSV/TSV**: `c`/`csv`, `t`/`tsv`
- **TOML**: `toml`
- **HCL**: `h`, `hcl`
- **Lua**: `l`, `lua`
- **INI**: `i`, `ini`
- **Base64**: `base64`
- **URI**: `uri`
- **Shell variables**: `s`, `shell`

## Installation

### Download Binary (Recommended)

```bash
# Latest version, Linux AMD64
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq &&\
    chmod +x /usr/local/bin/yq

# macOS Intel
curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_darwin_amd64 -o /usr/local/bin/yq &&\
    chmod +x /usr/local/bin/yq

# macOS Apple Silicon
curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_darwin_arm64 -o /usr/local/bin/yq &&\
    chmod +x /usr/local/bin/yq
```

**Available platforms:** `linux_amd64`, `linux_arm64`, `linux_arm`, `linux_386`, `darwin_amd64`, `darwin_arm64`, `windows_amd64`, `windows_386`

### Package Managers

```bash
# Homebrew (macOS / Linux)
brew install yq

# Snap (Linux)
snap install yq

# Nix
nix profile install nixpkgs#yq-go

# Arch Linux
pacman -S go-yq

# MacPorts
sudo port install yq

# Alpine Linux v3.20+
apk add yq-go

# Chocolatey (Windows)
choco install yq

# Scoop (Windows)
scoop install main/yq

# winget (Windows)
winget install --id MikeFarah.yq

# Go install
go install github.com/mikefarah/yq/v4@latest
```

### Docker / Podman

```bash
# One-time use with volume mount
docker run --rm -v "${PWD}":/workdir mikefarah/yq '.a.b[0].c' file.yaml

# Pipe from STDIN (needs -i flag)
docker run -i --rm mikefarah/yq '.this.thing' < myfile.yml

# Create a shell alias/function
yq() { docker run --rm -i -v "${PWD}":/workdir mikefarah/yq "$@"; }
```

**Security:** Run with restricted privileges:
```bash
docker run --rm --security-opt=no-new-privileges --cap-drop all --network none \
  -v "${PWD}":/workdir mikefarah/yq '.a.b[0].c' file.yaml
```

## Usage Patterns

### Reading & Querying

```bash
# Simple field access
yq '.database.host' config.yaml

# Array access
yq '.servers[0].name' servers.yaml

# Filter array items
yq '.items[] | select(.type == "fruit")' data.yaml

# Recursive descent
yq '.. | select(has("password"))' secrets.yaml

# Get keys at a path
yq '.server | keys' config.yaml

# Get length
yq '.items | length' data.yaml

# Check existence
yq 'has(".database")' config.yaml
```

### Writing & Updating

```bash
# Simple assignment (in-place)
yq -i '.database.host = "newhost"' config.yaml

# Create nested path
yq -i '.a.b.c = "value"' config.yaml

# Relative update
yq -i '.counter |= . + 1' config.yaml

# Update array element
yq -i '.items[0].name = "renamed"' data.yaml

# Add to array
yq -i '.items += ["new-item"]' data.yaml

# Append object to array
yq -i '.items += {"name": "foo", "value": 123}' data.yaml

# Delete field
yq -i 'del(.unwanted.field)' config.yaml

# Multiple updates in one expression
yq -i '
  .database.host = "newhost" |
  .database.port = 5432 |
  .app.debug = false
' config.yaml
```

### Merging & Combining Files

```bash
# Merge two files (eval-all with multiply)
yq ea 'select(fileIndex == 0) * select(fileIndex == 1)' file1.yaml file2.yaml

# Merge all YAML files in a directory
yq ea '. as $item ireduce ({}; . * $item )' path/to/*.yml

# Append arrays from multiple files
yq ea 'select(fileIndex == 0) * select(fileIndex == 1)' base.yaml override.yaml

# Load and merge with null-safe defaults
yq -n 'load("defaults.yaml") * load("overrides.yaml")'
```

### Format Conversion

```bash
# YAML to JSON
yq -o=json config.yaml > config.json

# JSON to YAML (idiomatic)
yq -Poy data.json

# XML to YAML
yq -p xml input.xml

# YAML to XML
yq -o xml config.yaml

# CSV/TSV to YAML
yq -p csv data.csv

# Properties to YAML
yq -p props app.properties
```

### Shell Integration

```bash
# Extract value for shell variable
DB_HOST=$(yq '.database.host' config.yaml)

# Create bash array from YAML list
readarray -t items < <(yq '.items[]' data.yaml)

# Loop over array elements
for item in $(yq '.items[].name' data.yaml); do
    echo "Processing: $item"
done

# Export as environment variables
yq -o=json '.' config.yaml | jq -r 'to_entries[] | "\(.key)=\(.value)"' | xargs -I{} export {}

# Use env vars in expressions
yq -i ".app.api_key = strenv(API_KEY)" config.yaml

# Process shell output
echo '{"key": "value"}' | yq '.key'
```

### Front Matter Processing

```bash
# Extract front matter from Markdown
yq -f extract file.md

# Process front matter, keep body intact
yq -f process 'del(.date)' file.md

# Write back in-place
yq -fi process 'del(.date)' file.md
```

### XML-Specific Operations

```bash
# Read XML with attributes (attributes prefixed with +@)
yq '.element."+@attr"' file.xml

# Read XML content (content node named +content by default)
yq '.element."+content"' file.xml

# Set XML attribute
yq -i '.element."+@id" = "new-id"' file.xml

# Control XML output naming
yq --xml-content-name "_text" '.element._text' file.xml

# Skip processing instructions
yq --xml-skip-proc-inst '.' file.xml

# Strict XML parsing
yq --xml-strict-mode '.' file.xml

# Keep namespace after parsing attributes
yq --xml-keep-namespace '.' file.xml
```

### Working with Multiple Documents

```bash
# Process each document separately (default)
yq '.items' multi-doc.yaml    # processes first doc only

# Process all documents together
yq ea '. + load("other.yaml")' doc1.yaml doc2.yaml

# Split output into separate files by expression
yq --split-exp '."+@id"' multi-output.xml

# Document index for multi-document files
yq 'documentIndex' multi-doc.yaml    # returns current document index
```

### Security Flags

```bash
# Disable file operations (load, etc.)
yq --security-disable-file-ops '.data' file.yaml

# Disable environment variable operations
yq --security-disable-env-ops '.data' file.yaml
```

## Key Operators Reference

See [references/01-operators-reference.md](references/01-operators-reference.md) for a complete index of all 60+ operators.

Key operator categories:
- **Assignment**: `=`, `|=` (relative update), `+=` (concatenate)
- **Selection**: `select()`, `has()`, `pick()`, `omit()`
- **Array ops**: `sort`, `unique`, `reverse`, `shuffle`, `slice`, `flatten`, `group-by`
- **Object ops**: `keys`, `entries`, `map`, `reduce`, `collect`
- **String ops**: `strenv()`, `test()`, `match()`, `capture()`, `gsub()`
- **Math ops**: `+`, `-`, `*`, `/`, `%` (modulo), arithmetic on numbers/dates
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`, boolean `and`/`or`/`not`
- **Navigation**: `.`, `[]`, `..` (recursive descent), `|` (pipe)
- **File ops**: `load()`, `fileIndex`, `documentIndex`
- **Type ops**: `tag`, `kind`, `style`, `to_number`

## Common Recipes

See [references/02-common-recipes.md](references/02-common-recipes.md) for practical examples including:
- Finding and updating items in arrays
- Deeply pruning trees
- Sorting, filtering, flattening
- Exporting as environment variables
- Converting formats
- Working with XML attributes/namespaces
- CSV/TSV processing
- Base64 encoding/decoding

## Tips & Gotchas

See [references/03-tips-and-tricks.md](references/03-tips-and-tricks.md) for:
- YAML validation patterns
- PowerShell quoting issues
- Multi-line expressions and comments
- Bash integration patterns
- Special character handling
- Performance considerations

## Upgrading from v3

yq v4 is a complete rewrite with significant changes. See [references/04-upgrading-from-v3.md](references/04-upgrading-from-v3.md) for migration guide including:
- How to do v3 things in v4
- Breaking changes
- New features available in v4

## Known Limitations

- `yq` attempts to preserve comment positions and whitespace, but does not handle all scenarios (see [go-yaml/yaml#3](https://github.com/go-yaml/yaml/tree/v3) for details)
- PowerShell has unique quoting requirements — use single quotes or escape double quotes carefully
- `"yes"`, `"no"` are treated as booleans per YAML 1.2 standard (which yq uses)
- `yq` does not yet support everything `jq` does, but covers the most common operations

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
