# Multi-format Support

yq reads and writes multiple data formats. Use `-p` (or `--printmode`) for input format and `-o` (or `--output-format`) for output format.

## Supported Formats

- **YAML** (`yaml`) — default input and output
- **JSON** (`json`)
- **XML** (`xml`)
- **Properties** (`props`) — Java-style `.properties` files
- **CSV** (`csv`)
- **TSV** (`tsv`)
- **HCL** (`hcl`) — HashiCorp Configuration Language (Terraform, Nomad)
- **TOML** (`toml`) — input only, no TOML output support yet
- **Lua** (`lua`)
- **Base64** (`base64`)
- **INI** — handled via Properties parser

## Format Flags

```bash
# Input format
yq -p=json '.a' file.json
yq -p=xml '.root' file.xml
yq -p=csv '.[] | .name' file.csv
yq -p=props '.key' file.properties
yq -p=base64 '.' file.txt

# Output format
yq -o=json '.' file.yaml
yq -o=xml '.' file.yaml
yq -o=csv '.items' file.yaml
yq -o=props '.' file.yaml
yq -o=lua '.' file.yaml
yq -o=base64 '.field' file.yaml

# Combined (convert)
yq -p=json -oy '.' data.json    # JSON to YAML
yq -p=csv -oy '.' data.csv      # CSV to YAML
yq -p=xml -oj '.' data.xml      # XML to JSON
```

## Working with JSON

JSON is a subset of YAML, so single-document JSON can be read without `-p=json`. Use `-P` for idiomatic YAML styling.

```bash
# Parse JSON to YAML
yq -p=json sample.json

# Encode YAML as JSON
yq -o=json '.' sample.yml

# One-line JSON
yq -o=json -I=0 '.' sample.yml

# NDJSON / JSON Lines roundtrip
yq -p=json -o=json -I=0 sample.jsonl

# Multi-document JSON
yq -p=json -o=json -I=2 sample.json

# Update specific document in multi-doc JSON
yq -p=json -o=json -I=0 '(select(di == 1) | .each) += "cool"' sample.json
```

## Working with XML

Parse XML to YAML, encode YAML back to XML. Flags control attribute and content naming:

- `--xml-attribute-prefix` — prefix for XML attributes (default `+`, changing to `+@`)
- `--xml-content-name` — field name for text content (default `+content`)
- `--xml-directive-name` — field name for DTD directives (default `+directive`)
- `--xml-proc-inst-prefix` — prefix for processing instructions (default `+p_`)
- `--xml-strict-mode` — enforce XML spec requirements (default false)
- `--xml-keep-namespace` — keep attribute namespaces (default true)
- `--xml-raw-token` — do not verify element matching (default true)
- `--xml-skip-proc-inst` — skip processing instructions (default false)
- `--xml-skip-directives` — skip DTD directives (default false)

```bash
# Parse XML to YAML
yq -oy sample.xml

# Force type coercion (XML values are strings by default)
yq -oy '(.. | select(tag == "!!str")) |= from_yaml' sample.xml

# Force single element into array
yq -oy '.zoo.animal |= ([] + .)' sample.xml

# Roundtrip XML with update
yq '.cat.legs = "5"' sample.xml

# Encode YAML as XML string
yq '.a | to_xml' file.yaml
```

## Working with CSV / TSV

CSV/TSV input assumes the first row is headers. Output requires an array of flat objects or arrays of scalar arrays.

```bash
# Parse CSV to YAML
yq -p=csv sample.csv

# Disable auto-parsing of values (leave as strings)
yq -p=csv --csv-auto-parse=false sample.csv

# Encode YAML array of objects as CSV
yq -o=csv '.items' file.yaml

# Custom CSV columns
yq -o=csv '[["Name", "Age"]] + [.[] | [.name, .age]]' file.yaml

# Parse TSV
yq -p=tsv sample.tsv

# Encode as TSV
yq -o=tsv '.items' file.yaml

# Roundtrip CSV with update
yq -p=csv -o=csv '(.[] | select(.name == "Gary") | .age) = 30' data.csv
```

