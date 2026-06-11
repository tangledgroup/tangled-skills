# Advanced Options

## Contents
- Format Validation
- Data Transforms
- Caching
- Optional Parsers
- Other CLI Options
- FAQ

## Format Validation

JSON Schema defines `format` for string fields but does not require validators to check them. check-jsonschema checks formats by default.

### Supported Formats

`date`, `date-time`, `duration`, `email`, `hostname`, `idn-email`, `idn-hostname`, `ipv4`, `ipv6`, `iri`, `iri-reference`, `json-pointer`, `regex`, `relative-json-pointer`, `time`, `uri`, `uri-reference`, `uri-template`, `uuid`

### Disabling Format Checks

```bash
# Disable all format checks
uvx check-jsonschema --disable-formats '*' --schemafile schema.json instance.json

# Disable specific formats
uvx check-jsonschema --disable-formats time,date-time --disable-formats iri --schemafile schema.json instance.json
```

Format checking is not enforced by all JSON Schema tools. If a file validates with another tool but fails here, try disabling format checks.

### Regex Variant

Control regex syntax for `format: "regex"` and `pattern`/`patternProperties`:

```bash
# ECMAScript (default)
uvx check-jsonschema --regex-variant default --schemafile schema.json instance.json

# ECMAScript without unicode escapes
uvx check-jsonschema --regex-variant nonunicode --schemafile schema.json instance.json

# Python regex syntax
uvx check-jsonschema --regex-variant python --schemafile schema.json instance.json
```

## Data Transforms

`--data-transform` modifies instance data before validation.

### `azure-pipelines`

Unpacks compile-time expressions (e.g., `${{ variables.foo }}`) so they are skipped during validation. Based on Microsoft's VSCode language-server behavior.

```bash
uvx check-jsonschema --builtin-schema vendor.azure-pipelines \
  --data-transform azure-pipelines \
  --regex-variant nonunicode \
  azure-pipelines.yml
```

### `gitlab-ci`

Expands `!reference` tags to lists of strings so they pass schema validation. Only affects YAML data; does not interpret `!reference` values semantically.

```bash
uvx check-jsonschema --builtin-schema vendor.gitlab-ci \
  --data-transform gitlab-ci \
  --regex-variant nonunicode \
  .gitlab-ci.yml
```

## Caching

Remote schemas (via `--schemafile http(s)://...`) and `$ref` lookups are automatically cached.

### Cache Directories

| Platform | Location |
|---|---|
| Linux | `$XDG_CACHE_HOME/check_jsonschema/` or `~/.cache/check_jsonschema/` |
| macOS | `~/Library/Caches/check_jsonschema/` |
| Windows | `%LOCALAPPDATA%/check_jsonschema/` or `%APPDATA%/check_jsonschema/` |

Cached data is stored in `downloads/` (schemas) and `refs/` (resolved references).

### Cache Behavior

Cache hits are determined by comparing local file modification times against the `Last-Modified` HTTP header. If the local copy is older, the file is re-downloaded.

### Disabling or Clearing Cache

```bash
# Disable caching for a single run
uvx check-jsonschema --no-cache --schemafile https://example.com/schema.json instance.json

# Clear cache — remove the cache directory manually
rm -rf ~/.cache/check_jsonschema/
```

## Optional Parsers

### JSON5

JSON5 support requires `pyjson5` or `json5` installed alongside check-jsonschema. Supported for both instances and schemas.

```bash
# With uvx, add the dependency inline
uvx 'check-jsonschema' --force-filetype json5 --schemafile schema.json config.json5
```

In pre-commit, use `additional_dependencies: ['pyjson5']`.

### TOML

TOML parsing is always available (uses `tomllib` on Python 3.11+, `tomli` on older versions). Supported for instances only, not schemas.

TOML dates and times are converted to strings during parsing, checkable with `format: "date-time"`, `format: "date"`, or `format: "time"`.

```bash
uvx check-jsonschema --schemafile schema.json config.toml
```

## Other CLI Options

### `--fill-defaults`

Fill in `default` values from the schema before validation. Behavior is undefined when multiple defaults exist via `anyOf`, `oneOf`, or other polymorphism.

```bash
uvx check-jsonschema --fill-defaults --schemafile schema.json instance.json
```

### `--base-uri`

Override the base URI for `$ref` resolution (defaults to `$id` in the schema, falling back to retrieval URI).

```bash
uvx check-jsonschema --base-uri https://example.com/schemas/ --schemafile schema.json instance.json
```

### `--validator-class`

Use a custom validator class implementing `jsonschema.protocols.Validator`. Format: `<module>:<class>`.

```bash
# Use Draft7 explicitly
uvx check-jsonschema --validator-class 'jsonschema.validators:Draft7Validator' --schemafile schema.json instance.json
```

### `--default-filetype`

Assume a filetype for files not detected as JSON or YAML by extension.

```bash
# Treat extensionless files as YAML
uvx check-jsonschema --default-filetype yaml --schemafile schema.json config
```

### `--force-filetype`

Override file type detection entirely.

```bash
uvx check-jsonschema --force-filetype json5 --schemafile schema.json data.txt
```

### `--traceback-mode`

Control error output for debugging:

```bash
# Full Python traceback (default is pretty-printed errors)
uvx check-jsonschema --traceback-mode full --schemafile schema.json instance.json
```

### `--color`

Control colorized output: `always`, `never`, or `auto` (default). Also respects `NO_COLOR=1`.

## FAQ

### Self-hosted GitHub Actions runners

The SchemaStore GitHub Actions schema rejects custom `runs-on` strings. Work around by using an array with `self-hosted`:

```yaml
jobs:
  myjob:
    runs-on: [self-hosted, spot-self-hosted]
```

### Azure Pipelines quoted booleans

Microsoft's schema requires `"true"` / `"false"` as strings in some contexts. Quote boolean defaults:

```yaml
parameters:
  - name: myBoolean
    type: boolean
    default: 'true'  # quoted, not bare true
```

### Invoking from other languages

Run check-jsonschema via subprocess, controlling the installation. For Python:

```python
import subprocess, sys
result = subprocess.check_output([sys.executable, "-m", "check_jsonschema", "--version"])
```

For non-Python, install into a virtualenv and invoke explicitly: `venv/bin/check-jsonschema`.