## Working with Properties

Java-style `.properties` files with dot-separated keys.

```bash
# Parse properties to YAML
yq -p=props sample.properties

# Encode YAML as properties
yq -o=props '.' file.yaml

# Array brackets (Spring Boot style)
yq -o=props --properties-array-brackets '.' file.yaml

# Custom separator
yq -o=props --properties-separator=" :@ " '.' file.yaml

# Keep empty arrays/maps
yq -o=props '(.. | select((tag == "!!map" or tag == "!!seq") and length == 0)) = ""' file.yaml

# Force type coercion (properties values are strings)
yq -p=props '(.. | select(tag == "!!str")) |= from_yaml' file.properties

# Convert numeric map key to map (not array)
yq -p=props '.things |= array_to_map' file.properties

# Roundtrip with update
yq -p=props -o=props '.person.name = "John"' config.properties
```

## Working with HCL

HashiCorp Configuration Language — used by Terraform, Nomad, Consul. Supports blocks, attributes, string interpolation, and comments.

```bash
# Parse HCL to YAML
yq -oy sample.hcl

# Roundtrip (HCL in, HCL out)
yq '.service.cat.process.main.command += "meow"' sample.hcl

# Preserve templates, functions, and arithmetic
yq '.port = 9090' sample.hcl
```

## Working with TOML

TOML input only — yq does not yet support TOML output.

```bash
# Parse TOML to YAML
yq -oy sample.toml

# Update and output as YAML
yq -p=toml '.server.port = 8080' sample.toml
```

## Working with Lua

Encode and decode Lua table structures. Flags:

- `--lua-unquoted` — produce unquoted keys for nicer output
- `--lua-globals` — export values to global scope instead of returning a table

```bash
# Parse Lua to YAML
yq -oy sample.lua

# Encode YAML as Lua
yq -o=lua '.' file.yaml

# Unquoted keys
yq -o=lua --lua-unquoted '.' file.yaml

# Global exports
yq -o=lua --lua-globals '.' file.yaml
```

## Working with Base64

Base64 assumes RFC4648 encoding, UTF-8 strings.

```bash
# Decode base64 to YAML
yq -p=base64 -oy '.' sample.txt

# Encode YAML value as base64
yq -o=base64 '.coolData' file.yaml

# Encode entire document as base64
yq '@yaml | @base64' file.yaml

# Decode base64 YAML document
yq '.coolData |= (@base64d | from_yaml)' file.yaml
```

## Working with INI

INI files are handled via the Properties parser.

```bash
yq -p=props config.ini
```

## Front Matter

Process YAML front matter in markdown files (Jekyll, Hugo, Assemble).

```bash
# Process front matter (update YAML, output entire file)
yq --front-matter=process '.a = "chocolate"' file.md

# Extract front matter only
yq --front-matter=extract '.a' file.md
```

## Split into Multiple Files

Use `-s` / `--split-exp` with an expression that returns a filename string. `$index` is available for the result index.

```bash
# Split multi-document YAML
yq -s '.name' file.yml   # creates files named by .name value

# Use index in filename
yq -s '"file_" + $index' file.yml

# Split array into individual files
yq '.[]' file.yml -s '"user_" + .name'

# Suppress document separators
yq -N -s '.a' file.yml
```

## Output Format Flags

- `-C` / `--colors`: Force color output
- `-M` / `--no-colors`: Force no color output
- `-P` / `--prettyPrint`: Idiomatic YAML (shorthand for `... style=""`)
- `-I <int>`: Indentation level (default 2)
- `-j` / `--tojson`: Output as JSON
- `-N` / `--no-doc`: Suppress document separators
- `--unwrapScalar` / `-r`: Unwrap scalar values (default true). Set to false to preserve formatting and comments on extracted scalars.
